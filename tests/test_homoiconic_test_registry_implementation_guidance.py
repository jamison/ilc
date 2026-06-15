from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
GUIDANCE = ROOT / "docs/specs/ilc_homoiconic_test_registry_implementation_guidance_v0.1.md"
PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix32_g10_homoiconic_test_registry_contract.md"
)
FORWARD_PLAN = ROOT / "docs/specs/ilc_homoiconic_test_registry_forward_plan_v0.1.md"
WINDOW = (
    ROOT
    / "docs/specs/ilc_window_1576_1584_homoiconic_test_registry_candidate_phase_grouping_v0.1.md"
)
INVENTORY = ROOT / "docs/testing/test_inventory.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_guidance_records_required_pushback_and_no_authority_overclaim():
    text = _read(GUIDANCE)

    for required in [
        "AST parsing alone is not sufficient",
        "pytest --collect-only",
        "Passing tests are evidence, not authority",
        "Test nodes must survive pruning",
        "Private and environment-sensitive tests need gates",
        "Candidate Atlas nodes are not Genesis-signed until the signing gate",
    ]:
        assert required in text


def test_guidance_defines_concrete_phase_route():
    text = _read(GUIDANCE)

    for phase in [
        "Phase 1545p-Fix32: contract",
        "Phase 1545p-Fix33: test-node Atlas smoke audit",
        "Phase 1545p-Fix34: pytest collection to function-node candidates",
        "Phase 1545p-Fix35: canonical evidence envelope rehearsal",
        "Phase 1545p-Fix36: graph-derived test frontier report",
        "Window 1576-1584: pytest sidecar implementation window",
    ]:
        assert phase in text

    for node_kind in ["test_file", "test_function", "test_evidence_run"]:
        assert f'"node_kind": "{node_kind}"' in text


def test_sonnet_checker_feedback_is_recorded_with_correct_boundaries():
    combined = "\n".join([_read(GUIDANCE), _read(FORWARD_PLAN), _read(WINDOW)])

    for required in [
        "tools/check_test_graph_coverage.py",
        "genesis_atlas_enriched_candidate_1545p_fix27_prepass.json",
        "genesis_atlas_atom_candidates_1545p_fix26.jsonl",
        "genesis_atlas_semantic_prepass_fix27.jsonl",
        "coverage_input_scope: lower_information_fallback",
        "out/test_graph_coverage_phase_1577.json",
        "docs/specs/ilc_test_graph_coverage_report_1577_v0.1.md",
        "missing_candidate_node",
        "missing_tests_edge",
        "dangling_tests_target",
        "ready_for_function_collection",
        "--enforce-threshold",
        "report-first",
        "sort_keys=True",
        "allow_nan=False",
    ]:
        assert required in combined

    assert "REFERENCES_AUTHORITY` is not mandatory for every test" in _read(GUIDANCE)
    assert "role-specific authority traces are checked only where expected" in _read(FORWARD_PLAN)
    assert "test_graph_coverage_enriched_input_preferred_phase_1577" in _read(WINDOW)


def test_fix32_prompt_is_valid_and_non_authorizing():
    result = subprocess.run(
        [sys.executable, "tools/validate_phase_prompt.py", str(PROMPT)],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    text = _read(PROMPT)
    assert "This is a NON-SENSITIVE planning/spec phase" in text
    assert "No collector implementation" in text
    assert "No graph mutation" in text
    assert "No Genesis signing or node upload" in text
    assert "If MemPalace is used, direct-read every returned path." in text


def test_forward_plan_points_to_fix32_and_prompt_exists():
    text = _read(FORWARD_PLAN)

    assert "Phase 1545p-Fix32: Homoiconic Test Registry Contract" in text
    assert "Candidate Window 1576-1584: pytest sidecar implementation" in text
    assert PROMPT.exists()
    assert WINDOW.exists()


def test_sidecar_architecture_records_registry_then_hydration_then_plugin_deferral():
    combined = "\n".join([_read(GUIDANCE), _read(FORWARD_PLAN), _read(INVENTORY), _read(WINDOW)])

    for required in [
        "registry-mode executor",
        "graph-hydrated workspace",
        "native pytest collector/plugin",
        "native pytest plugin mode is deferred",
        "pytest <path>::<test_name>",
    ]:
        assert required in combined


def test_window_1576_1584_has_scopes_tokens_and_non_claims():
    text = _read(WINDOW)

    for phase in [str(number) for number in range(1576, 1585)]:
        assert f"Phase {phase}" in text

    for token in [
        "test_graph_coverage_checker_committed_phase_1577",
        "pytest_sidecar_registry_mode_scaffold_committed_phase_1579",
        "canonical_test_evidence_envelope_rehearsed_phase_1580",
        "pytest_sidecar_graph_hydrated_workspace_committed_phase_1581",
        "graph_derived_test_frontier_report_committed_phase_1582",
        "window_1576_1584_homoiconic_test_registry_closed_phase_1584",
    ]:
        assert token in text

    for non_claim in [
        "does not open Window 1576-1584",
        "public RC activation",
        "Genesis signing",
        "canonical Atlas mutation",
        "replacement of `pytest`",
        "ADR/CDL mutation",
    ]:
        assert non_claim in text

    assert "docs/specs/ilc_window_1576_1584_homoiconic_test_registry_candidate_phase_grouping_v0.1.md" in _read(
        PLANNING_INDEX
    )
