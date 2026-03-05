"""Phase-361 runtime tests for CDL-035 validation lifecycle implementation tranche."""

from __future__ import annotations

import copy
import subprocess
from pathlib import Path

from ilc_core.node import (
    CDL_035_DEPENDENCY,
    NODE_SCHEMA_CORE_DEPENDENCY,
    VALIDATION_LIFECYCLE_RUNTIME_VERSION,
    ValidationLifecycleRuntimeError,
    canonical_validation_lifecycle_vectors,
    generate_validation_lifecycle_record,
    verify_validation_lifecycle_record,
)


DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
HANDOFF_PATH = Path("docs/specs/ilc_validation_lifecycle_runtime_handoff_361_v0.1.md")
PHASE_361_COMMIT_SUBJECT = "feat(g8): phase 361 cdl-035 validation lifecycle runtime implementation tranche"
RUNTIME_PATH = "ilc_core/node/validation_lifecycle_runtime_361.py"
NODE_INIT_PATH = "ilc_core/node/__init__.py"

FORBIDDEN_RUNTIME_PREFIXES = (
    "ilc_core/consensus/",
    "ilc_core/security/",
    "ilc_core/ledger/",
    "ilc_core/issuance/",
    "ilc_core/genesis/",
    "ilc_core/epoch/",
    "ilc_core/network/",
    "ilc_core/d2e/",
    "ilc_core/cli/",
)


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_361_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )

    matching: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_361_COMMIT_SUBJECT:
            matching.append(commit_hash)

    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if RUNTIME_PATH in changed_paths:
            return commit_ref

    if matching:
        raise AssertionError("phase_361_commit_subject_present_but_no_runtime_commit")
    raise AssertionError("phase_361_commit_not_present_in_local_history")


def _assert_runtime_mutation_scope(commit_ref: str) -> None:
    changed_paths = _changed_paths_for_commit(commit_ref)

    assert DECISION_LOG_PATH not in changed_paths

    runtime_changes = [path for path in changed_paths if path.startswith("ilc_core/")]
    disallowed_runtime_changes = [
        path
        for path in runtime_changes
        if path not in {RUNTIME_PATH, NODE_INIT_PATH}
    ]
    assert not disallowed_runtime_changes, f"phase_361_runtime_scope_violation:{disallowed_runtime_changes}"

    forbidden_mutations = [path for path in changed_paths if path.startswith(FORBIDDEN_RUNTIME_PREFIXES)]
    assert not forbidden_mutations, f"phase_361_forbidden_runtime_mutations:{forbidden_mutations}"

    assert RUNTIME_PATH in changed_paths, "phase_361_runtime_file_missing_from_commit"


def test_runtime_surface_is_importable_and_invocable() -> None:
    vector = canonical_validation_lifecycle_vectors()[0]
    record = generate_validation_lifecycle_record(vector)
    verified = verify_validation_lifecycle_record(record)

    assert record["runtime_version"] == VALIDATION_LIFECYCLE_RUNTIME_VERSION
    assert record["cdl_dependency"] == CDL_035_DEPENDENCY
    assert record["node_schema_dependency"] == NODE_SCHEMA_CORE_DEPENDENCY
    assert isinstance(record["record_sha256"], str)

    assert verified["valid"] is True
    assert verified["runtime_version"] == VALIDATION_LIFECYCLE_RUNTIME_VERSION


def test_runtime_constants_lock_exact_dependency_and_version_tokens() -> None:
    assert VALIDATION_LIFECYCLE_RUNTIME_VERSION == "validation_lifecycle_runtime_361.v0.1"
    assert CDL_035_DEPENDENCY == "cdl_035_ratified_350.v0.1"
    assert NODE_SCHEMA_CORE_DEPENDENCY == "node_schema_core_runtime_360.v0.1"


def test_deterministic_output_for_repeated_identical_vectors() -> None:
    vector = canonical_validation_lifecycle_vectors()[1]
    one = generate_validation_lifecycle_record(vector)
    two = generate_validation_lifecycle_record(vector)

    assert one == two
    assert verify_validation_lifecycle_record(one) == verify_validation_lifecycle_record(two)


def test_invalid_transition_and_gate_verdict_inputs_fail_with_tokens() -> None:
    vector = canonical_validation_lifecycle_vectors()[0]

    invalid_transition = {
        "authored_payload": vector["authored_payload"],
        "transition": {
            "from_state": "proposed",
            "to_state": "finalized",
            "gate_verdict_ref": None,
        },
    }
    try:
        generate_validation_lifecycle_record(invalid_transition)
        raise AssertionError("expected_transition_forbidden")
    except ValidationLifecycleRuntimeError as exc:
        assert exc.token == "validation_lifecycle_transition_forbidden"

    missing_gate_ref = {
        "authored_payload": vector["authored_payload"],
        "transition": {
            "from_state": "under_review",
            "to_state": "quarantined",
            "gate_verdict_ref": None,
        },
    }
    try:
        generate_validation_lifecycle_record(missing_gate_ref)
        raise AssertionError("expected_gate_verdict_ref_required")
    except ValidationLifecycleRuntimeError as exc:
        assert exc.token == "validation_lifecycle_gate_verdict_ref_required"


def test_gate_verdict_attachment_is_by_reference_and_authored_payload_is_immutable() -> None:
    vector = canonical_validation_lifecycle_vectors()[1]
    authored_before = copy.deepcopy(vector["authored_payload"])

    record = generate_validation_lifecycle_record(vector)
    protocol = record["envelopes"]["protocol_interpretation"]
    authored_after = record["envelopes"]["authored_payload"]

    assert authored_before == authored_after
    assert "gate_verdict_ref" not in authored_after
    assert protocol["gate_verdict_ref"] == vector["transition"]["gate_verdict_ref"]


def test_quarantine_transition_semantics_are_enforced() -> None:
    vector = canonical_validation_lifecycle_vectors()[1]
    record = generate_validation_lifecycle_record(vector)

    protocol = record["envelopes"]["protocol_interpretation"]
    assert protocol["lifecycle_state"] == "quarantined"
    assert protocol["previous_lifecycle_state"] == "under_review"
    assert protocol["transition_edge"] == "under_review->quarantined"


def test_canonical_vectors_validate_generator_and_verifier_contract() -> None:
    vectors = canonical_validation_lifecycle_vectors()
    assert len(vectors) == 2

    for vector in vectors:
        record = generate_validation_lifecycle_record(vector)
        verified = verify_validation_lifecycle_record(record)
        checks = verified["checks"]
        assert [item["check_type"] for item in checks] == [
            "runtime_version_supported",
            "cdl_dependency_locked",
            "node_schema_dependency_locked",
            "gate_verdict_attached_by_reference",
            "quarantine_transition_semantics_enforced",
            "record_digest_matches",
        ]
        assert all(item["passed"] is True for item in checks)


def test_runtime_handoff_contains_required_sections_and_tokens() -> None:
    assert HANDOFF_PATH.exists()
    text = HANDOFF_PATH.read_text(encoding="utf-8")
    for token in (
        "## 1. Implementation scope",
        "## 2. Dependency and version locks",
        "## 3. Lifecycle state machine and transition matrix",
        "## 4. Gate-verdict by-reference attachment contract",
        "## 5. Quarantine handling contract",
        "## 6. Validation failure token catalog",
        "## 7. Carry-forward constraints for phase 362",
        "## 8. Non-goals",
        "validation_lifecycle_runtime_361.v0.1",
        "cdl_035_ratified_350.v0.1",
        "node_schema_core_runtime_360.v0.1",
        "authored payload remains immutable",
        "gate verdict references",
        "quarantine",
    ):
        assert token in text


def test_no_decision_log_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_361_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed_paths


def test_commit_anchored_runtime_mutation_scope_is_limited() -> None:
    commit_ref = _resolve_phase_361_commit_ref()
    _assert_runtime_mutation_scope(commit_ref)
