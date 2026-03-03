"""Command-line interface for CyberBara skill."""

from __future__ import annotations

import argparse

from cyberbara_cli.config import resolve_api_key
from cyberbara_cli.constants import DEFAULT_BASE_URL
from cyberbara_cli.gateways import CyberbaraClient
from cyberbara_cli.output import print_payload
from cyberbara_cli.payloads import add_json_input_flags, load_json_payload
from cyberbara_cli.usecases.generation import generate_media_with_credit_guard
from cyberbara_cli.usecases.wait_task import wait_for_task


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cyberbara_api.py",
        description="Call CyberBara Public API v1 endpoints from CLI.",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="CyberBara API key. If omitted, CLI uses env/cache and prompts when missing.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="HTTP request timeout in seconds (default: 120).",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Print compact JSON output.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    models_cmd = subparsers.add_parser("models", help="List available models.")
    models_cmd.add_argument(
        "--media-type",
        choices=["image", "video"],
        help="Optional media type filter.",
    )

    subparsers.add_parser("balance", help="Get current credit balance.")

    usage_cmd = subparsers.add_parser("usage", help="Get credits usage history.")
    usage_cmd.add_argument("--page", type=int, default=1, help="Page number.")
    usage_cmd.add_argument("--limit", type=int, default=20, help="Items per page.")
    usage_cmd.add_argument(
        "--from-date",
        help="Start date/time. Accepts ISO datetime or YYYY-MM-DD.",
    )
    usage_cmd.add_argument(
        "--to-date",
        help="End date/time. Accepts ISO datetime or YYYY-MM-DD.",
    )

    quote_cmd = subparsers.add_parser("quote", help="Estimate credit cost.")
    add_json_input_flags(quote_cmd, required=True)

    image_cmd = subparsers.add_parser(
        "generate-image",
        help="Quote credits, require confirmation, then create image generation task(s).",
    )
    add_json_input_flags(image_cmd, required=True)
    image_cmd.add_argument(
        "--yes",
        action="store_true",
        help="Skip interactive prompt after quote. Use only after explicit user approval.",
    )

    video_cmd = subparsers.add_parser(
        "generate-video",
        help="Quote credits, require confirmation, then create video generation task(s).",
    )
    add_json_input_flags(video_cmd, required=True)
    video_cmd.add_argument(
        "--yes",
        action="store_true",
        help="Skip interactive prompt after quote. Use only after explicit user approval.",
    )

    upload_cmd = subparsers.add_parser("upload-images", help="Upload reference image files.")
    upload_cmd.add_argument("files", nargs="+", help="Local image files to upload.")

    task_cmd = subparsers.add_parser("task", help="Fetch task status by task ID.")
    task_cmd.add_argument("--task-id", required=True, help="Task ID.")

    wait_cmd = subparsers.add_parser(
        "wait",
        help="Poll task status until success/failed/canceled.",
    )
    wait_cmd.add_argument("--task-id", required=True, help="Task ID.")
    wait_cmd.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Polling interval in seconds (default: 5).",
    )
    wait_cmd.add_argument(
        "--timeout",
        type=int,
        default=900,
        help="Total polling timeout in seconds (default: 900). Use 0 for no limit.",
    )
    wait_cmd.add_argument(
        "--timeout-per-request",
        type=int,
        default=120,
        help="HTTP timeout per polling request in seconds (default: 120).",
    )

    raw_cmd = subparsers.add_parser("raw", help="Call any endpoint directly.")
    raw_cmd.add_argument("--method", required=True, help="HTTP method.")
    raw_cmd.add_argument("--path", required=True, help="API path (for example /api/v1/models).")
    add_json_input_flags(raw_cmd, required=False)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    api_key = resolve_api_key(args.api_key)

    client = CyberbaraClient(api_key=api_key, base_url=DEFAULT_BASE_URL)

    if args.command == "models":
        payload = client.models(media_type=args.media_type, timeout=args.timeout)
        print_payload(payload, args.compact)
        return

    if args.command == "balance":
        payload = client.balance(timeout=args.timeout)
        print_payload(payload, args.compact)
        return

    if args.command == "usage":
        payload = client.usage(
            page=args.page,
            limit=args.limit,
            from_date=args.from_date,
            to_date=args.to_date,
            timeout=args.timeout,
        )
        print_payload(payload, args.compact)
        return

    if args.command == "quote":
        request_payload = load_json_payload(args.json, args.file)
        payload = client.quote(request_payload, timeout=args.timeout)
        print_payload(payload, args.compact)
        return

    if args.command == "generate-image":
        request_payload = load_json_payload(args.json, args.file)
        payload = generate_media_with_credit_guard(
            client=client,
            media_label="image",
            payload_body=request_payload,
            yes=args.yes,
            timeout=args.timeout,
        )
        print_payload(payload, args.compact)
        return

    if args.command == "generate-video":
        request_payload = load_json_payload(args.json, args.file)
        payload = generate_media_with_credit_guard(
            client=client,
            media_label="video",
            payload_body=request_payload,
            yes=args.yes,
            timeout=args.timeout,
        )
        print_payload(payload, args.compact)
        return

    if args.command == "upload-images":
        payload = client.upload_images(args.files, timeout=args.timeout)
        print_payload(payload, args.compact)
        return

    if args.command == "task":
        payload = client.task(args.task_id, timeout=args.timeout)
        print_payload(payload, args.compact)
        return

    if args.command == "wait":
        wait_for_task(
            client=client,
            task_id=args.task_id,
            interval=args.interval,
            timeout=args.timeout,
            timeout_per_request=args.timeout_per_request,
            compact=args.compact,
        )
        return

    if args.command == "raw":
        raw_payload = None
        if args.json or args.file:
            raw_payload = load_json_payload(args.json, args.file)
        payload = client.raw(
            method=args.method,
            path=args.path,
            payload=raw_payload,
            timeout=args.timeout,
        )
        print_payload(payload, args.compact)
        return

    parser.error(f"Unsupported command: {args.command}")
