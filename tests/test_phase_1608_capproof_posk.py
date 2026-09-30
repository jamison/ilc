from dataclasses import replace
from decimal import Decimal

import pytest

from ilc_core.capproof.graph_probe_posk import (
    POSK_MAX_TRAVERSAL_NODES,
    POSK_MAX_REPLAY_LEDGER_ENTRIES,
    PoSKError,
    PoSKInput,
    PoSKProof,
    PoSKReplayLedger,
    build_posk_proof,
    derive_posk_challenge,
    record_posk_replay_or_raise,
    verify_posk_proof,
)
from ilc_core.capproof.probe_runner import GraphProbe, run_graph_probe_with_posk

_SALT = "1" * 64
_OTHER_SALT = "2" * 64
_ROOT = "a" * 64
_OTHER_ROOT = "b" * 64
_NODES = (
    "bafybeiaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "bafybeibbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    "bafybeicccccccccccccccccccccccccccccccccccccccccccccccc",
)
_EDGES = ((_NODES[0], _NODES[1]), (_NODES[1], _NODES[2]))


def _inp(
    *,
    salt: str = _SALT,
    epoch: int = 7,
    root: str = _ROOT,
    nodes: tuple[str, ...] = _NODES,
    edges: tuple[tuple[str, str], ...] = _EDGES,
) -> PoSKInput:
    return PoSKInput(
        graph_root_hash=root,
        epoch_salt=salt,
        epoch=epoch,
        visited_node_ids=nodes,
        traversal_edges=edges,
    )


def _assert_token(excinfo: pytest.ExceptionInfo[BaseException], token: str) -> None:
    assert getattr(excinfo.value, "token", None) == token
    assert token in str(excinfo.value)


def test_basic_commitment_is_64_lower_hex() -> None:
    proof = build_posk_proof(_inp())

    assert len(proof.proof_commitment) == 64
    assert proof.proof_commitment == proof.proof_commitment.lower()
    int(proof.proof_commitment, 16)
    assert proof.node_count == 3
    assert proof.edge_count == 2


def test_same_input_produces_same_commitment() -> None:
    first = build_posk_proof(_inp())
    second = build_posk_proof(_inp())

    assert first.proof_commitment == second.proof_commitment
    assert first.challenge.challenge_id == second.challenge.challenge_id


def test_different_epoch_salt_changes_challenge_and_commitment() -> None:
    first = build_posk_proof(_inp())
    second = build_posk_proof(_inp(salt=_OTHER_SALT))

    assert first.challenge.challenge_id != second.challenge.challenge_id
    assert first.proof_commitment != second.proof_commitment


def test_different_epoch_changes_commitment() -> None:
    first = build_posk_proof(_inp(epoch=7))
    second = build_posk_proof(_inp(epoch=8))

    assert first.proof_commitment != second.proof_commitment


def test_empty_visited_nodes_rejected() -> None:
    with pytest.raises(PoSKError) as excinfo:
        _inp(nodes=())

    _assert_token(excinfo, "posk_visited_node_ids_must_be_non_empty")


def test_too_many_nodes_rejected_before_sorting() -> None:
    nodes = tuple(f"{i:064x}" for i in range(POSK_MAX_TRAVERSAL_NODES + 1))

    with pytest.raises(PoSKError) as excinfo:
        _inp(nodes=nodes, edges=())

    _assert_token(excinfo, "posk_traversal_exceeds_max_node_count")


def test_duplicate_nodes_rejected_as_noncanonical() -> None:
    with pytest.raises(PoSKError) as excinfo:
        _inp(nodes=(_NODES[0], _NODES[0]), edges=())

    _assert_token(excinfo, "posk_visited_node_ids_must_be_canonical_unique_sorted")


def test_unsorted_nodes_rejected_as_noncanonical() -> None:
    with pytest.raises(PoSKError) as excinfo:
        _inp(nodes=(_NODES[1], _NODES[0]), edges=())

    _assert_token(excinfo, "posk_visited_node_ids_must_be_canonical_unique_sorted")


def test_fabricated_wrong_node_set_changes_commitment() -> None:
    honest = build_posk_proof(_inp())
    fabricated = build_posk_proof(_inp(nodes=_NODES[:2], edges=(_EDGES[0],)))

    assert honest.proof_commitment != fabricated.proof_commitment


def test_graph_probe_with_posk_populates_commitment_and_metric() -> None:
    result, ledger = run_graph_probe_with_posk(
        _SALT,
        graph_root_hash=_ROOT,
        epoch=7,
        visited_node_ids=_NODES,
        traversal_edges=_EDGES,
    )

    assert result.graph_mteps > Decimal("0")
    assert result.posk_commitment is not None
    assert len(result.posk_commitment) == 64
    assert isinstance(ledger, PoSKReplayLedger)
    assert len(ledger.entries) == 1


def test_graph_probe_without_posk_keeps_backward_compatible_none() -> None:
    result = GraphProbe().run(_SALT)

    assert result.posk_commitment is None


def test_spectral_activation_rejected_in_phase_1608() -> None:
    proof = build_posk_proof(_inp())

    with pytest.raises(PoSKError) as excinfo:
        PoSKProof(
            challenge=proof.challenge,
            visited_node_ids=proof.visited_node_ids,
            traversal_edges=proof.traversal_edges,
            proof_commitment=proof.proof_commitment,
            node_count=proof.node_count,
            edge_count=proof.edge_count,
            spectral_activated=True,
        )

    _assert_token(excinfo, "posk_spectral_not_activated_in_phase_1608")


def test_non_string_node_id_rejected() -> None:
    with pytest.raises(PoSKError) as excinfo:
        PoSKInput(
            graph_root_hash=_ROOT,
            epoch_salt=_SALT,
            epoch=7,
            visited_node_ids=(42,),  # type: ignore[tuple-item]
        )

    _assert_token(excinfo, "posk_node_id_must_be_content_addressed_string")


def test_replay_ledger_rejects_duplicate_epoch_commitment() -> None:
    proof = build_posk_proof(_inp())
    ledger = record_posk_replay_or_raise(None, proof)

    with pytest.raises(PoSKError) as excinfo:
        record_posk_replay_or_raise(ledger, proof)

    _assert_token(excinfo, "posk_replay_detected_phase_1608")


def test_replay_ledger_accepts_final_slot_then_rejects_full_ledger() -> None:
    proof = build_posk_proof(_inp())
    entries = tuple((7, f"{index:064x}") for index in range(POSK_MAX_REPLAY_LEDGER_ENTRIES - 1))
    ledger = PoSKReplayLedger(entries=entries)

    full = record_posk_replay_or_raise(ledger, proof)
    assert len(full.entries) == POSK_MAX_REPLAY_LEDGER_ENTRIES

    next_proof = build_posk_proof(_inp(salt=_OTHER_SALT))
    with pytest.raises(PoSKError) as excinfo:
        record_posk_replay_or_raise(full, next_proof)

    _assert_token(excinfo, "posk_replay_ledger_exceeds_max_entries")


def test_graph_root_hash_changes_challenge_and_commitment() -> None:
    first = build_posk_proof(_inp(root=_ROOT))
    second = build_posk_proof(_inp(root=_OTHER_ROOT))

    assert first.challenge.challenge_id != second.challenge.challenge_id
    assert first.proof_commitment != second.proof_commitment


def test_verifier_rejects_tampered_commitment() -> None:
    proof = build_posk_proof(_inp())

    with pytest.raises(PoSKError) as excinfo:
        replace(proof, proof_commitment="0" * 64)

    _assert_token(excinfo, "posk_commitment_mismatch")


def test_posk_proof_constructor_self_verifies_commitment() -> None:
    proof = build_posk_proof(_inp())

    with pytest.raises(PoSKError) as excinfo:
        PoSKProof(
            challenge=proof.challenge,
            visited_node_ids=proof.visited_node_ids,
            traversal_edges=proof.traversal_edges,
            proof_commitment="f" * 64,
            node_count=proof.node_count,
            edge_count=proof.edge_count,
        )

    _assert_token(excinfo, "posk_commitment_mismatch")


def test_challenge_id_must_match_inputs() -> None:
    with pytest.raises(PoSKError) as excinfo:
        derive_posk_challenge(_ROOT, _SALT, True)  # type: ignore[arg-type]

    _assert_token(excinfo, "posk_epoch_must_be_non_negative_int")


def test_edges_must_reference_visited_nodes() -> None:
    outsider = "bafybeidddddddddddddddddddddddddddddddddddddddddddddddd"

    with pytest.raises(PoSKError) as excinfo:
        _inp(edges=((_NODES[0], outsider),))

    _assert_token(excinfo, "posk_traversal_edge_references_unvisited_node")
