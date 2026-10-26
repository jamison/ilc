from __future__ import annotations

import argparse
import os
import signal

import pytest

from ilc_core.cli import upgrade_cli
from ilc_core.cli.upgrade_cli import UpgradeCliError, run_upgrade_command
from ilc_core.release.upgrade_state import read_upgrade_state


def _watch_args(tmp_path, **overrides):
    data = {
        "upgrade_subcommand": "watch",
        "endpoint": "",
        "state_path": str(tmp_path / "upgrade_state.json"),
        "pid_path": str(tmp_path / "upgrade_watcher.pid"),
        "log_path": str(tmp_path / "upgrade_watcher.log"),
        "interval": "1",
        "daemon": False,
        "stop": False,
        "json": True,
        "_max_cycles": 1,
    }
    data.update(overrides)
    return argparse.Namespace(**data)


def test_upgrade_watch_single_poll_writes_watcher_state(tmp_path, monkeypatch):
    calls = []

    def fake_check_for_upgrade(*, endpoint=None, state_path=None):
        calls.append((endpoint, state_path))
        return {
            "checked_at_utc": "2026-10-14T00:00:00Z",
            "candidate_upgrade_available": False,
            "discovery_source": "test",
        }

    monkeypatch.setattr(upgrade_cli, "check_for_upgrade", fake_check_for_upgrade)

    result = run_upgrade_command(_watch_args(tmp_path))

    assert result["action"] == "upgrade-watch"
    assert result["cycles"] == 1
    assert len(calls) == 1
    state = read_upgrade_state(tmp_path / "upgrade_state.json")
    assert state["watcher"]["last_run_utc"] == "2026-10-14T00:00:00Z"
    assert state["watcher"]["interval_seconds"] == 1
    assert state["watcher"]["daemon"] is False


@pytest.mark.parametrize("bad_interval", ["0", "-1", "nan", "inf", "1.5"])
def test_upgrade_watch_rejects_invalid_interval(tmp_path, bad_interval):
    with pytest.raises(UpgradeCliError) as exc:
        run_upgrade_command(_watch_args(tmp_path, interval=bad_interval))

    assert exc.value.token == "upgrade_watch_interval_invalid"


def test_upgrade_watch_daemon_rejects_live_pid(tmp_path):
    pid_path = tmp_path / "upgrade_watcher.pid"
    lock_fd = upgrade_cli._acquire_watcher_lock(pid_path)
    upgrade_cli._write_locked_pid(lock_fd, os.getpid())
    try:
        with pytest.raises(UpgradeCliError) as exc:
            run_upgrade_command(_watch_args(tmp_path, daemon=True, _max_cycles=None))
        assert pid_path.exists()
    finally:
        os.close(lock_fd)
        pid_path.unlink(missing_ok=True)

    assert exc.value.token == "upgrade_watcher_already_running"


def test_upgrade_watch_stop_cleans_stale_pid(tmp_path):
    pid_path = tmp_path / "upgrade_watcher.pid"
    pid_path.write_text("999999\n", encoding="utf-8")

    result = run_upgrade_command(_watch_args(tmp_path, stop=True, _max_cycles=None))

    assert result["status"] == "upgrade_watcher_stale_pid_cleaned"
    assert result["pid"] == 999999
    assert not pid_path.exists()


def test_upgrade_watch_stop_sends_sigterm(tmp_path, monkeypatch):
    pid_path = tmp_path / "upgrade_watcher.pid"
    pid_path.write_text("12345\n", encoding="utf-8")
    killed = []
    monkeypatch.setattr(upgrade_cli, "_watcher_lock_is_held", lambda path: True)
    monkeypatch.setattr(upgrade_cli.os, "kill", lambda pid, sig: killed.append((pid, sig)))

    result = run_upgrade_command(_watch_args(tmp_path, stop=True, _max_cycles=None))

    assert result["status"] == "upgrade_watcher_stopped"
    assert killed == [(12345, signal.SIGTERM)]
    assert pid_path.exists()  # daemon owns cleanup after releasing the lock
