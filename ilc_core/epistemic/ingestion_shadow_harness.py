# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1397 / J-007 — Shadow Public-Ingestion Jury Harness.

Exercises the T0.5 quarantine state, external-identifier deduplication,
J-003 taxonomy classification, and maintenance task lifecycle end-to-end,
*without* activating production ingestion, live ECU distribution, or any
public economic path.

Required phase tokens:
  shadow_public_ingestion_harness_phase_j007
  j007_harness_no_live_ecu_distribution
  j007_t0_5_quarantine_exercised
  j007_maintenance_task_lifecycle_exercised
  j007_no_production_activation

Hard prerequisite satisfied:
  adr_0041_agent_init_and_ingestion_protocol_accepted  (ADR-0041 / J-003a)
  public_node_review_taxonomy_phase_j003                (J-003 taxonomy)
  default_off_jury_assignment_quote_runtime_phase_j006  (J-006 quote runtime)
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from ilc_core.genesis.work_task import EpistemicWorkTask

INGESTION_SHADOW_HARNESS_VERSION = "ingestion_shadow_harness_phase_j007.v0.1"
ADR_0041_DEPENDENCY = "adr_0041_agent_init_and_ingestion_protocol_accepted"
J003_DEPENDENCY = "public_node_review_taxonomy_phase_j003"
J006_DEPENDENCY = "default_off_jury_assignment_quote_runtime_phase_j006"

# Phase tokens — must appear in source (referenced by tests)
_TOKEN_HARNESS = "shadow_public_ingestion_harness_phase_j007"
_TOKEN_NO_ECU = "j007_harness_no_live_ecu_distribution"
_TOKEN_T0_5 = "j007_t0_5_quarantine_exercised"
_TOKEN_LIFECYCLE = "j007_maintenance_task_lifecycle_exercised"
_TOKEN_NO_ACTIVATION = "j007_no_production_activation"

# Safety gate: must remain True until J-008 production activation gate passes.
PRODUCTION_INGESTION_NOT_ACTIVATED: bool = True

# Valid task state forward-transition graph (EpistemicWorkTask.task_state)
_TASK_STATE_TRANSITIONS: dict = {
    "proposed": {"claimed", "expired"},
    "claimed": {"completed", "expired"},
    "completed": {"audited", "expired"},
    "audited": {"rewarded", "expired"},
    "rewarded": set(),   # terminal
    "expired": set(),    # terminal
}


# ---------------------------------------------------------------------------
# Taxonomy types (J-003 §3 taxonomy table)
# ---------------------------------------------------------------------------

class TaxonomyClass(str, Enum):
    T0_PRIVATE_LOCAL_DRAFT = "T0_PRIVATE_LOCAL_DRAFT"
    T0_5_PENDING_PUBLIC_INGESTION = "T0_5_PENDING_PUBLIC_INGESTION"
    T1_PUBLIC_NON_REWARD_METADATA = "T1_PUBLIC_NON_REWARD_METADATA"
    T2_REWARD_BEARING_OBJECTIVE_NODE = "T2_REWARD_BEARING_OBJECTIVE_NODE"
    T3_CONTESTED_HIGH_VALUE_OBJECTIVE_NODE = "T3_CONTESTED_HIGH_VALUE_OBJECTIVE_NODE"
    T4_SUBJECTIVE_AESTHETIC_NODE = "T4_SUBJECTIVE_AESTHETIC_NODE"
    T5_REFUTATION_PROVENANCE_STAKE_AFFECTING_CLAIM = (
        "T5_REFUTATION_PROVENANCE_STAKE_AFFECTING_CLAIM"
    )
    T6_VALIDATOR_CONSENSUS_CLAIM = "T6_VALIDATOR_CONSENSUS_CLAIM"


# ---------------------------------------------------------------------------
# Deduplication result (ADR-0041 §2)
# ---------------------------------------------------------------------------

class DedupResult(str, Enum):
    FIRST_SUBMISSION = "FIRST_SUBMISSION"
    ATTESTATION_TO_EXISTING = "ATTESTATION_TO_EXISTING"  # same external id already present


# ---------------------------------------------------------------------------
# Submission descriptor
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SubmissionDescriptor:
    """Minimal description of a graph-submission for harness classification.

    Fields map directly to the ADR-0041 / J-003 classification criteria.
    No protocol bytes — this is a harness descriptor, not a wire envelope.
    """

    submission_id: str
    submission_content_hash: str      # sha256:<hex>
    content_type: str
    byte_count: int

    # Visibility / intent signals
    is_private: bool = False           # if True → T0
    public_intent: bool = False        # if True and not yet admitted → T0.5

    # Classification signals
    claim_form: str = "metadata"       # bounded_existential | metadata | structural |
                                       # subjective | refutation | provenance | consensus
    reward_bearing: bool = False
    contested: bool = False

    # External identifier anchoring (ADR-0041 §2)
    canonical_external_id: Optional[str] = None  # e.g. "doi:10.1234/xyz" or None

    # Extraction provenance (ADR-0041 §4)
    extraction_method: Optional[str] = None      # human | llm-assisted | automated-rule | hybrid
    source_span_present: bool = True             # best-effort from human; required for automated


# ---------------------------------------------------------------------------
# Quarantine validation result
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class QuarantineValidationResult:
    submission_id: str
    valid: bool
    taxonomy_class: TaxonomyClass
    dedup_result: Optional[DedupResult]
    failure_token: Optional[str]      # None if valid
    warnings: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Task lifecycle trace
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TaskLifecycleStep:
    from_state: str
    to_state: str
    valid: bool
    failure_token: Optional[str]


@dataclass(frozen=True)
class TaskLifecycleTrace:
    task_id: str
    task_class: str
    steps: List[TaskLifecycleStep]
    reached_audited: bool
    terminal_state: str


# ---------------------------------------------------------------------------
# Harness report
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class HarnessReport:
    """Output of a shadow harness run.  No economic or protocol effect."""

    harness_id: str
    review_epoch: int
    quarantine_results: List[QuarantineValidationResult]
    task_lifecycle_traces: List[TaskLifecycleTrace]
    t0_5_count: int
    dedup_hit_count: int
    tasks_reached_audited: int
    verdict: str                   # "PASS" | "FAIL" — shadow-mode only
    phase_tokens: List[str]
    production_activated: bool     # always False
    live_ecu_distributed: bool     # always False
    runtime_version: str


class IngestionHarnessError(Exception):
    """Raised when the harness detects a fatal configuration error."""


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def classify_submission(descriptor: SubmissionDescriptor) -> TaxonomyClass:
    """Implement J-003 §11 decision procedure.

    The procedure is applied in order; the first matching condition wins.
    When a submission fits multiple classes, the stricter lane is chosen.
    """
    # Step 1 — private / local / operator-only / harness-only draft
    if descriptor.is_private:
        return TaxonomyClass.T0_PRIVATE_LOCAL_DRAFT

    # Step 9 — validator / consensus evidence
    if descriptor.claim_form == "consensus":
        return TaxonomyClass.T6_VALIDATOR_CONSENSUS_CLAIM

    # Step 8 — refutation / provenance / stake-affecting
    if descriptor.claim_form in {"refutation", "provenance"}:
        return TaxonomyClass.T5_REFUTATION_PROVENANCE_STAKE_AFFECTING_CLAIM

    # Step 7 — subjective / aesthetic
    if descriptor.claim_form == "subjective":
        return TaxonomyClass.T4_SUBJECTIVE_AESTHETIC_NODE

    # Step 2 — declared public intent but not yet admitted → quarantine
    if descriptor.public_intent:
        # Contested / high-value nodes still land in T0.5 first (quarantine entry)
        # They will be promoted by the admission path. At quarantine entry time
        # the taxonomy class is T0.5.
        return TaxonomyClass.T0_5_PENDING_PUBLIC_INGESTION

    # Step 4–6 — admitted public nodes; classify by claim type
    # Step 6 — contested, high-value, safety-critical, or high-reward
    if descriptor.contested and descriptor.reward_bearing:
        return TaxonomyClass.T3_CONTESTED_HIGH_VALUE_OBJECTIVE_NODE

    # Step 5 — objective reward-bearing
    if descriptor.reward_bearing:
        return TaxonomyClass.T2_REWARD_BEARING_OBJECTIVE_NODE

    # Step 3 — public but non-economic / descriptive
    return TaxonomyClass.T1_PUBLIC_NON_REWARD_METADATA


def check_external_id_dedup(
    canonical_external_id: Optional[str],
    known_ids: set,
) -> DedupResult:
    """Implement ADR-0041 §2 deduplication rule.

    If canonical_external_id is None or not known: FIRST_SUBMISSION.
    If canonical_external_id is in known_ids: ATTESTATION_TO_EXISTING.
    """
    if not canonical_external_id:
        return DedupResult.FIRST_SUBMISSION
    if canonical_external_id in known_ids:
        return DedupResult.ATTESTATION_TO_EXISTING
    return DedupResult.FIRST_SUBMISSION


def validate_t0_5_quarantine(
    descriptor: SubmissionDescriptor,
    known_external_ids: set,
) -> QuarantineValidationResult:
    """Validate a T0.5-bound submission at quarantine entry.

    Checks:
    1. submission_id and submission_content_hash must be non-empty.
    2. content_type must be non-empty.
    3. byte_count must be a positive integer.
    4. Automated extractors must carry source_span_present=True (ADR-0041 §4).
    5. External-id dedup check (ADR-0041 §2).
    6. claim_form must not be "consensus" (those go to T6, not T0.5).

    Returns a QuarantineValidationResult. Validation is advisory in shadow mode —
    the harness records failures but does not raise.
    """
    warnings: List[str] = []
    failure_token: Optional[str] = None
    valid = True

    # Required-field presence
    if not descriptor.submission_id:
        failure_token = "quarantine_missing_submission_id"
        valid = False
    if not descriptor.submission_content_hash:
        failure_token = failure_token or "quarantine_missing_content_hash"
        valid = False
    if not descriptor.content_type:
        failure_token = failure_token or "quarantine_missing_content_type"
        valid = False
    if not isinstance(descriptor.byte_count, int) or descriptor.byte_count <= 0:
        failure_token = failure_token or "quarantine_invalid_byte_count"
        valid = False

    # Automated extractors must carry source_span (ADR-0041 §4)
    if (
        descriptor.extraction_method in {"automated-rule"}
        and not descriptor.source_span_present
    ):
        failure_token = failure_token or "automated_extractor_missing_source_span"
        valid = False

    # claim_form sanity
    if descriptor.claim_form == "consensus":
        failure_token = failure_token or "quarantine_consensus_claim_form_invalid_for_t0_5"
        valid = False

    # External-id dedup
    dedup = check_external_id_dedup(descriptor.canonical_external_id, known_external_ids)

    taxonomy = (
        TaxonomyClass.T0_5_PENDING_PUBLIC_INGESTION
        if valid
        else TaxonomyClass.T0_PRIVATE_LOCAL_DRAFT  # failed validation → treat as local draft
    )

    return QuarantineValidationResult(
        submission_id=descriptor.submission_id,
        valid=valid,
        taxonomy_class=taxonomy,
        dedup_result=dedup,
        failure_token=failure_token,
        warnings=warnings,
    )


def exercise_task_lifecycle(
    task: EpistemicWorkTask,
    transition_sequence: List[str],
) -> TaskLifecycleTrace:
    """Walk an EpistemicWorkTask through a caller-supplied state-transition sequence.

    Validates each transition against the canonical forward-transition graph.
    Terminal states (rewarded, expired) may not transition further.

    The harness runs in shadow mode: no ECU is distributed, no graph is written,
    no production queue is populated.

    Args:
        task: Initial EpistemicWorkTask (its task_state is the starting point).
        transition_sequence: List of target states to step through, in order.
            Example: ["claimed", "completed", "audited", "rewarded"]

    Returns:
        TaskLifecycleTrace with per-step validity records.
    """
    steps: List[TaskLifecycleStep] = []
    current_state = task.task_state
    terminal = False

    for target_state in transition_sequence:
        if terminal:
            steps.append(TaskLifecycleStep(
                from_state=current_state,
                to_state=target_state,
                valid=False,
                failure_token="task_lifecycle_already_in_terminal_state",
            ))
            continue

        from_state = current_state
        allowed_next = _TASK_STATE_TRANSITIONS.get(from_state, set())
        valid = target_state in allowed_next

        if not valid:
            failure_token = (
                f"task_lifecycle_invalid_transition_{from_state}_to_{target_state}"
            )
        else:
            failure_token = None
            current_state = target_state
            if current_state in {"rewarded", "expired"}:
                terminal = True

        steps.append(TaskLifecycleStep(
            from_state=from_state,
            to_state=target_state,
            valid=valid,
            failure_token=failure_token,
        ))

    reached_audited = any(
        s.to_state == "audited" and s.valid for s in steps
    )

    return TaskLifecycleTrace(
        task_id=task.task_id,
        task_class=task.task_class,
        steps=steps,
        reached_audited=reached_audited,
        terminal_state=current_state,
    )


# ---------------------------------------------------------------------------
# Top-level harness runner
# ---------------------------------------------------------------------------

def run_shadow_ingestion_harness(
    *,
    review_epoch: int,
    submissions: List[SubmissionDescriptor],
    tasks_with_transitions: List[tuple],
    harness_id: Optional[str] = None,
) -> HarnessReport:
    """Run the shadow public-ingestion jury harness end-to-end.

    Args:
        review_epoch: Protocol epoch number (not wall-clock).
        submissions: List of SubmissionDescriptor for T0.5 quarantine exercise.
        tasks_with_transitions: List of (EpistemicWorkTask, List[str]) pairs.
            The second element is the transition_sequence to walk.
        harness_id: Optional stable identifier for this harness run.

    Returns:
        HarnessReport with PASS or FAIL verdict (shadow mode only).
        PASS requires: ≥1 T0.5 submission processed; ≥1 task reached audited state.
    """
    if isinstance(review_epoch, bool) or not isinstance(review_epoch, int) or review_epoch < 0:
        raise IngestionHarnessError("review_epoch must be a non-negative integer")

    if harness_id is None:
        # Deterministic harness ID from the actual shadow inputs, not just counts.
        harness_id = hashlib.sha256(
            json.dumps(
                {
                    "epoch": review_epoch,
                    "submissions": [
                        {
                            "submission_content_hash": item.submission_content_hash,
                            "submission_id": item.submission_id,
                        }
                        for item in submissions
                    ],
                    "tasks": [
                        {
                            "task_id": task.task_id,
                            "transitions": list(transition_sequence),
                        }
                        for task, transition_sequence in tasks_with_transitions
                    ],
                },
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
        ).hexdigest()[:16]

    # --- Process submissions ---
    known_external_ids: set = set()
    quarantine_results: List[QuarantineValidationResult] = []
    t0_5_count = 0
    dedup_hit_count = 0

    for desc in submissions:
        taxonomy_class = classify_submission(desc)

        if taxonomy_class == TaxonomyClass.T0_5_PENDING_PUBLIC_INGESTION:
            result = validate_t0_5_quarantine(desc, known_external_ids)
            quarantine_results.append(result)
            if result.valid:
                t0_5_count += 1
                if result.dedup_result == DedupResult.ATTESTATION_TO_EXISTING:
                    dedup_hit_count += 1
                elif desc.canonical_external_id:
                    known_external_ids.add(desc.canonical_external_id)
            # Failed validation also recorded in quarantine_results
        else:
            # Non-T0.5 submissions are classified only (not quarantine-validated)
            quarantine_results.append(QuarantineValidationResult(
                submission_id=desc.submission_id,
                valid=True,
                taxonomy_class=taxonomy_class,
                dedup_result=None,
                failure_token=None,
                warnings=[],
            ))

    # --- Exercise task lifecycles ---
    task_traces: List[TaskLifecycleTrace] = []
    tasks_reached_audited = 0

    for task, transition_seq in tasks_with_transitions:
        trace = exercise_task_lifecycle(task, transition_seq)
        task_traces.append(trace)
        if trace.reached_audited:
            tasks_reached_audited += 1

    # --- Verdict ---
    # PASS: at least one valid T0.5 submission processed AND at least one
    # maintenance task reached the audited state.
    verdict = (
        "PASS"
        if (t0_5_count >= 1 and tasks_reached_audited >= 1)
        else "FAIL"
    )

    return HarnessReport(
        harness_id=harness_id,
        review_epoch=review_epoch,
        quarantine_results=quarantine_results,
        task_lifecycle_traces=task_traces,
        t0_5_count=t0_5_count,
        dedup_hit_count=dedup_hit_count,
        tasks_reached_audited=tasks_reached_audited,
        verdict=verdict,
        phase_tokens=[
            _TOKEN_HARNESS,
            _TOKEN_NO_ECU,
            _TOKEN_T0_5,
            _TOKEN_LIFECYCLE,
            _TOKEN_NO_ACTIVATION,
        ],
        production_activated=False,
        live_ecu_distributed=False,
        runtime_version=INGESTION_SHADOW_HARNESS_VERSION,
    )
