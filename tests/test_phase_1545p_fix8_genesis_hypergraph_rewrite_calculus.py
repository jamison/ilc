from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/specs/ilc_genesis_hypergraph_rewrite_calculus_1545p_fix8_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix8_genesis_hypergraph_rewrite_calculus_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
STAR_MAP = ROOT / "out/genesis_core_star_map_v0.3_candidate.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_fix8_tokens_and_non_authority_boundary() -> None:
    text = read(SPEC)
    for token in (
        "phase_1545p_fix8_genesis_hypergraph_rewrite_calculus_committed",
        "genesis_rewrite_calculus_support_only_phase_1545p_fix8",
        "dpo_interface_preservation_rule_recorded_phase_1545p_fix8",
        "hrg_candidate_generation_not_authority_recorded_phase_1545p_fix8",
        "transitivity_preserving_projection_support_view_recorded_phase_1545p_fix8",
        "genesis_manifest_not_mutated_phase_1545p_fix8",
        "public_path_remains_blocked_phase_1545p_fix8",
    ):
        assert token in text
    assert "It does not create authority." in text
    assert "The schema is support-only." in text


def test_research_mapping_and_rule_types_are_present() -> None:
    text = read(SPEC)
    for phrase in (
        "Hyperedge replacement grammars (HRG)",
        "DPO/SPO graph rewriting",
        "Multiway hypergraph rewriting",
        "Transitivity-preserving projection",
        "`node_expand`",
        "`node_split`",
        "`node_merge`",
        "`hyperedge_replace`",
        "`edge_refine`",
        "`projection_simplify`",
        "`candidate_reject`",
        "`candidate_defer`",
    ):
        assert phrase in text


def test_dpo_interface_preservation_checklist_is_strict() -> None:
    text = read(SPEC)
    for phrase in (
        "No dangling edge endpoints",
        "No broken authority trace",
        "No loss of basis reachability",
        "No decomposition gap",
        "No evidence erasure",
        "No signed-artifact mutation",
        "No implicit authority",
    ):
        assert phrase in text


def test_hrg_schema_contains_required_fields_and_non_authority_invariants() -> None:
    text = read(SPEC)
    for phrase in (
        '"rule_id": "rewrite:<stable-id>"',
        '"left_hand_support_pattern"',
        '"boundary_node_set"',
        '"right_hand_candidate_replacement"',
        '"evidence_path_set"',
        '"authority_trace_preserved": true',
        '"basis_reachability_preserved": true',
        '"candidate_not_authority": true',
    ):
        assert phrase in text


def test_projection_boundary_preserves_view_semantics_only() -> None:
    text = read(SPEC)
    assert "Transitivity-preserving projections" in text
    assert "support-only projection" in text
    assert "must not replace canonical edge semantics" in text
    assert "change ECU attribution" in text
    assert "create graph authority" in text


def test_signed_v03_star_map_was_not_mutated_by_fix8() -> None:
    data = json.loads(read(STAR_MAP))
    assert len(data["nodes"]) == 54
    assert len(data["edges"]) == 77


def test_frontier_docs_record_fix8() -> None:
    for path in (WALKTHROUGH, STATUS, PLANNING_INDEX):
        text = read(path)
        assert "phase_1545p_fix8_genesis_hypergraph_rewrite_calculus_committed" in text
        assert "genesis_rewrite_calculus_support_only_phase_1545p_fix8" in text
        assert "public_path_remains_blocked_phase_1545p_fix8" in text
    assert "rewrite generation is not Genesis authority" in read(WALKTHROUGH)
