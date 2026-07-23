from __future__ import annotations

from copy import deepcopy

import pytest

import ilc_core.epoch.genesis_tranche_reconciliation_runtime as reconciliation_runtime
from ilc_core.epoch.genesis_tranche_reconciliation_runtime import (
    GENESIS_TRANCHE_REALIZATION_CONTROLLER_DEFERRED_TOKEN,
    GENESIS_TRANCHE_REALIZATION_MECHANISM_CLOSED_TOKEN,
    build_genesis_tranche_reconciliation_from_rehearsal_record,
    verify_genesis_tranche_reconciliation_record,
)
from tests.test_phase_1568_fix2l_rehearsal_economics_record import _record


CDL_REGISTER_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"


def test_phase_1575p_quote_uses_closed_realization_mechanism_token() -> None:
    record = _record()
    reconciliation = build_genesis_tranche_reconciliation_from_rehearsal_record(record)
    tokens = set(reconciliation["tokens"])

    assert GENESIS_TRANCHE_REALIZATION_MECHANISM_CLOSED_TOKEN in tokens
    assert GENESIS_TRANCHE_REALIZATION_CONTROLLER_DEFERRED_TOKEN not in tokens

    verification = verify_genesis_tranche_reconciliation_record(reconciliation)
    assert verification["verified"] is True


def test_phase_1575p_deferred_token_not_in_required_tokens() -> None:
    record = _record()
    reconciliation = build_genesis_tranche_reconciliation_from_rehearsal_record(record)
    tokens = list(reconciliation["tokens"])
    tokens.remove(GENESIS_TRANCHE_REALIZATION_MECHANISM_CLOSED_TOKEN)
    tokens.append(GENESIS_TRANCHE_REALIZATION_CONTROLLER_DEFERRED_TOKEN)
    stale_record = deepcopy(reconciliation)
    stale_record["tokens"] = tokens

    with pytest.raises(
        ValueError,
        match="genesis_tranche_reconciliation_tokens_missing_phase_1568_fix2q",
    ):
        verify_genesis_tranche_reconciliation_record(stale_record)


def test_phase_1575p_deferred_token_is_not_exported_from_runtime_all() -> None:
    assert (
        "GENESIS_TRANCHE_REALIZATION_MECHANISM_CLOSED_TOKEN"
        in reconciliation_runtime.__all__
    )
    assert (
        "GENESIS_TRANCHE_REALIZATION_CONTROLLER_DEFERRED_TOKEN"
        not in reconciliation_runtime.__all__
    )


def test_phase_1575p_cdl029_amendment_3_records_flat_cap_mechanism() -> None:
    with open(CDL_REGISTER_PATH, encoding="utf-8") as handle:
        register = handle.read()

    cdl029_rows = [
        line
        for line in register.splitlines()
        if line.startswith("| CDL-029 | CDL-005 / CDL-011 |")
    ]
    assert len(cdl029_rows) == 1
    row = cdl029_rows[0]

    assert "amendment_count: 3" in row
    assert "amendment_3_phase: amendment_3_1575p" in row
    assert (
        "amendment_3_token: cdl_029_amendment_3_ratified_realization_mechanism_phase_1575p"
        in row
    )
    assert "no separate realization controller module is implemented or required" in row
    assert "taper multiplier computed by the genesis accrual governor is advisory" in row
