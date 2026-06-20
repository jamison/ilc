#!/usr/bin/env python3
"""Close the Genesis Atlas governance-spine trace gaps.

PUBLIC_RC_EXCLUDE: fix62g_governance_spine_closure_research_only
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Genesis Atlas LMDB maintenance pass;
not Genesis signing, public graph upload, canonical graph mutation, runtime
activation, public serving, ECU minting, or public RC publication.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.storage.genesis_atlas_lmdb_writer import (  # noqa: E402
    AtlasLmdbSafeWriter,
    AtlasLmdbWritePlan,
    AtlasPhaseFileRegistration,
    deterministic_edge_id,
    write_json_atomic,
)


PHASE = "1545p-Fix62g"
PHASE_TOKEN = "phase_1545p_fix62g"
ROOT = "artifact:genesis_intent_attestation_init_authority_map"
CDL074 = "cdl:074_truth_primitive_runtime"
SUPPORT_POLICY = "policy:full_repo_genesis_atlas_candidate_unsigned_support_only_phase_1545p_fix22"
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
INPUT_QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix62f_manual_graph_finish_queue_v0.1.json"
LEDGER_PATH = REPO_ROOT / "docs/specs/ilc_fix62g_governance_spine_closure_ledger_v0.1.json"
QUEUE_PATH = REPO_ROOT / "docs/specs/ilc_fix62g_manual_graph_finish_queue_v0.1.json"
REPORT_MD_PATH = REPO_ROOT / "docs/specs/ilc_fix62g_governance_spine_closure_report_v0.1.md"
WALKTHROUGH_PATH = REPO_ROOT / "docs/phases/phase_1545p_fix62g_governance_spine_closure_walkthrough.md"
OUT_REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix62g_governance_spine_closure_v0.1.json"
EVALUATOR_PATH = REPO_ROOT / "tools/evaluators/sim_genesis_atlas_fix62g_governance_spine_closure.py"
TEST_PATH = REPO_ROOT / "tests/test_phase_1545p_fix62g_governance_spine_closure.py"

INPUT_TOKENS = ("fix62f_complete",)
OUTPUT_TOKENS = (
    "fix62g_governance_spine_closure_complete",
    "fix62g_truth_primitives_governed_by_cdl074",
    "fix62g_alias_overlays_demoted_to_support_trace",
    "fix62g_complete",
)


def _verify_tokens() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    for token in INPUT_TOKENS:
        if token not in status:
            raise ValueError(f"fix62g_missing_input_token:{token}")
    for token in OUTPUT_TOKENS:
        if token in status:
            raise ValueError(f"fix62g_output_token_already_present:{token}")


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"fix62g_json_not_object:{path}")
    return payload


def _canonical_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _canonical_sha256(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _candidate_id(node: dict[str, Any]) -> str:
    value = node.get("candidate_id")
    if not isinstance(value, str) or not value:
        raise ValueError("fix62g_node_candidate_id_missing")
    return value


def _edge_source(edge: dict[str, Any]) -> str:
    for key in ("source", "src", "source_candidate_id", "from", "source_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("fix62g_edge_source_missing")


def _edge_target(edge: dict[str, Any]) -> str:
    for key in ("target", "tgt", "target_candidate_id", "to", "target_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("fix62g_edge_target_missing")


def _edge_type(edge: dict[str, Any]) -> str:
    value = edge.get("edge_type")
    if not isinstance(value, str) or not value:
        raise ValueError("fix62g_edge_type_missing")
    return value


def _edge_payload(source: str, edge_type: str, target: str, *, reason: str) -> dict[str, Any]:
    return {
        "annotation_method": "fix62g_governance_spine_closure",
        "annotation_phase": PHASE_TOKEN,
        "candidate_status": "fix62g_unsigned_governance_spine_lmdb_candidate",
        "edge_id": deterministic_edge_id(source, edge_type, target),
        "edge_type": edge_type,
        "evidence": reason,
        "reason": reason,
        "source": source,
        "target": target,
    }


def _node_preimage(node: dict[str, Any]) -> dict[str, Any]:
    node_id = _candidate_id(node)
    fields = {
        "authority_status": node.get("authority_status"),
        "candidate_id": node_id,
        "canonicality_tier": node.get("canonicality_tier"),
        "graph_projection": node.get("graph_projection"),
        "node_kind": node.get("node_kind"),
        "phase": PHASE,
        "source_path": node.get("source_path"),
    }
    return {
        "canonical_sha256": _canonical_sha256(fields),
        "fields": fields,
        "node_id": node_id,
        "preimage_version": "v0.4.fix62g_governance_spine_closure",
    }


def _edge_preimage(edge: dict[str, Any]) -> dict[str, Any]:
    fields = {
        "edge_id": edge.get("edge_id")
        or deterministic_edge_id(_edge_source(edge), _edge_type(edge), _edge_target(edge)),
        "edge_type": _edge_type(edge),
        "phase": PHASE,
        "source": _edge_source(edge),
        "target": _edge_target(edge),
    }
    return {
        "canonical_sha256": _canonical_sha256(fields),
        "edge_id": fields["edge_id"],
        "fields": fields,
        "preimage_version": "v0.4.fix62g_governance_spine_closure",
    }


def _number(node_id: str, prefix: str) -> int | str | None:
    if prefix == "cdl":
        match = re.match(r"cdl:(?:v([0-9]+)|0*([0-9]{1,4})(?:\b|_|$))", node_id, re.IGNORECASE)
        if not match:
            return None
        if match.group(1):
            return f"v{int(match.group(1))}"
        return int(match.group(2))
    match = re.match(r"adr:(?:ADR_)?0*([0-9]{1,4})(?:\b|_|$)", node_id, re.IGNORECASE)
    return int(match.group(1)) if match else None


def _alias_edge_type(node_id: str) -> str:
    lowered = node_id.lower()
    if any(token in lowered for token in ("opening", "prelock", "ratification", "phase", "spec")):
        return "DERIVED_FROM"
    return "SAME_AUTHORITY"


def _support_patch(reason: str, *, node_kind: str) -> dict[str, str]:
    return {
        "authority_status": reason,
        "canonicality_tier": "support_trace_not_independent_authority",
        "graph_projection": "support_candidate_graph",
        "inclusion_status": "support_trace_not_independent_authority",
        "node_kind": node_kind,
        "promotion_status": "not_independent_authority",
        "tier": "support_candidate",
    }


def _root_governed_targets(edges: list[dict[str, Any]]) -> set[str]:
    return {
        _edge_target(edge)
        for edge in edges
        if _edge_source(edge) == ROOT and _edge_type(edge) == "GOVERNS"
    }


def _governed_by_any(edges: list[dict[str, Any]]) -> set[str]:
    return {_edge_target(edge) for edge in edges if _edge_type(edge) == "GOVERNS"}


def _build_governance_repairs(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, dict[str, str]], list[dict[str, Any]]]:
    node_by_id = {_candidate_id(node): node for node in nodes}
    node_ids = set(node_by_id)
    root_targets = _root_governed_targets(edges)
    governed_any = _governed_by_any(edges)
    repair_edges: list[dict[str, Any]] = []
    node_updates: dict[str, dict[str, str]] = {}
    ledger_rows: list[dict[str, Any]] = []

    if CDL074 not in node_ids:
        raise ValueError("fix62g_cdl074_missing")
    truth_primitives = sorted(node_id for node_id in node_ids if node_id.startswith("truth_primitive:"))
    for node_id in truth_primitives:
        if node_id not in governed_any:
            edge = _edge_payload(
                CDL074,
                "GOVERNS",
                node_id,
                reason="CDL-074 ratified truth primitive runtime governs Genesis truth primitive operator nodes",
            )
            repair_edges.append(edge)
            ledger_rows.append(
                {
                    "disposition": "add_governs",
                    "edge_type": "GOVERNS",
                    "source": CDL074,
                    "target": node_id,
                    "trace_class": "truth_primitive_runtime_authority",
                }
            )

    for prefix in ("cdl", "adr"):
        groups: dict[int | str, list[str]] = defaultdict(list)
        for node_id in sorted(node_id for node_id in node_ids if node_id.startswith(f"{prefix}:")):
            number = _number(node_id, prefix)
            if number is not None:
                groups[number].append(node_id)
        for number, group in sorted(groups.items(), key=lambda item: str(item[0])):
            governed = sorted(node_id for node_id in group if node_id in root_targets)
            missing = sorted(node_id for node_id in group if node_id not in governed_any)
            canonical_target = governed[0] if governed else ""
            for node_id in missing:
                node = node_by_id[node_id]
                if node.get("authority_status") == "proposed_adr_not_authority":
                    node_updates[node_id] = _support_patch(
                        "proposed_adr_not_authority",
                        node_kind="adr_proposal_artifact",
                    )
                    repair_edges.append(
                        _edge_payload(
                            node_id,
                            "CLASSIFIED_BY",
                            SUPPORT_POLICY,
                            reason="Proposed ADR candidate remains support-only until accepted",
                        )
                    )
                    ledger_rows.append(
                        {
                            "disposition": "classify_support_only",
                            "edge_type": "CLASSIFIED_BY",
                            "source": node_id,
                            "target": SUPPORT_POLICY,
                            "trace_class": "proposed_adr_support_classification",
                        }
                    )
                    continue
                if canonical_target:
                    edge_type = _alias_edge_type(node_id)
                    node_updates[node_id] = _support_patch(
                        "alias_or_lifecycle_overlay_to_rooted_authority",
                        node_kind=f"{prefix}_alias_or_lifecycle_support_node",
                    )
                    repair_edges.append(
                        _edge_payload(
                            node_id,
                            edge_type,
                            canonical_target,
                            reason="Alias or lifecycle overlay traces to already rooted canonical authority node",
                        )
                    )
                    ledger_rows.append(
                        {
                            "canonical_target": canonical_target,
                            "disposition": "trace_to_canonical_authority",
                            "edge_type": edge_type,
                            "source": node_id,
                            "target": canonical_target,
                            "trace_class": f"{prefix}_alias_overlay_trace",
                        }
                    )
                    continue
                node_updates[node_id] = _support_patch(
                    "open_unratified_or_unresolved_candidate_not_authority",
                    node_kind=f"{prefix}_support_candidate_overlay",
                )
                repair_edges.append(
                    _edge_payload(
                        node_id,
                        "CLASSIFIED_BY",
                        SUPPORT_POLICY,
                        reason="Open, unratified, or unresolved candidate overlay is not independent authority",
                    )
                )
                ledger_rows.append(
                    {
                        "disposition": "classify_support_only",
                        "edge_type": "CLASSIFIED_BY",
                        "source": node_id,
                        "target": SUPPORT_POLICY,
                        "trace_class": f"{prefix}_noncanonical_support_classification",
                    }
                )

    valid_edges = [
        edge
        for edge in repair_edges
        if _edge_source(edge) in node_ids and _edge_target(edge) in node_ids
    ]
    if len(valid_edges) != len(repair_edges):
        raise ValueError("fix62g_repair_edge_endpoint_missing")
    return valid_edges, node_updates, ledger_rows


def _queue_payload(entries: list[dict[str, Any]], *, source_queue: Path) -> dict[str, Any]:
    entries.sort(key=lambda item: (item["priority"], item["work_family"], item.get("path", ""), item["candidate_id"]))
    for index, entry in enumerate(entries, start=1):
        entry["queue_index"] = index
        entry["batch_id"] = f"fix62g_batch_{((index - 1) // 10) + 1:04d}"
    priority_counts = Counter(str(entry["priority"]) for entry in entries)
    work_family_counts = Counter(str(entry.get("work_family", "")) for entry in entries)
    reason_counts: Counter[str] = Counter()
    for entry in entries:
        reason_counts.update(str(reason) for reason in entry.get("reasons", []))
    return {
        "entry_count": len(entries),
        "entries": entries,
        "phase": PHASE,
        "priority_counts": dict(sorted(priority_counts.items())),
        "reason_counts": dict(sorted(reason_counts.items())),
        "source_queue": str(source_queue.relative_to(REPO_ROOT)),
        "status": "carry_forward_after_governance_spine_closure",
        "work_family_counts": dict(sorted(work_family_counts.items())),
    }


def _register_phase_files(writer: AtlasLmdbSafeWriter) -> dict[str, Any]:
    files = (
        AtlasPhaseFileRegistration(
            path=EVALUATOR_PATH.relative_to(REPO_ROOT),
            node_kind="tooling_source_file_node",
            graph_projection="support_candidate_graph",
            required_edges=(("IMPLEMENTS", "phase:1545p_fix62g"),),
        ),
        AtlasPhaseFileRegistration(
            path=TEST_PATH.relative_to(REPO_ROOT),
            node_kind="test_evidence_node",
            graph_projection="support_candidate_graph",
            required_edges=(("TESTS", "phase:1545p_fix62g"),),
        ),
        AtlasPhaseFileRegistration(
            path=LEDGER_PATH.relative_to(REPO_ROOT),
            node_kind="spec_json_artifact_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62g"),),
        ),
        AtlasPhaseFileRegistration(
            path=QUEUE_PATH.relative_to(REPO_ROOT),
            node_kind="spec_json_artifact_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62g"),),
        ),
        AtlasPhaseFileRegistration(
            path=REPORT_MD_PATH.relative_to(REPO_ROOT),
            node_kind="spec_document_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62g"),),
        ),
        AtlasPhaseFileRegistration(
            path=WALKTHROUGH_PATH.relative_to(REPO_ROOT),
            node_kind="phase_walkthrough_node",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", "phase:1545p_fix62g"),),
        ),
    )
    return writer.register_phase_files(PHASE, files, dry_run=False)


def _audit(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
    governed_any = _governed_by_any(edges)
    node_by_id = {_candidate_id(node): node for node in nodes}
    truth_missing = sorted(node_id for node_id in node_by_id if node_id.startswith("truth_primitive:") and node_id not in governed_any)
    core_authority_missing = []
    for node_id, node in node_by_id.items():
        if not (node_id.startswith("cdl:") or node_id.startswith("adr:")):
            continue
        if node.get("graph_projection") != "genesis_core_star_map":
            continue
        if node.get("authority_status") in {"proposed_adr_not_authority", "open_unratified_or_unresolved_candidate_not_authority"}:
            continue
        if node_id not in governed_any:
            core_authority_missing.append(node_id)
    return {
        "core_authority_missing_governs": sorted(core_authority_missing),
        "core_authority_missing_governs_count": len(core_authority_missing),
        "truth_primitive_missing_governs": truth_missing,
        "truth_primitive_missing_governs_count": len(truth_missing),
    }


def _append_status(report: dict[str, Any]) -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    block = f"""

### Phase 1545p-Fix62g — Governance Spine Closure

**Status:** complete

**Output:** Added `{report['truth_primitive_governs_added']}` CDL-074 truth-primitive GOVERNS edges, traced or demoted `{report['alias_or_support_trace_count']}` CDL/ADR alias, lifecycle, proposed, open, or unresolved overlay nodes, refreshed preimages, and preserved all non-activation boundaries.

**Tokens:** {', '.join(OUTPUT_TOKENS)}
"""
    STATUS_PATH.write_text(status.rstrip() + block + "\n", encoding="utf-8")


def _report_markdown(report: dict[str, Any]) -> str:
    return f"""# ILC Fix62g Governance Spine Closure Report

PUBLIC_RC_EXCLUDE: fix62g_governance_spine_closure_research_only

## Summary

- Truth primitive GOVERNS edges added: `{report['truth_primitive_governs_added']}`
- Alias/support traces added: `{report['alias_or_support_trace_count']}`
- Node field updates accepted: `{report['node_update']['accepted_update_count']}`
- Edge additions accepted: `{report['edge_application']['accepted_edge_count']}`
- Final LMDB nodes: `{report['final_counts']['nodes']}`
- Final LMDB edges: `{report['final_counts']['edges']}`
- Final LMDB preimages: `{report['final_counts']['preimages']}`

## Boundary

This phase updates the local unsigned Genesis Atlas LMDB candidate only. It does
not sign Genesis, publish the graph, activate public serving, mint ECU, settle
ILC, or mutate canonical protocol authority. No ECU minting, production
emission, wallet settlement, or public claimability activation occurred.

## Governance-Spine Policy

This phase deliberately does not add root `GOVERNS` edges to aliases, lifecycle
snapshots, proposed ADRs, open CDLs, or unresolved candidate overlays. Those
nodes receive role-specific traces to their rooted canonical sibling or support
classification. Only `cdl:074_truth_primitive_runtime` receives new outbound
`GOVERNS` edges, and only to the seven existing Genesis truth primitive nodes.
"""


def _walkthrough_markdown(report: dict[str, Any]) -> str:
    return f"""# Phase 1545p-Fix62g Walkthrough

## Commands

```bash
python tools/evaluators/sim_genesis_atlas_fix62g_governance_spine_closure.py
python -m pytest tests/test_phase_1545p_fix62g_governance_spine_closure.py tests/test_phase_1545p_fix62f_runtime_source_trace.py tests/test_phase_1545p_fix59b_atlas_lmdb_safe_writer.py -q
python -m ilc_core.cli.main atlas validate --lmdb out/genesis_base_graph_v0.4_unified.lmdb
```

## Result

- Truth primitive GOVERNS edges added: `{report['truth_primitive_governs_added']}`
- Alias/support traces added: `{report['alias_or_support_trace_count']}`
- Post-audit truth primitive missing GOVERNS: `{report['post_audit']['truth_primitive_missing_governs_count']}`
- Post-audit core authority missing GOVERNS: `{report['post_audit']['core_authority_missing_governs_count']}`
- Final LMDB counts: `{report['final_counts']['nodes']}` nodes / `{report['final_counts']['edges']}` edges / `{report['final_counts']['preimages']}` preimages

## Non-Claims

No Genesis signing, public graph upload, public RC publication, public serving,
runtime activation, ECU minting, or ILC settlement occurred.
"""


def _validate_report(report: dict[str, Any]) -> None:
    if report["truth_primitive_governs_added"] != 7:
        raise ValueError("fix62g_expected_seven_truth_primitive_edges")
    if report["post_audit"]["truth_primitive_missing_governs_count"] != 0:
        raise ValueError("fix62g_truth_primitives_still_ungoverned")
    if report["post_audit"]["core_authority_missing_governs_count"] != 0:
        raise ValueError("fix62g_core_authority_still_unrooted")
    if report["edge_application"]["rejected_edge_count"] != 0:
        raise ValueError("fix62g_rejected_edges_present")


def run() -> dict[str, Any]:
    _verify_tokens()
    input_queue = _read_json(INPUT_QUEUE_PATH)
    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        pre_counts = writer.inspect()
        nodes = writer.store.iter_nodes()
        edges = writer.store.iter_edges()
        repair_edges, node_updates, ledger_rows = _build_governance_repairs(nodes, edges)
        truth_edge_count = sum(1 for edge in repair_edges if _edge_source(edge) == CDL074 and _edge_type(edge) == "GOVERNS")
        alias_or_support_count = len(repair_edges) - truth_edge_count

        plan = AtlasLmdbWritePlan(
            edges_to_add=repair_edges,
            metadata={"operation": "fix62g_governance_spine_closure"},
            phase=PHASE,
            dry_run=False,
        )
        edge_receipt = writer.apply_plan(plan)
        node_update_receipt = writer.update_node_fields(
            node_updates,
            phase=PHASE,
            dry_run=False,
            metadata={"operation": "fix62g_alias_overlay_demote"},
        )

        repaired_ids = {row["target"] for row in ledger_rows if row["disposition"] == "add_governs"}
        repaired_ids.update(row["source"] for row in ledger_rows if row["disposition"] != "add_governs")
        carry_entries = [
            dict(entry)
            for entry in input_queue.get("entries", [])
            if entry.get("candidate_id") not in repaired_ids
        ]
        queue_payload = _queue_payload(carry_entries, source_queue=INPUT_QUEUE_PATH)
        ledger = {
            "entry_count": len(ledger_rows),
            "entries": ledger_rows,
            "phase": PHASE,
            "status": "governance_spine_closure_complete",
        }
        write_json_atomic(LEDGER_PATH, ledger)
        write_json_atomic(QUEUE_PATH, queue_payload)

        file_registration_receipt = _register_phase_files(writer)
        post_nodes = writer.store.iter_nodes()
        post_edges = writer.store.iter_edges()
        touched_node_ids = set(repaired_ids)
        touched_node_ids.update(
            _candidate_id(node)
            for node in post_nodes
            if str(node.get("annotation_phase")) == PHASE_TOKEN
        )
        touched_edge_ids = {
            str(edge.get("edge_id"))
            for edge in post_edges
            if str(edge.get("annotation_phase")) == PHASE_TOKEN and edge.get("edge_id")
        }
        preimages = [
            _node_preimage(node)
            for node in post_nodes
            if _candidate_id(node) in touched_node_ids
        ]
        preimages.extend(
            _edge_preimage(edge)
            for edge in post_edges
            if str(edge.get("edge_id")) in touched_edge_ids
        )
        preimage_receipt = writer.write_preimages(
            preimages,
            phase=PHASE,
            dry_run=False,
            metadata={"preimage_scope": "fix62g_governance_spine_closure"},
        )
        final_counts = writer.inspect()
        post_audit = _audit(post_nodes, post_edges)
        report = {
            "alias_or_support_trace_count": alias_or_support_count,
            "edge_application": {
                "accepted_edge_count": edge_receipt["accepted_edge_count"],
                "rejected_edge_count": edge_receipt["rejected_edge_count"],
                "skipped_edge_count": edge_receipt["skipped_edge_count"],
            },
            "file_registration": {
                "accepted_edge_count": file_registration_receipt["accepted_edge_count"],
                "accepted_node_count": file_registration_receipt["accepted_node_count"],
            },
            "final_counts": {
                "edges": final_counts["edge_count"],
                "nodes": final_counts["node_count"],
                "preimages": final_counts["preimage_count"],
            },
            "ledger_path": str(LEDGER_PATH.relative_to(REPO_ROOT)),
            "node_update": {
                "accepted_update_count": node_update_receipt["accepted_update_count"],
                "rejected_update_count": node_update_receipt["rejected_update_count"],
            },
            "phase": PHASE,
            "post_audit": post_audit,
            "pre_counts": pre_counts,
            "preimage_receipt": {
                "preimage_count": preimage_receipt["preimage_count"],
                "post_preimage_count": preimage_receipt["post_preimage_count"],
            },
            "queue_path": str(QUEUE_PATH.relative_to(REPO_ROOT)),
            "status": "PASS",
            "truth_primitive_governs_added": truth_edge_count,
        }
        _validate_report(report)
        REPORT_MD_PATH.write_text(_report_markdown(report), encoding="utf-8")
        WALKTHROUGH_PATH.write_text(_walkthrough_markdown(report), encoding="utf-8")
        write_json_atomic(OUT_REPORT_PATH, report)
        _append_status(report)
        return report
    finally:
        writer.close()


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, separators=(",", ":"), allow_nan=False))
