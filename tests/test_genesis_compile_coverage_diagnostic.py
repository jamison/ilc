"""GENESIS-COMPILE-01 diagnostic tests."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest


ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/genesis_compile_coverage_diagnostic.py"
@pytest.fixture(scope="module")
def diagnostic(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[dict[str, object], pathlib.Path]:
    output_dir = tmp_path_factory.mktemp("genesis_compile_coverage")
    json_out = output_dir / "diagnostic.json"
    report_out = output_dir / "diagnostic.md"
    subprocess.run(
        [
            sys.executable,
            str(TOOL),
            "--json-out",
            str(json_out),
            "--report-out",
            str(report_out),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    data = json.loads(json_out.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data, report_out


def test_genesis_compile_coverage_outputs_exist_and_have_verdict(
    diagnostic: tuple[dict[str, object], pathlib.Path],
) -> None:
    payload, report_out = diagnostic
    assert report_out.exists()
    assert payload["metadata"]["format_version"] == "genesis_compile_coverage_diagnostic.v0.1"
    assert payload["verdict"] in {
        "COMPLETE_ENOUGH_FOR_PHASE_1136",
        "PARTIAL_WITH_STRUCTURAL_GAPS",
        "FAIL_CORE_INADEQUATE",
    }


def test_genesis_compile_coverage_records_current_partial_result(
    diagnostic: tuple[dict[str, object], pathlib.Path],
) -> None:
    payload, _ = diagnostic
    coverage = payload["compile_coverage"]
    assert payload["verdict"] == "PARTIAL_WITH_STRUCTURAL_GAPS"
    assert coverage["observed_source_files_total"] >= 1600
    assert coverage["core_nodes_total"] == 32
    assert coverage["basis_reachable_core_nodes"] == 17
    assert payload["authority_traceability"]["authority_traceable_core_nodes"] == 31
    assert coverage["core_explainable_sources"] >= 500
    assert coverage["basis_explainable_sources"] >= 250


def test_genesis_compile_coverage_edge_recipes_are_complete(
    diagnostic: tuple[dict[str, object], pathlib.Path],
) -> None:
    payload, _ = diagnostic
    edge_analysis = payload["edge_recipe_analysis"]
    assert edge_analysis["proposed_edge_count"] == 25
    assert edge_analysis["missing_decomposition_recipe_count"] == 0
    assert edge_analysis["proposed_edge_type_counts"] == {
        "CONSTRAINS": 2,
        "GOVERNS": 20,
        "PRIMITIVE_INVOCATION": 3,
    }


def test_genesis_compile_coverage_surfaces_basis_unreachable_overlay_cluster(
    diagnostic: tuple[dict[str, object], pathlib.Path],
) -> None:
    payload, _ = diagnostic
    unreachable = {item["candidate_id"] for item in payload["gaps"]["basis_unreachable_core_nodes"]}
    assert "policy:provenance_decay_alpha_0_45" in unreachable
    assert "cdl:084_provenance_chain_attribution" in unreachable
    assert "adr:0035_homoiconic_type_definition_system" in unreachable


def test_genesis_compile_coverage_report_is_human_readable(
    diagnostic: tuple[dict[str, object], pathlib.Path],
) -> None:
    _, report_out = diagnostic
    text = report_out.read_text(encoding="utf-8")
    assert "# GENESIS-COMPILE-01 Compile Coverage Diagnostic v0.1" in text
    assert "`PARTIAL_WITH_STRUCTURAL_GAPS`" in text
    assert "genesis_compile_coverage_diagnostic_complete_v0_1" in text
