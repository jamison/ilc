#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Deterministic RC frontier gap audit for Phase 1250 Fix1.

This is a planning/audit tool, not runtime code. It re-runs the useful part of
the scratch Gemini crawl in a reproducible way and reconciles raw grep-style
signals against current canon before assigning phase routes.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


AUDIT_VERSION = "rc_frontier_gap_audit_1250_fix1.v0.1"
PHASE_TOKEN = "phase_1250_fix1_rc_frontier_gap_audit_complete"
GEMINI_RERUN_TOKEN = "phase_1250_fix1_improved_gemini_gap_study_rerun"

CANON_FILES = (
    "docs/PLANNING_INDEX.md",
    "docs/specs/ilc_antigravity_context_capsule_v5.50.md",
    "docs/phases/STATUS.md",
    "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md",
    "docs/specs/ilc_phase_1249_1256_sequence_lock_v0.1.md",
    "docs/specs/ilc_window_1249_1256_candidate_phase_grouping_v0.1.md",
    "docs/specs/ilc_cdl_087_governance_review_disposition_1246_v0.1.md",
)

CODE_SCAN_ROOTS = ("ilc_core", "ilc_consensus/src")
PHASE_DOC_ROOT = "docs/phases"
MAX_SCAN_FILE_BYTES = 5_000_000
MAX_MARKER_SAMPLES = 80

MARKERS = (
    "TODO",
    "FIXME",
    "MOCK",
    "mock",
    "deferred",
    "not public RC",
    "not authorized",
    "not ratified",
    "local-only",
    "no public",
)

CONTRADICTION_TOKENS = (
    "deferred",
    "blocked",
    "not authorized",
    "not ratified",
    "local-only",
    "no public",
    "superseded",
)


def _repo_relative(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def _read_text(path: Path) -> str:
    if path.stat().st_size > MAX_SCAN_FILE_BYTES:
        raise ValueError(f"rc_frontier_gap_audit_file_too_large:{path.as_posix()}")
    return path.read_text(encoding="utf-8")


def _iter_files(repo_root: Path, roots: Iterable[str], suffixes: tuple[str, ...]) -> list[Path]:
    files: list[Path] = []
    for root_name in roots:
        root = repo_root / root_name
        if not root.exists():
            continue
        if root.is_file() and root.suffix in suffixes:
            files.append(root)
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in suffixes and "__pycache__" not in path.parts:
                files.append(path)
    return sorted(set(files), key=lambda item: item.as_posix())


def _canon_texts(repo_root: Path) -> dict[str, str]:
    texts: dict[str, str] = {}
    for relative in CANON_FILES:
        path = repo_root / relative
        texts[relative] = _read_text(path) if path.exists() else ""
    return texts


def _contains_any(texts: dict[str, str], token: str) -> bool:
    return any(token in text for text in texts.values())


def _scan_digest_truncations(repo_root: Path) -> list[dict[str, Any]]:
    pattern = re.compile(r"(?:hexdigest|digest)\(\)\s*\[:\s*(\d+)\s*\]")
    hits: list[dict[str, Any]] = []
    for path in _iter_files(repo_root, CODE_SCAN_ROOTS, (".py", ".rs")):
        text = _read_text(path)
        relative = _repo_relative(path, repo_root)
        for line_no, line in enumerate(text.splitlines(), start=1):
            for match in pattern.finditer(line):
                route = "Phase 1252 chain/crypto dependency inventory"
                classification = "route_to_phase_1252"
                if "/network/" in f"/{relative}/" or relative.startswith("ilc_consensus/"):
                    route = "Phase 1253 TransportPrincipal and public-P2P substrate audit"
                    classification = "route_to_phase_1253"
                hits.append(
                    {
                        "classification": classification,
                        "digest_hex_chars": int(match.group(1)),
                        "line": line_no,
                        "route": route,
                        "source_path": relative,
                        "snippet": line.strip(),
                    }
                )
    return sorted(hits, key=lambda hit: (hit["source_path"], hit["line"], hit["snippet"]))


def _scan_rust_fixmes(repo_root: Path) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for path in _iter_files(repo_root, ("ilc_consensus/src",), (".rs",)):
        text = _read_text(path)
        relative = _repo_relative(path, repo_root)
        for line_no, line in enumerate(text.splitlines(), start=1):
            if "FIXME" not in line and "TODO" not in line:
                continue
            classification = "route_to_phase_1253"
            if "mock_" in line.lower():
                classification = "test_only_not_rc_blocker"
            hits.append(
                {
                    "classification": classification,
                    "line": line_no,
                    "route": (
                        "Phase 1253 Rust public-P2P/TransportPrincipal audit"
                        if classification == "route_to_phase_1253"
                        else "No current route; test-only marker"
                    ),
                    "source_path": relative,
                    "snippet": line.strip(),
                }
            )
    return sorted(hits, key=lambda hit: (hit["source_path"], hit["line"], hit["snippet"]))


def _scan_literal_hits(repo_root: Path, roots: Iterable[str], literals: tuple[str, ...]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for path in _iter_files(repo_root, roots, (".py", ".rs", ".md")):
        text = _read_text(path)
        relative = _repo_relative(path, repo_root)
        for line_no, line in enumerate(text.splitlines(), start=1):
            lower = line.lower()
            matched = [literal for literal in literals if literal.lower() in lower]
            if matched:
                hits.append(
                    {
                        "line": line_no,
                        "markers": sorted(set(matched)),
                        "source_path": relative,
                        "snippet": line.strip(),
                    }
                )
    return sorted(hits, key=lambda hit: (hit["source_path"], hit["line"], hit["snippet"]))


def _legacy_phase_scan(repo_root: Path) -> dict[str, Any]:
    phase_root = repo_root / PHASE_DOC_ROOT
    phase_docs = _iter_files(repo_root, (PHASE_DOC_ROOT,), (".md",))
    missing_graph_delta: list[str] = []
    marker_counts: Counter[str] = Counter()
    marker_sample_hits: list[dict[str, Any]] = []

    for path in phase_docs:
        relative = _repo_relative(path, repo_root)
        text = _read_text(path)
        stem = path.stem.lower()
        closure_or_handoff = "closure" in stem or "handoff" in stem
        if closure_or_handoff and "graph_delta=" not in text:
            missing_graph_delta.append(relative)

        for line_no, line in enumerate(text.splitlines(), start=1):
            lower = line.lower()
            matched_markers = [marker for marker in MARKERS if marker.lower() in lower]
            for marker in matched_markers:
                marker_counts[marker] += 1
            if matched_markers and len(marker_sample_hits) < MAX_MARKER_SAMPLES:
                marker_sample_hits.append(
                    {
                        "line": line_no,
                        "markers": sorted(set(matched_markers)),
                        "source_path": relative,
                        "snippet": line.strip(),
                    }
                )

    return {
        "classification": "legacy_doc_hygiene",
        "marker_counts": dict(sorted(marker_counts.items())),
        "marker_sample_hit_limit": MAX_MARKER_SAMPLES,
        "marker_sample_hits": marker_sample_hits,
        "missing_graph_delta_closure_or_handoff_count": len(missing_graph_delta),
        "missing_graph_delta_closure_or_handoff_files": sorted(missing_graph_delta),
        "phase_doc_count": len(phase_docs),
        "phase_doc_root": phase_root.relative_to(repo_root).as_posix(),
        "route": "Phase 1254 ATLAS-G backfill plan; do not batch-edit legacy docs in Phase 1251",
    }


def _current_canon(repo_root: Path) -> dict[str, Any]:
    texts = _canon_texts(repo_root)
    return {
        "canonical_sources": list(CANON_FILES),
        "cdl_086": {
            "classification": "resolved_stale",
            "status": "ratified" if _contains_any(texts, "cdl_086_ratified_phase_1220") else "unknown",
            "token": "cdl_086_ratified_phase_1220",
        },
        "cdl_087": {
            "classification": "current_blocker",
            "status": (
                "open_prelocked_not_ratified"
                if _contains_any(texts, "OPEN / PRELOCKED / NOT RATIFIED")
                else "unknown"
            ),
            "token": "cdl_087_ratification_deferred_pending_production_candidate_fetch_evidence",
        },
        "current_frontier": {
            "phase_1250_complete": _contains_any(texts, "phase_1250_gap14_adapter_extraction_complete"),
            "phase_1251_next": _contains_any(
                texts,
                "Phase 1251 - Gap 14 package CI gate, profile export audit, package-size measurement",
            ),
            "phase_1252_sensitive": _contains_any(texts, "phase_1252_gap13_claimability_boundary_requires_explicit_go"),
        },
        "non_claims": {
            "no_public_rc_claim": _contains_any(texts, "public RC claim"),
            "no_public_p2p": _contains_any(texts, "no public ILC-owned P2P claim"),
            "v0_2_signing_deferred": _contains_any(texts, "v0_2_signing_ceremony_deferred_pending_signing_authorization"),
        },
    }


def _build_findings(
    *,
    canon: dict[str, Any],
    legacy_scan: dict[str, Any],
    digest_hits: list[dict[str, Any]],
    rust_fixmes: list[dict[str, Any]],
    claimability_hits: list[dict[str, Any]],
    deferred_transport_hits: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    security_digest_sources = sorted(
        {
            hit["source_path"]
            for hit in digest_hits
            if hit["classification"] == "route_to_phase_1252"
        }
    )
    network_digest_sources = sorted(
        {
            hit["source_path"]
            for hit in digest_hits
            if hit["classification"] == "route_to_phase_1253"
        }
    )
    active_rust_fixmes = [hit for hit in rust_fixmes if hit["classification"] == "route_to_phase_1253"]

    findings = [
        {
            "classification": "route_to_phase_1251",
            "evidence": "Phase 1250 closed ilc_logic adapter-import debt; current canon still lists package CI, profile export audit, and package-size measurement as next.",
            "finding_id": "RCGAP-1250-FIX1-001",
            "route": "Phase 1251",
            "severity": "high",
            "source_paths": [
                "docs/PLANNING_INDEX.md",
                "docs/phases/STATUS.md",
                "docs/specs/ilc_phase_1249_1256_sequence_lock_v0.1.md",
            ],
            "title": "Gap 14 immediate next step remains package CI/profile audit/size measurement.",
        },
        {
            "classification": "legacy_doc_hygiene",
            "evidence": (
                f"{legacy_scan['missing_graph_delta_closure_or_handoff_count']} closure/handoff "
                "phase docs lack graph_delta markers. These are legacy/historical hygiene holes, not current public-RC blockers."
            ),
            "finding_id": "RCGAP-1250-FIX1-002",
            "route": "Phase 1254 ATLAS-G backfill planning, not Phase 1251 package CI",
            "severity": "low",
            "source_paths": legacy_scan["missing_graph_delta_closure_or_handoff_files"][:20],
            "title": "Legacy graph_delta gaps should be classified before any bulk backfill.",
        },
        {
            "classification": "route_to_phase_1252",
            "evidence": (
                f"{len(security_digest_sources)} security/ledger/code surfaces contain truncated digest identifiers. "
                "Some may be human-readable fingerprints, but Phase 1252 should classify which are security-binding."
            ),
            "finding_id": "RCGAP-1250-FIX1-003",
            "route": "Phase 1252 chain/crypto dependency inventory",
            "severity": "medium",
            "source_paths": security_digest_sources,
            "title": "Digest truncation candidates require chain/crypto classification before public claimability.",
        },
        {
            "classification": "route_to_phase_1253",
            "evidence": (
                f"{len(network_digest_sources)} network/consensus surfaces contain truncated digest identifiers "
                "or transport-adjacent fingerprints that should be assessed with TransportPrincipal work."
            ),
            "finding_id": "RCGAP-1250-FIX1-004",
            "route": "Phase 1253 TransportPrincipal and public-P2P substrate audit",
            "severity": "medium",
            "source_paths": network_digest_sources,
            "title": "Network digest/fingerprint truncations route to TransportPrincipal audit.",
        },
        {
            "classification": "route_to_phase_1253",
            "evidence": (
                "Rust consensus contains an active M-5 FIXME: f is captured at NodeRunner::new() and not updated. "
                "This does not block OpenClaw/NemoClaw local package work but matters for public-P2P substrate confidence."
            ),
            "finding_id": "RCGAP-1250-FIX1-005",
            "route": "Phase 1253 Rust public-P2P/TransportPrincipal audit",
            "severity": "medium",
            "source_paths": sorted({hit["source_path"] for hit in active_rust_fixmes}),
            "title": "Rust M-5 FIXME is real and should not be lost in generic marker noise.",
        },
        {
            "classification": "phase_1252_sensitive_gate",
            "evidence": (
                f"{len(claimability_hits)} current code/canon hits keep claimability deferred or blocked. "
                "This confirms Phase 1252 must inventory dependencies without activating wallet withdrawal/transfer/spend semantics."
            ),
            "finding_id": "RCGAP-1250-FIX1-006",
            "route": "Phase 1252 after explicit GO Phase 1252",
            "severity": "high",
            "source_paths": sorted({hit["source_path"] for hit in claimability_hits}),
            "title": "Public claimability remains deferred and sensitive.",
        },
        {
            "classification": "current_blocker",
            "evidence": (
                "CDL-087 is open/prelocked/not ratified. Current canon narrows remaining blockers to "
                "production-candidate fetch evidence and later sensitive ratification, not generic SIM-FETCH incompleteness."
            ),
            "finding_id": "RCGAP-1250-FIX1-007",
            "route": "Future sensitive CDL-087 evidence/ratification phase; not Phase 1251",
            "severity": "high",
            "source_paths": [
                "docs/specs/ilc_cdl_087_governance_review_disposition_1246_v0.1.md",
                "docs/specs/ilc_phase_1249_1256_sequence_lock_v0.1.md",
            ],
            "title": "CDL-087 remains a public sidecar/fetch blocker, but current blocker wording matters.",
        },
        {
            "classification": "route_to_phase_1253",
            "evidence": (
                f"{len(deferred_transport_hits)} transport or gossip hits preserve deferred/public-P2P boundaries. "
                "Dynamic discovery and non-loopback exposure should stay in TransportPrincipal routing."
            ),
            "finding_id": "RCGAP-1250-FIX1-008",
            "route": "Phase 1253",
            "severity": "medium",
            "source_paths": sorted({hit["source_path"] for hit in deferred_transport_hits}),
            "title": "Deferred peer discovery/HTTP surfaces are public-P2P lane work, not skill-first package blockers.",
        },
        {
            "classification": "needs_human_gate",
            "evidence": "v0.2 signing remains explicitly deferred pending signing authorization.",
            "finding_id": "RCGAP-1250-FIX1-009",
            "route": "Human signing authorization gate; no current-window code task",
            "severity": "high",
            "source_paths": [
                "docs/specs/ilc_antigravity_context_capsule_v5.50.md",
                "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md",
            ],
            "title": "v0.2 signing is not unlocked by gap scraping.",
        },
        {
            "classification": "resolved_stale",
            "evidence": (
                f"Current canon status for CDL-086 is {canon['cdl_086']['status']}; stale reports that "
                "treat CDL-086 as deferred should be ignored for current sequencing."
            ),
            "finding_id": "RCGAP-1250-FIX1-010",
            "route": "No action",
            "severity": "info",
            "source_paths": [
                "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md",
                "docs/specs/ilc_cdl_086_ratification_evidence_1220_v0.1.md",
            ],
            "title": "CDL-086 deferred status is stale.",
        },
    ]
    return sorted(findings, key=lambda finding: finding["finding_id"])


def build_audit(repo_root: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    canon = _current_canon(repo_root)
    legacy_scan = _legacy_phase_scan(repo_root)
    digest_hits = _scan_digest_truncations(repo_root)
    rust_fixmes = _scan_rust_fixmes(repo_root)
    claimability_hits = _scan_literal_hits(
        repo_root,
        ("ilc_core/ledger", "ilc_core/protocol", "docs/specs/ilc_phase_1249_1256_sequence_lock_v0.1.md"),
        ("claimability_state", "public claimability", "wallet withdrawal", "transfer", "spend semantics"),
    )
    deferred_transport_hits = _scan_literal_hits(
        repo_root,
        ("ilc_core/network", "ilc_consensus/src", "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"),
        ("deferred", "TransportPrincipal", "public P2P", "no public", "mock"),
    )
    findings = _build_findings(
        canon=canon,
        legacy_scan=legacy_scan,
        digest_hits=digest_hits,
        rust_fixmes=rust_fixmes,
        claimability_hits=claimability_hits,
        deferred_transport_hits=deferred_transport_hits,
    )
    return {
        "audit_scope": {
            "code_scan_roots": list(CODE_SCAN_ROOTS),
            "contradiction_tokens": list(CONTRADICTION_TOKENS),
            "legacy_phase_doc_root": PHASE_DOC_ROOT,
            "phase": "1250 Fix1",
            "purpose": "Reproducible canon-aware rerun of RC frontier gap scraping before Phase 1251.",
            "tokens": [PHASE_TOKEN, GEMINI_RERUN_TOKEN],
        },
        "code_scans": {
            "claimability_hits": claimability_hits,
            "deferred_transport_hits": deferred_transport_hits,
            "digest_truncation_hits": digest_hits,
            "rust_fixme_hits": rust_fixmes,
        },
        "current_canon": canon,
        "findings": findings,
        "legacy_phase_scan": legacy_scan,
        "non_authorization_boundary": [
            "no_public_rc_claim",
            "no_public_repository_publication",
            "no_public_p2p_exposure",
            "no_public_sidecar_projection_serving",
            "no_public_claimability_activation",
            "no_wallet_withdrawal_transfer_spend_semantics",
            "no_cdl_mutation",
            "no_cdl_087_ratification",
            "no_release_key_generation",
            "no_v0_2_signing",
        ],
        "recommended_next_phase": "Phase 1251 - Gap 14 package CI gate, profile export audit, package-size measurement.",
        "version": AUDIT_VERSION,
    }


def export_audit_json(audit: dict[str, Any]) -> str:
    return json.dumps(audit, allow_nan=False, indent=2, sort_keys=True) + "\n"


def export_audit_markdown(audit: dict[str, Any]) -> str:
    findings = audit["findings"]
    legacy = audit["legacy_phase_scan"]
    digest_hits = audit["code_scans"]["digest_truncation_hits"]
    rust_fixmes = audit["code_scans"]["rust_fixme_hits"]
    lines = [
        "# ILC RC Frontier Gap Audit 1250 Fix1 v0.1",
        "",
        "**Phase:** 1250 Fix1",
        f"**Version:** `{audit['version']}`",
        f"**Token:** `{PHASE_TOKEN}`",
        f"**Rerun token:** `{GEMINI_RERUN_TOKEN}`",
        "**Status:** COMPLETE",
        "",
        "## Verdict",
        "",
        "The improved study treats grep results as leads, not authority. Current canon keeps "
        "Phase 1251 as the next non-sensitive package-readiness phase, routes chain/crypto "
        "and claimability work to sensitive Phase 1252, routes transport/Rust/P2P findings "
        "to Phase 1253, and classifies legacy graph_delta gaps as ATLAS-G hygiene rather "
        "than immediate public-RC blockers.",
        "",
        "## Current Routing",
        "",
        "| Route | Classification | Summary |",
        "|-------|----------------|---------|",
    ]
    for finding in findings:
        lines.append(
            f"| {finding['route']} | `{finding['classification']}` | {finding['title']} |"
        )
    lines.extend(
        [
            "",
            "## Scan Metrics",
            "",
            f"- Phase docs scanned: `{legacy['phase_doc_count']}`.",
            (
                "- Closure/handoff phase docs missing `graph_delta=`: "
                f"`{legacy['missing_graph_delta_closure_or_handoff_count']}` "
                "(classified as `legacy_doc_hygiene`)."
            ),
            f"- Digest truncation candidates: `{len(digest_hits)}`.",
            f"- Rust TODO/FIXME hits: `{len(rust_fixmes)}`.",
            "",
            "## Key Corrections To Scratch-Only Gap Crawls",
            "",
            "- CDL-086 is ratified by Phase 1220; do not treat it as a deferred current blocker.",
            "- CDL-087 is still open/prelocked/not ratified, but the blocker is now production-candidate fetch evidence plus later sensitive ratification.",
            "- v0.2 signing remains deferred pending explicit signing authorization.",
            "- Missing graph_delta markers in older closure/handoff docs are real hygiene debt, but not a reason to stop Phase 1251.",
            "- Digest truncation findings need code-context classification before mutation; many may be display tags rather than security roots.",
            "",
            "## Graph Delta",
            "",
            "```text",
            "graph_delta=support_only:docs/specs/ilc_rc_frontier_gap_audit_1250_fix1_v0.1.json -> planning/frontier",
            "graph_delta=support_only:docs/specs/ilc_rc_frontier_gap_audit_1250_fix1_v0.1.md -> planning/frontier",
            "graph_delta=support_only:tools/rc_frontier_gap_audit.py -> validation",
            "```",
            "",
            "## Non-Authorization Boundary",
            "",
        ]
    )
    for token in audit["non_authorization_boundary"]:
        lines.append(f"- `{token}`")
    lines.extend(
        [
            "",
            "## Next Phase",
            "",
            audit["recommended_next_phase"],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--json-out", required=True, help="Canonical JSON output path")
    parser.add_argument("--markdown-out", required=True, help="Markdown summary output path")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    audit = build_audit(repo_root)
    json_out = Path(args.json_out)
    markdown_out = Path(args.markdown_out)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    markdown_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(export_audit_json(audit), encoding="utf-8")
    markdown_out.write_text(export_audit_markdown(audit), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
