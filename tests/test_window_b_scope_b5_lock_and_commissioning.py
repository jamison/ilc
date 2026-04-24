from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path("/Users/jamstar/Documents/ILC_Main/01_Current")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_b5_required_artifacts_exist() -> None:
    required = [
        ROOT / "docs/phases/phase_b5_row5_b_scope_closure_gate.md",
        ROOT / "docs/specs/ilc_row5_mechanism_selection_lock_b5_v0.1.md",
        ROOT / "docs/specs/ilc_row5_b_impl_commissioning_spec_v0.1.md",
        ROOT / "docs/specs/ilc_codex_model_transition_supplement_b5_v0.1.md",
        ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.13.md",
        ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.6.md",
    ]
    for path in required:
        assert path.exists(), path


def test_b5_tokens_and_primary_lock_are_present() -> None:
    closure = _read(ROOT / "docs/phases/phase_b5_row5_b_scope_closure_gate.md")
    lock = _read(ROOT / "docs/specs/ilc_row5_mechanism_selection_lock_b5_v0.1.md")
    capsule = _read(ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.13.md")
    for token in (
        "row5_mechanism_selection_human_gate_closed",
        "row5_b_scope_window_closed",
        "row5_k_anonymity_jitter3_primary_locked",
        "row5_k_anonymity_jitter3_k20_fallback_locked",
        "row5_still_spec_closed_runtime_pending",
        "capsule_v5_13_supersedes_v5_12",
    ):
        assert token in "\n".join([closure, lock, capsule])


def test_lock_doc_records_two_tier_privacy_lanes() -> None:
    text = _read(ROOT / "docs/specs/ilc_row5_mechanism_selection_lock_b5_v0.1.md")
    assert "Contribution" in text
    assert "Payment" in text
    assert "ExpressConsent" in text
    assert "A<=0.15" in text
    assert "B<=0.15" in text
    assert "C<=0.05" in text


def test_commissioning_spec_lists_six_runtime_obligations() -> None:
    text = _read(ROOT / "docs/specs/ilc_row5_b_impl_commissioning_spec_v0.1.md")
    expected_phrases = (
        "rolling group construction",
        "deferred release queue",
        "bounded_hold carry-over",
        "Group-fill monitoring",
        "degraded-anonymity",
        "SIM-LEAKAGE-03",
    )
    for phrase in expected_phrases:
        assert phrase in text


def test_transition_supplement_corrects_stale_governance_assumptions() -> None:
    text = _read(ROOT / "docs/specs/ilc_codex_model_transition_supplement_b5_v0.1.md")
    assert "mixing family" in text
    assert "k=30" in text
    assert "CDL-017 | `ratified`" in text
    assert "Option D active" not in text
    assert "CDL-017 ratification is still pending" not in text


def test_planning_index_and_launch_roadmap_advance() -> None:
    index = _read(ROOT / "docs/PLANNING_INDEX.md")
    roadmap = _read(ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.6.md")
    assert "B-Scope CLOSED" in index
    assert "ilc_row5_mechanism_selection_lock_b5_v0.1.md" in index
    assert "ilc_codex_model_transition_supplement_b5_v0.1.md" in index
    assert "Row-5 mechanism lock is complete" in roadmap
    assert "B-Impl commissioned" in roadmap


def test_decision_log_not_mutated_in_worktree() -> None:
    decision_log = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
    result = subprocess.run(
        ["git", "diff", "--name-only", "--", str(decision_log.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == ""
