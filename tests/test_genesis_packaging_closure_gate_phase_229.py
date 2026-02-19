from __future__ import annotations

from pathlib import Path
import subprocess


CLOSURE_GATE_SCRIPT = Path("tools/check_genesis_packaging_closure_222_228_phase_229.sh")
HANDOFF_PATH = Path("docs/specs/ilc_genesis_packaging_222_228_handoff_v0.1.md")
PROVENANCE_SUPPLEMENT_PATH = Path("docs/specs/ilc_constitutional_provenance_supplement_phase_229_v0.1.md")
PATH_LIFT_CONTRACT_PATH = Path("docs/specs/ilc_path_lift_counterfactual_contract_v0.1.md")


def _run_gate(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(CLOSURE_GATE_SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
        timeout=900,
    )


def test_phase_229_closure_gate_dry_run_contract() -> None:
    result = _run_gate(["--dry-run"])
    assert result.returncode == 0
    assert "Dry run: genesis packaging closure gate (222-228) commands" in result.stdout
    assert "tools/check_phase_226_security_triage_artifacts.sh" in result.stdout
    assert "tools/check_phase_227_blocker_remediation_package.sh" in result.stdout
    assert "tools/check_genesis_distribution_surface_phase_225.sh" in result.stdout
    assert "tools/check_genesis_release_artifacts_phase_228.sh" in result.stdout


def test_phase_229_closure_gate_unknown_argument_contract() -> None:
    result = _run_gate(["--bad-arg"])
    assert result.returncode == 2
    assert "Unknown argument: --bad-arg" in result.stderr


def test_phase_229_closure_gate_help_contract() -> None:
    result = _run_gate(["--help"])
    assert result.returncode == 0
    assert "Usage: check_genesis_packaging_closure_222_228_phase_229.sh" in result.stdout
    assert "--dry-run" in result.stdout


def test_phase_229_required_docs_have_expected_sections() -> None:
    handoff = HANDOFF_PATH.read_text(encoding="utf-8")
    supplement = PROVENANCE_SUPPLEMENT_PATH.read_text(encoding="utf-8")
    path_lift_contract = PATH_LIFT_CONTRACT_PATH.read_text(encoding="utf-8")

    assert "## 2. Phase-by-phase delivery summary (223/224/226/227/225/228)" in handoff
    assert "## 4. Open CDL posture and bounded remediation state" in handoff
    assert "## 5. Backlog disposition carry-forward (phase-226 queue)" in handoff
    assert "## 6. Deferred debt carried forward" in handoff
    assert "## 7. Forward pointer" in handoff

    assert "## 2. SG-01 - issuance framing provenance note" in supplement
    assert "## 3. SG-03 - operational cap targets preserved as non-binding historical evidence" in supplement
    assert "## 4. SG-04 - path-lift lineage note" in supplement
    assert "## 5. CG-01 - optional calibration note" in supplement

    assert "## 4.2 Historical lineage note (SG-04)" in path_lift_contract


def test_phase_229_closure_gate_runs_successfully() -> None:
    result = _run_gate([])
    assert result.returncode == 0
    assert "=== Genesis Packaging Closure Gate (222-228) ===" in result.stdout
    assert "Genesis packaging closure gate (222-228): PASS" in result.stdout
