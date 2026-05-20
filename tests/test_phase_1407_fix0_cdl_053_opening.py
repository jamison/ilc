"""Regression tests for Phase 1407-Fix0 CDL-053 opening."""

from __future__ import annotations

import subprocess
from pathlib import Path


OPENING_PATH = Path(
    "docs/specs/ilc_cdl_053_werner_local_productive_credit_opening_1407_fix0_v0.1.md"
)
CDL_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _cdl_053_rows(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.startswith("| CDL-053 |")]


def test_opening_document_has_required_token_and_scope() -> None:
    text = _read(OPENING_PATH)
    assert "cdl_053_werner_local_productive_credit_opened_phase_1407_fix0" in text
    assert "Werner local productive-credit architecture" in text
    assert "maintenance-equivalent reviewed productive work" in text


def test_q1_q4_deliberation_questions_recorded() -> None:
    text = _read(OPENING_PATH)
    for label in (
        "Q1 - Productive-Work Scope",
        "Q2 - Local Credit Unit and Conversion Gate",
        "Q3 - CDL-085 Phi-Bound Inheritance",
        "Q4 - Anti-Gaming and Anti-Inflation Boundary",
    ):
        assert label in text


def test_non_scope_excludes_phase_1263_flow_governor_path() -> None:
    text = _read(OPENING_PATH)
    assert "direct_werner_ecu_creation_rejected_phase_1263" in text
    assert "werner_flow_governor_cdl_not_opened_without_evidence_phase_1263" in text
    assert "heat-to-ECU minting" in text
    assert "topology-pressure-to-ECU minting" in text


def test_historical_hardening_cdl_053_absent_at_phase_1407_main_commit() -> None:
    result = subprocess.run(
        [
            "git",
            "show",
            "9eaffd74:docs/specs/ilc_constitutional_decision_log_v0.1.md",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert not _cdl_053_rows(result.stdout)


def test_cdl_053_not_ratified_in_current_register() -> None:
    rows = _cdl_053_rows(_read(CDL_PATH))
    if not rows:
        return
    assert len(rows) == 1
    assert "| ratified |" not in rows[0]
    assert "opened_phase: 1407_fix0" in rows[0]
