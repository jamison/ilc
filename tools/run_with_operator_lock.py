#!/usr/bin/env python3
from __future__ import annotations

import argparse
import atexit
import fcntl
import json
import os
import signal
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LOCK_ROOT = Path("out/operator_run_locks")
BUSY_EXIT_CODE = 73


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sanitize_lock_name(name: str) -> str:
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.")
    if not name or any(ch not in allowed for ch in name):
        raise SystemExit(
            "invalid_lock_name: use only letters, numbers, '-', '_' or '.'"
        )
    return name


def _lock_paths(lock_name: str) -> tuple[Path, Path]:
    LOCK_ROOT.mkdir(parents=True, exist_ok=True)
    base = LOCK_ROOT / lock_name
    return base.with_suffix(".lock"), base.with_suffix(".json")


def _read_metadata(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return obj if isinstance(obj, dict) else None


def _pid_is_live(pid: int | None) -> bool:
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _format_metadata(metadata: dict[str, Any] | None) -> str:
    if not metadata:
        return "metadata=unavailable"
    pieces = []
    for key in ("owner", "label", "pid", "host", "started_at", "cwd", "command"):
        value = metadata.get(key)
        if value:
            pieces.append(f"{key}={value}")
    return ", ".join(pieces) if pieces else "metadata=empty"


def _print_status(lock_name: str) -> int:
    lock_path, metadata_path = _lock_paths(lock_name)
    metadata = _read_metadata(metadata_path)
    with lock_path.open("a", encoding="utf-8") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(f"ACTIVE lock={lock_name} {_format_metadata(metadata)}")
            return 0
        finally:
            try:
                fcntl.flock(handle, fcntl.LOCK_UN)
            except OSError:
                pass

    if metadata and _pid_is_live(metadata.get("pid")):
        print(f"ACTIVE_METADATA_ONLY lock={lock_name} {_format_metadata(metadata)}")
    elif metadata:
        print(f"STALE_METADATA lock={lock_name} {_format_metadata(metadata)}")
    else:
        print(f"INACTIVE lock={lock_name}")
    return 0


def _write_metadata(
    metadata_path: Path,
    lock_name: str,
    owner: str,
    label: str | None,
    command: list[str],
) -> None:
    payload = {
        "lock_name": lock_name,
        "owner": owner,
        "label": label,
        "pid": os.getpid(),
        "host": socket.gethostname(),
        "started_at": _utc_now(),
        "cwd": str(Path.cwd()),
        "command": " ".join(command),
    }
    metadata_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _run_with_lock(lock_name: str, owner: str, label: str | None, wait: bool, command: list[str]) -> int:
    lock_path, metadata_path = _lock_paths(lock_name)
    handle = lock_path.open("a", encoding="utf-8")
    cleanup_complete = False

    def cleanup() -> None:
        nonlocal cleanup_complete
        if cleanup_complete:
            return
        cleanup_complete = True
        try:
            if metadata_path.exists():
                metadata_path.unlink()
        except OSError:
            pass
        try:
            fcntl.flock(handle, fcntl.LOCK_UN)
        except OSError:
            pass
        try:
            handle.close()
        except OSError:
            pass

    atexit.register(cleanup)

    try:
        lock_mode = fcntl.LOCK_EX if wait else (fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(handle, lock_mode)
    except BlockingIOError:
        metadata = _read_metadata(metadata_path)
        print(
            f"LOCK_BUSY lock={lock_name} {_format_metadata(metadata)}",
            file=sys.stderr,
        )
        cleanup()
        return BUSY_EXIT_CODE

    _write_metadata(metadata_path, lock_name, owner, label, command)

    child: subprocess.Popen[Any] | None = None

    def _forward_signal(signum: int, _frame: object) -> None:
        if child is not None and child.poll() is None:
            child.send_signal(signum)

    previous_handlers: dict[int, Any] = {}
    for signame in ("SIGINT", "SIGTERM", "SIGHUP"):
        sig = getattr(signal, signame, None)
        if sig is not None:
            previous_handlers[sig] = signal.getsignal(sig)
            signal.signal(sig, _forward_signal)

    try:
        child = subprocess.Popen(command)
        return child.wait()
    finally:
        for sig, handler in previous_handlers.items():
            signal.signal(sig, handler)
        cleanup()


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Run a command under a shared operator lock to block overlapping long runs."
    )
    parser.add_argument("--lock", required=True, help="Logical lock name, for example repo_verification.")
    parser.add_argument("--owner", default=os.environ.get("USER", "unknown"), help="Human or agent owner label.")
    parser.add_argument("--label", help="Short run label, for example gate-357 or full-suite.")
    parser.add_argument("--wait", action="store_true", help="Wait for the lock instead of failing fast.")
    parser.add_argument("--status", action="store_true", help="Show current lock status and exit.")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run after '--'.")
    args = parser.parse_args(argv[1:])

    lock_name = _sanitize_lock_name(args.lock)
    if args.status:
        return _print_status(lock_name)

    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.error("command is required unless --status is used")
    return _run_with_lock(lock_name, args.owner, args.label, args.wait, command)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
