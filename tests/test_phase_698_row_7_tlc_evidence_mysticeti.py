from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_dag_censorship_bounds_tlc_evidence_698_v0.1.md")
TEST_PATH = Path("tests/test_phase_698_row_7_tlc_evidence_mysticeti.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_698_g8_row_7_tlc_model_check_evidence_for_mysticeti_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TLA_SPEC_A_PATH = Path("docs/specs/tla/ilc_dag_censorship_bounds.tla")
TLA_CFG_A_PATH = Path("docs/specs/tla/ilc_dag_censorship_bounds.cfg")
TLA_SPEC_B_PATH = Path("docs/specs/tla/ilc_ecu_fast_path_bcast.tla")
TLA_CFG_B_PATH = Path("docs/specs/tla/ilc_ecu_fast_path_bcast.cfg")
REQUIRED_HEADINGS = (
    "## 1. Verification target and model parameters",
    "## 2. Checked invariants and temporal properties",
    "## 3. TLC execution record",
    "## 4. TTrace artifact disposition",
    "## 5. Row-7 disposition",
)
REQUIRED_TOKENS = (
    "row_7_tlc_evidence_698_complete",
    "tlc_model_n4_f1_maxround5",
    "checked_properties=TypeOK,Safety,CommittedSubsetDag,Liveness",
)
TTRACE_DISPOSITION_LINES = {
    "`spec_b_ttrace_1776345420_disposition=stale_pre_fix_artifact`",
    "`spec_b_ttrace_1776345420_disposition=active_gap`",
}
ROW_7_STATUS_LINES = {
    "`row_7_post_698_status=spec_closed_runtime_pending`",
    "`row_7_post_698_status=gap_found_no_state_advance`",
}
PHASE_698_SUBJECT = ("phase 698", "row-7 tlc evidence for mysticeti")
PHASE_698_BACKFILL_SUBJECT = ("phase 698", "walkthrough", "backfill")
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
    raise AssertionError("phase_698_commit_not_present_in_local_history")


def _try_resolve_commit_ref(subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str | None:
    try:
        return _resolve_commit_ref(subject_tokens, expected_paths)
    except AssertionError:
        return None


def test_artifact_exists_and_contains_all_required_headings_in_order() -> None:
    text = _read(ARTIFACT_PATH)
    positions = [text.index(heading) for heading in REQUIRED_HEADINGS]
    assert positions == sorted(positions)


def test_artifact_contains_all_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_exactly_one_ttrace_disposition_line_is_present() -> None:
    text = _read(ARTIFACT_PATH)
    found = [line for line in TTRACE_DISPOSITION_LINES if line in text]
    assert len(found) == 1


def test_exactly_one_row_7_status_line_is_present() -> None:
    text = _read(ARTIFACT_PATH)
    found = [line for line in ROW_7_STATUS_LINES if line in text]
    assert len(found) == 1


def test_artifact_references_tlc_output_log_and_model_parameters() -> None:
    text = _read(ARTIFACT_PATH)
    assert "tools/tla/ilc_dag_censorship_bounds.tlc.out" in text
    assert "N=4" in text
    assert "F=1" in text
    assert "MaxRound=5" in text
    assert "bash tools/run_tlc_m_series_gate.sh" in text


def test_decision_log_tla_specs_ilc_core_and_ilc_consensus_remain_unmutated_in_this_phase() -> None:
    main_commit = _try_resolve_commit_ref(PHASE_698_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    backfill_commit = _try_resolve_commit_ref(
        PHASE_698_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS
    )
    if main_commit and backfill_commit:
        forbidden_paths = {
            str(DECISION_LOG_PATH),
            str(TLA_SPEC_A_PATH),
            str(TLA_CFG_A_PATH),
            str(TLA_SPEC_B_PATH),
            str(TLA_CFG_B_PATH),
        }
        for commit_ref in (main_commit, backfill_commit):
            changed_paths = _changed_paths_for_commit(commit_ref)
            assert forbidden_paths.isdisjoint(changed_paths)
            assert not any(
                path == "ilc_core" or path.startswith("ilc_core/") for path in changed_paths
            )
            assert not any(
                path == "ilc_consensus" or path.startswith("ilc_consensus/")
                for path in changed_paths
            )
        return

    for path in (
        DECISION_LOG_PATH,
        TLA_SPEC_A_PATH,
        TLA_CFG_A_PATH,
        TLA_SPEC_B_PATH,
        TLA_CFG_B_PATH,
    ):
        result = subprocess.run(
            ["git", "diff", "--exit-code", "--", str(path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

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


def test_phase_698_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_698_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_698_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_698_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
