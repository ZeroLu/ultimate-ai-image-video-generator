"""Output helpers for JSON responses."""

from __future__ import annotations

import json
import sys
from typing import Any


def to_json(payload: Any, compact: bool) -> str:
    if compact:
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return json.dumps(payload, ensure_ascii=False, indent=2)


def print_payload(payload: Any, compact: bool) -> None:
    print(to_json(payload, compact=compact))


def print_error_and_exit(payload: Any) -> None:
    print(to_json(payload, compact=False), file=sys.stderr)
    raise SystemExit(1)

