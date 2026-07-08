#!/usr/bin/env python3
"""Compare the proposed Genesis core star-map against observed repo evidence.

This is a research/atlas tool only. It derives an observed hypergraph from
deterministic repo scans and compares that graph to the curated core star-map.
It does not mutate protocol runtime state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


DEFAULT_STAR_MAP = Path("out/genesis_core_star_map_v0.1.json")
DEFAULT_CRAWL = Path("out/genesis_node_candidate_crawl.json")
DEFAULT_OBSERVED_OUT = Path("out/genesis_observed_repo_hypergraph_v0.1.json")
DEFAULT_GAP_OUT = Path("out/genesis_core_star_map_gap_analysis_v0.1.json")
DEFAULT_REPORT_OUT = Path("docs/sims/sim_spectral_02/genesis_core_star_map_gap_analysis_v0.1.md")

OBSERVED_REPO_HYPERGRAPH_COMPILER_VERSION = "observed_repo_hypergraph_compiler_1247.v0.1"
MAX_SCAN_FILES = 20_000
MAX_SCAN_FILE_BYTES = 3_000_000
MAX_SCAN_LINES_PER_FILE = 200_000
MAX_OBSERVED_VERTICES = 250_000
MAX_OBSERVED_HYPEREDGES = 250_000
MAX_OBSERVED_INCIDENCE = 750_000

SCAN_ROOTS = (Path("docs"), Path("config"), Path("ilc_core"), Path("tools"), Path("tests"))
SKIP_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "out",
    "venv",
}
TEXT_SUFFIXES = {".json", ".md", ".py", ".toml", ".txt", ".yaml", ".yml"}

REFERENCE_RE = re.compile(r"\b(?:ADR[-_ ]?0*\d{1,4}|CDL-\d{3}|Phase\s+\d{3,4})\b", re.IGNORECASE)
SYMBOL_RE = re.compile(r"\b[A-Z][A-Z0-9_]{2,}\b")
GENESIS_TERMS = (
    "genesis",
    "truth primitive",
    "assert.truth",
    "validate.claim",
    "refute.claim",
    "star.map",
    "provenance",
    "morphogen",
    "hypergraph",
)


@dataclass
class Vertex:
    vertex_id: str
    vertex_type: str
    label: str
    properties: dict[str, Any] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "properties": self.properties,
            "vertex_id": self.vertex_id,
            "vertex_type": self.vertex_type,
        }


@dataclass
class Hyperedge:
    hyperedge_id: str
    hyperedge_type: str
    members: list[dict[str, str]]
    evidence: list[dict[str, Any]]
    features: dict[str, Any] = field(default_factory=dict)
    relation: str = ""

    def as_json(self) -> dict[str, Any]:
        return {
            "evidence": self.evidence,
            "features": self.features,
            "hyperedge_id": self.hyperedge_id,
            "hyperedge_type": self.hyperedge_type,
            "members": self.members,
            "relation": self.relation,
        }


def _stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}:{digest}"


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object: {path}")
    return data


def _iter_text_files(roots: Iterable[Path], max_files: int = MAX_SCAN_FILES) -> Iterable[Path]:
    yielded = 0
    for root in roots:
        if not root.exists():
            continue
        if root.is_file():
            if root.suffix in TEXT_SUFFIXES:
                yielded += 1
                if yielded > max_files:
                    raise ValueError("observed_repo_hypergraph_scan_file_limit_exceeded")
                yield root
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix not in TEXT_SUFFIXES:
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            yielded += 1
            if yielded > max_files:
                raise ValueError("observed_repo_hypergraph_scan_file_limit_exceeded")
            yield path


def _read_lines(path: Path) -> list[str]:
    try:
        if path.stat().st_size > MAX_SCAN_FILE_BYTES:
            return []
        lines: list[str] = []
        contains_genesis_term = False
        with path.open("r", encoding="utf-8") as handle:
            for line_no, raw_line in enumerate(handle, start=1):
                if line_no > MAX_SCAN_LINES_PER_FILE:
                    raise ValueError("observed_repo_hypergraph_scan_file_line_limit_exceeded")
                line = raw_line.rstrip("\n\r")
                lines.append(line)
                lowered = line.lower()
                if not contains_genesis_term and any(term in lowered for term in GENESIS_TERMS):
                    contains_genesis_term = True
    except UnicodeDecodeError:
        return []
    if not contains_genesis_term:
        return []
    return lines


def _node_aliases(node: dict[str, Any]) -> list[str]:
    aliases = {
        str(node["candidate_id"]),
        str(node.get("label", "")),
    }
    symbol = node.get("symbol")
    if symbol:
        aliases.add(str(symbol))
    for evidence in node.get("evidence", []):
        evidence_text = str(evidence.get("evidence_text", "")).strip()
        if evidence_text and len(evidence_text) <= 120:
            aliases.add(evidence_text)
    if node["candidate_id"].startswith("truth_primitive:"):
        aliases.add(node["candidate_id"].split(":", 1)[1])
    if node["candidate_id"].startswith("policy:genesis_theta_hard"):
        aliases.update({"theta_hard", "5% hard cap", "0.05"})
    if node["candidate_id"].startswith("policy:genesis_theta_soft"):
        aliases.update({"theta_soft", "exp(-3)"})
    if node["candidate_id"].startswith("policy:provenance_decay_alpha"):
        aliases.update({"PROVENANCE_DECAY_ALPHA", "Decimal(\"0.45\")", "0.45"})
    return sorted(alias for alias in aliases if alias)


def _is_generated_artifact(path: Path) -> bool:
    text = path.as_posix()
    return text.startswith("out/genesis_") or text.endswith("genesis_core_star_map_gap_analysis_v0.1.md")


def _source_kind(path: Path) -> str:
    text = path.as_posix()
    if text.startswith("docs/adr/"):
        return "adr"
    if text.startswith("docs/specs/"):
        return "spec"
    if text.startswith("docs/research/"):
        return "research"
    if text.startswith("docs/phases/"):
        return "phase_doc"
    if text.startswith("config/"):
        return "config"
    if text.startswith("ilc_core/"):
        return "runtime_or_schema"
    if text.startswith("tools/"):
        return "tool"
    if text.startswith("tests/"):
        return "test"
    return "other"


def _authority_score(path: Path) -> int:
    kind = _source_kind(path)
    return {
        "config": 90,
        "runtime_or_schema": 85,
        "adr": 80,
        "spec": 75,
        "test": 65,
        "phase_doc": 60,
        "tool": 55,
        "research": 45,
        "other": 20,
    }.get(kind, 20)


def _add_vertex(vertices: dict[str, Vertex], vertex: Vertex) -> None:
    if vertex.vertex_id not in vertices and len(vertices) >= MAX_OBSERVED_VERTICES:
        raise ValueError("observed_repo_hypergraph_vertex_limit_exceeded")
    vertices.setdefault(vertex.vertex_id, vertex)


def _add_hyperedge(hyperedges: dict[str, Hyperedge], hyperedge: Hyperedge) -> None:
    if hyperedge.hyperedge_id not in hyperedges and len(hyperedges) >= MAX_OBSERVED_HYPEREDGES:
        raise ValueError("observed_repo_hypergraph_hyperedge_limit_exceeded")
    hyperedges[hyperedge.hyperedge_id] = hyperedge


def _source_vertex(path: Path) -> Vertex:
    path_text = path.as_posix()
    return Vertex(
        vertex_id=f"source:{path_text}",
        vertex_type="source_file",
        label=path_text,
        properties={
            "authority_score": _authority_score(path),
            "source_kind": _source_kind(path),
        },
    )


def _build_observed_hypergraph(star_map: dict[str, Any], crawl: dict[str, Any]) -> dict[str, Any]:
    star_nodes = {node["candidate_id"]: node for node in star_map["nodes"]}
    crawl_nodes = {node["candidate_id"]: node for node in crawl["nodes"]}
    vertices: dict[str, Vertex] = {}
    hyperedges: dict[str, Hyperedge] = {}
    support_counts: Counter[str] = Counter()
    direct_support_counts: Counter[str] = Counter()
    co_mention_counts: Counter[tuple[str, str]] = Counter()
    observed_symbols: Counter[str] = Counter()
    observed_references: Counter[str] = Counter()

    for node_id, node in star_nodes.items():
        _add_vertex(
            vertices,
            Vertex(
                vertex_id=node_id,
                vertex_type="core_star_map_node",
                label=str(node.get("label", node_id)),
                properties={
                    "category": node.get("category"),
                    "canonicality_tier": node.get("canonicality_tier"),
                    "inclusion_status": node.get("inclusion_status"),
                    "layer": node.get("layer"),
                    "node_kind": node.get("node_kind"),
                },
            ),
        )

    aliases_by_node = {
        node_id: tuple(alias.lower() for alias in _node_aliases(node))
        for node_id, node in star_nodes.items()
    }
    symbol_nodes = {node.get("symbol"): node_id for node_id, node in star_nodes.items() if node.get("symbol")}

    scanned_file_count = 0
    for path in _iter_text_files(SCAN_ROOTS):
        if _is_generated_artifact(path):
            continue
        lines = _read_lines(path)
        if not lines:
            continue
        source_v = _source_vertex(path)
        scanned_file_count += 1
        _add_vertex(vertices, source_v)

        mentioned_nodes: set[str] = set()
        for line_no, line in enumerate(lines, start=1):
            lowered = line.lower()
            line_nodes: set[str] = set()
            for node_id, aliases in aliases_by_node.items():
                if any(alias in lowered for alias in aliases):
                    mentioned_nodes.add(node_id)
                    line_nodes.add(node_id)
                    support_counts[node_id] += 1
                    evidence = {
                        "source_line": line_no,
                        "source_path": path.as_posix(),
                        "text_hash": hashlib.sha256(line.strip().encode("utf-8")).hexdigest(),
                    }
                    edge_id = _stable_id("he:mentions", path.as_posix(), str(line_no), node_id)
                    _add_hyperedge(
                        hyperedges,
                        Hyperedge(
                            hyperedge_id=edge_id,
                            hyperedge_type="OBSERVED_MENTION",
                            relation="source_mentions_core_node",
                            members=[
                                {"role": "source", "vertex": source_v.vertex_id},
                                {"role": "mentioned", "vertex": node_id},
                            ],
                            evidence=[evidence],
                            features={
                                "authority_score": _authority_score(path),
                                "source_kind": _source_kind(path),
                            },
                        ),
                    )
            for left in sorted(line_nodes):
                for right in sorted(line_nodes):
                    if left < right:
                        co_mention_counts[(left, right)] += 1

            for symbol in SYMBOL_RE.findall(line):
                if symbol in symbol_nodes:
                    observed_symbols[symbol] += 1
                    symbol_id = f"symbol:{symbol}"
                    _add_vertex(
                        vertices,
                        Vertex(
                            vertex_id=symbol_id,
                            vertex_type="symbol",
                            label=symbol,
                            properties={"core_node": symbol_nodes[symbol]},
                        ),
                    )
                    edge_id = _stable_id("he:symbol", path.as_posix(), str(line_no), symbol)
                    _add_hyperedge(
                        hyperedges,
                        Hyperedge(
                            hyperedge_id=edge_id,
                            hyperedge_type="SYMBOL_OCCURRENCE",
                            relation="source_contains_symbol",
                            members=[
                                {"role": "source", "vertex": source_v.vertex_id},
                                {"role": "symbol", "vertex": symbol_id},
                                {"role": "semantic_node", "vertex": symbol_nodes[symbol]},
                            ],
                            evidence=[
                                {
                                    "source_line": line_no,
                                    "source_path": path.as_posix(),
                                    "text_hash": hashlib.sha256(line.strip().encode("utf-8")).hexdigest(),
                                }
                            ],
                            features={"source_kind": _source_kind(path)},
                        ),
                    )

            for reference in REFERENCE_RE.findall(line):
                normalized = reference.upper().replace("_", "-").replace(" ", "-")
                observed_references[normalized] += 1

        for node_id in mentioned_nodes:
            node = crawl_nodes.get(node_id, star_nodes[node_id])
            for evidence in node.get("evidence", []):
                if evidence.get("source_path") == path.as_posix():
                    direct_support_counts[node_id] += 1

    for edge in star_map["edges"]:
        source = edge["source"]
        target = edge["target"]
        if source not in star_nodes or target not in star_nodes:
            continue
        edge_id = f"he:star_map_edge:{edge['edge_id']}"
        _add_hyperedge(
            hyperedges,
            Hyperedge(
                hyperedge_id=edge_id,
                hyperedge_type="PROPOSED_CORE_EDGE",
                relation=edge.get("relation", ""),
                members=[
                    {"role": "source", "vertex": source},
                    {"role": "target", "vertex": target},
                ],
                evidence=[
                    {
                        "edge_id": edge["edge_id"],
                        "edge_type": edge["edge_type"],
                        "source": source,
                        "target": target,
                    }
                ],
                features={
                    "co_mention_count": co_mention_counts.get((min(source, target), max(source, target)), 0),
                    "edge_type": edge["edge_type"],
                    "proposed_edge_type": edge.get("feature_hints", {}).get("proposed_edge_type", False),
                    "sim_weight_seed": edge.get("feature_hints", {}).get("sim_weight_seed"),
                },
            ),
        )

    incidence = []
    for hyperedge in hyperedges.values():
        for member in hyperedge.members:
            if len(incidence) >= MAX_OBSERVED_INCIDENCE:
                raise ValueError("observed_repo_hypergraph_incidence_limit_exceeded")
            incidence.append(
                {
                    "hyperedge_id": hyperedge.hyperedge_id,
                    "role": member["role"],
                    "vertex": member["vertex"],
                }
            )

    observed = {
        "metadata": {
            "compiler_version": OBSERVED_REPO_HYPERGRAPH_COMPILER_VERSION,
            "description": "Observed repo/governance hypergraph derived from deterministic source scans.",
            "format_version": "genesis_observed_repo_hypergraph.v0.1",
            "limits": {
                "max_observed_hyperedges": MAX_OBSERVED_HYPEREDGES,
                "max_observed_incidence": MAX_OBSERVED_INCIDENCE,
                "max_observed_vertices": MAX_OBSERVED_VERTICES,
                "max_scan_file_bytes": MAX_SCAN_FILE_BYTES,
                "max_scan_files": MAX_SCAN_FILES,
                "max_scan_lines_per_file": MAX_SCAN_LINES_PER_FILE,
            },
            "scan_roots": [path.as_posix() for path in SCAN_ROOTS],
            "scanned_source_file_count": scanned_file_count,
            "source_core_star_map": str(DEFAULT_STAR_MAP),
            "source_crawl": str(DEFAULT_CRAWL),
        },
        "vertices": [vertices[key].as_json() for key in sorted(vertices)],
        "hyperedges": [hyperedges[key].as_json() for key in sorted(hyperedges)],
        "incidence": sorted(incidence, key=lambda row: (row["hyperedge_id"], row["vertex"], row["role"])),
        "observed_counts": {
            "direct_support_by_core_node": dict(sorted(direct_support_counts.items())),
            "mentions_by_core_node": dict(sorted(support_counts.items())),
            "references": dict(sorted(observed_references.items())),
            "symbols": dict(sorted(observed_symbols.items())),
        },
    }
    _enforce_observed_bounds(observed)
    return observed


def _enforce_observed_bounds(observed: dict[str, Any]) -> None:
    if len(observed["vertices"]) > MAX_OBSERVED_VERTICES:
        raise ValueError("observed_repo_hypergraph_vertex_limit_exceeded")
    if len(observed["hyperedges"]) > MAX_OBSERVED_HYPEREDGES:
        raise ValueError("observed_repo_hypergraph_hyperedge_limit_exceeded")
    if len(observed["incidence"]) > MAX_OBSERVED_INCIDENCE:
        raise ValueError("observed_repo_hypergraph_incidence_limit_exceeded")


def _gap_analysis(star_map: dict[str, Any], observed: dict[str, Any]) -> dict[str, Any]:
    star_nodes = {node["candidate_id"]: node for node in star_map["nodes"]}
    mention_counts = Counter(observed["observed_counts"]["mentions_by_core_node"])
    direct_counts = Counter(observed["observed_counts"]["direct_support_by_core_node"])
    symbol_counts = Counter(observed["observed_counts"]["symbols"])
    source_vertices = [v for v in observed["vertices"] if v["vertex_type"] == "source_file"]
    proposed_edges = [
        edge
        for edge in star_map["edges"]
        if edge.get("feature_hints", {}).get("proposed_edge_type") is True
    ]
    proposed_edges_without_comention = []
    for hyperedge in observed["hyperedges"]:
        if hyperedge["hyperedge_type"] != "PROPOSED_CORE_EDGE":
            continue
        if hyperedge["features"].get("co_mention_count") == 0:
            proposed_edges_without_comention.append(hyperedge["evidence"][0]["edge_id"])

    core_without_direct_support = [
        {
            "candidate_id": node_id,
            "label": star_nodes[node_id].get("label"),
            "mention_count": mention_counts.get(node_id, 0),
            "reason": "core_star_map_node_has_no_source_path_evidence_match_in_observed_scan",
        }
        for node_id in sorted(star_nodes)
        if direct_counts.get(node_id, 0) == 0
    ]
    low_observed_support = [
        {
            "candidate_id": node_id,
            "label": star_nodes[node_id].get("label"),
            "mention_count": mention_counts.get(node_id, 0),
            "reason": "core_star_map_node_has_fewer_than_two_observed_mentions",
        }
        for node_id in sorted(star_nodes)
        if mention_counts.get(node_id, 0) < 2
    ]
    symbol_nodes_without_occurrence = [
        {
            "candidate_id": node["candidate_id"],
            "symbol": node.get("symbol"),
            "reason": "core_symbol_not_seen_in_observed_scan",
        }
        for node in sorted(star_map["nodes"], key=lambda item: item["candidate_id"])
        if node.get("symbol") and symbol_counts.get(node["symbol"], 0) == 0
    ]
    observed_reference_not_core = []
    core_ref_tokens = set()
    for node_id in star_nodes:
        if node_id.startswith("adr:"):
            core_ref_tokens.add("ADR-" + node_id.split(":")[1].split("_", 1)[0])
        if node_id.startswith("cdl:"):
            core_ref_tokens.add("CDL-" + node_id.split(":")[1].split("_", 1)[0])
    for ref, count in sorted(observed["observed_counts"]["references"].items()):
        normalized = ref.replace("ADR-", "ADR-").replace("CDL-", "CDL-")
        if normalized.startswith("ADR-"):
            number = normalized.split("-")[1].zfill(4)
            token = f"ADR-{number}"
        elif normalized.startswith("CDL-"):
            token = normalized
        else:
            continue
        if token not in core_ref_tokens and count >= 3:
            observed_reference_not_core.append(
                {
                    "reference": token,
                    "observed_count": count,
                    "reason": "frequently_observed_governance_reference_not_in_core_star_map",
                }
            )

    return {
        "metadata": {
            "compiler_version": OBSERVED_REPO_HYPERGRAPH_COMPILER_VERSION,
            "description": "Gap analysis comparing observed repo hypergraph to proposed Genesis core star-map.",
            "format_version": "genesis_core_star_map_gap_analysis.v0.1",
            "source_observed_hypergraph": str(DEFAULT_OBSERVED_OUT),
            "source_core_star_map": str(DEFAULT_STAR_MAP),
        },
        "summary": {
            "core_edge_count": len(star_map["edges"]),
            "core_node_count": len(star_map["nodes"]),
            "core_nodes_without_direct_support": len(core_without_direct_support),
            "low_observed_support_core_nodes": len(low_observed_support),
            "observed_source_file_count": len(source_vertices),
            "proposed_edge_type_count": len(proposed_edges),
            "proposed_edges_without_comention_count": len(proposed_edges_without_comention),
            "symbol_nodes_without_occurrence": len(symbol_nodes_without_occurrence),
        },
        "gap_categories": {
            "core_nodes_without_direct_support": core_without_direct_support,
            "low_observed_support_core_nodes": low_observed_support,
            "observed_governance_references_not_in_core": observed_reference_not_core[:50],
            "proposed_edges_needing_authority": [
                {
                    "edge_id": edge["edge_id"],
                    "edge_type": edge["edge_type"],
                    "edge_type_status": edge.get("feature_hints", {}).get("edge_type_status"),
                    "reason": "edge_type_is_atlas_proposal_not_runtime_edge_type",
                }
                for edge in proposed_edges
            ],
            "proposed_edges_without_comention": [
                {
                    "edge_id": edge_id,
                    "reason": "core_edge_endpoints_not_observed_together_in_same_scanned_line",
                }
                for edge_id in sorted(proposed_edges_without_comention)
            ],
            "symbol_nodes_without_occurrence": symbol_nodes_without_occurrence,
        },
    }


def _write_canonical_json(path: Path, payload: dict[str, Any], *, indent: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    kwargs: dict[str, Any] = {"allow_nan": False, "sort_keys": True}
    if indent is None:
        kwargs["separators"] = (",", ":")
    else:
        kwargs["indent"] = indent
    path.write_text(json.dumps(payload, **kwargs) + "\n", encoding="utf-8")


def _write_report(path: Path, gap: dict[str, Any]) -> None:
    summary = gap["summary"]
    categories = gap["gap_categories"]
    lines = [
        "# Genesis Core Star-Map Gap Analysis v0.1",
        "",
        "Status: deterministic comparison output — research/atlas input, not protocol canon",
        "",
        "## Summary",
        "",
        f"- Core nodes: `{summary['core_node_count']}`",
        f"- Core edges: `{summary['core_edge_count']}`",
        f"- Observed source files: `{summary['observed_source_file_count']}`",
        f"- Core nodes without direct source-path support: `{summary['core_nodes_without_direct_support']}`",
        f"- Low observed-support core nodes: `{summary['low_observed_support_core_nodes']}`",
        f"- Proposed edge types needing authority: `{summary['proposed_edge_type_count']}`",
        f"- Symbol nodes without occurrence: `{summary['symbol_nodes_without_occurrence']}`",
        "",
        "## Interpretation",
        "",
        "This report compares a deterministic observed repo/governance hypergraph against the proposed Genesis core star-map. A listed gap is not an automatic defect; it is a review queue item for Phase 1136A / future atlas work.",
        "",
    ]
    for title, items in (
        ("Core Nodes Without Direct Support", categories["core_nodes_without_direct_support"][:25]),
        ("Low Observed-Support Core Nodes", categories["low_observed_support_core_nodes"][:25]),
        ("Observed Governance References Not In Core", categories["observed_governance_references_not_in_core"][:25]),
        ("Proposed Edges Needing Authority", categories["proposed_edges_needing_authority"][:25]),
        ("Symbol Nodes Without Occurrence", categories["symbol_nodes_without_occurrence"][:25]),
    ):
        lines.extend([f"## {title}", ""])
        if not items:
            lines.extend(["No items.", ""])
            continue
        for item in items:
            label = item.get("candidate_id") or item.get("edge_id") or item.get("reference") or item.get("symbol")
            reason = item.get("reason", "")
            lines.append(f"- `{label}` — {reason}")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    while lines and lines[-1] == "":
        lines.pop()
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(
    star_map_path: Path = DEFAULT_STAR_MAP,
    crawl_path: Path = DEFAULT_CRAWL,
    observed_out: Path = DEFAULT_OBSERVED_OUT,
    gap_out: Path = DEFAULT_GAP_OUT,
    report_out: Path = DEFAULT_REPORT_OUT,
) -> tuple[dict[str, Any], dict[str, Any]]:
    star_map = _read_json(star_map_path)
    crawl = _read_json(crawl_path)
    observed = _build_observed_hypergraph(star_map, crawl)
    gap = _gap_analysis(star_map, observed)

    observed["metadata"]["source_core_star_map"] = str(star_map_path)
    observed["metadata"]["source_crawl"] = str(crawl_path)
    gap["metadata"]["source_observed_hypergraph"] = str(observed_out)
    gap["metadata"]["source_core_star_map"] = str(star_map_path)

    _write_canonical_json(observed_out, observed)
    _write_canonical_json(gap_out, gap, indent=2)
    _write_report(report_out, gap)
    return observed, gap


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--star-map", type=Path, default=DEFAULT_STAR_MAP)
    parser.add_argument("--crawl", type=Path, default=DEFAULT_CRAWL)
    parser.add_argument("--observed-out", type=Path, default=DEFAULT_OBSERVED_OUT)
    parser.add_argument("--gap-out", type=Path, default=DEFAULT_GAP_OUT)
    parser.add_argument("--report-out", type=Path, default=DEFAULT_REPORT_OUT)
    args = parser.parse_args()
    observed, gap = run(args.star_map, args.crawl, args.observed_out, args.gap_out, args.report_out)
    print(
        json.dumps(
            {
                "gap_summary": gap["summary"],
                "observed_hyperedges": len(observed["hyperedges"]),
                "observed_vertices": len(observed["vertices"]),
            },
            allow_nan=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
