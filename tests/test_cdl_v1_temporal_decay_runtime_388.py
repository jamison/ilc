from __future__ import annotations

import subprocess
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.reputation.temporal_decay_runtime import (
    CDL_V1_DECIMAL_REWRITE_TOKEN,
    CDL_V1_DEPENDENCY,
    CDL_V1_RUNTIME_VERSION,
    TemporalDecayValidationError,
    apply_temporal_decay,
    compute_decay_multiplier,
)


RUNTIME_INIT_PATH = Path("ilc_core/reputation/__init__.py")
RUNTIME_PATH = Path("ilc_core/reputation/temporal_decay_runtime.py")
HANDOFF_PATH = Path("docs/specs/ilc_cdl_v1_temporal_decay_runtime_handoff_388_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SUBJECT_TOKEN = "feat(g8): phase 388 cdl-v1 temporal decay runtime"

AUTHORIZED_RUNTIME_PATHS = {
    "ilc_core/reputation/__init__.py",
    "ilc_core/reputation/temporal_decay_runtime.py",
}
FORBIDDEN_PREFIXES = (
    "ilc_core/consensus/",
    "ilc_core/security/",
    "ilc_core/ledger/",
    "ilc_core/issuance/",
    "ilc_core/schema/",
    "ilc_core/genesis/",
    "ilc_core/epoch/",
    "ilc_core/network/",
    "ilc_core/node/",
)


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_388_commit_ref_or_fail() -> str:
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
        "ilc_core/reputation/__init__.py",
        "ilc_core/reputation/temporal_decay_runtime.py",
        "docs/specs/ilc_cdl_v1_temporal_decay_runtime_handoff_388_v0.1.md",
        "tests/test_cdl_v1_temporal_decay_runtime_388.py",
    }

    for commit_ref in matching_commits:
        changed = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_388_commit_subject_present_but_no_runtime_commit")
    raise AssertionError("phase_388_commit_not_present_in_local_history")


def _assert_v_series_mutation_scope(commit_ref: str) -> None:
    changed = _changed_paths_for_commit(commit_ref)

    assert DECISION_LOG_PATH not in changed
    assert any(path in changed for path in AUTHORIZED_RUNTIME_PATHS), "phase_388_authorized_runtime_missing"

    forbidden = [path for path in changed if path.startswith(FORBIDDEN_PREFIXES)]
    assert not forbidden, f"phase_388_forbidden_prefix_mutation:{forbidden}"

    unexpected_ilc_core = [
        path
        for path in changed
        if path.startswith("ilc_core/") and path not in AUTHORIZED_RUNTIME_PATHS
    ]
    assert not unexpected_ilc_core, f"phase_388_ilc_core_scope_violation:{unexpected_ilc_core}"


def test_runtime_paths_and_constants_exist() -> None:
    assert RUNTIME_INIT_PATH.exists()
    assert RUNTIME_PATH.exists()
    assert CDL_V1_RUNTIME_VERSION == "cdl_v1_temporal_decay_runtime_388.v0.1"
    assert CDL_V1_DEPENDENCY == "cdl_v1_temporal_decay_388.v0.1"
    assert CDL_V1_DECIMAL_REWRITE_TOKEN == "temporal_decay_no_float_arithmetic_phase_1357"


def test_decay_multiplier_zero_elapsed_is_one() -> None:
    assert compute_decay_multiplier(
        elapsed_issuance_epochs=Decimal("0"),
        half_life_epochs=Decimal("4"),
        floor_multiplier=Decimal("0.2"),
    ) == Decimal("1")


def test_decay_multiplier_half_life_boundary() -> None:
    actual = compute_decay_multiplier(
        elapsed_issuance_epochs=Decimal("8"),
        half_life_epochs=Decimal("8"),
        floor_multiplier=Decimal("0"),
    )
    assert actual == Decimal("0.500000000000")


def test_decay_multiplier_floor_enforcement() -> None:
    actual = compute_decay_multiplier(
        elapsed_issuance_epochs=Decimal("100"),
        half_life_epochs=Decimal("2"),
        floor_multiplier=Decimal("0.31"),
    )
    assert actual == Decimal("0.310000000000")


def test_apply_temporal_decay_nominal_case() -> None:
    decayed = apply_temporal_decay(
        base_ecu_score=Decimal("10"),
        elapsed_issuance_epochs=Decimal("4"),
        half_life_epochs=Decimal("8"),
        floor_multiplier=Decimal("0"),
    )
    assert decayed == Decimal("7.071067811870")


def test_apply_temporal_decay_issuance_epoch_guard() -> None:
    with pytest.raises(TemporalDecayValidationError) as exc:
        apply_temporal_decay(
            base_ecu_score=Decimal("10"),
            elapsed_issuance_epochs=Decimal("1"),
            half_life_epochs=Decimal("8"),
            floor_multiplier=Decimal("0"),
            epoch_type="validation_epoch",
        )
    assert exc.value.token == "cdl_v1_temporal_decay_epoch_context_invalid"


def test_half_life_must_be_positive() -> None:
    with pytest.raises(TemporalDecayValidationError) as exc:
        compute_decay_multiplier(
            elapsed_issuance_epochs=Decimal("1"),
            half_life_epochs=Decimal("0"),
            floor_multiplier=Decimal("0"),
        )
    assert exc.value.token == "cdl_v1_temporal_decay_half_life_non_positive"


def test_floor_must_be_within_unit_interval() -> None:
    with pytest.raises(TemporalDecayValidationError) as exc:
        compute_decay_multiplier(
            elapsed_issuance_epochs=Decimal("1"),
            half_life_epochs=Decimal("8"),
            floor_multiplier=Decimal("1.2"),
        )
    assert exc.value.token == "cdl_v1_temporal_decay_floor_out_of_range"


def test_non_finite_numeric_inputs_raise_tokenized_error() -> None:
    for invalid in (Decimal("NaN"), Decimal("Infinity"), Decimal("-Infinity")):
        with pytest.raises(TemporalDecayValidationError) as exc:
            compute_decay_multiplier(
                elapsed_issuance_epochs=invalid,
                half_life_epochs=Decimal("8"),
                floor_multiplier=Decimal("0.2"),
            )
        assert exc.value.token == "cdl_v1_temporal_decay_invalid_numeric"

    for invalid in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(TemporalDecayValidationError) as exc:
            apply_temporal_decay(
                base_ecu_score=Decimal("10"),
                elapsed_issuance_epochs=Decimal("1"),
                half_life_epochs=invalid,
                floor_multiplier=Decimal("0.2"),
            )
        assert exc.value.token == "cdl_v1_temporal_decay_invalid_numeric"


def test_base_score_must_be_non_negative() -> None:
    with pytest.raises(TemporalDecayValidationError) as exc:
        apply_temporal_decay(
            base_ecu_score=Decimal("-1"),
            elapsed_issuance_epochs=Decimal("1"),
            half_life_epochs=Decimal("8"),
            floor_multiplier=Decimal("0"),
        )
    assert exc.value.token == "cdl_v1_temporal_decay_negative_base_score"


def test_handoff_artifact_has_required_headings_and_tokens() -> None:
    assert HANDOFF_PATH.exists()
    text = HANDOFF_PATH.read_text(encoding="utf-8")
    for heading in (
        "## 1. Implementation scope summary",
        "## 2. Dependency/version lock section",
        "## 3. Issuance-epoch temporal-decay model statement",
        "## 4. Deterministic failure-token catalog",
        "## 5. Mutation-scope boundary statement",
        "## 6. Carry-forward constraints for Phase 389",
        "## 7. Non-goals",
    ):
        assert heading in text

    for token in (
        'CDL_V1_DEPENDENCY = "cdl_v1_temporal_decay_388.v0.1"',
        "CDL-V1 temporal decay enforcement is issuance-epoch scoped.",
        "Phase 388 uses Phase-387 authorization targets as binding scope.",
        "No decision-log mutation occurred in Phase 388.",
    ):
        assert token in text


def test_phase_388_commit_runtime_scope_guard() -> None:
    commit_ref = _resolve_phase_388_commit_ref_or_fail()
    _assert_v_series_mutation_scope(commit_ref)


def test_phase_388_commit_no_decision_log_mutation() -> None:
    commit_ref = _resolve_phase_388_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed
