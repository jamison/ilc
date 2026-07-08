import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix38_g10_graph_derived_test_frontier_report.md"
)
TOOL = ROOT / "tools/build_test_registry_frontier_report.py"
ARTIFACT = ROOT / "out/test_registry_frontier_report_1545p_fix38.json"
REPORT = ROOT / "docs/specs/ilc_test_registry_frontier_report_1545p_fix38_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"


TOKENS = {
    "graph_derived_test_frontier_report_committed_phase_1545p_fix38",
    "test_frontier_gap_categories_recorded_phase_1545p_fix38",
    "test_evidence_frontier_compared_phase_1545p_fix38",
    "manual_test_connectivity_annotations_recorded_phase_1545p_fix38",
    "stale_and_gated_test_frontier_recorded_phase_1545p_fix38",
    "test_frontier_report_no_authority_overclaim_phase_1545p_fix38",
    "public_path_remains_blocked_phase_1545p_fix38",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load(path: Path):
    return json.loads(read(path))


def test_fix38_prompt_validates() -> None:
    result = subprocess.run(
        [sys.executable, "tools/validate_phase_prompt.py", str(PROMPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_fix38_artifact_records_frontier_counts_and_manual_annotations() -> None:
    payload = load(ARTIFACT)
    fix33 = payload["fix33_file_frontier"]
    manual = payload["manual_connectivity_annotations"]
    all_frontier = payload["manual_connectivity_annotations_all_frontier_gaps"]

    assert payload["phase"] == "1545p-Fix38"
    assert payload["status"] == "pass"
    assert (
        payload["execution_scope"]
        == "report_only_no_test_execution_no_canonical_graph_mutation_candidate_overlay_only"
    )
    assert payload["graph_summary"]["graph_candidate_status"] == "unsigned_support_only_not_canonical"
    assert TOKENS.issubset(set(payload["output_tokens"]))
    assert fix33["local_test_python_file_count"] == 1472
    assert fix33["mapped_test_file_count"] == 1458
    assert fix33["missing_candidate_node_count"] == 14
    assert fix33["missing_tests_edge_count"] == 544
    assert fix33["dangling_tests_target_count"] == 0
    assert manual["manual_annotation_count"] == 14
    assert manual["manual_annotation_coverage"] == "14/14"
    assert manual["missing_candidate_nodes_remaining_unannotated_count"] == 0
    assert all_frontier["frontier_gap_file_count"] == 756
    assert all_frontier["frontier_gap_annotation_count"] == 756
    assert all_frontier["frontier_gap_annotation_coverage"] == "756/756"
    assert all_frontier["batch_count"] == 76
    assert all_frontier["batch_record_counts"]["batch_001_frontier_files_0001_0010"] == 10
    assert all_frontier["batch_record_counts"]["batch_076_frontier_files_0751_0756"] == 6
    assert payload["manual_edge_ledger_summary"]["ledger_annotation_count"] == 756
    assert payload["manual_edge_ledger_summary"]["combined_curated_edge_annotation_count"] == 756
    assert payload["curated_frontier_edge_batch"]["manual_edge_annotation_count"] == 756
    assert (
        payload["unified_candidate_summary"]["fix38_overlay_summary"][
            "curated_manual_edge_file_count"
        ]
        == 756
    )

    tranches = {item["annotation_tranche"] for item in manual["annotations"]}
    assert tranches == {
        "tranche_001_missing_candidate_nodes_01_10",
        "tranche_002_missing_candidate_nodes_tail_11_14",
    }

    for item in manual["annotations"]:
        assert item["annotation_source"] == "direct_read_by_codex_phase_1545p_fix38"
        assert item["proposed_node_kind"] == "test_file"
        assert item["promotion_status"] == "manual_annotation_for_graph_refresh_only"
        assert item["canonical_mutation_status"] == "not_mutated"
        assert item["proposed_candidate_node_id"].startswith("repo:file:")
        assert item["source_sha256"]
        assert "TESTS" in item["proposed_trace_roles"]
        assert item["proposed_tests_targets"]
        assert item["manual_read_summary"]

    for item in all_frontier["annotations"]:
        assert item["annotation_source"] == "direct_file_read_phase_1545p_fix38"
        assert item["annotation_batch"].startswith("batch_")
        assert item["proposed_node_kind"] == "test_file"
        assert item["gap_annotation_status"] == "manual_annotation_complete_graph_not_mutated"
        assert item["proposed_candidate_node_id"].startswith("repo:file:")
        assert item["proposed_tests_targets"]
        assert "TESTS" in item["proposed_trace_roles"]
        assert not any(str(target).startswith("/") for target in item["proposed_tests_targets"])
        assert item["repo_path"] not in item["proposed_tests_targets"]


def test_fix38_larger_frontiers_are_recorded_not_overclaimed_closed() -> None:
    payload = load(ARTIFACT)
    categories = payload["frontier_categories"]

    assert categories["missing_candidate_nodes"]["manual_annotation_coverage"] == "14/14"
    assert categories["missing_candidate_nodes"]["action"] == (
        "refresh_atlas_candidate_with_manual_test_file_nodes_and_TESTS_edges"
    )
    assert categories["missing_tests_edges"]["count"] == 544
    assert categories["missing_tests_edges"]["sample"]
    assert categories["missing_expected_authority_traces"]["count"] == 621
    assert categories["missing_expected_authority_traces"]["sample"]
    assert categories["function_nodes_without_inherited_targets"]["count"] == 3766
    assert categories["gated_or_non_default_tests"]["count"] == 426
    assert categories["git_history_dependent_hydration_exclusions"]["count"] == 2
    assert categories["dangling_tests_targets"]["count"] == 0
    assert payload["manual_connectivity_annotations_all_frontier_gaps"][
        "frontier_gap_annotation_coverage"
    ] == "756/756"


def test_fix38_compares_execution_evidence_without_running_tests() -> None:
    payload = load(ARTIFACT)

    assert payload["fix36_evidence_summary"]["selected_count"] == 8
    assert payload["fix36_evidence_summary"]["result_status_counts"] == {"passed": 8}
    assert payload["fix37_hydration_summary"]["selected_count"] == 6
    assert payload["fix37_hydration_summary"]["excluded_count"] == 2
    assert payload["fix37_hydration_summary"]["result_status_counts"] == {"passed": 6}
    assert "no_test_execution" in payload["non_claims"]
    assert "manual_annotations_are_review_queue_not_canonical_edges" in payload["non_claims"]


def test_fix38_runner_can_regenerate_deterministically(tmp_path: Path) -> None:
    json_out = tmp_path / "frontier.json"
    report = tmp_path / "frontier.md"
    candidate = tmp_path / "candidate.json"

    result = subprocess.run(
        [
            sys.executable,
            str(TOOL),
            "--json-out",
            str(json_out),
            "--report",
            str(report),
            "--candidate-out",
            str(candidate),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    regenerated = load(json_out)
    original = load(ARTIFACT)
    # HISTORICAL_SNAPSHOT: the manual edge ledger is append-only and now
    # includes later non-Fix38 schema rows. The runner must regenerate
    # deterministically and tolerate those rows, but the historical artifact
    # digest is no longer expected to be byte-identical.
    assert regenerated["report_digest"].startswith("test_frontier_report:")
    assert regenerated["manual_connectivity_annotations"]
    assert original["manual_connectivity_annotations"]
    assert regenerated["manual_connectivity_annotations_all_frontier_gaps"][
        "frontier_gap_annotation_coverage"
    ].endswith("/756")
    assert report.exists()
    assert candidate.exists()
    assert regenerated["unified_candidate_summary"]["candidate_digest"].startswith(
        "fix38_unified_candidate:"
    )


def test_fix38_report_status_and_planning_preserve_boundaries() -> None:
    combined = read(REPORT) + read(STATUS) + read(PLANNING_INDEX)

    for token in TOKENS:
        assert token in combined
    for phrase in [
        "Manual annotations are review-queue records, not canonical graph edges.",
        "The enriched graph input remains unsigned support-only and not canonical.",
        "This report does not grant authority, activation, eligibility, claimability, governance effect, or economic effect.",
        "No canonical graph mutation, edge promotion, signing, upload, publication, runtime activation, sidecar activation, ADR mutation, or CDL mutation occurred.",
    ]:
        assert phrase in combined


def test_fix38_docs_have_no_placeholder_ellipses() -> None:
    combined = read(REPORT) + read(PROMPT)

    assert "..." not in combined
    assert "…" not in combined
