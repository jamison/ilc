from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

BLOCKED_REPORT = (
    REPO
    / "docs/specs/ilc_phase_1388_cdl_048_activation_counsel_clearance_blocked_v0.1.md"
)
WALKTHROUGH = (
    REPO
    / "docs/phases/phase_1388_cdl_048_activation_counsel_clearance_blocked_walkthrough.md"
)
STATUS = REPO / "docs/phases/STATUS.md"
PLANNING_INDEX = REPO / "docs/PLANNING_INDEX.md"
SEQUENCE_LOCK = REPO / "docs/specs/ilc_phase_1369_1390_sequence_lock_v0.1.md"
WINDOW_GROUPING = REPO / "docs/specs/ilc_window_1369_1390_candidate_phase_grouping_v0.1.md"
PACKAGING_PLAN = (
    REPO / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
)
RUNTIME = REPO / "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py"
COUNSEL_SUCCESS_RECORD = REPO / "docs/specs/ilc_counsel_clearance_1388_v0.1.md"

FAIL_TOKENS = {
    "phase_1388_cdl_048_activation_failed_closed",
    "cdl_048_activation_not_performed_phase_1388",
    "counsel_clearance_public_verifier_api_missing_phase_1388",
    "first_live_value_path_activation_not_performed_phase_1388",
    "phase_1388_prompt_v0_1_gate_reference_superseded_by_v0_2_pass",
    "phase_1389_not_opened_phase_1388",
}

SUCCESS_TOKENS = {
    "cdl_048" + "_activated_phase_1388",
    "counsel_clearance_public_verifier_api" + "_phase_1388",
    "first_live_value_path" + "_activation_phase_1388",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1388_blocked_report_records_fail_closed_tokens() -> None:
    text = _read(BLOCKED_REPORT)
    for token in FAIL_TOKENS:
        assert token in text


def test_phase_1388_blocked_walkthrough_records_fail_closed_tokens() -> None:
    text = _read(WALKTHROUGH)
    for token in FAIL_TOKENS:
        assert token in text


def test_phase_1388_blocked_artifacts_do_not_record_success_tokens() -> None:
    combined = _read(BLOCKED_REPORT) + "\n" + _read(WALKTHROUGH)
    for token in SUCCESS_TOKENS:
        assert token not in combined


def test_phase_1388_success_counsel_record_supersedes_blocked_artifact_when_present() -> None:
    if COUNSEL_SUCCESS_RECORD.exists():
        text = _read(COUNSEL_SUCCESS_RECORD)
        for token in SUCCESS_TOKENS:
            assert token in text


def test_blocked_artifacts_remain_historical_and_without_success_tokens() -> None:
    text = _read(RUNTIME)
    assert 'CDL048_NOT_ACTIVATED_PHASE_1380_TOKEN = "cdl_048_not_activated_phase_1380"' in text
    assert "PUBLIC_RC_EXCLUDE" in text

    combined = _read(BLOCKED_REPORT) + "\n" + _read(WALKTHROUGH)
    for token in SUCCESS_TOKENS:
        assert token not in combined


def test_phase_1388_report_cites_superseding_1387_rerun_pass() -> None:
    text = _read(BLOCKED_REPORT)
    assert "ilc_pre_activation_hardening_gate_report_1387_v0.1.md" in text
    assert "ilc_pre_activation_hardening_gate_report_1387_rerun_v0.2.md" in text
    assert "historical failed-closed report" in text
    assert "Current Phase 1387 routing authority" in text


def test_phase_1388_report_cites_1387a_pass_evidence() -> None:
    text = _read(BLOCKED_REPORT)
    assert "ilc_accepted_adr_cdl_public_rc_coverage_matrix_1387a_v0.1.md" in text
    assert "ilc_public_economics_admission_firewall_1387a_v0.1.md" in text


def test_phase_1388_report_cites_counsel_blockers() -> None:
    text = _read(BLOCKED_REPORT)
    assert "ilc_counsel_ip_publication_clearance_inventory_1300_v0.1.md" in text
    assert "ilc_cdl_086_counsel_disposition_1220_v0.1.md" in text
    assert "counsel_publication_clearance_missing" in text
    assert "not counsel-approved legal conclusions" in text


def test_planning_surfaces_record_phase_1388_failed_closed() -> None:
    for path in (STATUS, PLANNING_INDEX, SEQUENCE_LOCK, WINDOW_GROUPING, PACKAGING_PLAN):
        text = _read(path)
        assert "phase_1388_cdl_048_activation_failed_closed" in text, path
        assert "counsel_clearance_public_verifier_api_missing_phase_1388" in text, path
        assert "phase_1389_not_opened_phase_1388" in text, path
