from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _run_cli(home: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["HOME"] = str(home)
    return subprocess.run(
        [sys.executable, "-m", "ilc_core.cli.main", *args],
        cwd=ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_validator_status_reports_missing_identity_without_mutation(tmp_path: Path) -> None:
    result = _run_cli(tmp_path, "validator", "status", "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    data = payload["data"]
    assert data["action"] == "validator-status"
    assert data["agent_id"] is None
    assert data["identity_provisioned"] is False
    assert data["validator_participation_enabled"] is False
    assert data["lmdb_epoch"] is None
    assert not (tmp_path / ".ilc" / "identity").exists()


def test_validator_status_reports_agent_id_and_lmdb_readability(tmp_path: Path) -> None:
    identity_dir = tmp_path / ".ilc" / "identity"
    identity_dir.mkdir(parents=True)
    agent_id = "a" * 96
    (identity_dir / "agent_id").write_text(f"{agent_id}\n", encoding="utf-8")
    lmdb_path = tmp_path / ".ilc" / "lmdb"
    lmdb_path.mkdir(parents=True)

    result = _run_cli(tmp_path, "validator", "status", "--json", "--lmdb-path", str(lmdb_path))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    data = payload["data"]
    assert data["agent_id"] == agent_id
    assert data["identity_provisioned"] is True
    assert data["identity_status"] == "present"
    assert data["lmdb_readable"] is True
    assert data["validator_participation_enabled"] is True


def test_validator_status_rejects_invalid_agent_id(tmp_path: Path) -> None:
    identity_dir = tmp_path / ".ilc" / "identity"
    identity_dir.mkdir(parents=True)
    (identity_dir / "agent_id").write_text("not-an-agent-id\n", encoding="utf-8")

    result = _run_cli(tmp_path, "validator", "status")

    assert result.returncode != 0
    assert "validator_status_agent_id_invalid" in result.stderr
