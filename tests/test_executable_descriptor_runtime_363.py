"""Phase-363 runtime tests for CDL-037 executable descriptor implementation tranche."""

from __future__ import annotations

import copy
import subprocess
from pathlib import Path

from ilc_core.node import (
    CDL_037_DEPENDENCY,
    EXECUTABLE_DESCRIPTOR_RUNTIME_VERSION,
    NODE_DISSEMINATION_DEPENDENCY,
    ExecutableDescriptorRuntimeError,
    canonical_executable_descriptor_vectors,
    generate_executable_descriptor_record,
    verify_executable_descriptor_record,
)


DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
HANDOFF_PATH = Path("docs/specs/ilc_executable_descriptor_runtime_handoff_363_v0.1.md")
PHASE_363_COMMIT_SUBJECT = "feat(g8): phase 363 cdl-037 executable descriptor runtime implementation tranche"
RUNTIME_PATH = "ilc_core/node/executable_descriptor_runtime_363.py"
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


def _resolve_phase_363_commit_ref() -> str:
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
        if subject.strip() == PHASE_363_COMMIT_SUBJECT:
            matching.append(commit_hash)

    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if RUNTIME_PATH in changed_paths:
            return commit_ref

    if matching:
        raise AssertionError("phase_363_commit_subject_present_but_no_runtime_commit")
    raise AssertionError("phase_363_commit_not_present_in_local_history")


def _assert_runtime_mutation_scope(commit_ref: str) -> None:
    changed_paths = _changed_paths_for_commit(commit_ref)

    assert DECISION_LOG_PATH not in changed_paths

    runtime_changes = [path for path in changed_paths if path.startswith("ilc_core/")]
    disallowed_runtime_changes = [
        path
        for path in runtime_changes
        if path not in {RUNTIME_PATH, NODE_INIT_PATH}
    ]
    assert not disallowed_runtime_changes, f"phase_363_runtime_scope_violation:{disallowed_runtime_changes}"

    forbidden_mutations = [path for path in changed_paths if path.startswith(FORBIDDEN_RUNTIME_PREFIXES)]
    assert not forbidden_mutations, f"phase_363_forbidden_runtime_mutations:{forbidden_mutations}"

    assert RUNTIME_PATH in changed_paths, "phase_363_runtime_file_missing_from_commit"


def test_runtime_surface_is_importable_and_invocable() -> None:
    vector = canonical_executable_descriptor_vectors()[0]
    record = generate_executable_descriptor_record(vector)
    verified = verify_executable_descriptor_record(record)

    assert record["runtime_version"] == EXECUTABLE_DESCRIPTOR_RUNTIME_VERSION
    assert record["cdl_dependency"] == CDL_037_DEPENDENCY
    assert record["node_dissemination_dependency"] == NODE_DISSEMINATION_DEPENDENCY
    assert isinstance(record["record_sha256"], str)

    assert verified["valid"] is True
    assert verified["runtime_version"] == EXECUTABLE_DESCRIPTOR_RUNTIME_VERSION


def test_runtime_constants_lock_exact_dependency_and_version_tokens() -> None:
    assert EXECUTABLE_DESCRIPTOR_RUNTIME_VERSION == "executable_descriptor_runtime_363.v0.1"
    assert CDL_037_DEPENDENCY == "cdl_037_ratified_352.v0.1"
    assert NODE_DISSEMINATION_DEPENDENCY == "node_dissemination_runtime_362.v0.1"


def test_deterministic_output_for_repeated_identical_vectors() -> None:
    vector = canonical_executable_descriptor_vectors()[1]
    one = generate_executable_descriptor_record(vector)
    two = generate_executable_descriptor_record(vector)

    assert one == two
    assert verify_executable_descriptor_record(one) == verify_executable_descriptor_record(two)


def test_invalid_descriptor_shapes_and_safety_contract_failures_use_deterministic_tokens() -> None:
    vector = canonical_executable_descriptor_vectors()[0]

    invalid_descriptor = copy.deepcopy(vector)
    invalid_descriptor["authored_payload"]["descriptor"].pop("declared_inputs")
    try:
        generate_executable_descriptor_record(invalid_descriptor)
        raise AssertionError("expected_descriptor_field_invalid")
    except ExecutableDescriptorRuntimeError as exc:
        assert exc.token == "executable_descriptor_field_invalid"

    invalid_contract = copy.deepcopy(vector)
    invalid_contract["authored_payload"]["safety_contract_ref"] = "contract://wrong-for-genesis"
    try:
        generate_executable_descriptor_record(invalid_contract)
        raise AssertionError("expected_genesis_boundary_violation")
    except ExecutableDescriptorRuntimeError as exc:
        assert exc.token == "executable_genesis_boundary_violation"


def test_genesis_trusted_boundary_semantics_are_enforced() -> None:
    genesis_vector = canonical_executable_descriptor_vectors()[0]
    non_genesis_vector = canonical_executable_descriptor_vectors()[1]

    genesis_record = generate_executable_descriptor_record(genesis_vector)
    non_genesis_record = generate_executable_descriptor_record(non_genesis_vector)

    assert genesis_record["envelopes"]["protocol_interpretation"]["descriptor_class"] == "genesis_trusted"
    assert non_genesis_record["envelopes"]["protocol_interpretation"]["descriptor_class"] == "non_genesis"


def test_execution_context_remains_outside_authored_payload() -> None:
    vector = canonical_executable_descriptor_vectors()[0]
    authored_before = copy.deepcopy(vector["authored_payload"])

    record = generate_executable_descriptor_record(vector)
    authored_after = record["envelopes"]["authored_payload"]

    assert authored_after == authored_before
    assert "execution_context" not in authored_after

    runtime_binding = record["envelopes"]["runtime_binding"]
    assert runtime_binding["runtime_binding"] == "sandboxed_agent_runtime"
    assert runtime_binding["recommendation_only"] is True
    assert runtime_binding["self_authorized_execution"] is False


def test_canonical_vectors_validate_generator_and_verifier_contract() -> None:
    vectors = canonical_executable_descriptor_vectors()
    assert len(vectors) == 2

    for vector in vectors:
        record = generate_executable_descriptor_record(vector)
        verified = verify_executable_descriptor_record(record)
        checks = verified["checks"]
        assert [item["check_type"] for item in checks] == [
            "runtime_version_supported",
            "cdl_dependency_locked",
            "node_dissemination_dependency_locked",
            "sandboxed_runtime_binding_enforced",
            "safety_contract_boundary_enforced",
            "genesis_trust_boundary_enforced",
            "record_digest_matches",
        ]
        assert all(item["passed"] is True for item in checks)


def test_runtime_handoff_contains_required_sections_and_tokens() -> None:
    assert HANDOFF_PATH.exists()
    text = HANDOFF_PATH.read_text(encoding="utf-8")
    for token in (
        "## 1. Implementation scope",
        "## 2. Dependency and version locks",
        "## 3. Descriptor field contract",
        "## 4. Sandboxed runtime binding contract",
        "## 5. Safety-contract verification and genesis-trust boundary",
        "## 6. Authored-envelope and transport-boundary preservation statement",
        "## 7. Validation failure token catalog",
        "## 8. Carry-forward constraints for phase 364",
        "## 9. Non-goals",
        "executable_descriptor_runtime_363.v0.1",
        "cdl_037_ratified_352.v0.1",
        "node_dissemination_runtime_362.v0.1",
        "Nodes recommend logic; they do not self-authorize execution.",
        "structured descriptor with sandboxed runtime binding",
        "agent-side sandboxing is a safety-contract obligation",
    ):
        assert token in text


def test_no_decision_log_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_363_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed_paths


def test_commit_anchored_runtime_mutation_scope_is_limited() -> None:
    commit_ref = _resolve_phase_363_commit_ref()
    _assert_runtime_mutation_scope(commit_ref)
