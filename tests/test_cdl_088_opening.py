from __future__ import annotations

from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]

PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1374_g8_cdl_088_opening.md"
)
REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
OPENING = ROOT / "docs/specs/ilc_cdl_088_public_claimability_opening_1374_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
FORWARD_PLAN = (
    ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
)
WALKTHROUGH = ROOT / "docs/phases/phase_1374_cdl_088_opening_walkthrough.md"

REQUIRED_TOKENS = (
    "cdl_088_public_claimability_opened_phase_1374",
    "cdl_088_not_ratified_phase_1374",
    "cdl_088_bounded_claimability_candidate_scope_phase_1374",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def cdl_row(text: str, cdl_id: str) -> str:
    rows = [line for line in text.splitlines() if line.startswith(f"| {cdl_id} |")]
    assert len(rows) == 1
    return rows[0]


def normalized(text: str) -> str:
    return " ".join(text.split())


def test_phase_1374_prompt_remains_schema_valid() -> None:
    assert validate(PROMPT) == []


def test_cdl_088_opening_artifacts_record_required_tokens() -> None:
    texts = (
        read(OPENING),
        read(REGISTER),
        read(WALKTHROUGH),
        read(STATUS),
        read(PLANNING_INDEX),
        read(FORWARD_PLAN),
    )

    for text in texts:
        for token in REQUIRED_TOKENS:
            assert token in text

    opening = read(OPENING)
    assert "GO Phase 1374" in opening
    assert "ILC_CDL_MUTATION_PHASE=1374" in opening
    assert "phase_1375_cdl_088_deliberation_prelock_next" in opening


def test_cdl_088_register_row_is_open_and_not_ratified() -> None:
    register = read(REGISTER)
    row = cdl_row(register, "CDL-088")

    assert "| open |" in row
    assert "| ratified |" not in row
    assert "opened_phase: 1374" in row
    assert "opened_date: 2026-05-18" in row
    assert "opening_token: cdl_088_public_claimability_opened_phase_1374" in row
    assert "historical_non_ratification_token: cdl_088_not_ratified_phase_1374" in row
    assert (
        "candidate_scope_token: cdl_088_bounded_claimability_candidate_scope_phase_1374"
        in row
    )
    assert "prelock_status: deferred_to_phase_1375" in row
    assert "ratification_status: not_ratified_phase_1374" in row
    assert "public_claimability_activation_status: not_enabled" in row
    assert "claim_endpoint_status: not_enabled" in row
    assert "runtime_activation_status: not_authorized" in row


def test_cdl_088_candidate_scope_is_open_not_locked_or_activated() -> None:
    opening = read(OPENING)
    row = cdl_row(read(REGISTER), "CDL-088")

    for phrase in (
        "Bounded public claimability authority",
        "Reciprocal scoring, if included",
        "ECU-escrow admission, if included",
        "Public verifier API boundary",
        "Open for deliberation",
    ):
        assert phrase in opening

    for forbidden in (
        "public_claimability_activation_status: enabled",
        "claim_endpoint_status: enabled",
        "runtime_activation_status: authorized",
        "ratified_phase: 1374",
    ):
        assert forbidden not in row
        assert forbidden not in opening

    normalized_opening = normalized(opening)
    assert "does not activate public claimability" in normalized_opening
    assert "does not lock final scope" in normalized_opening


def test_phase_1374_frontier_docs_route_phase_1375_next() -> None:
    for text in (read(WALKTHROUGH), read(STATUS), read(PLANNING_INDEX), read(FORWARD_PLAN)):
        assert "CDL-088" in text
        assert "Phase 1375" in text
        assert "deliberation/prelock" in text

    assert "Phase 1374 complete" in read(PLANNING_INDEX)
    assert "CDL-only opening commit `43bcddc0`" in read(FORWARD_PLAN)
