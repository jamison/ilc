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
import re
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
_KNOWN_EDGE_TYPES: frozenset[str] = frozenset(
    {
        "ATTESTATION",
        "CARRIES_FORWARD",
        "CLASSIFIED_BY",
        "CONSTRAINS",
        "CONTAINS_FILE",
        "CONTAINS_GROUP",
        "CONTAINS_PARTITION",
        "COVERS_COMMAND_CONTRACT",
        "COVERS_SYMBOL",
        "DERIVED_FROM",
        "EVIDENCES",
        "EXPECTS_RESOLUTION",
        "GOVERNS",
        "IMPLEMENTS",
        "IMPLEMENTS_MODULE",
        "IMPORTS_MODULE",
        "NEGATIVE_ASSERTS",
        "OPENED_FOR",
        "PRELOCK_FOR",
        "PRIMITIVE_INVOCATION",
        "PROPOSES_CHANGE_TO",
        "PROVENANCE",
        "RATIFICATION_EVIDENCE_FOR",
        "REFERENCES",
        "REFERENCES_AUTHORITY",
        "REGRESSES",
        "REQUIRES_PROFILE",
        "RESOLVED_BY",
        "SAME_AUTHORITY",
        "SAME_SOURCE",
        "SIM_EVIDENCE",
        "SOURCE_TREE_MEMBER",
        "SUPERSEDED_BY",
        "TESTS",
        "TESTS_STORAGE",
        "USES",
    }
)
_AUTHORITY_ID_PREFIXES = ("cdl:", "adr:", "artifact:genesis", "artifact:full_repo_genesis")
_AUTHORITY_NODE_KINDS = {
    "adr_node",
    "authority_map",
    "cdl_node",
    "genesis_artifact_node",
    "genesis_intent_node",
    "genesis_root_node",
    "invariant_node",
    "phase_node",
}
_RUNTIME_REPO_PREFIXES = ("repo:", "target:", "sim:")
_SOURCE_TREE_GROUP_PREFIXES = ("repo:group:", "repo:partition:")
_CLASSIFIED_BY_FANIN_CAP = 100


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
            "duplicate_semantic_edge_extra_row_count": _duplicate_semantic_edge_extra_row_count(edges),
            "duplicate_semantic_edge_group_count": _duplicate_semantic_edge_group_count(edges),
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
        receipt = self.apply_plan(plan)
        identity_updates: dict[str, dict[str, Any]] = {}
        desired_same_source_targets: dict[str, str] = {}
        for registration in registrations:
            repo_path = Path(registration.path).as_posix()
            file_ref_id = repo_file_ref_id(repo_path)
            identity_fields = _file_identity_fields(repo_path)
            existing = self.store.get_node(file_ref_id)
            if (
                existing
                and existing.get("source_identity_status") == "content_addressed_by_fix64"
                and identity_fields.get("source_identity_status") == "content_addressed_at_registration"
            ):
                identity_fields["source_identity_status"] = "content_addressed_by_fix64"
            identity_updates[file_ref_id] = identity_fields
            repo_file_node = _repo_file_node_from_registration(registration, phase=phase)
            if repo_file_node is not None:
                desired_same_source_targets[file_ref_id] = _candidate_id(repo_file_node)
        receipt["file_identity_update_count"] = len(identity_updates)
        if not dry_run and identity_updates:
            receipt["file_identity_update_receipt"] = self.update_node_fields(
                identity_updates,
                phase=f"{phase}:phase_file_identity",
                dry_run=False,
            )
        if not dry_run and desired_same_source_targets:
            stale_same_source_semantics: list[tuple[str, str, str]] = []
            for edge in self.store.iter_edges():
                if _edge_type(edge) != "SAME_SOURCE":
                    continue
                source = _edge_source(edge)
                target = _edge_target(edge)
                desired_target = desired_same_source_targets.get(source)
                if desired_target is not None and target != desired_target:
                    stale_same_source_semantics.append((source, "SAME_SOURCE", target))
            receipt["stale_same_source_removed_count"] = len(stale_same_source_semantics)
            if stale_same_source_semantics:
                receipt["stale_same_source_removal_receipt"] = self.remove_edges_by_semantic(
                    stale_same_source_semantics,
                    phase=f"{phase}:phase_file_same_source_refresh",
                    dry_run=False,
                    metadata={"operation": "phase_file_same_source_refresh"},
                )
        return receipt

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
        edge_semantics_to_add: set[tuple[str, str, str]] = set()
        phase_node_id = f"phase:{_phase_slug(phase)}"

        def append_edge_if_missing(edge: dict[str, Any]) -> None:
            semantic = (_edge_source(edge), _edge_type(edge), _edge_target(edge))
            if semantic in edge_semantics_to_add:
                return
            edge_semantics_to_add.add(semantic)
            edges_to_add.append(edge)

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
            repo_file_node = _repo_file_node_from_registration(registration, phase=phase)
            if repo_file_node is not None:
                _append_if_missing(nodes_to_add, current_node_ids, repo_file_node)
                append_edge_if_missing(
                    _edge(
                        source=file_id,
                        edge_type="SAME_SOURCE",
                        target=_candidate_id(repo_file_node),
                        phase=phase,
                        candidate_status="phase_file_registration_content_addressed_same_source",
                    )
                )
            # Routine phase-file registration must not create a high-fan-in
            # public-path classification hub. Public-path tagging history is
            # tracked by Fix67's migration receipt instead of canonical topology.
            if not registration.skip_carries_forward:
                append_edge_if_missing(
                    _edge(
                        source=file_id,
                        edge_type="CARRIES_FORWARD",
                        target=phase_node_id,
                        phase=phase,
                        candidate_status="fix59b_phase_file_registration_edge",
                    )
                )
            for edge_type, target in registration.required_edges:
                append_edge_if_missing(
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

    def dedupe_semantic_edges(
        self,
        *,
        phase: str,
        dry_run: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Remove duplicate edge rows that assert the same semantic triple.

        The dedupe key is ``(source, edge_type, target)``. The retained row is
        selected deterministically by metadata richness, confidence, authority
        status hints, and finally edge_id. Removed rows are preserved in the
        receipt so provenance loss remains auditable.
        """

        current_nodes = self.store.iter_nodes()
        current_edges = self.store.iter_edges()
        current_payload = self.store.get_graph_payload() or {}
        edge_groups: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
        for edge in current_edges:
            semantic = (_edge_source(edge), _edge_type(edge), _edge_target(edge))
            edge_groups.setdefault(semantic, []).append(dict(edge))

        retained_edges: list[dict[str, Any]] = []
        entries: list[dict[str, Any]] = []
        duplicate_groups = {
            semantic: edges
            for semantic, edges in edge_groups.items()
            if len(edges) > 1
        }
        for semantic, edges in sorted(edge_groups.items()):
            if len(edges) == 1:
                retained_edges.append(edges[0])
                continue
            ordered = sorted(edges, key=_semantic_dedupe_sort_key)
            canonical = ordered[0]
            removed = ordered[1:]
            retained_edges.append(canonical)
            source, edge_type, target = semantic
            entries.append(
                {
                    "canonical_edge": canonical,
                    "canonical_edge_id": str(canonical.get("edge_id", "")),
                    "edge_type": edge_type,
                    "removed_edge_ids": [str(edge.get("edge_id", "")) for edge in removed],
                    "removed_edges": removed,
                    "source": source,
                    "target": target,
                }
            )

        retained_edges = sorted(
            retained_edges,
            key=lambda edge: (
                str(edge.get("edge_id", "")),
                _edge_source(edge),
                _edge_type(edge),
                _edge_target(edge),
            ),
        )
        payload = dict(current_payload)
        payload["nodes"] = current_nodes
        payload["edges"] = retained_edges
        payload["safe_writer"] = {
            "last_phase": phase,
            "version": GENESIS_ATLAS_LMDB_WRITER_VERSION,
        }
        receipt: dict[str, Any] = {
            "dry_run": dry_run,
            "duplicate_groups": len(duplicate_groups),
            "entries": entries,
            "metadata": dict(metadata or {}),
            "mutated": False,
            "phase": phase,
            "post_edge_rows": len(retained_edges),
            "pre_edge_rows": len(current_edges),
            "removed_duplicate_rows": len(current_edges) - len(retained_edges),
            "semantic_triples": len(edge_groups),
            "version": GENESIS_ATLAS_LMDB_WRITER_VERSION,
        }
        if dry_run:
            return receipt
        if entries:
            self.store.replace_edges(retained_edges)
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
        receipt["mutated"] = bool(entries)
        receipt["post_invariants"] = post_invariants
        receipt["status"] = "PASS" if all(post_invariants.values()) else "FAIL"
        if phase:
            self.store.put_meta(f"safe_writer_semantic_edge_dedupe:{phase}", receipt)
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

    def remove_edges_by_semantic(
        self,
        edge_semantics: Iterable[tuple[str, str, str]],
        *,
        phase: str,
        dry_run: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Remove exact edge semantics through a validation-first rewrite."""

        semantics = {
            (str(source), str(edge_type), str(target))
            for source, edge_type, target in edge_semantics
        }
        current_nodes = self.store.iter_nodes()
        current_edges = self.store.iter_edges()
        current_payload = self.store.get_graph_payload() or {}
        retained_edges: list[dict[str, Any]] = []
        removed_edges: list[dict[str, Any]] = []
        for edge in current_edges:
            semantic = (_edge_source(edge), _edge_type(edge), _edge_target(edge))
            if semantic in semantics:
                removed_edges.append(dict(edge))
            else:
                retained_edges.append(edge)
        removed_semantics = {
            (_edge_source(edge), _edge_type(edge), _edge_target(edge))
            for edge in removed_edges
        }
        missing_semantics = sorted(semantics - removed_semantics)
        payload = dict(current_payload)
        payload["nodes"] = current_nodes
        payload["edges"] = retained_edges
        payload["safe_writer"] = {
            "last_phase": phase,
            "version": GENESIS_ATLAS_LMDB_WRITER_VERSION,
        }
        receipt: dict[str, Any] = {
            "dry_run": dry_run,
            "metadata": dict(metadata or {}),
            "missing_semantic_count": len(missing_semantics),
            "missing_semantics": [
                {"source": source, "edge_type": edge_type, "target": target}
                for source, edge_type, target in missing_semantics
            ],
            "mutated": False,
            "phase": phase,
            "pre_counts": {"edges": len(current_edges), "nodes": len(current_nodes)},
            "removed_edge_count": len(removed_edges),
            "removed_edges": removed_edges[:50],
            "version": GENESIS_ATLAS_LMDB_WRITER_VERSION,
        }
        if dry_run:
            receipt["projected_counts"] = {
                "edges": len(retained_edges),
                "nodes": len(current_nodes),
            }
            return receipt
        if removed_edges:
            self.store.replace_edges(retained_edges)
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
        receipt["mutated"] = bool(removed_edges)
        receipt["post_counts"] = {"edges": len(post_edges), "nodes": len(post_nodes)}
        receipt["post_invariants"] = post_invariants
        receipt["status"] = "PASS" if all(post_invariants.values()) else "FAIL"
        if phase:
            self.store.put_meta(f"safe_writer_edge_removals:{phase}", receipt)
            self.store.put_meta("last_safe_writer_receipt", receipt)
        return receipt

    def remove_nodes_by_id(
        self,
        node_ids: Iterable[str],
        *,
        phase: str,
        dry_run: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Remove exact nodes through a validation-first full node-store rewrite.

        Node removal is intentionally stricter than field updates. Any requested
        node with incident edges is rejected, because deleting it would create
        dangling graph topology. Callers must remove or rewrite edges first.
        """

        requested = {str(node_id) for node_id in node_ids if str(node_id)}
        current_nodes = self.store.iter_nodes()
        current_edges = self.store.iter_edges()
        current_payload = self.store.get_graph_payload() or {}
        node_by_id = {_candidate_id(node): dict(node) for node in current_nodes}
        incident_counts: dict[str, int] = {node_id: 0 for node_id in requested}
        for edge in current_edges:
            source = _edge_source(edge)
            target = _edge_target(edge)
            if source in incident_counts:
                incident_counts[source] += 1
            if target in incident_counts:
                incident_counts[target] += 1

        missing_node_ids = sorted(requested - set(node_by_id))
        rejected_nodes = [
            {
                "candidate_id": node_id,
                "incident_edge_count": incident_counts[node_id],
                "reason": "incident_edges_remain",
            }
            for node_id in sorted(requested & set(node_by_id))
            if incident_counts[node_id] > 0
        ]
        removable_ids = sorted(
            node_id
            for node_id in requested & set(node_by_id)
            if incident_counts[node_id] == 0
        )
        retained_nodes = [
            node
            for node in current_nodes
            if _candidate_id(node) not in set(removable_ids)
        ]
        payload = dict(current_payload)
        payload["nodes"] = retained_nodes
        payload["edges"] = current_edges
        payload["safe_writer"] = {
            "last_phase": phase,
            "version": GENESIS_ATLAS_LMDB_WRITER_VERSION,
        }
        receipt: dict[str, Any] = {
            "dry_run": dry_run,
            "metadata": dict(metadata or {}),
            "missing_node_count": len(missing_node_ids),
            "missing_node_ids": missing_node_ids,
            "mutated": False,
            "phase": phase,
            "pre_counts": {"edges": len(current_edges), "nodes": len(current_nodes)},
            "rejected_node_count": len(rejected_nodes),
            "rejected_nodes": rejected_nodes,
            "removed_node_count": len(removable_ids),
            "removed_node_ids": removable_ids,
            "version": GENESIS_ATLAS_LMDB_WRITER_VERSION,
        }
        if dry_run:
            receipt["projected_counts"] = {
                "edges": len(current_edges),
                "nodes": len(retained_nodes),
            }
            return receipt

        if removable_ids:
            self.store.replace_nodes(retained_nodes)
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
        receipt["mutated"] = bool(removable_ids)
        receipt["post_counts"] = {"edges": len(post_edges), "nodes": len(post_nodes)}
        receipt["post_invariants"] = post_invariants
        receipt["status"] = "PASS" if all(post_invariants.values()) else "FAIL"
        if phase:
            self.store.put_meta(f"safe_writer_node_removals:{phase}", receipt)
            self.store.put_meta("last_safe_writer_receipt", receipt)
        return receipt


def deterministic_edge_id(source: str, edge_type: str, target: str) -> str:
    digest = hashlib.sha256(f"{source}|{edge_type}|{target}".encode("utf-8")).hexdigest()[:16]
    return f"edge:{digest}"


def _duplicate_semantic_edge_group_count(edges: Sequence[dict[str, Any]]) -> int:
    counts: dict[tuple[str, str, str], int] = {}
    for edge in edges:
        semantic = (_edge_source(edge), _edge_type(edge), _edge_target(edge))
        counts[semantic] = counts.get(semantic, 0) + 1
    return sum(1 for count in counts.values() if count > 1)


def _duplicate_semantic_edge_extra_row_count(edges: Sequence[dict[str, Any]]) -> int:
    counts: dict[tuple[str, str, str], int] = {}
    for edge in edges:
        semantic = (_edge_source(edge), _edge_type(edge), _edge_target(edge))
        counts[semantic] = counts.get(semantic, 0) + 1
    return sum(count - 1 for count in counts.values() if count > 1)


def _semantic_dedupe_sort_key(edge: dict[str, Any]) -> tuple[int, float, int, str]:
    confidence = _numeric_confidence(edge)
    confidence_key = -confidence if confidence is not None else float("inf")
    return (
        -_metadata_richness(edge),
        confidence_key,
        -_authority_status_score(edge),
        str(edge.get("edge_id", "")),
    )


def _metadata_richness(edge: dict[str, Any]) -> int:
    return sum(1 for value in edge.values() if not _empty_metadata_value(value))


def _empty_metadata_value(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {} or value == ()


def _numeric_confidence(edge: dict[str, Any]) -> float | None:
    value = edge.get("confidence")
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _authority_status_score(edge: dict[str, Any]) -> int:
    status_text = " ".join(
        str(edge.get(key, ""))
        for key in (
            "authority_status",
            "candidate_status",
            "canonicality_tier",
            "promotion_status",
            "signature_status",
            "status",
            "tier",
        )
    ).lower()
    return int(any(token in status_text for token in ("signed", "canonical", "ratified")))


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
        _validate_edge_semantics(
            edge=normalized,
            node_by_id=node_by_id,
            all_edges=[*current_edges, *accepted_edges],
            plan_metadata=plan.metadata,
        )
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


def _validate_edge_semantics(
    *,
    edge: dict[str, Any],
    node_by_id: Mapping[str, dict[str, Any]],
    all_edges: Sequence[dict[str, Any]],
    plan_metadata: Mapping[str, Any],
) -> None:
    edge_type = _edge_type(edge)
    source = _edge_source(edge)
    target = _edge_target(edge)
    source_node = node_by_id.get(source)
    target_node = node_by_id.get(target)
    override = plan_metadata.get("allowlist_override") is True
    migration_phase = str(plan_metadata.get("migration_phase", ""))
    if override and not migration_phase:
        raise ValueError("allowlist_override_requires_migration_phase_token")
    if edge_type not in _KNOWN_EDGE_TYPES and not override:
        raise ValueError(f"unknown_edge_type_rejected:{edge_type}")
    if override:
        return

    if edge_type == "GOVERNS":
        if not _is_authority_like(source, source_node):
            raise ValueError(f"governs_source_not_authority_like:{source}")
    elif edge_type == "SAME_SOURCE":
        if not (_is_file_ref(source) and _is_repo_file(target)):
            raise ValueError(f"same_source_requires_file_ref_to_repo_file:{source}->{target}")
    elif edge_type == "REFERENCES_AUTHORITY":
        if _is_runtime_or_repo(target):
            raise ValueError(f"references_authority_target_must_not_be_repo_or_runtime:{target}")
    elif edge_type == "SOURCE_TREE_MEMBER":
        if not (
            (_is_source_tree_container(source) or _is_repo_file(source) or _is_file_ref(source))
            and (_is_source_tree_container(target) or _is_repo_file(target) or _is_file_ref(target))
        ):
            raise ValueError(f"source_tree_member_requires_source_tree_endpoints:{source}->{target}")
    elif edge_type == "CLASSIFIED_BY":
        existing_fanin = sum(
            1
            for existing in all_edges
            if _edge_type(existing) == "CLASSIFIED_BY" and _edge_target(existing) == target
        )
        allowlisted_targets = {
            str(candidate_id)
            for candidate_id in plan_metadata.get("classified_by_fanin_allowlist", [])
        }
        if existing_fanin >= _CLASSIFIED_BY_FANIN_CAP and target not in allowlisted_targets:
            raise ValueError(f"classified_by_fanin_cap_exceeded:{target}:{existing_fanin}")
    if edge_type == "GOVERNS" and target_node is None:
        raise ValueError(f"governs_target_missing:{target}")


def _is_authority_like(candidate_id: str, node_record: Mapping[str, Any] | None) -> bool:
    if any(candidate_id.startswith(prefix) for prefix in _AUTHORITY_ID_PREFIXES):
        return True
    if node_record and str(node_record.get("node_kind", "")) in _AUTHORITY_NODE_KINDS:
        return True
    return False


def _is_runtime_or_repo(candidate_id: str) -> bool:
    return any(candidate_id.startswith(prefix) for prefix in _RUNTIME_REPO_PREFIXES)


def _is_file_ref(candidate_id: str) -> bool:
    return candidate_id.startswith("repo:file_ref:")


def _is_repo_file(candidate_id: str) -> bool:
    return candidate_id.startswith("repo:file:")


def _is_source_tree_container(candidate_id: str) -> bool:
    return any(candidate_id.startswith(prefix) for prefix in _SOURCE_TREE_GROUP_PREFIXES)


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
    node = {
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
    node.update(_file_identity_fields(repo_path))
    return node


def _repo_file_node_from_registration(
    registration: AtlasPhaseFileRegistration,
    *,
    phase: str,
) -> dict[str, Any] | None:
    repo_path = Path(registration.path).as_posix()
    path = Path(repo_path)
    if not path.is_file():
        return None
    source_sha256 = _file_sha256(path)
    return {
        "annotation_method": "phase_file_lmdb_registration_content_addressing",
        "annotation_phase": _phase_token(phase),
        "candidate_id": _repo_file_node_id(repo_path, source_sha256),
        "candidate_status": "phase_file_registration_content_addressed_repo_file",
        "creator_agent_id": "genesis_agent:01",
        "genesis_attested": False,
        "graph_delta": registration.graph_delta,
        "graph_projection": registration.graph_projection,
        "label": repo_path,
        "node_kind": _repo_file_node_kind(repo_path),
        "size_bytes": path.stat().st_size,
        "source_path": repo_path,
        "source_sha256": source_sha256,
        "source_identity_status": "content_addressed_at_registration",
        "tier": "support_candidate",
    }


def _repo_file_node_id(repo_path: str, source_sha256: str) -> str:
    return f"repo:file:{source_sha256[:16]}:{_path_slug(repo_path)}"


def _repo_file_node_kind(repo_path: str) -> str:
    path = Path(repo_path)
    if repo_path.startswith("ilc_core/") and path.suffix == ".py":
        return "runtime_source_file_node"
    if repo_path.startswith("tests/") and path.suffix == ".py":
        return "test_evidence_node"
    if repo_path.startswith("tools/") and path.suffix == ".py":
        return "tooling_source_file_node"
    if repo_path.startswith("docs/adr/") and path.suffix == ".md":
        return "adr_document_node"
    if repo_path.startswith("docs/") and path.suffix == ".md":
        return "spec_document_node"
    if repo_path.startswith("docs/") and path.suffix == ".json":
        return "spec_data_node"
    return "repo_material_node"


def _path_slug(repo_path: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", repo_path.lower()).strip("_")


def _file_identity_fields(repo_path: str) -> dict[str, Any]:
    path = Path(repo_path)
    if path.is_file():
        return {
            "source_path": repo_path,
            "source_sha256": _file_sha256(path),
            "size_bytes": path.stat().st_size,
            "source_identity_status": "content_addressed_at_registration",
        }
    return {
        "source_path": repo_path,
        "source_identity_status": "source_path_not_found_at_registration",
    }


def _file_sha256(path: Path, chunk_size: int = 65536) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


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
