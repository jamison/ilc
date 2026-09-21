from __future__ import annotations

import pytest

from ilc_core.consensus.attribution_batch_bridge import (
    AttributionBatchBridgeError,
    build_attribution_batch_from_claims,
)
from ilc_core.encoding.cidv1 import node_id_from_obj


SUBMITTER = "a" * 96
CREATOR_1 = "1" * 96
CREATOR_2 = "2" * 96
CREATOR_3 = "3" * 96
CREATOR_4 = "4" * 96


def _node_id(label: str) -> str:
    return node_id_from_obj({"label": label, "phase": 1602})


NEW_NODE_ID = _node_id("new-node")
REF_1_ID = _node_id("ref-1")
REF_2_ID = _node_id("ref-2")
REF_3_ID = _node_id("ref-3")
REF_4_ID = _node_id("ref-4")


def _claim_payload(agent_id: str = SUBMITTER) -> dict[str, object]:
    return {
        "claims": [
            {
                "agent_id": agent_id,
                "amount": "1",
                "claim_id": "claim-source-refs",
                "epoch": 10,
            }
        ],
        "marker": "agent_loop_claims_ok",
    }


def _node(agent_id: str) -> dict[str, object]:
    return {
        "artifact_type": "claim",
        "created_epoch": 0,
        "novelty_score": "1",
        "recipient_agent_id": agent_id,
        "status_quality_weight": "1",
    }


def _edge(source: str, target: str) -> dict[str, object]:
    return {
        "edge_confidence": "1",
        "edge_type": "PROVENANCE",
        "source_node_id": source,
        "target_node_id": target,
    }


def _source_refs_context(
    *,
    source_refs: list[str] | None = None,
    nodes: dict[str, object] | None = None,
    event_overrides: dict[str, object] | None = None,
) -> dict[str, object]:
    refs = list(source_refs or [REF_1_ID, REF_2_ID, REF_3_ID])
    context_nodes: dict[str, object] = {
        NEW_NODE_ID: _node(SUBMITTER),
        REF_1_ID: _node(CREATOR_1),
        REF_2_ID: _node(CREATOR_2),
        REF_3_ID: _node(CREATOR_3),
        REF_4_ID: _node(CREATOR_4),
    }
    if nodes:
        context_nodes.update(nodes)
    event = {
        "event_budget_ecu": "100",
        "event_epoch": 10,
        "event_id": "event-source-refs",
        "source_node_id": NEW_NODE_ID,
        "source_refs": refs,
        "submitting_agent_id": SUBMITTER,
    }
    if event_overrides:
        event.update(event_overrides)
    return {
        "edges": [_edge(NEW_NODE_ID, ref) for ref in refs if ref in context_nodes],
        "events": [event],
        "nodes": context_nodes,
    }


def test_source_refs_with_three_distinct_creators_generates_backward_attribution() -> None:
    batch = build_attribution_batch_from_claims(
        _claim_payload(),
        backward_attribution_graph_context=_source_refs_context(),
    )

    assert batch["source_refs_attribution_bridge"] is True
    assert batch["source_refs_cdl114_guard_pass_count"] == 1
    assert batch["source_refs_cdl114_guard_block_count"] == 0
    assert batch["source_refs_sybil_diversity_threshold"] == 3
    assert batch["backward_attribution_entry_count"] == 3
    assert batch["backward_attribution_total_final_credit_ecu"] != "0"
    assert {
        entry["recipient_agent_id"]
        for entry in batch["backward_attribution_entries"]
    } == {CREATOR_1, CREATOR_2, CREATOR_3}
    assert all(
        entry["sybil_diversity_token"]
        == "cdl_114_sybil_diversity_guard_passed"
        for entry in batch["backward_attribution_entries"]
    )


def test_source_refs_with_fewer_than_three_distinct_creators_is_guarded() -> None:
    batch = build_attribution_batch_from_claims(
        _claim_payload(),
        backward_attribution_graph_context=_source_refs_context(
            source_refs=[REF_1_ID, REF_2_ID],
        ),
    )

    assert batch["source_refs_cdl114_guard_pass_count"] == 0
    assert batch["source_refs_cdl114_guard_block_count"] == 1
    assert batch["backward_attribution_entry_count"] == 0
    assert batch["attribution_event_log"][0]["dedup_reason"] == (
        "cdl_114_sybil_diversity_guard_insufficient_distinct_creators"
    )


def test_submitting_agents_own_node_does_not_count_toward_diversity() -> None:
    own_ref = _node_id("submitter-own-ref")
    batch = build_attribution_batch_from_claims(
        _claim_payload(),
        backward_attribution_graph_context=_source_refs_context(
            source_refs=[own_ref, REF_1_ID, REF_2_ID],
            nodes={own_ref: _node(SUBMITTER)},
        ),
    )

    assert batch["source_refs_cdl114_guard_block_count"] == 1
    assert batch["attribution_event_log"][0]["distinct_source_ref_creator_count"] == 2


def test_duplicate_creator_counts_once_for_source_refs_diversity() -> None:
    duplicate_creator_ref = _node_id("creator-one-second-node")
    batch = build_attribution_batch_from_claims(
        _claim_payload(),
        backward_attribution_graph_context=_source_refs_context(
            source_refs=[REF_1_ID, duplicate_creator_ref, REF_2_ID],
            nodes={duplicate_creator_ref: _node(CREATOR_1)},
        ),
    )

    assert batch["source_refs_cdl114_guard_block_count"] == 1
    assert batch["attribution_event_log"][0]["distinct_source_ref_creator_count"] == 2


@pytest.mark.parametrize(
    ("node", "token"),
    [
        (_node("A" * 96), "agent_id_hex_must_be_96_lower_hex"),
        (_node(f" {CREATOR_1}"), "agent_id_hex_must_be_96_lower_hex"),
    ],
)
def test_source_ref_creator_agent_ids_are_strictly_validated(
    node: dict[str, object],
    token: str,
) -> None:
    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        build_attribution_batch_from_claims(
            _claim_payload(),
            backward_attribution_graph_context=_source_refs_context(
                nodes={REF_1_ID: node},
            ),
        )

    assert excinfo.value.token == token


@pytest.mark.parametrize(
    "bad_node_id",
    [
        "artifact:genesis_intent_attestation_init_authority_map",
        f" {REF_1_ID}",
        REF_1_ID.upper(),
    ],
)
def test_malformed_source_ref_node_ids_fail_before_payout(
    bad_node_id: str,
) -> None:
    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        build_attribution_batch_from_claims(
            _claim_payload(),
            backward_attribution_graph_context=_source_refs_context(
                source_refs=[bad_node_id, REF_2_ID, REF_3_ID],
            ),
        )

    assert excinfo.value.token == "source_ref_node_id_must_be_cidv1_nodeid"


def test_source_ref_creator_binding_must_come_from_graph_context() -> None:
    context = _source_refs_context(
        source_refs=[REF_1_ID, REF_2_ID, REF_3_ID],
        event_overrides={"source_ref_creator_ids": [CREATOR_1, CREATOR_2, CREATOR_3]},
    )
    del context["nodes"][REF_2_ID]

    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        build_attribution_batch_from_claims(
            _claim_payload(),
            backward_attribution_graph_context=context,
        )

    assert excinfo.value.token == "source_ref_node_missing_from_graph_context"


def test_genesis_single_creator_exemption_requires_durable_receipt_token() -> None:
    batch = build_attribution_batch_from_claims(
        _claim_payload(),
        backward_attribution_graph_context=_source_refs_context(
            source_refs=[REF_1_ID],
            event_overrides={
                "genesis_single_creator_exemption": True,
                "genesis_single_creator_exemption_receipt_token": (
                    "serving_receipt:"
                    "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
                ),
            },
        ),
    )

    assert batch["source_refs_cdl114_guard_pass_count"] == 1
    assert batch["backward_attribution_entry_count"] == 1
    assert batch["backward_attribution_entries"][0]["sybil_diversity_token"] == (
        "genesis_single_creator_exemption"
    )
