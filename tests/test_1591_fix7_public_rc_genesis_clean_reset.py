# SPDX-License-Identifier: AGPL-3.0-only
"""Tests for Phase 1591-Fix7 public-RC genesis clean-reset gate."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from tools.testbed import public_rc_genesis_clean_reset as reset


def _write_inputs(tmp_path: Path, *, testnet_zero: bool = False) -> tuple[Path, Path, Path]:
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(
        reset.stable_json(
            {
                "endpoint_labels": [
                    {"ssh_host": "node-a", "validator_id": 1},
                    {"ssh_host": "node-a", "validator_id": 2},
                    {"ssh_host": "node-b", "validator_id": 3},
                    {"ssh_host": "node-c", "validator_id": 4},
                ],
                "final_epoch": 8,
                "initial_epoch": 7,
            }
        ),
        encoding="utf-8",
    )
    genesis_path = tmp_path / "genesis.json"
    genesis_path.write_text(
        reset.stable_json({"epoch": 0, "network_id": "ilc-rc01"}),
        encoding="utf-8",
    )
    node_config_path = tmp_path / "node_config.toml"
    node_config_path.write_text(
        "\n".join(
            [
                '[network]',
                'network_id = "ilc-rc01"',
                '[storage]',
                'lmdb_path = "/var/lib/ilc/rc01"',
                "testnet_min_epoch_duration_ms = 0" if testnet_zero else "",
            ]
        ),
        encoding="utf-8",
    )
    return evidence_path, genesis_path, node_config_path


def test_inspect_mode_returns_non_empty_artifact_list(tmp_path: Path) -> None:
    evidence_path, _genesis_path, node_config_path = _write_inputs(tmp_path)

    report = reset.build_inspection(
        evidence_path=evidence_path,
        node_config_path=node_config_path,
    )

    assert report["status"] == "inspect_only"
    assert report["artifact_count"] > 0
    assert report["artifacts"]


def test_plan_output_contains_explicit_classification_table(tmp_path: Path) -> None:
    evidence_path, genesis_path, node_config_path = _write_inputs(tmp_path)

    plan = reset.build_plan(
        evidence_path=evidence_path,
        genesis_path=genesis_path,
        node_config_path=node_config_path,
    )

    table = plan["artifact_classification_table"]
    assert table
    assert all(
        set(row).issuperset({"path", "artifact_class", "disposition", "reason"})
        for row in table
    )


def test_no_lmdb_binary_in_preserved_artifacts(tmp_path: Path) -> None:
    evidence_path, genesis_path, node_config_path = _write_inputs(tmp_path)

    plan = reset.build_plan(
        evidence_path=evidence_path,
        genesis_path=genesis_path,
        node_config_path=node_config_path,
    )

    preserved = plan["preserved_artifacts"]
    assert not any(path.endswith("/data.mdb") for path in preserved)
    assert not any(path.endswith("/lock.mdb") for path in preserved)
    assert not any(Path(path).name in {"data.mdb", "lock.mdb"} for path in preserved)


def test_rejects_phase1591_fix_paths_as_launch_namespace_input(tmp_path: Path) -> None:
    evidence_path, genesis_path, node_config_path = _write_inputs(tmp_path)
    node_config_path.write_text(
        '[storage]\nlmdb_path = "/home/ilcops/phase1591_fix2/public/db_1"\n',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="public_rc_clean_reset_launch_namespace_reuses_phase_path"):
        reset.build_plan(
            evidence_path=evidence_path,
            genesis_path=genesis_path,
            node_config_path=node_config_path,
        )


def test_testnet_zero_rejected_before_ready_token_can_emit(tmp_path: Path) -> None:
    evidence_path, genesis_path, node_config_path = _write_inputs(tmp_path, testnet_zero=True)

    with pytest.raises(ValueError, match="public_rc_clean_reset_testnet_zero_rejected"):
        reset.build_plan(
            evidence_path=evidence_path,
            genesis_path=genesis_path,
            node_config_path=node_config_path,
        )


def test_json_style_testnet_zero_is_rejected(tmp_path: Path) -> None:
    config_path = tmp_path / "node_config.json"
    config_path.write_text(
        '{"testnet_min_epoch_duration_ms": 0, "lmdb_path": "/var/lib/ilc/rc01"}',
        encoding="utf-8",
    )

    assert reset.launch_config_has_testnet_zero(config_path) is True


def test_canonical_json_receipt_determinism(tmp_path: Path) -> None:
    evidence_path, genesis_path, node_config_path = _write_inputs(tmp_path)
    plan_a = reset.build_plan(
        evidence_path=evidence_path,
        genesis_path=genesis_path,
        node_config_path=node_config_path,
    )
    plan_b = reset.build_plan(
        evidence_path=evidence_path,
        genesis_path=genesis_path,
        node_config_path=node_config_path,
    )

    assert reset.stable_json(plan_a) == reset.stable_json(plan_b)
    assert json.loads(reset.stable_json(plan_a)) == plan_a


def test_execute_without_confirm_fails_closed(tmp_path: Path) -> None:
    evidence_path, genesis_path, node_config_path = _write_inputs(tmp_path)

    completed = subprocess.run(
        [
            sys.executable,
            "tools/testbed/public_rc_genesis_clean_reset.py",
            "execute",
            "--network",
            "public-rc",
            "--evidence-path",
            str(evidence_path),
            "--genesis-path",
            str(genesis_path),
            "--node-config-path",
            str(node_config_path),
            "--json",
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert completed.returncode != 0
    assert "public_rc_clean_reset_execute_requires_confirm" in completed.stderr


def test_stale_planning_text_detection_helper(tmp_path: Path) -> None:
    planning = tmp_path / "planning.md"
    planning.write_text(
        "All four validators currently at epoch 0, ready for public RC launch\n",
        encoding="utf-8",
    )

    findings = reset.stale_planning_claims((planning,))

    assert findings == [
        {
            "line": "1",
            "path": str(planning),
            "text": "All four validators currently at epoch 0, ready for public RC launch",
        }
    ]


def test_execute_with_confirm_returns_plan_only_blocked_status(tmp_path: Path) -> None:
    evidence_path, genesis_path, node_config_path = _write_inputs(tmp_path)
    plan = reset.build_plan(
        evidence_path=evidence_path,
        genesis_path=genesis_path,
        node_config_path=node_config_path,
    )

    refusal = reset.build_execute_refusal(plan)

    assert refusal["status"] == "blocked_plan_only"
    assert refusal["epoch0_ready_token_emit_allowed"] is False


def test_build_validator_reset_targets_from_evidence(tmp_path: Path) -> None:
    evidence_path, _genesis_path, node_config_path = _write_inputs(tmp_path)

    targets = reset.build_validator_reset_targets(
        evidence_path=evidence_path,
        node_config_path=node_config_path,
        remote_harness_dir="/home/ilcops/phase1591_fix2/public",
    )

    assert [target.validator_id for target in targets] == [1, 2, 3, 4]
    assert targets[0].old_db_dir == "/home/ilcops/phase1591_fix2/public/db_1"
    assert targets[0].fresh_validator_namespace == "/var/lib/ilc/rc01/validator_1"


def test_production_execute_passes_with_fake_runner_and_writes_pre_receipt(tmp_path: Path) -> None:
    evidence_path, genesis_path, node_config_path = _write_inputs(tmp_path)
    receipt_path = tmp_path / "reset_receipt.json"
    calls: list[tuple[str, str]] = []

    def fake_runner(host: str, script: str) -> dict[str, object]:
        calls.append((host, script))
        stdout = ""
        if "old_db_present=" in script:
            stdout = "old_db_present=no\nforbidden_count=0\nfresh_exists=yes\n"
        return {
            "argv": ["ssh", host],
            "returncode": 0,
            "stderr": "",
            "stderr_truncated": False,
            "stdout": stdout,
            "stdout_truncated": False,
        }

    result = reset.build_live_execution(
        evidence_path=evidence_path,
        genesis_path=genesis_path,
        node_config_path=node_config_path,
        no_interactive=True,
        receipt_path=receipt_path,
        command_runner=fake_runner,
    )

    assert result["status"] == "pass"
    assert result["epoch0_ready_token_emit_allowed"] is True
    assert result["epoch0_ready_token"] == reset.OUTPUT_TOKEN
    assert len(calls) == 12
    pre_path = tmp_path / "reset_receipt.pre_deletion.json"
    assert pre_path.exists()
    assert json.loads(pre_path.read_text(encoding="utf-8"))["status"] == "pre_deletion_receipt_written"


def test_production_execute_withholds_ready_token_when_readback_fails(tmp_path: Path) -> None:
    evidence_path, genesis_path, node_config_path = _write_inputs(tmp_path)

    def fake_runner(_host: str, script: str) -> dict[str, object]:
        stdout = ""
        if "old_db_present=" in script:
            stdout = "old_db_present=yes\nforbidden_count=1\nfresh_exists=yes\n"
        return {
            "argv": ["ssh"],
            "returncode": 0,
            "stderr": "",
            "stderr_truncated": False,
            "stdout": stdout,
            "stdout_truncated": False,
        }

    result = reset.build_live_execution(
        evidence_path=evidence_path,
        genesis_path=genesis_path,
        node_config_path=node_config_path,
        no_interactive=True,
        command_runner=fake_runner,
    )

    assert result["status"] == "fail_closed"
    assert result["epoch0_ready_token_emit_allowed"] is False
    assert result["epoch0_ready_token"] is None


def test_remote_path_guard_rejects_relative_and_forbidden_components() -> None:
    with pytest.raises(ValueError, match="public_rc_clean_reset_remote_path_not_absolute"):
        reset._assert_under_allowed_root("relative/db_1", ("/home/ilcops/phase1591_fix2/public",))
    with pytest.raises(ValueError, match="public_rc_clean_reset_remote_path_forbidden_component"):
        reset._assert_under_allowed_root(
            "/home/ilcops/genesis/db_1",
            ("/home/ilcops/phase1591_fix2/public",),
        )


def test_remote_path_guard_rejects_outside_allowed_namespace() -> None:
    with pytest.raises(ValueError, match="public_rc_clean_reset_remote_path_outside_allowed_namespace"):
        reset._assert_under_allowed_root(
            "/home/ilcops/other/db_1",
            ("/home/ilcops/phase1591_fix2/public",),
        )
