from pathlib import Path


REPO = Path(__file__).resolve().parents[1]

REPORT_V1 = REPO / "docs/specs/ilc_public_claimability_activation_gate_report_1389_v0.1.md"
REPORT_V2 = REPO / "docs/specs/ilc_public_claimability_activation_gate_report_1389_rerun_v0.2.md"
WALKTHROUGH = REPO / "docs/phases/phase_1389_public_claimability_activation_gate_rerun_walkthrough.md"
VERIFIER = REPO / "ilc_core/sidecars/claimability_receipt_verifier.py"
REGISTRY = REPO / "ilc_core/sidecars/claim_nullifier_registry_v1.py"
STATUS = REPO / "docs/phases/STATUS.md"
PLANNING_INDEX = REPO / "docs/PLANNING_INDEX.md"
SEQUENCE_LOCK = REPO / "docs/specs/ilc_phase_1369_1390_sequence_lock_v0.1.md"
WINDOW_GROUPING = REPO / "docs/specs/ilc_window_1369_1390_candidate_phase_grouping_v0.1.md"


PASS_TOKENS = (
    "public_claimability_gate_phase_1389_executed",
    "result=public_claimability_activated",
    "public_claimability_gate_rerun_passed_after_1389b",
    "claimability_runtime_public_mode_blockers_cleared_phase_1389_rerun",
    "phase_1389_v0_1_failed_closed_superseded_by_v0_2_pass",
)

BLOCKER_CLOSURE_TOKENS = (
    "cdl_088_is_public_claimability_api_authority_phase_1389a",
    "public_safe_disclosure_schema_final_cdl_088_scope_phase_1389a",
    "transport_principal_resolved_at_d2d_layer_adr_0039_cdl_078_phase_1389a",
    "claim_nullifier_registry_v1_active_phase_1389b",
    "duplicate_claim_registry_active_phase_1389b",
    "public_mode_blockers_empty_phase_1389b",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1389_rerun_report_records_pass_tokens() -> None:
    text = _read(REPORT_V2)
    for token in PASS_TOKENS:
        assert token in text
    assert "FAILED CLOSED" not in text


def test_phase_1389_v1_failure_preserved_as_historical_evidence() -> None:
    text = _read(REPORT_V1)
    assert "public_claimability_gate_failed_phase_1389" in text
    assert "claimability_runtime_public_mode_blockers_still_active_phase_1389" in text


def test_phase_1389_rerun_report_lists_all_closure_tokens() -> None:
    text = _read(REPORT_V2) + "\n" + _read(WALKTHROUGH)
    for token in BLOCKER_CLOSURE_TOKENS:
        assert token in text


def test_claimability_verifier_public_mode_blockers_are_empty() -> None:
    text = _read(VERIFIER)
    assert "_PUBLIC_MODE_BLOCKERS: tuple[str, ...] = ()" in text
    assert '"public_mode_blockers": list(_PUBLIC_MODE_BLOCKERS)' in text


def test_claimability_runtime_registry_tokens_exist() -> None:
    text = _read(REGISTRY) + "\n" + _read(VERIFIER)
    assert "claim_nullifier_registry_v1_active_phase_1389b" in text
    assert "duplicate_claim_registry_active_phase_1389b" in text
    assert "claimability_verifier_public_mode_ready_phase_1389b" in text


def test_phase_1389_rerun_planning_surfaces_record_pass() -> None:
    combined = "\n".join(
        _read(path)
        for path in (
            STATUS,
            PLANNING_INDEX,
            SEQUENCE_LOCK,
            WINDOW_GROUPING,
        )
    )
    for token in PASS_TOKENS:
        assert token in combined
    assert "Phase 1390 window closure" in combined
