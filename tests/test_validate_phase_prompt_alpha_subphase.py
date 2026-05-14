from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]
PROMPT_DIR = ROOT / "docs/antigravity_tasks"


def test_phase_prompt_validator_accepts_authorized_alpha_subphase() -> None:
    prompt = (
        PROMPT_DIR
        / "antigravity_prompt__phase_1351a_g8_cdl_029_amendment_post_theta_hard_dust_routing.md"
    )

    errors = validate(prompt)

    assert "invalid_filename_pattern" not in errors
    assert "invalid_h1_pattern" not in errors
    assert not any(error.startswith("h1_phase_mismatch") for error in errors)
