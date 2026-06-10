from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from ilc_core.epoch.fee_burn_split_runtime import (
    FEE_BURN_RATIO,
    PRODUCTION_FEE_BURN_NOT_ACTIVATED_TOKEN,
    require_cdl_028_fee_burn_ratio,
    require_production_fee_burn_activation,
)


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/specs/ilc_adaptive_fee_burn_ratio_spec_1549p_v0.1.md"
SIM_REPORT = ROOT / "docs/sims/ilc_adaptive_fee_burn_ratio_sim_1549p_v0.1.md"
SIM_JSON = ROOT / "docs/sims/ilc_adaptive_fee_burn_ratio_sim_1549p_v0.1.json"
REGISTER = ROOT / "docs/specs/ilc_open_obligation_register_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
RUNTIME = ROOT / "ilc_core/epoch/fee_burn_split_runtime.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def walk_values(value: Any) -> list[Any]:
    if isinstance(value, dict):
        values: list[Any] = []
        for item in value.values():
            values.extend(walk_values(item))
        return values
    if isinstance(value, list):
        values = []
        for item in value:
            values.extend(walk_values(item))
        return values
    return [value]


def test_phase_1549p_spec_and_sim_report_record_tokens_and_non_activation() -> None:
    spec = read(SPEC)
    report = read(SIM_REPORT)

    for text in (spec, report):
        for needle in (
            "obl_028_adaptive_fee_burn_sim_committed_phase_1549p",
            "obl_028_closed_phase_1549p",
            "fee_burn_runtime_unchanged_phase_1549p",
        ):
            assert needle in text

    assert "obl_028_adaptive_fee_burn_spec_committed_phase_1549p" in spec
    assert "FEE_BURN_RATIO = Decimal(\"0.10\")" in spec
    assert "This specification does not change CDL-028" in spec
    assert "This SIM does not change CDL-028" in report


def test_phase_1549p_sim_json_is_sorted_key_finite_and_deterministic() -> None:
    raw = read(SIM_JSON)
    payload = json.loads(raw)

    assert raw == json.dumps(payload, indent=2, sort_keys=True) + "\n"
    assert "NaN" not in raw
    assert "Infinity" not in raw
    assert "-Infinity" not in raw
    assert all(not isinstance(value, float) for value in walk_values(payload))

    scenarios = {item["label"]: item for item in payload["scenarios"]}
    assert scenarios["early_growth"]["epoch_path"] == ["0.100", "0.095"]
    assert scenarios["transition_balanced"]["epoch_path"] == [
        "0.100",
        "0.090",
        "0.080",
        "0.075",
    ]
    assert scenarios["late_healthy"]["target_ratio"] == "0.055"
    assert scenarios["late_low_velocity"]["target_ratio"] == "0.050"

    for item in payload["scenarios"]:
        assert Decimal("0.05") <= Decimal(item["target_ratio"]) <= Decimal("0.10")
        assert item["converged_ratio"] == item["epoch_path"][-1]


def test_phase_1549p_fee_burn_runtime_still_enforces_cdl028_fixed_ratio() -> None:
    assert FEE_BURN_RATIO == Decimal("0.10")
    assert require_cdl_028_fee_burn_ratio("0.10") == Decimal("0.10")

    with pytest.raises(ValueError, match="fee_burn_ratio_must_equal_cdl_028"):
        require_cdl_028_fee_burn_ratio("0.05")

    with pytest.raises(ValueError, match=PRODUCTION_FEE_BURN_NOT_ACTIVATED_TOKEN):
        require_production_fee_burn_activation(None)

    runtime = read(RUNTIME)
    assert 'FEE_BURN_RATIO = Decimal("0.10")' in runtime
    assert "adaptive_fee_burn" not in runtime


def test_phase_1549p_obl028_closed_without_closing_obl029() -> None:
    register = read(REGISTER)
    row = next(line for line in register.splitlines() if line.startswith("| OBL-028 |"))
    assert "| closed |" in row
    assert "obl_028_closed_phase_1549p" in row
    assert "ilc_adaptive_fee_burn_ratio_spec_1549p_v0.1.md" in row
    assert "ilc_adaptive_fee_burn_ratio_sim_1549p_v0.1.json" in row

    obl029 = next(line for line in register.splitlines() if line.startswith("| OBL-029 |"))
    assert "closed_phase_1549p" not in obl029

    status = read(STATUS)
    assert "## Phase 1549p - OBL-028 Adaptive Fee-Burn Ratio Spec and SIM" in status
    assert "obl_028_adaptive_fee_burn_spec_committed_phase_1549p" in status
    assert "No fee-burn runtime change" in status
