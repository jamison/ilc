import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIGEST = ROOT / "docs/specs/ilc_pytest_function_node_collection_digest_1545p_fix34_v0.1.json"
REPORT = ROOT / "docs/specs/ilc_pytest_function_node_collection_report_1545p_fix34_v0.1.md"
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix34_g10_pytest_collection_function_nodes.md"
TOOL = ROOT / "tools/collect_pytest_function_nodes.py"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix34_pytest_function_nodes_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"


TOKENS = {
    "pytest_function_node_candidates_committed_phase_1545p_fix34",
    "pytest_nodeid_identity_grounded_phase_1545p_fix34",
    "ast_only_identity_rejected_phase_1545p_fix34",
    "pytest_function_edges_deferred_where_uncertain_phase_1545p_fix34",
    "pytest_collection_no_test_execution_phase_1545p_fix34",
    "public_path_remains_blocked_phase_1545p_fix34",
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_fix34_summary_records_pytest_collection_identity():
    payload = _json(DIGEST)
    summary = payload["summary"]

    assert summary["phase"] == "1545p-Fix34"
    assert summary["status"] == "pass"
    assert payload["full_artifact_git_policy"] == "local_reproducible_not_committed_large_artifact"
    assert payload["full_artifact_size_bytes"] > 40_000_000
    assert len(payload["full_artifact_sha256"]) == 64
    assert summary["coverage_input_scope"] in {"enriched_graph", "lower_information_fallback", "explicit_graph"}
    assert summary["collected_test_function_count"] > 1000
    assert summary["source_test_file_count"] > 500
    assert summary["collection_command"][2:5] == ["pytest", "--collect-only", "-q"]
    assert summary["identity_policy"]["pytest_nodeid_identity_source_required"] is True
    assert summary["identity_policy"]["ast_only_identity_rejected"] is True
    assert summary["edge_policy"]["file_level_tests_inheritance_is_provisional"] is True
    assert summary["function_nodes_with_fixture_metadata_count"] > 0
    assert summary["function_nodes_with_mark_metadata_count"] > 0
    assert TOKENS.issubset(set(summary["output_tokens"]))


def test_fix34_nodes_are_collected_function_candidates_not_ast_only():
    payload = _json(DIGEST)
    nodes = payload["sample_test_function_nodes"]

    assert nodes
    assert all(node["node_kind"] == "test_function" for node in nodes[:100])
    assert all(node["identity_source"] == "pytest_collect_only" for node in nodes[:100])
    assert all(node["pytest_nodeid"].startswith("tests/") for node in nodes[:100])
    assert all("::" in node["pytest_nodeid"] for node in nodes[:100])


def test_fix34_edges_are_candidate_only_and_defer_uncertain_coverage():
    payload = _json(DIGEST)
    summary = payload["summary"]
    edges = payload["sample_candidate_edges"]

    assert summary["candidate_edge_count"] > len(edges)
    assert summary["candidate_edge_type_counts"]["DERIVED_FROM"] > 0
    assert summary["candidate_edge_type_counts"]["TESTS"] > 0
    assert summary["candidate_edge_type_counts"]["REQUIRES_PROFILE"] > 0
    assert summary["candidate_edge_type_counts"]["USES_FIXTURE"] > 0
    assert all(edge["promotion_status"] == "candidate_only" for edge in edges[:500])
    assert summary["edge_policy"]["covers_symbol_candidate_count"] == 0

    deferred = payload["sample_deferred_records"]
    assert deferred
    assert any(
        item["deferred_reason"]
        == "function_specific_coverage_not_proven_by_file_level_inheritance"
        for item in deferred
    )


def test_fix34_report_status_and_planning_preserve_nonclaims():
    combined = _text(REPORT) + _text(WALKTHROUGH) + _text(STATUS) + _text(PLANNING_INDEX)

    for token in TOKENS:
        assert token in combined
    for phrase in [
        "No tests were executed.",
        "No graph-selected test runner was implemented.",
        "No evidence envelope was generated.",
        "No canonical Atlas mutation occurred.",
        "No Genesis signing occurred.",
        "No public RC activation occurred.",
        "File-level `TESTS` inheritance is provisional",
    ]:
        assert phrase in combined


def test_fix34_tool_and_prompt_encode_safety_boundaries():
    combined = _text(TOOL) + _text(PROMPT)

    assert "pytest --collect-only" in combined
    assert "timeout" in combined
    assert "sort_keys=True" in combined
    assert "allow_nan=False" in combined
    assert "Do not create `test_function` identity from AST alone" in combined
    assert "AST data is enrichment only and cannot create a candidate identity" in combined
    assert "no_test_execution" in combined


def test_fix34_docs_have_no_placeholder_ellipses():
    combined = _text(REPORT) + _text(WALKTHROUGH)

    assert "..." not in combined
    assert "…" not in combined
