# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1356 default-off CDL-013 governance-weight decision surface.

This module connects the Phase 207 CDL-013 governance-weight computation to a
protocol governance decision quote. It does not finalize governance records,
mutate protocol state, execute ratification outcomes, or activate production
governance decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import json
import math
import re
from typing import Any, Iterable, Mapping

import ilc_core.analysis.governance_weight as governance_weight_module
from ilc_core.ledger.exact_numeric import decimal_to_canonical_string


GOVERNANCE_WEIGHTED_DECISION_RUNTIME_VERSION = (
    "governance_weighted_decision_runtime_1356.v0.1"
)
CDL_013_DEPENDENCY = "cdl_013_governance_weight_decay_ratified_phase_215.v0.1"
CDL_013_GOVERNANCE_WEIGHT_LIVE_INTEGRATION_TOKEN = (
    "cdl_013_governance_weight_live_integration_phase_1356.v0.1"
)
GOVERNANCE_WEIGHT_OUTPUT_WIRED_DECISION_SURFACES_TOKEN = (
    "governance_weight_output_wired_decision_surfaces_phase_1356"
)
COMPUTE_GOVERNANCE_WEIGHTS_IN_CALL_PATH_TOKEN = (
    "compute_governance_weights_in_call_path_phase_1356"
)
PRODUCTION_GOVERNANCE_DECISIONS_NOT_ACTIVATED_TOKEN = (
    "production_governance_decisions_not_activated_phase_1356"
)
PRODUCTION_GOVERNANCE_DECISION_ACTIVATION_TOKEN = (
    "later_human_governance_activation_required_after_phase_1356"
)
LEGACY_FLOAT_CONVERSION_GUARD_TOKEN = (
    "legacy_governance_weight_float_conversion_guard_phase_1356"
)
GOVERNANCE_WEIGHT_DECIMAL_REWRITE_CLOSED_TOKEN = (
    "governance_weight_vote_share_precision_gap_closed_phase_1357"
)
NONFINITE_FLOAT_INF_NEGATIVE_INF_REGRESSION_TOKEN = (
    "nonfinite_float_inf_negative_inf_regression_phase_1357"
)
EMPTY_GOVERNANCE_PARTICIPANT_SET_REGRESSION_TOKEN = (
    "empty_governance_participant_set_regression_phase_1357"
)

VOTE_APPROVE = "approve"
VOTE_REJECT = "reject"
VOTE_ABSTAIN = "abstain"
VALID_VOTES = frozenset({VOTE_APPROVE, VOTE_REJECT, VOTE_ABSTAIN})
HEX64_PATTERN = re.compile(r"[a-f0-9]{64}")
ZERO = Decimal("0")


@dataclass(frozen=True)
class GovernanceWeightedParticipant:
    agent_id: str
    governance_weight: Decimal
    vote_share: Decimal
    vote: str

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "governance_weight": decimal_to_canonical_string(self.governance_weight),
            "vote": self.vote,
            "vote_share": decimal_to_canonical_string(self.vote_share),
        }


@dataclass(frozen=True)
class GovernanceWeightedDecisionQuote:
    runtime_version: str
    cdl_013_dependency: str
    integration_token: str
    decision_surface_token: str
    compute_call_token: str
    legacy_float_conversion_guard_token: str
    phase_1357_decimal_rewrite_token: str
    proposal_id: str
    decision_epoch: int
    participants: tuple[GovernanceWeightedParticipant, ...]
    total_governance_weight: Decimal
    approval_governance_weight: Decimal
    rejection_governance_weight: Decimal
    abstain_governance_weight: Decimal
    approval_vote_share: Decimal
    rejection_vote_share: Decimal
    abstain_vote_share: Decimal
    production_governance_decisions_activated: bool
    decision_token: str

    def to_canonical_record(self) -> dict[str, Any]:
        return {
            "abstain_governance_weight": decimal_to_canonical_string(
                self.abstain_governance_weight
            ),
            "abstain_vote_share": decimal_to_canonical_string(self.abstain_vote_share),
            "approval_governance_weight": decimal_to_canonical_string(
                self.approval_governance_weight
            ),
            "approval_vote_share": decimal_to_canonical_string(self.approval_vote_share),
            "cdl_013_dependency": self.cdl_013_dependency,
            "compute_call_token": self.compute_call_token,
            "decision_epoch": self.decision_epoch,
            "decision_surface_token": self.decision_surface_token,
            "decision_token": self.decision_token,
            "integration_token": self.integration_token,
            "legacy_float_conversion_guard_token": (
                self.legacy_float_conversion_guard_token
            ),
            "participants": [
                participant.to_canonical_record()
                for participant in self.participants
            ],
            "phase_1357_decimal_rewrite_token": (
                self.phase_1357_decimal_rewrite_token
            ),
            "production_governance_decisions_activated": (
                self.production_governance_decisions_activated
            ),
            "proposal_id": self.proposal_id,
            "rejection_governance_weight": decimal_to_canonical_string(
                self.rejection_governance_weight
            ),
            "rejection_vote_share": decimal_to_canonical_string(self.rejection_vote_share),
            "runtime_version": self.runtime_version,
            "total_governance_weight": decimal_to_canonical_string(
                self.total_governance_weight
            ),
        }

    def to_canonical_json(self) -> str:
        return json.dumps(
            self.to_canonical_record(),
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )


def _require_proposal_id(value: str) -> str:
    if not isinstance(value, str) or HEX64_PATTERN.fullmatch(value) is None:
        raise ValueError("governance_proposal_id_must_be_hex64_phase_1356")
    return value


def _require_epoch(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("governance_decision_epoch_must_be_non_negative_int")
    return value


def _require_agent_id(value: object, token: str) -> str:
    if not isinstance(value, str) or value == "":
        raise ValueError(token)
    return value


def _legacy_weight_to_decimal(value: object, field_name: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{field_name}_must_be_exact_numeric_phase_1356")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"{field_name}_must_be_finite_phase_1356")
    if isinstance(value, float):
        raise ValueError(f"{field_name}_must_be_exact_numeric_phase_1356")
    if isinstance(value, Decimal):
        amount = value
    else:
        try:
            amount = Decimal(str(value))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(f"{field_name}_must_be_exact_numeric_phase_1356") from exc
    if not amount.is_finite():
        raise ValueError(f"{field_name}_must_be_finite_phase_1356")
    if amount < ZERO:
        raise ValueError(f"{field_name}_must_be_non_negative_phase_1356")
    return amount


def _normalize_votes(votes: Iterable[Mapping[str, object]]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for raw_vote in votes:
        if not isinstance(raw_vote, Mapping):
            raise ValueError("governance_vote_entry_must_be_mapping_phase_1356")
        agent_id = _require_agent_id(
            raw_vote.get("agent_id"),
            "governance_vote_agent_id_invalid_phase_1356",
        )
        if agent_id in normalized:
            raise ValueError("governance_vote_duplicate_agent_id_phase_1356")
        vote = raw_vote.get("vote")
        if not isinstance(vote, str) or vote not in VALID_VOTES:
            raise ValueError("governance_vote_choice_invalid_phase_1356")
        normalized[agent_id] = vote
    return normalized


def build_governance_weighted_decision_quote(
    *,
    proposal_id: str,
    decision_epoch: int,
    governance_weight_inputs: Iterable[Mapping[str, object]],
    votes: Iterable[Mapping[str, object]],
    policy: Mapping[str, object] = governance_weight_module.DEFAULT_GOVERNANCE_WEIGHT_POLICY,
) -> GovernanceWeightedDecisionQuote:
    proposal = _require_proposal_id(proposal_id)
    epoch = _require_epoch(decision_epoch)
    vote_by_agent = _normalize_votes(votes)

    raw_outputs = governance_weight_module.compute_governance_weights(
        governance_weight_inputs,
        policy=policy,
    )

    participants: list[GovernanceWeightedParticipant] = []
    seen_agents: set[str] = set()
    for raw_output in raw_outputs:
        agent_id = _require_agent_id(
            raw_output.get("agent_id"),
            "governance_weight_output_agent_id_invalid_phase_1356",
        )
        if agent_id in seen_agents:
            raise ValueError("governance_weight_output_duplicate_agent_id_phase_1356")
        seen_agents.add(agent_id)
        participants.append(
            GovernanceWeightedParticipant(
                agent_id=agent_id,
                governance_weight=_legacy_weight_to_decimal(
                    raw_output.get("governance_weight"),
                    "governance_weight_output",
                ),
                vote_share=_legacy_weight_to_decimal(
                    raw_output.get("vote_share"),
                    "governance_vote_share_output",
                ),
                vote=vote_by_agent.get(agent_id, VOTE_ABSTAIN),
            )
        )

    unknown_vote_agents = sorted(set(vote_by_agent) - seen_agents)
    if unknown_vote_agents:
        raise ValueError("governance_vote_agent_not_in_weight_output_phase_1356")

    ordered_participants = tuple(sorted(participants, key=lambda item: item.agent_id))
    total_weight = sum(
        (participant.governance_weight for participant in ordered_participants),
        ZERO,
    )
    approval_weight = sum(
        (
            participant.governance_weight
            for participant in ordered_participants
            if participant.vote == VOTE_APPROVE
        ),
        ZERO,
    )
    rejection_weight = sum(
        (
            participant.governance_weight
            for participant in ordered_participants
            if participant.vote == VOTE_REJECT
        ),
        ZERO,
    )
    abstain_weight = sum(
        (
            participant.governance_weight
            for participant in ordered_participants
            if participant.vote == VOTE_ABSTAIN
        ),
        ZERO,
    )
    approval_share = sum(
        (
            participant.vote_share
            for participant in ordered_participants
            if participant.vote == VOTE_APPROVE
        ),
        ZERO,
    )
    rejection_share = sum(
        (
            participant.vote_share
            for participant in ordered_participants
            if participant.vote == VOTE_REJECT
        ),
        ZERO,
    )
    abstain_share = sum(
        (
            participant.vote_share
            for participant in ordered_participants
            if participant.vote == VOTE_ABSTAIN
        ),
        ZERO,
    )

    return GovernanceWeightedDecisionQuote(
        runtime_version=GOVERNANCE_WEIGHTED_DECISION_RUNTIME_VERSION,
        cdl_013_dependency=CDL_013_DEPENDENCY,
        integration_token=CDL_013_GOVERNANCE_WEIGHT_LIVE_INTEGRATION_TOKEN,
        decision_surface_token=GOVERNANCE_WEIGHT_OUTPUT_WIRED_DECISION_SURFACES_TOKEN,
        compute_call_token=COMPUTE_GOVERNANCE_WEIGHTS_IN_CALL_PATH_TOKEN,
        legacy_float_conversion_guard_token=LEGACY_FLOAT_CONVERSION_GUARD_TOKEN,
        phase_1357_decimal_rewrite_token=GOVERNANCE_WEIGHT_DECIMAL_REWRITE_CLOSED_TOKEN,
        proposal_id=proposal,
        decision_epoch=epoch,
        participants=ordered_participants,
        total_governance_weight=total_weight,
        approval_governance_weight=approval_weight,
        rejection_governance_weight=rejection_weight,
        abstain_governance_weight=abstain_weight,
        approval_vote_share=approval_share,
        rejection_vote_share=rejection_share,
        abstain_vote_share=abstain_share,
        production_governance_decisions_activated=False,
        decision_token=PRODUCTION_GOVERNANCE_DECISIONS_NOT_ACTIVATED_TOKEN,
    )


def require_production_governance_decision_activation(
    activation_token: str | None = None,
) -> None:
    if activation_token != PRODUCTION_GOVERNANCE_DECISION_ACTIVATION_TOKEN:
        raise ValueError(PRODUCTION_GOVERNANCE_DECISIONS_NOT_ACTIVATED_TOKEN)
    raise ValueError("production_governance_decision_activation_not_implemented_phase_1356")
