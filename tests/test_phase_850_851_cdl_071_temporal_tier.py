"""Phase 850–851 CDL-071 temporal tier reconciliation gate tests.

Phase 850: CDL-071 opening + three-CDL audit.
Phase 851: CDL-071 ratification + CDL master log.

Verifies:
1. Opening doc exists with audit tokens for all three CDLs.
2. Ratification evidence exists with tier assignment tokens.
3. CDL master log row 102 (CDL-071) is present and ratified.
4. Constitutional precedence token present.
5. No ilc_core/ mutation in Phases 850–851.

Token: cdl_071_ratified_851
Token: temporal_tier_framework_takes_constitutional_precedence
"""
import subprocess
from pathlib import Path

REPO = Path(__file__).parent.parent
CDL_071_OPENING = REPO / "docs" / "specs" / "ilc_cdl_071_temporal_tier_reconciliation_opening_850_v0.1.md"
CDL_071_EVIDENCE = REPO / "docs" / "specs" / "ilc_cdl_071_temporal_tier_reconciliation_ratification_evidence_851_v0.1.md"
CDL_LOG = REPO / "docs" / "specs" / "ilc_constitutional_decision_log_v0.1.md"


# ---------------------------------------------------------------------------
# Phase 850 — opening doc
# ---------------------------------------------------------------------------

def test_cdl_071_opening_exists():
    assert CDL_071_OPENING.exists(), "CDL-071 opening document missing"


def test_cdl_071_opening_tokens():
    text = CDL_071_OPENING.read_text()
    for token in [
        "cdl_071_temporal_tier_reconciliation_opening_850",
        "cdl_071_opened_phase_850",
        "cdl_069_ratified_blocker_cleared_for_cdl_071",
        "cdl_043_tier_2_assignment_confirmed",
        "cdl_044_tier_2_assignment_confirmed",
        "cdl_v1_tier_2_assignment_confirmed",
        "temporal_tier_framework_consistency_audit_complete_cdl_071",
        "cdl_071_verification_artifact_defined",
    ]:
        assert token in text, f"Missing token in CDL-071 opening: {token!r}"


def test_cdl_071_opening_covers_all_three_cdls():
    text = CDL_071_OPENING.read_text()
    assert "CDL-043" in text
    assert "CDL-044" in text
    assert "CDL-V1" in text


def test_cdl_071_opening_option_b_selected():
    text = CDL_071_OPENING.read_text()
    assert "Option B" in text
    assert "Normative consolidation" in text or "normative consolidation" in text


# ---------------------------------------------------------------------------
# Phase 851 — ratification evidence
# ---------------------------------------------------------------------------

def test_cdl_071_evidence_exists():
    assert CDL_071_EVIDENCE.exists(), "CDL-071 ratification evidence missing"


def test_cdl_071_evidence_tokens():
    text = CDL_071_EVIDENCE.read_text()
    for token in [
        "cdl_071_ratified_851",
        "cdl_071_temporal_tier_reconciliation_ratified_851.v0.1",
        "temporal_tier_framework_takes_constitutional_precedence",
        "cdl_043_tier_2_assignment_ratified",
        "cdl_044_tier_2_assignment_ratified",
        "cdl_v1_tier_2_assignment_ratified",
        "cdl_071_constitutional_precedence_on_tiering",
        "cdl_071_no_new_forward_obligations",
    ]:
        assert token in text, f"Missing token in CDL-071 evidence: {token!r}"


def test_cdl_071_evidence_four_criteria_satisfied():
    text = CDL_071_EVIDENCE.read_text()
    assert "Source citations" in text or "source citation" in text.lower()
    assert "Chosen option" in text or "chosen option" in text.lower()
    assert "implementation impact" in text.lower()
    assert "Verification artifact" in text or "verification artifact" in text.lower()


def test_cdl_071_evidence_no_code_changes():
    text = CDL_071_EVIDENCE.read_text()
    assert "No runtime files changed" in text or "no runtime files" in text.lower()


# ---------------------------------------------------------------------------
# CDL master log
# ---------------------------------------------------------------------------

def test_cdl_071_in_master_log():
    text = CDL_LOG.read_text()
    assert "CDL-071" in text, "CDL-071 not in master log"


def test_cdl_071_master_log_ratified():
    text = CDL_LOG.read_text()
    row_start = text.find("CDL-071")
    row = text[row_start:row_start + 1200]
    assert "ratified" in row, "CDL-071 master log row must show ratified"
    assert "ratified_phase: 851" in row
    assert "ratified_date: 2026-04-27" in row
    assert "opened_phase: 850" in row


def test_cdl_071_before_cdl_072_in_log():
    """CDL-071 must appear before CDL-072 in the log (numerical order)."""
    text = CDL_LOG.read_text()
    pos_071 = text.find("CDL-071")
    pos_072 = text.find("CDL-072")
    assert pos_071 < pos_072, "CDL-071 must appear before CDL-072 in master log"


# ---------------------------------------------------------------------------
# No ilc_core/ mutation
# ---------------------------------------------------------------------------

def test_no_ilc_core_mutation_in_cdl_071_phases():
    """CDL-071 is normative only — no ilc_core/ files may change."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~2", "HEAD"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    changed = result.stdout.splitlines()
    ilc_core_changes = [f for f in changed if f.startswith("ilc_core/")]
    assert not ilc_core_changes, (
        f"CDL-071 phases must not mutate ilc_core/. Changed:\n" +
        "\n".join(ilc_core_changes)
    )
