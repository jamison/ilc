"""Contract tests for Phase 315 infrastructure economic risk monitoring update."""

from __future__ import annotations

from pathlib import Path
import subprocess


ARTIFACT_PATH = Path("docs/specs/ilc_infrastructure_economic_risk_monitoring_update_315_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PHASE_315_COMMIT_SUBJECT = "docs(g8): phase 315 infrastructure economic risk monitoring update"


def _read() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def test_artifact_exists() -> None:
    assert ARTIFACT_PATH.exists()


def test_required_sections_present() -> None:
    text = _read()
    for heading in (
        "## 1. Purpose and constitutional boundary",
        "## 2. Surface expansion from Phase 305 baseline",
        "## 3. KPI catalog update for schema/genesis/epoch surfaces",
        "## 4. Severity thresholds and Phase-316 release-gate mapping",
        "## 5. Measurement window and reporting artifacts",
        "## 6. Owner and escalation path",
        "## 7. Complexity gate carry-forward",
        "## 8. Phase-316 entry criteria lock",
        "## 9. Non-goals and canonical anchors",
    ):
        assert heading in text


def test_infrastructure_kpi_tokens_are_explicit() -> None:
    text = _read()
    for token in (
        "kpi_schema_invalid_catalog_rate",
        "kpi_schema_dependency_mismatch_rate",
        "kpi_schema_canonical_drift_rate",
        "kpi_genesis_ceremony_sequence_failure_rate",
        "kpi_genesis_dependency_mismatch_rate",
        "kpi_genesis_digest_mismatch_rate",
        "kpi_epoch_bootstrap_range_failure_rate",
        "kpi_epoch_retention_window_failure_rate",
        "kpi_epoch_dependency_mismatch_rate",
        "formula:",
    ):
        assert token in text


def test_dependency_tokens_are_explicit() -> None:
    text = _read()
    for token in (
        "d2_schema_baseline_310.v0.1",
        "genesis_state_bundle_312.v0.1",
        "epoch_snapshot_runtime_314.v0.1",
    ):
        assert token in text


def test_measurement_window_and_preflight_scope_rules_are_explicit() -> None:
    text = _read()
    for token in (
        "Measurement-window rule:",
        "for operational monitoring, denominators are per-epoch request totals per surface",
        "for Phase-316 composed preflight snapshot, denominators are scenario executions per lane",
        "`preflight_scope: true`",
        "lane denominator counts",
    ):
        assert token in text


def test_severity_and_phase_316_release_gate_mapping_are_explicit() -> None:
    text = _read()
    for token in (
        "`S0`: informational",
        "`S1`: warning",
        "`S2`: elevated risk",
        "`S3`: release-blocking",
        "Release-blocking gate for Phase 316",
        "no open `S3` indicators",
        "all open `S2` indicators require mitigation note or explicit GO override",
    ):
        assert token in text


def test_complexity_gate_tokens_are_explicit() -> None:
    text = _read()
    for token in (
        "necessity test",
        "simpler-alternative test",
        "`n_new_params`",
        "`n_new_conditionals`",
        "`n_new_cross_dependencies`",
        "`n_new_params > 2`",
        "`n_new_conditionals > 2`",
        "`n_new_cross_dependencies > 1`",
    ):
        assert token in text


def test_phase_316_entry_criteria_reference_required_runtime_suites() -> None:
    text = _read()
    for token in (
        "tests/test_d2_schema_baseline_runtime_310.py",
        "tests/test_genesis_state_bundle_runtime_312.py",
        "tests/test_epoch_snapshot_runtime_314.py",
        "tests/test_infrastructure_economic_risk_monitoring_update_315.py",
        "no open `S3` indicators",
    ):
        assert token in text


def _resolve_phase_315_commit_ref() -> str:
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
        if subject.strip() == PHASE_315_COMMIT_SUBJECT:
            return commit_hash
    raise AssertionError("phase_315_commit_not_present_in_local_history")


def test_no_decision_log_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_315_commit_ref()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    assert DECISION_LOG_PATH not in changed


def test_no_runtime_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_315_commit_ref()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_315_runtime_mutations:{forbidden}"
