# SPDX-License-Identifier: AGPL-3.0-only
"""CDL-075 truth primitive graph persistence logic.

Defines the canonical node record schema, CIDv1 derivation rule, and
store-contract write path for truth primitive submissions validated by the
CDL-074 runtime. Concrete LMDB persistence lives behind the storage adapter in
`ilc_core.storage.truth_primitive_graph_lmdb_adapter`.

Write path only — no read-path query integration, no network delivery,
no cross-epoch compaction.

Phases:
    879 — node_record_from_submission, node_id_from_submission
    880 — graph persistence contract write path
    881 — idempotency guard, edge-only writes
"""

from __future__ import annotations

from typing import Any

from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.epistemic.truth_primitive_submission_runtime import (
    TruthPrimitiveResult,
    AGENT_ISSUABLE_PRIMITIVES,
)
from ilc_core.protocol.harness_interfaces import TruthPrimitiveGraphPersistence

# ---------------------------------------------------------------------------
# Dependency and version tokens
# ---------------------------------------------------------------------------

CDL_075_DEPENDENCY = "cdl_075_truth_primitive_graph_persistence.v0.1"
CDL_074_DEPENDENCY = "cdl_074_truth_primitive_runtime_ratified.v0.1"

TRUTH_PRIMITIVE_GRAPH_STORE_VERSION = "truth_primitive_graph_store_880.v0.1"

_CDL_075_VERSION_TAG = "cdl_075.v0.1"

# Import guard — CDL-075 is open at Phase 878; this tag locks at ratification.
# Updated to ratified token at Phase 884.
_CDL_075_OPEN_TOKEN = "cdl_075_open_at_phase_878"

# Primitives that create a new graph node (others produce edge-only writes).
_NODE_CREATING_PRIMITIVES: frozenset[str] = frozenset({
    "assert.truth",
    "revise.assert",
})

# ---------------------------------------------------------------------------
# Phase 879 — Canonical node record schema + CIDv1 derivation
# ---------------------------------------------------------------------------


def node_record_from_submission(
    envelope: dict[str, Any],
    result: TruthPrimitiveResult,
) -> dict[str, Any]:
    """Build the canonical CDL-075 node record from a validated submission.

    The returned dict is deterministic (sorted string keys, DAG-CBOR encodable)
    and is used both for LMDB storage and CIDv1 derivation.

    Only valid for node-creating primitives (assert.truth, revise.assert).
    Call node_id_from_submission to verify before persisting.

    Args:
        envelope: CDL-073 wire-format submission dict {v, primitive, agent_id,
                  epoch, payload, sig}.
        result: TruthPrimitiveResult from validate_truth_primitive_submission.

    Returns:
        Deterministic canonical node record dict.

    Raises:
        ValueError: If the primitive does not create a node.
    """
    primitive = str(envelope.get("primitive", ""))
    if primitive not in _NODE_CREATING_PRIMITIVES:
        raise ValueError(
            f"node_record_from_submission_invalid_primitive: "
            f"'{primitive}' does not create a node; "
            f"node-creating set: {sorted(_NODE_CREATING_PRIMITIVES)}"
        )

    # Canonical field order is fixed by CDL-075 §2.1.
    # Keys are sorted strings to satisfy node_id_from_obj invariants.
    record = {
        "agent_id": str(envelope.get("agent_id", "")),
        "cdl_version": _CDL_075_VERSION_TAG,
        "epoch": int(envelope.get("epoch", 0)),
        "payload": dict(envelope.get("payload", {})),
        "primitive": primitive,
        "primitive_type": result.node_primitive_type,
    }
    if result.uncertainty_declared is not None:
        record["uncertainty_declared"] = result.uncertainty_declared
    sig = envelope.get("sig")
    if isinstance(sig, str) and sig not in {"", "UNSIGNED"}:
        record["v"] = int(envelope.get("v", 1))
        record["sig"] = sig
        record["sig_pubkey_hex"] = str(envelope.get("sig_pubkey_hex", ""))
        record["sig_pubkey_fingerprint"] = str(envelope.get("sig_pubkey_fingerprint", ""))
        record["sig_scheme"] = str(envelope.get("sig_scheme", ""))
    return record


def node_id_from_submission(
    envelope: dict[str, Any],
    result: TruthPrimitiveResult,
) -> str:
    """Derive the deterministic CIDv1 node identifier for a submission.

    CIDv1 derivation rule (CDL-075 §2.2):
        node_id = node_id_from_obj(canonical_node_record)

    Identical submissions always produce the same CIDv1, providing the
    idempotency guarantee.

    Args:
        envelope: CDL-073 submission envelope.
        result: Validated TruthPrimitiveResult.

    Returns:
        CIDv1 string (multibase base32 lowercase, 'b' prefix).

    Raises:
        ValueError: If the primitive does not create a node.
    """
    record = node_record_from_submission(envelope, result)
    return node_id_from_obj(record)


# ---------------------------------------------------------------------------
# Phase 881 — Edge resolution helpers
# ---------------------------------------------------------------------------


def _resolve_label(
    label: str,
    *,
    agent_id: str,
    node_id: str | None,
    payload: dict[str, Any],
    parent_iter: Any,
    evidence_iter: Any,
) -> str | None:
    """Map an EdgeSpec semantic label to its concrete value.

    Multi-valued labels (parent_node_id, evidence_node_id) consume the next
    item from the corresponding iterator on each call.
    """
    if label == "new_node_id":
        return node_id
    if label == "agent_id":
        return agent_id
    if label == "target_node_id":
        return str(payload.get("target_node_id", ""))
    if label == "node_a_id":
        return str(payload.get("node_a_id", ""))
    if label == "node_b_id":
        return str(payload.get("node_b_id", ""))
    if label == "source_node_id":
        return str(payload.get("source_node_id", ""))
    if label == "parent_node_id":
        return next(parent_iter, None)
    if label == "refutation_context":
        # The refutation context is keyed off the target node being refuted.
        return str(payload.get("target_node_id", ""))
    if label == "evidence_node_id":
        return next(evidence_iter, None)
    # Unknown label — pass through as literal (forward compatibility).
    return label


def _resolve_edges(
    envelope: dict[str, Any],
    result: TruthPrimitiveResult,
    node_id: str | None,
) -> list[dict[str, Any]]:
    """Resolve EdgeSpec semantic labels to concrete edge records.

    Args:
        envelope: CDL-073 submission envelope.
        result: Validated TruthPrimitiveResult.
        node_id: Computed CIDv1 for node-creating primitives; None otherwise.

    Returns:
        List of edge record dicts ready for LMDB storage.
    """
    agent_id = str(envelope.get("agent_id", ""))
    epoch = int(envelope.get("epoch", 0))
    primitive = str(envelope.get("primitive", ""))
    payload = dict(envelope.get("payload", {}))

    parent_iter = iter(list(payload.get("parent_node_ids", [])))
    evidence_iter = iter(list(payload.get("evidence_node_ids", [])))

    records: list[dict[str, Any]] = []
    for edge in result.edges:
        source = _resolve_label(
            edge.source,
            agent_id=agent_id,
            node_id=node_id,
            payload=payload,
            parent_iter=parent_iter,
            evidence_iter=evidence_iter,
        )
        target = _resolve_label(
            edge.target,
            agent_id=agent_id,
            node_id=node_id,
            payload=payload,
            parent_iter=parent_iter,
            evidence_iter=evidence_iter,
        )
        if source is None or target is None:
            # Label resolved to nothing (e.g. empty parent_node_ids list) — skip.
            continue
        records.append({
            "agent_id": agent_id,
            "edge_type": edge.edge_type,
            "epoch": epoch,
            "source": source,
            "target": target,
        })
        if result.uncertainty_declared is not None:
            records[-1]["uncertainty_declared"] = result.uncertainty_declared
        sig = envelope.get("sig")
        if isinstance(sig, str) and sig not in {"", "UNSIGNED"}:
            records[-1]["payload"] = payload
            records[-1]["primitive"] = primitive
            records[-1]["sig"] = sig
            records[-1]["sig_pubkey_hex"] = str(envelope.get("sig_pubkey_hex", ""))
            records[-1]["sig_pubkey_fingerprint"] = str(envelope.get("sig_pubkey_fingerprint", ""))
            records[-1]["sig_scheme"] = str(envelope.get("sig_scheme", ""))
            records[-1]["v"] = int(envelope.get("v", 1))

    return records


def _edge_key(record: dict[str, Any]) -> str:
    """Derive the LMDB key for an edge record.

    Key format (CDL-075 §2.3): "{source}:{edge_type}:{target}"
    """
    return f"{record['source']}:{record['edge_type']}:{record['target']}"


# ---------------------------------------------------------------------------
# Phase 880 — Primary write function
# ---------------------------------------------------------------------------


def write_truth_primitive_result(
    store: TruthPrimitiveGraphPersistence,
    envelope: dict[str, Any],
    result: TruthPrimitiveResult,
) -> dict[str, Any]:
    """Persist a validated truth primitive submission to a graph store.

    For node-creating primitives (assert.truth, revise.assert):
        - Derives the CIDv1 node_id from the canonical node record.
        - Writes the node record under the CIDv1 key (put_if_absent).
        - Writes all resolved edge records (put_if_absent).

    For edge-only primitives (validate.claim, contradict.assert, link.claim,
    refute.claim):
        - Derives no node_id.
        - Writes only the resolved edge records.

    Idempotency: calling this function twice with identical input is safe —
    records already present are skipped and the same node_id is returned.

    Args:
        store: Open graph persistence contract.
        envelope: CDL-073 submission envelope dict.
        result: Validated TruthPrimitiveResult from CDL-074 runtime.

    Returns:
        Write receipt dict: {node_id, nodes_written, edges_written, primitive}.
    """
    primitive = result.primitive

    # Derive node_id for node-creating primitives.
    node_id: str | None = None
    node_written = False
    if result.creates_node:
        node_id = node_id_from_submission(envelope, result)
        canonical = node_record_from_submission(envelope, result)
        node_written = store.put_node_if_absent(node_id, canonical)

    # Resolve and persist edges.
    edge_records = _resolve_edges(envelope, result, node_id)
    edges_written = 0
    for record in edge_records:
        key = _edge_key(record)
        if store.put_edge_if_absent(key, record):
            edges_written += 1

    return {
        "node_id": node_id,
        "nodes_written": 1 if node_written else 0,
        "edges_written": edges_written,
        "primitive": primitive,
        "version": TRUTH_PRIMITIVE_GRAPH_STORE_VERSION,
    }
