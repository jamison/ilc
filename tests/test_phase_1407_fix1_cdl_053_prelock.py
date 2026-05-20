"""Regression tests for Phase 1407-Fix1 CDL-053 prelock."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


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


def test_prelock_spec_present_with_required_tokens() -> None:
    text = _read(PRELOCK_PATH)
    assert "cdl_053_prelock_committed_phase_1407_fix1" in text
    assert "cdl_053_scope_constants_locked_phase_1407_fix1" in text
    assert "CDL-053 remains open and unratified after Phase 1407-fix1" in text


def test_q1_q4_resolved_with_explicit_constants() -> None:
    text = _read(PRELOCK_PATH)
    required = (
        "WERNER_PRODUCTIVE_WORK_SCOPE",
        "WERNER_LOCAL_CREDIT_UNIT_DESIGNATION",
        "WERNER_EDGE_MINT_PHI_BOUND_INHERITED",
        "WERNER_LOCAL_CREDIT_ANTI_GAMING_CONTROLS",
        "star.map.embedding",
        "contradiction.sweep",
        "graph.compression",
        "stability.simulation",
        "custom_review_lane_assigned",
    )
    for token in required:
        assert token in text


def test_direct_ecu_creation_remains_forbidden() -> None:
    text = _read(PRELOCK_PATH)
    assert "| `WERNER_DIRECT_ECU_CREATION_AUTHORIZED` | `false` |" in text
    assert "| `WERNER_DIRECT_HEAT_TO_ECU_MINTING` | `not_authorized` |" in text
    assert "direct_werner_ecu_creation_rejected_phase_1263" in text


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


def test_current_cdl_053_register_row_is_not_ratified() -> None:
    rows = _cdl_053_rows(_read(CDL_PATH))
    assert len(rows) == 1
    assert "| open |" in rows[0]
    assert "| ratified |" not in rows[0]
    assert "ratification_status: not_ratified_pending_phase_1407_fix2" in rows[0]


def test_local_credit_is_not_wallet_or_settlement_grade() -> None:
    text = _read(PRELOCK_PATH)
    assert "| `WERNER_LOCAL_CREDIT_IS_SETTLEMENT_GRADE` | `false` |" in text
    assert "| `WERNER_LOCAL_CREDIT_IS_WALLET_VISIBLE` | `false` |" in text
    assert "| `WERNER_LOCAL_CREDIT_IS_TRANSFERABLE` | `false` |" in text
    assert "| `WERNER_LIVE_DISTRIBUTION_AUTHORIZED` | `false` |" in text
