"""Phase 1387c — Compiler basis expansion + two-tier verdict.

Tests verify:
- All 32/32 core nodes are now basis-reachable after adding Category A bootstrap axioms
- basis_unreachable_core_nodes gap is empty
- Two-tier tier_analysis section is present and correct
- Verdict is GENESIS_CORE_COMPLETE_SOURCE_COVERAGE_PARTIAL
- The compiler tool itself contains the 3 Category A node IDs in _basis_roots
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
DIAGNOSTIC_JSON = ROOT / "out" / "genesis_compile_coverage_diagnostic_v0.3_candidate.json"
COMPILER = ROOT / "tools" / "genesis_compile_coverage_diagnostic_v0.3_candidate.py"

CATEGORY_A_NODES = {
    "artifact:genesis_intent_attestation_init_authority_map",
    "artifact:genesis_agent1_pubkey_record_838a",
    "ceremony:genesis_agent1_keygen_838a",
}


def test_basis_reachable_all_32() -> None:
    data = json.loads(DIAGNOSTIC_JSON.read_text())
    cc = data["compile_coverage"]
    assert cc["basis_reachable_core_nodes"] == cc["core_nodes_total"], (
        f"Expected all core nodes reachable; got {cc['basis_reachable_core_nodes']} / {cc['core_nodes_total']}"
    )


def test_basis_unreachable_gap_empty() -> None:
    data = json.loads(DIAGNOSTIC_JSON.read_text())
    unreachable = data["gaps"]["basis_unreachable_core_nodes"]
    assert unreachable == [], (
        f"Expected empty gap; got {[n['candidate_id'] for n in unreachable]}"
    )


def test_verdict_genesis_core_complete_source_coverage_partial() -> None:
    data = json.loads(DIAGNOSTIC_JSON.read_text())
    assert data["verdict"] == "GENESIS_CORE_COMPLETE_SOURCE_COVERAGE_PARTIAL", (
        f"Unexpected verdict: {data['verdict']!r}"
    )


def test_tier_analysis_present() -> None:
    data = json.loads(DIAGNOSTIC_JSON.read_text())
    assert "tier_analysis" in data, "tier_analysis section missing from diagnostic"
    tier = data["tier_analysis"]
    assert "genesis_derivable_node_count" in tier
    assert "governance_extended_node_count" in tier
    assert "basis_unreachable_count" in tier


def test_tier_analysis_genesis_derivable_equals_core_total() -> None:
    data = json.loads(DIAGNOSTIC_JSON.read_text())
    tier = data["tier_analysis"]
    core_total = data["compile_coverage"]["core_nodes_total"]
    assert tier["genesis_derivable_node_count"] == core_total, (
        f"Expected {core_total} genesis-derivable nodes; got {tier['genesis_derivable_node_count']}"
    )


def test_tier_analysis_basis_unreachable_zero() -> None:
    data = json.loads(DIAGNOSTIC_JSON.read_text())
    assert data["tier_analysis"]["basis_unreachable_count"] == 0


def test_compiler_contains_category_a_nodes() -> None:
    """Category A bootstrap axioms are present in the compiler source."""
    source = COMPILER.read_text()
    for node_id in CATEGORY_A_NODES:
        assert node_id in source, (
            f"Category A node {node_id!r} not found in compiler _basis_roots"
        )


def test_phase_1387c_token() -> None:
    source = COMPILER.read_text()
    assert "Phase 1387c" in source, "Phase 1387c annotation not found in compiler"
