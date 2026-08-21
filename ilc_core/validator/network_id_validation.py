# SPDX-License-Identifier: AGPL-3.0-only
"""Shared validator network-id validation.

Validator-facing runtimes use the same conservative network-id grammar so
endpoint assertions and admission records cannot diverge on accepted IDs.
"""

from __future__ import annotations

import re
from typing import Any

_NETWORK_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{1,62}$")


def require_validator_network_id(value: Any, *, token: str) -> str:
    if not isinstance(value, str) or not _NETWORK_ID_RE.fullmatch(value):
        raise ValueError(token)
    return value


__all__ = ["require_validator_network_id"]
