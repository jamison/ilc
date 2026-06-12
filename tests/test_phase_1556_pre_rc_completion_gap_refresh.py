from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1556_1564_sequence_lock_v0.1.md"
GAP_REFRESH = ROOT / "docs/specs/ilc_gap_refresh_1556_pre_rc_completion_v0.1.md"
CENSUS_JSON = ROOT / "docs/specs/ilc_phase_boolean_token_census_600_plus_1556_v0.1.json"
CENSUS_MD = ROOT / "docs/specs/ilc_phase_boolean_token_census_600_plus_1556_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1556_pre_rc_completion_sequence_lock_walkthrough.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
STATUS = ROOT / "docs/phases/STATUS.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1556_artifacts_exist_and_tokens_present():
    for path in (SEQUENCE_LOCK, GAP_REFRESH, CENSUS_JSON, CENSUS_MD, WALKTHROUGH):
        assert path.exists(), f"missing Phase 1556 artifact: {path}"

    text = read(SEQUENCE_LOCK)
    for token in (
        "window_1556_1564_opened",
        "window_1555p_closed_inherits_to_window_1556",
        "pre_rc_completion_sequence_lock_committed_phase_1556",
        "gap_refresh_1556_pre_rc_completion_committed",
        "mempalace_rebuild_complete_phase_1556",
        "hb_obligations_carry_forward_inventoried_phase_1556",
        "phase_numbering_p_suffix_retired_phase_1556",
        "boolean_token_census_600_plus_committed_phase_1556",
        "public_path_remains_blocked_phase_1556",
    ):
        assert token in text


def test_phase_order_and_sensitive_gates_are_locked():
    text = read(SEQUENCE_LOCK)
    assert "| 1556 | Sequence lock" in text
    assert "| 1557 | HB-001" in text
    assert "| 1558 | HB-003" in text
    assert "| 1559 | HB-002" in text
    assert "requires `GO Phase 1560`" in text
    assert "requires `GO Phase 1561`" in text
    assert "requires `GO Phase 1564`" in text
    assert "p` suffix is retired" in text


def test_gap_refresh_records_hb_state_and_obl_boundaries():
    text = read(GAP_REFRESH)
    assert "OBL-002 remains permanent invariant" in text
    assert "OBL-030 remains open" in text
    assert "assertion_schema.py" in text
    assert "Phase 858" in text
    assert "layer0_protocol_bundle.py" in text
    assert "schemas=" in text
    assert "bootstrap_fetch_runtime.py" in text
    assert "serving_receipt.py" in text
    assert "routed to Phase 1559" in text
    assert "Agent INIT" in text
    assert "ECU live smoke" in text
    assert "Invitation provenance" in text
    assert "OpenClaw harness coverage" in text


def test_boolean_token_census_schema_and_classifications():
    data = json.loads(read(CENSUS_JSON))
    assert data["schema_version"] == "phase_boolean_token_census_600_plus_1556.v0.1"
    assert data["generated_phase"] == "1556"
    assert data["summary"]["total_entries"] > 100
    assert data["summary"]["files_scanned"] > 20
    classes = data["summary"]["classification_counts"]
    for classification in (
        "code_style_noise",
        "default_off_guard",
        "possible_orphan",
        "still_blocking",
    ):
        assert classification in classes
    assert data["entries"]
    first = data["entries"][0]
    for key in (
        "phase",
        "file_path",
        "line_number",
        "token",
        "boolean_value",
        "surrounding_text",
        "classification",
    ):
        assert key in first


def test_boolean_token_census_summary_preserves_non_authorization():
    text = read(CENSUS_MD)
    assert "boolean_token_census_600_plus_committed_phase_1556" in text
    assert "possible_orphan" in text
    assert "still_blocking" in text
    assert "sort_keys=True" in text
    assert "No raw boolean hit authorizes public RC" in text
    assert "PUBLIC-RC-GATE-001" in text


def test_frontier_docs_advance_to_phase_1557_without_public_activation():
    planning = read(PLANNING_INDEX)
    status = read(STATUS)
    for text in (planning, status):
        assert "Phase 1556" in text
        assert "pre_rc_completion_sequence_lock_committed_phase_1556" in text
        assert "public_path_remains_blocked_phase_1556" in text
        assert "Phase 1557" in text
    assert "No public RC was activated" in read(WALKTHROUGH)
