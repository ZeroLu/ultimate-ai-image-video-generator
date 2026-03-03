"""API key resolution and local persistence helpers."""

from __future__ import annotations

import os
from pathlib import Path
import sys

from cyberbara_cli.constants import API_KEY_PAGE_URL

API_KEY_ENV_VAR = "CYBERBARA_API_KEY"
API_KEY_STORE_PATH = Path.home() / ".config" / "cyberbara" / "api_key"


def _normalize_api_key(api_key: str | None) -> str:
    return (api_key or "").strip()


def load_cached_api_key() -> str | None:
    if not API_KEY_STORE_PATH.is_file():
        return None
    key = _normalize_api_key(API_KEY_STORE_PATH.read_text(encoding="utf-8"))
    return key or None


def save_cached_api_key(api_key: str) -> None:
    key = _normalize_api_key(api_key)
    if not key:
        raise SystemExit("API key is empty.")

    API_KEY_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        API_KEY_STORE_PATH.parent.chmod(0o700)
    except OSError:
        pass

    API_KEY_STORE_PATH.write_text(f"{key}\n", encoding="utf-8")
    try:
        API_KEY_STORE_PATH.chmod(0o600)
    except OSError:
        pass


def _prompt_and_cache_api_key() -> str:
    message = (
        "API key not found. Visit "
        f"{API_KEY_PAGE_URL} to create one."
    )

    if not sys.stdin.isatty():
        raise SystemExit(
            f"{message} Then provide --api-key or set {API_KEY_ENV_VAR}."
        )

    print(message, file=sys.stderr)
    entered = _normalize_api_key(input("Please paste your CyberBara API key: "))
    if not entered:
        raise SystemExit("No API key provided.")

    save_cached_api_key(entered)
    print(f"API key saved to {API_KEY_STORE_PATH}.", file=sys.stderr)
    return entered


def resolve_api_key(cli_api_key: str | None) -> str:
    key_from_arg = _normalize_api_key(cli_api_key)
    if key_from_arg:
        save_cached_api_key(key_from_arg)
        return key_from_arg

    key_from_env = _normalize_api_key(os.getenv(API_KEY_ENV_VAR))
    if key_from_env:
        return key_from_env

    key_from_cache = load_cached_api_key()
    if key_from_cache:
        return key_from_cache

    return _prompt_and_cache_api_key()

