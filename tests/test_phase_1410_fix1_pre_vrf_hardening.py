"""Regression tests for Phase 1410-Fix1 pre-VRF hardening."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.economics.epoch_attribution_settle_runtime import (
    _PAYOUT_QUANTUM,
    _stake_proportional_payouts,
)
from ilc_core.epoch.treasury_governance_runtime import (
    build_treasury_governance_quote,
)
from ilc_core.epistemic.ingestion_shadow_harness import (
    exercise_task_lifecycle,
)
from ilc_core.epistemic.jury_assignment_runtime import (
    EligibleAgent,
    JuryAssignmentError,
    quote_jury_assignment,
)
from ilc_core.genesis.work_task import EpistemicWorkTask
from ilc_core.sidecars.claim_nullifier_registry_v1 import (
    ClaimNullifierRegistryError,
    _sha256_canonical,
)
from ilc_core.sidecars.claimability_receipt_verifier import (
    ClaimabilityReceiptVerifierError,
    _require_non_negative_int,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
ADR_0042 = REPO_ROOT / "docs/adr/ADR_0042_VRF_Proof_Verifier.md"
PROMPT = (
    REPO_ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1410_fix1_g8_pre_vrf_hardening.md"
)


def _make_agent(
    agent_id: str,
    *,
    cluster_id: str = "cluster-a",
    operator_domain: str = "operator-a",
    outsider: bool = False,
) -> EligibleAgent:
    return EligibleAgent(
        agent_id=agent_id,
        cluster_id=cluster_id,
        operator_domain=operator_domain,
        identity_lineage_ref=f"lineage:{agent_id}",
        outsider_candidate_flag=outsider,
        capability_tier_or_lane_score="tier1",
    )


def _valid_agent_pool() -> list[EligibleAgent]:
    return [
        _make_agent("regular-1", operator_domain="operator-a"),
        _make_agent("regular-2", operator_domain="operator-a"),
        _make_agent("regular-3", operator_domain="operator-b"),
        _make_agent("regular-4", operator_domain="operator-b"),
        _make_agent("regular-5", operator_domain="operator-c"),
        _make_agent("regular-6", operator_domain="operator-c"),
        _make_agent("regular-7", operator_domain="operator-d"),
        _make_agent("outsider-1", operator_domain="operator-out", outsider=True),
        _make_agent("outsider-2", operator_domain="operator-out", outsider=True),
    ]


def _make_task() -> EpistemicWorkTask:
    return EpistemicWorkTask(
        task_id="task-phase-1410-fix1",
        task_class="star.map.embedding",  # type: ignore[arg-type]
        agent_id="agent-phase-1410-fix1",
        region_scope=["region-1"],
        verification_method="hash-match",
        task_state="proposed",  # type: ignore[arg-type]
        timestamp_created=1000,
        ecu_estimate=Decimal("1.5"),
    )


def test_required_phase_tokens_are_recorded() -> None:
    prompt = PROMPT.read_text(encoding="utf-8")
    adr = ADR_0042.read_text(encoding="utf-8")

    assert "pre_vrf_hardening_phase_1410_fix1" in prompt
    assert "epoch_zero_receipt_rejection_fixed_phase_1410_fix1" in prompt
    assert "jury_panel_dedup_fixed_phase_1410_fix1" in prompt
    assert "vrf_pynacl_api_gap_documented_phase_1410_fix1" in adr


def test_require_non_negative_int_accepts_epoch_zero() -> None:
    assert _require_non_negative_int(0, token="phase_1410_fix1_epoch") == 0


def test_require_non_negative_int_rejects_negative_one() -> None:
    with pytest.raises(
        ClaimabilityReceiptVerifierError,
        match="required non-negative bounded integer",
    ):
        _require_non_negative_int(-1, token="phase_1410_fix1_epoch")


def test_quote_jury_assignment_rejects_duplicate_agent_ids() -> None:
    agents = _valid_agent_pool()
    agents.append(
        _make_agent(
            "regular-1",
            cluster_id="cluster-duplicate",
            operator_domain="operator-duplicate",
        )
    )

    with pytest.raises(JuryAssignmentError, match="jury_eligible_agents_duplicate_agent_id"):
        quote_jury_assignment(
            review_epoch=1410,
            review_lane="objective",
            claim_or_task_id="claim-phase-1410-fix1",
            author_agent_id="author-1",
            author_operator_domain="operator-author",
            eligible_agents=agents,
        )


def test_sha256_canonical_raises_registry_error_for_non_serializable() -> None:
    with pytest.raises(
        ClaimNullifierRegistryError,
        match="payload is not JSON-serializable",
    ) as exc_info:
        _sha256_canonical({"amount": Decimal("1.25")})

    assert (
        exc_info.value.token
        == "claim_nullifier_canonical_serialization_failed_phase_1410_fix1"
    )


def test_stake_proportional_payouts_last_member_share_is_quantized() -> None:
    payouts = _stake_proportional_payouts(
        Decimal("1.000000000"),
        {"agent-a": Decimal("1"), "agent-b": Decimal("1"), "agent-c": Decimal("1")},
        Decimal("3"),
    )

    assert payouts[-1] == ("agent-c", Decimal("0.333333334"))
    assert all(amount.quantize(_PAYOUT_QUANTUM) == amount for _, amount in payouts)


def test_stake_proportional_payouts_conservation_three_members() -> None:
    payouts = _stake_proportional_payouts(
        Decimal("1.000000000"),
        {"agent-a": Decimal("1"), "agent-b": Decimal("1"), "agent-c": Decimal("1")},
        Decimal("3"),
    )

    assert sum((amount for _, amount in payouts), Decimal("0")) == Decimal("1.000000000")


def test_treasury_remaining_budget_is_quantized() -> None:
    quote = build_treasury_governance_quote(
        issuance_epoch=0,
        epoch_budget_ilc="1.2345678999",
        requested_bounty_ilc="0.1851851849",
        planned_burn_ilc="0.0617283949",
        observed_velocity="0.50",
    )

    assert quote.treasury_remaining_budget_ilc == Decimal("0.987654321")
    assert quote.treasury_remaining_budget_ilc.quantize(Decimal("0.000000001")) == (
        quote.treasury_remaining_budget_ilc
    )


def test_task_lifecycle_from_state_accurate_after_failed_transition() -> None:
    trace = exercise_task_lifecycle(
        _make_task(),
        ["claimed", "rewarded", "completed", "audited"],
    )

    assert trace.steps[0].from_state == "proposed"
    assert trace.steps[0].to_state == "claimed"
    assert trace.steps[0].valid is True
    assert trace.steps[1].from_state == "claimed"
    assert trace.steps[1].to_state == "rewarded"
    assert trace.steps[1].valid is False
    assert trace.steps[2].from_state == "claimed"
    assert trace.steps[2].to_state == "completed"
    assert trace.steps[2].valid is True
    assert trace.steps[3].from_state == "completed"
    assert trace.steps[3].to_state == "audited"
    assert trace.steps[3].valid is True


def test_adr_0042_documents_pynacl_bindings_validation_gate() -> None:
    text = ADR_0042.read_text(encoding="utf-8")

    assert "vrf_pynacl_api_gap_documented_phase_1410_fix1" in text
    assert "crypto_core_ed25519_from_uniform" in text
    assert "crypto_scalarmult_ed25519_noclamp" in text
    assert "RFC 9381 Appendix B.4" in text
    assert "Do not skip the test-vector validation step" in text
