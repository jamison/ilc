from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CDL_REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
RESOLUTION_DOC = ROOT / "docs/specs/ilc_blocking_authority_vehicle_selection_phase_1344_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1362_blocking_authority_vehicle_opening_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1343_1368_sequence_lock_v0.1.md"
FORWARD_PLAN = ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
RUNTIME = ROOT / "ilc_core/epoch/epoch_boundary_witness_runtime.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _decision_rows() -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in _read(CDL_REGISTER).splitlines():
        if line.startswith("| CDL-"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if cells:
                rows[cells[0]] = line
    return rows


def test_phase_1362_resolution_doc_selects_cdl_089_unambiguously() -> None:
    text = _read(RESOLUTION_DOC)

    assert "FINAL" in text
    assert "**CDL-089**" in text
    assert "blocking_authority_vehicle_selected_cdl_089_human_authorized_2026_05_16" in text
    assert "blocking_authority_vehicle_selection_deferred_to_phase_1362_phase_1344_resolved" in text
    assert "CDL-053" in text
    assert "Excluded by `blocking_authority_vehicle_must_not_be_cdl_053_phase_1344`" in text
    assert "CDL-088" in text
    assert "do not disturb" in text


def test_phase_1362_opens_cdl_089_only_and_preserves_cdl_053_088_boundaries() -> None:
    rows = _decision_rows()
    walkthrough = _read(WALKTHROUGH)

    assert "CDL-089" in rows
    assert "| CDL-089 |" in rows["CDL-089"]
    assert "| ratified |" in rows["CDL-089"]
    assert "| open |" in walkthrough
    assert "opened_phase: 1362" in rows["CDL-089"]
    assert "opened_date: 2026-05-16" in rows["CDL-089"]
    assert "cdl_057_activation_vehicle_open_phase_1362" in rows["CDL-089"]
    assert "cdl_053_vehicle_collision_resolved_phase_1362" in rows["CDL-089"]
    assert "blocking_authority_not_ratified_phase_1362" in walkthrough
    assert "docs/specs/ilc_blocking_authority_vehicle_selection_phase_1344_v0.1.md" in rows["CDL-089"]

    assert "CDL-053" not in rows
    assert "CDL-088" not in rows


def test_phase_1362_runtime_deferral_record_is_historical_after_phase_1364() -> None:
    runtime = _read(RUNTIME)
    walkthrough = _read(WALKTHROUGH)

    assert "Phase 1362 did not modify `ilc_core/`" in walkthrough
    assert "BLOCKING_AUTHORITY_DEFERRED = True" in walkthrough
    assert "`is_blocking_authority_active()` still returns `False`" in walkthrough

    assert 'EPOCH_BOUNDARY_WITNESS_RUNTIME_VERSION = "epoch_boundary_witness_blocking_active_phase_1364.v0.1"' in runtime
    assert 'CDL_057_DEPENDENCY = "cdl_057_ratified_511.v0.1"' in runtime
    assert "BLOCKING_AUTHORITY_DEFERRED = False" in runtime
    assert "return not BLOCKING_AUTHORITY_DEFERRED" in runtime


def test_phase_1362_walkthrough_records_required_tokens_and_hard_gate() -> None:
    text = _read(WALKTHROUGH)

    for token in (
        "blocking_authority_vehicle_opening_phase_1362.v0.1",
        "cdl_053_vehicle_collision_resolved_phase_1362",
        "blocking_authority_cdl_vehicle_selected_phase_1362",
        "cdl_057_activation_vehicle_open_phase_1362",
        "blocking_authority_not_ratified_phase_1362",
    ):
        assert token in text

    assert "docs/specs/ilc_blocking_authority_vehicle_selection_phase_1344_v0.1.md" in text
    assert "CDL-089" in text
    assert "HARD GATE PASS" in text
    assert "ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1362" in text
    assert "graph_delta=load_bearing_register_changed:docs/specs/ilc_constitutional_decision_log_v0.1.md -> governance/cdl089" in text


def test_phase_1362_status_and_planning_surfaces_advance_to_1363() -> None:
    status = _read(STATUS)
    planning = _read(PLANNING_INDEX)
    sequence_lock = _read(SEQUENCE_LOCK)
    forward_plan = _read(FORWARD_PLAN)

    assert "## Phase 1362" in status
    assert "CDL vehicle opened (CDL-089)" in status
    assert "BLOCKING_AUTHORITY_DEFERRED still True" in status

    assert "Phase 1362 addendum" in planning
    assert "Phase 1363 was subsequently executed" in planning
    assert "CDL-089" in planning

    assert "| 1362 | Blocking-authority vehicle opening | COMPLETE" in sequence_lock
    assert "| 1363 | Blocking-authority deliberation/prelock | COMPLETE" in sequence_lock

    assert "| 1362 | Blocking-authority vehicle opening: open CDL-089" in forward_plan
    assert "| 1363 | Blocking-authority deliberation/prelock: CDL-089 prelock" in forward_plan
    assert "| CDL-089, CDL-057 |" in forward_plan
