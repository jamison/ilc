from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/specs/ilc_homoiconic_test_registry_contract_1545p_fix32_v0.1.md"
ROUTE = ROOT / "docs/specs/ilc_homoiconic_test_registry_implementation_route_1545p_fix32_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix32_homoiconic_test_registry_contract_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
TEST_INVENTORY = ROOT / "docs/testing/test_inventory.md"


TOKENS = {
    "homoiconic_test_registry_contract_committed_phase_1545p_fix32",
    "homoiconic_test_node_schema_recorded_phase_1545p_fix32",
    "homoiconic_test_graph_smoke_plan_recorded_phase_1545p_fix32",
    "homoiconic_test_evidence_envelope_schema_recorded_phase_1545p_fix32",
    "homoiconic_test_registry_not_runtime_executor_phase_1545p_fix32",
    "public_path_remains_blocked_phase_1545p_fix32",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_fix32_contract_and_tokens_exist():
    combined = _read(CONTRACT) + _read(WALKTHROUGH) + _read(STATUS)

    assert "Phase: 1545p-Fix32" in _read(CONTRACT)
    assert TOKENS.issubset(set(token for token in TOKENS if token in combined))


def test_fix32_declares_test_node_schemas_and_pytest_identity_boundary():
    text = _read(CONTRACT)

    for required in [
        '"node_kind": "test_file"',
        '"node_kind": "test_function"',
        '"node_kind": "test_evidence_run"',
        '"pytest_nodeid"',
        '"collection_source": "pytest_collect_only"',
        "AST alone must not define the function-level identity",
        "pytest_nodeid` identity must be grounded in real `pytest --collect-only`",
    ]:
        assert required in text


def test_fix32_edge_vocabulary_and_executor_profiles_are_gated():
    text = _read(CONTRACT)

    for edge_role in [
        "`SOURCE_TREE_MEMBER`",
        "`DERIVED_FROM`",
        "`TESTS`",
        "`COVERS_SYMBOL`",
        "`USES_FIXTURE`",
        "`REQUIRES_PROFILE`",
        "`SKIPPED_BY_DEFAULT_UNLESS`",
        "`PRODUCES_EVIDENCE`",
        "`EVIDENCES`",
        "`SUPERSEDES`",
    ]:
        assert edge_role in text

    for profile in [
        "`default_local_pytest`",
        "`historical_phase_snapshot`",
        "`expensive_release_artifact`",
        "`sensitive_phase_selftest`",
        "`private_local_only`",
        "`live_network_vps_gated`",
        "`graph_hydrated_workspace`",
    ]:
        assert profile in text

    assert "Default graph-runner queries must return only nodes in `default_local_pytest`" in text


def test_fix32_preserves_authority_and_activation_non_claims():
    text = _read(CONTRACT) + _read(ROUTE) + _read(WALKTHROUGH)

    for non_claim in [
        "A passing test is evidence under its declared scope. It is not authority.",
        "No canonical Atlas mutation occurred",
        "No Genesis signing occurred",
        "No public RC activation occurred",
        "No ADR or CDL mutation occurred",
        "No runtime, economic, sidecar, ADR, or CDL mutation occurred",
    ]:
        assert non_claim in text


def test_fix32_successor_route_names_fix33_through_fix38():
    text = _read(ROUTE)

    for successor in [
        "Phase 1545p-Fix33: Test-Node Atlas Smoke Audit",
        "Phase 1545p-Fix34: Pytest Collection To Function-Node Candidates",
        "Phase 1545p-Fix35: Registry-Mode Pytest Sidecar Scaffold",
        "Phase 1545p-Fix36: Canonical Evidence Envelope Rehearsal",
        "Phase 1545p-Fix37: Graph-Hydrated Workspace Rehearsal",
        "Phase 1545p-Fix38: Graph-Derived Test Frontier Report",
    ]:
        assert successor in text

    assert "coverage_input_scope: lower_information_fallback" in text
    assert "enriched_candidate_1545p_fix27_prepass.json" in text


def test_fix32_contract_section_numbers_are_sequential_after_fix37_audit():
    text = _read(CONTRACT)

    assert "## 12. Fix38 Frontier Report Contract" in text
    assert "## 13. Acceptance Criteria For Later Implementation" in text
    assert "## 14. Non-Claims" in text
    assert "## 12. Non-Claims" not in text


def test_fix32_planning_surfaces_reference_contract_and_route():
    contract = "docs/specs/ilc_homoiconic_test_registry_contract_1545p_fix32_v0.1.md"
    route = "docs/specs/ilc_homoiconic_test_registry_implementation_route_1545p_fix32_v0.1.md"

    for path in [PLANNING_INDEX, TEST_INVENTORY]:
        text = _read(path)
        assert contract in text
        assert route in text


def test_fix32_docs_have_no_placeholder_ellipses():
    combined = _read(CONTRACT) + _read(ROUTE) + _read(WALKTHROUGH)

    assert "..." not in combined
    assert "…" not in combined
