"""Payload parsing helpers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json_payload(inline_json: str | None, json_file: str | None) -> Any:
    if inline_json:
        try:
            return json.loads(inline_json)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid --json payload: {exc}") from exc

    if json_file:
        path = Path(json_file)
        if not path.is_file():
            raise SystemExit(f"JSON file not found: {path}")
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid JSON file {path}: {exc}") from exc

    raise SystemExit("JSON payload is required. Use --json or --file.")


def add_json_input_flags(cmd: argparse.ArgumentParser, required: bool = True) -> None:
    group = cmd.add_mutually_exclusive_group(required=required)
    group.add_argument("--json", help="Inline JSON payload string.")
    group.add_argument("--file", help="Path to JSON payload file.")

