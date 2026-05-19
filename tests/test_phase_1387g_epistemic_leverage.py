"""Phase 1387g — SIM-GRAPHOPT-02: epistemic leverage analysis.

Tests verify:
- epistemic_leverage_analysis section present in diagnostic
- All non-root leverage scores are computed and non-negative
- No keystone nodes (leverage ≥ 5): graph has no single point of epistemic failure
- Leverage=1 for all non-root nodes confirms hub-and-spoke resilience
  (every node is reachable via multiple paths; removal only isolates itself)
- Axiomatic root count matches expected 15 (7 truth primitives + ADR-0004 +
  3 axioms + genesis_agent + 3 Category A bootstrap nodes)
- Baseline reachable count == 54 (full star map after Phase 1387e)
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
DIAGNOSTIC_JSON = ROOT / "out" / "genesis_compile_coverage_diagnostic_v0.3_candidate.json"


def _ela() -> dict:
    return json.loads(DIAGNOSTIC_JSON.read_text())["epistemic_leverage_analysis"]


def test_epistemic_leverage_section_present() -> None:
    data = json.loads(DIAGNOSTIC_JSON.read_text())
    assert "epistemic_leverage_analysis" in data, "epistemic_leverage_analysis section missing"


def test_baseline_reachable_count_54() -> None:
    assert _ela()["baseline_reachable_count"] == 54


def test_leverage_scores_cover_all_core_nodes() -> None:
    ela = _ela()
    # baseline = 54; axiomatic roots + non-roots = 54
    total_scored = len(ela["leverage_scores"])
    assert total_scored == 54, f"Expected 54 leverage scores; got {total_scored}"


def test_all_non_root_leverage_non_negative() -> None:
    for entry in _ela()["leverage_scores"]:
        if entry["leverage"] is not None:
            assert entry["leverage"] >= 0, (
                f"Node {entry['node_id']!r} has negative leverage {entry['leverage']}"
            )


def test_no_keystone_nodes() -> None:
    """Hub-and-spoke graph has no single-point epistemic failures (leverage ≥ 5)."""
    ela = _ela()
    assert ela["keystone_count"] == 0, (
        f"Expected 0 keystone nodes; got {ela['keystone_count']}: {ela['keystone_nodes']}"
    )


def test_axiomatic_root_count_15() -> None:
    """15 axiomatic roots: 7 truth primitives + ADR-0004 + 3 axioms +
    genesis_agent:01 + 3 Category A bootstrap nodes."""
    ela = _ela()
    assert ela["axiomatic_root_count"] == 15, (
        f"Expected 15 axiomatic roots; got {ela['axiomatic_root_count']}"
    )


def test_hub_and_spoke_resilience_all_leverage_one() -> None:
    """All non-root core nodes have leverage=1: removal only isolates the node
    itself, confirming the graph has no epistemic bottlenecks."""
    ela = _ela()
    non_root = [s for s in ela["leverage_scores"] if s["leverage"] is not None]
    wrong = [s for s in non_root if s["leverage"] != 1]
    assert wrong == [], (
        f"Expected all non-root nodes to have leverage=1 (hub-and-spoke resilience); "
        f"got different values: {[(s['node_id'], s['leverage']) for s in wrong[:5]]}"
    )


def test_leverage_type_distribution() -> None:
    """With all leverage=1, every non-root node is classified 'normal'."""
    ela = _ela()
    non_root_types = {
        s["leverage_type"]
        for s in ela["leverage_scores"]
        if s["leverage"] is not None
    }
    assert non_root_types == {"normal"}, (
        f"Expected only 'normal' leverage type for non-root nodes; got {non_root_types}"
    )


def test_phase_1387g_token_in_compiler() -> None:
    compiler = (ROOT / "tools" / "genesis_compile_coverage_diagnostic_v0.3_candidate.py").read_text()
    assert "Phase 1387g" in compiler, "Phase 1387g annotation not found in candidate compiler"
