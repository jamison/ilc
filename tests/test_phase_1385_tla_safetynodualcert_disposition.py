from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DISPOSITION = ROOT / "docs/specs/ilc_tla_plus_safetynodualcert_disposition_1385_v0.1.md"
WALKTHROUGH = (
    ROOT / "docs/phases/phase_1385_tla_plus_safetynodualcert_disposition_walkthrough.md"
)
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
WINDOW_PLAN = ROOT / "docs/specs/ilc_window_1369_1390_candidate_phase_grouping_v0.1.md"
FORWARD_PLAN = (
    ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
)
ROADMAP = ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
ADR_MAP = ROOT / "docs/architecture/ilc_cdl_adr_implementation_map_v0.1.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1385_disposition_records_defer_with_authority() -> None:
    text = read(DISPOSITION)

    assert "tla_plus_safetynodualcert_disposed_phase_1385" in text
    assert "safetynodualcert_deferred_with_authority_phase_1385" in text
    assert "phase_1385_epoch_checkpoint_safetynodualcert_deferred_to_spec_d" in text
    assert "Disposition selected: defer-with-authority" in text
    assert "Graph delta:" in text


def test_phase_1385_distinguishes_spec_b_from_epoch_checkpoint_scope() -> None:
    text = read(DISPOSITION)

    assert "owned-object" in text
    assert "epoch-checkpoint" in text
    assert "shared-object" in text
    assert "Spec B" in text
    assert "Spec D" in text
    assert "docs/specs/tla/ilc_ecu_fast_path_bcast.tla" in text
    assert "tools/tla/ilc_ecu_fast_path_bcast.tlc.out" in text
    assert "not proof of the epoch-checkpoint/shared-object property" in text


def test_phase_1385_m019_limitations_are_explicit() -> None:
    text = read(DISPOSITION)

    assert "tools/testbed/m019_run.log" in text
    assert "BroadcastHonest" in text
    assert "ConflictingTransfer / Equivocation Detected" in text
    assert "loopback four-validator testbed only" in text
    assert "testnet fault-injection build" in text
    assert "not a durable" in text
    assert "not a formal proof" in text


def test_phase_1385_planning_surfaces_are_updated() -> None:
    combined = "\n".join(
        read(path)
        for path in (STATUS, PLANNING_INDEX, WINDOW_PLAN, FORWARD_PLAN, ROADMAP, ADR_MAP)
    )

    assert "tla_plus_safetynodualcert_disposed_phase_1385" in combined
    assert "safetynodualcert_deferred_with_authority_phase_1385" in combined
    assert "Phase 1386" in read(PLANNING_INDEX)
    assert "epoch-checkpoint" in combined
    assert "owned-object" in combined


def test_phase_1385_walkthrough_has_required_sections_and_no_ellipses() -> None:
    text = read(WALKTHROUGH)

    assert "## 1. Purpose" in text
    assert "## 2. Delivery Summary" in text
    assert "## 3. Disposition Selected" in text
    assert "## 4. M-019 Coverage Characterization" in text
    assert "..." not in text
    assert "\u2026" not in text
