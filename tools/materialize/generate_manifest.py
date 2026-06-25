# SPDX-License-Identifier: AGPL-3.0-only
"""Generate an ILC public-RC materialization manifest from a package profile."""

from __future__ import annotations

from ilc_core.distribution.materialization import cli_generate_manifest


if __name__ == "__main__":  # pragma: no cover - CLI wrapper
    raise SystemExit(cli_generate_manifest())
