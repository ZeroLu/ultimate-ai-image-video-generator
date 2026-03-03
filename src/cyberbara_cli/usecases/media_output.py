"""Download and open generated media outputs."""

from __future__ import annotations

from datetime import datetime, timezone
import mimetypes
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any
from urllib import parse, request
import uuid

from cyberbara_cli.constants import DEFAULT_HTTP_USER_AGENT, DEFAULT_OUTPUT_DIR


def _extract_output_urls(task_payload: Any) -> list[str]:
    if not isinstance(task_payload, dict):
        return []
    data = task_payload.get("data")
    if not isinstance(data, dict):
        return []
    task = data.get("task")
    if not isinstance(task, dict):
        return []
    output = task.get("output")
    if not isinstance(output, dict):
        return []

    urls: list[str] = []
    images = output.get("images")
    videos = output.get("videos")
    for collection in (images, videos):
        if isinstance(collection, list):
            for item in collection:
                if isinstance(item, str) and item.strip():
                    urls.append(item.strip())
    return urls


def _guess_extension(url: str, content_type: str | None) -> str:
    path_suffix = Path(parse.urlparse(url).path).suffix.lower()
    if path_suffix:
        return path_suffix

    if content_type:
        ext = mimetypes.guess_extension(content_type)
        if ext:
            if ext == ".jpe":
                return ".jpg"
            return ext

    return ".bin"


def _download_media_url(url: str, output_dir: Path) -> Path:
    req = request.Request(
        url=url,
        headers={"User-Agent": DEFAULT_HTTP_USER_AGENT},
        method="GET",
    )

    with request.urlopen(req, timeout=180) as resp:
        content = resp.read()
        content_type = resp.headers.get_content_type() if resp.headers else None

    ext = _guess_extension(url, content_type)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"cyberbara_{timestamp}_{uuid.uuid4().hex[:8]}{ext}"
    file_path = output_dir / filename
    file_path.write_bytes(content)
    return file_path


def _open_file(file_path: Path) -> None:
    try:
        if sys.platform.startswith("darwin"):
            subprocess.Popen(["open", str(file_path)])
            return

        if os_name_is_windows():
            subprocess.Popen(["cmd", "/c", "start", "", str(file_path)])
            return

        xdg_open = shutil.which("xdg-open")
        if xdg_open:
            subprocess.Popen([xdg_open, str(file_path)])
            return

        print(
            f"[open] Unable to auto-open {file_path}. No supported opener found.",
            file=sys.stderr,
        )
    except Exception as exc:  # pragma: no cover - best-effort open
        print(f"[open] Failed to open {file_path}: {exc}", file=sys.stderr)


def os_name_is_windows() -> bool:
    return sys.platform.startswith("win")


def persist_and_open_task_output(
    *,
    task_payload: Any,
    output_dir: str | None = None,
    open_files: bool = True,
) -> list[str]:
    urls = _extract_output_urls(task_payload)
    if not urls:
        return []

    target_dir = Path(output_dir or DEFAULT_OUTPUT_DIR).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    saved_files: list[str] = []
    for url in urls:
        path = _download_media_url(url, target_dir)
        saved_files.append(str(path))
        print(f"[save] {path}", file=sys.stderr)
        if open_files:
            _open_file(path)

    return saved_files

