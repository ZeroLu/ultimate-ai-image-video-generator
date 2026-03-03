"""Credit guard policy used before generation requests."""

from __future__ import annotations

from dataclasses import dataclass
import sys
from typing import Any


@dataclass
class QuoteResult:
    index: int
    estimated_credits: float
    quote_data: dict[str, Any]


def normalize_generation_requests(payload_body: Any, media_label: str) -> list[dict[str, Any]]:
    if isinstance(payload_body, dict):
        return [payload_body]

    if isinstance(payload_body, list):
        if not payload_body:
            raise SystemExit(f"{media_label.capitalize()} generation request list is empty.")
        requests: list[dict[str, Any]] = []
        for index, item in enumerate(payload_body, start=1):
            if not isinstance(item, dict):
                raise SystemExit(
                    f"{media_label.capitalize()} generation request #{index} must be a JSON object."
                )
            requests.append(item)
        return requests

    raise SystemExit(
        f"{media_label.capitalize()} generation payload must be an object or an array of objects."
    )


def build_quote_payload(request_body: dict[str, Any], media_type: str) -> dict[str, Any]:
    payload = dict(request_body)
    existing_media_type = payload.get("media_type")
    if existing_media_type in (None, ""):
        payload["media_type"] = media_type
    return payload


def extract_estimated_credits(quote_payload: Any) -> float:
    if not isinstance(quote_payload, dict):
        raise SystemExit("Quote response is not valid JSON.")

    data = quote_payload.get("data")
    if not isinstance(data, dict):
        raise SystemExit("Quote response missing data object.")

    estimated = data.get("estimated_credits")
    if isinstance(estimated, bool):
        raise SystemExit("Quote response estimated_credits has invalid type.")

    if isinstance(estimated, (int, float)):
        return float(estimated)

    if isinstance(estimated, str):
        text = estimated.strip()
        if text:
            try:
                return float(text)
            except ValueError as exc:
                raise SystemExit("Quote response estimated_credits is not numeric.") from exc

    raise SystemExit("Quote response missing estimated_credits.")


def normalize_credit_number(value: float) -> int | float:
    return int(value) if float(value).is_integer() else value


def format_credit_number(value: float) -> str:
    normalized = normalize_credit_number(value)
    if isinstance(normalized, int):
        return str(normalized)
    return str(normalized)


def collect_quote_results(
    *,
    client: Any,
    requests: list[dict[str, Any]],
    media_label: str,
    timeout: int,
) -> list[QuoteResult]:
    results: list[QuoteResult] = []
    for index, request_body in enumerate(requests, start=1):
        quote_body = build_quote_payload(request_body, media_label)
        quote_payload = client.quote(quote_body, timeout=timeout)
        estimated = extract_estimated_credits(quote_payload)
        quote_data = (
            quote_payload.get("data", {})
            if isinstance(quote_payload, dict) and isinstance(quote_payload.get("data"), dict)
            else {}
        )
        results.append(
            QuoteResult(
                index=index,
                estimated_credits=estimated,
                quote_data=quote_data,
            )
        )
    return results


def confirm_generation_or_exit(
    *,
    quote_results: list[QuoteResult],
    request_count: int,
    media_label: str,
    yes: bool,
) -> float:
    total_estimated = sum(item.estimated_credits for item in quote_results)

    print(
        f"[quote] {media_label}_requests={request_count} "
        f"total_estimated_credits={format_credit_number(total_estimated)}",
        file=sys.stderr,
    )
    for item in quote_results:
        model = item.quote_data.get("model", "unknown")
        scene = item.quote_data.get("scene", "unknown")
        estimated = format_credit_number(item.estimated_credits)
        print(
            f"[quote] request#{item.index} model={model} scene={scene} "
            f"estimated_credits={estimated}",
            file=sys.stderr,
        )

    if yes:
        print("[confirm] --yes provided, continue to submit requests.", file=sys.stderr)
        return total_estimated

    if not sys.stdin.isatty():
        raise SystemExit(
            f"Formal confirmation required before {media_label} generation. "
            "Run interactively and type CONFIRM, or re-run with --yes only after explicit user approval."
        )

    answer = input(f"Type CONFIRM to submit {media_label} generation request(s): ").strip()
    if answer != "CONFIRM":
        raise SystemExit("Canceled: confirmation not received.")

    return total_estimated

