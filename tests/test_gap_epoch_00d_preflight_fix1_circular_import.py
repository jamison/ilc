# SPDX-License-Identifier: AGPL-3.0-only
"""Regression coverage for GAP-PUBLIC-RC-EPOCH-00d-PREFLIGHT-FIX1."""

from __future__ import annotations

import subprocess
import sys


CASES = [
    "from ilc_core.ledger import ecu_ilc_lifecycle_runtime",
    "import ilc_core.ledger.ecu_ilc_lifecycle_runtime",
    "from ilc_core.protocol.public_wallet_runtime import PublicWalletRuntime",
    "import ilc_core.epoch.epoch_distribution_writer",
]


def test_fresh_process_imports_succeed() -> None:
    for statement in CASES:
        result = subprocess.run(
            [sys.executable, "-c", statement],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"Fresh-process import failed for: {statement!r}\n"
            f"stderr: {result.stderr}"
        )
