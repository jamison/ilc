from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CDL_REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1363_blocking_authority_deliberation_prelock_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1343_1368_sequence_lock_v0.1.md"
FORWARD_PLAN = ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
RUNTIME = ROOT / "ilc_core/epoch/epoch_boundary_witness_runtime.py"


REQUIRED_TOKENS = (
    "blocking_authority_deliberation_prelock_phase_1363.v0.1",
    "blocking_authority_scope_locked_phase_1363",
    "cdl_055_cdl_030_interaction_clauses_locked_phase_1363",
    "blocking_authority_not_ratified_phase_1363",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _decision_rows() -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in _read(CDL_REGISTER).splitlines():
        if line.startswith("| CDL-"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) >= 7 and cells[3] in {"open", "ratified"}:
                rows[cells[0]] = line
    return rows


def _squash(text: str) -> str:
    return " ".join(text.split())


def test_phase_1363_prelocks_cdl_089_without_ratification() -> None:
    rows = _decision_rows()
    row = rows["CDL-089"]

    assert "| open |" in row
    assert "prelock_phase: 1363" in row
    assert "prelock_date: 2026-05-16" in row
    assert "blocking_authority_deliberation_prelock_phase_1363.v0.1" in row
    assert "blocking_authority_scope_locked_phase_1363" in row
    assert "cdl_055_cdl_030_interaction_clauses_locked_phase_1363" in row
    assert "blocking_authority_not_ratified_phase_1363" in row
    assert "ratified_phase: 1363" not in row
    assert "BLOCKING_AUTHORITY_DEFERRED` change in Phase 1363" in row


def test_phase_1363_scoped_prelock_record_locks_scope_and_interactions() -> None:
    text = _read(CDL_REGISTER)
    squashed = _squash(text)

    assert "## Scoped Prelock Record (Phase 1363: CDL-089)" in text
    for token in REQUIRED_TOKENS:
        assert token in text

    assert "Phase 1362 recorded carry-forward items rather than a literal open-question" in squashed
    assert "scope is locked to the CDL-057 epoch-boundary witness lane" in squashed
    assert "CDL-053 remains reserved for Werner-credit architecture" in squashed
    assert "CDL-088 remains unopened and reserved for public-claimability authority" in squashed
    assert "A CDL-057 witness-lane block is not itself a CDL-055 liveness miss" in squashed
    assert "`GENESIS_STAKE_AMOUNT = 400`" in text
    assert "`LIVENESS_MISS_THRESHOLD = 8`" in text
    assert "`LIVENESS_PENALTY_FRACTION = 0.25`" in text
    assert "`EQUIVOCATION_FULL_SLASH = 1`" in text
    assert "The ECU price clamp remains" in squashed
    assert "`P_min = 0.75`, `P_max = 1.30`" in text
    assert "must not recompute, widen, narrow, override, or bypass the ECU" in squashed


def test_phase_1363_preserves_related_cdl_rows_and_runtime_deferred_flag() -> None:
    rows = _decision_rows()
    runtime = _read(RUNTIME)

    for decision_id in ("CDL-030", "CDL-055", "CDL-057"):
        assert decision_id in rows
        assert "| ratified |" in rows[decision_id]

    assert 'EPOCH_BOUNDARY_WITNESS_RUNTIME_VERSION = "epoch_boundary_witness_runtime_516.v0.1"' in runtime
    assert "BLOCKING_AUTHORITY_DEFERRED = True" in runtime
    assert "BLOCKING_AUTHORITY_DEFERRED = False" not in runtime
    assert "def is_blocking_authority_active() -> bool:" in runtime
    assert "return False" in runtime


def test_phase_1363_walkthrough_records_required_evidence() -> None:
    text = _read(WALKTHROUGH)

    assert "..." not in text
    for token in REQUIRED_TOKENS:
        assert token in text

    for heading in (
        "## Purpose",
        "## Open Question Resolution Record",
        "## Blocking-Authority Scope",
        "## CDL-055 Interaction Clause",
        "## CDL-030 Interaction Clause",
        "## Delivery Summary",
        "## Key Outcomes",
        "## Pre-Execution Verification Record",
        "## CDL Mutation Commit Evidence",
        "## Blocking Authority Deferred Confirmation",
        "## Carry-Forward",
        "## Graph Delta",
    ):
        assert heading in text

    assert "ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1363" in text
    assert "graph_delta=load_bearing_register_changed:docs/specs/ilc_constitutional_decision_log_v0.1.md -> governance/cdl089-prelock" in text


def test_phase_1363_status_and_planning_surfaces_advance_to_1364() -> None:
    status = _read(STATUS)
    planning = _read(PLANNING_INDEX)
    sequence_lock = _read(SEQUENCE_LOCK)
    forward_plan = _read(FORWARD_PLAN)

    assert "## Phase 1363" in status
    assert "| 1363 | blocking authority deliberation prelock | COMPLETE |" in status
    assert "prelock written; scope locked; CDL-055/CDL-030 interaction clauses locked; not ratified" in status

    assert "Window 1343-1368 is OPEN through Phase 1363" in planning
    assert "Phase 1364 is the next planned phase" in planning
    assert "CDL-089 prelock complete" in planning
    assert "CDL-089 ratification" in planning

    assert "| 1363 | Blocking-authority deliberation/prelock | COMPLETE" in sequence_lock
    assert "| 1364 | Blocking-authority ratification + CDL-057 activation | SENSITIVE; future explicit GO and CDL mutation authority required; next planned phase." in sequence_lock

    assert "| 1363 | Blocking-authority deliberation/prelock: CDL-089 prelock" in forward_plan
    assert "COMPLETE; CDL-089 remains open and not ratified" in forward_plan
