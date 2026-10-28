# SPDX-License-Identifier: AGPL-3.0-only
"""Bounded advisory candidate selection for local Sufficiency fixtures.

Model output is never authorization or proof. The deterministic evaluator owns
eligibility, and every non-fixture backend remains behind a default-off guard.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Callable, Mapping, Protocol


MODEL_SELECTOR_ENABLED = False

MAX_CANDIDATES = 64
MAX_IDENTIFIER_LENGTH = 256
MAX_EVIDENCE_REFS = 16
MAX_CONSTRAINTS = 32
MAX_ADVISORY_FIELDS = 16
MAX_ADVISORY_STRING_LENGTH = 1_024
OUTCOMES = frozenset(
    {
        "selected",
        "abstained",
        "backend_failed",
        "unknown_candidate",
        "stale_candidate",
        "ineligible_candidate",
    }
)


class ModelSelectorError(ValueError):
    """Base class for stable selector failures."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class ModelSelectorGuardError(ModelSelectorError):
    """A non-fixture backend reached the default-off production boundary."""


class ModelSelectorValidationError(ModelSelectorError):
    """The request, candidate set, backend response, or evaluator was invalid."""


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    candidate_version: str
    operation_ref: str
    policy_ref: str
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in (
            "candidate_id",
            "candidate_version",
            "operation_ref",
            "policy_ref",
        ):
            _require_identifier(getattr(self, name), name)
        if type(self.evidence_refs) is not tuple or len(self.evidence_refs) > MAX_EVIDENCE_REFS:
            raise ModelSelectorValidationError("candidate_evidence_refs_invalid")
        if len(set(self.evidence_refs)) != len(self.evidence_refs):
            raise ModelSelectorValidationError("candidate_evidence_ref_duplicate")
        for ref in self.evidence_refs:
            _require_identifier(ref, "candidate_evidence_ref")


@dataclass(frozen=True)
class SelectionRequest:
    request_id: str
    operation_ref: str
    policy_ref: str
    current_tick: int
    constraints: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        for name in ("request_id", "operation_ref", "policy_ref"):
            _require_identifier(getattr(self, name), name)
        _require_nonnegative_int(self.current_tick, "current_tick")
        if type(self.constraints) is not tuple or len(self.constraints) > MAX_CONSTRAINTS:
            raise ModelSelectorValidationError("request_constraints_invalid")
        names: set[str] = set()
        for item in self.constraints:
            if type(item) is not tuple or len(item) != 2:
                raise ModelSelectorValidationError("request_constraint_shape_invalid")
            name, value = item
            _require_identifier(name, "request_constraint_name")
            _require_identifier(value, "request_constraint_value")
            if name in names:
                raise ModelSelectorValidationError("request_constraint_duplicate")
            names.add(name)


@dataclass(frozen=True)
class EligibilityDecision:
    eligible: bool
    reason_code: str
    evidence_refs: tuple[str, ...]
    cost_units: int

    def __post_init__(self) -> None:
        if type(self.eligible) is not bool:
            raise ModelSelectorValidationError("eligibility_flag_invalid")
        _require_identifier(self.reason_code, "eligibility_reason_code")
        if type(self.evidence_refs) is not tuple or len(self.evidence_refs) > MAX_EVIDENCE_REFS:
            raise ModelSelectorValidationError("eligibility_evidence_refs_invalid")
        if len(set(self.evidence_refs)) != len(self.evidence_refs):
            raise ModelSelectorValidationError("eligibility_evidence_ref_duplicate")
        for ref in self.evidence_refs:
            _require_identifier(ref, "eligibility_evidence_ref")
        _require_nonnegative_int(self.cost_units, "eligibility_cost_units")


@dataclass(frozen=True)
class ModelProposal:
    candidate_id: str | None
    candidate_version: str | None
    advisory_metadata: Mapping[str, Any] = field(default_factory=dict)
    reported_cost_units: int = 0
    reported_bytes: int = 0


class ModelBackend(Protocol):
    def propose(
        self,
        candidates: tuple[Candidate, ...],
        request: SelectionRequest,
    ) -> ModelProposal:
        """Return an advisory proposal from the supplied immutable eligible set."""


class LocalFixtureModelBackend:
    """Explicit local capability used by deterministic tests only."""

    def __init__(
        self,
        proposal: ModelProposal | None = None,
        *,
        failure: Exception | None = None,
    ) -> None:
        if proposal is not None and failure is not None:
            raise ModelSelectorValidationError("fixture_backend_configuration_invalid")
        self._proposal = proposal or ModelProposal(None, None)
        self._failure = failure
        self.calls = 0
        self.last_candidate_ids: tuple[str, ...] = ()

    def propose(
        self,
        candidates: tuple[Candidate, ...],
        request: SelectionRequest,
    ) -> ModelProposal:
        del request
        self.calls += 1
        self.last_candidate_ids = tuple(item.candidate_id for item in candidates)
        if self._failure is not None:
            raise self._failure
        return self._proposal


EligibilityEvaluator = Callable[[Candidate, SelectionRequest], EligibilityDecision]


def select_candidate(
    *,
    candidates: tuple[Candidate, ...],
    request: SelectionRequest,
    backend: ModelBackend,
    evaluate_eligibility: EligibilityEvaluator,
) -> dict[str, Any]:
    """Select advisably, then deterministically recheck the proposed candidate."""

    _validate_inputs(candidates, request, backend, evaluate_eligibility)
    if type(backend) is not LocalFixtureModelBackend and not MODEL_SELECTOR_ENABLED:
        raise ModelSelectorGuardError("model_selector_not_enabled")

    fingerprint_before = candidate_set_fingerprint(candidates)
    candidate_by_id = {candidate.candidate_id: candidate for candidate in candidates}
    prefilter: dict[str, EligibilityDecision] = {}
    eligibility_checks = 0
    eligibility_cost_units = 0
    for candidate in candidates:
        decision = _evaluate(evaluate_eligibility, candidate, request)
        prefilter[candidate.candidate_id] = decision
        eligibility_checks += 1
        eligibility_cost_units += decision.cost_units
    eligible_candidates = tuple(
        candidate for candidate in candidates if prefilter[candidate.candidate_id].eligible
    )
    if not eligible_candidates:
        return _result(
            outcome="abstained",
            reason_code="no_deterministically_eligible_candidates",
            fingerprint=fingerprint_before,
            selected=None,
            proposal=None,
            eligibility=None,
            model_calls=0,
            eligibility_checks=eligibility_checks,
            eligibility_cost_units=eligibility_cost_units,
        )

    try:
        proposal = backend.propose(eligible_candidates, request)
    except Exception:
        return _result(
            outcome="backend_failed",
            reason_code="model_backend_failed",
            fingerprint=fingerprint_before,
            selected=None,
            proposal=None,
            eligibility=None,
            model_calls=1,
            eligibility_checks=eligibility_checks,
            eligibility_cost_units=eligibility_cost_units,
        )

    if candidate_set_fingerprint(candidates) != fingerprint_before:
        raise ModelSelectorValidationError("candidate_set_mutated_during_backend_call")
    validated_proposal = _validate_proposal(proposal)
    if validated_proposal is None:
        return _result(
            outcome="unknown_candidate",
            reason_code="malformed_backend_output",
            fingerprint=fingerprint_before,
            selected=None,
            proposal=None,
            eligibility=None,
            model_calls=1,
            eligibility_checks=eligibility_checks,
            eligibility_cost_units=eligibility_cost_units,
        )
    proposal = validated_proposal
    if proposal.candidate_id is None:
        return _result(
            outcome="abstained",
            reason_code="backend_abstained",
            fingerprint=fingerprint_before,
            selected=None,
            proposal=proposal,
            eligibility=None,
            model_calls=1,
            eligibility_checks=eligibility_checks,
            eligibility_cost_units=eligibility_cost_units,
        )
    selected = candidate_by_id.get(proposal.candidate_id)
    if selected is None:
        return _result(
            outcome="unknown_candidate",
            reason_code="proposal_candidate_not_in_pinned_set",
            fingerprint=fingerprint_before,
            selected=None,
            proposal=proposal,
            eligibility=None,
            model_calls=1,
            eligibility_checks=eligibility_checks,
            eligibility_cost_units=eligibility_cost_units,
        )
    if proposal.candidate_version != selected.candidate_version:
        return _result(
            outcome="stale_candidate",
            reason_code="proposal_candidate_version_mismatch",
            fingerprint=fingerprint_before,
            selected=selected,
            proposal=proposal,
            eligibility=None,
            model_calls=1,
            eligibility_checks=eligibility_checks,
            eligibility_cost_units=eligibility_cost_units,
        )

    final_eligibility = _evaluate(evaluate_eligibility, selected, request)
    eligibility_checks += 1
    eligibility_cost_units += final_eligibility.cost_units
    if not final_eligibility.eligible:
        return _result(
            outcome="ineligible_candidate",
            reason_code=final_eligibility.reason_code,
            fingerprint=fingerprint_before,
            selected=selected,
            proposal=proposal,
            eligibility=final_eligibility,
            model_calls=1,
            eligibility_checks=eligibility_checks,
            eligibility_cost_units=eligibility_cost_units,
        )
    return _result(
        outcome="selected",
        reason_code="deterministic_eligibility_recheck_passed",
        fingerprint=fingerprint_before,
        selected=selected,
        proposal=proposal,
        eligibility=final_eligibility,
        model_calls=1,
        eligibility_checks=eligibility_checks,
        eligibility_cost_units=eligibility_cost_units,
    )


def candidate_set_fingerprint(candidates: tuple[Candidate, ...]) -> str:
    payload = [
        {
            "candidate_id": item.candidate_id,
            "candidate_version": item.candidate_version,
            "evidence_refs": list(item.evidence_refs),
            "operation_ref": item.operation_ref,
            "policy_ref": item.policy_ref,
        }
        for item in candidates
    ]
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(b"ilc.sufficiency.candidate-set.v0\x00" + encoded).hexdigest()


def _validate_inputs(
    candidates: tuple[Candidate, ...],
    request: SelectionRequest,
    backend: ModelBackend,
    evaluate_eligibility: EligibilityEvaluator,
) -> None:
    if type(candidates) is not tuple or len(candidates) > MAX_CANDIDATES:
        raise ModelSelectorValidationError("candidate_set_invalid")
    if not isinstance(request, SelectionRequest):
        raise ModelSelectorValidationError("selection_request_type_invalid")
    if not callable(getattr(backend, "propose", None)):
        raise ModelSelectorValidationError("model_backend_invalid")
    if not callable(evaluate_eligibility):
        raise ModelSelectorValidationError("eligibility_evaluator_invalid")
    seen: set[str] = set()
    for candidate in candidates:
        if not isinstance(candidate, Candidate):
            raise ModelSelectorValidationError("candidate_type_invalid")
        if candidate.candidate_id in seen:
            raise ModelSelectorValidationError("candidate_id_duplicate")
        seen.add(candidate.candidate_id)


def _evaluate(
    evaluator: EligibilityEvaluator,
    candidate: Candidate,
    request: SelectionRequest,
) -> EligibilityDecision:
    try:
        decision = evaluator(candidate, request)
    except ModelSelectorError:
        raise
    except Exception as exc:
        raise ModelSelectorValidationError("eligibility_evaluator_failed") from exc
    if not isinstance(decision, EligibilityDecision):
        raise ModelSelectorValidationError("eligibility_decision_type_invalid")
    return decision


def _validate_proposal(proposal: Any) -> ModelProposal | None:
    if not isinstance(proposal, ModelProposal):
        return None
    if proposal.candidate_id is None:
        if proposal.candidate_version is not None:
            return None
    else:
        try:
            _require_identifier(proposal.candidate_id, "proposal_candidate_id")
            _require_identifier(proposal.candidate_version, "proposal_candidate_version")
        except ModelSelectorValidationError:
            return None
    try:
        _require_nonnegative_int(proposal.reported_cost_units, "reported_cost_units")
        _require_nonnegative_int(proposal.reported_bytes, "reported_bytes")
        advisory = _validate_advisory_metadata(proposal.advisory_metadata)
    except ModelSelectorValidationError:
        return None
    return ModelProposal(
        proposal.candidate_id,
        proposal.candidate_version,
        MappingProxyType(advisory),
        proposal.reported_cost_units,
        proposal.reported_bytes,
    )


def _validate_advisory_metadata(value: Mapping[str, Any]) -> dict[str, Any]:
    if type(value) is not dict or len(value) > MAX_ADVISORY_FIELDS:
        raise ModelSelectorValidationError("advisory_metadata_invalid")
    result: dict[str, Any] = {}
    for key, item in value.items():
        _require_identifier(key, "advisory_metadata_key")
        _validate_advisory_value(item)
        result[key] = item
    return result


def _validate_advisory_value(value: Any) -> None:
    if type(value) is str:
        if len(value) > MAX_ADVISORY_STRING_LENGTH:
            raise ModelSelectorValidationError("advisory_metadata_string_too_long")
        return
    if type(value) is int:
        if abs(value) > 2**53:
            raise ModelSelectorValidationError("advisory_metadata_integer_too_large")
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise ModelSelectorValidationError("advisory_metadata_non_finite")
        return
    if type(value) is bool or value is None:
        return
    raise ModelSelectorValidationError("advisory_metadata_value_invalid")


def _result(
    *,
    outcome: str,
    reason_code: str,
    fingerprint: str,
    selected: Candidate | None,
    proposal: ModelProposal | None,
    eligibility: EligibilityDecision | None,
    model_calls: int,
    eligibility_checks: int,
    eligibility_cost_units: int,
) -> dict[str, Any]:
    if outcome not in OUTCOMES:
        raise ModelSelectorValidationError("selector_outcome_invalid")
    advisory = dict(proposal.advisory_metadata) if proposal is not None else {}
    return {
        "schema_version": "sufficiency_model_selection_result_v0",
        "outcome": outcome,
        "reason_code": reason_code,
        "candidate_set_fingerprint": fingerprint,
        "selected_candidate_id": selected.candidate_id if selected is not None else None,
        "selected_candidate_version": selected.candidate_version if selected is not None else None,
        "advisory": advisory,
        "eligibility_evidence": list(eligibility.evidence_refs) if eligibility else [],
        "overhead": {
            "model_backend": {
                "calls": model_calls,
                "reported_cost_units": proposal.reported_cost_units if proposal else 0,
                "reported_bytes": proposal.reported_bytes if proposal else 0,
            },
            "deterministic_eligibility": {
                "checks": eligibility_checks,
                "cost_units": eligibility_cost_units,
            },
        },
        "fallback_authorized": False,
        "canonical_genesis_lineage": "local_only_not_applicable",
    }


def _require_identifier(value: Any, field_name: str) -> None:
    if type(value) is not str or not value or len(value) > MAX_IDENTIFIER_LENGTH:
        raise ModelSelectorValidationError(f"{field_name}_invalid")
    if any(ord(char) < 0x20 for char in value):
        raise ModelSelectorValidationError(f"{field_name}_invalid")


def _require_nonnegative_int(value: Any, field_name: str) -> None:
    if type(value) is not int or value < 0 or value > 2**53:
        raise ModelSelectorValidationError(f"{field_name}_invalid")
