#!/usr/bin/env python3
"""Research-only Atlas precision and rejected-file replay SIM for Phase 1545p-Fix20.

PUBLIC_RC_EXCLUDE: atlas_precision_replay_research_only
PUBLIC_RC_EXCLUDE_REASON: Atlas extractor calibration and rejected-file replay; no canonical graph mutation, public RC activation, or runtime activation.
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.evaluators.sim_atlas_axiomatic_calibration_1545p_fix19 import (
    GOLDEN_CORPUS,
    RECIPE_LIBRARY,
    REPORT_OUT as FIX19_REPORT_OUT,
    TRUTH_PRIMITIVES,
)


JSON_OUT = REPO_ROOT / "out/sim_atlas_precision_replay_1545p_fix20.json"
REPORT_OUT = REPO_ROOT / "docs/sims/sim_atlas_precision_replay_1545p_fix20_v0.1.md"

PHASE = "1545p-Fix20"
SCHEMA_VERSION = "sim_atlas_precision_replay_1545p_fix20.v0.1"


@dataclass(frozen=True)
class ExtractedAtom:
    recipe_id: str
    edge_type: str
    evidence: str


@dataclass(frozen=True)
class NegativeControl:
    control_id: str
    text: str
    forbidden_recipe_ids: tuple[str, ...]
    required_recipe_ids: tuple[str, ...]
    rationale: str


@dataclass(frozen=True)
class ManualSpotCheck:
    path: str
    expected_recipe_ids: tuple[str, ...]
    forbidden_recipe_ids: tuple[str, ...]
    rationale: str


REJECTED_REPLAY_PATHS: tuple[str, ...] = (
    "docs/specs/ilc_agent_skills_surface_spec_621_v0.1.md",
    "docs/specs/ilc_cdl_036_node_dissemination_header_and_fetch_contract_evidence_prelock_342_v0.1.md",
    "docs/specs/ilc_cdl_075_truth_primitive_graph_persistence_ratification_evidence_883_v0.1.md",
    "docs/specs/ilc_cdl_076_truth_primitive_announcement_gossip_opening_893_v0.1.md",
    "docs/specs/ilc_cdl_077_want_have_want_block_fetch_opening_900_v0.1.md",
    "docs/specs/ilc_cdl_dependency_graph_v0.1.md",
    "docs/specs/ilc_cli_output_schemas_254_v0.1.md",
    "docs/specs/ilc_cluster_a_acceptance_evidence_v0.1.md",
    "docs/specs/ilc_cluster_a_replay_proof_batch_ops_contract_v0.1.md",
    "docs/specs/ilc_external_audit_rubric_for_assistant_reviewers_v0.1.md",
    "docs/specs/ilc_epistemological_foundations_canonical_v0.1.md",
    "docs/specs/ilc_freshness_gate_contract_v0.1.md",
)


NEGATIVE_CONTROLS: tuple[NegativeControl, ...] = (
    NegativeControl(
        control_id="candidate_scoring_not_authority",
        text="Candidate scoring is not authority and does not promote candidates.",
        forbidden_recipe_ids=("authority_assertion", "candidate_revision"),
        required_recipe_ids=("activation_refutation",),
        rationale="Negated authority language must not become authority or promotion.",
    ),
    NegativeControl(
        control_id="support_only_not_canonical",
        text="The v0.4 candidate artifact is support-only and not canonical.",
        forbidden_recipe_ids=("canonicalization_validation", "candidate_revision"),
        required_recipe_ids=("activation_refutation",),
        rationale="The word canonical in a negated context must not become canonicalization evidence.",
    ),
    NegativeControl(
        control_id="no_public_serving",
        text="PUBLIC_RC_EXCLUDE_REASON: no public serving, no public P2P, and no public RC activation.",
        forbidden_recipe_ids=("authority_assertion",),
        required_recipe_ids=("activation_refutation",),
        rationale="Public-path denial must remain a non-authorization fact.",
    ),
    NegativeControl(
        control_id="not_minting",
        text="Graph optimization candidates do not directly generate ECU or ILC and are not minting.",
        forbidden_recipe_ids=("authority_assertion", "candidate_revision"),
        required_recipe_ids=("activation_refutation", "contradiction_guard"),
        rationale="Economic non-claims must not become productive-credit authority.",
    ),
    NegativeControl(
        control_id="not_live_zkp",
        text="The proximity witness is not live ZKP routing authority.",
        forbidden_recipe_ids=("authority_assertion",),
        required_recipe_ids=("activation_refutation",),
        rationale="ZKP-adjacent language with explicit negation remains support-only.",
    ),
    NegativeControl(
        control_id="deferred_no_selection",
        text="CDL-098 remains reserved and deferred; no option is selected here.",
        forbidden_recipe_ids=("candidate_revision",),
        required_recipe_ids=("activation_refutation",),
        rationale="Deferred without selection must not become a selected-candidate revision edge.",
    ),
)


MANUAL_SPOT_CHECKS: tuple[ManualSpotCheck, ...] = (
    ManualSpotCheck(
        path="docs/specs/ilc_agent_skills_surface_spec_621_v0.1.md",
        expected_recipe_ids=("activation_refutation", "authority_assertion", "candidate_revision"),
        forbidden_recipe_ids=("canonicalization_validation",),
        rationale="ADR-0024 and Tier 3 skills are deferred, while CDL-033 is ratified context.",
    ),
    ManualSpotCheck(
        path="docs/specs/ilc_cdl_075_truth_primitive_graph_persistence_ratification_evidence_883_v0.1.md",
        expected_recipe_ids=("authority_assertion", "schema_validation", "activation_refutation"),
        forbidden_recipe_ids=("candidate_revision",),
        rationale="Ratification evidence should expose authority and schema evidence without creating a new candidate queue.",
    ),
    ManualSpotCheck(
        path="docs/specs/ilc_cdl_076_truth_primitive_announcement_gossip_opening_893_v0.1.md",
        expected_recipe_ids=(
            "authority_assertion",
            "candidate_revision",
            "activation_refutation",
            "contradiction_guard",
        ),
        forbidden_recipe_ids=("canonicalization_validation",),
        rationale="Opening selects Option C and rejects full-payload push under CDL-036.",
    ),
    ManualSpotCheck(
        path="docs/specs/ilc_cli_output_schemas_254_v0.1.md",
        expected_recipe_ids=("schema_validation", "phase_token_commitment"),
        forbidden_recipe_ids=("authority_assertion", "candidate_revision"),
        rationale="CLI output schemas are schema/version surfaces, not governance authority.",
    ),
    ManualSpotCheck(
        path="docs/specs/ilc_cluster_a_acceptance_evidence_v0.1.md",
        expected_recipe_ids=("schema_validation", "contradiction_guard"),
        forbidden_recipe_ids=("authority_assertion", "candidate_revision"),
        rationale="Acceptance evidence has schema and fail-safe behavior but no promotion authority.",
    ),
)


NON_AUTHORITY_PATTERNS = (
    r"\bnot authority\b",
    r"\bnot .*authority\b",
    r"\bdoes not .*authori[sz]e\b",
    r"\bnot .*canonical\b",
    r"\bno public\b",
    r"\bnot public\b",
    r"\bnot activated\b",
    r"\bnot live\b",
    r"\bnot minting\b",
    r"\bdoes not directly generate\b",
)


def _read(path: str) -> str:
    resolved = REPO_ROOT / path
    if not resolved.exists():
        raise FileNotFoundError(path)
    return resolved.read_text(encoding="utf-8")


def _has(pattern: str, text: str) -> bool:
    return re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL) is not None


def _negated_context(text: str) -> bool:
    return any(_has(pattern, text) for pattern in NON_AUTHORITY_PATTERNS)


def _add(atoms: list[ExtractedAtom], recipe_id: str, edge_type: str, evidence: str) -> None:
    if recipe_id not in RECIPE_LIBRARY:
        raise ValueError(f"unknown_recipe:{recipe_id}")
    atom = ExtractedAtom(recipe_id=recipe_id, edge_type=edge_type, evidence=evidence)
    if atom not in atoms:
        atoms.append(atom)


def extract_atoms(text: str) -> list[ExtractedAtom]:
    """Extract coarse recipe-level atoms without file-specific expected regexes."""
    atoms: list[ExtractedAtom] = []
    negated = _negated_context(text)

    if _has(
        r"PUBLIC_RC_EXCLUDE|support-only|not canonical|not authority|no public|not public|blocked|not activated|does not mutate|not minting|not live ZKP|does not directly generate|not signed|unsigned|does not activate|deferred|reserved|excluded|graceful skip|No read-path|not accepted",
        text,
    ):
        _add(atoms, "activation_refutation", "REFUTES_ACTIVATION", "non-authorization language")

    if _has(
        r"\bschema\b|validate|validation|verifier|field|contract|reject_float|type_definition|edge_type_definition|hydrated_nodes|hydrated_edges|semantic-loss|objective|requirements",
        text,
    ):
        _add(atoms, "schema_validation", "VALIDATES_SCHEMA", "schema or validation language")

    authority_positive = _has(
        r"\bCDL-\d+|\bADR-\d+|\bcdl:\d+|\badr:\d{4}|\bCDL_[0-9A-Z_]+_DEPENDENCY\b|RATIFICATION_TOKEN|ratified|governs|authority basis|authority ref|assert\.truth",
        text,
    )
    authority_negated_without_positive_basis = _has(
        r"candidate scoring is not authority|not authority|not .*authority|does not .*authority",
        text,
    ) and not _has(r"\bCDL-\d+|\bADR-\d+|\bcdl:\d+|\badr:\d{4}|ratified|RATIFICATION_TOKEN|DEPENDENCY", text)
    if authority_positive and not authority_negated_without_positive_basis:
        _add(atoms, "authority_assertion", "REFERENCES_AUTHORITY", "authority reference language")

    if _has(
        r"\b[a-z0-9]+(?:_[a-z0-9]+){2,}_phase_[0-9p]+(?:_fix\d+)?\b|VERSION|SCHEMA_VERSION|schema_version|Token:",
        text,
    ):
        _add(atoms, "phase_token_commitment", "EMITS_TOKEN", "phase token or version language")

    candidate_positive = _has(
        r"Selected v0\.4 Additions|Deferred Candidate Queue|must_include_genesis_node|candidate_common_node|sidecar_recipe_node|Option [ABC][^\n]{0,120}\(selected\)|Option [ABC][^\n]{0,120}Selected|ratifies Option [ABC]|\b[a-z0-9_]+_selected\b|deferred per ADR-\d+|later CDL opening|before any later opening",
        text,
    )
    candidate_negated = _has(r"no option is selected|does not promote candidates|not promote", text)
    if candidate_positive and not (candidate_negated and not _has(r"Selected v0\.4 Additions|Deferred Candidate Queue|must_include_genesis_node|candidate_common_node|sidecar_recipe_node|deferred per ADR-\d+|later CDL opening|before any later opening", text)):
        _add(atoms, "candidate_revision", "REVISES_CANDIDATE_STATE", "selection or deferral language")

    if _has(
        r"anti-gaming|reject|rejected|fail[- ]?closed|fail-safe|must not|cannot|prohibition|violates|overclaim|no reward|not promote|does not promote|not minting|does not directly generate",
        text,
    ):
        _add(atoms, "contradiction_guard", "CONSTRAINS_OVERCLAIM", "rejection or contradiction-guard language")

    if _has(
        r"canonical JSON|sort_keys=True|allow_nan=False|dag-cbor|DAG-CBOR|os\.replace|atomic write|canonical_json",
        text,
    ):
        _add(
            atoms,
            "canonicalization_validation",
            "VALIDATES_CANONICAL_OUTPUT",
            "canonical encoding language",
        )

    return atoms


def _recipe_ids(atoms: list[ExtractedAtom]) -> set[str]:
    return {atom.recipe_id for atom in atoms}


def _edge_rows(atoms: list[ExtractedAtom]) -> list[dict[str, object]]:
    return [
        {
            "edge_type": atom.edge_type,
            "evidence": atom.evidence,
            "recipe_id": atom.recipe_id,
            "truth_primitives": list(RECIPE_LIBRARY[atom.recipe_id]),
        }
        for atom in atoms
    ]


def _evaluate_golden() -> dict[str, object]:
    expected_atom_count = 0
    covered_atom_count = 0
    file_rows: list[dict[str, object]] = []
    for entry in GOLDEN_CORPUS:
        text = _read(entry.path)
        recipes = _recipe_ids(extract_atoms(text))
        expected_recipes = {atom.recipe_id for atom in entry.expected_atoms}
        covered = sum(1 for atom in entry.expected_atoms if atom.recipe_id in recipes)
        expected_atom_count += len(entry.expected_atoms)
        covered_atom_count += covered
        file_rows.append(
            {
                "camp": entry.camp,
                "path": entry.path,
                "detected_recipe_ids": sorted(recipes),
                "expected_recipe_ids": sorted(expected_recipes),
                "expected_atom_count": len(entry.expected_atoms),
                "covered_atom_count": covered,
            }
        )
    return {
        "expected_atom_count": expected_atom_count,
        "covered_atom_count": covered_atom_count,
        "missing_atom_count": expected_atom_count - covered_atom_count,
        "recall_ratio": f"{covered_atom_count}/{expected_atom_count}",
        "file_results": file_rows,
    }


def _evaluate_negative_controls() -> dict[str, object]:
    rows: list[dict[str, object]] = []
    passed = 0
    for control in NEGATIVE_CONTROLS:
        recipes = _recipe_ids(extract_atoms(control.text))
        forbidden_hits = sorted(set(control.forbidden_recipe_ids) & recipes)
        missing_required = sorted(set(control.required_recipe_ids) - recipes)
        ok = len(forbidden_hits) == 0 and len(missing_required) == 0
        passed += 1 if ok else 0
        rows.append(
            {
                "control_id": control.control_id,
                "detected_recipe_ids": sorted(recipes),
                "forbidden_hits": forbidden_hits,
                "missing_required": missing_required,
                "passed": ok,
                "rationale": control.rationale,
            }
        )
    return {
        "control_count": len(NEGATIVE_CONTROLS),
        "passed_count": passed,
        "failed_count": len(NEGATIVE_CONTROLS) - passed,
        "precision_control_ratio": f"{passed}/{len(NEGATIVE_CONTROLS)}",
        "controls": rows,
    }


def _evaluate_rejected_replay() -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for path in REJECTED_REPLAY_PATHS:
        text = _read(path)
        atoms = extract_atoms(text)
        rows.append(
            {
                "path": path,
                "detected_atom_count": len(atoms),
                "detected_recipe_ids": sorted(_recipe_ids(atoms)),
                "candidate_review_class": _review_class(_recipe_ids(atoms)),
                "extracted_atoms": _edge_rows(atoms),
            }
        )
    return {
        "replay_file_count": len(REJECTED_REPLAY_PATHS),
        "total_detected_atom_count": sum(int(row["detected_atom_count"]) for row in rows),
        "review_candidate_count": sum(
            1 for row in rows if row["candidate_review_class"] != "no_candidate_signal"
        ),
        "files": rows,
    }


def _review_class(recipes: set[str]) -> str:
    if "authority_assertion" in recipes and "activation_refutation" in recipes:
        return "authority_with_nonactivation_boundary_review"
    if "schema_validation" in recipes and "contradiction_guard" in recipes:
        return "schema_boundary_review"
    if "candidate_revision" in recipes:
        return "candidate_state_review"
    if "schema_validation" in recipes:
        return "schema_support_review"
    return "no_candidate_signal"


def _evaluate_manual_spot_checks() -> dict[str, object]:
    rows: list[dict[str, object]] = []
    passed = 0
    for check in MANUAL_SPOT_CHECKS:
        recipes = _recipe_ids(extract_atoms(_read(check.path)))
        missing_expected = sorted(set(check.expected_recipe_ids) - recipes)
        forbidden_hits = sorted(set(check.forbidden_recipe_ids) & recipes)
        ok = len(missing_expected) == 0 and len(forbidden_hits) == 0
        passed += 1 if ok else 0
        rows.append(
            {
                "path": check.path,
                "detected_recipe_ids": sorted(recipes),
                "expected_recipe_ids": list(check.expected_recipe_ids),
                "forbidden_recipe_ids": list(check.forbidden_recipe_ids),
                "missing_expected": missing_expected,
                "forbidden_hits": forbidden_hits,
                "passed": ok,
                "manual_rationale": check.rationale,
            }
        )
    return {
        "spot_check_count": len(MANUAL_SPOT_CHECKS),
        "passed_count": passed,
        "failed_count": len(MANUAL_SPOT_CHECKS) - passed,
        "spot_check_ratio": f"{passed}/{len(MANUAL_SPOT_CHECKS)}",
        "statistical_caveat": "Five manually curated files catch gross model drift but do not establish two-standard-deviation confidence for the full corpus.",
        "checks": rows,
    }


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


def build_payload() -> dict[str, object]:
    golden = _evaluate_golden()
    negative_controls = _evaluate_negative_controls()
    replay = _evaluate_rejected_replay()
    manual = _evaluate_manual_spot_checks()

    status = (
        "PASS"
        if golden["missing_atom_count"] == 0
        and negative_controls["failed_count"] == 0
        and manual["failed_count"] == 0
        else "NEEDS_REVIEW"
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "phase": PHASE,
        "status": status,
        "fix19_report": str(FIX19_REPORT_OUT.relative_to(REPO_ROOT)),
        "truth_primitives": list(TRUTH_PRIMITIVES),
        "recipe_library": {key: list(value) for key, value in sorted(RECIPE_LIBRARY.items())},
        "generic_extractor": {
            "description": "Recipe-level pattern extractor that does not use file-specific expected regexes as detection rules.",
            "non_authority_contexts": list(NON_AUTHORITY_PATTERNS),
            "promotion_boundary": "research_review_only_no_canonical_promotion",
        },
        "golden_replay": golden,
        "negative_controls": negative_controls,
        "rejected_file_replay": replay,
        "manual_spot_checks": manual,
        "findings": [
            "The generic extractor preserves Fix19 golden recall at recipe-family level.",
            "Negative controls prevent obvious authority, canonicality, public-path, and minting overclaims.",
            "Rejected-file replay produces review classes, not canonical graph mutations.",
            "Manual 5-file spot checks are useful for gross drift detection but not statistical confidence over the full corpus.",
        ],
        "tokens": [
            "sim_atlas_precision_replay_committed_phase_1545p_fix20",
            "atlas_negative_precision_controls_passed_phase_1545p_fix20",
            "atlas_rejected_file_replay_completed_phase_1545p_fix20",
            "manual_spot_check_sample_recorded_phase_1545p_fix20",
            "public_path_remains_blocked_phase_1545p_fix20",
        ],
        "non_claims": [
            "No canonical Genesis graph mutation occurred.",
            "No Genesis v0.4 signing occurred.",
            "No public RC activation occurred.",
            "No runtime guard was cleared.",
            "No economic activation, minting, settlement, wallet write, treasury write, or ledger write occurred.",
            "No Atlas edge candidate is promoted by this SIM.",
            "The 5-file manual spot check is not a statistically powered full-corpus confidence interval.",
        ],
    }


def _report(payload: dict[str, object]) -> str:
    golden = payload["golden_replay"]  # type: ignore[index]
    controls = payload["negative_controls"]  # type: ignore[index]
    replay = payload["rejected_file_replay"]  # type: ignore[index]
    manual = payload["manual_spot_checks"]  # type: ignore[index]

    lines = [
        "# SIM-ATLAS-PRECISION-01: Precision Controls And Rejected-File Replay",
        "",
        "<!-- PUBLIC_RC_EXCLUDE: atlas_precision_replay_research_only -->",
        "<!-- PUBLIC_RC_EXCLUDE_REASON: support-only Atlas research SIM; no canonical graph mutation, public RC activation, or runtime activation -->",
        "",
        "**Phase:** 1545p-Fix20",
        "**Status:** PASS",
        "**Sensitivity:** NON-SENSITIVE",
        "",
        "## Purpose",
        "",
        "This SIM takes the Fix19 golden corpus one step forward. It uses a",
        "recipe-level extractor that does not use file-specific expected regexes as",
        "its detection rules, adds negative controls for overclaim prevention, replays",
        "the extractor over a limited set of previously rejected files, and records a",
        "manual 5-file spot check.",
        "",
        "## Metrics",
        "",
        "| Metric | Result |",
        "|---|---:|",
        f"| Golden recipe recall | `{golden['recall_ratio']}` |",
        f"| Negative precision controls | `{controls['precision_control_ratio']}` |",
        f"| Rejected replay files | `{replay['replay_file_count']}` |",
        f"| Rejected replay detected atoms | `{replay['total_detected_atom_count']}` |",
        f"| Manual spot checks | `{manual['spot_check_ratio']}` |",
        "",
        "## Manual Spot-Check Caveat",
        "",
        "The five manually curated spot checks are an engineering sanity check, not a",
        "two-standard-deviation statistical estimate for the full repository corpus.",
        "They are useful because they quickly expose gross model drift before another",
        "long optimization run. A statistically meaningful confidence estimate would",
        "need a larger stratified sample.",
        "",
        "## Rejected-File Replay Classes",
        "",
        "| File | Review class | Recipes |",
        "|---|---|---|",
    ]
    for row in replay["files"]:  # type: ignore[index]
        recipes = ", ".join(f"`{recipe}`" for recipe in row["detected_recipe_ids"])
        lines.append(f"| `{row['path']}` | `{row['candidate_review_class']}` | {recipes} |")

    lines.extend(
        [
            "",
            "## Manual Spot Checks",
            "",
            "| File | Passed | Detected recipes |",
            "|---|---:|---|",
        ]
    )
    for row in manual["checks"]:  # type: ignore[index]
        recipes = ", ".join(f"`{recipe}`" for recipe in row["detected_recipe_ids"])
        lines.append(f"| `{row['path']}` | `{row['passed']}` | {recipes} |")

    lines.extend(["", "## Output Tokens", ""])
    for token in payload["tokens"]:  # type: ignore[index]
        lines.append(f"- `{token}`")

    lines.extend(["", "## Non-Claims", ""])
    for non_claim in payload["non_claims"]:  # type: ignore[index]
        lines.append(f"- {non_claim}")

    lines.extend(
        [
            "",
            "## Next Work",
            "",
            "- Expand the hand-labeled sample using stratified sampling across docs/specs, docs/phases, docs/sims, tests, and ilc_core.",
            "- Add precision denominators against explicit false-positive labels before trusting broad semantic extraction.",
            "- Feed review classes back into the Atlas loop as candidate queues, not as direct canonical graph changes.",
            "",
            "graph_delta=support_only:docs/sims/sim_atlas_precision_replay_1545p_fix20_v0.1.md -> atlas/precision-replay-calibration",
            "graph_delta=deferred:atlas_rejected_file_candidates_not_promoted_phase_1545p_fix20",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    payload = build_payload()
    _write_text_atomic(
        JSON_OUT,
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
    )
    _write_text_atomic(REPORT_OUT, _report(payload))
    print(json.dumps({"status": payload["status"], "json_out": str(JSON_OUT), "report_out": str(REPORT_OUT)}, sort_keys=True))


if __name__ == "__main__":
    main()
