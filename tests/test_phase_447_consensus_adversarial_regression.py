from __future__ import annotations

import copy
from decimal import Decimal
import re
import subprocess
from pathlib import Path

import pytest

from ilc_core.consensus.epoch_state_runtime import (
    ConsensusEpochStateValidationError,
    canonical_epoch_state_vectors,
    generate_epoch_state_record,
    generate_quorum_record,
    verify_quorum_record,
)
from ilc_core.consensus.finality_evaluator import (
    ConsensusFinalityEvaluatorError,
    evaluate_epoch_finality,
    resolve_fork,
)


FINDINGS_MEMO_PATH = Path("docs/specs/ilc_consensus_findings_memo_447_v0.1.md")
EPOCH_STATE_RUNTIME_PATH = Path("ilc_core/consensus/epoch_state_runtime.py")
FINALITY_EVALUATOR_PATH = Path("ilc_core/consensus/finality_evaluator.py")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_446_REPORT_PATH = Path("out/runtime_baseline/phase_446_report.json")
PHASE_447_SUBJECT_TOKEN = "docs(g8): phase 447 consensus findings memo and adversarial regression hardening"
REQUIRED_MEMO_HEADINGS = (
    "## 1. Executive summary",
    "## 2. What the prototype proves",
    "## 3. Timing evidence (Phase 446 harness baseline)",
    "## 4. Failure modes and edge cases",
    "## 5. Missing measurements",
    "## 6. Unresolved assumptions",
    "## 7. Adversarial regression guards added",
)
REQUIRED_MEMO_TOKENS = (
    "Phase 447 records the settled findings state after the consensus runtime tranche completed in Phases 444, 445, and 446.",
    "CDL-051 ratification evidence anchor: docs/specs/ilc_cdl_051_constitutional_consensus_and_epoch_finality_ratification_evidence_443_v0.1.md",
    "Phase 446 harness report anchor: out/runtime_baseline/phase_446_report.json",
    "The consensus prototype proves deterministic quorum-record generation, epoch-state record generation, finality evaluation, and fork-resolution selection.",
    "Timing evidence in Section 3 references the Phase 446 harness baseline measurements.",
    "The current conflict label conflates true competing-threshold forks with multi-candidate no-qualifier states; a future phase may need an explicit undecided or insufficient_votes distinction.",
    "No multi-validator or multi-process consensus measurement exists yet; that remains future work outside Phase 447.",
    "CDL-050 remains unopened and unaffected by Phase 447.",
    "Phase 447 did not introduce new runtime surfaces.",
    "Phase 448 is the next authorized synthesis phase.",
    "The Phase 445 flat-aggregate finality evaluator does not enforce the CDL-V3 cluster diversity floor; diversity_floor_runtime.py is not called during finality evaluation. Enforcing the CDL-V3 distinct_cluster_floor and max_cluster_share_ceiling in the finality pipeline is a future constitutional obligation before production finality.",
    "The current quorum-record schema does not carry cluster_id or equivalent cluster-membership metadata; enforcing the CDL-V3 distinct_cluster_floor and max_cluster_share_ceiling requires both a quorum-record schema extension and a two-gate finality evaluation change in a future phase.",
    "The 7+1 epistemic panel for knowledge-claim evaluation and the CDL-051 epoch-finality quorum are architecturally distinct quorum types and must not be conflated.",
    "The epistemic finality claims model (agents filing epoch_finality_attestation knowledge nodes evaluated by 7+1 panels with ECU and reputation staking) is a future architectural lane building on CDL-051, not replacing it. A full design proposal is planned as ADR-0021 after Phase 447 completes, using this findings memo and session transcript as primary inputs.",
)
REQUIRED_TIMING_KEYS = (
    "quorum_record_generation_ms",
    "epoch_state_generation_ms",
    "finality_evaluation_ms",
    "fork_resolution_ms",
)
EXPECTED_CHANGED_PATHS = {
    "docs/specs/ilc_consensus_findings_memo_447_v0.1.md",
    "tests/test_phase_447_consensus_adversarial_regression.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_447_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    saw_subject = False
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() != PHASE_447_SUBJECT_TOKEN:
            continue
        saw_subject = True
        if _changed_paths_for_commit(commit_hash) == EXPECTED_CHANGED_PATHS:
            return commit_hash
    if saw_subject:
        raise AssertionError("phase_447_commit_subject_present_but_no_qualifying_findings_commit")
    raise AssertionError("phase_447_commit_not_present_in_local_history")


def _evaluator_text_at_ref(ref: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{ref}:{FINALITY_EVALUATOR_PATH}"],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"unable_to_read_finality_evaluator_at_ref:{ref}:{result.stderr.strip()}")
    return result.stdout

def test_findings_memo_exists_and_contains_required_headings_and_tokens() -> None:
    text = _read(FINDINGS_MEMO_PATH)

    assert FINDINGS_MEMO_PATH.exists()
    assert PHASE_446_REPORT_PATH.exists()
    for heading in REQUIRED_MEMO_HEADINGS:
        assert heading in text
    for token in REQUIRED_MEMO_TOKENS:
        assert token in text
    for key in REQUIRED_TIMING_KEYS:
        assert re.search(rf"`{re.escape(key)}`:[^\n]*[0-9]+(?:\.[0-9]+)?\s*ms", text)
    historical_evaluator_text = _evaluator_text_at_ref(_resolve_phase_447_commit_ref())
    assert "diversity_floor_runtime" not in historical_evaluator_text
    assert "distinct_cluster_floor" not in historical_evaluator_text
    assert "max_cluster_share_ceiling" not in historical_evaluator_text


def test_adversarial_missing_quorum_threshold_under_various_invalid_inputs() -> None:
    vector = canonical_epoch_state_vectors()[0]
    missing_threshold = copy.deepcopy(vector["epoch_state"])
    missing_threshold.pop("quorum_threshold", None)

    with pytest.raises(ConsensusEpochStateValidationError) as missing_key_error:
        generate_epoch_state_record(missing_threshold)
    assert missing_key_error.value.token == "consensus_epoch_state_quorum_threshold_missing"

    none_threshold = copy.deepcopy(vector["epoch_state"])
    none_threshold["quorum_threshold"] = None
    with pytest.raises(ConsensusEpochStateValidationError) as none_error:
        generate_epoch_state_record(none_threshold)
    assert none_error.value.token == "consensus_epoch_state_quorum_threshold_missing"

    invalid_threshold = copy.deepcopy(vector["epoch_state"])
    invalid_threshold["quorum_threshold"] = {}
    with pytest.raises(ConsensusEpochStateValidationError) as invalid_error:
        generate_epoch_state_record(invalid_threshold)
    assert invalid_error.value.token == "consensus_epoch_state_quorum_threshold_invalid"

    with pytest.raises(ConsensusFinalityEvaluatorError) as finality_error:
        evaluate_epoch_finality(vector["quorum_records"], quorum_threshold=None)
    assert finality_error.value.token == "consensus_finality_evaluator_quorum_threshold_missing"


def test_adversarial_zero_weight_and_negative_weight_vote_injection() -> None:
    raw_record = canonical_epoch_state_vectors()[0]["quorum_records"][0]

    for invalid_weight in (0, -1.0):
        injected = copy.deepcopy(raw_record)
        injected["vote_weight"] = invalid_weight

        with pytest.raises(ConsensusEpochStateValidationError) as generate_error:
            generate_quorum_record(injected)
        assert generate_error.value.token == "consensus_quorum_record_vote_weight_invalid"

        with pytest.raises(ConsensusEpochStateValidationError) as verify_error:
            verify_quorum_record(injected)
        assert verify_error.value.token == "consensus_quorum_record_vote_weight_invalid"


def test_adversarial_duplicate_block_hash_vote_injection() -> None:
    quorum_records = [
        {"block_hash": "block-dup", "epoch_index": 12, "vote_weight": Decimal("0.40")},
        {"block_hash": "block-dup", "epoch_index": 12, "vote_weight": Decimal("0.30")},
        {"block_hash": "block-other", "epoch_index": 12, "vote_weight": Decimal("0.10")},
    ]
    result = evaluate_epoch_finality(quorum_records, {"numerator": 2, "denominator": 3})

    assert result["finality_status"] == "finalized"
    assert result["canonical_block_hash"] == "block-dup"
    assert result["aggregate_weights"]["block-dup"] == pytest.approx(0.70)

    vector = canonical_epoch_state_vectors()[0]
    record_a = generate_quorum_record(vector["quorum_records"][0])
    record_b = generate_quorum_record(vector["quorum_records"][1])
    epoch_state = copy.deepcopy(vector["epoch_state"])
    epoch_state["quorum_record_digests"] = [
        record_b["record_digest"],
        record_a["record_digest"],
        record_a["record_digest"],  # intentional duplicate: tests deduplication
    ]
    generated_state = generate_epoch_state_record(epoch_state)

    assert generated_state["quorum_record_digests"] == sorted(
        {record_a["record_digest"], record_b["record_digest"]}
    )


def test_adversarial_fork_resolution_with_mismatched_epoch_indices() -> None:
    base_state = canonical_epoch_state_vectors()[1]["epoch_state"]
    state_a = generate_epoch_state_record(copy.deepcopy(base_state))

    competing_state = copy.deepcopy(base_state)
    competing_state["candidate_block_hash"] = "block-gamma"
    competing_state["epoch_index"] = base_state["epoch_index"] + 1
    competing_state["parent_epoch_state_digest"] = "state-mismatch-parent"
    competing_state["quorum_state_digest"] = "quorum-state-mismatch"
    competing_state["quorum_record_digests"] = [f"{digest}-mismatch" for digest in base_state["quorum_record_digests"]]
    state_b = generate_epoch_state_record(competing_state)

    with pytest.raises(ConsensusFinalityEvaluatorError) as mismatch_error:
        resolve_fork([state_a, state_b])
    assert mismatch_error.value.token == "consensus_fork_resolution_epoch_index_mismatch"


def test_adversarial_fork_resolution_with_fewer_than_two_candidates() -> None:
    with pytest.raises(ConsensusFinalityEvaluatorError) as empty_error:
        resolve_fork([])
    assert empty_error.value.token == "consensus_fork_resolution_insufficient_candidates"

    single_state = generate_epoch_state_record(
        {
            "candidate_block_hash": "block-solo",
            "epoch_index": 33,
            "finality_status": "conflict",
            "parent_epoch_state_digest": "state-32-root",
            "quorum_record_digests": ["digest-single"],
            "quorum_state_digest": "quorum-state-33",
            "quorum_threshold": {"numerator": 2, "denominator": 3},
        }
    )
    with pytest.raises(ConsensusFinalityEvaluatorError) as single_error:
        resolve_fork([single_state])
    assert single_error.value.token == "consensus_fork_resolution_insufficient_candidates"


def test_phase_447_commit_touches_exactly_required_paths() -> None:
    commit_ref = _resolve_phase_447_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXPECTED_CHANGED_PATHS


def test_phase_447_commit_respects_non_mutation_boundaries() -> None:
    commit_ref = _resolve_phase_447_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)

    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
    assert not any(path.startswith("tools/") for path in changed_paths)
    assert not any(
        path.startswith(prefix)
        for prefix in (
            "ILC_release_track/",
            "release_engineering/",
            "docs/release_engineering/",
            "docs/packaging/",
        )
        for path in changed_paths
    )
