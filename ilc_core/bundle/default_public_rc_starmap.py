# SPDX-License-Identifier: AGPL-3.0-only
"""Installed default public-RC starmap payload for invite onboarding."""

from __future__ import annotations

import hashlib
from typing import Any

from ilc_core.bundle.atlas_slice_schema import (
    build_signed_slice_preimage,
    canonical_schema_json,
    derive_portable_manifest_witness,
    merkle_root_from_rows,
    native_signed_slice_record,
)
from ilc_core.sidecars.starmap_installer import canonical_sha256


DEFAULT_PUBLIC_RC_SLICE_ID = "public-rc-default-starmap-v1"
DEFAULT_PUBLIC_RC_SLICE_VERSION = "0.4.4"
_ZERO_SHA256 = "0" * 64


def build_default_public_rc_starmap_payload() -> dict[str, Any]:
    """Return a minimal public-safe starmap payload bundled with ilc-core."""

    entry = {
        "authority_source": "adr:0004_genesis_truth_primitives",
        "edge_types": ["asserted_by"],
        "export_category": "public",
        "graph_projection": "genesis_core_star_map",
        "node_id": "truth_primitive:assert.truth",
        "node_kind": "truth_primitive_definition",
        "origin_mode": "installed_default_public_rc_starmap",
        "recipe_status": "irreducible_primitive",
        "record_sha256": hashlib.sha256(
            b"ilc-default-public-rc-starmap:truth_primitive:assert.truth"
        ).hexdigest(),
        "required_for": ["invite_onboarding_materialization"],
        "source_path": "ilc_core.bundle.default_public_rc_starmap",
    }
    envelope = {
        "content_entries": [entry],
        "cross_section_ref_count": 0,
        "exclusion_policy": "no_excluded_private_material",
        "included_node_merkle_root": hashlib.sha256(
            entry["record_sha256"].encode("utf-8")
        ).hexdigest(),
        "installer_profile": "installer_profile:default_public_rc_invite_onboarding",
        "privacy_budget": "public",
        "projection_filter": "genesis_core_star_map",
        "public_rc_exclude": True,
        "receipt_sha256": None,
        "root_pointers": ["truth_primitive:assert.truth"],
        "runtime_version": "default_public_rc_starmap_00b_fix1.v0.1",
        "section_label": "core",
        "semantic_loss_annotations": ["minimal_default_starmap_not_full_atlas_graph"],
        "slice_id": DEFAULT_PUBLIC_RC_SLICE_ID,
        "slice_version": DEFAULT_PUBLIC_RC_SLICE_VERSION,
        "source_lmdb_root_sha256": _ZERO_SHA256,
    }
    payload = {
        **envelope,
        "canonical_json": canonical_schema_json(envelope),
        "cidv1": "bafkreiadefaultpublicrcstarmapv1",
        "cose_sign1_b64": "",
        "dag_cbor_b64": "default_public_rc_starmap_not_dag_cbor",
        "dev_signed": False,
        "sha256": canonical_sha256(envelope),
    }
    return payload


def build_default_public_rc_starmap_witness(
    starmap_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a verifier-valid portable witness for the default starmap."""

    payload = starmap_payload or build_default_public_rc_starmap_payload()
    rows = [
        {
            "key": str(entry["node_id"]),
            "table": "content_entries",
            "value": entry,
        }
        for entry in payload["content_entries"]
    ]
    preimage = build_signed_slice_preimage(
        slice_id=str(payload["slice_id"]),
        projection_query_id="genesis_core_star_map",
        projection_parameters={"source": "installed_default_public_rc_starmap"},
        included_tables=["content_entries"],
        privacy_class="public",
        authority_root=str(payload["source_lmdb_root_sha256"]),
        epoch_or_version=str(payload["slice_version"]),
        merkle_root=merkle_root_from_rows(rows),
    )
    native_record = native_signed_slice_record(
        preimage=preimage,
        signer_authority_class="genesis",
        signer_key_ref="genesis_public_rc_default_starmap",
        authority_proof_path=["adr:0004_genesis_truth_primitives"],
    )
    return derive_portable_manifest_witness(
        native_record=native_record,
        required_tests=["starmap_installer_verify"],
        semantic_loss_annotations=["minimal_default_starmap_not_full_atlas_graph"],
    )


__all__ = [
    "DEFAULT_PUBLIC_RC_SLICE_ID",
    "DEFAULT_PUBLIC_RC_SLICE_VERSION",
    "build_default_public_rc_starmap_payload",
    "build_default_public_rc_starmap_witness",
]
