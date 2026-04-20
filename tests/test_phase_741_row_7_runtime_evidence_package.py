from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_row_7_runtime_evidence_package_741_v0.1.md")
TEST_PATH = Path("tests/test_phase_741_row_7_runtime_evidence_package.py")
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Purpose and inherited authority",
    "## 2. The two distinct row-7 runtime obligations",
    "## 3. Censorship-resistance runtime confirmation contract",
    "## 4. Strong exitability drill contract",
    "## 5. Current status and row-8 disposition",
)
REQUIRED_TOKENS = (
    "row_7_runtime_evidence_package_741_complete",
    "row_7_runtime_obligations_split_censorship_and_exitability",
    "row_7_censorship_runtime_confirmation_requires_m019_evidence",
    "row_7_exitability_drill_deferred_to_mysticeti_convergence_window",
    "row_7_status_after_phase_741=spec_closed_runtime_pending",
    "row_8_inherited_criteria_lock_not_advanced_in_phase_741",
    "row_7_censorship_and_exitability_do_not_share_evidence_source",
    "row_7_exitability_execution_explicitly_deferred",
)
PHASE_MAIN_SUBJECT = (
    "phase 741",
    "row-7 runtime evidence package",
)
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
    str(STATUS_PATH),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split())


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
    raise AssertionError("phase_741_commit_not_present_in_local_history")


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


def test_document_exists_with_required_headings_in_order() -> None:
    text = _read(ARTIFACT_PATH)
    positions = [text.index(heading) for heading in REQUIRED_HEADINGS]
    assert positions == sorted(positions)


def test_document_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_two_row_7_obligations_are_treated_separately_without_conflation() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "two distinct runtime obligations that do not share an evidence source" in text
    assert "Censorship-resistance runtime confirmation" in text
    assert "Strong exitability drill" in text
    assert "The strong exitability side does not come from `M-019`." in text


def test_censorship_resistance_side_names_m019_as_expected_evidence_source() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "Gemini `M-019` is the expected runtime evidence source for the censorship side." in text
    assert "it must at least cover the `N=4`, `F=1` shape" in text
    assert "`MaxRound=5`" in text
    assert "`Liveness`" in text


def test_exitability_side_references_export_verify_replay_and_migrate_without_operator_consent() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "export legitimacy-relevant state" in text
    assert "independently verify exported state and receipts" in text
    assert "replay legitimacy-relevant history from portable data" in text
    assert "migrate without privileged original-operator consent" in text


def test_exitability_drill_is_explicitly_deferred_not_claimed_complete() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "Execution of this drill is explicitly deferred to the Mysticeti convergence window." in text
    assert "This phase publishes the drill contract only. It does not claim that export, verification, replay, or migration has already been executed successfully." in text


def test_row_7_status_remains_spec_closed_runtime_pending() -> None:
    combined = _normalized(_read(ARTIFACT_PATH) + "\n" + _read(STATUS_PATH))
    assert "row `7` remains `spec_closed_runtime_pending`" in combined
    assert "no row-7 runtime-closed claim is authorized by this phase" in combined


def test_row_8_is_noted_as_inherited_criteria_lock_with_no_advancement() -> None:
    combined = _normalized(_read(ARTIFACT_PATH) + "\n" + _read(STATUS_PATH)).lower()
    assert "row `8` is unchanged in this window" in combined
    assert "inherited criteria lock" in combined
    assert "no runtime confirmation commissioned here" in combined


def test_decision_log_and_ilc_core_and_ilc_consensus_are_untouched_in_this_phase() -> None:
    main_commit = _try_resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    if main_commit:
        changed_paths = _changed_paths_for_commit(main_commit)
        assert str(DECISION_LOG_PATH) not in changed_paths
        assert not any(path == "ilc_core" or path.startswith("ilc_core/") for path in changed_paths)
        assert not any(
            path == "ilc_consensus" or path.startswith("ilc_consensus/")
            for path in changed_paths
        )
        return

    result_decision = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result_decision.returncode == 0


def test_phase_741_single_commit_touches_expected_paths_only() -> None:
    commit_ref = _try_resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    if commit_ref:
        assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS
        return

    assert _current_phase_paths_in_worktree(EXACT_REQUIRED_MAIN_PATHS) == EXACT_REQUIRED_MAIN_PATHS
