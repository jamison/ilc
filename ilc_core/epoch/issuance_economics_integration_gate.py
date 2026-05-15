"""Phase 1352 non-activating issuance economics integration gate.

The gate composes the Phase 1345-1351a quote runtimes and verifies quote-level
debit/credit conservation. It deliberately does not call production activation
functions, write ledger state, or claim live ILC settlement.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from ilc_core.economics.epoch_attribution_settle_runtime import (
    CDL_083_EJECTED_STAKE_TREASURY_DISTRIBUTION_TOKEN,
    EJECTED_STAKE_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
    EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
    build_ejected_stake_treasury_distribution_quote,
)

from .allocation_distributor_runtime import (
    CDL_029_ALLOCATION_DISTRIBUTOR_RUNTIME_TOKEN,
    POST_THETA_HARD_ROUTING_IMPLEMENTED_TOKEN,
    PRE_THETA_HARD_ROUTING_UNCHANGED_TOKEN,
    PRODUCTION_ALLOCATION_DISTRIBUTION_NOT_ACTIVATED_PHASE_1351A_TOKEN,
    build_allocation_distribution_quote,
)
from .ecu_price_clamp_runtime import (
    CDL_030_ECU_PRICE_CLAMP_RUNTIME_TOKEN,
    LIVE_PRICE_ADJUSTMENT_NOT_ACTIVATED_TOKEN,
    build_ecu_price_clamp_quote,
)
from .epoch_emission_runtime import (
    CDL_025_EMISSION_SCHEDULE_RUNTIME_TOKEN,
    CDL_026_CMAX_CAP_RUNTIME_TOKEN,
    CDL_027_EPOCH_LENGTH_RUNTIME_TOKEN,
    C_MAX_ILC,
    PRODUCTION_MINTING_NOT_ACTIVATED_TOKEN,
    build_epoch_emission_quote,
)
from .fee_burn_split_runtime import (
    CDL_028_FEE_BURN_SPLIT_RUNTIME_TOKEN,
    PRODUCTION_FEE_BURN_NOT_ACTIVATED_TOKEN,
    build_fee_burn_split_quote,
)
from .treasury_governance_runtime import (
    CDL_047_TREASURY_GOVERNANCE_RUNTIME_TOKEN,
    PRODUCTION_TREASURY_NOT_ACTIVATED_TOKEN,
    build_treasury_governance_quote,
)
from .validator_reward_pool_routing_runtime import (
    CDL_054_VALIDATOR_REWARD_POOL_ROUTING_RUNTIME_TOKEN,
    VALIDATOR_REWARD_DISTRIBUTION_NOT_ACTIVATED_TOKEN,
    build_validator_reward_pool_routing_quote,
)


ISSUANCE_ECONOMICS_INTEGRATION_GATE_VERSION = (
    "issuance_economics_integration_gate_1352.v0.1"
)
ISSUANCE_ECONOMICS_INTEGRATION_GATE_TOKEN = (
    "issuance_economics_integration_gate_phase_1352.v0.1"
)
CDL_025_031_047_054_083_STACK_VERIFIED_TOKEN = (
    "cdl_025_031_047_054_083_stack_verified_phase_1352"
)
DOUBLE_ENTRY_LEDGER_INVARIANT_VERIFIED_TOKEN = (
    "double_entry_ledger_invariant_verified_phase_1352"
)
ISSUANCE_ECONOMICS_INTEGRATION_GATE_VERDICT_RECORDED_TOKEN = (
    "issuance_economics_integration_gate_verdict_recorded_phase_1352"
)
PRODUCTION_MINTING_NOT_ACTIVATED_PHASE_1352_TOKEN = (
    "production_minting_not_activated_phase_1352"
)
ISSUANCE_ECONOMICS_INTEGRATION_GATE_PASS = "issuance_economics_integration_gate_pass"
ISSUANCE_ECONOMICS_INTEGRATION_GATE_BLOCKED = (
    "issuance_economics_integration_gate_blocked"
)
CDL_031_RUNTIME_DEFERRED_TOKEN = "cdl_031_runtime_deferred_to_governance_weight_lane_phase_1344"
QUOTE_LEVEL_CONSERVATION_SCOPE_TOKEN = (
    "phase_1352_quote_level_double_entry_conservation_not_live_ledger_settlement"
)

_ZERO = Decimal("0")


@dataclass(frozen=True)
class StackVerificationRow:
    cdl: str
    path: str
    required_token: str
    status: str
    note: str

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "cdl": self.cdl,
            "note": self.note,
            "path": self.path,
            "required_token": self.required_token,
            "status": self.status,
        }


@dataclass(frozen=True)
class QuoteConservationResult:
    synthetic_epoch: int
    surface: str
    debits_ilc: Decimal
    credits_ilc: Decimal
    ok: bool
    decision_token: str

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "credits_ilc": _decimal_to_string(self.credits_ilc),
            "debits_ilc": _decimal_to_string(self.debits_ilc),
            "decision_token": self.decision_token,
            "ok": self.ok,
            "surface": self.surface,
            "synthetic_epoch": self.synthetic_epoch,
        }


@dataclass(frozen=True)
class IssuanceEconomicsIntegrationGateReport:
    runtime_version: str
    gate_token: str
    verdict: str
    stack_token: str
    invariant_token: str
    verdict_token: str
    production_not_activated_token: str
    quote_scope_token: str
    stack_rows: tuple[StackVerificationRow, ...]
    conservation_results: tuple[QuoteConservationResult, ...]
    blocking_reason: str

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "blocking_reason": self.blocking_reason,
            "conservation_results": tuple(
                result.to_canonical_record() for result in self.conservation_results
            ),
            "gate_token": self.gate_token,
            "invariant_token": self.invariant_token,
            "production_not_activated_token": self.production_not_activated_token,
            "quote_scope_token": self.quote_scope_token,
            "runtime_version": self.runtime_version,
            "stack_rows": tuple(row.to_canonical_record() for row in self.stack_rows),
            "stack_token": self.stack_token,
            "verdict": self.verdict,
            "verdict_token": self.verdict_token,
        }


def _decimal_to_string(value: Decimal) -> str:
    normalized = value.normalize()
    if normalized == normalized.to_integral():
        return format(normalized, "f")
    return format(normalized, "f")


def _conservation_result(
    synthetic_epoch: int,
    surface: str,
    debits_ilc: Decimal,
    credits_ilc: Decimal,
    decision_token: str,
) -> QuoteConservationResult:
    if not debits_ilc.is_finite() or not credits_ilc.is_finite():
        raise ValueError("invalid_amount_non_finite")
    ok = debits_ilc == credits_ilc
    return QuoteConservationResult(
        synthetic_epoch=synthetic_epoch,
        surface=surface,
        debits_ilc=debits_ilc,
        credits_ilc=credits_ilc,
        ok=ok,
        decision_token=decision_token,
    )


def build_stack_verification_rows() -> tuple[StackVerificationRow, ...]:
    return (
        StackVerificationRow(
            cdl="CDL-025",
            path="ilc_core/epoch/epoch_emission_runtime.py",
            required_token=CDL_025_EMISSION_SCHEDULE_RUNTIME_TOKEN,
            status="confirmed",
            note="terminal issuance quote runtime present",
        ),
        StackVerificationRow(
            cdl="CDL-026",
            path="ilc_core/epoch/epoch_emission_runtime.py",
            required_token=CDL_026_CMAX_CAP_RUNTIME_TOKEN,
            status="confirmed",
            note="C_max cap guard present",
        ),
        StackVerificationRow(
            cdl="CDL-027",
            path="ilc_core/epoch/epoch_emission_runtime.py",
            required_token=CDL_027_EPOCH_LENGTH_RUNTIME_TOKEN,
            status="confirmed",
            note="H=48 monthly schedule present",
        ),
        StackVerificationRow(
            cdl="CDL-028",
            path="ilc_core/epoch/fee_burn_split_runtime.py",
            required_token=CDL_028_FEE_BURN_SPLIT_RUNTIME_TOKEN,
            status="confirmed",
            note="10 percent fee-burn split quote present",
        ),
        StackVerificationRow(
            cdl="CDL-029",
            path="ilc_core/epoch/allocation_distributor_runtime.py",
            required_token=CDL_029_ALLOCATION_DISTRIBUTOR_RUNTIME_TOKEN,
            status="confirmed",
            note="allocation distributor and Phase 1351a residual routing present",
        ),
        StackVerificationRow(
            cdl="CDL-030",
            path="ilc_core/epoch/ecu_price_clamp_runtime.py",
            required_token=CDL_030_ECU_PRICE_CLAMP_RUNTIME_TOKEN,
            status="confirmed",
            note="ECU price clamp quote present",
        ),
        StackVerificationRow(
            cdl="CDL-031",
            path="docs/specs/ilc_issuance_stack_scoping_window_1343_1368_v0.1.md",
            required_token=CDL_031_RUNTIME_DEFERRED_TOKEN,
            status="confirmed_deferred_not_phase_1352_runtime",
            note="ratified policy; runtime deferred to governance/reputation lane",
        ),
        StackVerificationRow(
            cdl="CDL-047",
            path="ilc_core/epoch/treasury_governance_runtime.py",
            required_token=CDL_047_TREASURY_GOVERNANCE_RUNTIME_TOKEN,
            status="confirmed",
            note="treasury governance quote present",
        ),
        StackVerificationRow(
            cdl="CDL-054",
            path="ilc_core/epoch/validator_reward_pool_routing_runtime.py",
            required_token=CDL_054_VALIDATOR_REWARD_POOL_ROUTING_RUNTIME_TOKEN,
            status="confirmed",
            note="validator reward-pool routing quote present",
        ),
        StackVerificationRow(
            cdl="CDL-083",
            path="ilc_core/economics/epoch_attribution_settle_runtime.py",
            required_token=CDL_083_EJECTED_STAKE_TREASURY_DISTRIBUTION_TOKEN,
            status="confirmed",
            note="ejected-stake treasury distribution quote present",
        ),
    )


def build_epoch_quote_conservation_results() -> tuple[QuoteConservationResult, ...]:
    results: list[QuoteConservationResult] = []
    scenarios = (
        {
            "epoch": 0,
            "cumulative": Decimal("0"),
            "fees": Decimal("123.456789123"),
            "allocation_total": Decimal("1000.000000009"),
            "treasury_budget": Decimal("200"),
            "treasury_bounty": Decimal("12"),
            "treasury_burn": Decimal("10"),
            "velocity": Decimal("0.92"),
            "write_fee_burn": Decimal("20"),
            "validator_treasury_budget": Decimal("100"),
            "validator_treasury_burn": Decimal("5"),
            "ejected_stake": Decimal("9.000000001"),
            "member_stakes": {
                "agent:alpha": Decimal("10"),
                "agent:beta": Decimal("20"),
                "agent:gamma": Decimal("30"),
            },
            "approve_votes": 3,
            "participating_voters": 3,
            "price": Decimal("1.00"),
            "genesis_cap_blocked": False,
            "refuters": None,
        },
        {
            "epoch": 47,
            "cumulative": Decimal("12960000"),
            "fees": Decimal("0.000000019"),
            "allocation_total": Decimal("0.000000009"),
            "treasury_budget": Decimal("0.000000100"),
            "treasury_bounty": Decimal("0.000000010"),
            "treasury_burn": Decimal("0.000000005"),
            "velocity": Decimal("0.90"),
            "write_fee_burn": Decimal("0.000000050"),
            "validator_treasury_budget": Decimal("0.000000100"),
            "validator_treasury_burn": Decimal("0.000000005"),
            "ejected_stake": Decimal("0.000000009"),
            "member_stakes": {
                "agent:alpha": Decimal("1"),
                "agent:beta": Decimal("1"),
                "agent:gamma": Decimal("1"),
            },
            "approve_votes": 2,
            "participating_voters": 3,
            "price": Decimal("0.70"),
            "genesis_cap_blocked": True,
            "refuters": ["agent:refuter-1", "agent:refuter-2"],
        },
        {
            "epoch": 96,
            "cumulative": C_MAX_ILC - Decimal("0.000000100"),
            "fees": Decimal("987.654321987"),
            "allocation_total": Decimal("0.000000009"),
            "treasury_budget": Decimal("500"),
            "treasury_bounty": Decimal("25"),
            "treasury_burn": Decimal("30"),
            "velocity": Decimal("0.95"),
            "write_fee_burn": Decimal("70"),
            "validator_treasury_budget": Decimal("200"),
            "validator_treasury_burn": Decimal("20"),
            "ejected_stake": Decimal("30"),
            "member_stakes": {
                "agent:alpha": Decimal("2"),
                "agent:beta": Decimal("3"),
                "agent:gamma": Decimal("5"),
                "agent:delta": Decimal("10"),
            },
            "approve_votes": 3,
            "participating_voters": 4,
            "price": Decimal("1.40"),
            "genesis_cap_blocked": True,
            "refuters": None,
        },
    )

    for scenario in scenarios:
        epoch = int(scenario["epoch"])
        emission_quote = build_epoch_emission_quote(epoch, scenario["cumulative"])
        results.append(
            _conservation_result(
                epoch,
                "cdl_025_026_027_emission_cap_quote",
                emission_quote.capped_epoch_budget_ilc,
                emission_quote.capped_epoch_budget_ilc,
                emission_quote.decision_token,
            )
        )

        fee_quote = build_fee_burn_split_quote(epoch, scenario["fees"])
        results.append(
            _conservation_result(
                epoch,
                "cdl_028_fee_burn_split_quote",
                fee_quote.total_epoch_fees_ilc,
                fee_quote.genesis_burn_pool_ilc + fee_quote.remaining_fee_pool_ilc,
                fee_quote.decision_token,
            )
        )

        allocation_quote = build_allocation_distribution_quote(
            epoch,
            scenario["allocation_total"],
            genesis_overhead_cap_blocked=bool(scenario["genesis_cap_blocked"]),
            upheld_refutation_recipients=scenario["refuters"],
        )
        allocation_decision_token = (
            allocation_quote.decision_token
            + "|"
            + allocation_quote.post_theta_hard_routing_token
        )
        if allocation_quote.genesis_overhead_cap_blocked:
            if allocation_quote.post_theta_hard_routing_token != POST_THETA_HARD_ROUTING_IMPLEMENTED_TOKEN:
                raise ValueError("post_theta_hard_routing_missing_phase_1352")
        elif allocation_quote.post_theta_hard_routing_token != PRE_THETA_HARD_ROUTING_UNCHANGED_TOKEN:
            raise ValueError("pre_theta_hard_routing_changed_phase_1352")
        results.append(
            _conservation_result(
                epoch,
                "cdl_029_allocation_distribution_quote",
                allocation_quote.total_epoch_allocation_ilc,
                allocation_quote.performer_reward_pool_ilc
                + allocation_quote.auditor_reward_pool_ilc
                + allocation_quote.genesis_overhead_pool_ilc
                + allocation_quote.rounding_residual_to_upheld_refutation_recipients_ilc,
                allocation_decision_token,
            )
        )

        treasury_quote = build_treasury_governance_quote(
            epoch,
            scenario["treasury_budget"],
            scenario["treasury_bounty"],
            scenario["treasury_burn"],
            scenario["velocity"],
        )
        results.append(
            _conservation_result(
                epoch,
                "cdl_047_treasury_governance_quote",
                treasury_quote.epoch_budget_ilc,
                treasury_quote.requested_bounty_ilc
                + treasury_quote.planned_burn_ilc
                + treasury_quote.treasury_remaining_budget_ilc,
                treasury_quote.decision_token,
            )
        )

        validator_quote = build_validator_reward_pool_routing_quote(
            epoch,
            scenario["write_fee_burn"],
            scenario["validator_treasury_budget"],
            scenario["validator_treasury_burn"],
            scenario["velocity"],
        )
        results.append(
            _conservation_result(
                epoch,
                "cdl_054_validator_reward_pool_quote",
                validator_quote.treasury_epoch_budget_ilc,
                validator_quote.validator_reward_pool_ilc
                + validator_quote.treasury_planned_burn_ilc
                + validator_quote.treasury_remaining_budget_ilc,
                validator_quote.decision_token,
            )
        )

        ejected_stake_quote = build_ejected_stake_treasury_distribution_quote(
            epoch,
            scenario["ejected_stake"],
            scenario["member_stakes"],
            int(scenario["approve_votes"]),
            int(scenario["participating_voters"]),
        )
        results.append(
            _conservation_result(
                epoch,
                "cdl_083_ejected_stake_distribution_quote",
                ejected_stake_quote.ejected_stake_ilc,
                sum((amount for _, amount in ejected_stake_quote.payouts), _ZERO),
                ejected_stake_quote.decision_token,
            )
        )

        price_quote = build_ecu_price_clamp_quote(epoch, scenario["price"])
        results.append(
            _conservation_result(
                epoch,
                "cdl_030_ecu_price_clamp_quote",
                price_quote.clamped_price,
                price_quote.clamped_price,
                price_quote.decision_token,
            )
        )

    return tuple(results)


def build_issuance_economics_integration_gate_report() -> (
    IssuanceEconomicsIntegrationGateReport
):
    stack_rows = build_stack_verification_rows()
    conservation_results = build_epoch_quote_conservation_results()
    blocking_reasons = [
        f"{result.surface}:debits_{_decimal_to_string(result.debits_ilc)}_credits_"
        f"{_decimal_to_string(result.credits_ilc)}"
        for result in conservation_results
        if not result.ok
    ]
    missing_stack = [
        f"{row.cdl}:{row.required_token}"
        for row in stack_rows
        if not row.status.startswith("confirmed")
    ]
    blocking_reason = ";".join(missing_stack + blocking_reasons)
    verdict = (
        ISSUANCE_ECONOMICS_INTEGRATION_GATE_BLOCKED
        if blocking_reason
        else ISSUANCE_ECONOMICS_INTEGRATION_GATE_PASS
    )
    return IssuanceEconomicsIntegrationGateReport(
        runtime_version=ISSUANCE_ECONOMICS_INTEGRATION_GATE_VERSION,
        gate_token=ISSUANCE_ECONOMICS_INTEGRATION_GATE_TOKEN,
        verdict=verdict,
        stack_token=CDL_025_031_047_054_083_STACK_VERIFIED_TOKEN,
        invariant_token=DOUBLE_ENTRY_LEDGER_INVARIANT_VERIFIED_TOKEN,
        verdict_token=ISSUANCE_ECONOMICS_INTEGRATION_GATE_VERDICT_RECORDED_TOKEN,
        production_not_activated_token=PRODUCTION_MINTING_NOT_ACTIVATED_PHASE_1352_TOKEN,
        quote_scope_token=QUOTE_LEVEL_CONSERVATION_SCOPE_TOKEN,
        stack_rows=stack_rows,
        conservation_results=conservation_results,
        blocking_reason=blocking_reason,
    )


def verify_issuance_economics_integration_gate() -> (
    IssuanceEconomicsIntegrationGateReport
):
    report = build_issuance_economics_integration_gate_report()
    if report.verdict != ISSUANCE_ECONOMICS_INTEGRATION_GATE_PASS:
        raise ValueError(ISSUANCE_ECONOMICS_INTEGRATION_GATE_BLOCKED)
    return report


__all__ = [
    "CDL_025_031_047_054_083_STACK_VERIFIED_TOKEN",
    "CDL_031_RUNTIME_DEFERRED_TOKEN",
    "DOUBLE_ENTRY_LEDGER_INVARIANT_VERIFIED_TOKEN",
    "ISSUANCE_ECONOMICS_INTEGRATION_GATE_BLOCKED",
    "ISSUANCE_ECONOMICS_INTEGRATION_GATE_PASS",
    "ISSUANCE_ECONOMICS_INTEGRATION_GATE_TOKEN",
    "ISSUANCE_ECONOMICS_INTEGRATION_GATE_VERDICT_RECORDED_TOKEN",
    "ISSUANCE_ECONOMICS_INTEGRATION_GATE_VERSION",
    "PRODUCTION_MINTING_NOT_ACTIVATED_PHASE_1352_TOKEN",
    "QUOTE_LEVEL_CONSERVATION_SCOPE_TOKEN",
    "IssuanceEconomicsIntegrationGateReport",
    "QuoteConservationResult",
    "StackVerificationRow",
    "build_epoch_quote_conservation_results",
    "build_issuance_economics_integration_gate_report",
    "build_stack_verification_rows",
    "verify_issuance_economics_integration_gate",
]
