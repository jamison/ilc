from __future__ import annotations

import argparse
import hashlib
import json

import pytest

from ilc_core.cli import d2e_submit_cli as submit_cli
from ilc_core.cli.d2e_submit_cli import (
    _build_native_submit_sig_object,
    _load_bls_signing_key,
    handle_submit,
    SubmitCommandError,
)
from ilc_core.epistemic.truth_primitive_graph_store import write_truth_primitive_result
from ilc_core.epistemic import truth_primitive_submission_runtime as truth_runtime
from ilc_core.epistemic.node_submission_runtime import EpistemicSubmissionError
from ilc_core.identity.bls_backend import (
    keypair_from_ikm_hex,
    public_key_from_secret_key_hex,
    sign_native_submit_bytes,
    verify_native_submit_bytes,
)
from ilc_core.storage.truth_primitive_graph_lmdb_adapter import TruthPrimitiveGraphStore

NETWORK_ID = "ilc-public-rc-01-testnet-harness"
SECRET_KEY_HEX, AGENT_ID = keypair_from_ikm_hex("11" * 32)


@pytest.fixture(autouse=True)
def _clear_replay_state(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ILC_TRUTH_GRAPH_STORE_PATH", raising=False)
    monkeypatch.delenv("ILC_AGENT_BLS_SIGNING_KEY", raising=False)
    truth_runtime._NATIVE_SUBMIT_REPLAY_FALLBACK.clear()


def _payload() -> dict[str, object]:
    return {
        "content": {"claim": "native submit signer binding fixture"},
        "primitive_type": "observation",
        "epistemic_type": "objective",
        "parent_node_ids": [],
    }


def _envelope() -> dict[str, object]:
    return {
        "v": 1,
        "primitive": "assert.truth",
        "agent_id": AGENT_ID,
        "epoch": 0,
        "payload": _payload(),
        "sig": "UNSIGNED",
    }


def _canonical_bytes(envelope: dict[str, object]) -> bytes:
    return json.dumps(
        {key: value for key, value in envelope.items() if key != "sig"},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _attach_sig(envelope: dict[str, object], *, signing_key: str = SECRET_KEY_HEX) -> dict[str, object]:
    canonical = _canonical_bytes(envelope)
    envelope["sig"] = {
        "schema_version": "native_submit_sig.v0.1",
        "verifier_profile": "native_submit_sig_profile.v0.1",
        "dst": f"ILC_NATIVE_TRUTH_SUBMIT_V1:{NETWORK_ID}",
        "payload_sha256": hashlib.sha256(canonical).hexdigest(),
        "signature_hex": sign_native_submit_bytes(signing_key, canonical, NETWORK_ID),
        "key_ref": public_key_from_secret_key_hex(signing_key),
    }
    return envelope


def _assert_token(exc_info: pytest.ExceptionInfo[EpistemicSubmissionError], token: str) -> None:
    assert exc_info.value.token == token


def test_canonical_bytes_valid_signature_passes() -> None:
    truth_runtime.verify_native_submit_sig_envelope(_attach_sig(_envelope()))


def test_sha256_digest_signing_fails() -> None:
    envelope = _envelope()
    canonical = _canonical_bytes(envelope)
    digest_signature = sign_native_submit_bytes(
        SECRET_KEY_HEX,
        hashlib.sha256(canonical).digest(),
        NETWORK_ID,
    )
    envelope["sig"] = {
        "schema_version": "native_submit_sig.v0.1",
        "verifier_profile": "native_submit_sig_profile.v0.1",
        "dst": f"ILC_NATIVE_TRUTH_SUBMIT_V1:{NETWORK_ID}",
        "payload_sha256": hashlib.sha256(canonical).hexdigest(),
        "signature_hex": digest_signature,
        "key_ref": AGENT_ID,
    }

    with pytest.raises(EpistemicSubmissionError) as exc_info:
        truth_runtime.verify_native_submit_sig_envelope(envelope)
    _assert_token(exc_info, "native_submit_sig_bls_verification_failed_CDL_118")


def test_mutated_envelope_with_recomputed_hash_fails_bls() -> None:
    envelope = _attach_sig(_envelope())
    assert isinstance(envelope["payload"], dict)
    envelope["payload"] = {
        **envelope["payload"],
        "content": {"claim": "mutated after signing"},
    }
    assert isinstance(envelope["sig"], dict)
    envelope["sig"]["payload_sha256"] = hashlib.sha256(_canonical_bytes(envelope)).hexdigest()

    with pytest.raises(EpistemicSubmissionError) as exc_info:
        truth_runtime.verify_native_submit_sig_envelope(envelope)
    _assert_token(exc_info, "native_submit_sig_bls_verification_failed_CDL_118")


def test_mismatched_payload_sha256_fails_before_bls() -> None:
    envelope = _attach_sig(_envelope())
    assert isinstance(envelope["sig"], dict)
    envelope["sig"]["payload_sha256"] = "0" * 64

    with pytest.raises(EpistemicSubmissionError) as exc_info:
        truth_runtime.verify_native_submit_sig_envelope(envelope)
    _assert_token(exc_info, "native_submit_sig_payload_sha256_mismatch_IMPL_00")


def test_wrong_network_signature_fails_bls() -> None:
    envelope = _envelope()
    canonical = _canonical_bytes(envelope)
    envelope["sig"] = {
        "schema_version": "native_submit_sig.v0.1",
        "verifier_profile": "native_submit_sig_profile.v0.1",
        "dst": f"ILC_NATIVE_TRUTH_SUBMIT_V1:{NETWORK_ID}",
        "payload_sha256": hashlib.sha256(canonical).hexdigest(),
        "signature_hex": sign_native_submit_bytes(SECRET_KEY_HEX, canonical, "other-network"),
        "key_ref": AGENT_ID,
    }

    with pytest.raises(EpistemicSubmissionError) as exc_info:
        truth_runtime.verify_native_submit_sig_envelope(envelope)
    _assert_token(exc_info, "native_submit_sig_bls_verification_failed_CDL_118")


def test_key_ref_agent_id_mismatch_fails() -> None:
    envelope = _attach_sig(_envelope())
    assert isinstance(envelope["sig"], dict)
    envelope["sig"]["key_ref"] = keypair_from_ikm_hex("22" * 32)[1]

    with pytest.raises(EpistemicSubmissionError) as exc_info:
        truth_runtime.verify_native_submit_sig_envelope(envelope)
    _assert_token(exc_info, "native_submit_sig_key_ref_agent_id_mismatch_CDL_118")


def test_signature_hex_length_not_192_fails() -> None:
    envelope = _attach_sig(_envelope())
    assert isinstance(envelope["sig"], dict)
    envelope["sig"]["signature_hex"] = "ab" * 95

    with pytest.raises(EpistemicSubmissionError) as exc_info:
        truth_runtime.verify_native_submit_sig_envelope(envelope)
    _assert_token(exc_info, "native_submit_sig_signature_hex_length_invalid_CDL_118")


def test_replay_same_triple_rejected_with_lmdb(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ILC_TRUTH_GRAPH_STORE_PATH", str(tmp_path / "truth_graph_lmdb"))
    envelope = _attach_sig(_envelope())

    result = truth_runtime.validate_truth_primitive_submission(envelope)
    store = TruthPrimitiveGraphStore(tmp_path / "truth_graph_lmdb")
    try:
        write_truth_primitive_result(store, envelope, result)
        with pytest.raises(EpistemicSubmissionError) as exc_info:
            write_truth_primitive_result(store, envelope, result)
    finally:
        store.close()
    _assert_token(exc_info, "native_submit_sig_replay_rejected_CDL_118")


def test_replay_marker_not_stored_as_graph_node(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ILC_TRUTH_GRAPH_STORE_PATH", str(tmp_path / "truth_graph_lmdb"))
    envelope = _attach_sig(_envelope())
    result = truth_runtime.validate_truth_primitive_submission(envelope)
    store = TruthPrimitiveGraphStore(tmp_path / "truth_graph_lmdb")
    try:
        receipt = write_truth_primitive_result(store, envelope, result)
        nodes = store.iter_nodes()
        replay_record = truth_runtime.native_submit_replay_record_from_envelope(envelope)
        assert replay_record is not None
        assert store.get_native_submit_replay(replay_record[0]) == replay_record[1]
    finally:
        store.close()

    assert receipt["native_submit_replay_written"] == 1
    assert len(nodes) == 1
    assert nodes[0]["primitive"] == "assert.truth"
    assert nodes[0]["native_submit_sig"] == envelope["sig"]


def test_semantically_invalid_payload_does_not_consume_replay(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ILC_TRUTH_GRAPH_STORE_PATH", str(tmp_path / "truth_graph_lmdb"))
    envelope = _attach_sig(_envelope())
    assert isinstance(envelope["payload"], dict)
    envelope["payload"] = {**envelope["payload"], "primitive_type": "not_registered"}
    assert isinstance(envelope["sig"], dict)
    envelope["sig"]["payload_sha256"] = hashlib.sha256(_canonical_bytes(envelope)).hexdigest()
    envelope["sig"]["signature_hex"] = sign_native_submit_bytes(
        SECRET_KEY_HEX,
        _canonical_bytes(envelope),
        NETWORK_ID,
    )
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        truth_runtime.validate_truth_primitive_submission(envelope)
    _assert_token(exc_info, "primitive_type_not_allowed")

    fixed = _attach_sig(_envelope())
    result = truth_runtime.validate_truth_primitive_submission(fixed)
    store = TruthPrimitiveGraphStore(tmp_path / "truth_graph_lmdb")
    try:
        receipt = write_truth_primitive_result(store, fixed, result)
    finally:
        store.close()
    assert receipt["nodes_written"] == 1


def test_validate_only_replay_fallback_is_locked_and_capped(monkeypatch: pytest.MonkeyPatch) -> None:
    envelope = _attach_sig(_envelope())
    truth_runtime.verify_native_submit_sig_envelope(envelope)
    monkeypatch.setattr(truth_runtime, "_NATIVE_SUBMIT_REPLAY_FALLBACK_MAX_SIZE", 1)

    truth_runtime.consume_native_submit_replay_fallback(envelope)
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        truth_runtime.consume_native_submit_replay_fallback(envelope)
    _assert_token(exc_info, "native_submit_sig_replay_rejected_CDL_118")

    other = _attach_sig({**_envelope(), "epoch": 1})
    with pytest.raises(EpistemicSubmissionError) as cap_exc:
        truth_runtime.consume_native_submit_replay_fallback(other)
    _assert_token(cap_exc, "native_submit_replay_fallback_capacity_exhausted")


def test_bls_wrapper_domain_separation() -> None:
    message = _canonical_bytes(_envelope())
    signature = sign_native_submit_bytes(SECRET_KEY_HEX, message, NETWORK_ID)
    assert verify_native_submit_bytes(AGENT_ID, message, signature, NETWORK_ID) is True
    assert verify_native_submit_bytes(AGENT_ID, message, signature, "wrong-network") is False


def test_bls_network_id_is_stripped_and_control_chars_rejected() -> None:
    message = _canonical_bytes(_envelope())
    signature = sign_native_submit_bytes(SECRET_KEY_HEX, message, f" {NETWORK_ID} ")
    assert verify_native_submit_bytes(AGENT_ID, message, signature, NETWORK_ID) is True
    with pytest.raises(ValueError, match="bls_network_id_invalid"):
        sign_native_submit_bytes(SECRET_KEY_HEX, message, f"{NETWORK_ID}\n")


def test_cli_loads_bls_key_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ILC_AGENT_BLS_SIGNING_KEY", SECRET_KEY_HEX)
    assert _load_bls_signing_key() == SECRET_KEY_HEX


def test_cli_builds_native_submit_sig_object() -> None:
    envelope = _envelope()
    sig = _build_native_submit_sig_object(envelope, SECRET_KEY_HEX)
    assert sig["key_ref"] == AGENT_ID
    envelope["sig"] = sig
    truth_runtime.verify_native_submit_sig_envelope(envelope)


def test_cli_auto_signs_with_bls_key_while_guard_remains_true(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ILC_AGENT_BLS_SIGNING_KEY", SECRET_KEY_HEX)
    ns = argparse.Namespace(
        primitive="assert.truth",
        payload_json=json.dumps(_payload()),
        payload_file=None,
        agent_id=AGENT_ID,
        epoch=0,
        sig="UNSIGNED",
        signing_key=None,
    )

    response = handle_submit(ns)

    assert response["primitive"] == "assert.truth"
    assert response["native_submit_sig"]["key_ref"] == AGENT_ID


def test_cli_rejects_ed25519_and_bls_ambiguity(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ILC_AGENT_BLS_SIGNING_KEY", SECRET_KEY_HEX)
    ns = argparse.Namespace(
        primitive="assert.truth",
        payload_json=json.dumps(_payload()),
        payload_file=None,
        agent_id=AGENT_ID,
        epoch=0,
        sig="UNSIGNED",
        signing_key="file:///tmp/ed25519.key",
    )

    with pytest.raises(SubmitCommandError) as exc_info:
        handle_submit(ns)
    assert exc_info.value.token == "submit_signature_ambiguous"


def test_cli_file_bls_key_agent_mismatch_raises_while_guard_true(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    key_path = tmp_path / "signing_key.hex"
    key_path.write_text("22" * 32, encoding="ascii")
    monkeypatch.setattr(submit_cli, "_ILC_AGENT_BLS_KEY_DEFAULT_PATH", key_path)
    monkeypatch.setattr(truth_runtime, "NATIVE_SUBMISSION_SIG_VERIFICATION_NOT_ACTIVATED", True)
    ns = argparse.Namespace(
        primitive="assert.truth",
        payload_json=json.dumps(_payload()),
        payload_file=None,
        agent_id=AGENT_ID,
        epoch=0,
        sig="UNSIGNED",
        signing_key=None,
    )

    with pytest.raises(SubmitCommandError) as exc_info:
        handle_submit(ns)
    assert exc_info.value.token == "submit_bls_key_agent_id_mismatch"
