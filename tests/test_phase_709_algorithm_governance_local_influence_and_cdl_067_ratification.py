from __future__ import annotations

import subprocess
from pathlib import Path


CONTRACT_PATH = Path(
    "docs/specs/ilc_graph_native_algorithm_governance_contract_and_local_influence_example_709_v0.1.md"
)
EVIDENCE_PATH = Path(
    "docs/specs/ilc_cdl_067_settlement_substrate_governance_ratification_evidence_709_v0.1.md"
)
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_709_algorithm_governance_local_influence_and_cdl_067_ratification.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_709_g8_algorithm_governance_local_influence_and_cdl_067_ratification_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")

REQUIRED_CONTRACT_HEADINGS = (
    "## 1. Namespace and selection boundary",
    "## 2. Admissible source classes and compile path",
    "## 3. Local-influence worked example",
    "## 4. Limits and exclusions",
    "## 5. Carry-forward implications",
)
REQUIRED_CONTRACT_TOKENS = (
    "graph_native_algorithm_governance_contract_published",
    "algorithm_governance_namespace_bounded",
    "compiled_governance_artifacts_not_raw_nodes_feed_selection",
    "local_influence_example_is_bounded_and_non_autonomous",
    "algorithm_governance_contract_not_self_executing_beyond_scope",
)
REQUIRED_EVIDENCE_HEADINGS = (
    "## 1. Evidence basis",
    "## 2. Ratified settlement-state rule",
    "## 3. Carried state versus off-chain preserved state",
    "## 4. Preserved exclusions and backend non-goals",
    "## 5. Decision-log consequence",
)
REQUIRED_EVIDENCE_TOKENS = (
    "cdl_067_ratified_narrow_settlement_state_governance_vehicle",
    "settlement_state_scope_is_constitutional_surface",
    "backend_carries_already_legitimate_protocol_state_only",
    "epoch_boundary_submission_surface_is_ratified_narrowly",
    "cdl_067_does_not_freeze_backend_schema_or_select_option_b",
)
PHASE_MAIN_SUBJECT = ("phase 709", "algorithm governance", "cdl-067 ratification")
PHASE_BACKFILL_SUBJECT = ("phase 709", "walkthrough", "backfill")
EXACT_REQUIRED_MAIN_PATHS = {
    str(CONTRACT_PATH),
    str(EVIDENCE_PATH),
    str(DECISION_LOG_PATH),
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
    raise AssertionError("phase_709_commit_not_present_in_local_history")


def test_contract_contains_required_headings_and_tokens() -> None:
    text = _read(CONTRACT_PATH)
    for heading in REQUIRED_CONTRACT_HEADINGS:
        assert heading in text
    for token in REQUIRED_CONTRACT_TOKENS:
        assert token in text


def test_contract_records_bounded_local_influence_and_exclusions() -> None:
    text = _read(CONTRACT_PATH)
    assert "local neighborhood evidence may contribute up to a capped adjustment band" in text
    assert "`+/- 0.05`" in text
    assert "may not author protocol legitimacy" in text
    assert "runtime consumption of raw governance nodes" in text


def test_cdl_067_evidence_contains_required_headings_and_tokens() -> None:
    text = _read(EVIDENCE_PATH)
    for heading in REQUIRED_EVIDENCE_HEADINGS:
        assert heading in text
    for token in REQUIRED_EVIDENCE_TOKENS:
        assert token in text


def test_cdl_067_evidence_records_narrow_scope_and_preserved_exclusions() -> None:
    text = _read(EVIDENCE_PATH)
    assert "epoch-boundary commit records" in text
    assert "public node-linkage graph anchors" in text
    assert "per-agent detailed ECU balance ledgers" in text
    assert "final Option B selection" in text
    assert "full backend-schema freeze" in text


def test_decision_log_marks_cdl_067_as_ratified() -> None:
    log_text = _read(DECISION_LOG_PATH)
    line = next(line for line in log_text.splitlines() if line.startswith("| CDL-067 |"))
    assert "| ratified |" in line
    assert "ratified_phase: 709" in line
    assert (
        "evidence_document: docs/specs/ilc_cdl_067_settlement_substrate_governance_ratification_evidence_709_v0.1.md"
        in line
    )


def test_contract_and_evidence_do_not_overclaim_backend_freeze_or_cdl_017_ratification() -> None:
    contract_text = _read(CONTRACT_PATH)
    evidence_text = _read(EVIDENCE_PATH)
    assert "full graph-native governance runtime already exists" not in contract_text
    assert "`CDL-017` remains open" in evidence_text
    assert "does not ratify a specific sovereign substrate family" in evidence_text


def test_phase_709_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_709_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
