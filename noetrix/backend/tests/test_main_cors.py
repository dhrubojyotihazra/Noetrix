"""Tests for CORS configuration in app/main.py (Item 14)."""

import os
from fastapi.testclient import TestClient


def test_cors_default_origin(monkeypatch):
    """By default, CORS must only allow localhost:3000 (no wildcard '*')."""
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
    # Re-import main to reload middleware settings
    import importlib
    import app.main
    importlib.reload(app.main)

    client = TestClient(app.main.app)

    # Test allowed origin
    resp_allowed = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert resp_allowed.headers.get("access-control-allow-origin") == "http://localhost:3000"

    # Test disallowed origin
    resp_disallowed = client.options(
        "/api/health",
        headers={
            "Origin": "http://evil-site.com",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert "access-control-allow-origin" not in resp_disallowed.headers


def test_cors_env_configured_origins(monkeypatch):
    """CORS origins configured via ALLOWED_ORIGINS comma-separated string."""
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://localhost:3000,https://noetrix.example.com")
    import importlib
    import app.main
    importlib.reload(app.main)

    client = TestClient(app.main.app)

    resp1 = client.options(
        "/api/health",
        headers={
            "Origin": "https://noetrix.example.com",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert resp1.headers.get("access-control-allow-origin") == "https://noetrix.example.com"
