"""Phase 316 tests for composed schema/genesis/epoch infrastructure preflight."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from ilc_core.epoch import EPOCH_SNAPSHOT_RUNTIME_VERSION
from ilc_core.genesis import GENESIS_BUNDLE_RUNTIME_VERSION
from ilc_core.schema import SCHEMA_BASELINE_VERSION


GATE_CMD = ["bash", "tools/check_infrastructure_composed_preflight_phase_316.sh"]
SNAPSHOT_PATH = Path("out/monitoring/infrastructure_risk_snapshot_phase_316.json")
D2E_BASELINE_PATH = Path("out/monitoring/d2e_risk_snapshot_phase_306.json")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PHASE_316_COMMIT_SUBJECT = "feat(g8): phase 316 infrastructure composed preflight schema-genesis-epoch"


def _run_gate(args: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(GATE_CMD + args, capture_output=True, text=True, env=env, check=False)


def _resolve_phase_316_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_316_COMMIT_SUBJECT:
            return commit_hash
    raise AssertionError("phase_316_commit_not_present_in_local_history")


def test_gate_cli_contract_dry_run_help_unknown_arg() -> None:
    help_result = _run_gate(["--help"])
    assert help_result.returncode == 0
    assert "Usage:" in help_result.stdout

    dry_run = _run_gate(["--dry-run"])
    assert dry_run.returncode == 0
    lines = [line.strip() for line in dry_run.stdout.splitlines() if line.strip()]
    assert lines == [
        "[1/5] schema_lane_scenarios",
        "[2/5] genesis_lane_scenarios",
        "[3/5] epoch_lane_scenarios",
        "[4/5] cross_lane_dependency_regression",
        "[5/5] kpi_snapshot",
    ]

    unknown = _run_gate(["--unknown-arg"])
    assert unknown.returncode == 2


def test_gate_full_run_emits_snapshot_metadata_and_kpis() -> None:
    result = _run_gate([])
    assert result.returncode == 0
    assert SNAPSHOT_PATH.exists()

    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    assert snapshot["phase"] == "316"
    assert snapshot["preflight_scope"] is True
    assert snapshot["generated_at"].endswith("Z")
    assert snapshot["categories"] == [
        "schema_lane_scenarios",
        "genesis_lane_scenarios",
        "epoch_lane_scenarios",
        "cross_lane_dependency_regression",
        "kpi_snapshot",
    ]

    counts = snapshot["lane_request_counts"]
    assert set(counts.keys()) == {"schema", "genesis", "epoch"}
    assert counts["schema"] > 0
    assert counts["genesis"] > 0
    assert counts["epoch"] > 0

    kpis = snapshot["kpis"]
    expected_kpi_keys = {
        "kpi_schema_invalid_catalog_rate",
        "kpi_schema_dependency_mismatch_rate",
        "kpi_schema_canonical_drift_rate",
        "kpi_genesis_ceremony_sequence_failure_rate",
        "kpi_genesis_dependency_mismatch_rate",
        "kpi_genesis_digest_mismatch_rate",
        "kpi_epoch_bootstrap_range_failure_rate",
        "kpi_epoch_retention_window_failure_rate",
        "kpi_epoch_dependency_mismatch_rate",
        "kpi_out_of_scope_file_mutation_count",
        "kpi_decision_log_mutation_count",
    }
    assert set(kpis.keys()) == expected_kpi_keys

    summary = snapshot["severity_summary"]
    assert summary["verdict"] in {"pass", "conditional", "blocked"}
    if summary["s3_indicators"]:
        assert summary["verdict"] == "blocked"
    elif summary["s2_indicators"]:
        assert summary["verdict"] == "conditional"
    else:
        assert summary["verdict"] == "pass"

    baseline = snapshot["baseline_reference"]
    assert baseline["path"] == str(D2E_BASELINE_PATH)
    assert baseline["phase"] == "306"
    assert baseline["preflight_scope"] is True


def test_conditional_and_blocked_simulation_use_snapshot_override_path(tmp_path: Path) -> None:
    canonical_before = SNAPSHOT_PATH.read_bytes() if SNAPSHOT_PATH.exists() else None

    conditional_path = tmp_path / "snapshot_conditional.json"
    env_conditional = os.environ.copy()
    env_conditional["ILC_PHASE_316_SNAPSHOT_PATH"] = str(conditional_path)
    env_conditional["ILC_PHASE_316_FORCE_VERDICT"] = "conditional"

    result_conditional = _run_gate([], env=env_conditional)
    assert result_conditional.returncode == 0
    conditional = json.loads(conditional_path.read_text(encoding="utf-8"))
    assert conditional["severity_summary"]["verdict"] == "conditional"

    blocked_path = tmp_path / "snapshot_blocked.json"
    env_blocked = os.environ.copy()
    env_blocked["ILC_PHASE_316_SNAPSHOT_PATH"] = str(blocked_path)
    env_blocked["ILC_PHASE_316_FORCE_VERDICT"] = "blocked"

    result_blocked = _run_gate([], env=env_blocked)
    assert result_blocked.returncode == 0
    blocked = json.loads(blocked_path.read_text(encoding="utf-8"))
    assert blocked["severity_summary"]["verdict"] == "blocked"

    if canonical_before is not None:
        assert SNAPSHOT_PATH.read_bytes() == canonical_before


def test_runtime_dependency_tokens_remain_unchanged() -> None:
    assert SCHEMA_BASELINE_VERSION == "d2_schema_baseline_310.v0.1"
    assert GENESIS_BUNDLE_RUNTIME_VERSION == "genesis_state_bundle_312.v0.1"
    assert EPOCH_SNAPSHOT_RUNTIME_VERSION == "epoch_snapshot_runtime_314.v0.1"


def test_no_decision_log_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_316_commit_ref()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    assert DECISION_LOG_PATH not in changed


def test_no_runtime_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_316_commit_ref()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_316_runtime_mutations:{forbidden}"
