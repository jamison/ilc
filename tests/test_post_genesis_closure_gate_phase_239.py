from __future__ import annotations

from pathlib import Path
import subprocess


CLOSURE_GATE_SCRIPT = Path("tools/check_post_genesis_window_closure_230_238_phase_239.sh")
HANDOFF_PATH = Path("docs/specs/ilc_post_genesis_window_230_238_handoff_v0.1.md")


def _run_gate(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(CLOSURE_GATE_SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
        timeout=1200,
    )


def _section(text: str, heading: str) -> str:
    parts = text.split(heading)
    assert len(parts) >= 2, f"missing heading: {heading}"
    tail = parts[1]
    next_idx = tail.find("\n## ")
    if next_idx == -1:
        return tail
    return tail[:next_idx]


def test_phase_239_closure_gate_script_exists() -> None:
    assert CLOSURE_GATE_SCRIPT.exists()


def test_phase_239_closure_gate_dry_run_contract() -> None:
    result = _run_gate(["--dry-run"])
    assert result.returncode == 0
    assert "Phase 239 closure dry-run:" in result.stdout
    assert "python3 tools/run_phase_236_preflight.py" in result.stdout
    assert "tests/test_integration_coherence_237.py" in result.stdout
    assert "tests/test_release_readiness_package_238.py" in result.stdout


def test_phase_239_closure_gate_help_and_unknown_arg_contract() -> None:
    help_result = _run_gate(["--help"])
    assert help_result.returncode == 0
    assert "Usage: tools/check_post_genesis_window_closure_230_238_phase_239.sh" in help_result.stdout

    unknown_result = _run_gate(["--bad-arg"])
    assert unknown_result.returncode == 2
    assert "Unknown argument: --bad-arg" in unknown_result.stderr


def test_phase_239_handoff_exists_with_required_sections() -> None:
    assert HANDOFF_PATH.exists()
    text = HANDOFF_PATH.read_text(encoding="utf-8")

    required_sections = [
        "## 1. Window summary",
        "## 2. Hard prerequisites for Phase 240",
        "## 3. Soft carry-forward items",
        "## 4. Next sequence pointer",
    ]
    for token in required_sections:
        assert token in text


def test_phase_239_handoff_hard_prerequisites_and_forbidden_phrases() -> None:
    text = HANDOFF_PATH.read_text(encoding="utf-8")
    section2 = _section(text, "## 2. Hard prerequisites for Phase 240")
    section3 = _section(text, "## 3. Soft carry-forward items")

    assert "register" in section2
    assert "rotate" in section2
    assert "revoke" in section2
    assert "recover" in section2
    assert "ilc_security_runtime_implementation_plan_232_v0.1.md" in section2
    assert "Section 6.1" in section2
    assert "CDL-001" in section2
    assert "CDL-002" in section2
    assert "CDL-007" in section2

    assert "CDL-032" in section3
    assert "D2e" in section3

    forbidden = [
        "is hereby ratified",
        "ratified in this phase",
        "this phase ratifies",
        "status changed to ratified",
    ]
    lowered = text.lower()
    for token in forbidden:
        assert token not in lowered
