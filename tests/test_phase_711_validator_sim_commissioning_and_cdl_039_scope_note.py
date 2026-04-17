from __future__ import annotations

import subprocess
from pathlib import Path


SIM_VALIDATOR_PATH = Path("docs/specs/ilc_sim_validator_01_commissioning_711_v0.1.md")
SIM_TOPOLOGY_PATH = Path("docs/specs/ilc_sim_topology_01_commissioning_711_v0.1.md")
SCOPE_NOTE_PATH = Path(
    "docs/specs/ilc_cdl_039_topology_shuffling_authorization_scope_note_711_v0.1.md"
)
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_711_validator_sim_commissioning_and_cdl_039_scope_note.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_711_g8_validator_sim_commissioning_and_cdl_039_scope_note_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")

REQUIRED_SIM_VALIDATOR_HEADINGS = (
    "## 1. Purpose and calibrated question",
    "## 2. Inputs and parameter sweep",
    "## 3. Required outputs and failure criteria",
    "## 4. Constitutional consequence and evidence threshold",
)
REQUIRED_SIM_VALIDATOR_TOKENS = (
    "sim_validator_01_commissioned",
    "stake_floor_not_yet_constitutional_numeric_law",
    "equivocation_must_be_economically_irrational",
    "sim_validator_01_results_required_before_cdl_017_numeric_floor",
)
REQUIRED_SIM_TOPOLOGY_HEADINGS = (
    "## 1. Commissioned questions",
    "## 2. Inputs, scenarios, and measured outputs",
    "## 3. Commissioning-only boundary and completion path",
    "## 4. Failure conditions and carry-forward meaning",
)
REQUIRED_SIM_TOPOLOGY_TOKENS = (
    "sim_topology_01_commissioned",
    "topology_commissioning_only_in_window_707_712",
    "epoch_hash_testnet_acceptable_vrf_production_open",
    "sim_topology_01_results_feed_later_cdl_039_authorization",
)
REQUIRED_SCOPE_NOTE_HEADINGS = (
    "## 1. Current ratified boundary",
    "## 2. Narrow authorization path for topology shuffling",
    "## 3. Epoch-hash versus VRF framing",
    "## 4. Preserved exclusions and privacy constraints",
)
REQUIRED_SCOPE_NOTE_TOKENS = (
    "cdl_039_scope_note_published",
    "topology_shuffling_requires_later_authorization",
    "cdl_039_privacy_boundary_preserved_during_shuffle_scope",
    "vrf_not_yet_production_ratified_here",
)
PHASE_MAIN_SUBJECT = ("phase 711", "validator sims", "cdl-039 scope note")
PHASE_BACKFILL_SUBJECT = ("phase 711", "walkthrough", "backfill")
EXACT_REQUIRED_MAIN_PATHS = {
    str(SIM_VALIDATOR_PATH),
    str(SIM_TOPOLOGY_PATH),
    str(SCOPE_NOTE_PATH),
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
    raise AssertionError("phase_711_commit_not_present_in_local_history")


def test_sim_validator_artifact_contains_required_headings_and_tokens() -> None:
    text = _read(SIM_VALIDATOR_PATH)
    for heading in REQUIRED_SIM_VALIDATOR_HEADINGS:
        assert heading in text
    for token in REQUIRED_SIM_VALIDATOR_TOKENS:
        assert token in text


def test_sim_validator_artifact_defines_inputs_outputs_and_failure_criteria() -> None:
    text = _read(SIM_VALIDATOR_PATH)
    assert "expected transfer volume per epoch" in text
    assert "`CDL-055` slash-rate assumptions" in text
    assert "candidate stake-floor interval" in text
    assert "non-negative expected value" in text
    assert "deterministic inputs" in text


def test_sim_topology_artifact_contains_required_headings_and_tokens() -> None:
    text = _read(SIM_TOPOLOGY_PATH)
    for heading in REQUIRED_SIM_TOPOLOGY_HEADINGS:
        assert heading in text
    for token in REQUIRED_SIM_TOPOLOGY_TOKENS:
        assert token in text


def test_sim_topology_artifact_records_commissioning_only_boundary_and_completion_path() -> None:
    text = _read(SIM_TOPOLOGY_PATH)
    assert "This phase is commissioning-only, not results-bearing" in text
    assert "connectivity / fragmentation results" in text
    assert "topology-inference or exposure risk indicators" in text
    assert "later `CDL-039` authorization work and `CDL-017` convergence consume the results" in text


def test_scope_note_preserves_narrow_authorization_boundary() -> None:
    text = _read(SCOPE_NOTE_PATH)
    for heading in REQUIRED_SCOPE_NOTE_HEADINGS:
        assert heading in text
    for token in REQUIRED_SCOPE_NOTE_TOKENS:
        assert token in text
    assert "epoch-hash is acceptable for testnet framing" in text
    assert "neither option is finally selected for production by this note" in text
    assert "production topology shuffling" in text
    assert "no heavy topology payload push that violates the hybrid push-pull posture" in text


def test_decision_log_states_remain_unchanged_for_cdl_039_and_cdl_017() -> None:
    log_text = _read(DECISION_LOG_PATH)
    cdl_039_line = next(line for line in log_text.splitlines() if line.startswith("| CDL-039 |"))
    cdl_017_line = next(line for line in log_text.splitlines() if line.startswith("| CDL-017 |"))
    assert "| ratified |" in cdl_039_line
    assert "| open |" in cdl_017_line


def test_phase_711_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_711_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
