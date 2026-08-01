"""Phase-382 runtime tests for D2d gossip runtime implementation tranche."""

from __future__ import annotations

import asyncio
from pathlib import Path
import subprocess

from ilc_core.network.d2d.gossip import (
    D2D_GOSSIP_DEPENDENCY,
    D2D_GOSSIP_RUNTIME_VERSION,
    D2dGossipValidationError,
    MAX_OBSERVER_METADATA_TRACE_PEERS,
    analyze_passive_observer_membership_leakage,
    build_observer_metadata_trace,
    build_transport_envelope,
    deterministic_gossip_candidates,
    execute_gossip_round,
)
from ilc_core.network.d2d.peer import D2D_PEERING_DEPENDENCY


DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
HANDOFF_PATH = Path("docs/specs/ilc_d2d_gossip_runtime_handoff_382_v0.1.md")
RUNTIME_GOSSIP_PATH = "ilc_core/network/d2d/gossip.py"
PHASE_382_COMMIT_SUBJECT = (
    "feat(g8): phase 382 d2d gossip state machine and cdl-039 invariant enforcement runtime tranche"
)

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


def _resolve_phase_382_commit_ref() -> str:
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
        if subject.strip() == PHASE_382_COMMIT_SUBJECT:
            matching.append(commit_hash)

    required_paths = {
        RUNTIME_GOSSIP_PATH,
        "docs/specs/ilc_d2d_gossip_runtime_handoff_382_v0.1.md",
        "tests/test_d2d_gossip_runtime_382.py",
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching:
        raise AssertionError("phase_382_commit_subject_present_but_no_runtime_commit")
    raise AssertionError("phase_382_commit_not_present_in_local_history")


def _assert_runtime_mutation_scope(commit_ref: str) -> None:
    changed_paths = _changed_paths_for_commit(commit_ref)

    assert DECISION_LOG_PATH not in changed_paths

    runtime_changes = [path for path in changed_paths if path.startswith("ilc_core/")]
    disallowed_runtime_changes = [path for path in runtime_changes if path != RUNTIME_GOSSIP_PATH]
    assert not disallowed_runtime_changes, f"phase_382_runtime_scope_violation:{disallowed_runtime_changes}"

    forbidden_prefix_mutations = [path for path in changed_paths if path.startswith(FORBIDDEN_RUNTIME_PREFIXES)]
    assert not forbidden_prefix_mutations, f"phase_382_forbidden_runtime_mutations:{forbidden_prefix_mutations}"

    forbidden_legacy_mutations = [path for path in changed_paths if path in FORBIDDEN_LEGACY_NETWORK_PATHS]
    assert not forbidden_legacy_mutations, f"phase_382_legacy_network_mutations:{forbidden_legacy_mutations}"

    assert RUNTIME_GOSSIP_PATH in changed_paths, "phase_382_runtime_file_missing_from_commit"


def test_dependency_and_version_constants_locked_and_source_contracts() -> None:
    assert D2D_GOSSIP_RUNTIME_VERSION == "d2d_gossip_runtime_382.v0.1"
    assert D2D_GOSSIP_DEPENDENCY == "d2d_gossip_382.v0.1"
    assert D2D_PEERING_DEPENDENCY == "d2d_peering_381.v0.1"

    source = Path(RUNTIME_GOSSIP_PATH).read_text(encoding="utf-8")
    required_docstring_token = (
        "This module enforces CDL-039 transport invariants: no creator_agent_id in transport headers, "
        "opaque channel routing field, and cluster membership non-inferrability."
    )
    assert required_docstring_token in source
    for forbidden in (
        "socket.",
        "open_connection(",
        "getaddrinfo(",
        "time.sleep(",
    ):
        assert forbidden not in source


def test_gossip_candidate_selection_determinism() -> None:
    peers = ["peer:delta-04", "peer:alpha-01", "peer:gamma-03", "peer:beta-02", "peer:alpha-01"]

    one = deterministic_gossip_candidates(peers, seed=382, limit=3)
    two = deterministic_gossip_candidates(peers, seed=382, limit=3)
    three = deterministic_gossip_candidates(peers, seed=383, limit=3)

    assert one == two
    assert one != three
    assert len(one) == 3


def test_observer_metadata_trace_peer_count_is_bounded() -> None:
    peers = [
        f"peer:bounded-{index:04d}"
        for index in range(MAX_OBSERVER_METADATA_TRACE_PEERS + 1)
    ]
    try:
        build_observer_metadata_trace(
            peers,
            channel_id="cid:1234abcd5678ef901234abcd5678ef90",
            epoch_slot=1,
        )
        raise AssertionError("expected_observer_trace_limit_rejection")
    except D2dGossipValidationError as exc:
        assert exc.token == "d2d_observer_trace_peer_limit_exceeded"


def test_invariant_creator_agent_id_absent_from_transport_structures() -> None:
    envelope = build_transport_envelope(
        message_id="msg-382-001",
        payload_cid="bafybeigdyrzt6ncp4m2xg7r5z2xw7sbn3r7r2j7vph6a2m5wqk35m4w5ay",
        channel_id="cid:1234abcd5678ef901234abcd5678ef90",
        sender_peer_id="peer:alpha-01",
        transport_headers={"schema_ref": "d2d.message.v1", "topic": "node.header"},
    )
    assert "creator_agent_id" not in envelope["transport_headers"]

    forbidden_key_variants = (
        "creator_agent_id",
        "Creator_Agent_Id",
        "creator-agent-id",
        "CREATOR.AGENT.ID",
    )
    for key_variant in forbidden_key_variants:
        try:
            build_transport_envelope(
                message_id="msg-382-002",
                payload_cid="bafybeibohv7i2fylx5vzo3h5smzqj2pvyew53kkr7bt7sn4l3vhh2n7zeu",
                channel_id="cid:9f7a8c42bb11ddee99aa22cc33ff44aa",
                sender_peer_id="peer:beta-02",
                transport_headers={key_variant: "cid:bad", "topic": "node.fetch"},
            )
            raise AssertionError("expected_creator_agent_id_rejection")
        except D2dGossipValidationError as exc:
            assert exc.token == "d2d_creator_agent_id_forbidden"

    try:
        build_transport_envelope(
            message_id="msg-382-002b",
            payload_cid="bafybeibohv7i2fylx5vzo3h5smzqj2pvyew53kkr7bt7sn4l3vhh2n7zeu",
            channel_id="cid:9f7a8c42bb11ddee99aa22cc33ff44aa",
            sender_peer_id="peer:beta-02",
            transport_headers={"Topic": "node.fetch", "topic": "node.header"},
        )
        raise AssertionError("expected_header_collision_rejection")
    except D2dGossipValidationError as exc:
        assert exc.token == "d2d_transport_header_key_collision"


def test_invariant_channel_field_is_opaque_identifier() -> None:
    envelope = build_transport_envelope(
        message_id="msg-382-003",
        payload_cid="bafybeif6rk7wf4klkznx7bwupexyxpr4r7w6m6q7fo4jrp2mxy7ul4jz7m",
        channel_id="rand:abcdef0123456789abcdef0123456789",
        sender_peer_id="peer:gamma-03",
        transport_headers={"schema_ref": "d2d.message.v1", "topic": "node.header"},
    )
    assert envelope["channel_id"].startswith("rand:")

    try:
        build_transport_envelope(
            message_id="msg-382-004",
            payload_cid="bafybeif6rk7wf4klkznx7bwupexyxpr4r7w6m6q7fo4jrp2mxy7ul4jz7m",
            channel_id="PublicChannel",
            sender_peer_id="peer:delta-04",
            transport_headers={"schema_ref": "d2d.message.v1", "topic": "node.fetch"},
        )
        raise AssertionError("expected_opaque_channel_rejection")
    except D2dGossipValidationError as exc:
        assert exc.token == "d2d_channel_not_opaque"


def test_invariant_membership_non_inferrability_and_handoff_contract() -> None:
    selected = deterministic_gossip_candidates(
        ["peer:alpha-01", "peer:beta-02", "peer:gamma-03"],
        seed=382,
        limit=2,
    )
    trace = build_observer_metadata_trace(
        selected,
        channel_id="cid:1234abcd5678ef901234abcd5678ef90",
        epoch_slot=12,
    )
    analysis = analyze_passive_observer_membership_leakage(trace)
    assert analysis["membership_leak_detected"] is False

    round_result = asyncio.run(
        execute_gossip_round(
            ["peer:alpha-01", "peer:beta-02", "peer:gamma-03"],
            seed=382,
            channel_id="cid:1234abcd5678ef901234abcd5678ef90",
            epoch_slot=12,
            limit=2,
        )
    )
    assert round_result["analysis"]["membership_leak_detected"] is False

    leaked = [dict(trace[0]), {"cluster_id": "cluster-a", "relay_peer_id": "peer:beta-02", "channel_tag": "tag", "epoch_slot": 12}]
    try:
        analyze_passive_observer_membership_leakage(leaked)
        raise AssertionError("expected_membership_leak_rejection")
    except D2dGossipValidationError as exc:
        assert exc.token == "d2d_cluster_membership_leak_detected"

    assert HANDOFF_PATH.exists()
    handoff_text = HANDOFF_PATH.read_text(encoding="utf-8")
    for token in (
        "## 1. Implementation scope summary",
        "## 2. Dependency/version lock section",
        "## 3. Gossip state-machine summary",
        "## 4. CDL-039 invariant enforcement summary",
        "## 5. Deterministic passive-observer leak analysis summary",
        "## 6. Asyncio boundary statement",
        "## 7. Deterministic validation-failure token catalog",
        "## 8. Mutation-scope boundary statement",
        "## 9. Carry-forward constraints for Phase 383",
        "## 10. Non-goals",
        'D2D_GOSSIP_DEPENDENCY = "d2d_gossip_382.v0.1"',
        "This module enforces CDL-039 transport invariants: no creator_agent_id in transport headers, opaque channel routing field, and cluster membership non-inferrability.",
        "No real socket, DNS, or wall-clock timeout behavior is implemented in Phase 382.",
        "Phase 383 consumes this artifact as an implementation anchor for CDL-040 prelock drafting context.",
    ):
        assert token in handoff_text


def test_phase_382_commit_touched_no_decision_log_mutation() -> None:
    commit_ref = _resolve_phase_382_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed_paths


def test_phase_382_commit_runtime_mutation_scope_is_limited() -> None:
    commit_ref = _resolve_phase_382_commit_ref()
    _assert_runtime_mutation_scope(commit_ref)
