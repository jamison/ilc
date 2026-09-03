from __future__ import annotations

import argparse
import base64
import json
import threading
from typing import Any

import pytest

from ilc_core.cli import main as cli_main
from ilc_core.identity.bls_backend import (
    keypair_from_ikm_hex,
    sign_relay_admission_digest,
    sign_relay_invite_bundle_digest,
    sign_relay_invite_store_digest,
)
from ilc_core.network.relay import relay_server as relay_server_module
from ilc_core.network.relay.invite_code import ALPHABET, checksum_char, generate_code, validate_code
from ilc_core.network.relay.relay_server import (
    RELAY_INVITE_PATH_PREFIX,
    RELAY_INVITE_STORE_PATH,
    RelayRendezvousServer,
    RelayServerConfig,
    attach_shortcode_invite_bundle_auth,
    encode_shortcode_invite_bundle,
    relay_invite_store_payload_ref,
    shortcode_invite_bundle_payload_ref,
    verify_shortcode_invite_bundle,
)


IKM_HEX = "71" * 32
OTHER_IKM_HEX = "72" * 32
RELAY_AGENT_ID = "8" * 96


def _server() -> RelayRendezvousServer:
    return RelayRendezvousServer(
        RelayServerConfig(
            relay_agent_id=RELAY_AGENT_ID,
            relay_host="127.0.0.1",
            control_port=51151,
        )
    )


def _raw_bundle(index: int = 0, *, inviter_sig: str = "legacy-placeholder") -> dict[str, Any]:
    return {
        "atlas_slice_manifest_witness": {"slice_id": "slice-a"},
        "intended_epoch": 0,
        "intended_profile": "public_rc_invitee_bootstrap",
        "invite_batch_record": {
            "batch_id": "batch-a",
            "count": 1,
            "created_epoch": 0,
            "inviter_cid": "inviter-a",
            "inviter_sig": inviter_sig,
            "nonce_merkle_root": "a" * 64,
        },
        "invite_id": "batch-a",
        "nonce_membership_proof": [],
        "private_invite_nonce": f"{index + 1:064x}",
        "starmap_manifest_payload": {"slice_id": "slice-a"},
    }


def _signed_bundle(index: int = 0) -> tuple[str, str, str, dict[str, Any]]:
    secret_key, public_key = keypair_from_ikm_hex(IKM_HEX)
    bundle = attach_shortcode_invite_bundle_auth(
        _raw_bundle(index),
        inviting_agent_id=public_key,
        inviting_bls_public_key_hex=public_key,
        inviting_bls_secret_key_hex=secret_key,
    )
    return secret_key, public_key, public_key, bundle


def _store_request(
    bundles: list[dict[str, Any]],
    *,
    signer_ikm: str = IKM_HEX,
    public_key: str | None = None,
) -> dict[str, Any]:
    secret_key, derived_public_key = keypair_from_ikm_hex(signer_ikm)
    verifier_key = public_key or derived_public_key
    request = {
        "bundles": [encode_shortcode_invite_bundle(bundle) for bundle in bundles],
        "inviting_agent_id": verifier_key,
        "inviting_bls_public_key_hex": verifier_key,
        "ttl_seconds": 3600,
    }
    request["request_signature"] = sign_relay_invite_store_digest(
        secret_key,
        relay_invite_store_payload_ref(request),
    )
    return request


@pytest.fixture(autouse=True)
def _activate_shortcode_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(relay_server_module, "INVITE_SHORTCODE_NOT_ACTIVATED", False)


def test_code_format_valid() -> None:
    code = generate_code()
    assert validate_code(code)
    assert code.startswith("ILC-")
    assert len(code) == len("ILC-H7K2-X9P4")


def test_checksum_roundtrip() -> None:
    payload = "H7K2X9P"
    assert checksum_char(payload) == "4"
    assert validate_code("ILC-H7K2-X9P4")
    assert not validate_code("ILC-H7K2-X9P5")


def test_code_alphabet_exclusions() -> None:
    for _ in range(100):
        code = generate_code()
        body = code.removeprefix("ILC-").replace("-", "")
        assert all(char not in body for char in "OI01")
        assert all(char in ALPHABET for char in body)


def test_store_and_retrieve_happy_path() -> None:
    server = _server()
    bundles = [_signed_bundle(index)[3] for index in range(3)]
    status, stored = server.handle_json_request(
        method="POST",
        path=RELAY_INVITE_STORE_PATH,
        payload=_store_request(bundles),
        source_host="198.51.100.10",
    )
    assert status == 200
    code = stored["code"]
    for expected_remaining in (2, 1, 0):
        status, fetched = server.handle_json_request(
            method="GET",
            path=f"{RELAY_INVITE_PATH_PREFIX}{code}",
            payload=None,
            source_host="198.51.100.11",
        )
        assert status == 200
        assert fetched["slots_remaining"] == expected_remaining
        assert verify_shortcode_invite_bundle(
            json.loads(base64.b64decode(fetched["bundle_b64"]).decode("utf-8"))
        )
    status, body = server.handle_json_request(
        method="GET",
        path=f"{RELAY_INVITE_PATH_PREFIX}{code}",
        payload=None,
        source_host="198.51.100.11",
    )
    assert status == 410
    assert body == {"error": "code_exhausted"}


def test_store_and_retrieve_atomic() -> None:
    server = _server()
    bundles = [_signed_bundle(index)[3] for index in range(5)]
    status, stored = server.handle_json_request(
        method="POST",
        path=RELAY_INVITE_STORE_PATH,
        payload=_store_request(bundles),
        source_host="198.51.100.10",
    )
    assert status == 200
    results: list[int] = []
    lock = threading.Lock()

    def fetch() -> None:
        status, _body = server.handle_json_request(
            method="GET",
            path=f"{RELAY_INVITE_PATH_PREFIX}{stored['code']}",
            payload=None,
            source_host="198.51.100.12",
        )
        with lock:
            results.append(status)

    threads = [threading.Thread(target=fetch) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert results.count(200) == 5
    assert results.count(410) == 3


def test_ttl_expiry_410(monkeypatch: pytest.MonkeyPatch) -> None:
    now = [1000.0]
    monkeypatch.setattr(relay_server_module.time, "time", lambda: now[0])
    server = _server()
    bundle = _signed_bundle()[3]
    request = _store_request([bundle])
    request["ttl_seconds"] = 1
    request["request_signature"] = sign_relay_invite_store_digest(
        keypair_from_ikm_hex(IKM_HEX)[0],
        relay_invite_store_payload_ref(request),
    )
    status, stored = server.handle_json_request(
        method="POST",
        path=RELAY_INVITE_STORE_PATH,
        payload=request,
        source_host="198.51.100.10",
    )
    assert status == 200
    now[0] = 1002.0
    status, body = server.handle_json_request(
        method="GET",
        path=f"{RELAY_INVITE_PATH_PREFIX}{stored['code']}",
        payload=None,
        source_host="198.51.100.10",
    )
    assert status == 410
    assert body == {"error": "code_expired"}


def test_status_endpoint_redacts_raw_inviter_keys() -> None:
    server = _server()
    _secret_key, agent_id, public_key, bundle = _signed_bundle()
    status, stored = server.handle_json_request(
        method="POST",
        path=RELAY_INVITE_STORE_PATH,
        payload=_store_request([bundle]),
        source_host="198.51.100.10",
    )
    assert status == 200
    status, body = server.handle_json_request(
        method="GET",
        path=f"{RELAY_INVITE_PATH_PREFIX}{stored['code']}/status",
        payload=None,
        source_host="198.51.100.11",
    )
    assert status == 200
    assert body["slots_remaining"] == 1
    assert body["slots_total"] == 1
    assert agent_id not in body.values()
    assert public_key not in body.values()
    assert len(body["inviting_agent_ref"]) == 64
    assert len(body["inviting_bls_public_key_ref"]) == 64


def test_store_invalid_signature() -> None:
    server = _server()
    bundle = _signed_bundle()[3]
    request = _store_request([bundle])
    request["request_signature"] = "0" * 192
    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_INVITE_STORE_PATH,
        payload=request,
        source_host="198.51.100.10",
    )
    assert status == 400
    assert body["error"] == "relay_invite_store_signature_verification_failed"


def test_store_request_signature_wrong_dst_rejected() -> None:
    server = _server()
    secret_key, public_key = keypair_from_ikm_hex(IKM_HEX)
    bundle = _signed_bundle()[3]
    request = _store_request([bundle])
    request["request_signature"] = sign_relay_admission_digest(
        secret_key,
        relay_invite_store_payload_ref(request),
    )
    request["inviting_bls_public_key_hex"] = public_key
    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_INVITE_STORE_PATH,
        payload=request,
        source_host="198.51.100.10",
    )
    assert status == 400
    assert body["error"] == "relay_invite_store_signature_verification_failed"


def test_invalid_store_signature_does_not_burn_inviter_quota() -> None:
    server = _server()
    _secret_key, public_key, _agent_id, bundle = _signed_bundle()
    for index in range(5):
        status, body = server.handle_json_request(
            method="POST",
            path=RELAY_INVITE_STORE_PATH,
            payload=_store_request(
                [bundle],
                signer_ikm=OTHER_IKM_HEX,
                public_key=public_key,
            ),
            source_host=f"198.51.100.{index + 20}",
        )
        assert status == 400
        assert body["error"] == "relay_invite_store_signature_verification_failed"

    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_INVITE_STORE_PATH,
        payload=_store_request([bundle], public_key=public_key),
        source_host="198.51.100.99",
    )
    assert status == 200
    assert validate_code(str(body["code"]))


def test_distinct_inviter_agent_id_without_key_binding_rejected() -> None:
    server = _server()
    secret_key, public_key = keypair_from_ikm_hex(IKM_HEX)
    non_bls_agent_id = "a" * 96
    request = {
        "bundles": [encode_shortcode_invite_bundle(_signed_bundle()[3])],
        "inviting_agent_id": non_bls_agent_id,
        "inviting_bls_public_key_hex": public_key,
        "ttl_seconds": 3600,
    }
    request["request_signature"] = sign_relay_invite_store_digest(
        secret_key,
        relay_invite_store_payload_ref(request),
    )
    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_INVITE_STORE_PATH,
        payload=request,
        source_host="198.51.100.77",
    )
    assert status == 400
    assert body["error"] == "relay_invite_inviter_key_binding_unsupported"


def test_bundle_signature_wrong_dst_rejected() -> None:
    secret_key, public_key = keypair_from_ikm_hex(IKM_HEX)
    bundle = _raw_bundle()
    payload_ref = shortcode_invite_bundle_payload_ref(bundle)
    signed = dict(bundle)
    signed["shortcode_auth"] = {
        "bundle_payload_sha384": payload_ref,
        "inviting_agent_id": public_key,
        "inviting_bls_public_key_hex": public_key,
        "schema_version": "relay_invite_code_bundle_auth.v0.1",
        "signature": sign_relay_invite_store_digest(secret_key, payload_ref),
        "signature_alg": "BLS12-381-G2-SHA-256-SSWU-RO",
    }
    assert not verify_shortcode_invite_bundle(signed)


def test_legacy_inviter_sig_placeholder_rejected_for_shortcode_store() -> None:
    server = _server()
    secret_key, public_key = keypair_from_ikm_hex(IKM_HEX)
    bundle_b64 = base64.b64encode(
        json.dumps(_raw_bundle(inviter_sig="definitely-non-empty"), sort_keys=True).encode()
    ).decode("ascii")
    request = {
        "bundles": [bundle_b64],
        "inviting_agent_id": public_key,
        "inviting_bls_public_key_hex": public_key,
        "ttl_seconds": 3600,
    }
    request["request_signature"] = sign_relay_invite_store_digest(
        secret_key,
        relay_invite_store_payload_ref(request),
    )
    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_INVITE_STORE_PATH,
        payload=request,
        source_host="198.51.100.10",
    )
    assert status == 400
    assert body["error"] == "relay_invite_bundle_signature_verification_failed"


def test_store_bundle_too_large() -> None:
    server = _server()
    secret_key, public_key = keypair_from_ikm_hex(IKM_HEX)
    raw = b'{"x":"' + b"a" * 33000 + b'"}'
    request = {
        "bundles": [base64.b64encode(raw).decode("ascii")],
        "inviting_agent_id": public_key,
        "inviting_bls_public_key_hex": public_key,
        "ttl_seconds": 3600,
    }
    request["request_signature"] = sign_relay_invite_store_digest(
        secret_key,
        relay_invite_store_payload_ref(request),
    )
    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_INVITE_STORE_PATH,
        payload=request,
        source_host="198.51.100.10",
    )
    assert status == 413
    assert body["error"] == "relay_invite_bundle_too_large"


def test_store_too_many_bundles() -> None:
    server = _server()
    secret_key, public_key = keypair_from_ikm_hex(IKM_HEX)
    request = {
        "bundles": ["e30="] * 10001,
        "inviting_agent_id": public_key,
        "inviting_bls_public_key_hex": public_key,
        "ttl_seconds": 3600,
    }
    request["request_signature"] = sign_relay_invite_store_digest(
        secret_key,
        relay_invite_store_payload_ref(request),
    )
    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_INVITE_STORE_PATH,
        payload=request,
        source_host="198.51.100.10",
    )
    assert status == 413
    assert body["error"] == "relay_invite_store_too_many_bundles"


def test_get_rate_limit() -> None:
    server = _server()
    bundle = _signed_bundle()[3]
    status, stored = server.handle_json_request(
        method="POST",
        path=RELAY_INVITE_STORE_PATH,
        payload=_store_request([bundle]),
        source_host="198.51.100.10",
    )
    assert status == 200
    for _ in range(10):
        status, _body = server.handle_json_request(
            method="GET",
            path=f"{RELAY_INVITE_PATH_PREFIX}{stored['code']}/status",
            payload=None,
            source_host="198.51.100.99",
        )
        assert status == 200
    status, body = server.handle_json_request(
        method="GET",
        path=f"{RELAY_INVITE_PATH_PREFIX}{stored['code']}/status",
        payload=None,
        source_host="198.51.100.99",
    )
    assert status == 429
    assert body["error"] == "relay_invite_status_rate_limited"


def test_guard_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(relay_server_module, "INVITE_SHORTCODE_NOT_ACTIVATED", True)
    status, body = _server().handle_json_request(
        method="GET",
        path=f"{RELAY_INVITE_PATH_PREFIX}ILC-H7K2-X9P4/status",
        payload=None,
    )
    assert status == 404
    assert body["error"] == "invite_shortcode_not_activated"


def test_invite_generate_no_capsule_no_relay_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli_main, "_load_bundled_relay_records_for_generate", lambda: ())
    with pytest.raises(ValueError, match="invite_generate_no_relay_url_and_no_bundled_capsule"):
        cli_main._run_identity_invite_generate_subcommand(
            argparse.Namespace(slots=1, ttl="24h", relay_url="")
        )


def test_invite_generate_parser_has_zero_required_flags() -> None:
    parser = cli_main._build_parser()
    args = parser.parse_args(["identity", "invite", "generate"])
    assert args.identity_invite_subcommand == "generate"
    assert not hasattr(args, "enable_invites")
    assert args.output == "~/.ilc/invite_bundle.json"


def test_install_sh_no_redirect() -> None:
    text = (cli_main.Path(__file__).resolve().parents[1] / "tools/install.sh").read_text(
        encoding="utf-8"
    )
    assert "--invite-code" in text
    assert "HTTPRedirectHandler" not in text
    assert "http.client.HTTPSConnection" in text
    assert "getpeercert(binary_form=True)" in text
    assert "--location" not in text
    assert "--location-trusted" not in text
