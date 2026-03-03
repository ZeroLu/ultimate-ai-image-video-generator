"""Task polling use case."""

from __future__ import annotations

import sys
import time
from typing import Any

from cyberbara_cli.constants import FINAL_TASK_STATUSES
from cyberbara_cli.output import print_payload


def extract_task_status(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None
    data = payload.get("data")
    if not isinstance(data, dict):
        return None
    task = data.get("task")
    if not isinstance(task, dict):
        return None
    status = task.get("status")
    if isinstance(status, str):
        return status
    return None


def wait_for_task(
    *,
    client: Any,
    task_id: str,
    interval: float,
    timeout: int,
    timeout_per_request: int,
    compact: bool,
) -> None:
    deadline = time.time() + timeout if timeout > 0 else None
    last_payload: Any = {}

    while True:
        payload = client.task(task_id, timeout=timeout_per_request)
        last_payload = payload
        task_status = extract_task_status(payload)
        if not task_status:
            print_payload(payload, compact)
            raise SystemExit("Task status is missing in response.")

        print(f"[wait] task={task_id} status={task_status}", file=sys.stderr)

        if task_status in FINAL_TASK_STATUSES:
            print_payload(payload, compact)
            if task_status != "success":
                raise SystemExit(2)
            return

        if deadline is not None and time.time() >= deadline:
            print_payload(last_payload, compact)
            raise SystemExit(3)

        time.sleep(interval)

