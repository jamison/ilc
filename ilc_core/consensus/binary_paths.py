# SPDX-License-Identifier: AGPL-3.0-only
"""Discovery helpers for packaged ILC consensus helper binaries."""

from __future__ import annotations

import os
from pathlib import Path
import re
from typing import Final

ILC_CONSENSUS_BIN_DIR_ENV: Final[str] = "ILC_CONSENSUS_BIN_DIR"
_BINARY_NAME_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9_.-]+$")
_ALLOWED_BINARY_NAMES: Final[frozenset[str]] = frozenset(
    {
        "bls_verify_digest",
        "invite_pop_bls",
        "keygen",
        "ilc_p2p_bridge",
        "validator_endpoint_assertion_bls",
        "validator_harness",
    }
)


def installed_consensus_binary_path(binary_name: str) -> Path | None:
    """Return an executable packaged helper binary, if one is installed.

    Public installs place Rust consensus helpers in ``~/.ilc/bin``. The optional
    environment override is operator-local and exists for tests or managed
    deployments where HOME is not the desired binary root.
    """

    if (
        not isinstance(binary_name, str)
        or _BINARY_NAME_RE.fullmatch(binary_name) is None
        or binary_name not in _ALLOWED_BINARY_NAMES
    ):
        raise ValueError("consensus_binary_name_invalid")
    candidates: list[Path] = []
    env_dir = os.environ.get(ILC_CONSENSUS_BIN_DIR_ENV)
    if env_dir is not None and env_dir.strip():
        candidates.append(Path(env_dir).expanduser() / binary_name)
    candidates.append(Path.home() / ".ilc" / "bin" / binary_name)
    for candidate in candidates:
        try:
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return candidate
        except OSError:
            continue
    return None


def installed_consensus_binary_command(binary_name: str) -> tuple[str, ...] | None:
    path = installed_consensus_binary_path(binary_name)
    if path is None:
        return None
    return (str(path),)


__all__ = [
    "ILC_CONSENSUS_BIN_DIR_ENV",
    "installed_consensus_binary_command",
    "installed_consensus_binary_path",
]
