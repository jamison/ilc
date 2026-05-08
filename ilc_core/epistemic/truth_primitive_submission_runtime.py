"""CDL-074 truth primitive submission runtime.

Validates CDL-073 wire-format submissions for all six agent-issuable truth
primitives and returns the graph-output contract for each.  Does NOT perform
graph persistence, CID generation, or network delivery — those are Phase 873+.

Wire format (CDL-073):
    {v: 1, primitive, agent_id, epoch, payload, sig}

The six agent-issuable primitives handled here:
    assert.truth, validate.claim, contradict.assert,
    refute.claim, revise.assert, link.claim

commit.epoch is permanently excluded from agent submission (consensus-layer
only) and is rejected with token commit_epoch_agent_submission_rejected.

Phases:
    865 — assert.truth + validate.claim
    866 — contradict.assert + link.claim
    867 — refute.claim + commit.epoch rejection
    868 — revise.assert (module complete)
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

from ilc_core.protocol.primitive_type_registry import (
    ALLOWED_PRIMITIVE_TYPES,
    SYSTEM_PRIMITIVE_TYPES,
)
from ilc_core.epistemic.node_submission_runtime import EpistemicSubmissionError
from ilc_core.epistemic.node_submission_runtime import _validate_refutation_criterion as _cdl_052_validate_criterion

# ---------------------------------------------------------------------------
# Dependency and version tokens
# ---------------------------------------------------------------------------

CDL_074_DEPENDENCY = "cdl_074_truth_primitive_runtime_ratified.v0.1"
CDL_073_DEPENDENCY = "cdl_073_homoiconic_bootstrap_schema_ratified.v0.1"
CDL_052_DEPENDENCY = "cdl_052_ratified_466.v0.1"

TRUTH_PRIMITIVE_RUNTIME_VERSION = "truth_primitive_submission_runtime_868.v0.1"

# ---------------------------------------------------------------------------
# Agent-issuable primitive set (commit.epoch excluded)
# ---------------------------------------------------------------------------

AGENT_ISSUABLE_PRIMITIVES: frozenset[str] = frozenset({
    "assert.truth",
    "validate.claim",
    "contradict.assert",
    "refute.claim",
    "revise.assert",
    "link.claim",
})

_LINK_CLAIM_TYPES: frozenset[str] = frozenset({
    "cites", "elaborates", "contrasts", "instantiates", "generalizes",
})

_EPISTEMIC_TYPES: frozenset[str] = frozenset({
    "objective", "subjective", "normative", "creative_speculative",
})

_CONTRADICTION_SCOPES: frozenset[str] = frozenset({
    "logical", "empirical", "definitional",
})

_KNOWN_PRIMITIVE_TYPES: frozenset[str] = (
    frozenset(ALLOWED_PRIMITIVE_TYPES) | SYSTEM_PRIMITIVE_TYPES
)

_PROTOCOL_VERSION = 1

# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EdgeSpec:
    """A single directed edge produced by a truth primitive submission."""
    edge_type: str
    source: str   # semantic label (e.g. "new_node_id", "agent_id", ...)
    target: str


@dataclass(frozen=True)
class TruthPrimitiveResult:
    """Graph-output contract returned after a successful submission validation."""
    primitive: str
    creates_node: bool
    edges: tuple[EdgeSpec, ...]
    node_primitive_type: str | None  # None when creates_node is False


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _require(name: str, value: Any) -> Any:
    if value is None:
        raise EpistemicSubmissionError(
            f"missing_field_{name}",
            f"required field '{name}' is missing",
        )
    return value


def _require_str(name: str, obj: dict, *, min_len: int = 1) -> str:
    v = obj.get(name)
    if not isinstance(v, str) or len(v) < min_len:
        raise EpistemicSubmissionError(
            f"field_invalid_{name}",
            f"'{name}' must be a non-empty string (min length {min_len})",
        )
    return v


def _require_list(name: str, obj: dict) -> list:
    v = obj.get(name)
    if not isinstance(v, list):
        raise EpistemicSubmissionError(
            f"field_invalid_{name}",
            f"'{name}' must be an array",
        )
    return v


def _require_map(name: str, obj: dict) -> dict:
    v = obj.get(name)
    if not isinstance(v, dict):
        raise EpistemicSubmissionError(
            f"field_invalid_{name}",
            f"'{name}' must be a map/object",
        )
    return v


def _require_in(name: str, value: str, allowed: frozenset[str]) -> None:
    if value not in allowed:
        raise EpistemicSubmissionError(
            f"field_value_invalid_{name}",
            f"'{name}' value {value!r} is not in allowed set {sorted(allowed)}",
        )


def _validate_decimal_confidence(name: str, value: Any) -> None:
    """Validate a decimal string confidence value: 0 < v <= 1.0."""
    if not isinstance(value, str):
        raise EpistemicSubmissionError(
            f"field_invalid_{name}",
            f"'{name}' must be a canonical decimal string",
        )
    try:
        d = Decimal(value)
    except InvalidOperation:
        raise EpistemicSubmissionError(
            f"field_invalid_{name}",
            f"'{name}' is not a valid decimal: {value!r}",
        )
    if d <= 0 or d > 1:
        raise EpistemicSubmissionError(
            f"field_out_of_range_{name}",
            f"'{name}' must satisfy 0 < value <= 1.0, got {value!r}",
        )


def _validate_outer_envelope(submission: Any) -> dict:
    """Validate the CDL-073 outer submission envelope."""
    if not isinstance(submission, dict):
        raise EpistemicSubmissionError(
            "submission_must_be_dict",
            "submission must be a dict",
        )
    v = submission.get("v")
    if v != _PROTOCOL_VERSION:
        raise EpistemicSubmissionError(
            "protocol_version_invalid",
            f"submission.v must equal {_PROTOCOL_VERSION}, got {v!r}",
        )
    primitive = submission.get("primitive")
    if not isinstance(primitive, str) or not primitive:
        raise EpistemicSubmissionError(
            "primitive_missing",
            "submission.primitive must be a non-empty string",
        )
    # commit.epoch is rejected unconditionally for agent submissions
    if primitive == "commit.epoch":
        raise EpistemicSubmissionError(
            "commit_epoch_agent_submission_rejected",
            "commit.epoch is consensus-layer only; agent submission is rejected",
        )
    if primitive not in AGENT_ISSUABLE_PRIMITIVES:
        raise EpistemicSubmissionError(
            "primitive_unknown",
            f"unknown primitive {primitive!r}; "
            f"agent-issuable set: {sorted(AGENT_ISSUABLE_PRIMITIVES)}",
        )
    agent_id = submission.get("agent_id")
    if not isinstance(agent_id, str) or not agent_id:
        raise EpistemicSubmissionError(
            "agent_id_missing",
            "submission.agent_id must be a non-empty string",
        )
    epoch = submission.get("epoch")
    if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 0:
        raise EpistemicSubmissionError(
            "epoch_invalid",
            f"submission.epoch must be a non-negative integer, got {epoch!r}",
        )
    payload = submission.get("payload")
    if not isinstance(payload, dict):
        raise EpistemicSubmissionError(
            "payload_missing",
            "submission.payload must be a map/object",
        )
    return submission


# ---------------------------------------------------------------------------
# Phase 865 — assert.truth
# ---------------------------------------------------------------------------


def _validate_assert_truth(payload: dict) -> TruthPrimitiveResult:
    _require_map("content", payload)
    primitive_type = _require_str("primitive_type", payload)
    if primitive_type not in _KNOWN_PRIMITIVE_TYPES:
        raise EpistemicSubmissionError(
            "primitive_type_not_allowed",
            f"primitive_type {primitive_type!r} is not in ALLOWED_PRIMITIVE_TYPES "
            f"or SYSTEM_PRIMITIVE_TYPES; use a separate CDL to extend the set",
        )
    epistemic_type = _require_str("epistemic_type", payload)
    _require_in("epistemic_type", epistemic_type, _EPISTEMIC_TYPES)
    parent_node_ids = _require_list("parent_node_ids", payload)
    for i, pid in enumerate(parent_node_ids):
        if not isinstance(pid, str) or not pid:
            raise EpistemicSubmissionError(
                "parent_node_ids_invalid_entry",
                f"parent_node_ids[{i}] must be a non-empty CIDv1 string",
            )

    edges: list[EdgeSpec] = [
        EdgeSpec("asserted_by", "new_node_id", "agent_id"),
    ]
    for _ in parent_node_ids:
        edges.append(EdgeSpec("extends", "new_node_id", "parent_node_id"))

    return TruthPrimitiveResult(
        primitive="assert.truth",
        creates_node=True,
        edges=tuple(edges),
        node_primitive_type=primitive_type,
    )


# ---------------------------------------------------------------------------
# Phase 865 — validate.claim
# ---------------------------------------------------------------------------


def _validate_validate_claim(payload: dict) -> TruthPrimitiveResult:
    _require_str("target_node_id", payload)
    confidence = payload.get("confidence")
    _require("confidence", confidence)
    _validate_decimal_confidence("confidence", confidence)
    evidence_summary = _require_str("evidence_summary", payload)
    if len(evidence_summary.encode("utf-8")) > 1024:
        raise EpistemicSubmissionError(
            "evidence_summary_too_long",
            "evidence_summary must be at most 1024 bytes UTF-8",
        )
    return TruthPrimitiveResult(
        primitive="validate.claim",
        creates_node=False,
        edges=(
            EdgeSpec("validated_by", "target_node_id", "agent_id"),
        ),
        node_primitive_type=None,
    )


# ---------------------------------------------------------------------------
# Phase 866 — contradict.assert
# ---------------------------------------------------------------------------


def _validate_contradict_assert(payload: dict) -> TruthPrimitiveResult:
    node_a_id = _require_str("node_a_id", payload)
    node_b_id = _require_str("node_b_id", payload)
    if node_a_id == node_b_id:
        raise EpistemicSubmissionError(
            "contradict_assert_same_node",
            "node_a_id and node_b_id must differ; a node cannot contradict itself",
        )
    contradiction_scope = _require_str("contradiction_scope", payload)
    _require_in("contradiction_scope", contradiction_scope, _CONTRADICTION_SCOPES)
    rationale = _require_str("rationale", payload)
    if len(rationale.encode("utf-8")) > 2048:
        raise EpistemicSubmissionError(
            "rationale_too_long",
            "rationale must be at most 2048 bytes UTF-8",
        )
    return TruthPrimitiveResult(
        primitive="contradict.assert",
        creates_node=False,
        edges=(
            EdgeSpec("contradicts", "node_a_id", "node_b_id"),
        ),
        node_primitive_type=None,
    )


# ---------------------------------------------------------------------------
# Phase 866 — link.claim
# ---------------------------------------------------------------------------


def _validate_link_claim(payload: dict) -> TruthPrimitiveResult:
    source_node_id = _require_str("source_node_id", payload)
    target_node_id = _require_str("target_node_id", payload)
    if source_node_id == target_node_id:
        raise EpistemicSubmissionError(
            "link_claim_same_node",
            "source_node_id and target_node_id must differ",
        )
    link_type = _require_str("link_type", payload)
    _require_in("link_type", link_type, _LINK_CLAIM_TYPES)
    link_rationale = _require_str("link_rationale", payload)
    if len(link_rationale.encode("utf-8")) > 1024:
        raise EpistemicSubmissionError(
            "link_rationale_too_long",
            "link_rationale must be at most 1024 bytes UTF-8",
        )
    return TruthPrimitiveResult(
        primitive="link.claim",
        creates_node=False,
        edges=(
            EdgeSpec(link_type, "source_node_id", "target_node_id"),
        ),
        node_primitive_type=None,
    )


# ---------------------------------------------------------------------------
# Phase 867 — refute.claim
# ---------------------------------------------------------------------------


def _validate_refute_claim(payload: dict) -> TruthPrimitiveResult:
    _require_str("target_node_id", payload)
    criterion = _require_map("refutation_criterion", payload)
    # CDL-052 integration: check has_falsifiable_test before delegating to the
    # Popperian gate validator — gives a specific token instead of the generic
    # MALFORMED_REFUTATION_CRITERION from the gate path.
    if criterion.get("has_falsifiable_test") is not True:
        raise EpistemicSubmissionError(
            "refute_claim_has_falsifiable_test_required",
            "refutation_criterion.has_falsifiable_test must be true; "
            "submissions with false are rejected (CDL-052)",
        )
    _cdl_052_validate_criterion(criterion)
    evidence_node_ids = _require_list("evidence_node_ids", payload)
    for i, eid in enumerate(evidence_node_ids):
        if not isinstance(eid, str) or not eid:
            raise EpistemicSubmissionError(
                "evidence_node_ids_invalid_entry",
                f"evidence_node_ids[{i}] must be a non-empty CIDv1 string",
            )
    edges: list[EdgeSpec] = [
        EdgeSpec("refuted_by", "target_node_id", "agent_id"),
    ]
    for _ in evidence_node_ids:
        edges.append(EdgeSpec("supported_by", "refutation_context", "evidence_node_id"))

    return TruthPrimitiveResult(
        primitive="refute.claim",
        creates_node=False,
        edges=tuple(edges),
        node_primitive_type=None,
    )


# ---------------------------------------------------------------------------
# Phase 868 — revise.assert
# ---------------------------------------------------------------------------


def _validate_revise_assert(payload: dict) -> TruthPrimitiveResult:
    _require_str("source_node_id", payload)
    revised_content = _require_map("revised_content", payload)
    # revised_content must carry a primitive_type for the new node
    revised_primitive_type = revised_content.get("primitive_type")
    if not isinstance(revised_primitive_type, str) or not revised_primitive_type:
        raise EpistemicSubmissionError(
            "revised_content_missing_primitive_type",
            "revised_content must contain a non-empty primitive_type field",
        )
    if revised_primitive_type not in _KNOWN_PRIMITIVE_TYPES:
        raise EpistemicSubmissionError(
            "revised_primitive_type_not_allowed",
            f"revised_content.primitive_type {revised_primitive_type!r} is not "
            f"in ALLOWED_PRIMITIVE_TYPES or SYSTEM_PRIMITIVE_TYPES",
        )
    revision_rationale = _require_str("revision_rationale", payload)
    if len(revision_rationale.encode("utf-8")) > 2048:
        raise EpistemicSubmissionError(
            "revision_rationale_too_long",
            "revision_rationale must be at most 2048 bytes UTF-8",
        )
    return TruthPrimitiveResult(
        primitive="revise.assert",
        creates_node=True,
        edges=(
            EdgeSpec("asserted_by", "new_node_id", "agent_id"),
            EdgeSpec("revision_of", "new_node_id", "source_node_id"),
            EdgeSpec("revised_by", "source_node_id", "new_node_id"),
        ),
        node_primitive_type=revised_primitive_type,
    )


# ---------------------------------------------------------------------------
# Primary dispatcher
# ---------------------------------------------------------------------------

_HANDLERS = {
    "assert.truth":      _validate_assert_truth,
    "validate.claim":    _validate_validate_claim,
    "contradict.assert": _validate_contradict_assert,
    "link.claim":        _validate_link_claim,
    "refute.claim":      _validate_refute_claim,
    "revise.assert":     _validate_revise_assert,
}


def validate_truth_primitive_submission(submission: Any) -> TruthPrimitiveResult:
    """Validate a CDL-073 wire-format truth primitive submission.

    Validates the outer envelope, routes to the per-primitive handler, and
    returns a TruthPrimitiveResult describing the graph-output contract.

    Raises EpistemicSubmissionError on any validation failure.
    commit.epoch is always rejected with token commit_epoch_agent_submission_rejected.
    """
    envelope = _validate_outer_envelope(submission)
    primitive = envelope["primitive"]
    payload = envelope["payload"]
    handler = _HANDLERS[primitive]
    return handler(payload)
