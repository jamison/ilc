from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
from pathlib import Path

import pytest

from ilc_core.cli.d2e_agent_cli import agent_hotkey_fingerprint, handle_agent_keygen
from ilc_core.cli.d2e_submit_cli import SubmitCommandError, handle_submit
from ilc_core.epistemic.truth_primitive_sig_verifier import (
    TRUTH_PRIMITIVE_SIG_SCHEME,
    verify_truth_primitive_sig,
)
from ilc_core.storage.truth_primitive_graph_lmdb_adapter import TruthPrimitiveGraphStore


AGENT_ID = "agent-test-signed-graph"
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
    signing_key: str | None,
    payload: dict[str, object] | None = None,
) -> tuple[dict[str, object], dict[str, object]]:
    store_path = tmp_path / "truth-store"
    monkeypatch.setenv("ILC_TRUTH_GRAPH_STORE_PATH", str(store_path))
    monkeypatch.delenv("ILC_D2D_GOSSIP_PEERS", raising=False)
    result = handle_submit(
        _ns(
            payload_json=_payload_json(payload),
            signing_key=signing_key,
        )
    )
    store = TruthPrimitiveGraphStore(store_path)
    try:
        record = store.get_node(str(result["node_id"]))
    finally:
        store.close()
    assert record is not None
    return result, record


def test_unsigned_submission_accepted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result, record = _submitted_record(tmp_path, monkeypatch, signing_key=None)

    assert result["primitive"] == "assert.truth"
    assert result["creates_node"] is True
    assert "sig" not in record
    assert verify_truth_primitive_sig(record) is None


def test_signed_submission_accepted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _, record = _submitted_record(tmp_path, monkeypatch, signing_key=_key_uri(tmp_path))

    assert verify_truth_primitive_sig(record) is True


def test_signed_submission_stores_pubkey_hex(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _, record = _submitted_record(tmp_path, monkeypatch, signing_key=_key_uri(tmp_path))

    assert isinstance(record["sig_pubkey_hex"], str)
    assert len(str(record["sig_pubkey_hex"])) == 64
    assert len(bytes.fromhex(str(record["sig_pubkey_hex"]))) == 32


def test_signed_submission_stores_fingerprint(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _, record = _submitted_record(tmp_path, monkeypatch, signing_key=_key_uri(tmp_path))

    pubkey_bytes = bytes.fromhex(str(record["sig_pubkey_hex"]))
    assert record["sig_pubkey_fingerprint"] == hashlib.sha256(pubkey_bytes).hexdigest()


def test_signed_submission_stores_scheme(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _, record = _submitted_record(tmp_path, monkeypatch, signing_key=_key_uri(tmp_path))

    assert record["sig_scheme"] == TRUTH_PRIMITIVE_SIG_SCHEME


def test_signed_edge_only_submission_record_verifies(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store_path = tmp_path / "truth-store"
    monkeypatch.setenv("ILC_TRUTH_GRAPH_STORE_PATH", str(store_path))
    monkeypatch.delenv("ILC_D2D_GOSSIP_PEERS", raising=False)
    payload = {
        "confidence": "0.80",
        "evidence_summary": "signed edge-only verification",
        "target_node_id": "bafy-target-node",
    }

    handle_submit(
        _ns(
            primitive="validate.claim",
            payload_json=_payload_json(payload),
            signing_key=_key_uri(tmp_path),
        )
    )

    store = TruthPrimitiveGraphStore(store_path)
    try:
        edge_record = store.get_edge(f"{payload['target_node_id']}:validated_by:{AGENT_ID}")
    finally:
        store.close()
    assert edge_record is not None
    assert verify_truth_primitive_sig(edge_record) is True


def test_fingerprint_definition_matches_keygen(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _, record = _submitted_record(tmp_path, monkeypatch, signing_key=_key_uri(tmp_path))

    pubkey_bytes = bytes.fromhex(str(record["sig_pubkey_hex"]))
    assert record["sig_pubkey_fingerprint"] == agent_hotkey_fingerprint(pubkey_bytes)


def test_wrong_key_signature_fails_verification(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _, record = _submitted_record(tmp_path, monkeypatch, signing_key=_key_uri(tmp_path, "key-a.pem"))
    _, wrong_record = _submitted_record(
        tmp_path,
        monkeypatch,
        signing_key=_key_uri(tmp_path, "key-b.pem"),
        payload={
            "content": {"body": "different"},
            "epistemic_type": "objective",
            "parent_node_ids": [],
            "primitive_type": "observation",
        },
    )
    record["sig_pubkey_hex"] = wrong_record["sig_pubkey_hex"]
    record["sig_pubkey_fingerprint"] = wrong_record["sig_pubkey_fingerprint"]

    with pytest.raises(ValueError, match="invalid_truth_primitive_signature"):
        verify_truth_primitive_sig(record)


def test_tampered_content_fails_verification(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _, record = _submitted_record(tmp_path, monkeypatch, signing_key=_key_uri(tmp_path))
    record["payload"]["content"]["body"] = "tampered body"

    with pytest.raises(ValueError, match="invalid_truth_primitive_signature"):
        verify_truth_primitive_sig(record)


def test_tampered_sig_bytes_fails_verification(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Flipping a byte inside the sig field must fail Ed25519 verification.

    This is distinct from wrong-key and wrong-payload tests: the public key
    and payload are untouched; only the signature bytes are mutated.
    """
    _, record = _submitted_record(tmp_path, monkeypatch, signing_key=_key_uri(tmp_path))
    sig_bytes = bytes.fromhex(str(record["sig"]))
    # Flip the last byte — produces a syntactically valid 64-byte Ed25519 sig
    # that doesn't match the signing key's output over the canonical payload.
    flipped = sig_bytes[:-1] + bytes([sig_bytes[-1] ^ 0xFF])
    record["sig"] = flipped.hex()

    with pytest.raises(ValueError, match="invalid_truth_primitive_signature"):
        verify_truth_primitive_sig(record)


def test_verifier_propagates_canonical_payload_type_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, record = _submitted_record(tmp_path, monkeypatch, signing_key=_key_uri(tmp_path))

    def _raise_type_error(_record: dict[str, object]) -> bytes:
        raise TypeError("programmer error")

    monkeypatch.setattr(
        "ilc_core.epistemic.truth_primitive_sig_verifier.canonical_truth_primitive_sig_payload",
        _raise_type_error,
    )

    with pytest.raises(TypeError, match="programmer error"):
        verify_truth_primitive_sig(record)


def test_verifier_returns_none_for_unsigned() -> None:
    assert verify_truth_primitive_sig({"sig": "UNSIGNED"}) is None
    assert verify_truth_primitive_sig({}) is None


def test_verifier_returns_true_for_valid(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _, record = _submitted_record(tmp_path, monkeypatch, signing_key=_key_uri(tmp_path))

    assert verify_truth_primitive_sig(record) is True


def test_no_central_registry_needed() -> None:
    sig = inspect.signature(verify_truth_primitive_sig)

    assert list(sig.parameters) == ["record"]


def test_signing_key_rejects_explicit_sig_ambiguity(tmp_path: Path) -> None:
    with pytest.raises(SubmitCommandError, match="provide --sig or --signing-key"):
        handle_submit(_ns(sig="abc123", signing_key=_key_uri(tmp_path)))


def test_submit_parser_exposes_signing_key_flag() -> None:
    text = Path("ilc_core/cli/main.py").read_text(encoding="utf-8")

    assert "--signing-key" in text
    assert "signing_key" in text


def test_action_type_unchanged() -> None:
    from ilc_core.value_action.ilc_transfer_intent import ActionType

    assert list(ActionType) == [ActionType.ILC_TRANSFER]
