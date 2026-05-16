from __future__ import annotations

from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]

PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1369_g8_sequence_lock.md"
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1369_1390_sequence_lock_v0.1.md"
CAPSULE = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.58.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1369_sequence_lock_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
LAUNCH_ROADMAP = ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"

REQUIRED_TOKENS = (
    "window_1369_1390_sequence_lock_committed_phase_1369.v0.1",
    "capsule_v5_58_supersedes_v5_57",
    "hardening_carry_forward_disposition_recorded_phase_1369",
    "phase_1369_fix1_authorized_numeric_hardening",
    "go_phase_1374_required_cdl_088_opening",
    "go_phase_1389_required_public_claimability_gate",
    "production_minting_activation_deferred_phase_1368",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1369_prompt_is_valid_and_future_cdl_088_token_is_not_prerequisite() -> None:
    assert validate(PROMPT) == []
    prompt = read(PROMPT)

    assert "Future output token that must remain absent before Phase 1374 execution" in prompt
    assert "cdl_088_not_ratified_phase_1374" in prompt
    assert "1387a" in prompt


def test_sequence_lock_and_capsule_carry_required_tokens() -> None:
    sequence_lock = read(SEQUENCE_LOCK)
    capsule = read(CAPSULE)

    for token in REQUIRED_TOKENS:
        assert token in sequence_lock
        assert token in capsule

    assert "Window 1369-1390 is OPEN through Phase 1369 only" in sequence_lock
    assert "Phase 1369 Fix1" in sequence_lock
    assert "Phase 1387a" in sequence_lock
    assert "Phase 1389" in sequence_lock


def test_sequence_lock_routes_hardening_and_public_economics_firewall() -> None:
    sequence_lock = read(SEQUENCE_LOCK)

    assert "Decimal magnitude" in sequence_lock
    assert "Genesis intervention counter TOCTOU" in sequence_lock
    assert "Governance weight accepts unbounded" in sequence_lock
    assert "LMDB pruning batch cap" in sequence_lock
    assert "get_epoch_chain()" in sequence_lock
    assert "Phase 1386a" in sequence_lock
    assert "operator-local advisory scoring only" in sequence_lock
    assert "public-economics admission firewall" in sequence_lock


def test_status_planning_and_walkthrough_reference_phase_1369_outputs() -> None:
    for path in (STATUS, PLANNING_INDEX, WALKTHROUGH, LAUNCH_ROADMAP):
        text = read(path)
        assert "Phase 1369" in text
        assert "docs/specs/ilc_phase_1369_1390_sequence_lock_v0.1.md" in text
        assert "phase_1369_fix1_authorized_numeric_hardening" in text
        assert "go_phase_1374_required_cdl_088_opening" in text
        assert "go_phase_1389_required_public_claimability_gate" in text

    assert "Window 1369-1390 is OPEN through Phase 1369 only" in read(PLANNING_INDEX)
    assert "Window 1369-1390 is OPEN through Phase 1369 only" in read(LAUNCH_ROADMAP)
