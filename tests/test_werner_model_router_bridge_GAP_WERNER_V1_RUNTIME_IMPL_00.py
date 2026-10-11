from __future__ import annotations

from decimal import Decimal

import pytest

from ilc_core.sidecars.execution_receipt import SidecarExecutionReceipt
from ilc_model_router.receipt_schema import MODEL_ROUTER_TOOL_ID, RouterCompanionRecord, RouterReceipt
from ilc_model_router.werner_model_router_bridge import (
    CAPABILITY_WEIGHTS,
    CONSENT_WEIGHTS,
    MAX_AGENT_SIGNAL,
    NON_CLAIMS,
    PER_RECEIPT_TOKEN_CAP,
    RUNTIME_POLICY_CAP,
    STATUS_WEIGHTS,
    WERNER_CONTEXT_ABSENT_TOKEN,
    WERNER_MODEL_ROUTER_NOT_ACTIVATED,
    WernerModelRouterBridgeError,
    _receipt_signal,
    compute_werner_model_router_context,
    receipt_status_from_companion,
)


AGENT_ID = "a" * 96


def _receipt(
    *,
    token: str = "1" * 64,
    in_tokens: int = 10_000,
    out_tokens: int = 10_000,
    capability: str | None = "inference",
    consent: str = "promoted",
) -> RouterCompanionRecord:
    return RouterCompanionRecord(
        receipt_token=token,
        model_id="model-x",
        provider="provider-x",
        token_counts_input=in_tokens,
        token_counts_output=out_tokens,
        capability_class=capability,
        consent_status=consent,
    )


def _router_receipt(
    *,
    status: str = "success",
    consent: str = "promoted",
    token: str = "1" * 64,
    in_tokens: int = 10_000,
    out_tokens: int = 10_000,
) -> RouterReceipt:
    error_token = "" if status == "success" else f"provider_{status}"
    core = SidecarExecutionReceipt(
        tool_id=MODEL_ROUTER_TOOL_ID,
        action_type="model_inference",
        epoch=7,
        agent_id_hex=AGENT_ID,
        inputs_hash="a" * 64,
        outputs_hash="b" * 64,
        status=status,
        error_token=error_token,
    )
    companion = _receipt(
        token=core.receipt_token,
        consent=consent,
        in_tokens=in_tokens,
        out_tokens=out_tokens,
    )
    return RouterReceipt.from_core_and_companion(core, companion)


def _unsafe_receipt_with_tokens(input_value: object, output_value: object) -> RouterCompanionRecord:
    receipt = object.__new__(RouterCompanionRecord)
    object.__setattr__(receipt, "receipt_token", "2" * 64)
    object.__setattr__(receipt, "model_id", "model-x")
    object.__setattr__(receipt, "provider", "provider-x")
    object.__setattr__(receipt, "token_counts_input", input_value)
    object.__setattr__(receipt, "token_counts_output", output_value)
    object.__setattr__(receipt, "capability_class", "inference")
    object.__setattr__(receipt, "consent_status", "promoted")
    object.__setattr__(
        receipt,
        "schema_version",
        "ilc_model_router_companion_meta_phase_1610.v0.1",
    )
    return receipt


def test_empty_receipts_fail_closed() -> None:
    context = compute_werner_model_router_context(AGENT_ID, 7, [])

    assert context.flow_budget == Decimal("0")
    assert context.werner_context_present is False
    assert context.receipt_count == 0
    assert WERNER_CONTEXT_ABSENT_TOKEN in context.non_claims
    assert context.absent_token == WERNER_CONTEXT_ABSENT_TOKEN


def test_single_local_only_receipt_has_zero_signal() -> None:
    context = compute_werner_model_router_context(
        AGENT_ID,
        7,
        [_receipt(consent="local_only")],
    )

    assert receipt_status_from_companion(_receipt(consent="local_only")) == "local_only"
    assert context.flow_budget == Decimal("0E-12")
    assert context.werner_context_present is True


def test_single_promoted_inference_receipt_has_positive_budget_within_cap() -> None:
    context = compute_werner_model_router_context(AGENT_ID, 7, [_receipt()])

    assert context.flow_budget > Decimal("0")
    assert context.flow_budget <= RUNTIME_POLICY_CAP
    assert context.werner_context_present is True


def test_agent_signal_caps_at_max_agent_signal() -> None:
    receipts = [
        _receipt(token=f"{index:064x}", in_tokens=20_000, out_tokens=0, capability="multimodal")
        for index in range(20)
    ]

    context = compute_werner_model_router_context(AGENT_ID, 7, receipts)

    assert context.capped_agent_signal == MAX_AGENT_SIGNAL
    assert context.flow_budget == RUNTIME_POLICY_CAP


@pytest.mark.parametrize(
    "receipts",
    [
        [_receipt(in_tokens=100, out_tokens=100)],
        [_receipt(consent="promotion_pending")],
        [_receipt(capability="embedding"), _receipt(token="3" * 64, capability=None)],
    ],
)
def test_flow_budget_never_exceeds_runtime_policy_cap(
    receipts: list[RouterCompanionRecord],
) -> None:
    context = compute_werner_model_router_context(AGENT_ID, 7, receipts)

    assert context.flow_budget <= RUNTIME_POLICY_CAP


def test_candidate_priority_derivation_for_known_input() -> None:
    context = compute_werner_model_router_context(
        AGENT_ID,
        7,
        [_receipt(in_tokens=1_000, out_tokens=1_000)],
    )

    assert context.capped_agent_signal == Decimal("0.100000000000")
    assert context.candidate_priority == Decimal("0.000833333333")
    assert context.flow_budget == Decimal("0.000833333333")


def test_embedding_capability_has_lower_signal_than_inference() -> None:
    inference = _receipt_signal(_receipt(capability="inference"))
    embedding = _receipt_signal(_receipt(capability="embedding"))

    assert CAPABILITY_WEIGHTS["embedding"] == Decimal("0.70")
    assert embedding == inference * Decimal("0.70")


def test_none_capability_uses_sim_weight_one() -> None:
    inference = _receipt_signal(_receipt(capability="inference"))
    none_weight = _receipt_signal(_receipt(capability=None))

    assert CAPABILITY_WEIGHTS[None] == Decimal("1.00")
    assert none_weight == inference


def test_token_count_cap_at_20000() -> None:
    capped = _receipt_signal(_receipt(in_tokens=20_000, out_tokens=0))
    over_cap = _receipt_signal(_receipt(in_tokens=30_000, out_tokens=0))

    assert PER_RECEIPT_TOKEN_CAP == Decimal("20000.000000000000")
    assert over_cap == capped


def test_promotion_pending_consent_has_zero_signal_until_graph_write_succeeds() -> None:
    promoted = _receipt_signal(_receipt(consent="promoted"))
    pending = _receipt_signal(_receipt(consent="promotion_pending"))

    assert CONSENT_WEIGHTS["promotion_pending"] == Decimal("0.00")
    assert promoted > Decimal("0")
    assert pending == Decimal("0E-12")


def test_full_receipt_failure_status_has_zero_signal_even_when_promoted() -> None:
    signal = _receipt_signal(_router_receipt(status="failure", consent="promoted"))

    assert signal == Decimal("0E-12")


def test_full_receipt_partial_status_uses_partial_weight() -> None:
    success = _receipt_signal(_router_receipt(status="success", consent="promoted"))
    partial = _receipt_signal(_router_receipt(status="partial", consent="promoted"))

    assert partial == (success * STATUS_WEIGHTS["partial"]).quantize(Decimal("0.000000000001"))


@pytest.mark.parametrize("bad_value", [Decimal("NaN"), Decimal("Infinity")])
def test_non_finite_decimal_input_is_rejected_by_internal_signal_path(
    bad_value: Decimal,
) -> None:
    receipt = _unsafe_receipt_with_tokens(bad_value, 0)

    with pytest.raises(WernerModelRouterBridgeError):
        _receipt_signal(receipt)


def test_float_input_is_rejected_by_internal_signal_path() -> None:
    receipt = _unsafe_receipt_with_tokens(1.0, 0)

    with pytest.raises(WernerModelRouterBridgeError):
        _receipt_signal(receipt)


def test_required_no_stacking_non_claims_are_present() -> None:
    context = compute_werner_model_router_context(AGENT_ID, 7, [_receipt()])

    assert "no_capproof_stacking" in context.non_claims
    assert "no_passive_ecu_quality_factor_stacking" in context.non_claims
    assert "guard_not_cleared_WERNER_MODEL_ROUTER_NOT_ACTIVATED" not in NON_CLAIMS
    assert "guard_not_cleared_WERNER_MODEL_ROUTER_NOT_ACTIVATED" not in context.non_claims
    assert set(NON_CLAIMS).issubset(context.non_claims)


def test_guard_constant_is_cleared() -> None:
    assert WERNER_MODEL_ROUTER_NOT_ACTIVATED is False


def test_signal_computation_failures_fail_closed_in_public_context_function() -> None:
    receipt = object.__new__(RouterCompanionRecord)
    object.__setattr__(receipt, "receipt_token", "4" * 64)
    object.__setattr__(receipt, "model_id", "model-x")
    object.__setattr__(receipt, "provider", "provider-x")
    object.__setattr__(receipt, "token_counts_input", 10_000)
    object.__setattr__(receipt, "token_counts_output", 0)
    object.__setattr__(receipt, "capability_class", "unknown")
    object.__setattr__(receipt, "consent_status", "promoted")
    object.__setattr__(
        receipt,
        "schema_version",
        "ilc_model_router_companion_meta_phase_1610.v0.1",
    )

    context = compute_werner_model_router_context(AGENT_ID, 7, [receipt])

    assert context.werner_context_present is False
    assert context.flow_budget == Decimal("0")


def test_decimal_only_result_types_and_weight_constants() -> None:
    context = compute_werner_model_router_context(AGENT_ID, 7, [_receipt()])

    assert isinstance(context.flow_budget, Decimal)
    assert isinstance(context.candidate_priority, Decimal)
    assert STATUS_WEIGHTS["success"] == Decimal("1.00")
    assert STATUS_WEIGHTS["partial"] == Decimal("0.25")
    assert STATUS_WEIGHTS["failure"] == Decimal("0.00")
    assert CONSENT_WEIGHTS["promoted"] == Decimal("1.00")
    assert CAPABILITY_WEIGHTS["multimodal"] == Decimal("1.10")
