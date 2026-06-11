from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/specs/ilc_genesis_star_map_candidate_methodology_preservation_1545p_fix6_v0.1.md"
INVENTORY = ROOT / "docs/sims/sim_spectral_02/genesis_node_candidate_inventory_v0.3_candidate.md"
REPORT = ROOT / "docs/sims/sim_spectral_02/genesis_compile_coverage_diagnostic_v0.3_candidate.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix6_genesis_v03_methodology_preservation_walkthrough.md"
STAR_MAP = ROOT / "out/genesis_core_star_map_v0.3_candidate.json"
SIGNED_DIAGNOSTIC = ROOT / "out/genesis_compile_coverage_diagnostic_v0.3_candidate.json"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_fix6_methodology_tokens_and_boundaries() -> None:
    text = read(SPEC)
    for token in (
        "phase_1545p_fix6_genesis_v03_methodology_preservation_committed",
        "genesis_v01_v02_v03_methodology_reconciled_phase_1545p_fix6",
        "authority_traceability_not_source_coverage_gate_recorded_phase_1545p_fix6",
        "public_rc_drift_reconciliation_anchor_consumed_phase_1545p_fix6",
        "post_1447_manifest_relevance_audit_committed_phase_1545p_fix6",
        "v03_signed_baseline_successor_decision_deferred_to_fix7_phase_1545p_fix6",
        "idea_descent_recorded_as_later_overlay_phase_1545p_fix6",
        "genesis_manifest_not_mutated_phase_1545p_fix6",
        "public_path_remains_blocked_phase_1545p_fix6",
    ):
        assert token in text
    assert "Idea descent overlay" in text
    assert "not the original v0.1/v0.2 generator" in text
    assert "does not mutate any signed Genesis artifact" in text


def test_methodology_distinguishes_reachability_authority_and_source_coverage() -> None:
    text = read(SPEC)
    assert "`basis_reachability`" in text
    assert "`authority_traceability`" in text
    assert "`source_explainability`" in text
    assert "support-graph expansion queue" in text
    assert "not by itself a failure of the signed v0.3 baseline" in text


def test_v03_inventory_matches_signed_star_map_shape() -> None:
    inventory = read(INVENTORY)
    star = json.loads(STAR_MAP.read_text(encoding="utf-8"))
    assert len(star["nodes"]) == 54
    assert len(star["edges"]) == 77
    assert "- Candidate nodes: `54`" in inventory
    assert "- Candidate edges: `77`" in inventory
    assert "| `truth_primitive:commit.epoch` |" in inventory
    assert "| `adr:0035_homoiconic_type_definition_system` |" in inventory
    assert "| `adr:0006_eve_canonical_capsule_integrity` |" in inventory


def test_signed_diagnostic_baseline_was_not_mutated_by_fix6() -> None:
    diagnostic = json.loads(SIGNED_DIAGNOSTIC.read_text(encoding="utf-8"))
    assert diagnostic["compile_coverage"]["observed_source_files_total"] == 2521
    assert diagnostic["compile_coverage"]["core_explainable_sources"] == 785
    assert diagnostic["metadata"]["source_star_map"] == "out/genesis_core_star_map_v0.1.json"


def test_current_support_report_records_post_1447_drift_without_signing_claim() -> None:
    report = read(REPORT)
    assert "Observed source files: `2573`" in report
    assert "Core-explainable source files: `801`" in report
    assert "support-graph expansion queue, not as a protocol failure" in report


def test_relevance_audit_flags_fix7_successor_decision() -> None:
    text = read(SPEC)
    assert "| ADR-0009 protocol-native bundle distribution |" in text
    assert "| ADR-0035 / CDL-097 type-definition authority |" in text
    assert "| CDL-096 Werner plus global-tier finality |" in text
    assert "successor_decision_point=must_include_items_present_fix7_required" in text
    assert "Fix7 must seriously evaluate `v0.4_candidate_required`" in text


def test_frontier_docs_record_fix6_and_carry_forward() -> None:
    for path in (WALKTHROUGH, STATUS, PLANNING_INDEX):
        text = read(path)
        assert "phase_1545p_fix6_genesis_v03_methodology_preservation_committed" in text
        assert "post_1447_manifest_relevance_audit_committed_phase_1545p_fix6" in text
        assert "public_path_remains_blocked_phase_1545p_fix6" in text
    assert "Phase 1545p-Fix7" in read(STATUS)
