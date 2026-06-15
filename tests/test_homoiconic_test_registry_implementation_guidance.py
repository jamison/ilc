from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
GUIDANCE = ROOT / "docs/specs/ilc_homoiconic_test_registry_implementation_guidance_v0.1.md"
PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix32_g10_homoiconic_test_registry_contract.md"
)
FORWARD_PLAN = ROOT / "docs/specs/ilc_homoiconic_test_registry_forward_plan_v0.1.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_guidance_records_required_pushback_and_no_authority_overclaim():
    text = _read(GUIDANCE)

    for required in [
        "AST parsing alone is not sufficient",
        "pytest --collect-only",
        "Passing tests are evidence, not authority",
        "Test nodes must survive pruning",
        "Private and environment-sensitive tests need gates",
        "Candidate Atlas nodes are not Genesis-signed until the signing gate",
    ]:
        assert required in text


def test_guidance_defines_concrete_phase_route():
    text = _read(GUIDANCE)

    for phase in [
        "Phase 1545p-Fix32: contract",
        "Phase 1545p-Fix33: test-node Atlas smoke audit",
        "Phase 1545p-Fix34: pytest collection to function-node candidates",
        "Phase 1545p-Fix35: canonical evidence envelope rehearsal",
        "Phase 1545p-Fix36: graph-derived test frontier report",
    ]:
        assert phase in text

    for node_kind in ["test_file", "test_function", "test_evidence_run"]:
        assert f'"node_kind": "{node_kind}"' in text


def test_fix32_prompt_is_valid_and_non_authorizing():
    result = subprocess.run(
        [sys.executable, "tools/validate_phase_prompt.py", str(PROMPT)],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    text = _read(PROMPT)
    assert "This is a NON-SENSITIVE planning/spec phase" in text
    assert "No collector implementation" in text
    assert "No graph mutation" in text
    assert "No Genesis signing or node upload" in text
    assert "If MemPalace is used, direct-read every returned path." in text


def test_forward_plan_points_to_fix32_and_prompt_exists():
    text = _read(FORWARD_PLAN)

    assert "Phase 1545p-Fix32: Homoiconic Test Registry Contract" in text
    assert PROMPT.exists()
