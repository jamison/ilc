from __future__ import annotations

import subprocess
from pathlib import Path


SCRIPT_PATH = Path("tools/check_cdl_ratification_window_closure_250_258_phase_259.sh")
HANDOFF_PATH = Path("docs/specs/ilc_cdl_ratification_window_250_258_handoff_v0.1.md")


def _run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_closure_script_exists() -> None:
    assert SCRIPT_PATH.exists()


def test_dry_run_mentions_phase_252_gate_and_phase_258_tests() -> None:
    result = _run_script("--dry-run")
    assert result.returncode == 0
    output = result.stdout + result.stderr
    assert "run_phase_252_security_ratification_gate.py" in output
    assert "test_integration_coherence_258.py" in output


def test_help_exits_zero_and_contains_usage() -> None:
    result = _run_script("--help")
    assert result.returncode == 0
    output = (result.stdout + result.stderr).lower()
    assert "usage" in output


def test_unknown_arg_exits_two() -> None:
    result = _run_script("--unknown-arg")
    assert result.returncode == 2


def test_handoff_exists() -> None:
    assert HANDOFF_PATH.exists()


def test_handoff_references_ratified_cdls() -> None:
    text = _read(HANDOFF_PATH)
    for cdl in ["CDL-001", "CDL-002", "CDL-007", "CDL-032"]:
        assert cdl in text


def test_handoff_references_d2e_03_readiness_assessment() -> None:
    text = _read(HANDOFF_PATH)
    assert "D2e-03" in text
    assert "ilc_d2e_03_readiness_assessment_257_v0.1.md" in text


def test_handoff_includes_signing_provider_dependency_details() -> None:
    text = _read(HANDOFF_PATH)
    assert "Signing provider interface specification" in text
    assert "pre-D2e-07 dependency" in text
    assert "sign(payload_bytes) -> COSE_Sign1_structure" in text


def test_handoff_includes_cose_kid_must_not_privacy_rule() -> None:
    text = _read(HANDOFF_PATH)
    assert "COSE `kid` MUST" in text
    assert "MUST NOT" in text
    assert "raw public key" in text


def test_handoff_includes_mutation_scope_fixture_carry_forward() -> None:
    text = _read(HANDOFF_PATH)
    assert "Ratification mutation-scope test fixture" in text
    assert "status" in text
    assert "ratified_phase" in text
    assert "ratified_date" in text
    assert "evidence_document" in text
