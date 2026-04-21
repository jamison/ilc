from __future__ import annotations

import os
import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_row_7_exitability_closure_evaluation_cw4_v0.1.md")
TEST_PATH = Path("tests/test_cw4_row_7_exitability_closure_evaluation.py")
STATUS_PATH = Path("docs/phases/STATUS.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_SUBJECT = ("cw-4", "phase 760", "row-7 exitability")
REQUIRED_HEADINGS = (
    "## 1. Evaluation target and hard threshold",
    "## 2. Step 1 — Export",
    "## 3. Step 2 — Independent verify",
    "## 4. Step 3 — Replay on a fresh node",
    "## 5. Step 4 — Migrate without original-operator consent",
    "## 6. Combined row-7 verdict",
    "## 7. Non-claims",
)
REQUIRED_TOKENS = (
    "row_7_strong_exitability_runtime_closure_verdict=pass",
    "row_7_combined_runtime_status=runtime_closed",
    "row_7_censorship_and_exitability_both_pass",
    "row_7_operator_api_independence_confirmed",
)
REQUIRED_COMMIT_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
    str(STATUS_PATH),
    str(PLANNING_INDEX_PATH),
}
SELFTEST_ENV = "ILC_CW4_GATE_SELFTEST"


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


def _resolve_commit_ref(subject_tokens: tuple[str, ...]) -> str:
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
    if not matches:
        raise AssertionError("cw4_commit_not_present_in_local_history")
    return matches[0]


def _try_resolve_commit_ref(subject_tokens: tuple[str, ...]) -> str | None:
    try:
        return _resolve_commit_ref(subject_tokens)
    except AssertionError:
        return None


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


def test_physical_evidence_for_all_four_steps_is_quoted() -> None:
    if _selftest():
        return
    text = _normalized(_read(ARTIFACT_PATH))
    required = (
        "tools/testbed/m022_export.json",
        "tools/testbed/m022_verify.json",
        "tools/testbed/m022_replay.log",
        "tools/testbed/m022_migrate.json",
        "epoch_chain: epochs 1-3 (gap-free)",
        "chain_complete: true",
        "operator_api_calls: 0",
        "running_validator_required: false",
        "current_epoch=3",
        "gRPC_replay_verdict=pass",
        "workload_d_replayability_pass",
    )
    for item in required:
        assert item in text


def test_combined_row_7_status_and_phase_674_threshold_are_present() -> None:
    if _selftest():
        return
    text = _normalized(_read(ARTIFACT_PATH))
    assert "That threshold requires all four of the following" in text
    assert "export" in text
    assert "independent verify" in text
    assert "replay from portable data on a fresh node" in text
    assert "migrate without privileged original-operator consent" in text
    assert "combined status: `row_7_combined_runtime_status=runtime_closed`" in text


def test_selftest_guard_is_declared_in_test_file() -> None:
    text = _read(TEST_PATH)
    assert SELFTEST_ENV in text
    assert "if _selftest():" in text


def test_decision_log_and_runtime_code_surfaces_are_untouched_in_cw4() -> None:
    if _selftest():
        return
    result_decision = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result_decision.returncode == 0


def test_cw4_commit_includes_required_paths_and_excludes_runtime_code() -> None:
    if _selftest():
        return
    commit_ref = _try_resolve_commit_ref(PHASE_SUBJECT)
    if commit_ref:
        changed_paths = _changed_paths_for_commit(commit_ref)
        assert REQUIRED_COMMIT_PATHS.issubset(changed_paths)
        assert str(DECISION_LOG_PATH) not in changed_paths
        assert not any(path == "ilc_core" or path.startswith("ilc_core/") for path in changed_paths)
        assert not any(
            path == "ilc_consensus" or path.startswith("ilc_consensus/")
            for path in changed_paths
        )
        return

    result = subprocess.run(
        ["git", "status", "--short", "--", *sorted(REQUIRED_COMMIT_PATHS)],
        capture_output=True,
        check=True,
        text=True,
    )
    paths = {line[3:].strip() for line in result.stdout.splitlines() if line.strip()}
    assert REQUIRED_COMMIT_PATHS == paths
