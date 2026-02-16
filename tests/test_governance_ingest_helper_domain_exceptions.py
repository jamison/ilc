from __future__ import annotations

import pytest

from ilc_core.exceptions import GovernanceIngestValidationError
from ilc_core.protocol import ilc_cluster_a_ingest as ingest


def test_emit_invalid_error_code_raises_domain_exception() -> None:
    errors: list[str] = []
    details: list[dict[str, object]] = []
    with pytest.raises(GovernanceIngestValidationError, match="unapproved_error_code:bad_code"):
        ingest._emit(errors, details, "bad_code")


def test_verify_signature_invalid_public_key_raises_domain_exception() -> None:
    if not ingest._HAS_CRYPTO:
        pytest.skip("cryptography unavailable in runtime")

    with pytest.raises(GovernanceIngestValidationError, match="invalid_public_key_bytes"):
        ingest.verify_ed25519_signature(b"short", b"payload", "00")


def test_verify_signature_invalid_hex_raises_domain_exception() -> None:
    if not ingest._HAS_CRYPTO:
        pytest.skip("cryptography unavailable in runtime")

    with pytest.raises(GovernanceIngestValidationError, match="invalid_signature_hex"):
        ingest.verify_ed25519_signature(b"\x00" * 32, b"payload", "zz")


def test_verify_signature_invalid_length_raises_domain_exception() -> None:
    if not ingest._HAS_CRYPTO:
        pytest.skip("cryptography unavailable in runtime")

    with pytest.raises(GovernanceIngestValidationError, match="invalid_signature_length"):
        ingest.verify_ed25519_signature(b"\x00" * 32, b"payload", "00")
