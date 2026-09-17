# SPDX-License-Identifier: AGPL-3.0-only
"""Regression coverage for GAP-PUBLIC-RC-EPOCH-00d-PREFLIGHT-FIX1."""

from __future__ import annotations

import subprocess
import sys
from decimal import Decimal


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


def test_ilc_quantum_single_source_matches_epoch_export() -> None:
    from ilc_core.economic_constants import ILC_QUANTUM as economic_quantum
    from ilc_core.epoch.epoch_emission_runtime import ILC_QUANTUM as epoch_quantum

    assert economic_quantum == Decimal("0.000000001")
    assert epoch_quantum is economic_quantum
