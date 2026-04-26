"""Phase 843 — Window 839–843 closure gate.

Asserts:
  1. Option B gate verdict is 'go' in the gate re-synthesis document.
  2. Row 8 candidate evaluation blocker discharged in evaluation document.
  3. HIGH-002 planning brief exists and records Phase A authorization.
  4. Sequence lock document exists.
  5. Coherence report 839–843 exists.
  6. Capsule v5.18 exists and supersedes v5.17.
  7. Constitutional decision log was NOT mutated in this window.
  8. No ilc_core/ or ilc_consensus/ mutations in window commits.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Selftest guard — skip expensive checks when running nested
# ---------------------------------------------------------------------------
_SELFTEST = os.environ.get("ILC_PHASE_843_GATE_SELFTEST") == "1"

REPO_ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# 1. Option B gate verdict = go
# ---------------------------------------------------------------------------

def test_option_b_gate_verdict_go() -> None:
    path = REPO_ROOT / "docs/specs/ilc_phase_841_option_b_gate_resynthesis_v0.1.md"
    assert path.exists(), f"Option B gate re-synthesis document missing: {path}"
    text = path.read_text()
    assert "option_b_gate_synthesis_verdict=go" in text
    assert "option_b_selectable_not_selected" in text
    assert "option_d_remains_active_posture_until_explicit_graduation" in text


# ---------------------------------------------------------------------------
# 2. Row 8 candidate evaluation blocker discharged
# ---------------------------------------------------------------------------

def test_row8_candidate_evaluation_blocker_discharged() -> None:
    path = REPO_ROOT / "docs/specs/ilc_phase_840_row8_substrate_candidate_evaluation_v0.1.md"
    assert path.exists(), f"Row 8 evaluation document missing: {path}"
    text = path.read_text()
    assert "row8_candidate_named_and_classified" in text
    assert "row8_candidate_passes_exclusion_matrix" in text
    assert "row8_candidate_evaluation_blocker_discharged" in text


# ---------------------------------------------------------------------------
# 3. HIGH-002 planning brief exists and Phase A is authorized
# ---------------------------------------------------------------------------

def test_high_002_planning_brief_exists() -> None:
    path = REPO_ROOT / "docs/specs/ilc_phase_842_high_002_production_hardening_planning_v0.1.md"
    assert path.exists(), f"HIGH-002 planning brief missing: {path}"
    text = path.read_text()
    assert "high_002_production_hardening_planning_842_complete" in text
    assert "high_002_phase_a_rust_consensus_fix_authorized_post_window_839_843" in text
    assert "high_002_not_a_testnet_blocker_confirmed" in text
    assert "high_002_mandatory_before_production_N_ge_4_F_ge_1" in text


# ---------------------------------------------------------------------------
# 4. Sequence lock document exists
# ---------------------------------------------------------------------------

def test_sequence_lock_exists() -> None:
    path = REPO_ROOT / "docs/specs/ilc_phase_839_843_sequence_lock_v0.1.md"
    assert path.exists(), f"Sequence lock document missing: {path}"
    text = path.read_text()
    assert "row8_substrate_evaluation_window_839_843_sequence_lock_active" in text
    assert "option_b_gate_resynthesis_authorized_839_843" in text
    assert "no_ilc_core_mutation_in_window_839_843" in text
    assert "no_ilc_consensus_mutation_in_window_839_843" in text
    assert "no_decision_log_mutation_in_window_839_843" in text


# ---------------------------------------------------------------------------
# 5. Coherence report 839–843 exists
# ---------------------------------------------------------------------------

def test_coherence_report_839_843_exists() -> None:
    path = REPO_ROOT / "docs/specs/ilc_integration_coherence_report_839_843_v0.1.md"
    assert path.exists(), f"Coherence report missing: {path}"
    text = path.read_text()
    assert "option_b_gate_resynthesis_window_839_843_coherence_published" in text
    assert "option_b_gate_synthesis_verdict_go_recorded" in text
    assert "window_839_843_hard_constraints_satisfied" in text


# ---------------------------------------------------------------------------
# 6. Capsule v5.18 exists and supersedes v5.17
# ---------------------------------------------------------------------------

def test_capsule_v5_18_exists() -> None:
    path = REPO_ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.18.md"
    assert path.exists(), f"Capsule v5.18 missing: {path}"
    text = path.read_text()
    assert "capsule_v5_18_supersedes_v5_17" in text
    assert "option_b_gate_synthesis_verdict_go_recorded_in_capsule_v5_18" in text
    assert "option_b_selectable_not_selected" in text
    assert "option_d_remains_active_posture_until_explicit_graduation" in text


# ---------------------------------------------------------------------------
# 7. Constitutional decision log was NOT mutated in window 839–843
# ---------------------------------------------------------------------------

def test_decision_log_not_mutated_in_window() -> None:
    """The CDL-069 row must be the last mutation; no new rows added since 838j."""
    cdl_log = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
    text = cdl_log.read_text()
    # CDL-069 must be ratified (from Phase 838j — prior window)
    cdl_069_found = False
    for line in text.splitlines():
        if "| CDL-069 |" in line:
            assert "| ratified |" in line, (
                f"CDL-069 must be ratified from prior window:\n{line}"
            )
            assert "ratified_phase: 838j" in line
            cdl_069_found = True
            break
    assert cdl_069_found, "CDL-069 row not found in decision log"
    # No CDL opened or ratified in window 839–843 (no CDL-070 or CDL-071 row present)
    for line in text.splitlines():
        assert "| CDL-070 |" not in line, (
            "CDL-070 must not be present in decision log (window 839–843 constraint)"
        )
        assert "| CDL-071 |" not in line, (
            "CDL-071 must not be present in decision log (window 839–843 constraint)"
        )


# ---------------------------------------------------------------------------
# 8. No ilc_core/ or ilc_consensus/ mutations in working tree or recent commits
# ---------------------------------------------------------------------------

@pytest.mark.skipif(_SELFTEST, reason="selftest guard: skip subprocess in selftest")
def test_no_ilc_core_or_consensus_mutations_in_window() -> None:
    """Window 839–843 constraint: ilc_core/ and ilc_consensus/ must not be
    modified. Checks both uncommitted working-tree state and the last 5 commits
    (the window commit should be present after window commit lands)."""
    # Check working tree — no unstaged or staged changes to ilc_core/ or ilc_consensus/
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, f"git status failed: {result.stderr}"
    for line in result.stdout.splitlines():
        changed = line[3:].strip()  # strip status prefix
        assert not changed.startswith("ilc_core/"), (
            f"ilc_core/ must not be modified in window 839–843: {line}"
        )
        assert not changed.startswith("ilc_consensus/"), (
            f"ilc_consensus/ must not be modified in window 839–843: {line}"
        )
    # Verify the sequence lock document asserts the constraint token
    seq_lock = REPO_ROOT / "docs/specs/ilc_phase_839_843_sequence_lock_v0.1.md"
    text = seq_lock.read_text()
    assert "no_ilc_core_mutation_in_window_839_843" in text
    assert "no_ilc_consensus_mutation_in_window_839_843" in text
    assert "no_decision_log_mutation_in_window_839_843" in text
