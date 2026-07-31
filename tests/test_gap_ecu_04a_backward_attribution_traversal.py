from decimal import Decimal, localcontext

import pytest

from ilc_core.economics.backward_attribution_traversal import (
    BACKWARD_ATTRIBUTION_BACKWARD_POOL_SHARE_BETA,
    BACKWARD_ATTRIBUTION_CDL_VERSION,
    BACKWARD_ATTRIBUTION_DECAY_ALPHA,
    BACKWARD_ATTRIBUTION_FORWARD_RETAINED_SHARE,
    BACKWARD_ATTRIBUTION_SCORE_FORMULA,
    BACKWARD_ATTRIBUTION_MAX_DEPTH,
    BACKWARD_ATTRIBUTION_MAX_TRAVERSAL_EDGES,
    BACKWARD_ATTRIBUTION_MAX_TRAVERSAL_NODES,
    BACKWARD_ATTRIBUTION_NOVELTY_MINIMUM_SCORE,
    BACKWARD_ATTRIBUTION_PER_AGENT_CAP,
    BACKWARD_ATTRIBUTION_PER_CLUSTER_CAP,
    BACKWARD_ATTRIBUTION_PER_NODE_CAP,
    BackwardAttributionEdge,
    BackwardAttributionNode,
    BackwardAttributionTraversal,
    collapse_event_ids,
)
from ilc_core.ledger.exact_numeric import decimal_to_canonical_string


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
    assert result.repeated_node_rejections == 0
    assert {credit.upstream_artifact_id for credit in result.credits} == {"B", "C"}
    assert "A" not in {credit.upstream_artifact_id for credit in result.credits}


def test_internal_repeated_node_rejection_is_distinct_from_source_cycle() -> None:
    engine = _engine(
        {
            "A": _node(agent="agent-a"),
            "B": _node(agent="agent-b"),
            "C": _node(agent="agent-c"),
        },
        [_edge("A", "B"), _edge("B", "C"), _edge("C", "B")],
    )

    result = _quote(engine)

    assert result.cycle_rejections == 0
    assert result.repeated_node_rejections == 1
    assert {credit.upstream_artifact_id for credit in result.credits} == {"B", "C"}


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


def test_age_weight_half_life_floor_applies_at_positive_epoch_age() -> None:
    engine = _engine(
        {
            "A": _node(agent="agent-a", epoch=32),
            "B": _node(agent="agent-b", epoch=0),
        },
        [_edge("A", "B")],
    )

    result = engine.traverse(
        "A",
        event_id="event-1",
        event_budget_ecu=Decimal("100"),
        event_epoch=32,
    )

    assert result.path_scores[0].age_weight == Decimal("0.25")
    assert result.path_scores[0].raw_path_score == BACKWARD_ATTRIBUTION_DECAY_ALPHA * Decimal("0.25")


def test_age_weight_half_life_boundaries_are_exact() -> None:
    engine = _engine(
        {
            "A": _node(agent="agent-a", epoch=32),
            "B": _node(agent="agent-b", epoch=32),
            "C": _node(agent="agent-c", epoch=16),
            "D": _node(agent="agent-d", epoch=0),
        },
        [_edge("A", "B"), _edge("A", "C"), _edge("A", "D")],
    )

    result = engine.traverse(
        "A",
        event_id="event-1",
        event_budget_ecu=Decimal("100"),
        event_epoch=32,
    )

    weights = {score.upstream_artifact_id: score.age_weight for score in result.path_scores}
    assert weights == {"B": Decimal("1"), "C": Decimal("0.5"), "D": Decimal("0.25")}


def test_path_scoring_ignores_caller_decimal_context_precision() -> None:
    engine = _engine(
        {
            "A": _node(agent="agent-a"),
            "B": _node(agent="agent-b"),
            "C": _node(agent="agent-c"),
            "D": _node(agent="agent-d"),
        },
        [_edge("A", "B"), _edge("B", "C"), _edge("C", "D")],
    )

    with localcontext() as ctx:
        ctx.prec = 2
        result = _quote(engine)

    by_depth = {score.depth: score.raw_path_score for score in result.path_scores}
    assert by_depth[3] == Decimal("0.091125")


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


@pytest.mark.parametrize("bad_budget", [Decimal("0"), Decimal("-1")])
def test_non_positive_event_budget_rejected(bad_budget: Decimal) -> None:
    engine = _engine({"A": _node(agent="agent-a")}, [])

    with pytest.raises(ValueError, match="backward_attribution_event_budget_must_be_positive"):
        engine.traverse(
            "A",
            event_id="event-1",
            event_budget_ecu=bad_budget,
            event_epoch=0,
        )


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


def test_novelty_threshold_is_inclusive() -> None:
    engine = _engine(
        {
            "A": _node(agent="agent-a"),
            "B": _node(
                agent="agent-b",
                novelty=str(BACKWARD_ATTRIBUTION_NOVELTY_MINIMUM_SCORE),
            ),
        },
        [_edge("A", "B")],
    )

    result = _quote(engine)

    assert [credit.upstream_artifact_id for credit in result.credits] == ["B"]
    assert result.path_scores[0].novelty_weight == BACKWARD_ATTRIBUTION_NOVELTY_MINIMUM_SCORE


def test_missing_status_quality_weight_fails_closed() -> None:
    node_without_status = {
        "artifact_type": "claim",
        "recipient_agent_id": "agent-b",
        "created_epoch": 0,
        "novelty_score": Decimal("1"),
    }
    engine = _engine(
        {"A": _node(agent="agent-a"), "B": node_without_status},
        [_edge("A", "B")],
    )

    result = _quote(engine)

    assert result.credits == ()
    assert result.unissued_backward_pool_ecu == result.backward_pool_ecu


def test_missing_edge_confidence_fails_closed() -> None:
    edge_without_confidence = {
        "source_node_id": "A",
        "target_node_id": "B",
        "edge_type": "PROVENANCE",
    }
    engine = _engine(
        {"A": _node(agent="agent-a"), "B": _node(agent="agent-b")},
        [edge_without_confidence],
    )

    result = _quote(engine)

    assert result.credits == ()
    assert result.unissued_backward_pool_ecu == result.backward_pool_ecu


def test_thin_intermediate_node_earns_no_credit_but_routes_to_descendant() -> None:
    engine = _engine(
        {
            "A": _node(agent="agent-a"),
            "B": _node(agent="agent-b", novelty=str(BACKWARD_ATTRIBUTION_NOVELTY_MINIMUM_SCORE - Decimal("0.01"))),
            "C": _node(agent="agent-c"),
        },
        [_edge("A", "B"), _edge("B", "C")],
    )

    result = _quote(engine)

    assert [credit.upstream_artifact_id for credit in result.credits] == ["C"]
    assert "B" not in {score.upstream_artifact_id for score in result.path_scores}
    assert result.path_scores[0].depth == 2


def test_refuted_intermediate_node_earns_no_credit_but_routes_to_descendant() -> None:
    engine = _engine(
        {
            "A": _node(agent="agent-a"),
            "B": _node(agent="agent-b", refuted=True),
            "C": _node(agent="agent-c"),
        },
        [_edge("A", "B"), _edge("B", "C")],
    )

    result = _quote(engine)

    assert [credit.upstream_artifact_id for credit in result.credits] == ["C"]
    assert "B" not in {score.upstream_artifact_id for score in result.path_scores}
    assert result.path_scores[0].depth == 2


def test_public_rc_excluded_artifact_gets_no_credit() -> None:
    engine = _engine(
        {
            "A": _node(agent="agent-a"),
            "B": _node(agent="agent-b", public_rc_excluded=True),
        },
        [_edge("A", "B")],
    )

    result = _quote(engine)

    assert result.credits == ()


def test_phi_suppressed_artifact_gets_no_credit() -> None:
    engine = _engine(
        {
            "A": _node(agent="agent-a"),
            "B": _node(agent="agent-b", phi_suppressed=True),
        },
        [_edge("A", "B")],
    )

    result = _quote(engine)

    assert result.credits == ()


def test_governance_control_intermediate_transparently_routes_to_upstream_claim() -> None:
    engine = _engine(
        {
            "A": _node(agent="agent-a"),
            "B": _node(agent="agent-b", artifact_type="claim", governance_control=True),
            "C": _node(agent="agent-c", artifact_type="claim"),
        },
        [_edge("A", "B"), _edge("B", "C")],
    )

    result = _quote(engine)

    assert [credit.upstream_artifact_id for credit in result.credits] == ["C"]
    assert "B" not in {score.upstream_artifact_id for score in result.path_scores}
    assert result.path_scores[0].path_node_ids == ("A", "B", "C")
    assert result.path_scores[0].raw_path_score == BACKWARD_ATTRIBUTION_DECAY_ALPHA**2


@pytest.mark.parametrize(
    ("flag_name", "flag_value"),
    [
        ("private_artifact", True),
        ("governance_control", True),
        ("unverified_mirror_metadata", True),
    ],
)
def test_artifact_exclusion_flags_get_no_credit(flag_name: str, flag_value: bool) -> None:
    engine = _engine(
        {
            "A": _node(agent="agent-a"),
            "B": _node(agent="agent-b", **{flag_name: flag_value}),
        },
        [_edge("A", "B")],
    )

    result = _quote(engine)

    assert result.credits == ()


def test_artifact_type_outside_mask_gets_no_credit() -> None:
    engine = _engine(
        {
            "A": _node(agent="agent-a"),
            "B": _node(agent="agent-b", artifact_type="governance-control"),
        },
        [_edge("A", "B")],
    )

    result = _quote(engine)

    assert result.credits == ()


def test_mixed_type_path_is_dropped_at_invalid_edge() -> None:
    engine = _engine(
        {
            "A": _node(agent="agent-a"),
            "B": _node(agent="agent-b"),
            "C": _node(agent="agent-c"),
        },
        [_edge("A", "B"), _edge("B", "C", edge_type="GOVERNANCE")],
    )

    result = _quote(engine)

    assert {credit.upstream_artifact_id for credit in result.credits} == {"B"}
    assert "C" not in {score.upstream_artifact_id for score in result.path_scores}


def test_node_count_cap_raises() -> None:
    nodes = {
        f"N{index}": _node(agent=f"agent-{index}")
        for index in range(BACKWARD_ATTRIBUTION_MAX_TRAVERSAL_NODES + 1)
    }

    with pytest.raises(ValueError, match="backward_attribution_node_count_exceeds_maximum"):
        _engine(nodes, [])


def test_edge_count_cap_raises() -> None:
    nodes = {
        "A": _node(agent="agent-a"),
        "B": _node(agent="agent-b"),
    }
    edges = [_edge("A", "B") for _ in range(BACKWARD_ATTRIBUTION_MAX_TRAVERSAL_EDGES + 1)]

    with pytest.raises(ValueError, match="backward_attribution_edge_count_exceeds_maximum"):
        _engine(nodes, edges)


def test_filtered_edge_types_do_not_consume_runtime_edge_budget() -> None:
    nodes = {
        "A": _node(agent="agent-a"),
        "B": _node(agent="agent-b"),
    }
    edges = [
        _edge("A", "B", edge_type="GOVERNANCE")
        for _ in range(BACKWARD_ATTRIBUTION_MAX_TRAVERSAL_EDGES - 1)
    ]
    edges.append(_edge("A", "B"))
    engine = _engine(nodes, edges)

    result = _quote(engine)

    assert result.loaded_edge_count == BACKWARD_ATTRIBUTION_MAX_TRAVERSAL_EDGES
    assert result.traversal_edge_count == 1
    assert [credit.upstream_artifact_id for credit in result.credits] == ["B"]


def test_runtime_edge_traversal_cap_raises_on_path_explosion() -> None:
    fanout = 20
    nodes = {"S": _node(agent="agent-source")}
    edges: list[dict[str, object]] = []
    for first in range(fanout):
        first_id = f"F{first}"
        nodes[first_id] = _node(agent=f"agent-first-{first}")
        edges.append(_edge("S", first_id))
    for first in range(fanout):
        for middle in range(fanout):
            middle_id = f"M{middle}"
            nodes.setdefault(middle_id, _node(agent=f"agent-middle-{middle}"))
            edges.append(_edge(f"F{first}", middle_id))
    for middle in range(fanout):
        for sink in range(fanout):
            sink_id = f"K{sink}"
            nodes.setdefault(sink_id, _node(agent=f"agent-sink-{sink}"))
            edges.append(_edge(f"M{middle}", sink_id))
    engine = _engine(nodes, edges)

    with pytest.raises(ValueError, match="backward_attribution_edge_traversal_exceeds_maximum"):
        _quote(engine, source="S")


@pytest.mark.parametrize("bad_value", [Decimal("NaN"), Decimal("Infinity")])
def test_dataclass_node_numeric_fields_are_revalidated(bad_value: Decimal) -> None:
    node = BackwardAttributionNode(
        node_id="A",
        artifact_type="claim",
        recipient_agent_id="agent-a",
        created_epoch=0,
        status_quality_weight=bad_value,
        novelty_score=Decimal("1"),
    )

    with pytest.raises(ValueError, match="backward_attribution_status_quality_weight_invalid"):
        BackwardAttributionTraversal({"A": node}, [])


def test_dataclass_edge_numeric_fields_are_revalidated() -> None:
    edge = BackwardAttributionEdge(
        source_node_id="A",
        target_node_id="B",
        edge_type="PROVENANCE",
        edge_confidence=Decimal("NaN"),
    )

    with pytest.raises(ValueError, match="backward_attribution_edge_confidence_invalid"):
        _engine({"A": _node(), "B": _node(agent="agent-b")}, [edge])


def test_string_boolean_flags_are_rejected() -> None:
    node = _node(agent="agent-b", refuted="False")

    with pytest.raises(ValueError, match="backward_attribution_refuted_must_be_bool"):
        _engine({"A": _node(agent="agent-a"), "B": node}, [_edge("A", "B")])


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


def test_cluster_cap_clips_multiple_agents_in_same_mutual_citation_cluster() -> None:
    nodes = {"A": _node(agent="agent-source")}
    edges: list[dict[str, object]] = []
    for index in range(6):
        node_id = f"N{index}"
        nodes[node_id] = _node(agent=f"agent-{index}")
        edges.append(_edge("A", node_id))
        edges.append(_edge(node_id, "A"))
    engine = _engine(nodes, edges)

    result = engine.traverse(
        "A",
        event_id="event-cluster",
        event_budget_ecu=Decimal("1000"),
        event_epoch=0,
        apply_antigaming_caps=True,
    )

    cluster_credit = sum(
        credit.final_credit_ecu
        for credit in result.final_credits
        if credit.cluster_id.startswith("cluster:")
    )
    assert cluster_credit == result.cluster_cap_amount_ecu
    assert any(credit.cluster_cap_applied for credit in result.final_credits)
    assert result.unissued_backward_pool_ecu > Decimal("0")


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
    assert collapse_event_ids(["event-1", "event-2", "event-2"]) == (
        "event-1",
        "event-2",
    )


def test_credit_allocation_never_exceeds_backward_pool_for_many_equal_paths() -> None:
    nodes = {"A": _node(agent="agent-a")}
    edges = []
    for index in range(18):
        node_id = f"N{index}"
        nodes[node_id] = _node(agent=f"agent-{index}")
        edges.append(_edge("A", node_id))
    engine = _engine(nodes, edges)

    result = _quote(engine)

    issued = sum((credit.pre_cap_credit_ecu for credit in result.credits), Decimal("0"))
    assert issued == result.backward_pool_ecu
    assert issued <= result.backward_pool_ecu
    assert result.unissued_backward_pool_ecu == Decimal("0")


def test_receipt_exposes_formula_and_loaded_vs_traversed_counts() -> None:
    engine = _engine(
        {
            "A": _node(agent="agent-a"),
            "B": _node(agent="agent-b"),
            "C": _node(agent="agent-c"),
        },
        [_edge("A", "B"), _edge("B", "C")],
    )

    result = _quote(engine)

    assert result.cdl_version == BACKWARD_ATTRIBUTION_CDL_VERSION
    assert result.score_formula == BACKWARD_ATTRIBUTION_SCORE_FORMULA
    assert result.loaded_node_count == 3
    assert result.loaded_edge_count == 2
    assert result.traversal_node_count == 3
    assert result.traversal_edge_count == 2
    assert result.path_scores[0].typed_path_weight == Decimal("1")
    assert result.path_scores[0].artifact_weight == Decimal("1")
    assert result.path_scores[1].path_edge_confidences == (Decimal("1"), Decimal("1"))


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


def test_decimal_to_canonical_string_root_format_contract() -> None:
    assert decimal_to_canonical_string(Decimal("0.5000")) == "0.5"
    assert decimal_to_canonical_string(Decimal("00012.3400")) == "12.34"
    assert decimal_to_canonical_string(Decimal("-0.000")) == "0"
    assert decimal_to_canonical_string(Decimal("1E-6")) == "0.000001"
