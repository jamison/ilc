from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SPEC = ROOT / "docs/specs/ilc_soft_rc_gate_rerun_1426_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1426_soft_rc_gate_rerun_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1399_1428_sequence_lock_v0.1.md"
MANIFEST_SCHEMA = ROOT / "docs/specs/ilc_launch_readiness_manifest_schema_1422_v0.1.md"

REQUIRED_TOKENS = (
    "soft_rc_gate_rerun_phase_1426",
    "soft_rc_eligible=true_phase_1426",
    "phase_1366_soft_rc_deferred_gate_now_closed_phase_1426",
    "soft_rc_eligible_true_not_public_rc_activated_phase_1426",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1426_report_exists_and_records_required_tokens() -> None:
    text = _read(SPEC)
    for token in REQUIRED_TOKENS:
        assert token in text
    assert "soft_rc_eligible=true" in text
    assert "soft_rc_eligible=false_with_blockers" in text


def test_phase_1426_report_records_blocker_closure_evidence() -> None:
    text = _read(SPEC)
    assert "phase_1366_treasury_epoch_budget_binding_unverified" in text
    assert "phase_1366_treasury_epoch_budget_binding_verified" in text
    assert "build_epoch_emission_quote" in text
    assert "capped_epoch_budget_ilc" in text
    assert "No new soft-RC gate blocker was found" in text


def test_phase_1426_report_preserves_non_authorization_boundary() -> None:
    text = _read(SPEC)
    for phrase in (
        "does not authorize public RC publication",
        "activation-certificate signing",
        "epoch 0-to-1 transition",
        "production jury assignment",
        "live ECU distribution",
        "ledger write",
        "wallet write",
        "CDL mutation",
        "Genesis signing",
    ):
        assert phrase in text


def test_launch_manifest_schema_remains_unsigned_template() -> None:
    text = _read(MANIFEST_SCHEMA)
    assert '"epoch_0_to_1_transition_authorized": false' in text
    assert '"manifest_content_hash": null' in text
    assert '"manifest_signature": null' in text
    assert '"status": "pending_phase_1426_rerun"' in text


def test_walkthrough_status_and_planning_are_backfilled() -> None:
    combined = "\n".join(
        _read(path) for path in (WALKTHROUGH, STATUS, PLANNING_INDEX, SEQUENCE_LOCK)
    )
    for token in REQUIRED_TOKENS:
        assert token in combined
    assert "Phase 1426" in combined
    assert "Phase 1427" in combined
    assert "SENSITIVE" in combined


def test_sequence_lock_marks_phase_1426_complete_and_phase_1427_next() -> None:
    text = _read(SEQUENCE_LOCK)
    assert "Phase 1426 soft-RC gate re-run complete" in text
    assert "Phase 1427 J-008 gate re-run is next and SENSITIVE" in text
    assert "`soft_rc_eligible=true`" in text
