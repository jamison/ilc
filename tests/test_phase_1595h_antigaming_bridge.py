from __future__ import annotations

import json
from decimal import Decimal

from ilc_core.consensus.attribution_batch_bridge import build_attribution_batch_from_claims
from ilc_core.economics.backward_attribution_traversal import (
    BACKWARD_ATTRIBUTION_SYBIL_DIVERSITY_GUARD_CDL_GAP,
    BackwardAttributionTraversal,
)


AGENT_1 = "1" * 96
AGENT_2 = "2" * 96
AGENT_3 = "3" * 96
AGENT_4 = "4" * 96
AGENT_5 = "5" * 96
AGENT_6 = "6" * 96
AGENT_A = "a" * 96


def _node(agent_id: str, *, novelty: str = "1", status: str = "1") -> dict[str, object]:
    return {
        "artifact_type": "claim",
        "created_epoch": 0,
        "novelty_score": novelty,
        "recipient_agent_id": agent_id,
        "status_quality_weight": status,
    }


def _edge(source: str, target: str) -> dict[str, object]:
    return {
        "edge_confidence": "1",
        "edge_type": "PROVENANCE",
        "source_node_id": source,
        "target_node_id": target,
    }


def _claim_payload() -> dict[str, object]:
    return {
        "claims": [
            {
                "agent_id": AGENT_A,
                "amount": "1",
                "claim_id": "claim-direct",
                "epoch": 9,
            }
        ],
        "marker": "agent_loop_claims_ok",
    }


def test_per_node_cap_clips_excessive_credit() -> None:
    traversal = BackwardAttributionTraversal(
        {"source": _node(AGENT_A), "upstream": _node(AGENT_1)},
        [_edge("source", "upstream")],
    )

    result = traversal.traverse(
        "source",
        event_id="event-node-cap",
        event_budget_ecu=Decimal("100"),
        event_epoch=9,
        apply_antigaming_caps=True,
    )

    assert result.backward_pool_ecu == Decimal("10.00")
    assert result.node_cap_amount_ecu == Decimal("0.5000")
    assert result.final_credits[0].final_credit_ecu == Decimal("0.5000")
    assert result.final_credits[0].clipped_residual_ecu == Decimal("9.5000")
    assert result.final_credits[0].node_cap_applied is True
    assert result.unissued_backward_pool_ecu == Decimal("9.5000")


def test_per_agent_cap_limits_combined_agent_credit() -> None:
    traversal = BackwardAttributionTraversal(
        {
            "source": _node(AGENT_A),
            "upstream1": _node(AGENT_1),
            "upstream2": _node(AGENT_1),
            "upstream3": _node(AGENT_1),
        },
        [
            _edge("source", "upstream1"),
            _edge("source", "upstream2"),
            _edge("source", "upstream3"),
        ],
    )

    result = traversal.traverse(
        "source",
        event_id="event-agent-cap",
        event_budget_ecu="100",
        event_epoch=9,
        apply_antigaming_caps=True,
    )

    total_agent_credit = sum(
        credit.final_credit_ecu
        for credit in result.final_credits
        if credit.recipient_agent_id == AGENT_1
    )
    assert result.agent_cap_amount_ecu == Decimal("1.0000")
    assert total_agent_credit == Decimal("1.0000")
    assert any(credit.agent_cap_applied for credit in result.final_credits)


def test_per_cluster_cap_limits_mutual_citation_cluster() -> None:
    nodes = {"source": _node(AGENT_A)}
    agents = [AGENT_1, AGENT_2, AGENT_3, AGENT_4, AGENT_5, AGENT_6]
    for index, agent_id in enumerate(agents, start=1):
        nodes[f"upstream{index}"] = _node(agent_id)
    edges = [_edge("source", f"upstream{index}") for index in range(1, 7)]
    for index in range(1, 6):
        edges.append(_edge(f"upstream{index}", f"upstream{index + 1}"))
        edges.append(_edge(f"upstream{index + 1}", f"upstream{index}"))
    traversal = BackwardAttributionTraversal(nodes, edges)

    result = traversal.traverse(
        "source",
        event_id="event-cluster-cap",
        event_budget_ecu="100",
        event_epoch=9,
        apply_antigaming_caps=True,
    )

    cluster_credits = [
        credit
        for credit in result.final_credits
        if credit.cluster_id.startswith("cluster:")
    ]
    total_cluster_credit = sum(
        credit.final_credit_ecu for credit in cluster_credits
    )
    assert result.cluster_cap_amount_ecu == Decimal("2.5000")
    assert total_cluster_credit == Decimal("2.5000")
    assert any(credit.cluster_cap_applied for credit in cluster_credits)


def test_sybil_diversity_guard_threshold_gap_documented_not_implemented() -> None:
    batch = build_attribution_batch_from_claims(
        _claim_payload(),
        backward_attribution_graph_context={
            "edges": [_edge("source", "upstream")],
            "events": [
                {
                    "event_budget_ecu": "100",
                    "event_epoch": 9,
                    "event_id": "event-sybil-gap",
                    "source_node_id": "source",
                }
            ],
            "nodes": {"source": _node(AGENT_A), "upstream": _node(AGENT_1)},
        },
    )

    assert (
        batch["sybil_diversity_guard_cdl_gap"]
        == BACKWARD_ATTRIBUTION_SYBIL_DIVERSITY_GUARD_CDL_GAP
    )
    assert "sybil_diversity_threshold" not in batch


def test_cdl084_explicit_chain_already_settled_blocks_graph_branch() -> None:
    batch = build_attribution_batch_from_claims(
        _claim_payload(),
        backward_attribution_graph_context={
            "edges": [_edge("source", "upstream")],
            "events": [
                {
                    "already_settled_by_cdl084": True,
                    "event_budget_ecu": "100",
                    "event_epoch": 9,
                    "event_id": "event-cdl084",
                    "source_node_id": "source",
                }
            ],
            "nodes": {"source": _node(AGENT_A), "upstream": _node(AGENT_1)},
        },
        cdl084_settled_event_ids={"event-cdl084"},
    )

    assert batch["backward_attribution_entry_count"] == 0
    assert batch["backward_attribution_total_final_credit_ecu"] == "0"
    assert batch["attribution_event_log"][0]["dedup_reason"] == (
        "cdl084_explicit_chain_already_settled"
    )


def test_bridge_adds_backward_attribution_entries_and_event_log() -> None:
    batch = build_attribution_batch_from_claims(
        _claim_payload(),
        backward_attribution_graph_context={
            "edges": [_edge("source", "upstream")],
            "events": [
                {
                    "event_budget_ecu": "100",
                    "event_epoch": 9,
                    "event_id": "event-bridge",
                    "source_node_id": "source",
                }
            ],
            "nodes": {"source": _node(AGENT_A), "upstream": _node(AGENT_1)},
        },
    )

    assert batch["backward_attribution_marker"] == (
        "backward_attribution_runtime_wired_GAP_ECU_04b"
    )
    assert batch["backward_attribution_caps_applied"] is True
    assert batch["backward_attribution_entry_count"] == 1
    assert batch["attribution_event_log"][0]["anti_gaming_cap_applied"] is True
    assert any(
        attribution["agent_id_hex"] == AGENT_1
        for attribution in batch["attributions"]
    )


def test_attribution_event_log_persisted_to_fallback_file_sink(tmp_path) -> None:
    batch = build_attribution_batch_from_claims(
        _claim_payload(),
        backward_attribution_graph_context={
            "edges": [_edge("source", "upstream")],
            "events": [
                {
                    "event_budget_ecu": "100",
                    "event_epoch": 9,
                    "event_id": "event-log",
                    "source_node_id": "source",
                }
            ],
            "nodes": {"source": _node(AGENT_A), "upstream": _node(AGENT_1)},
        },
        attribution_event_log_dir=tmp_path,
    )

    log_files = sorted(tmp_path.glob("attr_event_9_*.json"))
    assert len(log_files) == len(batch["attribution_event_log"])
    persisted = json.loads(log_files[0].read_text(encoding="utf-8"))
    assert persisted["event_id"] == "event-log"
    assert persisted["lmdb_key_hex"].startswith("617474725f6576656e743a")


def test_h3_zero_credit_intermediate_routes_before_antigaming_caps() -> None:
    traversal = BackwardAttributionTraversal(
        {
            "source": _node(AGENT_A),
            "thin": _node(AGENT_1, novelty="0.1"),
            "foundational": _node(AGENT_2),
        },
        [_edge("source", "thin"), _edge("thin", "foundational")],
    )

    result = traversal.traverse(
        "source",
        event_id="event-h3",
        event_budget_ecu="100",
        event_epoch=9,
        apply_antigaming_caps=True,
    )

    assert [credit.upstream_artifact_id for credit in result.final_credits] == [
        "foundational"
    ]
    assert result.final_credits[0].final_credit_ecu > Decimal("0")


def test_existing_claim_payload_conversion_unchanged_without_graph_context() -> None:
    batch = build_attribution_batch_from_claims(_claim_payload())

    assert "backward_attribution_entries" not in batch
    assert "sybil_diversity_guard_cdl_gap" not in batch
    assert batch["attribution_count"] == 1
