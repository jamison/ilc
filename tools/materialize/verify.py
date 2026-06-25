# SPDX-License-Identifier: AGPL-3.0-only
"""Verify a materialized ILC tree against a materialization manifest."""

from __future__ import annotations

from ilc_core.distribution.materialization import cli_verify


if __name__ == "__main__":  # pragma: no cover - CLI wrapper
    raise SystemExit(cli_verify())
