# SPDX-License-Identifier: AGPL-3.0-only
"""Release-authority key helpers for homoiconic upgrade checks."""

from __future__ import annotations

import re

from ilc_core.release.update_signature_verifier import (
    PUBLIC_RC_RELEASE_SIGNER_PUBLIC_KEY_HEX,
)


_ED25519_PUBLIC_KEY_HEX_RE = re.compile(r"^[0-9a-f]{64}$")


def release_signer_public_key_hex() -> str:
    """Return the embedded Phase 1335 Ed25519 release-signing public key."""

    key = PUBLIC_RC_RELEASE_SIGNER_PUBLIC_KEY_HEX
    if _ED25519_PUBLIC_KEY_HEX_RE.fullmatch(key) is None:
        raise ValueError("release_authority_pubkey_invalid")
    return key


__all__ = ["PUBLIC_RC_RELEASE_SIGNER_PUBLIC_KEY_HEX", "release_signer_public_key_hex"]
