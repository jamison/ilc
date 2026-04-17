from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/research/ilc_w_e_traceability_and_kernel_mapping_note_702_v0.1.md")
TEST_PATH = Path("tests/test_phase_702_w_e_traceability_and_doctrine_classification.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_702_g8_w_e_traceability_and_doctrine_classification_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Formula lineage and source basis",
    "## 2. Current canonical runtime surfaces",
    "## 3. W_e to kernel mapping",
    "## 4. Doctrine versus law classification",
    "## 5. Final disposition",
)
REQUIRED_TOKENS = (
    "w_e_traceability_702_complete",
    "w_e_formula_preserved_as_doctrine_not_binding_law",
    "w_e_four_component_kernel_mapping_recorded",
    "w_e_runtime_implications_mapped_without_formula_ratification",
    "w_e_disposition=doctrine_lock",
)
PHASE_702_SUBJECT = ("phase 702", "w_e traceability and doctrine classification")
PHASE_702_BACKFILL_SUBJECT = ("phase 702", "walkthrough", "backfill")
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
    raise AssertionError("phase_702_commit_not_present_in_local_history")


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


def test_artifact_records_current_four_component_kernel_slots() -> None:
    text = _read(ARTIFACT_PATH)
    assert "`reuse`" in text
    assert "`contradiction_resilience`" in text
    assert "`validation_integrity`" in text
    assert "`path_uplift`" in text


def test_artifact_distinguishes_formula_from_current_runtime_binding() -> None:
    text = _read(ARTIFACT_PATH)
    assert "not a machine-enforced formula contract" in text
    assert "No new constitutional formula-binding is created by this note." in text


def test_artifact_maps_runtime_surfaces_without_overclaiming_law() -> None:
    text = _read(ARTIFACT_PATH)
    assert "freshness / temporal-decay gate" in text
    assert "epoch-boundary ECU-to-ILC conversion pipeline" in text
    assert "four-component heuristic kernel" in text


def test_decision_log_and_runtime_paths_remain_unmutated_in_this_phase() -> None:
    main_commit = _try_resolve_commit_ref(PHASE_702_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    backfill_commit = _try_resolve_commit_ref(
        PHASE_702_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS
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


def test_phase_702_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_702_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_702_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_702_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
