from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/research/ilc_post_banking_economic_doctrine_note_704_v0.1.md")
TEST_PATH = Path("tests/test_phase_704_post_banking_doctrine_lock.py")
WALKTHROUGH_PATH = Path("docs/phases/phase_704_g8_post_banking_doctrine_lock_walkthrough.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Doctrine source basis",
    "## 2. Current canonical runtime echoes",
    "## 3. What the doctrine does and does not claim",
    "## 4. Doctrine versus law classification",
    "## 5. Final disposition",
)
REQUIRED_TOKENS = (
    "post_banking_doctrine_704_complete",
    "post_banking_is_doctrine_not_binding_law",
    "post_banking_runtime_implications_mapped",
    "post_banking_no_silent_constitutionalization",
    "post_banking_disposition=doctrine_lock",
)
PHASE_704_SUBJECT = ("phase 704", "post-banking doctrine lock")
PHASE_704_BACKFILL_SUBJECT = ("phase 704", "walkthrough", "backfill")
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
    raise AssertionError("phase_704_commit_not_present_in_local_history")


def _try_resolve_commit_ref(subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str | None:
    try:
        return _resolve_commit_ref(subject_tokens, expected_paths)
    except AssertionError:
        return None


def test_artifact_exists_and_contains_required_headings_in_order() -> None:
    text = _read(ARTIFACT_PATH)
    positions = [text.index(heading) for heading in REQUIRED_HEADINGS]
    assert positions == sorted(positions)


def test_artifact_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_artifact_records_real_source_basis_and_runtime_echoes() -> None:
    text = _read(ARTIFACT_PATH)
    assert "economic architecture document" in text
    assert "687-692 principles note" in text
    assert "Werner discussion" in text
    assert "ECU issuance through verified knowledge work" in text
    assert "Dual-layer economy with epoch-boundary settlement" in text
    assert "Governance-minimization trajectory" in text


def test_artifact_distinguishes_claims_from_non_claims() -> None:
    text = _read(ARTIFACT_PATH)
    assert "What the doctrine does claim:" in text
    assert "What the doctrine does not claim:" in text
    assert "does not itself ban every future financing mechanism" in text
    assert "does not silently convert an explanatory metaphor into binding protocol law" in text


def test_artifact_states_doctrine_not_law_explicitly() -> None:
    text = _read(ARTIFACT_PATH)
    assert "The correct classification is doctrine, not binding law." in text
    assert "This note itself does not establish binding law." in text
    assert "does not establish any new CDL, ADR, invariant, or executable prohibition" in text


def test_decision_log_and_runtime_paths_remain_unmutated_in_this_phase() -> None:
    main_commit = _try_resolve_commit_ref(PHASE_704_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    backfill_commit = _try_resolve_commit_ref(
        PHASE_704_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS
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


def test_phase_704_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_704_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_704_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_704_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
