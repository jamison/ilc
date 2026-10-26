from __future__ import annotations

from dataclasses import FrozenInstanceError
from types import MappingProxyType

import pytest

from ilc_core.sufficiency.model_selector import (
    MAX_CANDIDATES,
    Candidate,
    EligibilityDecision,
    LocalFixtureModelBackend,
    ModelProposal,
    ModelSelectorGuardError,
    ModelSelectorValidationError,
    SelectionRequest,
    candidate_set_fingerprint,
    select_candidate,
)


def candidate(candidate_id: str = "exact", version: str = "1") -> Candidate:
    return Candidate(
        candidate_id=candidate_id,
        candidate_version=version,
        operation_ref="fixture:operation:attention@1",
        policy_ref="fixture:policy:local",
        evidence_refs=(f"fixture:evidence:{candidate_id}",),
    )


def request() -> SelectionRequest:
    return SelectionRequest(
        request_id="fixture:request:1",
        operation_ref="fixture:operation:attention@1",
        policy_ref="fixture:policy:local",
        current_tick=10,
        constraints=(("approximation", "exact_only"),),
    )


def eligible(item: Candidate, selection_request: SelectionRequest) -> EligibilityDecision:
    allowed = (
        item.operation_ref == selection_request.operation_ref
        and item.policy_ref == selection_request.policy_ref
        and item.candidate_id != "blocked"
    )
    return EligibilityDecision(
        eligible=allowed,
        reason_code="eligible" if allowed else "candidate_not_eligible",
        evidence_refs=("fixture:eligibility:deterministic",),
        cost_units=3,
    )


def run(proposal: ModelProposal, candidates: tuple[Candidate, ...] | None = None):
    backend = LocalFixtureModelBackend(proposal)
    result = select_candidate(
        candidates=candidates or (candidate(),),
        request=request(),
        backend=backend,
        evaluate_eligibility=eligible,
    )
    return result, backend


def test_selects_only_after_deterministic_recheck():
    result, backend = run(ModelProposal("exact", "1", {"rank": 1}, 7, 24))
    assert result["outcome"] == "selected"
    assert result["reason_code"] == "deterministic_eligibility_recheck_passed"
    assert result["selected_candidate_id"] == "exact"
    assert result["eligibility_evidence"] == ["fixture:eligibility:deterministic"]
    assert backend.calls == 1
    assert result["overhead"] == {
        "model_backend": {"calls": 1, "reported_cost_units": 7, "reported_bytes": 24},
        "deterministic_eligibility": {"checks": 2, "cost_units": 6},
    }


def test_abstention_is_distinct_and_not_fallback_authority():
    result, _ = run(ModelProposal(None, None, {"reason": "uncertain"}, 1, 2))
    assert result["outcome"] == "abstained"
    assert result["reason_code"] == "backend_abstained"
    assert result["fallback_authorized"] is False


def test_unknown_candidate_is_not_abstention():
    result, _ = run(ModelProposal("invented", "1"))
    assert result["outcome"] == "unknown_candidate"
    assert result["reason_code"] == "proposal_candidate_not_in_pinned_set"


def test_stale_candidate_version_is_distinct():
    result, _ = run(ModelProposal("exact", "0"))
    assert result["outcome"] == "stale_candidate"
    assert result["reason_code"] == "proposal_candidate_version_mismatch"


def test_ineligible_candidate_is_distinct_from_unknown():
    calls = 0

    def changing(item, selection_request):
        nonlocal calls
        calls += 1
        return EligibilityDecision(
            eligible=calls == 1,
            reason_code="eligible" if calls == 1 else "policy_changed",
            evidence_refs=("fixture:eligibility:view",),
            cost_units=2,
        )

    result = select_candidate(
        candidates=(candidate(),),
        request=request(),
        backend=LocalFixtureModelBackend(ModelProposal("exact", "1")),
        evaluate_eligibility=changing,
    )
    assert result["outcome"] == "ineligible_candidate"
    assert result["reason_code"] == "policy_changed"
    assert calls == 2


def test_backend_failure_is_distinct_and_does_not_authorize_fallback():
    result = select_candidate(
        candidates=(candidate(),),
        request=request(),
        backend=LocalFixtureModelBackend(failure=RuntimeError("offline")),
        evaluate_eligibility=eligible,
    )
    assert result["outcome"] == "backend_failed"
    assert result["selected_candidate_id"] is None
    assert result["fallback_authorized"] is False


def test_nonlocal_backend_is_guarded_before_invocation():
    class ExternalBackend:
        calls = 0

        def propose(self, candidates, selection_request):
            del candidates, selection_request
            self.calls += 1
            return ModelProposal("exact", "1")

    backend = ExternalBackend()
    with pytest.raises(ModelSelectorGuardError, match="model_selector_not_enabled"):
        select_candidate(
            candidates=(candidate(),),
            request=request(),
            backend=backend,
            evaluate_eligibility=eligible,
        )
    assert backend.calls == 0


def test_no_eligible_candidates_skips_backend():
    backend = LocalFixtureModelBackend(ModelProposal("blocked", "1"))
    result = select_candidate(
        candidates=(candidate("blocked"),),
        request=request(),
        backend=backend,
        evaluate_eligibility=eligible,
    )
    assert result["outcome"] == "abstained"
    assert result["reason_code"] == "no_deterministically_eligible_candidates"
    assert backend.calls == 0
    assert result["overhead"]["model_backend"]["calls"] == 0


def test_advisory_confidence_never_becomes_eligibility_evidence():
    result, _ = run(ModelProposal("exact", "1", {"confidence": 0.999}, 1, 8))
    assert result["outcome"] == "selected"
    assert result["advisory"]["confidence"] == 0.999
    assert result["eligibility_evidence"] == ["fixture:eligibility:deterministic"]
    assert "confidence" not in " ".join(result["eligibility_evidence"]).lower()


def test_candidate_set_is_frozen_and_fingerprinted():
    item = candidate()
    before = candidate_set_fingerprint((item,))
    with pytest.raises(FrozenInstanceError):
        item.candidate_id = "changed"
    assert candidate_set_fingerprint((item,)) == before
    result, _ = run(ModelProposal("exact", "1"), (item,))
    assert result["candidate_set_fingerprint"] == before


@pytest.mark.parametrize(
    "candidates",
    [
        [candidate()],
        tuple(candidate(str(index)) for index in range(MAX_CANDIDATES + 1)),
        (candidate("duplicate"), candidate("duplicate")),
        (object(),),
    ],
)
def test_invalid_candidate_sets_fail_before_backend(candidates):
    backend = LocalFixtureModelBackend(ModelProposal(None, None))
    with pytest.raises(ModelSelectorValidationError):
        select_candidate(
            candidates=candidates,
            request=request(),
            backend=backend,
            evaluate_eligibility=eligible,
        )
    assert backend.calls == 0


@pytest.mark.parametrize(
    "factory",
    [
        lambda: Candidate("", "1", "op", "policy"),
        lambda: Candidate("x" * 257, "1", "op", "policy"),
        lambda: Candidate("a", "1", "op", "policy", ("dup", "dup")),
        lambda: SelectionRequest("r", "op", "policy", True),
        lambda: SelectionRequest("r", "op", "policy", 1, (("x", "y"), ("x", "z"))),
        lambda: EligibilityDecision(1, "reason", (), 0),
        lambda: EligibilityDecision(True, "reason", (), True),
    ],
)
def test_exact_type_and_bound_validation(factory):
    with pytest.raises(ModelSelectorValidationError):
        factory()


@pytest.mark.parametrize(
    "proposal",
    [
        object(),
        ModelProposal(None, "1"),
        ModelProposal("exact", None),
        ModelProposal("exact", "1", {"bad": float("nan")}),
        ModelProposal("exact", "1", MappingProxyType({"rank": 1})),
        ModelProposal("exact", "1", {}, True, 0),
    ],
)
def test_malformed_backend_output_is_unknown_candidate(proposal):
    result = select_candidate(
        candidates=(candidate(),),
        request=request(),
        backend=LocalFixtureModelBackend(proposal),
        evaluate_eligibility=eligible,
    )
    assert result["outcome"] == "unknown_candidate"
    assert result["reason_code"] == "malformed_backend_output"


def test_fixture_subclass_cannot_bypass_production_guard():
    class LookalikeBackend(LocalFixtureModelBackend):
        pass

    backend = LookalikeBackend(ModelProposal("exact", "1"))
    with pytest.raises(ModelSelectorGuardError, match="model_selector_not_enabled"):
        select_candidate(
            candidates=(candidate(),),
            request=request(),
            backend=backend,
            evaluate_eligibility=eligible,
        )
    assert backend.calls == 0


def test_empty_candidate_set_abstains_without_backend_call():
    backend = LocalFixtureModelBackend(ModelProposal("exact", "1"))
    result = select_candidate(
        candidates=(),
        request=request(),
        backend=backend,
        evaluate_eligibility=eligible,
    )
    assert result["outcome"] == "abstained"
    assert result["reason_code"] == "no_deterministically_eligible_candidates"
    assert backend.calls == 0


def test_evaluator_exception_fails_closed():
    def broken(item, selection_request):
        del item, selection_request
        raise RuntimeError("broken")

    with pytest.raises(ModelSelectorValidationError, match="eligibility_evaluator_failed"):
        select_candidate(
            candidates=(candidate(),),
            request=request(),
            backend=LocalFixtureModelBackend(ModelProposal("exact", "1")),
            evaluate_eligibility=broken,
        )


def test_evaluator_must_return_typed_decision():
    with pytest.raises(ModelSelectorValidationError, match="eligibility_decision_type_invalid"):
        select_candidate(
            candidates=(candidate(),),
            request=request(),
            backend=LocalFixtureModelBackend(ModelProposal("exact", "1")),
            evaluate_eligibility=lambda item, req: True,
        )


def test_local_lineage_envelope_is_explicitly_noncanonical():
    result, _ = run(ModelProposal("exact", "1"))
    assert result["canonical_genesis_lineage"] == "local_only_not_applicable"
