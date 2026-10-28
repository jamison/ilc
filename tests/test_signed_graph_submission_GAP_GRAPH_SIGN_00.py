from __future__ import annotations

import argparse
import inspect
import json
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.cli import d2e_submit_cli as submit_cli
from ilc_core.cli.d2e_agent_cli import handle_agent_keygen
from ilc_core.cli.d2e_submit_cli import (
    SubmitCommandError,
    handle_submit,
)
from ilc_core.epistemic.node_submission_runtime import EpistemicSubmissionError
from ilc_core.epistemic.truth_primitive_submission_runtime import (
    verify_native_submit_sig_envelope,
)
from ilc_core.epistemic.truth_primitive_sig_verifier import (
    attach_truth_primitive_signature,
    verify_truth_primitive_sig,
)
from ilc_core.identity.bls_backend import keypair_from_ikm_hex
from ilc_core.storage.truth_primitive_graph_lmdb_adapter import TruthPrimitiveGraphStore


TEST_BLS_SECRET_HEX, AGENT_ID = keypair_from_ikm_hex("94" * 32)
OTHER_BLS_SECRET_HEX, _OTHER_AGENT_ID = keypair_from_ikm_hex("95" * 32)
ASSERT_TRUTH_PAYLOAD = {
    "content": {"body": "signed graph submission test"},
    "epistemic_type": "objective",
    "parent_node_ids": [],
    "primitive_type": "observation",
}


def _payload_json(payload: dict[str, object] | None = None) -> str:
    return json.dumps(payload or ASSERT_TRUTH_PAYLOAD, sort_keys=True)


def _ns(**kwargs: object) -> argparse.Namespace:
    defaults = {
        "primitive": "assert.truth",
        "payload_json": _payload_json(),
        "payload_file": None,
        "agent_id": AGENT_ID,
        "epoch": 1,
        "sig": "UNSIGNED",
        "signing_key": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _key_uri(tmp_path: Path, name: str = "agent-hotkey.pem") -> str:
    return str(handle_agent_keygen(str(tmp_path / name))["key_uri"])


def _submitted_record(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    payload: dict[str, object] | None = None,
) -> tuple[dict[str, object], dict[str, object]]:
    store_path = tmp_path / "truth-store"
    monkeypatch.setenv("ILC_TRUTH_GRAPH_STORE_PATH", str(store_path))
    monkeypatch.setenv("ILC_AGENT_BLS_SIGNING_KEY", TEST_BLS_SECRET_HEX)
    monkeypatch.delenv("ILC_D2D_GOSSIP_PEERS", raising=False)
    monkeypatch.setattr(
        submit_cli,
        "_ILC_AGENT_BLS_KEY_DEFAULT_PATH",
        tmp_path / "no-default-signing-key.hex",
    )
    result = handle_submit(
        _ns(
            payload_json=_payload_json(payload),
            signing_key=None,
        )
    )
    store = TruthPrimitiveGraphStore(store_path)
    try:
        record = store.get_node(str(result["node_id"]))
    finally:
        store.close()
    assert record is not None
    return result, record


def _native_envelope_from_record(record: dict[str, object]) -> dict[str, object]:
    return {
        "v": record["v"],
        "primitive": record["primitive"],
        "agent_id": record["agent_id"],
        "epoch": record["epoch"],
        "payload": record["payload"],
        "sig": record["native_submit_sig"],
    }


def test_unsigned_submission_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ILC_TRUTH_GRAPH_STORE_PATH", str(tmp_path / "truth-store"))
    monkeypatch.delenv("ILC_AGENT_BLS_SIGNING_KEY", raising=False)
    monkeypatch.setattr(
        submit_cli,
        "_ILC_AGENT_BLS_KEY_DEFAULT_PATH",
        tmp_path / "no-default-signing-key.hex",
    )

    with pytest.raises(SubmitCommandError) as exc_info:
        handle_submit(_ns())
    assert exc_info.value.token == "native_submit_sig_unsigned_placeholder_rejected"


def test_native_bls_submission_accepted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result, record = _submitted_record(tmp_path, monkeypatch)

    assert result["primitive"] == "assert.truth"
    assert result["creates_node"] is True
    verify_native_submit_sig_envelope(_native_envelope_from_record(record))


def test_native_bls_submission_stores_complete_signature_object(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, record = _submitted_record(tmp_path, monkeypatch)
    native_sig = record["native_submit_sig"]

    assert isinstance(native_sig, dict)
    assert native_sig["schema_version"] == "native_submit_sig.v0.1"
    assert native_sig["verifier_profile"] == "native_submit_sig_profile.v0.1"
    assert native_sig["dst"] == "ILC_NATIVE_TRUTH_SUBMIT_V1:ilc-public-rc-01-testnet-harness"
    assert native_sig["key_ref"] == AGENT_ID
    assert len(str(native_sig["payload_sha256"])) == 64
    assert len(str(native_sig["signature_hex"])) == 192


def test_attach_signature_deep_copies_nested_payload() -> None:
    record = {
        "agent_id": AGENT_ID,
        "epoch": 1,
        "payload": dict(ASSERT_TRUTH_PAYLOAD),
        "primitive": "assert.truth",
        "v": 1,
    }
    signed = attach_truth_primitive_signature(record, ed25519.Ed25519PrivateKey.generate())
    signed["payload"]["content"]["body"] = "mutated through returned copy"  # type: ignore[index]

    assert record["payload"]["content"]["body"] == "signed graph submission test"  # type: ignore[index]


def test_native_bls_edge_only_submission_record_verifies(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store_path = tmp_path / "truth-store"
    monkeypatch.setenv("ILC_TRUTH_GRAPH_STORE_PATH", str(store_path))
    monkeypatch.setenv("ILC_AGENT_BLS_SIGNING_KEY", TEST_BLS_SECRET_HEX)
    monkeypatch.delenv("ILC_D2D_GOSSIP_PEERS", raising=False)
    monkeypatch.setattr(
        submit_cli,
        "_ILC_AGENT_BLS_KEY_DEFAULT_PATH",
        tmp_path / "no-default-signing-key.hex",
    )
    payload = {
        "confidence": "0.80",
        "evidence_summary": "signed edge-only verification",
        "target_node_id": "bafy-target-node",
    }

    handle_submit(
        _ns(
            primitive="validate.claim",
            payload_json=_payload_json(payload),
            signing_key=None,
        )
    )

    store = TruthPrimitiveGraphStore(store_path)
    try:
        edge_record = store.get_edge(f"{payload['target_node_id']}:validated_by:{AGENT_ID}")
    finally:
        store.close()
    assert edge_record is not None
    verify_native_submit_sig_envelope(_native_envelope_from_record(edge_record))


def test_wrong_key_signature_fails_verification(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ILC_AGENT_BLS_SIGNING_KEY", OTHER_BLS_SECRET_HEX)
    monkeypatch.setattr(
        submit_cli,
        "_ILC_AGENT_BLS_KEY_DEFAULT_PATH",
        tmp_path / "no-default-signing-key.hex",
    )

    with pytest.raises(SubmitCommandError) as exc_info:
        handle_submit(_ns(agent_id=AGENT_ID))
    assert exc_info.value.token == "submit_bls_key_agent_id_mismatch"


def test_tampered_content_fails_verification(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _, record = _submitted_record(tmp_path, monkeypatch)
    record["payload"]["content"]["body"] = "tampered body"

    with pytest.raises(EpistemicSubmissionError) as exc_info:
        verify_native_submit_sig_envelope(_native_envelope_from_record(record))
    assert exc_info.value.token == "native_submit_sig_payload_sha256_mismatch_IMPL_00"


def test_tampered_uncertainty_declared_fails_verification() -> None:
    record = {
        "agent_id": AGENT_ID,
        "epoch": 1,
        "payload": dict(ASSERT_TRUTH_PAYLOAD),
        "primitive": "assert.truth",
        "uncertainty_declared": "measurement uncertainty recorded",
        "v": 1,
    }
    signed = attach_truth_primitive_signature(
        record,
        ed25519.Ed25519PrivateKey.generate(),
    )

    assert verify_truth_primitive_sig(signed) is True

    signed["uncertainty_declared"] = "tampered uncertainty"
    with pytest.raises(ValueError, match="invalid_truth_primitive_signature"):
        verify_truth_primitive_sig(signed)


def test_tampered_sig_bytes_fails_verification(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Flipping a native BLS signature byte must fail verification."""
    _, record = _submitted_record(tmp_path, monkeypatch)
    native_sig = record["native_submit_sig"]
    assert isinstance(native_sig, dict)
    sig_bytes = bytes.fromhex(str(native_sig["signature_hex"]))
    flipped = sig_bytes[:-1] + bytes([sig_bytes[-1] ^ 0xFF])
    native_sig["signature_hex"] = flipped.hex()

    with pytest.raises(EpistemicSubmissionError) as exc_info:
        verify_native_submit_sig_envelope(_native_envelope_from_record(record))
    assert exc_info.value.token == "native_submit_sig_bls_verification_failed_CDL_118"


def test_verifier_returns_none_for_unsigned() -> None:
    assert verify_truth_primitive_sig({"sig": "UNSIGNED"}) is None
    assert verify_truth_primitive_sig({}) is None


def test_no_central_registry_needed() -> None:
    sig = inspect.signature(verify_native_submit_sig_envelope)

    assert list(sig.parameters) == ["envelope"]


def test_ed25519_and_native_bls_signing_are_rejected_as_ambiguous(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ILC_AGENT_BLS_SIGNING_KEY", TEST_BLS_SECRET_HEX)
    with pytest.raises(SubmitCommandError) as exc_info:
        handle_submit(_ns(signing_key=_key_uri(tmp_path)))
    assert exc_info.value.token == "submit_signature_ambiguous"


def test_legacy_ed25519_signature_helper_still_verifies() -> None:
    record = {
        "agent_id": AGENT_ID,
        "epoch": 1,
        "payload": dict(ASSERT_TRUTH_PAYLOAD),
        "primitive": "assert.truth",
        "v": 1,
    }
    signed = attach_truth_primitive_signature(record, ed25519.Ed25519PrivateKey.generate())

    assert verify_truth_primitive_sig(signed) is True


def test_submit_parser_exposes_signing_key_flag() -> None:
    text = Path("ilc_core/cli/main.py").read_text(encoding="utf-8")

    assert "--signing-key" in text
    assert "signing_key" in text


def test_action_type_unchanged() -> None:
    from ilc_core.value_action.ilc_transfer_intent import ActionType

    assert list(ActionType) == [ActionType.ILC_TRANSFER]
