"""Phase-381 runtime tests for D2d peering-loop implementation tranche."""

from __future__ import annotations

import asyncio
from pathlib import Path
import subprocess

from ilc_core.network.d2d.interface import D2D_INTERFACE_DEPENDENCY
from ilc_core.network.d2d.peer import (
    D2D_PEERING_DEPENDENCY,
    D2D_PEERING_RUNTIME_VERSION,
    PEER_STATE_BACKOFF,
    PEER_STATE_CONNECTED,
    PEER_STATE_DISCONNECTED,
    D2dPeeringValidationError,
    create_disconnected_state,
    deterministic_reconnect_candidates,
    execute_peering_cycle,
)


DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
HANDOFF_PATH = Path("docs/specs/ilc_d2d_peering_runtime_handoff_381_v0.1.md")
RUNTIME_PEER_PATH = "ilc_core/network/d2d/peer.py"
PHASE_381_COMMIT_SUBJECT = "feat(g8): phase 381 d2d peering loop runtime tranche"

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


def _resolve_phase_381_commit_ref() -> str:
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
        if subject.strip() == PHASE_381_COMMIT_SUBJECT:
            matching.append(commit_hash)

    required_paths = {
        RUNTIME_PEER_PATH,
        "docs/specs/ilc_d2d_peering_runtime_handoff_381_v0.1.md",
        "tests/test_d2d_peering_runtime_381.py",
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching:
        raise AssertionError("phase_381_commit_subject_present_but_no_runtime_commit")
    raise AssertionError("phase_381_commit_not_present_in_local_history")


def _assert_runtime_mutation_scope(commit_ref: str) -> None:
    changed_paths = _changed_paths_for_commit(commit_ref)

    assert DECISION_LOG_PATH not in changed_paths

    runtime_changes = [path for path in changed_paths if path.startswith("ilc_core/")]
    disallowed_runtime_changes = [path for path in runtime_changes if path != RUNTIME_PEER_PATH]
    assert not disallowed_runtime_changes, f"phase_381_runtime_scope_violation:{disallowed_runtime_changes}"

    forbidden_prefix_mutations = [path for path in changed_paths if path.startswith(FORBIDDEN_RUNTIME_PREFIXES)]
    assert not forbidden_prefix_mutations, f"phase_381_forbidden_runtime_mutations:{forbidden_prefix_mutations}"

    forbidden_legacy_mutations = [path for path in changed_paths if path in FORBIDDEN_LEGACY_NETWORK_PATHS]
    assert not forbidden_legacy_mutations, f"phase_381_legacy_network_mutations:{forbidden_legacy_mutations}"

    assert RUNTIME_PEER_PATH in changed_paths, "phase_381_runtime_file_missing_from_commit"


def test_dependency_and_version_constants_locked() -> None:
    assert D2D_PEERING_RUNTIME_VERSION == "d2d_peering_runtime_381.v0.1"
    assert D2D_PEERING_DEPENDENCY == "d2d_peering_381.v0.1"
    assert D2D_INTERFACE_DEPENDENCY == "d2d_interface_380.v0.1"


def test_handshake_success_path_is_deterministic() -> None:
    initial = create_disconnected_state("peer:alpha-01")
    assert initial.state == PEER_STATE_DISCONNECTED

    first = asyncio.run(execute_peering_cycle(initial, handshake_ok=True))
    second = asyncio.run(execute_peering_cycle(initial, handshake_ok=True))

    assert first == second
    assert first.state == PEER_STATE_CONNECTED
    assert first.attempt == 0
    assert first.last_error == ""


def test_handshake_failure_path_moves_to_backoff() -> None:
    initial = create_disconnected_state("peer:beta-02")
    failed = asyncio.run(
        execute_peering_cycle(
            initial,
            handshake_ok=False,
            failure_reason="handshake_rejected",
        )
    )

    assert failed.state == PEER_STATE_BACKOFF
    assert failed.attempt == 1
    assert failed.last_error == "handshake_rejected"

    try:
        asyncio.run(execute_peering_cycle(initial, handshake_ok=False, failure_reason=""))
        raise AssertionError("expected_missing_reason_validation")
    except D2dPeeringValidationError as exc:
        assert exc.token == "d2d_peering_handshake_reason_missing"


def test_reconnect_candidates_are_seed_deterministic() -> None:
    peers = [
        "peer:delta-04",
        "peer:alpha-01",
        "peer:gamma-03",
        "peer:beta-02",
        "peer:alpha-01",
    ]

    one = deterministic_reconnect_candidates(peers, seed=381, limit=3)
    two = deterministic_reconnect_candidates(peers, seed=381, limit=3)
    three = deterministic_reconnect_candidates(peers, seed=999, limit=3)

    assert one == two
    assert one != three
    assert len(one) == 3


def test_handoff_artifact_contract_and_source_no_network_patterns() -> None:
    assert HANDOFF_PATH.exists()
    handoff_text = HANDOFF_PATH.read_text(encoding="utf-8")
    for token in (
        "## 1. Implementation scope summary",
        "## 2. Dependency/version lock section",
        "## 3. Peering state model summary",
        "## 4. Deterministic handshake/reconnect strategy",
        "## 5. Asyncio boundary statement",
        "## 6. Deterministic validation-failure token catalog",
        "## 7. Mutation-scope boundary statement",
        "## 8. Carry-forward constraints for Phase 382",
        "## 9. Non-goals",
        'D2D_PEERING_DEPENDENCY = "d2d_peering_381.v0.1"',
        "Phase 381 introduces asyncio-compatible peering orchestration with deterministic mock-loop testing only.",
        "No real socket, DNS, or wall-clock timeout behavior is implemented in Phase 381.",
        "Phase 382 consumes this artifact for gossip state machine and CDL-039 invariant enforcement runtime.",
    ):
        assert token in handoff_text

    source = Path(RUNTIME_PEER_PATH).read_text(encoding="utf-8")
    for forbidden in (
        "socket.",
        "open_connection(",
        "getaddrinfo(",
        "time.sleep(",
    ):
        assert forbidden not in source


def test_phase_381_commit_touched_no_decision_log_mutation() -> None:
    commit_ref = _resolve_phase_381_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed_paths


def test_phase_381_commit_runtime_mutation_scope_is_limited() -> None:
    commit_ref = _resolve_phase_381_commit_ref()
    _assert_runtime_mutation_scope(commit_ref)
