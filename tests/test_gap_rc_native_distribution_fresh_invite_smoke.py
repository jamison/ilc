# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from copy import deepcopy

import pytest

from ilc_core.bundle.default_public_rc_starmap import (
    build_default_public_rc_starmap_payload,
    build_default_public_rc_starmap_witness,
)
from ilc_core.bundle.atlas_slice_schema import sha384_canonical
from ilc_core.identity.bls_backend import keypair_from_ikm_hex
from ilc_core.network.relay.relay_server import attach_shortcode_invite_bundle_auth
from tools.verify_invite_materialization_linkage import (
    InviteMaterializationLinkageError,
    verify_invite_materialization_linkage,
)


_IKM_HEX = "91" * 32


def _signed_bundle() -> tuple[str, str, dict[str, object]]:
    secret_key, public_key = keypair_from_ikm_hex(_IKM_HEX)
    payload = build_default_public_rc_starmap_payload()
    witness = build_default_public_rc_starmap_witness(payload)
    raw = {
        "atlas_slice_manifest_witness": witness,
        "intended_epoch": 0,
        "intended_profile": "public_rc_invitee_bootstrap",
        "starmap_manifest_payload": payload,
    }
    return secret_key, public_key, attach_shortcode_invite_bundle_auth(
        raw,
        inviting_agent_id=public_key,
        inviting_bls_public_key_hex=public_key,
        inviting_bls_secret_key_hex=secret_key,
    )


def _resign(
    bundle: dict[str, object],
    *,
    secret_key: str,
    public_key: str,
) -> dict[str, object]:
    return attach_shortcode_invite_bundle_auth(
        bundle,
        inviting_agent_id=public_key,
        inviting_bls_public_key_hex=public_key,
        inviting_bls_secret_key_hex=secret_key,
    )


def _verify(bundle: dict[str, object], public_key: str) -> dict[str, object]:
    return verify_invite_materialization_linkage(
        bundle,
        expected_inviting_agent_id=public_key,
        expected_inviting_bls_public_key_hex=public_key,
    )


def _refresh_witness_manifest(witness: dict[str, object]) -> None:
    body = {key: value for key, value in witness.items() if key != "manifest_sha384"}
    witness["manifest_sha384"] = sha384_canonical(body)


def test_valid_signed_bundle_binds_witness_to_materialization_payload() -> None:
    _, public_key, bundle = _signed_bundle()
    receipt = _verify(bundle, public_key)
    assert receipt["status"] == "verified"
    assert receipt["outer_bls_verified"] is True
    assert receipt["witness_verified"] is True
    assert receipt["payload_manifest_verified"] is True
    assert receipt["entry_count"] == 1


def test_outer_bls_scope_rejects_unsigned_witness_mutation() -> None:
    _, public_key, bundle = _signed_bundle()
    mutated = deepcopy(bundle)
    mutated["atlas_slice_manifest_witness"]["slice_id"] = "attacker-slice"  # type: ignore[index]
    with pytest.raises(InviteMaterializationLinkageError) as exc:
        _verify(mutated, public_key)
    assert exc.value.token == "invite_linkage_outer_bls_invalid"


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("slice_id", "invite_linkage_slice_id_mismatch"),
        ("version", "invite_linkage_version_mismatch"),
        ("authority_root", "invite_linkage_authority_root_mismatch"),
        ("merkle_root", "invite_linkage_witness_merkle_root_mismatch"),
        ("projection", "invite_linkage_projection_mismatch"),
        ("privacy", "invite_linkage_privacy_mismatch"),
    ],
)
def test_resigned_inconsistent_bindings_fail_closed(mutation: str, expected: str) -> None:
    secret_key, public_key, bundle = _signed_bundle()
    mutated = deepcopy(bundle)
    witness = mutated["atlas_slice_manifest_witness"]
    payload = mutated["starmap_manifest_payload"]
    assert isinstance(witness, dict)
    assert isinstance(payload, dict)
    if mutation == "slice_id":
        witness["slice_id"] = "different-slice"
    elif mutation == "version":
        witness["epoch_or_version"] = "different-version"
    elif mutation == "authority_root":
        witness["authority_root"] = "f" * 64
    elif mutation == "merkle_root":
        witness["merkle_root"] = "f" * 96
    elif mutation == "projection":
        witness["projection_query_id"] = "public_protocol_graph"
    elif mutation == "privacy":
        witness["permission_policy"] = {"privacy_class": "redacted"}
        witness["privacy_class"] = "redacted"
    else:  # pragma: no cover - parametrization is exhaustive
        raise AssertionError(mutation)
    _refresh_witness_manifest(witness)
    resigned = _resign(mutated, secret_key=secret_key, public_key=public_key)
    with pytest.raises(InviteMaterializationLinkageError) as exc:
        _verify(resigned, public_key)
    assert exc.value.token == expected


def test_wrong_expected_genesis_key_rejected() -> None:
    _, public_key, bundle = _signed_bundle()
    _, other_public_key = keypair_from_ikm_hex("92" * 32)
    assert other_public_key != public_key
    with pytest.raises(InviteMaterializationLinkageError) as exc:
        _verify(bundle, other_public_key)
    assert exc.value.token == "invite_linkage_outer_bls_invalid"
