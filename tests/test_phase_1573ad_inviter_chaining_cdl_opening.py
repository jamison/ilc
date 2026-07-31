# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from pathlib import Path


CDL_REGISTER = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
OPENING_DOC = Path("docs/specs/ilc_cdl_102_inviter_chaining_economics_opening_1573ad_v0.1.md")


def _register_text() -> str:
    return CDL_REGISTER.read_text(encoding="utf-8")


def test_phase_1573ad_cdl_102_row_preserves_opening_after_ratification() -> None:
    text = _register_text()
    row = next(line for line in text.splitlines() if line.startswith("| CDL-102 |"))

    assert "Inviter-Chaining Economics" in row
    assert " | ratified | " in row
    assert "opened_phase: 1573ad" in row
    assert "opening_token: cdl_102_inviter_chaining_economics_opened_phase_1573ad" in row
    assert "prelock_phase: 1573aq" in row
    assert "prelock_token: inviter_chaining_cdl_prelocked_phase_1573aq" in row
    assert "ratified_phase: 1576m" in row
    assert "ratification_token: cdl_102_ratified_phase_1576m" in row
    assert "economics_activation_status: not_authorized" in row
    assert "public_path_status: blocked" in row


def test_phase_1573ad_opening_token_present_once_in_cdl_row() -> None:
    text = _register_text()
    assert text.count("cdl_102_inviter_chaining_economics_opened_phase_1573ad") == 1


def test_phase_1573ad_cdl_091_remains_jury_incentive_economics() -> None:
    row = next(line for line in _register_text().splitlines() if line.startswith("| CDL-091 |"))

    assert "Jury incentive economics" in row
    assert "| ratified |" in row
    assert "ratified_phase: 1400" in row
    assert "cdl_091_ratified_phase_1400" in row
    assert "inviter-chaining" not in row.lower()


def test_phase_1573ad_opening_evidence_document_exists_and_records_questions() -> None:
    text = OPENING_DOC.read_text(encoding="utf-8")

    assert "Decision ID: CDL-102" in text
    assert "cdl_102_inviter_chaining_economics_opened_phase_1573ad" in text
    assert "CDL-091 is already ratified as Jury Incentive Economics" in text
    for marker in ("Q1:", "Q2:", "Q3:", "Q4:"):
        assert marker in text


def test_phase_1573ad_opening_evidence_non_activation_boundary() -> None:
    text = OPENING_DOC.read_text(encoding="utf-8")

    forbidden_claims = [
        "activate inviter credit",
        "modify CDL-029 allocation fractions",
        "modify CDL-091 Jury Incentive Economics",
        "mint ECU or settle ILC",
        "authorize public RC",
    ]
    for claim in forbidden_claims:
        assert claim in text
