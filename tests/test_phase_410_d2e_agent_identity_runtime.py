from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ilc_core.identity.agent_id_runtime import (
    AGENT_ID_RUNTIME_VERSION,
    CDL_042_DEPENDENCY,
    NODE_SCHEMA_DEPENDENCY,
    AgentIdentityError,
    derive_agent_id,
    verify_agent_id,
)


RUNTIME_PATH = Path("ilc_core/identity/agent_id_runtime.py")
INIT_PATH = Path("ilc_core/identity/__init__.py")
HANDOFF_PATH = Path("docs/specs/ilc_d2e_agent_id_runtime_handoff_410_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PHASE_410_COMMIT_SUBJECT = "feat(g8): phase 410 d2e agent identity runtime"
AUTHORIZED_RUNTIME_PATHS = {
    "ilc_core/identity/__init__.py",
    "ilc_core/identity/agent_id_runtime.py",
}


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_410_commit_ref() -> str:
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
        if subject.strip().lower() == PHASE_410_COMMIT_SUBJECT.lower():
            matching_commits.append(commit_hash)

    required_paths = {
        "ilc_core/identity/__init__.py",
        "ilc_core/identity/agent_id_runtime.py",
        "tests/test_phase_410_d2e_agent_identity_runtime.py",
        "docs/specs/ilc_d2e_agent_id_runtime_handoff_410_v0.1.md",
    }

    for commit_ref in matching_commits:
        changed = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_410_commit_subject_present_but_no_runtime_commit")
    raise AssertionError("phase_410_commit_not_present_in_local_history")


def _assert_runtime_mutation_scope(commit_ref: str) -> None:
    changed = _changed_paths_for_commit(commit_ref)

    assert DECISION_LOG_PATH not in changed
    assert any(path.startswith("ilc_core/identity/") for path in changed), (
        "phase_410_identity_runtime_mutation_missing"
    )

    non_identity_ilc_core = [
        path
        for path in changed
        if path.startswith("ilc_core/") and not path.startswith("ilc_core/identity/")
    ]
    assert not non_identity_ilc_core, (
        f"phase_410_ilc_core_scope_violation:{non_identity_ilc_core}"
    )

    unexpected_identity_paths = [
        path
        for path in changed
        if path.startswith("ilc_core/identity/") and path not in AUTHORIZED_RUNTIME_PATHS
    ]
    assert not unexpected_identity_paths, (
        f"phase_410_identity_scope_violation:{unexpected_identity_paths}"
    )


def test_runtime_paths_and_version_constant() -> None:
    assert RUNTIME_PATH.exists()
    assert INIT_PATH.exists()
    assert AGENT_ID_RUNTIME_VERSION == "agent_id_runtime_410.v0.1"


def test_cdl_042_dependency_token_correct() -> None:
    assert CDL_042_DEPENDENCY == "cdl_042_ratified_407.v0.1"


def test_node_schema_dependency_chain_imported() -> None:
    assert NODE_SCHEMA_DEPENDENCY == "cdl_038_ratified_353.v0.1"


def test_derive_agent_id_known_vector() -> None:
    # Locks the exact derivation formula: domain-separated SHA-256 with prefix b"ilc-agent-id-v1:".
    # If this assertion fails, the derivation formula has changed — a protocol-breaking identity change.
    expected = "agent-070ec3ad1e9141e73f8fe0d3feec00add72ff332e8a4ffcd67987774763f2a5b"
    assert derive_agent_id(b"canonical-root-key-test-bytes") == expected


def test_derive_agent_id_is_deterministic() -> None:
    first = derive_agent_id(b"canonical-root-key-test-bytes")
    second = derive_agent_id(b"canonical-root-key-test-bytes")
    assert first == second


def test_derive_agent_id_distinct_keys_produce_distinct_ids() -> None:
    assert derive_agent_id(b"key-A") != derive_agent_id(b"key-B")


def test_derive_agent_id_output_format() -> None:
    agent_id = derive_agent_id(b"format-check-key")
    assert agent_id.startswith("agent-")
    assert len(agent_id) == 70
    assert all(char in "0123456789abcdef" for char in agent_id[6:])


def test_derive_agent_id_rejects_non_bytes() -> None:
    with pytest.raises(AgentIdentityError) as exc:
        derive_agent_id("not-bytes")  # type: ignore[arg-type]
    assert exc.value.token == "cdl_042_agent_id_invalid_key_type"


def test_derive_agent_id_rejects_empty_bytes() -> None:
    with pytest.raises(AgentIdentityError) as exc:
        derive_agent_id(b"")
    assert exc.value.token == "cdl_042_agent_id_empty_key"


def test_verify_agent_id_cases() -> None:
    agent_id = derive_agent_id(b"verify-test-key")
    assert verify_agent_id(agent_id, b"verify-test-key") is True
    assert verify_agent_id("agent-wrong-id", b"verify-test-key") is False
    with pytest.raises(AgentIdentityError) as exc:
        verify_agent_id(12345, b"verify-test-key")  # type: ignore[arg-type]
    assert exc.value.token == "cdl_042_agent_id_invalid_id_type"


def test_handoff_artifact_has_required_headings_and_tokens() -> None:
    assert HANDOFF_PATH.exists()
    text = HANDOFF_PATH.read_text(encoding="utf-8")
    for heading in (
        "## 1. Implementation scope summary",
        "## 2. Dependency/version lock section",
        "## 3. CDL-042 agent_id derivation specification",
        "## 4. Deterministic failure-token catalog",
        "## 5. Wallet-agnostic signing boundary carry-forward",
        "## 6. Mutation-scope boundary statement",
        "## 7. Non-goals and carry-forward to Phase 411",
    ):
        assert heading in text

    for token in (
        'AGENT_ID_RUNTIME_VERSION = "agent_id_runtime_410.v0.1"',
        'CDL_042_DEPENDENCY = "cdl_042_ratified_407.v0.1"',
        "CDL-042 agent_id derivation is deterministic from canonical_root_key public bytes with no external registry or coordinator required.",
        "No decision-log mutation occurred in Phase 410.",
        "Wallet-agnostic signing boundary remains mandatory; the agent identity runtime does not handle key custody.",
        "D2e Agent SDK Part 2 (Phase 411) is the authorized next implementation slot.",
    ):
        assert token in text


def test_phase_410_commit_runtime_scope_guard() -> None:
    commit_ref = _resolve_phase_410_commit_ref()
    _assert_runtime_mutation_scope(commit_ref)


def test_phase_410_commit_no_decision_log_mutation() -> None:
    commit_ref = _resolve_phase_410_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed
