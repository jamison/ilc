# SPDX-License-Identifier: AGPL-3.0-only
"""CDL-108 backward attribution traversal engine.

This module is intentionally isolated from production settlement. GAP-ECU-04b
is responsible for bridge wiring, anti-gaming integration, and any later live
activation path.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Mapping


BACKWARD_ATTRIBUTION_CDL_VERSION = (
    "cdl_108_backward_attribution_ratification_GAP_ECU_03.v0.1"
)
BACKWARD_ATTRIBUTION_TRIGGERING_EVENTS = "accepted_frontier_plus_invite_init"
BACKWARD_ATTRIBUTION_ARTIFACT_MASK = frozenset(
    {
        "claim",
        "dataset",
        "evidence",
        "hyperedge_entity",
        "method",
        "review",
        "revision_chain",
        "software",
    }
)
BACKWARD_ATTRIBUTION_ALLOWED_EDGE_TYPES = frozenset(
    {"PROVENANCE", "REUSE", "VALIDATE", "REVISION"}
)
BACKWARD_ATTRIBUTION_SCORE_FORMULA = "status_quality_weighted_distance"
BACKWARD_ATTRIBUTION_DECAY_ALPHA = Decimal("0.45")
BACKWARD_ATTRIBUTION_MAX_DEPTH = 3
BACKWARD_ATTRIBUTION_AGE_HALF_LIFE_EPOCHS = 16
BACKWARD_ATTRIBUTION_BACKWARD_POOL_SHARE_BETA = Decimal("0.10")
BACKWARD_ATTRIBUTION_FORWARD_RETAINED_SHARE = Decimal("0.90")
BACKWARD_ATTRIBUTION_REFUTATION_SPECIFIC_BETA = Decimal("0")
BACKWARD_ATTRIBUTION_MAX_TRAVERSAL_NODES = 1000
BACKWARD_ATTRIBUTION_MAX_TRAVERSAL_EDGES = 5000
BACKWARD_ATTRIBUTION_NOVELTY_MINIMUM_SCORE = Decimal("0.20")
BACKWARD_ATTRIBUTION_PER_NODE_CAP = Decimal("0.05")
BACKWARD_ATTRIBUTION_PER_AGENT_CAP = Decimal("0.10")
BACKWARD_ATTRIBUTION_PER_CLUSTER_CAP = Decimal("0.25")
BACKWARD_ATTRIBUTION_REFUTATION_INTERACTION = (
    "refutation_excluded_from_generic_backward_pool"
)
BACKWARD_ATTRIBUTION_AUDIT_SURFACE = "hybrid_merkle_proof"

ZERO = Decimal("0")
ONE = Decimal("1")


@dataclass(frozen=True)
class BackwardAttributionNode:
    """Normalized graph node used by the isolated traversal engine."""

    node_id: str
    artifact_type: str
    recipient_agent_id: str
    created_epoch: int
    status_quality_weight: Decimal
    novelty_score: Decimal
    refuted: bool = False
    phi_suppressed: bool = False
    private_artifact: bool = False
    public_rc_excluded: bool = False
    governance_control: bool = False
    unverified_mirror_metadata: bool = False


@dataclass(frozen=True)
class BackwardAttributionEdge:
    """Directed typed edge from a downstream node to an upstream artifact."""

    source_node_id: str
    target_node_id: str
    edge_type: str
    edge_confidence: Decimal


@dataclass(frozen=True)
class BackwardAttributionPathScore:
    """Raw score for one collapsed eligible upstream artifact path."""

    event_id: str
    upstream_artifact_id: str
    recipient_agent_id: str
    depth: int
    path_node_ids: tuple[str, ...]
    path_edge_types: tuple[str, ...]
    raw_path_score: Decimal
    age_weight: Decimal
    status_quality_weight: Decimal
    novelty_weight: Decimal
    edge_confidence_weight: Decimal


@dataclass(frozen=True)
class BackwardAttributionCreditQuote:
    """Pre-cap traversal quote for an upstream artifact.

    GAP-ECU-04a does not wire production dominance caps. The cap reference
    amounts are returned for GAP-ECU-04b, while this isolated engine emits
    normalized pre-cap credit quotes only.
    """

    event_id: str
    upstream_artifact_id: str
    recipient_agent_id: str
    depth: int
    raw_path_score: Decimal
    pre_cap_credit_ecu: Decimal


@dataclass(frozen=True)
class BackwardAttributionResult:
    """Deterministic output of one backward traversal event quote."""

    cdl_version: str
    event_id: str
    source_node_id: str
    event_budget_ecu: Decimal
    backward_pool_ecu: Decimal
    forward_retained_ecu: Decimal
    path_scores: tuple[BackwardAttributionPathScore, ...]
    credits: tuple[BackwardAttributionCreditQuote, ...]
    unissued_backward_pool_ecu: Decimal
    node_cap_amount_ecu: Decimal
    agent_cap_amount_ecu: Decimal
    cluster_cap_amount_ecu: Decimal
    caps_applied: bool
    cycle_rejections: int
    repeated_node_rejections: int
    traversal_node_count: int
    traversal_edge_count: int


def _require_non_empty_string(value: object, token: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(token)
    return value.strip()


def _require_non_negative_int(value: object, token: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(token)
    return value


def _require_decimal(value: object, token: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(token)
    if isinstance(value, Decimal):
        number = value
    elif isinstance(value, int):
        number = Decimal(value)
    elif isinstance(value, str):
        try:
            number = Decimal(value)
        except InvalidOperation as exc:
            raise ValueError(token) from exc
    else:
        raise ValueError(token)
    if not number.is_finite():
        raise ValueError(token)
    return number


def _require_factor(value: object, token: str) -> Decimal:
    factor = _require_decimal(value, token)
    if factor < ZERO or factor > ONE:
        raise ValueError(token)
    return factor


def _canonical_edge_type(value: object) -> str:
    raw = _require_non_empty_string(value, "backward_attribution_edge_type_required")
    return raw.strip().upper()


def _node_from_mapping(node_id: str, value: object) -> BackwardAttributionNode:
    if isinstance(value, BackwardAttributionNode):
        if value.node_id != node_id:
            raise ValueError("backward_attribution_node_id_mismatch")
        return value
    if not isinstance(value, Mapping):
        raise ValueError("backward_attribution_node_must_be_mapping")
    return BackwardAttributionNode(
        node_id=node_id,
        artifact_type=_require_non_empty_string(
            value.get("artifact_type"),
            "backward_attribution_artifact_type_required",
        ),
        recipient_agent_id=_require_non_empty_string(
            value.get("recipient_agent_id"),
            "backward_attribution_recipient_agent_id_required",
        ),
        created_epoch=_require_non_negative_int(
            value.get("created_epoch"),
            "backward_attribution_created_epoch_must_be_non_negative_int",
        ),
        status_quality_weight=_require_factor(
            value.get("status_quality_weight", ZERO),
            "backward_attribution_status_quality_weight_invalid",
        ),
        novelty_score=_require_factor(
            value.get("novelty_score", ZERO),
            "backward_attribution_novelty_score_invalid",
        ),
        refuted=bool(value.get("refuted", False)),
        phi_suppressed=bool(value.get("phi_suppressed", False)),
        private_artifact=bool(value.get("private_artifact", False)),
        public_rc_excluded=bool(value.get("public_rc_excluded", False)),
        governance_control=bool(value.get("governance_control", False)),
        unverified_mirror_metadata=bool(value.get("unverified_mirror_metadata", False)),
    )


def _edge_from_mapping(value: object) -> BackwardAttributionEdge:
    if isinstance(value, BackwardAttributionEdge):
        return value
    if not isinstance(value, Mapping):
        raise ValueError("backward_attribution_edge_must_be_mapping")
    return BackwardAttributionEdge(
        source_node_id=_require_non_empty_string(
            value.get("source_node_id"),
            "backward_attribution_edge_source_required",
        ),
        target_node_id=_require_non_empty_string(
            value.get("target_node_id"),
            "backward_attribution_edge_target_required",
        ),
        edge_type=_canonical_edge_type(value.get("edge_type")),
        edge_confidence=_require_factor(
            value.get("edge_confidence", ZERO),
            "backward_attribution_edge_confidence_invalid",
        ),
    )


def _age_weight(created_epoch: int, event_epoch: int) -> Decimal:
    age_epochs = max(0, event_epoch - created_epoch)
    return Decimal("0.5") ** (age_epochs // BACKWARD_ATTRIBUTION_AGE_HALF_LIFE_EPOCHS)


def _eligible_artifact_weight(node: BackwardAttributionNode) -> Decimal:
    if node.refuted:
        return ZERO
    if node.phi_suppressed:
        return ZERO
    if node.private_artifact:
        return ZERO
    if node.public_rc_excluded:
        return ZERO
    if node.governance_control:
        return ZERO
    if node.unverified_mirror_metadata:
        return ZERO
    if node.artifact_type not in BACKWARD_ATTRIBUTION_ARTIFACT_MASK:
        return ZERO
    return ONE


def _novelty_weight(node: BackwardAttributionNode) -> Decimal:
    if node.novelty_score < BACKWARD_ATTRIBUTION_NOVELTY_MINIMUM_SCORE:
        return ZERO
    return node.novelty_score


class BackwardAttributionTraversal:
    """Isolated CDL-108 graph traversal and raw path scoring engine."""

    def __init__(
        self,
        nodes: Mapping[str, object],
        edges: tuple[object, ...] | list[object],
    ) -> None:
        self._nodes = {
            _require_non_empty_string(node_id, "backward_attribution_node_id_required"): (
                _node_from_mapping(node_id, node)
            )
            for node_id, node in nodes.items()
        }
        self._edges = tuple(_edge_from_mapping(edge) for edge in edges)
        if len(self._nodes) > BACKWARD_ATTRIBUTION_MAX_TRAVERSAL_NODES:
            raise ValueError("backward_attribution_node_count_exceeds_maximum")
        if len(self._edges) > BACKWARD_ATTRIBUTION_MAX_TRAVERSAL_EDGES:
            raise ValueError("backward_attribution_edge_count_exceeds_maximum")
        self._outgoing: dict[str, tuple[BackwardAttributionEdge, ...]] = {}
        edge_buckets: dict[str, list[BackwardAttributionEdge]] = {}
        for edge in self._edges:
            if edge.source_node_id not in self._nodes:
                raise ValueError("backward_attribution_edge_source_unknown")
            if edge.target_node_id not in self._nodes:
                raise ValueError("backward_attribution_edge_target_unknown")
            edge_buckets.setdefault(edge.source_node_id, []).append(edge)
        for source_node_id, bucket in edge_buckets.items():
            self._outgoing[source_node_id] = tuple(
                sorted(
                    bucket,
                    key=lambda edge: (edge.target_node_id, edge.edge_type),
                )
            )

    @staticmethod
    def collapse_event_ids(event_ids: tuple[str, ...] | list[str]) -> tuple[str, ...]:
        """Collapse duplicate event ids while preserving first-seen order."""
        seen: set[str] = set()
        collapsed: list[str] = []
        for event_id in event_ids:
            normalized = _require_non_empty_string(
                event_id,
                "backward_attribution_event_id_required",
            )
            if normalized in seen:
                continue
            seen.add(normalized)
            collapsed.append(normalized)
        if not collapsed:
            raise ValueError("backward_attribution_event_id_required")
        return tuple(collapsed)

    def traverse(
        self,
        source_node_id: str,
        *,
        event_id: str,
        event_budget_ecu: Decimal | int | str,
        event_epoch: int,
        event_ids: tuple[str, ...] | list[str] | None = None,
    ) -> BackwardAttributionResult:
        """Traverse upstream graph paths and quote event-local backward credit."""
        source_id = _require_non_empty_string(
            source_node_id,
            "backward_attribution_source_node_id_required",
        )
        if source_id not in self._nodes:
            raise ValueError("backward_attribution_source_node_unknown")
        primary_event_id = _require_non_empty_string(
            event_id,
            "backward_attribution_event_id_required",
        )
        all_event_ids = self.collapse_event_ids(
            (primary_event_id, *(event_ids or ())),
        )
        normalized_epoch = _require_non_negative_int(
            event_epoch,
            "backward_attribution_event_epoch_must_be_non_negative_int",
        )
        budget = _require_decimal(
            event_budget_ecu,
            "backward_attribution_event_budget_invalid",
        )
        if budget <= ZERO:
            raise ValueError("backward_attribution_event_budget_must_be_positive")

        raw_scores, cycle_count, repeated_count, traversed_edges = self._collect_raw_scores(
            source_id,
            all_event_ids[0],
            normalized_epoch,
        )
        collapsed_scores = self._collapse_scores(raw_scores)
        positive_scores = tuple(
            score for score in collapsed_scores if score.raw_path_score > ZERO
        )
        score_total = sum((score.raw_path_score for score in positive_scores), ZERO)
        backward_pool = budget * BACKWARD_ATTRIBUTION_BACKWARD_POOL_SHARE_BETA
        forward_retained = budget * BACKWARD_ATTRIBUTION_FORWARD_RETAINED_SHARE
        node_cap_amount = backward_pool * BACKWARD_ATTRIBUTION_PER_NODE_CAP
        agent_cap_amount = backward_pool * BACKWARD_ATTRIBUTION_PER_AGENT_CAP
        cluster_cap_amount = backward_pool * BACKWARD_ATTRIBUTION_PER_CLUSTER_CAP

        credits: list[BackwardAttributionCreditQuote] = []
        if score_total > ZERO:
            for score in positive_scores:
                credits.append(
                    BackwardAttributionCreditQuote(
                        event_id=score.event_id,
                        upstream_artifact_id=score.upstream_artifact_id,
                        recipient_agent_id=score.recipient_agent_id,
                        depth=score.depth,
                        raw_path_score=score.raw_path_score,
                        pre_cap_credit_ecu=backward_pool
                        * score.raw_path_score
                        / score_total,
                    )
                )
        issued = sum((credit.pre_cap_credit_ecu for credit in credits), ZERO)
        return BackwardAttributionResult(
            cdl_version=BACKWARD_ATTRIBUTION_CDL_VERSION,
            event_id=all_event_ids[0],
            source_node_id=source_id,
            event_budget_ecu=budget,
            backward_pool_ecu=backward_pool,
            forward_retained_ecu=forward_retained,
            path_scores=positive_scores,
            credits=tuple(credits),
            unissued_backward_pool_ecu=backward_pool - issued,
            node_cap_amount_ecu=node_cap_amount,
            agent_cap_amount_ecu=agent_cap_amount,
            cluster_cap_amount_ecu=cluster_cap_amount,
            caps_applied=False,
            cycle_rejections=cycle_count,
            repeated_node_rejections=repeated_count,
            traversal_node_count=len(self._nodes),
            traversal_edge_count=traversed_edges,
        )

    def _collect_raw_scores(
        self,
        source_node_id: str,
        event_id: str,
        event_epoch: int,
    ) -> tuple[list[BackwardAttributionPathScore], int, int, int]:
        scores: list[BackwardAttributionPathScore] = []
        cycle_count = 0
        repeated_count = 0
        traversed_edges = 0
        stack = [
            (
                source_node_id,
                0,
                (source_node_id,),
                (),
                ONE,
            )
        ]
        while stack:
            current_node_id, depth, path_nodes, path_edge_types, confidence = stack.pop()
            for edge in self._outgoing.get(current_node_id, ()):
                traversed_edges += 1
                if traversed_edges > BACKWARD_ATTRIBUTION_MAX_TRAVERSAL_EDGES:
                    raise ValueError("backward_attribution_edge_traversal_exceeds_maximum")
                if edge.edge_type not in BACKWARD_ATTRIBUTION_ALLOWED_EDGE_TYPES:
                    continue
                next_depth = depth + 1
                if next_depth > BACKWARD_ATTRIBUTION_MAX_DEPTH:
                    continue
                if edge.target_node_id in path_nodes:
                    cycle_count += 1
                    repeated_count += 1
                    continue

                upstream_node = self._nodes[edge.target_node_id]
                next_path_nodes = (*path_nodes, edge.target_node_id)
                next_edge_types = (*path_edge_types, edge.edge_type)
                next_confidence = confidence * edge.edge_confidence
                raw_score = self._score_path(
                    upstream_node,
                    next_depth,
                    event_epoch,
                    next_confidence,
                )
                if raw_score == ZERO:
                    continue
                scores.append(
                    BackwardAttributionPathScore(
                        event_id=event_id,
                        upstream_artifact_id=upstream_node.node_id,
                        recipient_agent_id=upstream_node.recipient_agent_id,
                        depth=next_depth,
                        path_node_ids=next_path_nodes,
                        path_edge_types=next_edge_types,
                        raw_path_score=raw_score,
                        age_weight=_age_weight(
                            upstream_node.created_epoch,
                            event_epoch,
                        ),
                        status_quality_weight=upstream_node.status_quality_weight,
                        novelty_weight=_novelty_weight(upstream_node),
                        edge_confidence_weight=next_confidence,
                    )
                )
                stack.append(
                    (
                        edge.target_node_id,
                        next_depth,
                        next_path_nodes,
                        next_edge_types,
                        next_confidence,
                    )
                )
        return scores, cycle_count, repeated_count, traversed_edges

    @staticmethod
    def _score_path(
        upstream_node: BackwardAttributionNode,
        depth: int,
        event_epoch: int,
        edge_confidence_weight: Decimal,
    ) -> Decimal:
        artifact_weight = _eligible_artifact_weight(upstream_node)
        if artifact_weight == ZERO:
            return ZERO
        novelty = _novelty_weight(upstream_node)
        if novelty == ZERO:
            return ZERO
        return (
            (BACKWARD_ATTRIBUTION_DECAY_ALPHA ** depth)
            * _age_weight(upstream_node.created_epoch, event_epoch)
            * edge_confidence_weight
            * artifact_weight
            * upstream_node.status_quality_weight
            * novelty
        )

    @staticmethod
    def _collapse_scores(
        scores: list[BackwardAttributionPathScore],
    ) -> tuple[BackwardAttributionPathScore, ...]:
        by_artifact: dict[str, BackwardAttributionPathScore] = {}
        for score in sorted(
            scores,
            key=lambda item: (
                item.upstream_artifact_id,
                item.recipient_agent_id,
                item.depth,
                item.path_node_ids,
            ),
        ):
            current = by_artifact.get(score.upstream_artifact_id)
            if current is None or score.raw_path_score > current.raw_path_score:
                by_artifact[score.upstream_artifact_id] = score

        by_triple: dict[
            tuple[str, str, str],
            BackwardAttributionPathScore,
        ] = {}
        for score in by_artifact.values():
            key = (score.event_id, score.upstream_artifact_id, score.recipient_agent_id)
            current = by_triple.get(key)
            if current is None or score.raw_path_score > current.raw_path_score:
                by_triple[key] = score
        return tuple(
            sorted(
                by_triple.values(),
                key=lambda item: (item.upstream_artifact_id, item.recipient_agent_id),
            )
        )
