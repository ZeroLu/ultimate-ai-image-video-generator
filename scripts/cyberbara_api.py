#!/usr/bin/env python3
"""Thin entrypoint for CyberBara CLI."""

from __future__ import annotations

import sys
from pathlib import Path


def _bootstrap() -> None:
    skill_root = Path(__file__).resolve().parents[1]
    src_path = skill_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


def main() -> None:
    _bootstrap()
    from cyberbara_cli.cli import main as run_main

    run_main()


if __name__ == "__main__":
    main()
