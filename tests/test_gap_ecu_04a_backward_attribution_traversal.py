from decimal import Decimal

import pytest

from ilc_core.economics.backward_attribution_traversal import (
    BACKWARD_ATTRIBUTION_BACKWARD_POOL_SHARE_BETA,
    BACKWARD_ATTRIBUTION_DECAY_ALPHA,
    BACKWARD_ATTRIBUTION_FORWARD_RETAINED_SHARE,
    BACKWARD_ATTRIBUTION_MAX_DEPTH,
    BACKWARD_ATTRIBUTION_NOVELTY_MINIMUM_SCORE,
    BACKWARD_ATTRIBUTION_PER_AGENT_CAP,
    BACKWARD_ATTRIBUTION_PER_CLUSTER_CAP,
    BACKWARD_ATTRIBUTION_PER_NODE_CAP,
    BackwardAttributionTraversal,
)


def _node(
    artifact_type: str = "claim",
    agent: str = "agent-a",
    epoch: int = 0,
    status: str = "1",
    novelty: str = "1",
    **flags: object,
) -> dict[str, object]:
    return {
        "artifact_type": artifact_type,
        "recipient_agent_id": agent,
        "created_epoch": epoch,
        "status_quality_weight": Decimal(status),
        "novelty_score": Decimal(novelty),
        **flags,
    }


def _edge(source: str, target: str, edge_type: str = "PROVENANCE") -> dict[str, object]:
    return {
        "source_node_id": source,
        "target_node_id": target,
        "edge_type": edge_type,
        "edge_confidence": Decimal("1"),
    }


def _engine(
    nodes: dict[str, dict[str, object]] | None = None,
    edges: list[dict[str, object]] | None = None,
) -> BackwardAttributionTraversal:
    return BackwardAttributionTraversal(nodes or {}, edges or [])


def _quote(engine: BackwardAttributionTraversal, source: str = "A"):
    return engine.traverse(
        source,
        event_id="event-1",
        event_budget_ecu=Decimal("100"),
        event_epoch=0,
    )


def test_simple_two_hop_attribution() -> None:
    engine = _engine(
        {
            "A": _node(agent="agent-a"),
            "B": _node(agent="agent-b"),
            "C": _node(agent="agent-c"),
        },
        [_edge("A", "B"), _edge("B", "C")],
    )

    result = _quote(engine)

    assert [credit.upstream_artifact_id for credit in result.credits] == ["B", "C"]
    raw_scores = {score.upstream_artifact_id: score.raw_path_score for score in result.path_scores}
    assert raw_scores["B"] == BACKWARD_ATTRIBUTION_DECAY_ALPHA
    assert raw_scores["C"] == BACKWARD_ATTRIBUTION_DECAY_ALPHA**2
    assert sum(credit.pre_cap_credit_ecu for credit in result.credits) == result.backward_pool_ecu


def test_cycle_detection_terminates() -> None:
    engine = _engine(
        {
            "A": _node(agent="agent-a"),
            "B": _node(agent="agent-b"),
            "C": _node(agent="agent-c"),
        },
        [_edge("A", "B"), _edge("B", "C"), _edge("C", "A")],
    )

    result = _quote(engine)

    assert result.cycle_rejections == 1
    assert result.repeated_node_rejections == 1
    assert {credit.upstream_artifact_id for credit in result.credits} == {"B", "C"}
    assert "A" not in {credit.upstream_artifact_id for credit in result.credits}


def test_max_depth_enforcement() -> None:
    nodes = {"N0": _node(agent="agent-0")}
    edges = []
    for index in range(1, 10):
        nodes[f"N{index}"] = _node(agent=f"agent-{index}")
        edges.append(_edge(f"N{index - 1}", f"N{index}"))
    engine = _engine(nodes, edges)

    result = _quote(engine, source="N0")

    credited_ids = {credit.upstream_artifact_id for credit in result.credits}
    assert credited_ids == {"N1", "N2", "N3"}
    assert all(score.depth <= BACKWARD_ATTRIBUTION_MAX_DEPTH for score in result.path_scores)


def test_decay_application() -> None:
    engine = _engine(
        {
            "A": _node(agent="agent-a"),
            "B": _node(agent="agent-b"),
            "C": _node(agent="agent-c"),
            "D": _node(agent="agent-d"),
        },
        [_edge("A", "B"), _edge("B", "C"), _edge("C", "D")],
    )

    result = _quote(engine)
    by_depth = {score.depth: score.raw_path_score for score in result.path_scores}

    assert by_depth[1] == BACKWARD_ATTRIBUTION_DECAY_ALPHA
    assert by_depth[2] == BACKWARD_ATTRIBUTION_DECAY_ALPHA**2
    assert by_depth[3] == BACKWARD_ATTRIBUTION_DECAY_ALPHA**3


def test_bidirectional_coefficient_separation() -> None:
    engine = _engine(
        {"A": _node(), "B": _node(agent="agent-b")},
        [_edge("A", "B")],
    )

    result = _quote(engine)

    assert result.backward_pool_ecu == Decimal("100") * BACKWARD_ATTRIBUTION_BACKWARD_POOL_SHARE_BETA
    assert result.forward_retained_ecu == Decimal("100") * BACKWARD_ATTRIBUTION_FORWARD_RETAINED_SHARE
    assert result.backward_pool_ecu != result.forward_retained_ecu
    assert result.backward_pool_ecu > Decimal("0")
    assert result.forward_retained_ecu > Decimal("0")


def test_dead_end_path() -> None:
    engine = _engine({"A": _node(agent="agent-a")}, [])

    result = _quote(engine)

    assert result.path_scores == ()
    assert result.credits == ()
    assert result.unissued_backward_pool_ecu == result.backward_pool_ecu


def test_refuted_upstream_node() -> None:
    engine = _engine(
        {
            "A": _node(agent="agent-a"),
            "B": _node(agent="agent-b", refuted=True),
        },
        [_edge("A", "B")],
    )

    result = _quote(engine)

    assert result.credits == ()
    assert result.unissued_backward_pool_ecu == result.backward_pool_ecu


@pytest.mark.parametrize("bad_value", [Decimal("NaN"), Decimal("Infinity")])
def test_non_finite_decimal_rejection(bad_value: Decimal) -> None:
    engine = _engine({"A": _node(agent="agent-a")}, [])

    with pytest.raises(ValueError, match="backward_attribution_event_budget_invalid"):
        engine.traverse(
            "A",
            event_id="event-1",
            event_budget_ecu=bad_value,
            event_epoch=0,
        )


def test_thin_node_below_novelty_gate_gets_no_credit() -> None:
    engine = _engine(
        {
            "A": _node(agent="agent-a"),
            "B": _node(agent="agent-b", novelty=str(BACKWARD_ATTRIBUTION_NOVELTY_MINIMUM_SCORE - Decimal("0.01"))),
        },
        [_edge("A", "B")],
    )

    result = _quote(engine)

    assert result.credits == ()


def test_thin_intermediate_node_cannot_bridge_credit_to_descendant() -> None:
    engine = _engine(
        {
            "A": _node(agent="agent-a"),
            "B": _node(agent="agent-b", novelty=str(BACKWARD_ATTRIBUTION_NOVELTY_MINIMUM_SCORE - Decimal("0.01"))),
            "C": _node(agent="agent-c"),
        },
        [_edge("A", "B"), _edge("B", "C")],
    )

    result = _quote(engine)

    assert result.credits == ()


def test_duplicate_artifact_paths_collapse_to_highest_score() -> None:
    engine = _engine(
        {
            "A": _node(agent="agent-a"),
            "B": _node(agent="agent-b", status="0.50"),
            "C": _node(agent="agent-c"),
        },
        [_edge("A", "B"), _edge("A", "C"), _edge("C", "B")],
    )

    result = _quote(engine)

    b_scores = [score for score in result.path_scores if score.upstream_artifact_id == "B"]
    assert len(b_scores) == 1
    assert b_scores[0].depth == 1
    assert b_scores[0].raw_path_score == BACKWARD_ATTRIBUTION_DECAY_ALPHA * Decimal("0.50")


def test_duplicate_event_ids_are_collapsed_before_traversal() -> None:
    engine = _engine(
        {"A": _node(), "B": _node(agent="agent-b")},
        [_edge("A", "B")],
    )

    result = engine.traverse(
        "A",
        event_id="event-1",
        event_ids=["event-1", "event-2", "event-2"],
        event_budget_ecu=Decimal("100"),
        event_epoch=0,
    )

    assert result.event_id == "event-1"
    assert len(result.credits) == 1


def test_cap_reference_amounts_are_event_local_and_not_applied_in_04a() -> None:
    engine = _engine(
        {"A": _node(), "B": _node(agent="agent-b")},
        [_edge("A", "B")],
    )

    result = _quote(engine)

    assert result.node_cap_amount_ecu == result.backward_pool_ecu * BACKWARD_ATTRIBUTION_PER_NODE_CAP
    assert result.agent_cap_amount_ecu == result.backward_pool_ecu * BACKWARD_ATTRIBUTION_PER_AGENT_CAP
    assert result.cluster_cap_amount_ecu == result.backward_pool_ecu * BACKWARD_ATTRIBUTION_PER_CLUSTER_CAP
    assert result.caps_applied is False
