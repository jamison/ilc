# SPDX-License-Identifier: AGPL-3.0-only
"""Human-readable relay invite code generation and validation."""

from __future__ import annotations

import re
import secrets
from typing import Final


ALPHABET: Final[str] = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
INVITE_CODE_RE: Final[re.Pattern[str]] = re.compile(
    r"^ILC-[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}$"
)


def checksum_char(payload: str) -> str:
    """Return the checksum character for a seven-character payload."""

    if not isinstance(payload, str) or len(payload) != 7:
        raise ValueError("invite_code_payload_invalid")
    total = 0
    for index, char in enumerate(payload):
        try:
            alphabet_index = ALPHABET.index(char)
        except ValueError as exc:
            raise ValueError("invite_code_payload_invalid") from exc
        total += alphabet_index * (index + 1)
    return ALPHABET[total % len(ALPHABET)]


def generate_code() -> str:
    """Generate a cryptographically random ``ILC-XXXX-XXXX`` invite code."""

    payload = "".join(ALPHABET[secrets.randbelow(len(ALPHABET))] for _ in range(7))
    body = payload + checksum_char(payload)
    return f"ILC-{body[:4]}-{body[4:]}"


def validate_code(code: str) -> bool:
    """Return True only when ``code`` has valid structure and checksum."""

    if not isinstance(code, str) or INVITE_CODE_RE.fullmatch(code) is None:
        return False
    body = code.removeprefix("ILC-").replace("-", "")
    payload = body[:7]
    return body[7] == checksum_char(payload)


__all__ = ["ALPHABET", "INVITE_CODE_RE", "checksum_char", "generate_code", "validate_code"]
