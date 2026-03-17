"""Phase 437 runtime-tranche findings memo and regression-hardening tests."""

from __future__ import annotations

import subprocess
from pathlib import Path

MEMO_PATH = Path("docs/specs/ilc_runtime_tranche_findings_memo_437_v0.1.md")
PHASE_435_HANDOFF_PATH = Path("docs/specs/ilc_runtime_tranche_peer_fanout_handoff_435_v0.1.md")
PHASE_436_HANDOFF_PATH = Path("docs/specs/ilc_runtime_tranche_benchmark_handoff_436_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_437_COMMIT_SUBJECT = "docs(g8): phase 437 runtime tranche findings memo and regression hardening"


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_437_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    required_paths = {
        str(MEMO_PATH),
        "tests/test_phase_437_runtime_tranche_findings_memo_and_regression_hardening.py",
    }
    matching_commits: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_437_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if changed_paths == required_paths:
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_437_commit_subject_present_but_no_qualifying_findings_commit")
    raise AssertionError("phase_437_commit_not_present_in_local_history")


def _assert_phase_437_scope(commit_ref: str) -> None:
    changed_paths = _changed_paths_for_commit(commit_ref)
    required_paths = {
        str(MEMO_PATH),
        "tests/test_phase_437_runtime_tranche_findings_memo_and_regression_hardening.py",
    }
    assert changed_paths == required_paths, f"phase_437_scope_mismatch:{sorted(changed_paths)}"
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
    assert "tools/runtime_baseline.py" not in changed_paths


def test_findings_memo_has_required_headings() -> None:
    text = MEMO_PATH.read_text(encoding="utf-8")
    for heading in (
        "## 1. Runtime tranche settlement summary",
        "## 2. Measured local baseline evidence",
        "## 3. Peer fanout observations",
        "## 4. Code-health and regression-hardening assessment",
        "## 5. Open items and non-goals",
        "## 6. Phase 438 pointer",
    ):
        assert heading in text


def test_findings_memo_contains_required_measurement_and_boundary_tokens() -> None:
    text = MEMO_PATH.read_text(encoding="utf-8")
    for token in (
        "Phase 437 records the settled findings state after the numbered runtime tranche completed in Phases 435 and 436.",
        "Real HTTP peer fanout landed in Phase 435 and the benchmark harness landed in Phase 436.",
        "The Phase-437 measurements were taken with tools/runtime_baseline.py using 3 iterations at fanout 2, 5, 10, and the default fanout 3 baseline.",
        "All four default runtime baseline budgets remained within budget in the Phase-437 local-process measurements.",
        "Peer fanout average latency at fanout 2 was 0.523 ms with 3824.092 deliveries_per_second.",
        "Peer fanout average latency at fanout 5 was 1.053 ms with 4748.338 deliveries_per_second.",
        "Peer fanout average latency at fanout 10 was 1.66 ms with 6024.096 deliveries_per_second.",
        "Default fanout-3 local-process averages were claim_ingest=2.395 ms, peer_fanout=0.718 ms, epoch_snapshot=0.176 ms, event_export=22.118 ms.",
        "tests/test_code_health.py` remained green after the Phase-435 hotspot cleanup.",
        "CDL-050 remains unopened and unaffected by Phase 437.",
        "Phase 438 is the next authorized Treasury P_e prerequisite-satisfaction review.",
    ):
        assert token in text


def test_findings_memo_records_no_additional_regression_hardening() -> None:
    text = MEMO_PATH.read_text(encoding="utf-8")
    assert "No additional regression hardening was required beyond the exact path-set and source-hash guards already published in Phases 435 and 436." in text


def test_findings_memo_records_open_measurement_gap() -> None:
    text = MEMO_PATH.read_text(encoding="utf-8")
    assert "No multi-process or native-P2P measurement exists yet; that remains future work outside Phase 437." in text


def test_phase_435_and_phase_436_handoffs_retain_carry_forward_tokens() -> None:
    phase_435_text = PHASE_435_HANDOFF_PATH.read_text(encoding="utf-8")
    phase_436_text = PHASE_436_HANDOFF_PATH.read_text(encoding="utf-8")
    assert "tools/runtime_baseline.py remains deferred to Phase 436." in phase_435_text
    assert "The numbered runtime tranche authorized by Phase 434 is complete after Phase 436." in phase_436_text
    assert "Phase 437 is the next authorized non-sensitive findings and regression-hardening phase." in phase_436_text


def test_phase_437_commit_did_not_mutate_decision_log() -> None:
    commit_ref = _resolve_phase_437_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths


def test_phase_437_scope_is_exact() -> None:
    commit_ref = _resolve_phase_437_commit_ref()
    _assert_phase_437_scope(commit_ref)
