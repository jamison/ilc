# SPDX-License-Identifier: AGPL-3.0-only
"""Verify the bounded Genesis invite witness-to-materialization linkage."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping

from ilc_core.bundle.atlas_slice_schema import merkle_root_from_rows
from ilc_core.bundle.atlas_slice_verifier import (
    AtlasSliceVerifierError,
    verify_portable_manifest_witness,
)
from ilc_core.genesis.invite_issuer_authority import GENESIS_INVITE_ISSUER_PK_HEX
from ilc_core.network.relay.relay_server import verify_shortcode_invite_bundle
from ilc_core.sidecars.starmap_installer import (
    StarMapInstallerError,
    verify_starmap_manifest,
)


MAX_INVITE_BUNDLE_BYTES = 1_048_576
MAX_JSON_DEPTH = 18
MAX_JSON_NODES = 24_000
MAX_JSON_STRING_BYTES = 16_384


class InviteMaterializationLinkageError(ValueError):
    """Stable-token failure for the bounded linkage verifier."""

    def __init__(self, token: str) -> None:
        super().__init__(token)
        self.token = token


def _mapping(value: Any, token: str) -> Mapping[str, Any]:
    if type(value) is not dict:
        raise InviteMaterializationLinkageError(token)
    return value


def _string(value: Any, token: str) -> str:
    if type(value) is not str or not value:
        raise InviteMaterializationLinkageError(token)
    return value


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise InviteMaterializationLinkageError("invite_linkage_duplicate_json_key")
        result[key] = value
    return result


def _reject_number(_: str) -> None:
    raise InviteMaterializationLinkageError("invite_linkage_non_integer_number")


def _walk_json(value: Any, *, depth: int = 0, count: list[int] | None = None) -> None:
    if count is None:
        count = [0]
    count[0] += 1
    if count[0] > MAX_JSON_NODES or depth > MAX_JSON_DEPTH:
        raise InviteMaterializationLinkageError("invite_linkage_json_bounds_exceeded")
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        if abs(value) > 2**63 - 1:
            raise InviteMaterializationLinkageError("invite_linkage_integer_out_of_range")
        return
    if type(value) is str:
        if len(value.encode("utf-8")) > MAX_JSON_STRING_BYTES:
            raise InviteMaterializationLinkageError("invite_linkage_string_too_large")
        return
    if type(value) is list:
        for item in value:
            _walk_json(item, depth=depth + 1, count=count)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise InviteMaterializationLinkageError("invite_linkage_json_key_invalid")
            _walk_json(key, depth=depth + 1, count=count)
            _walk_json(item, depth=depth + 1, count=count)
        return
    raise InviteMaterializationLinkageError("invite_linkage_json_type_invalid")


def load_invite_bundle(path: Path) -> dict[str, Any]:
    """Load one bounded invite bundle without accepting ambiguous JSON."""

    try:
        with path.expanduser().open("rb") as handle:
            raw = handle.read(MAX_INVITE_BUNDLE_BYTES + 1)
    except OSError as exc:
        raise InviteMaterializationLinkageError("invite_linkage_bundle_unreadable") from exc
    if len(raw) > MAX_INVITE_BUNDLE_BYTES:
        raise InviteMaterializationLinkageError("invite_linkage_bundle_too_large")
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_float=_reject_number,
            parse_constant=_reject_number,
        )
    except InviteMaterializationLinkageError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InviteMaterializationLinkageError("invite_linkage_bundle_json_invalid") from exc
    _walk_json(value)
    if type(value) is not dict:
        raise InviteMaterializationLinkageError("invite_linkage_bundle_not_object")
    return value


def verify_invite_materialization_linkage(
    bundle: Mapping[str, Any],
    *,
    expected_inviting_agent_id: str,
    expected_inviting_bls_public_key_hex: str,
) -> dict[str, Any]:
    """Verify BLS scope and all bounded witness/materialization bindings."""

    clean_bundle = _mapping(bundle, "invite_linkage_bundle_not_object")
    witness = _mapping(
        clean_bundle.get("atlas_slice_manifest_witness"),
        "invite_linkage_witness_missing",
    )
    payload = _mapping(
        clean_bundle.get("starmap_manifest_payload"),
        "invite_linkage_materialization_payload_missing",
    )

    if not verify_shortcode_invite_bundle(
        clean_bundle,
        inviting_agent_id=expected_inviting_agent_id,
        inviting_bls_public_key_hex=expected_inviting_bls_public_key_hex,
    ):
        raise InviteMaterializationLinkageError("invite_linkage_outer_bls_invalid")

    try:
        witness_receipt = verify_portable_manifest_witness(witness)
        payload_receipt = verify_starmap_manifest(payload)
    except AtlasSliceVerifierError as exc:
        raise InviteMaterializationLinkageError(
            f"invite_linkage_witness_invalid:{exc}"
        ) from exc
    except StarMapInstallerError as exc:
        raise InviteMaterializationLinkageError(
            f"invite_linkage_payload_invalid:{exc}"
        ) from exc

    if witness.get("signer_authority_class") != "genesis":
        raise InviteMaterializationLinkageError("invite_linkage_not_genesis_profile")

    witness_slice_id = _string(witness.get("slice_id"), "invite_linkage_witness_slice_id_invalid")
    payload_slice_id = _string(payload.get("slice_id"), "invite_linkage_payload_slice_id_invalid")
    if witness_slice_id != payload_slice_id:
        raise InviteMaterializationLinkageError("invite_linkage_slice_id_mismatch")

    witness_version = _string(
        witness.get("epoch_or_version"),
        "invite_linkage_witness_version_invalid",
    )
    payload_version = _string(
        payload.get("slice_version"),
        "invite_linkage_payload_version_invalid",
    )
    if witness_version != payload_version:
        raise InviteMaterializationLinkageError("invite_linkage_version_mismatch")

    witness_authority_root = _string(
        witness.get("authority_root"),
        "invite_linkage_witness_authority_root_invalid",
    )
    payload_authority_root = _string(
        payload.get("source_lmdb_root_sha256"),
        "invite_linkage_payload_authority_root_invalid",
    )
    if witness_authority_root != payload_authority_root:
        raise InviteMaterializationLinkageError("invite_linkage_authority_root_mismatch")

    entries = payload.get("content_entries")
    if type(entries) is not list or not entries:
        raise InviteMaterializationLinkageError("invite_linkage_content_entries_invalid")
    rows: list[dict[str, Any]] = []
    for entry in entries:
        clean_entry = _mapping(entry, "invite_linkage_content_entry_invalid")
        rows.append(
            {
                "key": _string(
                    clean_entry.get("node_id"),
                    "invite_linkage_content_entry_node_id_invalid",
                ),
                "table": "content_entries",
                "value": dict(clean_entry),
            }
        )
    observed_witness_root = merkle_root_from_rows(rows)
    declared_witness_root = _string(
        witness.get("merkle_root"),
        "invite_linkage_witness_merkle_root_invalid",
    )
    if observed_witness_root != declared_witness_root:
        raise InviteMaterializationLinkageError("invite_linkage_witness_merkle_root_mismatch")

    witness_projection = _string(
        witness.get("projection_query_id"),
        "invite_linkage_witness_projection_invalid",
    )
    payload_projection = _string(
        payload.get("projection_filter"),
        "invite_linkage_payload_projection_invalid",
    )
    if witness_projection != payload_projection:
        raise InviteMaterializationLinkageError("invite_linkage_projection_mismatch")
    projection_parameters = _mapping(
        witness.get("projection_parameters"),
        "invite_linkage_projection_parameters_invalid",
    )
    projection_source = _string(
        projection_parameters.get("source"),
        "invite_linkage_projection_source_invalid",
    )
    if any(entry.get("graph_projection") != witness_projection for entry in entries):
        raise InviteMaterializationLinkageError("invite_linkage_entry_projection_mismatch")
    if any(entry.get("origin_mode") != projection_source for entry in entries):
        raise InviteMaterializationLinkageError("invite_linkage_projection_source_mismatch")

    witness_privacy = _string(
        witness.get("privacy_class"),
        "invite_linkage_witness_privacy_invalid",
    )
    permission_policy = _mapping(
        witness.get("permission_policy"),
        "invite_linkage_permission_policy_invalid",
    )
    policy_privacy = _string(
        permission_policy.get("privacy_class"),
        "invite_linkage_permission_privacy_invalid",
    )
    payload_privacy = _string(
        payload.get("privacy_budget"),
        "invite_linkage_payload_privacy_invalid",
    )
    if len({witness_privacy, policy_privacy, payload_privacy}) != 1:
        raise InviteMaterializationLinkageError("invite_linkage_privacy_mismatch")
    if any(entry.get("export_category") != witness_privacy for entry in entries):
        raise InviteMaterializationLinkageError("invite_linkage_entry_privacy_mismatch")

    auth = _mapping(clean_bundle.get("shortcode_auth"), "invite_linkage_shortcode_auth_missing")
    return {
        "bundle_payload_sha384": _string(
            auth.get("bundle_payload_sha384"),
            "invite_linkage_bundle_payload_sha384_invalid",
        ),
        "entry_count": len(entries),
        "outer_bls_verified": True,
        "payload_cidv1": _string(payload.get("cidv1"), "invite_linkage_payload_cid_invalid"),
        "payload_manifest_verified": payload_receipt.get("verification") == "passed",
        "privacy_class": witness_privacy,
        "projection_query_id": witness_projection,
        "schema_version": "invite_materialization_linkage_receipt.v0.1",
        "slice_id": witness_slice_id,
        "slice_version": witness_version,
        "status": "verified",
        "witness_manifest_sha384": _string(
            witness.get("manifest_sha384"),
            "invite_linkage_witness_manifest_sha384_invalid",
        ),
        "witness_merkle_root_sha384": observed_witness_root,
        "witness_verified": bool(witness_receipt.get("verified")),
    }


def _write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode("utf-8")
    fd, raw_path = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp_path = Path(raw_path)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp_path, 0o600)
        os.replace(temp_path, path)
    finally:
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    bundle = load_invite_bundle(args.bundle)
    receipt = verify_invite_materialization_linkage(
        bundle,
        expected_inviting_agent_id=GENESIS_INVITE_ISSUER_PK_HEX,
        expected_inviting_bls_public_key_hex=GENESIS_INVITE_ISSUER_PK_HEX,
    )
    if args.receipt is not None:
        _write_json_atomic(args.receipt, receipt)
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
