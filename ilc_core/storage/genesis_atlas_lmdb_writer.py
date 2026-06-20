# SPDX-License-Identifier: AGPL-3.0-only
"""Safe writer contract for the unsigned Genesis Atlas LMDB projection.

PUBLIC_RC_EXCLUDE: genesis_atlas_lmdb_safe_writer_research_only
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Atlas LMDB maintenance helper; not
public graph activation, Genesis signing, canonical graph mutation, runtime
activation, public serving, or economic settlement.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import (
    GenesisAtlasCandidateStore,
)
from ilc_core.storage.lmdb_public_runtime import DEFAULT_MAP_SIZE_BYTES


GENESIS_ATLAS_LMDB_WRITER_VERSION = "genesis_atlas_lmdb_writer_1545p_fix59b.v0.1"
DEFAULT_PUBLIC_PATH_POLICY = "policy:public_path_still_blocked_phase_1545p"


@dataclass(frozen=True)
class AtlasLmdbWritePlan:
    """JSON-serializable write instruction set for unsigned Atlas LMDB edits."""

    nodes_to_add: list[dict[str, Any]] = field(default_factory=list)
    edges_to_add: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    phase: str = ""
    dry_run: bool = True


@dataclass(frozen=True)
class AtlasPhaseFileRegistration:
    """Support-only LMDB registration row for a committed phase artifact."""

    path: str | Path
    node_kind: str
    graph_projection: str
    graph_delta: str = "support_only"
    required_edges: tuple[tuple[str, str], ...] = ()
    skip_carries_forward: bool = False


class AtlasLmdbSafeWriter:
    """Validation-first writer over :class:`GenesisAtlasCandidateStore`.

    The raw adapter remains the only LMDB schema owner. This wrapper composes a
    full in-memory graph, rejects invalid deltas, writes accepted additions, and
    rebuilds the graph payload plus node indexes from the merged graph.
    """

    def __init__(
        self,
        lmdb_root: Path | str,
        *,
        allow_synthetic_edge_keys: bool = True,
        map_size: int = DEFAULT_MAP_SIZE_BYTES * 4,
    ) -> None:
        self.lmdb_root = Path(lmdb_root)
        self.store = GenesisAtlasCandidateStore(
            self.lmdb_root,
            allow_synthetic_edge_keys=allow_synthetic_edge_keys,
            map_size=map_size,
        )

    def close(self) -> None:
        self.store.close()

    def inspect(self) -> dict[str, Any]:
        nodes = self.store.iter_nodes()
        edges = self.store.iter_edges()
        payload = self.store.get_graph_payload() or {}
        node_ids = {_candidate_id(node) for node in nodes}
        invariants = _inspect_invariants(
            nodes=nodes,
            edges=edges,
            payload=payload,
            store=self.store,
        )
        return {
            "edge_count": len(edges),
            "edge_id_debt_count": sum(1 for edge in edges if not edge.get("edge_id")),
            "graph_payload_edge_count": len(payload.get("edges", []))
            if isinstance(payload.get("edges"), list)
            else 0,
            "graph_payload_node_count": len(payload.get("nodes", []))
            if isinstance(payload.get("nodes"), list)
            else 0,
            "invariants": invariants,
            "lmdb_path": str(self.lmdb_root),
            "node_count": len(nodes),
            "preimage_count": len(self.store.iter_preimages()),
            "version": GENESIS_ATLAS_LMDB_WRITER_VERSION,
            "dangling_edge_count": sum(
                1
                for edge in edges
                if _edge_source(edge) not in node_ids or _edge_target(edge) not in node_ids
            ),
        }

    def validate_plan(self, plan: AtlasLmdbWritePlan) -> dict[str, Any]:
        current_nodes = self.store.iter_nodes()
        current_edges = self.store.iter_edges()
        current_payload = self.store.get_graph_payload() or {}
        return _validate_plan(
            plan=plan,
            current_nodes=current_nodes,
            current_edges=current_edges,
            current_payload=current_payload,
        )

    def apply_plan(self, plan: AtlasLmdbWritePlan) -> dict[str, Any]:
        validation = self.validate_plan(plan)
        if plan.dry_run:
            receipt = _receipt_from_validation(validation, mutated=False)
            return receipt

        merged_nodes = validation["merged_nodes"]
        accepted_edges = validation["accepted_edges"]
        merged_edges = validation["merged_edges"]
        payload = dict(validation["current_payload"])
        payload["nodes"] = merged_nodes
        payload["edges"] = merged_edges
        payload["safe_writer"] = {
            "last_phase": plan.phase,
            "version": GENESIS_ATLAS_LMDB_WRITER_VERSION,
        }

        self.store.put_nodes(merged_nodes)
        if accepted_edges:
            self.store.put_edges(accepted_edges)
        self.store.put_graph_payload(payload)

        post_nodes = self.store.iter_nodes()
        post_edges = self.store.iter_edges()
        post_payload = self.store.get_graph_payload() or {}
        post_invariants = _inspect_invariants(
            nodes=post_nodes,
            edges=post_edges,
            payload=post_payload,
            store=self.store,
        )
        receipt = _receipt_from_validation(validation, mutated=True)
        receipt["post_lmdb_counts"] = {
            "edges": len(post_edges),
            "nodes": len(post_nodes),
            "payload_edges": len(post_payload.get("edges", []))
            if isinstance(post_payload.get("edges"), list)
            else 0,
            "payload_nodes": len(post_payload.get("nodes", []))
            if isinstance(post_payload.get("nodes"), list)
            else 0,
        }
        receipt["post_invariants"] = post_invariants
        receipt["status"] = "PASS" if all(post_invariants.values()) else "FAIL"
        if plan.phase:
            self.store.put_meta(f"safe_writer_receipt:{plan.phase}", receipt)
            self.store.put_meta("last_safe_writer_receipt", receipt)
        return receipt

    def register_phase_files(
        self,
        phase: str,
        files: Sequence[AtlasPhaseFileRegistration | dict[str, Any] | str | Path],
        *,
        dry_run: bool = True,
        extra_nodes: Sequence[dict[str, Any]] = (),
    ) -> dict[str, Any]:
        registrations = [_coerce_phase_file_registration(item) for item in files]
        plan = self.build_phase_file_registration_plan(
            phase=phase,
            files=registrations,
            dry_run=dry_run,
            extra_nodes=extra_nodes,
        )
        return self.apply_plan(plan)

    def build_phase_file_registration_plan(
        self,
        *,
        phase: str,
        files: Sequence[AtlasPhaseFileRegistration],
        dry_run: bool,
        extra_nodes: Sequence[dict[str, Any]] = (),
    ) -> AtlasLmdbWritePlan:
        current_node_ids = {_candidate_id(node) for node in self.store.iter_nodes()}
        nodes_to_add: list[dict[str, Any]] = []
        edges_to_add: list[dict[str, Any]] = []
        phase_node_id = f"phase:{_phase_slug(phase)}"
        _append_if_missing(
            nodes_to_add,
            current_node_ids,
            _support_node(
                phase_node_id,
                node_kind="phase_support_node",
                graph_projection="support_candidate_graph",
                label=phase,
                phase=phase,
            ),
        )
        _append_if_missing(
            nodes_to_add,
            current_node_ids,
            _support_node(
                DEFAULT_PUBLIC_PATH_POLICY,
                node_kind="policy_support_node",
                graph_projection="support_candidate_graph",
                label=DEFAULT_PUBLIC_PATH_POLICY,
                phase=phase,
            ),
        )
        for node in extra_nodes:
            _append_if_missing(nodes_to_add, current_node_ids, node)
        current_node_ids.update(_candidate_id(node) for node in nodes_to_add)

        for registration in files:
            file_node = _file_node_from_registration(registration, phase=phase)
            _append_if_missing(nodes_to_add, current_node_ids, file_node)
            file_id = _candidate_id(file_node)
            edges_to_add.append(
                _edge(
                    source=file_id,
                    edge_type="CLASSIFIED_BY",
                    target=DEFAULT_PUBLIC_PATH_POLICY,
                    phase=phase,
                    candidate_status="fix59b_phase_file_registration_edge",
                )
            )
            if not registration.skip_carries_forward:
                edges_to_add.append(
                    _edge(
                        source=file_id,
                        edge_type="CARRIES_FORWARD",
                        target=phase_node_id,
                        phase=phase,
                        candidate_status="fix59b_phase_file_registration_edge",
                    )
                )
            for edge_type, target in registration.required_edges:
                edges_to_add.append(
                    _edge(
                        source=file_id,
                        edge_type=edge_type,
                        target=target,
                        phase=phase,
                        candidate_status="fix59b_phase_file_registration_edge",
                    )
                )

        return AtlasLmdbWritePlan(
            nodes_to_add=nodes_to_add,
            edges_to_add=edges_to_add,
            metadata={
                "operation": "phase_file_registration",
                "registered_file_count": len(files),
            },
            phase=phase,
            dry_run=dry_run,
        )

    def repair_missing_edge_ids(
        self,
        *,
        phase: str,
        dry_run: bool = True,
    ) -> dict[str, Any]:
        """Repair missing edge IDs with a full edge-store rewrite if needed."""
        current_nodes = self.store.iter_nodes()
        current_edges = self.store.iter_edges()
        current_payload = self.store.get_graph_payload() or {}
        updated_edges: list[dict[str, Any]] = []
        repaired_edges: list[dict[str, str]] = []
        for edge in current_edges:
            normalized = dict(edge)
            if not isinstance(normalized.get("edge_id"), str) or not normalized.get("edge_id"):
                source = _edge_source(normalized)
                edge_type = _edge_type(normalized)
                target = _edge_target(normalized)
                normalized["source"] = source
                normalized["src"] = source
                normalized["target"] = target
                normalized["tgt"] = target
                normalized["edge_type"] = edge_type
                normalized["edge_id"] = deterministic_edge_id(source, edge_type, target)
                repaired_edges.append(
                    {
                        "edge_id": normalized["edge_id"],
                        "edge_type": edge_type,
                        "source": source,
                        "target": target,
                    }
                )
            updated_edges.append(normalized)

        payload = dict(current_payload)
        payload["nodes"] = current_nodes
        payload["edges"] = updated_edges
        payload["safe_writer"] = {
            "last_phase": phase,
            "version": GENESIS_ATLAS_LMDB_WRITER_VERSION,
        }
        receipt: dict[str, Any] = {
            "dry_run": dry_run,
            "edge_count": len(current_edges),
            "mutated": False,
            "phase": phase,
            "repaired_edge_count": len(repaired_edges),
            "repaired_edges": repaired_edges[:50],
            "version": GENESIS_ATLAS_LMDB_WRITER_VERSION,
        }
        if dry_run:
            return receipt
        if repaired_edges:
            self.store.replace_edges(updated_edges)
            self.store.put_graph_payload(payload)
        post_nodes = self.store.iter_nodes()
        post_edges = self.store.iter_edges()
        post_payload = self.store.get_graph_payload() or {}
        post_invariants = _inspect_invariants(
            nodes=post_nodes,
            edges=post_edges,
            payload=post_payload,
            store=self.store,
        )
        receipt["mutated"] = bool(repaired_edges)
        receipt["post_invariants"] = post_invariants
        receipt["status"] = "PASS" if all(post_invariants.values()) else "FAIL"
        if phase:
            self.store.put_meta(f"safe_writer_edge_id_repair:{phase}", receipt)
            self.store.put_meta("last_safe_writer_receipt", receipt)
        return receipt

    def write_preimages(
        self,
        preimages: Sequence[dict[str, Any]],
        *,
        phase: str,
        dry_run: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Write node or edge preimage records through the safe writer."""
        rows = [dict(row) for row in preimages]
        for row in rows:
            if not isinstance(row.get("node_id"), str) and not isinstance(row.get("edge_id"), str):
                raise ValueError("atlas_lmdb_preimage_key_missing")
            canonical_sha256 = row.get("canonical_sha256")
            if (
                not isinstance(canonical_sha256, str)
                or len(canonical_sha256) != 64
                or any(character not in "0123456789abcdef" for character in canonical_sha256)
            ):
                raise ValueError("atlas_lmdb_preimage_canonical_sha256_invalid")
        receipt = {
            "dry_run": dry_run,
            "metadata": dict(metadata or {}),
            "mutated": False,
            "phase": phase,
            "preimage_count": len(rows),
            "version": GENESIS_ATLAS_LMDB_WRITER_VERSION,
        }
        if dry_run:
            return receipt
        if rows:
            self.store.put_preimages(rows)
        receipt["mutated"] = bool(rows)
        receipt["post_preimage_count"] = len(self.store.iter_preimages())
        receipt["status"] = "PASS"
        if phase:
            scope = str(receipt["metadata"].get("preimage_scope") or receipt["metadata"].get("scope") or "")
            suffix = f":{scope}" if scope else ""
            self.store.put_meta(f"safe_writer_preimages:{phase}{suffix}", receipt)
            self.store.put_meta("last_safe_writer_receipt", receipt)
        return receipt

    def write_metadata(
        self,
        key: str,
        payload: dict[str, Any],
        *,
        phase: str,
        dry_run: bool = True,
    ) -> dict[str, Any]:
        """Write a metadata receipt through the safe writer boundary."""
        if not isinstance(key, str) or not key:
            raise ValueError("atlas_lmdb_metadata_key_missing")
        receipt = {
            "dry_run": dry_run,
            "key": key,
            "mutated": False,
            "phase": phase,
            "version": GENESIS_ATLAS_LMDB_WRITER_VERSION,
        }
        if dry_run:
            return receipt
        self.store.put_meta(key, dict(payload))
        receipt["mutated"] = True
        receipt["status"] = "PASS"
        self.store.put_meta(f"safe_writer_metadata:{phase}:{key}", receipt)
        self.store.put_meta("last_safe_writer_receipt", receipt)
        return receipt

    def update_node_fields(
        self,
        updates: Mapping[str, Mapping[str, Any]],
        *,
        phase: str,
        dry_run: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Apply bounded field updates to existing Atlas nodes.

        This is intentionally narrower than arbitrary node replacement. It
        forbids candidate_id changes, rejects missing nodes, rewrites the full
        node store plus graph payload through the adapter, and leaves edge rows
        untouched. Routine attribution/projection maintenance should use this
        instead of raw LMDB mutation.
        """

        current_nodes = self.store.iter_nodes()
        current_edges = self.store.iter_edges()
        current_payload = self.store.get_graph_payload() or {}
        node_by_id = {_candidate_id(node): dict(node) for node in current_nodes}
        accepted_updates: list[dict[str, Any]] = []
        rejected_updates: list[dict[str, str]] = []
        changed_node_ids: set[str] = set()

        for node_id, patch in sorted(updates.items()):
            if node_id not in node_by_id:
                rejected_updates.append(
                    {"candidate_id": node_id, "reason": "node_missing"}
                )
                continue
            if "candidate_id" in patch and patch["candidate_id"] != node_id:
                rejected_updates.append(
                    {"candidate_id": node_id, "reason": "candidate_id_update_forbidden"}
                )
                continue
            try:
                json.dumps(patch, sort_keys=True, separators=(",", ":"), allow_nan=False)
            except (TypeError, ValueError) as exc:
                raise ValueError("atlas_lmdb_node_update_non_canonical_json") from exc

            before = node_by_id[node_id]
            after = dict(before)
            changed_fields: list[str] = []
            for key, value in sorted(patch.items()):
                if after.get(key) != value:
                    after[key] = value
                    changed_fields.append(key)
            if not changed_fields:
                continue
            node_by_id[node_id] = after
            changed_node_ids.add(node_id)
            accepted_updates.append(
                {
                    "candidate_id": node_id,
                    "changed_fields": changed_fields,
                }
            )

        updated_nodes = sorted(node_by_id.values(), key=_candidate_id)
        payload = dict(current_payload)
        payload["nodes"] = updated_nodes
        payload["edges"] = current_edges
        payload["safe_writer"] = {
            "last_phase": phase,
            "version": GENESIS_ATLAS_LMDB_WRITER_VERSION,
        }
        receipt: dict[str, Any] = {
            "accepted_update_count": len(accepted_updates),
            "accepted_updates": accepted_updates[:50],
            "dry_run": dry_run,
            "metadata": dict(metadata or {}),
            "mutated": False,
            "phase": phase,
            "pre_counts": {"edges": len(current_edges), "nodes": len(current_nodes)},
            "rejected_update_count": len(rejected_updates),
            "rejected_updates": rejected_updates,
            "updated_field_count": sum(
                len(item["changed_fields"]) for item in accepted_updates
            ),
            "version": GENESIS_ATLAS_LMDB_WRITER_VERSION,
        }
        if dry_run:
            receipt["projected_counts"] = {
                "edges": len(current_edges),
                "nodes": len(updated_nodes),
            }
            return receipt

        if changed_node_ids:
            self.store.put_nodes(updated_nodes)
            self.store.put_graph_payload(payload)
        post_nodes = self.store.iter_nodes()
        post_edges = self.store.iter_edges()
        post_payload = self.store.get_graph_payload() or {}
        post_invariants = _inspect_invariants(
            nodes=post_nodes,
            edges=post_edges,
            payload=post_payload,
            store=self.store,
        )
        receipt["mutated"] = bool(changed_node_ids)
        receipt["post_counts"] = {"edges": len(post_edges), "nodes": len(post_nodes)}
        receipt["post_invariants"] = post_invariants
        receipt["status"] = "PASS" if all(post_invariants.values()) else "FAIL"
        if phase:
            self.store.put_meta(f"safe_writer_node_updates:{phase}", receipt)
            self.store.put_meta("last_safe_writer_receipt", receipt)
        return receipt


def deterministic_edge_id(source: str, edge_type: str, target: str) -> str:
    digest = hashlib.sha256(f"{source}|{edge_type}|{target}".encode("utf-8")).hexdigest()[:16]
    return f"edge:{digest}"


def repo_file_ref_id(path: str | Path) -> str:
    value = Path(path).as_posix()
    sanitized = (
        value.lower()
        .replace("/", "_")
        .replace(".", "_")
        .replace("-", "_")
    )
    while "__" in sanitized:
        sanitized = sanitized.replace("__", "_")
    return f"repo:file_ref:{sanitized}"


def write_json_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False))
            handle.write("\n")
        os.replace(tmp_path, path)
        path.chmod(0o644)
    except Exception:
        try:
            tmp_path.unlink()
        finally:
            raise


def _validate_plan(
    *,
    plan: AtlasLmdbWritePlan,
    current_nodes: list[dict[str, Any]],
    current_edges: list[dict[str, Any]],
    current_payload: dict[str, Any],
) -> dict[str, Any]:
    node_by_id = {_candidate_id(node): dict(node) for node in current_nodes}
    duplicate_nodes = _duplicates(_candidate_id(node) for node in plan.nodes_to_add)
    if duplicate_nodes:
        raise ValueError(f"atlas_lmdb_write_plan_duplicate_nodes:{duplicate_nodes}")
    accepted_nodes: list[dict[str, Any]] = []
    skipped_nodes: list[dict[str, str]] = []
    for node in plan.nodes_to_add:
        node_id = _candidate_id(node)
        if node_id in node_by_id:
            skipped_nodes.append({"candidate_id": node_id, "reason": "node_already_present"})
            continue
        normalized_node = dict(node)
        normalized_node.setdefault("annotation_phase", _phase_token(plan.phase))
        normalized_node.setdefault("graph_delta", "support_only")
        normalized_node.setdefault("tier", "support_candidate")
        node_by_id[node_id] = normalized_node
        accepted_nodes.append(normalized_node)

    existing_edge_semantics = {
        (_edge_source(edge), _edge_type(edge), _edge_target(edge)) for edge in current_edges
    }
    edge_by_id = {
        str(edge.get("edge_id")): edge
        for edge in current_edges
        if isinstance(edge.get("edge_id"), str) and edge.get("edge_id")
    }
    accepted_edges: list[dict[str, Any]] = []
    rejected_edges: list[dict[str, str]] = []
    skipped_edges: list[dict[str, str]] = []
    plan_edge_semantics: set[tuple[str, str, str]] = set()
    for edge in plan.edges_to_add:
        normalized = _normalize_edge(edge, phase=plan.phase)
        source = _edge_source(normalized)
        edge_type = _edge_type(normalized)
        target = _edge_target(normalized)
        edge_id = str(normalized["edge_id"])
        if source not in node_by_id:
            rejected_edges.append(
                {
                    "edge_id": edge_id,
                    "edge_type": edge_type,
                    "reason": "source_node_missing",
                    "source": source,
                    "target": target,
                }
            )
            continue
        if target not in node_by_id:
            rejected_edges.append(
                {
                    "edge_id": edge_id,
                    "edge_type": edge_type,
                    "reason": "target_node_missing",
                    "source": source,
                    "target": target,
                }
            )
            continue
        semantic = (source, edge_type, target)
        if semantic in existing_edge_semantics or edge_id in edge_by_id or semantic in plan_edge_semantics:
            skipped_edges.append(
                {
                    "edge_id": edge_id,
                    "edge_type": edge_type,
                    "reason": "duplicate_edge_semantic",
                    "source": source,
                    "target": target,
                }
            )
            continue
        accepted_edges.append(normalized)
        plan_edge_semantics.add(semantic)

    merged_nodes = sorted(node_by_id.values(), key=_candidate_id)
    merged_edges = sorted(
        [*current_edges, *accepted_edges],
        key=lambda edge: (
            str(edge.get("edge_id", "")),
            _edge_source(edge),
            _edge_type(edge),
            _edge_target(edge),
        ),
    )
    merged_node_ids = {_candidate_id(node) for node in merged_nodes}
    projected_dangling = [
        {
            "edge_id": str(edge.get("edge_id", "")),
            "source": _edge_source(edge),
            "target": _edge_target(edge),
        }
        for edge in merged_edges
        if _edge_source(edge) not in merged_node_ids or _edge_target(edge) not in merged_node_ids
    ]
    return {
        "accepted_edges": accepted_edges,
        "accepted_nodes": accepted_nodes,
        "current_payload": current_payload,
        "dry_run": plan.dry_run,
        "merged_edges": merged_edges,
        "merged_nodes": merged_nodes,
        "metadata": dict(plan.metadata),
        "phase": plan.phase,
        "pre_counts": {"edges": len(current_edges), "nodes": len(current_nodes)},
        "projected_counts": {"edges": len(merged_edges), "nodes": len(merged_nodes)},
        "projected_dangling_edges": projected_dangling,
        "rejected_edges": rejected_edges,
        "skipped_edges": skipped_edges,
        "skipped_nodes": skipped_nodes,
        "status": "PASS" if not projected_dangling else "FAIL",
    }


def _receipt_from_validation(validation: dict[str, Any], *, mutated: bool) -> dict[str, Any]:
    return {
        "accepted_edge_count": len(validation["accepted_edges"]),
        "accepted_edges": _edge_summary(validation["accepted_edges"]),
        "accepted_node_count": len(validation["accepted_nodes"]),
        "accepted_nodes": _node_summary(validation["accepted_nodes"]),
        "dry_run": bool(validation["dry_run"]),
        "metadata": validation["metadata"],
        "mutated": mutated,
        "phase": validation["phase"],
        "pre_counts": validation["pre_counts"],
        "projected_counts": validation["projected_counts"],
        "projected_dangling_edge_count": len(validation["projected_dangling_edges"]),
        "projected_dangling_edges": validation["projected_dangling_edges"][:50],
        "rejected_edge_count": len(validation["rejected_edges"]),
        "rejected_edges": validation["rejected_edges"],
        "skipped_edge_count": len(validation["skipped_edges"]),
        "skipped_edges": validation["skipped_edges"][:50],
        "skipped_node_count": len(validation["skipped_nodes"]),
        "skipped_nodes": validation["skipped_nodes"],
        "status": validation["status"],
        "version": GENESIS_ATLAS_LMDB_WRITER_VERSION,
    }


def _inspect_invariants(
    *,
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    payload: dict[str, Any],
    store: GenesisAtlasCandidateStore,
) -> dict[str, bool]:
    node_ids = {_candidate_id(node) for node in nodes}
    tier_index = _node_index(nodes, key="tier", default="unknown")
    tier_group_index: dict[str, list[str]] = {}
    source_path_index: dict[str, list[str]] = {}
    for node in nodes:
        node_id = _candidate_id(node)
        tier_group_index.setdefault(_tier_group(node), []).append(node_id)
        source_path = node.get("source_path")
        if isinstance(source_path, str) and source_path:
            source_path_index.setdefault(source_path, []).append(node_id)
    return {
        "no_dangling_edges": all(
            _edge_source(edge) in node_ids and _edge_target(edge) in node_ids for edge in edges
        ),
        "payload_edge_count_matches_rows": isinstance(payload.get("edges"), list)
        and len(payload["edges"]) == len(edges),
        "payload_node_count_matches_rows": isinstance(payload.get("nodes"), list)
        and len(payload["nodes"]) == len(nodes),
        "source_path_index_matches_rows": all(
            store.node_ids_by_source_path(path) == sorted(set(values))
            for path, values in source_path_index.items()
        ),
        "tier_group_index_matches_rows": all(
            store.node_ids_by_tier_group(tier_group) == sorted(set(values))
            for tier_group, values in tier_group_index.items()
        ),
        "tier_index_matches_rows": all(
            store.node_ids_by_tier(tier) == sorted(set(values)) for tier, values in tier_index.items()
        ),
    }


def _node_index(nodes: list[dict[str, Any]], *, key: str, default: str) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for node in nodes:
        index.setdefault(str(node.get(key, default)), []).append(_candidate_id(node))
    return index


def _candidate_id(node: dict[str, Any]) -> str:
    value = node.get("candidate_id")
    if not isinstance(value, str) or not value:
        raise ValueError("atlas_lmdb_write_node_missing_candidate_id")
    return value


def _edge_source(edge: dict[str, Any]) -> str:
    for key in ("source", "src", "source_candidate_id", "from", "source_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("atlas_lmdb_write_edge_source_missing")


def _edge_target(edge: dict[str, Any]) -> str:
    for key in ("target", "tgt", "target_candidate_id", "to", "target_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("atlas_lmdb_write_edge_target_missing")


def _edge_type(edge: dict[str, Any]) -> str:
    value = edge.get("edge_type")
    if not isinstance(value, str) or not value:
        raise ValueError("atlas_lmdb_write_edge_type_missing")
    return value


def _normalize_edge(edge: dict[str, Any], *, phase: str) -> dict[str, Any]:
    source = _edge_source(edge)
    target = _edge_target(edge)
    edge_type = _edge_type(edge)
    normalized = dict(edge)
    normalized["source"] = source
    normalized["src"] = source
    normalized["target"] = target
    normalized["tgt"] = target
    normalized["edge_type"] = edge_type
    normalized["edge_id"] = deterministic_edge_id(source, edge_type, target)
    normalized.setdefault("annotation_method", "atlas_lmdb_safe_writer")
    normalized.setdefault("annotation_phase", _phase_token(phase))
    normalized.setdefault("candidate_status", "applied_to_unified_lmdb_via_safe_writer")
    return normalized


def _edge(
    *,
    source: str,
    edge_type: str,
    target: str,
    phase: str,
    candidate_status: str,
) -> dict[str, Any]:
    return _normalize_edge(
        {
            "annotation_method": "phase_file_lmdb_registration",
            "candidate_status": candidate_status,
            "edge_type": edge_type,
            "source": source,
            "target": target,
        },
        phase=phase,
    )


def _support_node(
    candidate_id: str,
    *,
    node_kind: str,
    graph_projection: str,
    label: str,
    phase: str,
) -> dict[str, Any]:
    return {
        "annotation_method": "atlas_lmdb_safe_writer_phase_support_registration",
        "annotation_phase": _phase_token(phase),
        "candidate_id": candidate_id,
        "candidate_status": "fix59b_support_endpoint_registered",
        "graph_delta": "support_only",
        "graph_projection": graph_projection,
        "label": label,
        "node_kind": node_kind,
        "source_path": "",
        "tier": "support_candidate",
    }


def _file_node_from_registration(registration: AtlasPhaseFileRegistration, *, phase: str) -> dict[str, Any]:
    repo_path = Path(registration.path).as_posix()
    return {
        "annotation_method": "phase_file_lmdb_registration",
        "annotation_phase": _phase_token(phase),
        "candidate_id": repo_file_ref_id(repo_path),
        "candidate_status": "fix59b_phase_file_registered",
        "graph_delta": registration.graph_delta,
        "graph_projection": registration.graph_projection,
        "label": repo_path,
        "node_kind": registration.node_kind,
        "source_path": repo_path,
        "tier": "support_candidate",
    }


def _append_if_missing(
    nodes_to_add: list[dict[str, Any]],
    current_node_ids: set[str],
    node: dict[str, Any],
) -> None:
    node_id = _candidate_id(node)
    if node_id in current_node_ids:
        return
    nodes_to_add.append(node)
    current_node_ids.add(node_id)


def _coerce_phase_file_registration(
    item: AtlasPhaseFileRegistration | dict[str, Any] | str | Path,
) -> AtlasPhaseFileRegistration:
    if isinstance(item, AtlasPhaseFileRegistration):
        return item
    if isinstance(item, (str, Path)):
        return AtlasPhaseFileRegistration(path=item, node_kind="phase_artifact", graph_projection="support_candidate_graph")
    edges = item.get("required_edges", ())
    return AtlasPhaseFileRegistration(
        path=item["path"],
        node_kind=item["node_kind"],
        graph_projection=item["graph_projection"],
        graph_delta=item.get("graph_delta", "support_only"),
        required_edges=tuple(tuple(edge) for edge in edges),
        skip_carries_forward=bool(item.get("skip_carries_forward", False)),
    )


def _phase_slug(phase: str) -> str:
    return phase.lower().replace("-", "_")


def _phase_token(phase: str) -> str:
    return f"phase_{_phase_slug(phase)}" if phase else "phase_unspecified"


def _tier_group(node: dict[str, Any]) -> str:
    tier = str(node.get("tier", "unknown")).lower()
    canonicality_tier = str(node.get("canonicality_tier", "")).lower()
    node_kind = str(node.get("node_kind", "")).lower()
    sensitivity = str(node.get("sensitivity", "")).lower()
    inclusion_status = str(node.get("inclusion_status", "")).lower()
    if tier == "genesis_core" or "genesis_core" in canonicality_tier:
        return "canonical"
    if (
        "private" in tier
        or "excluded" in tier
        or "private" in sensitivity
        or "public_rc_exclude" in sensitivity
        or "excluded" in inclusion_status
    ):
        return "private"
    return "support"


def _duplicates(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def _node_summary(nodes: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "candidate_id": _candidate_id(node),
            "graph_projection": str(node.get("graph_projection", "")),
            "node_kind": str(node.get("node_kind", "")),
            "source_path": str(node.get("source_path", "")),
        }
        for node in nodes
    ]


def _edge_summary(edges: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "edge_id": str(edge.get("edge_id", "")),
            "edge_type": _edge_type(edge),
            "source": _edge_source(edge),
            "target": _edge_target(edge),
        }
        for edge in edges
    ]


__all__ = [
    "AtlasLmdbSafeWriter",
    "AtlasLmdbWritePlan",
    "AtlasPhaseFileRegistration",
    "GENESIS_ATLAS_LMDB_WRITER_VERSION",
    "deterministic_edge_id",
    "repo_file_ref_id",
    "write_json_atomic",
]
