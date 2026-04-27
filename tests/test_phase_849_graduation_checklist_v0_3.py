"""Phase 849 graduation checklist v0.3 gate tests.

Verifies:
1. Checklist v0.3 artifact exists and supersedes v0.1.
2. option_b_selected=true, option_d_active=false.
3. Row 5 status is runtime_closed.
4. All 9 rows are satisfied.
5. Sequence lock tokens present.
6. No CDL mutation in Phase 849.

Token: graduation_checklist_v0_3_published_849
Token: option_b_selected_recorded_in_checklist_v0_3
Token: row5_runtime_closed_in_checklist_v0_3
"""
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).parent.parent
CHECKLIST_V0_3 = REPO / "docs" / "specs" / "ilc_option_b_graduation_checklist_state_849_v0.3.json"
CHECKLIST_V0_1 = REPO / "docs" / "specs" / "ilc_option_b_graduation_checklist_state_682_v0.1.json"
SEQ_LOCK = REPO / "docs" / "phases" / "phase_848_window_848_852_sequence_lock.md"
CDL_LOG = REPO / "docs" / "specs" / "ilc_constitutional_decision_log_v0.1.md"


def load_checklist() -> dict:
    return json.loads(CHECKLIST_V0_3.read_text())


# ---------------------------------------------------------------------------
# Artifact existence
# ---------------------------------------------------------------------------

def test_checklist_v0_3_exists():
    assert CHECKLIST_V0_3.exists(), "Graduation checklist v0.3 missing"


def test_checklist_v0_1_still_exists():
    """v0.1 must not be deleted — it is a historical evidence artifact."""
    assert CHECKLIST_V0_1.exists(), "Original graduation checklist v0.1 must be preserved"


def test_sequence_lock_exists():
    assert SEQ_LOCK.exists(), "Window 848-852 sequence lock missing"


def test_sequence_lock_tokens():
    text = SEQ_LOCK.read_text()
    for token in [
        "window_848_852_sequence_lock_active",
        "window_848_852_primary_gate",
        "graduation_checklist_v0_3_precedes_cdl_071",
    ]:
        assert token in text, f"Missing sequence lock token: {token!r}"


# ---------------------------------------------------------------------------
# Checklist v0.3 content
# ---------------------------------------------------------------------------

def test_checklist_is_valid_json():
    data = load_checklist()
    assert isinstance(data, dict)


def test_checklist_supersedes_v0_1():
    data = load_checklist()
    assert data["supersedes"] == "ilc_option_b_graduation_checklist_state_682_v0.1"


def test_option_b_selected():
    data = load_checklist()
    assert data["option_b_selected"] is True, (
        "option_b_selected must be True — Option B was selected Phase 814"
    )


def test_option_d_not_active():
    data = load_checklist()
    assert data["option_d_active"] is False, (
        "option_d_active must be False — Option D is no longer the active posture"
    )


def test_option_b_selection_phase():
    data = load_checklist()
    assert data["option_b_selection_phase"] == 814


def test_option_b_gate_verdict():
    data = load_checklist()
    assert "option_b_gate_synthesis_verdict_go" in data["option_b_gate_verdict"]


def test_row_5_is_runtime_closed():
    data = load_checklist()
    row5 = next(r for r in data["rows"] if r["row"].startswith("5."))
    assert row5["status"] == "runtime_closed", (
        f"Row 5 must be runtime_closed in v0.3. Got: {row5['status']!r}"
    )


def test_row_5_was_partial_in_v0_1():
    """Confirm v0.3 records the prior state for audit trail."""
    data = load_checklist()
    row5 = next(r for r in data["rows"] if r["row"].startswith("5."))
    assert row5.get("prior_status_v0_1") == "partial", (
        "Row 5 v0.3 entry must record prior_status_v0_1=partial for audit trail"
    )


def test_all_nine_rows_present():
    data = load_checklist()
    assert len(data["rows"]) == 9, f"Expected 9 rows, got {len(data['rows'])}"


def test_all_rows_satisfied():
    data = load_checklist()
    assert data["all_rows_satisfied"] is True
    for row in data["rows"]:
        assert row["status"] in ("runtime_closed", "closed"), (
            f"Row not satisfied: {row['row']!r} — status: {row['status']!r}"
        )


def test_row_5_source_ref_points_to_rerun_evidence():
    data = load_checklist()
    row5 = next(r for r in data["rows"] if r["row"].startswith("5."))
    assert "rerun_846" in row5["source_ref"], (
        "Row 5 source_ref must point to Phase 846 re-run evidence"
    )


def test_updated_phase_is_849():
    data = load_checklist()
    assert data["updated_phase"] == 849


def test_no_cdl_mutation_in_phase_849():
    """Phase 849 must not mutate any CDL document."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    changed = result.stdout.splitlines()
    cdl_changes = [f for f in changed if "cdl_" in f.lower() and f.endswith(".md")]
    assert not cdl_changes, (
        f"Phase 849 must not mutate CDL documents. Changed:\n" +
        "\n".join(cdl_changes)
    )
