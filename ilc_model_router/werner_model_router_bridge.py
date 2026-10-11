# SPDX-License-Identifier: AGPL-3.0-only
"""CDL-116 Werner bridge for Model Router receipt metadata.

This module computes a dimensionless Werner flow budget from local Model Router
receipt companion records. The guard was cleared by GAP-WERNER-V1-GUARD-CLEAR-00;
the branch remains as defense in depth for tests and future emergency re-disable.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, localcontext
from ilc_core.economics.werner_runtime import compute_flow_budget

from .receipt_schema import RouterCompanionRecord, RouterReceipt


WERNER_MODEL_ROUTER_NOT_ACTIVATED = False

WERNER_CDL_116_VERSION = "cdl_116_model_router_v1_ratified_GAP_CDL_MODEL_ROUTER_RATIFY_00.v0.1"
WERNER_CDL_109_BRIDGE_VERSION = "werner_model_router_bridge_GAP_WERNER_V1_RUNTIME_IMPL_00.v0.1"
WERNER_CONTEXT_ABSENT_TOKEN = "werner_model_router_context_absent_no_reweight"
WERNER_GUARD_ACTIVE_ABSENT_TOKEN = "werner_model_router_guard_active_no_reweight"

ZERO = Decimal("0")
ONE = Decimal("1")
TWELVE_PLACES = Decimal("0.000000000001")
RUNTIME_POLICY_CAP = Decimal("0.100000000000")
PER_RECEIPT_TOKEN_CAP = Decimal("20000.000000000000")
MAX_AGENT_SIGNAL = Decimal("12.000000000000")

STATUS_WEIGHTS = {
    "success": Decimal("1.00"),
    "partial": Decimal("0.25"),
    "failure": Decimal("0.00"),
    # Bridge-only mapped status for consent_status="local_only"; the SIM source
    # reaches the same zero result through CONSENT_WEIGHTS["local_only"].
    "local_only": Decimal("0.00"),
}
CONSENT_WEIGHTS = {
    "promoted": Decimal("1.00"),
    "promotion_pending": Decimal("0.00"),
    "local_only": Decimal("0.00"),
}
CAPABILITY_WEIGHTS = {
    "embedding": Decimal("0.70"),
    "inference": Decimal("1.00"),
    "multimodal": Decimal("1.10"),
    None: Decimal("1.00"),
}

NON_CLAIMS = (
    "no_ecu_mint",
    "no_ilc_settlement",
    "no_genesis_atlas_lmdb_write",
    "no_signed_AtlasSliceManifest_mutation",
    "no_capproof_stacking",
    "no_passive_ecu_quality_factor_stacking",
)


class WernerModelRouterBridgeError(ValueError):
    """Stable fail-closed bridge error."""


@dataclass(frozen=True)
class WernerModelRouterContext:
    """Inspectable CDL-116 Werner context for one Model Router agent."""

    agent_id: str
    epoch: int
    flow_budget: Decimal
    candidate_priority: Decimal
    capped_agent_signal: Decimal
    receipt_count: int
    werner_context_present: bool
    cdl_version: str
    bridge_version: str
    non_claims: tuple[str, ...]
    absent_token: str = WERNER_CONTEXT_ABSENT_TOKEN

    def __post_init__(self) -> None:
        _require_non_empty_string(self.agent_id, "werner_model_router_agent_id_required")
        _require_non_negative_int(self.epoch, "werner_model_router_epoch_must_be_non_negative_int")
        _require_non_negative_int(
            self.receipt_count,
            "werner_model_router_receipt_count_must_be_non_negative_int",
        )
        flow_budget = _require_decimal(
            self.flow_budget,
            "werner_model_router_flow_budget_must_be_decimal",
        )
        candidate_priority = _require_decimal(
            self.candidate_priority,
            "werner_model_router_candidate_priority_must_be_decimal",
        )
        capped_agent_signal = _require_decimal(
            self.capped_agent_signal,
            "werner_model_router_capped_agent_signal_must_be_decimal",
        )
        _require_non_negative_decimal(flow_budget, "werner_model_router_flow_budget")
        _require_non_negative_decimal(candidate_priority, "werner_model_router_candidate_priority")
        _require_non_negative_decimal(capped_agent_signal, "werner_model_router_capped_signal")
        if type(self.werner_context_present) is not bool:
            raise WernerModelRouterBridgeError(
                "werner_model_router_context_present_must_be_bool"
            )
        if not self.werner_context_present and flow_budget != ZERO:
            raise WernerModelRouterBridgeError("werner_absent_context_requires_zero_flow_budget")
        _require_non_empty_string(self.cdl_version, "werner_model_router_cdl_version_required")
        _require_non_empty_string(self.bridge_version, "werner_model_router_bridge_version_required")
        if type(self.non_claims) is not tuple or any(
            type(claim) is not str or not claim for claim in self.non_claims
        ):
            raise WernerModelRouterBridgeError("werner_model_router_non_claims_invalid")
        for claim in (
            "no_capproof_stacking",
            "no_passive_ecu_quality_factor_stacking",
        ):
            if claim not in self.non_claims:
                raise WernerModelRouterBridgeError(f"werner_model_router_missing_{claim}")
        _require_non_empty_string(
            self.absent_token,
            "werner_model_router_absent_token_required",
        )
        if not self.werner_context_present and self.absent_token not in self.non_claims:
            raise WernerModelRouterBridgeError("werner_absent_context_requires_absent_token")


def compute_werner_model_router_context(
    agent_id: str,
    epoch: int,
    receipts: list[RouterReceipt | RouterCompanionRecord],
) -> WernerModelRouterContext:
    """Compute the guarded CDL-116 Werner context for Model Router receipts.

    Invalid or absent context fails closed to zero budget instead of crashing a
    caller. The returned value is a dimensionless reweighting input only.
    """

    if WERNER_MODEL_ROUTER_NOT_ACTIVATED:
        fallback_agent_id = agent_id if type(agent_id) is str and agent_id.strip() else "unknown"
        fallback_epoch = epoch if type(epoch) is int and epoch >= 0 else 0
        return _absent_context(
            agent_id=fallback_agent_id,
            epoch=fallback_epoch,
            absent_token=WERNER_GUARD_ACTIVE_ABSENT_TOKEN,
        )

    try:
        normalized_agent_id = _require_non_empty_string(
            agent_id,
            "werner_model_router_agent_id_required",
        )
        normalized_epoch = _require_non_negative_int(
            epoch,
            "werner_model_router_epoch_must_be_non_negative_int",
        )
        if not isinstance(receipts, list):
            raise WernerModelRouterBridgeError("werner_model_router_receipts_must_be_list")
        if not receipts:
            return _absent_context(agent_id=normalized_agent_id, epoch=normalized_epoch)

        with localcontext() as ctx:
            ctx.prec = 50
            agent_signal = ZERO
            for receipt in receipts:
                agent_signal += _receipt_signal(receipt)
            capped_signal = min(agent_signal, MAX_AGENT_SIGNAL).quantize(TWELVE_PLACES)
            candidate_priority = (
                (capped_signal / MAX_AGENT_SIGNAL) * RUNTIME_POLICY_CAP
            ).quantize(TWELVE_PLACES)
            flow_budget = compute_flow_budget(candidate_priority, RUNTIME_POLICY_CAP)
        return WernerModelRouterContext(
            agent_id=normalized_agent_id,
            epoch=normalized_epoch,
            flow_budget=flow_budget,
            candidate_priority=candidate_priority,
            capped_agent_signal=capped_signal,
            receipt_count=len(receipts),
            werner_context_present=True,
            cdl_version=WERNER_CDL_116_VERSION,
            bridge_version=WERNER_CDL_109_BRIDGE_VERSION,
            non_claims=NON_CLAIMS,
        )
    except (InvalidOperation, ValueError, TypeError, KeyError):
        fallback_agent_id = agent_id if type(agent_id) is str and agent_id.strip() else "unknown"
        fallback_epoch = epoch if type(epoch) is int and epoch >= 0 else 0
        return _absent_context(agent_id=fallback_agent_id, epoch=fallback_epoch)


def receipt_status_from_companion(receipt: RouterCompanionRecord) -> str:
    """Map companion-only metadata into the SIM status-weight vocabulary.

    Companion records do not carry the provider result status. They can only
    prove local-only/pending/promoted consent state, so pending stays zero and
    promoted companion-only callers retain the legacy success mapping.
    """

    if not isinstance(receipt, RouterCompanionRecord):
        raise WernerModelRouterBridgeError("werner_model_router_receipt_must_be_companion")
    if receipt.consent_status in {"local_only", "promotion_pending"}:
        return "local_only"
    if receipt.consent_status == "promoted":
        return "success"
    raise WernerModelRouterBridgeError("werner_model_router_consent_status_unknown")


def _receipt_signal(receipt: RouterReceipt | RouterCompanionRecord) -> Decimal:
    companion, status_key = _signal_inputs(receipt)
    with localcontext() as ctx:
        ctx.prec = 50
        input_tokens = _coerce_non_negative_decimal(
            companion.token_counts_input,
            "token_counts_input",
        )
        output_tokens = _coerce_non_negative_decimal(
            companion.token_counts_output,
            "token_counts_output",
        )
        token_factor = min(
            input_tokens + output_tokens,
            PER_RECEIPT_TOKEN_CAP,
        ) / PER_RECEIPT_TOKEN_CAP
        signal = (
            STATUS_WEIGHTS[status_key]
            * CONSENT_WEIGHTS[companion.consent_status]
            * CAPABILITY_WEIGHTS[companion.capability_class]
            * token_factor
        ).quantize(TWELVE_PLACES)
    if signal < ZERO:
        raise WernerModelRouterBridgeError("receipt_signal_must_be_non_negative")
    return signal


def _signal_inputs(
    receipt: RouterReceipt | RouterCompanionRecord,
) -> tuple[RouterCompanionRecord, str]:
    if isinstance(receipt, RouterReceipt):
        companion = receipt.companion
        if companion.consent_status in {"local_only", "promotion_pending"}:
            return companion, "local_only"
        if companion.consent_status != "promoted":
            raise WernerModelRouterBridgeError("werner_model_router_consent_status_unknown")
        if receipt.status not in STATUS_WEIGHTS:
            raise WernerModelRouterBridgeError("werner_model_router_receipt_status_unknown")
        return companion, receipt.status
    if isinstance(receipt, RouterCompanionRecord):
        return receipt, receipt_status_from_companion(receipt)
    raise WernerModelRouterBridgeError("werner_model_router_receipt_must_be_receipt_or_companion")


def _absent_context(
    *,
    agent_id: str,
    epoch: int,
    absent_token: str = WERNER_CONTEXT_ABSENT_TOKEN,
) -> WernerModelRouterContext:
    return WernerModelRouterContext(
        agent_id=agent_id,
        epoch=epoch,
        flow_budget=ZERO,
        candidate_priority=ZERO,
        capped_agent_signal=ZERO,
        receipt_count=0,
        werner_context_present=False,
        cdl_version=WERNER_CDL_116_VERSION,
        bridge_version=WERNER_CDL_109_BRIDGE_VERSION,
        non_claims=NON_CLAIMS + (absent_token,),
        absent_token=absent_token,
    )


def _require_non_empty_string(value: object, token: str) -> str:
    if type(value) is not str or not value.strip():
        raise WernerModelRouterBridgeError(token)
    return value.strip()


def _require_non_negative_int(value: object, token: str) -> int:
    if isinstance(value, bool) or type(value) is not int or value < 0:
        raise WernerModelRouterBridgeError(token)
    return value


def _require_decimal(value: object, token: str) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float) or not isinstance(value, Decimal):
        raise WernerModelRouterBridgeError(token)
    if not value.is_finite():
        raise WernerModelRouterBridgeError(token)
    return value


def _require_non_negative_decimal(value: Decimal, name: str) -> Decimal:
    if value < ZERO:
        raise WernerModelRouterBridgeError(f"{name}_must_be_non_negative")
    return value


def _coerce_non_negative_decimal(value: object, name: str) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise WernerModelRouterBridgeError(f"werner_model_router_{name}_must_be_decimal_safe")
    if isinstance(value, Decimal):
        result = value
    elif type(value) is int:
        result = Decimal(value)
    else:
        raise WernerModelRouterBridgeError(f"werner_model_router_{name}_invalid")
    if not result.is_finite():
        raise WernerModelRouterBridgeError("werner_non_finite_decimal")
    if result < ZERO:
        raise WernerModelRouterBridgeError(f"werner_model_router_{name}_must_be_non_negative")
    return result


__all__ = [
    "CAPABILITY_WEIGHTS",
    "CONSENT_WEIGHTS",
    "MAX_AGENT_SIGNAL",
    "NON_CLAIMS",
    "PER_RECEIPT_TOKEN_CAP",
    "RUNTIME_POLICY_CAP",
    "STATUS_WEIGHTS",
    "TWELVE_PLACES",
    "WERNER_CDL_109_BRIDGE_VERSION",
    "WERNER_CDL_116_VERSION",
    "WERNER_CONTEXT_ABSENT_TOKEN",
    "WERNER_GUARD_ACTIVE_ABSENT_TOKEN",
    "WERNER_MODEL_ROUTER_NOT_ACTIVATED",
    "WernerModelRouterBridgeError",
    "WernerModelRouterContext",
    "compute_werner_model_router_context",
    "receipt_status_from_companion",
]
