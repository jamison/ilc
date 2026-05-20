"""Regression tests for Phase 1407-Fix2 CDL-053 ratification."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


EVIDENCE_PATH = Path(
    "docs/specs/ilc_cdl_053_werner_local_productive_credit_ratification_evidence_1407_fix2_v0.1.md"
)
PRELOCK_PATH = Path(
    "docs/specs/ilc_cdl_053_werner_local_productive_credit_prelock_1407_fix1_v0.1.md"
)
CDL_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
STATUS_PATH = Path("docs/phases/STATUS.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _cdl_053_rows(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.startswith("| CDL-053 |")]


def _fix0_c2_hash() -> str:
    text = _read(STATUS_PATH)
    marker = "## Phase 1407-Fix0 / CDL-053 Werner Local Productive Credit Opening"
    assert marker in text
    segment = text[text.index(marker) :]
    match = re.search(r"\*\*C2 CDL mutation commit:\*\* `([0-9a-f]{8,40})`", segment)
    assert match is not None
    return match.group(1)


def test_ratification_evidence_present_with_required_tokens() -> None:
    text = _read(EVIDENCE_PATH)
    assert "cdl_053_ratified_phase_1407_fix2" in text
    assert "cdl_053_ratification_evidence_committed" in text
    assert "cdl_053_historical_hardening_fix0_ref_asserted" in text


def test_all_fix1_scope_constants_enumerated_in_evidence() -> None:
    evidence = _read(EVIDENCE_PATH)
    prelock = _read(PRELOCK_PATH)
    constants = re.findall(r"\| `(WERNER_[A-Z0-9_]+)` \|", prelock)
    assert constants
    for constant in constants:
        assert constant in evidence


def test_historical_hardening_cdl_053_open_at_fix0_c2() -> None:
    commit_hash = _fix0_c2_hash()
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
    rows = _cdl_053_rows(result.stdout)
    assert len(rows) == 1
    assert "| open |" in rows[0]
    assert "opened_phase: 1407_fix0" in rows[0]


def test_current_register_row_state_is_valid_before_or_after_c2() -> None:
    rows = _cdl_053_rows(_read(CDL_PATH))
    assert len(rows) == 1
    row = rows[0]
    if "| ratified |" in row:
        assert "ratified_phase: 1407_fix2" in row
        assert "ratification_token: cdl_053_ratified_phase_1407_fix2" in row
        assert (
            "evidence_document: docs/specs/ilc_cdl_053_werner_local_productive_credit_ratification_evidence_1407_fix2_v0.1.md"
            in row
        )
    else:
        assert "| open |" in row
        assert "ratification_status: not_ratified_pending_phase_1407_fix2" in row


def test_non_activation_boundaries_are_explicit() -> None:
    text = _read(EVIDENCE_PATH)
    for phrase in (
        "ECU minting",
        "direct Werner ECU creation",
        "ILC settlement",
        "wallet mutation",
        "live distribution",
        "maintenance lottery activation",
        "flow-governor activation",
        "heat-to-ECU signal activation",
    ):
        assert phrase in text
    assert "| `WERNER_DIRECT_ECU_CREATION_AUTHORIZED` | `false` |" in text


def test_cdl_085_inheritance_and_phase_1263_boundary_preserved() -> None:
    text = _read(EVIDENCE_PATH)
    assert "| `WERNER_EDGE_MINT_PHI_BOUND_VALUE` | `Decimal(\"0.60\")` |" in text
    assert "direct_werner_ecu_creation_rejected_phase_1263" in text
    assert "werner_flow_governor_cdl_not_opened_without_evidence_phase_1263" in text
