from __future__ import annotations

import builtins
import sys
from types import SimpleNamespace

import pytest

from ilc_core.crypto import pq_signature_verify
from ilc_core.crypto.pq_signature_verify import (
    _MLDSA_PK_HEX_LENGTH,
    verify_mldsa65_signature,
)
from ilc_core.network.d2d.gossip_peer_registry import (
    MAX_PEERS,
    GOSSIP_PEER_REGISTRY_VERSION,
    GossipPeerRegistry,
)


PUBKEY_HEX = "a" * _MLDSA_PK_HEX_LENGTH
SIG_HEX = "b" * 6618


def _import_oqs_or_skip() -> object:
    try:
        import oqs  # type: ignore[import]
    except BaseException as exc:  # oqs may call SystemExit while trying to install liboqs.
        pytest.skip(f"oqs unavailable: {exc.__class__.__name__}")
    return oqs


def _structured_peer(
    *,
    peer_id: str = "peer-alpha",
    endpoint: str = "https://a.example.com",
    key_id: str = "key-alpha",
    valid_from_epoch: int = 0,
    valid_until_epoch: int | None = None,
    authorized_actor_ids: list[str] | None = None,
    mldsa_pubkey_hex: str = PUBKEY_HEX,
) -> dict[str, object]:
    return {
        "endpoint": endpoint,
        "peer_id": peer_id,
        "mldsa_pubkey_hex": mldsa_pubkey_hex,
        "key_id": key_id,
        "authorized_actor_ids": authorized_actor_ids or ["agent-alpha"],
        "valid_from_epoch": valid_from_epoch,
        "valid_until_epoch": valid_until_epoch,
    }


@pytest.mark.parametrize(
    ("message", "signature", "pubkey"),
    [
        ("not-bytes", SIG_HEX, PUBKEY_HEX),
        (b"message", "", PUBKEY_HEX),
        (b"message", "b" * 10, PUBKEY_HEX),
        (b"message", "z" * 6618, PUBKEY_HEX),
        (b"message", SIG_HEX, ""),
        (b"message", SIG_HEX, "a" * 10),
        (b"message", SIG_HEX, "z" * _MLDSA_PK_HEX_LENGTH),
    ],
)
def test_verify_mldsa65_signature_invalid_inputs_fail_closed(
    message: object,
    signature: str,
    pubkey: str,
) -> None:
    assert verify_mldsa65_signature(message, signature, pubkey) is False  # type: ignore[arg-type]


def test_verify_mldsa65_signature_oqs_unavailable_returns_false(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__

    def fake_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "oqs":
            raise ImportError("missing oqs")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    assert verify_mldsa65_signature(b"message", SIG_HEX, PUBKEY_HEX) is False


def test_verify_mldsa65_signature_runtime_error_returns_false(monkeypatch: pytest.MonkeyPatch) -> None:
    class BrokenSignature:
        def __init__(self, _name: str) -> None:
            raise RuntimeError("liboqs unavailable")

    monkeypatch.setitem(sys.modules, "oqs", SimpleNamespace(Signature=BrokenSignature))

    assert verify_mldsa65_signature(b"message", SIG_HEX, PUBKEY_HEX) is False


def test_verify_mldsa65_signature_valid_signature_true_when_oqs_available() -> None:
    oqs = _import_oqs_or_skip()
    signer = oqs.Signature("ML-DSA-65")
    public_key = signer.generate_keypair()
    message = b"phase-1571-mldsa-verification"
    signature = signer.sign(message)

    assert verify_mldsa65_signature(message, signature.hex(), public_key.hex()) is True


def test_verify_mldsa65_signature_wrong_signature_false_when_oqs_available() -> None:
    oqs = _import_oqs_or_skip()
    signer = oqs.Signature("ML-DSA-65")
    public_key = signer.generate_keypair()
    signature = signer.sign(b"original")

    assert verify_mldsa65_signature(b"tampered", signature.hex(), public_key.hex()) is False


def test_verify_mldsa65_signature_valid_signature_true_with_cryptography_backend() -> None:
    from cryptography.hazmat.primitives.asymmetric.mldsa import MLDSA65PrivateKey

    private_key = MLDSA65PrivateKey.generate()
    public_key = private_key.public_key().public_bytes_raw()
    message = b"phase-1571-cryptography-mldsa-verification"
    signature = private_key.sign(message)

    assert len(public_key.hex()) == _MLDSA_PK_HEX_LENGTH
    assert verify_mldsa65_signature(message, signature.hex(), public_key.hex()) is True


def test_verify_mldsa65_signature_wrong_message_false_with_cryptography_backend() -> None:
    from cryptography.hazmat.primitives.asymmetric.mldsa import MLDSA65PrivateKey

    private_key = MLDSA65PrivateKey.generate()
    public_key = private_key.public_key().public_bytes_raw()
    signature = private_key.sign(b"original")

    assert verify_mldsa65_signature(b"tampered", signature.hex(), public_key.hex()) is False


def test_dependency_token_exported() -> None:
    assert (
        pq_signature_verify.CDL_101_PQ_VERIFY_DEPENDENCY
        == "cdl_101_d2d_signed_gossip_envelope_phase_1570.v0.1"
    )


def test_registry_version_bumped_for_structured_entries() -> None:
    assert GOSSIP_PEER_REGISTRY_VERSION == "gossip_peer_registry_1571.v0.1"


def test_plain_string_entry_is_unverifiable() -> None:
    registry = GossipPeerRegistry(["https://a.example.com"])

    assert registry.get_peers() == ["https://a.example.com"]
    assert registry.get_peer_pubkey("peer-alpha") is None
    assert registry.get_peer_key_id("peer-alpha") is None
    assert registry.get_authorized_actor_ids("peer-alpha") == ()
    assert registry.is_peer_key_valid("peer-alpha", 0) is False


def test_structured_entry_exposes_pubkey_key_id_and_actor_mapping() -> None:
    registry = GossipPeerRegistry([_structured_peer(authorized_actor_ids=["agent-alpha", "panel-1"])])

    assert registry.get_peers() == ["https://a.example.com"]
    assert registry.get_peer_pubkey("peer-alpha") == PUBKEY_HEX
    assert registry.get_peer_key_id("peer-alpha") == "key-alpha"
    assert registry.get_authorized_actor_ids("peer-alpha") == ("agent-alpha", "panel-1")
    assert registry.is_actor_authorized_for_peer("peer-alpha", "agent-alpha") is True
    assert registry.is_actor_authorized_for_peer("peer-alpha", "agent-beta") is False


def test_structured_entry_validity_window() -> None:
    registry = GossipPeerRegistry([
        _structured_peer(valid_from_epoch=3, valid_until_epoch=5),
    ])

    assert registry.is_peer_key_valid("peer-alpha", 2) is False
    assert registry.is_peer_key_valid("peer-alpha", 3) is True
    assert registry.is_peer_key_valid("peer-alpha", 5) is True
    assert registry.is_peer_key_valid("peer-alpha", 6) is False


def test_mixed_plain_and_structured_entries_coexist() -> None:
    registry = GossipPeerRegistry([
        "https://plain.example.com",
        _structured_peer(endpoint="https://structured.example.com"),
    ])

    assert registry.get_peers() == ["https://plain.example.com", "https://structured.example.com"]
    assert registry.get_peer_pubkey("peer-alpha") == PUBKEY_HEX


def test_max_peers_still_enforced_for_structured_entries() -> None:
    peers = [
        _structured_peer(
            peer_id=f"peer-{index}",
            endpoint=f"https://node{index}.example.com",
            key_id=f"key-{index}",
            authorized_actor_ids=[f"agent-{index}"],
        )
        for index in range(MAX_PEERS + 1)
    ]

    with pytest.raises(ValueError, match="peer_registry_exceeds_max_peers"):
        GossipPeerRegistry(peers)


def test_structured_entry_rejects_bad_pubkey_length() -> None:
    with pytest.raises(ValueError, match="peer_mldsa_pubkey_hex_invalid"):
        GossipPeerRegistry([_structured_peer(mldsa_pubkey_hex="a" * 10)])


def test_structured_entry_rejects_too_long_peer_id() -> None:
    with pytest.raises(ValueError, match="peer_id_invalid"):
        GossipPeerRegistry([_structured_peer(peer_id="p" * 129)])


def test_structured_entry_requires_authorized_actor_ids() -> None:
    peer = _structured_peer()
    del peer["authorized_actor_ids"]

    with pytest.raises(ValueError, match="peer_authorized_actor_ids_required"):
        GossipPeerRegistry([peer])
