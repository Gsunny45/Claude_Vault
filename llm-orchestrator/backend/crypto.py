"""
Simple Fernet-based encryption for storing user API keys locally.
Keys are encrypted at rest in a JSON file — never exposed to the browser.
"""

from __future__ import annotations
import json
import os
import base64
from pathlib import Path

from cryptography.fernet import Fernet

STORE_PATH = Path(__file__).parent / ".keystore.enc"


def _get_fernet() -> Fernet:
    """Return a Fernet instance using the configured or auto-generated secret."""
    from config import settings

    secret = settings.encryption_key
    if not secret:
        # Auto-generate and persist
        secret = Fernet.generate_key().decode()
        settings.encryption_key = secret
        # Write to .env so it persists across restarts
        env_path = Path(__file__).parent / ".env"
        with open(env_path, "a") as f:
            f.write(f"\nKEY_ENCRYPTION_SECRET={secret}\n")
    else:
        # Ensure it's valid base64 Fernet key
        if len(base64.urlsafe_b64decode(secret + "==")) != 32:
            secret = Fernet.generate_key().decode()
    return Fernet(secret.encode() if isinstance(secret, str) else secret)


def save_user_keys(keys: dict[str, str]) -> None:
    """Encrypt and save user keys to disk."""
    f = _get_fernet()
    payload = json.dumps(keys).encode()
    STORE_PATH.write_bytes(f.encrypt(payload))


def load_user_keys() -> dict[str, str]:
    """Load and decrypt user keys from disk."""
    if not STORE_PATH.exists():
        return {}
    f = _get_fernet()
    try:
        payload = f.decrypt(STORE_PATH.read_bytes())
        return json.loads(payload)
    except Exception:
        return {}


def apply_user_keys_to_settings() -> None:
    """Load stored keys and apply them to the runtime settings object."""
    from config import settings

    keys = load_user_keys()
    for provider in ("openai", "gemini", "mistral", "grok", "groq", "deepseek", "perplexity"):
        val = keys.get(f"{provider}_key", "")
        if val:
            setattr(settings, f"user_{provider}_key", val)
