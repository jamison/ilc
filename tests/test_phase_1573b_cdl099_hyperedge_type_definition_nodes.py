import json
from dataclasses import fields
from pathlib import Path

from ilc_core.bundle.type_registry import (
    ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED,
    CDL_097_RATIFICATION_TOKEN,
    compute_type_definition_id,
    verify_type_definition_record,
)
from ilc_core.types import HyperEdge


ROOT = Path(__file__).resolve().parents[1]
SPEC_ROOT = ROOT / "docs" / "specs"

DEFINITION_PATHS = {
    "panel": SPEC_ROOT / "ilc_cdl_099_definition_node_panel_v0.1.json",
    "co_authorship": SPEC_ROOT / "ilc_cdl_099_definition_node_co_authorship_v0.1.json",
    "refutation_coalition": SPEC_ROOT / "ilc_cdl_099_definition_node_refutation_coalition_v0.1.json",
    "epoch_boundary": SPEC_ROOT / "ilc_cdl_099_definition_node_epoch_boundary_v0.1.json",
    "jury_verdict": SPEC_ROOT / "ilc_cdl_099_definition_node_jury_verdict_v0.1.json",
}

EXPECTED_TYPES = frozenset(DEFINITION_PATHS)


def _load_definition(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    assert isinstance(data, dict)
    return data


def _load_all_definitions() -> dict[str, dict[str, object]]:
    return {name: _load_definition(path) for name, path in DEFINITION_PATHS.items()}


def test_cdl099_ratifies_exactly_five_initial_hyperedge_type_records() -> None:
    records = _load_all_definitions()
    discovered_paths = {
        path.name for path in SPEC_ROOT.glob("ilc_cdl_099_definition_node_*.json")
    }

    assert set(records) == EXPECTED_TYPES
    assert discovered_paths == {path.name for path in DEFINITION_PATHS.values()}
    assert {str(record["hyperedge_type"]) for record in records.values()} == EXPECTED_TYPES
    assert "reuse" not in records
    assert "carry_forward" not in records


def test_cdl099_definition_records_verify_against_default_off_type_registry() -> None:
    for hyperedge_type, record in _load_all_definitions().items():
        verify_type_definition_record(record)
        assert compute_type_definition_id(record) == record["definition_id"]
        assert record["node_type"] == "type_definition"
        assert record["content_type"] == "type_definition"
        assert record["target_surface"] == "HyperEdge.hyperedge_type"
        assert record["target_value"] == hyperedge_type
        assert record["hyperedge_type"] == hyperedge_type
        assert record["cdl_authority"] == "cdl_099"
        assert record["phase"] == "1573b"
        assert record["attribution_policy"] == "non_attributable"
        assert record["snapshot_semantics"] is True
        assert record["authority_ref"] == {
            "cdl": "CDL-097",
            "ratification_token": CDL_097_RATIFICATION_TOKEN,
        }


def test_epoch_boundary_is_the_only_irreducible_cdl099_definition() -> None:
    records = _load_all_definitions()

    for hyperedge_type, record in records.items():
        if hyperedge_type == "epoch_boundary":
            assert record["irreducible"] is True
            assert record["decomposition_recipe"] == []
            assert "commit.epoch" in str(record["irreducible_reason"])
            assert "commit.epoch" in str(record["decomposition_recipe_text"])
        else:
            assert record["irreducible"] is False
            recipe = record["decomposition_recipe"]
            assert isinstance(recipe, list)
            assert len(recipe) > 0


def test_jury_verdict_decomposition_is_resolved_without_closing_cdl100() -> None:
    record = _load_definition(DEFINITION_PATHS["jury_verdict"])

    assert record["irreducible"] is False
    assert record["decomposition_recipe_text"] == (
        "validate.claim compose link.claim compose commit.epoch"
    )
    assert "confirmed_reducible" in str(record["decomposition_resolution"])

    role_schema = record["role_schema"]
    assert isinstance(role_schema, dict)
    assert "verdict_outcome" in role_schema
    assert "finality_path" in role_schema
    assert "jury_panel" in role_schema

    cdl_register = (SPEC_ROOT / "ilc_constitutional_decision_log_v0.1.md").read_text(
        encoding="utf-8"
    )
    assert "| CDL-100 |" in cdl_register
    assert (
        "| planned_not_opened |" in cdl_register
        or "| ratified | phase_1573c | cdl_100_ratified |" in cdl_register
    )


def test_cdl099_does_not_activate_type_registry_or_runtime_migration() -> None:
    assert ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED is True

    hyperedge_type_field = next(
        field for field in fields(HyperEdge) if field.name == "hyperedge_type"
    )
    assert hyperedge_type_field.type in (str, "str")


def test_cdl099_register_status_evidence_and_status_tokens_are_precise() -> None:
    cdl_register = (SPEC_ROOT / "ilc_constitutional_decision_log_v0.1.md").read_text(
        encoding="utf-8"
    )
    evidence = (
        SPEC_ROOT
        / "ilc_cdl_099_hyperedge_type_definition_nodes_ratification_evidence_1573b_v0.1.md"
    ).read_text(encoding="utf-8")
    status = (ROOT / "docs" / "phases" / "STATUS.md").read_text(encoding="utf-8")

    assert "| CDL-099 |" in cdl_register
    assert "| ratified | phase_1573b | cdl_099_ratified |" in cdl_register
    assert "definition_node_instances_s8_ratified" in cdl_register
    assert "ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED=True" in cdl_register

    assert "cdl_099_ratified" in evidence
    assert "definition_node_instances_s8_ratified" in evidence
    assert "cdl_100_type_dispute_procedure_required_phase_1573c" in evidence

    for token in (
        "cdl_099_opened",
        "cdl_099_ratified",
        "definition_node_instances_s8_ratified",
        "adr_0035_type_registry_not_activated_confirmed_phase_1573b",
        "public_path_remains_blocked_phase_1573b",
    ):
        assert token in status
