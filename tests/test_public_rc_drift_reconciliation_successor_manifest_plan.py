from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_reconciliation_plan_records_phase_1447_as_complete_not_pending() -> None:
    text = _read(
        "docs/specs/"
        "ilc_public_rc_drift_reconciliation_and_successor_manifest_plan_v0.1.md"
    )

    assert "public_rc_drift_reconciliation_successor_manifest_plan_committed_2026_06_11" in text
    assert "phase_1447_complete_historical_not_pending" in text
    assert "Phase 1446" in text
    assert "Phase 1447" in text
    assert "COMPLETE" in text
    assert "Public repository publication" in text
    assert "NOT PERFORMED" in text


def test_reconciliation_plan_routes_successor_manifest_before_public_gate() -> None:
    text = _read(
        "docs/specs/"
        "ilc_public_rc_drift_reconciliation_and_successor_manifest_plan_v0.1.md"
    )

    assert "fix6_fix7_required_before_fix8_forward" in text
    assert "successor_manifest_target_v03_clean_or_v04_deferred_to_fix7" in text
    assert "v0.3_clean" in text
    assert "v0.4_candidate_required" in text
    assert "Block 6" in text
    assert "PUBLIC-RC-GATE-001" in text
    assert "public_rc_publication_gate_remains_blocked_pending_block6" in text


def test_reconciliation_plan_records_governance_routing_boundary() -> None:
    text = _read(
        "docs/specs/"
        "ilc_public_rc_drift_reconciliation_and_successor_manifest_plan_v0.1.md"
    )

    assert "ADR is required" in text
    assert "CDL is required" in text
    assert "protocol architecture rule" in text
    assert "constitutional authority" in text
    assert "credit or reward eligibility" in text
    assert "runtime gate clearance" in text


def test_fix6_and_fix7_consume_reconciliation_anchor() -> None:
    fix6 = _read(
        "docs/antigravity_tasks/"
        "antigravity_prompt__phase_1545p_fix6_g10_genesis_v03_methodology_preservation.md"
    )
    fix7 = _read(
        "docs/antigravity_tasks/"
        "antigravity_prompt__phase_1545p_fix7_g10_genesis_common_registry_node_candidate_audit.md"
    )

    for prompt in (fix6, fix7):
        assert "ilc_public_rc_drift_reconciliation_and_successor_manifest_plan_v0.1.md" in prompt
        assert "public_rc_drift_reconciliation_successor_manifest_plan_committed_2026_06_11" in prompt
        assert "phase_1447_complete_historical_not_pending" in prompt

    assert "public_rc_drift_reconciliation_anchor_consumed_phase_1545p_fix6" in fix6
    assert "public_rc_drift_reconciliation_anchor_consumed_phase_1545p_fix7" in fix7

