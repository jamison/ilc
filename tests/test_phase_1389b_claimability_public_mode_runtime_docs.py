"""Phase 1389b documentation and routing checks."""

from pathlib import Path


REPO = Path(__file__).resolve().parents[1]

PROMPT = REPO / "docs/antigravity_tasks/antigravity_prompt__phase_1389b_g8_claimability_public_mode_runtime.md"
SPEC = REPO / "docs/specs/ilc_claimability_public_mode_runtime_1389b_v0.1.md"
WALKTHROUGH = REPO / "docs/phases/phase_1389b_claimability_public_mode_runtime_walkthrough.md"
STATUS = REPO / "docs/phases/STATUS.md"
PLANNING = REPO / "docs/PLANNING_INDEX.md"
SEQUENCE_LOCK = REPO / "docs/specs/ilc_phase_1369_1390_sequence_lock_v0.1.md"
GROUPING = REPO / "docs/specs/ilc_window_1369_1390_candidate_phase_grouping_v0.1.md"

TOKENS = {
    "claimability_public_mode_runtime_phase_1389b",
    "claim_nullifier_registry_v1_active_phase_1389b",
    "duplicate_claim_registry_active_phase_1389b",
    "claimability_verifier_public_mode_ready_phase_1389b",
    "public_mode_blockers_empty_phase_1389b",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1389b_docs_exist_and_record_tokens() -> None:
    combined = "\n".join(_text(path) for path in (PROMPT, SPEC, WALKTHROUGH))
    for token in TOKENS:
        assert token in combined
    assert "Runtime commit:** `aed33474`" in combined


def test_phase_1389b_status_and_planning_record_completion() -> None:
    combined = "\n".join(
        _text(path)
        for path in (
            STATUS,
            PLANNING,
            SEQUENCE_LOCK,
            GROUPING,
        )
    )
    for token in TOKENS:
        assert token in combined
    assert "Phase 1389 has now been rerun" in combined
    assert "Phase 1389 v0.2 PASS report" in combined


def test_phase_1389b_docs_preserve_non_activation_boundary() -> None:
    combined = "\n".join(_text(path) for path in (SPEC, WALKTHROUGH, STATUS))
    for phrase in (
        "does not rerun Phase 1389",
        "activate public claimability",
        "wallet action",
        "ECU minting",
        "ILC settlement",
        "CDL mutation",
    ):
        assert phrase in combined


def test_phase_1389b_corrects_1397a_fat_finger() -> None:
    combined = "\n".join(_text(path) for path in (SPEC, WALKTHROUGH, PLANNING, SEQUENCE_LOCK))
    assert "fat-finger" in combined
    assert "Phase 1389b subsequently executed after Phase 1389a" in combined
