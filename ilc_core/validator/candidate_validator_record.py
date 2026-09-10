# SPDX-License-Identifier: AGPL-3.0-only
"""CDL-107 local Candidate validator record.

This module records public-RC validator candidacy only. It does not admit an
agent to the active validator set and deliberately carries zero consensus and
BFT quorum weight while the production admission gate remains closed.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


CANDIDATE_VALIDATOR_RECORD_SCHEMA_VERSION = "candidate_validator_record_cdl107.v0.1"
CANDIDATE_VALIDATOR_RECORD_KIND = "candidate_validator_record"
CDL_107_REF = "CDL-107"
DEFAULT_VALIDATOR_MODE = "candidate"
DEFAULT_ROLE_EVIDENCE_STATUS = "candidate_recorded_zero_weight"
REQUIRED_NON_CLAIMS = (
    "no_active_validator_set_membership",
    "no_consensus_weight",
    "no_bft_quorum_weight",
    "no_validator_rewards",
    "no_settlement_eligibility",
    "no_validator_admission_guard_clearance",
)

_AGENT_ID_HEX_RE = re.compile(r"^[0-9a-f]{96}$")
_NETWORK_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{1,62}$")


def _require_agent_id(value: str) -> str:
    if not isinstance(value, str) or _AGENT_ID_HEX_RE.fullmatch(value) is None:
        raise ValueError("candidate_validator_agent_id_invalid")
    return value


def _require_network_id(value: str) -> str:
    if not isinstance(value, str) or _NETWORK_ID_RE.fullmatch(value) is None:
        raise ValueError("candidate_validator_network_id_invalid")
    return value


def _require_exact_bool(value: bool, expected: bool, token: str) -> bool:
    if not isinstance(value, bool) or value is not expected:
        raise ValueError(token)
    return value


def _require_zero_int(value: int, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value != 0:
        raise ValueError(token)
    return value


def _require_optional_non_empty_string(value: str | None, token: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(token)
    if len(value) > 2048:
        raise ValueError(token)
    return value


def _reject_float(value: Any, token: str, *, depth: int = 0) -> None:
    if depth > 64:
        raise ValueError(token)
    if isinstance(value, float):
        raise ValueError(token)
    if isinstance(value, dict):
        for key, item in value.items():
            _reject_float(key, token, depth=depth + 1)
            _reject_float(item, token, depth=depth + 1)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _reject_float(item, token, depth=depth + 1)


def _require_non_claims(values: tuple[str, ...]) -> tuple[str, ...]:
    if not isinstance(values, tuple) or not values:
        raise ValueError("candidate_validator_non_claims_invalid")
    seen: set[str] = set()
    clean: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value:
            raise ValueError("candidate_validator_non_claims_invalid")
        if value in seen:
            raise ValueError("candidate_validator_non_claims_duplicate")
        seen.add(value)
        clean.append(value)
    missing = [value for value in REQUIRED_NON_CLAIMS if value not in seen]
    if missing:
        raise ValueError("candidate_validator_required_non_claim_missing")
    return tuple(clean)


@dataclass(frozen=True)
class CandidateValidatorRecord:
    agent_id: str
    network_id: str = "public-rc"
    validator_mode: str = DEFAULT_VALIDATOR_MODE
    source_cdl_ref: str = CDL_107_REF
    record_kind: str = CANDIDATE_VALIDATOR_RECORD_KIND
    consensus_weight: int = 0
    bft_quorum_weight: int = 0
    active_validator_set_member: bool = False
    reward_eligible: bool = False
    settlement_eligible: bool = False
    role_evidence_status: str = DEFAULT_ROLE_EVIDENCE_STATUS
    connectivity_receipt_ref: str | None = None
    relay_endpoint_ref: str | None = None
    endpoint_assertion_ref: str | None = None
    bootstrap_capsule_ref: str | None = None
    trust_tier_consecutive_missed_epochs: int | None = None
    trust_tier_equivocation_state: bool | None = None
    non_claims: tuple[str, ...] = REQUIRED_NON_CLAIMS
    schema_version: str = CANDIDATE_VALIDATOR_RECORD_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _require_agent_id(self.agent_id)
        _require_network_id(self.network_id)
        if self.validator_mode != DEFAULT_VALIDATOR_MODE:
            raise ValueError("candidate_validator_mode_must_be_candidate")
        if self.source_cdl_ref != CDL_107_REF:
            raise ValueError("candidate_validator_source_cdl_ref_invalid")
        if self.record_kind != CANDIDATE_VALIDATOR_RECORD_KIND:
            raise ValueError("candidate_validator_record_kind_invalid")
        if self.schema_version != CANDIDATE_VALIDATOR_RECORD_SCHEMA_VERSION:
            raise ValueError("candidate_validator_schema_version_invalid")
        _require_zero_int(
            self.consensus_weight,
            "candidate_validator_consensus_weight_must_be_zero",
        )
        _require_zero_int(
            self.bft_quorum_weight,
            "candidate_validator_bft_quorum_weight_must_be_zero",
        )
        _require_exact_bool(
            self.active_validator_set_member,
            False,
            "candidate_validator_active_membership_must_be_false",
        )
        _require_exact_bool(self.reward_eligible, False, "candidate_validator_reward_must_be_false")
        _require_exact_bool(
            self.settlement_eligible,
            False,
            "candidate_validator_settlement_must_be_false",
        )
        if not isinstance(self.role_evidence_status, str) or not self.role_evidence_status:
            raise ValueError("candidate_validator_role_evidence_status_invalid")
        _require_optional_non_empty_string(
            self.connectivity_receipt_ref,
            "candidate_validator_connectivity_ref_invalid",
        )
        _require_optional_non_empty_string(self.relay_endpoint_ref, "candidate_validator_relay_ref_invalid")
        _require_optional_non_empty_string(
            self.endpoint_assertion_ref,
            "candidate_validator_endpoint_ref_invalid",
        )
        _require_optional_non_empty_string(
            self.bootstrap_capsule_ref,
            "candidate_validator_bootstrap_ref_invalid",
        )
        if self.trust_tier_consecutive_missed_epochs is not None:
            raise ValueError("candidate_validator_trust_tier_missed_epochs_must_be_none")
        if self.trust_tier_equivocation_state is not None:
            raise ValueError("candidate_validator_trust_tier_equivocation_must_be_none")
        _require_non_claims(self.non_claims)

    def to_canonical_record(self) -> dict[str, Any]:
        record = {
            "active_validator_set_member": self.active_validator_set_member,
            "agent_id": self.agent_id,
            "bft_quorum_weight": self.bft_quorum_weight,
            "bootstrap_capsule_ref": self.bootstrap_capsule_ref,
            "connectivity_receipt_ref": self.connectivity_receipt_ref,
            "consensus_weight": self.consensus_weight,
            "endpoint_assertion_ref": self.endpoint_assertion_ref,
            "network_id": self.network_id,
            "non_claims": list(self.non_claims),
            "record_kind": self.record_kind,
            "relay_endpoint_ref": self.relay_endpoint_ref,
            "reward_eligible": self.reward_eligible,
            "role_evidence_status": self.role_evidence_status,
            "schema_version": self.schema_version,
            "settlement_eligible": self.settlement_eligible,
            "source_cdl_ref": self.source_cdl_ref,
            "trust_tier_consecutive_missed_epochs": self.trust_tier_consecutive_missed_epochs,
            "trust_tier_equivocation_state": self.trust_tier_equivocation_state,
            "validator_mode": self.validator_mode,
        }
        _reject_float(record, "candidate_validator_float_not_allowed")
        return record

    def to_canonical_json(self) -> str:
        return json.dumps(
            self.to_canonical_record(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )


def build_candidate_validator_record(
    *,
    agent_id: str,
    network_id: str = "public-rc",
    connectivity_receipt_ref: str | None = None,
    relay_endpoint_ref: str | None = None,
    endpoint_assertion_ref: str | None = None,
    bootstrap_capsule_ref: str | None = None,
    role_evidence_status: str = DEFAULT_ROLE_EVIDENCE_STATUS,
) -> CandidateValidatorRecord:
    return CandidateValidatorRecord(
        agent_id=agent_id,
        network_id=network_id,
        connectivity_receipt_ref=connectivity_receipt_ref,
        relay_endpoint_ref=relay_endpoint_ref,
        endpoint_assertion_ref=endpoint_assertion_ref,
        bootstrap_capsule_ref=bootstrap_capsule_ref,
        role_evidence_status=role_evidence_status,
    )


__all__ = [
    "CANDIDATE_VALIDATOR_RECORD_KIND",
    "CANDIDATE_VALIDATOR_RECORD_SCHEMA_VERSION",
    "CDL_107_REF",
    "DEFAULT_VALIDATOR_MODE",
    "REQUIRED_NON_CLAIMS",
    "CandidateValidatorRecord",
    "build_candidate_validator_record",
]
