from __future__ import annotations

import subprocess
import sys
from pathlib import Path


CLOSURE_MEMO_PATH = Path(
    "docs/specs/ilc_settlement_substrate_closure_and_mvp_gated_replan_612_v0.1.md"
)
TEST_PATH = Path("tests/test_phase_612_settlement_substrate_closure_and_mvp_gated_replan.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_612_g8_window_607_612_settlement_substrate_closure_synthesis_and_mvp_gated_downstream_replan_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")

REQUIRED_SECTION_HEADINGS = [
    "## 1. Closure target and inherited route",
    "## 2. Locked conclusions from Phases 607-611",
    "## 3. MVP gate and minimum participant-touch package",
    "## 4. Downstream lane openings and sequencing",
    "## 5. Explicit exclusions and unresolved later closures",
    "## 6. Closure verdict and carry-forward handoff",
]

REQUIRED_CLOSURE_TOKENS = [
    "phase_612_closes_window_607_612_without_reopening_substrate_selection",
    "phase_612_uses_phase_611_memo_plus_adr_route_as_governing_input",
    "minimum_participant_touch_package_is_required_before_broader_public_rc_claims",
    "phase_612_does_not_open_new_sub_lanes_inside_the_closure_phase",
    "downstream_replan_must_follow_mvp_gate_before_sovereign_substrate_execution",
    "option_b_remains_later_selectable_only_via_published_graduation_checklist",
    "public_rc_package_coherence_does_not_require_immediate_option_b_selection",
    "post_612_work_must_prioritize_receipts_lifecycle_wallet_touchpoints_and_init",
]


def _read_section(text: str, heading: str) -> str:
    """Return the content of a section beginning at heading up to the next ## heading."""
    start = text.find(heading)
    assert start != -1, f"section heading not found: {heading!r}"
    after = text.find("\n## ", start + len(heading))
    return text[start: after] if after != -1 else text[start:]


def test_closure_memo_exists_and_contains_all_required_section_headings() -> None:
    assert CLOSURE_MEMO_PATH.exists(), f"closure memo missing: {CLOSURE_MEMO_PATH}"
    text = CLOSURE_MEMO_PATH.read_text(encoding="utf-8")
    for heading in REQUIRED_SECTION_HEADINGS:
        assert heading in text, f"missing section heading: {heading!r}"


def test_closure_memo_contains_all_required_closure_tokens() -> None:
    text = CLOSURE_MEMO_PATH.read_text(encoding="utf-8")
    for token in REQUIRED_CLOSURE_TOKENS:
        assert token in text, f"missing closure token: {token!r}"


def test_section_1_states_phase_611_route_and_no_reopening() -> None:
    text = CLOSURE_MEMO_PATH.read_text(encoding="utf-8")
    sec1 = _read_section(text, "## 1. Closure target and inherited route")
    assert "Phase 611 memo-plus-ADR route" in sec1 or "actual Phase 611 memo-plus-ADR route" in sec1, (
        "Section 1 must state the Phase 611 memo-plus-ADR route as governing input"
    )
    assert "Option A" in sec1 and "Option B" in sec1 and "Option C" in sec1 and "Option D" in sec1, (
        "Section 1 must state that Phase 612 does not reopen Option A/B/C/D evaluation"
    )
    assert "does not reopen" in sec1 or "not reopen" in sec1, (
        "Section 1 must state substrate selection is not reopened"
    )
    assert "does not revisit" in sec1 or "not revisit" in sec1, (
        "Section 1 must state Phase 612 does not revisit the Phase 611 governance vehicle choice"
    )
    assert "synthesize the lane and route downstream work only" in sec1, (
        "Section 1 must state this memo exists to synthesize the lane and route downstream work only"
    )


def test_section_2_locks_conclusions_from_607_611() -> None:
    text = CLOSURE_MEMO_PATH.read_text(encoding="utf-8")
    sec2 = _read_section(text, "## 2. Locked conclusions from Phases 607-611")
    assert "bounded current truth" in sec2, (
        "Section 2 must state RC/runtime is bounded current truth, not forever-substrate closure"
    )
    assert "Option D" in sec2 and "active near-term posture" in sec2, (
        "Section 2 must state Option D remains the active near-term posture"
    )
    assert "Option B" in sec2 and "not yet selected" in sec2, (
        "Section 2 must state Option B is the likely sovereign later path but is not yet selected"
    )
    assert "public auditability remains distinct from public identity exposure" in sec2, (
        "Section 2 must state public auditability is distinct from public identity exposure"
    )
    assert "censorship-resistance" in sec2 and "independence from external constitutional centers" in sec2, (
        "Section 2 must state censorship-resistance and independence from external constitutional centers remain live criteria"
    )


def test_section_3_defines_minimum_participant_touch_package() -> None:
    text = CLOSURE_MEMO_PATH.read_text(encoding="utf-8")
    sec3 = _read_section(text, "## 3. MVP gate and minimum participant-touch package")
    assert "init/admission" in sec3, "Section 3 must include init/admission touchpoint"
    assert "receipt issuance" in sec3 and "query" in sec3, (
        "Section 3 must include receipt issuance and query touchpoint"
    )
    assert "ECU visibility" in sec3 or "ECU" in sec3 and "visibility" in sec3, (
        "Section 3 must include ECU visibility touchpoint"
    )
    assert "ILC visibility" in sec3 or "delayed ILC" in sec3, (
        "Section 3 must include delayed ILC visibility touchpoint"
    )
    assert "wallet" in sec3 and "query" in sec3, "Section 3 must include wallet/query touchpoint"
    assert "without forcing immediate sovereign-chain implementation" in sec3 or (
        "sufficient for public learning without forcing immediate sovereign-chain implementation" in sec3
    ), "Section 3 must explain why the package is sufficient without forcing sovereign-chain implementation"


def test_section_4_defines_downstream_lanes_and_sequencing() -> None:
    text = CLOSURE_MEMO_PATH.read_text(encoding="utf-8")
    sec4 = _read_section(text, "## 4. Downstream lane openings and sequencing")
    assert "first post-612 spec lane" in sec4 or "First post-612 spec lane" in sec4, (
        "Section 4 must name the first post-612 spec lane"
    )
    assert "first post-612 interface/runtime lane" in sec4 or "First post-612 interface/runtime lane" in sec4, (
        "Section 4 must name the first post-612 interface/runtime lane"
    )
    assert "public-legitimacy mechanism lane" in sec4 or "public legitimacy mechanism lane" in sec4, (
        "Section 4 must name the later public-legitimacy mechanism lane"
    )
    assert "sovereign substrate selection" in sec4, (
        "Section 4 must name the later sovereign substrate selection lane"
    )
    assert "MVP gate" in sec4 or "mvp gate" in sec4.lower(), (
        "Section 4 must include a strict statement that the MVP gate precedes sovereign substrate execution"
    )
    assert "before sovereign substrate execution" in sec4, (
        "Section 4 must explicitly require MVP gate to be passed before sovereign substrate execution is opened"
    )


def test_section_5_preserves_exclusions_and_forbids_new_sub_lanes() -> None:
    text = CLOSURE_MEMO_PATH.read_text(encoding="utf-8")
    sec5 = _read_section(text, "## 5. Explicit exclusions and unresolved later closures")
    assert "No final substrate ratification" in sec5 or "no final substrate ratification" in sec5.lower(), (
        "Section 5 must exclude final substrate ratification in Phase 612"
    )
    assert "No wallet widening" in sec5 or "no wallet widening" in sec5.lower(), (
        "Section 5 must exclude wallet widening in Phase 612"
    )
    assert "No payment runtime" in sec5 or "no payment runtime" in sec5.lower(), (
        "Section 5 must exclude payment runtime in Phase 612"
    )
    assert "No chain implementation" in sec5 or "no chain implementation" in sec5.lower(), (
        "Section 5 must exclude chain implementation in Phase 612"
    )
    assert "No new planning sub-lanes" in sec5 or "does not open new planning sub-lanes" in sec5, (
        "Section 5 must forbid new planning sub-lanes in Phase 612"
    )


def test_section_6_states_closure_verdict_and_planning_resumption() -> None:
    text = CLOSURE_MEMO_PATH.read_text(encoding="utf-8")
    sec6 = _read_section(text, "## 6. Closure verdict and carry-forward handoff")
    assert "Window 607-612 is closed" in sec6, (
        "Section 6 must state the closure verdict for Window 607-612"
    )
    assert "broader post-605 planning may resume" in sec6 or (
        "planning may resume" in sec6
    ), "Section 6 must state whether broader post-605 planning may resume"
    assert "Option D" in sec6 and ("bounded current truth" in sec6 or "not final-substrate closure" in sec6 or "option d" in sec6.lower()), (
        "Section 6 must state the substrate assumptions under which broader planning may resume"
    )
    assert "graduation checklist" in sec6, (
        "Section 6 must state the Phase 611 graduation checklist remains controlling for any later Option B selection"
    )
    assert "ADR-0028" in sec6, (
        "Section 6 must reference ADR-0028 as governing the graduation checklist"
    )
    assert "CDL-062" in sec6 or "unresolved" in sec6, (
        "Section 6 must reference unresolved items deliberately deferred beyond this window"
    )


def _resolve_main_commit() -> str:
    result = subprocess.run(
        ["git", "log", "--oneline", "--all"],
        check=True,
        capture_output=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if "phase 612" in line.lower() and "closure handoff" in line.lower():
            return line.split()[0]
    raise AssertionError(
        "No commit found with subject containing both 'phase 612' and 'closure handoff'"
    )


def _resolve_backfill_commit() -> str:
    result = subprocess.run(
        ["git", "log", "--oneline", "--all"],
        check=True,
        capture_output=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if "phase 612" in line.lower() and "walkthrough" in line.lower() and "backfill" in line.lower():
            return line.split()[0]
    raise AssertionError(
        "No commit found with subject containing 'phase 612' and 'walkthrough' and 'backfill'"
    )


def _commit_paths(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "-r", "--name-only", commit_ref],
        check=True,
        capture_output=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def test_main_commit_touches_exactly_closure_memo_and_test() -> None:
    commit = _resolve_main_commit()
    paths = _commit_paths(commit)
    expected = {str(CLOSURE_MEMO_PATH), str(TEST_PATH)}
    assert paths == expected, (
        f"main commit must touch exactly {expected!r}, got {paths!r}"
    )


def test_main_commit_touches_no_adr_cdl_decision_log_or_ilc_core() -> None:
    commit = _resolve_main_commit()
    paths = _commit_paths(commit)
    for p in paths:
        assert not p.startswith("docs/adr/"), f"main commit must not touch ADR path: {p}"
        assert "constitutional_decision_log" not in p, f"main commit must not touch CDL path: {p}"
        assert not p.startswith("ilc_core/"), f"main commit must not touch ilc_core/ path: {p}"


def test_backfill_commit_touches_exactly_walkthrough_and_status() -> None:
    commit = _resolve_backfill_commit()
    paths = _commit_paths(commit)
    expected = {str(WALKTHROUGH_PATH), str(STATUS_PATH)}
    assert paths == expected, (
        f"backfill commit must touch exactly {expected!r}, got {paths!r}"
    )
    for p in paths:
        assert not p.startswith("docs/adr/"), f"backfill commit must not touch ADR path: {p}"
        assert "constitutional_decision_log" not in p, f"backfill commit must not touch CDL path: {p}"
        assert not p.startswith("ilc_core/"), f"backfill commit must not touch ilc_core/ path: {p}"
