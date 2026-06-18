"""Tests for Phase 1545p-Fix53: Heuristic GOVERNS expansion."""

from __future__ import annotations

import json
import hashlib
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIX51 = ROOT / "out" / "atlas_research" / "genesis_atlas_enriched_candidate_fix51.json"
FIX53 = ROOT / "out" / "atlas_research" / "genesis_atlas_enriched_candidate_fix53.json"
SIM = ROOT / "out" / "genesis_authority_sim_battery_fix53_v0.1.json"
STATUS = ROOT / "docs" / "phases" / "STATUS.md"
VALIDATOR = ROOT / "tools" / "validate_authority_graph_invariants.py"
FIX50_LEDGER = ROOT / "docs" / "specs" / "ilc_fix50_authority_edge_repair_ledger_v0.1.json"

pytestmark = pytest.mark.skipif(
    not FIX51.exists() or not FIX53.exists() or not SIM.exists(),
    reason="Fix53 local Atlas artifacts are gitignored; regenerate with sim_genesis_atlas_fix53_heuristic_governs_expansion.py",
)


def _load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def test_fix53_complete_token_in_status():
    assert "fix53_complete" in STATUS.read_text(), (
        "fix53_complete token missing from STATUS.md"
    )


def test_fix53_candidate_exists_and_valid():
    assert FIX53.exists(), f"Fix53 candidate not found: {FIX53}"
    d = _load_json(FIX53)
    assert "edges" in d
    assert "nodes" in d
    assert "fix53_generation_report" in d


def test_fix53_has_more_governs_than_fix51():
    fix51 = _load_json(FIX51)
    fix53 = _load_json(FIX53)
    count51 = sum(1 for e in fix51["edges"] if e["edge_type"] == "GOVERNS")
    count53 = sum(1 for e in fix53["edges"] if e["edge_type"] == "GOVERNS")
    assert count53 > count51, (
        f"Fix53 GOVERNS count ({count53}) must exceed Fix51 ({count51})"
    )


def test_fix53_new_governs_edge_count_in_expected_range():
    d = _load_json(FIX53)
    total = d["fix53_generation_report"]["total_new_governs_edges"]
    assert total == 94, f"Expected 94 canonical-source new GOVERNS edges, got {total}"
    assert d["fix53_generation_report"]["canonical_source_guard"] == "canonical_ratified"
    assert d["fix53_generation_report"]["rejected_noncanonical_source_edges"] > 0


def test_fix53_invariant_coverage_strictly_improved():
    d = _load_json(FIX53)
    report = d["fix53_generation_report"]
    before = report["invariant_coverage_before"]
    after = report["invariant_coverage_after"]
    assert after > before, (
        f"Invariant coverage did not improve: {before:.4f} -> {after:.4f}"
    )


def test_fix53_policy_coverage_strictly_improved():
    d = _load_json(FIX53)
    report = d["fix53_generation_report"]
    before = report["policy_coverage_before"]
    after = report["policy_coverage_after"]
    assert after > before, (
        f"Policy coverage did not improve: {before:.4f} -> {after:.4f}"
    )


def _new_edges(fix53: dict) -> list:
    """Return edges in fix53 that have annotation_phase=phase_1545p_fix53."""
    return [e for e in fix53["edges"] if e.get("annotation_phase") == "phase_1545p_fix53"]


def test_fix53_new_edges_have_heuristic_annotation_method():
    fix53 = _load_json(FIX53)
    new_edges = _new_edges(fix53)
    assert len(new_edges) > 0, "No phase_1545p_fix53 edges found in Fix53 candidate"
    for e in new_edges:
        assert e.get("annotation_method") == "heuristic_cdl_source_doc", (
            f"New edge {e.get('edge_id')} has wrong annotation_method: {e.get('annotation_method')}"
        )


def test_fix53_new_edges_are_governs():
    fix53 = _load_json(FIX53)
    new_edges = _new_edges(fix53)
    for e in new_edges:
        assert e["edge_type"] == "GOVERNS", (
            f"New edge {e.get('edge_id')} has wrong type: {e['edge_type']}"
        )


def test_fix53_new_edges_have_deterministic_edge_ids_and_no_duplicates():
    fix53 = _load_json(FIX53)
    new_edges = _new_edges(fix53)
    edge_ids = [e.get("edge_id") for e in new_edges]
    assert len(edge_ids) == len(set(edge_ids)), "Duplicate Fix53 edge_id values found"
    for e in new_edges:
        expected = "edge:" + hashlib.sha256(
            f"{e['source']}|{e['edge_type']}|{e['target']}".encode("utf-8")
        ).hexdigest()[:16]
        assert e["edge_id"] == expected


def test_fix53_new_edges_have_candidate_boundary_metadata():
    fix53 = _load_json(FIX53)
    new_edges = _new_edges(fix53)
    for e in new_edges:
        assert e["candidate_status"] == "fix53_support_only_not_canonical"
        assert e["promotion_status"] == "candidate_only_not_canonical"
        assert e["review_status"] == "heuristic_not_manual_not_signing_ready"
        assert e["signature_status"] == "unsigned_candidate_preimage"
        assert e["authority_boundary"] == "canonical_ratified_cdl_source_only"


def test_fix53_new_governs_sources_are_canonical_ratified_cdls():
    ledger = _load_json(FIX50_LEDGER)
    classifications = ledger["authority_classifications"]
    fix53 = _load_json(FIX53)
    for e in _new_edges(fix53):
        assert classifications[e["source"]]["classification_tier"] == "canonical_ratified"


def test_fix53_new_edge_nodes_exist():
    d = _load_json(FIX53)
    node_ids = {n["candidate_id"] for n in d["nodes"]}
    new_edges = _new_edges(d)
    missing_sources = [e["source"] for e in new_edges if e["source"] not in node_ids]
    missing_targets = [e["target"] for e in new_edges if e["target"] not in node_ids]
    assert not missing_sources, f"New edges have missing sources: {missing_sources[:5]}"
    assert not missing_targets, f"New edges have missing targets: {missing_targets[:5]}"


def test_fix53_no_governs_cycles():
    d = _load_json(FIX53)
    # Build GOVERNS adjacency list
    governs: dict[str, list[str]] = {}
    for e in d["edges"]:
        if e["edge_type"] == "GOVERNS":
            governs.setdefault(e["source"], []).append(e["target"])

    # Detect cycles via DFS with a recursion stack (path tracking)
    # A cycle exists if we revisit a node that is currently on the DFS path.
    def has_cycle() -> str | None:
        visited: set[str] = set()
        rec_stack: set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in governs.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.discard(node)
            return False

        for src in governs:
            if src not in visited:
                if dfs(src):
                    return src
        return None

    cycle_src = has_cycle()
    assert cycle_src is None, f"GOVERNS cycle detected starting from {cycle_src}"


def test_fix53_node_count_unchanged():
    fix51 = _load_json(FIX51)
    fix53 = _load_json(FIX53)
    assert len(fix53["nodes"]) == len(fix51["nodes"]), (
        f"Node count changed: Fix51={len(fix51['nodes'])}, Fix53={len(fix53['nodes'])}"
    )


def test_fix53_sim_output_exists_and_valid():
    assert SIM.exists(), f"Fix53 SIM output not found: {SIM}"
    d = _load_json(SIM)
    assert "suite_d_rerun" in d
    assert "overall_verdict" in d


def test_fix53_sim_verdict_not_fail():
    d = _load_json(SIM)
    assert d["overall_verdict"] != "fail", (
        f"Fix53 SIM verdict is 'fail': {d.get('overall_verdict')}"
    )


def test_fix53_sim_coverage_strictly_improved():
    d = _load_json(SIM)
    rerun = d["suite_d_rerun"]
    assert rerun["coverage_strictly_improved"] is True, (
        "Fix53 SIM does not report coverage_strictly_improved=True"
    )


def test_fix53_validator_exits_zero():
    if not VALIDATOR.exists():
        return  # skip gracefully if tool not present
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(FIX53)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Validator failed on Fix53 candidate:\n{result.stdout}\n{result.stderr}"
    )
