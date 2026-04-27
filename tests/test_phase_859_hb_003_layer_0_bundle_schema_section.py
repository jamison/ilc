"""Phase 859 tests — HB-003 Layer 0 bundle schema section.

Tests cover CDL-073 Evidence items 4 and 6 (partial):
  Evidence 4 — Layer 0 bundle schema section artifact exists and is machine-parseable
  Evidence 6 — test coverage (this file)

The schema section is at:
  docs/specs/ilc_layer_0_bundle_schema_section_v0.1.json

A new participant can load this file without a compiled binary and extract:
  - the seven truth primitive identifiers
  - required fields for each
  - edge types produced by each
  - COSE Sign1 algorithm requirements
  - DAG-CBOR canonical encoding rules
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

# Path to the Layer 0 bundle schema section artifact
_SCHEMA_PATH = (
    Path(__file__).parent.parent
    / "docs" / "specs" / "ilc_layer_0_bundle_schema_section_v0.1.json"
)

_EXPECTED_PRIMITIVES = {
    "assert.truth",
    "validate.claim",
    "contradict.assert",
    "refute.claim",
    "revise.assert",
    "link.claim",
    "commit.epoch",
}

_EXPECTED_EDGE_TYPES = {
    "asserted_by", "extends", "validated_by", "contradicts",
    "refuted_by", "supported_by", "revision_of", "revised_by",
    "cites", "elaborates", "contrasts", "instantiates", "generalizes",
    "finalizes",
}


@pytest.fixture(scope="module")
def schema() -> dict:
    """Load the Layer 0 bundle schema section as a plain dict."""
    assert _SCHEMA_PATH.exists(), (
        f"Layer 0 bundle schema section not found at {_SCHEMA_PATH}"
    )
    with _SCHEMA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Evidence 4 — file exists and is machine-parseable
# ---------------------------------------------------------------------------

def test_layer_0_bundle_schema_section_file_exists():
    """CDL-073 Evidence 4: the schema section artifact exists."""
    assert _SCHEMA_PATH.exists(), f"Schema section not found: {_SCHEMA_PATH}"


def test_layer_0_bundle_schema_section_is_machine_parseable(schema):
    """CDL-073 Evidence 4: the artifact parses as a plain dict without compiled binary."""
    assert isinstance(schema, dict)


def test_layer_0_bundle_schema_section_meta_fields(schema):
    """Schema section carries required _meta fields."""
    meta = schema.get("_meta", {})
    assert meta.get("kind") == "ilc_layer_0_bundle_schema_section"
    assert meta.get("schema_section_version") == 1
    assert "cdl_073" in meta.get("cdl_dependency", "")
    assert meta.get("token") == "hb_003_layer_0_bundle_schema_section"


def test_layer_0_bundle_schema_section_contains_all_seven_primitives(schema):
    """CDL-073 Evidence 4: all seven truth primitives are defined."""
    primitives = schema.get("primitives", {})
    assert set(primitives.keys()) == _EXPECTED_PRIMITIVES


def test_layer_0_bundle_schema_section_each_primitive_has_required_fields(schema):
    """Each primitive definition has required_payload_fields."""
    primitives = schema.get("primitives", {})
    for name in _EXPECTED_PRIMITIVES:
        p = primitives.get(name, {})
        assert "required_payload_fields" in p, (
            f"Primitive {name!r} missing required_payload_fields"
        )
        assert "graph_output" in p, f"Primitive {name!r} missing graph_output"


def test_layer_0_bundle_schema_section_each_primitive_has_semantic(schema):
    """Each primitive definition has a semantic description."""
    primitives = schema.get("primitives", {})
    for name in _EXPECTED_PRIMITIVES:
        p = primitives.get(name, {})
        assert "semantic" in p, f"Primitive {name!r} missing semantic description"
        assert isinstance(p["semantic"], str) and p["semantic"]


def test_layer_0_bundle_schema_section_commit_epoch_is_consensus_only(schema):
    """commit.epoch must be marked consensus_layer_only."""
    commit_epoch = schema["primitives"]["commit.epoch"]
    assert commit_epoch.get("authorization") == "consensus_layer_only"


def test_layer_0_bundle_schema_section_edge_type_registry_complete(schema):
    """Edge type registry lists all expected edge types."""
    registry = schema.get("edge_type_registry", {})
    edges = registry.get("edges", [])
    edge_types_in_registry = {e["type"] for e in edges}
    assert edge_types_in_registry == _EXPECTED_EDGE_TYPES


def test_layer_0_bundle_schema_section_cose_sign1_section_present(schema):
    """COSE Sign1 requirements section is present and includes both algorithms."""
    cose = schema.get("cose_sign1", {})
    assert "default_algorithm" in cose
    assert cose["default_algorithm"]["label"] == -8       # Ed25519
    assert "genesis_and_consensus_algorithm" in cose
    assert cose["genesis_and_consensus_algorithm"]["label"] == -65  # ML-DSA-65


def test_layer_0_bundle_schema_section_dag_cbor_rules_present(schema):
    """DAG-CBOR canonical encoding rules section is present."""
    rules = schema.get("dag_cbor_canonical_rules", {})
    assert "map_key_ordering" in rules
    assert "no_float" in rules
    assert "decimal_amounts" in rules


def test_layer_0_bundle_schema_section_submission_envelope_present(schema):
    """Common submission envelope is specified."""
    envelope = schema.get("submission_envelope", {})
    required = envelope.get("required_fields", {})
    assert "v" in required
    assert "primitive" in required
    assert "agent_id" in required
    assert "epoch" in required
    assert "payload" in required
    assert "sig" in required


def test_layer_0_bundle_schema_section_primitive_identifiers_match_envelope(schema):
    """Primitive identifiers in the envelope allowed_values match the primitives section."""
    envelope = schema.get("submission_envelope", {})
    allowed = set(envelope["required_fields"]["primitive"]["allowed_values"])
    assert allowed == _EXPECTED_PRIMITIVES


def test_layer_0_bundle_schema_section_assert_truth_parent_node_ids_required(schema):
    """assert.truth requires parent_node_ids (may be empty array)."""
    fields = schema["primitives"]["assert.truth"]["required_payload_fields"]
    assert "parent_node_ids" in fields


def test_layer_0_bundle_schema_section_refute_claim_falsifiable_constraint(schema):
    """refute.claim documents has_falsifiable_test must be true."""
    criterion = schema["primitives"]["refute.claim"]["required_payload_fields"]["refutation_criterion"]
    assert "has_falsifiable_test" in criterion.get("constraint", "")


def test_layer_0_bundle_schema_section_genesis_authority_assertion_in_known_primitive_types(schema):
    """genesis_authority_assertion appears in assert.truth known_values."""
    assert_truth = schema["primitives"]["assert.truth"]
    known = assert_truth["required_payload_fields"]["primitive_type"].get("known_values", [])
    assert "genesis_authority_assertion" in known


def test_layer_0_bundle_schema_section_parseable_without_ilc_imports(schema):
    """The schema is a pure JSON structure — no ILC-specific objects required to parse it.
    This test proves the HB-003 property: a new participant can read this without
    a compiled binary or ILC Python package.
    """
    # Walk the entire schema and confirm all values are JSON-native types
    _assert_json_native(schema)


def _assert_json_native(obj, path: str = "root") -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            assert isinstance(k, str), f"Non-string key at {path}: {k!r}"
            _assert_json_native(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _assert_json_native(item, f"{path}[{i}]")
    elif not isinstance(obj, (str, int, float, bool, type(None))):
        raise AssertionError(
            f"Non-JSON-native value at {path}: {type(obj)} = {obj!r}"
        )
