# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1573aa CDL-029 Amendment 2 evidence tests."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/specs/ilc_cdl_029_amendment_2_cmax_denominator_evidence_1573aa_v0.1.md"
CDL_REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
GOVERNOR = ROOT / "ilc_core/analysis/genesis_accrual_governor.py"


def test_amendment_evidence_document_exists_and_contains_required_tokens() -> None:
    text = EVIDENCE.read_text(encoding="utf-8")

    assert "Amendment number:** 2" in text
    assert "cdl_029_amendment_2_cmax_denominator_phase_1573aa" in text
    assert "genesis_share_ratio_denominator_constitutionalized_cmax_phase_1573aa" in text
    assert "genesis_obligatory_tranche_design_intent_constitutionalized_phase_1573aa" in text
    assert "C_max = 25,920,000 ILC" in text
    assert "genesis_cumulative_accrual / C_MAX_ILC" in text
    assert "1,296,000 ILC" in text
    assert "Amendment 1" in text


def test_cdl029_row_contains_amendment_2_fields() -> None:
    register = CDL_REGISTER.read_text(encoding="utf-8")
    cdl029 = next(line for line in register.splitlines() if line.startswith("| CDL-029 |"))

    assert "amendment_count: 2" in cdl029
    assert "amendment_2_phase: amendment_2_1573aa" in cdl029
    assert "amendment_2_date: 2026-07-10" in cdl029
    assert "amendment_2_token: cdl_029_amendment_2_cmax_denominator_phase_1573aa" in cdl029
    assert (
        "amendment_2_evidence_document: "
        "docs/specs/ilc_cdl_029_amendment_2_cmax_denominator_evidence_1573aa_v0.1.md"
    ) in cdl029
    assert "genesis_cumulative_accrual / C_MAX_ILC" in cdl029
    assert "Amendment 1 post-theta-hard residual routing remains unchanged" in cdl029


def test_current_governor_runtime_still_uses_total_cumulative_issuance_until_1573ab() -> None:
    governor = GOVERNOR.read_text(encoding="utf-8")

    assert 'required_keys = {"genesis_cumulative_accrual", "total_cumulative_issuance"}' in governor
    assert 'total_issuance = resolved_signal["total_cumulative_issuance"]' in governor
    assert 'return resolved_signal["genesis_cumulative_accrual"] / total_issuance' in governor
    assert "C_MAX_ILC" not in governor


def test_cmax_canonical_value_confirmed_in_cdl026_row() -> None:
    register = CDL_REGISTER.read_text(encoding="utf-8")
    cdl026 = next(line for line in register.splitlines() if line.startswith("| CDL-026 |"))

    assert "C_max = 25,920,000 ILC" in cdl026
    assert 'C_MAX_ILC = Decimal("25920000")' in cdl026
    assert "ratified_phase: 273" in cdl026


def test_cdl029_amendment_1_still_present() -> None:
    register = CDL_REGISTER.read_text(encoding="utf-8")
    cdl029 = next(line for line in register.splitlines() if line.startswith("| CDL-029 |"))

    assert "amendment_phase: 1351a" in cdl029
    assert "amendment_token: cdl_029_post_theta_hard_dust_routing_1351a" in cdl029
    assert "sub-quantum residual" in cdl029
    assert "performer pool" in cdl029
