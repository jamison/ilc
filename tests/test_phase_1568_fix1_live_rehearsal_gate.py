from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1568_fix1_status_blocks_closure_until_fix2() -> None:
    status = _read("docs/phases/STATUS.md")
    assert "phase_1568_live_rehearsal_rerun_required_phase_1568_fix1" in status
    assert "phase_1568_live_rehearsal_rerun_pass_phase_1568_fix2" not in status


def test_phase_1569_prompt_hard_stops_without_live_rerun_pass() -> None:
    prompt = _read("docs/antigravity_tasks/antigravity_prompt__phase_1569_g10_block6_rehearsal_closure_wipe.md")
    assert "phase_1568_live_rehearsal_rerun_required_phase_1568_fix1" in prompt
    assert "phase_1568_live_rehearsal_rerun_pass_phase_1568_fix2" in prompt
    assert "Phase 1568-Fix2 live rerun missing" in prompt


def test_phase_1568_fix2_prompt_requires_live_economic_path() -> None:
    prompt = _read("docs/antigravity_tasks/antigravity_prompt__phase_1568_fix2_g10_live_private_soft_rc_rerun.md")
    required_terms = [
        "superseded_by_fix2b_fix2c_fix2d_fix2e",
        "Do not run this prompt with `GO Phase 1568-Fix2`",
        "Only synthetic input",
        "four issuance epochs",
        "CDL-048",
        "settlement root",
        "OpenClaw and Codex must submit",
        "Read-only balance checks are not sufficient",
    ]
    for term in required_terms:
        assert term in prompt


def test_phase_1568_fix2_split_prompts_exist() -> None:
    for path in [
        "docs/antigravity_tasks/antigravity_prompt__phase_1568_fix2b_g10_runtime_identity_economics_hardening.md",
        "docs/antigravity_tasks/antigravity_prompt__phase_1568_fix2c_g10_four_machine_d2d_readiness.md",
        "docs/antigravity_tasks/antigravity_prompt__phase_1568_fix2d_g10_live_production_path_soft_rc.md",
        "docs/antigravity_tasks/antigravity_prompt__phase_1568_fix2e_g10_pre_signing_guard_attack_surface.md",
    ]:
        assert (ROOT / path).exists(), path


def test_correction_plan_preserves_two_track_boundary() -> None:
    plan = _read("docs/specs/ilc_phase_1568_fix1_live_rehearsal_correction_plan_v0.1.md")
    assert "Clean Atlas track" in plan
    assert "Rehearsal graph track" in plan
    assert "Phase 1569 is blocked" in plan
