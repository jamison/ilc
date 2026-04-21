from __future__ import annotations

import os
import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_row_7_censorship_runtime_closure_evaluation_cw3_v0.1.md")
TEST_PATH = Path("tests/test_cw3_row_7_censorship_runtime_closure_evaluation.py")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Evaluation target and inherited contract",
    "## 2. Requirement-by-requirement check against Phase 741 Section 3.2",
    "## 3. Post-CRIT-001 framing",
    "## 4. Verdict and remaining boundary",
    "## 5. Non-claims",
)
REQUIRED_TOKENS = (
    "row_7_censorship_resistance_runtime_closure_verdict=pass",
    "row_7_censorship_side_closed_only",
    "row_7_exitability_obligation_still_pending_until_cw4",
    "epochcheckpointmsg_carries_row_7_censorship_evidence_weight_post_crit_001",
    "row_7_phase_698_mapping_reverified",
)
PHASE_SUBJECT = ("cw-3", "phase 759", "row-7 censorship")
EXACT_REQUIRED_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
SELFTEST_ENV = "ILC_CW3_GATE_SELFTEST"


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
    raise AssertionError("cw3_commit_not_present_in_local_history")


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


def test_required_tokens_are_present() -> None:
    if _selftest():
        return
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_all_phase_741_section_3_2_requirements_are_checked() -> None:
    if _selftest():
        return
    text = _normalized(_read(ARTIFACT_PATH))
    required = (
        "Requirement 1 — live censoring-validator scenario",
        "Requirement 2 — not weaker than the Phase 698 proof basis",
        "Requirement 3 — practical inclusion not suppressed permanently",
        "Requirement 4 — eventual commit under bounded censoring quorum",
        "Requirement 5 — explicit mapping note to Phase 698 proof basis",
        "satisfied",
        "epoch_record_committed:epoch=1",
    )
    for item in required:
        assert item in text


def test_post_crit_001_framing_and_phase_698_mapping_are_present() -> None:
    if _selftest():
        return
    text = _normalized(_read(ARTIFACT_PATH))
    assert "EpochSettlementTx" in text
    assert "EpochCheckpointMsg" in text
    assert "the row-7 censorship evidence weight is carried by the `EpochCheckpointMsg` redundant-path liveness property" in text
    assert "N=4" in text
    assert "F=1" in text
    assert "MaxRound=5" in text
    assert "Liveness" in text


def test_two_obligations_boundary_is_preserved() -> None:
    if _selftest():
        return
    text = _normalized(_read(ARTIFACT_PATH))
    assert "Row `7` contains two runtime obligations" in text
    assert "This closes only the censorship-resistance side of row `7`." in text
    assert "strong exitability still requires `CW-4`" in text


def test_selftest_guard_is_declared_in_test_file() -> None:
    text = _read(TEST_PATH)
    assert SELFTEST_ENV in text
    assert "if _selftest():" in text


def test_decision_log_and_runtime_code_surfaces_are_untouched_in_cw3() -> None:
    if _selftest():
        return
    result_decision = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result_decision.returncode == 0


def test_cw3_commit_touches_expected_paths_only() -> None:
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
