"""GENESIS-COMPILE-01 diagnostic tests."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/genesis_compile_coverage_diagnostic.py"
JSON_OUT = ROOT / "out/genesis_compile_coverage_diagnostic_v0.1.json"
REPORT_OUT = ROOT / "docs/sims/sim_spectral_02/genesis_compile_coverage_diagnostic_v0.1.md"
_TOOL_RAN = False


def _run_tool() -> None:
    global _TOOL_RAN
    if _TOOL_RAN:
        return
    subprocess.run([sys.executable, str(TOOL)], cwd=ROOT, check=True, text=True, capture_output=True)
    _TOOL_RAN = True


def _payload() -> dict[str, object]:
    _run_tool()
    data = json.loads(JSON_OUT.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_genesis_compile_coverage_outputs_exist_and_have_verdict() -> None:
    payload = _payload()
    assert JSON_OUT.exists()
    assert REPORT_OUT.exists()
    assert payload["metadata"]["format_version"] == "genesis_compile_coverage_diagnostic.v0.1"
    assert payload["verdict"] in {
        "COMPLETE_ENOUGH_FOR_PHASE_1136",
        "PARTIAL_WITH_STRUCTURAL_GAPS",
        "FAIL_CORE_INADEQUATE",
    }


def test_genesis_compile_coverage_records_current_partial_result() -> None:
    payload = _payload()
    coverage = payload["compile_coverage"]
    assert payload["verdict"] == "PARTIAL_WITH_STRUCTURAL_GAPS"
    assert coverage["observed_source_files_total"] >= 1600
    assert coverage["core_nodes_total"] == 32
    assert coverage["basis_reachable_core_nodes"] == 17
    assert payload["authority_traceability"]["authority_traceable_core_nodes"] == 31
    assert coverage["core_explainable_sources"] >= 500
    assert coverage["basis_explainable_sources"] >= 250


def test_genesis_compile_coverage_edge_recipes_are_complete() -> None:
    payload = _payload()
    edge_analysis = payload["edge_recipe_analysis"]
    assert edge_analysis["proposed_edge_count"] == 25
    assert edge_analysis["missing_decomposition_recipe_count"] == 0
    assert edge_analysis["proposed_edge_type_counts"] == {
        "CONSTRAINS": 2,
        "GOVERNS": 20,
        "PRIMITIVE_INVOCATION": 3,
    }


def test_genesis_compile_coverage_surfaces_basis_unreachable_overlay_cluster() -> None:
    payload = _payload()
    unreachable = {item["candidate_id"] for item in payload["gaps"]["basis_unreachable_core_nodes"]}
    assert "policy:provenance_decay_alpha_0_45" in unreachable
    assert "cdl:084_provenance_chain_attribution" in unreachable
    assert "adr:0035_homoiconic_type_definition_system" in unreachable


def test_genesis_compile_coverage_report_is_human_readable() -> None:
    _payload()
    text = REPORT_OUT.read_text(encoding="utf-8")
    assert "# GENESIS-COMPILE-01 Compile Coverage Diagnostic v0.1" in text
    assert "`PARTIAL_WITH_STRUCTURAL_GAPS`" in text
    assert "genesis_compile_coverage_diagnostic_complete_v0_1" in text
