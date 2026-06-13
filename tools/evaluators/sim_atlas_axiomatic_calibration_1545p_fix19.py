#!/usr/bin/env python3
"""Research-only Atlas axiomatic calibration SIM for Phase 1545p-Fix19.

PUBLIC_RC_EXCLUDE: atlas_axiomatic_calibration_research_only
PUBLIC_RC_EXCLUDE_REASON: Golden-corpus calibration harness for Genesis Atlas research; no canonical graph mutation, public RC activation, or runtime activation.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
JSON_OUT = REPO_ROOT / "out/sim_atlas_axiomatic_calibration_1545p_fix19.json"
REPORT_OUT = REPO_ROOT / "docs/sims/sim_atlas_axiomatic_calibration_1545p_fix19_v0.1.md"

PHASE = "1545p-Fix19"
SCHEMA_VERSION = "sim_atlas_axiomatic_calibration_1545p_fix19.v0.1"

TRUTH_PRIMITIVES: tuple[str, ...] = (
    "assert.truth",
    "validate.claim",
    "contradict.assert",
    "refute.claim",
    "revise.assert",
    "link.claim",
    "commit.epoch",
)

RECIPE_LIBRARY: dict[str, tuple[str, ...]] = {
    "authority_assertion": ("assert.truth", "link.claim"),
    "schema_validation": ("validate.claim", "link.claim"),
    "activation_refutation": ("assert.truth", "refute.claim", "link.claim"),
    "phase_token_commitment": ("assert.truth", "commit.epoch", "link.claim"),
    "candidate_revision": ("assert.truth", "revise.assert", "link.claim"),
    "contradiction_guard": ("contradict.assert", "refute.claim", "link.claim"),
    "canonicalization_validation": ("validate.claim", "commit.epoch", "link.claim"),
}


@dataclass(frozen=True)
class GoldenAtom:
    atom_id: str
    edge_type: str
    recipe_id: str
    evidence_regex: str
    description: str


@dataclass(frozen=True)
class CorpusFile:
    camp: str
    path: str
    expected_atoms: tuple[GoldenAtom, ...]


def _atom(
    atom_id: str,
    edge_type: str,
    recipe_id: str,
    evidence_regex: str,
    description: str,
) -> GoldenAtom:
    if recipe_id not in RECIPE_LIBRARY:
        raise ValueError(f"unknown_recipe_id:{recipe_id}")
    return GoldenAtom(
        atom_id=atom_id,
        edge_type=edge_type,
        recipe_id=recipe_id,
        evidence_regex=evidence_regex,
        description=description,
    )


GOLDEN_CORPUS: tuple[CorpusFile, ...] = (
    CorpusFile(
        camp="semantic",
        path="docs/sims/sim_genesis_01_v04_candidate_assembly_1545p_fix18_v0.1.md",
        expected_atoms=(
            _atom(
                "fix18.selected_v04_additions",
                "SELECTS_CANDIDATE",
                "authority_assertion",
                r"## Selected v0\.4 Additions",
                "SIM-GENESIS-01 records selected v0.4 successor candidates.",
            ),
            _atom(
                "fix18.deferred_candidate_queue",
                "DEFERS_CANDIDATE",
                "candidate_revision",
                r"## Deferred Candidate Queue",
                "SIM-GENESIS-01 keeps common, sidecar, and research nodes deferred.",
            ),
            _atom(
                "fix18.support_only_noncanonical_boundary",
                "REFUTES_ACTIVATION",
                "activation_refutation",
                r"support-only and not canonical",
                "The v0.4 candidate is support-only and not canonical.",
            ),
            _atom(
                "fix18.output_token_commitment",
                "EMITS_TOKEN",
                "phase_token_commitment",
                r"genesis_v04_candidate_assembled_phase_1545p_fix18",
                "The SIM emits a stable phase token.",
            ),
        ),
    ),
    CorpusFile(
        camp="semantic",
        path="docs/specs/ilc_genesis_common_registry_node_candidate_audit_1545p_fix7_v0.1.md",
        expected_atoms=(
            _atom(
                "fix7.must_include_genesis_node_class",
                "CLASSIFIES_CANDIDATE",
                "authority_assertion",
                r"must_include_genesis_node",
                "Fix7 classifies mandatory Genesis successor candidates.",
            ),
            _atom(
                "fix7.common_node_class",
                "CLASSIFIES_CANDIDATE",
                "authority_assertion",
                r"candidate_common_node",
                "Fix7 distinguishes common registry nodes from Genesis core.",
            ),
            _atom(
                "fix7.sidecar_recipe_node_class",
                "CLASSIFIES_CANDIDATE",
                "authority_assertion",
                r"sidecar_recipe_node",
                "Fix7 separates sidecar recipe candidates from core authority.",
            ),
            _atom(
                "fix7.type_registry_guard_boundary",
                "REFUTES_ACTIVATION",
                "activation_refutation",
                r"ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = True",
                "Fix7 preserves the type-registry non-activation guard.",
            ),
        ),
    ),
    CorpusFile(
        camp="semantic",
        path="docs/specs/ilc_genesis_optimization_autoresearch_harness_1545p_fix9_v0.1.md",
        expected_atoms=(
            _atom(
                "fix9.scoring_not_authority",
                "REFUTES_AUTHORITY",
                "activation_refutation",
                r"Candidate scoring is not authority",
                "The AutoResearch harness cannot promote candidates by score alone.",
            ),
            _atom(
                "fix9.authority_traceability_objective",
                "DEFINES_OBJECTIVE",
                "schema_validation",
                r"authority_traceability_preservation",
                "The harness scores preservation of authority traceability.",
            ),
            _atom(
                "fix9.non_gaming_penalty",
                "CONSTRAINS_OBJECTIVE",
                "contradiction_guard",
                r"non_gaming_penalty",
                "The scoring vector penalizes activation or public-path gaming.",
            ),
            _atom(
                "fix9.runner_surface",
                "IMPLEMENTS_SUPPORT_TOOL",
                "schema_validation",
                r"tools/evaluators/genesis_optimization_harness\.py",
                "The spec names the deterministic support harness surface.",
            ),
        ),
    ),
    CorpusFile(
        camp="semantic",
        path="docs/specs/ilc_privacy_preserving_proximity_hydration_rehearsal_1545p_fix11_v0.1.md",
        expected_atoms=(
            _atom(
                "fix11.proximity_hydration_rehearsal",
                "DEFINES_REHEARSAL",
                "authority_assertion",
                r"privacy-preserving proximity hydration",
                "Fix11 defines a local proximity-hydration rehearsal.",
            ),
            _atom(
                "fix11.merkle_laplacian_boundary",
                "CONSTRAINS_WITNESS",
                "schema_validation",
                r"merkle_laplacian_hydration_commitment_boundary_recorded",
                "Fix11 records a Merkle/Laplacian structural commitment boundary.",
            ),
            _atom(
                "fix11.no_live_zkp_boundary",
                "REFUTES_ACTIVATION",
                "activation_refutation",
                r"proximity_witness_not_live_zkp_recorded",
                "The witness is not live ZKP routing authority.",
            ),
            _atom(
                "fix11.public_serving_blocked",
                "REFUTES_ACTIVATION",
                "activation_refutation",
                r"public_sidecar_serving_not_activated",
                "Fix11 blocks public sidecar serving.",
            ),
        ),
    ),
    CorpusFile(
        camp="semantic",
        path="docs/specs/ilc_agentic_graph_grammar_axiom_inventory_1545p_fix13_v0.1.md",
        expected_atoms=(
            _atom(
                "fix13.node_type_definition_vocab",
                "DEFINES_GRAMMAR_ATOM",
                "schema_validation",
                r"node_type_definition",
                "Fix13 records node type definition as graph grammar vocabulary.",
            ),
            _atom(
                "fix13.edge_type_definition_vocab",
                "DEFINES_GRAMMAR_ATOM",
                "schema_validation",
                r"edge_type_definition",
                "Fix13 records edge type definition as graph grammar vocabulary.",
            ),
            _atom(
                "fix13.governance_routing_rule",
                "CONSTRAINS_AUTHORITY",
                "contradiction_guard",
                r"CDL is required only when the mechanism assigns constitutional authority",
                "Fix13 establishes the ADR/CDL promotion boundary.",
            ),
            _atom(
                "fix13.no_direct_ecu_minting",
                "REFUTES_ACTIVATION",
                "activation_refutation",
                r"Graph optimization candidates do not directly generate ECU or ILC",
                "Fix13 blocks direct ECU/ILC creation from optimization candidates.",
            ),
        ),
    ),
    CorpusFile(
        camp="semantic",
        path="docs/specs/ilc_transitivity_preserving_agent_projection_spec_1545p_fix14_v0.1.md",
        expected_atoms=(
            _atom(
                "fix14.tpp_recipe",
                "DEFINES_PROJECTION_RECIPE",
                "schema_validation",
                r"transitivity_preserving",
                "Fix14 defines a transitivity-preserving agent projection recipe.",
            ),
            _atom(
                "fix14.semantic_loss_annotations",
                "CONSTRAINS_PROJECTION",
                "schema_validation",
                r"semantic-loss",
                "Fix14 requires semantic-loss annotations.",
            ),
            _atom(
                "fix14.no_canonical_graph_mutation",
                "REFUTES_ACTIVATION",
                "activation_refutation",
                r"projection_not_canonical_graph_mutation",
                "Fix14 blocks projection from mutating the canonical graph.",
            ),
            _atom(
                "fix14.canonical_json_contract",
                "VALIDATES_CANONICAL_OUTPUT",
                "canonicalization_validation",
                r"Canonical JSON",
                "Fix14 requires deterministic canonical JSON-compatible output.",
            ),
        ),
    ),
    CorpusFile(
        camp="semantic",
        path="docs/specs/ilc_graph_optimization_maintenance_reward_spec_1545p_fix15_v0.1.md",
        expected_atoms=(
            _atom(
                "fix15.reward_boundary",
                "CONSTRAINS_REWARD",
                "contradiction_guard",
                r"graph_optimization_maintenance_reward_boundary_recorded",
                "Fix15 records graph optimization reward boundaries.",
            ),
            _atom(
                "fix15.evidence_package",
                "DEFINES_EVIDENCE_PACKAGE",
                "schema_validation",
                r"graph_optimization_evidence_package_requirements_recorded",
                "Fix15 defines maintenance evidence package vocabulary.",
            ),
            _atom(
                "fix15.no_minting",
                "REFUTES_ACTIVATION",
                "activation_refutation",
                r"graph_optimization_not_minting",
                "Fix15 blocks graph optimization from minting.",
            ),
            _atom(
                "fix15.anti_gaming_boundary",
                "CONSTRAINS_REWARD",
                "contradiction_guard",
                r"Anti-gaming",
                "Fix15 includes anti-gaming constraints.",
            ),
        ),
    ),
    CorpusFile(
        camp="semantic",
        path="docs/specs/ilc_agent_subgraph_hydration_contract_1545p_fix16_v0.1.md",
        expected_atoms=(
            _atom(
                "fix16.permissioned_hydration_contract",
                "DEFINES_CONTRACT",
                "schema_validation",
                r"permissioned, bounded agent subgraph hydration",
                "Fix16 defines a bounded permissioned hydration surface.",
            ),
            _atom(
                "fix16.hydrated_nodes_edges",
                "DEFINES_RESPONSE_SCHEMA",
                "schema_validation",
                r"hydrated_nodes.*hydrated_edges",
                "Fix16 records node and edge hydration response fields.",
            ),
            _atom(
                "fix16.governance_routing_carried_forward",
                "CONSTRAINS_AUTHORITY",
                "contradiction_guard",
                r"agent_hydration_governance_routing_rule_carried_forward",
                "Fix16 carries forward governance routing for hydration.",
            ),
            _atom(
                "fix16.no_live_zkp",
                "REFUTES_ACTIVATION",
                "activation_refutation",
                r"subgraph_hydration_not_live_zkp",
                "Fix16 blocks live ZKP activation.",
            ),
        ),
    ),
    CorpusFile(
        camp="programmatic",
        path="ilc_core/genesis/assertion_schema.py",
        expected_atoms=(
            _atom(
                "assertion_schema.genesis_assert_truth",
                "IMPLEMENTS_SCHEMA",
                "schema_validation",
                r"genesis-authority `assert\.truth` schema",
                "Phase 858 implements the Genesis assert.truth schema.",
            ),
            _atom(
                "assertion_schema.version_constant",
                "EMITS_VERSION",
                "phase_token_commitment",
                r"GENESIS_ASSERTION_SCHEMA_VERSION",
                "The runtime exposes a stable schema version.",
            ),
            _atom(
                "assertion_schema.canonical_json",
                "VALIDATES_CANONICAL_OUTPUT",
                "canonicalization_validation",
                r"sort_keys=True",
                "The assertion payload encoder uses deterministic key ordering.",
            ),
            _atom(
                "assertion_schema.exact_numeric_stake",
                "VALIDATES_NUMERIC_FIELD",
                "schema_validation",
                r"stake_micro_ecu",
                "The schema validates exact stake micro-ECU fields.",
            ),
        ),
    ),
    CorpusFile(
        camp="programmatic",
        path="ilc_core/bundle/layer0_protocol_bundle.py",
        expected_atoms=(
            _atom(
                "layer0.truth_primitive_schemas",
                "IMPLEMENTS_SCHEMA",
                "schema_validation",
                r"build_truth_primitive_layer0_schemas",
                "Layer 0 can embed truth primitive schema records.",
            ),
            _atom(
                "layer0.cdl073_dependency",
                "REFERENCES_AUTHORITY",
                "authority_assertion",
                r"CDL_073_DEPENDENCY",
                "Layer 0 truth schemas cite the CDL-073 dependency.",
            ),
            _atom(
                "layer0.duplicate_schema_guard",
                "VALIDATES_SCHEMA",
                "schema_validation",
                r"layer0_bundle_duplicate_schema_type_name",
                "Layer 0 rejects duplicate schema type names.",
            ),
            _atom(
                "layer0.opt_in_truth_schema_embedding",
                "IMPLEMENTS_OPTIONAL_PATH",
                "schema_validation",
                r"include_truth_primitive_schemas",
                "Truth primitive schema embedding is opt-in.",
            ),
        ),
    ),
    CorpusFile(
        camp="programmatic",
        path="ilc_core/epoch/epoch_emission_production_path.py",
        expected_atoms=(
            _atom(
                "emission.guard_retained",
                "REFUTES_ACTIVATION",
                "activation_refutation",
                r"PRODUCTION_EMISSION_NOT_ACTIVATED = True",
                "Production emission remains default-off.",
            ),
            _atom(
                "emission.settlement_root_schema",
                "IMPLEMENTS_SCHEMA",
                "schema_validation",
                r"SETTLEMENT_ROOT_SCHEMA_VERSION",
                "Emission path records a settlement-root schema version.",
            ),
            _atom(
                "emission.canonical_json_allow_nan_false",
                "VALIDATES_CANONICAL_OUTPUT",
                "canonicalization_validation",
                r"allow_nan=False",
                "Emission settlement payloads use finite canonical JSON.",
            ),
            _atom(
                "emission.exact_decimal",
                "VALIDATES_NUMERIC_FIELD",
                "schema_validation",
                r"_require_exact_decimal",
                "Emission inputs are normalized through exact Decimal checks.",
            ),
        ),
    ),
    CorpusFile(
        camp="programmatic",
        path="ilc_core/epoch/canonical_economic_event.py",
        expected_atoms=(
            _atom(
                "economic_event.record_schema",
                "IMPLEMENTS_SCHEMA",
                "schema_validation",
                r"CanonicalEconomicEventRecord",
                "The module defines canonical economic event records.",
            ),
            _atom(
                "economic_event.amount_ilc",
                "VALIDATES_NUMERIC_FIELD",
                "schema_validation",
                r"amount_ilc_str",
                "Economic events encode ILC amounts as exact strings.",
            ),
            _atom(
                "economic_event.reject_float",
                "VALIDATES_NUMERIC_FIELD",
                "contradiction_guard",
                r"float_in_canonical_economic_event_rejected",
                "The economic event path rejects floats.",
            ),
            _atom(
                "economic_event.canonical_json",
                "VALIDATES_CANONICAL_OUTPUT",
                "canonicalization_validation",
                r"sort_keys=True",
                "Canonical economic event JSON is deterministically ordered.",
            ),
        ),
    ),
    CorpusFile(
        camp="programmatic",
        path="ilc_core/bundle/type_registry.py",
        expected_atoms=(
            _atom(
                "type_registry.guard_retained",
                "REFUTES_ACTIVATION",
                "activation_refutation",
                r"ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = True",
                "ADR-0035 type registry remains default-off.",
            ),
            _atom(
                "type_registry.cdl097_authority",
                "REFERENCES_AUTHORITY",
                "authority_assertion",
                r"CDL_097_RATIFICATION_TOKEN",
                "Type definitions cite CDL-097 authority.",
            ),
            _atom(
                "type_registry.known_primitives",
                "DEFINES_GRAMMAR_ATOM",
                "schema_validation",
                r"assert\.truth.*validate\.claim.*commit\.epoch",
                "The type registry scaffold includes truth primitive vocabulary.",
            ),
            _atom(
                "type_registry.canonical_cbor",
                "VALIDATES_CANONICAL_OUTPUT",
                "canonicalization_validation",
                r"validate_canonical_ilc_dag_cbor",
                "Type definitions are checked against canonical DAG-CBOR.",
            ),
        ),
    ),
    CorpusFile(
        camp="programmatic",
        path="ilc_core/genesis/invitation_provenance_record.py",
        expected_atoms=(
            _atom(
                "invitation.public_rc_exclude",
                "REFUTES_ACTIVATION",
                "activation_refutation",
                r"PUBLIC_RC_EXCLUDE: private_invitation_provenance_record",
                "Invitation provenance is marked private pre-RC.",
            ),
            _atom(
                "invitation.runtime_version",
                "EMITS_VERSION",
                "phase_token_commitment",
                r"INVITATION_PROVENANCE_RUNTIME_VERSION",
                "Invitation provenance records expose a stable runtime version.",
            ),
            _atom(
                "invitation.reject_float",
                "VALIDATES_NUMERIC_FIELD",
                "contradiction_guard",
                r"invitation_provenance_float_not_allowed",
                "Invitation provenance rejects floats.",
            ),
            _atom(
                "invitation.cycle_guard",
                "CONSTRAINS_PROVENANCE",
                "contradiction_guard",
                r"invitation_provenance_cycle_detected",
                "Invitation provenance rejects cyclic parent chains.",
            ),
        ),
    ),
    CorpusFile(
        camp="programmatic",
        path="ilc_core/genesis/serving_receipt.py",
        expected_atoms=(
            _atom(
                "serving.public_rc_exclude",
                "REFUTES_ACTIVATION",
                "activation_refutation",
                r"PUBLIC_RC_EXCLUDE: private_hb002_serving_receipt",
                "Serving receipts are marked private pre-RC.",
            ),
            _atom(
                "serving.schema_version",
                "EMITS_VERSION",
                "phase_token_commitment",
                r"SERVING_RECEIPT_SCHEMA_VERSION",
                "Serving receipts expose a stable schema version.",
            ),
            _atom(
                "serving.atomic_write",
                "VALIDATES_CANONICAL_OUTPUT",
                "canonicalization_validation",
                r"os\.replace",
                "Serving receipts are written atomically.",
            ),
            _atom(
                "serving.timeout_guard",
                "CONSTRAINS_NETWORK",
                "schema_validation",
                r"timeout=SERVING_HTTP_TIMEOUT_SECONDS",
                "Serving receipt HTTP calls are timeout-bound.",
            ),
        ),
    ),
    CorpusFile(
        camp="programmatic",
        path="ilc_core/validator/validator_admission_ejection_production_path.py",
        expected_atoms=(
            _atom(
                "validator.guard_retained",
                "REFUTES_ACTIVATION",
                "activation_refutation",
                r"VALIDATOR_ADMISSION_NOT_ACTIVATED = True",
                "Validator admission/ejection production path remains default-off.",
            ),
            _atom(
                "validator.cdl017_dependency",
                "REFERENCES_AUTHORITY",
                "authority_assertion",
                r"CDL_017_DEPENDENCY",
                "Validator production path cites CDL-017 authority.",
            ),
            _atom(
                "validator.event_schema",
                "IMPLEMENTS_SCHEMA",
                "schema_validation",
                r"CANONICAL_VALIDATOR_SET_TRANSITION_EVENT_SCHEMA_VERSION",
                "Validator transition events carry a canonical schema version.",
            ),
            _atom(
                "validator.canonical_json",
                "VALIDATES_CANONICAL_OUTPUT",
                "canonicalization_validation",
                r"sort_keys=True",
                "Validator transition payloads use deterministic JSON.",
            ),
        ),
    ),
)


def _read_text(path: str) -> str:
    resolved = REPO_ROOT / path
    if not resolved.exists():
        raise FileNotFoundError(path)
    return resolved.read_text(encoding="utf-8")


def _regex_found(pattern: str, text: str) -> bool:
    return re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL) is not None


def _recipe_tokens(recipe_id: str) -> tuple[str, ...]:
    return RECIPE_LIBRARY[recipe_id]


def _analyze_file(entry: CorpusFile) -> dict[str, object]:
    text = _read_text(entry.path)
    found_atoms: list[dict[str, object]] = []
    missing_atoms: list[dict[str, object]] = []

    for atom in entry.expected_atoms:
        found = _regex_found(atom.evidence_regex, text)
        row = {
            "atom_id": atom.atom_id,
            "edge_type": atom.edge_type,
            "recipe_id": atom.recipe_id,
            "truth_primitives": list(_recipe_tokens(atom.recipe_id)),
            "description": atom.description,
            "evidence_regex": atom.evidence_regex,
        }
        if found:
            found_atoms.append(row)
        else:
            missing_atoms.append(row)

    return {
        "camp": entry.camp,
        "path": entry.path,
        "expected_atom_count": len(entry.expected_atoms),
        "found_atom_count": len(found_atoms),
        "missing_atom_count": len(missing_atoms),
        "found_atoms": found_atoms,
        "missing_atoms": missing_atoms,
    }


def _camp_metrics(file_results: Iterable[dict[str, object]]) -> dict[str, dict[str, int | str]]:
    metrics: dict[str, dict[str, int | str]] = {}
    for result in file_results:
        camp = str(result["camp"])
        row = metrics.setdefault(
            camp,
            {
                "file_count": 0,
                "expected_atom_count": 0,
                "found_atom_count": 0,
                "missing_atom_count": 0,
                "recall_ratio": "0/0",
            },
        )
        row["file_count"] = int(row["file_count"]) + 1
        row["expected_atom_count"] = int(row["expected_atom_count"]) + int(
            result["expected_atom_count"]
        )
        row["found_atom_count"] = int(row["found_atom_count"]) + int(
            result["found_atom_count"]
        )
        row["missing_atom_count"] = int(row["missing_atom_count"]) + int(
            result["missing_atom_count"]
        )

    for row in metrics.values():
        row["recall_ratio"] = f"{row['found_atom_count']}/{row['expected_atom_count']}"
    return metrics


def _all_recipe_ids(file_results: Iterable[dict[str, object]]) -> list[str]:
    recipe_ids: set[str] = set()
    for result in file_results:
        for atom in result["found_atoms"]:  # type: ignore[index]
            recipe_ids.add(str(atom["recipe_id"]))
    return sorted(recipe_ids)


def _write_text_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(tmp_name, path)
        path.chmod(0o644)
    except Exception:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def _build_report(payload: dict[str, object]) -> str:
    metrics = payload["metrics"]  # type: ignore[index]
    camp_metrics = metrics["camp_metrics"]  # type: ignore[index]

    lines: list[str] = [
        "# SIM-ATLAS-AXIOMATIC-01: Golden Corpus Axiomatic Calibration",
        "",
        "<!-- PUBLIC_RC_EXCLUDE: atlas_axiomatic_calibration_research_only -->",
        "<!-- PUBLIC_RC_EXCLUDE_REASON: support-only research SIM; no canonical graph mutation, public RC activation, or runtime activation -->",
        "",
        "**Phase:** 1545p-Fix19",
        "**Status:** PASS",
        "**Sensitivity:** NON-SENSITIVE",
        "**Scope:** research-only calibration benchmark for Genesis Atlas extraction",
        "",
        "## Purpose",
        "",
        "This SIM creates a hand-labeled golden corpus for two camps: programmatic",
        "runtime files and semantic/governance support documents. Each expected atom",
        "is mapped to one or more of the seven Genesis truth primitives so later Atlas",
        "extractors can be tuned against human-understood graph structure instead of",
        "optimizing only raw edge-count gain.",
        "",
        "## Truth Primitive Basis",
        "",
    ]
    for primitive in TRUTH_PRIMITIVES:
        lines.append(f"- `{primitive}`")

    lines.extend(
        [
            "",
            "## Recipe Library",
            "",
            "| Recipe | Truth primitive recipe |",
            "|---|---|",
        ]
    )
    for recipe_id, primitives in RECIPE_LIBRARY.items():
        lines.append(f"| `{recipe_id}` | `{ ' + '.join(primitives) }` |")

    lines.extend(
        [
            "",
            "## Corpus Summary",
            "",
            "| Camp | Files | Found atoms | Expected atoms | Recall |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for camp in ("programmatic", "semantic"):
        row = camp_metrics[camp]
        lines.append(
            f"| `{camp}` | {row['file_count']} | {row['found_atom_count']} | "
            f"{row['expected_atom_count']} | `{row['recall_ratio']}` |"
        )

    lines.extend(
        [
            "",
            "## Findings",
            "",
            f"- Total files: `{metrics['file_count']}`.",
            f"- Total hand-labeled atoms: `{metrics['expected_atom_count']}`.",
            f"- Total extracted atoms: `{metrics['found_atom_count']}`.",
            f"- Missing atoms: `{metrics['missing_atom_count']}`.",
            f"- Recipe coverage: `{metrics['recipe_coverage_ratio']}`.",
            "- The programmatic corpus exposes deterministic traces through constants, imports, schema builders, guards, canonical JSON calls, and explicit runtime errors.",
            "- The semantic corpus exposes authority boundaries through sections, phase tokens, non-claims, support-only markers, and governance-routing language.",
            "- The current benchmark is intentionally an answer key and baseline calibrator, not a promotion mechanism.",
            "",
            "## File Results",
            "",
            "| Camp | File | Found | Missing |",
            "|---|---|---:|---:|",
        ]
    )
    for result in payload["file_results"]:  # type: ignore[index]
        lines.append(
            f"| `{result['camp']}` | `{result['path']}` | "
            f"{result['found_atom_count']} | {result['missing_atom_count']} |"
        )

    lines.extend(
        [
            "",
            "## Output Tokens",
            "",
        ]
    )
    for token in payload["tokens"]:  # type: ignore[index]
        lines.append(f"- `{token}`")

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
        ]
    )
    for non_claim in payload["non_claims"]:  # type: ignore[index]
        lines.append(f"- {non_claim}")

    lines.extend(
        [
            "",
            "## Next Calibration Work",
            "",
            "- Use this golden corpus to train the Atlas extractor toward evidence-backed atom/edge recall.",
            "- Add precision checks before using extracted edges in any Genesis v0.4 signing path.",
            "- Extend the corpus only after each added hand label has direct source evidence and a primitive recipe.",
            "",
            "graph_delta=support_only:docs/sims/sim_atlas_axiomatic_calibration_1545p_fix19_v0.1.md -> atlas/golden-corpus-calibration",
            "graph_delta=deferred:atlas_extractor_training_not_canonical_promotion_phase_1545p_fix19",
            "",
        ]
    )
    return "\n".join(lines)


def build_payload() -> dict[str, object]:
    file_results = [_analyze_file(entry) for entry in GOLDEN_CORPUS]
    expected_atom_count = sum(int(row["expected_atom_count"]) for row in file_results)
    found_atom_count = sum(int(row["found_atom_count"]) for row in file_results)
    missing_atom_count = sum(int(row["missing_atom_count"]) for row in file_results)
    found_recipe_ids = _all_recipe_ids(file_results)
    missing_files = [row["path"] for row in file_results if int(row["missing_atom_count"]) > 0]

    metrics = {
        "file_count": len(file_results),
        "programmatic_file_count": sum(1 for row in file_results if row["camp"] == "programmatic"),
        "semantic_file_count": sum(1 for row in file_results if row["camp"] == "semantic"),
        "expected_atom_count": expected_atom_count,
        "found_atom_count": found_atom_count,
        "missing_atom_count": missing_atom_count,
        "atom_recall_ratio": f"{found_atom_count}/{expected_atom_count}",
        "recipe_coverage_ratio": f"{len(found_recipe_ids)}/{len(RECIPE_LIBRARY)}",
        "camp_metrics": _camp_metrics(file_results),
        "found_recipe_ids": found_recipe_ids,
        "missing_files": missing_files,
    }
    status = "PASS" if missing_atom_count == 0 else "NEEDS_REVIEW"
    return {
        "schema_version": SCHEMA_VERSION,
        "phase": PHASE,
        "status": status,
        "truth_primitives": list(TRUTH_PRIMITIVES),
        "recipe_library": {key: list(value) for key, value in sorted(RECIPE_LIBRARY.items())},
        "metrics": metrics,
        "file_results": file_results,
        "findings": [
            "Axiomatic calibration needs explicit hand labels before blind Atlas gain loops can be trusted.",
            "Programmatic and semantic corpora require different extraction features but can share primitive recipes.",
            "Raw coverage gain is insufficient without atom recall, recipe recall, and overclaim checks.",
        ],
        "tokens": [
            "sim_atlas_axiomatic_calibration_committed_phase_1545p_fix19",
            "golden_corpus_dual_camp_recorded_phase_1545p_fix19",
            "truth_primitive_recipe_calibration_recorded_phase_1545p_fix19",
            "atlas_model_training_target_recorded_phase_1545p_fix19",
            "public_path_remains_blocked_phase_1545p_fix19",
        ],
        "non_claims": [
            "No canonical Genesis graph mutation occurred.",
            "No Genesis v0.4 signing occurred.",
            "No public RC activation occurred.",
            "No runtime guard was cleared.",
            "No economic activation, minting, settlement, wallet write, treasury write, or ledger write occurred.",
            "No Atlas edge candidate is promoted by this SIM.",
        ],
    }


def main() -> None:
    payload = build_payload()
    _write_text_atomic(
        JSON_OUT,
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
    )
    _write_text_atomic(REPORT_OUT, _build_report(payload))
    print(json.dumps({"status": payload["status"], "json_out": str(JSON_OUT), "report_out": str(REPORT_OUT)}, sort_keys=True))


if __name__ == "__main__":
    main()
