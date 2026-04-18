from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CAPSULE = REPO_ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.0.md"
GATE = REPO_ROOT / "docs/specs/ilc_window_727_732_closure_gate_732_v0.1.md"
PLANNING_INDEX = REPO_ROOT / "docs/PLANNING_INDEX.md"
ROADMAP = REPO_ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.3.md"
WALKTHROUGH = (
    REPO_ROOT
    / "docs/phases/phase_732_g8_capsule_v5_0_and_window_727_732_closure_gate_walkthrough.md"
)
STATUS = REPO_ROOT / "docs/phases/STATUS.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_capsule_exists():
    assert CAPSULE.exists(), "capsule v5.0 must exist"


def test_closure_gate_exists():
    assert GATE.exists(), "window 727-732 closure gate must exist"


def test_capsule_records_true_frontier():
    text = _read(CAPSULE)
    required = [
        "Supersedes: docs/specs/ilc_antigravity_context_capsule_v4.9.md",
        "Window 727-732 is now closed as the adjacent gated-economy hardening lane.",
        "Window 733+ is the next main-lane continuation to be defined.",
        "no CDL ratification occurred in-window",
        "no financial-shard activation occurred in-window",
        "`M-016 complete; next planned phase M-017 (Workload E: Validator Operability)`",
    ]
    for item in required:
        assert item in text, f"capsule must record {item}"


def test_closure_gate_confirms_window_outputs_and_boundaries():
    text = _read(GATE)
    required = [
        "window_727_732_closure_gate_published",
        "Phase `727` sequence lock",
        "Phase `728` carry-forward selection and boundary lock",
        "Phase `729` rights/licensing and gated-access disposition",
        "Phase `730` private/gated contract hardening note",
        "Phase `731` coherence report",
        "no_cdl_ratification_occurred_in_window_727_732",
        "no_financial_shard_activation_occurred_in_window_727_732",
        "`CDL-062` remained separate",
        "ADR-0022/private-gated boundary hardening remained separate",
        "window_733_plus_carry_forward_explicit",
    ]
    for item in required:
        assert item in text, f"closure gate must confirm {item}"


def test_closure_gate_records_track_b_line():
    text = _read(GATE)
    assert "track_b_status_verified_from_status_tail" in text
    assert (
        "`M-016 complete; next planned phase M-017 (Workload E: Validator Operability)`"
        in text
    )


def test_capsule_carry_forward_is_explicit():
    text = _read(CAPSULE)
    required = [
        "preserve the no-ratification and no-financial-activation posture of",
        "preserve separation between `CDL-062`, ADR-0022, and any later",
        "keep adjacent gated-economy hardening results as bounded planning surfaces",
        "re-verify the live Track B line from `STATUS.md` before any next-window",
    ]
    for item in required:
        assert item in text, f"capsule must carry forward {item}"


def test_planning_index_and_roadmap_advance_to_post_732_frontier():
    planning = _read(PLANNING_INDEX)
    roadmap = _read(ROADMAP)
    assert (
        "Window 727-732 CLOSED; Window 733+ next main-lane continuation to be defined; capsule v5.0;"
        in planning
    ), "PLANNING_INDEX must advance to the post-732 frontier"
    assert (
        "Context Capsule v5.0" in planning
        and "docs/specs/ilc_antigravity_context_capsule_v5.0.md" in planning
    ), "PLANNING_INDEX session canon must point to capsule v5.0"
    assert (
        "Session context**: Window 727-732 CLOSED (today); capsule v5.0 current; M-016 complete; next planned phase M-017"
        in roadmap
    ), "launch roadmap must reflect the post-732 frontier"
    assert "727-732 | Adjacent gated-economy hardening closure" in roadmap


def test_backfill_records_walkthrough_and_status():
    assert WALKTHROUGH.exists(), "phase 732 walkthrough must exist after backfill"
    text = _read(STATUS)
    assert "## Phase 732" in text, "STATUS must include a Phase 732 entry"
    assert (
        "Window 733+ — next main-lane continuation to be defined." in text
    ), "STATUS must point to the next main-lane continuation"
