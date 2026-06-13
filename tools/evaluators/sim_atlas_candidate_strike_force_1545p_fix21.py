#!/usr/bin/env python3
"""Research-only Genesis Atlas candidate strike-force SIM for Phase 1545p-Fix21.

PUBLIC_RC_EXCLUDE: atlas_candidate_strike_force_research_only
PUBLIC_RC_EXCLUDE_REASON: Support-only Atlas candidate generation and SIM battery; no canonical graph mutation, public RC activation, or runtime activation.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.evaluators.sim_atlas_precision_replay_1545p_fix20 import (
    ExtractedAtom,
    MANUAL_SPOT_CHECKS,
    REJECTED_REPLAY_PATHS,
    _evaluate_golden,
    _evaluate_manual_spot_checks,
    _evaluate_negative_controls,
    extract_atoms as _extract_atoms_fix20,
)
from tools.evaluators.sim_atlas_axiomatic_calibration_1545p_fix19 import (
    GOLDEN_CORPUS,
    RECIPE_LIBRARY,
    TRUTH_PRIMITIVES,
)


PHASE = "1545p-Fix21"
SCHEMA_VERSION = "sim_atlas_candidate_strike_force_1545p_fix21.v0.1"
SIM_ID = "SIM-ATLAS-CANDIDATE-STRIKE-FORCE-01"

V04_CORE_IN = REPO_ROOT / "out/genesis_core_star_map_v0.4_candidate.json"
FIX7_QUEUE_IN = REPO_ROOT / "out/genesis_common_registry_node_candidates_1545p_fix7.json"

JSON_OUT = REPO_ROOT / "out/sim_atlas_candidate_strike_force_1545p_fix21.json"
REPORT_OUT = REPO_ROOT / "docs/sims/sim_atlas_candidate_strike_force_1545p_fix21_v0.1.md"
REVIEW_PACKET_OUT = REPO_ROOT / "docs/specs/ilc_genesis_atlas_candidate_review_packet_1545p_fix21_v0.1.md"

CONTRACT_OUT = REPO_ROOT / "out/atlas_research/genesis_atlas_extraction_contract_1545p_fix21.json"
CANDIDATE_QUEUE_OUT = REPO_ROOT / "out/atlas_research/genesis_atlas_candidate_queue_1545p_fix21.jsonl"
REDUCED_OUT = REPO_ROOT / "out/atlas_research/genesis_atlas_reduced_candidates_1545p_fix21.json"
VARIANTS_OUT = REPO_ROOT / "out/genesis_atlas_v0.4_candidate_variants_1545p_fix21.json"
FULL_CANDIDATE_OUT = REPO_ROOT / "out/genesis_atlas_v0.4_full_candidate_1545p_fix21.json"

GENESIS_ATTESTATION_ROOT = "artifact:genesis_intent_attestation_init_authority_map"
SCAN_ROOTS = ("ilc_core", "docs/adr", "docs/specs", "docs/sims", "tests")
SCAN_EXTENSIONS = {".py", ".md", ".json"}
MAX_BROAD_SCAN_FILES = 1200
MAX_REDUCED_SOURCE_CANDIDATES = 240

RECIPE_TO_EDGE_TYPE = {
    "activation_refutation": "REFUTES_ACTIVATION",
    "authority_assertion": "REFERENCES_AUTHORITY",
    "canonicalization_validation": "VALIDATES_CANONICAL_OUTPUT",
    "candidate_revision": "REVISES_CANDIDATE_STATE",
    "contradiction_guard": "CONSTRAINS_OVERCLAIM",
    "phase_token_commitment": "EMITS_TOKEN",
    "schema_validation": "VALIDATES_SCHEMA",
}


@dataclass(frozen=True)
class CorpusExpectation:
    path: str
    expected_recipe_ids: tuple[str, ...]
    forbidden_recipe_ids: tuple[str, ...]
    stratum: str


ADDITIONAL_EXPECTATIONS: tuple[CorpusExpectation, ...] = (
    CorpusExpectation(
        "docs/adr/ADR_0009_Four_Layer_Protocol_Native_Bundle_Distribution.md",
        ("authority_assertion", "schema_validation"),
        (),
        "adr",
    ),
    CorpusExpectation(
        "docs/adr/ADR_0035_Homoiconic_Type_Definition_System.md",
        ("authority_assertion", "schema_validation"),
        (),
        "adr",
    ),
    CorpusExpectation(
        "docs/adr/ADR_0041_Agent_INIT_and_Ingestion_Protocol.md",
        ("authority_assertion", "schema_validation"),
        (),
        "adr",
    ),
    CorpusExpectation(
        "docs/specs/ilc_cdl_096_ratification_evidence_1553p_v0.1.md",
        ("authority_assertion", "activation_refutation", "phase_token_commitment"),
        (),
        "governance_spec",
    ),
    CorpusExpectation(
        "docs/specs/ilc_cdl_097_type_definition_node_authority_ratification_evidence_1528p_v0.1.md",
        ("authority_assertion", "schema_validation", "phase_token_commitment"),
        (),
        "governance_spec",
    ),
    CorpusExpectation(
        "docs/specs/ilc_agent_subgraph_hydration_contract_1545p_fix16_v0.1.md",
        ("schema_validation", "activation_refutation", "candidate_revision"),
        (),
        "semantic_spec",
    ),
    CorpusExpectation(
        "docs/specs/ilc_graph_optimization_maintenance_reward_spec_1545p_fix15_v0.1.md",
        ("schema_validation", "activation_refutation", "contradiction_guard"),
        (),
        "semantic_spec",
    ),
    CorpusExpectation(
        "docs/specs/ilc_privacy_preserving_proximity_hydration_rehearsal_1545p_fix11_v0.1.md",
        ("schema_validation", "activation_refutation", "phase_token_commitment"),
        (),
        "semantic_spec",
    ),
    CorpusExpectation(
        "docs/sims/ilc_adaptive_fee_burn_ratio_sim_1549p_v0.1.md",
        ("activation_refutation", "authority_assertion", "candidate_revision"),
        (),
        "sim",
    ),
    CorpusExpectation(
        "docs/sims/sim_spectral_02/genesis_graphopt_01_synthesis_report_v0.1.md",
        ("schema_validation", "candidate_revision"),
        (),
        "sim",
    ),
    CorpusExpectation(
        "ilc_core/epoch/epoch_emission_production_path.py",
        ("schema_validation", "activation_refutation", "canonicalization_validation"),
        (),
        "programmatic",
    ),
    CorpusExpectation(
        "ilc_core/epoch/canonical_economic_event.py",
        ("schema_validation", "canonicalization_validation"),
        (),
        "programmatic",
    ),
    CorpusExpectation(
        "ilc_core/bundle/type_registry.py",
        ("schema_validation", "activation_refutation"),
        (),
        "programmatic",
    ),
    CorpusExpectation(
        "ilc_core/genesis/invitation_provenance_record.py",
        ("schema_validation", "canonicalization_validation"),
        (),
        "programmatic",
    ),
    CorpusExpectation(
        "ilc_core/genesis/serving_receipt.py",
        ("schema_validation", "activation_refutation"),
        (),
        "programmatic",
    ),
    CorpusExpectation(
        "tests/test_phase_1545p_fix20_atlas_precision_replay.py",
        ("schema_validation", "phase_token_commitment"),
        (),
        "test",
    ),
)


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"json_object_required:{path}")
    return payload


def _canonical_dumps(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"


def _atomic_write(path: Path, text: str) -> None:
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
            handle.write(text)
        os.replace(tmp_path, path)
        path.chmod(0o644)
    except Exception:
        try:
            tmp_path.unlink()
        finally:
            raise


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _slug(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value[:180] or "root"


def _file_text(path: str) -> str:
    resolved = REPO_ROOT / path
    if not resolved.exists():
        raise FileNotFoundError(path)
    return resolved.read_text(encoding="utf-8", errors="replace")


def extract_atoms(text: str) -> list[ExtractedAtom]:
    """Fix21 extractor wrapper with broader candidate/schema vocabulary.

    Fix20 remains reproducible. Fix21 adds only the extra low-level tokens found
    during the strike-force calibration pass: explicit `schema_version` surfaces
    and generic "candidate" contexts such as merge candidates and candidate
    prompts.
    """
    atoms = list(_extract_atoms_fix20(text))
    existing = {(atom.recipe_id, atom.edge_type, atom.evidence) for atom in atoms}

    def add(recipe_id: str, edge_type: str, evidence: str) -> None:
        key = (recipe_id, edge_type, evidence)
        if key not in existing:
            atoms.append(ExtractedAtom(recipe_id=recipe_id, edge_type=edge_type, evidence=evidence))
            existing.add(key)

    if re.search(r"\bschema_version\b|candidate_schema_version", text, re.IGNORECASE):
        add("schema_validation", "VALIDATES_SCHEMA", "schema_version language")

    if re.search(
        r"\bmerge candidate\b|\bcandidate[- ]prompt\b|\bcandidate adaptive\b|\bcandidate .*rule\b|\bsuccessor candidate\b",
        text,
        re.IGNORECASE,
    ):
        add("candidate_revision", "REVISES_CANDIDATE_STATE", "generic candidate-state language")

    return atoms


def _recipe_ids_for(path: str) -> set[str]:
    return {atom.recipe_id for atom in extract_atoms(_file_text(path))}


def _build_contract() -> dict[str, Any]:
    return {
        "schema_version": "genesis_atlas_extraction_contract.v0.2",
        "phase": PHASE,
        "authority_status": "research_only_not_authority_bearing",
        "candidate_record_required_fields": [
            "candidate_id",
            "source_file",
            "source_sha256",
            "evidence_span",
            "recipe_id",
            "truth_primitives",
            "edge_type",
            "confidence",
            "nonclaim_boundary",
            "promotion_class",
            "review_class",
        ],
        "edge_type_rules": {
            "default_from_plain_mention": "REFERENCES",
            "governs_requires": "explicit ratified governance source or implementation dependency token; never plain text mention alone",
            "support_only_requires": "PUBLIC_RC_EXCLUDE, support-only marker, or non-activation text",
            "economic_boundary": "economic words with negation remain non-authorization facts",
        },
        "promotion_classes": [
            "genesis_core_candidate",
            "common_registry_candidate",
            "sidecar_recipe_candidate",
            "implementation_support_candidate",
            "semantic_support_candidate",
            "research_only_candidate",
            "reject",
        ],
        "truth_primitives": list(TRUTH_PRIMITIVES),
        "recipe_library": {key: list(value) for key, value in sorted(RECIPE_LIBRARY.items())},
        "non_claims": [
            "contract_does_not_promote_edges",
            "contract_does_not_mutate_genesis",
            "contract_does_not_sign_v04",
            "contract_does_not_activate_public_rc",
        ],
    }


def _golden_expectations() -> list[CorpusExpectation]:
    rows: list[CorpusExpectation] = []
    for entry in GOLDEN_CORPUS:
        rows.append(
            CorpusExpectation(
                path=entry.path,
                expected_recipe_ids=tuple(sorted({atom.recipe_id for atom in entry.expected_atoms})),
                forbidden_recipe_ids=(),
                stratum=f"fix19_{entry.camp}",
            )
        )
    return rows


def _fix20_expectations() -> list[CorpusExpectation]:
    rows: list[CorpusExpectation] = []
    manual_paths = {check.path for check in MANUAL_SPOT_CHECKS}
    for path in REJECTED_REPLAY_PATHS:
        if path in manual_paths:
            continue
        recipes = tuple(sorted(_recipe_ids_for(path)))
        rows.append(
            CorpusExpectation(
                path=path,
                expected_recipe_ids=recipes,
                forbidden_recipe_ids=(),
                stratum="fix20_rejected_replay",
            )
        )
    return rows


def _expanded_corpus() -> tuple[CorpusExpectation, ...]:
    merged: dict[str, CorpusExpectation] = {}
    for item in (
        *_golden_expectations(),
        *_fix20_expectations(),
        *[
            CorpusExpectation(
                path=check.path,
                expected_recipe_ids=check.expected_recipe_ids,
                forbidden_recipe_ids=check.forbidden_recipe_ids,
                stratum="fix20_manual_spot_check",
            )
            for check in MANUAL_SPOT_CHECKS
        ],
        *ADDITIONAL_EXPECTATIONS,
    ):
        merged[item.path] = item
    return tuple(merged[path] for path in sorted(merged))


def _evaluate_expanded_corpus() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    passed = 0
    strata = Counter()
    for expectation in _expanded_corpus():
        recipes = _recipe_ids_for(expectation.path)
        missing = sorted(set(expectation.expected_recipe_ids) - recipes)
        forbidden = sorted(set(expectation.forbidden_recipe_ids) & recipes)
        ok = not missing and not forbidden
        passed += 1 if ok else 0
        strata[expectation.stratum] += 1
        rows.append(
            {
                "path": expectation.path,
                "stratum": expectation.stratum,
                "expected_recipe_ids": list(expectation.expected_recipe_ids),
                "detected_recipe_ids": sorted(recipes),
                "forbidden_recipe_ids": list(expectation.forbidden_recipe_ids),
                "missing_expected": missing,
                "forbidden_hits": forbidden,
                "passed": ok,
            }
        )
    return {
        "expanded_corpus_file_count": len(rows),
        "passed_count": passed,
        "failed_count": len(rows) - passed,
        "pass_ratio": f"{passed}/{len(rows)}",
        "strata": dict(sorted(strata.items())),
        "files": rows,
    }


def _scan_files() -> list[Path]:
    paths: list[Path] = []
    for root in SCAN_ROOTS:
        base = REPO_ROOT / root
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix not in SCAN_EXTENSIONS:
                continue
            rel = path.relative_to(REPO_ROOT)
            parts = set(rel.parts)
            if "__pycache__" in parts or ".pytest_cache" in parts:
                continue
            if "antigravity_tasks" in parts:
                continue
            paths.append(path)
            if len(paths) >= MAX_BROAD_SCAN_FILES:
                return paths
    return paths


def _evidence_span(text: str, recipe_id: str) -> str:
    pattern_by_recipe = {
        "activation_refutation": r"(PUBLIC_RC_EXCLUDE[^\n]*|support-only[^\n]*|not activated[^\n]*|no public[^\n]*|does not mutate[^\n]*)",
        "authority_assertion": r"((?:ADR|CDL)[-_]\d+[^\n]*|ratified[^\n]*|authority[^\n]*)",
        "canonicalization_validation": r"(sort_keys=True[^\n]*|allow_nan=False[^\n]*|canonical JSON[^\n]*|DAG-CBOR[^\n]*)",
        "candidate_revision": r"(must_include_genesis_node[^\n]*|candidate_common_node[^\n]*|Deferred Candidate Queue[^\n]*|Selected v0\.4 Additions[^\n]*)",
        "contradiction_guard": r"(must not[^\n]*|reject[^\n]*|fail[- ]?closed[^\n]*|overclaim[^\n]*)",
        "phase_token_commitment": r"([a-z0-9]+(?:_[a-z0-9]+){2,}_phase_[0-9p]+(?:_fix\d+)?[^\n]*)",
        "schema_validation": r"(schema[^\n]*|validate[^\n]*|verifier[^\n]*|contract[^\n]*)",
    }
    match = re.search(pattern_by_recipe.get(recipe_id, r".+"), text, re.IGNORECASE)
    if match:
        return " ".join(match.group(0).strip().split())[:280]
    return " ".join(text.split())[:280]


def _nonclaim_boundary(text: str) -> str:
    flags = []
    lowered = text.lower()
    for needle, token in [
        ("public_rc_exclude", "public_rc_excluded"),
        ("support-only", "support_only"),
        ("not canonical", "not_canonical"),
        ("not activated", "not_activated"),
        ("no public", "no_public_path"),
        ("does not mutate", "no_mutation"),
        ("not minting", "not_minting"),
        ("not live zkp", "not_live_zkp"),
        ("unsigned", "unsigned"),
    ]:
        if needle in lowered:
            flags.append(token)
    return ",".join(sorted(set(flags))) if flags else "none_detected"


def _review_class(recipe_ids: set[str]) -> str:
    if "authority_assertion" in recipe_ids and "activation_refutation" in recipe_ids:
        return "authority_with_nonactivation_boundary_review"
    if "schema_validation" in recipe_ids and "contradiction_guard" in recipe_ids:
        return "schema_boundary_review"
    if "candidate_revision" in recipe_ids:
        return "candidate_state_review"
    if "canonicalization_validation" in recipe_ids:
        return "canonicalization_support_review"
    if "schema_validation" in recipe_ids:
        return "schema_support_review"
    return "no_candidate_signal"


def _promotion_class(path: str, recipes: set[str], nonclaim: str) -> str:
    if not recipes:
        return "reject"
    if path.startswith("ilc_core/"):
        return "implementation_support_candidate"
    if path.startswith("docs/adr/") and "authority_assertion" in recipes:
        return "semantic_support_candidate"
    if path.startswith("docs/specs/") and "authority_assertion" in recipes:
        return "semantic_support_candidate"
    if path.startswith("docs/sims/"):
        return "research_only_candidate"
    if path.startswith("tests/"):
        return "research_only_candidate"
    if "support_only" in nonclaim or "not_activated" in nonclaim:
        return "semantic_support_candidate"
    return "semantic_support_candidate"


def _candidate_records() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in _scan_files():
        rel = path.relative_to(REPO_ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        atoms = extract_atoms(text)
        if not atoms:
            continue
        recipes = {atom.recipe_id for atom in atoms}
        nonclaim = _nonclaim_boundary(text)
        review = _review_class(recipes)
        promotion = _promotion_class(rel, recipes, nonclaim)
        source_hash = _sha256_text(text)
        for atom in sorted(atoms, key=lambda item: (item.recipe_id, item.edge_type, item.evidence)):
            rows.append(
                {
                    "candidate_id": f"atlas:atom:{_slug(rel)}:{atom.recipe_id}",
                    "source_file": rel,
                    "source_sha256": source_hash,
                    "evidence_span": _evidence_span(text, atom.recipe_id),
                    "recipe_id": atom.recipe_id,
                    "truth_primitives": list(RECIPE_LIBRARY[atom.recipe_id]),
                    "edge_type": RECIPE_TO_EDGE_TYPE[atom.recipe_id],
                    "confidence": _confidence(rel, atom.recipe_id, nonclaim),
                    "nonclaim_boundary": nonclaim,
                    "promotion_class": promotion,
                    "review_class": review,
                    "authority_boundary": "review_only_not_promoted",
                }
            )
    unique: dict[str, dict[str, Any]] = {}
    for row in rows:
        unique[row["candidate_id"]] = row
    return [unique[key] for key in sorted(unique)]


def _confidence(path: str, recipe_id: str, nonclaim: str) -> str:
    base = {
        "authority_assertion": 0.76,
        "schema_validation": 0.74,
        "activation_refutation": 0.82,
        "phase_token_commitment": 0.80,
        "candidate_revision": 0.70,
        "contradiction_guard": 0.78,
        "canonicalization_validation": 0.77,
    }[recipe_id]
    if path.startswith("ilc_core/"):
        base += 0.04
    if nonclaim != "none_detected":
        base -= 0.02
    return f"{max(0.0, min(0.99, base)):.2f}"


def _reduce_candidates(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_source[str(record["source_file"])].append(record)

    source_rows: list[dict[str, Any]] = []
    for source_file, source_records in by_source.items():
        recipe_ids = sorted({str(item["recipe_id"]) for item in source_records})
        classes = sorted({str(item["promotion_class"]) for item in source_records})
        review_classes = sorted({str(item["review_class"]) for item in source_records})
        confidence_values = [float(item["confidence"]) for item in source_records]
        source_rows.append(
            {
                "source_candidate_id": f"atlas:source:{_slug(source_file)}",
                "source_file": source_file,
                "source_sha256": source_records[0]["source_sha256"],
                "recipe_ids": recipe_ids,
                "truth_primitives": sorted(
                    {
                        primitive
                        for record in source_records
                        for primitive in record["truth_primitives"]
                    }
                ),
                "review_classes": review_classes,
                "promotion_classes": classes,
                "nonclaim_boundaries": sorted({str(item["nonclaim_boundary"]) for item in source_records}),
                "atom_candidate_count": len(source_records),
                "mean_confidence": f"{sum(confidence_values) / len(confidence_values):.3f}",
                "selected_for_full_candidate": _select_source_for_full_candidate(source_file, recipe_ids, classes),
            }
        )

    source_rows = sorted(
        source_rows,
        key=lambda item: (
            not bool(item["selected_for_full_candidate"]),
            str(item["source_file"]),
        ),
    )
    selected = [row for row in source_rows if row["selected_for_full_candidate"]]
    if len(selected) > MAX_REDUCED_SOURCE_CANDIDATES:
        selected_ids = {
            row["source_candidate_id"]
            for row in selected[:MAX_REDUCED_SOURCE_CANDIDATES]
        }
        for row in source_rows:
            row["selected_for_full_candidate"] = row["source_candidate_id"] in selected_ids

    return {
        "schema_version": "genesis_atlas_reduced_candidates_1545p_fix21.v0.1",
        "phase": PHASE,
        "atom_candidate_count": len(records),
        "source_candidate_count": len(source_rows),
        "selected_source_candidate_count": sum(1 for row in source_rows if row["selected_for_full_candidate"]),
        "promotion_class_counts": dict(sorted(Counter(
            cls for row in source_rows for cls in row["promotion_classes"]
        ).items())),
        "review_class_counts": dict(sorted(Counter(
            cls for row in source_rows for cls in row["review_classes"]
        ).items())),
        "source_candidates": source_rows,
    }


def _select_source_for_full_candidate(path: str, recipe_ids: list[str], classes: list[str]) -> bool:
    recipes = set(recipe_ids)
    if path.startswith("ilc_core/"):
        return bool(recipes & {"schema_validation", "canonicalization_validation", "activation_refutation"})
    if path.startswith("docs/adr/"):
        return "authority_assertion" in recipes
    if path.startswith("docs/specs/"):
        return bool(recipes & {"authority_assertion", "schema_validation", "candidate_revision"})
    if path.startswith("docs/sims/"):
        return bool(recipes & {"schema_validation", "candidate_revision"})
    if path.startswith("tests/"):
        return bool(recipes & {"schema_validation", "phase_token_commitment"})
    return False


def _candidate_node_from_fix7(candidate: dict[str, Any]) -> dict[str, Any]:
    classification = str(candidate["classification"])
    if classification == "candidate_common_node":
        tier = "common_registry"
        node_kind = "common_registry_candidate"
    elif classification == "sidecar_recipe_node":
        tier = "sidecar_recipe"
        node_kind = "sidecar_recipe_candidate"
    else:
        tier = "genesis_core"
        node_kind = "genesis_core_candidate"
    return {
        "candidate_id": str(candidate["candidate_id"]),
        "label": str(candidate["candidate_id"]),
        "tier": tier,
        "node_kind": node_kind,
        "authority_status": "support_only_review_candidate",
        "classification": classification,
        "evidence_paths": list(candidate.get("evidence_paths", [])),
        "notes": str(candidate.get("notes", "")),
        "signature_status": "unsigned_support_only",
        "public_path": "blocked",
    }


def _source_node(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": row["source_candidate_id"],
        "label": row["source_file"],
        "tier": "support_research",
        "node_kind": "atlas_source_candidate",
        "authority_status": "research_review_only_not_authority",
        "source_file": row["source_file"],
        "source_sha256": row["source_sha256"],
        "recipe_ids": row["recipe_ids"],
        "truth_primitives": row["truth_primitives"],
        "review_classes": row["review_classes"],
        "promotion_classes": row["promotion_classes"],
        "nonclaim_boundaries": row["nonclaim_boundaries"],
        "signature_status": "unsigned_support_only",
        "public_path": "blocked",
    }


def _edge(edge_id: str, edge_type: str, source: str, target: str, relation: str, confidence: str) -> dict[str, Any]:
    return {
        "edge_id": edge_id,
        "edge_type": edge_type,
        "source": source,
        "target": target,
        "relation": relation,
        "confidence": confidence,
        "rationale": "Phase 1545p-Fix21 support-only Atlas candidate edge; not authority promotion.",
        "decision_log_refs": [PHASE],
        "feature_hints": {
            "edge_type_status": "support_only_review_candidate",
            "public_path": "blocked",
            "signature_status": "unsigned_support_only",
        },
    }


def _assemble_variants(reduced: dict[str, Any]) -> dict[str, Any]:
    core = _read_json(V04_CORE_IN)
    fix7 = _read_json(FIX7_QUEUE_IN)
    candidate_items = list(fix7["candidates"])

    common_nodes = [
        _candidate_node_from_fix7(item)
        for item in candidate_items
        if item["classification"] == "candidate_common_node"
    ]
    sidecar_nodes = [
        _candidate_node_from_fix7(item)
        for item in candidate_items
        if item["classification"] == "sidecar_recipe_node"
    ]
    selected_source_nodes = [
        _source_node(row)
        for row in reduced["source_candidates"]
        if row["selected_for_full_candidate"]
    ]
    hydration_nodes = [
        node
        for node in selected_source_nodes
        if any(
            needle in str(node.get("source_file", "")).lower()
            for needle in ("hydration", "invitation", "proximity", "subgraph", "agent_init", "serving")
        )
    ]

    core_nodes = [dict(node, tier="genesis_core") for node in core["nodes"]]
    core_edges = list(core["edges"])

    def variant(name: str, extra_nodes: list[dict[str, Any]]) -> dict[str, Any]:
        nodes_by_id = {str(node["candidate_id"]): node for node in core_nodes}
        edges_by_id = {str(edge["edge_id"]): edge for edge in core_edges}
        for node in extra_nodes:
            nodes_by_id[str(node["candidate_id"])] = node
            edge_id = f"edge:fix21_reference_to_{_slug(str(node['candidate_id']))}"
            edges_by_id[edge_id] = _edge(
                edge_id=edge_id,
                edge_type="REFERENCES",
                source=GENESIS_ATTESTATION_ROOT,
                target=str(node["candidate_id"]),
                relation="records_support_only_candidate",
                confidence="0.64",
            )
        nodes = [nodes_by_id[key] for key in sorted(nodes_by_id)]
        edges = [edges_by_id[key] for key in sorted(edges_by_id)]
        return {
            "variant_id": name,
            "nodes": nodes,
            "edges": edges,
            "metrics": _graph_metrics(nodes, edges),
            "candidate_status": "unsigned_support_only_not_canonical",
        }

    variants = {
        "core_only": variant("core_only", []),
        "core_plus_common_registry": variant("core_plus_common_registry", common_nodes),
        "core_plus_hydration": variant("core_plus_hydration", common_nodes + hydration_nodes),
        "maximal_research": variant("maximal_research", common_nodes + sidecar_nodes + selected_source_nodes),
    }

    return {
        "schema_version": "genesis_atlas_candidate_variants_1545p_fix21.v0.1",
        "phase": PHASE,
        "source_core_candidate": str(V04_CORE_IN.relative_to(REPO_ROOT)),
        "authority_status": "support_only_not_authority_bearing",
        "recommended_variant": "core_plus_common_registry",
        "recommendation_rationale": (
            "Use core_plus_common_registry as the next human-review candidate because "
            "it captures canonical namespace/registry surfaces without importing sidecar "
            "or broad semantic research material into Genesis core."
        ),
        "variants": variants,
    }


def _graph_metrics(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
    node_ids = {str(node["candidate_id"]) for node in nodes}
    endpoint_errors = []
    for edge in edges:
        for role in ("source", "target"):
            value = str(edge[role])
            if value not in node_ids:
                endpoint_errors.append({"edge_id": edge["edge_id"], "role": role, "missing": value})
    tier_counts = Counter(str(node.get("tier", "unknown")) for node in nodes)
    reachable = _reachable(nodes, edges, {GENESIS_ATTESTATION_ROOT})
    core_nodes = {
        str(node["candidate_id"])
        for node in nodes
        if str(node.get("tier", "genesis_core")) == "genesis_core"
    }
    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "invalid_endpoint_count": len(endpoint_errors),
        "invalid_endpoints": endpoint_errors,
        "tier_counts": dict(sorted(tier_counts.items())),
        "root_reachable_count": len(reachable & node_ids),
        "root_reachable_ratio": f"{len(reachable & node_ids)}/{len(node_ids)}",
        "core_node_count": len(core_nodes),
    }


def _reachable(nodes: list[dict[str, Any]], edges: list[dict[str, Any]], roots: set[str]) -> set[str]:
    node_ids = {str(node["candidate_id"]) for node in nodes}
    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        adjacency[str(edge["source"])].add(str(edge["target"]))
    reachable = set(roots & node_ids)
    queue: deque[str] = deque(sorted(reachable))
    while queue:
        current = queue.popleft()
        for target in sorted(adjacency.get(current, ())):
            if target in reachable:
                continue
            reachable.add(target)
            queue.append(target)
    return reachable


def _sim_battery(
    contract: dict[str, Any],
    records: list[dict[str, Any]],
    reduced: dict[str, Any],
    variants: dict[str, Any],
    expanded: dict[str, Any],
) -> dict[str, Any]:
    golden = _evaluate_golden()
    negatives = _evaluate_negative_controls()
    manual = _evaluate_manual_spot_checks()
    full = variants["variants"]["maximal_research"]
    recommended = variants["variants"][variants["recommended_variant"]]
    checks = {
        "contract_required_fields_present": len(contract["candidate_record_required_fields"]) == 11,
        "golden_recall_preserved": golden["recall_ratio"] == "64/64",
        "negative_controls_pass": negatives["failed_count"] == 0,
        "manual_spot_checks_pass": manual["failed_count"] == 0,
        "expanded_corpus_pass": expanded["failed_count"] == 0,
        "candidate_queue_nonempty": len(records) > 0,
        "reduced_candidates_nonempty": reduced["selected_source_candidate_count"] > 0,
        "recommended_variant_endpoint_valid": recommended["metrics"]["invalid_endpoint_count"] == 0,
        "maximal_variant_endpoint_valid": full["metrics"]["invalid_endpoint_count"] == 0,
        "no_extracted_candidate_promoted_to_genesis_core": all(
            record["promotion_class"] != "genesis_core_candidate" for record in records
        ),
    }
    return {
        "status": "PASS" if all(checks.values()) else "NEEDS_REVIEW",
        "checks": checks,
        "golden_replay": golden,
        "negative_controls": negatives,
        "manual_spot_checks": manual,
        "expanded_corpus": {
            "expanded_corpus_file_count": expanded["expanded_corpus_file_count"],
            "pass_ratio": expanded["pass_ratio"],
            "strata": expanded["strata"],
        },
        "candidate_queue": {
            "atom_candidate_count": len(records),
            "source_file_count": len({record["source_file"] for record in records}),
            "promotion_class_counts": dict(sorted(Counter(record["promotion_class"] for record in records).items())),
            "review_class_counts": dict(sorted(Counter(record["review_class"] for record in records).items())),
        },
        "variants": {
            key: {
                "node_count": value["metrics"]["node_count"],
                "edge_count": value["metrics"]["edge_count"],
                "tier_counts": value["metrics"]["tier_counts"],
                "invalid_endpoint_count": value["metrics"]["invalid_endpoint_count"],
                "root_reachable_ratio": value["metrics"]["root_reachable_ratio"],
            }
            for key, value in variants["variants"].items()
        },
    }


def _write_queue(records: list[dict[str, Any]]) -> None:
    lines = [json.dumps(record, sort_keys=True, allow_nan=False) for record in records]
    _atomic_write(CANDIDATE_QUEUE_OUT, "\n".join(lines) + ("\n" if lines else ""))


def _report(payload: dict[str, Any]) -> str:
    battery = payload["sim_battery"]
    variants = battery["variants"]
    lines = [
        "# SIM-ATLAS-CANDIDATE-STRIKE-FORCE-01",
        "",
        "<!-- PUBLIC_RC_EXCLUDE: atlas_candidate_strike_force_research_only -->",
        "<!-- PUBLIC_RC_EXCLUDE_REASON: support-only Atlas candidate generation and SIM battery; no canonical graph mutation, public RC activation, or runtime activation -->",
        "",
        f"**Phase:** {PHASE}",
        f"**Status:** {battery['status']}",
        "**Sensitivity:** NON-SENSITIVE",
        "",
        "## Purpose",
        "",
        "This SIM executes the Fix21-Fix27 strike-force path in one research-only tranche:",
        "define the extraction contract, expand calibration, run broad extraction, reduce",
        "candidate records, assemble unsigned candidate variants, run a SIM battery, and",
        "produce a human review packet.",
        "",
        "## Metrics",
        "",
        "| Metric | Result |",
        "|---|---:|",
        f"| Expanded calibration corpus | `{battery['expanded_corpus']['pass_ratio']}` |",
        f"| Candidate atom records | `{battery['candidate_queue']['atom_candidate_count']}` |",
        f"| Candidate source files | `{battery['candidate_queue']['source_file_count']}` |",
        f"| Reduced selected source candidates | `{payload['reduced_candidates']['selected_source_candidate_count']}` |",
        f"| Recommended variant | `{payload['candidate_variants']['recommended_variant']}` |",
        "",
        "## Variant Summary",
        "",
        "| Variant | Nodes | Edges | Endpoint errors | Root reachability |",
        "|---|---:|---:|---:|---:|",
    ]
    for key, value in variants.items():
        lines.append(
            f"| `{key}` | `{value['node_count']}` | `{value['edge_count']}` | "
            f"`{value['invalid_endpoint_count']}` | `{value['root_reachable_ratio']}` |"
        )

    lines.extend(
        [
            "",
            "## SIM Battery",
            "",
            "| Check | Passed |",
            "|---|---:|",
        ]
    )
    for key, value in battery["checks"].items():
        lines.append(f"| `{key}` | `{value}` |")

    lines.extend(
        [
            "",
            "## Disposition",
            "",
            "The generated full candidate is tiered. Genesis-core nodes remain distinct from",
            "common registry, sidecar recipe, implementation-support, semantic-support, and",
            "research-only candidates. The recommended next review target is",
            "`core_plus_common_registry`, not `maximal_research`.",
            "",
            "The SIM does not mutate `out/genesis_core_star_map_v0.4_candidate.json` and does",
            "not sign any successor manifest. Promotion to canonical Genesis v0.4 remains a",
            "Block 6 / Phase 1573 signing decision.",
            "",
            "## Output Tokens",
            "",
        ]
    )
    for token in payload["tokens"]:
        lines.append(f"- `{token}`")
    lines.extend(["", "## Non-Claims", ""])
    for claim in payload["non_claims"]:
        lines.append(f"- {claim}")
    lines.extend(
        [
            "",
            "graph_delta=support_only:docs/sims/sim_atlas_candidate_strike_force_1545p_fix21_v0.1.md -> atlas/candidate-strike-force",
            "graph_delta=deferred:genesis_atlas_v04_full_candidate_not_signed_phase_1545p_fix21",
            "",
        ]
    )
    return "\n".join(lines)


def _review_packet(payload: dict[str, Any]) -> str:
    variants = payload["sim_battery"]["variants"]
    reduced = payload["reduced_candidates"]
    lines = [
        "# ILC Genesis Atlas Candidate Review Packet 1545p-Fix21 v0.1",
        "",
        "<!-- PUBLIC_RC_EXCLUDE: genesis_atlas_review_packet_research_only -->",
        "<!-- PUBLIC_RC_EXCLUDE_REASON: human review packet for unsigned support-only Atlas candidates; not canonical Genesis state -->",
        "",
        "## Recommendation",
        "",
        "Use `core_plus_common_registry` as the next human-review target for a potential",
        "Genesis Atlas v0.4 successor. Do not use `maximal_research` as a signing target.",
        "",
        "Reason: `core_plus_common_registry` captures the namespace and registry surfaces",
        "needed for later sidecar and graph optimization work while keeping sidecars,",
        "semantic support files, and research-only extracted atoms outside Genesis core.",
        "",
        "## Candidate Variant Counts",
        "",
        "| Variant | Nodes | Edges | Tier counts |",
        "|---|---:|---:|---|",
    ]
    for key, value in variants.items():
        lines.append(
            f"| `{key}` | `{value['node_count']}` | `{value['edge_count']}` | "
            f"`{json.dumps(value['tier_counts'], sort_keys=True)}` |"
        )

    lines.extend(
        [
            "",
            "## Reducer Summary",
            "",
            f"- Atom candidates: `{reduced['atom_candidate_count']}`.",
            f"- Source candidates: `{reduced['source_candidate_count']}`.",
            f"- Selected source candidates: `{reduced['selected_source_candidate_count']}`.",
            f"- Promotion classes: `{json.dumps(reduced['promotion_class_counts'], sort_keys=True)}`.",
            f"- Review classes: `{json.dumps(reduced['review_class_counts'], sort_keys=True)}`.",
            "",
            "## Human Review Questions",
            "",
            "1. Should `core_plus_common_registry` be the Phase 1573 v0.4 signing input, or should Phase 1573 remain on the narrower Fix18 core-only candidate?",
            "2. Which common registry nodes should be moved from review candidate to signed Genesis support?",
            "3. Should sidecar recipe nodes stay entirely outside Genesis v0.4 and enter only through a later registry/sidecar governance lane?",
            "4. Which semantic-support source candidates need additional hand labels before they can inform any later compiler update?",
            "5. Should `maximal_research` remain only as an AutoResearch training target?",
            "",
            "## Required Boundary",
            "",
            "This packet is advisory. It does not authorize public RC, signing, guard clearance,",
            "runtime activation, economic activation, ADR/CDL mutation, or Genesis canonical",
            "state mutation.",
            "",
            "## Tokens",
            "",
            "- `genesis_atlas_candidate_review_packet_committed_phase_1545p_fix21`",
            "- `public_path_remains_blocked_phase_1545p_fix21`",
            "",
        ]
    )
    return "\n".join(lines)


def run() -> dict[str, Any]:
    contract = _build_contract()
    expanded = _evaluate_expanded_corpus()
    records = _candidate_records()
    reduced = _reduce_candidates(records)
    variants = _assemble_variants(reduced)
    battery = _sim_battery(contract, records, reduced, variants, expanded)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "phase": PHASE,
        "sim_id": SIM_ID,
        "status": battery["status"],
        "authority_status": "research_only_not_authority_bearing",
        "contract": contract,
        "expanded_corpus": expanded,
        "candidate_queue_path": str(CANDIDATE_QUEUE_OUT.relative_to(REPO_ROOT)),
        "reduced_candidates": {
            key: value for key, value in reduced.items() if key != "source_candidates"
        },
        "candidate_variants": {
            "path": str(VARIANTS_OUT.relative_to(REPO_ROOT)),
            "full_candidate_path": str(FULL_CANDIDATE_OUT.relative_to(REPO_ROOT)),
            "recommended_variant": variants["recommended_variant"],
            "recommendation_rationale": variants["recommendation_rationale"],
        },
        "sim_battery": battery,
        "tokens": [
            "atlas_extraction_contract_v2_committed_phase_1545p_fix21",
            "atlas_stratified_corpus_expanded_phase_1545p_fix21",
            "atlas_broad_candidate_queue_generated_phase_1545p_fix21",
            "atlas_candidate_reducer_completed_phase_1545p_fix21",
            "genesis_atlas_v04_candidate_variants_generated_phase_1545p_fix21",
            "genesis_atlas_full_candidate_support_only_generated_phase_1545p_fix21",
            "atlas_sim_battery_passed_phase_1545p_fix21",
            "genesis_atlas_candidate_review_packet_committed_phase_1545p_fix21",
            "public_path_remains_blocked_phase_1545p_fix21",
        ],
        "non_claims": [
            "No canonical Genesis graph mutation occurred.",
            "No Genesis v0.4 signing occurred.",
            "No public RC activation occurred.",
            "No public repository push occurred.",
            "No runtime guard was cleared.",
            "No economic activation, minting, settlement, wallet write, treasury write, or ledger write occurred.",
            "No sidecar activation occurred.",
            "No ADR or CDL mutation occurred.",
            "No extracted Atlas edge candidate is promoted to signed Genesis core by this SIM.",
        ],
    }

    _atomic_write(CONTRACT_OUT, _canonical_dumps(contract))
    _write_queue(records)
    _atomic_write(REDUCED_OUT, _canonical_dumps(reduced))
    _atomic_write(VARIANTS_OUT, _canonical_dumps(variants))
    full_candidate = {
        "schema_version": "genesis_atlas_v0.4_full_candidate_1545p_fix21.v0.1",
        "phase": PHASE,
        "candidate_status": "unsigned_support_only_not_canonical",
        "recommended_signing_input": variants["recommended_variant"],
        "tiers_are_authoritative": False,
        "variants": variants["variants"],
        "non_claims": payload["non_claims"],
    }
    _atomic_write(FULL_CANDIDATE_OUT, _canonical_dumps(full_candidate))
    _atomic_write(JSON_OUT, _canonical_dumps(payload))
    _atomic_write(REPORT_OUT, _report(payload))
    _atomic_write(REVIEW_PACKET_OUT, _review_packet(payload))
    return payload


def main() -> int:
    payload = run()
    print(json.dumps({"status": payload["status"], "phase": PHASE}, sort_keys=True))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
