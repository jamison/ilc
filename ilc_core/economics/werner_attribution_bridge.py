# SPDX-License-Identifier: AGPL-3.0-only
"""CDL-109 Werner reweighting for CDL-108 raw path scores."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, localcontext

from ilc_core.economics.werner_runtime import compute_flow_budget


WERNER_CDL_109_VERSION = "cdl_109_werner_flow_governor_economic_bridge_GAP_WERNER_02a.v0.1"
WERNER_BRIDGE_VERSION = "werner_attribution_bridge_02b.v0.1"
WERNER_BRIDGE_SCOPE = "cdl_108_backward_attribution_only_v1"
WERNER_ATTRIBUTION_FORMULA = "raw_path_score * (Decimal('1') + flow_budget)"
WERNER_APPLICATION_STAGE = "pre_normalization"
WERNER_CONTEXT_ABSENT_TOKEN = "werner_context_absent_no_reweight"
RUNTIME_POLICY_CAP = Decimal("0.10")
WERNER_RUNTIME_POLICY_CAP = RUNTIME_POLICY_CAP
ZERO = Decimal("0")
ONE = Decimal("1")
_BINARY64_TYPE = type(0.0)


@dataclass(frozen=True)
class WernerAttributionContext:
    """Prepared same-epoch Werner context for one recipient agent."""

    agent_id: str
    epoch: int
    raw_werner_pressure: Decimal | None


@dataclass(frozen=True)
class WernerAttributionMultiplier:
    """Inspectable CDL-109 multiplier evidence for one attribution score."""

    cdl_version: str
    bridge_scope: str
    application_stage: str
    formula: str
    agent_id: str
    epoch: int
    raw_werner_pressure: Decimal | None
    flow_budget: Decimal
    multiplier: Decimal
    context_present: bool
    disposition_token: str | None


def _require_non_empty_string(value: object, token: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(token)
    return value.strip()


def _require_non_negative_int(value: object, token: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(token)
    return value


def _require_decimal(value: object, token: str) -> Decimal:
    if isinstance(value, bool) or type(value) is _BINARY64_TYPE:
        raise ValueError(token)
    if not isinstance(value, Decimal):
        raise ValueError(token)
    if not value.is_finite():
        raise ValueError(token)
    return value


def _absent_multiplier(*, agent_id: str, event_epoch: int) -> WernerAttributionMultiplier:
    return WernerAttributionMultiplier(
        cdl_version=WERNER_CDL_109_VERSION,
        bridge_scope=WERNER_BRIDGE_SCOPE,
        application_stage=WERNER_APPLICATION_STAGE,
        formula=WERNER_ATTRIBUTION_FORMULA,
        agent_id=agent_id,
        epoch=event_epoch,
        raw_werner_pressure=None,
        flow_budget=ZERO,
        multiplier=ONE,
        context_present=False,
        disposition_token=WERNER_CONTEXT_ABSENT_TOKEN,
    )


def compute_werner_multiplier(
    context: WernerAttributionContext | None,
    *,
    recipient_agent_id: str,
    event_epoch: int,
    runtime_policy_cap: Decimal = RUNTIME_POLICY_CAP,
) -> WernerAttributionMultiplier:
    """Return the CDL-109 multiplier for a recipient agent.

    Missing context is a no-op reweight with a named disposition token. Present
    context must be same-epoch, agent-bound, Decimal-only evidence.
    """

    agent_id = _require_non_empty_string(
        recipient_agent_id,
        "werner_recipient_agent_id_required",
    )
    normalized_epoch = _require_non_negative_int(
        event_epoch,
        "werner_event_epoch_must_be_non_negative_int",
    )
    cap = _require_decimal(
        runtime_policy_cap,
        "werner_runtime_policy_cap_must_be_decimal",
    )
    if cap != WERNER_RUNTIME_POLICY_CAP:
        raise ValueError("werner_runtime_policy_cap_must_match_cdl109")
    if context is None:
        return _absent_multiplier(agent_id=agent_id, event_epoch=normalized_epoch)
    if not isinstance(context, WernerAttributionContext):
        raise ValueError("werner_context_must_be_prepared_context")

    context_agent_id = _require_non_empty_string(
        context.agent_id,
        "werner_context_agent_id_required",
    )
    if context_agent_id != agent_id:
        raise ValueError("werner_context_agent_id_mismatch")
    context_epoch = _require_non_negative_int(
        context.epoch,
        "werner_context_epoch_must_be_non_negative_int",
    )
    if context_epoch != normalized_epoch:
        raise ValueError("werner_context_epoch_must_match_event_epoch")
    if context.raw_werner_pressure is None:
        return _absent_multiplier(agent_id=agent_id, event_epoch=normalized_epoch)
    if (
        isinstance(context.raw_werner_pressure, Decimal)
        and not context.raw_werner_pressure.is_finite()
    ):
        return _absent_multiplier(agent_id=agent_id, event_epoch=normalized_epoch)

    raw_pressure = _require_decimal(
        context.raw_werner_pressure,
        "werner_raw_pressure_must_be_decimal",
    )
    flow_budget = compute_flow_budget(raw_pressure, cap)
    with localcontext() as ctx:
        ctx.prec = 50
        multiplier = ONE + flow_budget
    return WernerAttributionMultiplier(
        cdl_version=WERNER_CDL_109_VERSION,
        bridge_scope=WERNER_BRIDGE_SCOPE,
        application_stage=WERNER_APPLICATION_STAGE,
        formula=WERNER_ATTRIBUTION_FORMULA,
        agent_id=agent_id,
        epoch=normalized_epoch,
        raw_werner_pressure=raw_pressure,
        flow_budget=flow_budget,
        multiplier=multiplier,
        context_present=True,
        disposition_token=None,
    )


def apply_werner_to_raw_score(
    raw_path_score: Decimal,
    context: WernerAttributionContext | None,
    *,
    recipient_agent_id: str,
    event_epoch: int,
) -> tuple[Decimal, WernerAttributionMultiplier]:
    """Apply CDL-109 before CDL-108 normalization."""

    raw_score = _require_decimal(
        raw_path_score,
        "werner_raw_path_score_must_be_decimal",
    )
    if raw_score < ZERO:
        raise ValueError("werner_raw_path_score_must_be_non_negative")
    multiplier = compute_werner_multiplier(
        context,
        recipient_agent_id=recipient_agent_id,
        event_epoch=event_epoch,
    )
    with localcontext() as ctx:
        ctx.prec = 50
        return raw_score * multiplier.multiplier, multiplier
