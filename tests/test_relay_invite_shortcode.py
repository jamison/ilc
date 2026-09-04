from __future__ import annotations

import argparse
import base64
from collections import deque
import json
import threading
import time
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
    RelayServerError,
    attach_shortcode_invite_bundle_auth,
    encode_shortcode_invite_bundle,
    relay_invite_store_payload_ref,
    shortcode_invite_bundle_payload_ref,
    verify_shortcode_invite_bundle,
)


IKM_HEX = "71" * 32
OTHER_IKM_HEX = "72" * 32
RELAY_AGENT_ID = "8" * 96


def _server(*, now_provider: Any | None = None) -> RelayRendezvousServer:
    return RelayRendezvousServer(
        RelayServerConfig(
            relay_agent_id=RELAY_AGENT_ID,
            relay_host="127.0.0.1",
            control_port=51151,
        ),
        now_provider=now_provider,
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


def test_ttl_expiry_410() -> None:
    now = [1000.0]
    server = _server(now_provider=lambda: now[0])
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


def test_fetch_and_status_share_get_rate_limit() -> None:
    server = _server()
    bundles = [_signed_bundle(index)[3] for index in range(11)]
    status, stored = server.handle_json_request(
        method="POST",
        path=RELAY_INVITE_STORE_PATH,
        payload=_store_request(bundles),
        source_host="198.51.100.10",
    )
    assert status == 200
    for _ in range(5):
        status, _body = server.handle_json_request(
            method="GET",
            path=f"{RELAY_INVITE_PATH_PREFIX}{stored['code']}",
            payload=None,
            source_host="198.51.100.100",
        )
        assert status == 200
    for _ in range(5):
        status, _body = server.handle_json_request(
            method="GET",
            path=f"{RELAY_INVITE_PATH_PREFIX}{stored['code']}/status",
            payload=None,
            source_host="198.51.100.100",
        )
        assert status == 200
    status, body = server.handle_json_request(
        method="GET",
        path=f"{RELAY_INVITE_PATH_PREFIX}{stored['code']}/status",
        payload=None,
        source_host="198.51.100.100",
    )
    assert status == 429
    assert body["error"] == "relay_invite_status_rate_limited"


def test_invite_batch_storage_cap_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(relay_server_module, "_MAX_INVITE_BATCH_ENTRIES", 1)
    server = _server()
    server._invite_batches["ILC-H7K2-X9P4"] = relay_server_module._InviteCodeBatch(
        code="ILC-H7K2-X9P4",
        bundles_b64=deque(["e30="]),
        expires_at_unix=time.time() + 3600,
        inviting_agent_id="a" * 96,
        inviting_bls_public_key_hex="a" * 96,
        slots_total=1,
    )
    with pytest.raises(RelayServerError, match="invite_code_storage_capacity_exhausted"):
        with server._state_lock:
            server._allocate_invite_code_locked()


def test_invite_batch_storage_cap_sweeps_expired(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(relay_server_module, "_MAX_INVITE_BATCH_ENTRIES", 1)
    server = _server()
    server._invite_batches["ILC-H7K2-X9P4"] = relay_server_module._InviteCodeBatch(
        code="ILC-H7K2-X9P4",
        bundles_b64=deque(["e30="]),
        expires_at_unix=time.time() - 1,
        inviting_agent_id="a" * 96,
        inviting_bls_public_key_hex="a" * 96,
        slots_total=1,
    )
    with server._state_lock:
        code = server._allocate_invite_code_locked()
    assert validate_code(code)
    assert "ILC-H7K2-X9P4" not in server._invite_batches


def test_invite_batch_expiry_heap_removes_only_matching_generation() -> None:
    server = _server(now_provider=lambda: 2000.0)
    with server._state_lock:
        server._invite_batches["ILC-H7K2-X9P4"] = relay_server_module._InviteCodeBatch(
            code="ILC-H7K2-X9P4",
            bundles_b64=deque(["e30="]),
            expires_at_unix=3000.0,
            inviting_agent_id="a" * 96,
            inviting_bls_public_key_hex="a" * 96,
            slots_total=1,
        )
        server._invite_expiry_heap.append((1000.0, "ILC-H7K2-X9P4"))
        server._sweep_expired_invite_batches_locked(2000.0)
    assert "ILC-H7K2-X9P4" in server._invite_batches


def test_invite_store_rejects_colon_delimited_source_host() -> None:
    server = _server()
    bundle = _signed_bundle()[3]
    status, body = server.handle_json_request(
        method="POST",
        path=RELAY_INVITE_STORE_PATH,
        payload=_store_request([bundle]),
        source_host="198.51.100.10:agent:evil",
    )
    assert status == 400
    assert body["error"] == "relay_invite_store_source_host_invalid"


def test_invite_rate_limiter_is_thread_safe() -> None:
    limiter = relay_server_module._InviteRateLimiter(
        limit=10,
        window_seconds=60.0,
        now_provider=lambda: 1000.0,
    )
    results: list[bool] = []
    results_lock = threading.Lock()

    def attempt() -> None:
        allowed = limiter.allow("ip:198.51.100.101:get")
        with results_lock:
            results.append(allowed)

    threads = [threading.Thread(target=attempt) for _ in range(50)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert results.count(True) == 10
    assert results.count(False) == 40


def test_shortcode_bundle_payload_ref_rejects_non_string_keys() -> None:
    with pytest.raises(RelayServerError, match="relay_invite_bundle_key_invalid"):
        shortcode_invite_bundle_payload_ref({1: "value"})


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


def test_invite_generate_stdout_upload_conflict_fails_before_capsule_load(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_if_loaded() -> tuple[dict[str, Any], ...]:
        raise AssertionError("capsule loader must not run before flag conflict check")

    monkeypatch.setattr(cli_main, "_load_bundled_relay_records_for_generate", fail_if_loaded)
    with pytest.raises(ValueError, match="invite_generate_stdout_upload_conflict"):
        cli_main._run_identity_invite_generate_subcommand(
            argparse.Namespace(slots=1, ttl="24h", stdout=True, upload=True)
        )


def test_invite_generate_corrupt_bundled_capsule_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cli_main, "_load_bundled_relay_capsule_payload", lambda: {"bad": "capsule"})
    monkeypatch.setattr(cli_main, "_install_verified_relay_bootstrap_records", lambda *_args, **_kwargs: ())
    with pytest.raises(ValueError, match="invite_generate_bundled_capsule_no_verified_records"):
        cli_main._load_bundled_relay_records_for_generate()


def test_invite_generate_explicit_relay_install_command_includes_pin(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Any,
) -> None:
    secret_key, public_key = keypair_from_ikm_hex(IKM_HEX)
    identity_dir = tmp_path / "identity"
    identity_dir.mkdir()
    (identity_dir / "signing_key.hex").write_text(f"{secret_key}\n", encoding="utf-8")
    (identity_dir / "agent_id").write_text(f"{public_key}\n", encoding="utf-8")

    def fake_hint(args: argparse.Namespace) -> dict[str, Any]:
        output = {
            "known_peer_hint_key_bindings": {},
            "known_peer_hints": [],
            "schema_version": "bootstrap_peer_hints.v0.1",
        }
        cli_main.Path(str(args.output)).write_text(json.dumps(output), encoding="utf-8")
        return {"action": "peer_hint_created"}

    monkeypatch.setattr(cli_main, "_load_bundled_relay_records_for_generate", lambda: ())
    monkeypatch.setattr(cli_main, "_load_bundled_relay_capsule_payload", lambda: {"schema_version": "test"})
    monkeypatch.setattr(cli_main, "_run_identity_invite_hint_subcommand", fake_hint)
    monkeypatch.setattr(
        "ilc_core.identity.first_run_provisioning.identity_root",
        lambda _home: identity_dir,
    )
    monkeypatch.setattr(
        cli_main,
        "_post_invite_store_request",
        lambda **_kwargs: {
            "code": "ILC-H7K2-X9P4",
            "schema_version": "relay_invite_code_store_response.v0.1",
            "slots": 1,
            "status_url": "https://relay.example:51151/relay/invite/ILC-H7K2-X9P4/status",
        },
    )

    result = cli_main._run_identity_invite_generate_subcommand(
        argparse.Namespace(
            batch_id="batch-a",
            emit_store_request=False,
            intended_profile="public_rc_invitee_bootstrap",
            output="",
            relay_tls_cert_der_sha256="b" * 64,
            relay_url="https://relay.example:51151",
            slots=1,
            stdout=False,
            ttl="24h",
            upload=True,
        )
    )

    assert "--invite-code ILC-H7K2-X9P4" in result["install_command"]
    assert "--relay-url https://relay.example:51151" in result["install_command"]
    assert f"--relay-tls-cert-der-sha256 {'b' * 64}" in result["install_command"]


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
    assert "ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)" in text
    assert "ssl._create_unverified_context" not in text
    assert "--location" not in text
    assert "--location-trusted" not in text


def test_invite_generate_cli_uses_public_tls_context() -> None:
    text = (cli_main.Path(__file__).resolve().parents[1] / "ilc_core/cli/main.py").read_text(
        encoding="utf-8"
    )
    assert "ssl.create_default_context()" in text
    assert "ssl._create_unverified_context" not in text
