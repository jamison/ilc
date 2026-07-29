import json
from decimal import Decimal
from pathlib import Path

from ilc_core.economics.epoch_attribution_settle_runtime import (
    PASSIVE_ECU_WIRING_NOT_ACTIVATED,
    AttributionEvent,
)
from ilc_core.types import (
    EDGE_MINT_PHI_BOUND,
    PROVENANCE_DECAY_ALPHA,
    PROVENANCE_MAX_DEPTH,
    REUSE_ATTRIBUTION_RATE,
    EdgeType,
    EpochAttributionBatch,
)


SPEC = Path(
    "docs/specs/ilc_ecu_backward_attribution_canon_reconciliation_GAP_ECU_00_v0.1.md"
)
WALKTHROUGH = Path("docs/phases/phase_gap_ecu_00_ecu_canon_reconciliation_walkthrough.md")
STATUS = Path("docs/phases/STATUS.md")
LEDGER = Path("docs/specs/ilc_fix38_manual_edge_annotation_ledger_v0.1.json")


def _status_block(heading: str) -> str:
    status = STATUS.read_text(encoding="utf-8")
    return status.split(heading, 1)[1].split("\n### ", 1)[0]


def test_gap_ecu_00_spec_contains_patent_and_gate_boundaries():
    text = SPEC.read_text(encoding="utf-8")
    assert "64/231,846" in text
    assert "official_written_filing_receipts_received = False" in text
    assert "public_path_remains_blocked = True" in text
    assert "public disclosure gate remains in force" in text
    assert "does not authorize public disclosure" in text


def test_gap_ecu_00_spec_lists_exact_nine_backward_attribution_surfaces():
    text = SPEC.read_text(encoding="utf-8")
    expected = [
        "Triggering events",
        "Eligible upstream artifacts",
        "Typed path semantics",
        "Provenance-distance score",
        "Decay rule",
        "Bidirectional coefficients",
        "Depth and dominance bounds",
        "Refutation interaction",
        "Audit surface",
    ]
    for item in expected:
        assert item in text
    section = text.split("## 4. Nine Open Backward-Attribution CDL Parameter Surfaces", 1)[1]
    section = section.split("## 5. Public Claim Audit", 1)[0]
    assert section.count("| ") >= 10
    assert "The count from Phase 1492p section 3.1 is exactly nine." in section


def test_gap_ecu_00_spec_preserves_live_vs_unimplemented_boundary():
    text = SPEC.read_text(encoding="utf-8")
    assert "Current live `ProtocolECU` settlement supports REUSE" in text
    assert "implemented by `settle_attribution_batch()`" in text
    assert "`AttributionEvent` objects" in text
    assert "Full backward attribution" in text
    assert "Not implemented" in text or "not implemented" in text
    assert "No CDL opened yet" in text
    assert "GAP-ECU-06" in text


def test_gap_ecu_00_node_value_kernel_is_not_settlement_formula():
    text = SPEC.read_text(encoding="utf-8")
    assert "`node_value_kernel.py` is not the ECU settlement formula." in text
    assert "not imported by `epoch_attribution_settle_runtime.py`" in text
    assert "ilc_core/analysis/node_value_kernel.py" in text


def test_gap_ecu_00_cdl083_cdl084_no_double_pay_constraint_recorded():
    text = SPEC.read_text(encoding="utf-8")
    assert "CDL-083 REFUTATION remains valid" in text
    assert "CDL-084 PROVENANCE remains valid" in text
    assert "no-double-pay requirement" in text
    assert "PROVENANCE_DECAY_ALPHA = Decimal(\"0.45\")" in text
    assert "PROVENANCE_MAX_DEPTH = 3" in text
    assert "EDGE_MINT_PHI_BOUND" in text
    assert "provenance_events_processed / epoch_node_mint_count >= 0.60" in text


def test_gap_ecu_00_runtime_constants_are_source_verified():
    assert PROVENANCE_DECAY_ALPHA == Decimal("0.45")
    assert PROVENANCE_MAX_DEPTH == 3
    assert EDGE_MINT_PHI_BOUND == Decimal("0.60")
    assert REUSE_ATTRIBUTION_RATE == Decimal("0.20")
    assert PASSIVE_ECU_WIRING_NOT_ACTIVATED is False


def test_gap_ecu_00_passive_ecu_requires_star_node_id_even_when_guard_active():
    no_star_batch = EpochAttributionBatch(epoch=1)
    no_star_batch.add_event(
        AttributionEvent(
            edge_type=EdgeType.REUSE,
            target_creator_id="agent_a",
            star_node_id=None,
            epoch=1,
        )
    )
    no_star_batch.seal()
    assert no_star_batch.settle(
        stake_map={},
        passive_ecu_centrality_state={"star_a": Decimal("0.10")},
    ) == [("agent_a", Decimal("0.20"))]

    with_star_batch = EpochAttributionBatch(epoch=1)
    with_star_batch.add_event(
        AttributionEvent(
            edge_type=EdgeType.REUSE,
            target_creator_id="agent_a",
            star_node_id="star_a",
            epoch=1,
        )
    )
    with_star_batch.seal()
    assert with_star_batch.settle(
        stake_map={},
        passive_ecu_centrality_state={"star_a": Decimal("0.10")},
    ) == [
        ("agent_a", Decimal("0.20")),
        ("agent_a", Decimal("0.004000000000")),
    ]


def test_gap_ecu_00_provenance_phi_bound_suppresses_payout_after_threshold():
    batch = EpochAttributionBatch(epoch=1)
    for event_id in ("a", "b"):
        batch.add_event(
            AttributionEvent(
                edge_type=EdgeType.PROVENANCE,
                target_creator_id=f"target_{event_id}",
                star_node_id=None,
                epoch=1,
                provenance_chain=((f"node_{event_id}", f"creator_{event_id}"),),
            )
        )
    batch.seal()

    emitted_tokens: list[str] = []
    payouts = batch.settle(
        stake_map={},
        emitted_tokens=emitted_tokens,
        epoch_node_mint_count=1,
    )

    assert payouts == [("creator_a", Decimal("0.090000000"))]
    assert emitted_tokens == ["edge_mint_phi_bound_exceeded"]


def test_gap_ecu_00_status_and_walkthrough_tokens():
    block = _status_block("### Phase GAP-ECU-00")
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")
    token = "ecu_canon_reconciliation_committed_GAP_ECU_00"
    assert token in block
    assert token in walkthrough
    assert "no runtime\ncode was changed" in block
    assert "This phase did not open a CDL" in walkthrough


def test_gap_ecu_00_fix1_ledger_taxonomy_and_load_bearing_justification():
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    by_path = {
        entry.get("repo_path"): entry for entry in data.get("annotations", [])
    }
    for test_path in [
        "tests/test_phase_1589b_cdl106_opening.py",
        "tests/test_gap_ecu_00_canon_reconciliation.py",
        "tests/test_gap_ecu_01a_sim_contract.py",
    ]:
        assert by_path[test_path]["node_kind"] == "test_file"

    gap_ecu_00 = by_path[
        "docs/specs/ilc_ecu_backward_attribution_canon_reconciliation_GAP_ECU_00_v0.1.md"
    ]
    assert gap_ecu_00["recommended_graph_action"].startswith(
        "load_bearing_artifact_added:"
    )
    assert "pre-RC sequencing gate for the GAP-ECU backward-attribution lane" in (
        gap_ecu_00["manual_read_summary"]
    )
