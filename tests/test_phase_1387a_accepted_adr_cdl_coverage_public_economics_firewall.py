from __future__ import annotations

from pathlib import Path

import pytest

from ilc_core.ledger.public_economics_admission_firewall import (
    PRIVATE_VISIBILITY_EXCLUSION_TOKEN,
    PUBLIC_ECONOMIC_EVENT_TYPES,
    PublicEconomicsAdmissionError,
    build_public_economic_event,
)
from ilc_core.node.promotion_continuity_runtime_364 import (
    generate_promotion_continuity_record,
)


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs/specs/ilc_accepted_adr_cdl_public_rc_coverage_matrix_1387a_v0.1.md"
FIREWALL = ROOT / "docs/specs/ilc_public_economics_admission_firewall_1387a_v0.1.md"
WALKTHROUGH = (
    ROOT
    / "docs/phases/phase_1387a_accepted_adr_cdl_coverage_public_economics_firewall_walkthrough.md"
)


def public_node(**overrides):
    node = {
        "node_id": "bafy-public-1387a",
        "visibility": "public",
        "eligible_public_state": "public_evaluated",
        "public_graph_admission_evidence": {
            "admission_id": "admit-1387a",
            "admitted_epoch": 1387,
            "admission_proof_sha256": "a" * 64,
            "public_graph_root": "root-public-1387a",
        },
    }
    node.update(overrides)
    return node


def assert_rejects(node, event_type="public_ecu", token: str | None = None):
    with pytest.raises(PublicEconomicsAdmissionError) as exc:
        build_public_economic_event(event_type=event_type, source_node=node, payload={})
    if token is not None:
        assert exc.value.token == token


def test_public_node_can_construct_each_public_economic_event_type():
    for event_type in sorted(PUBLIC_ECONOMIC_EVENT_TYPES):
        event = build_public_economic_event(
            event_type=event_type,
            source_node=public_node(),
            payload={"amount_minor_units": "0"},
        )
        assert event["event_type"] == event_type
        assert len(event["event_sha256"]) == 64
        assert event["source"]["visibility"] == "public"
        assert event["source"]["public_graph_admission_evidence"]["admitted_epoch"] == 1387


def test_private_and_semi_private_visibility_rejected():
    assert_rejects(
        public_node(visibility="private"),
        token=PRIVATE_VISIBILITY_EXCLUSION_TOKEN,
    )
    assert_rejects(
        public_node(visibility="semi-private"),
        token=PRIVATE_VISIBILITY_EXCLUSION_TOKEN,
    )


def test_missing_public_graph_admission_evidence_rejected():
    assert_rejects(
        public_node(public_graph_admission_evidence=None),
        token="public_graph_admission_evidence_missing_phase_1387a",
    )


def test_caller_supplied_public_boolean_is_not_admission_evidence():
    node = public_node(public_graph_admission_evidence=None)
    node["public_graph_admitted"] = True
    assert_rejects(node, token="public_graph_admission_evidence_missing_phase_1387a")


def test_private_commitments_do_not_create_retroactive_public_priority():
    assert_rejects(
        public_node(private_commitment_ref="commitment://opaque-private-root"),
        token="private_or_opaque_commitments_do_not_create_retroactive_public_priority",
    )
    assert_rejects(
        public_node(quantum_hedge_private_sides=["left", "right"]),
        token="private_or_opaque_commitments_do_not_create_retroactive_public_priority",
    )


def test_private_promotion_carry_forward_rejected():
    assert_rejects(
        public_node(
            eligible_public_state="public_promoted_zero_carry_forward",
            private_promotion_carry_forward={"reputation_score": 1},
        ),
        token="private_promotion_does_not_rewrite_existing_public_reward_history",
    )


def test_valid_promotion_continuity_record_is_accepted_for_zero_carry_forward():
    record = generate_promotion_continuity_record(
        {
            "original_private_node": {
                "node_cid": "bafy-private-1387a",
                "visibility": "private",
                "validation_state": "corroborated",
                "corroboration_reuse_credit": 1,
                "reputation_score": 1,
            },
            "public_successor_node": {
                "node_cid": "bafy-public-1387a",
                "visibility": "public",
                "validation_state": "proposed",
                "corroboration_reuse_credit": 0,
                "reputation_score": 0,
            },
            "promotion_receipt": {
                "original_node_cid": "bafy-private-1387a",
                "public_successor_node_cid": "bafy-public-1387a",
                "disclosed_lineage_reference": "lineage://phase-1387a",
                "promotion_epoch": 1387,
            },
        }
    )

    event = build_public_economic_event(
        event_type="public_claimability",
        source_node=public_node(
            eligible_public_state="public_promoted_zero_carry_forward",
            promoted_from_private=True,
            promotion_continuity_record=record,
        ),
        payload={"claim_class": "bounded_public_claimability"},
    )
    assert event["source"]["eligible_public_state"] == "public_promoted_zero_carry_forward"


def test_float_payload_and_source_values_rejected():
    assert_rejects(
        public_node(public_graph_admission_evidence={"admission_id": "a", "admitted_epoch": 1.2}),
        token="public_economic_source_node_float_forbidden_phase_1387a",
    )
    with pytest.raises(PublicEconomicsAdmissionError) as exc:
        build_public_economic_event(
            event_type="public_ecu",
            source_node=public_node(),
            payload={"amount": 1.2},
        )
    assert exc.value.token == "public_economic_event_payload_float_forbidden_phase_1387a"


def test_phase_1387a_docs_record_pass_tokens_and_gap_dispositions():
    matrix = MATRIX.read_text(encoding="utf-8")
    firewall = FIREWALL.read_text(encoding="utf-8")
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")

    for text in (matrix, firewall, walkthrough):
        assert "accepted_adr_cdl_coverage_phase_1387a_executed" in text
        assert "accepted_adr_cdl_runtime_coverage_matrix_phase_1387a" in text
        assert "public_economics_requires_public_node_admission_verified_phase_1387a" in text
        assert "private_visibility_excluded_from_public_economics_phase_1387a" in text
        assert "no_unrouted_accepted_cdl_adr_functionality_before_public_rc_phase_1387a" in text

    assert "private_or_opaque_commitments_do_not_create_retroactive_public_priority" in matrix
    assert "independent_public_connection_credit_not_clawed_back_by_later_private_promotion" in matrix
    assert "private_promotion_does_not_rewrite_existing_public_reward_history" in matrix
    assert "quantum hedge" in matrix
    assert "front-running / submission-race" in matrix
    assert "gap_blocks_public_rc" not in matrix
