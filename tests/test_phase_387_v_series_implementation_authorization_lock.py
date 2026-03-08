"""Contract tests for Phase 387 V-series implementation authorization lock artifact."""

from __future__ import annotations

from pathlib import Path
import subprocess


ARTIFACT_PATH = Path("docs/specs/ilc_v_series_implementation_authorization_lock_387_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SUBJECT_TOKEN = "docs(g8): phase 387 v-series implementation authorization lock"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_artifact_exists_and_contains_required_headings() -> None:
    assert ARTIFACT_PATH.exists()
    text = _read(ARTIFACT_PATH)
    for heading in (
        "## 1. Scope and authority boundary",
        "## 2. Inputs and constitutional carry-forward",
        "## 3. Single-source-of-truth declaration",
        "## 4. Authorized runtime target paths for phases 388/389",
        "## 5. Dependency token and version lock",
        "## 6. Mutation scope restrictions for runtime phases",
        "## 7. CDL-V3/V7 deferral and SIM-006 evidence linkage",
        "## 8. Conflict resolution and forward boundary",
        "## 9. Non-goals and immutable boundaries",
    ):
        assert heading in text


def test_artifact_contains_required_authority_and_dependency_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in (
        "This is the single source of truth for CDL-V1/V2 implementation authorization.",
        "If Phase 378 and Phase 387 conflict on exact target paths or dependency token values, Phase 387 governs.",
        'CDL_V1_DEPENDENCY = "cdl_v1_temporal_decay_388.v0.1"',
        'CDL_V2_DEPENDENCY = "cdl_v2_sybil_resistance_389.v0.1"',
        "CDL-V3 and CDL-V7 remain requires_additional_governance_input. SIM-006 results (Phase 386) are available for governance review. CDL-V3/V7 governance resolution is deferred to Window 392+ where capsule v1.3 section on CDL-V3/V7 readiness provides the authoritative declaration.",
        "Mutation scope for Phases 388/389 forbids: ilc_core/consensus/, ilc_core/security/, ilc_core/ledger/, ilc_core/issuance/, ilc_core/schema/, ilc_core/genesis/, ilc_core/epoch/, ilc_core/network/, ilc_core/node/.",
        "Phase 387 is non-sensitive and planning/authorization-only.",
        "No decision-log mutation occurred. No ilc_core runtime files were changed.",
    ):
        assert token in text


def test_authorized_runtime_target_paths_are_explicit_for_v1_and_v2() -> None:
    text = _read(ARTIFACT_PATH)
    for token in (
        "`ilc_core/reputation/__init__.py`",
        "`ilc_core/reputation/temporal_decay_runtime.py`",
        "`ilc_core/identity/__init__.py`",
        "`ilc_core/identity/sybil_resistance_runtime.py`",
    ):
        assert token in text


def test_forbidden_prefixes_and_runtime_scope_constraints_are_explicit() -> None:
    text = _read(ARTIFACT_PATH)
    for token in (
        "ilc_core/consensus/",
        "ilc_core/security/",
        "ilc_core/ledger/",
        "ilc_core/issuance/",
        "ilc_core/schema/",
        "ilc_core/genesis/",
        "ilc_core/epoch/",
        "ilc_core/network/",
        "ilc_core/node/",
        "Phases 388/389 must use custom runtime mutation-scope asserters.",
        "Phases 388/389 must not use `assert_head_commit_touched_no_runtime_files`.",
    ):
        assert token in text


def test_v3_v7_deferral_and_sim_006_linkage_present() -> None:
    text = _read(ARTIFACT_PATH)
    assert "CDL-V3 and CDL-V7 remain requires_additional_governance_input." in text
    assert "SIM-006 results (Phase 386) are available for governance review." in text


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_387_commit_ref_or_fail() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )

    matching_commits: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip().lower() == SUBJECT_TOKEN.lower():
            matching_commits.append(commit_hash)

    required_paths = {
        "docs/specs/ilc_v_series_implementation_authorization_lock_387_v0.1.md",
        "tests/test_phase_387_v_series_implementation_authorization_lock.py",
    }
    for commit_ref in matching_commits:
        changed = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed):
            return commit_ref

    if matching_commits:
        raise AssertionError(
            "phase_387_commit_subject_present_but_no_qualifying_authorization_lock_commit"
        )
    raise AssertionError("phase_387_commit_not_present_in_local_history")


def test_phase_387_commit_touched_required_paths_and_not_decision_log() -> None:
    commit_ref = _resolve_phase_387_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_phase_387_commit_touched_no_ilc_core_paths() -> None:
    commit_ref = _resolve_phase_387_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_387_runtime_mutations:{forbidden}"
