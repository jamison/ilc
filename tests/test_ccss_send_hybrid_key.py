from __future__ import annotations

import json
from pathlib import Path

import pytest

from ilc_core.ccss import runtime
from ilc_core.ccss.contact_envelope import (
    CONTACT_ENVELOPE_AEAD_BYTES,
    CONTACT_ENVELOPE_BYTES,
    CONTACT_ENVELOPE_MAX_MESSAGE_BYTES,
    CONTACT_ENVELOPE_NONCE_BYTES,
    CONTACT_ENVELOPE_PLAINTEXT_BYTES,
    CONTACT_ENVELOPE_TAG_BYTES,
    seal_contact_envelope,
)
from ilc_core.network.d2d import interface as d2d_interface
from ilc_core.network.d2d.spectral_route_token import (
    CCSS_SPECTRAL_HYBRID_CIPHERTEXT_BYTES,
    CCSS_SPECTRAL_HYBRID_PUBLIC_KEY_BYTES,
    CCSS_SPECTRAL_01_NOT_ACTIVATED,
    generate_hybrid_recipient_keypair,
    kem_encap,
)


def test_contact_envelope_fixed_size_arithmetic() -> None:
    assert CCSS_SPECTRAL_HYBRID_CIPHERTEXT_BYTES == 1120
    assert CONTACT_ENVELOPE_NONCE_BYTES == 12
    assert CONTACT_ENVELOPE_AEAD_BYTES == 3024
    assert CONTACT_ENVELOPE_PLAINTEXT_BYTES + CONTACT_ENVELOPE_TAG_BYTES == 3024
    assert CONTACT_ENVELOPE_BYTES == 4156
    assert CCSS_SPECTRAL_HYBRID_CIPHERTEXT_BYTES + 12 + 3024 == CONTACT_ENVELOPE_BYTES
    assert CONTACT_ENVELOPE_MAX_MESSAGE_BYTES == 2000


def test_contact_envelope_seals_to_hybrid_key_without_route_token_activation() -> None:
    public_key, _private_key = generate_hybrid_recipient_keypair()

    envelope = seal_contact_envelope(b"hello hybrid", public_key)

    assert len(public_key) == CCSS_SPECTRAL_HYBRID_PUBLIC_KEY_BYTES
    assert len(envelope) == CONTACT_ENVELOPE_BYTES
    assert CCSS_SPECTRAL_01_NOT_ACTIVATED is True
    with pytest.raises(Exception, match="ccss_spectral_01_not_activated"):
        kem_encap(public_key)


def test_hybrid_envelope_rejects_oversized_message() -> None:
    public_key, _private_key = generate_hybrid_recipient_keypair()
    message = b"x" * (CONTACT_ENVELOPE_MAX_MESSAGE_BYTES + 1)

    with pytest.raises(ValueError, match="message_too_long:2001:2000"):
        seal_contact_envelope(message, public_key)


def test_genesis_imported_hybrid_contact_is_pending_not_configured(tmp_path: Path) -> None:
    result = runtime.import_genesis_contact(home=tmp_path, overwrite=True)
    contacts = runtime.list_contacts(home=tmp_path)

    assert result["ok"] is True
    assert not hasattr(d2d_interface, "d2d_send_to_agent")
    assert contacts[0]["id"] == "genesis"
    assert contacts[0]["configured"] is False
    assert contacts[0]["transports"] == ["d2d(pending)"]


def test_send_genesis_hybrid_key_fails_closed_without_d2d_adapter(tmp_path: Path) -> None:
    runtime.import_genesis_contact(home=tmp_path, overwrite=True)

    with pytest.raises(runtime.CCSSRuntimeError, match="d2d_transport_not_reachable:genesis"):
        runtime.send_message("genesis", "hello from phase 1576g", home=tmp_path)


def test_legacy_x25519_contact_still_seals_before_endpoint_requirement(tmp_path: Path) -> None:
    runtime.generate_identity(home=tmp_path, contact_id="legacy", name="Legacy")
    identity = json.loads((Path(tmp_path) / "identity.json").read_text(encoding="utf-8"))
    runtime.add_contact(
        home=tmp_path,
        contact_id="legacy-recipient",
        name="Legacy Recipient",
        public_key_hex=identity["ccss_recipient_pubkey"],
        overwrite=True,
    )

    with pytest.raises(runtime.CCSSRuntimeError, match="contact_endpoint_not_configured"):
        runtime.send_message("legacy-recipient", "hello legacy", home=tmp_path)
