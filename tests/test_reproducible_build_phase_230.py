from __future__ import annotations

from pathlib import Path
import subprocess


GATE_SCRIPT = Path("tools/check_reproducible_build.sh")
SEQUENCE_SPEC = Path("docs/specs/ilc_post_genesis_capability_proof_activation_sequence_230_239_v0.1.md")
DECISION_NOTE = Path("docs/specs/ilc_build_reproducibility_backend_decision_note_v0.1.md")
RELEASE_ARTIFACT_CONTRACT = Path("docs/specs/ilc_genesis_release_artifact_contract_v0.1.md")
RELEASE_PROVENANCE = Path("docs/specs/ilc_genesis_release_artifact_provenance_phase_228_v0.1.md")
DECISION_LOG = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")


def _run_gate(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(GATE_SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
        timeout=1200,
    )


def test_phase_230_gate_dry_run_contract() -> None:
    result = _run_gate(["--dry-run"])
    assert result.returncode == 0
    assert "Dry run: phase-230 reproducible build commands" in result.stdout
    assert "SOURCE_DATE_EPOCH=0" in result.stdout
    assert "compare SHA-256 manifests" in result.stdout


def test_phase_230_gate_unknown_argument_contract() -> None:
    result = _run_gate(["--bad-arg"])
    assert result.returncode == 2
    assert "Unknown argument: --bad-arg" in result.stderr


def test_phase_230_gate_help_contract() -> None:
    result = _run_gate(["--help"])
    assert result.returncode == 0
    assert "Usage: check_reproducible_build.sh" in result.stdout
    assert "--dry-run" in result.stdout


def test_phase_230_docs_and_cdl_019_presence() -> None:
    sequence_text = SEQUENCE_SPEC.read_text(encoding="utf-8")
    decision_note_text = DECISION_NOTE.read_text(encoding="utf-8")
    contract_text = RELEASE_ARTIFACT_CONTRACT.read_text(encoding="utf-8")
    provenance_text = RELEASE_PROVENANCE.read_text(encoding="utf-8")
    decision_log_text = DECISION_LOG.read_text(encoding="utf-8")

    assert "## 1. Purpose and sequence scope" in sequence_text
    assert "## 2. Dependency baseline and entry gate" in sequence_text
    assert "## 3. Locked phase table (230-239)" in sequence_text
    assert "## 4. Per-phase sensitivity classification" in sequence_text
    assert "## 5. Mandatory entry/exit gates per phase lane" in sequence_text
    assert "## 6. D1 reproducibility baseline lock and exit criteria" in sequence_text
    assert "## 7. Non-goals and out-of-scope boundaries" in sequence_text
    assert "## 8. Forward pointer and carry-forward debt list" in sequence_text

    assert "setuptools.build_meta" in decision_note_text
    assert "python -m build" in decision_note_text

    assert "same-platform reproducibility" in contract_text
    assert "Phase-228 build event" in contract_text
    assert "same commit" in provenance_text

    assert "| CDL-019 |" in decision_log_text
    assert "Multiplier-governance surface" in decision_log_text


def test_phase_230_gate_runs_successfully() -> None:
    result = _run_gate([])
    assert result.returncode == 0
    assert "=== Phase 230 Reproducible Build Gate ===" in result.stdout
    assert "Phase 230 reproducible build gate: PASS" in result.stdout
