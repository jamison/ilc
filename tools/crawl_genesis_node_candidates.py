#!/usr/bin/env python3
"""Deterministically crawl candidate Genesis-level graph nodes.

This is a research/atlas tool only. It does not mutate protocol runtime state.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


DEFAULT_JSON_OUT = Path("out/genesis_node_candidate_crawl.json")
DEFAULT_RAW_LEDGER_OUT = Path("out/genesis_node_candidate_raw_match_ledger.ndjson")
DEFAULT_REJECTED_LEDGER_OUT = Path("out/genesis_node_candidate_rejected_sources.ndjson")
DEFAULT_STAR_MAP_OUT = Path("out/genesis_core_star_map_v0.1.json")
DEFAULT_STAR_MAP_INDEX_OUT = Path("out/genesis_core_star_map_index_v0.1.json")
DEFAULT_INVENTORY_OUT = Path("docs/sims/sim_spectral_02/genesis_node_candidate_inventory_v0.1.md")
DEFAULT_DECISION_LOG_OUT = Path("docs/sims/sim_spectral_02/genesis_node_candidate_decision_log_v0.1.md")
DEFAULT_CURATED_SEED = Path("docs/sims/sim_spectral_02/genesis_core_star_map_curated_seed_v0.1.json")
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

RUNTIME_EDGE_TYPES = {
    "PROVENANCE",
    "REUSE",
    "REFUTATION",
    "MAINTENANCE",
    "CO_AUTHORSHIP",
    "ATTESTATION",
    "EPOCH_BOUNDARY",
}
PROPOSED_ATLAS_EDGE_TYPES = {"PRIMITIVE_INVOCATION", "GOVERNS", "CONSTRAINS"}

GENESIS_AGENT_ID = "genesis_agent:01"
GENESIS_CAP_POLICY_ID = "policy:genesis_theta_hard_0_05"
TRUTH_PRIMITIVE_NODE_IDS = tuple(f"truth_primitive:{primitive}" for primitive in TRUTH_PRIMITIVES)


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
    genesis_attested: bool = False
    genesis_attested_by: str | None = None
    attestation_type: str | None = None
    signature_scope: str | None = None
    signature_status: str | None = None
    signing_key_ref: str | None = None
    signature_envelope_ref: str | None = None
    signature_file_ref: str | None = None
    star_map_version: str | None = None
    reuse_economic_surface: str = "none"
    economic_cap_policy: str | None = None
    depth_index: int | None = None
    graph_projection: str = "core_star_map"
    promotion_path: str = "already_core_or_not_applicable"
    symbol: str | None = None
    value: dict[str, Any] | None = None
    applies_to: list[str] = field(default_factory=list)
    version: str | None = None
    valid_epoch_range: tuple[int | None, int | None] = (0, None)
    superseded_by: str | None = None
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
        core_star_map_candidate = _core_star_map_candidate(self.inclusion_status, self.graph_projection)
        return {
            "applies_to": self.applies_to,
            "authority_status": self.authority_status,
            "candidate_id": self.candidate_id,
            "canonicality_tier": self.canonicality_tier,
            "category": self.category,
            "confidence": self.confidence,
            "core_star_map_candidate": core_star_map_candidate,
            "decision_log_refs": self.decision_log_refs,
            "economic_boundary": self.economic_boundary,
            "economic_cap_policy": self.economic_cap_policy,
            "edge_hints": self.edge_hints,
            "evidence": [item.to_dict() for item in self.evidence],
            "depth_index": self.depth_index,
            "attestation_type": self.attestation_type,
            "genesis_attested": self.genesis_attested,
            "genesis_attested_by": self.genesis_attested_by,
            "genesis_exempt": self.genesis_exempt,
            "graph_projection": self.graph_projection,
            "inclusion_status": self.inclusion_status,
            "label": self.label,
            "layer": self.layer,
            "node_kind": self.node_kind,
            "promotion_path": _promotion_path(self.promotion_path, core_star_map_candidate),
            "rationale": self.rationale,
            "reuse_economic_surface": self.reuse_economic_surface,
            "sensitivity": self.sensitivity,
            "signature_scope": self.signature_scope,
            "signature_status": self.signature_status,
            "signing_key_ref": self.signing_key_ref,
            "signature_envelope_ref": self.signature_envelope_ref,
            "signature_file_ref": self.signature_file_ref,
            "star_map_version": self.star_map_version,
            "source_kind": self.source_kind,
            "symbol": self.symbol,
            "superseded_by": self.superseded_by,
            "sunset_status": self.sunset_status,
            "valid_epoch_range": list(self.valid_epoch_range),
            "value": self.value,
            "version": self.version,
        }


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "unnamed"


def _core_star_map_candidate(inclusion_status: str, graph_projection: str) -> bool | str:
    if graph_projection != "core_star_map":
        return False
    if inclusion_status == "must_include":
        return True
    if inclusion_status == "strong_candidate":
        return "review"
    return False


def _promotion_path(configured_path: str, core_star_map_candidate: bool | str) -> str:
    if configured_path != "already_core_or_not_applicable":
        return configured_path
    if core_star_map_candidate is True:
        return "already_core_star_map"
    if core_star_map_candidate == "review":
        return "candidate_requires_jury_review_or_ADR_CDL_runtime_synthesis"
    return "support_graph_to_core_requires_synthesis_artifact_and_jury_or_cdl_review"


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


def _first_line_evidence(path: Path) -> Evidence | None:
    text = _read_text(path)
    if text is None:
        return None
    for line_number, line in enumerate(text.splitlines(), 1):
        if line.strip():
            return _evidence(path, line_number, line)
    return None


def _load_curated_seed(path: Path = DEFAULT_CURATED_SEED) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("genesis_curated_seed_must_be_json_object")
    return data


def _seed_evidence(item: dict[str, Any]) -> Evidence | None:
    source_path = Path(item["source_path"])
    source_line = item.get("source_line")
    if source_line is None:
        return _first_line_evidence(source_path)
    text = _read_text(source_path)
    if text is None:
        return None
    lines = text.splitlines()
    line_index = int(source_line) - 1
    if line_index < 0 or line_index >= len(lines):
        return None
    return _evidence(source_path, int(source_line), lines[line_index])


def _add_curated_seed_candidates(candidates: dict[str, Candidate], seed: dict[str, Any]) -> None:
    for spec in seed.get("nodes", []):
        candidate_spec = copy.deepcopy(spec)
        evidence_specs = candidate_spec.pop("evidence", [])
        candidate_spec.pop("core_star_map_candidate", None)
        candidate = _new_candidate(**candidate_spec)
        for evidence_spec in evidence_specs:
            evidence = _seed_evidence(evidence_spec)
            if evidence is not None:
                candidate.add_evidence(evidence)
        candidates[candidate.candidate_id] = candidate

def _apply_genesis_attested_overrides(candidates: dict[str, Candidate], seed: dict[str, Any]) -> None:
    # The crawler is not the authority source for Genesis attestation.
    # It compiles explicit curated-seed decisions and fails closed if the seed
    # references a node that the complete deterministic crawl no longer emits.
    for override in seed.get("genesis_attested_overrides", []):
        candidate_id = override["candidate_id"]
        if candidate_id not in candidates:
            raise ValueError(f"genesis_attested_override_unknown_candidate:{candidate_id}")
        candidate = candidates[candidate_id]
        candidate.genesis_attested = True
        candidate.genesis_attested_by = override.get("genesis_attested_by", GENESIS_AGENT_ID)
        candidate.signing_key_ref = override["signing_key_ref"]
        candidate.attestation_type = override.get("attestation_type", "ex_post_facto")
        candidate.signature_status = override.get("signature_status", "pending_human_signature")
        candidate.signature_scope = override.get(
            "signature_scope",
            "genesis_node_attestation_manifest_v0.1",
        )
        candidate.signature_envelope_ref = override.get("signature_envelope_ref")
        candidate.signature_file_ref = override.get("signature_file_ref")
        candidate.star_map_version = override.get("star_map_version")


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
    genesis_attested: bool = False,
    genesis_attested_by: str | None = None,
    attestation_type: str | None = None,
    signature_scope: str | None = None,
    signature_status: str | None = None,
    signing_key_ref: str | None = None,
    signature_envelope_ref: str | None = None,
    signature_file_ref: str | None = None,
    star_map_version: str | None = None,
    reuse_economic_surface: str = "none",
    economic_cap_policy: str | None = None,
    depth_index: int | None = None,
    graph_projection: str = "core_star_map",
    promotion_path: str = "already_core_or_not_applicable",
    symbol: str | None = None,
    value: dict[str, Any] | None = None,
    applies_to: list[str] | None = None,
    version: str | None = None,
    valid_epoch_range: tuple[int | None, int | None] = (0, None),
    superseded_by: str | None = None,
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
        economic_cap_policy=economic_cap_policy,
        edge_hints=edge_hints or [],
        depth_index=depth_index,
        attestation_type=attestation_type,
        graph_projection=graph_projection,
        genesis_attested=genesis_attested,
        genesis_attested_by=genesis_attested_by,
        genesis_exempt=genesis_exempt,
        inclusion_status=inclusion_status,
        label=label,
        layer=layer,
        node_kind=node_kind,
        promotion_path=promotion_path,
        rationale=rationale,
        reuse_economic_surface=reuse_economic_surface,
        sensitivity=sensitivity,
        signature_scope=signature_scope,
        signature_status=signature_status,
        signing_key_ref=signing_key_ref,
        signature_envelope_ref=signature_envelope_ref,
        signature_file_ref=signature_file_ref,
        star_map_version=star_map_version,
        source_kind=source_kind,
        symbol=symbol,
        superseded_by=superseded_by,
        sunset_status=sunset_status,
        valid_epoch_range=valid_epoch_range,
        value=value,
        applies_to=applies_to or [],
        version=version,
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
            edge_hints=["EPOCH_BOUNDARY", "ATTESTATION", "REUSE"]
            if primitive == "commit.epoch"
            else ["PRIMITIVE_INVOCATION", "ATTESTATION", "REUSE"],
            economic_boundary="genesis_attested_provenance_flow",
            genesis_attested=True,
            genesis_attested_by=GENESIS_AGENT_ID,
            reuse_economic_surface="high",
            economic_cap_policy=GENESIS_CAP_POLICY_ID,
            depth_index=0,
            graph_projection="core_star_map",
            decision_log_refs=["GND-0001", "GND-0022", "GND-0023"],
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
            economic_boundary="genesis_attested_provenance_flow",
            genesis_exempt=True,
            genesis_attested=True,
            genesis_attested_by=GENESIS_AGENT_ID,
            reuse_economic_surface="domain_foundational",
            economic_cap_policy=GENESIS_CAP_POLICY_ID,
            depth_index=1,
            graph_projection="core_star_map",
            sunset_status="bootstrap_exempt_policy_review_required",
            decision_log_refs=["GND-0002"],
        )
        candidate.add_evidence(_evidence(GENESIS_CONFIG, line_number, text[line_number - 1]))
        candidates[candidate.candidate_id] = candidate


def _add_static_promoted_candidates(candidates: dict[str, Candidate]) -> None:
    """Promote high-confidence Genesis atlas nodes that should not remain review-only."""
    specs: list[dict[str, Any]] = [
        {
            "candidate_id": "policy:provenance_decay_alpha_0_45",
            "label": "CDL-084 PROVENANCE_DECAY_ALPHA Decimal(0.45)",
            "layer": "L3_policy_economic",
            "category": "economic_policy",
            "node_kind": "policy_constant",
            "authority_status": "cdl_084_q2_alpha_locked_phase_1126",
            "canonicality_tier": "ratified_cdl",
            "inclusion_status": "must_include",
            "confidence": 0.96,
            "rationale": "CDL-084 Q2 locks the geometric decay constant controlling PROVENANCE chain ECU flow.",
            "source_kind": "spec",
            "source_path": Path("docs/specs/ilc_cdl_084_provenance_chain_attribution_opening_1111_v0.1.md"),
            "evidence_pattern": re.compile(r'PROVENANCE_DECAY_ALPHA = Decimal\("0\.45"\)'),
            "edge_hints": ["PROVENANCE"],
            "economic_boundary": "provenance_chain_decay",
            "symbol": "PROVENANCE_DECAY_ALPHA",
            "value": {
                "kind": "decimal",
                "literal": "0.45",
                "python_symbol": "PROVENANCE_DECAY_ALPHA",
                "runtime_path": "ilc_core/types.py",
            },
            "applies_to": ["edge_type:PROVENANCE", "settlement:provenance_chain_attribution"],
            "depth_index": 3,
            "decision_log_refs": ["GND-0027", "GND-0031"],
        },
        {
            "candidate_id": "artifact:genesis_agent1_pubkey_record_838a",
            "label": "Genesis Agent 1 public key record 838a",
            "layer": "L2_genesis_authority",
            "category": "genesis_authority_artifact",
            "node_kind": "public_key_record",
            "authority_status": "phase_838a_public_identity_record",
            "canonicality_tier": "ratified_or_evidence",
            "inclusion_status": "must_include",
            "confidence": 0.95,
            "rationale": "The Genesis Agent identity node must retain its concrete public key artifact.",
            "source_kind": "genesis_artifact",
            "source_path": Path("docs/genesis/genesis_agent1_pubkey_record_838a.txt"),
            "edge_hints": ["ATTESTATION"],
            "sensitivity": "PUBLIC_RECORD_ONLY",
            "genesis_exempt": True,
            "depth_index": 2,
            "sunset_status": "bounded_bootstrap_authority",
            "decision_log_refs": ["GND-0003", "GND-0026"],
        },
        {
            "candidate_id": "ceremony:genesis_agent1_keygen_838a",
            "label": "Genesis Agent 1 PQ keygen ceremony 838a",
            "layer": "L2_genesis_authority",
            "category": "genesis_authority_ceremony",
            "node_kind": "keygen_ceremony",
            "authority_status": "phase_838a_closure_pass",
            "canonicality_tier": "ratified_or_evidence",
            "inclusion_status": "must_include",
            "confidence": 0.88,
            "rationale": "The key ceremony is a lineage event for Genesis Agent 1 authority.",
            "source_kind": "spec",
            "source_path": Path("docs/specs/ilc_phase_838a_genesis_agent1_keygen_closure_v0.1.md"),
            "edge_hints": ["ATTESTATION", "EPOCH_BOUNDARY"],
            "sensitivity": "PUBLIC_RECORD_ONLY",
            "genesis_exempt": True,
            "depth_index": 2,
            "sunset_status": "bounded_bootstrap_authority",
            "decision_log_refs": ["GND-0003", "GND-0026", "GND-0033"],
        },
        {
            "candidate_id": "policy:genesis_governance_dilution",
            "label": "Genesis governance dilution policy",
            "layer": "L3_policy_economic",
            "category": "economic_policy",
            "node_kind": "policy_rule",
            "authority_status": "proposed_ADR_0008",
            "canonicality_tier": "supporting_context",
            "inclusion_status": "strong_candidate",
            "confidence": 0.82,
            "rationale": "ADR-0008 separates epistemic usefulness from governance and Genesis dilution.",
            "source_kind": "adr",
            "source_path": Path("docs/adr/ADR_0008_Node_Usefulness_vs_Governance_Weight_and_Genesis_Dilution.md"),
            "edge_hints": ["EPOCH_BOUNDARY"],
            "economic_boundary": "governance_weight_not_epistemic_centrality",
            "depth_index": 3,
            "decision_log_refs": ["GND-0007", "GND-0026"],
        },
        {
            "candidate_id": "policy:genesis_accrual_governor",
            "label": "Genesis accrual governor policy",
            "layer": "L3_policy_economic",
            "category": "economic_policy",
            "node_kind": "policy_contract",
            "authority_status": "genesis_accrual_governor_contract",
            "canonicality_tier": "supporting_context",
            "inclusion_status": "must_include",
            "confidence": 0.90,
            "rationale": "The governor is the policy surface that enforces the Genesis economic cap.",
            "source_kind": "spec",
            "source_path": Path("docs/specs/ilc_genesis_accrual_governor_contract_v0.1.md"),
            "edge_hints": ["EPOCH_BOUNDARY"],
            "economic_boundary": "caps_genesis_accrual_not_epistemic_centrality",
            "applies_to": [
                "genesis_agent:01",
                "policy:genesis_theta_hard_0_05",
                "policy:genesis_theta_soft_exp_minus_3",
            ],
            "depth_index": 3,
            "decision_log_refs": ["GND-0007", "GND-0026", "GND-0033"],
        },
        {
            "candidate_id": "policy:genesis_theta_soft_exp_minus_3",
            "label": "Genesis soft taper threshold exp(-3)",
            "layer": "L3_policy_economic",
            "category": "economic_policy",
            "node_kind": "policy_constant",
            "authority_status": "genesis_accrual_governor_modeling_target",
            "canonicality_tier": "supporting_context",
            "inclusion_status": "must_include",
            "confidence": 0.84,
            "rationale": "The soft taper explains how Genesis dominance is compressed before the 5% hard cap.",
            "source_kind": "spec",
            "source_path": Path("docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.3.md"),
            "edge_hints": ["EPOCH_BOUNDARY"],
            "economic_boundary": "genesis_accrual_soft_taper",
            "symbol": "GENESIS_THETA_SOFT",
            "value": {
                "kind": "expression",
                "literal": "exp(-3)",
                "note": "evaluate with Decimal arithmetic; do not store as float",
            },
            "applies_to": ["policy:genesis_accrual_governor", "economic_surface:genesis_accrual_soft_taper"],
            "depth_index": 3,
            "decision_log_refs": ["GND-0007", "GND-0026", "GND-0031", "GND-0033"],
        },
        {
            "candidate_id": "artifact:star_map_demoted_by_adr_0004",
            "label": "star.map demoted from Genesis truth primitive by ADR-0004",
            "layer": "L2_bootstrap_lineage",
            "category": "governance_event",
            "node_kind": "demotion_event",
            "authority_status": "accepted_ADR_0004",
            "canonicality_tier": "accepted_adr",
            "inclusion_status": "must_include",
            "confidence": 0.92,
            "rationale": "ADR-0004 records star.map as explicitly not a Genesis truth primitive, preserving a real governance demotion event.",
            "source_kind": "adr",
            "source_path": Path("docs/adr/ADR_0004_Genesis_Primitive_Commit_Epoch.md"),
            "evidence_pattern": re.compile(r"star\.map.*not.*Genesis truth primitive|demotes `star\.map`", re.IGNORECASE),
            "edge_hints": ["REFUTATION", "PROVENANCE"],
            "depth_index": 2,
            "superseded_by": "adr:0033_star_map_homoiconic_entity",
            "decision_log_refs": ["GND-0032"],
        },
        {
            "candidate_id": "artifact:genesis_release_artifact_contract",
            "label": "Genesis release artifact contract",
            "layer": "L2_bootstrap_lineage",
            "category": "bootstrap_artifact",
            "node_kind": "release_contract",
            "authority_status": "phase_228_release_contract",
            "canonicality_tier": "ratified_or_evidence",
            "inclusion_status": "strong_candidate",
            "confidence": 0.88,
            "rationale": "The release artifact contract participates in install/load Genesis lineage.",
            "source_kind": "spec",
            "source_path": Path("docs/specs/ilc_genesis_release_artifact_contract_v0.1.md"),
            "edge_hints": ["PROVENANCE", "ATTESTATION"],
            "depth_index": 2,
            "decision_log_refs": ["GND-0005", "GND-0026"],
        },
        {
            "candidate_id": "artifact:genesis_release_provenance_phase_228",
            "label": "Genesis release artifact provenance phase 228",
            "layer": "L2_bootstrap_lineage",
            "category": "bootstrap_artifact",
            "node_kind": "release_provenance",
            "authority_status": "phase_228_release_provenance",
            "canonicality_tier": "ratified_or_evidence",
            "inclusion_status": "strong_candidate",
            "confidence": 0.88,
            "rationale": "The phase 228 provenance artifact records release lineage for Genesis packaging.",
            "source_kind": "spec",
            "source_path": Path("docs/specs/ilc_genesis_release_artifact_provenance_phase_228_v0.1.md"),
            "edge_hints": ["PROVENANCE", "ATTESTATION"],
            "depth_index": 2,
            "decision_log_refs": ["GND-0005", "GND-0026"],
        },
        {
            "candidate_id": "policy:genesis_authority_sunset",
            "label": "Genesis authority sunset and fork legitimacy policy",
            "layer": "L3_policy_exemption",
            "category": "exemption_policy",
            "node_kind": "policy_rule",
            "authority_status": "locked_phase_590",
            "canonicality_tier": "locked_spec",
            "inclusion_status": "must_include",
            "confidence": 0.90,
            "rationale": "Genesis bootstrap authority requires explicit sunset and fork-legitimacy boundaries.",
            "source_kind": "spec",
            "source_path": Path("docs/specs/ilc_genesis_authority_sunset_and_fork_legitimacy_coherence_lock_590_v0.1.md"),
            "edge_hints": ["ATTESTATION", "EPOCH_BOUNDARY"],
            "economic_boundary": "exemption_is_not_uncapped_reward_authority",
            "genesis_exempt": True,
            "depth_index": 3,
            "sunset_status": "sunset_or_reconciliation_required",
            "decision_log_refs": ["GND-0008", "GND-0026"],
        },
        {
            "candidate_id": "artifact:rc0_1_curated_genesis_lineage",
            "label": "RC0.1 curated Genesis/bootstrap lineage lock",
            "layer": "L2_bootstrap_lineage",
            "category": "bootstrap_lineage",
            "node_kind": "lineage_lock",
            "authority_status": "locked_phase_578",
            "canonicality_tier": "locked_spec",
            "inclusion_status": "strong_candidate",
            "confidence": 0.86,
            "rationale": "The curated Genesis/bootstrap lineage lock is a launch-facing install/load artifact.",
            "source_kind": "spec",
            "source_path": Path("docs/specs/ilc_rc0_1_curated_genesis_bootstrap_lineage_lock_578_v0.1.md"),
            "edge_hints": ["PROVENANCE", "ATTESTATION"],
            "depth_index": 2,
            "decision_log_refs": ["GND-0005", "GND-0026"],
        },
        {
            "candidate_id": "policy:genesis_intervention_cdl_v6",
            "label": "CDL-V6 Genesis intervention protocol",
            "layer": "L3_policy_exemption",
            "category": "exemption_policy",
            "node_kind": "constitutional_policy",
            "authority_status": "ratified_phase_334",
            "canonicality_tier": "ratified_or_evidence",
            "inclusion_status": "strong_candidate",
            "confidence": 0.84,
            "rationale": "The Genesis intervention protocol is a bounded authority surface relevant to exemption semantics.",
            "source_kind": "spec",
            "source_path": Path("docs/specs/ilc_cdl_v6_genesis_intervention_protocol_ratification_evidence_334_v0.1.md"),
            "edge_hints": ["ATTESTATION", "EPOCH_BOUNDARY"],
            "economic_boundary": "exemption_is_not_uncapped_reward_authority",
            "genesis_exempt": True,
            "depth_index": 3,
            "sunset_status": "sunset_or_reconciliation_required",
            "decision_log_refs": ["GND-0008", "GND-0026"],
        },
        {
            "candidate_id": "adr:0029_hypergraph_substrate",
            "label": "ADR-0029 Hypergraph substrate",
            "layer": "L4_morphogenic_overlay",
            "category": "hypergraph_overlay",
            "node_kind": "adr_artifact",
            "authority_status": "accepted_ADR_0029",
            "canonicality_tier": "accepted_adr",
            "inclusion_status": "must_include",
            "confidence": 0.92,
            "rationale": "The hypergraph substrate is a distinct morphogenic atlas dependency.",
            "source_kind": "adr",
            "source_path": Path("docs/adr/ADR_0029_Hypergraph_Substrate.md"),
            "edge_hints": list(EDGE_TYPE_HINTS),
            "depth_index": 4,
            "decision_log_refs": ["GND-0010", "GND-0026"],
        },
        {
            "candidate_id": "adr:0030_node_embedding_substrate",
            "label": "ADR-0030 Node embedding substrate and content typing",
            "layer": "L4_morphogenic_overlay",
            "category": "hypergraph_overlay",
            "node_kind": "adr_artifact",
            "authority_status": "accepted_ADR_0030",
            "canonicality_tier": "accepted_adr",
            "inclusion_status": "must_include",
            "confidence": 0.90,
            "rationale": "Node embedding/content typing should remain separate from the hypergraph edge substrate.",
            "source_kind": "adr",
            "source_path": Path("docs/adr/ADR_0030_Node_Embedding_Substrate_and_Content_Typing.md"),
            "edge_hints": list(EDGE_TYPE_HINTS),
            "depth_index": 4,
            "decision_log_refs": ["GND-0010", "GND-0026"],
        },
        {
            "candidate_id": "adr:0032_temporal_hypergraph",
            "label": "ADR-0032 Temporal hypergraph epoch-stamped incidence",
            "layer": "L4_morphogenic_overlay",
            "category": "hypergraph_overlay",
            "node_kind": "adr_artifact",
            "authority_status": "accepted_ADR_0032",
            "canonicality_tier": "accepted_adr",
            "inclusion_status": "must_include",
            "confidence": 0.90,
            "rationale": "Temporal incidence is required for epoch-aware Genesis graph loading and simulation.",
            "source_kind": "adr",
            "source_path": Path("docs/adr/ADR_0032_Temporal_Hypergraph_Epoch_Stamped_Incidence.md"),
            "edge_hints": ["EPOCH_BOUNDARY", "PROVENANCE"],
            "depth_index": 4,
            "decision_log_refs": ["GND-0010", "GND-0026"],
        },
        {
            "candidate_id": "adr:0033_star_map_homoiconic_entity",
            "label": "ADR-0033 Star map homoiconic epistemological entity",
            "layer": "L4_morphogenic_overlay",
            "category": "hypergraph_overlay",
            "node_kind": "adr_artifact",
            "authority_status": "accepted_ADR_0033",
            "canonicality_tier": "accepted_adr",
            "inclusion_status": "must_include",
            "confidence": 0.90,
            "rationale": "The star map is the install/load surface for a local base graph.",
            "source_kind": "adr",
            "source_path": Path("docs/adr/ADR_0033_Star_Map_Homoiconic_Epistemiological_Entity.md"),
            "edge_hints": ["PROVENANCE", "ATTESTATION"],
            "depth_index": 4,
            "decision_log_refs": ["GND-0010", "GND-0026"],
        },
        {
            "candidate_id": "cdl:081_hyperedge_ecu_attribution",
            "label": "CDL-081 Hyperedge ECU attribution",
            "layer": "L4_morphogenic_overlay",
            "category": "constitutional_artifact",
            "node_kind": "cdl_artifact",
            "authority_status": "ratified_phase_943",
            "canonicality_tier": "ratified_or_evidence",
            "inclusion_status": "must_include",
            "confidence": 0.94,
            "rationale": "CDL-081 defines the attribution edge settlement surface.",
            "source_kind": "spec",
            "source_path": Path("docs/specs/ilc_cdl_081_hyperedge_ecu_attribution_opening_929_v0.1.md"),
            "edge_hints": ["REUSE", "CO_AUTHORSHIP", "PROVENANCE"],
            "depth_index": 4,
            "decision_log_refs": ["GND-0010", "GND-0026"],
        },
        {
            "candidate_id": "cdl:083_panel_quorum_refutation",
            "label": "CDL-083 Panel quorum and REFUTATION attribution",
            "layer": "L4_morphogenic_overlay",
            "category": "constitutional_artifact",
            "node_kind": "cdl_artifact",
            "authority_status": "ratified_phase_1105",
            "canonicality_tier": "ratified_or_evidence",
            "inclusion_status": "must_include",
            "confidence": 0.94,
            "rationale": "CDL-083 defines the H-CON-02 quorum and REFUTATION path.",
            "source_kind": "spec",
            "source_path": Path("docs/specs/ilc_cdl_083_h_con_02_panel_quorum_ejected_stake_opening_1103_v0.1.md"),
            "edge_hints": ["REFUTATION", "ATTESTATION"],
            "depth_index": 4,
            "decision_log_refs": ["GND-0010", "GND-0026"],
        },
        {
            "candidate_id": "cdl:084_provenance_chain_attribution",
            "label": "CDL-084 PROVENANCE chain attribution",
            "layer": "L4_morphogenic_overlay",
            "category": "constitutional_artifact",
            "node_kind": "cdl_artifact",
            "authority_status": "ratified_phase_1113",
            "canonicality_tier": "ratified_or_evidence",
            "inclusion_status": "must_include",
            "confidence": 0.96,
            "rationale": "CDL-084 defines PROVENANCE chain attribution and alpha 0.45 inheritance.",
            "source_kind": "spec",
            "source_path": Path("docs/specs/ilc_cdl_084_provenance_chain_attribution_opening_1111_v0.1.md"),
            "edge_hints": ["PROVENANCE"],
            "depth_index": 4,
            "decision_log_refs": ["GND-0010", "GND-0025", "GND-0026"],
        },
    ]
    for spec in specs:
        source_path = spec.pop("source_path")
        if not source_path.exists():
            continue
        evidence_pattern = spec.pop("evidence_pattern", None)
        candidate = _new_candidate(**spec)
        evidence = _first_matching_line(source_path, evidence_pattern) if evidence_pattern else _first_line_evidence(source_path)
        if evidence is not None:
            candidate.add_evidence(evidence)
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
                "symbol": "GENESIS_THETA_HARD",
                "value": {
                    "kind": "decimal",
                    "literal": "0.05",
                },
                "applies_to": ["policy:genesis_accrual_governor", "economic_surface:genesis_accrual_cap"],
                "decision_log_refs": ["GND-0007", "GND-0031"],
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
                        genesis_attested=defaults.get("genesis_attested", False),
                        genesis_attested_by=defaults.get("genesis_attested_by"),
                        reuse_economic_surface=defaults.get("reuse_economic_surface", "none"),
                        economic_cap_policy=defaults.get("economic_cap_policy"),
                        depth_index=defaults.get("depth_index"),
                        graph_projection=defaults.get("graph_projection", "core_star_map"),
                        promotion_path=defaults.get("promotion_path", "already_core_or_not_applicable"),
                        symbol=defaults.get("symbol"),
                        value=defaults.get("value"),
                        applies_to=defaults.get("applies_to"),
                        version=defaults.get("version"),
                        valid_epoch_range=defaults.get("valid_epoch_range", (0, None)),
                        superseded_by=defaults.get("superseded_by"),
                        sunset_status=defaults.get("sunset_status", "not_applicable"),
                        decision_log_refs=defaults.get("decision_log_refs", []),
                    )
                    candidates[candidate_id] = candidate
                candidate.add_evidence(_evidence(path, line_number, line))
                break
    return stats


def _review_patterns() -> list[tuple[str, re.Pattern[str]]]:
    return [
        ("genesis_homoiconicity", re.compile(r"genesis.*homoiconic|homoiconic.*genesis|Genesis.*graph", re.IGNORECASE)),
        ("genesis_authority", re.compile(r"Genesis authority|Genesis Agent|genesis root|Genesis-rooted", re.IGNORECASE)),
        ("genesis_policy", re.compile(r"genesis_exempt|freshness exemption|Genesis.*sunset|Genesis.*cap|theta_hard|theta_soft", re.IGNORECASE)),
        ("truth_primitives", re.compile(r"truth primitives|assert\\.truth|validate\\.claim|refute\\.claim|commit\\.epoch", re.IGNORECASE)),
        ("morphogenic_edges", re.compile(r"morphogenetic|HyperEdge|PROVENANCE|REUSE|REFUTATION|CO_AUTHORSHIP|ATTESTATION|EPOCH_BOUNDARY", re.IGNORECASE)),
        ("external_modeling", re.compile(r"Lean|Terence Tao|Tao|magma|theorem|formal proof", re.IGNORECASE)),
    ]


def _source_priority(source_kind: str) -> int:
    priority = {
        "config": 0,
        "genesis_artifact": 1,
        "adr": 2,
        "spec": 3,
        "runtime_schema": 4,
        "research": 5,
        "test_evidence": 6,
        "other": 7,
    }
    return priority.get(source_kind, 99)


def _raw_match_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in _iter_files():
        text = _read_text(path)
        if text is None:
            continue
        authority_status, canonicality_tier = _status_from_text(path, text)
        source_kind = _source_kind(path)
        for line_number, line in enumerate(text.splitlines(), 1):
            for category, pattern in _review_patterns():
                if not pattern.search(line):
                    continue
                evidence = _evidence(path, line_number, line)
                records.append(
                    {
                        "authority_status": authority_status,
                        "candidate_action": "raw_match_unclassified",
                        "canonicality_tier": canonicality_tier,
                        "category": category,
                        "evidence": evidence.to_dict(),
                        "graph_projection": "support_candidate_graph",
                        "promotion_path": "support_graph_to_core_requires_synthesis_artifact_and_jury_or_cdl_review",
                        "source_kind": source_kind,
                    }
                )
                break
    records.sort(
        key=lambda item: (
            _source_priority(item["source_kind"]),
            item["category"],
            item["evidence"]["source_path"],
            item["evidence"]["source_line"],
            item["evidence"]["evidence_hash"],
        )
    )
    return records


def _unique_review_records(records: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
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
        review_item = {
            **item,
            "candidate_action": "review_required",
            "inclusion_rule": "may_be_promoted_by_jury_or_future_SIM_after_refutation_review",
        }
        unique.append(review_item)
        if len(unique) >= limit:
            break
    return unique


def _exclusion_reason(item: dict[str, Any]) -> str:
    source_kind = item["source_kind"]
    category = item["category"]
    if source_kind == "test_evidence":
        return "test_evidence_not_promoted_to_genesis_node"
    if source_kind == "research":
        return "research_context_requires_synthesis_before_core_promotion"
    if category == "external_modeling":
        return "external_modeling_context_not_ilc_native_node"
    if category == "morphogenic_edges":
        return "edge_semantics_context_not_standalone_genesis_node"
    if source_kind == "other":
        return "low_authority_source_requires_manual_triage"
    return "not_selected_for_bounded_review_queue"


def _audit_ledgers(nodes: list[dict[str, Any]], review_limit: int = 160) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    raw_records = _raw_match_records()
    promoted_hashes: dict[str, str] = {}
    for node in nodes:
        for evidence in node["evidence"]:
            promoted_hashes[evidence["evidence_hash"]] = node["candidate_id"]
    review_sources = _unique_review_records(raw_records, review_limit)
    review_hashes = {item["evidence"]["evidence_hash"] for item in review_sources}

    raw_match_ledger: list[dict[str, Any]] = []
    rejected_sources: list[dict[str, Any]] = []
    promotion_trace: list[dict[str, Any]] = []
    for item in raw_records:
        evidence_hash = item["evidence"]["evidence_hash"]
        promoted_id = promoted_hashes.get(evidence_hash)
        if promoted_id is not None:
            action = "promoted_node_evidence"
            reason = "evidence_attached_to_promoted_candidate_node"
        elif evidence_hash in review_hashes:
            action = "review_required"
            reason = "retained_in_bounded_review_queue"
        else:
            action = "rejected_candidate_source"
            reason = _exclusion_reason(item)
        ledger_item = {
            **item,
            "candidate_action": action,
            "exclusion_reason": None if action != "rejected_candidate_source" else reason,
            "matched_promoted_candidate_id": promoted_id,
            "selection_reason": reason,
        }
        raw_match_ledger.append(ledger_item)
        if action == "rejected_candidate_source":
            rejected_sources.append(ledger_item)
    for node in nodes:
        promotion_trace.append(
            {
                "candidate_id": node["candidate_id"],
                "core_star_map_candidate": node["core_star_map_candidate"],
                "decision_log_refs": node["decision_log_refs"],
                "evidence_count": len(node["evidence"]),
                "inclusion_status": node["inclusion_status"],
                "promotion_path": node["promotion_path"],
                "selection_reason": node["rationale"],
            }
        )
    return raw_match_ledger, review_sources, rejected_sources, promotion_trace


def _dredge_summary(raw_match_ledger: list[dict[str, Any]], rejected_sources: list[dict[str, Any]]) -> dict[str, Any]:
    def counts(field: str, records: list[dict[str, Any]]) -> dict[str, int]:
        result: dict[str, int] = {}
        for record in records:
            key = str(record.get(field))
            result[key] = result.get(key, 0) + 1
        return dict(sorted(result.items()))

    return {
        "raw_match_count": len(raw_match_ledger),
        "rejected_candidate_source_count": len(rejected_sources),
        "raw_matches_by_action": counts("candidate_action", raw_match_ledger),
        "raw_matches_by_category": counts("category", raw_match_ledger),
        "raw_matches_by_source_kind": counts("source_kind", raw_match_ledger),
        "rejections_by_reason": counts("exclusion_reason", rejected_sources),
    }


def build_inventory(curated_seed: Path = DEFAULT_CURATED_SEED) -> dict[str, Any]:
    seed = _load_curated_seed(curated_seed)
    candidates: dict[str, Candidate] = {}
    _add_static_truth_primitives(candidates)
    _add_genesis_axioms(candidates)
    _add_static_promoted_candidates(candidates)
    _add_curated_seed_candidates(candidates, seed)
    stats = _scan_candidate_files(candidates)
    _apply_genesis_attested_overrides(candidates, seed)
    ordered = sorted(candidates.values(), key=lambda item: (item.layer, item.category, item.candidate_id))
    nodes = [candidate.to_dict() for candidate in ordered]
    edges = _candidate_edges({node["candidate_id"] for node in nodes}, seed)
    raw_match_ledger, review_sources, rejected_sources, promotion_trace = _audit_ledgers(nodes)
    dredge_summary = _dredge_summary(raw_match_ledger, rejected_sources)
    return {
        "_raw_match_ledger_full": raw_match_ledger,
        "_rejected_candidate_sources_full": rejected_sources,
        "audit_artifacts": {
            "raw_match_ledger_ndjson": str(DEFAULT_RAW_LEDGER_OUT),
            "rejected_candidate_sources_ndjson": str(DEFAULT_REJECTED_LEDGER_OUT),
        },
        "decision_log": _decision_log(),
        "dredge_summary": dredge_summary,
        "edges": edges,
        "metadata": {
            "description": "Deterministic candidate inventory for a proposed Genesis-level morphogenic hypergraph atlas.",
            "format_version": "genesis_node_candidate_crawl.v0.1",
            "curated_seed": str(curated_seed),
            "curated_seed_format_version": seed.get("format_version"),
            "scan_roots": [str(path) for path in SCAN_ROOTS],
            "skip_dirs": sorted(SKIP_DIRS),
            "star_map_metadata_overrides": seed.get("star_map_metadata", {}),
            "stats": stats,
            "type_decomposition_basis": seed.get("type_decomposition_basis", {}),
        },
        "nodes": nodes,
        "promotion_trace": promotion_trace,
        "raw_match_ledger_sample": raw_match_ledger[:20],
        "rejected_candidate_sources_sample": rejected_sources[:20],
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
    decomposition_recipe: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if edge_type not in RUNTIME_EDGE_TYPES:
        feature_hints = {
            **feature_hints,
            "edge_type_status": "atlas_proposal_pending_ADR",
            "proposed_edge_type": True,
        }
    edge = {
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
    if decomposition_recipe is not None:
        edge["decomposition_recipe"] = decomposition_recipe
    return edge


def _edge_recipe_from_seed(seed: dict[str, Any], edge_id: str) -> dict[str, Any] | None:
    recipe = seed.get("edge_decomposition_recipes", {}).get(edge_id)
    return copy.deepcopy(recipe) if recipe is not None else None


def _curated_seed_edges(seed: dict[str, Any]) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for spec in seed.get("edges", []):
        edge_spec = copy.deepcopy(spec)
        edges.append(
            _edge(
                edge_spec["edge_id"],
                edge_spec["source"],
                edge_spec["target"],
                edge_spec["edge_type"],
                edge_spec["relation"],
                confidence=edge_spec["confidence"],
                rationale=edge_spec["rationale"],
                feature_hints=edge_spec.get("feature_hints", {}),
                decision_log_refs=edge_spec.get("decision_log_refs", []),
                decomposition_recipe=edge_spec.get("decomposition_recipe")
                or _edge_recipe_from_seed(seed, edge_spec["edge_id"]),
            )
        )
    return edges


def _candidate_edges(node_ids: set[str], seed: dict[str, Any]) -> list[dict[str, Any]]:
    proposed = _curated_seed_edges(seed)
    for primitive in TRUTH_PRIMITIVES:
        proposed.append(
            _edge(
                f"edge:genesis_agent_attests_{_slug(primitive)}",
                GENESIS_AGENT_ID,
                f"truth_primitive:{primitive}",
                "ATTESTATION",
                "genesis_signed_primitive",
                confidence=0.91,
                rationale="Genesis Agent 1 signs the primitive surface at bootstrap; reuse flow is economically capped by the Genesis hard limit.",
                feature_hints={
                    "authority_carrying": True,
                    "directional": True,
                    "economic_cap_policy": GENESIS_CAP_POLICY_ID,
                    "economic_surface": "genesis_attested_provenance_flow",
                    "genesis_bootstrap": True,
                    "layer_span": "L2_to_L0",
                    "reuse_economic_surface": "high",
                    "sim_weight_seed": 0.95,
                },
                decision_log_refs=["GND-0012", "GND-0022", "GND-0023"],
            )
        )
    for axiom in ("axiom:math:01", "axiom:physics:01", "axiom:logic:01"):
        primitive_edge_id = f"edge:assert_truth_to_{_slug(axiom)}"
        proposed.append(
            _edge(
                primitive_edge_id,
                "truth_primitive:assert.truth",
                axiom,
                "PRIMITIVE_INVOCATION",
                "operator_instantiates_assertion",
                confidence=0.82,
                rationale="Genesis axioms are expressed through assert.truth; the primitive is an operator, not an attesting agent.",
                feature_hints={
                    "directional": True,
                    "economic_surface": "none",
                    "genesis_bootstrap": True,
                    "layer_span": "L0_to_L1",
                    "non_economic_edge": True,
                    "sim_weight_seed": 1.0,
                },
                decision_log_refs=["GND-0011", "GND-0024"],
                decomposition_recipe=_edge_recipe_from_seed(seed, primitive_edge_id),
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
                    "economic_cap_policy": GENESIS_CAP_POLICY_ID,
                    "economic_surface": "genesis_attested_provenance_flow",
                    "genesis_exempt": True,
                    "layer_span": "L2_to_L1",
                    "sim_weight_seed": 0.9,
                },
                decision_log_refs=["GND-0012", "GND-0023"],
            )
        )
        proposed.append(
            _edge(
                f"edge:{_slug(axiom)}_to_genesis_state_bundle",
                axiom,
                "artifact:genesis_state_bundle",
                "PROVENANCE",
                "included_in_seed_bundle",
                confidence=0.76,
                rationale="Genesis axioms are ancestors of the Genesis state bundle that carries seed state.",
                feature_hints={
                    "directional": True,
                    "layer_span": "L1_to_L2",
                    "sim_expansion_required": True,
                    "sim_weight_seed": 0.7,
                },
                decision_log_refs=["GND-0015", "GND-0025"],
            )
        )
    proposed.extend(
        [
            _edge(
                "edge:adr_0004_to_star_map_demotion",
                "truth_primitive:commit.epoch",
                "artifact:star_map_demoted_by_adr_0004",
                "PROVENANCE",
                "records_truth_primitive_replacement",
                confidence=0.78,
                rationale="ADR-0004 replaces the prior star.map primitive slot with commit.epoch and records the demotion as governance history.",
                feature_hints={
                    "directional": True,
                    "layer_span": "L0_to_L2",
                    "sim_weight_seed": 0.5,
                    "supersession_event": True,
                },
                decision_log_refs=["GND-0032"],
            ),
            _edge(
                "edge:star_map_demotion_to_adr_0033",
                "artifact:star_map_demoted_by_adr_0004",
                "adr:0033_star_map_homoiconic_entity",
                "PROVENANCE",
                "reclassified_as_star_map_artifact",
                confidence=0.76,
                rationale="The demoted star.map primitive slot is later represented by ADR-0033 as a homoiconic star-map entity.",
                feature_hints={
                    "directional": True,
                    "layer_span": "L2_to_L4",
                    "sim_weight_seed": 0.5,
                    "superseded_by": "adr:0033_star_map_homoiconic_entity",
                },
                decision_log_refs=["GND-0032"],
            ),
            _edge(
                "edge:keygen_to_pubkey_record",
                "ceremony:genesis_agent1_keygen_838a",
                "artifact:genesis_agent1_pubkey_record_838a",
                "ATTESTATION",
                "produces_public_key_record",
                confidence=0.86,
                rationale="The keygen ceremony produces the public key record used by Genesis Agent 1.",
                feature_hints={
                    "authority_carrying": True,
                    "directional": True,
                    "layer_span": "L2_to_L2",
                    "sim_weight_seed": 0.75,
                },
                decision_log_refs=["GND-0003", "GND-0026"],
            ),
            _edge(
                "edge:pubkey_record_to_genesis_agent",
                "artifact:genesis_agent1_pubkey_record_838a",
                GENESIS_AGENT_ID,
                "ATTESTATION",
                "identifies_authority_key",
                confidence=0.88,
                rationale="The public key record identifies the committed Genesis Agent 1 authority key.",
                feature_hints={
                    "authority_carrying": True,
                    "directional": True,
                    "layer_span": "L2_to_L2",
                    "sim_weight_seed": 0.78,
                },
                decision_log_refs=["GND-0003", "GND-0026"],
            ),
            _edge(
                "edge:genesis_agent_to_assertion_schema",
                GENESIS_AGENT_ID,
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
                "truth_primitive:assert.truth",
                "artifact:genesis_authority_assertion_schema",
                "PROVENANCE",
                "specializes_primitive",
                confidence=0.90,
                rationale="assert.truth is the ancestor primitive; the Genesis assertion schema is its constrained authority specialization.",
                feature_hints={
                    "directional": True,
                    "layer_span": "L0_to_L2",
                    "schema_edge": True,
                    "sim_weight_seed": 0.75,
                },
                decision_log_refs=["GND-0014", "GND-0025"],
            ),
            _edge(
                "edge:bootstrap_boundary_to_state_bundle",
                "artifact:canonical_self_describing_bootstrap_boundary",
                "artifact:genesis_state_bundle",
                "GOVERNS",
                "governs_lineage",
                confidence=0.86,
                rationale="ADR-0027 governs the self-describing bootstrap lineage; this is governance, not PROVENANCE ancestry.",
                feature_hints={
                    "authority_carrying": True,
                    "directional": True,
                    "layer_span": "L2_to_L2",
                    "lineage_edge": True,
                    "sim_weight_seed": 0.8,
                },
                decision_log_refs=["GND-0016", "GND-0025"],
                decomposition_recipe=_edge_recipe_from_seed(seed, "edge:bootstrap_boundary_to_state_bundle"),
            ),
            _edge(
                "edge:state_bundle_to_release_contract",
                "artifact:genesis_state_bundle",
                "artifact:genesis_release_artifact_contract",
                "PROVENANCE",
                "release_contract_descends_from_state_bundle",
                confidence=0.78,
                rationale="Genesis release artifacts are downstream of the state bundle lineage.",
                feature_hints={
                    "directional": True,
                    "layer_span": "L2_to_L2",
                    "lineage_edge": True,
                    "sim_weight_seed": 0.68,
                },
                decision_log_refs=["GND-0005", "GND-0025"],
            ),
            _edge(
                "edge:release_contract_to_release_provenance",
                "artifact:genesis_release_artifact_contract",
                "artifact:genesis_release_provenance_phase_228",
                "PROVENANCE",
                "records_release_provenance",
                confidence=0.82,
                rationale="The phase 228 provenance artifact records execution evidence for the release contract.",
                feature_hints={
                    "directional": True,
                    "layer_span": "L2_to_L2",
                    "lineage_edge": True,
                    "sim_weight_seed": 0.68,
                },
                decision_log_refs=["GND-0005", "GND-0025"],
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
                GENESIS_CAP_POLICY_ID,
                "truth_primitive:commit.epoch",
                "CONSTRAINS",
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
                decomposition_recipe=_edge_recipe_from_seed(seed, "edge:theta_hard_to_commit_epoch"),
            ),
            _edge(
                "edge:accrual_governor_to_theta_hard",
                "policy:genesis_accrual_governor",
                GENESIS_CAP_POLICY_ID,
                "GOVERNS",
                "enforces_hard_cap",
                confidence=0.88,
                rationale="The Genesis accrual governor is the policy surface that enforces the 5% hard cap.",
                feature_hints={
                    "directional": True,
                    "economic_surface": "genesis_accrual_cap",
                    "layer_span": "L3_to_L3",
                    "sim_weight_seed": 0.64,
                },
                decision_log_refs=["GND-0007", "GND-0018"],
                decomposition_recipe=_edge_recipe_from_seed(seed, "edge:accrual_governor_to_theta_hard"),
            ),
            _edge(
                "edge:theta_soft_to_accrual_governor",
                "policy:genesis_theta_soft_exp_minus_3",
                "policy:genesis_accrual_governor",
                "CONSTRAINS",
                "parameterizes_soft_taper",
                confidence=0.80,
                rationale="theta_soft parameterizes taper compression before the hard cap is reached.",
                feature_hints={
                    "directional": True,
                    "economic_surface": "genesis_accrual_soft_taper",
                    "layer_span": "L3_to_L3",
                    "sim_weight_seed": 0.58,
                },
                decision_log_refs=["GND-0007", "GND-0018"],
                decomposition_recipe=_edge_recipe_from_seed(seed, "edge:theta_soft_to_accrual_governor"),
            ),
            _edge(
                "edge:genesis_agent_subject_to_freshness_exemption",
                GENESIS_AGENT_ID,
                "policy:genesis_freshness_exemption",
                "CONSTRAINS",
                "subject_to_bootstrap_exemption_policy",
                confidence=0.72,
                rationale="Genesis Agent 1 is subject to the bootstrap exemption policy; the policy does not attest the agent.",
                feature_hints={
                    "directional": True,
                    "genesis_exempt": True,
                    "layer_span": "L2_to_L3",
                    "sunset_required": True,
                    "sim_weight_seed": 0.55,
                },
                decision_log_refs=["GND-0019", "GND-0028"],
                decomposition_recipe=_edge_recipe_from_seed(seed, "edge:genesis_agent_subject_to_freshness_exemption"),
            ),
            _edge(
                "edge:genesis_authority_sunset_to_exemption",
                "policy:genesis_authority_sunset",
                "policy:genesis_freshness_exemption",
                "CONSTRAINS",
                "bounds_bootstrap_exemption",
                confidence=0.82,
                rationale="Genesis exemption must be bounded by sunset and reconciliation policy.",
                feature_hints={
                    "directional": True,
                    "genesis_exempt": True,
                    "layer_span": "L3_to_L3",
                    "sunset_required": True,
                    "sim_weight_seed": 0.56,
                },
                decision_log_refs=["GND-0008", "GND-0019", "GND-0028"],
                decomposition_recipe=_edge_recipe_from_seed(seed, "edge:genesis_authority_sunset_to_exemption"),
            ),
            _edge(
                "edge:cdl_084_to_provenance_decay_alpha",
                "cdl:084_provenance_chain_attribution",
                "policy:provenance_decay_alpha_0_45",
                "GOVERNS",
                "locks_policy_constant",
                confidence=0.92,
                rationale="CDL-084 Q2 locks PROVENANCE_DECAY_ALPHA at Decimal(0.45), controlling PROVENANCE chain ECU flow.",
                feature_hints={
                    "directional": True,
                    "economic_surface": "provenance_chain_decay",
                    "layer_span": "L4_to_L3",
                    "sim_weight_seed": 0.72,
                },
                decision_log_refs=["GND-0027", "GND-0028"],
                decomposition_recipe=_edge_recipe_from_seed(seed, "edge:cdl_084_to_provenance_decay_alpha"),
            ),
            _edge(
                "edge:adr_0033_to_bootstrap_boundary",
                "adr:0033_star_map_homoiconic_entity",
                "artifact:canonical_self_describing_bootstrap_boundary",
                "GOVERNS",
                "defines_star_map_projection_boundary",
                confidence=0.80,
                rationale="ADR-0033 defines the star-map projection that consumes the canonical bootstrap boundary as a load surface.",
                feature_hints={
                    "directional": True,
                    "layer_span": "L4_to_L2",
                    "sim_weight_seed": 0.62,
                },
                decision_log_refs=["GND-0010", "GND-0028"],
                decomposition_recipe=_edge_recipe_from_seed(seed, "edge:adr_0033_to_bootstrap_boundary"),
            ),
        ]
    )
    return [
        edge
        for edge in sorted(proposed, key=lambda item: item["edge_id"])
        if edge["source"] in node_ids and edge["target"] in node_ids
    ]


def _decision_log() -> list[dict[str, str]]:
    entries = [
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
        {
            "decision_id": "GND-0022",
            "decision": "Keep truth primitive IDs universal while recording Genesis attestation as metadata and edges.",
            "rationale": "primitive identity should not be renamed as Genesis-owned; Genesis authority enters through signed ATTESTATION relations.",
        },
        {
            "decision_id": "GND-0023",
            "decision": "Mark Genesis-to-truth-primitive attestation as an economically significant capped surface.",
            "rationale": "Truth primitives are high-traffic reuse surfaces; Genesis accrual must remain visible and bounded by the 5% hard cap.",
        },
        {
            "decision_id": "GND-0024",
            "decision": "Use PRIMITIVE_INVOCATION for operator-to-content edges instead of ATTESTATION.",
            "rationale": "assert.truth is an operator, not an authority identity that vouches for content.",
        },
        {
            "decision_id": "GND-0025",
            "decision": "Orient PROVENANCE edges ancestor-to-descendant and use non-provenance types for governance overlays.",
            "rationale": "Wrong edge direction corrupts downstream Laplacian/SIM interpretation; governance and overlay relations need explicit types.",
        },
        {
            "decision_id": "GND-0026",
            "decision": "Represent core star-map and support-candidate graph projections in the same crawl artifact.",
            "rationale": "Diffuse material can be retained and later promoted through synthesis without being treated as canonical core at ingestion time.",
        },
        {
            "decision_id": "GND-0027",
            "decision": "Promote CDL-084 PROVENANCE_DECAY_ALPHA Decimal(0.45) as a core economic policy node.",
            "rationale": "The alpha constant directly governs PROVENANCE chain ECU flow, including chains passing through Genesis-attested primitives and axioms.",
        },
        {
            "decision_id": "GND-0028",
            "decision": "Flag PRIMITIVE_INVOCATION, GOVERNS, and CONSTRAINS as atlas-proposed edge types.",
            "rationale": "These are useful for the Genesis star-map atlas but are not members of the current runtime EdgeType enum.",
        },
        {
            "decision_id": "GND-0029",
            "decision": "Remove the coarse morphogenetic overlay hub from the core star-map candidate set.",
            "rationale": "The individual ADR/CDL substrate nodes now carry the usable semantics without a redundant single-layer hub.",
        },
        {
            "decision_id": "GND-0030",
            "decision": "Retain raw-match, rejected-candidate, and promotion-trace ledgers for dredge auditability.",
            "rationale": "The atlas crawl must show what was seen and not promoted, not only the final node set.",
        },
        {
            "decision_id": "GND-0031",
            "decision": "Represent policy constants with typed value, symbol, and applies_to fields plus a symbol index.",
            "rationale": "Agents need deterministic index lookup for executable constants; LLM semantic extraction from prose is not an operational value path.",
        },
        {
            "decision_id": "GND-0032",
            "decision": "Represent ADR-0004 star.map demotion as a governance event node.",
            "rationale": "The demotion is a real ILC refutation/supersession event and should be visible in the Genesis morphogenic graph.",
        },
        {
            "decision_id": "GND-0033",
            "decision": "Promote theta-soft and the Genesis Agent 1 keygen ceremony into the core star-map projection.",
            "rationale": "The accrual governor needs both hard and soft theta constants, and the keygen ceremony is the provenance event that produces the Genesis authority key record.",
        },
        {
            "decision_id": "GND-0034",
            "decision": "Require decomposition_recipe for proposed edge and hyperedge type definitions before ratification.",
            "rationale": "Types should derive from truth primitives where possible; identical recipes must unify or justify distinct role/scope semantics.",
        },
        {
            "decision_id": "GND-0035",
            "decision": "Reserve Markov/trace terminology for a future formal kernel algebra ADR.",
            "rationale": "Use derived_from, projection_rule, observer_scope, and transition_basis for atlas projections until trace logic is formally specified.",
        },
    ]
    for entry in entries:
        entry["id"] = entry["decision_id"]
    return entries


def _write_ndjson(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, allow_nan=False, sort_keys=True) + "\n")


def _public_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in payload.items()
        if not key.startswith("_")
    }


def _core_star_map_payload(payload: dict[str, Any]) -> dict[str, Any]:
    nodes = [node for node in payload["nodes"] if node["core_star_map_candidate"] is True]
    node_ids = {node["candidate_id"] for node in nodes}
    edges = [edge for edge in payload["edges"] if edge["source"] in node_ids and edge["target"] in node_ids]
    metadata = {
        "description": "Core Genesis star-map projection for high-authority install/load graph consumers.",
        "format_version": "genesis_core_star_map.v0.1",
        "source_crawl": str(DEFAULT_JSON_OUT),
    }
    metadata.update(payload["metadata"].get("star_map_metadata_overrides", {}))
    if payload["metadata"].get("type_decomposition_basis"):
        metadata["type_decomposition_basis"] = payload["metadata"]["type_decomposition_basis"]
    return {
        "edges": edges,
        "metadata": metadata,
        "nodes": nodes,
    }


def _core_star_map_index_payload(star_map: dict[str, Any]) -> dict[str, Any]:
    symbols: dict[str, str] = {}
    applies_to: dict[str, list[str]] = {}
    nodes_by_id: dict[str, dict[str, Any]] = {}
    edges_by_type: dict[str, list[str]] = {}
    nodes_by_kind: dict[str, list[str]] = {}
    for node in star_map["nodes"]:
        node_id = node["candidate_id"]
        nodes_by_id[node_id] = {
            "canonicality_tier": node["canonicality_tier"],
            "node_kind": node["node_kind"],
            "symbol": node["symbol"],
            "value": node["value"],
        }
        nodes_by_kind.setdefault(node["node_kind"], []).append(node_id)
        if node["symbol"]:
            symbols[node["symbol"]] = node_id
        for target in node["applies_to"]:
            applies_to.setdefault(target, []).append(node_id)
    for edge in star_map["edges"]:
        edges_by_type.setdefault(edge["edge_type"], []).append(edge["edge_id"])
    return {
        "applies_to": {key: sorted(value) for key, value in sorted(applies_to.items())},
        "edges_by_type": {key: sorted(value) for key, value in sorted(edges_by_type.items())},
        "metadata": {
            "description": "Lookup index for the Genesis core star-map projection.",
            "format_version": "genesis_core_star_map_index.v0.1",
            "source_star_map": str(DEFAULT_STAR_MAP_OUT),
        },
        "nodes_by_id": dict(sorted(nodes_by_id.items())),
        "nodes_by_kind": {key: sorted(value) for key, value in sorted(nodes_by_kind.items())},
        "symbols": dict(sorted(symbols.items())),
    }


def write_inventory(
    payload: dict[str, Any],
    json_out: Path,
    inventory_out: Path,
    decision_log_out: Path,
    raw_ledger_out: Path,
    rejected_ledger_out: Path,
    star_map_out: Path,
    star_map_index_out: Path,
) -> None:
    json_out.parent.mkdir(parents=True, exist_ok=True)
    inventory_out.parent.mkdir(parents=True, exist_ok=True)
    decision_log_out.parent.mkdir(parents=True, exist_ok=True)
    _write_ndjson(raw_ledger_out, payload["_raw_match_ledger_full"])
    _write_ndjson(rejected_ledger_out, payload["_rejected_candidate_sources_full"])
    public_payload = _public_payload(payload)
    public_payload["audit_artifacts"] = {
        "raw_match_ledger_ndjson": str(raw_ledger_out),
        "rejected_candidate_sources_ndjson": str(rejected_ledger_out),
    }
    json_out.write_text(json.dumps(public_payload, allow_nan=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    star_map = _core_star_map_payload(public_payload)
    star_map["metadata"]["source_crawl"] = str(json_out)
    star_map_out.parent.mkdir(parents=True, exist_ok=True)
    star_map_out.write_text(json.dumps(star_map, allow_nan=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    star_map_index = _core_star_map_index_payload(star_map)
    star_map_index["metadata"]["source_star_map"] = str(star_map_out)
    star_map_index_out.parent.mkdir(parents=True, exist_ok=True)
    star_map_index_out.write_text(json.dumps(star_map_index, allow_nan=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    inventory_out.write_text(_render_inventory_md(public_payload), encoding="utf-8")
    decision_log_out.write_text(_render_decision_log_md(public_payload), encoding="utf-8")


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
        f"- Raw match ledger entries: `{payload['dredge_summary']['raw_match_count']}`",
        f"- Rejected candidate sources: `{payload['dredge_summary']['rejected_candidate_source_count']}`",
        f"- Candidate nodes: `{len(payload['nodes'])}`",
        f"- Review-required sources: `{len(payload['review_required_sources'])}`",
        f"- Raw ledger artifact: `{payload['audit_artifacts']['raw_match_ledger_ndjson']}`",
        f"- Rejected ledger artifact: `{payload['audit_artifacts']['rejected_candidate_sources_ndjson']}`",
        f"- Rejections by reason: `{payload['dredge_summary']['rejections_by_reason']}`",
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
            "Each JSON node records: `candidate_id`, `label`, `layer`, `depth_index`, `category`, `node_kind`, `authority_status`, `canonicality_tier`, `inclusion_status`, `graph_projection`, `promotion_path`, `confidence`, `rationale`, `source_kind`, `evidence`, `edge_hints`, `sensitivity`, `economic_boundary`, `economic_cap_policy`, `reuse_economic_surface`, `genesis_attested`, `genesis_attested_by`, `genesis_exempt`, `symbol`, `value`, `applies_to`, `sunset_status`, `valid_epoch_range`, `version`, `superseded_by`, and `decision_log_refs`.",
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
    lines.extend(
        [
            "",
            "## Rejected Candidate Source Ledger",
            "",
            "These matched sources were retained in the JSON audit trail but excluded from node promotion and the bounded review queue. Each record carries an `exclusion_reason` for future jury/refutation review.",
            "",
            "| Reason | Category | Source Kind | Evidence |",
            "|---|---|---|---|",
        ]
    )
    for item in payload["rejected_candidate_sources_sample"][:40]:
        evidence = item["evidence"]
        source = f"{evidence['source_path']}:{evidence['source_line']}"
        lines.append(
            "| "
            + " | ".join(
                [
                    item["exclusion_reason"],
                    item["category"],
                    item["source_kind"],
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
        decision_id = decision.get("id", decision["decision_id"])
        lines.append(f"| `{decision_id}` | {decision['decision']} | {decision['rationale']} |")
    lines.append("")
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--curated-seed", type=Path, default=DEFAULT_CURATED_SEED)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--raw-ledger-out", type=Path, default=DEFAULT_RAW_LEDGER_OUT)
    parser.add_argument("--rejected-ledger-out", type=Path, default=DEFAULT_REJECTED_LEDGER_OUT)
    parser.add_argument("--star-map-out", type=Path, default=DEFAULT_STAR_MAP_OUT)
    parser.add_argument("--star-map-index-out", type=Path, default=DEFAULT_STAR_MAP_INDEX_OUT)
    parser.add_argument("--inventory-out", type=Path, default=DEFAULT_INVENTORY_OUT)
    parser.add_argument("--decision-log-out", type=Path, default=DEFAULT_DECISION_LOG_OUT)
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    payload = build_inventory(args.curated_seed)
    write_inventory(
        payload,
        args.json_out,
        args.inventory_out,
        args.decision_log_out,
        args.raw_ledger_out,
        args.rejected_ledger_out,
        args.star_map_out,
        args.star_map_index_out,
    )
    print(json.dumps(payload["metadata"], allow_nan=False, sort_keys=True))


if __name__ == "__main__":
    main()
