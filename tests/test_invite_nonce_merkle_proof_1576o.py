from __future__ import annotations

import hashlib

import pytest

from ilc_core.genesis.invitation_provenance_record import (
    INVITE_NONCE_BYTES,
    INVITE_NONCE_LEAF_DOMAIN,
    INVITE_NONCE_NODE_DOMAIN,
    InvitationProvenanceError,
    build_invite_batch_record,
    invite_nonce_merkle_root,
    verify_nonce_membership_proof,
)
from ilc_core.sidecars.openclaw_invite_bootstrap import verify_invite_bootstrap


PROFILE = "openclaw_public_rc_bootstrap"


def _leaf(nonce: bytes) -> bytes:
    return hashlib.sha256(INVITE_NONCE_LEAF_DOMAIN + nonce).digest()


def _root(left: bytes, right: bytes) -> str:
    return hashlib.sha256(INVITE_NONCE_NODE_DOMAIN + left + right).hexdigest()


def _verify(
    *,
    nonce: bytes,
    root: str,
    count: int,
    proof: tuple[dict[str, object], ...],
) -> None:
    verify_nonce_membership_proof(
        nonce_bytes=nonce,
        nonce_merkle_root=root,
        count=count,
        proof=proof,
    )


def test_valid_proof_single_nonce() -> None:
    nonce = b"a" * 32
    _verify(nonce=nonce, root=_leaf(nonce).hex(), count=1, proof=())


def test_nonce_bytes_must_be_exactly_32_bytes() -> None:
    assert INVITE_NONCE_BYTES == 32
    with pytest.raises(InvitationProvenanceError, match="invite_nonce_invalid"):
        invite_nonce_merkle_root((b"a",))
    with pytest.raises(InvitationProvenanceError, match="invite_nonce_invalid"):
        build_invite_batch_record(
            inviter_cid="genesis_agent:01",
            batch_id="short-nonce",
            count=1,
            created_epoch=0,
            inviter_sig="genesis",
            nonces=(b"a",),
        )
    with pytest.raises(InvitationProvenanceError, match="invite_nonce_invalid"):
        verify_nonce_membership_proof(
            nonce_bytes=b"a",
            nonce_merkle_root="00" * 32,
            count=1,
            proof=(),
        )


def test_valid_proof_two_nonces_left() -> None:
    left = b"a" * 32
    right = b"b" * 32
    _verify(
        nonce=left,
        root=_root(_leaf(left), _leaf(right)),
        count=2,
        proof=({"sibling": _leaf(right).hex(), "position": "right"},),
    )


def test_valid_proof_two_nonces_right() -> None:
    left = b"a" * 32
    right = b"b" * 32
    _verify(
        nonce=right,
        root=_root(_leaf(left), _leaf(right)),
        count=2,
        proof=({"sibling": _leaf(left).hex(), "position": "left"},),
    )


def test_invalid_sibling_hex() -> None:
    with pytest.raises(InvitationProvenanceError, match="invite_nonce_membership_proof_invalid"):
        _verify(
            nonce=b"a" * 32,
            root="00" * 32,
            count=2,
            proof=({"sibling": "not-hex", "position": "right"},),
        )


def test_wrong_root_rejected() -> None:
    left = b"a" * 32
    right = b"b" * 32
    with pytest.raises(InvitationProvenanceError, match="invite_nonce_membership_mismatch"):
        _verify(
            nonce=left,
            root="00" * 32,
            count=2,
            proof=({"sibling": _leaf(right).hex(), "position": "right"},),
        )


def test_tampered_position_rejected() -> None:
    left = b"a" * 32
    right = b"b" * 32
    with pytest.raises(InvitationProvenanceError, match="invite_nonce_membership_mismatch"):
        _verify(
            nonce=left,
            root=_root(_leaf(left), _leaf(right)),
            count=2,
            proof=({"sibling": _leaf(right).hex(), "position": "left"},),
        )


def test_empty_proof_multi_nonce_rejected() -> None:
    left = b"a" * 32
    right = b"b" * 32
    with pytest.raises(InvitationProvenanceError, match="invite_nonce_membership_proof_required"):
        _verify(nonce=left, root=_root(_leaf(left), _leaf(right)), count=2, proof=())


def test_proof_wrong_length_rejected() -> None:
    left = b"a" * 32
    right = b"b" * 32
    extra = b"c" * 32
    with pytest.raises(InvitationProvenanceError, match="invite_nonce_membership_proof_length_invalid"):
        _verify(
            nonce=left,
            root=_root(_leaf(left), _leaf(right)),
            count=2,
            proof=(
                {"sibling": _leaf(right).hex(), "position": "right"},
                {"sibling": _leaf(extra).hex(), "position": "right"},
            ),
        )


def test_sidecar_mirror_rejects_wrong_proof_length() -> None:
    left = b"a" * 32
    right = b"b" * 32
    bundle = {
        "intended_epoch": 0,
        "intended_profile": PROFILE,
        "invite_batch_record": {
            "batch_id": "batch",
            "count": 2,
            "created_epoch": 0,
            "inviter_cid": "genesis_agent:01",
            "inviter_sig": "synthetic-local-signature",
            "nonce_merkle_root": invite_nonce_merkle_root((left, right)),
        },
        "nonce_membership_proof": [
            {"sibling": _leaf(right).hex(), "position": "right"},
            {"sibling": _leaf(right).hex(), "position": "right"},
        ],
        "private_invite_nonce": left.hex(),
    }
    decision = verify_invite_bootstrap(bundle, expected_profile=PROFILE, current_epoch=0, persist_nullifier=False)
    assert decision.bootstrap_allowed is False
    assert decision.defect_token == "nonce_membership_proof_length_invalid"
