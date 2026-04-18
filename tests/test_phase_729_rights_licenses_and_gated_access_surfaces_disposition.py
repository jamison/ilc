from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_rights_licenses_and_gated_access_surfaces_disposition_729_v0.1.md")
TEST_PATH = Path("tests/test_phase_729_rights_licenses_and_gated_access_surfaces_disposition.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_729_g8_rights_licenses_and_gated_access_surfaces_disposition_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Baseline",
    "## 2. Rights and licensing treatment",
    "## 3. Layer assignment",
    "## 4. Dispute and adjudication posture",
    "## 5. Deferred implementation surfaces",
    "## 6. Non-goals",
    "## 7. Source inputs",
)
REQUIRED_TOKENS = (
    "rights_licensing_not_collapsed_into_refutation_criterion",
    "gated_access_layer_assignment_locked_for_727_732",
    "l1_l2_l3_boundary_for_gated_access_recorded",
    "rights_dispute_surface_not_yet_ratified",
    "no_financial_shard_activation_in_phase_729",
)
PHASE_MAIN_SUBJECT = ("phase 729", "rights licenses and gated access disposition")
PHASE_BACKFILL_SUBJECT = ("phase 729", "walkthrough", "backfill")
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
    raise AssertionError("phase_729_commit_not_present_in_local_history")


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


def test_artifact_records_rights_treatment_not_refutation() -> None:
    text = _read(ARTIFACT_PATH)
    assert "Rights, licensing, attribution conditions, and access conditions are not the\nsame thing as epistemic refutation." in text
    assert "metadata," in text
    assert "provenance," in text
    assert "contract surfaces," in text
    assert "dispute/adjudication surfaces." in text


def test_artifact_records_layer_assignment() -> None:
    text = _read(ARTIFACT_PATH)
    assert "**L1 / public anchor layer**" in text
    assert "**Gated/private shard contract layer**" in text
    assert "**L2/L3 business-logic layer**" in text
    assert "creator identity / attribution anchor" in text
    assert "minimal header surface" in text
    assert "recurring billing logic" in text


def test_artifact_records_dispute_posture_and_deferred_surfaces() -> None:
    text = _read(ARTIFACT_PATH)
    assert "false attribution" in text
    assert "false claim of exclusive rights" in text
    assert "does not ratify a new rights\ncontract" in text
    assert "a dedicated rights-dispute contract" in text
    assert "runtime capability-token implementation" in text


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
        ["git", "diff", "--cached", "--name-only", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert not result_decision.stdout.strip()


def test_phase_729_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_729_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
