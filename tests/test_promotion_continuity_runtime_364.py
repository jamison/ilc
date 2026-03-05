"""Phase-364 runtime tests for CDL-038 promotion continuity implementation tranche."""

from __future__ import annotations

import copy
import subprocess
from pathlib import Path

from ilc_core.node import (
    CDL_038_DEPENDENCY,
    EXECUTABLE_DESCRIPTOR_DEPENDENCY,
    PROMOTION_CONTINUITY_RUNTIME_VERSION,
    PromotionContinuityRuntimeError,
    canonical_promotion_continuity_vectors,
    generate_promotion_continuity_record,
    verify_promotion_continuity_record,
)


DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
HANDOFF_PATH = Path("docs/specs/ilc_promotion_continuity_runtime_handoff_364_v0.1.md")
PHASE_364_COMMIT_SUBJECT = "feat(g8): phase 364 cdl-038 promotion continuity runtime implementation tranche"
RUNTIME_PATH = "ilc_core/node/promotion_continuity_runtime_364.py"
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


def _resolve_phase_364_commit_ref() -> str:
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
        if subject.strip() == PHASE_364_COMMIT_SUBJECT:
            matching.append(commit_hash)

    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if RUNTIME_PATH in changed_paths:
            return commit_ref

    if matching:
        raise AssertionError("phase_364_commit_subject_present_but_no_runtime_commit")
    raise AssertionError("phase_364_commit_not_present_in_local_history")


def _assert_runtime_mutation_scope(commit_ref: str) -> None:
    changed_paths = _changed_paths_for_commit(commit_ref)

    assert DECISION_LOG_PATH not in changed_paths

    runtime_changes = [path for path in changed_paths if path.startswith("ilc_core/")]
    disallowed_runtime_changes = [
        path
        for path in runtime_changes
        if path not in {RUNTIME_PATH, NODE_INIT_PATH}
    ]
    assert not disallowed_runtime_changes, f"phase_364_runtime_scope_violation:{disallowed_runtime_changes}"

    forbidden_mutations = [path for path in changed_paths if path.startswith(FORBIDDEN_RUNTIME_PREFIXES)]
    assert not forbidden_mutations, f"phase_364_forbidden_runtime_mutations:{forbidden_mutations}"

    assert RUNTIME_PATH in changed_paths, "phase_364_runtime_file_missing_from_commit"


def test_runtime_surface_is_importable_and_invocable() -> None:
    vector = canonical_promotion_continuity_vectors()[0]
    record = generate_promotion_continuity_record(vector)
    verified = verify_promotion_continuity_record(record)

    assert record["runtime_version"] == PROMOTION_CONTINUITY_RUNTIME_VERSION
    assert record["cdl_dependency"] == CDL_038_DEPENDENCY
    assert record["executable_descriptor_dependency"] == EXECUTABLE_DESCRIPTOR_DEPENDENCY
    assert isinstance(record["record_sha256"], str)

    assert verified["valid"] is True
    assert verified["runtime_version"] == PROMOTION_CONTINUITY_RUNTIME_VERSION


def test_runtime_constants_lock_exact_dependency_and_version_tokens() -> None:
    assert PROMOTION_CONTINUITY_RUNTIME_VERSION == "promotion_continuity_runtime_364.v0.1"
    assert CDL_038_DEPENDENCY == "cdl_038_ratified_353.v0.1"
    assert EXECUTABLE_DESCRIPTOR_DEPENDENCY == "executable_descriptor_runtime_363.v0.1"


def test_deterministic_output_for_repeated_identical_vectors() -> None:
    vector = canonical_promotion_continuity_vectors()[1]
    one = generate_promotion_continuity_record(vector)
    two = generate_promotion_continuity_record(vector)

    assert one == two
    assert verify_promotion_continuity_record(one) == verify_promotion_continuity_record(two)


def test_invalid_receipt_shape_and_visibility_transitions_fail_with_tokens() -> None:
    vector = canonical_promotion_continuity_vectors()[0]

    reordered_receipt = {
        "public_successor_node_cid": vector["promotion_receipt"]["public_successor_node_cid"],
        "promotion_epoch": vector["promotion_receipt"]["promotion_epoch"],
        "disclosed_lineage_reference": vector["promotion_receipt"]["disclosed_lineage_reference"],
        "original_node_cid": vector["promotion_receipt"]["original_node_cid"],
    }
    reordered_payload = copy.deepcopy(vector)
    reordered_payload["promotion_receipt"] = reordered_receipt
    verified = verify_promotion_continuity_record(generate_promotion_continuity_record(reordered_payload))
    assert verified["valid"] is True

    invalid_receipt = copy.deepcopy(vector)
    invalid_receipt["promotion_receipt"].pop("promotion_epoch")
    try:
        generate_promotion_continuity_record(invalid_receipt)
        raise AssertionError("expected_promotion_receipt_field_set_invalid")
    except PromotionContinuityRuntimeError as exc:
        assert exc.token == "promotion_receipt_field_set_invalid"

    invalid_visibility = copy.deepcopy(vector)
    invalid_visibility["public_successor_node"]["visibility"] = "private"
    try:
        generate_promotion_continuity_record(invalid_visibility)
        raise AssertionError("expected_promotion_successor_visibility_invalid")
    except PromotionContinuityRuntimeError as exc:
        assert exc.token == "promotion_successor_visibility_invalid"


def test_original_node_immutability_and_successor_model_are_enforced() -> None:
    vector = canonical_promotion_continuity_vectors()[0]
    original_before = copy.deepcopy(vector["original_private_node"])

    record = generate_promotion_continuity_record(vector)
    authored = record["envelopes"]["authored_payload"]

    assert authored["original_private_node"] == original_before
    assert authored["original_private_node"]["visibility"] == "private"
    assert authored["public_successor_node"]["visibility"] == "public"
    assert authored["original_private_node"]["node_cid"] != authored["public_successor_node"]["node_cid"]


def test_no_automatic_carry_forward_is_enforced() -> None:
    record = generate_promotion_continuity_record(canonical_promotion_continuity_vectors()[0])
    protocol = record["envelopes"]["protocol_interpretation"]
    successor = record["envelopes"]["authored_payload"]["public_successor_node"]

    assert protocol["carry_forward_blocked"] == {
        "validation_state": True,
        "corroboration_reuse_credit": True,
        "reputation": True,
    }
    assert successor["validation_state"] == "proposed"
    assert successor["corroboration_reuse_credit"] == 0
    assert successor["reputation_score"] == 0


def test_canonical_vectors_validate_generator_and_verifier_contract() -> None:
    vectors = canonical_promotion_continuity_vectors()
    assert len(vectors) == 2

    for vector in vectors:
        record = generate_promotion_continuity_record(vector)
        verified = verify_promotion_continuity_record(record)
        checks = verified["checks"]
        assert [item["check_type"] for item in checks] == [
            "runtime_version_supported",
            "cdl_dependency_locked",
            "executable_descriptor_dependency_locked",
            "successor_node_promotion_enforced",
            "in_place_visibility_mutation_forbidden",
            "carry_forward_blocked",
            "record_digest_matches",
        ]
        assert all(item["passed"] is True for item in checks)


def test_runtime_handoff_contains_required_sections_and_tokens() -> None:
    assert HANDOFF_PATH.exists()
    text = HANDOFF_PATH.read_text(encoding="utf-8")
    for token in (
        "## 1. Implementation scope",
        "## 2. Dependency and version locks",
        "## 3. Successor-node and original-node immutability contract",
        "## 4. promotion_receipt schema and field requirements",
        "## 5. Carry-forward prohibition contract",
        "## 6. One-way visibility transition and lineage disclosure rules",
        "## 7. Validation failure token catalog",
        "## 8. Carry-forward constraints for phase 365",
        "## 9. Non-goals",
        "promotion_continuity_runtime_364.v0.1",
        "cdl_038_ratified_353.v0.1",
        "executable_descriptor_runtime_363.v0.1",
        "successor-node plus promotion_receipt without automatic reputation carry-forward",
        "No automatic reputation carry-forward is allowed.",
        "Promotion is a one-way visibility transition.",
    ):
        assert token in text


def test_no_decision_log_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_364_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed_paths


def test_commit_anchored_runtime_mutation_scope_is_limited() -> None:
    commit_ref = _resolve_phase_364_commit_ref()
    _assert_runtime_mutation_scope(commit_ref)
