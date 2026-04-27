"""Phase 852 window 848–852 closure gate.

Token: window_848_852_closed
Token: capsule_v5_21_published
"""
import subprocess
from pathlib import Path

REPO = Path(__file__).parent.parent

CAPSULE_V5_21 = REPO / "docs" / "specs" / "ilc_antigravity_context_capsule_v5.21.md"
COHERENCE = REPO / "docs" / "specs" / "ilc_integration_coherence_report_852_v0.1.md"
STATUS_MD = REPO / "docs" / "phases" / "STATUS.md"
CHECKLIST_V0_3 = REPO / "docs" / "specs" / "ilc_option_b_graduation_checklist_state_849_v0.3.json"
CDL_LOG = REPO / "docs" / "specs" / "ilc_constitutional_decision_log_v0.1.md"


def test_capsule_v5_21_exists():
    assert CAPSULE_V5_21.exists()


def test_capsule_v5_21_supersedes_v5_20():
    text = CAPSULE_V5_21.read_text()
    assert "capsule_v5_21_supersedes_v5_20" in text
    assert "v5.20" in text


def test_capsule_records_cdl_071_ratified():
    text = CAPSULE_V5_21.read_text()
    assert "cdl_071_ratified_recorded_in_capsule_v5_21" in text
    cdl_table_line = [l for l in text.splitlines() if "CDL-071" in l and ("Ratified" in l or "ratified" in l)]
    assert cdl_table_line, "Capsule must show CDL-071 as Ratified"


def test_capsule_records_graduation_checklist():
    text = CAPSULE_V5_21.read_text()
    assert "graduation_checklist_v0_3_recorded_in_capsule_v5_21" in text
    assert "all_rows_satisfied" in text or "All 9 rows" in text


def test_coherence_report_exists():
    assert COHERENCE.exists()


def test_coherence_report_tokens():
    text = COHERENCE.read_text()
    assert "coherence_report_852_published" in text
    assert "window_848_852_coherent" in text


def test_status_md_all_five_phases():
    text = STATUS_MD.read_text()
    for phase in ["## Phase 848", "## Phase 849", "## Phase 850", "## Phase 851", "## Phase 852"]:
        assert phase in text, f"STATUS.md missing {phase}"


def test_cdl_071_ratified_in_cdl_log():
    text = CDL_LOG.read_text()
    assert "CDL-071" in text
    row_start = text.find("CDL-071")
    row = text[row_start:row_start + 1200]
    assert "ratified_phase: 851" in row
    assert "ratified_date: 2026-04-27" in row


def test_checklist_v0_3_all_rows_satisfied():
    import json
    data = json.loads(CHECKLIST_V0_3.read_text())
    assert data["all_rows_satisfied"] is True
    assert data["option_b_selected"] is True


def test_window_closure_tokens_in_this_file():
    text = Path(__file__).read_text()
    assert "window_848_852_closed" in text
    assert "capsule_v5_21_published" in text
