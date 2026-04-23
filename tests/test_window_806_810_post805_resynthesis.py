from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

PHASE_DOCS = [
    REPO_ROOT / "docs/specs/ilc_phase_806_810_sequence_lock_v0.1.md",
    REPO_ROOT / "docs/phases/phase_806_sequence_lock_acknowledgment.md",
    REPO_ROOT / "docs/phases/phase_807_phase673_post805_resynthesis.md",
    REPO_ROOT / "docs/phases/phase_808_phase675_cdl062_post805_resynthesis.md",
    REPO_ROOT / "docs/phases/phase_809_option_b_gate_post805_resynthesis.md",
    REPO_ROOT / "docs/phases/phase_810_coherence_report.md",
    REPO_ROOT / "docs/phases/phase_810_closure_gate.md",
]

CAPSULE = REPO_ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.11.md"
PHASE_805 = REPO_ROOT / "docs/phases/phase_805_dag_audit_cli_implementation.md"
DECISION_LOG = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _window_text() -> str:
    return "\n".join(_read(path) for path in [*PHASE_DOCS, CAPSULE, PHASE_805])


def test_window_outputs_exist() -> None:
    for path in [*PHASE_DOCS, CAPSULE]:
        assert path.exists(), f"missing window output: {path}"


def test_phase_805_condition_is_consumed() -> None:
    text = _window_text()
    assert "verification_tooling_tier1_condition_discharged" in text
    assert "verification_tooling_delivery_before_public_deployment=discharged_by_phase_805" in text
    assert "dag_audit_tier1_pass" in text


def test_row8_and_option_b_verdicts_are_updated_without_selection() -> None:
    text = _window_text()
    for token in (
        "mysticeti_sovereign_phase_673_exclusion_matrix_verdict=pass",
        "mysticeti_sovereign_phase_675_criteria_lock_verdict=pass",
        "cdl_062_evaluation_verdict=pass",
        "mysticeti_sovereign_row_8_combined_status=pass",
        "option_b_gate_synthesis_verdict=go_pending_human_authorization",
        "option_b_gate_conditions=none",
        "option_b_implementation_side_conditions=none_remaining",
    ):
        assert token in text
    assert "option_b_selection_not_claimed" in text
    assert "human_authorization_required_for_option_b_selection" in text


def test_capsule_advances_to_v511_from_v510() -> None:
    text = _read(CAPSULE)
    assert "capsule_v5_11_supersedes_v5_10" in text
    assert "docs/specs/ilc_antigravity_context_capsule_v5.10.md" in text
    assert "option_b_gate_conditions=none" in text


def test_boundaries_preserved() -> None:
    text = _window_text()
    assert "no_cdl_mutation_in_window_806_810" in text
    assert "no_option_b_selection_in_window_806_810" in text
    assert "row_5_status_unchanged_spec_closed_runtime_pending" in text
    assert "first non-Genesis validator deployment" in text


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
