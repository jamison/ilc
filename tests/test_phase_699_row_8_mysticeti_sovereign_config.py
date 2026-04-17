from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_row_8_mysticeti_sovereign_config_699_v0.1.md")
TEST_PATH = Path("tests/test_phase_699_row_8_mysticeti_sovereign_config.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_699_g8_row_8_mysticeti_sovereign_configuration_confirmation_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Locked row-8 criteria inherited from Phase 675",
    "## 2. Mysticeti sovereign deployment assumptions",
    "## 3. Criterion-by-criterion confirmation matrix",
    "## 4. Residual ambiguities and required resolution path",
    "## 5. Final disposition",
)
REQUIRED_TOKENS = (
    "row_8_mysticeti_sovereign_confirmation_699_complete",
    "row_8_reopened=no",
    "mysticeti_sovereign_mode_external_constitutional_center=absent",
)
FINAL_DISPOSITION_LINES = {
    "`row_8_post_699_disposition=CONFIRMED`",
    "`row_8_post_699_disposition=GAP_FOUND`",
}
PHASE_699_SUBJECT = ("phase 699", "row-8 mysticeti sovereign configuration confirmation")
PHASE_699_BACKFILL_SUBJECT = ("phase 699", "walkthrough", "backfill")
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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
    raise AssertionError("phase_699_commit_not_present_in_local_history")


def _try_resolve_commit_ref(subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str | None:
    try:
        return _resolve_commit_ref(subject_tokens, expected_paths)
    except AssertionError:
        return None


def test_artifact_exists_and_contains_all_required_headings_in_order() -> None:
    text = _read(ARTIFACT_PATH)
    positions = [text.index(heading) for heading in REQUIRED_HEADINGS]
    assert positions == sorted(positions)


def test_artifact_contains_all_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_exactly_one_final_disposition_line_is_present() -> None:
    text = _read(ARTIFACT_PATH)
    found = [line for line in FINAL_DISPOSITION_LINES if line in text]
    assert len(found) == 1


def test_criterion_matrix_explicitly_addresses_external_center_independence_and_sovereign_validator_control() -> None:
    text = _read(ARTIFACT_PATH)
    assert "outside validator-set control" in text
    assert "outside veto authority" in text
    assert "Sui Foundation" in text
    assert "Mysten Labs" in text
    assert "external bridge" in text
    assert "static bootstrap validator set" in text


def test_artifact_states_row_8_is_not_reopened() -> None:
    text = _read(ARTIFACT_PATH)
    assert "`row_8_reopened=no`" in text
    assert "This phase does not reopen row 8." in text


def test_decision_log_ilc_core_and_ilc_consensus_remain_unmutated_in_this_phase() -> None:
    main_commit = _try_resolve_commit_ref(PHASE_699_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    backfill_commit = _try_resolve_commit_ref(
        PHASE_699_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS
    )
    if main_commit and backfill_commit:
        for commit_ref in (main_commit, backfill_commit):
            changed_paths = _changed_paths_for_commit(commit_ref)
            assert str(DECISION_LOG_PATH) not in changed_paths
            assert not any(
                path == "ilc_core" or path.startswith("ilc_core/") for path in changed_paths
            )
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

    result_ilc_core = subprocess.run(
        ["git", "diff", "--exit-code", "--", "ilc_core/"],
        capture_output=True,
        text=True,
    )
    assert result_ilc_core.returncode == 0

    result_ilc_consensus = subprocess.run(
        ["git", "diff", "--exit-code", "--", "ilc_consensus/"],
        capture_output=True,
        text=True,
    )
    assert result_ilc_consensus.returncode == 0


def test_phase_699_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_699_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_699_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_699_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
