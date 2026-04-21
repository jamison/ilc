from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path(
    "docs/specs/ilc_cdl_017_interaction_synthesis_and_activation_boundary_record_764_v0.1.md"
)
TEST_PATH = Path(
    "tests/test_phase_764_cdl_017_interaction_synthesis_and_activation_boundary_record.py"
)
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_764_g8_cdl_017_interaction_synthesis_and_activation_boundary_record_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_763_TEST_PATH = Path("tests/test_phase_763_window_763_766_sequence_lock.py")
CW6_TEST_PATH = Path("tests/test_cw6_convergence_window_closure_gate.py")
REQUIRED_HEADINGS = (
    "## 1. Purpose and authority order",
    "## 2. Explicit interaction matrix",
    "## 3. Activation-boundary record",
    "## 4. Consumed evidence inputs and dossier-question dispositions",
    "## 5. Phase 765 handoff constraints",
    "## 6. Source inputs",
)
REQUIRED_TOKENS = (
    "cdl_017_interaction_synthesis_764_complete",
    "cdl_055_carry_forward_verdict_unchanged_under_cdl_017",
    "cdl_056_carry_forward_verdict_unchanged_under_cdl_017",
    "cdl_068_adjacent_lane_carry_forward_unchanged_under_cdl_017",
    "sec_004_post_ratification_activation_scope_reaffirmed",
    "activation_boundary_record_764_complete",
    "state_at_ratification_genesis_only_hooks_unimplemented_no_non_genesis_validators",
    "ratification_opens_validator_governance_lane_only",
    "hooks_remain_disabled_until_separate_activation_work",
    "first_non_genesis_deployment_requires_human_gate_after_ratification",
    "phase_755_dossier_questions_consumed_not_rederived",
    "bootstrap_transition_criteria_scope_named_from_opening_and_dossier",
    "genesis_sunset_trigger_scope_named_from_opening_and_dossier",
    "dynamic_validator_set_activation_boundary_named_from_dossier_and_m_series_lane",
    "no_decision_log_mutation_in_phase_764",
)
PHASE_MAIN_SUBJECT = ("phase 764", "cdl-017 interaction synthesis", "activation-boundary")
PHASE_BACKFILL_SUBJECT = ("phase 764", "walkthrough", "planning backfill")
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
    str(PHASE_763_TEST_PATH),
    str(CW6_TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
    str(PLANNING_INDEX_PATH),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split())


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
    raise AssertionError("phase_764_commit_not_present_in_local_history")


def test_artifact_exists_and_contains_required_headings_in_order() -> None:
    text = _read(ARTIFACT_PATH)
    positions = [text.index(heading) for heading in REQUIRED_HEADINGS]
    assert positions == sorted(positions)


def test_artifact_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_carry_forward_matrix_has_explicit_verdicts_for_cdl_055_and_cdl_056() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "| `CDL-055` | **carried forward unchanged** |" in text
    assert "| `CDL-056` | **carried forward unchanged** |" in text
    assert "`CDL-017` does not alter validator participation stake, liveness penalties, equivocation slash boundary, or the separate re-admission boundary." in text
    assert "`CDL-017` does not alter the non-inheritable trust-tier flag, its liveness-threshold tie to `CDL-055`, or the bounded consensus-dispute tiebreaker." in text
    assert "No amendment text is proposed in Phase `764`." in text


def test_activation_boundary_record_states_pre_ratification_and_post_ratification_boundaries() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "Genesis-only validator authority remains operative for the near-term testnet" in text
    assert "no non-Genesis validator has been admitted by constitutional act alone" in text
    assert "`admit_validator` is `unimplemented!`" in text
    assert "`eject_validator` is `unimplemented!`" in text
    assert "`SEC-004` is not yet implemented" in text
    assert "validator admission and ejection become a ratified governed protocol action" in text
    assert "This is the constitutional opening of the validator-governance lane only." in text


def test_artifact_explicitly_states_what_does_not_change_automatically() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "Ratification does **not** automatically do any of the following:" in text
    assert "activate the M-007 `admit_validator` / `eject_validator` hooks" in text
    assert "implement `SEC-004`" in text
    assert "authorize the first non-Genesis validator deployment without a later human gate" in text
    assert "rewrite `CDL-055`" in text
    assert "rewrite `CDL-056`" in text
    assert "rewrite `CDL-068`" in text


def test_q1_q6_and_phase_755_dossier_are_consumed_not_rederived() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "Phase `764` consumes the committed prelock block rather than re-deriving it" in text
    assert "derived-sub-key with provable linkage" in text
    assert "threshold-gated eligibility" in text
    assert "Validation pools remain outside `CDL-017` core" in text
    assert "Epoch-hash posture and the named VRF-upgrade trigger are already explicit" in text
    assert "`validator_cluster_id` diversity language and the committed full-pass `SIM-TOPOLOGY-01` thresholds" in text


def test_phase_755_dossier_question_dispositions_are_explicit() -> None:
    text = _normalized(_read(ARTIFACT_PATH))
    assert "| Bootstrap-transition criteria | **Resolved in scope.**" in text
    assert "| Genesis-sunset trigger scope | **Resolved in scope.**" in text
    assert "| Dynamic validator-set activation boundary | **Named explicitly.**" in text
    assert "The questions are answered at the law-and-boundary level" in text


def test_no_decision_log_or_runtime_mutation_in_phase_764_main_commit() -> None:
    commit_ref = _resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path == "ilc_core" or path.startswith("ilc_core/") for path in changed_paths)
    assert not any(
        path == "ilc_consensus" or path.startswith("ilc_consensus/")
        for path in changed_paths
    )


def test_phase_764_backfill_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path == "ilc_core" or path.startswith("ilc_core/") for path in changed_paths)
    assert not any(
        path == "ilc_consensus" or path.startswith("ilc_consensus/")
        for path in changed_paths
    )


def test_backfill_surfaces_advance_active_window_state() -> None:
    status_text = _normalized(_read(STATUS_PATH))
    planning_text = _normalized(_read(PLANNING_INDEX_PATH))
    walkthrough_text = _normalized(_read(WALKTHROUGH_PATH))
    assert "## Phase 764" in status_text
    assert "CDL-017 interaction synthesis and activation-boundary record" in status_text
    assert "**Next planned phase:** Phase 765" in status_text
    assert (
        "`CDL-017` ratification window ACTIVE through Phase `764`" in planning_text
        or "`CDL-017` ratification window ACTIVE through Phase `765`" in planning_text
    )
    assert "CDL-017 Interaction Synthesis" in planning_text
    assert "explicit carry-forward matrix for `CDL-055` and `CDL-056`" in walkthrough_text
