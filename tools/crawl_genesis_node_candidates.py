#!/usr/bin/env python3
"""Deterministically crawl candidate Genesis-level graph nodes.

This is a research/atlas tool only. It does not mutate protocol runtime state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


DEFAULT_JSON_OUT = Path("out/genesis_node_candidate_crawl.json")
DEFAULT_INVENTORY_OUT = Path("docs/sims/sim_spectral_02/genesis_node_candidate_inventory_v0.1.md")
DEFAULT_DECISION_LOG_OUT = Path("docs/sims/sim_spectral_02/genesis_node_candidate_decision_log_v0.1.md")
GENESIS_CONFIG = Path("config/genesis.json")

SCAN_ROOTS = (Path("docs"), Path("config"), Path("ilc_core"), Path("tests"))
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

TRUTH_PRIMITIVES = (
    "assert.truth",
    "validate.claim",
    "contradict.assert",
    "refute.claim",
    "revise.assert",
    "link.claim",
    "commit.epoch",
)

EDGE_TYPE_HINTS = (
    "PROVENANCE",
    "REUSE",
    "REFUTATION",
    "CO_AUTHORSHIP",
    "ATTESTATION",
    "EPOCH_BOUNDARY",
)


@dataclass(frozen=True)
class Evidence:
    source_path: str
    source_line: int
    evidence_text: str
    evidence_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_hash": self.evidence_hash,
            "evidence_text": self.evidence_text,
            "source_line": self.source_line,
            "source_path": self.source_path,
        }


@dataclass
class Candidate:
    candidate_id: str
    label: str
    layer: str
    category: str
    node_kind: str
    authority_status: str
    canonicality_tier: str
    inclusion_status: str
    confidence: float
    rationale: str
    source_kind: str
    evidence: list[Evidence] = field(default_factory=list)
    edge_hints: list[str] = field(default_factory=list)
    sensitivity: str = "NON-SENSITIVE"
    economic_boundary: str = "none"
    genesis_exempt: bool = False
    sunset_status: str = "not_applicable"
    decision_log_refs: list[str] = field(default_factory=list)

    def add_evidence(self, evidence: Evidence) -> None:
        if all(existing.evidence_hash != evidence.evidence_hash for existing in self.evidence):
            self.evidence.append(evidence)
            self.evidence.sort(
                key=lambda item: (
                    _candidate_evidence_rank(self.candidate_id, item.source_path),
                    item.source_path,
                    item.source_line,
                    item.evidence_hash,
                )
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "authority_status": self.authority_status,
            "candidate_id": self.candidate_id,
            "canonicality_tier": self.canonicality_tier,
            "category": self.category,
            "confidence": self.confidence,
            "decision_log_refs": self.decision_log_refs,
            "economic_boundary": self.economic_boundary,
            "edge_hints": self.edge_hints,
            "evidence": [item.to_dict() for item in self.evidence],
            "genesis_exempt": self.genesis_exempt,
            "inclusion_status": self.inclusion_status,
            "label": self.label,
            "layer": self.layer,
            "node_kind": self.node_kind,
            "rationale": self.rationale,
            "sensitivity": self.sensitivity,
            "source_kind": self.source_kind,
            "sunset_status": self.sunset_status,
        }


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "unnamed"


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def _evidence(path: Path, line_number: int, text: str) -> Evidence:
    clean = text.strip()
    digest = hashlib.sha256(f"{path}:{line_number}:{clean}".encode("utf-8")).hexdigest()
    return Evidence(
        source_path=str(path),
        source_line=line_number,
        evidence_text=clean[:240],
        evidence_hash=digest,
    )


def _source_kind(path: Path) -> str:
    path_text = str(path)
    if path_text.startswith("docs/adr/"):
        return "adr"
    if path_text.startswith("docs/specs/"):
        return "spec"
    if path_text.startswith("docs/research/"):
        return "research"
    if path_text.startswith("docs/genesis/"):
        return "genesis_artifact"
    if path_text.startswith("config/"):
        return "config"
    if path_text.startswith("ilc_core/"):
        return "runtime_schema"
    if path_text.startswith("tests/"):
        return "test_evidence"
    return "other"


def _evidence_rank(source_path: str) -> int:
    if source_path == str(GENESIS_CONFIG):
        return 0
    if source_path.startswith("docs/genesis/"):
        return 1
    if source_path.startswith("docs/adr/"):
        return 2
    if source_path.startswith("docs/specs/"):
        return 3
    if source_path.startswith("ilc_core/"):
        return 4
    if source_path.startswith("docs/research/"):
        return 5
    if source_path.startswith("tests/"):
        return 6
    if source_path.startswith("docs/phases/"):
        return 7
    return 8


def _candidate_evidence_rank(candidate_id: str, source_path: str) -> int:
    preferred: dict[str, tuple[str, ...]] = {
        "artifact:genesis_state_bundle": (
            "docs/specs/ilc_genesis_state_bundle_contract_and_cdl_022_evidence_prelock_311_v0.1.md",
            "docs/specs/ilc_cdl_022_genesis_state_bundle_ratification_evidence_320_v0.1.md",
            "ilc_core/genesis/genesis_state_bundle_runtime.py",
        ),
        "artifact:genesis_authority_assertion_schema": (
            "ilc_core/genesis/assertion_schema.py",
            "docs/specs/ilc_phase_856_genesis_assertion_schema_design_v0.1.md",
        ),
        "policy:genesis_theta_hard_0_05": (
            "docs/specs/ilc_genesis_accrual_governor_contract_v0.1.md",
            "docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.1.md",
            "docs/specs/ilc_deterministic_genesis_economics_evidence_and_parameter_closure_600_v0.1.md",
        ),
        "policy:genesis_freshness_exemption": (
            "docs/specs/ilc_freshness_gate_contract_v0.1.md",
            "docs/specs/ilc_freshness_gate_provenance_and_genesis_exemption_closure_598_v0.1.md",
            "docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md",
        ),
        "overlay:morphogenetic_hypergraph_substrate": (
            "docs/research/ilc_morphogenetic_hypergraph_planning_classification_v0.1.md",
            "docs/research/ilc_morphogenetic_substrate_additions_now_v0.1.md",
            "docs/adr/ADR_0029_Hypergraph_Substrate.md",
            "docs/adr/ADR_0033_Star_Map_Homoiconic_Epistemiological_Entity.md",
        ),
    }
    for rank, preferred_path in enumerate(preferred.get(candidate_id, ())):
        if source_path == preferred_path:
            return rank
    return 100 + _evidence_rank(source_path)


def _status_from_text(path: Path, text: str) -> tuple[str, str]:
    match = re.search(r"^\s*(?:\*\*)?Status(?:\*\*)?\s*[:|]\s*([^\n]+)", text, re.IGNORECASE | re.MULTILINE)
    status = match.group(1).strip().strip("*") if match else "unlabeled"
    path_text = str(path)
    lower = text.lower()
    if path_text == str(GENESIS_CONFIG):
        return "committed_config", "binding_config"
    if path_text.startswith("docs/adr/") and "status:** accepted" in lower:
        return "accepted", "accepted_adr"
    if "ratification evidence" in lower or "ratified" in lower:
        return status, "ratified_or_evidence"
    if "locked" in status.lower():
        return status, "locked_spec"
    if "draft" in status.lower() or "candidate" in status.lower() or "proposed" in status.lower():
        return status, "supporting_context"
    if path_text.startswith("ilc_core/"):
        return status, "implemented_runtime"
    if path_text.startswith("tests/"):
        return status, "test_evidence"
    return status, "unclassified"


def _iter_files() -> Iterable[Path]:
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            if set(path.parts) & SKIP_DIRS:
                continue
            if path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            yield path


def _first_matching_line(path: Path, pattern: re.Pattern[str]) -> Evidence | None:
    text = _read_text(path)
    if text is None:
        return None
    for line_number, line in enumerate(text.splitlines(), 1):
        if pattern.search(line):
            return _evidence(path, line_number, line)
    return None


def _new_candidate(
    *,
    candidate_id: str,
    label: str,
    layer: str,
    category: str,
    node_kind: str,
    authority_status: str,
    canonicality_tier: str,
    inclusion_status: str,
    confidence: float,
    rationale: str,
    source_kind: str,
    edge_hints: list[str] | None = None,
    sensitivity: str = "NON-SENSITIVE",
    economic_boundary: str = "none",
    genesis_exempt: bool = False,
    sunset_status: str = "not_applicable",
    decision_log_refs: list[str] | None = None,
) -> Candidate:
    return Candidate(
        authority_status=authority_status,
        candidate_id=candidate_id,
        canonicality_tier=canonicality_tier,
        category=category,
        confidence=confidence,
        decision_log_refs=decision_log_refs or [],
        economic_boundary=economic_boundary,
        edge_hints=edge_hints or [],
        genesis_exempt=genesis_exempt,
        inclusion_status=inclusion_status,
        label=label,
        layer=layer,
        node_kind=node_kind,
        rationale=rationale,
        sensitivity=sensitivity,
        source_kind=source_kind,
        sunset_status=sunset_status,
    )


def _add_static_truth_primitives(candidates: dict[str, Candidate]) -> None:
    source = Path("docs/adr/ADR_0004_Genesis_Primitive_Commit_Epoch.md")
    for primitive in TRUTH_PRIMITIVES:
        candidate = _new_candidate(
            candidate_id=f"truth_primitive:{primitive}",
            label=primitive,
            layer="L0_truth_primitive",
            category="truth_primitive",
            node_kind="operator_primitive",
            authority_status="accepted_ADR_0004",
            canonicality_tier="accepted_adr",
            inclusion_status="must_include",
            confidence=1.0,
            rationale="ADR-0004 adopts the New Seven Genesis Truth Primitives.",
            source_kind="adr",
            edge_hints=["EPOCH_BOUNDARY"] if primitive == "commit.epoch" else ["PROVENANCE"],
            decision_log_refs=["GND-0001"],
        )
        evidence = _first_matching_line(source, re.compile(re.escape(primitive)))
        if evidence is not None:
            candidate.add_evidence(evidence)
        candidates[candidate.candidate_id] = candidate


def _add_genesis_axioms(candidates: dict[str, Candidate]) -> None:
    data = json.loads(GENESIS_CONFIG.read_text(encoding="utf-8"))
    axioms = data.get("axiomatic_core", [])
    if not isinstance(axioms, list):
        return
    text = GENESIS_CONFIG.read_text(encoding="utf-8").splitlines()
    for axiom in axioms:
        if not isinstance(axiom, dict) or not isinstance(axiom.get("id"), str):
            continue
        axiom_id = axiom["id"]
        label = str(axiom.get("claim", axiom_id))
        line_number = next(
            (index for index, line in enumerate(text, 1) if axiom_id in line),
            1,
        )
        candidate = _new_candidate(
            candidate_id=axiom_id,
            label=label,
            layer="L1_genesis_axiom",
            category="genesis_axiom",
            node_kind="axiom_node",
            authority_status="committed_config",
            canonicality_tier="binding_config",
            inclusion_status="must_include",
            confidence=1.0,
            rationale="Present in config/genesis.json axiomatic_core.",
            source_kind="config",
            edge_hints=["PROVENANCE", "ATTESTATION"],
            genesis_exempt=True,
            sunset_status="bootstrap_exempt_policy_review_required",
            decision_log_refs=["GND-0002"],
        )
        candidate.add_evidence(_evidence(GENESIS_CONFIG, line_number, text[line_number - 1]))
        candidates[candidate.candidate_id] = candidate


def _scan_candidate_files(candidates: dict[str, Candidate]) -> dict[str, Any]:
    patterns: list[tuple[str, re.Pattern[str], dict[str, Any]]] = [
        (
            "genesis_agent:01",
            re.compile(r"Genesis Agent 1|Genesis Agent 01|genesis_agent1", re.IGNORECASE),
            {
                "label": "Genesis Agent 1 identity",
                "layer": "L2_genesis_authority",
                "category": "genesis_authority",
                "node_kind": "authority_identity",
                "inclusion_status": "must_include",
                "confidence": 0.95,
                "rationale": "Genesis Agent 1 is the committed bootstrap authority identity surface.",
                "edge_hints": ["ATTESTATION", "PROVENANCE"],
                "sensitivity": "PUBLIC_RECORD_ONLY",
                "genesis_exempt": True,
                "sunset_status": "bounded_bootstrap_authority",
                "decision_log_refs": ["GND-0003"],
                "authority_status": "phase_838a_public_identity_record",
                "canonicality_tier": "ratified_or_evidence",
                "source_kind": "genesis_artifact",
            },
        ),
        (
            "artifact:genesis_authority_assertion_schema",
            re.compile(r"genesis_authority_assertion|GenesisAssertionContent|GENESIS_AUTHORITY_ASSERTION", re.IGNORECASE),
            {
                "label": "Genesis authority assertion schema",
                "layer": "L2_genesis_authority",
                "category": "genesis_authority_schema",
                "node_kind": "schema_artifact",
                "inclusion_status": "must_include",
                "confidence": 0.92,
                "rationale": "Defines genesis-authority assert.truth payload semantics.",
                "edge_hints": ["ATTESTATION", "EPOCH_BOUNDARY"],
                "genesis_exempt": True,
                "sunset_status": "bounded_bootstrap_authority",
                "decision_log_refs": ["GND-0004"],
                "authority_status": "implemented_runtime_schema",
                "canonicality_tier": "implemented_runtime",
                "source_kind": "runtime_schema",
            },
        ),
        (
            "artifact:genesis_state_bundle",
            re.compile(r"Genesis State Bundle|genesis_state_bundle|genesis bundle|genesis_bundle", re.IGNORECASE),
            {
                "label": "Genesis state bundle",
                "layer": "L2_bootstrap_lineage",
                "category": "bootstrap_artifact",
                "node_kind": "bundle_artifact",
                "inclusion_status": "must_include",
                "confidence": 0.90,
                "rationale": "Genesis state bundle is a canonical bootstrap lineage artifact class.",
                "edge_hints": ["PROVENANCE", "ATTESTATION"],
                "decision_log_refs": ["GND-0005"],
                "authority_status": "genesis_state_bundle_lineage",
                "canonicality_tier": "ratified_or_evidence",
                "source_kind": "spec",
            },
        ),
        (
            "artifact:eve_capsule_v0_1",
            re.compile(r"EVE capsule|canonical capsule|Genesis-signed capsules", re.IGNORECASE),
            {
                "label": "EVE canonical capsule root",
                "layer": "L2_bootstrap_lineage",
                "category": "capsule_artifact",
                "node_kind": "capsule_artifact",
                "inclusion_status": "strong_candidate",
                "confidence": 0.86,
                "rationale": "EVE/capsule lineage participates in canonical bootstrap and fork boundary semantics.",
                "edge_hints": ["PROVENANCE", "ATTESTATION"],
                "decision_log_refs": ["GND-0006"],
                "authority_status": "accepted_or_packaged_capsule_lineage",
                "canonicality_tier": "accepted_adr",
                "source_kind": "adr",
            },
        ),
        (
            "policy:genesis_theta_hard_0_05",
            re.compile(r"theta_hard|1/20|0\\.05|5%", re.IGNORECASE),
            {
                "label": "Genesis 5% hard accrual cap",
                "layer": "L3_policy_economic",
                "category": "economic_policy",
                "node_kind": "policy_constant",
                "inclusion_status": "must_include",
                "confidence": 0.90,
                "rationale": "Genesis topological dominance must be separated from economic accrual authority.",
                "edge_hints": ["EPOCH_BOUNDARY"],
                "economic_boundary": "caps_genesis_accrual_not_epistemic_centrality",
                "decision_log_refs": ["GND-0007"],
                "authority_status": "genesis_accrual_governor_policy",
                "canonicality_tier": "supporting_context",
                "source_kind": "spec",
            },
        ),
        (
            "policy:genesis_freshness_exemption",
            re.compile(r"genesis_exempt|freshness exemption|Genesis freshness", re.IGNORECASE),
            {
                "label": "Genesis freshness/refutation bootstrap exemption",
                "layer": "L3_policy_exemption",
                "category": "exemption_policy",
                "node_kind": "policy_rule",
                "inclusion_status": "strong_candidate",
                "confidence": 0.84,
                "rationale": "Genesis exemption is a bootstrap policy surface that must be visible in the atlas.",
                "edge_hints": ["ATTESTATION"],
                "economic_boundary": "exemption_is_not_uncapped_reward_authority",
                "genesis_exempt": True,
                "sunset_status": "sunset_or_reconciliation_required",
                "decision_log_refs": ["GND-0008"],
                "authority_status": "genesis_exemption_policy_surface",
                "canonicality_tier": "supporting_context",
                "source_kind": "spec",
            },
        ),
        (
            "artifact:canonical_self_describing_bootstrap_boundary",
            re.compile(r"self-describing bootstrap|recursive self-anchor|Genesis-signed bootstrap", re.IGNORECASE),
            {
                "label": "Canonical self-describing bootstrap boundary",
                "layer": "L2_bootstrap_lineage",
                "category": "bootstrap_lineage",
                "node_kind": "adr_artifact",
                "inclusion_status": "must_include",
                "confidence": 0.93,
                "rationale": "ADR-0027 defines Genesis-rooted canonical public legitimacy lineage.",
                "edge_hints": ["PROVENANCE", "ATTESTATION"],
                "decision_log_refs": ["GND-0009"],
                "authority_status": "accepted_ADR_0027",
                "canonicality_tier": "accepted_adr",
                "source_kind": "adr",
            },
        ),
        (
            "overlay:morphogenetic_hypergraph_substrate",
            re.compile(r"HyperEdge|EdgeType|PROVENANCE|REUSE|REFUTATION|CO_AUTHORSHIP|ATTESTATION|EPOCH_BOUNDARY|morphogenetic", re.IGNORECASE),
            {
                "label": "Morphogenetic hypergraph substrate overlay",
                "layer": "L4_morphogenic_overlay",
                "category": "hypergraph_overlay",
                "node_kind": "substrate_overlay",
                "inclusion_status": "strong_candidate",
                "confidence": 0.80,
                "rationale": "Defines the feature-rich edge system used to paint the Genesis morphogenic hypergraph.",
                "edge_hints": list(EDGE_TYPE_HINTS),
                "decision_log_refs": ["GND-0010"],
                "authority_status": "morphogenetic_hypergraph_planning_surface",
                "canonicality_tier": "research_planning",
                "source_kind": "research",
            },
        ),
    ]

    stats = {
        "files_scanned": 0,
        "lines_scanned": 0,
        "raw_matches": 0,
    }
    for path in _iter_files():
        text = _read_text(path)
        if text is None:
            continue
        lines = text.splitlines()
        stats["files_scanned"] += 1
        stats["lines_scanned"] += len(lines)
        authority_status, canonicality_tier = _status_from_text(path, text)
        source_kind = _source_kind(path)
        for candidate_id, pattern, defaults in patterns:
            for line_number, line in enumerate(lines, 1):
                if not pattern.search(line):
                    continue
                stats["raw_matches"] += 1
                candidate = candidates.get(candidate_id)
                if candidate is None:
                    candidate = _new_candidate(
                        candidate_id=candidate_id,
                        label=defaults["label"],
                        layer=defaults["layer"],
                        category=defaults["category"],
                        node_kind=defaults["node_kind"],
                        authority_status=defaults.get("authority_status", authority_status),
                        canonicality_tier=defaults.get("canonicality_tier", canonicality_tier),
                        inclusion_status=defaults["inclusion_status"],
                        confidence=defaults["confidence"],
                        rationale=defaults["rationale"],
                        source_kind=defaults.get("source_kind", source_kind),
                        edge_hints=defaults.get("edge_hints", []),
                        sensitivity=defaults.get("sensitivity", "NON-SENSITIVE"),
                        economic_boundary=defaults.get("economic_boundary", "none"),
                        genesis_exempt=defaults.get("genesis_exempt", False),
                        sunset_status=defaults.get("sunset_status", "not_applicable"),
                        decision_log_refs=defaults.get("decision_log_refs", []),
                    )
                    candidates[candidate_id] = candidate
                candidate.add_evidence(_evidence(path, line_number, line))
                break
    return stats


def _broad_review_sources(limit: int = 160) -> list[dict[str, Any]]:
    review_patterns: list[tuple[str, re.Pattern[str]]] = [
        ("genesis_homoiconicity", re.compile(r"genesis.*homoiconic|homoiconic.*genesis|Genesis.*graph", re.IGNORECASE)),
        ("genesis_authority", re.compile(r"Genesis authority|Genesis Agent|genesis root|Genesis-rooted", re.IGNORECASE)),
        ("genesis_policy", re.compile(r"genesis_exempt|freshness exemption|Genesis.*sunset|Genesis.*cap|theta_hard|theta_soft", re.IGNORECASE)),
        ("truth_primitives", re.compile(r"truth primitives|assert\\.truth|validate\\.claim|refute\\.claim|commit\\.epoch", re.IGNORECASE)),
        ("morphogenic_edges", re.compile(r"morphogenetic|HyperEdge|PROVENANCE|REUSE|REFUTATION|CO_AUTHORSHIP|ATTESTATION|EPOCH_BOUNDARY", re.IGNORECASE)),
        ("external_modeling", re.compile(r"Lean|Terence Tao|Tao|magma|theorem|formal proof", re.IGNORECASE)),
    ]
    source_priority = {
        "config": 0,
        "genesis_artifact": 1,
        "adr": 2,
        "spec": 3,
        "runtime_schema": 4,
        "research": 5,
        "test_evidence": 6,
        "other": 7,
    }
    records: list[dict[str, Any]] = []
    for path in _iter_files():
        text = _read_text(path)
        if text is None:
            continue
        authority_status, canonicality_tier = _status_from_text(path, text)
        source_kind = _source_kind(path)
        for line_number, line in enumerate(text.splitlines(), 1):
            for category, pattern in review_patterns:
                if not pattern.search(line):
                    continue
                evidence = _evidence(path, line_number, line)
                records.append(
                    {
                        "authority_status": authority_status,
                        "canonicality_tier": canonicality_tier,
                        "candidate_action": "review_required",
                        "category": category,
                        "evidence": evidence.to_dict(),
                        "inclusion_rule": "may_be_promoted_by_jury_or_future_SIM_after_refutation_review",
                        "source_kind": source_kind,
                    }
                )
                break
    records.sort(
        key=lambda item: (
            source_priority.get(item["source_kind"], 99),
            item["category"],
            item["evidence"]["source_path"],
            item["evidence"]["source_line"],
        )
    )
    seen: set[tuple[str, int, str]] = set()
    unique: list[dict[str, Any]] = []
    for item in records:
        key = (
            item["evidence"]["source_path"],
            item["evidence"]["source_line"],
            item["category"],
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
        if len(unique) >= limit:
            break
    return unique


def build_inventory() -> dict[str, Any]:
    candidates: dict[str, Candidate] = {}
    _add_static_truth_primitives(candidates)
    _add_genesis_axioms(candidates)
    stats = _scan_candidate_files(candidates)
    ordered = sorted(candidates.values(), key=lambda item: (item.layer, item.category, item.candidate_id))
    nodes = [candidate.to_dict() for candidate in ordered]
    edges = _candidate_edges({node["candidate_id"] for node in nodes})
    review_sources = _broad_review_sources()
    return {
        "decision_log": _decision_log(),
        "edges": edges,
        "metadata": {
            "description": "Deterministic candidate inventory for a proposed Genesis-level morphogenic hypergraph atlas.",
            "format_version": "genesis_node_candidate_crawl.v0.1",
            "scan_roots": [str(path) for path in SCAN_ROOTS],
            "skip_dirs": sorted(SKIP_DIRS),
            "stats": stats,
        },
        "nodes": nodes,
        "review_required_sources": review_sources,
    }


def _edge(
    edge_id: str,
    source: str,
    target: str,
    edge_type: str,
    relation: str,
    *,
    confidence: float,
    rationale: str,
    feature_hints: dict[str, Any],
    decision_log_refs: list[str],
) -> dict[str, Any]:
    return {
        "confidence": confidence,
        "decision_log_refs": decision_log_refs,
        "edge_id": edge_id,
        "edge_type": edge_type,
        "feature_hints": feature_hints,
        "rationale": rationale,
        "relation": relation,
        "source": source,
        "target": target,
    }


def _candidate_edges(node_ids: set[str]) -> list[dict[str, Any]]:
    proposed = []
    for axiom in ("axiom:math:01", "axiom:physics:01", "axiom:logic:01"):
        proposed.append(
            _edge(
                f"edge:assert_truth_to_{_slug(axiom)}",
                "truth_primitive:assert.truth",
                axiom,
                "ATTESTATION",
                "creates_or_declares",
                confidence=0.82,
                rationale="Genesis axioms are declared through the assert.truth primitive surface.",
                feature_hints={
                    "directional": True,
                    "economic_surface": "none",
                    "genesis_bootstrap": True,
                    "layer_span": "L0_to_L1",
                    "sim_weight_seed": 1.0,
                },
                decision_log_refs=["GND-0011"],
            )
        )
        proposed.append(
            _edge(
                f"edge:{_slug(axiom)}_to_genesis_authority",
                "genesis_agent:01",
                axiom,
                "ATTESTATION",
                "genesis_signed_assertion",
                confidence=0.78,
                rationale="Genesis Agent 1 is the authority identity that signs Genesis-level assertions.",
                feature_hints={
                    "authority_carrying": True,
                    "directional": True,
                    "genesis_exempt": True,
                    "layer_span": "L2_to_L1",
                    "sim_weight_seed": 0.9,
                },
                decision_log_refs=["GND-0012"],
            )
        )
    proposed.extend(
        [
            _edge(
                "edge:genesis_agent_to_assertion_schema",
                "genesis_agent:01",
                "artifact:genesis_authority_assertion_schema",
                "ATTESTATION",
                "uses_schema",
                confidence=0.88,
                rationale="Genesis authority assertions bind Genesis Agent identity to the assert.truth schema.",
                feature_hints={
                    "authority_carrying": True,
                    "directional": True,
                    "layer_span": "L2_to_L2",
                    "schema_edge": True,
                    "sim_weight_seed": 0.8,
                },
                decision_log_refs=["GND-0013"],
            ),
            _edge(
                "edge:assertion_schema_to_assert_truth",
                "artifact:genesis_authority_assertion_schema",
                "truth_primitive:assert.truth",
                "PROVENANCE",
                "specializes_primitive",
                confidence=0.90,
                rationale="The Genesis assertion schema is a genesis-authority specialization of assert.truth.",
                feature_hints={
                    "directional": True,
                    "layer_span": "L2_to_L0",
                    "schema_edge": True,
                    "sim_weight_seed": 0.75,
                },
                decision_log_refs=["GND-0014"],
            ),
            _edge(
                "edge:genesis_state_bundle_to_axioms",
                "artifact:genesis_state_bundle",
                "axiom:math:01",
                "PROVENANCE",
                "includes_seed_axioms_representative",
                confidence=0.70,
                rationale="The state bundle should carry Genesis seed state; this representative edge anchors the bundle to axiomatic core.",
                feature_hints={
                    "directional": True,
                    "layer_span": "L2_to_L1",
                    "representative_edge": True,
                    "sim_expansion_required": True,
                    "sim_weight_seed": 0.7,
                },
                decision_log_refs=["GND-0015"],
            ),
            _edge(
                "edge:bootstrap_boundary_to_state_bundle",
                "artifact:canonical_self_describing_bootstrap_boundary",
                "artifact:genesis_state_bundle",
                "PROVENANCE",
                "governs_lineage",
                confidence=0.86,
                rationale="ADR-0027 governs the self-describing bootstrap lineage that state bundle artifacts participate in.",
                feature_hints={
                    "authority_carrying": True,
                    "directional": True,
                    "layer_span": "L2_to_L2",
                    "lineage_edge": True,
                    "sim_weight_seed": 0.8,
                },
                decision_log_refs=["GND-0016"],
            ),
            _edge(
                "edge:eve_capsule_to_bootstrap_boundary",
                "artifact:eve_capsule_v0_1",
                "artifact:canonical_self_describing_bootstrap_boundary",
                "ATTESTATION",
                "canonical_capsule_integrity_support",
                confidence=0.74,
                rationale="EVE/capsule integrity supports the canonical bootstrap and fork boundary.",
                feature_hints={
                    "directional": True,
                    "layer_span": "L2_to_L2",
                    "lineage_edge": True,
                    "sim_weight_seed": 0.65,
                },
                decision_log_refs=["GND-0017"],
            ),
            _edge(
                "edge:theta_hard_to_commit_epoch",
                "policy:genesis_theta_hard_0_05",
                "truth_primitive:commit.epoch",
                "EPOCH_BOUNDARY",
                "caps_epoch_accrual",
                confidence=0.83,
                rationale="The 5% hard cap is enforced across cumulative issuance/accrual over epoch boundaries.",
                feature_hints={
                    "directional": True,
                    "economic_surface": "genesis_accrual_cap",
                    "layer_span": "L3_to_L0",
                    "not_epistemic_centrality_cap": True,
                    "sim_weight_seed": 0.6,
                },
                decision_log_refs=["GND-0018"],
            ),
            _edge(
                "edge:genesis_exemption_to_genesis_agent",
                "policy:genesis_freshness_exemption",
                "genesis_agent:01",
                "ATTESTATION",
                "bootstrap_exemption_policy",
                confidence=0.72,
                rationale="Genesis exemption applies to Genesis bootstrap authority surfaces and must carry sunset/reconciliation metadata.",
                feature_hints={
                    "directional": True,
                    "genesis_exempt": True,
                    "layer_span": "L3_to_L2",
                    "sunset_required": True,
                    "sim_weight_seed": 0.55,
                },
                decision_log_refs=["GND-0019"],
            ),
            _edge(
                "edge:hypergraph_overlay_to_bootstrap_boundary",
                "overlay:morphogenetic_hypergraph_substrate",
                "artifact:canonical_self_describing_bootstrap_boundary",
                "PROVENANCE",
                "paints_feature_rich_edges",
                confidence=0.68,
                rationale="The morphogenetic overlay supplies feature-rich edge semantics for the proposed Genesis atlas.",
                feature_hints={
                    "available_edge_types": list(EDGE_TYPE_HINTS),
                    "directional": True,
                    "layer_span": "L4_to_L2",
                    "sim_expansion_required": True,
                    "sim_weight_seed": 0.5,
                },
                decision_log_refs=["GND-0020"],
            ),
        ]
    )
    return [
        edge
        for edge in sorted(proposed, key=lambda item: item["edge_id"])
        if edge["source"] in node_ids and edge["target"] in node_ids
    ]


def _decision_log() -> list[dict[str, str]]:
    return [
        {
            "decision_id": "GND-0001",
            "decision": "Include the New Seven as Layer 0 operator primitives, not axioms.",
            "rationale": "ADR-0004 accepts the New Seven and demotes star.map.",
        },
        {
            "decision_id": "GND-0002",
            "decision": "Include config/genesis.json axiomatic_core as must-include Genesis axiom nodes.",
            "rationale": "These are committed Genesis config entries.",
        },
        {
            "decision_id": "GND-0003",
            "decision": "Include Genesis Agent 1 as an authority identity node.",
            "rationale": "Agent identity and public key record are committed public bootstrap artifacts.",
        },
        {
            "decision_id": "GND-0004",
            "decision": "Include the Genesis authority assertion schema as a schema artifact node.",
            "rationale": "It defines the genesis-authority assert.truth surface.",
        },
        {
            "decision_id": "GND-0005",
            "decision": "Include Genesis state bundle surfaces as bootstrap lineage nodes.",
            "rationale": "The atlas needs install/load lineage, not only epistemic claims.",
        },
        {
            "decision_id": "GND-0006",
            "decision": "Include capsule lineage as strong candidate, with authority labels.",
            "rationale": "Capsules participate in canonical-vs-fork lineage but are not all equal canon.",
        },
        {
            "decision_id": "GND-0007",
            "decision": "Represent the 5% Genesis cap as an economic policy node, not a centrality cap.",
            "rationale": "Genesis early topology may dominate; economic accrual remains capped separately.",
        },
        {
            "decision_id": "GND-0008",
            "decision": "Represent Genesis exemption as a bootstrap policy node with sunset/reconciliation flags.",
            "rationale": "Exemption is real but should not be misread as an abstract truth claim.",
        },
        {
            "decision_id": "GND-0009",
            "decision": "Include ADR-0027 bootstrap boundary as a must-include lineage node.",
            "rationale": "It defines Genesis-rooted canonical public legitimacy.",
        },
        {
            "decision_id": "GND-0010",
            "decision": "Keep morphogenetic hypergraph substrate as overlay, not narrow Genesis seed.",
            "rationale": "It paints feature-rich edges without flattening authority classes.",
        },
        {
            "decision_id": "GND-0011",
            "decision": "Seed representative truth-primitive-to-axiom edges.",
            "rationale": "The MVP graph needs edges as well as nodes for visualization and SIM optimization.",
        },
        {
            "decision_id": "GND-0012",
            "decision": "Represent Genesis signatures as authority-carrying ATTESTATION edges.",
            "rationale": "Authority edges should be visible without treating authority as ordinary truth.",
        },
        {
            "decision_id": "GND-0013",
            "decision": "Connect Genesis Agent identity to the Genesis authority assertion schema.",
            "rationale": "The install/load graph needs schema lineage for authority assertions.",
        },
        {
            "decision_id": "GND-0014",
            "decision": "Model schema-to-primitive relation as PROVENANCE/specialization.",
            "rationale": "Genesis authority assertion is a constrained assert.truth surface.",
        },
        {
            "decision_id": "GND-0015",
            "decision": "Use representative state-bundle-to-axiom edge pending full bundle expansion.",
            "rationale": "The MVP should mark where later node expansion is required.",
        },
        {
            "decision_id": "GND-0016",
            "decision": "Connect bootstrap boundary to state bundle as lineage governance.",
            "rationale": "ADR-0027 governs how bootstrap artifacts carry canonical public legitimacy.",
        },
        {
            "decision_id": "GND-0017",
            "decision": "Connect capsule integrity to bootstrap boundary as support, not equal canon.",
            "rationale": "Capsule integrity is lineage-relevant but must retain authority labeling.",
        },
        {
            "decision_id": "GND-0018",
            "decision": "Connect Genesis 5% cap to commit.epoch as economic boundary.",
            "rationale": "Economic accrual caps are epoch-settlement constraints, not centrality constraints.",
        },
        {
            "decision_id": "GND-0019",
            "decision": "Connect Genesis exemption policy to Genesis Agent authority with sunset flags.",
            "rationale": "Bootstrap exemption must be visible and bounded.",
        },
        {
            "decision_id": "GND-0020",
            "decision": "Connect morphogenetic overlay to bootstrap boundary for feature-rich edge expansion.",
            "rationale": "The atlas needs an explicit bridge from seed graph to hypergraph feature semantics.",
        },
        {
            "decision_id": "GND-0021",
            "decision": "Keep lower-authority and historical material in a review queue instead of excluding it.",
            "rationale": "The ILC process should be able to refute, improve, and promote candidate Genesis graph material over time.",
        },
    ]


def write_inventory(payload: dict[str, Any], json_out: Path, inventory_out: Path, decision_log_out: Path) -> None:
    json_out.parent.mkdir(parents=True, exist_ok=True)
    inventory_out.parent.mkdir(parents=True, exist_ok=True)
    decision_log_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    inventory_out.write_text(_render_inventory_md(payload), encoding="utf-8")
    decision_log_out.write_text(_render_decision_log_md(payload), encoding="utf-8")


def _render_inventory_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Genesis Node Candidate Inventory v0.1",
        "",
        "Status: deterministic crawl output — proposed SIM/atlas input, not protocol canon",
        "",
        "## Metadata",
        "",
        f"- Files scanned: `{payload['metadata']['stats']['files_scanned']}`",
        f"- Lines scanned: `{payload['metadata']['stats']['lines_scanned']}`",
        f"- Raw matches: `{payload['metadata']['stats']['raw_matches']}`",
        f"- Candidate nodes: `{len(payload['nodes'])}`",
        f"- Review-required sources: `{len(payload['review_required_sources'])}`",
        "",
        "## Candidate Nodes",
        "",
        "| Candidate ID | Layer | Category | Inclusion | Canonicality | Evidence |",
        "|---|---|---|---|---|---|",
    ]
    for node in payload["nodes"]:
        evidence = node["evidence"][0] if node["evidence"] else {"source_path": "", "source_line": ""}
        source = f"{evidence['source_path']}:{evidence['source_line']}" if evidence["source_path"] else ""
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{node['candidate_id']}`",
                    node["layer"],
                    node["category"],
                    node["inclusion_status"],
                    node["canonicality_tier"],
                    f"`{source}`",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Schema Fields",
            "",
            "Each JSON node records: `candidate_id`, `label`, `layer`, `category`, `node_kind`, `authority_status`, `canonicality_tier`, `inclusion_status`, `confidence`, `rationale`, `source_kind`, `evidence`, `edge_hints`, `sensitivity`, `economic_boundary`, `genesis_exempt`, `sunset_status`, and `decision_log_refs`.",
            "",
            "## Review-Required Source Queue",
            "",
            "These sources are not promoted to candidate nodes by default. They are retained for jury/refutation review and may be promoted, revised, or rejected in a later atlas iteration.",
            "",
            "| Category | Source Kind | Canonicality | Evidence |",
            "|---|---|---|---|",
        ]
    )
    for item in payload["review_required_sources"][:40]:
        evidence = item["evidence"]
        source = f"{evidence['source_path']}:{evidence['source_line']}"
        lines.append(
            "| "
            + " | ".join(
                [
                    item["category"],
                    item["source_kind"],
                    item["canonicality_tier"],
                    f"`{source}`",
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def _render_decision_log_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Genesis Node Candidate Decision Log v0.1",
        "",
        "Status: GND research decision log — analogous to CDL shape, but non-constitutional and non-binding",
        "",
        "| ID | Decision | Rationale |",
        "|---|---|---|",
    ]
    for decision in payload["decision_log"]:
        lines.append(f"| `{decision['decision_id']}` | {decision['decision']} | {decision['rationale']} |")
    lines.append("")
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--inventory-out", type=Path, default=DEFAULT_INVENTORY_OUT)
    parser.add_argument("--decision-log-out", type=Path, default=DEFAULT_DECISION_LOG_OUT)
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    payload = build_inventory()
    write_inventory(payload, args.json_out, args.inventory_out, args.decision_log_out)
    print(json.dumps(payload["metadata"], allow_nan=False, sort_keys=True))


if __name__ == "__main__":
    main()
