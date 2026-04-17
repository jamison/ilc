from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/research/ilc_validator_agent_design_evidence_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path(
    "tests/test_phase_710_validator_agent_design_evidence_and_cdl_017_prelock_mapping.py"
)
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_710_g8_validator_agent_design_evidence_and_cdl_017_prelock_mapping_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")

REQUIRED_HEADINGS = (
    "## 1. Baseline and accepted premises",
    "## 2. Q1-Q6 resolved answers",
    "## 3. Rejected alternatives",
    "## 4. CDL-017 prelock mapping",
    "## 5. Deferred items and later-window routing",
)
REQUIRED_TOKENS = (
    "validator_agent_design_evidence_complete",
    "q1_q6_answers_recorded_for_cdl_017_prelock",
    "cdl_017_prelock_only_not_ratified_here",
    "validation_pools_deferred_beyond_cdl_017_core",
)
PHASE_MAIN_SUBJECT = ("phase 710", "validator-agent design evidence")
PHASE_BACKFILL_SUBJECT = ("phase 710", "walkthrough", "backfill")
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
    raise AssertionError("phase_710_commit_not_present_in_local_history")


def test_artifact_contains_required_headings_and_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text
    for token in REQUIRED_TOKENS:
        assert token in text


def test_artifact_records_all_q1_q6_choices_and_rejected_alternatives() -> None:
    text = _read(ARTIFACT_PATH)
    assert "Derived sub-key with provable linkage from `AgentID`" in text
    assert "Simulation-derived minimum ECU stake floor" in text
    assert "Threshold-gated eligibility pool" in text
    assert "Separate subsequent CDL for validation pools" in text
    assert "Epoch-hash is acceptable for testnet framing; production VRF remains open" in text
    assert "Extend `CDL-V3` to validator composition with an explicit metric" in text
    assert "Same BLS key for both surfaces" in text
    assert "Proportional `ecu_score` weighting" in text


def test_artifact_maps_answers_into_concrete_cdl_017_prelock_requirements() -> None:
    text = _read(ARTIFACT_PATH)
    assert "Identity linkage clause" in text
    assert "Stake-floor evidence gate" in text
    assert "Admission semantics" in text
    assert "Validation-pool exclusion clause" in text
    assert "Topology-seed provisional rule" in text
    assert "Validator-composition diversity clause" in text


def test_artifact_records_explicit_diversity_metric_and_later_evidence_path() -> None:
    text = _read(ARTIFACT_PATH)
    assert "`ecu_score_band` as epoch-boundary terciles" in text
    assert "span all three bands" in text
    assert "no more than `50%` of seats in a single band" in text
    assert "`SIM-TOPOLOGY-01`" in text
    assert "prelock candidate metric, not ratified runtime law" in text


def test_artifact_preserves_deferrals_and_non_ratification_boundary() -> None:
    text = _read(ARTIFACT_PATH)
    assert "`CDL-017` is still open and unratified" in text
    assert "validation pools, delegation, and slash propagation" in text
    assert "route to a separate subsequent CDL" in text
    assert "Mysticeti convergence window" in text


def test_decision_log_keeps_cdl_017_open() -> None:
    log_text = _read(DECISION_LOG_PATH)
    line = next(line for line in log_text.splitlines() if line.startswith("| CDL-017 |"))
    assert "| open |" in line
    assert "ratified_phase" not in line


def test_phase_710_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_710_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
