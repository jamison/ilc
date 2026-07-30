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
BACKWARD_ATTRIBUTION_SYBIL_DIVERSITY_GUARD_CDL_GAP = (
    "no CDL-108 locked threshold; omitted from Phase 1595h; requires governance "
    "phase to define and lock threshold before implementation"
)

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
    typed_path_weight: Decimal
    artifact_weight: Decimal
    status_quality_weight: Decimal
    novelty_weight: Decimal
    edge_confidence_weight: Decimal
    path_edge_confidences: tuple[Decimal, ...]


@dataclass(frozen=True)
class BackwardAttributionCreditQuote:
    """Pre-cap traversal quote for an upstream artifact.

    The pre-cap quote remains inspectable after GAP-ECU-04b. The authoritative
    capped credit is emitted separately as BackwardAttributionFinalCredit.
    """

    event_id: str
    upstream_artifact_id: str
    recipient_agent_id: str
    depth: int
    raw_path_score: Decimal
    pre_cap_credit_ecu: Decimal


@dataclass(frozen=True)
class BackwardAttributionFinalCredit:
    """Final CDL-108 credit after event-local anti-gaming caps."""

    event_id: str
    upstream_artifact_id: str
    recipient_agent_id: str
    depth: int
    raw_path_score: Decimal
    pre_cap_credit_ecu: Decimal
    final_credit_ecu: Decimal
    clipped_residual_ecu: Decimal
    node_cap_applied: bool
    agent_cap_applied: bool
    cluster_cap_applied: bool
    cluster_id: str


@dataclass(frozen=True)
class BackwardAttributionResult:
    """Deterministic output of one backward traversal event quote."""

    cdl_version: str
    score_formula: str
    event_id: str
    source_node_id: str
    event_budget_ecu: Decimal
    backward_pool_ecu: Decimal
    forward_retained_ecu: Decimal
    path_scores: tuple[BackwardAttributionPathScore, ...]
    credits: tuple[BackwardAttributionCreditQuote, ...]
    final_credits: tuple[BackwardAttributionFinalCredit, ...]
    unissued_backward_pool_ecu: Decimal
    node_cap_amount_ecu: Decimal
    agent_cap_amount_ecu: Decimal
    cluster_cap_amount_ecu: Decimal
    caps_applied: bool
    sybil_diversity_guard_cdl_gap: str
    cycle_rejections: int
    repeated_node_rejections: int
    traversal_node_count: int
    traversal_edge_count: int
    loaded_node_count: int
    loaded_edge_count: int


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


def _require_bool(value: object, token: str) -> bool:
    if type(value) is not bool:
        raise ValueError(token)
    return value


def _canonical_edge_type(value: object) -> str:
    raw = _require_non_empty_string(value, "backward_attribution_edge_type_required")
    return raw.strip().upper()


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


def _node_from_mapping(node_id: str, value: object) -> BackwardAttributionNode:
    normalized_node_id = _require_non_empty_string(
        node_id,
        "backward_attribution_node_id_required",
    )
    if isinstance(value, BackwardAttributionNode):
        value_node_id = _require_non_empty_string(
            value.node_id,
            "backward_attribution_node_id_required",
        )
        if value_node_id != normalized_node_id:
            raise ValueError("backward_attribution_node_id_mismatch")
        return BackwardAttributionNode(
            node_id=value_node_id,
            artifact_type=_require_non_empty_string(
                value.artifact_type,
                "backward_attribution_artifact_type_required",
            ),
            recipient_agent_id=_require_non_empty_string(
                value.recipient_agent_id,
                "backward_attribution_recipient_agent_id_required",
            ),
            created_epoch=_require_non_negative_int(
                value.created_epoch,
                "backward_attribution_created_epoch_must_be_non_negative_int",
            ),
            status_quality_weight=_require_factor(
                value.status_quality_weight,
                "backward_attribution_status_quality_weight_invalid",
            ),
            novelty_score=_require_factor(
                value.novelty_score,
                "backward_attribution_novelty_score_invalid",
            ),
            refuted=_require_bool(
                value.refuted,
                "backward_attribution_refuted_must_be_bool",
            ),
            phi_suppressed=_require_bool(
                value.phi_suppressed,
                "backward_attribution_phi_suppressed_must_be_bool",
            ),
            private_artifact=_require_bool(
                value.private_artifact,
                "backward_attribution_private_artifact_must_be_bool",
            ),
            public_rc_excluded=_require_bool(
                value.public_rc_excluded,
                "backward_attribution_public_rc_excluded_must_be_bool",
            ),
            governance_control=_require_bool(
                value.governance_control,
                "backward_attribution_governance_control_must_be_bool",
            ),
            unverified_mirror_metadata=_require_bool(
                value.unverified_mirror_metadata,
                "backward_attribution_unverified_mirror_metadata_must_be_bool",
            ),
        )
    if not isinstance(value, Mapping):
        raise ValueError("backward_attribution_node_must_be_mapping")
    return BackwardAttributionNode(
        node_id=normalized_node_id,
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
        refuted=_require_bool(
            value.get("refuted", False),
            "backward_attribution_refuted_must_be_bool",
        ),
        phi_suppressed=_require_bool(
            value.get("phi_suppressed", False),
            "backward_attribution_phi_suppressed_must_be_bool",
        ),
        private_artifact=_require_bool(
            value.get("private_artifact", False),
            "backward_attribution_private_artifact_must_be_bool",
        ),
        public_rc_excluded=_require_bool(
            value.get("public_rc_excluded", False),
            "backward_attribution_public_rc_excluded_must_be_bool",
        ),
        governance_control=_require_bool(
            value.get("governance_control", False),
            "backward_attribution_governance_control_must_be_bool",
        ),
        unverified_mirror_metadata=_require_bool(
            value.get("unverified_mirror_metadata", False),
            "backward_attribution_unverified_mirror_metadata_must_be_bool",
        ),
    )


def _edge_from_mapping(value: object) -> BackwardAttributionEdge:
    if isinstance(value, BackwardAttributionEdge):
        return BackwardAttributionEdge(
            source_node_id=_require_non_empty_string(
                value.source_node_id,
                "backward_attribution_edge_source_required",
            ),
            target_node_id=_require_non_empty_string(
                value.target_node_id,
                "backward_attribution_edge_target_required",
            ),
            edge_type=_canonical_edge_type(value.edge_type),
            edge_confidence=_require_factor(
                value.edge_confidence,
                "backward_attribution_edge_confidence_invalid",
            ),
        )
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
        if not isinstance(nodes, Mapping):
            raise ValueError("backward_attribution_nodes_must_be_mapping")
        if not isinstance(edges, (list, tuple)):
            raise ValueError("backward_attribution_edges_must_be_sequence")
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
        self._cluster_ids = self._compute_mutual_citation_cluster_ids()

    @staticmethod
    def collapse_event_ids(event_ids: tuple[str, ...] | list[str]) -> tuple[str, ...]:
        """Compatibility wrapper for the module-level helper."""
        return collapse_event_ids(event_ids)

    def traverse(
        self,
        source_node_id: str,
        *,
        event_id: str,
        event_budget_ecu: Decimal | int | str,
        event_epoch: int,
        event_ids: tuple[str, ...] | list[str] | None = None,
        apply_antigaming_caps: bool = False,
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

        (
            raw_scores,
            cycle_count,
            repeated_count,
            traversed_nodes,
            traversed_edges,
        ) = self._collect_raw_scores(source_id, all_event_ids[0], normalized_epoch)
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
            running_credit = ZERO
            for score in positive_scores[:-1]:
                pre_cap_credit = backward_pool * score.raw_path_score / score_total
                running_credit += pre_cap_credit
                credits.append(
                    BackwardAttributionCreditQuote(
                        event_id=score.event_id,
                        upstream_artifact_id=score.upstream_artifact_id,
                        recipient_agent_id=score.recipient_agent_id,
                        depth=score.depth,
                        raw_path_score=score.raw_path_score,
                        pre_cap_credit_ecu=pre_cap_credit,
                    )
                )
            last_score = positive_scores[-1]
            last_credit = backward_pool - running_credit
            if last_credit < ZERO:
                raise ValueError("backward_attribution_credit_allocation_overflow")
            credits.append(
                BackwardAttributionCreditQuote(
                    event_id=last_score.event_id,
                    upstream_artifact_id=last_score.upstream_artifact_id,
                    recipient_agent_id=last_score.recipient_agent_id,
                    depth=last_score.depth,
                    raw_path_score=last_score.raw_path_score,
                    pre_cap_credit_ecu=last_credit,
                )
            )
        issued = sum((credit.pre_cap_credit_ecu for credit in credits), ZERO)
        final_credits, issued_final = self._apply_antigaming_caps(
            credits=tuple(credits),
            apply_caps=apply_antigaming_caps,
            node_cap_amount=node_cap_amount,
            agent_cap_amount=agent_cap_amount,
            cluster_cap_amount=cluster_cap_amount,
        )
        issued_authoritative = issued_final if apply_antigaming_caps else issued
        return BackwardAttributionResult(
            cdl_version=BACKWARD_ATTRIBUTION_CDL_VERSION,
            score_formula=BACKWARD_ATTRIBUTION_SCORE_FORMULA,
            event_id=all_event_ids[0],
            source_node_id=source_id,
            event_budget_ecu=budget,
            backward_pool_ecu=backward_pool,
            forward_retained_ecu=forward_retained,
            path_scores=positive_scores,
            credits=tuple(credits),
            final_credits=final_credits,
            unissued_backward_pool_ecu=backward_pool - issued_authoritative,
            node_cap_amount_ecu=node_cap_amount,
            agent_cap_amount_ecu=agent_cap_amount,
            cluster_cap_amount_ecu=cluster_cap_amount,
            caps_applied=apply_antigaming_caps,
            sybil_diversity_guard_cdl_gap=BACKWARD_ATTRIBUTION_SYBIL_DIVERSITY_GUARD_CDL_GAP,
            cycle_rejections=cycle_count,
            repeated_node_rejections=repeated_count,
            traversal_node_count=traversed_nodes,
            traversal_edge_count=traversed_edges,
            loaded_node_count=len(self._nodes),
            loaded_edge_count=len(self._edges),
        )

    def _apply_antigaming_caps(
        self,
        *,
        credits: tuple[BackwardAttributionCreditQuote, ...],
        apply_caps: bool,
        node_cap_amount: Decimal,
        agent_cap_amount: Decimal,
        cluster_cap_amount: Decimal,
    ) -> tuple[tuple[BackwardAttributionFinalCredit, ...], Decimal]:
        node_issued: dict[str, Decimal] = {}
        agent_issued: dict[str, Decimal] = {}
        cluster_issued: dict[str, Decimal] = {}
        final_credits: list[BackwardAttributionFinalCredit] = []
        total_final = ZERO

        for credit in credits:
            cluster_id = self._cluster_ids.get(
                credit.upstream_artifact_id,
                f"singleton:{credit.upstream_artifact_id}",
            )
            node_remaining = node_cap_amount - node_issued.get(
                credit.upstream_artifact_id, ZERO
            )
            agent_remaining = agent_cap_amount - agent_issued.get(
                credit.recipient_agent_id, ZERO
            )
            cluster_remaining = cluster_cap_amount - cluster_issued.get(cluster_id, ZERO)

            if apply_caps:
                final_credit = min(
                    credit.pre_cap_credit_ecu,
                    max(node_remaining, ZERO),
                    max(agent_remaining, ZERO),
                    max(cluster_remaining, ZERO),
                )
            else:
                final_credit = credit.pre_cap_credit_ecu

            clipped_residual = credit.pre_cap_credit_ecu - final_credit
            if final_credit > ZERO:
                node_issued[credit.upstream_artifact_id] = (
                    node_issued.get(credit.upstream_artifact_id, ZERO) + final_credit
                )
                agent_issued[credit.recipient_agent_id] = (
                    agent_issued.get(credit.recipient_agent_id, ZERO) + final_credit
                )
                cluster_issued[cluster_id] = (
                    cluster_issued.get(cluster_id, ZERO) + final_credit
                )
                total_final += final_credit

            final_credits.append(
                BackwardAttributionFinalCredit(
                    event_id=credit.event_id,
                    upstream_artifact_id=credit.upstream_artifact_id,
                    recipient_agent_id=credit.recipient_agent_id,
                    depth=credit.depth,
                    raw_path_score=credit.raw_path_score,
                    pre_cap_credit_ecu=credit.pre_cap_credit_ecu,
                    final_credit_ecu=final_credit,
                    clipped_residual_ecu=clipped_residual,
                    node_cap_applied=apply_caps
                    and credit.pre_cap_credit_ecu > max(node_remaining, ZERO),
                    agent_cap_applied=apply_caps
                    and credit.pre_cap_credit_ecu > max(agent_remaining, ZERO),
                    cluster_cap_applied=apply_caps
                    and credit.pre_cap_credit_ecu > max(cluster_remaining, ZERO),
                    cluster_id=cluster_id,
                )
            )

        return tuple(final_credits), total_final

    def _compute_mutual_citation_cluster_ids(self) -> dict[str, str]:
        parent: dict[str, str] = {node_id: node_id for node_id in self._nodes}

        def find(node_id: str) -> str:
            parent.setdefault(node_id, node_id)
            while parent[node_id] != node_id:
                parent[node_id] = parent[parent[node_id]]
                node_id = parent[node_id]
            return node_id

        def union(left: str, right: str) -> None:
            left_root = find(left)
            right_root = find(right)
            if left_root == right_root:
                return
            if left_root < right_root:
                parent[right_root] = left_root
            else:
                parent[left_root] = right_root

        directed_pairs = {
            (edge.source_node_id, edge.target_node_id)
            for edge in self._edges
            if edge.edge_type in BACKWARD_ATTRIBUTION_ALLOWED_EDGE_TYPES
        }
        for source_id, target_id in sorted(directed_pairs):
            if (target_id, source_id) in directed_pairs:
                union(source_id, target_id)

        components: dict[str, list[str]] = {}
        for node_id in sorted(parent):
            components.setdefault(find(node_id), []).append(node_id)

        cluster_ids: dict[str, str] = {}
        for members in components.values():
            if len(members) <= 1:
                cluster_ids[members[0]] = f"singleton:{members[0]}"
                continue
            cluster_id = "cluster:" + "|".join(sorted(members))
            for member in members:
                cluster_ids[member] = cluster_id
        return cluster_ids

    def _collect_raw_scores(
        self,
        source_node_id: str,
        event_id: str,
        event_epoch: int,
    ) -> tuple[list[BackwardAttributionPathScore], int, int, int, int]:
        scores: list[BackwardAttributionPathScore] = []
        cycle_count = 0
        repeated_count = 0
        traversed_node_ids = {source_node_id}
        traversed_edges = 0
        stack = [
            (
                source_node_id,
                0,
                (source_node_id,),
                (),
                ONE,
                (),
            )
        ]
        while stack:
            (
                current_node_id,
                depth,
                path_nodes,
                path_edge_types,
                confidence,
                path_edge_confidences,
            ) = stack.pop()
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
                    if edge.target_node_id == source_node_id:
                        cycle_count += 1
                    else:
                        repeated_count += 1
                    continue

                upstream_node = self._nodes[edge.target_node_id]
                traversed_node_ids.add(edge.target_node_id)
                next_path_nodes = (*path_nodes, edge.target_node_id)
                next_edge_types = (*path_edge_types, edge.edge_type)
                next_confidence = confidence * edge.edge_confidence
                next_edge_confidences = (*path_edge_confidences, edge.edge_confidence)
                raw_score = self._score_path(
                    upstream_node,
                    next_depth,
                    event_epoch,
                    next_confidence,
                )
                if raw_score > ZERO:
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
                            typed_path_weight=ONE,
                            artifact_weight=ONE,
                            status_quality_weight=upstream_node.status_quality_weight,
                            novelty_weight=_novelty_weight(upstream_node),
                            edge_confidence_weight=next_confidence,
                            path_edge_confidences=next_edge_confidences,
                        )
                    )
                # CDL-108 scores each upstream artifact as a terminal. A node
                # that earns zero credit remains a valid routing hop through
                # typed edges, so foundational upstream work is not erased by
                # a weak or excluded intermediate artifact.
                if next_depth < BACKWARD_ATTRIBUTION_MAX_DEPTH:
                    stack.append(
                        (
                            edge.target_node_id,
                            next_depth,
                            next_path_nodes,
                            next_edge_types,
                            next_confidence,
                            next_edge_confidences,
                        )
                    )
        return scores, cycle_count, repeated_count, len(traversed_node_ids), traversed_edges

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
