# SPDX-License-Identifier: AGPL-3.0-only
"""CLI adapter for ``ilc upgrade``."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from ilc_core.release.upgrade_check import UpgradeCheckError, check_for_upgrade
from ilc_core.release.upgrade_state import read_upgrade_state


class UpgradeCliError(Exception):
    """Typed CLI error wrapper with stable token."""

    def __init__(self, token: str, message: str | None = None) -> None:
        super().__init__(message or token)
        self.token = token
        self.message = message or token


def run_upgrade_command(args: argparse.Namespace) -> dict[str, Any]:
    subcommand = getattr(args, "upgrade_subcommand", None)
    try:
        if subcommand == "check":
            return {
                "action": "upgrade-check",
                **check_for_upgrade(endpoint=str(args.endpoint or "") or None),
            }
        if subcommand == "status":
            state_path = Path(args.state_path) if getattr(args, "state_path", "") else None
            return {"action": "upgrade-status", **read_upgrade_state(path=state_path)}
    except UpgradeCheckError as exc:
        raise UpgradeCliError(exc.token, exc.message) from exc
    except ValueError as exc:
        token = str(exc).split(":", 1)[0]
        raise UpgradeCliError(token, str(exc)) from exc
    raise UpgradeCliError(f"unknown_upgrade_subcommand:{subcommand}")


__all__ = ["UpgradeCliError", "run_upgrade_command"]
