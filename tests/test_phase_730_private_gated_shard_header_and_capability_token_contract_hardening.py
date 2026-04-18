from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_private_gated_shard_header_and_capability_token_contract_hardening_730_v0.1.md")
TEST_PATH = Path(
    "tests/test_phase_730_private_gated_shard_header_and_capability_token_contract_hardening.py"
)
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_730_g8_private_gated_shard_header_and_capability_token_contract_hardening_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Baseline",
    "## 2. Minimum public header surface",
    "## 3. Access-right reference model",
    "## 4. Promotion and lineage continuity",
    "## 5. Deferred implementation and constitutional questions",
    "## 6. Non-goals",
    "## 7. Source inputs",
)
REQUIRED_TOKENS = (
    "private_gated_header_minimum_surface_hardened_for_planning",
    "capability_token_reference_model_bounded_for_planning",
    "private_to_public_promotion_continuity_preserved",
    "no_runtime_mutation_in_phase_730",
    "no_new_cdl_recommended_in_phase_730",
)
PHASE_MAIN_SUBJECT = ("phase 730", "private gated header", "capability contract hardening")
PHASE_BACKFILL_SUBJECT = ("phase 730", "walkthrough", "backfill")
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
    raise AssertionError("phase_730_commit_not_present_in_local_history")


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


def test_artifact_records_minimum_public_header_surface() -> None:
    text = _read(ARTIFACT_PATH)
    assert "`shard_id`" in text
    assert "`creator_agent_id`" in text
    assert "`root_commitment_ref`" in text
    assert "`access_model`" in text
    assert "enough public surface to prove existence, anchoring, continuity, and\n  navigability" in text


def test_artifact_records_access_right_reference_model() -> None:
    text = _read(ARTIFACT_PATH)
    assert "`access_grant_id`" in text
    assert "`target_shard_id`" in text
    assert "`valid_from_epoch`" in text
    assert "`payment_ref`" in text
    assert "the protocol needs a place to point to access rights" in text


def test_artifact_records_promotion_continuity_and_deferred_items() -> None:
    text = _read(ARTIFACT_PATH)
    assert "no automatic public corroboration carry-forward" in text
    assert "no automatic public reputation carry-forward" in text
    assert "shard formation remains an explicit shard-lifecycle event" in text
    assert "runtime implementation of capability-token custody and validation" in text
    assert "any new CDL opening tied to this lane" in text


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


def test_phase_730_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_730_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
