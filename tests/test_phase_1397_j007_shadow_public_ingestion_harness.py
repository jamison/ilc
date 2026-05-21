"""Phase 1397 / J-007 — Shadow Public-Ingestion Jury Harness tests.

Proves:
- module and prerequisite dependency tokens exist
- required phase tokens present in source
- TaxonomyClass classification follows J-003 §11 decision procedure
- T0.5 quarantine validation: valid and invalid cases
- external-id deduplication (ADR-0041 §2): first-submission vs attestation-to-existing
- task lifecycle forward transitions succeed; backward/invalid transitions fail
- full harness run: PASS verdict when ≥1 T0.5 valid + ≥1 task reached audited
- full harness run: FAIL verdict when conditions are not met
- dedup_hit_count increments correctly
- production_activated=False, live_ecu_distributed=False always
- PRODUCTION_INGESTION_NOT_ACTIVATED=True
- phase tokens present in harness report
- no import random in source
- package exports
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
HARNESS_MODULE = REPO / "ilc_core/epistemic/ingestion_shadow_harness.py"

# ---------------------------------------------------------------------------
# Module / dependency existence
# ---------------------------------------------------------------------------

def test_harness_module_exists():
    assert HARNESS_MODULE.exists(), "ingestion_shadow_harness.py must exist"


def test_adr_0041_dependency_in_source():
    src = HARNESS_MODULE.read_text(encoding="utf-8")
    assert "adr_0041_agent_init_and_ingestion_protocol_accepted" in src


def test_j003_dependency_in_source():
    src = HARNESS_MODULE.read_text(encoding="utf-8")
    assert "public_node_review_taxonomy_phase_j003" in src


# ---------------------------------------------------------------------------
# Required phase tokens in source
# ---------------------------------------------------------------------------

_REQUIRED_TOKENS = [
    "shadow_public_ingestion_harness_phase_j007",
    "j007_harness_no_live_ecu_distribution",
    "j007_t0_5_quarantine_exercised",
    "j007_maintenance_task_lifecycle_exercised",
    "j007_no_production_activation",
]


@pytest.mark.parametrize("token", _REQUIRED_TOKENS)
def test_source_contains_token(token):
    src = HARNESS_MODULE.read_text(encoding="utf-8")
    assert token in src, f"ingestion_shadow_harness.py must contain token: {token}"


# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

from ilc_core.epistemic.ingestion_shadow_harness import (
    PRODUCTION_INGESTION_NOT_ACTIVATED,
    INGESTION_SHADOW_HARNESS_VERSION,
    DedupResult,
    HarnessReport,
    IngestionHarnessError,
    QuarantineValidationResult,
    SubmissionDescriptor,
    TaskLifecycleTrace,
    TaxonomyClass,
    check_external_id_dedup,
    classify_submission,
    exercise_task_lifecycle,
    run_shadow_ingestion_harness,
    validate_t0_5_quarantine,
)
from ilc_core.genesis.work_task import EpistemicWorkTask


def test_production_ingestion_not_activated():
    assert PRODUCTION_INGESTION_NOT_ACTIVATED is True


def test_version_token_present():
    assert "ingestion_shadow_harness_phase_j007" in INGESTION_SHADOW_HARNESS_VERSION


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_desc(
    sid: str = "sub-1",
    content_hash: str = "sha256:abc123",
    content_type: str = "application/pdf",
    byte_count: int = 1024,
    is_private: bool = False,
    public_intent: bool = True,
    claim_form: str = "metadata",
    reward_bearing: bool = False,
    contested: bool = False,
    canonical_external_id: str | None = None,
    extraction_method: str | None = None,
    source_span_present: bool = True,
) -> SubmissionDescriptor:
    return SubmissionDescriptor(
        submission_id=sid,
        submission_content_hash=content_hash,
        content_type=content_type,
        byte_count=byte_count,
        is_private=is_private,
        public_intent=public_intent,
        claim_form=claim_form,
        reward_bearing=reward_bearing,
        contested=contested,
        canonical_external_id=canonical_external_id,
        extraction_method=extraction_method,
        source_span_present=source_span_present,
    )


def _make_task(
    task_id: str = "task-1",
    task_class: str = "star.map.embedding",
    task_state: str = "proposed",
    agent_id: str = "agent-a",
) -> EpistemicWorkTask:
    return EpistemicWorkTask(
        task_id=task_id,
        task_class=task_class,  # type: ignore[arg-type]
        agent_id=agent_id,
        region_scope=["region-1"],
        verification_method="hash-match",
        task_state=task_state,  # type: ignore[arg-type]
        timestamp_created=1000,
        ecu_estimate=Decimal("1.5"),
    )


# ---------------------------------------------------------------------------
# TaxonomyClass classification (J-003 §11)
# ---------------------------------------------------------------------------

def test_classify_private_is_t0():
    desc = _make_desc(is_private=True, public_intent=False)
    assert classify_submission(desc) == TaxonomyClass.T0_PRIVATE_LOCAL_DRAFT


def test_classify_public_intent_is_t0_5():
    desc = _make_desc(is_private=False, public_intent=True)
    assert classify_submission(desc) == TaxonomyClass.T0_5_PENDING_PUBLIC_INGESTION


def test_classify_consensus_is_t6():
    desc = _make_desc(is_private=False, public_intent=False, claim_form="consensus")
    assert classify_submission(desc) == TaxonomyClass.T6_VALIDATOR_CONSENSUS_CLAIM


def test_classify_refutation_is_t5():
    desc = _make_desc(is_private=False, public_intent=False, claim_form="refutation")
    assert classify_submission(desc) == TaxonomyClass.T5_REFUTATION_PROVENANCE_STAKE_AFFECTING_CLAIM


def test_classify_provenance_is_t5():
    desc = _make_desc(is_private=False, public_intent=False, claim_form="provenance")
    assert classify_submission(desc) == TaxonomyClass.T5_REFUTATION_PROVENANCE_STAKE_AFFECTING_CLAIM


def test_classify_subjective_is_t4():
    desc = _make_desc(is_private=False, public_intent=False, claim_form="subjective")
    assert classify_submission(desc) == TaxonomyClass.T4_SUBJECTIVE_AESTHETIC_NODE


def test_classify_contested_reward_bearing_is_t3():
    desc = _make_desc(
        is_private=False, public_intent=False, reward_bearing=True, contested=True
    )
    assert classify_submission(desc) == TaxonomyClass.T3_CONTESTED_HIGH_VALUE_OBJECTIVE_NODE


def test_classify_reward_bearing_not_contested_is_t2():
    desc = _make_desc(
        is_private=False, public_intent=False, reward_bearing=True, contested=False
    )
    assert classify_submission(desc) == TaxonomyClass.T2_REWARD_BEARING_OBJECTIVE_NODE


def test_classify_non_reward_public_metadata_is_t1():
    desc = _make_desc(
        is_private=False, public_intent=False, reward_bearing=False, claim_form="metadata"
    )
    assert classify_submission(desc) == TaxonomyClass.T1_PUBLIC_NON_REWARD_METADATA


def test_classify_private_overrides_public_intent():
    """is_private takes precedence over public_intent (step 1 before step 2)."""
    desc = _make_desc(is_private=True, public_intent=True)
    assert classify_submission(desc) == TaxonomyClass.T0_PRIVATE_LOCAL_DRAFT


# ---------------------------------------------------------------------------
# External-id deduplication (ADR-0041 §2)
# ---------------------------------------------------------------------------

def test_dedup_no_external_id_is_first():
    assert check_external_id_dedup(None, set()) == DedupResult.FIRST_SUBMISSION


def test_dedup_unknown_id_is_first():
    assert check_external_id_dedup("doi:10.1234/xyz", set()) == DedupResult.FIRST_SUBMISSION


def test_dedup_known_id_is_attestation():
    known = {"doi:10.1234/xyz"}
    assert check_external_id_dedup("doi:10.1234/xyz", known) == DedupResult.ATTESTATION_TO_EXISTING


def test_dedup_different_id_is_first():
    known = {"doi:10.1234/xyz"}
    assert check_external_id_dedup("doi:10.5678/abc", known) == DedupResult.FIRST_SUBMISSION


# ---------------------------------------------------------------------------
# T0.5 quarantine validation
# ---------------------------------------------------------------------------

def test_valid_t0_5_submission():
    desc = _make_desc(public_intent=True, canonical_external_id="doi:10.9999/test")
    result = validate_t0_5_quarantine(desc, set())
    assert result.valid is True
    assert result.taxonomy_class == TaxonomyClass.T0_5_PENDING_PUBLIC_INGESTION
    assert result.dedup_result == DedupResult.FIRST_SUBMISSION
    assert result.failure_token is None


def test_t0_5_missing_submission_id():
    desc = _make_desc(sid="")
    result = validate_t0_5_quarantine(desc, set())
    assert result.valid is False
    assert result.failure_token is not None


def test_t0_5_missing_content_hash():
    desc = _make_desc(content_hash="")
    result = validate_t0_5_quarantine(desc, set())
    assert result.valid is False


def test_t0_5_invalid_byte_count():
    desc = _make_desc(byte_count=0)
    result = validate_t0_5_quarantine(desc, set())
    assert result.valid is False


def test_t0_5_consensus_claim_form_invalid():
    desc = _make_desc(claim_form="consensus")
    result = validate_t0_5_quarantine(desc, set())
    assert result.valid is False
    assert result.failure_token == "quarantine_consensus_claim_form_invalid_for_t0_5"


def test_t0_5_dedup_hit():
    known = {"doi:10.1234/dup"}
    desc = _make_desc(canonical_external_id="doi:10.1234/dup")
    result = validate_t0_5_quarantine(desc, known)
    assert result.valid is True
    assert result.dedup_result == DedupResult.ATTESTATION_TO_EXISTING


def test_t0_5_automated_extractor_missing_span_warning():
    desc = _make_desc(extraction_method="automated-rule", source_span_present=False)
    result = validate_t0_5_quarantine(desc, set())
    assert result.valid is False
    assert result.failure_token == "automated_extractor_missing_source_span"


# ---------------------------------------------------------------------------
# Task lifecycle
# ---------------------------------------------------------------------------

def test_valid_full_lifecycle():
    task = _make_task(task_state="proposed")
    trace = exercise_task_lifecycle(
        task, ["claimed", "completed", "audited", "rewarded"]
    )
    assert all(s.valid for s in trace.steps)
    assert trace.reached_audited is True
    assert trace.terminal_state == "rewarded"


def test_lifecycle_to_expired():
    task = _make_task(task_state="proposed")
    trace = exercise_task_lifecycle(task, ["claimed", "expired"])
    assert all(s.valid for s in trace.steps)
    assert trace.terminal_state == "expired"


def test_lifecycle_invalid_backward_transition():
    """proposed → completed is not a valid transition (must go through claimed)."""
    task = _make_task(task_state="proposed")
    trace = exercise_task_lifecycle(task, ["completed"])
    assert trace.steps[0].valid is False
    assert "invalid_transition" in trace.steps[0].failure_token


def test_lifecycle_cannot_leave_terminal_rewarded():
    task = _make_task(task_state="proposed")
    trace = exercise_task_lifecycle(
        task, ["claimed", "completed", "audited", "rewarded", "proposed"]
    )
    last_step = trace.steps[-1]
    assert last_step.valid is False
    assert "terminal" in last_step.failure_token


def test_lifecycle_reached_audited_flag():
    task = _make_task(task_state="proposed")
    trace = exercise_task_lifecycle(task, ["claimed", "completed", "audited"])
    assert trace.reached_audited is True


def test_lifecycle_not_reached_audited():
    task = _make_task(task_state="proposed")
    trace = exercise_task_lifecycle(task, ["claimed", "completed"])
    assert trace.reached_audited is False


def test_lifecycle_empty_transition_sequence():
    task = _make_task(task_state="proposed")
    trace = exercise_task_lifecycle(task, [])
    assert trace.steps == []
    assert trace.reached_audited is False
    assert trace.terminal_state == "proposed"


# ---------------------------------------------------------------------------
# Full harness run
# ---------------------------------------------------------------------------

def _standard_harness_call(**overrides):
    submissions = [
        _make_desc(sid="s1", public_intent=True, canonical_external_id="doi:10.1/a"),
        _make_desc(sid="s2", public_intent=True, canonical_external_id="doi:10.2/b"),
    ]
    task = _make_task(task_id="t1", task_state="proposed")
    tasks = [(task, ["claimed", "completed", "audited", "rewarded"])]
    kwargs = dict(
        review_epoch=200,
        submissions=submissions,
        tasks_with_transitions=tasks,
    )
    kwargs.update(overrides)
    return run_shadow_ingestion_harness(**kwargs)


def test_harness_pass_verdict():
    report = _standard_harness_call()
    assert report.verdict == "PASS"


def test_harness_t0_5_count():
    report = _standard_harness_call()
    assert report.t0_5_count == 2


def test_harness_tasks_reached_audited():
    report = _standard_harness_call()
    assert report.tasks_reached_audited == 1


def test_harness_production_activated_false():
    report = _standard_harness_call()
    assert report.production_activated is False


def test_harness_live_ecu_distributed_false():
    report = _standard_harness_call()
    assert report.live_ecu_distributed is False


def test_harness_phase_tokens_present():
    report = _standard_harness_call()
    for token in _REQUIRED_TOKENS:
        assert token in report.phase_tokens, f"report must contain token: {token}"


def test_harness_fail_verdict_no_t0_5():
    """No public-intent submissions → t0_5_count=0 → FAIL."""
    task = _make_task(task_state="proposed")
    report = run_shadow_ingestion_harness(
        review_epoch=1,
        submissions=[_make_desc(is_private=True)],
        tasks_with_transitions=[(task, ["claimed", "completed", "audited"])],
    )
    assert report.verdict == "FAIL"
    assert report.t0_5_count == 0


def test_harness_fail_verdict_no_audited_task():
    """Task never reaches audited → FAIL."""
    task = _make_task(task_state="proposed")
    report = run_shadow_ingestion_harness(
        review_epoch=1,
        submissions=[_make_desc(sid="s1", public_intent=True)],
        tasks_with_transitions=[(task, ["claimed", "completed"])],
    )
    assert report.verdict == "FAIL"
    assert report.tasks_reached_audited == 0


def test_harness_dedup_hit_count():
    submissions = [
        _make_desc(sid="s1", public_intent=True, canonical_external_id="doi:10.1/a"),
        _make_desc(sid="s2", public_intent=True, canonical_external_id="doi:10.1/a"),  # dedup hit
    ]
    task = _make_task(task_state="proposed")
    report = run_shadow_ingestion_harness(
        review_epoch=1,
        submissions=submissions,
        tasks_with_transitions=[(task, ["claimed", "completed", "audited"])],
    )
    assert report.dedup_hit_count == 1
    # Both submissions are valid T0.5 entries — the dedup hit creates an ATTESTATION
    # edge rather than a new node, but the quarantine entry itself is still valid.
    assert report.t0_5_count == 2


def test_harness_invalid_epoch_raises():
    with pytest.raises(IngestionHarnessError):
        run_shadow_ingestion_harness(
            review_epoch=-1,
            submissions=[],
            tasks_with_transitions=[],
        )
    with pytest.raises(IngestionHarnessError):
        run_shadow_ingestion_harness(
            review_epoch=True,
            submissions=[],
            tasks_with_transitions=[],
        )


def test_harness_deterministic_id():
    """Same epoch and same inputs -> same harness_id."""
    subs = [_make_desc(sid="s1", public_intent=True)]
    task = _make_task(task_state="proposed")
    r1 = run_shadow_ingestion_harness(
        review_epoch=42,
        submissions=subs,
        tasks_with_transitions=[(task, ["claimed"])],
    )
    r2 = run_shadow_ingestion_harness(
        review_epoch=42,
        submissions=subs,
        tasks_with_transitions=[(task, ["claimed"])],
    )
    assert r1.harness_id == r2.harness_id


def test_harness_default_id_changes_when_same_count_content_changes():
    task = _make_task(task_state="proposed")
    r1 = run_shadow_ingestion_harness(
        review_epoch=42,
        submissions=[_make_desc(sid="s1", content_hash="sha256:" + "1" * 64, public_intent=True)],
        tasks_with_transitions=[(task, ["claimed"])],
    )
    r2 = run_shadow_ingestion_harness(
        review_epoch=42,
        submissions=[_make_desc(sid="s2", content_hash="sha256:" + "2" * 64, public_intent=True)],
        tasks_with_transitions=[(task, ["claimed"])],
    )
    assert r1.harness_id != r2.harness_id


def test_harness_custom_id():
    task = _make_task(task_state="proposed")
    report = run_shadow_ingestion_harness(
        review_epoch=1,
        submissions=[_make_desc(sid="s1", public_intent=True)],
        tasks_with_transitions=[(task, ["claimed", "completed", "audited"])],
        harness_id="custom-harness-01",
    )
    assert report.harness_id == "custom-harness-01"


# ---------------------------------------------------------------------------
# Security / coding standards
# ---------------------------------------------------------------------------

def test_no_random_import():
    src = HARNESS_MODULE.read_text(encoding="utf-8")
    assert "import random" not in src


def test_no_float_for_ecu():
    src = HARNESS_MODULE.read_text(encoding="utf-8")
    # byte_count is int, not float
    assert "byte_count: float" not in src


# ---------------------------------------------------------------------------
# Package exports
# ---------------------------------------------------------------------------

def test_package_exports_run_function():
    from ilc_core.epistemic import run_shadow_ingestion_harness as fn
    assert callable(fn)


def test_package_exports_taxonomy_class():
    from ilc_core.epistemic import TaxonomyClass as TC
    assert TC.T0_5_PENDING_PUBLIC_INGESTION is not None


def test_package_exports_production_flag():
    from ilc_core.epistemic import PRODUCTION_INGESTION_NOT_ACTIVATED as flag
    assert flag is True
