"""Task polling use case."""

from __future__ import annotations

import sys
import time
from typing import Any

from cyberbara_cli.constants import FINAL_TASK_STATUSES
from cyberbara_cli.output import print_payload
from cyberbara_cli.usecases.media_output import persist_and_open_task_output


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
    auto_save: bool = True,
    open_files: bool = True,
    output_dir: str | None = None,
) -> None:
    payload = wait_for_task_payload(
        client=client,
        task_id=task_id,
        interval=interval,
        timeout=timeout,
        timeout_per_request=timeout_per_request,
    )
    print_payload(payload, compact)
    if auto_save:
        persist_and_open_task_output(
            task_payload=payload,
            output_dir=output_dir,
            open_files=open_files,
        )


def wait_for_task_payload(
    *,
    client: Any,
    task_id: str,
    interval: float,
    timeout: int,
    timeout_per_request: int,
) -> Any:
    deadline = time.time() + timeout if timeout > 0 else None
    last_payload: Any = {}

    while True:
        payload = client.task(task_id, timeout=timeout_per_request)
        last_payload = payload
        task_status = extract_task_status(payload)
        if not task_status:
            raise SystemExit("Task status is missing in response.")

        print(f"[wait] task={task_id} status={task_status}", file=sys.stderr)

        if task_status in FINAL_TASK_STATUSES:
            if task_status != "success":
                print_payload(payload, compact=False)
                raise SystemExit(2)
            return payload

        if deadline is not None and time.time() >= deadline:
            print_payload(last_payload, compact=False)
            raise SystemExit(3)

        time.sleep(interval)
