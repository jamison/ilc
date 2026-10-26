# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric.mldsa import MLDSA65PrivateKey

from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.identity.bls_backend import keypair_from_ikm_hex
from ilc_core.cli.d2e_submit_cli import _build_native_submit_sig_object
from ilc_core.release.installable_release_signature import validate_envelope_set
from ilc_core.release.upgrade_check import validate_release_assertion
from tools import rc_native_distribution_vnext_sign_publish as ceremony


ENVELOPES = Path(
    "docs/specs/ilc_core_0434_release_envelopes_"
    "GAP_RC_NATIVE_DISTRIBUTION_VNEXT_SIGN_PUBLISH_00_v0.1.json"
)
ASSERTION = Path(
    "docs/specs/ilc_core_0434_release_assertion_"
    "GAP_RC_NATIVE_DISTRIBUTION_VNEXT_SIGN_PUBLISH_00_v0.1.json"
)
BASELINE = Path(
    "docs/specs/ilc_rc_native_distribution_closure_strike_force_"
    "execution_manifest_v0.2.json"
)
AMENDMENT = Path(
    "docs/specs/ilc_rc_native_distribution_closure_strike_force_"
    "execution_manifest_v0.2_amendment_01.md"
)


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_authorization_files_remain_bound_to_supplied_hashes() -> None:
    ceremony._verify_authorization_hashes(BASELINE, AMENDMENT)


def test_authorization_hash_mismatch_fails_closed(tmp_path: Path) -> None:
    altered = tmp_path / "amendment.md"
    altered.write_text("changed\n", encoding="utf-8")
    with pytest.raises(
        ceremony.VNextCeremonyError, match="amendment_sha256_mismatch"
    ):
        ceremony._verify_authorization_hashes(BASELINE, altered)


def test_v0434_envelopes_are_complete_and_structurally_valid() -> None:
    envelope_set = _load(ENVELOPES)
    validate_envelope_set(envelope_set)
    assert envelope_set["version"] == "0.4.34"
    assert len(envelope_set["envelopes"]) == 3
    for envelope in envelope_set["envelopes"].values():
        assert envelope["signer_public_key_hex"] == ceremony.EXPECTED_RELEASE_PUBLIC_KEY_HEX
        assert len(envelope["signature_hex"]) == 128
        assert envelope["prior_release_envelope_ref"] == ceremony.PRIOR_RELEASE_ENVELOPE_REF


def test_v0434_release_assertion_has_exact_signed_artifact_coverage() -> None:
    assertion = _load(ASSERTION)
    validation = validate_release_assertion(assertion)
    assert assertion["assertion_cid"] == node_id_from_obj(
        {
            key: value
            for key, value in assertion.items()
            if key not in {"assertion_cid", "native_submit_envelope"}
        }
    )
    assert assertion["assertion_cid"] == (
        "bafyreihdrkharlpx2oejwpdbmjeaypsnnk7az5vaixqjzoftdk4o6ko4d4"
    )
    assert assertion["software_release_node"]["version"] == "0.4.34"
    assert validation["release_signature_verified"] is True
    assert validation["signature_scheme"] == "ed25519_phase_1335"
    assert validation["verified_attestation_count"] == 3
    assert validation["current_release_eligibility_status"] == "unresolved"
    assert len(assertion["artifact_nodes"]) == 3
    assert sum(
        node["artifact_type"] == "binary_tarball"
        for node in assertion["artifact_nodes"]
    ) == 1
    assert {
        node["artifact_type"] for node in assertion["artifact_nodes"]
    } == {"wheel", "sdist", "binary_tarball"}


def _native_release_envelope(assertion: dict, secret: str, public: str) -> dict:
    unsigned = {
        "agent_id": public,
        "epoch": 0,
        "payload": {
            "content": {
                "phase": ceremony.PHASE,
                "software_release_assertion": assertion,
            },
            "epistemic_type": "objective",
            "parent_node_ids": [],
            "primitive_type": "observation",
        },
        "primitive": "assert.truth",
        "v": 1,
    }
    return {
        **unsigned,
        "sig": _build_native_submit_sig_object(
            unsigned, secret, network_id=ceremony.NETWORK_ID
        ),
    }


def test_release_native_envelope_attachment_makes_graph_binding_portable(
    tmp_path: Path,
) -> None:
    assertion = _load(ASSERTION)
    assertion.pop("native_submit_envelope", None)
    assertion_path = tmp_path / "assertion.json"
    assertion_path.write_text(json.dumps(assertion), encoding="utf-8")
    secret, public = keypair_from_ikm_hex("63" * 32)
    envelope_path = tmp_path / "envelope.json"
    envelope_path.write_text(
        json.dumps(_native_release_envelope(assertion, secret, public)),
        encoding="utf-8",
    )

    portable, receipt = ceremony.attach_release_native_envelope(
        assertion_path=assertion_path,
        native_submit_envelope_path=envelope_path,
    )

    validation = validate_release_assertion(portable)
    assert portable["assertion_cid"] == assertion["assertion_cid"]
    assert validation["full_release_graph_binding_verified"] is True
    assert receipt["network_id"] == ceremony.NETWORK_ID


def test_release_native_envelope_attachment_rejects_wrong_assertion(
    tmp_path: Path,
) -> None:
    assertion = _load(ASSERTION)
    assertion.pop("native_submit_envelope", None)
    assertion_path = tmp_path / "assertion.json"
    assertion_path.write_text(json.dumps(assertion), encoding="utf-8")
    nested = json.loads(json.dumps(assertion))
    nested["software_release_node"]["version"] = "9.9.9"
    secret, public = keypair_from_ikm_hex("64" * 32)
    envelope_path = tmp_path / "envelope.json"
    envelope_path.write_text(
        json.dumps(_native_release_envelope(nested, secret, public)),
        encoding="utf-8",
    )

    with pytest.raises(
        ceremony.VNextCeremonyError,
        match="release_graph_provenance_assertion_core_mismatch",
    ):
        ceremony.attach_release_native_envelope(
            assertion_path=assertion_path,
            native_submit_envelope_path=envelope_path,
        )


def test_policy_preparation_uses_detached_genesis_signature_boundary() -> None:
    source = Path("tools/rc_native_distribution_vnext_sign_publish.py").read_text(
        encoding="utf-8"
    )
    assert "policy_signature_path" in source
    assert "policy_seed" not in source
    assert "Secret seed material" not in source
    assert "verify_mldsa65_signature" in source


def _write_private_hex(path: Path, value: str) -> None:
    path.write_text(value + "\n", encoding="ascii")
    os.chmod(path, 0o600)


def _policy_fixture(tmp_path: Path) -> tuple[dict, Path]:
    assertion = _load(ASSERTION)
    previous_record = {"fixture": "previous-policy-record"}
    previous_path = tmp_path / "previous.json"
    previous_path.write_text(json.dumps(previous_record), encoding="utf-8")
    body = {
        "action": "select",
        "authority_basis": "CDL-122",
        "channel": ceremony.POLICY_CHANNEL,
        "effective_validation_epoch": 0,
        "genesis_lineage_ref": "artifact:genesis_agent1_pubkey_record_838a",
        "max_observer_lag_epochs": 0,
        "network_id": ceremony.POLICY_NETWORK_ID,
        "policy_id": ceremony.POLICY_ID,
        "policy_sequence": 2,
        "previous_policy_claim_cid": node_id_from_obj(previous_record),
        "rejected_release_assertion_cids": [],
        "release_signer_profile": "ed25519_phase_1335",
        "release_signer_public_key_hex": ceremony.EXPECTED_RELEASE_PUBLIC_KEY_HEX,
        "selected_artifact_cids": sorted(
            assertion["software_release_node"]["artifact_cids"]
        ),
        "selected_release_assertion_cid": assertion["assertion_cid"],
        "selected_software_release_cid": assertion["software_release_node"]["cid"],
        "valid_through_validation_epoch": 0,
        "withdrawn_release_assertion_cids": [],
    }
    return body, previous_path


def test_policy_finalization_verifies_detached_mldsa_and_separates_bls_roles(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    body, previous_path = _policy_fixture(tmp_path)
    payload = (
        ceremony.POLICY_SIGNATURE_DOMAIN.encode("ascii")
        + b"\0"
        + ceremony._canonical_bytes(body)
    )
    body_path = tmp_path / "body.json"
    payload_path = tmp_path / "payload.bin"
    signature_path = tmp_path / "signature.hex"
    public_record = tmp_path / "public.txt"
    submit_path = tmp_path / "submit.hex"
    invite_path = tmp_path / "invite.hex"
    body_path.write_text(json.dumps(body), encoding="utf-8")
    payload_path.write_bytes(payload)

    policy_key = MLDSA65PrivateKey.generate()
    policy_public_hex = policy_key.public_key().public_bytes_raw().hex()
    public_record.write_text(f"mldsa_pk_hex:             {policy_public_hex}\n")
    signature_path.write_text(
        policy_key.sign(payload, ceremony.POLICY_MLDSA_SIGNING_CONTEXT).hex() + "\n"
    )
    monkeypatch.setattr(
        ceremony,
        "EXPECTED_POLICY_PUBLIC_KEY_SHA256",
        hashlib.sha256(bytes.fromhex(policy_public_hex)).hexdigest(),
    )

    submit_secret, submit_public = keypair_from_ikm_hex("61" * 32)
    invite_secret, invite_public = keypair_from_ikm_hex("62" * 32)
    _write_private_hex(submit_path, submit_secret)
    _write_private_hex(invite_path, invite_secret)
    monkeypatch.setattr(
        ceremony, "GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX", submit_public
    )
    monkeypatch.setattr(ceremony, "GENESIS_INVITE_ISSUER_PK_HEX", invite_public)

    record, native_submit, binding, receipt = ceremony.finalize_policy(
        policy_body_path=body_path,
        policy_payload_path=payload_path,
        policy_signature_path=signature_path,
        policy_public_key_record_path=public_record,
        prior_policy_record_path=previous_path,
        public_submit_secret_path=submit_path,
        invite_secret_path=invite_path,
    )
    assert receipt["mldsa_signature_verified"] is True
    assert receipt["claim_cid"] == node_id_from_obj(record)
    assert native_submit["sig"]["key_ref"] == submit_public
    assert binding["shortcode_auth"]["inviting_bls_public_key_hex"] == invite_public
    assert submit_public != invite_public


def test_policy_finalization_rejects_tampered_signature(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    body, previous_path = _policy_fixture(tmp_path)
    payload = (
        ceremony.POLICY_SIGNATURE_DOMAIN.encode("ascii")
        + b"\0"
        + ceremony._canonical_bytes(body)
    )
    key = MLDSA65PrivateKey.generate()
    public_hex = key.public_key().public_bytes_raw().hex()
    body_path = tmp_path / "body.json"
    payload_path = tmp_path / "payload.bin"
    signature_path = tmp_path / "signature.hex"
    record_path = tmp_path / "public.txt"
    body_path.write_text(json.dumps(body), encoding="utf-8")
    payload_path.write_bytes(payload)
    signature = bytearray(key.sign(payload, ceremony.POLICY_MLDSA_SIGNING_CONTEXT))
    signature[0] ^= 1
    signature_path.write_text(signature.hex() + "\n")
    record_path.write_text(f"mldsa_pk_hex:             {public_hex}\n")
    monkeypatch.setattr(
        ceremony,
        "EXPECTED_POLICY_PUBLIC_KEY_SHA256",
        hashlib.sha256(bytes.fromhex(public_hex)).hexdigest(),
    )
    with pytest.raises(
        ceremony.VNextCeremonyError, match="policy_signature_verification_failed"
    ):
        ceremony.finalize_policy(
            policy_body_path=body_path,
            policy_payload_path=payload_path,
            policy_signature_path=signature_path,
            policy_public_key_record_path=record_path,
            prior_policy_record_path=previous_path,
            public_submit_secret_path=tmp_path / "unused-submit.hex",
            invite_secret_path=tmp_path / "unused-invite.hex",
        )
