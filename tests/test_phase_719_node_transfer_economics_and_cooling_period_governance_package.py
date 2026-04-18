from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path(
    "docs/specs/ilc_node_transfer_economics_and_cooling_period_governance_package_719_v0.1.md"
)
TEST_PATH = Path(
    "tests/test_phase_719_node_transfer_economics_and_cooling_period_governance_package.py"
)
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_719_g8_node_transfer_economics_and_cooling_period_governance_package_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Baseline",
    "## 2. Transfer-tax structure",
    "## 3. Cooling-period duration class",
    "## 4. Launch-bound versus deferred posture",
    "## 5. Preserved invariants and non-goals",
)
REQUIRED_TOKENS = (
    "visible_taxed_transfer_principle_preserved",
    "cooling_period_duration_class_selected",
    "creator_attribution_not_transferred",
    "governance_influence_not_purchased",
    "numeric_tax_and_cooling_constants_not_constitutionalized_here",
)
PHASE_MAIN_SUBJECT = ("phase 719", "node transfer economics", "cooling period package")
PHASE_BACKFILL_SUBJECT = ("phase 719", "walkthrough", "backfill")
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
    raise AssertionError("phase_719_commit_not_present_in_local_history")


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


def test_artifact_rejects_off_protocol_transfer_evasion_and_preserves_visibility() -> None:
    text = _read(ARTIFACT_PATH)
    assert (
        "Off-protocol transfer evasion is unacceptable because it recreates node trading\n"
        "outside protocol visibility, taxation, and audit." in text
    )
    assert "transfer remains protocol-visible rather than informally hidden" in text


def test_artifact_selects_epoch_duration_class_and_launch_bound_posture() -> None:
    text = _read(ARTIFACT_PATH)
    assert "Cooling period is expressed in epochs, not issuance cycles and not wall-clock\ntime." in text
    assert "Transfer tax is `launch_bound` at the principle-and-structure level." in text
    assert "Cooling period is `launch_bound` at the duration-class level" in text


def test_artifact_preserves_attribution_and_governance_boundaries() -> None:
    text = _read(ARTIFACT_PATH)
    assert "Creator attribution remains permanent and is not transferred by sale, lease, or\nportfolio movement." in text
    assert "Node portfolio size does not become protocol governance influence." in text
    assert "numeric tax brackets, exact cooling duration, and any adaptive calibration" in text


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


def test_phase_719_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_719_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
