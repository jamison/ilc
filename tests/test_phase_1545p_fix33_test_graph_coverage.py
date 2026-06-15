import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "out/test_graph_coverage_1545p_fix33.json"
REPORT = ROOT / "docs/specs/ilc_test_graph_coverage_report_1545p_fix33_v0.1.md"
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix33_g10_test_node_atlas_smoke_audit.md"
TOOL = ROOT / "tools/check_test_graph_coverage.py"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix33_test_node_atlas_smoke_audit_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"


TOKENS = {
    "homoiconic_test_graph_coverage_checker_committed_phase_1545p_fix33",
    "homoiconic_test_file_node_mapping_audited_phase_1545p_fix33",
    "homoiconic_test_executor_gate_classification_recorded_phase_1545p_fix33",
    "homoiconic_test_missing_tests_edges_routed_phase_1545p_fix33",
    "homoiconic_test_graph_checker_report_only_phase_1545p_fix33",
    "public_path_remains_blocked_phase_1545p_fix33",
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_fix33_summary_uses_enriched_graph_and_report_first_mode():
    payload = _json(SUMMARY)
    summary = payload["summary"]

    assert summary["phase"] == "1545p-Fix33"
    assert summary["status"] == "pass"
    assert summary["coverage_input_scope"] == "enriched_graph"
    assert summary["graph_node_count"] >= 10035
    assert summary["graph_tests_edge_count"] >= 4998
    assert summary["report_first_mode"] is True
    assert summary["enforce_threshold_default"] is False
    assert TOKENS.issubset(set(summary["output_tokens"]))


def test_fix33_file_mapping_and_gap_classes_are_recorded():
    payload = _json(SUMMARY)
    summary = payload["summary"]

    assert summary["local_test_python_file_count"] >= 1400
    assert summary["mapped_test_file_count"] > 0
    assert summary["files_with_tests_edge_count"] > 0
    assert summary["missing_candidate_node_count"] > 0
    assert "missing_candidate_node" in summary["gap_class_counts"]
    assert "missing_tests_edge" in summary["gap_class_counts"]

    records = {record["repo_path"]: record for record in payload["file_records"]}
    assert (
        records["tests/test_phase_1545p_fix32_homoiconic_test_registry_contract.py"][
            "candidate_node_status"
        ]
        == "missing_candidate_node"
    )
    assert records["tests/test_phase_1426_soft_rc_gate_rerun.py"]["tests_edge_count"] > 0


def test_fix33_executor_profiles_preserve_pytest_gates():
    summary = _json(SUMMARY)["summary"]
    profiles = summary["executor_profile_counts"]

    assert profiles["default_local_pytest"] > 0
    assert profiles["historical_phase_snapshot"] > 0
    assert profiles["expensive_release_artifact"] > 0
    assert profiles["pytest_support_file"] >= 1
    assert (
        summary["authority_trace_policy"][
            "ordinary_runtime_tests_do_not_require_references_authority"
        ]
        is True
    )


def test_fix33_report_and_status_preserve_nonclaims():
    combined = _text(REPORT) + _text(WALKTHROUGH) + _text(STATUS) + _text(PLANNING_INDEX)

    for token in TOKENS:
        assert token in combined
    for phrase in [
        "No graph-selected tests were executed.",
        "No evidence envelope was generated.",
        "No canonical Atlas mutation occurred.",
        "No Genesis signing occurred.",
        "No public RC activation occurred.",
        "Ordinary runtime unit tests do not require `REFERENCES_AUTHORITY`.",
    ]:
        assert phrase in combined


def test_fix33_tool_and_prompt_encode_fallback_boundary():
    combined = _text(TOOL) + _text(PROMPT)

    assert "coverage_input_scope" in combined
    assert "lower_information_fallback" in combined
    assert "enforce-threshold" in combined
    assert "sort_keys=True" in combined
    assert "allow_nan=False" in combined


def test_fix33_docs_have_no_placeholder_ellipses():
    combined = _text(REPORT) + _text(WALKTHROUGH)

    assert "..." not in combined
    assert "…" not in combined
