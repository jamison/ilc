# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import base64
import binascii
from pathlib import Path


def load_key_bytes_with_b64_fallback(key_path: Path) -> bytes:
    """
    Load key bytes, preferring strict base64 decode but falling back to raw bytes.

    This preserves existing CLI behavior for key-registry utilities:
    - If strict base64 decode succeeds and decoded size looks like key material, use it.
    - If strict base64 decode fails due to malformed encoding, return raw bytes.
    """
    content = key_path.read_bytes().strip()
    try:
        decoded = base64.b64decode(content, validate=True)
        if len(decoded) >= 16:
            return decoded
    except (binascii.Error, ValueError):
        # For non-base64 key files we intentionally preserve raw-byte fallback.
        return content
    return content
