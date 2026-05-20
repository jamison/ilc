"""Regression tests for Phase 1407-Fix3 CDL-093 amendment and Q2 SIM."""

from __future__ import annotations

import json
from pathlib import Path


AMENDMENT_PATH = Path(
    "docs/specs/ilc_cdl_093_maintenance_lottery_pool_prelock_amendment_1407_fix3_v0.1.md"
)
SIM_DOC_PATH = Path(
    "docs/sims/ilc_cdl_093_maintenance_lottery_funding_fraction_sim_1407_fix3_v0.1.md"
)
SIM_JSON_PATH = Path(
    "out/ilc_cdl_093_maintenance_lottery_funding_fraction_sim_1407_fix3.json"
)
PROMPT_1408_PATH = Path(
    "docs/antigravity_tasks/antigravity_prompt__phase_1408_g8_cdl_093_maintenance_lottery_pool_ratification.md"
)
CDL_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_no_float_values(value: object) -> None:
    if isinstance(value, float):
        raise AssertionError(f"float value found in SIM JSON: {value!r}")
    if isinstance(value, dict):
        for child in value.values():
            _assert_no_float_values(child)
    if isinstance(value, list):
        for child in value:
            _assert_no_float_values(child)


def test_amendment_doc_present_with_required_tokens() -> None:
    text = _read(AMENDMENT_PATH)
    assert "cdl_093_prelock_amended_cdl_053_source_phase_1407_fix3" in text
    assert "maintenance_lottery_funding_fraction_sim_complete_phase_1407_fix3" in text


def test_amended_funding_source_is_cdl_053() -> None:
    text = _read(AMENDMENT_PATH)
    assert "`MAINTENANCE_LOTTERY_POOL_FUNDING_SOURCE`" in text
    assert "cdl_053_werner_local_productive_credit" in text
    assert "cdl_047_treasury_governance_quote_candidate" in text


def test_pending_sim_resolved_and_fraction_is_decimal_string() -> None:
    text = _read(AMENDMENT_PATH)
    assert "`MAINTENANCE_POOL_FUNDING_FRACTION_PENDING_SIM` | `true` | `false`" in text
    assert "`MAINTENANCE_LOTTERY_POOL_FUNDING_FRACTION` | `Decimal(\"0.00\")` | `Decimal(\"0.10\")`" in text


def test_sim_json_present_non_activating_and_decimal_string_values() -> None:
    payload = json.loads(_read(SIM_JSON_PATH))
    assert payload["sim_id"] == "cdl_093_maintenance_lottery_funding_fraction_sim_1407_fix3"
    assert payload["recommended_funding_fraction"] == "0.10"
    assert payload["werner_phi_bound_applied"] == "0.60"
    assert payload["direct_ecu_mint_authorized"] is False
    assert payload["ilc_settlement_authorized"] is False
    assert len(payload["scenario_results"]) == 27
    _assert_no_float_values(payload)


def test_no_random_import_in_fix3_sim_artifacts() -> None:
    assert "import random" not in _read(SIM_JSON_PATH)
    sim_text = _read(SIM_DOC_PATH)
    assert "No `import random`" in sim_text
    assert "no `import random`" in sim_text


def test_phase_1408_prompt_consumes_fix3_and_cdl_053() -> None:
    text = _read(PROMPT_1408_PATH)
    assert "ilc_cdl_093_maintenance_lottery_pool_prelock_amendment_1407_fix3_v0.1.md" in text
    assert "cdl_053_ratified_phase_1407_fix2" in text
    assert "cdl_093_prelock_amended_cdl_053_source_phase_1407_fix3" in text
    assert "maintenance_lottery_funding_fraction_sim_complete_phase_1407_fix3" in text
    assert "MAINTENANCE_LOTTERY_POOL_FUNDING_FRACTION = Decimal(\"0.10\")" in text


def test_cdl_093_remains_open_after_fix3() -> None:
    rows = [line for line in _read(CDL_PATH).splitlines() if line.startswith("| CDL-093 |")]
    assert len(rows) == 1
    assert "| open |" in rows[0]
    assert "| ratified |" not in rows[0]
