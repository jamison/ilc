from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/specs/ilc_final_deterministic_code_security_audit_1332_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1332_final_deterministic_code_security_audit_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
WINDOW_GROUPING = ROOT / "docs/specs/ilc_window_1330_1342_candidate_phase_grouping_v0.1.md"


REQUIRED_TOKENS = (
    "final_deterministic_code_security_audit_phase_1332.v0.1",
    "runtime_guardrail_scope_revalidated_phase_1332",
    "canonical_json_security_sweep_recorded_phase_1332",
    "release_blocker_audit_no_activation_phase_1332",
    "phase_1333_source_allowlist_export_execution_gate_next",
    "public_rc_remains_blocked_after_phase_1332",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1332_report_records_required_tokens_and_blocked_next_gate() -> None:
    text = _read(REPORT)
    for token in REQUIRED_TOKENS:
        assert token in text

    assert "phase_1333_status=blocked_pending_fix4_before_phase_1333" in text
    assert "fix4_private_address_denial_cbor_size_cap_required_before_phase_1333" in text
    assert "release_blocker_audit_no_activation_phase_1332" in text


def test_phase_1332_report_records_closed_and_open_findings() -> None:
    text = _read(REPORT)
    for closed in (
        "CCSS-001 missing pre-serialization byte budget and integer guard",
        "bootstrap signature env-var bypass",
        "CDL-069 identity seed commitment mismatch",
        "economics entropy/reward/exact numeric float chain",
        "unsafe `read_bundle()` materialization",
    ):
        assert closed in text

    for open_item in (
        "Private-address SSRF denial is not enforced",
        "CBOR decode has no pre-load size cap",
        "`test_code_health.py` still fails",
        "`reputation.py` uses floats",
    ):
        assert open_item in text


def test_phase_1332_walkthrough_status_and_index_are_backfilled() -> None:
    for path in (WALKTHROUGH, STATUS, PLANNING_INDEX, WINDOW_GROUPING):
        text = _read(path)
        assert "final_deterministic_code_security_audit_phase_1332.v0.1" in text
        assert "public_rc_remains_blocked_after_phase_1332" in text

    status = _read(STATUS)
    assert "## Phase 1332" in status
    assert "Phase 1332 Fix4" in status


def test_phase_1332_records_graph_delta_and_non_authorization() -> None:
    text = _read(REPORT) + "\n" + _read(WALKTHROUGH)
    assert (
        "graph_delta=support_only:docs/specs/"
        "ilc_final_deterministic_code_security_audit_1332_v0.1.md -> planning/frontier"
    ) in text
    assert "source allowlist export" in text
    assert "release artifact production" in text
    assert "CDL-088" in text
