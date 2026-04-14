from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = ROOT / "docs/specs/ilc_transport_hardening_and_maturity_decision_669_v0.1.md"
TEST_PATH = ROOT / "tests/test_phase_669_transport_hardening_and_maturity_decision.py"
WALKTHROUGH_PATH = ROOT / "docs/phases/phase_669_g8_transport_hardening_loop_and_maturity_decision_walkthrough.md"
STATUS_PATH = ROOT / "docs/phases/STATUS.md"
DECISION_LOG_PATH = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"


REQUIRED_HEADINGS = [
    "## 1. Purpose and hardening posture",
    "## 2. Failure classes addressed",
    "## 3. Changes made and why",
    "## 4. Closure-tier rerun results",
    "## 5. Maturity decision and residual risks",
    "## 6. Stretch-tier carry-forward",
]

REQUIRED_TOKENS = [
    "highest_value_failures_addressed_before_long_tail_polish",
    "row_9_closure_candidate_if_and_only_if_closure_tier_passes_after_hardening",
    "stretch_tier_findings_block_only_if_core_failure",
    "residual_risks_recorded_honestly",
    "dynamic_discovery_still_deferred_after_669",
    "openclaw_overlay_not_required_for_base_transport_correctness",
]

MAIN_COMMIT_SUBJECT_TOKENS = ("phase 669", "transport hardening and maturity decision")
BACKFILL_COMMIT_SUBJECT_TOKENS = ("phase 669", "walkthrough", "backfill")
MAIN_PATH_SET = {
    "docs/specs/ilc_transport_hardening_and_maturity_decision_669_v0.1.md",
    "tests/test_phase_669_transport_hardening_and_maturity_decision.py",
}
BACKFILL_PATH_SET = {
    "docs/phases/phase_669_g8_transport_hardening_loop_and_maturity_decision_walkthrough.md",
    "docs/phases/STATUS.md",
}


def _read_artifact() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def _paths_for_subject_tokens(subject_tokens: tuple[str, ...]) -> set[str]:
    log = subprocess.run(
        ["git", "log", "--format=%H%x00%s"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    for line in log.stdout.splitlines():
        commit, subject = line.split("\x00", 1)
        lowered = subject.lower()
        if all(token in lowered for token in subject_tokens):
            show = subprocess.run(
                ["git", "show", "--name-only", "--format=", commit],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            return {entry.strip() for entry in show.stdout.splitlines() if entry.strip()}
    raise AssertionError(f"commit_not_found:{subject_tokens}")


def _current_changed_paths() -> set[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return {line[3:] for line in result.stdout.splitlines() if line.strip()}


def test_artifact_exists_and_contains_required_headings() -> None:
    text = _read_artifact()
    assert ARTIFACT_PATH.exists()
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_artifact_contains_required_decision_tokens() -> None:
    text = _read_artifact()
    for token in REQUIRED_TOKENS:
        assert token in text


def test_artifact_records_addressed_failure_classes_and_justified_non_addressed_items() -> None:
    text = _read_artifact()
    assert "repo-local harness ambiguity" in text
    assert "live operational preconditions" in text
    assert "Not addressed in this window" in text


def test_artifact_records_closure_tier_rerun_results_explicitly() -> None:
    text = _read_artifact()
    for scenario in (
        "bootstrap",
        "steady-state dissemination",
        "churn",
        "partition/heal/recovery",
        "HTTP/2 fallback activation",
        "restart/rejoin",
        "bounded push correctness",
        "pull-only heavy payload correctness",
    ):
        assert scenario in text
    assert "blocked by missing SSH agent identity" in text


def test_artifact_contains_clear_row9_non_candidate_decision() -> None:
    text = _read_artifact()
    assert "row 9 is not a closure candidate for Phase 670" in text


def test_stretch_tier_findings_are_non_blocking_unless_core_failure() -> None:
    text = _read_artifact()
    assert "stretch-tier work stays non-blocking" in text
    assert "closure-tier precondition" in text


def test_dynamic_discovery_remains_deferred() -> None:
    text = _read_artifact()
    assert "dynamic_discovery_still_deferred_after_669" in text


def test_mutations_stay_within_allowed_surfaces() -> None:
    try:
        assert _paths_for_subject_tokens(MAIN_COMMIT_SUBJECT_TOKENS) == MAIN_PATH_SET
    except AssertionError as exc:
        if not str(exc).startswith("commit_not_found:"):
            raise
        assert _current_changed_paths() == MAIN_PATH_SET


def test_decision_log_remains_unchanged() -> None:
    subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH.relative_to(ROOT))],
        cwd=ROOT,
        check=True,
    )


def test_main_and_backfill_commit_path_sets_obey_phase_scope() -> None:
    try:
        assert _paths_for_subject_tokens(MAIN_COMMIT_SUBJECT_TOKENS) == MAIN_PATH_SET
    except AssertionError as exc:
        if not str(exc).startswith("commit_not_found:"):
            raise
        assert _current_changed_paths() == MAIN_PATH_SET

    try:
        assert _paths_for_subject_tokens(BACKFILL_COMMIT_SUBJECT_TOKENS) == BACKFILL_PATH_SET
    except AssertionError as exc:
        if not str(exc).startswith("commit_not_found:"):
            raise
