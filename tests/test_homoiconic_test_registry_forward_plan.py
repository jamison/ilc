from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/specs/ilc_homoiconic_test_registry_forward_plan_v0.1.md"
INVENTORY = ROOT / "docs/testing/test_inventory.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"


def test_homoiconic_test_registry_forward_plan_exists_and_preserves_pytest_executor():
    text = SPEC.read_text(encoding="utf-8")

    assert "`pytest` should remain an executor" in text
    assert "It should not remain the only registry" in text
    assert "filesystem model:" in text
    assert "homoiconic model:" in text


def test_homoiconic_test_registry_declares_file_function_and_evidence_nodes():
    text = SPEC.read_text(encoding="utf-8")

    for required in [
        'node_kind: "test_file"',
        'node_kind: "test_function"',
        'node_kind: "test_evidence_run"',
        "pytest_nodeid",
        "expected_invariants",
        "environment_gates",
        "non_claim_boundaries",
    ]:
        assert required in text


def test_homoiconic_test_registry_edge_vocabulary_is_role_specific():
    text = SPEC.read_text(encoding="utf-8")

    for edge_role in [
        "`TESTS`",
        "`COVERS_SYMBOL`",
        "`EVIDENCES`",
        "`REQUIRES_PROFILE`",
        "`SKIPPED_BY_DEFAULT_UNLESS`",
        "`PRODUCES_EVIDENCE`",
        "`CLOSES`",
        "`REGRESSES`",
        "`SUPERSEDES`",
    ]:
        assert edge_role in text


def test_homoiconic_test_registry_is_non_authorizing_forward_plan():
    text = SPEC.read_text(encoding="utf-8")

    for non_claim in [
        "does not execute a phase",
        "authorize public RC",
        "authorize Genesis signing",
        "upload nodes",
        "mutate ADR/CDL state",
        "replacement of `pytest` as an executor",
    ]:
        assert non_claim in text


def test_test_inventory_and_planning_index_point_to_forward_plan():
    spec_path = "docs/specs/ilc_homoiconic_test_registry_forward_plan_v0.1.md"

    assert spec_path in INVENTORY.read_text(encoding="utf-8")
    assert spec_path in PLANNING_INDEX.read_text(encoding="utf-8")
    assert "Phase 1545p-Fix32: Homoiconic Test Registry Contract" in PLANNING_INDEX.read_text(
        encoding="utf-8"
    )
