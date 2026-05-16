from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from ilc_core.epoch import (
    CDL_025_031_047_054_083_STACK_VERIFIED_TOKEN,
    CDL_031_RUNTIME_DEFERRED_TOKEN,
    DOUBLE_ENTRY_LEDGER_INVARIANT_VERIFIED_TOKEN,
    ISSUANCE_ECONOMICS_INTEGRATION_GATE_PASS,
    ISSUANCE_ECONOMICS_INTEGRATION_GATE_TOKEN,
    ISSUANCE_ECONOMICS_INTEGRATION_GATE_VERDICT_RECORDED_TOKEN,
    PRODUCTION_MINTING_NOT_ACTIVATED_PHASE_1352_TOKEN,
    QUOTE_LEVEL_CONSERVATION_SCOPE_TOKEN,
    build_issuance_economics_integration_gate_report,
    verify_issuance_economics_integration_gate,
)


ROOT = Path(__file__).resolve().parents[1]
GATE_RUNTIME = ROOT / "ilc_core/epoch/issuance_economics_integration_gate.py"
GATE_REPORT = ROOT / "docs/specs/ilc_issuance_economics_integration_gate_report_1352_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1352_issuance_economics_integration_gate_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
INDEX = ROOT / "docs/PLANNING_INDEX.md"
PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1352_g8_issuance_economics_integration_gate.md"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1352_gate_report_passes_and_records_tokens() -> None:
    report = verify_issuance_economics_integration_gate()

    assert report.verdict == ISSUANCE_ECONOMICS_INTEGRATION_GATE_PASS
    assert report.gate_token == "issuance_economics_integration_gate_phase_1352.v0.1"
    assert report.gate_token == ISSUANCE_ECONOMICS_INTEGRATION_GATE_TOKEN
    assert report.stack_token == CDL_025_031_047_054_083_STACK_VERIFIED_TOKEN
    assert report.invariant_token == DOUBLE_ENTRY_LEDGER_INVARIANT_VERIFIED_TOKEN
    assert report.verdict_token == ISSUANCE_ECONOMICS_INTEGRATION_GATE_VERDICT_RECORDED_TOKEN
    assert report.production_not_activated_token == PRODUCTION_MINTING_NOT_ACTIVATED_PHASE_1352_TOKEN
    assert report.quote_scope_token == QUOTE_LEVEL_CONSERVATION_SCOPE_TOKEN
    assert report.blocking_reason == ""


def test_phase_1352_stack_verification_covers_each_cdl_and_cdl_031_deferral() -> None:
    report = build_issuance_economics_integration_gate_report()
    rows = {row.cdl: row for row in report.stack_rows}

    assert set(rows) == {
        "CDL-025",
        "CDL-026",
        "CDL-027",
        "CDL-028",
        "CDL-029",
        "CDL-030",
        "CDL-031",
        "CDL-047",
        "CDL-054",
        "CDL-083",
    }
    assert rows["CDL-031"].required_token == CDL_031_RUNTIME_DEFERRED_TOKEN
    assert rows["CDL-031"].status == "confirmed_deferred_not_phase_1352_runtime"
    assert all(row.status.startswith("confirmed") for row in report.stack_rows)


def test_phase_1352_quote_level_conservation_passes_for_three_epoch_boundaries() -> None:
    report = build_issuance_economics_integration_gate_report()
    results_by_epoch: dict[int, list[str]] = {}

    for result in report.conservation_results:
        assert result.ok is True
        assert result.debits_ilc == result.credits_ilc
        assert result.debits_ilc >= Decimal("0")
        assert result.debits_ilc.is_finite()
        assert result.credits_ilc.is_finite()
        results_by_epoch.setdefault(result.synthetic_epoch, []).append(result.surface)

    assert sorted(results_by_epoch) == [0, 47, 96]
    assert all(len(surfaces) == 7 for surfaces in results_by_epoch.values())
    assert "cdl_025_026_027_emission_cap_quote" in results_by_epoch[96]
    assert "cdl_029_allocation_distribution_quote" in results_by_epoch[47]


def test_phase_1352_gate_runtime_does_not_call_production_activation_functions() -> None:
    runtime = _read(GATE_RUNTIME)

    forbidden_calls = (
        "require_production_minting_activation(",
        "require_production_fee_burn_activation(",
        "require_production_allocation_distribution_activation(",
        "require_production_treasury_activation(",
        "require_production_validator_reward_distribution_activation(",
        "require_production_ejected_stake_distribution_activation(",
        "require_live_price_adjustment_activation(",
    )
    for call in forbidden_calls:
        assert call not in runtime

    assert "production_minting_not_activated_phase_1352" in runtime
    assert "phase_1352_quote_level_double_entry_conservation_not_live_ledger_settlement" in runtime
    assert "validator_treasury_budget" not in runtime
    assert "TREASURY_EPOCH_BUDGET_BINDING_VERIFIED_TOKEN" in runtime


def test_phase_1352_docs_record_gate_verdict_and_non_activation() -> None:
    for path in (GATE_REPORT, WALKTHROUGH, STATUS, INDEX, PROMPT):
        text = _read(path)
        assert "issuance_economics_integration_gate_phase_1352.v0.1" in text
        assert "issuance_economics_integration_gate_pass" in text
        assert "cdl_025_031_047_054_083_stack_verified_phase_1352" in text
        assert "double_entry_ledger_invariant_verified_phase_1352" in text
        assert "production_minting_not_activated_phase_1352" in text

    report = _read(GATE_REPORT)
    assert "quote-level double-entry conservation" in report
    assert "CDL-031" in report
    assert "confirmed_deferred_not_phase_1352_runtime" in report
