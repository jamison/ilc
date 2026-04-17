from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_adaptive_gossip_law_vs_freedom_contract_714_v0.1.md")
TEST_PATH = Path(
    "tests/test_phase_714_adaptive_gossip_contract_and_law_vs_freedom_classification.py"
)
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_714_g8_adaptive_gossip_contract_and_law_vs_freedom_classification_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Baseline",
    "## 2. Inherited settled law",
    "## 3. Live gossip parameter inventory",
    "## 4. Classification matrix",
    "## 5. Constitutional-law set",
    "## 6. Operator-configurable set",
    "## 7. Deferred set",
    "## 8. Non-goals and carry-forward",
)
REQUIRED_TOKENS = (
    "adaptive_gossip_law_vs_freedom_contract_714",
    "every_live_gossip_parameter_classified",
    "constitutional_law",
    "operator_configurable",
    "deferred",
    "cdl_060_and_cdl_061_settled_not_reopened",
    "retry_and_epoch_range_surfaces_classified_or_explicitly_deferred",
)
PHASE_MAIN_SUBJECT = (
    "phase 714",
    "adaptive gossip contract",
    "law-vs-freedom classification",
)
PHASE_BACKFILL_SUBJECT = ("phase 714", "walkthrough", "status", "backfill")
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
    raise AssertionError("phase_714_commit_not_present_in_local_history")


def _try_resolve_commit_ref(
    subject_tokens: tuple[str, ...], expected_paths: set[str]
) -> str | None:
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


def test_artifact_classifies_required_minimum_surfaces() -> None:
    text = _read(ARTIFACT_PATH)
    assert "`PEER_DISCOVERY_MODE`" in text
    assert "`MAX_PEERS`" in text
    assert "`MAX_FANOUT`" in text
    assert "select_fanout_peers()" in text
    assert "`request_timeout_seconds`" in text
    assert "`ILC-Epoch`" in text


def test_artifact_keeps_fanout_principle_distinct_from_exact_numeric_value() -> None:
    text = _read(ARTIFACT_PATH)
    assert "bounded-fanout principle" in text
    assert "`MAX_FANOUT = 3` | `operator_configurable`" in text
    assert "The inherited law is bounded fanout, not clearly the literal value `3`" in text


def test_artifact_classifies_retry_and_epoch_range_surfaces_honestly() -> None:
    text = _read(ARTIFACT_PATH)
    assert "stronger epoch staleness / range rule | `deferred`" in text
    assert "explicit retry / backoff knob | `deferred`" in text
    assert "marked `deferred` rather than invented" in text


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
    text = _read(ARTIFACT_PATH)
    assert "`CDL-060` and `CDL-061` are inherited anchors, not reopened here" in text
    assert "`CDL-039` ratification does not occur in this window" in text
    assert "ratify any CDL" in text


def test_phase_714_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_714_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
