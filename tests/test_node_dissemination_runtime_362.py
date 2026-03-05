"""Phase-362 runtime tests for CDL-036 node dissemination implementation tranche."""

from __future__ import annotations

import copy
import subprocess
from pathlib import Path

from ilc_core.node import (
    CDL_036_DEPENDENCY,
    NODE_DISSEMINATION_RUNTIME_VERSION,
    VALIDATION_LIFECYCLE_DEPENDENCY,
    NodeDisseminationRuntimeError,
    canonical_node_dissemination_vectors,
    generate_node_dissemination_record,
    verify_node_dissemination_record,
)


DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
HANDOFF_PATH = Path("docs/specs/ilc_node_dissemination_runtime_handoff_362_v0.1.md")
PHASE_362_COMMIT_SUBJECT = "feat(g8): phase 362 cdl-036 node dissemination runtime implementation tranche"
RUNTIME_PATH = "ilc_core/node/node_dissemination_runtime_362.py"
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


def _resolve_phase_362_commit_ref() -> str:
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
        if subject.strip() == PHASE_362_COMMIT_SUBJECT:
            matching.append(commit_hash)

    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if RUNTIME_PATH in changed_paths:
            return commit_ref

    if matching:
        raise AssertionError("phase_362_commit_subject_present_but_no_runtime_commit")
    raise AssertionError("phase_362_commit_not_present_in_local_history")


def _assert_runtime_mutation_scope(commit_ref: str) -> None:
    changed_paths = _changed_paths_for_commit(commit_ref)

    assert DECISION_LOG_PATH not in changed_paths

    runtime_changes = [path for path in changed_paths if path.startswith("ilc_core/")]
    disallowed_runtime_changes = [
        path
        for path in runtime_changes
        if path not in {RUNTIME_PATH, NODE_INIT_PATH}
    ]
    assert not disallowed_runtime_changes, f"phase_362_runtime_scope_violation:{disallowed_runtime_changes}"

    forbidden_mutations = [path for path in changed_paths if path.startswith(FORBIDDEN_RUNTIME_PREFIXES)]
    assert not forbidden_mutations, f"phase_362_forbidden_runtime_mutations:{forbidden_mutations}"

    assert RUNTIME_PATH in changed_paths, "phase_362_runtime_file_missing_from_commit"


def test_runtime_surface_is_importable_and_invocable() -> None:
    vector = canonical_node_dissemination_vectors()[0]
    record = generate_node_dissemination_record(vector)
    verified = verify_node_dissemination_record(record)

    assert record["runtime_version"] == NODE_DISSEMINATION_RUNTIME_VERSION
    assert record["cdl_dependency"] == CDL_036_DEPENDENCY
    assert record["validation_lifecycle_dependency"] == VALIDATION_LIFECYCLE_DEPENDENCY
    assert isinstance(record["record_sha256"], str)

    assert verified["valid"] is True
    assert verified["runtime_version"] == NODE_DISSEMINATION_RUNTIME_VERSION


def test_runtime_constants_lock_exact_dependency_and_version_tokens() -> None:
    assert NODE_DISSEMINATION_RUNTIME_VERSION == "node_dissemination_runtime_362.v0.1"
    assert CDL_036_DEPENDENCY == "cdl_036_ratified_351.v0.1"
    assert VALIDATION_LIFECYCLE_DEPENDENCY == "validation_lifecycle_runtime_361.v0.1"


def test_deterministic_output_for_repeated_identical_vectors() -> None:
    vector = canonical_node_dissemination_vectors()[1]
    one = generate_node_dissemination_record(vector)
    two = generate_node_dissemination_record(vector)

    assert one == two
    assert verify_node_dissemination_record(one) == verify_node_dissemination_record(two)


def test_invalid_header_field_set_and_signature_scope_violations_fail_with_tokens() -> None:
    vector = canonical_node_dissemination_vectors()[0]
    record = generate_node_dissemination_record(vector)

    reordered_header_record = copy.deepcopy(record)
    original_header = reordered_header_record["envelopes"]["transport"]["header"]
    reordered_header_record["envelopes"]["transport"]["header"] = {
        "signature": original_header["signature"],
        "payload_cid": original_header["payload_cid"],
        "epoch_created": original_header["epoch_created"],
        "channel": original_header["channel"],
        "visibility": original_header["visibility"],
        "epistemic_type": original_header["epistemic_type"],
        "creator_agent_id": original_header["creator_agent_id"],
        "node_id": original_header["node_id"],
    }
    verified = verify_node_dissemination_record(reordered_header_record)
    assert verified["valid"] is True

    missing_header_field_record = copy.deepcopy(record)
    missing_header_field_record["envelopes"]["transport"]["header"].pop("payload_cid")
    try:
        verify_node_dissemination_record(missing_header_field_record)
        raise AssertionError("expected_header_field_set_invalid")
    except NodeDisseminationRuntimeError as exc:
        assert exc.token == "node_dissemination_header_field_set_invalid"

    signature_violation_record = copy.deepcopy(record)
    signature_violation_record["envelopes"]["transport"]["header"]["signature"] = "sig::tampered"
    try:
        verify_node_dissemination_record(signature_violation_record)
        raise AssertionError("expected_signature_scope_violation")
    except NodeDisseminationRuntimeError as exc:
        assert exc.token == "node_dissemination_signature_scope_violation"


def test_cid_pull_fetch_and_idempotence_semantics_are_enforced() -> None:
    record = generate_node_dissemination_record(canonical_node_dissemination_vectors()[0])
    fetch_contract = record["envelopes"]["transport"]["fetch_contract"]

    assert fetch_contract["fetch_mode"] == "cid_pull"
    assert fetch_contract["retry_safe"] is True
    assert fetch_contract["content_address_verified_before_interpretation"] is True
    assert isinstance(fetch_contract["idempotence_key"], str)
    assert len(fetch_contract["idempotence_key"]) == 64


def test_visibility_channel_routing_inputs_do_not_mutate_authored_payload() -> None:
    vector = canonical_node_dissemination_vectors()[1]
    authored_before = copy.deepcopy(vector["authored_payload"])

    record = generate_node_dissemination_record(vector)
    authored_after = record["envelopes"]["authored_payload"]

    assert authored_after == authored_before
    assert "routing_inputs" not in authored_after

    transport_routing = record["envelopes"]["transport"]["routing_inputs"]
    protocol_routing = record["envelopes"]["protocol_interpretation"]["routing_inputs"]
    assert transport_routing == {
        "visibility": authored_before["visibility"],
        "channel": authored_before["channel"],
    }
    assert protocol_routing == {
        "visibility": authored_before["visibility"],
        "channel": authored_before["channel"],
    }


def test_canonical_vectors_validate_generator_and_verifier_contract() -> None:
    vectors = canonical_node_dissemination_vectors()
    assert len(vectors) == 2

    for vector in vectors:
        record = generate_node_dissemination_record(vector)
        verified = verify_node_dissemination_record(record)
        checks = verified["checks"]
        assert [item["check_type"] for item in checks] == [
            "runtime_version_supported",
            "cdl_dependency_locked",
            "validation_lifecycle_dependency_locked",
            "header_signature_scope_enforced",
            "cid_pull_fetch_idempotence_enforced",
            "routing_inputs_are_transport_only",
            "record_digest_matches",
        ]
        assert all(item["passed"] is True for item in checks)


def test_runtime_handoff_contains_required_sections_and_tokens() -> None:
    assert HANDOFF_PATH.exists()
    text = HANDOFF_PATH.read_text(encoding="utf-8")
    for token in (
        "## 1. Implementation scope",
        "## 2. Dependency and version locks",
        "## 3. Header schema and signature-scope contract",
        "## 4. Fetch contract and idempotence semantics",
        "## 5. Visibility/channel routing-only contract",
        "## 6. Orderer-agnostic boundary statement",
        "## 7. Validation failure token catalog",
        "## 8. Carry-forward constraints for phase 363",
        "## 9. Non-goals",
        "node_dissemination_runtime_362.v0.1",
        "cdl_036_ratified_351.v0.1",
        "validation_lifecycle_runtime_361.v0.1",
        "header-first dissemination",
        "CID-addressed pull fetch",
        "pull-dominant with soft push-signals",
    ):
        assert token in text


def test_no_decision_log_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_362_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed_paths


def test_commit_anchored_runtime_mutation_scope_is_limited() -> None:
    commit_ref = _resolve_phase_362_commit_ref()
    _assert_runtime_mutation_scope(commit_ref)
