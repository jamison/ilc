#!/usr/bin/env python3
"""Materialize Fix59 missing-target endpoint debt into the unified Atlas LMDB.

PUBLIC_RC_EXCLUDE: fix59_missing_target_materialization_research_only
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Atlas LMDB research materialization pass; not Genesis signing, public graph upload, canonical mutation, runtime activation, or public RC publication.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import (  # noqa: E402
    GenesisAtlasCandidateStore,
)
from ilc_core.storage.lmdb_public_runtime import DEFAULT_MAP_SIZE_BYTES  # noqa: E402
from tools.evaluators.sim_genesis_atlas_fix56_projection_aware_fiedler_rebaseline import (  # noqa: E402
    _candidate_id,
    _edge_source,
    _edge_target,
    _edge_type,
)


PHASE = "1545p-Fix59"
ANNOTATION_PHASE = "phase_1545p_fix59"
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
FIX57_REPORT = REPO_ROOT / "out/genesis_atlas_fix57_manual_bridge_edge_application_report_v0.1.json"
FIX58_REPORT = REPO_ROOT / "out/genesis_atlas_fix58_residual_queue_application_report_v0.1.json"
REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix59_missing_target_materialization_report_v0.1.json"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"

LOW_AUTHORITY_STUB_PREFIXES = frozenset({"target", "invariant", "phase", "sim", "window", "atlas"})
HIGH_AUTHORITY_PREFIXES = frozenset(
    {"cdl", "adr", "policy", "artifact", "truth_primitive", "genesis_agent", "ceremony"}
)
CDL_DISPATCH: dict[str, tuple[str, str | None, str]] = {
    "cdl:030": ("remap", "cdl:030_ecu_price_clamp_runtime", "pre-resolved CDL dispatch table"),
    "cdl:039": ("remap", "cdl:039_topology_shuffling_authorization", "ratified CDL preferred over opening doc"),
    "cdl:050": ("remap", "cdl:050_treasury_ecu_governor_lane", "pre-resolved CDL dispatch table"),
    "cdl:051": ("remap", "cdl:051_epoch_state_quorum", "pre-resolved CDL dispatch table"),
    "cdl:052": ("remap", "cdl:052_epistemic_evaluation_contract", "pre-resolved CDL dispatch table"),
    "cdl:053": (
        "remap",
        "cdl:053_werner_local_productive_credit_future_vehicle",
        "ratified CDL preferred over shorter alias",
    ),
    "cdl:084": (
        "remap",
        "cdl:084_provenance_chain_attribution",
        "full-label provenance chain attribution CDL preferred",
    ),
    "cdl:085_prelock_spec": ("defer", None, "no canonical LMDB equivalent found"),
    "cdl:093": ("remap", "cdl:093_maintenance_lottery", "pre-resolved CDL dispatch table"),
    "cdl:020": ("defer", None, "no canonical LMDB equivalent found"),
    "cdl:021": ("defer", None, "no canonical LMDB equivalent found"),
    "cdl:024": ("defer", None, "no canonical LMDB equivalent found"),
    "cdl:032": ("defer", None, "no canonical LMDB equivalent found"),
    "cdl:033": ("defer", None, "no canonical LMDB equivalent found"),
    "cdl:082": ("defer", None, "no canonical LMDB equivalent found"),
}


def _canonical_text(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def _atomic_write_json(path: Path, payload: Any) -> None:
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
            handle.write(_canonical_text(payload))
        os.replace(tmp_path, path)
        path.chmod(0o644)
    except Exception:
        try:
            tmp_path.unlink()
        finally:
            raise


def _edge_id(source: str, edge_type: str, target: str) -> str:
    digest = hashlib.sha256(f"{source}|{edge_type}|{target}".encode("utf-8")).hexdigest()[:16]
    return f"edge:{digest}"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"fix59_json_object_required:{path}")
    return payload


def _prefix(node_id: str) -> str:
    return node_id.split(":", 1)[0] if ":" in node_id else "other"


def _extract_fix57_rejections() -> list[dict[str, Any]]:
    report = _load_json(FIX57_REPORT)
    edge_application = report.get("edge_application")
    if not isinstance(edge_application, dict):
        raise ValueError("fix59_fix57_edge_application_missing")
    rejections = edge_application.get("rejections")
    if not isinstance(rejections, list):
        raise ValueError("fix59_fix57_rejections_missing")
    rows: list[dict[str, Any]] = []
    for row in rejections:
        if not isinstance(row, dict):
            raise ValueError("fix59_fix57_rejection_object_required")
        if row.get("rejection_reason") != "fix57_target_node_missing":
            continue
        rows.append(
            {
                "edge_id": row.get("edge_id", ""),
                "edge_type": row.get("edge_type", ""),
                "reason": row.get("rejection_reason", ""),
                "source": row.get("source", ""),
                "target": row.get("target", ""),
                "source_report": str(FIX57_REPORT.relative_to(REPO_ROOT)),
            }
        )
    if len(rows) != 478:
        raise ValueError(f"fix59_fix57_missing_target_count_mismatch:{len(rows)}")
    return rows


def _extract_fix58_rejections() -> list[dict[str, Any]]:
    report = _load_json(FIX58_REPORT)
    rejections = report.get("missing_target_rejections")
    if not isinstance(rejections, list):
        raise ValueError("fix59_fix58_missing_target_rejections_missing")
    rows: list[dict[str, Any]] = []
    for row in rejections:
        if not isinstance(row, dict):
            raise ValueError("fix59_fix58_rejection_object_required")
        rows.append(
            {
                "edge_id": row.get("edge_id", ""),
                "edge_type": row.get("edge_type", ""),
                "reason": row.get("reason", ""),
                "source": row.get("source", ""),
                "target": row.get("target", ""),
                "source_report": str(FIX58_REPORT.relative_to(REPO_ROOT)),
            }
        )
    if len(rows) != 7:
        raise ValueError(f"fix59_fix58_missing_target_count_mismatch:{len(rows)}")
    return rows


def _validate_rejection(row: dict[str, Any]) -> None:
    for key in ("source", "target", "edge_type"):
        value = row.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"fix59_rejection_{key}_missing")
    if row["edge_type"] == "GOVERNS":
        raise ValueError("fix59_governs_edge_forbidden")


def _existing_edge_indexes(edges: list[dict[str, Any]]) -> tuple[set[str], set[tuple[str, str, str]]]:
    edge_ids: set[str] = set()
    semantics: set[tuple[str, str, str]] = set()
    for edge in edges:
        source = _edge_source(edge)
        target = _edge_target(edge)
        edge_type = _edge_type(edge)
        if source and target and edge_type:
            semantics.add((source, edge_type, target))
            edge_ids.add(_edge_id(source, edge_type, target))
        explicit = edge.get("edge_id")
        if isinstance(explicit, str) and explicit:
            edge_ids.add(explicit)
    return edge_ids, semantics


def _graph_projection_for_stub(prefix: str) -> str:
    if prefix in HIGH_AUTHORITY_PREFIXES:
        return "genesis_core_star_map"
    return "support_candidate_graph"


def _node_kind_for_stub(prefix: str) -> str:
    if prefix in HIGH_AUTHORITY_PREFIXES:
        return "authority_stub"
    return "repo_material_node"


def _build_stub_node(target_id: str, *, disposition: str, reason: str) -> dict[str, Any]:
    prefix = _prefix(target_id)
    node = {
        "annotation_method": "stub_materialized",
        "annotation_phase": ANNOTATION_PHASE,
        "candidate_id": target_id,
        "candidate_status": f"fix59_{disposition}",
        "graph_delta": "support_only",
        "graph_projection": _graph_projection_for_stub(prefix),
        "node_kind": _node_kind_for_stub(prefix),
        "source_path": "",
        "stub_reason": reason,
        "tier": "support_candidate",
    }
    if prefix in HIGH_AUTHORITY_PREFIXES:
        node["canonical_materialize_evidence"] = {
            "basis": reason,
            "phase": ANNOTATION_PHASE,
            "source": "Fix59 high-authority materialization rule",
        }
    return node


def _determine_disposition(target_id: str, node_ids: set[str]) -> tuple[str, str | None, str]:
    prefix = _prefix(target_id)
    if prefix == "cdl":
        if target_id in CDL_DISPATCH:
            return CDL_DISPATCH[target_id]
        suffix = target_id.split(":", 1)[1]
        key = suffix.split("_", 1)[0]
        matches = sorted(candidate_id for candidate_id in node_ids if candidate_id.startswith(f"cdl:{key}_"))
        if len(matches) == 1:
            return ("remap", matches[0], "single canonical CDL prefix match")
        return ("defer", None, f"unexpected CDL target without unique dispatch match:{len(matches)}")
    if prefix in LOW_AUTHORITY_STUB_PREFIXES:
        return ("stub", None, "low-authority missing endpoint materialized as support stub")
    if target_id in node_ids:
        return ("remap", target_id, "exact LMDB node already exists")
    if prefix in HIGH_AUTHORITY_PREFIXES:
        return ("defer", None, "high-authority prefix requires direct evidence before materialization")
    return ("defer", None, "no safe Fix59 materialization rule for prefix")


def _build_edge(row: dict[str, Any], target: str, *, disposition: str) -> dict[str, Any]:
    source = str(row["source"])
    edge_type = str(row["edge_type"])
    edge_id = _edge_id(source, edge_type, target)
    return {
        "annotation_method": "stub_materialization_replayed" if disposition == "stub" else "missing_target_remapped",
        "annotation_phase": ANNOTATION_PHASE,
        "candidate_status": f"applied_to_unified_lmdb_fix59_{disposition}",
        "edge_id": edge_id,
        "edge_type": edge_type,
        "original_rejection_edge_id": str(row.get("edge_id", "")),
        "original_target": str(row["target"]),
        "resolution_disposition": disposition,
        "source": source,
        "source_report": str(row.get("source_report", "")),
        "src": source,
        "target": target,
        "tgt": target,
    }


def _report_edge(edge: dict[str, Any]) -> dict[str, Any]:
    return {
        "edge_id": edge["edge_id"],
        "edge_type": edge["edge_type"],
        "original_target": edge["original_target"],
        "resolution_disposition": edge["resolution_disposition"],
        "source": edge["source"],
        "target": edge["target"],
    }


def _build_missing_target_map(
    rows: list[dict[str, Any]],
    *,
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    for row in rows:
        _validate_rejection(row)
    missing_by_target: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        missing_by_target[str(row["target"])].append(row)
    node_ids = {_candidate_id(node) for node in nodes}
    lmdb_survivors: list[dict[str, Any]] = []
    seen_survivor_semantics = {
        (str(row["source"]), str(row["edge_type"]), str(row["target"])) for row in rows
    }
    for edge in edges:
        source = _edge_source(edge)
        target = _edge_target(edge)
        edge_type = _edge_type(edge)
        if target in node_ids:
            continue
        survivor = {
            "edge_id": str(edge.get("edge_id", "")),
            "edge_type": edge_type,
            "reason": "lmdb_sanity_scan_target_missing",
            "source": source,
            "source_report": "lmdb_sanity_scan",
            "target": target,
        }
        semantic = (source, edge_type, target)
        if semantic not in seen_survivor_semantics:
            missing_by_target[target].append(survivor)
            seen_survivor_semantics.add(semantic)
        lmdb_survivors.append(survivor)
    return dict(sorted(missing_by_target.items())), lmdb_survivors


def run() -> dict[str, Any]:
    if not (LMDB_ROOT / "data.mdb").exists():
        raise ValueError("fix59_unified_lmdb_missing")
    status_text = STATUS_PATH.read_text(encoding="utf-8")
    for token in (
        "fix57_complete",
        "fix57_bridge_edges_applied_to_lmdb",
        "fix58_complete",
        "fix58_residual_queue_fully_dispositioned",
        "fix55_complete",
        "fix55_lmdb_all_nodes_have_graph_projection",
        "fix54_unified_lmdb_materialized",
    ):
        if token not in status_text:
            raise ValueError(f"fix59_required_token_missing:{token}")
    if "fix59_complete" in status_text:
        raise ValueError("fix59_already_complete")

    fix57_rows = _extract_fix57_rejections()
    fix58_rows = _extract_fix58_rejections()
    rejection_rows = [*fix57_rows, *fix58_rows]

    store = GenesisAtlasCandidateStore(
        LMDB_ROOT,
        allow_synthetic_edge_keys=True,
        map_size=DEFAULT_MAP_SIZE_BYTES * 4,
    )
    try:
        nodes = store.iter_nodes()
        edges = store.iter_edges()
        graph_payload = store.get_graph_payload()
        if not isinstance(graph_payload, dict):
            raise ValueError("fix59_graph_payload_missing")
        graph_nodes = graph_payload.get("nodes")
        graph_edges = graph_payload.get("edges")
        if not isinstance(graph_nodes, list) or not isinstance(graph_edges, list):
            raise ValueError("fix59_graph_payload_lists_required")
        if len(nodes) < 15677:
            raise ValueError(f"fix59_node_count_below_baseline:{len(nodes)}")
        if len(edges) < 76295:
            raise ValueError(f"fix59_edge_count_below_fix58_baseline:{len(edges)}")
        node_ids = {_candidate_id(node) for node in nodes}
        missing_projection = [
            _candidate_id(node)
            for node in nodes
            if not isinstance(node.get("graph_projection"), str) or not node.get("graph_projection")
        ]
        if missing_projection:
            raise ValueError(f"fix59_existing_node_graph_projection_missing:{len(missing_projection)}")
        if any(node.get("annotation_phase") == ANNOTATION_PHASE for node in nodes):
            raise ValueError("fix59_nodes_already_present_in_lmdb")
        if any(edge.get("annotation_phase") == ANNOTATION_PHASE for edge in edges):
            raise ValueError("fix59_edges_already_present_in_lmdb")

        pre_materialization_node_count = len(nodes)
        pre_materialization_edge_count = len(edges)
        edges_missing_edge_id_before = sum(1 for edge in edges if not edge.get("edge_id"))
        existing_edge_ids, existing_semantics = _existing_edge_indexes(edges)
        missing_by_target, lmdb_scan_survivors = _build_missing_target_map(
            rejection_rows,
            nodes=nodes,
            edges=edges,
        )
        source_counts = Counter(str(row["source_report"]) for row in rejection_rows)
        by_prefix = Counter(_prefix(target_id) for target_id in missing_by_target)

        new_nodes: list[dict[str, Any]] = []
        new_edges: list[dict[str, Any]] = []
        created_nodes: list[dict[str, Any]] = []
        remapped_targets: list[dict[str, str]] = []
        deferred_targets: list[dict[str, str]] = []
        skipped_edges: list[dict[str, str]] = []
        disposition_counts: Counter[str] = Counter()
        high_authority_decisions: list[dict[str, str]] = []

        for target_id, rows in missing_by_target.items():
            disposition, remap_target, reason = _determine_disposition(target_id, node_ids)
            prefix = _prefix(target_id)
            disposition_counts[disposition] += 1
            if prefix in HIGH_AUTHORITY_PREFIXES:
                high_authority_decisions.append(
                    {
                        "disposition": disposition,
                        "prefix": prefix,
                        "rationale": reason,
                        "remap_target": remap_target or "",
                        "target_id": target_id,
                    }
                )
            if disposition == "stub":
                if target_id in node_ids:
                    raise ValueError(f"fix59_stub_target_already_exists:{target_id}")
                node = _build_stub_node(target_id, disposition=disposition, reason=reason)
                new_nodes.append(node)
                node_ids.add(target_id)
                created_nodes.append(
                    {
                        "candidate_id": target_id,
                        "graph_projection": node["graph_projection"],
                        "node_kind": node["node_kind"],
                        "annotation_method": node["annotation_method"],
                    }
                )
                resolved_target = target_id
            elif disposition == "canonical_materialize":
                if target_id in node_ids:
                    raise ValueError(f"fix59_canonical_materialize_target_already_exists:{target_id}")
                node = _build_stub_node(target_id, disposition=disposition, reason=reason)
                new_nodes.append(node)
                node_ids.add(target_id)
                created_nodes.append(
                    {
                        "candidate_id": target_id,
                        "graph_projection": node["graph_projection"],
                        "node_kind": node["node_kind"],
                        "annotation_method": node["annotation_method"],
                    }
                )
                resolved_target = target_id
            elif disposition == "remap":
                if not remap_target or remap_target not in node_ids:
                    raise ValueError(f"fix59_remap_target_missing:{target_id}:{remap_target}")
                remapped_targets.append(
                    {
                        "from": target_id,
                        "rationale": reason,
                        "to": remap_target,
                    }
                )
                resolved_target = remap_target
            elif disposition == "defer":
                deferred_targets.append({"target_id": target_id, "prefix": prefix, "reason": reason})
                continue
            else:
                raise ValueError(f"fix59_unknown_disposition:{disposition}")

            for row in rows:
                source = str(row["source"])
                edge_type = str(row["edge_type"])
                semantic = (source, edge_type, resolved_target)
                edge_id = _edge_id(*semantic)
                if source not in node_ids:
                    skipped_edges.append(
                        {
                            "edge_type": edge_type,
                            "reason": "source_node_missing_after_resolution",
                            "source": source,
                            "target": resolved_target,
                        }
                    )
                    continue
                if semantic in existing_semantics or edge_id in existing_edge_ids:
                    skipped_edges.append(
                        {
                            "edge_type": edge_type,
                            "reason": "duplicate_after_resolution",
                            "source": source,
                            "target": resolved_target,
                        }
                    )
                    continue
                edge = _build_edge(row, resolved_target, disposition=disposition)
                new_edges.append(edge)
                existing_semantics.add(semantic)
                existing_edge_ids.add(edge_id)

        if any(edge["edge_type"] == "GOVERNS" for edge in new_edges):
            raise ValueError("fix59_governs_edge_generated")

        if new_nodes:
            store.put_nodes([*nodes, *new_nodes])
        if new_edges:
            store.put_edges(new_edges)
        updated_payload = dict(graph_payload)
        updated_payload["nodes"] = [*graph_nodes, *new_nodes]
        updated_payload["edges"] = [*graph_edges, *new_edges]
        store.put_graph_payload(updated_payload)

        post_nodes = store.iter_nodes()
        post_edges = store.iter_edges()
        post_materialization_node_count = len(post_nodes)
        post_materialization_edge_count = len(post_edges)
        edges_missing_edge_id_after = sum(1 for edge in post_edges if not edge.get("edge_id"))
        expected_post_nodes = pre_materialization_node_count + len(new_nodes)
        expected_post_edges = pre_materialization_edge_count + len(new_edges)
        if post_materialization_node_count != expected_post_nodes:
            raise ValueError(
                "fix59_node_count_mismatch:"
                f"{pre_materialization_node_count}:{len(new_nodes)}:{post_materialization_node_count}"
            )
        if post_materialization_edge_count != expected_post_edges:
            raise ValueError(
                "fix59_edge_count_mismatch:"
                f"{pre_materialization_edge_count}:{len(new_edges)}:{post_materialization_edge_count}"
            )
        readback_payload = store.get_graph_payload()
        if not isinstance(readback_payload, dict):
            raise ValueError("fix59_graph_payload_readback_missing")
        if len(readback_payload.get("nodes", [])) != expected_post_nodes:
            raise ValueError("fix59_graph_payload_node_count_mismatch")
        if len(readback_payload.get("edges", [])) != expected_post_edges:
            raise ValueError("fix59_graph_payload_edge_count_mismatch")

        report: dict[str, Any] = {
            "created_nodes": created_nodes,
            "edge_count_nondecreasing": post_materialization_edge_count >= pre_materialization_edge_count,
            "edge_id_debt": {
                "carried_forward_to_fix60": True,
                "edges_missing_edge_id_after": edges_missing_edge_id_after,
                "edges_missing_edge_id_before": edges_missing_edge_id_before,
                "global_repair_performed": False,
            },
            "high_authority_decisions": high_authority_decisions,
            "lmdb_path": str(LMDB_ROOT.relative_to(REPO_ROOT)),
            "missing_target_resolution": {
                "by_prefix": {
                    "atlas": int(by_prefix["atlas"]),
                    "cdl": int(by_prefix["cdl"]),
                    "invariant": int(by_prefix["invariant"]),
                    "other": int(
                        sum(count for prefix, count in by_prefix.items() if prefix not in {
                            "atlas",
                            "cdl",
                            "invariant",
                            "phase",
                            "policy",
                            "sim",
                            "target",
                            "window",
                        })
                    ),
                    "phase": int(by_prefix["phase"]),
                    "policy": int(by_prefix["policy"]),
                    "sim": int(by_prefix["sim"]),
                    "target": int(by_prefix["target"]),
                    "window": int(by_prefix["window"]),
                },
                "canonical_materialize": int(disposition_counts["canonical_materialize"]),
                "defer": int(disposition_counts["defer"]),
                "deferred_targets": deferred_targets,
                "from_lmdb_sanity_scan": len(lmdb_scan_survivors),
                "from_rejection_reports": len(missing_by_target)
                - sum(1 for target_rows in missing_by_target.values() if all(row.get("source_report") == "lmdb_sanity_scan" for row in target_rows)),
                "re_applied_edges": len(new_edges),
                "remap": int(disposition_counts["remap"]),
                "stub": int(disposition_counts["stub"]),
                "total_unique_missing_targets": len(missing_by_target),
            },
            "new_edges": [_report_edge(edge) for edge in new_edges],
            "node_count_nondecreasing": post_materialization_node_count >= pre_materialization_node_count,
            "non_claims": [
                "Stub nodes are minimal materialization anchors -- not manually reviewed annotations",
                "Fix59 does not perform global edge_id repair; Fix60 owns remaining edge_id debt",
                "Fix59 does not add GOVERNS edges",
                "Stub nodes have annotation_method stub_materialized -- not manual_reviewed",
                "canonical_materialize nodes are authority stubs -- they do not grant authority or signing eligibility",
                "No CDL mutation, signing, runtime activation",
            ],
            "phase": PHASE,
            "post_materialization_edge_count": post_materialization_edge_count,
            "post_materialization_node_count": post_materialization_node_count,
            "pre_materialization_edge_count": pre_materialization_edge_count,
            "pre_materialization_node_count": pre_materialization_node_count,
            "rejection_report_entry_counts": dict(sorted(source_counts.items())),
            "rejection_report_sources": [
                str(FIX57_REPORT.relative_to(REPO_ROOT)),
                str(FIX58_REPORT.relative_to(REPO_ROOT)),
            ],
            "remapped_targets": remapped_targets,
            "skipped_edges": skipped_edges,
            "status": "PASS",
        }
        store.put_meta("fix59_missing_target_materialization", report)
    finally:
        store.close()

    _atomic_write_json(REPORT_PATH, report)
    print(
        "Done. status=PASS, "
        f"edge_id_debt_for_fix60={report['edge_id_debt']['edges_missing_edge_id_after']}, "
        f"rejection_report_targets={report['missing_target_resolution']['from_rejection_reports']}, "
        f"lmdb_scan_survivors={report['missing_target_resolution']['from_lmdb_sanity_scan']}, "
        f"stub={report['missing_target_resolution']['stub']}, "
        f"remap={report['missing_target_resolution']['remap']}, "
        f"canonical_materialize={report['missing_target_resolution']['canonical_materialize']}, "
        f"defer={report['missing_target_resolution']['defer']}, "
        f"new_nodes={len(report['created_nodes'])}, "
        f"re_applied_edges={report['missing_target_resolution']['re_applied_edges']}"
    )
    return report


def main() -> int:
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
