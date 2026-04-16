from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_row_5_mechanism_proof_mysticeti_697_v0.1.md")
TEST_PATH = Path("tests/test_phase_697_row_5_mechanism_proof_mysticeti.py")
WALKTHROUGH_PATH = Path("docs/phases/phase_697_g8_row_5_mechanism_proof_over_mysticeti_walkthrough.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Inherited row-5 narrowing basis",
    "## 2. Mysticeti privacy-relevant architecture surfaces",
    "## 3. Criterion-by-criterion proof matrix",
    "## 4. New gaps or residual incompatibilities",
    "## 5. Final disposition",
)
REQUIRED_TOKENS = (
    "row_5_mysticeti_reproof_697_complete",
    "phase_682_narrowing_reused_without_reopening_row_5",
    "owned_object_fast_path_privacy_surface_evaluated",
    "shared_object_epoch_settlement_privacy_surface_evaluated",
    "validator_gossip_privacy_surface_evaluated",
)
FINAL_STATUS_LINES = {
    "`row_5_post_697_status=spec_closed_runtime_pending`",
    "`row_5_post_697_status=partial`",
}
ALLOWED_VERDICTS = {"HOLDS", "DOES NOT HOLD", "NEW GAP IDENTIFIED"}
PHASE_697_SUBJECT = ("phase 697", "row-5 mechanism proof over mysticeti")
PHASE_697_BACKFILL_SUBJECT = ("phase 697", "walkthrough", "backfill")
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


def _section(text: str, start_heading: str, end_heading: str | None = None) -> str:
    start = text.index(start_heading)
    if end_heading is None:
        return text[start:]
    end = text.index(end_heading, start)
    return text[start:end]


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
    raise AssertionError("phase_697_commit_not_present_in_local_history")


def test_artifact_exists_and_contains_all_required_headings_in_order() -> None:
    text = _read(ARTIFACT_PATH)
    positions = [text.index(heading) for heading in REQUIRED_HEADINGS]
    assert positions == sorted(positions)


def test_artifact_contains_all_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_proof_matrix_uses_only_allowed_verdict_vocabulary() -> None:
    text = _read(ARTIFACT_PATH)
    matrix = _section(
        text,
        "## 3. Criterion-by-criterion proof matrix",
        "## 4. New gaps or residual incompatibilities",
    )
    verdict_rows = []
    for line in matrix.splitlines():
        if not line.startswith("|") or "Verdict" in line or "---" in line:
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) != 3:
            continue
        verdict_rows.append(parts[-1])
    assert len(verdict_rows) >= 4
    assert set(verdict_rows).issubset(ALLOWED_VERDICTS)


def test_exactly_one_final_status_line_is_present() -> None:
    text = _read(ARTIFACT_PATH)
    found = [line for line in FINAL_STATUS_LINES if line in text]
    assert len(found) == 1


def test_artifact_explicitly_evaluates_owned_shared_gossip_and_operator_path_surfaces() -> None:
    text = _read(ARTIFACT_PATH)
    assert "owned-object fast path" in text
    assert "shared-object epoch settlement" in text
    assert "validator gossip" in text
    assert "operator-path" in text
    assert "hosting-path" in text


def test_decision_log_and_ilc_core_remain_unmutated_in_this_phase() -> None:
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


def test_phase_697_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_697_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_697_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_697_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
