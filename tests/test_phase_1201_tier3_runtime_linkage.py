from pathlib import Path

import pytest

from ilc_core.node.tier3_runtime_linkage_runtime import (
    RUNTIME_NODE_REQUIRED_FIELDS,
    SCHEMA_NODE_REQUIRED_FIELDS,
    TIER3_RUNTIME_LINKAGE_VERSION,
    serialize_tier3_record,
    validate_runtime_node,
    validate_schema_node,
)


ROOT = Path(__file__).resolve().parents[1]
ROOT_HASH = "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"


def _valid_schema_node() -> dict:
    return {
        "schema_id": "schema:tier3-runtime-linkage",
        "schema_version": "v0.1",
        "schema_digest": "sha256:abc123",
        "schema_artifact_ref": "docs/specs/schema_tier3_runtime_linkage_v0.1.md",
        "authority_ref": "adr:0020",
        "lineage_ref": "genesis:v0.1",
        "status": "accepted",
    }


def _valid_runtime_node() -> dict:
    return {
        "runtime_id": "runtime:tier3-runtime-linkage",
        "runtime_version": TIER3_RUNTIME_LINKAGE_VERSION,
        "implementation_ref": "ilc_core/node/tier3_runtime_linkage_runtime.py",
        "schema_refs": ["schema:tier3-runtime-linkage"],
        "cdl_dependency_refs": ["CDL-085"],
        "adr_dependency_refs": ["ADR-0020"],
        "test_evidence_refs": ["tests/test_phase_1201_tier3_runtime_linkage.py"],
        "lineage_ref": "genesis:v0.1",
        "status": "active",
    }


def test_schema_node_valid_passes() -> None:
    assert validate_schema_node(_valid_schema_node()) == _valid_schema_node()


@pytest.mark.parametrize("field", SCHEMA_NODE_REQUIRED_FIELDS)
def test_schema_node_missing_required_field(field: str) -> None:
    record = _valid_schema_node()
    del record[field]
    with pytest.raises(ValueError, match=f"tier3_schema_node_missing_field:{field}"):
        validate_schema_node(record)


def test_schema_node_invalid_status() -> None:
    record = _valid_schema_node()
    record["status"] = "active"
    with pytest.raises(ValueError, match="tier3_schema_node_invalid_status"):
        validate_schema_node(record)


def test_schema_node_rejects_empty_required_string() -> None:
    record = _valid_schema_node()
    record["schema_digest"] = ""
    with pytest.raises(ValueError, match="tier3_schema_node_invalid_field:schema_digest"):
        validate_schema_node(record)


def test_runtime_node_valid_passes() -> None:
    assert validate_runtime_node(_valid_runtime_node()) == _valid_runtime_node()


@pytest.mark.parametrize("field", RUNTIME_NODE_REQUIRED_FIELDS)
def test_runtime_node_missing_required_field(field: str) -> None:
    record = _valid_runtime_node()
    del record[field]
    with pytest.raises(ValueError, match=f"tier3_runtime_node_missing_field:{field}"):
        validate_runtime_node(record)


def test_runtime_node_schema_refs_must_be_nonempty() -> None:
    record = _valid_runtime_node()
    record["schema_refs"] = []
    with pytest.raises(ValueError, match="tier3_runtime_node_schema_refs_empty"):
        validate_runtime_node(record)


def test_runtime_node_invalid_status() -> None:
    record = _valid_runtime_node()
    record["status"] = "ratified"
    with pytest.raises(ValueError, match="tier3_runtime_node_invalid_status"):
        validate_runtime_node(record)


def test_runtime_node_rejects_non_string_list_items() -> None:
    record = _valid_runtime_node()
    record["schema_refs"] = ["schema:tier3-runtime-linkage", 123]
    with pytest.raises(ValueError, match="tier3_runtime_node_invalid_field:schema_refs"):
        validate_runtime_node(record)


def test_tier3_serialization_deterministic() -> None:
    first = serialize_tier3_record({"b": 2, "a": {"z": "last", "m": "middle"}})
    second = serialize_tier3_record({"a": {"m": "middle", "z": "last"}, "b": 2})
    assert first == second
    assert first == '{"a":{"m":"middle","z":"last"},"b":2}'


def test_tier3_serialization_rejects_float_values() -> None:
    with pytest.raises(ValueError, match="tier3_float_not_allowed:tier3_record.weight"):
        serialize_tier3_record({"weight": 1.0})


def test_tier3_runtime_version_token() -> None:
    assert TIER3_RUNTIME_LINKAGE_VERSION == "tier3_runtime_linkage_runtime_1201.v0.1"
    assert "1201" in TIER3_RUNTIME_LINKAGE_VERSION


def test_no_signed_genesis_mutation() -> None:
    sequence_lock = (
        ROOT / "docs/specs/ilc_phase_1200_1208_sequence_lock_v0.1.md"
    ).read_text(encoding="utf-8")
    assert ROOT_HASH in sequence_lock
