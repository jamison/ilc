# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1575a economic soft-RC rehearsal tests."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = REPO_ROOT / "tools/phase_1575a_economic_soft_rc_rehearsal_runner.py"


def _load_runner():
    spec = importlib.util.spec_from_file_location("phase_1575a_runner", RUNNER_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_phase_1575a_runner_builds_deterministic_candidate_evidence() -> None:
    runner = _load_runner()
    first = runner.build_evidence()
    second = runner.build_evidence()
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["namespace"] == "block6_economic_soft_rc_production_candidate_1575a"
    assert first["settlement_root_deterministic_replay"] is True
    assert first["epoch_0_to_1_transition"] == "blocked"
    assert first["production_candidate_retained"] is True
    assert all(value is True for value in first["pre_guard_snapshot"].values())
    assert all(value is True for value in first["post_guard_snapshot"].values())


def test_phase_1575a_runner_rows_cover_activation_matrix_surfaces() -> None:
    runner = _load_runner()
    rows = runner.build_evidence()["rows"]
    assert set(rows) == {
        "conversion",
        "ejected_stake",
        "emission",
        "productive_ecu_bounty",
        "treasury_validator_reward",
        "validator_admission_ejection",
    }
    assert rows["emission"]["production_activated"] is False
    assert rows["validator_admission_ejection"]["production_activated"] is False
    assert rows["treasury_validator_reward"]["production_activated"] is False
    assert rows["ejected_stake"]["production_activated"] is False
    assert rows["productive_ecu_bounty"]["production_activated"] is False
    assert rows["conversion"]["public_helper_exported"] is False


def test_phase_1575a_runner_cli_writes_json_evidence(tmp_path: Path) -> None:
    evidence_path = tmp_path / "evidence.json"
    subprocess.run(
        [sys.executable, str(RUNNER_PATH), "--json-out", str(evidence_path)],
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["disposition"] == "freeze_retain_candidate_pending_human_review"
    assert evidence["rows"]["emission"]["settlement_root_hex"]
