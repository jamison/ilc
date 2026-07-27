# SPDX-License-Identifier: AGPL-3.0-only
"""Module entry point for `python -m ilc_core.cli`."""

from __future__ import annotations

from ilc_core.cli.main import main


if __name__ == "__main__":
    raise SystemExit(main())
