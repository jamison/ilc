from __future__ import annotations

import subprocess
from pathlib import Path


TRIGGER_PATH = Path("docs/specs/ilc_sequestered_financial_shard_post_launch_trigger_matrix_725_v0.1.md")
FIREWALL_PATH = Path("docs/specs/ilc_sequestered_financial_shard_contagion_firewall_prerequisites_725_v0.1.md")
TEST_PATH = Path(
    "tests/test_phase_725_financial_shard_trigger_matrix_and_contagion_firewall_prerequisites.py"
)
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_725_g8_financial_shard_trigger_matrix_and_contagion_firewall_prerequisites_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TRIGGER_HEADINGS = (
    "## 1. Baseline",
    "## 2. Minimum trigger conditions",
    "## 3. Disqualifying conditions",
    "## 4. Monitoring evidence requirement",
    "## 5. Current verdict",
)
FIREWALL_HEADINGS = (
    "## 1. Baseline",
    "## 2. Required isolation surfaces",
    "## 3. Budget and firewall prerequisites",
    "## 4. Auditability and failure containment",
    "## 5. Non-goals",
)
REQUIRED_TOKENS = (
    "post_launch_trigger_matrix_explicit",
    "public_launch_plus_monitoring_cycle_required",
    "concrete_demand_signal_required",
    "current_verdict_not_yet_eligible",
    "contagion_firewall_prerequisites_explicit",
    "b_hft_must_be_separate_from_b_e",
    "l1_l2_firewall_required",
    "market_microstructure_must_remain_sequestered",
)
PHASE_MAIN_SUBJECT = ("phase 725", "financial shard trigger matrix", "firewall prerequisites")
PHASE_BACKFILL_SUBJECT = ("phase 725", "walkthrough", "backfill")
EXACT_REQUIRED_MAIN_PATHS = {
    str(TRIGGER_PATH),
    str(FIREWALL_PATH),
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
    raise AssertionError("phase_725_commit_not_present_in_local_history")


def _try_resolve_commit_ref(subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str | None:
    try:
        return _resolve_commit_ref(subject_tokens, expected_paths)
    except AssertionError:
        return None


def test_artifacts_exist_and_contain_required_headings_in_order() -> None:
    trigger_text = _read(TRIGGER_PATH)
    firewall_text = _read(FIREWALL_PATH)
    trigger_positions = [trigger_text.index(heading) for heading in TRIGGER_HEADINGS]
    firewall_positions = [firewall_text.index(heading) for heading in FIREWALL_HEADINGS]
    assert trigger_positions == sorted(trigger_positions)
    assert firewall_positions == sorted(firewall_positions)


def test_artifacts_contain_required_tokens() -> None:
    combined = "\n".join((_read(TRIGGER_PATH), _read(FIREWALL_PATH)))
    for token in REQUIRED_TOKENS:
        assert token in combined


def test_trigger_matrix_records_minimum_triggers_and_current_verdict() -> None:
    text = _read(TRIGGER_PATH)
    assert "public launch must already exist" in text
    assert "at least one public-launch monitoring cycle must have completed" in text
    assert "concrete demand signal" in text
    assert "No new CDL opening is recommended in the current window." in text
    assert "The current verdict is not yet eligible." in text


def test_firewall_artifact_records_b_hft_and_isolation_requirements() -> None:
    text = _read(FIREWALL_PATH)
    assert "a dedicated `B_hft` surface must remain separate from `B_e`" in text
    assert "Treasury / L1 logic must not read or react to the market lane directly" in text
    assert "explicit separation from `CDL-062` sovereign-substrate work" in text
    assert "explicit separation from ADR-0022/private-gated rights and access hardening" in text


def test_artifacts_preserve_no_activation_boundary() -> None:
    combined = "\n".join((_read(TRIGGER_PATH), _read(FIREWALL_PATH)))
    assert "without activating\nthe lane" in combined or "without activating the lane" in combined
    assert "does not:\n\n- activate the lane" in combined


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


def test_phase_725_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_725_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
