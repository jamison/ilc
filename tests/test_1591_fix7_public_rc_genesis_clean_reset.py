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
                    {"validator_id": 1},
                    {"validator_id": 2},
                    {"validator_id": 3},
                    {"validator_id": 4},
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
