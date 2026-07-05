from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WALKTHROUGH = ROOT / "docs/phases/phase_1569_rehearsal_closure_wipe_walkthrough.md"
SPEC = ROOT / "docs/specs/ilc_phase_1569_rehearsal_closure_wipe_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
LOCAL_NAMESPACE_ROOT = ROOT / "out/block6_rehearsal/block6_rehearsal_2026_06_27_v0_1"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_walkthrough_exists_with_required_sections() -> None:
    text = _read(WALKTHROUGH)

    for section in (
        "## Purpose",
        "## Delivery Summary",
        "## Defect Inventory",
        "## Evidence Hash Table",
        "## Wipe Verification",
        "## Non-Claims",
        "## Carry-Forward",
    ):
        assert section in text

    assert "No ellipses in walkthrough." in text


def test_support_spec_records_adjudication_path_and_receipt_hash() -> None:
    text = _read(SPEC)

    assert "fix2d_rerun005_classified_as_quote_only_partial_pass" in text
    assert "phase_1568_fix2d_adj_rerun005_adjudication_complete" in text
    assert "fix2d_rerun006_required_for_full_obl_040_043_closure` | absent" in text
    assert "receipt_sha256=b881e9ba4ef291226d7601a6f55cdb196fe512701e623e973edb94371b4f59ef" in text
    assert "all_hosts_confirmed_wiped=true" in text


def test_status_records_exactly_one_phase_1569_scenario_token() -> None:
    text = _read(STATUS)
    scenario_tokens = (
        "defect_inventory_empty_phase_1569",
        "defect_inventory_1_items_phase_1569",
        "defect_inventory_2_items_phase_1569",
        "defect_inventory_3_items_phase_1569",
        "defect_inventory_protocol_gap_phase_1569",
    )
    present = [token for token in scenario_tokens if token in text]

    assert present == ["defect_inventory_empty_phase_1569"]


def test_status_records_closure_and_wipe_tokens() -> None:
    text = _read(STATUS)

    for token in (
        "block6_rehearsal_closed_phase_1569",
        "rehearsal_wipe_executed_phase_1569",
        "rehearsal_state_confirmed_wiped_phase_1569",
        "public_path_remains_blocked_phase_1569",
    ):
        assert token in text


def test_local_rehearsal_namespace_is_wiped() -> None:
    assert not LOCAL_NAMESPACE_ROOT.exists()


def test_no_scenario_c_phase_1573_authorization_from_phase_1569() -> None:
    text = _read(WALKTHROUGH)

    assert "defect_inventory_protocol_gap_phase_1569" not in _read(STATUS)
    assert "GO Phase 1573a" in text
    assert "separate explicit `GO Phase 1573a`" in text
    assert "separate `GO Phase 1573`" in text
