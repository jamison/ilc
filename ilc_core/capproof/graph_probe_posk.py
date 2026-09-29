# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1608 CapProof GraphProbe Proof of Structural Knowledge substrate.

This module implements a challenge-bound, replay-detectable commitment over a
canonical local graph traversal. It is not consensus-binding in Phase 1608.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Sequence

POSK_RUNTIME_VERSION = "graph_probe_posk_runtime_phase_1608.v0.1"
POSK_SPECTRAL_NOT_ACTIVATED = True
POSK_CONSENSUS_BINDING = False

POSK_MAX_TRAVERSAL_NODES = 1024
POSK_MAX_TRAVERSAL_EDGES = 4096
POSK_MAX_REPLAY_LEDGER_ENTRIES = 8192

_LOWER_HEX_64_RE = re.compile(r"^[0-9a-f]{64}$")
_EPOCH_SALT_RE = re.compile(r"^[0-9a-f]{64,128}$")
_CID_OR_HASH_RE = re.compile(r"^(?:bafy[a-z2-7]{10,}|[0-9a-f]{64})$")


class PoSKError(ValueError):
    """Stable-token error for Phase 1608 PoSK callers and tests."""

    def __init__(self, token: str, message: str = "") -> None:
        super().__init__(message or token)
        self.token = token


@dataclass(frozen=True)
class PoSKChallenge:
    """Epoch-bound PoSK challenge derived from graph root and epoch salt."""

    graph_root_hash: str
    epoch_salt: str
    epoch: int
    challenge_id: str
    runtime_version: str = POSK_RUNTIME_VERSION

    def __post_init__(self) -> None:
        graph_root_hash = _require_lower_hex_64(
            self.graph_root_hash,
            "posk_graph_root_hash_must_be_64_lower_hex",
        )
        epoch_salt = _require_epoch_salt(self.epoch_salt)
        epoch = _require_epoch(self.epoch)
        challenge_id = _require_lower_hex_64(
            self.challenge_id,
            "posk_challenge_id_must_be_64_lower_hex",
        )
        expected = _challenge_digest(graph_root_hash, epoch_salt, epoch)
        if challenge_id != expected:
            raise PoSKError("posk_challenge_id_mismatch")
        _require_bool(
            self.runtime_version == POSK_RUNTIME_VERSION,
            "posk_runtime_version_mismatch",
        )


@dataclass(frozen=True)
class PoSKInput:
    """Input material used to build a challenge-bound traversal proof."""

    graph_root_hash: str
    epoch_salt: str
    epoch: int
    visited_node_ids: tuple[str, ...]
    traversal_edges: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _require_lower_hex_64(
            self.graph_root_hash,
            "posk_graph_root_hash_must_be_64_lower_hex",
        )
        _require_epoch_salt(self.epoch_salt)
        _require_epoch(self.epoch)
        _require_canonical_nodes(self.visited_node_ids)
        _require_canonical_edges(self.traversal_edges, self.visited_node_ids)


@dataclass(frozen=True)
class PoSKProof:
    """Challenge-bound local-graph traversal proof."""

    challenge: PoSKChallenge
    visited_node_ids: tuple[str, ...]
    traversal_edges: tuple[tuple[str, str], ...]
    proof_commitment: str
    node_count: int
    edge_count: int
    spectral_activated: bool = False
    consensus_binding: bool = POSK_CONSENSUS_BINDING
    runtime_version: str = POSK_RUNTIME_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.challenge, PoSKChallenge):
            raise PoSKError("posk_challenge_required")
        nodes = _require_canonical_nodes(self.visited_node_ids)
        edges = _require_canonical_edges(self.traversal_edges, nodes)
        commitment = _require_lower_hex_64(
            self.proof_commitment,
            "posk_commitment_must_be_64_char_hex",
        )
        if self.node_count != len(nodes):
            raise PoSKError("posk_node_count_mismatch")
        if self.edge_count != len(edges):
            raise PoSKError("posk_edge_count_mismatch")
        if self.spectral_activated:
            raise PoSKError("posk_spectral_not_activated_in_phase_1608")
        if self.consensus_binding:
            raise PoSKError("posk_consensus_binding_not_activated_phase_1608")
        _require_bool(
            self.runtime_version == POSK_RUNTIME_VERSION,
            "posk_runtime_version_mismatch",
        )
        _require_lower_hex_64(commitment, "posk_commitment_must_be_64_char_hex")


@dataclass(frozen=True)
class PoSKReplayLedger:
    """Append-only bounded replay ledger for `(epoch, proof_commitment)` pairs."""

    entries: tuple[tuple[int, str], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if len(self.entries) > POSK_MAX_REPLAY_LEDGER_ENTRIES:
            raise PoSKError("posk_replay_ledger_exceeds_max_entries")
        seen: set[tuple[int, str]] = set()
        for epoch, commitment in self.entries:
            normalized_epoch = _require_epoch(epoch)
            normalized_commitment = _require_lower_hex_64(
                commitment,
                "posk_commitment_must_be_64_char_hex",
            )
            key = (normalized_epoch, normalized_commitment)
            if key in seen:
                raise PoSKError("posk_replay_ledger_contains_duplicate")
            seen.add(key)


def derive_posk_challenge(graph_root_hash: str, epoch_salt: str, epoch: int) -> PoSKChallenge:
    """Derive a deterministic PoSK challenge.

    # CDL-115-DELIBERATION-Q6: graph_root_hash binding for GraphProbe remains
    # under governance review; Phase 1608 binds it explicitly for Gate-A tests.
    """

    normalized_graph_root_hash = _require_lower_hex_64(
        graph_root_hash,
        "posk_graph_root_hash_must_be_64_lower_hex",
    )
    normalized_epoch_salt = _require_epoch_salt(epoch_salt)
    normalized_epoch = _require_epoch(epoch)
    return PoSKChallenge(
        graph_root_hash=normalized_graph_root_hash,
        epoch_salt=normalized_epoch_salt,
        epoch=normalized_epoch,
        challenge_id=_challenge_digest(
            normalized_graph_root_hash,
            normalized_epoch_salt,
            normalized_epoch,
        ),
    )


def build_posk_proof(inp: PoSKInput) -> PoSKProof:
    """Build a canonical challenge-bound traversal proof."""

    challenge = derive_posk_challenge(inp.graph_root_hash, inp.epoch_salt, inp.epoch)
    nodes = _require_canonical_nodes(inp.visited_node_ids)
    edges = _require_canonical_edges(inp.traversal_edges, nodes)
    commitment = _proof_digest(challenge, nodes, edges)
    return PoSKProof(
        challenge=challenge,
        visited_node_ids=nodes,
        traversal_edges=edges,
        proof_commitment=commitment,
        node_count=len(nodes),
        edge_count=len(edges),
    )


def compute_posk_commitment(inp: PoSKInput) -> PoSKProof:
    """Compatibility wrapper returning the Phase 1608 proof object."""

    return build_posk_proof(inp)


def verify_posk_proof(proof: PoSKProof) -> bool:
    """Verify that the proof commitment matches the challenge and traversal."""

    if not isinstance(proof, PoSKProof):
        raise PoSKError("posk_proof_required")
    expected = _proof_digest(proof.challenge, proof.visited_node_ids, proof.traversal_edges)
    if proof.proof_commitment != expected:
        raise PoSKError("posk_commitment_mismatch")
    return True


def record_posk_replay_or_raise(
    ledger: PoSKReplayLedger | None,
    proof: PoSKProof,
) -> PoSKReplayLedger:
    """Return a new replay ledger after rejecting duplicate proof commitments."""

    current = ledger if ledger is not None else PoSKReplayLedger()
    verify_posk_proof(proof)
    key = (proof.challenge.epoch, proof.proof_commitment)
    if key in current.entries:
        raise PoSKError("posk_replay_detected_phase_1608")
    if len(current.entries) >= POSK_MAX_REPLAY_LEDGER_ENTRIES:
        raise PoSKError("posk_replay_ledger_exceeds_max_entries")
    return PoSKReplayLedger(entries=current.entries + (key,))


def _challenge_digest(graph_root_hash: str, epoch_salt: str, epoch: int) -> str:
    payload = json.dumps(
        {
            "epoch": epoch,
            "epoch_salt": epoch_salt,
            "graph_root_hash": graph_root_hash,
            "runtime_version": POSK_RUNTIME_VERSION,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _proof_digest(
    challenge: PoSKChallenge,
    visited_node_ids: tuple[str, ...],
    traversal_edges: tuple[tuple[str, str], ...],
) -> str:
    payload = json.dumps(
        {
            "challenge_id": challenge.challenge_id,
            "edge_count": len(traversal_edges),
            "node_count": len(visited_node_ids),
            "traversal_edges": traversal_edges,
            "visited_node_ids": visited_node_ids,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _require_canonical_nodes(node_ids: Sequence[str]) -> tuple[str, ...]:
    if not isinstance(node_ids, tuple):
        raise PoSKError("posk_visited_node_ids_must_be_tuple")
    if len(node_ids) == 0:
        raise PoSKError("posk_visited_node_ids_must_be_non_empty")
    if len(node_ids) > POSK_MAX_TRAVERSAL_NODES:
        raise PoSKError("posk_traversal_exceeds_max_node_count")
    for node_id in node_ids:
        _require_node_id(node_id)
    if tuple(sorted(set(node_ids))) != node_ids:
        raise PoSKError("posk_visited_node_ids_must_be_canonical_unique_sorted")
    return node_ids


def _require_canonical_edges(
    traversal_edges: Sequence[tuple[str, str]],
    node_ids: tuple[str, ...],
) -> tuple[tuple[str, str], ...]:
    if not isinstance(traversal_edges, tuple):
        raise PoSKError("posk_traversal_edges_must_be_tuple")
    if len(traversal_edges) > POSK_MAX_TRAVERSAL_EDGES:
        raise PoSKError("posk_traversal_exceeds_max_edge_count")
    node_set = set(node_ids)
    normalized_edges: list[tuple[str, str]] = []
    for edge in traversal_edges:
        if (
            not isinstance(edge, tuple)
            or len(edge) != 2
            or not isinstance(edge[0], str)
            or not isinstance(edge[1], str)
        ):
            raise PoSKError("posk_traversal_edge_must_be_pair")
        source = _require_node_id(edge[0])
        target = _require_node_id(edge[1])
        if source not in node_set or target not in node_set:
            raise PoSKError("posk_traversal_edge_references_unvisited_node")
        normalized_edges.append((source, target))
    canonical = tuple(sorted(set(normalized_edges)))
    if canonical != traversal_edges:
        raise PoSKError("posk_traversal_edges_must_be_canonical_unique_sorted")
    return traversal_edges


def _require_node_id(node_id: str) -> str:
    if (
        not isinstance(node_id, str)
        or node_id != node_id.strip()
        or _CID_OR_HASH_RE.fullmatch(node_id) is None
    ):
        raise PoSKError("posk_node_id_must_be_content_addressed_string")
    return node_id


def _require_epoch_salt(epoch_salt: str) -> str:
    if (
        not isinstance(epoch_salt, str)
        or epoch_salt != epoch_salt.strip()
        or epoch_salt != epoch_salt.lower()
        or _EPOCH_SALT_RE.fullmatch(epoch_salt) is None
    ):
        raise PoSKError("posk_epoch_salt_must_be_64_to_128_lower_hex")
    return epoch_salt


def _require_lower_hex_64(value: str, token: str) -> str:
    if not isinstance(value, str) or _LOWER_HEX_64_RE.fullmatch(value) is None:
        raise PoSKError(token)
    return value


def _require_epoch(epoch: int) -> int:
    if not isinstance(epoch, int) or type(epoch) is bool or epoch < 0:
        raise PoSKError("posk_epoch_must_be_non_negative_int")
    return epoch


def _require_bool(condition: bool, token: str) -> None:
    if condition is not True:
        raise PoSKError(token)
