from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path(
    "docs/research/ilc_inverted_ecu_model_runtime_traceability_note_705_v0.1.md"
)
TEST_PATH = Path(
    "tests/test_phase_705_inverted_ecu_runtime_traceability_and_doctrine_preservation.py"
)
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_705_g8_inverted_ecu_runtime_traceability_and_doctrine_preservation_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Historical model and scope boundary",
    "## 2. Current runtime surfaces under review",
    "## 3. Traceability matrix",
    "## 4. Doctrine preservation versus current law",
    "## 5. Final disposition",
)
REQUIRED_TOKENS = (
    "inverted_ecu_traceability_705_complete",
    "cdl_v1_temporal_decay_explicitly_evaluated",
    "cdl_048_mandatory_conversion_explicitly_evaluated",
    "inverted_ecu_runtime_mapping=partial_operational_implementation_via_cdl_v1_and_cdl_048",
    "inverted_ecu_disposition=spec_or_contract_lock_plus_doctrine_preservation",
)
PHASE_705_SUBJECT = ("phase 705", "inverted-ecu runtime traceability and doctrine preservation")
PHASE_705_BACKFILL_SUBJECT = ("phase 705", "walkthrough", "backfill")
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
    raise AssertionError("phase_705_commit_not_present_in_local_history")


def _try_resolve_commit_ref(subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str | None:
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


def test_artifact_marks_historical_model_as_precanonical_and_bounded() -> None:
    text = _read(ARTIFACT_PATH)
    assert "The historical inverted-ECU model is not current law." in text
    assert "precanonical" in text
    assert "current earn-first model" in text
    assert "proposed inverted model" in text


def test_artifact_explicitly_evaluates_cdl_v1_and_cdl_048() -> None:
    text = _read(ARTIFACT_PATH)
    assert "`CDL-V1` temporal decay" in text
    assert "`CDL-048` mandatory conversion" in text
    assert "partial operational implementation of inverted circulation" in text
    assert "The live system is still earn-first, not spend-first." in text


def test_artifact_preserves_doctrine_without_ratifying_cdl_053() -> None:
    text = _read(ARTIFACT_PATH)
    assert "This note does not itself ratify `CDL-053`." in text
    assert "`CDL-053` is still a future constitutional/design vehicle" in text
    assert "the full historical package is not yet ratified as law" in text


def test_decision_log_and_runtime_paths_remain_unmutated_in_this_phase() -> None:
    main_commit = _try_resolve_commit_ref(PHASE_705_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    backfill_commit = _try_resolve_commit_ref(
        PHASE_705_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS
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


def test_phase_705_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_705_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_705_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_705_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
