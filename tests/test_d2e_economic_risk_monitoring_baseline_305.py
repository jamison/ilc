"""Contract tests for Phase 305 D2e economic risk monitoring baseline."""

from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_d2e_economic_risk_monitoring_baseline_305_v0.1.md")


def _read() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def test_artifact_exists() -> None:
    assert ARTIFACT_PATH.exists()


def test_required_sections_present() -> None:
    text = _read()
    for heading in (
        "## 1. Purpose and constitutional boundary",
        "## 2. Monitoring planes mapped to D2e surfaces",
        "## 3. KPI catalog and formula definitions",
        "## 4. Severity thresholds and release gates",
        "## 5. Cadence and reporting artifacts",
        "## 6. Owner and escalation path",
        "## 7. Complexity gate (mandatory)",
        "## 8. Phase-306 entry criteria lock",
        "## 9. Non-goals",
    ):
        assert heading in text


def test_query_verify_bundle_kpi_tokens_and_formulas_are_explicit() -> None:
    text = _read()
    for token in (
        "kpi_query_invalid_input_rate",
        "kpi_query_not_found_rate",
        "kpi_query_backend_unavailable_rate",
        "kpi_verify_invalid_input_rate",
        "kpi_verify_not_found_rate",
        "kpi_verify_backend_unavailable_rate",
        "kpi_verify_check_failure_ratio",
        "kpi_bundle_invalid_input_rate",
        "kpi_bundle_not_found_rate",
        "kpi_bundle_manifest_invalid_rate",
        "kpi_bundle_provider_blocked_rate",
        "kpi_bundle_backend_unavailable_rate",
        "kpi_bundle_validate_local_ref_missing_rate",
        "formula:",
        "unit:",
    ):
        assert token in text


def test_measurement_window_and_preflight_scope_rules_are_explicit() -> None:
    text = _read()
    for token in (
        "Measurement-window rule:",
        "for operational monitoring, denominators are per-epoch request/check totals",
        "for Phase-306 composed preflight snapshot, denominators are scenario executions per lane",
        "`preflight_scope: true`",
        "lane denominator counts",
    ):
        assert token in text


def test_governance_operational_and_narrative_plane_kpis_are_explicit() -> None:
    text = _read()
    for token in (
        "kpi_out_of_scope_file_mutation_count",
        "kpi_missing_evidence_anchor_count",
        "kpi_non_target_guardrail_failure_count",
        "kpi_local_state_path_failure_rate",
        "kpi_provider_blocked_recovery_ratio",
        "kpi_runbook_recency_days",
        "kpi_utility_framing_coverage",
        "kpi_macro_hedge_claim_incidents",
        "kpi_vendor_lock_language_incidents",
    ):
        assert token in text


def test_severity_levels_and_release_blockers_are_explicit() -> None:
    text = _read()
    for token in (
        "`S0`: informational",
        "`S1`: warning",
        "`S2`: elevated risk",
        "`S3`: release-blocking",
        "Release-blocking gate for Phase 306",
        "no `S3` indicators may be open",
        "all `S2` indicators require documented mitigation or explicit GO override",
        "kpi_query_invalid_input_rate > 0.10",
        "kpi_query_not_found_rate > 0.20",
    ):
        assert token in text


def test_cadence_and_reporting_paths_are_explicit() -> None:
    text = _read()
    for token in (
        "per-epoch snapshot",
        "per-phase summary",
        "per-window consolidated rollup",
        "out/monitoring/d2e_risk_snapshot_phase_<phase>.json",
        "docs/specs/ilc_d2e_risk_monitoring_rollup_298_307_v0.1.md",
        "docs/phases/phase_<phase>_..._walkthrough.md",
        "Required snapshot metadata fields:",
        "`preflight_scope`",
        "`lane_request_counts`",
        "`severity_summary`",
    ):
        assert token in text


def test_owner_and_escalation_mapping_is_explicit() -> None:
    text = _read()
    for token in (
        "`S0`: phase executor records KPI in phase walkthrough",
        "`S1`: phase executor + reviewer",
        "`S2`: escalate to architecture/governance review",
        "`S3`: immediate execution freeze",
        "indicator name",
        "threshold breached",
        "mitigation plan",
    ):
        assert token in text


def test_complexity_gate_fields_are_explicit() -> None:
    text = _read()
    for token in (
        "Necessity test",
        "Simpler-alternative test",
        "`n_new_params`",
        "`n_new_conditionals`",
        "`n_new_cross_dependencies`",
        "`n_new_params > 2`",
        "`n_new_conditionals > 2`",
        "`n_new_cross_dependencies > 1`",
    ):
        assert token in text


def test_phase_306_entry_criteria_references_required_regression_suites() -> None:
    text = _read()
    for token in (
        "tests/test_d2e_05_query_subsystem_300.py",
        "tests/test_d2e_06_verify_subsystem_302.py",
        "tests/test_d2e_07_bundle_subsystem_304.py",
        "no open `S3` indicators",
    ):
        assert token in text


def test_non_goals_protect_runtime_and_decision_log_boundaries() -> None:
    text = _read()
    for token in (
        "mutate CDL rows",
        "require any third-party monitoring provider",
        "implement runtime telemetry collectors in this phase",
        "no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`",
        "no runtime implementation changes under `ilc_core/`",
    ):
        assert token in text
