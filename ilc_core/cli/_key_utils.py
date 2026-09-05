# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import base64
import binascii
import re
from pathlib import Path

_BASE64ISH_RE = re.compile(rb"^[A-Za-z0-9+/=_-]+$")
_BASE64_PREFIX = b"base64:"
MIN_KEY_BYTES = 16
MAX_KEY_BYTES = 4096


def load_key_bytes_with_b64_fallback(key_path: Path) -> bytes:
    """
    Load key bytes, preferring strict base64 decode but falling back to raw bytes.

    This preserves existing CLI behavior for key-registry utilities:
    - If strict base64 decode succeeds and decoded size looks like key material, use it.
    - If strict base64 decode fails due to malformed encoding, return raw bytes.
    """
    content = key_path.read_bytes().strip()
    if not content:
        raise ValueError("key_material_empty")
    if len(content) > MAX_KEY_BYTES:
        raise ValueError("key_material_too_large")
    declared_base64 = content.lower().startswith(_BASE64_PREFIX)
    encoded = content[len(_BASE64_PREFIX) :] if declared_base64 else content
    try:
        decoded = base64.b64decode(encoded, validate=True)
        if MIN_KEY_BYTES <= len(decoded) <= MAX_KEY_BYTES:
            return decoded
    except (binascii.Error, ValueError):
        if declared_base64 or b"=" in content:
            raise ValueError("key_material_malformed_base64")
        # For clearly non-base64 key files we intentionally preserve raw-byte fallback.
        return content
    if declared_base64 or b"=" in content:
        raise ValueError("key_material_decoded_length_invalid")
    return content
