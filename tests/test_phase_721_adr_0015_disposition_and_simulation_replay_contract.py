from __future__ import annotations

import subprocess
from pathlib import Path


DISPOSITION_PATH = Path("docs/specs/ilc_adr_0015_node_transfer_economics_disposition_721_v0.1.md")
CONTRACT_PATH = Path(
    "docs/specs/ilc_transfer_tax_cooling_and_leasehold_simulation_replay_contract_721_v0.1.md"
)
CDL_MEMO_PATH = Path(
    "docs/specs/ilc_transfer_economics_cdl_opening_recommendation_or_deferment_721_v0.1.md"
)
TEST_PATH = Path("tests/test_phase_721_adr_0015_disposition_and_simulation_replay_contract.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_721_g8_adr_0015_disposition_and_simulation_replay_contract_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
DISPOSITION_HEADINGS = (
    "## 1. Baseline",
    "## 2. Per-mechanism verdicts",
    "## 3. Launch-bound versus deferred matrix",
    "## 4. Required follow-on evidence",
    "## 5. Non-ratification boundary",
)
CONTRACT_HEADINGS = (
    "## 1. Baseline",
    "## 2. Scenario family",
    "## 3. Pass criteria",
    "## 4. Evidence format",
    "## 5. Out-of-window results boundary",
)
CDL_MEMO_HEADINGS = (
    "## 1. Baseline",
    "## 2. Why a new CDL is or is not required",
    "## 3. Recommended next action",
    "## 4. Non-goals",
)
REQUIRED_TOKENS = (
    "adr_0015_family_disposition_explicit",
    "per_mechanism_verdicts_recorded",
    "launch_bound_post_launch_bound_and_deferred_matrix_recorded",
    "no_cdl_ratification_occurs_in_phase_721",
    "simulation_and_replay_commissioning_only",
    "transfer_tax_cooling_and_leasehold_questions_commissioned",
    "results_not_claimed_in_window_717_722",
    "cdl_opening_recommendation_or_deferment_explicit",
    "no_ratification_requested_here",
)
PHASE_MAIN_SUBJECT = ("phase 721", "adr-0015 disposition", "simulation contract")
PHASE_BACKFILL_SUBJECT = ("phase 721", "walkthrough", "backfill")
EXACT_REQUIRED_MAIN_PATHS = {
    str(DISPOSITION_PATH),
    str(CONTRACT_PATH),
    str(CDL_MEMO_PATH),
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
    raise AssertionError("phase_721_commit_not_present_in_local_history")


def _try_resolve_commit_ref(subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str | None:
    try:
        return _resolve_commit_ref(subject_tokens, expected_paths)
    except AssertionError:
        return None


def test_artifacts_exist_and_contain_required_headings_in_order() -> None:
    for path, headings in (
        (DISPOSITION_PATH, DISPOSITION_HEADINGS),
        (CONTRACT_PATH, CONTRACT_HEADINGS),
        (CDL_MEMO_PATH, CDL_MEMO_HEADINGS),
    ):
        text = _read(path)
        positions = [text.index(heading) for heading in headings]
        assert positions == sorted(positions)


def test_artifacts_contain_required_tokens() -> None:
    combined = "\n".join((_read(DISPOSITION_PATH), _read(CONTRACT_PATH), _read(CDL_MEMO_PATH)))
    for token in REQUIRED_TOKENS:
        assert token in combined


def test_disposition_records_explicit_family_verdicts_and_matrix() -> None:
    text = _read(DISPOSITION_PATH)
    assert "transfer tax: amended_accept" in text
    assert "cooling period: amended_accept" in text
    assert "commons dedication: amended_accept" in text
    assert "leasehold / reversion: deferred" in text
    assert "transfer tax -> `launch_bound`" in text
    assert "cooling period -> `launch_bound`" in text
    assert "commons dedication -> `launch_bound`" in text
    assert "leasehold / reversion -> `deferred`" in text


def test_commissioning_contract_is_results_free_and_has_pass_criteria() -> None:
    text = _read(CONTRACT_PATH)
    assert "This window commissions the evidence only. Results are not claimed in Window\n`717-722`." in text
    assert "a transfer-tax candidate range that discourages speculative flipping" in text
    assert "a cooling-period candidate that preserves a meaningful challenge window" in text
    assert "a leasehold candidate that does not collapse reuse incentives" in text


def test_cdl_memo_explicitly_defers_new_opening() -> None:
    text = _read(CDL_MEMO_PATH)
    assert "No new CDL opening is required in this window." in text
    assert "The recommended next action is explicit deferment of any new transfer-economics\nCDL opening" in text


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


def test_phase_721_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_721_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
