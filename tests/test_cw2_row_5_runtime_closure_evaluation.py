from __future__ import annotations

import os
import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_row_5_runtime_closure_evaluation_cw2_v0.1.md")
TEST_PATH = Path("tests/test_cw2_row_5_runtime_closure_evaluation.py")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Evaluation target and inherited bar",
    "## 2. Raw committed results and threshold comparison",
    "## 3. Observability-floor verdict",
    "## 4. Honest row-5 verdict",
    "## 5. Required carry-forward before row 5 can close",
    "## 6. Non-claims",
)
REQUIRED_TOKENS = (
    "row_5_runtime_closure_verdict=fail",
    "row_5_status=spec_closed_runtime_pending",
    "row_5_observability_floor_verdict=pass",
    "row_5_fail_expected_pre_constitutional_no_privacy_layer",
    "row_5_two_layer_defence_required_before_runtime_closure",
)
PHASE_SUBJECT = ("cw-2", "phase 758", "row-5 runtime-closure evaluation")
EXACT_REQUIRED_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
SELFTEST_ENV = "ILC_CW2_GATE_SELFTEST"


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
    raise AssertionError("cw2_commit_not_present_in_local_history")


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


def test_fail_verdict_and_pending_status_are_explicit() -> None:
    if _selftest():
        return
    text = _normalized(_read(ARTIFACT_PATH))
    assert "Overall row-5 runtime-closure verdict: - `row_5_runtime_closure_verdict=fail`" in text
    assert "Status after evaluation: - `row_5_status=spec_closed_runtime_pending`" in text
    assert "row `5` remains pending" in text


def test_raw_recall_figures_and_thresholds_are_quoted_not_softened() -> None:
    if _selftest():
        return
    text = _normalized(_read(ARTIFACT_PATH))
    required = (
        "`Recall = 1.0`",
        "`Recall (observed) = 0.0`",
        "`Recall (structural) = 1.0`",
        "`structural recall = 1.0`",
        "`<= 0.60`",
        "`<= 0.45`",
        "`1.0 > 0.60`",
        "`1.0 > 0.45`",
    )
    for item in required:
        assert item in text


def test_observability_floor_and_two_layer_defence_are_present() -> None:
    if _selftest():
        return
    text = _normalized(_read(ARTIFACT_PATH))
    assert "receipts discoverable: `PASS`" in text
    assert "lineage legible: `PASS`" in text
    assert "challengeability preserved: `PASS`" in text
    assert "bounded human auditability preserved: `PASS`" in text
    assert "AgentID redaction" in text
    assert "mixing or k-anonymity-style protection" in text


def test_selftest_guard_is_declared_in_test_file() -> None:
    text = _read(TEST_PATH)
    assert SELFTEST_ENV in text
    assert "if _selftest():" in text


def test_decision_log_and_runtime_code_surfaces_are_untouched_in_cw2() -> None:
    if _selftest():
        return
    result_decision = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result_decision.returncode == 0


def test_cw2_commit_touches_expected_paths_only() -> None:
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
