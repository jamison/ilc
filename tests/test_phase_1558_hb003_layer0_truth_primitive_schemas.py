"""Phase 1558 — HB-003 Layer 0 truth-primitive schema embedding tests.

PUBLIC_RC_EXCLUDE: phase_1558_private_runtime_selftest
PUBLIC_RC_EXCLUDE_REASON: Private pre-RC HB-003 selftest. Not a public RC artifact.
"""

from __future__ import annotations

import pytest

from ilc_core.bundle.layer0_protocol_bundle import (
    CDL_073_DEPENDENCY,
    LAYER0_TRUTH_PRIMITIVE_SCHEMA_SECTION_VERSION,
    TRUTH_PRIMITIVE_SCHEMA_TYPE_NAMES,
    build_truth_primitive_layer0_schemas,
    generate_layer0_protocol_bundle,
    verify_layer0_protocol_bundle,
)
from ilc_core.bundle.layer1_genesis_bundle import generate_layer1_genesis_bundle
from ilc_core.encoding.dag_cbor import validate_canonical_ilc_dag_cbor


def _base_layer0(*, include_truth_primitive_schemas: bool = False):
    return generate_layer0_protocol_bundle(
        bundle_id="phase1558-layer0",
        version="v0.1-private",
        schemas=[{"type_name": "Node", "required": ["node_id", "type"]}],
        parameters={"truth_primitives": 7},
        include_truth_primitive_schemas=include_truth_primitive_schemas,
    )


def test_truth_primitive_schema_builder_matches_cdl073_canon() -> None:
    schemas = build_truth_primitive_layer0_schemas()
    names = tuple(str(row["type_name"]) for row in schemas)

    assert names == TRUTH_PRIMITIVE_SCHEMA_TYPE_NAMES
    assert len(schemas) == 8
    assert all(row["cdl_dependency"] == CDL_073_DEPENDENCY for row in schemas)
    assert all(
        row["schema_version"] == LAYER0_TRUTH_PRIMITIVE_SCHEMA_SECTION_VERSION
        for row in schemas
    )
    assert {
        row["type_name"]
        for row in schemas
        if row["schema_kind"] == "truth_primitive_submission"
    } == {
        "truth_primitive.assert.truth",
        "truth_primitive.commit.epoch",
        "truth_primitive.contradict.assert",
        "truth_primitive.link.claim",
        "truth_primitive.refute.claim",
        "truth_primitive.revise.assert",
        "truth_primitive.validate.claim",
    }
    assert schemas[-1]["type_name"] == "system.genesis_authority_assertion"


def test_layer0_embedding_is_opt_in_and_changes_cidv1() -> None:
    base = _base_layer0(include_truth_primitive_schemas=False)
    embedded = _base_layer0(include_truth_primitive_schemas=True)
    embedded_again = _base_layer0(include_truth_primitive_schemas=True)

    assert base.cidv1 != embedded.cidv1
    assert base.sha256 != embedded.sha256
    assert embedded.cidv1 == embedded_again.cidv1
    assert embedded.sha256 == embedded_again.sha256
    assert verify_layer0_protocol_bundle(embedded) is True
    validate_canonical_ilc_dag_cbor(embedded.dag_cbor)


def test_layer0_embedded_schemas_are_sorted_with_existing_schema() -> None:
    embedded = _base_layer0(include_truth_primitive_schemas=True)
    names = [str(row["type_name"]) for row in embedded.schemas]

    assert names == sorted(names)
    assert "Node" in names
    assert "system.genesis_authority_assertion" in names
    assert "truth_primitive.assert.truth" in names
    assert "truth_primitive.commit.epoch" in names


def test_layer0_embedding_updates_layer1_reference_chain() -> None:
    layer0 = _base_layer0(include_truth_primitive_schemas=True)
    layer1 = generate_layer1_genesis_bundle(
        bundle_id="phase1558-layer1",
        layer0_sha256=layer0.sha256,
        layer0_cidv1=layer0.cidv1,
        seed_claims=[{"truth_primitive": "assert.truth", "claim_id": "seed-001"}],
        initial_agent_roster=[{"agent_id": "agent-a", "identity_anchor": "anchor-a"}],
        initial_shard_topology={"version": "v0.1-private", "shards": []},
        genesis_signing_key_refs=[{"purpose": "private_fixture", "key_ref": "key-a"}],
    )

    assert layer1.layer0_protocol_bundle_sha256 == layer0.sha256
    assert layer1.layer0_protocol_bundle_cidv1 == layer0.cidv1


def test_layer0_rejects_duplicate_schema_type_names_after_embedding() -> None:
    with pytest.raises(ValueError, match="layer0_bundle_duplicate_schema_type_name"):
        generate_layer0_protocol_bundle(
            bundle_id="phase1558-layer0",
            version="v0.1-private",
            schemas=[{"type_name": "truth_primitive.assert.truth"}],
            parameters={"truth_primitives": 7},
            include_truth_primitive_schemas=True,
        )


def test_layer0_rejects_non_bool_truth_primitive_schema_flag() -> None:
    with pytest.raises(
        ValueError,
        match="layer0_bundle_include_truth_primitive_schemas_must_be_bool",
    ):
        generate_layer0_protocol_bundle(
            bundle_id="phase1558-layer0",
            version="v0.1-private",
            schemas=[{"type_name": "Node"}],
            parameters={"truth_primitives": 7},
            include_truth_primitive_schemas="yes",  # type: ignore[arg-type]
        )
