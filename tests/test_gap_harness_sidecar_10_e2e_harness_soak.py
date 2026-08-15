# SPDX-License-Identifier: AGPL-3.0-only
"""Tests for GAP-HARNESS-SIDECAR-10 local E2E harness soak."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.testbed import e2e_harness_soak
from tools.testbed.e2e_harness_soak import E2EHarnessSoakConfig, run_e2e_harness_soak


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "tools/testbed/e2e_harness_soak.py"
AGENT_ID = "a" * 96


def _write_key(path: Path) -> Path:
    private_key = Ed25519PrivateKey.generate()
    path.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    path.chmod(0o600)
    return path


def _config(tmp_path: Path, *, dry_run: bool = False, epoch: int = 7) -> E2EHarnessSoakConfig:
    return E2EHarnessSoakConfig(
        agent_id=AGENT_ID,
        lmdb_base_path=tmp_path / "lmdb",
        signing_key_path=Path("/dev/null") if dry_run else _write_key(tmp_path / "agent.pem"),
        epoch=epoch,
        dry_run=dry_run,
        output_path=tmp_path / "evidence.json",
    )


def test_dry_run_completes_all_five_legs_with_receipts(tmp_path: Path) -> None:
    evidence = run_e2e_harness_soak(_config(tmp_path, dry_run=True))

    assert evidence["verdict"] == "PASS"
    assert list(evidence["steps"].keys()) == ["perceive", "act", "prove", "receive", "delegate"]
    assert all(isinstance(step["receipt_token"], str) for step in evidence["steps"].values())
    assert evidence["steps"]["act"]["write_receipt"]["dry_run"] is True
    assert not (tmp_path / "evidence.json").exists()


def test_non_dry_run_writes_evidence_and_local_lmdb_state(tmp_path: Path) -> None:
    evidence = run_e2e_harness_soak(_config(tmp_path, dry_run=False))

    assert evidence["verdict"] == "PASS"
    written = json.loads((tmp_path / "evidence.json").read_text())
    assert written == evidence
    assert evidence["steps"]["act"]["write_receipt"]["nodes_written"] == 1
    assert evidence["steps"]["receive"]["attribution_event_count"] == 1
    assert evidence["steps"]["receive"]["local_event_found"] is True
    assert evidence["steps"]["delegate"]["task_lifecycle"] == "completed"


def test_graph_mutation_guard_is_called_before_local_graph_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def fake_guard(value: bool) -> None:
        calls.append(f"guard:{value}")

    def fake_write(store: object, envelope: dict[str, object], result: object) -> dict[str, object]:
        calls.append("write")
        return {
            "edges_written": 0,
            "node_id": "node:test",
            "nodes_written": 1,
            "primitive": "assert.truth",
            "version": "test",
        }

    monkeypatch.setattr(e2e_harness_soak, "check_graph_mutation_allowed", fake_guard)
    monkeypatch.setattr(e2e_harness_soak, "write_truth_primitive_result", fake_write)

    evidence = run_e2e_harness_soak(_config(tmp_path, dry_run=False))

    assert evidence["verdict"] == "PASS"
    assert calls[:2] == ["guard:False", "write"]


def test_graph_mutation_guard_failure_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_guard(value: bool) -> None:
        raise ValueError("public_path_truth_mutation_not_authorized")

    monkeypatch.setattr(e2e_harness_soak, "check_graph_mutation_allowed", fake_guard)

    evidence = run_e2e_harness_soak(_config(tmp_path, dry_run=False))

    assert evidence["verdict"] == "FAIL"
    assert any("public_path_truth_mutation_not_authorized" in item for item in evidence["failures"])
    assert "act" not in evidence["steps"]


def test_task_coordination_transfer_remains_default_off(tmp_path: Path) -> None:
    evidence = run_e2e_harness_soak(_config(tmp_path, dry_run=False))

    assert evidence["task_coordination_transfer_enabled"] is False
    assert evidence["steps"]["delegate"]["transfer_enabled"] is False


def test_invalid_agent_id_and_epoch_are_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="e2e_harness_agent_id_invalid"):
        run_e2e_harness_soak(
            E2EHarnessSoakConfig(
                agent_id="A" * 96,
                lmdb_base_path=tmp_path / "lmdb",
                signing_key_path=Path("/dev/null"),
                epoch=1,
            )
        )
    with pytest.raises(ValueError, match="e2e_harness_epoch_invalid"):
        run_e2e_harness_soak(_config(tmp_path, epoch=True))  # type: ignore[arg-type]


def test_non_dry_run_rejects_invalid_signing_key_path(tmp_path: Path) -> None:
    evidence = run_e2e_harness_soak(
        E2EHarnessSoakConfig(
            agent_id=AGENT_ID,
            lmdb_base_path=tmp_path / "lmdb",
            signing_key_path=Path("/dev/null"),
            epoch=1,
        )
    )

    assert evidence["verdict"] == "FAIL"
    assert any("e2e_harness_signing_key_path_invalid" in item for item in evidence["failures"])


def test_cli_dry_run_prints_pass_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = e2e_harness_soak.main(
        [
            "--agent-id",
            AGENT_ID,
            "--lmdb-base-path",
            str(tmp_path / "lmdb"),
            "--signing-key-path",
            "/dev/null",
            "--epoch",
            "8",
            "--dry-run",
            "--skip-transfer",
        ]
    )

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["verdict"] == "PASS"
    assert payload["steps"]["delegate"]["task_lifecycle"] == "dry_run"


def test_source_has_no_public_network_subprocess_or_wall_clock_imports() -> None:
    source = MODULE.read_text()
    tree = ast.parse(source)
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert "subprocess" not in imported_roots
    assert "socket" not in imported_roots
    assert "requests" not in imported_roots
    assert "urllib" not in imported_roots
    assert "time" not in imported_roots
    assert "datetime" not in imported_roots


def test_json_dumps_calls_are_canonical_and_nan_rejecting() -> None:
    tree = ast.parse(MODULE.read_text())
    dumps_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "dumps"
    ]
    assert dumps_calls
    for call in dumps_calls:
        kwargs = {keyword.arg: keyword.value for keyword in call.keywords if keyword.arg is not None}
        assert isinstance(kwargs.get("sort_keys"), ast.Constant)
        assert kwargs["sort_keys"].value is True
        assert isinstance(kwargs.get("allow_nan"), ast.Constant)
        assert kwargs["allow_nan"].value is False


def test_cli_help_exposes_required_flags(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        e2e_harness_soak.parse_args(["--help"])

    assert exc.value.code == 0
    help_text = capsys.readouterr().out
    assert "--agent-id" in help_text
    assert "--lmdb-base-path" in help_text
    assert "--signing-key-path" in help_text
    assert "--epoch" in help_text
