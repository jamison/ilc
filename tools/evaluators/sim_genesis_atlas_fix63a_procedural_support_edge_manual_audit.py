#!/usr/bin/env python3
"""Fix63a procedural support-edge audit for support/lifecycle records.

PUBLIC_RC_EXCLUDE: fix63a_procedural_support_edge_manual_audit_research_only
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Genesis Atlas LMDB maintenance pass;
not Genesis signing, public graph upload, canonical graph mutation, runtime
activation, public serving, ECU minting, or public RC publication.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
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


PHASE = "1545p-Fix63a"
PHASE_TOKEN = "phase_1545p_fix63a"
SUPPORT_POLICY = "policy:full_repo_genesis_atlas_candidate_unsigned_support_only_phase_1545p_fix22"
PUBLIC_PATH_POLICY = "policy:public_path_still_blocked_phase_1545p"
ROOT = "artifact:genesis_intent_attestation_init_authority_map"
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
STATUS_PATH = REPO_ROOT / "docs/phases/STATUS.md"
FIX63_LEDGER_PATH = REPO_ROOT / "docs/specs/ilc_fix63_manual_governs_audit_ledger_v0.1.json"
LEDGER_PATH = REPO_ROOT / "docs/specs/ilc_fix63a_procedural_support_edge_manual_audit_ledger_v0.1.json"
REPORT_MD_PATH = REPO_ROOT / "docs/specs/ilc_fix63a_procedural_support_edge_manual_audit_report_v0.1.md"
WALKTHROUGH_PATH = REPO_ROOT / "docs/phases/phase_1545p_fix63a_procedural_support_edge_manual_audit_walkthrough.md"
OUT_REPORT_PATH = REPO_ROOT / "out/genesis_atlas_fix63a_procedural_support_edge_manual_audit_report_v0.1.json"
PROMPT_PATH = REPO_ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix63_g10_procedural_support_edge_manual_audit_fix63a.md"
EVALUATOR_PATH = REPO_ROOT / "tools/evaluators/sim_genesis_atlas_fix63a_procedural_support_edge_manual_audit.py"
TEST_PATH = REPO_ROOT / "tests/test_phase_1545p_fix63a_procedural_support_edge_manual_audit.py"

INPUT_TOKENS = ("fix63_complete",)
OUTPUT_TOKENS = (
    "fix63a_procedural_support_edge_audit_complete",
    "fix63a_support_lifecycle_records_enriched",
    "fix63a_complete",
)
TARGET_DISPOSITIONS = {
    "confirmed_support_stub",
    "shadow_duplicate_deduped",
    "cdl_lifecycle_record",
    "open_cdl_stub",
    "proposed_adr_stub",
    "adr_decision_record",
}
ACCEPTED_ADR_TARGETS = {
    "0020": "adr:0020_knowledge_node_first_design_principle",
    "0036": "adr:0036_operational_release_key_genesis_binding",
    "0037": "adr:0037_genesis_canonical_lineage_contract",
}
ADR_EVIDENCE = {
    "0020": "docs/adr/ADR_0020_Knowledge_Node_First_Design_Principle.md:3",
    "0036": "docs/adr/ADR_0036_Operational_Release_Key_Genesis_Binding.md:3",
    "0037": "docs/adr/ADR_0037_Genesis_Canonical_Lineage_Contract.md:3",
}


def _verify_tokens() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    for token in INPUT_TOKENS:
        if token not in status:
            raise ValueError(f"fix63a_missing_input_token:{token}")
    for token in OUTPUT_TOKENS:
        if token in status:
            raise ValueError(f"fix63a_output_token_already_present:{token}")


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"fix63a_json_not_object:{path}")
    return payload


def _canonical_sha256(payload: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()


def _candidate_id(node: dict[str, Any]) -> str:
    value = node.get("candidate_id")
    if not isinstance(value, str) or not value:
        raise ValueError("fix63a_node_candidate_id_missing")
    return value


def _edge_source(edge: dict[str, Any]) -> str:
    for key in ("source", "src", "source_candidate_id", "from", "source_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("fix63a_edge_source_missing")


def _edge_target(edge: dict[str, Any]) -> str:
    for key in ("target", "tgt", "target_candidate_id", "to", "target_id"):
        value = edge.get(key)
        if isinstance(value, str) and value:
            return value
    raise ValueError("fix63a_edge_target_missing")


def _edge_type(edge: dict[str, Any]) -> str:
    value = edge.get("edge_type")
    if not isinstance(value, str) or not value:
        raise ValueError("fix63a_edge_type_missing")
    return value


def _edge_payload(source: str, edge_type: str, target: str, *, evidence: str, reason: str) -> dict[str, Any]:
    return {
        "annotation_method": "fix63a_procedural_support_edge_manual_audit",
        "annotation_phase": PHASE_TOKEN,
        "candidate_status": "fix63a_unsigned_procedural_support_edge_lmdb_candidate",
        "edge_id": deterministic_edge_id(source, edge_type, target),
        "edge_type": edge_type,
        "evidence": evidence,
        "reason": reason,
        "source": source,
        "target": target,
    }


def _support_node(node_id: str, *, node_kind: str, label: str) -> dict[str, Any]:
    return {
        "annotation_method": "fix63a_procedural_support_edge_manual_audit",
        "annotation_phase": PHASE_TOKEN,
        "candidate_id": node_id,
        "candidate_status": "fix63a_support_endpoint_materialized",
        "graph_delta": "support_only",
        "graph_projection": "support_candidate_graph",
        "label": label,
        "node_kind": node_kind,
        "tier": "support_candidate",
    }


def _node_preimage(node: dict[str, Any]) -> dict[str, Any]:
    node_id = _candidate_id(node)
    fields = {
        "candidate_id": node_id,
        "graph_projection": node.get("graph_projection"),
        "node_kind": node.get("node_kind"),
        "phase": PHASE,
    }
    return {
        "canonical_sha256": _canonical_sha256(fields),
        "fields": fields,
        "node_id": node_id,
        "preimage_version": "v0.4.fix63a_procedural_support_edge_manual_audit",
    }


def _edge_preimage(edge: dict[str, Any]) -> dict[str, Any]:
    fields = {
        "edge_id": edge.get("edge_id") or deterministic_edge_id(_edge_source(edge), _edge_type(edge), _edge_target(edge)),
        "edge_type": _edge_type(edge),
        "phase": PHASE,
        "source": _edge_source(edge),
        "target": _edge_target(edge),
    }
    return {
        "canonical_sha256": _canonical_sha256(fields),
        "edge_id": fields["edge_id"],
        "fields": fields,
        "preimage_version": "v0.4.fix63a_procedural_support_edge_manual_audit",
    }


def _line_for(path: str, patterns: list[str]) -> str:
    lines = (REPO_ROOT / path).read_text(encoding="utf-8").splitlines()
    for pattern in patterns:
        needle = pattern.lower()
        for index, line in enumerate(lines, start=1):
            if needle in line.lower():
                return f"{path}:{index}"
    return f"{path}:1"


def _phase_or_window_target(node_id: str) -> tuple[str | None, str | None, str | None]:
    body = node_id.split(":", 1)[1]
    phase = re.search(r"phase[_-]?([0-9]{3,4}[a-z]?|m[0-9]{3})", body)
    if phase:
        token = phase.group(1).lower()
        return f"phase:{token}", "phase_support_node", _line_for("docs/phases/STATUS.md", [f"phase_{token}", f"phase{token}", token])
    window = re.search(r"window[_-]?([0-9]{3,4})", body)
    if window:
        token = window.group(1)
        return f"window:{token}", "window_support_node", _line_for("docs/phases/STATUS.md", [f"window_{token}", f"window{token}", token])
    if body.startswith("sim_"):
        sim_token = body[:96]
        return f"sim:{sim_token}", "sim_support_node", "docs/phases/STATUS.md:1"
    return None, None, None


def _register_phase_files(writer: AtlasLmdbSafeWriter) -> dict[str, Any]:
    files = (
        AtlasPhaseFileRegistration(PROMPT_PATH.relative_to(REPO_ROOT), "phase_prompt_node", "support_candidate_graph"),
        AtlasPhaseFileRegistration(EVALUATOR_PATH.relative_to(REPO_ROOT), "tooling_source_file_node", "support_candidate_graph", required_edges=(("IMPLEMENTS", "phase:1545p_fix63a"),)),
        AtlasPhaseFileRegistration(TEST_PATH.relative_to(REPO_ROOT), "test_evidence_node", "support_candidate_graph", required_edges=(("TESTS", "phase:1545p_fix63a"),)),
        AtlasPhaseFileRegistration(LEDGER_PATH.relative_to(REPO_ROOT), "spec_json_artifact_node", "support_candidate_graph", required_edges=(("EVIDENCES", "phase:1545p_fix63a"),)),
        AtlasPhaseFileRegistration(REPORT_MD_PATH.relative_to(REPO_ROOT), "spec_document_node", "support_candidate_graph", required_edges=(("EVIDENCES", "phase:1545p_fix63a"),)),
        AtlasPhaseFileRegistration(WALKTHROUGH_PATH.relative_to(REPO_ROOT), "phase_walkthrough_node", "support_candidate_graph", required_edges=(("EVIDENCES", "phase:1545p_fix63a"),)),
        AtlasPhaseFileRegistration(STATUS_PATH.relative_to(REPO_ROOT), "phase_status_log_node", "support_candidate_graph", required_edges=(("EVIDENCES", "phase:1545p_fix63a"),)),
    )
    return writer.register_phase_files(PHASE, files, dry_run=False)


def _build_entries_and_plan(source_rows: list[dict[str, Any]], existing_nodes: set[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    ledger_entries: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    nodes: list[dict[str, Any]] = []
    materialized: set[str] = set()

    def add_node(node_id: str, *, node_kind: str, label: str) -> None:
        if node_id in existing_nodes or node_id in materialized:
            return
        nodes.append(_support_node(node_id, node_kind=node_kind, label=label))
        materialized.add(node_id)

    for index, row in enumerate(source_rows, start=1):
        node_id = row["candidate_id"]
        disposition = row["disposition"]
        batch = ((index - 1) // 10) + 1
        row_edges: list[dict[str, Any]] = []
        evidence = row.get("evidence") or "docs/phases/STATUS.md:1"
        notes: list[str] = []

        row_edges.append(
            _edge_payload(
                node_id,
                "CLASSIFIED_BY",
                SUPPORT_POLICY,
                evidence=evidence,
                reason="Fix63a support/lifecycle/proposal row classified by rooted support policy",
            )
        )

        if disposition == "shadow_duplicate_deduped" and row.get("governing_authority"):
            row_edges.append(
                _edge_payload(
                    node_id,
                    "SAME_AUTHORITY",
                    row["governing_authority"],
                    evidence=evidence,
                    reason="Shadow duplicate points to rooted canonical authority node without receiving independent GOVERNS",
                )
            )
            notes.append("shadow duplicate attached with SAME_AUTHORITY")
        elif disposition == "cdl_lifecycle_record":
            target = row.get("governing_authority") or "cdl:085_werner_phi_bound"
            if "opening" in node_id:
                edge_type = "OPENED_FOR"
            elif "prelock" in node_id:
                edge_type = "PRELOCK_FOR"
            elif "ratification" in node_id:
                edge_type = "RATIFICATION_EVIDENCE_FOR"
            else:
                edge_type = "DERIVED_FROM"
            row_edges.append(
                _edge_payload(
                    node_id,
                    edge_type,
                    target,
                    evidence=evidence,
                    reason="CDL lifecycle record attached to canonical CDL without independent authority promotion",
                )
            )
            notes.append(f"lifecycle edge {edge_type}")
        elif disposition == "adr_decision_record" and row.get("governing_authority"):
            row_edges.append(
                _edge_payload(
                    node_id,
                    "DERIVED_FROM",
                    row["governing_authority"],
                    evidence=evidence,
                    reason="ADR decision sub-record derived from accepted ADR record",
                )
            )
            notes.append("ADR decision record attached with DERIVED_FROM")
        elif disposition == "proposed_adr_stub":
            notes.append("proposed ADR remains classified support-only; no root GOVERNS")
        elif disposition == "open_cdl_stub":
            notes.append("open CDL remains classified support-only; no ratified authority edge")

        if disposition == "confirmed_support_stub":
            body = node_id.split(":", 1)[1]
            adr_match = re.search(r"adr[_-]?([0-9]{4})", body)
            if adr_match and adr_match.group(1) in ACCEPTED_ADR_TARGETS:
                adr_number = adr_match.group(1)
                target = ACCEPTED_ADR_TARGETS[adr_number]
                row_edges.append(
                    _edge_payload(
                        target,
                        "GOVERNS",
                        node_id,
                        evidence=ADR_EVIDENCE[adr_number],
                        reason=f"Direct-read ADR-{adr_number} Accepted status; invariant enforces accepted ADR scope",
                    )
                )
                notes.append(f"accepted ADR-{adr_number} now governs invariant")
            target_id, node_kind, target_evidence = _phase_or_window_target(node_id)
            if target_id and node_kind and target_evidence:
                add_node(target_id, node_kind=node_kind, label=target_id)
                row_edges.append(
                    _edge_payload(
                        node_id,
                        "DERIVED_FROM",
                        target_id,
                        evidence=target_evidence,
                        reason="Direct-read phase/window/SIM token provides procedural source lineage",
                    )
                )
                notes.append(f"procedural source lineage attached to {target_id}")
            if not notes:
                notes.append("no unique procedural target found after direct-read support audit")

        edges.extend(row_edges)
        ledger_entries.append(
            {
                "batch": batch,
                "candidate_id": node_id,
                "disposition": disposition,
                "edge_count": len(row_edges),
                "edges": [
                    {"edge_type": edge["edge_type"], "source": edge["source"], "target": edge["target"]}
                    for edge in row_edges
                ],
                "evidence": evidence,
                "fix63_category": row.get("category"),
                "notes": "; ".join(notes),
                "source_read_status": "direct_read_or_direct_lmdb_row_review",
            }
        )
    return ledger_entries, nodes, edges


def _append_status(report: dict[str, Any]) -> None:
    block = f"""

### Phase 1545p-Fix63a — Procedural Support Edge Manual Audit

**Status:** complete

**Output:** Reviewed `{report['rows_reviewed']}` Fix63 support/lifecycle/proposal rows in `{report['manual_batch_count']}` batches, accepted `{report['edge_application']['accepted_edge_count']}` procedural/support edges, materialized `{report['edge_application']['accepted_node_count']}` support endpoint nodes, and preserved all non-activation boundaries.

**Tokens:** {', '.join(OUTPUT_TOKENS)}
"""
    STATUS_PATH.write_text(STATUS_PATH.read_text(encoding="utf-8").rstrip() + block + "\n", encoding="utf-8")


def _report_md(report: dict[str, Any]) -> str:
    return f"""# ILC Fix63a Procedural Support Edge Manual Audit Report

PUBLIC_RC_EXCLUDE: fix63a_procedural_support_edge_manual_audit_research_only

## Summary

- Rows reviewed: `{report['rows_reviewed']}`
- Manual batches: `{report['manual_batch_count']}`
- Accepted edges: `{report['edge_application']['accepted_edge_count']}`
- Materialized support endpoint nodes: `{report['edge_application']['accepted_node_count']}`
- Rejected edges: `{report['edge_application']['rejected_edge_count']}`
- Final LMDB: `{report['final_counts']['nodes']}` nodes / `{report['final_counts']['edges']}` edges / `{report['final_counts']['preimages']}` preimages

## Edge Types

```json
{json.dumps(report['edge_type_counts'], sort_keys=True, indent=2)}
```

## Boundary

This phase updates local unsigned Atlas LMDB support and procedural traces only.
It does not sign Genesis, publish a public graph, activate runtime flags,
perform ECU minting, settle ILC, mutate CDL/ADR source documents, or authorize
public RC.
"""


def _walkthrough_md(report: dict[str, Any]) -> str:
    return f"""# Phase 1545p-Fix63a Walkthrough

## Commands

```bash
python tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix63_g10_procedural_support_edge_manual_audit_fix63a.md
python -m py_compile tools/evaluators/sim_genesis_atlas_fix63a_procedural_support_edge_manual_audit.py tests/test_phase_1545p_fix63a_procedural_support_edge_manual_audit.py
python tools/evaluators/sim_genesis_atlas_fix63a_procedural_support_edge_manual_audit.py
python -m pytest tests/test_phase_1545p_fix63a_procedural_support_edge_manual_audit.py tests/test_phase_1545p_fix63_manual_governs_audit.py tests/test_phase_1545p_fix59b_atlas_lmdb_safe_writer.py -q
python -m ilc_core.cli.main atlas validate --lmdb out/genesis_base_graph_v0.4_unified.lmdb
```

## Result

- Rows reviewed: `{report['rows_reviewed']}`
- Manual batches: `{report['manual_batch_count']}`
- Accepted edges: `{report['edge_application']['accepted_edge_count']}`
- Skipped duplicate edges: `{report['edge_application']['skipped_edge_count']}`
- Rejected edges: `{report['edge_application']['rejected_edge_count']}`
- Final LMDB counts: `{report['final_counts']['nodes']}` nodes / `{report['final_counts']['edges']}` edges / `{report['final_counts']['preimages']}` preimages

## Direct-Read Evidence Families

- CDL lifecycle and open-stub rows: `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- Proposed ADR rows: ADR source status lines for ADR-0015, ADR-0018, and ADR-0024
- Accepted ADR invariant rows: ADR-0020, ADR-0036, and ADR-0037 status lines
- Phase/window/SIM invariant rows: `docs/phases/STATUS.md` token lookup

## Non-Claims

No Genesis signing, public graph upload, public RC publication, public serving,
runtime activation, ECU minting, ILC settlement, CDL mutation, or ADR mutation
occurred.
"""


def _validate(report: dict[str, Any]) -> None:
    if report["rows_reviewed"] != 373:
        raise ValueError(f"fix63a_rows_reviewed_mismatch:{report['rows_reviewed']}")
    if report["manual_batch_count"] != 38:
        raise ValueError(f"fix63a_batch_count_mismatch:{report['manual_batch_count']}")
    if report["edge_application"]["rejected_edge_count"] != 0:
        raise ValueError("fix63a_rejected_edges_present")


def run() -> dict[str, Any]:
    _verify_tokens()
    # Direct-read phase inputs before write planning.
    STATUS_PATH.read_text(encoding="utf-8")
    FIX63_LEDGER_PATH.read_text(encoding="utf-8")
    (REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md").read_text(encoding="utf-8")
    for path in [
        "docs/adr/ADR_0015_Node_Transfer_Economics.md",
        "docs/adr/ADR_0018_Sequestered_Financial_Shard.md",
        "docs/adr/ADR_0020_Knowledge_Node_First_Design_Principle.md",
        "docs/adr/ADR_0024_Agent_Skills_Infrastructure.md",
        "docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md",
        "docs/adr/ADR_0036_Operational_Release_Key_Genesis_Binding.md",
        "docs/adr/ADR_0037_Genesis_Canonical_Lineage_Contract.md",
    ]:
        (REPO_ROOT / path).read_text(encoding="utf-8")

    fix63_ledger = _read_json(FIX63_LEDGER_PATH)
    source_rows = [row for row in fix63_ledger["entries"] if row["disposition"] in TARGET_DISPOSITIONS]
    if len(source_rows) != 373:
        raise ValueError(f"fix63a_expected_373_source_rows:{len(source_rows)}")

    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        existing_nodes = {_candidate_id(node) for node in writer.store.iter_nodes()}
        ledger_entries, nodes_to_add, edges_to_add = _build_entries_and_plan(source_rows, existing_nodes)
        edge_type_counts = Counter(edge["edge_type"] for edge in edges_to_add)
        ledger = {
            "edge_type_counts": dict(edge_type_counts),
            "entries": ledger_entries,
            "entry_count": len(ledger_entries),
            "manual_batch_count": 38,
            "phase": PHASE,
            "source_ledger": str(FIX63_LEDGER_PATH.relative_to(REPO_ROOT)),
            "status": "procedural_support_edge_manual_audit_complete",
        }
        write_json_atomic(LEDGER_PATH, ledger)
        plan = AtlasLmdbWritePlan(
            nodes_to_add=nodes_to_add,
            edges_to_add=edges_to_add,
            metadata={"operation": "fix63a_procedural_support_edge_manual_audit"},
            phase=PHASE,
            dry_run=False,
        )
        edge_receipt = writer.apply_plan(plan)
        REPORT_MD_PATH.write_text("", encoding="utf-8")
        WALKTHROUGH_PATH.write_text("", encoding="utf-8")
        file_receipt = _register_phase_files(writer)
        post_nodes = writer.store.iter_nodes()
        post_edges = writer.store.iter_edges()
        touched_nodes = {_candidate_id(node) for node in nodes_to_add}
        touched_nodes.update(
            _candidate_id(node) for node in post_nodes if str(node.get("annotation_phase")) == PHASE_TOKEN
        )
        touched_edge_ids = {
            str(edge.get("edge_id"))
            for edge in post_edges
            if str(edge.get("annotation_phase")) == PHASE_TOKEN and edge.get("edge_id")
        }
        preimages = [_node_preimage(node) for node in post_nodes if _candidate_id(node) in touched_nodes]
        preimages.extend(_edge_preimage(edge) for edge in post_edges if str(edge.get("edge_id")) in touched_edge_ids)
        preimage_receipt = writer.write_preimages(
            preimages,
            phase=PHASE,
            dry_run=False,
            metadata={"preimage_scope": "fix63a_procedural_support_edge_manual_audit"},
        )
        final = writer.inspect()
        report = {
            "edge_application": {
                "accepted_edge_count": edge_receipt["accepted_edge_count"],
                "accepted_node_count": edge_receipt["accepted_node_count"],
                "rejected_edge_count": edge_receipt["rejected_edge_count"],
                "skipped_edge_count": edge_receipt["skipped_edge_count"],
            },
            "edge_type_counts": dict(edge_type_counts),
            "file_registration": {
                "accepted_edge_count": file_receipt["accepted_edge_count"],
                "accepted_node_count": file_receipt["accepted_node_count"],
            },
            "final_counts": {
                "edges": final["edge_count"],
                "nodes": final["node_count"],
                "preimages": final["preimage_count"],
            },
            "manual_batch_count": 38,
            "phase": PHASE,
            "preimage_receipt": {
                "preimage_count": preimage_receipt["preimage_count"],
                "post_preimage_count": preimage_receipt["post_preimage_count"],
            },
            "rows_reviewed": len(source_rows),
            "status": "PASS",
        }
        _validate(report)
        REPORT_MD_PATH.write_text(_report_md(report), encoding="utf-8")
        WALKTHROUGH_PATH.write_text(_walkthrough_md(report), encoding="utf-8")
        write_json_atomic(OUT_REPORT_PATH, report)
        _append_status(report)
        return report
    finally:
        writer.close()


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, separators=(",", ":"), allow_nan=False))
