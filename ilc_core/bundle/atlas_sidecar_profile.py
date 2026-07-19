# SPDX-License-Identifier: AGPL-3.0-only
"""Atlas sidecar profile and recipe schema helpers for Window 1576.

This module defines deterministic descriptors only. It does not install slices,
write LMDB, serve sidecars, fetch blobs, grant roles, clear guards, sign
records, mint, settle, write wallets, activate public P2P, or transition epochs.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from ilc_core.bundle.atlas_slice_schema import (
    ALLOWED_PRIVACY_CLASSES,
    ALLOWED_SIGNER_AUTHORITY_CLASSES,
)
from ilc_core.rc.package_profiles import (
    PACKAGE_PROFILES,
    PROFILE_CONFIDENTIAL_COORDINATION_LOCAL_PREVIEW,
    PROFILE_OPENCLAW_SKILL_CLAIMABLE,
    PROFILE_OPENCLAW_SKILL_LOCAL,
    validate_all_package_profiles,
)
from ilc_core.sidecars.registry_manifest import build_sidecar_registry_manifest


ATLAS_SIDECAR_RECIPE_SCHEMA_VERSION = "atlas_sidecar_recipe_1576.v0.1"
ATLAS_SIDECAR_PROFILE_SCHEMA_VERSION = "atlas_sidecar_profile_1576.v0.1"
ATLAS_SIDECAR_PROFILE_PHASE = "1576-sidecar-profile"
ATLAS_SIDECAR_PROFILE_VALIDATION_SCHEMA_VERSION = (
    "atlas_sidecar_profile_validation_receipt_1576.v0.1"
)
ATLAS_SIDECAR_PROFILE_SCHEMA_TOKEN = "atlas_sidecar_profile_schema_committed_phase_1576"
ATLAS_SIDECAR_RECIPE_FORMAT_TOKEN = "atlas_sidecar_recipe_format_committed_phase_1576"
ATLAS_SIDECAR_PROFILE_NO_INSTALL_TOKEN = "atlas_sidecar_profile_no_install_no_lmdb_phase_1576"
ATLAS_SIDECAR_RECIPE_DIGEST_TOKEN = (
    "atlas_sidecar_recipe_digest_commitment_schema_committed_phase_1576"
)
ATLAS_SIDECAR_RECIPE_BOUNDED_QUERY_TOKEN = (
    "atlas_sidecar_recipe_bounded_query_declarations_committed_phase_1576"
)

ALLOWED_BOUNDED_QUERY_TYPES = frozenset(
    {
        "authority_path",
        "hyperedge_expansion",
        "membership_chunk",
        "neighborhood",
    }
)
ALLOWED_CONTENT_AVAILABILITY_MODES = frozenset(
    {
        "local_only",
        "local_with_staged_fetch",
        "network_fetch_authorized",
    }
)
ALLOWED_PACKAGE_PROFILE_REFS = frozenset(
    {
        PROFILE_CONFIDENTIAL_COORDINATION_LOCAL_PREVIEW,
        PROFILE_OPENCLAW_SKILL_CLAIMABLE,
        PROFILE_OPENCLAW_SKILL_LOCAL,
    }
)
REQUIRED_INSTALL_POLICY = {
    "local_source_only": True,
    "require_digest_verification": True,
}
NODE_COMMITMENT_DIGEST_FIELD = "record_sha384"
EDGE_COMMITMENT_DIGEST_FIELD = "record_sha384"
CONTENT_COMMITMENT_DIGEST_FIELD = "sha384"

MAX_PROFILE_RECIPES = 100
MAX_RECIPE_DEPENDENCIES = 10
MAX_CONFORMANCE_TEST_REFS = 20
MAX_INDEX_ROOTS = 20
MAX_STRING_LENGTH = 512
MAX_PROFILE_JSON_DEPTH = 32
MAX_TOTAL_PROFILE_JSON_BYTES = 1024 * 1024
MAX_BOUNDED_QUERIES_PER_RECIPE = len(ALLOWED_BOUNDED_QUERY_TYPES)

_HEX_96 = frozenset("0123456789abcdef")
_RECIPE_PREFIX = "atlas_sidecar_recipe:"
_PROFILE_PREFIX = "atlas_sidecar_profile:"
_VALIDATION_RECEIPT_PREFIX = "atlas_sidecar_profile_validation_receipt:"
_RECIPE_FIELDS = frozenset(
    {
        "bounded_queries",
        "content_availability_mode",
        "content_commitment_digest_field",
        "conformance_test_refs",
        "creator_or_registry_root",
        "dependency_recipe_ids",
        "edge_commitment_digest_field",
        "graph_scope",
        "index_roots",
        "install_policy",
        "manifest_sha384",
        "native_record_sha384",
        "node_commitment_digest_field",
        "non_authority_by_default",
        "non_claims",
        "package_profile_ref",
        "privacy_class",
        "projection_query_id",
        "recipe_id",
        "recipe_schema_version",
        "retrieval_receipt_schema",
        "sidecar_kind",
        "signer_authority_class",
        "slice_id",
    }
)
_PROFILE_FIELDS = frozenset(
    {
        "authority_precedence",
        "installed_slice_registry_target",
        "non_claims",
        "privacy_restriction",
        "profile_id",
        "profile_name",
        "profile_schema_version",
        "recipes",
        "sidecar_id_refs",
    }
)
_INSTALL_POLICY_FIELDS = frozenset(
    {
        "allow_missing_blobs",
        "local_source_only",
        "require_digest_verification",
    }
)
_NON_CLAIMS = {
    "no_epoch_transition": True,
    "no_guard_clearance": True,
    "no_lmdb_install": True,
    "no_lmdb_write": True,
    "no_production_minting": True,
    "no_production_signing": True,
    "no_public_graph_write": True,
    "no_role_grant": True,
    "no_verifier_role_grant": True,
    "no_wallet_write": True,
}
_OUTPUT_TOKENS = (
    ATLAS_SIDECAR_PROFILE_SCHEMA_TOKEN,
    ATLAS_SIDECAR_RECIPE_FORMAT_TOKEN,
    ATLAS_SIDECAR_PROFILE_NO_INSTALL_TOKEN,
    ATLAS_SIDECAR_RECIPE_DIGEST_TOKEN,
    ATLAS_SIDECAR_RECIPE_BOUNDED_QUERY_TOKEN,
)


class AtlasSidecarProfileError(ValueError):
    """Stable Atlas sidecar profile error."""


def build_sidecar_recipe(
    *,
    sidecar_kind: str,
    graph_scope: str,
    content_availability_mode: str,
    index_roots: Sequence[str],
    retrieval_receipt_schema: str,
    privacy_class: str,
    non_authority_by_default: bool,
    creator_or_registry_root: str,
    package_profile_ref: str,
    conformance_test_refs: Sequence[str],
    slice_id: str,
    projection_query_id: str,
    signer_authority_class: str,
    manifest_sha384: str,
    native_record_sha384: str,
    dependency_recipe_ids: Sequence[str] = (),
    bounded_queries: Sequence[str] = (),
    install_policy: Mapping[str, Any] | None = None,
    non_claims: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a deterministic sidecar recipe with a SHA-384 identity."""

    body = {
        "bounded_queries": _normalize_str_sequence(
            bounded_queries,
            "bounded_queries",
            max_count=MAX_BOUNDED_QUERIES_PER_RECIPE,
        ),
        "content_availability_mode": content_availability_mode,
        "content_commitment_digest_field": CONTENT_COMMITMENT_DIGEST_FIELD,
        "conformance_test_refs": _normalize_str_sequence(
            conformance_test_refs,
            "conformance_test_refs",
            max_count=MAX_CONFORMANCE_TEST_REFS,
        ),
        "creator_or_registry_root": creator_or_registry_root,
        "dependency_recipe_ids": _normalize_str_sequence(
            dependency_recipe_ids,
            "dependency_recipe_ids",
            max_count=MAX_RECIPE_DEPENDENCIES,
        ),
        "edge_commitment_digest_field": EDGE_COMMITMENT_DIGEST_FIELD,
        "graph_scope": graph_scope,
        "index_roots": _normalize_sha384_sequence(
            index_roots,
            "index_roots",
            max_count=MAX_INDEX_ROOTS,
        ),
        "install_policy": _normalize_install_policy(install_policy),
        "manifest_sha384": manifest_sha384,
        "native_record_sha384": native_record_sha384,
        "node_commitment_digest_field": NODE_COMMITMENT_DIGEST_FIELD,
        "non_authority_by_default": non_authority_by_default,
        "non_claims": _normalize_non_claims(non_claims),
        "package_profile_ref": package_profile_ref,
        "privacy_class": privacy_class,
        "projection_query_id": projection_query_id,
        "recipe_schema_version": ATLAS_SIDECAR_RECIPE_SCHEMA_VERSION,
        "retrieval_receipt_schema": retrieval_receipt_schema,
        "sidecar_kind": sidecar_kind,
        "signer_authority_class": signer_authority_class,
        "slice_id": slice_id,
    }
    _validate_recipe_body(body)
    return validate_sidecar_recipe(
        {
            **body,
            "recipe_id": f"{_RECIPE_PREFIX}{_sha384_canonical(body)}",
        }
    )


def validate_sidecar_recipe(recipe: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and return a normalized Atlas sidecar recipe."""

    _reject_unsafe_json_tree(recipe)
    normalized = dict(recipe)
    _require_exact_fields(normalized, _RECIPE_FIELDS, "atlas_sidecar_recipe_fields_invalid")
    recipe_id = _required_str(normalized, "recipe_id")
    body = {key: normalized[key] for key in sorted(_RECIPE_FIELDS - {"recipe_id"})}
    _validate_recipe_body(body)
    expected = f"{_RECIPE_PREFIX}{_sha384_canonical(body)}"
    if recipe_id != expected:
        raise AtlasSidecarProfileError("atlas_sidecar_recipe_id_mismatch")
    return {**body, "recipe_id": recipe_id}


def build_sidecar_profile(
    *,
    profile_name: str,
    recipes: Sequence[Mapping[str, Any]],
    authority_precedence: Sequence[str],
    sidecar_id_refs: Sequence[str],
    privacy_restriction: str,
    installed_slice_registry_target: str,
    non_claims: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a deterministic sidecar profile with a SHA-384 identity."""

    body = {
        "authority_precedence": _normalize_str_sequence(
            authority_precedence,
            "authority_precedence",
            max_count=MAX_PROFILE_RECIPES,
        ),
        "installed_slice_registry_target": installed_slice_registry_target,
        "non_claims": _normalize_non_claims(non_claims),
        "privacy_restriction": privacy_restriction,
        "profile_name": profile_name,
        "profile_schema_version": ATLAS_SIDECAR_PROFILE_SCHEMA_VERSION,
        "recipes": [validate_sidecar_recipe(recipe) for recipe in recipes],
        "sidecar_id_refs": _normalize_str_sequence(
            sidecar_id_refs,
            "sidecar_id_refs",
            max_count=len(_canonical_sidecar_ids()),
        ),
    }
    _validate_profile_body(body)
    return validate_sidecar_profile(
        {
            **body,
            "profile_id": f"{_PROFILE_PREFIX}{_sha384_canonical(body)}",
        }
    )


def validate_sidecar_profile(profile: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and return a normalized Atlas sidecar profile."""

    _reject_unsafe_json_tree(profile)
    normalized = dict(profile)
    _require_exact_fields(normalized, _PROFILE_FIELDS, "atlas_sidecar_profile_fields_invalid")
    profile_id = _required_str(normalized, "profile_id")
    body = {key: normalized[key] for key in sorted(_PROFILE_FIELDS - {"profile_id"})}
    _validate_profile_body(body)
    expected = f"{_PROFILE_PREFIX}{_sha384_canonical(body)}"
    if profile_id != expected:
        raise AtlasSidecarProfileError("atlas_sidecar_profile_id_mismatch")
    return {**body, "profile_id": profile_id}


def build_sidecar_profile_validation_receipt(
    *,
    profile: Mapping[str, Any],
    generated_at_utc: str | None = None,
) -> dict[str, Any]:
    """Build a deterministic validation receipt for a sidecar profile."""

    generated_at_source = "caller_supplied"
    if generated_at_utc is None:
        generated_at_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        generated_at_source = "wall_clock_utc"
    _validate_timestamp(generated_at_utc)
    validated = validate_sidecar_profile(profile)
    body = {
        "generated_at_source": generated_at_source,
        "generated_at_utc": generated_at_utc,
        "non_claims": _standard_non_claims(),
        "phase": ATLAS_SIDECAR_PROFILE_PHASE,
        "profile_id": validated["profile_id"],
        "profile_schema_version": validated["profile_schema_version"],
        "recipe_count": len(validated["recipes"]),
        "recipe_ids": [recipe["recipe_id"] for recipe in validated["recipes"]],
        "schema_version": ATLAS_SIDECAR_PROFILE_VALIDATION_SCHEMA_VERSION,
        "sidecar_id_refs": validated["sidecar_id_refs"],
        "tokens": list(_OUTPUT_TOKENS),
        "verdict": "pass",
    }
    receipt_sha384 = _sha384_canonical(body)
    return {
        **body,
        "receipt_body_sha384": receipt_sha384,
        "receipt_id": f"{_VALIDATION_RECEIPT_PREFIX}{receipt_sha384}",
    }


def write_sidecar_profile_validation_receipt(
    path: str | Path,
    receipt: Mapping[str, Any],
    *,
    allowed_root: str | Path | None = None,
) -> Path:
    """Atomically write a sidecar profile validation receipt."""

    _reject_unsafe_json_tree(receipt)
    target = Path(path)
    if allowed_root is not None:
        root = Path(allowed_root).resolve()
        target_resolved = target.resolve()
        if target_resolved != root and root not in target_resolved.parents:
            raise AtlasSidecarProfileError("atlas_sidecar_profile_output_path_outside_allowed_root")
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(f".{target.name}.tmp.{os.getpid()}")
    payload = json.dumps(receipt, sort_keys=True, indent=2, allow_nan=False) + "\n"
    try:
        with tmp.open("w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, target)
    finally:
        if tmp.exists():
            tmp.unlink()
    return target


def _validate_recipe_body(body: Mapping[str, Any]) -> None:
    _require_exact_fields(body, _RECIPE_FIELDS - {"recipe_id"}, "atlas_sidecar_recipe_body_fields_invalid")
    if body.get("recipe_schema_version") != ATLAS_SIDECAR_RECIPE_SCHEMA_VERSION:
        raise AtlasSidecarProfileError("atlas_sidecar_recipe_schema_version_invalid")
    _required_str(body, "sidecar_kind")
    _required_str(body, "graph_scope")
    if body.get("content_availability_mode") != "local_only":
        raise AtlasSidecarProfileError("atlas_sidecar_recipe_content_availability_not_local_only")
    _normalize_sha384_sequence(body.get("index_roots"), "index_roots", max_count=MAX_INDEX_ROOTS)
    _required_str(body, "retrieval_receipt_schema")
    if body.get("privacy_class") not in ALLOWED_PRIVACY_CLASSES:
        raise AtlasSidecarProfileError("atlas_sidecar_recipe_privacy_class_invalid")
    if body.get("non_authority_by_default") is not True:
        raise AtlasSidecarProfileError("atlas_sidecar_recipe_must_be_non_authority")
    _required_str(body, "creator_or_registry_root")
    if body.get("package_profile_ref") not in ALLOWED_PACKAGE_PROFILE_REFS:
        raise AtlasSidecarProfileError("atlas_sidecar_recipe_package_profile_ref_invalid")
    validate_all_package_profiles()
    if body.get("package_profile_ref") not in PACKAGE_PROFILES:
        raise AtlasSidecarProfileError("atlas_sidecar_recipe_package_profile_missing")
    _normalize_str_sequence(
        body.get("conformance_test_refs"),
        "conformance_test_refs",
        max_count=MAX_CONFORMANCE_TEST_REFS,
    )
    _required_str(body, "slice_id")
    _required_str(body, "projection_query_id")
    if body.get("signer_authority_class") not in ALLOWED_SIGNER_AUTHORITY_CLASSES:
        raise AtlasSidecarProfileError("atlas_sidecar_recipe_signer_authority_class_invalid")
    _require_sha384(body.get("manifest_sha384"), "atlas_sidecar_recipe_manifest_sha384_invalid")
    _require_sha384(
        body.get("native_record_sha384"),
        "atlas_sidecar_recipe_native_record_sha384_invalid",
    )
    if body.get("node_commitment_digest_field") != NODE_COMMITMENT_DIGEST_FIELD:
        raise AtlasSidecarProfileError("atlas_sidecar_recipe_node_digest_field_invalid")
    if body.get("edge_commitment_digest_field") != EDGE_COMMITMENT_DIGEST_FIELD:
        raise AtlasSidecarProfileError("atlas_sidecar_recipe_edge_digest_field_invalid")
    if body.get("content_commitment_digest_field") != CONTENT_COMMITMENT_DIGEST_FIELD:
        raise AtlasSidecarProfileError("atlas_sidecar_recipe_content_digest_field_invalid")
    _normalize_str_sequence(
        body.get("dependency_recipe_ids"),
        "dependency_recipe_ids",
        max_count=MAX_RECIPE_DEPENDENCIES,
    )
    queries = _normalize_str_sequence(
        body.get("bounded_queries"),
        "bounded_queries",
        max_count=MAX_BOUNDED_QUERIES_PER_RECIPE,
    )
    if len(set(queries)) != len(queries):
        raise AtlasSidecarProfileError("atlas_sidecar_recipe_bounded_queries_duplicate")
    if any(query not in ALLOWED_BOUNDED_QUERY_TYPES for query in queries):
        raise AtlasSidecarProfileError("atlas_sidecar_recipe_bounded_query_invalid")
    _normalize_install_policy(body.get("install_policy"))
    _normalize_non_claims(body.get("non_claims"))


def _validate_profile_body(body: Mapping[str, Any]) -> None:
    _require_exact_fields(body, _PROFILE_FIELDS - {"profile_id"}, "atlas_sidecar_profile_body_fields_invalid")
    if body.get("profile_schema_version") != ATLAS_SIDECAR_PROFILE_SCHEMA_VERSION:
        raise AtlasSidecarProfileError("atlas_sidecar_profile_schema_version_invalid")
    profile_name = _required_str(body, "profile_name")
    if len(profile_name) > 128:
        raise AtlasSidecarProfileError("atlas_sidecar_profile_name_too_long")
    recipes_raw = body.get("recipes")
    if not isinstance(recipes_raw, list):
        raise AtlasSidecarProfileError("atlas_sidecar_profile_recipes_invalid")
    if not recipes_raw or len(recipes_raw) > MAX_PROFILE_RECIPES:
        raise AtlasSidecarProfileError("atlas_sidecar_profile_recipe_count_invalid")
    recipes = [validate_sidecar_recipe(recipe) for recipe in recipes_raw]
    recipe_ids = [recipe["recipe_id"] for recipe in recipes]
    if len(set(recipe_ids)) != len(recipe_ids):
        raise AtlasSidecarProfileError("atlas_sidecar_profile_recipe_id_duplicate")
    known_recipe_ids = set(recipe_ids)
    for recipe in recipes:
        for dependency in recipe["dependency_recipe_ids"]:
            if dependency not in known_recipe_ids:
                raise AtlasSidecarProfileError("atlas_sidecar_profile_dependency_missing")
    slice_ids = [recipe["slice_id"] for recipe in recipes]
    if len(set(slice_ids)) != len(slice_ids):
        raise AtlasSidecarProfileError("atlas_sidecar_profile_slice_id_duplicate")
    precedence = _normalize_str_sequence(
        body.get("authority_precedence"),
        "authority_precedence",
        max_count=MAX_PROFILE_RECIPES,
    )
    if len(set(precedence)) != len(precedence) or set(precedence) != set(slice_ids):
        raise AtlasSidecarProfileError("atlas_sidecar_profile_authority_precedence_invalid")
    sidecar_refs = _normalize_str_sequence(
        body.get("sidecar_id_refs"),
        "sidecar_id_refs",
        max_count=len(_canonical_sidecar_ids()),
    )
    if len(set(sidecar_refs)) != len(sidecar_refs):
        raise AtlasSidecarProfileError("atlas_sidecar_profile_sidecar_id_duplicate")
    canonical_sidecars = _canonical_sidecar_ids()
    if any(sidecar_id not in canonical_sidecars for sidecar_id in sidecar_refs):
        raise AtlasSidecarProfileError("atlas_sidecar_profile_sidecar_id_unknown")
    if body.get("privacy_restriction") not in ALLOWED_PRIVACY_CLASSES:
        raise AtlasSidecarProfileError("atlas_sidecar_profile_privacy_restriction_invalid")
    _required_str(body, "installed_slice_registry_target")
    _normalize_non_claims(body.get("non_claims"))


def _normalize_install_policy(value: Mapping[str, Any] | None) -> dict[str, bool]:
    policy = (
        {
            "allow_missing_blobs": False,
            **REQUIRED_INSTALL_POLICY,
        }
        if value is None
        else dict(value)
    )
    _require_exact_fields(policy, _INSTALL_POLICY_FIELDS, "atlas_sidecar_recipe_install_policy_fields_invalid")
    if policy.get("local_source_only") is not True:
        raise AtlasSidecarProfileError("atlas_sidecar_recipe_install_policy_not_local_only")
    if policy.get("require_digest_verification") is not True:
        raise AtlasSidecarProfileError("atlas_sidecar_recipe_install_policy_digest_not_required")
    if type(policy.get("allow_missing_blobs")) is not bool:
        raise AtlasSidecarProfileError("atlas_sidecar_recipe_install_policy_allow_missing_invalid")
    return {
        "allow_missing_blobs": bool(policy["allow_missing_blobs"]),
        "local_source_only": True,
        "require_digest_verification": True,
    }


def _normalize_non_claims(value: Mapping[str, Any] | None) -> dict[str, bool]:
    claims = dict(_NON_CLAIMS if value is None else value)
    _require_exact_fields(claims, frozenset(_NON_CLAIMS), "atlas_sidecar_profile_non_claims_fields_invalid")
    if any(claims[key] is not True for key in _NON_CLAIMS):
        raise AtlasSidecarProfileError("atlas_sidecar_profile_non_claims_not_true")
    return dict(_NON_CLAIMS)


def _standard_non_claims() -> dict[str, bool]:
    return dict(_NON_CLAIMS)


def _normalize_sha384_sequence(value: Any, label: str, *, max_count: int) -> list[str]:
    values = _normalize_str_sequence(value, label, max_count=max_count)
    for item in values:
        _require_sha384(item, f"atlas_sidecar_profile_{label}_sha384_invalid")
    return values


def _normalize_str_sequence(value: Any, label: str, *, max_count: int) -> list[str]:
    if not isinstance(value, (list, tuple)):
        raise AtlasSidecarProfileError(f"atlas_sidecar_profile_{label}_invalid")
    if len(value) > max_count:
        raise AtlasSidecarProfileError(f"atlas_sidecar_profile_{label}_too_many")
    normalized = []
    for item in value:
        if not isinstance(item, str) or not item:
            raise AtlasSidecarProfileError(f"atlas_sidecar_profile_{label}_item_invalid")
        if len(item) > MAX_STRING_LENGTH:
            raise AtlasSidecarProfileError(f"atlas_sidecar_profile_{label}_item_too_long")
        normalized.append(item)
    return normalized


def _canonical_sidecar_ids() -> frozenset[str]:
    manifest = build_sidecar_registry_manifest()
    return frozenset(sidecar["sidecar_id"] for sidecar in manifest["sidecars"])


def _required_str(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise AtlasSidecarProfileError(f"atlas_sidecar_profile_required_string_invalid:{key}")
    if len(value) > MAX_STRING_LENGTH:
        raise AtlasSidecarProfileError(f"atlas_sidecar_profile_string_too_long:{key}")
    return value


def _require_sha384(value: Any, token: str) -> None:
    if not isinstance(value, str) or len(value) != 96 or any(char not in _HEX_96 for char in value):
        raise AtlasSidecarProfileError(token)


def _require_exact_fields(payload: Mapping[str, Any], fields: frozenset[str], token: str) -> None:
    if set(payload) != set(fields):
        raise AtlasSidecarProfileError(token)


def _sha384_canonical(payload: Mapping[str, Any]) -> str:
    _reject_unsafe_json_tree(payload)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    if len(canonical.encode("utf-8")) > MAX_TOTAL_PROFILE_JSON_BYTES:
        raise AtlasSidecarProfileError("atlas_sidecar_profile_json_too_large")
    return hashlib.sha384(canonical.encode("utf-8")).hexdigest()


def _validate_timestamp(value: str) -> None:
    if not isinstance(value, str) or not value:
        raise AtlasSidecarProfileError("atlas_sidecar_profile_timestamp_invalid")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AtlasSidecarProfileError("atlas_sidecar_profile_timestamp_invalid") from exc


def _reject_unsafe_json_tree(value: Any, *, _depth: int = 0) -> None:
    if _depth > MAX_PROFILE_JSON_DEPTH:
        raise AtlasSidecarProfileError("atlas_sidecar_profile_json_depth_exceeded")
    if isinstance(value, float):
        raise AtlasSidecarProfileError("atlas_sidecar_profile_float_not_allowed")
    if isinstance(value, str):
        if len(value) > MAX_STRING_LENGTH:
            raise AtlasSidecarProfileError("atlas_sidecar_profile_string_too_long")
        return
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if not isinstance(key, str):
                raise AtlasSidecarProfileError("atlas_sidecar_profile_key_not_string")
            _reject_unsafe_json_tree(key, _depth=_depth + 1)
            _reject_unsafe_json_tree(nested, _depth=_depth + 1)
        return
    if isinstance(value, (list, tuple)):
        for nested in value:
            _reject_unsafe_json_tree(nested, _depth=_depth + 1)


__all__ = [
    "ALLOWED_BOUNDED_QUERY_TYPES",
    "ALLOWED_CONTENT_AVAILABILITY_MODES",
    "ALLOWED_PACKAGE_PROFILE_REFS",
    "ATLAS_SIDECAR_PROFILE_PHASE",
    "ATLAS_SIDECAR_PROFILE_SCHEMA_TOKEN",
    "ATLAS_SIDECAR_PROFILE_SCHEMA_VERSION",
    "ATLAS_SIDECAR_PROFILE_VALIDATION_SCHEMA_VERSION",
    "ATLAS_SIDECAR_RECIPE_BOUNDED_QUERY_TOKEN",
    "ATLAS_SIDECAR_RECIPE_DIGEST_TOKEN",
    "ATLAS_SIDECAR_RECIPE_FORMAT_TOKEN",
    "ATLAS_SIDECAR_RECIPE_SCHEMA_VERSION",
    "AtlasSidecarProfileError",
    "CONTENT_COMMITMENT_DIGEST_FIELD",
    "EDGE_COMMITMENT_DIGEST_FIELD",
    "MAX_PROFILE_JSON_DEPTH",
    "MAX_PROFILE_RECIPES",
    "MAX_STRING_LENGTH",
    "MAX_TOTAL_PROFILE_JSON_BYTES",
    "NODE_COMMITMENT_DIGEST_FIELD",
    "build_sidecar_profile",
    "build_sidecar_profile_validation_receipt",
    "build_sidecar_recipe",
    "validate_sidecar_profile",
    "validate_sidecar_recipe",
    "write_sidecar_profile_validation_receipt",
]
