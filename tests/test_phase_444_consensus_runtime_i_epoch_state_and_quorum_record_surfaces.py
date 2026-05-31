from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from ilc_core.consensus.epoch_state_runtime import (
    CDL_051_RATIFICATION_DEPENDENCY,
    EPOCH_STATE_RUNTIME_VERSION,
    ConsensusEpochStateValidationError,
    canonical_epoch_state_vectors,
    generate_epoch_state_record,
    generate_quorum_record,
    verify_epoch_state_record,
    verify_quorum_record,
)


RUNTIME_PATH = Path("ilc_core/consensus/epoch_state_runtime.py")
HANDOFF_PATH = Path("docs/specs/ilc_consensus_runtime_epoch_state_and_quorum_record_handoff_444_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_443_EVIDENCE_PATH = Path(
    "docs/specs/ilc_cdl_051_constitutional_consensus_and_epoch_finality_ratification_evidence_443_v0.1.md"
)
PHASE_444_SUBJECT_TOKEN = "runtime(g8): phase 444 epoch-state and quorum-record surfaces"
REQUIRED_HANDOFF_HEADINGS = (
    "## 1. Phase 444 runtime scope summary",
    "## 2. Ratified constitutional anchors",
    "## 3. Implemented runtime surfaces",
    "## 4. Canonical record shapes and provenance boundaries",
    "## 5. Test evidence and remaining runtime scope",
    "## 6. Non-goals and Phase 445 pointer",
)
REQUIRED_HANDOFF_TOKENS = (
    "Phase 444 implemented only the ratified epoch-state and quorum-record runtime surfaces authorized by CDL-051.",
    "CDL-051 ratification evidence anchor: docs/specs/ilc_cdl_051_constitutional_consensus_and_epoch_finality_ratification_evidence_443_v0.1.md",
    "The Phase-444 runtime surface is JSON-first, deterministic, and machine-auditable.",
    "Phase 444 did not implement deterministic finality evaluation or fork-resolution selection; those remain assigned to Phase 445.",
    "Phase 444 did not mutate the constitutional decision log.",
    "Phase 444 did not perform DAG-CBOR or storage-format cutover.",
    "The epoch-state runtime requires explicit quorum-threshold input; no implicit constitutional threshold default was introduced in Phase 444.",
    "CDL-050 remains unopened and unaffected by Phase 444.",
    "Phase 445 is the next authorized consensus runtime phase.",
)
EXPECTED_QUORUM_RECORD_KEYS = [
    "attestation_ref",
    "block_hash",
    "epoch_index",
    "quorum_state_digest",
    "record_digest",
    "validator_id",
    "vote_weight",
]
EXPECTED_QUORUM_VERIFY_KEYS = [
    "valid",
    "record_digest",
    "runtime_version",
    "dependency",
    "checks",
]
EXPECTED_QUORUM_CHECKS = [
    "epoch_index_valid",
    "validator_id_present",
    "block_hash_present",
    "quorum_state_digest_present",
    "vote_weight_positive",
    "attestation_ref_present",
    "record_digest_matches",
]
EXPECTED_EPOCH_STATE_KEYS = [
    "candidate_block_hash",
    "epoch_index",
    "finality_status",
    "parent_epoch_state_digest",
    "quorum_record_digests",
    "quorum_state_digest",
    "quorum_threshold",
    "state_digest",
]
EXPECTED_EPOCH_VERIFY_KEYS = [
    "valid",
    "state_digest",
    "runtime_version",
    "dependency",
    "checks",
]
EXPECTED_EPOCH_CHECKS = [
    "epoch_index_valid",
    "candidate_block_hash_present",
    "quorum_state_digest_present",
    "parent_epoch_state_digest_present",
    "quorum_threshold_valid",
    "quorum_record_digests_non_empty",
    "finality_status_supported",
    "state_digest_matches",
]
EXPECTED_CHANGED_PATHS = {
    "ilc_core/consensus/epoch_state_runtime.py",
    "tests/test_phase_444_consensus_runtime_i_epoch_state_and_quorum_record_surfaces.py",
    "docs/specs/ilc_consensus_runtime_epoch_state_and_quorum_record_handoff_444_v0.1.md",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _stable_sha256(value: Any) -> str:
    return hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_444_commit_ref() -> str:
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
        if subject.strip() != PHASE_444_SUBJECT_TOKEN:
            continue
        saw_subject = True
        if _changed_paths_for_commit(commit_hash) == EXPECTED_CHANGED_PATHS:
            return commit_hash
    if saw_subject:
        raise AssertionError("phase_444_commit_subject_present_but_no_qualifying_runtime_commit")
    raise AssertionError("phase_444_commit_not_present_in_local_history")


def test_runtime_module_exports_exact_version_dependency_and_vector_surface() -> None:
    vectors = canonical_epoch_state_vectors()

    assert RUNTIME_PATH.exists()
    assert EPOCH_STATE_RUNTIME_VERSION == "epoch_state_runtime_444.v0.1"
    assert CDL_051_RATIFICATION_DEPENDENCY == "cdl_051_constitutional_consensus_and_epoch_finality_443.v0.1"
    assert len(vectors) == 2


def test_quorum_record_generation_and_verification_are_deterministic() -> None:
    vector = canonical_epoch_state_vectors()[0]
    raw_record = copy.deepcopy(vector["quorum_records"][0])

    one = generate_quorum_record(raw_record)
    two = generate_quorum_record(raw_record)
    payload = {key: one[key] for key in one if key != "record_digest"}
    verified = verify_quorum_record(one)

    assert one == two
    assert list(one.keys()) == EXPECTED_QUORUM_RECORD_KEYS
    assert one["record_digest"] == _stable_sha256(payload)
    assert list(verified.keys()) == EXPECTED_QUORUM_VERIFY_KEYS
    assert [item["check_type"] for item in verified["checks"]] == EXPECTED_QUORUM_CHECKS
    assert verified["runtime_version"] == EPOCH_STATE_RUNTIME_VERSION
    assert verified["dependency"] == CDL_051_RATIFICATION_DEPENDENCY
    assert verified["valid"] is True


def test_epoch_state_record_generation_and_verification_are_deterministic() -> None:
    vector = canonical_epoch_state_vectors()[0]
    raw_record = copy.deepcopy(vector["epoch_state"])

    one = generate_epoch_state_record(raw_record)
    two = generate_epoch_state_record(raw_record)
    payload = {key: one[key] for key in one if key != "state_digest"}
    verified = verify_epoch_state_record(one)

    assert one == two
    assert list(one.keys()) == EXPECTED_EPOCH_STATE_KEYS
    assert one["quorum_record_digests"] == sorted(set(one["quorum_record_digests"]))
    assert one["state_digest"] == _stable_sha256(payload)
    assert list(verified.keys()) == EXPECTED_EPOCH_VERIFY_KEYS
    assert [item["check_type"] for item in verified["checks"]] == EXPECTED_EPOCH_CHECKS
    assert verified["runtime_version"] == EPOCH_STATE_RUNTIME_VERSION
    assert verified["dependency"] == CDL_051_RATIFICATION_DEPENDENCY
    assert verified["valid"] is True


def test_verifiers_report_digest_mismatch_without_trivial_success() -> None:
    vector = canonical_epoch_state_vectors()[0]
    quorum_record = generate_quorum_record(copy.deepcopy(vector["quorum_records"][0]))
    quorum_record["record_digest"] = "malformed"
    quorum_verified = verify_quorum_record(quorum_record)

    epoch_record = generate_epoch_state_record(copy.deepcopy(vector["epoch_state"]))
    epoch_record["state_digest"] = "malformed"
    epoch_verified = verify_epoch_state_record(epoch_record)

    assert quorum_verified["valid"] is False
    assert quorum_verified["checks"][-1] == {
        "check_type": "record_digest_matches",
        "passed": False,
    }
    assert epoch_verified["valid"] is False
    assert epoch_verified["checks"][-1] == {
        "check_type": "state_digest_matches",
        "passed": False,
    }


def test_conflict_state_vector_is_preserved_without_fork_resolution_selection() -> None:
    vector = canonical_epoch_state_vectors()[1]
    record = generate_epoch_state_record(copy.deepcopy(vector["epoch_state"]))
    verified = verify_epoch_state_record(record)

    assert record["finality_status"] == "conflict"
    assert verified["valid"] is True
    assert list(record.keys()) == EXPECTED_EPOCH_STATE_KEYS
    assert "canonical_fork_choice" not in record


def test_missing_or_invalid_threshold_and_weight_fail_with_deterministic_tokens() -> None:
    vector = canonical_epoch_state_vectors()[0]
    epoch_state = copy.deepcopy(vector["epoch_state"])
    epoch_state.pop("quorum_threshold")

    with pytest.raises(ConsensusEpochStateValidationError) as missing_threshold:
        generate_epoch_state_record(epoch_state)
    assert missing_threshold.value.token == "consensus_epoch_state_quorum_threshold_missing"

    quorum_record = copy.deepcopy(vector["quorum_records"][0])
    quorum_record["vote_weight"] = 0.0
    with pytest.raises(ConsensusEpochStateValidationError) as invalid_weight:
        generate_quorum_record(quorum_record)
    assert invalid_weight.value.token == "consensus_quorum_record_vote_weight_invalid"


def test_handoff_exists_and_contains_required_headings_and_tokens() -> None:
    text = _read(HANDOFF_PATH)

    assert HANDOFF_PATH.exists()
    for heading in REQUIRED_HANDOFF_HEADINGS:
        assert heading in text
    for token in REQUIRED_HANDOFF_TOKENS:
        assert token in text
    assert str(PHASE_443_EVIDENCE_PATH) in text


def test_phase_444_commit_touches_exactly_required_paths() -> None:
    commit_ref = _resolve_phase_444_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXPECTED_CHANGED_PATHS


def test_phase_444_commit_respects_non_mutation_boundaries() -> None:
    commit_ref = _resolve_phase_444_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)

    assert str(DECISION_LOG_PATH) not in changed
    assert {path for path in changed if path.startswith("ilc_core/")} == {str(RUNTIME_PATH)}
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
