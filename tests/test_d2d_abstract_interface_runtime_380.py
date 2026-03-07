"""Phase-380 runtime tests for D2d abstract interface implementation tranche."""

from __future__ import annotations

import inspect
from pathlib import Path
import subprocess

from ilc_core.network.d2d import (
    D2D_INTERFACE_DEPENDENCY,
    D2D_INTERFACE_RUNTIME_VERSION,
    WIRE_TRANSPORT_DEPENDENCY,
    D2dInterfaceValidationError,
    D2dMessage,
    D2dPeer,
    D2dTopology,
    canonical_d2d_interface_vectors,
    validate_d2d_channel,
    validate_d2d_message_envelope,
    validate_d2d_peer_id,
)


DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
HANDOFF_PATH = Path("docs/specs/ilc_d2d_abstract_interface_runtime_handoff_380_v0.1.md")
RUNTIME_INIT_PATH = "ilc_core/network/d2d/__init__.py"
RUNTIME_INTERFACE_PATH = "ilc_core/network/d2d/interface.py"
PHASE_380_COMMIT_SUBJECT = "feat(g8): phase 380 d2d abstract interface and dependency token runtime tranche"

FORBIDDEN_RUNTIME_PREFIXES = (
    "ilc_core/consensus/",
    "ilc_core/security/",
    "ilc_core/ledger/",
    "ilc_core/issuance/",
    "ilc_core/schema/",
    "ilc_core/genesis/",
    "ilc_core/epoch/",
    "ilc_core/node/",
    "ilc_core/reputation/",
)

FORBIDDEN_LEGACY_NETWORK_PATHS = {
    "ilc_core/network/wire_transport_runtime.py",
    "ilc_core/network/peer.py",
    "ilc_core/network/gossip.py",
    "ilc_core/network/topology.py",
}


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_380_commit_ref() -> str:
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
        if subject.strip() == PHASE_380_COMMIT_SUBJECT:
            matching.append(commit_hash)

    required_paths = {
        RUNTIME_INIT_PATH,
        RUNTIME_INTERFACE_PATH,
        "docs/specs/ilc_d2d_abstract_interface_runtime_handoff_380_v0.1.md",
        "tests/test_d2d_abstract_interface_runtime_380.py",
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching:
        raise AssertionError("phase_380_commit_subject_present_but_no_runtime_commit")
    raise AssertionError("phase_380_commit_not_present_in_local_history")


def _assert_runtime_mutation_scope(commit_ref: str) -> None:
    changed_paths = _changed_paths_for_commit(commit_ref)

    assert DECISION_LOG_PATH not in changed_paths

    runtime_changes = [path for path in changed_paths if path.startswith("ilc_core/")]
    allowed_runtime_changes = {RUNTIME_INIT_PATH, RUNTIME_INTERFACE_PATH}
    disallowed_runtime_changes = [path for path in runtime_changes if path not in allowed_runtime_changes]
    assert not disallowed_runtime_changes, f"phase_380_runtime_scope_violation:{disallowed_runtime_changes}"

    forbidden_prefix_mutations = [path for path in changed_paths if path.startswith(FORBIDDEN_RUNTIME_PREFIXES)]
    assert not forbidden_prefix_mutations, f"phase_380_forbidden_runtime_mutations:{forbidden_prefix_mutations}"

    forbidden_legacy_mutations = [path for path in changed_paths if path in FORBIDDEN_LEGACY_NETWORK_PATHS]
    assert not forbidden_legacy_mutations, f"phase_380_legacy_network_mutations:{forbidden_legacy_mutations}"

    assert RUNTIME_INTERFACE_PATH in changed_paths, "phase_380_runtime_file_missing_from_commit"


def test_runtime_surface_is_invocable_and_deterministic() -> None:
    vectors = canonical_d2d_interface_vectors()
    assert len(vectors) >= 2

    one = validate_d2d_message_envelope(vectors[0])
    two = validate_d2d_message_envelope(vectors[0])
    assert one == two

    peer_id = validate_d2d_peer_id(vectors[0]["sender_peer_id"])
    assert peer_id == vectors[0]["sender_peer_id"]

    try:
        validate_d2d_message_envelope(
            {
                "message_id": "msg-creator-variant",
                "payload_cid": vectors[0]["payload_cid"],
                "channel_id": vectors[0]["channel_id"],
                "sender_peer_id": vectors[0]["sender_peer_id"],
                "transport_headers": {"Creator_Agent_Id": "cid:not-allowed", "topic": "node.fetch"},
            }
        )
        raise AssertionError("expected_creator_agent_id_rejection")
    except D2dInterfaceValidationError as exc:
        assert exc.token == "d2d_creator_agent_id_forbidden"

    try:
        validate_d2d_message_envelope(
            {
                "message_id": "msg-header-collision",
                "payload_cid": vectors[0]["payload_cid"],
                "channel_id": vectors[0]["channel_id"],
                "sender_peer_id": vectors[0]["sender_peer_id"],
                "transport_headers": {"Topic": "node.fetch", "topic": "node.header"},
            }
        )
        raise AssertionError("expected_transport_header_collision_rejection")
    except D2dInterfaceValidationError as exc:
        assert exc.token == "d2d_transport_header_key_collision"


def test_runtime_constants_lock_exact_dependency_and_version_tokens() -> None:
    assert D2D_INTERFACE_RUNTIME_VERSION == "d2d_interface_runtime_380.v0.1"
    assert D2D_INTERFACE_DEPENDENCY == "d2d_interface_380.v0.1"
    assert WIRE_TRANSPORT_DEPENDENCY == "wire_transport_runtime_323.v0.1"


def test_interface_contract_shapes_exist() -> None:
    envelope = validate_d2d_message_envelope(canonical_d2d_interface_vectors()[0])
    message = D2dMessage(**envelope)
    assert message.message_id.startswith("msg-")
    assert isinstance(message.channel_id, str)

    # Protocols are runtime-checkable shape declarations for downstream phases.
    assert hasattr(D2dPeer, "__dict__")
    assert hasattr(D2dTopology, "__dict__")


def test_channel_opacity_validator_rejects_human_labels() -> None:
    try:
        validate_d2d_channel("PublicChannel")
        raise AssertionError("expected_non_opaque_channel_rejection")
    except D2dInterfaceValidationError as exc:
        assert exc.token == "d2d_channel_not_opaque"

    accepted = validate_d2d_channel("cid:11223344556677889900aabbccddeeff")
    assert accepted == "cid:11223344556677889900aabbccddeeff"


def test_handoff_artifact_contract_and_source_no_asyncio_no_io_patterns() -> None:
    assert HANDOFF_PATH.exists()
    handoff_text = HANDOFF_PATH.read_text(encoding="utf-8")
    for token in (
        "## 1. Implementation scope summary",
        "## 2. Dependency and version lock section",
        "## 3. D2d abstract interface surface summary",
        "## 4. No-asyncio/no-I-O boundary statement",
        "## 5. Deterministic validation-failure token catalog",
        "## 6. Mutation-scope boundary statement",
        "## 7. Carry-forward constraints for Phase 381",
        "## 8. Non-goals",
        'D2D_INTERFACE_DEPENDENCY = "d2d_interface_380.v0.1"',
        "Phase 380 is abstract-interface only; no asyncio, no peering loop, no gossip loop.",
        "No runtime implementation of CDL-039 invariants occurs in Phase 380.",
        "Phase 381 consumes this artifact for peering-loop implementation.",
    ):
        assert token in handoff_text

    source = Path(RUNTIME_INTERFACE_PATH).read_text(encoding="utf-8")
    for forbidden in (
        "import asyncio",
        "socket.",
        "open_connection(",
        "time.sleep(",
        "dns",
    ):
        assert forbidden not in source


def test_phase_380_commit_touched_no_decision_log_mutation() -> None:
    commit_ref = _resolve_phase_380_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed_paths


def test_phase_380_commit_runtime_mutation_scope_is_limited() -> None:
    commit_ref = _resolve_phase_380_commit_ref()
    _assert_runtime_mutation_scope(commit_ref)
