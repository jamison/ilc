from __future__ import annotations

import copy
import subprocess
from pathlib import Path

import pytest

from ilc_core.consensus.epoch_state_runtime import (
    canonical_epoch_state_vectors,
    generate_epoch_state_record,
)
from ilc_core.consensus.finality_evaluator import (
    CDL_051_RATIFICATION_DEPENDENCY,
    FINALITY_EVALUATOR_VERSION,
    ConsensusFinalityEvaluatorError,
    evaluate_epoch_finality,
    resolve_fork,
)


EVALUATOR_PATH = Path("ilc_core/consensus/finality_evaluator.py")
EPOCH_STATE_RUNTIME_PATH = Path("ilc_core/consensus/epoch_state_runtime.py")
HANDOFF_PATH = Path("docs/specs/ilc_consensus_runtime_finality_evaluator_handoff_445_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_445_SUBJECT_TOKEN = "runtime(g8): phase 445 deterministic finality evaluator and fork-resolution rules"
REQUIRED_HANDOFF_HEADINGS = (
    "## 1. Phase 445 runtime scope summary",
    "## 2. Ratified constitutional anchors",
    "## 3. Implemented runtime surfaces",
    "## 4. Finality evaluation algorithm and fork-resolution rule",
    "## 5. Test evidence and remaining runtime scope",
    "## 6. Non-goals and Phase 446 pointer",
)
REQUIRED_HANDOFF_TOKENS = (
    "Phase 445 implemented the deterministic finality evaluator and fork-resolution rule authorized by CDL-051.",
    "CDL-051 ratification evidence anchor: docs/specs/ilc_cdl_051_constitutional_consensus_and_epoch_finality_ratification_evidence_443_v0.1.md",
    "The fork-resolution rule is deterministic and operator-independent: the epoch-state record with the lexicographically smallest state_digest is selected as canonical.",
    "Phase 445 did not implement harness integration or network-bridge exercise; those remain assigned to Phase 446.",
    "Phase 445 did not mutate the constitutional decision log.",
    "Phase 445 did not perform DAG-CBOR or storage-format cutover.",
    "The finality evaluator requires explicit quorum-threshold input; no implicit constitutional threshold default was introduced in Phase 445.",
    "CDL-050 remains unopened and unaffected by Phase 445.",
    "Phase 446 is the next authorized consensus runtime phase.",
)
EXPECTED_CHANGED_PATHS = {
    "ilc_core/consensus/finality_evaluator.py",
    "tests/test_phase_445_consensus_runtime_ii_finality_evaluator_and_fork_resolution.py",
    "docs/specs/ilc_consensus_runtime_finality_evaluator_handoff_445_v0.1.md",
}
EXPECTED_FINALITY_RESULT_KEYS = [
    "finality_status",
    "canonical_block_hash",
    "aggregate_weights",
    "threshold_fraction",
    "fork_resolution_applied",
    "runtime_version",
    "dependency",
]
EXPECTED_FORK_RESOLUTION_RESULT_KEYS = [
    "selected_state_digest",
    "rule_applied",
    "candidate_count",
    "epoch_index",
    "runtime_version",
    "dependency",
]


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


def _resolve_phase_445_commit_ref() -> str:
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
        if subject.strip() != PHASE_445_SUBJECT_TOKEN:
            continue
        saw_subject = True
        if _changed_paths_for_commit(commit_hash) == EXPECTED_CHANGED_PATHS:
            return commit_hash
    if saw_subject:
        raise AssertionError("phase_445_commit_subject_present_but_no_qualifying_runtime_commit")
    raise AssertionError("phase_445_commit_not_present_in_local_history")


def test_evaluator_module_exports_exact_version_and_dependency() -> None:
    text = _read(HANDOFF_PATH)

    assert EVALUATOR_PATH.exists()
    assert HANDOFF_PATH.exists()
    assert FINALITY_EVALUATOR_VERSION == "finality_evaluator_445.v0.1"
    assert CDL_051_RATIFICATION_DEPENDENCY == "cdl_051_constitutional_consensus_and_epoch_finality_443.v0.1"
    for heading in REQUIRED_HANDOFF_HEADINGS:
        assert heading in text
    for token in REQUIRED_HANDOFF_TOKENS:
        assert token in text


def test_finality_evaluation_finalized_case_is_deterministic() -> None:
    quorum_records = [
        {"block_hash": "block-a", "epoch_index": 9, "vote_weight": 0.45},
        {"block_hash": "block-a", "epoch_index": 9, "vote_weight": 0.30},
        {"block_hash": "block-b", "epoch_index": 9, "vote_weight": 0.10},
    ]
    threshold = {"numerator": 2, "denominator": 3}

    one = evaluate_epoch_finality(copy.deepcopy(quorum_records), threshold)
    two = evaluate_epoch_finality(copy.deepcopy(quorum_records), threshold)

    assert one == two
    assert one["finality_status"] == "finalized"
    assert one["canonical_block_hash"] == "block-a"
    assert one["fork_resolution_applied"] is False
    assert list(one.keys()) == EXPECTED_FINALITY_RESULT_KEYS


def test_finality_evaluation_provisional_case_when_threshold_not_met() -> None:
    quorum_records = [
        {"block_hash": "block-a", "epoch_index": 10, "vote_weight": 0.20},
        {"block_hash": "block-a", "epoch_index": 10, "vote_weight": 0.15},
    ]
    threshold = {"numerator": 2, "denominator": 3}

    result = evaluate_epoch_finality(quorum_records, threshold)

    assert result["finality_status"] == "provisional"
    assert result["canonical_block_hash"] is None


def test_finality_evaluation_conflict_case_with_two_competing_blocks() -> None:
    quorum_records = canonical_epoch_state_vectors()[1]["quorum_records"]
    threshold = {"numerator": 2, "denominator": 3}

    result = evaluate_epoch_finality(quorum_records, threshold)

    assert result["finality_status"] == "conflict"
    assert result["canonical_block_hash"] is None
    assert len(result["aggregate_weights"]) >= 2


def test_fork_resolution_selects_lexicographic_minimum_state_digest() -> None:
    base_state = {
        "candidate_block_hash": "block-a",
        "epoch_index": 22,
        "finality_status": "conflict",
        "parent_epoch_state_digest": "state-21-root",
        "quorum_record_digests": ["digest-zeta"],
        "quorum_state_digest": "quorum-state-22",
        "quorum_threshold": {"numerator": 2, "denominator": 3},
    }
    candidate_a = generate_epoch_state_record(copy.deepcopy(base_state))
    base_state["candidate_block_hash"] = "block-b"
    base_state["quorum_record_digests"] = ["digest-alpha"]
    candidate_b = generate_epoch_state_record(copy.deepcopy(base_state))

    result = resolve_fork([candidate_a, candidate_b])

    assert result["rule_applied"] == "lexicographic_state_digest_minimum"
    assert result["selected_state_digest"] == min(candidate_a["state_digest"], candidate_b["state_digest"])
    assert result["candidate_count"] == 2
    assert list(result.keys()) == EXPECTED_FORK_RESOLUTION_RESULT_KEYS


def test_missing_threshold_and_insufficient_candidates_fail_with_deterministic_tokens() -> None:
    quorum_records = [{"block_hash": "block-a", "epoch_index": 15, "vote_weight": 0.25}]
    valid_threshold = {"numerator": 2, "denominator": 3}

    with pytest.raises(ConsensusFinalityEvaluatorError) as missing_threshold:
        evaluate_epoch_finality(quorum_records, quorum_threshold=None)
    assert missing_threshold.value.token == "consensus_finality_evaluator_quorum_threshold_missing"

    with pytest.raises(ConsensusFinalityEvaluatorError) as empty_records:
        evaluate_epoch_finality([], quorum_threshold=valid_threshold)
    assert empty_records.value.token == "consensus_finality_evaluator_quorum_records_empty"

    mixed_epoch_records = [
        {"block_hash": "block-a", "epoch_index": 15, "vote_weight": 0.25},
        {"block_hash": "block-a", "epoch_index": 16, "vote_weight": 0.25},
    ]
    with pytest.raises(ConsensusFinalityEvaluatorError) as mixed_epochs:
        evaluate_epoch_finality(mixed_epoch_records, quorum_threshold=valid_threshold)
    assert mixed_epochs.value.token == "consensus_finality_evaluator_epoch_index_mismatch"

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
    with pytest.raises(ConsensusFinalityEvaluatorError) as insufficient_candidates:
        resolve_fork([single_state])
    assert insufficient_candidates.value.token == "consensus_fork_resolution_insufficient_candidates"


def test_phase_445_commit_touches_exactly_required_paths() -> None:
    commit_ref = _resolve_phase_445_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXPECTED_CHANGED_PATHS


def test_phase_445_commit_respects_non_mutation_boundaries() -> None:
    commit_ref = _resolve_phase_445_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)

    assert str(DECISION_LOG_PATH) not in changed
    assert not any(
        path.startswith("ilc_core/") and path != str(EVALUATOR_PATH)
        for path in changed
    )
    assert str(EPOCH_STATE_RUNTIME_PATH) not in changed
    assert not any(path.startswith("tools/") for path in changed)
    assert not any(
        path.startswith(prefix)
        for prefix in (
            "docs/antigravity_tasks/",
            "docs/phases/",
            "ILC_release_track/",
            "release_engineering/",
        )
        for path in changed
    )
