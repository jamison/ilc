"""Phase-323 runtime tests for wire transport implementation tranche."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from ilc_core.network import (
    EPOCH_SNAPSHOT_DEPENDENCY,
    GENESIS_BUNDLE_DEPENDENCY,
    SCHEMA_BASELINE_DEPENDENCY,
    WIRE_TRANSPORT_RUNTIME_VERSION,
    WireTransportValidationError,
    canonical_wire_transport_vectors,
    generate_wire_transport_envelope,
    verify_wire_transport_envelope,
)


DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
HANDOFF_PATH = Path("docs/specs/ilc_wire_transport_runtime_handoff_323_v0.1.md")
PHASE_323_COMMIT_SUBJECT = "feat(g8): phase 323 wire transport initial implementation tranche"
NETWORK_RUNTIME_PATH = "ilc_core/network/wire_transport_runtime.py"
NETWORK_INIT_PATH = "ilc_core/network/__init__.py"


FORBIDDEN_RUNTIME_PREFIXES = (
    "ilc_core/consensus/",
    "ilc_core/security/",
    "ilc_core/ledger/",
    "ilc_core/issuance/",
    "ilc_core/schema/",
    "ilc_core/genesis/",
    "ilc_core/epoch/",
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


def _resolve_phase_323_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matching_commits: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_323_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if NETWORK_RUNTIME_PATH in changed_paths:
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_323_commit_subject_present_but_no_runtime_commit")
    raise AssertionError("phase_323_commit_not_present_in_local_history")


def _assert_runtime_mutation_scope(commit_ref: str) -> None:
    changed_paths = _changed_paths_for_commit(commit_ref)

    assert DECISION_LOG_PATH not in changed_paths

    runtime_changes = [path for path in changed_paths if path.startswith("ilc_core/")]
    disallowed_runtime_changes = [
        path
        for path in runtime_changes
        if path not in {NETWORK_RUNTIME_PATH, NETWORK_INIT_PATH}
    ]
    assert not disallowed_runtime_changes, f"phase_323_runtime_scope_violation:{disallowed_runtime_changes}"

    forbidden_mutations = [path for path in changed_paths if path.startswith(FORBIDDEN_RUNTIME_PREFIXES)]
    assert not forbidden_mutations, f"phase_323_forbidden_runtime_mutations:{forbidden_mutations}"

    assert NETWORK_RUNTIME_PATH in changed_paths, "phase_323_runtime_file_missing_from_commit"


def test_runtime_surface_is_invocable() -> None:
    vector = canonical_wire_transport_vectors()[0]
    envelope = generate_wire_transport_envelope(vector)
    verified = verify_wire_transport_envelope(envelope)

    assert envelope["runtime_version"] == WIRE_TRANSPORT_RUNTIME_VERSION
    assert envelope["schema_dependency"] == SCHEMA_BASELINE_DEPENDENCY
    assert envelope["genesis_dependency"] == GENESIS_BUNDLE_DEPENDENCY
    assert envelope["epoch_dependency"] == EPOCH_SNAPSHOT_DEPENDENCY
    assert isinstance(envelope["envelope_sha256"], str)

    assert verified["valid"] is True
    assert verified["runtime_version"] == WIRE_TRANSPORT_RUNTIME_VERSION


def test_runtime_constants_lock_exact_dependency_and_version_tokens() -> None:
    assert WIRE_TRANSPORT_RUNTIME_VERSION == "wire_transport_runtime_323.v0.1"
    assert SCHEMA_BASELINE_DEPENDENCY == "d2_schema_baseline_310.v0.1"
    assert GENESIS_BUNDLE_DEPENDENCY == "genesis_state_bundle_312.v0.1"
    assert EPOCH_SNAPSHOT_DEPENDENCY == "epoch_snapshot_runtime_314.v0.1"


def test_deterministic_output_for_repeated_identical_input_vectors() -> None:
    vector = canonical_wire_transport_vectors()[0]
    one = generate_wire_transport_envelope(vector)
    two = generate_wire_transport_envelope(vector)

    assert one == two
    assert verify_wire_transport_envelope(one) == verify_wire_transport_envelope(two)


def test_canonical_wire_transport_digest_rejects_non_finite_payload_values() -> None:
    vector = canonical_wire_transport_vectors()[0]
    vector["envelope"]["payload"]["non_finite"] = float("nan")

    try:
        generate_wire_transport_envelope(vector)
        raise AssertionError("expected_wire_transport_non_finite_rejection")
    except ValueError as exc:
        assert "Out of range float values" in str(exc)


def test_invalid_header_or_payload_inputs_fail_with_deterministic_tokens() -> None:
    invalid_headers = {
        "envelope": {
            "message_id": "msg-invalid-1",
            "schema_ref": "d2.claim.v1",
            "content_type": "application/json",
            "headers": ["not-a-dict"],
            "payload": {"claim_id": "claim-a"},
        },
        "transport": {
            "kind": "quic",
            "delivery_mode": "request_response",
            "qos": "at_least_once",
            "retry_policy": {"max_retries": 1, "backoff_ms": 100},
        },
    }

    try:
        generate_wire_transport_envelope(invalid_headers)
        raise AssertionError("expected_wire_transport_header_validation_error")
    except WireTransportValidationError as exc:
        assert exc.token == "wire_transport_headers_not_object"

    invalid_payload = {
        "envelope": {
            "message_id": "msg-invalid-2",
            "schema_ref": "d2.claim.v1",
            "content_type": "application/json",
            "headers": {"source": "agent-a"},
            "payload": "not-object",
        },
        "transport": {
            "kind": "quic",
            "delivery_mode": "request_response",
            "qos": "at_least_once",
            "retry_policy": {"max_retries": 1, "backoff_ms": 100},
        },
    }

    try:
        generate_wire_transport_envelope(invalid_payload)
        raise AssertionError("expected_wire_transport_payload_validation_error")
    except WireTransportValidationError as exc:
        assert exc.token == "wire_transport_payload_not_object"


def test_invalid_transport_policy_inputs_fail_with_deterministic_tokens() -> None:
    vector = canonical_wire_transport_vectors()[0]

    invalid_kind = {
        "envelope": vector["envelope"],
        "transport": {
            "kind": "tcp",
            "delivery_mode": "request_response",
            "qos": "at_least_once",
            "retry_policy": {"max_retries": 1, "backoff_ms": 100},
        },
    }

    try:
        generate_wire_transport_envelope(invalid_kind)
        raise AssertionError("expected_wire_transport_kind_validation_error")
    except WireTransportValidationError as exc:
        assert exc.token == "wire_transport_kind_invalid"

    invalid_retry = {
        "envelope": vector["envelope"],
        "transport": {
            "kind": "quic",
            "delivery_mode": "request_response",
            "qos": "at_least_once",
            "retry_policy": {"max_retries": -1, "backoff_ms": 100},
        },
    }

    try:
        generate_wire_transport_envelope(invalid_retry)
        raise AssertionError("expected_wire_transport_retry_validation_error")
    except WireTransportValidationError as exc:
        assert exc.token == "wire_transport_retry_max_invalid"


def test_canonical_vectors_validate_generator_and_verifier_surface() -> None:
    vectors = canonical_wire_transport_vectors()
    assert len(vectors) == 2

    for vector in vectors:
        envelope = generate_wire_transport_envelope(vector)
        verified = verify_wire_transport_envelope(envelope)
        assert verified["valid"] is True
        checks = verified["checks"]
        assert [item["check_type"] for item in checks] == [
            "runtime_version_supported",
            "schema_dependency_locked",
            "genesis_dependency_locked",
            "epoch_dependency_locked",
            "transport_envelope_digest_matches",
        ]
        assert all(item["passed"] is True for item in checks)


def test_runtime_handoff_records_compatibility_notes_for_310_312_314() -> None:
    assert HANDOFF_PATH.exists()
    text = HANDOFF_PATH.read_text(encoding="utf-8")
    for token in (
        "## 6. Compatibility notes for prior runtime lanes",
        "d2_schema_baseline_310.v0.1",
        "genesis_state_bundle_312.v0.1",
        "epoch_snapshot_runtime_314.v0.1",
    ):
        assert token in text


def test_no_decision_log_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_323_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed_paths


def test_commit_anchored_runtime_mutation_scope_is_limited() -> None:
    commit_ref = _resolve_phase_323_commit_ref()
    _assert_runtime_mutation_scope(commit_ref)
