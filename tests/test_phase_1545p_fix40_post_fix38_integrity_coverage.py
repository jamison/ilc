from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix40_g10_post_fix38_integrity_coverage.md"
)
RUNNER = ROOT / "tools/build_fix40_post_fix38_integrity_coverage.py"
CANDIDATE = ROOT / "out/atlas_research/genesis_atlas_enriched_candidate_fix40.json"
GAP_ANALYSIS = ROOT / "out/genesis_core_star_map_gap_analysis_v0.2.json"
COMPILE_DIAGNOSTIC = ROOT / "out/genesis_compile_coverage_diagnostic_v0.2.json"
COVERAGE = ROOT / "out/test_graph_coverage_1545p_fix40.json"
DELTA_REPORT = ROOT / "docs/sims/sim_spectral_02/genesis_coverage_delta_fix38_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"


TOKENS = {
    "fix40_integrity_checks_passed",
    "fix40_coverage_rerun_complete",
    "fix40_enriched_candidate_produced",
    "fix40_complete",
    "public_path_remains_blocked_phase_1545p_fix40",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_fix40_prompt_validates() -> None:
    result = subprocess.run(
        [sys.executable, "tools/validate_phase_prompt.py", str(PROMPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_fix40_runner_can_regenerate_outputs(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate.json"
    coverage = tmp_path / "coverage.json"
    coverage_report = tmp_path / "coverage.md"
    gap = tmp_path / "gap.json"
    compile_diag = tmp_path / "compile.json"
    delta = tmp_path / "delta.md"

    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--candidate-out",
            str(candidate),
            "--coverage-json",
            str(coverage),
            "--coverage-report",
            str(coverage_report),
            "--gap-analysis",
            str(gap),
            "--compile-diagnostic",
            str(compile_diag),
            "--delta-report",
            str(delta),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["integrity"] == "pass"
    assert payload["added_candidate_edges"] >= 4999
    regenerated_delta = load(gap)["coverage_delta_from_fix33"]
    historical_delta = load(GAP_ANALYSIS)["coverage_delta_from_fix33"]
    assert historical_delta["missing_expected_authority_trace_count"]["current"] == 57
    regenerated_missing = regenerated_delta["missing_expected_authority_trace_count"]["current"]
    assert 0 <= regenerated_missing < historical_delta["missing_expected_authority_trace_count"]["current"]
    assert load(coverage)["summary"]["phase"] == "1545p-Fix40"
    assert "1545p-Fix40" in coverage_report.read_text(encoding="utf-8")
    assert "Fix40 Post-Fix38 Coverage Delta" in delta.read_text(encoding="utf-8")


def test_fix40_candidate_integrity_and_merge_counts() -> None:
    candidate = load(CANDIDATE)
    gap = load(GAP_ANALYSIS)
    integrity = gap["integrity"]
    merge = candidate["fix40_merge_summary"]

    assert candidate["phase"] == "1545p-Fix40"
    assert candidate["candidate_status"] == (
        "unsigned_support_only_not_canonical_fix40_post_fix38_integrity_candidate"
    )
    assert len(candidate["nodes"]) == 15657
    assert len(candidate["edges"]) == 75258
    assert merge["annotations_processed"] == 756
    assert merge["considered_ledger_edges"] == 4999
    assert merge["added_candidate_edges"] == 4999
    assert merge["created_source_nodes"] == 0
    assert integrity["status"] == "pass"
    assert integrity["endpoint_dangling_edge_count"] == 0
    assert integrity["duplicate_node_id_count"] == 0
    assert integrity["fix40_references_authority_missing_annotation_method_count"] == 0
    assert integrity["manual_reviewed_edges_missing_annotation_phase_count"] == 0


def test_fix40_coverage_delta_improves_fix33_frontier() -> None:
    delta = load(GAP_ANALYSIS)["coverage_delta_from_fix33"]
    coverage = load(COVERAGE)["summary"]

    assert delta["files_with_tests_edge_count"]["delta"] == 558
    assert delta["missing_tests_edge_count"]["delta"] == -544
    assert delta["authority_trace_satisfied_file_count"]["delta"] == 576
    assert delta["missing_expected_authority_trace_count"]["delta"] == -564
    assert coverage["missing_tests_edge_count"] == 0
    assert coverage["gap_class_counts"]["missing_expected_authority_trace"] == 57
    assert coverage["missing_candidate_node_count"] == 8


def test_fix40_docs_preserve_non_claims_and_tokens() -> None:
    token_text = (
        DELTA_REPORT.read_text(encoding="utf-8")
        + STATUS.read_text(encoding="utf-8")
        + (ROOT / "docs/specs/ilc_test_graph_coverage_report_1545p_fix40_v0.1.md").read_text(
            encoding="utf-8"
        )
    )
    fix40_docs = (
        DELTA_REPORT.read_text(encoding="utf-8")
        + (ROOT / "docs/specs/ilc_test_graph_coverage_report_1545p_fix40_v0.1.md").read_text(
            encoding="utf-8"
        )
        + (
            ROOT
            / "docs/phases/phase_1545p_fix40_post_fix38_integrity_coverage_walkthrough.md"
        ).read_text(encoding="utf-8")
    )

    for token in TOKENS:
        assert token in token_text
    for phrase in [
        "does not promote candidate edges",
        "No canonical Atlas mutation occurred.",
        "No Genesis signing occurred.",
        "No public RC activation occurred.",
    ]:
        assert phrase in fix40_docs
    assert "..." not in fix40_docs
    assert "…" not in fix40_docs
