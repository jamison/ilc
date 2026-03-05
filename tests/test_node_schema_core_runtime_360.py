"""Phase-360 runtime tests for CDL-034 node schema core implementation tranche."""

from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.node import (
    CDL_034_DEPENDENCY,
    NODE_SCHEMA_CORE_RUNTIME_VERSION,
    SCHEMA_BASELINE_DEPENDENCY,
    NodeSchemaCoreValidationError,
    canonical_node_schema_core_vectors,
    generate_node_schema_core_record,
    verify_node_schema_core_record,
)


DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
HANDOFF_PATH = Path("docs/specs/ilc_node_schema_core_runtime_handoff_360_v0.1.md")
PHASE_360_COMMIT_SUBJECT = "feat(g8): phase 360 cdl-034 node schema core runtime implementation tranche"
RUNTIME_PATH = "ilc_core/node/node_schema_core_runtime_360.py"
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


def _resolve_phase_360_commit_ref() -> str:
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
        if subject.strip() == PHASE_360_COMMIT_SUBJECT:
            matching.append(commit_hash)

    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if RUNTIME_PATH in changed_paths:
            return commit_ref

    if matching:
        raise AssertionError("phase_360_commit_subject_present_but_no_runtime_commit")
    raise AssertionError("phase_360_commit_not_present_in_local_history")


def _assert_runtime_mutation_scope(commit_ref: str) -> None:
    changed_paths = _changed_paths_for_commit(commit_ref)

    assert DECISION_LOG_PATH not in changed_paths

    runtime_changes = [path for path in changed_paths if path.startswith("ilc_core/")]
    disallowed_runtime_changes = [
        path
        for path in runtime_changes
        if path not in {RUNTIME_PATH, NODE_INIT_PATH}
    ]
    assert not disallowed_runtime_changes, f"phase_360_runtime_scope_violation:{disallowed_runtime_changes}"

    forbidden_mutations = [path for path in changed_paths if path.startswith(FORBIDDEN_RUNTIME_PREFIXES)]
    assert not forbidden_mutations, f"phase_360_forbidden_runtime_mutations:{forbidden_mutations}"

    assert RUNTIME_PATH in changed_paths, "phase_360_runtime_file_missing_from_commit"


def test_runtime_surface_is_invocable() -> None:
    vector = canonical_node_schema_core_vectors()[0]
    record = generate_node_schema_core_record(vector)
    verified = verify_node_schema_core_record(record)

    assert record["runtime_version"] == NODE_SCHEMA_CORE_RUNTIME_VERSION
    assert record["cdl_dependency"] == CDL_034_DEPENDENCY
    assert record["schema_dependency"] == SCHEMA_BASELINE_DEPENDENCY
    assert isinstance(record["record_sha256"], str)

    assert verified["valid"] is True
    assert verified["runtime_version"] == NODE_SCHEMA_CORE_RUNTIME_VERSION


def test_runtime_constants_lock_exact_dependency_and_version_tokens() -> None:
    assert NODE_SCHEMA_CORE_RUNTIME_VERSION == "node_schema_core_runtime_360.v0.1"
    assert CDL_034_DEPENDENCY == "cdl_034_ratified_349.v0.1"
    assert SCHEMA_BASELINE_DEPENDENCY == "d2_schema_baseline_310.v0.1"


def test_deterministic_output_for_repeated_identical_input_vectors() -> None:
    vector = canonical_node_schema_core_vectors()[0]
    one = generate_node_schema_core_record(vector)
    two = generate_node_schema_core_record(vector)

    assert one == two
    assert verify_node_schema_core_record(one) == verify_node_schema_core_record(two)


def test_invalid_authored_payload_inputs_fail_with_deterministic_tokens() -> None:
    vector = canonical_node_schema_core_vectors()[0]

    invalid_gate_routing = {"authored_payload": dict(vector["authored_payload"], gate_routing="popperian_eligible")}
    try:
        generate_node_schema_core_record(invalid_gate_routing)
        raise AssertionError("expected_gate_routing_submitter_forbidden")
    except NodeSchemaCoreValidationError as exc:
        assert exc.token == "node_schema_gate_routing_submitter_forbidden"

    invalid_primitive = {
        "authored_payload": dict(vector["authored_payload"], primitive_type="refutation")
    }
    try:
        generate_node_schema_core_record(invalid_primitive)
        raise AssertionError("expected_refutation_not_default_primitive")
    except NodeSchemaCoreValidationError as exc:
        assert exc.token == "node_schema_refutation_not_default_primitive"


def test_reserved_field_collision_rules_and_gate_routing_derived_enforcement() -> None:
    vector = canonical_node_schema_core_vectors()[0]
    invalid_meta = {
        "authored_payload": dict(
            vector["authored_payload"],
            meta={"visibility": "shadow"},
        )
    }

    try:
        generate_node_schema_core_record(invalid_meta)
        raise AssertionError("expected_reserved_field_collision")
    except NodeSchemaCoreValidationError as exc:
        assert exc.token == "node_schema_reserved_field_shadow"


def test_canonical_vectors_validate_generator_and_verifier_surface() -> None:
    vectors = canonical_node_schema_core_vectors()
    assert len(vectors) == 2

    for vector in vectors:
        record = generate_node_schema_core_record(vector)
        verified = verify_node_schema_core_record(record)
        assert verified["valid"] is True
        checks = verified["checks"]
        assert [item["check_type"] for item in checks] == [
            "runtime_version_supported",
            "cdl_dependency_locked",
            "schema_dependency_locked",
            "gate_routing_protocol_derived",
            "record_digest_matches",
        ]
        assert all(item["passed"] is True for item in checks)


def test_runtime_handoff_records_boundary_and_dependency_notes() -> None:
    assert HANDOFF_PATH.exists()
    text = HANDOFF_PATH.read_text(encoding="utf-8")
    for token in (
        "## 1. Implementation scope",
        "## 2. Dependency and version locks",
        "## 3. Envelope-boundary runtime semantics",
        "## 4. Reserved-field collision enforcement",
        "## 5. Validation failure token catalog",
        "## 6. Deterministic vector and digest behavior",
        "## 7. Carry-forward constraints for phase 361",
        "## 8. Non-goals",
        "node_schema_core_runtime_360.v0.1",
        "cdl_034_ratified_349.v0.1",
        "d2_schema_baseline_310.v0.1",
        "gate_routing",
        "confidence",
        "uncertainty_note",
        "refutation is not a default primitive_type",
    ):
        assert token in text


def test_no_decision_log_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_360_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed_paths


def test_commit_anchored_runtime_mutation_scope_is_limited() -> None:
    commit_ref = _resolve_phase_360_commit_ref()
    _assert_runtime_mutation_scope(commit_ref)
