# SPDX-License-Identifier: AGPL-3.0-only
"""CLI adapter for ``ilc upgrade``."""

from __future__ import annotations

import argparse
import os
import select
import signal
import shutil
import subprocess
import stat
import sys
import time
from pathlib import Path
from typing import Any, Callable

try:  # POSIX-only daemon support; foreground upgrade commands stay portable.
    import fcntl
except ImportError:  # pragma: no cover - exercised only on non-POSIX hosts.
    fcntl = None  # type: ignore[assignment]

from ilc_core.release.artifact_fetch import ArtifactFetchError, fetch_and_verify
from ilc_core.release.current_policy import (
    POLICY_CHANNEL,
    POLICY_ID,
    POLICY_NETWORK_ID,
    CurrentPolicyEvaluationInput,
)
from ilc_core.release.current_policy_view import (
    CurrentPolicyViewError,
    load_current_policy_evaluation_input,
)
from ilc_core.release.upgrade_check import (
    UpgradeCheckError,
    check_for_upgrade,
    is_transient_upgrade_error,
    require_arbitrary_source_release_authorized,
    validate_release_assertion,
)
from ilc_core.release.upgrade_state import (
    CURRENT_POLICY_HIGH_WATER_MARKS_KEY,
    default_upgrade_state_path,
    read_current_policy_high_water_mark,
    read_upgrade_state,
    write_upgrade_state,
)


DEFAULT_UPGRADE_WATCH_INTERVAL_SECONDS = 86_400
MAX_UPGRADE_WATCH_INTERVAL_SECONDS = 2_678_400
UPGRADE_APPLY_PIP_TIMEOUT_SECONDS = 600
UPGRADE_APPLY_VERIFY_TIMEOUT_SECONDS = 60
UPGRADE_WATCH_STARTUP_TIMEOUT_SECONDS = 10
UPGRADE_WATCH_MAX_LOG_BYTES = 1_048_576
UPGRADE_WATCH_MAX_TRANSIENT_BACKOFF_SECONDS = 3_600


class UpgradeCliError(Exception):
    """Typed CLI error wrapper with stable token."""

    def __init__(self, token: str, message: str | None = None) -> None:
        super().__init__(message or token)
        self.token = token
        self.message = message or token


def _state_with_preserved_policy_marks(
    payload: dict[str, Any],
    *,
    state_path: Path | None,
) -> dict[str, Any]:
    """Preserve anti-rollback state across watcher metadata writes."""

    try:
        prior = read_upgrade_state(path=state_path)
    except ValueError as exc:
        if str(exc) != "upgrade_state_missing":
            raise
        prior = {}
    marks = prior.get(CURRENT_POLICY_HIGH_WATER_MARKS_KEY)
    result = dict(payload)
    if marks is not None:
        if not isinstance(marks, dict):
            raise ValueError("current_policy_high_water_marks_corrupt")
        result[CURRENT_POLICY_HIGH_WATER_MARKS_KEY] = dict(marks)
    return result


def _load_apply_policy_input(
    *,
    policy_view_path: str,
    state_path: Path | None,
) -> CurrentPolicyEvaluationInput:
    """Load an untrusted portable view against independent local state."""

    if not policy_view_path:
        raise UpgradeCliError("upgrade_apply_policy_view_required")
    try:
        state = read_upgrade_state(path=state_path)
    except ValueError as exc:
        if str(exc) != "upgrade_state_missing":
            raise
        state = {}
    highest_seen = read_current_policy_high_water_mark(
        state,
        policy_id=POLICY_ID,
        network_id=POLICY_NETWORK_ID,
        channel=POLICY_CHANNEL,
    )
    return load_current_policy_evaluation_input(
        Path(policy_view_path),
        observer_highest_seen_sequence=highest_seen,
    )


def _parse_watch_interval(value: Any) -> int:
    if isinstance(value, bool):
        raise UpgradeCliError("upgrade_watch_interval_invalid")
    if isinstance(value, int):
        interval = value
    elif isinstance(value, str) and value.isascii() and value.isdigit():
        interval = int(value)
    else:
        raise UpgradeCliError("upgrade_watch_interval_invalid")
    if interval <= 0 or interval > MAX_UPGRADE_WATCH_INTERVAL_SECONDS:
        raise UpgradeCliError("upgrade_watch_interval_invalid")
    return interval


def _pid_path_for_state(state_path: Path | None, explicit_pid_path: str = "") -> Path:
    if explicit_pid_path:
        return Path(explicit_pid_path).expanduser()
    base_state_path = state_path or default_upgrade_state_path()
    return base_state_path.parent / "upgrade_watcher.pid"


def _log_path_for_pid(pid_path: Path, explicit_log_path: str = "") -> Path:
    if explicit_log_path:
        return Path(explicit_log_path).expanduser()
    return pid_path.with_name("upgrade_watcher.log")


def _acquire_watcher_lock(path: Path) -> int:
    if fcntl is None:
        raise UpgradeCliError("upgrade_watcher_daemon_unsupported_platform")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_CREAT | os.O_RDWR, stat.S_IRUSR | stat.S_IWUSR)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        os.close(fd)
        raise UpgradeCliError("upgrade_watcher_already_running") from exc
    return fd


def _write_locked_pid(fd: int, pid: int) -> None:
    encoded = f"{pid}\n".encode("ascii")
    os.lseek(fd, 0, os.SEEK_SET)
    os.ftruncate(fd, 0)
    os.write(fd, encoded)
    os.fsync(fd)


def _watcher_lock_is_held(path: Path) -> bool:
    if fcntl is None:
        return False
    try:
        fd = os.open(path, os.O_RDWR)
    except FileNotFoundError:
        return False
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        fcntl.flock(fd, fcntl.LOCK_UN)
        return False
    except Exception:
        return True
    finally:
        os.close(fd)


def _rotate_watcher_log(path: Path) -> None:
    try:
        if path.stat().st_size <= UPGRADE_WATCH_MAX_LOG_BYTES:
            return
    except FileNotFoundError:
        return
    rotated = path.with_suffix(path.suffix + ".1")
    rotated.unlink(missing_ok=True)
    os.replace(path, rotated)


def _read_pid(path: Path) -> int | None:
    try:
        text = path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None
    try:
        pid = int(text)
    except ValueError as exc:
        raise UpgradeCliError("upgrade_watcher_pid_file_invalid") from exc
    if pid <= 0:
        raise UpgradeCliError("upgrade_watcher_pid_file_invalid")
    return pid


def _remove_pid_file(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def _write_watcher_state(
    result: dict[str, Any],
    *,
    state_path: Path | None,
    interval_seconds: int,
    daemon: bool,
) -> None:
    checked_at = str(result.get("checked_at_utc", ""))
    payload = {
        **result,
        "watcher": {
            "last_run_utc": checked_at,
            "last_result": "ok",
            "interval_seconds": interval_seconds,
            "daemon": daemon,
        },
    }
    write_upgrade_state(
        _state_with_preserved_policy_marks(payload, state_path=state_path),
        path=state_path,
    )


def _write_watcher_error_state(
    exc: UpgradeCheckError,
    *,
    state_path: Path | None,
    interval_seconds: int,
    daemon: bool,
    transient_failures: int,
) -> None:
    payload = {
        "checked_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "watcher": {
            "daemon": daemon,
            "interval_seconds": interval_seconds,
            "last_result": "transient_error",
            "last_error_token": exc.token,
            "transient_failures": transient_failures,
        },
    }
    write_upgrade_state(
        _state_with_preserved_policy_marks(payload, state_path=state_path),
        path=state_path,
    )


def _run_watch_loop(
    *,
    endpoint: str | None,
    state_path: Path | None,
    interval_seconds: int,
    daemon: bool,
    sleep_fn: Callable[[float], None] = time.sleep,
    check_fn: Callable[..., dict[str, Any]] | None = None,
    max_cycles: int | None = None,
) -> dict[str, Any]:
    stop_requested = False
    check = check_fn or check_for_upgrade

    def _handle_sigterm(signum: int, frame: object) -> None:
        nonlocal stop_requested
        stop_requested = True

    previous_handler = signal.getsignal(signal.SIGTERM)
    signal.signal(signal.SIGTERM, _handle_sigterm)
    cycles = 0
    transient_failures = 0
    last_result: dict[str, Any] | None = None
    try:
        while not stop_requested:
            try:
                result = dict(check(endpoint=endpoint, state_path=state_path))
            except UpgradeCheckError as exc:
                if not is_transient_upgrade_error(exc):
                    raise
                transient_failures += 1
                cycles += 1
                _write_watcher_error_state(
                    exc,
                    state_path=state_path,
                    interval_seconds=interval_seconds,
                    daemon=daemon,
                    transient_failures=transient_failures,
                )
                if max_cycles is not None and cycles >= max_cycles:
                    break
                backoff = min(
                    interval_seconds,
                    UPGRADE_WATCH_MAX_TRANSIENT_BACKOFF_SECONDS,
                    2 ** min(transient_failures - 1, 12),
                )
                sleep_fn(backoff)
                continue
            transient_failures = 0
            _write_watcher_state(
                result,
                state_path=state_path,
                interval_seconds=interval_seconds,
                daemon=daemon,
            )
            last_result = result
            cycles += 1
            if not daemon and result.get("candidate_upgrade_available") is True:
                print("upgrade_candidate_available", file=sys.stdout, flush=True)
            if max_cycles is not None and cycles >= max_cycles:
                break
            sleep_fn(interval_seconds)
    finally:
        signal.signal(signal.SIGTERM, previous_handler)
    return {
        "action": "upgrade-watch",
        "cycles": cycles,
        "last_result": last_result or {},
        "upgrade_watcher_stopped": stop_requested,
    }


def _stop_watcher(pid_path: Path) -> dict[str, Any]:
    pid = _read_pid(pid_path)
    if pid is None:
        return {"action": "upgrade-watch-stop", "status": "upgrade_watcher_not_running"}
    if not _watcher_lock_is_held(pid_path):
        _remove_pid_file(pid_path)
        return {
            "action": "upgrade-watch-stop",
            "status": "upgrade_watcher_stale_pid_cleaned",
            "pid": pid,
        }
    os.kill(pid, signal.SIGTERM)
    return {"action": "upgrade-watch-stop", "status": "upgrade_watcher_stopped", "pid": pid}


def _start_daemon(
    *,
    endpoint: str | None,
    state_path: Path | None,
    pid_path: Path,
    log_path: Path,
    interval_seconds: int,
) -> dict[str, Any]:
    if os.name != "posix":
        raise UpgradeCliError("upgrade_watcher_daemon_unsupported_platform")

    lock_fd = _acquire_watcher_lock(pid_path)
    ready_read_fd, ready_write_fd = os.pipe()
    try:
        child_pid = os.fork()
        if child_pid:
            os.close(ready_write_fd)
            os.close(lock_fd)
            ready, _, _ = select.select(
                [ready_read_fd],
                [],
                [],
                UPGRADE_WATCH_STARTUP_TIMEOUT_SECONDS,
            )
            message = os.read(ready_read_fd, 128) if ready else b""
            os.close(ready_read_fd)
            if message != b"READY\n":
                try:
                    os.kill(child_pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                raise UpgradeCliError("upgrade_watcher_startup_failed")
            return {
                "action": "upgrade-watch",
                "status": "upgrade_watcher_daemon_started",
                "pid": child_pid,
                "pid_path": str(pid_path),
                "log_path": str(log_path),
            }
    except Exception:
        for fd in (ready_read_fd, ready_write_fd, lock_fd):
            try:
                os.close(fd)
            except OSError:
                pass
        _remove_pid_file(pid_path)
        raise

    exit_code = 0
    try:
        os.close(ready_read_fd)
        os.setsid()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        _rotate_watcher_log(log_path)
        with open(os.devnull, "rb", buffering=0) as stdin_handle, open(
            log_path, "ab", buffering=0
        ) as log_handle:
            os.dup2(stdin_handle.fileno(), sys.stdin.fileno())
            os.dup2(log_handle.fileno(), sys.stdout.fileno())
            os.dup2(log_handle.fileno(), sys.stderr.fileno())
        _write_locked_pid(lock_fd, os.getpid())
        os.write(ready_write_fd, b"READY\n")
        os.close(ready_write_fd)
        _run_watch_loop(
            endpoint=endpoint,
            state_path=state_path,
            interval_seconds=interval_seconds,
            daemon=True,
        )
    except BaseException as exc:  # noqa: BLE001 - daemon must preserve crash exit status.
        exit_code = 1
        try:
            print(
                f"upgrade_watcher_crashed:{type(exc).__name__}:{exc}",
                file=sys.stderr,
                flush=True,
            )
        except Exception:
            pass
    finally:
        try:
            os.close(ready_write_fd)
        except OSError:
            pass
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            os.close(lock_fd)
        except OSError:
            pass
        _remove_pid_file(pid_path)
        os._exit(exit_code)


def _verify_installed_release(version: str) -> None:
    script = """
import importlib
import importlib.metadata
import sys
expected = sys.argv[1]
observed = importlib.metadata.version('ilc-core')
if observed != expected:
    raise SystemExit(21)
importlib.import_module('ilc_core.release.upgrade_check')
importlib.import_module('ilc_model_router.cli')
from ilc_core.cli.main import _build_parser
args = _build_parser().parse_args(['upgrade', 'status'])
if args.command != 'upgrade' or args.upgrade_subcommand != 'status':
    raise SystemExit(22)
"""
    try:
        subprocess.run(
            [sys.executable, "-I", "-c", script, version],
            check=True,
            timeout=UPGRADE_APPLY_VERIFY_TIMEOUT_SECONDS,
        )
    except subprocess.CalledProcessError as exc:
        if exc.returncode == 21:
            raise UpgradeCliError("upgrade_apply_installed_version_mismatch") from exc
        raise UpgradeCliError("upgrade_apply_post_install_import_failed") from exc
    except subprocess.TimeoutExpired as exc:
        raise UpgradeCliError("upgrade_apply_post_install_verify_timeout") from exc


def run_upgrade_command(args: argparse.Namespace) -> dict[str, Any]:
    subcommand = getattr(args, "upgrade_subcommand", None)
    try:
        if subcommand == "check":
            state_path = Path(args.state_path) if getattr(args, "state_path", "") else None
            return {
                "action": "upgrade-check",
                **check_for_upgrade(endpoint=str(args.endpoint or "") or None, state_path=state_path),
            }
        if subcommand == "status":
            state_path = Path(args.state_path) if getattr(args, "state_path", "") else None
            return {"action": "upgrade-status", **read_upgrade_state(path=state_path)}
        if subcommand == "watch":
            state_path = Path(args.state_path) if getattr(args, "state_path", "") else None
            pid_path = _pid_path_for_state(state_path, str(getattr(args, "pid_path", "") or ""))
            interval_seconds = _parse_watch_interval(
                getattr(args, "interval", DEFAULT_UPGRADE_WATCH_INTERVAL_SECONDS)
            )
            if bool(getattr(args, "stop", False)):
                return _stop_watcher(pid_path)
            endpoint = str(getattr(args, "endpoint", "") or "") or None
            if bool(getattr(args, "daemon", False)):
                log_path = _log_path_for_pid(
                    pid_path,
                    str(getattr(args, "log_path", "") or ""),
                )
                return _start_daemon(
                    endpoint=endpoint,
                    state_path=state_path,
                    pid_path=pid_path,
                    log_path=log_path,
                    interval_seconds=interval_seconds,
                )
            return _run_watch_loop(
                endpoint=endpoint,
                state_path=state_path,
                interval_seconds=interval_seconds,
                daemon=False,
                max_cycles=getattr(args, "_max_cycles", None),
            )
        if subcommand == "apply":
            state_path = Path(args.state_path) if getattr(args, "state_path", "") else None
            policy_view_path = str(getattr(args, "policy_view", "") or "")
            policy_input = _load_apply_policy_input(
                policy_view_path=policy_view_path,
                state_path=state_path,
            )
            result = check_for_upgrade(
                endpoint=str(getattr(args, "endpoint", "") or "") or None,
                state_path=state_path,
                current_policy_evaluation_input=policy_input,
                include_release_assertion_payload=True,
            )
            if result.get("current_release_eligibility_status") == "rejected_by_current_policy":
                raise UpgradeCliError("upgrade_apply_release_rejected_current_policy")
            if result.get("authorized_upgrade_available") is not True:
                raise UpgradeCliError("upgrade_apply_no_authorized_upgrade_available")
            payload = result.get("release_assertion_payload")
            if not isinstance(payload, dict):
                raise UpgradeCliError("upgrade_apply_release_assertion_missing")
            verified_path = fetch_and_verify(
                payload,
                policy_evaluation_input=policy_input,
            )
            temp_dir = verified_path.parent
            try:
                if bool(getattr(args, "dry_run", False)):
                    return {
                        "action": "upgrade-apply",
                        "dry_run": True,
                        "status": "upgrade_apply_dry_run_verified",
                        "available_version": result.get("available_version", ""),
                        "verified_artifact_filename": verified_path.name,
                        "verified_artifact_size_bytes": verified_path.stat().st_size,
                    }
                fresh_policy_input = _load_apply_policy_input(
                    policy_view_path=policy_view_path,
                    state_path=state_path,
                )
                fresh_validation = validate_release_assertion(
                    payload,
                    current_policy_evaluation_input=fresh_policy_input,
                )
                require_arbitrary_source_release_authorized(fresh_validation)
                try:
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", "--no-deps", str(verified_path)],
                        check=True,
                        timeout=UPGRADE_APPLY_PIP_TIMEOUT_SECONDS,
                    )
                except subprocess.CalledProcessError as exc:
                    raise UpgradeCliError("upgrade_apply_pip_install_failed") from exc
                except subprocess.TimeoutExpired as exc:
                    raise UpgradeCliError("upgrade_apply_pip_install_timeout") from exc
                available_version = str(result.get("available_version", ""))
                _verify_installed_release(available_version)
                return {
                    "action": "upgrade-apply",
                    "dry_run": False,
                    "status": "upgrade_apply_success",
                    "available_version": available_version,
                }
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)
    except ArtifactFetchError as exc:
        raise UpgradeCliError(exc.token, exc.message) from exc
    except CurrentPolicyViewError as exc:
        raise UpgradeCliError(exc.token) from exc
    except UpgradeCheckError as exc:
        raise UpgradeCliError(exc.token, exc.message) from exc
    except ValueError as exc:
        token = str(exc).split(":", 1)[0]
        raise UpgradeCliError(token, str(exc)) from exc
    raise UpgradeCliError(f"unknown_upgrade_subcommand:{subcommand}")


__all__ = ["UpgradeCliError", "run_upgrade_command"]
