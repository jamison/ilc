from __future__ import annotations

import copy
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ilc_core.epoch.allocation_distributor_runtime import (
    FINDING_1_ROUNDING_RESIDUAL_CAP_BLOCKED_RESOLVED_TOKEN,
    UPHELD_REFUTATION_RECIPIENTS_RESIDUAL_ROUTE,
    build_allocation_distribution_quote,
)
from ilc_core.epoch.ecu_price_clamp_runtime import (
    FINDING_3_PRICE_CLAMP_WIDTH_DERIVED_RESOLVED_TOKEN,
    P_MAX,
    P_MIN,
    PRICE_CLAMP_WIDTH,
)
from ilc_core.ledger.cdl048_conversion_sweeper_runtime import (
    Cdl048ConversionSweeperRuntimeError,
    convert_ecu_lot,
    conversion_receipt_payload,
    empty_conversion_sweeper_state,
    register_ecu_lot,
)
from ilc_core.ledger.claimability_proof_binding_runtime import (
    build_claimability_proof_binding,
    claimability_proof_payload,
)
from ilc_core.protocol.event_log_retention import (
    EVENT_LOG_RETENTION_INTERNAL_PLAN_PROVENANCE_TOKEN,
    FINDING_14_EVENT_LOG_RETENTION_PROVENANCE_GUARD_RESOLVED_TOKEN,
    apply_event_log_retention_plan,
    build_event_log_retention_plan,
)
from ilc_core.server import create_app
from ilc_core.sidecars.claimability_receipt_verifier import (
    FINDING_13_NEGATIVE_INT_CONSTRAINT_DOCUMENTED_RESOLVED_TOKEN,
    REJECTED_DECISION,
    build_claimability_verifier_presentation,
)
from ilc_core.sidecars.public_verifier_api_activation import (
    ACCEPTED_PUBLIC_VERIFIER_API_DECISION,
    CLAIMABILITY_INTEGRATION_TESTS_PHASE_1440_TOKEN,
    FINDING_11_NULLIFIER_EXPIRE_STALE_PUBLIC_PATH_RESOLVED_TOKEN,
    SECURITY_REVIEW_GATE_PASSED_PHASE_1440_TOKEN,
    public_verifier_api_activation_manifest,
)


def _valid_presentation() -> dict:
    agent_id = "agent:phase-1440-integration"
    epoch_id = "epoch-1440"
    wallet_state_root = f"wallet_state_sha256:{'a' * 64}"
    settled_runtime_root = f"settled_runtime_sha256:{'b' * 64}"
    history_digest = f"history_sha256:{'c' * 64}"

    state = register_ecu_lot(
        empty_conversion_sweeper_state(),
        lot_id="lot-phase-1440",
        agent_id=agent_id,
        amount_ecu="13",
        issue_epoch=10,
        origin="phase-1440-test-fixture",
        funding_provenance=("phase-1440-public-api",),
    )
    result = convert_ecu_lot(
        state,
        lot_id="lot-phase-1440",
        agent_id=agent_id,
        conversion_epoch=12,
        settled_runtime_epoch=12,
        wallet_state_root=wallet_state_root,
        settled_runtime_root=settled_runtime_root,
    )
    conversion_receipt = conversion_receipt_payload(result.receipt)
    latest_balance_receipt = {
        "balance_after_ilc": "13",
        "epoch_id": epoch_id,
        "reward_delta_ilc": "0",
        "settlement_status": "applied",
    }
    proof_binding = build_claimability_proof_binding(
        agent_id=agent_id,
        epoch_id=epoch_id,
        settled_runtime_root=settled_runtime_root,
        wallet_state_root=wallet_state_root,
        latest_balance_receipt=latest_balance_receipt,
        history_digest=history_digest,
        conversion_receipt=conversion_receipt,
    )
    return build_claimability_verifier_presentation(
        canonical_agent_identity=agent_id,
        epoch_id=epoch_id,
        settled_runtime_root=settled_runtime_root,
        wallet_state_root=wallet_state_root,
        latest_balance_receipt=latest_balance_receipt,
        history_digest=history_digest,
        claimability_proof=claimability_proof_payload(proof_binding),
        conversion_receipt=conversion_receipt,
    )


def _post_claimability(client: TestClient, presentation: dict, epoch: int = 12):
    return client.post(
        "/api/v1/claimability/verify",
        json={"presentation": presentation, "current_issuance_epoch": epoch},
    )


def test_phase_1440_public_claimability_happy_path_uses_phase_1439_contract() -> None:
    with TestClient(create_app()) as client:
        response = _post_claimability(client, _valid_presentation())

    assert response.status_code == 200
    decision = response.json()
    assert decision["decision"] == ACCEPTED_PUBLIC_VERIFIER_API_DECISION
    assert decision["public_api_enabled"] is True
    assert decision["receipt_verifier_public_serving_enabled"] is True
    assert decision["ecu_mint_authorized"] is False
    assert decision["ilc_settlement_authorized"] is False
    assert decision["wallet_withdrawal_enabled"] is False


def test_phase_1440_duplicate_presentation_rejected_by_nullifier_gate() -> None:
    presentation = _valid_presentation()
    with TestClient(create_app()) as client:
        first = _post_claimability(client, presentation)
        second = _post_claimability(client, presentation)

    assert first.json()["decision"] == ACCEPTED_PUBLIC_VERIFIER_API_DECISION
    assert second.status_code == 200
    assert second.json()["decision"] == REJECTED_DECISION
    assert second.json()["rejection_reasons"] == ["claim_nullifier_replay_rejected_phase_1389b"]


def test_phase_1440_expired_ecu_lot_rejected_by_deadline_check() -> None:
    state = register_ecu_lot(
        empty_conversion_sweeper_state(),
        lot_id="expired-lot-phase-1440",
        agent_id="agent:expired-phase-1440",
        amount_ecu="13",
        issue_epoch=10,
        origin="phase-1440-expired-fixture",
        funding_provenance=("phase-1440-expired",),
    )

    with pytest.raises(Cdl048ConversionSweeperRuntimeError) as exc_info:
        convert_ecu_lot(
            state,
            lot_id="expired-lot-phase-1440",
            agent_id="agent:expired-phase-1440",
            conversion_epoch=15,
            settled_runtime_epoch=15,
            wallet_state_root=f"wallet_state_sha256:{'a' * 64}",
            settled_runtime_root=f"settled_runtime_sha256:{'b' * 64}",
        )

    assert exc_info.value.token == "cdl048_conversion_deadline_expired"


def test_phase_1440_malformed_presentation_fails_closed_on_public_path() -> None:
    presentation = copy.deepcopy(_valid_presentation())
    presentation["conversion_deadline_epoch"] = -1

    with TestClient(create_app()) as client:
        response = _post_claimability(client, presentation)

    assert response.status_code == 200
    decision = response.json()
    assert decision["decision"] == REJECTED_DECISION
    assert decision["rejection_reasons"] == ["claimability_payload_int_invalid_phase_1305"]


def test_phase_1440_finding_1_routes_cap_blocked_residual_to_refutation_recipients() -> None:
    quote = build_allocation_distribution_quote(
        issuance_epoch=1440,
        total_epoch_allocation_ilc="0.000000019",
        genesis_overhead_cap_blocked=True,
        upheld_refutation_recipients=["agent:z", "agent:a"],
    )

    assert FINDING_1_ROUNDING_RESIDUAL_CAP_BLOCKED_RESOLVED_TOKEN
    assert quote.residual_route == UPHELD_REFUTATION_RECIPIENTS_RESIDUAL_ROUTE
    assert quote.rounding_residual_to_upheld_refutation_recipients_ilc == Decimal("0.000000002")
    assert quote.rounding_residual_refutation_recipient_allocations_ilc == (
        ("agent:a", Decimal("0.000000001")),
        ("agent:z", Decimal("0.000000001")),
    )
    assert (
        sum(
            (
                amount
                for _, amount in quote.rounding_residual_refutation_recipient_allocations_ilc
            ),
            Decimal("0"),
        )
        == quote.rounding_residual_to_upheld_refutation_recipients_ilc
    )


def test_phase_1440_finding_3_price_clamp_width_is_derived_from_bounds() -> None:
    assert FINDING_3_PRICE_CLAMP_WIDTH_DERIVED_RESOLVED_TOKEN
    assert PRICE_CLAMP_WIDTH == P_MAX - P_MIN
    assert PRICE_CLAMP_WIDTH == Decimal("0.55")


def test_phase_1440_finding_14_rejects_untrusted_event_log_retention_plan(tmp_path: Path) -> None:
    trusted = build_event_log_retention_plan(tmp_path, keep_last=1)
    untrusted = dict(trusted)
    untrusted.pop("plan_provenance_token")

    assert trusted["plan_provenance_token"] == EVENT_LOG_RETENTION_INTERNAL_PLAN_PROVENANCE_TOKEN
    assert FINDING_14_EVENT_LOG_RETENTION_PROVENANCE_GUARD_RESOLVED_TOKEN
    with pytest.raises(ValueError, match="event_log_retention_plan_provenance_invalid_phase_1440"):
        apply_event_log_retention_plan(untrusted, dry_run=True)  # type: ignore[arg-type]


def test_phase_1440_security_review_tokens_are_recorded() -> None:
    manifest = public_verifier_api_activation_manifest()

    assert FINDING_11_NULLIFIER_EXPIRE_STALE_PUBLIC_PATH_RESOLVED_TOKEN in str(manifest)
    assert FINDING_13_NEGATIVE_INT_CONSTRAINT_DOCUMENTED_RESOLVED_TOKEN
    assert CLAIMABILITY_INTEGRATION_TESTS_PHASE_1440_TOKEN in str(manifest)
    assert SECURITY_REVIEW_GATE_PASSED_PHASE_1440_TOKEN in str(manifest)
