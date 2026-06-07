"""Phase 1529p ADR-0035 type registry scaffold checks.

PUBLIC_RC_EXCLUDE: phase_1529p_private_type_registry_scaffold_selftest
PUBLIC_RC_EXCLUDE_REASON: Internal private-window runtime scaffold assertions. Not a public RC artifact.
"""

from __future__ import annotations

from pathlib import Path
from typing import get_args

import pytest

from ilc_core.encoding.dag_cbor import encode_dag_cbor
from ilc_core.graph import EpistemicGraph
from ilc_core.types import Node, NodeType
from ilc_core.bundle.type_registry import (
    ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED,
    CDL_097_AUTHORITY_REF,
    CDL_097_RATIFICATION_TOKEN,
    TypeRegistryCache,
    __all__ as TYPE_REGISTRY_EXPORTS,
    compute_type_definition_id,
    parse_type_definition_record,
    verify_type_definition_record,
    verify_type_definition_record_cbor,
)


def _base_record() -> dict[str, object]:
    record: dict[str, object] = {
        "definition_id": "",
        "node_type": "type_definition",
        "content_type": "type_definition",
        "definition_version": 1,
        "target_surface": "hyperedge_type",
        "target_value": "co_authorship",
        "scope": "co-authorship hyperedge semantics",
        "role_schema": {"roles": ["member"]},
        "decomposition_recipe": [
            {
                "primitive": "ASSERT",
                "role": "candidate governed statement",
                "input_ref": "target_value",
                "output_ref": "definition_id",
            }
        ],
        "irreducible": False,
        "membership_requirements": {"min_members": 2},
        "attribution_policy": "non_attributable",
        "type_level_dispute_path": "CDL amendment path",
        "instance_level_dispute_path": "epistemic review path citing definition node",
        "authority_ref": CDL_097_AUTHORITY_REF,
        "effective_epoch": 0,
        "snapshot_semantics": "definition valid at instance creation epoch",
    }
    record["definition_id"] = compute_type_definition_id(record)
    return record


def _with_recomputed_id(**updates: object) -> dict[str, object]:
    record = _base_record()
    record.update(updates)
    record["definition_id"] = compute_type_definition_id(record)
    return record


def _expect_token(record: dict[str, object], token: str) -> None:
    with pytest.raises(ValueError, match=f"^{token}$"):
        verify_type_definition_record(record)


def test_phase_1529p_guard_is_retained_and_node_type_parse_support_exists() -> None:
    assert ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED is True
    assert "type_definition" in get_args(NodeType)


def test_valid_record_verifies_parses_and_cbor_path_enforces_public_decode_path() -> None:
    record = _base_record()

    verify_type_definition_record(record)
    parsed = parse_type_definition_record(record)
    verify_type_definition_record_cbor(encode_dag_cbor(record))

    assert parsed.definition_id == record["definition_id"]
    assert parsed.node_type == "type_definition"
    assert parsed.authority_ref == CDL_097_AUTHORITY_REF


def test_type_definition_cbor_path_rejects_noncanonical_encoding() -> None:
    record = _base_record()
    canonical = encode_dag_cbor(record)
    noncanonical = canonical.replace(
        b"\x72definition_version\x01",
        b"\x72definition_version\x18\x01",
        1,
    )

    with pytest.raises(ValueError, match="Non-canonical ILC DAG-CBOR bytes"):
        verify_type_definition_record_cbor(noncanonical)


def test_phase_1525p_stable_error_tokens_are_implemented() -> None:
    missing = _base_record()
    del missing["target_surface"]
    _expect_token(missing, "type_definition_required_field_missing")

    _expect_token(
        _with_recomputed_id(node_type="claim"),
        "type_definition_node_type_mismatch",
    )
    _expect_token(
        _with_recomputed_id(content_type="application/json"),
        "type_definition_content_type_not_authorized",
    )

    bad_cid = _base_record()
    bad_cid["definition_id"] = _base_record()["definition_id"]
    bad_cid["target_value"] = "reuse"
    _expect_token(bad_cid, "type_definition_cid_mismatch")

    missing_authority = _base_record()
    del missing_authority["authority_ref"]
    _expect_token(missing_authority, "type_definition_missing_authority_ref")
    _expect_token(
        _with_recomputed_id(authority_ref="CDL-999:nope"),
        "type_definition_not_cdl_ratified",
    )
    _expect_token(
        _with_recomputed_id(attribution_policy="productive_credit"),
        "type_definition_attribution_policy_invalid",
    )
    _expect_token(
        _with_recomputed_id(decomposition_recipe=[]),
        "type_definition_decomposition_recipe_missing",
    )
    _expect_token(
        _with_recomputed_id(
            decomposition_recipe=[
                {
                    "primitive": "STAR_MAP",
                    "role": "candidate governed statement",
                    "input_ref": "target_value",
                    "output_ref": "definition_id",
                }
            ]
        ),
        "type_definition_unknown_truth_primitive",
    )
    _expect_token(
        _with_recomputed_id(irreducible=True, irreducible_reason=""),
        "type_definition_irreducible_reason_missing",
    )
    _expect_token(
        _with_recomputed_id(
            scope="",
            role_schema={},
            decomposition_recipe=[
                {
                    "primitive": "ASSERT",
                    "role": "candidate governed statement",
                    "input_ref": "target_value",
                    "output_ref": "definition_id",
                },
                {
                    "primitive": "ASSERT",
                    "role": "candidate governed statement",
                    "input_ref": "target_value",
                    "output_ref": "definition_id",
                },
            ],
        ),
        "type_definition_duplicate_recipe_scope_missing",
    )

    self_superseding = _base_record()
    self_superseding["supersedes_definition_id"] = self_superseding["definition_id"]
    self_superseding["definition_id"] = compute_type_definition_id(self_superseding)
    self_superseding["supersedes_definition_id"] = self_superseding["definition_id"]
    _expect_token(self_superseding, "type_definition_supersession_cycle")

    _expect_token(
        _with_recomputed_id(effective_epoch=-1),
        "type_definition_effective_epoch_before_authority",
    )


def test_authority_ref_mapping_is_accepted_only_for_cdl_097_token() -> None:
    verify_type_definition_record(
        _with_recomputed_id(
            authority_ref={
                "cdl": "CDL-097",
                "ratification_token": CDL_097_RATIFICATION_TOKEN,
            }
        )
    )
    _expect_token(
        _with_recomputed_id(
            authority_ref={
                "cdl": "CDL-097",
                "ratification_token": "wrong",
            }
        ),
        "type_definition_not_cdl_ratified",
    )


def test_type_definition_parse_support_is_not_authority_bearing_under_guard() -> None:
    record = _base_record()
    node = Node(
        id=str(record["definition_id"]),
        type="type_definition",
        content=record,
        agent_id="agent:test:adr0035",
        signature="candidate-signature",
        content_type="type_definition",
    )
    graph = EpistemicGraph()

    assert graph.add_node(node) is True
    assert graph.nodes[node.id] == node

    cache = TypeRegistryCache()
    state = cache.load_from_graph(graph)
    assert state.activated is False
    assert state.guard is True
    assert dict(state.definitions) == {}
    assert cache.is_authority_bearing_node(node) is False


def test_type_registry_module_records_public_rc_exclusion_and_guard_tokens() -> None:
    source = Path("ilc_core/bundle/type_registry.py").read_text()

    assert "PUBLIC_RC_EXCLUDE: adr_0035_type_registry_not_activated" in source
    assert "ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = True" in source
    assert "ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED" in TYPE_REGISTRY_EXPORTS
