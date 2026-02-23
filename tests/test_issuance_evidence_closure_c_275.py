from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


EVIDENCE_PATH = Path("docs/specs/ilc_issuance_evidence_closure_c_275_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_275_COMMIT_SUBJECT = (
    "docs(g8): phase 275 issuance evidence closure c option-b carry-forward lock"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _resolve_phase_275_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"], check=True, capture_output=True, text=True
    )
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_275_COMMIT_SUBJECT:
            return commit_hash
    return "HEAD"


def test_evidence_artifact_exists() -> None:
    assert EVIDENCE_PATH.exists()


def test_evidence_artifact_has_required_sections() -> None:
    text = _read(EVIDENCE_PATH)
    headings = [
        "## 1. Scope",
        "## 2. CDL-027 Decay Formulation Evidence",
        "## 3. Epoch Duration Matrix and Policy Options (A/B/C)",
        "## 4. Practical Risk Controls Carry-Forward",
        "## 5. CDL-030 Derivation Methodology",
        "## 6. Non-goals",
        "## 7. Canonical Anchors",
    ]
    for heading in headings:
        assert heading in text


def test_cmax_anchor_and_matrix_reference_are_present() -> None:
    text = _read(EVIDENCE_PATH)
    assert "C_max = 25,920,000" in text
    assert "ilc_cdl_026_cmax_lock_ratification_evidence_273_v0.1.md" in text
    assert "ilc_epoch_duration_candidate_matrix_and_policy_options_274_fix2_v0.1.md" in text


def test_epoch_duration_matrix_contains_day_week_month_candidates() -> None:
    text = _read(EVIDENCE_PATH)
    assert "1 day epoch" in text
    assert "1 week epoch" in text
    assert "1 month epoch" in text


def test_option_abc_comparison_and_option_b_lock_statement_are_present() -> None:
    text = _read(EVIDENCE_PATH)
    assert "Option A" in text
    assert "Option B" in text
    assert "Option C" in text
    assert "Phase 275 selects **Option B** as the only carry-forward candidate to Phase 276" in text
    assert "`halving`, `H=48`, `1 month` epochs" in text


def test_practical_risk_controls_section_contains_all_required_controls() -> None:
    text = _read(EVIDENCE_PATH)
    required_controls = [
        "No macro-hedge claim boundary",
        "Custody/liquidity resilience carry-forward",
        "Anti-leverage/reflexivity control note",
        "Utility-first KPI requirement",
    ]
    for control in required_controls:
        assert control in text


def test_non_ratifying_boundary_language_is_explicit() -> None:
    text = _read(EVIDENCE_PATH)
    assert "non-ratifying" in text
    assert "no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`" in text
    assert "No schedule constant is ratified in this phase." in text


def test_no_decision_log_mutation_for_phase_275() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    for cdl_id in ["CDL-027", "CDL-030", "CDL-031", "CDL-026", "CDL-028", "CDL-029"]:
        assert rows[cdl_id].get("ratified_phase") != "275", cdl_id
    assert "ratified_phase: 275" not in _read(DECISION_LOG_PATH)


def test_no_runtime_files_touched_in_this_phase() -> None:
    commit_ref = _resolve_phase_275_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
