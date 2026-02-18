from __future__ import annotations

from typing import Iterable, Mapping, TypedDict

from ilc_core.analysis.freshness_gate import (
    DEFAULT_FRESHNESS_GATE_POLICY,
    validate_freshness_gate_policy,
)
from ilc_core.analysis.genesis_accrual_governor import (
    DEFAULT_GENESIS_ACCRUAL_GOVERNOR_POLICY,
    evaluate_genesis_accrual_governor,
)
from ilc_core.analysis.node_value_conformance import (
    compute_score_rows_sha256,
    evaluate_anti_sybil_invariants,
)
from ilc_core.analysis.node_value_input_canon import NodeValueInputEvent
from ilc_core.analysis.node_value_kernel import (
    DEFAULT_EW_WEIGHTS,
    NodeScoreVector,
    build_node_evidence_vectors,
    compute_node_scores,
)
from ilc_core.analysis.reuse_diversity_invariants import (
    DEFAULT_REUSE_DIVERSITY_POLICY,
    validate_reuse_diversity_policy,
)
from ilc_core.analysis.utility_flow_rewards import (
    UtilityFlowRewardAllocation,
    evaluate_refutation_profitability_invariant,
)
from ilc_core.exceptions import (
    GenesisAccrualGovernorError,
    NodeValueKernelError,
    RewardGovernorError,
)


class ConformanceInvariantCheck(TypedDict):
    ok: bool
    skipped: bool
    errors: list[str]
    detail: dict[str, object]


class NodeValueGovernanceConformanceChecks(TypedDict):
    score_vector_schema: ConformanceInvariantCheck
    anti_sybil: ConformanceInvariantCheck
    reuse_diversity_policy: ConformanceInvariantCheck
    freshness_policy: ConformanceInvariantCheck
    refutation_profitability: ConformanceInvariantCheck
    genesis_accrual_governor: ConformanceInvariantCheck


class NodeValueGovernanceConformanceReport(TypedDict):
    contract_version: str
    score_row_count: int
    score_rows_sha256: str
    checks: NodeValueGovernanceConformanceChecks
    overall_ok: bool


_SCORE_VECTOR_REQUIRED_KEYS = {
    "node_id",
    "reuse_component",
    "contradiction_component",
    "validation_component",
    "path_component",
    "reuse_diversity_multiplier",
    "epistemic_weight",
    "freshness_gate",
    "utility_flow",
}


def _build_check(
    *,
    ok: bool,
    skipped: bool = False,
    errors: list[str] | None = None,
    detail: dict[str, object] | None = None,
) -> ConformanceInvariantCheck:
    return {
        "ok": ok,
        "skipped": skipped,
        "errors": [] if errors is None else errors,
        "detail": {} if detail is None else detail,
    }


def _validate_score_row_schema(score_rows: list[NodeScoreVector]) -> ConformanceInvariantCheck:
    errors: list[str] = []
    row_keys: list[list[str]] = []
    for row in score_rows:
        keys = sorted(row.keys())
        row_keys.append(keys)
        if set(keys) != _SCORE_VECTOR_REQUIRED_KEYS:
            errors.append(f"conformance_score_vector_schema_mismatch:{row.get('node_id', '_missing')}")

    return _build_check(
        ok=len(errors) == 0,
        errors=errors,
        detail={
            "required_keys": sorted(_SCORE_VECTOR_REQUIRED_KEYS),
            "row_keys": row_keys,
        },
    )


def _evaluate_anti_sybil(events: list[NodeValueInputEvent]) -> ConformanceInvariantCheck:
    vectors = build_node_evidence_vectors(events)
    flags = evaluate_anti_sybil_invariants(vectors)
    return _build_check(
        ok=len(flags) == 0,
        errors=flags,
        detail={
            "flag_count": len(flags),
        },
    )


def _evaluate_reuse_diversity_policy(
    reuse_diversity_policy: Mapping[str, object],
) -> ConformanceInvariantCheck:
    try:
        resolved = validate_reuse_diversity_policy(reuse_diversity_policy)
    except NodeValueKernelError as exc:
        return _build_check(
            ok=False,
            errors=[str(exc)],
        )
    return _build_check(
        ok=True,
        detail={
            "policy": dict(resolved),
        },
    )


def _evaluate_freshness_policy(
    freshness_policy: Mapping[str, object],
) -> ConformanceInvariantCheck:
    try:
        resolved = validate_freshness_gate_policy(freshness_policy)
    except NodeValueKernelError as exc:
        return _build_check(
            ok=False,
            errors=[str(exc)],
        )
    return _build_check(
        ok=True,
        detail={
            "policy": dict(resolved),
        },
    )


def _evaluate_refutation_profitability(
    reward_allocations: Iterable[UtilityFlowRewardAllocation] | None,
) -> ConformanceInvariantCheck:
    if reward_allocations is None:
        return _build_check(
            ok=True,
            skipped=True,
            detail={"reason": "conformance_missing_reward_allocations"},
        )

    try:
        check = evaluate_refutation_profitability_invariant(reward_allocations)
    except RewardGovernorError as exc:
        return _build_check(
            ok=False,
            errors=[str(exc)],
        )
    return _build_check(
        ok=bool(check["ok"]),
        errors=list(check["errors"]),
        detail={
            "compared_groups": int(check["compared_groups"]),
            "skipped_rows": int(check["skipped_rows"]),
        },
    )


def _evaluate_genesis_accrual_governor(
    genesis_signal: Mapping[str, object] | None,
    *,
    genesis_governor_policy: Mapping[str, object],
) -> ConformanceInvariantCheck:
    if genesis_signal is None:
        return _build_check(
            ok=True,
            skipped=True,
            detail={"reason": "conformance_missing_genesis_signal"},
        )

    try:
        check = evaluate_genesis_accrual_governor(
            genesis_signal,
            policy=genesis_governor_policy,
        )
    except GenesisAccrualGovernorError as exc:
        return _build_check(
            ok=False,
            errors=[str(exc)],
        )

    return _build_check(
        ok=True,
        detail={
            "genesis_share_ratio": float(check["genesis_share_ratio"]),
            "taper_multiplier": float(check["taper_multiplier"]),
            "cap_blocked": bool(check["cap_blocked"]),
        },
    )


def build_node_value_governance_conformance_report(
    events: list[NodeValueInputEvent],
    *,
    reward_allocations: Iterable[UtilityFlowRewardAllocation] | None = None,
    genesis_signal: Mapping[str, object] | None = None,
    weights: Mapping[str, float] = DEFAULT_EW_WEIGHTS,
    reuse_diversity_policy: Mapping[str, object] = DEFAULT_REUSE_DIVERSITY_POLICY,
    freshness_policy: Mapping[str, object] = DEFAULT_FRESHNESS_GATE_POLICY,
    genesis_governor_policy: Mapping[str, object] = DEFAULT_GENESIS_ACCRUAL_GOVERNOR_POLICY,
) -> NodeValueGovernanceConformanceReport:
    reuse_policy_check = _evaluate_reuse_diversity_policy(reuse_diversity_policy)
    freshness_policy_check = _evaluate_freshness_policy(freshness_policy)

    resolved_reuse_policy = (
        reuse_diversity_policy
        if reuse_policy_check["ok"]
        else DEFAULT_REUSE_DIVERSITY_POLICY
    )
    resolved_freshness_policy = (
        freshness_policy
        if freshness_policy_check["ok"]
        else DEFAULT_FRESHNESS_GATE_POLICY
    )

    if not reuse_policy_check["ok"]:
        reuse_policy_check["detail"]["fallback_policy_used_for_score_rows"] = True
    if not freshness_policy_check["ok"]:
        freshness_policy_check["detail"]["fallback_policy_used_for_score_rows"] = True

    score_rows: list[NodeScoreVector] = []
    score_schema_check: ConformanceInvariantCheck
    try:
        score_rows = compute_node_scores(
            events,
            weights=weights,
            reuse_diversity_policy=resolved_reuse_policy,
            freshness_policy=resolved_freshness_policy,
        )
        score_schema_check = _validate_score_row_schema(score_rows)
    except NodeValueKernelError as exc:
        score_schema_check = _build_check(
            ok=False,
            errors=[str(exc)],
            detail={
                "required_keys": sorted(_SCORE_VECTOR_REQUIRED_KEYS),
                "row_keys": [],
            },
        )

    checks: NodeValueGovernanceConformanceChecks = {
        "score_vector_schema": score_schema_check,
        "anti_sybil": _evaluate_anti_sybil(events),
        "reuse_diversity_policy": reuse_policy_check,
        "freshness_policy": freshness_policy_check,
        "refutation_profitability": _evaluate_refutation_profitability(reward_allocations),
        "genesis_accrual_governor": _evaluate_genesis_accrual_governor(
            genesis_signal,
            genesis_governor_policy=genesis_governor_policy,
        ),
    }

    overall_ok = all(
        check["ok"] for check in checks.values() if not check["skipped"]
    )
    return {
        "contract_version": "v0.1",
        "score_row_count": len(score_rows),
        "score_rows_sha256": compute_score_rows_sha256(score_rows),
        "checks": checks,
        "overall_ok": overall_ok,
    }


def evaluate_node_value_governance_conformance(
    events: list[NodeValueInputEvent],
    *,
    reward_allocations: Iterable[UtilityFlowRewardAllocation] | None = None,
    genesis_signal: Mapping[str, object] | None = None,
    weights: Mapping[str, float] = DEFAULT_EW_WEIGHTS,
    reuse_diversity_policy: Mapping[str, object] = DEFAULT_REUSE_DIVERSITY_POLICY,
    freshness_policy: Mapping[str, object] = DEFAULT_FRESHNESS_GATE_POLICY,
    genesis_governor_policy: Mapping[str, object] = DEFAULT_GENESIS_ACCRUAL_GOVERNOR_POLICY,
) -> NodeValueGovernanceConformanceReport:
    return build_node_value_governance_conformance_report(
        events,
        reward_allocations=reward_allocations,
        genesis_signal=genesis_signal,
        weights=weights,
        reuse_diversity_policy=reuse_diversity_policy,
        freshness_policy=freshness_policy,
        genesis_governor_policy=genesis_governor_policy,
    )
