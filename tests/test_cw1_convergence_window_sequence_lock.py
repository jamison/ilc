from __future__ import annotations

import os
import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_mysticeti_convergence_window_sequence_lock_cw1_v0.1.md")
TEST_PATH = Path("tests/test_cw1_convergence_window_sequence_lock.py")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Baseline and authority order",
    "## 2. Artifact-class re-verification",
    "## 3. Window scope and phase reservation",
    "## 4. Constitutional and runtime posture at open",
    "## 5. Gate verdict and non-claims",
    "## 6. Source inputs",
)
REQUIRED_TOKENS = (
    "convergence_window_cw1_sequence_lock_active",
    "cw1_artifact_verification_pass",
    "track_b_m022_complete_convergence_window_next",
    "cdl_017_open_at_cw1",
    "row_5_spec_closed_runtime_pending_at_cw1",
    "row_7_spec_closed_runtime_pending_at_cw1",
    "row_8_inherited_at_cw1",
    "convergence_window_open_after_cw1_artifact_reverification",
    "no_cdl_017_ratification_in_cw1",
    "no_decision_log_mutation_in_cw1",
)
PHASE_SUBJECT = ("cw-1", "phase 757", "sequence lock", "artifact re-verification")
EXACT_REQUIRED_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
SELFTEST_ENV = "ILC_CW1_GATE_SELFTEST"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split())


def _selftest() -> bool:
    return os.environ.get(SELFTEST_ENV) == "1"


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_commit_ref(subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        lowered = subject.lower()
        if all(token in lowered for token in subject_tokens):
            matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError("cw1_commit_not_present_in_local_history")


def _try_resolve_commit_ref(subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str | None:
    try:
        return _resolve_commit_ref(subject_tokens, expected_paths)
    except AssertionError:
        return None


def _current_phase_paths_in_worktree(expected_paths: set[str]) -> set[str]:
    result = subprocess.run(
        ["git", "status", "--short", "--", *sorted(expected_paths)],
        capture_output=True,
        check=True,
        text=True,
    )
    paths: set[str] = set()
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        paths.add(line[3:].strip())
    return paths


def test_output_exists_with_required_headings_in_order() -> None:
    if _selftest():
        return
    text = _read(ARTIFACT_PATH)
    positions = [text.index(heading) for heading in REQUIRED_HEADINGS]
    assert positions == sorted(positions)


def test_required_tokens_and_gate_verdict_are_present() -> None:
    if _selftest():
        return
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text
    assert "cw1_artifact_verification_fail" not in text


def test_each_artifact_class_path_is_explicitly_reverified() -> None:
    if _selftest():
        return
    text = _normalized(_read(ARTIFACT_PATH))
    required = (
        "docs/research/ilc_row_7_runtime_evidence_package_bundle_M020_v0.1.md",
        "docs/research/ilc_sim_leakage_01_results_M021_v0.1.md",
        "docs/research/ilc_mysticeti_gemini_lane_handoff_M022_v0.1.md",
        "N=4",
        "F=1",
        "MaxRound=5",
        "Liveness",
        "tools/testbed/m022_export.json",
        "tools/testbed/m022_verify.json",
        "tools/testbed/m022_replay.log",
        "tools/testbed/m022_migrate.json",
    )
    for item in required:
        assert item in text


def test_live_track_b_line_and_open_posture_are_recorded() -> None:
    if _selftest():
        return
    text = _normalized(_read(ARTIFACT_PATH))
    assert "M-022 (Gemini Lane Handoff Package + Strong Exitability Drill) complete." in text
    assert "run_m022_exitability_drill_verdict=pass" in text
    assert "Mysticeti convergence window — all three entry artifact classes committed; CW-1 artifact re-verification may now proceed." in text
    assert "This sequence lock activates the convergence window" in text


def test_no_cdl_017_ratification_assertion_is_present() -> None:
    if _selftest():
        return
    text = _normalized(_read(ARTIFACT_PATH))
    assert "`CDL-017` remains open and unratified" in text
    assert "any `CDL-017` ratification act" in text


def test_selftest_guard_is_declared_in_test_file() -> None:
    text = _read(TEST_PATH)
    assert SELFTEST_ENV in text
    assert "if _selftest():" in text


def test_decision_log_and_runtime_code_surfaces_are_untouched_in_cw1() -> None:
    if _selftest():
        return
    result_decision = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result_decision.returncode == 0


def test_cw1_commit_touches_expected_paths_only() -> None:
    if _selftest():
        return
    commit_ref = _try_resolve_commit_ref(PHASE_SUBJECT, EXACT_REQUIRED_PATHS)
    if commit_ref:
        changed_paths = _changed_paths_for_commit(commit_ref)
        assert changed_paths == EXACT_REQUIRED_PATHS
        assert str(DECISION_LOG_PATH) not in changed_paths
        assert not any(path == "ilc_core" or path.startswith("ilc_core/") for path in changed_paths)
        assert not any(
            path == "ilc_consensus" or path.startswith("ilc_consensus/")
            for path in changed_paths
        )
        return

    assert _current_phase_paths_in_worktree(EXACT_REQUIRED_PATHS) == EXACT_REQUIRED_PATHS
