"""Long-lived token helpers."""
from __future__ import annotations

import time

REFRESH_THRESHOLD_SECONDS = 300


def is_token_expiring(expires_at: int | None) -> bool:
    """True if token expires within 300 seconds. False if None (long-lived token)."""
    if expires_at is None:
        return False
    return (expires_at - int(time.time())) < REFRESH_THRESHOLD_SECONDS


def make_longtoken_config(subdomain: str, token: str) -> dict[str, object]:
    """Build a config dict for long-lived token auth mode."""
    return {
        "subdomain": subdomain,
        "auth_mode": "longtoken",
        "access_token": token,
        "refresh_token": None,
        "expires_at": None,
        "client_id": None,
        "client_secret": None,
        "redirect_uri": "http://localhost:8080",
    }
