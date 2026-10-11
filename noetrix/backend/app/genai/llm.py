"""Central Groq Generative AI Adapter for Noetrix.

Requirements:
- Interface: complete_json(system, user, model_cls, model=None, retries=1) -> validated Pydantic object
- Temperature 0, request timeout configurable via LLM_TIMEOUT (default 20s)
- Strict structured outputs (strict: true) for supported models, json_object mode fallback
- Bounded retry on invalid JSON with repair prompt
- Bounded retry on HTTP 429 backoff
- Concurrency limited to 3 simultaneous calls
- In-memory SHA-256 caching of validated results (capped at 256 entries with TTL eviction)
- LLMUnavailable raised when off, unconfigured, or failing
- ZERO logging of sensitive text, CV text, JD text, or API keys
"""

import hashlib
import json
import logging
import os
import threading
import time
from typing import Any, TypeVar

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

# Load environment variables from .env
load_dotenv()

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

PROMPT_VERSION = "v1.0"

# In-memory thread-safe LRU/dict cache: hash -> (timestamp, validated_model_instance)
_CACHE: dict[str, tuple[float, BaseModel]] = {}
_CACHE_LOCK = threading.Lock()
_CACHE_TTL_SECONDS = 3600  # 1 hour
_MAX_CACHE_ENTRIES = 256


def _evict_expired_cache():
    """Evict expired entries from _CACHE (must be called with _CACHE_LOCK held)."""
    now = time.time()
    expired_keys = [k for k, (ts, _) in _CACHE.items() if now - ts >= _CACHE_TTL_SECONDS]
    for k in expired_keys:
        del _CACHE[k]


def _store_in_cache(key: str, val: BaseModel):
    """Store validated object in cache with TTL eviction and size cap (max 256)."""
    with _CACHE_LOCK:
        _evict_expired_cache()
        if len(_CACHE) >= _MAX_CACHE_ENTRIES:
            oldest_keys = sorted(_CACHE.keys(), key=lambda k: _CACHE[k][0])
            to_remove = len(_CACHE) - _MAX_CACHE_ENTRIES + 1
            for k in oldest_keys[:to_remove]:
                del _CACHE[k]
        _CACHE[key] = (time.time(), val)


def get_llm_timeout() -> float:
    """Retrieve LLM request timeout from LLM_TIMEOUT env var (default 20.0s)."""
    try:
        return float(os.getenv("LLM_TIMEOUT", "20.0").strip())
    except Exception:
        return 20.0

# Concurrency limiter: limit to 3 simultaneous calls
_SEMAPHORE = threading.Semaphore(3)

# Performance & Evaluation metrics tracker
_METRICS: dict[str, Any] = {"call_count": 0, "latencies": []}
_METRICS_LOCK = threading.Lock()


def get_llm_metrics() -> dict[str, Any]:
    with _METRICS_LOCK:
        lats = list(_METRICS["latencies"])
        count = _METRICS["call_count"]
    median_lat = float(sorted(lats)[len(lats) // 2]) if lats else 0.0
    return {"call_count": count, "latencies": lats, "median_latency": median_lat}


def reset_llm_metrics():
    with _METRICS_LOCK:
        _METRICS["call_count"] = 0
        _METRICS["latencies"] = []


class LLMUnavailable(Exception):
    """Raised when LLM mode is off, unconfigured, rate-limited, or unavailable."""
    pass


def get_llm_config() -> dict[str, str]:
    """Retrieve current LLM configuration from environment variables."""
    mode = os.getenv("LLM_MODE", "off").strip().lower()
    provider = os.getenv("LLM_PROVIDER", "groq").strip().lower()
    model = os.getenv("LLM_MODEL", "openai/gpt-oss-20b").strip()
    fast_model = os.getenv("LLM_FAST_MODEL", "openai/gpt-oss-20b").strip()
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    return {
        "mode": mode,
        "provider": provider,
        "model": model,
        "fast_model": fast_model,
        "api_key": api_key
    }


def _prepare_strict_schema(schema: dict) -> dict:
    """Recursively inject additionalProperties: False into schema for strict structured output."""
    if not isinstance(schema, dict):
        return schema
    res = dict(schema)
    if res.get("type") == "object":
        res["additionalProperties"] = False
    if "properties" in res:
        res["properties"] = {k: _prepare_strict_schema(v) for k, v in res["properties"].items()}
    if "$defs" in res:
        res["$defs"] = {k: _prepare_strict_schema(v) for k, v in res["$defs"].items()}
    return res


def _compute_cache_key(model: str, system: str, user: str) -> str:
    """Compute SHA-256 hash of model + prompt_version + redacted input for cache key."""
    raw = f"{model}:{PROMPT_VERSION}:{system}:{user}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def complete_json(
    system: str,
    user: str,
    model_cls: type[T],
    model: str | None = None,
    retries: int = 1,
    timeout: float | None = None
) -> T:
    """Execute a structured completion returning a validated Pydantic object.
    
    Guarantees:
    - Temperature 0, timeout configurable via LLM_TIMEOUT (default 20s)
    - Strict structured outputs with Pydantic validation
    - In-memory SHA-256 caching (capped at 256 entries with TTL eviction)
    - Concurrency limited to 3 simultaneous requests
    - Clean fallback with LLMUnavailable
    - Safe logging: only latency, token sizes, model, and non-sensitive error categories
    """
    cfg = get_llm_config()

    if cfg["mode"] != "on":
        raise LLMUnavailable("LLM mode is off (LLM_MODE != 'on')")

    if not cfg["api_key"] or cfg["api_key"] == "PASTE_YOUR_GROQ_API_KEY_HERE":
        raise LLMUnavailable("GROQ_API_KEY is not configured or placeholder was not replaced")

    effective_timeout = timeout if timeout is not None else get_llm_timeout()
    selected_model = model or cfg["model"]
    cache_key = _compute_cache_key(selected_model, system, user)

    # 1. Check in-memory cache
    with _CACHE_LOCK:
        _evict_expired_cache()
        if cache_key in _CACHE:
            ts, cached_obj = _CACHE[cache_key]
            if time.time() - ts < _CACHE_TTL_SECONDS:
                logger.info(
                    f"[LLM] Cache HIT for model='{selected_model}', "
                    f"input_len={len(user)}, version='{PROMPT_VERSION}'"
                )
                if isinstance(cached_obj, model_cls):
                    return cached_obj

    # 2. Lazy import Groq SDK
    try:
        from groq import Groq, RateLimitError, APIError, APIConnectionError
    except ImportError:
        raise LLMUnavailable("Groq SDK is not installed")

    client = Groq(api_key=cfg["api_key"], timeout=effective_timeout)

    # 3. Acquire semaphore (max 3 concurrent requests)
    acquired = _SEMAPHORE.acquire(timeout=effective_timeout)
    if not acquired:
        raise LLMUnavailable("LLM concurrency limit reached (3 concurrent calls active)")

    start_time = time.time()
    try:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]

        # Prepare strict schema
        schema_dict = _prepare_strict_schema(model_cls.model_json_schema())
        response_format: dict[str, Any] = {
            "type": "json_schema",
            "json_schema": {
                "name": model_cls.__name__,
                "strict": True,
                "schema": schema_dict
            }
        }

        # Attempt call with repair retry logic
        last_error = None
        for attempt in range(retries + 1):
            try:
                try:
                    resp = client.chat.completions.create(
                        model=selected_model,
                        messages=messages,
                        temperature=0,
                        response_format=response_format
                    )
                except APIError as api_err:
                    # If model returned model_not_found or json_schema rejected, try json_object mode
                    if "schema" in str(api_err).lower() or "response_format" in str(api_err).lower():
                        resp = client.chat.completions.create(
                            model=selected_model,
                            messages=messages,
                            temperature=0,
                            response_format={"type": "json_object"}
                        )
                    elif "model_not_found" in str(api_err).lower() and selected_model != cfg["model"]:
                        # If fast model was not found, fall back to default model
                        selected_model = cfg["model"]
                        resp = client.chat.completions.create(
                            model=selected_model,
                            messages=messages,
                            temperature=0,
                            response_format={"type": "json_object"}
                        )
                    else:
                        raise api_err

                raw_content = resp.choices[0].message.content or ""
                parsed_json = json.loads(raw_content)
                validated_obj = model_cls.model_validate(parsed_json)

                elapsed = round(time.time() - start_time, 2)
                logger.info(
                    f"[LLM] Success model='{selected_model}', latency={elapsed}s, "
                    f"input_len={len(user)}, output_len={len(raw_content)}"
                )

                # Store in cache (with TTL eviction and 256 cap)
                _store_in_cache(cache_key, validated_obj)

                with _METRICS_LOCK:
                    _METRICS["call_count"] += 1
                    _METRICS["latencies"].append(elapsed)

                return validated_obj

            except RateLimitError as rle:
                # HTTP 429 bounded backoff retry once
                if attempt < retries:
                    logger.warning(f"[LLM] Rate limit 429 encountered. Backing off 2.0s before retry.")
                    time.sleep(2.0)
                    continue
                last_error = "RateLimitError 429 (quota exceeded)"
                break

            except (json.JSONDecodeError, ValidationError) as parse_err:
                if attempt < retries:
                    logger.info(f"[LLM] Output validation failed ({type(parse_err).__name__}). Retrying with repair prompt.")
                    messages.append({"role": "assistant", "content": raw_content if 'raw_content' in locals() else ""})
                    messages.append({
                        "role": "user",
                        "content": f"Previous output was invalid: {str(parse_err)[:150]}. Please output strictly valid JSON matching the exact schema."
                    })
                    continue
                last_error = f"Validation failed ({type(parse_err).__name__})"
                break

            except Exception as e:
                last_error = f"{type(e).__name__}"
                break

        elapsed = round(time.time() - start_time, 2)
        logger.warning(f"[LLM] Call failed after {elapsed}s: {last_error}")
        raise LLMUnavailable(f"LLM call failed: {last_error}")

    finally:
        _SEMAPHORE.release()


def check_llm_health() -> dict[str, Any]:
    """Check LLM configuration and reachability without exposing sensitive credentials or requiring documents."""
    cfg = get_llm_config()
    is_on = cfg["mode"] == "on"
    has_key = bool(cfg["api_key"] and cfg["api_key"] != "PASTE_YOUR_GROQ_API_KEY_HERE")

    reachable = False
    if is_on and has_key:
        try:
            from groq import Groq
            client = Groq(api_key=cfg["api_key"], timeout=5.0)
            models = client.models.list()
            # Verify configured model is present or list was retrieved
            reachable = bool(models.data)
        except Exception as e:
            logger.info(f"[LLM Health] Probe failed: {type(e).__name__}")
            reachable = False

    return {
        "mode": cfg["mode"],
        "provider": cfg["provider"],
        "model": cfg["model"],
        "fast_model": cfg["fast_model"],
        "reachable": reachable
    }
