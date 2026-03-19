"""Read and write ~/.amocrm/config.json."""
from __future__ import annotations

import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".amocrm" / "config.json"
VALID_AUTH_MODES = {"longtoken", "oauth"}

_DEFAULTS: dict = {
    "refresh_token": None,
    "expires_at": None,
    "client_id": None,
    "client_secret": None,
    "redirect_uri": "http://localhost:8080",
}


def load_config() -> dict:
    """Load config from disk. Raises FileNotFoundError if missing, ValueError if invalid."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"No config found at {CONFIG_PATH}. Run: amocrm auth login"
        )
    data = json.loads(CONFIG_PATH.read_text())
    mode = data.get("auth_mode")
    if mode not in VALID_AUTH_MODES:
        raise ValueError(
            f"Invalid auth_mode {mode!r} in config. Must be one of: {VALID_AUTH_MODES}"
        )
    return {**_DEFAULTS, **data}


def save_config(config: dict) -> None:
    """Write config to disk. Creates parent directory if needed."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2))
