"""
Phase 1385a Strike Force — Spec D epoch-checkpoint SafetyNoDualCert tests.

Verifies that:
1. The Spec D TLA+ file and config exist and are well-formed.
2. The TLC output log exists and records a clean run (no violations).
3. The required closure tokens are present in the evidence document.
4. The Phase 1385 disposition document records the deferral as closed.
5. The TLC gate script includes Spec D.
6. The TLC output stats confirm exhaustive exploration (0 states left on queue).
"""

import re
from pathlib import Path

REPO = Path(__file__).parent.parent

SPEC_D_TLA = REPO / "docs/specs/tla/ilc_epoch_checkpoint_safety.tla"
SPEC_D_CFG = REPO / "docs/specs/tla/ilc_epoch_checkpoint_safety.cfg"
TLC_OUT    = REPO / "tools/tla/ilc_epoch_checkpoint_safety.tlc.out"
EVIDENCE   = REPO / "docs/specs/ilc_epoch_checkpoint_safety_tlc_evidence_1385a_v0.1.md"
DISP_1385  = REPO / "docs/specs/ilc_tla_plus_safetynodualcert_disposition_1385_v0.1.md"
TLC_SCRIPT = REPO / "tools/run_tlc_m_series_gate.sh"


# ── 1. Spec D files exist ─────────────────────────────────────────────────────

def test_spec_d_tla_exists():
    assert SPEC_D_TLA.exists(), f"Spec D TLA+ file not found: {SPEC_D_TLA}"


def test_spec_d_cfg_exists():
    assert SPEC_D_CFG.exists(), f"Spec D cfg file not found: {SPEC_D_CFG}"


def test_tlc_output_exists():
    assert TLC_OUT.exists(), f"TLC output log not found: {TLC_OUT}"


# ── 2. Spec D content checks ──────────────────────────────────────────────────

def test_spec_d_declares_safetynodualcert():
    text = SPEC_D_TLA.read_text()
    assert "SafetyNoDualCert" in text, "Spec D must declare SafetyNoDualCert invariant"


def test_spec_d_declares_monotonic_commit():
    text = SPEC_D_TLA.read_text()
    assert "MonotonicCommit" in text, "Spec D must declare MonotonicCommit invariant"


def test_spec_d_threshold_formula():
    text = SPEC_D_TLA.read_text()
    assert "2 * F + 1" in text, "Spec D must define Threshold = 2*F+1"


def test_spec_d_honest_sign_conflict_guard():
    text = SPEC_D_TLA.read_text()
    assert "HonestSign" in text, "Spec D must model HonestSign (one-vote-per-epoch rule)"
    assert "Conflicts" in text, "Spec D must model Conflicts"


def test_spec_d_byzantine_equivocation():
    text = SPEC_D_TLA.read_text()
    assert "ByzantineSign" in text, "Spec D must model ByzantineSign (equivocation)"


def test_spec_d_closure_token_in_spec():
    text = SPEC_D_TLA.read_text()
    assert "safetynodualcert_spec_d_proven_epoch_checkpoint" in text, \
        "Spec D must include the closure token"


# ── 3. TLC output clean ───────────────────────────────────────────────────────

def test_tlc_no_error():
    text = TLC_OUT.read_text()
    assert "No error has been found" in text, \
        "TLC output must record 'No error has been found'"


def test_tlc_queue_exhausted():
    text = TLC_OUT.read_text()
    assert "0 states left on queue" in text, \
        "TLC must have exhausted the state space (0 states left on queue)"


def test_tlc_distinct_states_nonzero():
    """Confirm TLC explored a non-trivial state space.

    The final summary line has no commas: '67020103 states generated, 7931925 distinct states found, 0 states left'
    Progress lines use comma-separated numbers.  We take the last match.
    """
    text = TLC_OUT.read_text()
    # Match both comma-formatted (progress lines) and plain-integer (summary line) forms.
    matches = re.findall(r"([\d,]+) distinct states found", text)
    assert matches, "TLC output must report distinct states found"
    # Last match is the final summary line.
    count = int(matches[-1].replace(",", ""))
    assert count > 100_000, \
        f"Expected > 100K distinct states for a non-trivial run; got {count}"


# ── 4. Evidence document tokens ───────────────────────────────────────────────

def test_evidence_closure_token():
    text = EVIDENCE.read_text()
    assert "safetynodualcert_spec_d_proven_epoch_checkpoint" in text, \
        "Evidence doc must contain safetynodualcert_spec_d_proven_epoch_checkpoint"


def test_evidence_deferral_closed_token():
    text = EVIDENCE.read_text()
    assert "safetynodualcert_deferred_with_authority_phase_1385_closed_1385a" in text, \
        "Evidence doc must contain the deferral-closed token"


def test_evidence_tlc_clean_token():
    text = EVIDENCE.read_text()
    assert "tla_spec_d_epoch_checkpoint_tlc_clean" in text, \
        "Evidence doc must contain tla_spec_d_epoch_checkpoint_tlc_clean"


# ── 5. Phase 1385 disposition doc records deferral closed ─────────────────────

def test_disposition_1385_records_closure():
    text = DISP_1385.read_text()
    assert "safetynodualcert_spec_d_proven_epoch_checkpoint" in text, \
        "Phase 1385 disposition doc must record the Spec D closure token"


def test_disposition_1385_deferral_closed_annotation():
    text = DISP_1385.read_text()
    assert "DEFERRAL CLOSED" in text, \
        "Phase 1385 disposition doc must be annotated DEFERRAL CLOSED"


# ── 6. TLC gate script includes Spec D ────────────────────────────────────────

def test_gate_script_includes_spec_d():
    text = TLC_SCRIPT.read_text()
    assert "ilc_epoch_checkpoint_safety" in text, \
        "TLC gate script must include Spec D (ilc_epoch_checkpoint_safety)"
