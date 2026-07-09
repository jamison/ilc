# SPDX-License-Identifier: AGPL-3.0-only
"""PUBLIC_RC_EXCLUDE: adr_0035_type_registry_not_activated
PUBLIC_RC_EXCLUDE_REASON: Default-off ADR-0035 type registry scaffold. Guard retained
until separate production activation authority granted after CDL-097 ratification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

from ilc_core.crypto.cbor_canonical import MAX_CANONICAL_CBOR_INPUT_BYTES
from ilc_core.encoding.cidv1 import node_id_from_obj, parse_nodeid_strict
from ilc_core.encoding.dag_cbor import (
    decode_dag_cbor_strict,
    validate_canonical_ilc_dag_cbor,
)
from ilc_core.private_json_guardrails import normalize_json_value, reject_float

ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = True  # guard retained until production activation phase
CDL_097_RATIFICATION_TOKEN = "cdl_097_ratified_phase_1528p"
CDL_097_AUTHORITY_REF = f"CDL-097:{CDL_097_RATIFICATION_TOKEN}"

_REQUIRED_FIELDS = frozenset(
    {
        "definition_id",
        "node_type",
        "content_type",
        "definition_version",
        "target_surface",
        "target_value",
        "scope",
        "irreducible",
        "membership_requirements",
        "attribution_policy",
        "type_level_dispute_path",
        "instance_level_dispute_path",
        "authority_ref",
        "effective_epoch",
        "snapshot_semantics",
    }
)
_KNOWN_TRUTH_PRIMITIVES = frozenset(
    {
        "ASSERT",
        "VALIDATE",
        "CONTRADICT",
        "REFUTE",
        "REVISE",
        "LINK",
        "COMMIT_EPOCH",
        "assert.truth",
        "validate.claim",
        "contradict.assert",
        "refute.claim",
        "revise.assert",
        "link.claim",
        "commit.epoch",
    }
)
_VALID_AUTHORITY_REFS = frozenset(
    {
        "CDL-097",
        CDL_097_RATIFICATION_TOKEN,
        CDL_097_AUTHORITY_REF,
    }
)


@dataclass(frozen=True)
class TypeDefinitionRecord:
    definition_id: str
    node_type: str
    content_type: str
    definition_version: object
    target_surface: str
    target_value: str
    scope: object
    role_schema: Mapping[str, object] | None
    decomposition_recipe: tuple[Mapping[str, object], ...]
    irreducible: bool
    irreducible_reason: str | None
    membership_requirements: Mapping[str, object]
    attribution_policy: str
    type_level_dispute_path: str
    instance_level_dispute_path: str
    authority_ref: object
    effective_epoch: int
    supersedes_definition_id: str | None
    snapshot_semantics: str


@dataclass(frozen=True)
class TypeRegistryCacheState:
    activated: bool
    guard: bool
    authority_token: str
    definitions: Mapping[str, TypeDefinitionRecord] = field(
        default_factory=lambda: MappingProxyType({})
    )


class TypeRegistryCache:
    """Default-off startup cache facade for future ADR-0035 definition loading."""

    def startup_state(self) -> TypeRegistryCacheState:
        return TypeRegistryCacheState(
            activated=False,
            guard=ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED,
            authority_token=CDL_097_RATIFICATION_TOKEN,
        )

    def load_from_records(self, _records: object = None) -> TypeRegistryCacheState:
        return self.startup_state()

    def load_from_graph(self, _graph: object = None) -> TypeRegistryCacheState:
        return self.startup_state()

    def is_authority_bearing_node(self, _node: object) -> bool:
        if ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED:
            return False
        return False


def compute_type_definition_id(record: Mapping[str, object]) -> str:
    """Compute the CIDv1 over the canonical definition payload."""
    reject_float(record, "type_definition_cid_mismatch")
    payload = _definition_id_payload(record)
    try:
        return node_id_from_obj(payload)
    except (TypeError, ValueError) as exc:
        raise ValueError("type_definition_cid_mismatch") from exc


def parse_type_definition_record(record: Mapping[str, object]) -> TypeDefinitionRecord:
    verify_type_definition_record(record)
    recipe = record.get("decomposition_recipe", ())
    if not isinstance(recipe, list):
        recipe = []
    normalized_recipe = tuple(item for item in recipe if isinstance(item, Mapping))
    role_schema = record.get("role_schema")
    supersedes = record.get("supersedes_definition_id")
    irreducible_reason = record.get("irreducible_reason")
    return TypeDefinitionRecord(
        definition_id=str(record["definition_id"]),
        node_type=str(record["node_type"]),
        content_type=str(record["content_type"]),
        definition_version=record["definition_version"],
        target_surface=str(record["target_surface"]),
        target_value=str(record["target_value"]),
        scope=record["scope"],
        role_schema=role_schema if isinstance(role_schema, Mapping) else None,
        decomposition_recipe=normalized_recipe,
        irreducible=bool(record["irreducible"]),
        irreducible_reason=irreducible_reason if isinstance(irreducible_reason, str) else None,
        membership_requirements=record["membership_requirements"],  # type: ignore[arg-type]
        attribution_policy=str(record["attribution_policy"]),
        type_level_dispute_path=str(record["type_level_dispute_path"]),
        instance_level_dispute_path=str(record["instance_level_dispute_path"]),
        authority_ref=record["authority_ref"],
        effective_epoch=record["effective_epoch"],  # type: ignore[arg-type]
        supersedes_definition_id=supersedes if isinstance(supersedes, str) else None,
        snapshot_semantics=str(record["snapshot_semantics"]),
    )


def verify_type_definition_record(record: Mapping[str, object]) -> None:
    """Raise a stable Phase 1525p error token when a candidate record fails."""
    reject_float(record, "type_definition_cid_mismatch")
    _require_fields(record)
    if record.get("node_type") != "type_definition":
        raise ValueError("type_definition_node_type_mismatch")
    if record.get("content_type") != "type_definition":
        raise ValueError("type_definition_content_type_not_authorized")
    _require_ratified_authority(record)
    if record.get("attribution_policy") != "non_attributable":
        raise ValueError("type_definition_attribution_policy_invalid")
    _verify_decomposition_contract(record)
    _verify_supersession(record)
    _verify_effective_epoch(record)
    _verify_definition_id(record)


def verify_type_definition_record_cbor(data: bytes) -> None:
    """Verify a canonical DAG-CBOR encoded type-definition candidate record."""
    if len(data) > MAX_CANONICAL_CBOR_INPUT_BYTES:
        raise ValueError("type_definition_cid_mismatch")
    validate_canonical_ilc_dag_cbor(data)
    decoded = decode_dag_cbor_strict(data)
    if not isinstance(decoded, Mapping):
        raise ValueError("type_definition_required_field_missing")
    verify_type_definition_record(decoded)


def _definition_id_payload(record: Mapping[str, object]) -> dict[str, object]:
    return {
        str(key): normalize_json_value(value)
        for key, value in record.items()
        if key != "definition_id"
    }


def _require_fields(record: Mapping[str, object]) -> None:
    if "authority_ref" not in record:
        raise ValueError("type_definition_missing_authority_ref")
    for field_name in sorted(_REQUIRED_FIELDS):
        if field_name not in record:
            raise ValueError("type_definition_required_field_missing")


def _require_ratified_authority(record: Mapping[str, object]) -> None:
    authority_ref = record.get("authority_ref")
    if _authority_ref_is_ratified(authority_ref):
        return
    raise ValueError("type_definition_not_cdl_ratified")


def _authority_ref_is_ratified(authority_ref: object) -> bool:
    if isinstance(authority_ref, str):
        return authority_ref in _VALID_AUTHORITY_REFS
    if isinstance(authority_ref, Mapping):
        return (
            authority_ref.get("cdl") == "CDL-097"
            and authority_ref.get("ratification_token") == CDL_097_RATIFICATION_TOKEN
        )
    return False


def _verify_decomposition_contract(record: Mapping[str, object]) -> None:
    irreducible = record.get("irreducible")
    if not isinstance(irreducible, bool):
        raise ValueError("type_definition_required_field_missing")
    if irreducible:
        if not isinstance(record.get("irreducible_reason"), str) or record.get("irreducible_reason") == "":
            raise ValueError("type_definition_irreducible_reason_missing")
        return

    recipe = record.get("decomposition_recipe")
    if not isinstance(recipe, list) or len(recipe) == 0:
        raise ValueError("type_definition_decomposition_recipe_missing")

    seen_steps: set[tuple[object, object, object, object]] = set()
    for step in recipe:
        if not isinstance(step, Mapping):
            raise ValueError("type_definition_unknown_truth_primitive")
        primitive = step.get("primitive")
        if primitive not in _KNOWN_TRUTH_PRIMITIVES:
            raise ValueError("type_definition_unknown_truth_primitive")
        signature = (
            step.get("primitive"),
            step.get("role"),
            step.get("input_ref"),
            step.get("output_ref"),
        )
        if signature in seen_steps and _scope_distinction_missing(record):
            raise ValueError("type_definition_duplicate_recipe_scope_missing")
        seen_steps.add(signature)


def _scope_distinction_missing(record: Mapping[str, object]) -> bool:
    scope = record.get("scope")
    role_schema = record.get("role_schema")
    return (
        not isinstance(scope, str)
        or scope.strip() == ""
    ) and not (isinstance(role_schema, Mapping) and len(role_schema) > 0)


def _verify_supersession(record: Mapping[str, object]) -> None:
    supersedes = record.get("supersedes_definition_id")
    if supersedes is not None and supersedes == record.get("definition_id"):
        raise ValueError("type_definition_supersession_cycle")


def _verify_effective_epoch(record: Mapping[str, object]) -> None:
    effective_epoch = record.get("effective_epoch")
    if (
        not isinstance(effective_epoch, int)
        or isinstance(effective_epoch, bool)
        or effective_epoch < 0
    ):
        raise ValueError("type_definition_effective_epoch_before_authority")


def _verify_definition_id(record: Mapping[str, object]) -> None:
    definition_id = record.get("definition_id")
    if not isinstance(definition_id, str) or definition_id == "":
        raise ValueError("type_definition_cid_mismatch")
    try:
        parse_nodeid_strict(definition_id)
    except ValueError as exc:
        raise ValueError("type_definition_cid_mismatch") from exc
    if compute_type_definition_id(record) != definition_id:
        raise ValueError("type_definition_cid_mismatch")


__all__ = [
    "ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED",
    "CDL_097_AUTHORITY_REF",
    "CDL_097_RATIFICATION_TOKEN",
    "TypeDefinitionRecord",
    "TypeRegistryCache",
    "TypeRegistryCacheState",
    "compute_type_definition_id",
    "parse_type_definition_record",
    "verify_type_definition_record",
    "verify_type_definition_record_cbor",
]
