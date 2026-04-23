from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

PHASE_DOCS = [
    REPO_ROOT / "docs/phases/phase_783_sequence_lock_acknowledgment.md",
    REPO_ROOT / "docs/phases/phase_784_tla_status_audit.md",
    REPO_ROOT / "docs/phases/phase_785_phase673_classification.md",
    REPO_ROOT / "docs/phases/phase_786_phase675_classification.md",
    REPO_ROOT / "docs/phases/phase_787_cdl_062_evaluation.md",
    REPO_ROOT / "docs/phases/phase_788_option_b_gate_synthesis.md",
    REPO_ROOT / "docs/phases/phase_789_coherence_report.md",
    REPO_ROOT / "docs/phases/phase_790_closure_gate.md",
]

CAPSULE = REPO_ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.9.md"
DECISION_LOG = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _all_window_text() -> str:
    return "\n".join(_read(path) for path in [*PHASE_DOCS, CAPSULE])


def test_all_window_outputs_exist() -> None:
    for path in [*PHASE_DOCS, CAPSULE]:
        assert path.exists(), f"missing window output: {path}"


def test_required_verdict_tokens_are_present() -> None:
    text = _all_window_text()
    for token in (
        "phase_783_sequence_lock_acknowledged",
        "tla_formal_verification_gate_status=cleared",
        "mysticeti_sovereign_phase_673_exclusion_matrix_verdict=conditional",
        "mysticeti_sovereign_phase_675_criteria_lock_verdict=conditional",
        "cdl_062_evaluation_verdict=conditional",
        "option_b_gate_synthesis_verdict=go_pending_human_authorization",
        "phase_790_window_783_790_verdict=pass",
    ):
        assert token in text


def test_human_gate_and_condition_are_preserved() -> None:
    text = _all_window_text()
    assert "verification_tooling_delivery_before_public_deployment" in text
    assert "human_authorization_required_for_option_b_selection" in text
    assert "option_b_selection_not_claimed" in text


def test_tla_status_records_spec_b_safety_verdict() -> None:
    text = _read(REPO_ROOT / "docs/phases/phase_784_tla_status_audit.md")
    assert "tla_dag_censorship_bounds_tlc_status=pass" in text
    assert "tla_ecu_fast_path_safety_no_dual_cert_tlc_status=pass" in text
    assert "m019_safety_no_dual_cert_todo_disposition=stale_spec_and_tlc_evidence_now_exist" in text


def test_no_ellipsis_in_window_walkthroughs() -> None:
    for path in PHASE_DOCS:
        assert "..." not in _read(path), f"ellipsis found in {path}"


def test_decision_log_not_mutated_in_worktree() -> None:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--", str(DECISION_LOG.relative_to(REPO_ROOT))],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == ""

