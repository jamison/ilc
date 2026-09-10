# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from pathlib import Path

from ilc_core.validator.validator_admission_ejection_production_path import (
    VALIDATOR_ADMISSION_NOT_ACTIVATED,
)


ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PRELOCK = (
    ROOT
    / "docs/specs/ilc_cdl_107_reputation_ecu_boundary_validator_eligibility_prelock_GAP_PROVISIONAL_VALIDATOR_CDL_00_v0.1.md"
)
RATIFICATION = (
    ROOT
    / "docs/specs/ilc_cdl_107_reputation_ecu_boundary_validator_eligibility_ratification_evidence_GAP_PROVISIONAL_VALIDATOR_CDL_00_v0.1.md"
)
STATUS = ROOT / "docs/phases/STATUS.md"


PRELOCK_TOKEN = "cdl_107_validator_eligibility_prelocked_GAP_PROVISIONAL_VALIDATOR_CDL_00"
RATIFICATION_TOKEN = "cdl_107_validator_eligibility_ratified_GAP_PROVISIONAL_VALIDATOR_CDL_00"


def _cdl_107_row() -> str:
    for line in REGISTER.read_text(encoding="utf-8").splitlines():
        if line.startswith("| CDL-107 |"):
            return line
    raise AssertionError("CDL-107 row missing")


def test_cdl_107_register_is_ratified_with_phase_tokens() -> None:
    row = _cdl_107_row()
    assert "| ratified |" in row
    assert PRELOCK_TOKEN in row
    assert RATIFICATION_TOKEN in row
    assert "docs/specs/ilc_cdl_107_reputation_ecu_boundary_validator_eligibility_prelock_GAP_PROVISIONAL_VALIDATOR_CDL_00_v0.1.md" in row
    assert "docs/specs/ilc_cdl_107_reputation_ecu_boundary_validator_eligibility_ratification_evidence_GAP_PROVISIONAL_VALIDATOR_CDL_00_v0.1.md" in row


def test_cdl_107_prelock_preserves_candidate_zero_weight_boundary() -> None:
    text = PRELOCK.read_text(encoding="utf-8")
    assert "consensus_weight=0" in text
    assert "bft_quorum_weight=0" in text
    assert "Candidate and Provisional validators are explicitly non-voting" in text
    assert "No validator rewards" in text
    assert "No settlement eligibility" in text


def test_cdl_107_prelock_defers_scoring_and_live_admission() -> None:
    text = PRELOCK.read_text(encoding="utf-8")
    assert "CDL-106 is opened only" in text
    assert "does not ratify the final AgentReputationRecord formula" in text
    assert "SIM-F" in text
    assert "VALIDATOR_ADMISSION_NOT_ACTIVATED=True" in text
    assert "post-launch Part 3n" in text


def test_cdl_107_ratification_records_historical_artifact_boundary() -> None:
    text = RATIFICATION.read_text(encoding="utf-8")
    assert "GAP-REPUTATION-04" in text
    assert "Phase 1589" in text
    assert "VALIDATOR_ADMISSION_NOT_ACTIVATED = True" in text
    assert "does not modify runtime code or clear admission guards" in text


def test_validator_admission_guard_remains_closed() -> None:
    assert VALIDATOR_ADMISSION_NOT_ACTIVATED is True


def test_status_contains_exact_cdl_107_completion_tokens_once() -> None:
    text = STATUS.read_text(encoding="utf-8")
    assert text.count(f"Output token: `{PRELOCK_TOKEN}`") == 1
    assert text.count(f"Output token: `{RATIFICATION_TOKEN}`") == 1
