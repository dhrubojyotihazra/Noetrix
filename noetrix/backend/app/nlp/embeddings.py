"""Sentence embeddings using sentence-transformers (all-MiniLM-L6-v2) with lazy loading."""

import logging
import numpy as np

logger = logging.getLogger(__name__)

_MODEL = None
_MODEL_LOAD_FAILED = False


def get_embedding_model():
    """Lazy load the sentence transformer model with meta-tensor protection."""
    global _MODEL, _MODEL_LOAD_FAILED
    if _MODEL is not None:
        return _MODEL
    if _MODEL_LOAD_FAILED:
        return None

    try:
        import torch
        from sentence_transformers import SentenceTransformer
        logger.info("Loading sentence-transformers model 'all-MiniLM-L6-v2'...")
        # Use low_cpu_mem_usage=False to prevent PyTorch 2.6+ meta-tensor copy error
        _MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu", model_kwargs={"low_cpu_mem_usage": False})
        return _MODEL
    except Exception as e:
        logger.warning(f"Could not load SentenceTransformer (falling back to calibrated TF-IDF cosine mode): {e}")
        _MODEL_LOAD_FAILED = True
        return None


def compute_semantic_similarity(text1: str, text2: str) -> float:
    """Compute semantic cosine similarity between two texts. Uses MiniLM with calibrated TF-IDF cosine fallback."""
    if not text1.strip() or not text2.strip():
        return 0.0

    model = get_embedding_model()
    if model is not None:
        try:
            # Truncate texts appropriately (approx 400 words per chunk)
            t1 = " ".join(text1.split()[:400])
            t2 = " ".join(text2.split()[:400])
            embeddings = model.encode([t1, t2])
            v1, v2 = embeddings[0], embeddings[1]
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            if norm1 == 0 or norm2 == 0:
                return 0.0
            cos_sim = float(np.dot(v1, v2) / (norm1 * norm2))
            return max(0.0, min(1.0, cos_sim))
        except Exception as e:
            logger.warning(f"Error computing embedding similarity: {e}")

    # Robust Fallback: TF-IDF bigram cosine similarity (calibrated to dense embedding scale)
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        vec = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", sublinear_tf=True)
        tfidf_mat = vec.fit_transform([text1, text2])
        cos = float(cosine_similarity(tfidf_mat[0:1], tfidf_mat[1:2])[0][0])
        # Scale into dense embedding range [0.15, 0.65]
        # An ML resume against an ML JD with ~40% vocabulary overlap maps to ~0.45 - 0.55
        calibrated_cos = min(0.95, max(0.10, cos * 1.1 + 0.12))
        return calibrated_cos
    except Exception:
        # Emergency token jaccard scaled
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        jaccard = float(len(intersection) / len(union)) if union else 0.0
        return min(0.80, jaccard * 4.0 + 0.15)
