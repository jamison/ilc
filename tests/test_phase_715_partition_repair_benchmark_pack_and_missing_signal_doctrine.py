from __future__ import annotations

import subprocess
from pathlib import Path


BENCHMARK_PATH = Path("docs/specs/ilc_partition_repair_benchmark_pack_715_v0.1.md")
DOCTRINE_PATH = Path("docs/specs/ilc_missing_signal_doctrine_disposition_715_v0.1.md")
TEST_PATH = Path("tests/test_phase_715_partition_repair_benchmark_pack_and_missing_signal_doctrine.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_715_g8_partition_repair_benchmark_pack_and_missing_signal_doctrine_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
BENCHMARK_REQUIRED_HEADINGS = (
    "## 1. Baseline",
    "## 2. Commissioning posture",
    "## 3. Scenario matrix",
    "## 4. Pass criteria and evidence format",
    "## 5. Repair definition",
    "## 6. Explicit deferred boundaries",
)
DOCTRINE_REQUIRED_HEADINGS = (
    "## 1. Baseline",
    "## 2. Selected behavior",
    "## 3. Escalation path",
    "## 4. Implicated source surfaces",
    "## 5. Deferred items and non-goals",
)
BENCHMARK_REQUIRED_TOKENS = (
    "partition_repair_commissioning_only_no_results_claimed",
    "static_v1_peer_registry_preserved",
    "repair_evidence_format_defined",
    "topology_shuffling_not_authorized_here",
)
DOCTRINE_REQUIRED_TOKENS = (
    "missing_signal_behavior_explicitly_selected",
    "behavior_defines_escalation_without_new_ratification",
    "no_dynamic_discovery_or_topology_shuffling_authorized_here",
)
PHASE_MAIN_SUBJECT = (
    "phase 715",
    "partition-repair benchmark pack",
    "missing-signal doctrine",
)
PHASE_BACKFILL_SUBJECT = ("phase 715", "walkthrough", "status", "backfill")
EXACT_REQUIRED_MAIN_PATHS = {
    str(BENCHMARK_PATH),
    str(DOCTRINE_PATH),
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
    raise AssertionError("phase_715_commit_not_present_in_local_history")


def _try_resolve_commit_ref(
    subject_tokens: tuple[str, ...], expected_paths: set[str]
) -> str | None:
    try:
        return _resolve_commit_ref(subject_tokens, expected_paths)
    except AssertionError:
        return None


def test_benchmark_and_doctrine_artifacts_have_required_headings_in_order() -> None:
    benchmark_text = _read(BENCHMARK_PATH)
    doctrine_text = _read(DOCTRINE_PATH)
    benchmark_positions = [benchmark_text.index(heading) for heading in BENCHMARK_REQUIRED_HEADINGS]
    doctrine_positions = [doctrine_text.index(heading) for heading in DOCTRINE_REQUIRED_HEADINGS]
    assert benchmark_positions == sorted(benchmark_positions)
    assert doctrine_positions == sorted(doctrine_positions)


def test_benchmark_and_doctrine_artifacts_contain_required_tokens() -> None:
    benchmark_text = _read(BENCHMARK_PATH)
    doctrine_text = _read(DOCTRINE_PATH)
    for token in BENCHMARK_REQUIRED_TOKENS:
        assert token in benchmark_text
    for token in DOCTRINE_REQUIRED_TOKENS:
        assert token in doctrine_text


def test_benchmark_pack_is_commissioning_only_and_defines_repair_under_static_baseline() -> None:
    text = _read(BENCHMARK_PATH)
    assert "does not publish benchmark results" in text
    assert "bounded reconnect and re-sync over the same static peer set" in text
    assert "no dynamic discovery authorization" in text
    assert "no topology-shuffling authorization" in text


def test_benchmark_pack_defines_scenarios_and_evidence_format() -> None:
    text = _read(BENCHMARK_PATH)
    assert "`PR-715-01`" in text
    assert "`PR-715-02`" in text
    assert "`PR-715-03`" in text
    assert "repair-complete epoch" in text
    assert "deterministic and auditable" in text


def test_missing_signal_doctrine_selects_explicit_behavior_and_names_cdl_v1_role() -> None:
    text = _read(DOCTRINE_PATH)
    assert "grace period + alert, then fail-soft degradation" in text
    assert "`CDL-V1` temporal decay participates only as a longer-horizon reputational" in text
    assert "`CDL-039` ratification does not occur here" in text
    assert "no new CDL row" in text


def test_decision_log_and_runtime_surfaces_remain_unmutated_in_this_phase() -> None:
    main_commit = _try_resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    backfill_commit = _try_resolve_commit_ref(
        PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS
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


def test_phase_715_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_715_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
