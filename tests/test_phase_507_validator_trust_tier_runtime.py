from __future__ import annotations

import importlib
import subprocess
from pathlib import Path

from ilc_core.validator import staking_liveness_runtime
from ilc_core.validator import trust_tier_runtime

MODULE_PATH = Path("ilc_core/validator/trust_tier_runtime.py")
TEST_PATH = Path("tests/test_phase_507_validator_trust_tier_runtime.py")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_507_SUBJECT_TOKEN = "phase 507 cdl-056 validator trust-tier runtime"
EXACT_REQUIRED_MAIN_PATHS = {
    str(MODULE_PATH),
    str(TEST_PATH),
}
FORBIDDEN_PREFIXES = (
    "ilc_core/consensus/",
    "ilc_core/security/",
    "ilc_core/ledger/",
    "ilc_core/issuance/",
    "ilc_core/schema/",
    "ilc_core/genesis/",
    "ilc_core/epoch/",
    "ilc_core/d2e/",
    "ilc_core/cli/",
    "ilc_core/identity/",
    "ilc_core/reputation/",
    "ilc_core/network/",
    "ilc_core/node/",
)
FORBIDDEN_CHANGED_PATHS = {
    "ilc_core/validator/__init__.py",
    "ilc_core/validator/staking_liveness_runtime.py",
}


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_507_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if PHASE_507_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError("phase_507_commit_subject_present_but_no_qualifying_runtime_commit")
    raise AssertionError("phase_507_commit_not_present_in_local_history")


def test_module_imports_and_runtime_exports() -> None:
    module = importlib.import_module("ilc_core.validator.trust_tier_runtime")
    assert module.TRUST_TIER_RUNTIME_VERSION == "trust_tier_runtime_507.v0.1"
    assert hasattr(module, "revoke_trust_tier_if_below_threshold")


def test_cdl_056_dependency_constant_value() -> None:
    assert trust_tier_runtime.CDL_056_DEPENDENCY == "cdl_056_ratified_501.v0.1"


def test_cdl_055_staking_dependency_chain() -> None:
    assert (
        trust_tier_runtime.CDL_055_STAKING_DEPENDENCY
        == staking_liveness_runtime.STAKING_LIVENESS_RUNTIME_VERSION
    )


def test_consensus_dispute_types_match_contract() -> None:
    assert trust_tier_runtime.CONSENSUS_DISPUTE_TYPES == frozenset(
        ("block_proposal", "equivocation", "fork_choice")
    )


def test_is_trust_tier_eligible_returns_true_for_passing_inputs() -> None:
    assert trust_tier_runtime.is_trust_tier_eligible(0, 8, False) is True


def test_is_trust_tier_eligible_returns_false_for_liveness_failure() -> None:
    assert trust_tier_runtime.is_trust_tier_eligible(8, 8, False) is False


def test_is_trust_tier_eligible_returns_false_for_unresolved_equivocation() -> None:
    assert trust_tier_runtime.is_trust_tier_eligible(0, 8, True) is False


def test_revoke_trust_tier_if_below_threshold_revokes_failing_validator() -> None:
    assert trust_tier_runtime.revoke_trust_tier_if_below_threshold(True, 8, 8) is False


def test_apply_consensus_dispute_tiebreaker_accepts_consensus_types() -> None:
    candidates = [
        {"validator_id": "v1", "trust_tier": False},
        {"validator_id": "v2", "trust_tier": True},
    ]
    for dispute_type in trust_tier_runtime.CONSENSUS_DISPUTE_TYPES:
        result = trust_tier_runtime.apply_consensus_dispute_tiebreaker(dispute_type, candidates)
        assert result == {"validator_id": "v2", "trust_tier": True}


def test_apply_consensus_dispute_tiebreaker_raises_for_governance_vote() -> None:
    try:
        trust_tier_runtime.apply_consensus_dispute_tiebreaker("governance_vote", [])
    except ValueError as exc:
        assert str(exc) == "non_consensus_dispute_type"
    else:
        raise AssertionError("expected ValueError for non-consensus dispute type")


def test_phase_507_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_507_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_507_main_commit_respects_scope_and_cdl_log() -> None:
    commit_ref = _resolve_phase_507_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not FORBIDDEN_CHANGED_PATHS.intersection(changed_paths)
    assert all(
        not any(path.startswith(prefix) for prefix in FORBIDDEN_PREFIXES)
        for path in changed_paths
    )
