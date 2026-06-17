from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/build_fix41a_authority_trace_frontier.py"
LEDGER = ROOT / "docs/specs/ilc_fix41a_authority_trace_frontier_ledger_v0.1.json"
REPORT = ROOT / "docs/specs/ilc_fix41a_authority_trace_frontier_report_v0.1.md"
CANDIDATE = ROOT / "out/atlas_research/genesis_atlas_enriched_candidate_fix41a.json"
COVERAGE = ROOT / "out/test_graph_coverage_1545p_fix41a.json"
COVERAGE_REPORT = ROOT / "docs/specs/ilc_test_graph_coverage_report_1545p_fix41a_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix41a_authority_trace_frontier_walkthrough.md"


TOKENS = {
    "fix41a_authority_trace_frontier_manual_audit_complete",
    "fix41a_role_specific_checker_hardening_committed",
    "fix41a_authority_trace_overlay_produced",
    "fix41a_coverage_rerun_complete",
    "fix41a_complete",
    "public_path_remains_blocked_phase_1545p_fix41a",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_fix41a_runner_can_regenerate_outputs(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate.json"
    ledger = tmp_path / "ledger.json"
    report = tmp_path / "report.md"
    coverage = tmp_path / "coverage.json"
    coverage_report = tmp_path / "coverage.md"

    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--candidate-out",
            str(candidate),
            "--ledger-out",
            str(ledger),
            "--report-out",
            str(report),
            "--coverage-json",
            str(coverage),
            "--coverage-report",
            str(coverage_report),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["integrity"] == "pass"
    assert payload["frontier_file_count"] == 57
    assert payload["new_candidate_trace_required_count"] == 7
    assert payload["added_candidate_edges"] == 21
    assert payload["coverage_missing_expected_authority_trace"] == 0
    assert load(coverage)["summary"]["phase"] == "1545p-Fix41a"
    assert "Fix41a Authority-Trace Frontier" in report.read_text(encoding="utf-8")


def test_fix41a_ledger_records_batches_and_new_trace_boundary() -> None:
    ledger = load(LEDGER)
    annotations = ledger["annotations"]
    statuses = {}
    for row in annotations:
        statuses[row["trace_status"]] = statuses.get(row["trace_status"], 0) + 1

    assert ledger["metadata"]["frontier_file_count"] == 57
    assert ledger["metadata"]["manual_batch_policy"] == "batches_of_10_plus_tail"
    assert statuses["existing_role_trace_checker_hardening_only"] == 50
    assert statuses["new_candidate_trace_required"] == 7
    assert all(row["batch_id"].startswith("manual_batch_") for row in annotations)
    assert all("manual_read_summary" in row for row in annotations)


def test_fix41a_candidate_integrity_and_edge_scope() -> None:
    candidate = load(CANDIDATE)
    merge = candidate["fix41a_merge_summary"]
    node_ids = {
        node.get("candidate_id") or node.get("node_id") or node.get("id") or node.get("vertex_id")
        for node in candidate["nodes"]
    }

    assert candidate["phase"] == "1545p-Fix41a"
    assert candidate["candidate_status"] == (
        "unsigned_support_only_not_canonical_fix41a_authority_trace_candidate"
    )
    assert merge["added_candidate_edges"] == 21
    assert merge["created_target_nodes"] == 19
    assert merge["added_edges_by_type"] == {
        "CLASSIFIED_BY": 6,
        "EVIDENCES": 6,
        "REFERENCES_AUTHORITY": 8,
        "TESTS": 1,
    }

    fix41a_edges = [
        edge for edge in candidate["edges"] if edge.get("source_phase") == "1545p-Fix41a"
    ]
    assert len(fix41a_edges) == 21
    assert {edge["edge_type"] for edge in fix41a_edges}.isdisjoint({"GOVERNS", "ATTESTATION"})
    assert all(edge["source"] in node_ids and edge["target"] in node_ids for edge in fix41a_edges)
    assert all(edge["promotion_status"] == "candidate_only_not_canonical" for edge in fix41a_edges)


def test_fix41a_coverage_closes_authority_trace_gap_only() -> None:
    coverage = load(COVERAGE)
    summary = coverage["summary"]

    assert summary["phase"] == "1545p-Fix41a"
    assert summary["authority_trace_policy"]["role_specific_trace_edges_are_evaluated_directly"]
    assert summary["gap_class_counts"].get("missing_expected_authority_trace", 0) == 0
    assert summary["authority_trace_expected_file_count"] == 1181
    assert summary["authority_trace_satisfied_file_count"] == (
        summary["authority_trace_expected_file_count"]
        - summary["missing_candidate_node_count"]
    )
    assert summary["missing_tests_edge_count"] == 0
    assert summary["missing_candidate_node_count"] == 9


def test_fix41a_docs_preserve_nonclaims_and_tokens() -> None:
    combined = REPORT.read_text(encoding="utf-8") + COVERAGE_REPORT.read_text(
        encoding="utf-8"
    ) + WALKTHROUGH.read_text(encoding="utf-8")
    token_text = combined + STATUS.read_text(encoding="utf-8")

    for token in TOKENS:
        assert token in token_text
    for phrase in [
        "No graph-selected tests were executed.",
        "No canonical Atlas mutation occurred.",
        "No edge promotion occurred.",
        "No Genesis signing occurred.",
        "No public RC activation occurred.",
        "candidate-only role-specific authority traces",
    ]:
        assert phrase in combined
    assert "..." not in combined
    assert "…" not in combined
