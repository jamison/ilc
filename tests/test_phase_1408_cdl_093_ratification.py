"""Regression tests for Phase 1408 CDL-093 ratification."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


EVIDENCE_PATH = Path(
    "docs/specs/ilc_cdl_093_maintenance_lottery_pool_ratification_evidence_1408_v0.1.md"
)
PRELOCK_PATH = Path("docs/specs/ilc_cdl_093_maintenance_lottery_pool_prelock_1407_v0.1.md")
AMENDMENT_PATH = Path(
    "docs/specs/ilc_cdl_093_maintenance_lottery_pool_prelock_amendment_1407_fix3_v0.1.md"
)
CDL_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
STATUS_PATH = Path("docs/phases/STATUS.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _cdl_093_rows(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.startswith("| CDL-093 |")]


def _phase_1406_c2_hash() -> str:
    text = _read(STATUS_PATH)
    marker = "## Phase 1406 / CDL-093 Maintenance Lottery Pool Opening"
    assert marker in text
    segment = text[text.index(marker) :]
    match = re.search(r"\*\*C2 CDL mutation commit:\*\* `([0-9a-f]{8,40})`", segment)
    assert match is not None
    return match.group(1)


def test_ratification_evidence_present_with_required_tokens() -> None:
    text = _read(EVIDENCE_PATH)
    assert "cdl_093_ratified_phase_1408" in text
    assert "cdl_093_ratification_evidence_committed" in text
    assert "cdl_093_historical_hardening_phase_1406_ref_asserted" in text
    assert "maintenance_lottery_activation_not_authorized_phase_1408" in text


def test_all_phase_1407_scope_constants_enumerated_with_fix3_values() -> None:
    evidence = _read(EVIDENCE_PATH)
    prelock = _read(PRELOCK_PATH)
    constants = re.findall(r"\| `(MAINTENANCE_LOTTERY_[A-Z0-9_]+|MAINTENANCE_POOL_[A-Z0-9_]+)` \|", prelock)
    assert constants
    for constant in constants:
        assert constant in evidence
    assert "| `MAINTENANCE_LOTTERY_POOL_FUNDING_SOURCE` | `cdl_053_werner_local_productive_credit` |" in evidence
    assert "| `MAINTENANCE_LOTTERY_POOL_FUNDING_FRACTION` | `Decimal(\"0.10\")` |" in evidence
    assert "| `MAINTENANCE_POOL_FUNDING_FRACTION_PENDING_SIM` | `false` |" in evidence
    assert (
        "| `MAINTENANCE_LOTTERY_ECU_DISTRIBUTION_PATH` | `cdl_053_werner_local_credit_to_phase_1409_default_off_runtime_stub` |"
        in evidence
    )


def test_fix3_amendment_and_cdl_053_ratification_consumed() -> None:
    evidence = _read(EVIDENCE_PATH)
    amendment = _read(AMENDMENT_PATH)
    assert "cdl_053_ratified_phase_1407_fix2" in evidence
    assert "cdl_093_prelock_amended_cdl_053_source_phase_1407_fix3" in evidence
    assert "maintenance_lottery_funding_fraction_sim_complete_phase_1407_fix3" in evidence
    assert "MAINTENANCE_LOTTERY_POOL_FUNDING_FRACTION = Decimal(\"0.10\")" in amendment


def test_historical_hardening_cdl_093_open_at_phase_1406_c2() -> None:
    commit_hash = _phase_1406_c2_hash()
    result = subprocess.run(
        [
            "git",
            "show",
            f"{commit_hash}:docs/specs/ilc_constitutional_decision_log_v0.1.md",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    rows = _cdl_093_rows(result.stdout)
    assert len(rows) == 1
    assert "| open |" in rows[0]
    assert "opened_phase: 1406" in rows[0]


def test_current_register_row_state_is_valid_before_or_after_c2() -> None:
    rows = _cdl_093_rows(_read(CDL_PATH))
    assert len(rows) == 1
    row = rows[0]
    if "| ratified |" in row:
        assert "ratified_phase: 1408" in row
        assert "ratification_token: cdl_093_ratified_phase_1408" in row
        assert (
            "evidence_document: docs/specs/ilc_cdl_093_maintenance_lottery_pool_ratification_evidence_1408_v0.1.md"
            in row
        )
    else:
        assert "| open |" in row
        assert "ratification_status: not_ratified_pending_phase_1408" in row


def test_non_activation_boundaries_are_explicit() -> None:
    text = _read(EVIDENCE_PATH)
    for phrase in (
        "maintenance lottery activation",
        "live lottery draws",
        "ECU distribution",
        "ECU settlement",
        "wallet mutation",
        "runtime activation",
        "J-008 gate verdict change",
    ):
        assert phrase in text
    assert "| `MAINTENANCE_LOTTERY_LIVE_DRAWS_ALLOWED` | `false` |" in text
    assert "| `MAINTENANCE_LOTTERY_ECU_SETTLEMENT_ALLOWED` | `false` |" in text


def test_j008_not_flipped_by_phase_1408() -> None:
    text = _read(EVIDENCE_PATH)
    assert "MAINTENANCE_LOTTERY_CDL_RATIFIED" in text
    assert "NOT_MET" in text
    assert "maintenance_lottery_cdl_not_opened_phase_j008" in text
