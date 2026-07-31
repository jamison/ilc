# SPDX-License-Identifier: AGPL-3.0-only
"""Validator eligibility certificate runtime for GAP-REPUTATION-04.

This module is intentionally standalone. Phase 1589 wires the certificate into
validator admission; this phase only creates the deterministic artifact surface.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from ilc_core.ledger.exact_numeric import decimal_to_canonical_string

VALIDATOR_ELIGIBILITY_CERT_VERSION = "validator_eligibility_cert_GAP_REPUTATION_04.v0.1"
CDL_106_DEPENDENCY = "cdl_106_agent_reputation_record_opened_GAP_REPUTATION_01"
CDL_107_DEPENDENCY = "reputation_ecu_boundary_cdl_107_opened_GAP_REPUTATION_03"
GENESIS_BOOTSTRAP_AUTHORITY_TOKEN = "genesis_bootstrap_authority_opened_GAP_REPUTATION_03"
PRODUCTION_ELIGIBILITY_NOT_ACTIVATED_TOKEN = (
    "production_eligibility_not_activated_GAP_REPUTATION_04"
)

CANDIDATE = "candidate"
PROVISIONAL = "provisional"
OFFICIAL = "official"
ELIGIBILITY_VERDICTS = frozenset({CANDIDATE, PROVISIONAL, OFFICIAL})

BOOTSTRAP_ACTIVE_RATIONALE = "bootstrap_authority_active_GAP_REPUTATION_04"
OFFICIAL_EVIDENCE_RATIONALE = "all_required_evidence_roots_present_GAP_REPUTATION_04"
PROVISIONAL_EVIDENCE_RATIONALE = "partial_eligibility_evidence_roots_present_GAP_REPUTATION_04"
CANDIDATE_EVIDENCE_RATIONALE = "no_eligibility_evidence_roots_GAP_REPUTATION_04"

_AGENT_ID_RE = re.compile(r"^[0-9a-f]{96}$")
_SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")
_NETWORK_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$")


def _reject_float_or_non_finite_decimal(value: object, field_name: str) -> None:
    if isinstance(value, bool):
        raise ValueError(f"{field_name}_bool_not_allowed")
    if isinstance(value, float):
        raise ValueError(f"{field_name}_float_not_allowed")
    if isinstance(value, Decimal) and not value.is_finite():
        raise ValueError(f"{field_name}_non_finite_decimal")


def _require_agent_id(value: object, field_name: str) -> str:
    _reject_float_or_non_finite_decimal(value, field_name)
    if not isinstance(value, str) or not _AGENT_ID_RE.fullmatch(value):
        raise ValueError(f"{field_name}_must_be_96_lower_hex")
    return value


def _require_epoch(value: object, field_name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field_name}_must_be_non_negative_int")
    _reject_float_or_non_finite_decimal(value, field_name)
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name}_must_be_non_negative_int")
    return value


def _require_network_id(value: object, field_name: str) -> str:
    _reject_float_or_non_finite_decimal(value, field_name)
    if not isinstance(value, str) or _NETWORK_ID_RE.fullmatch(value) is None:
        raise ValueError(f"{field_name}_must_be_non_empty_network_id")
    return value


def _require_optional_root(value: object, field_name: str) -> str | None:
    _reject_float_or_non_finite_decimal(value, field_name)
    if value is None:
        return None
    if not isinstance(value, str) or not _SHA256_HEX_RE.fullmatch(value):
        raise ValueError(f"{field_name}_must_be_sha256_hex_or_none")
    return value


def _require_token(value: object, field_name: str) -> str:
    _reject_float_or_non_finite_decimal(value, field_name)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name}_must_be_non_empty_string")
    return value


def _require_bootstrap_authority_token(value: object) -> str:
    token = _require_token(value, "authority_token")
    if token != GENESIS_BOOTSTRAP_AUTHORITY_TOKEN:
        raise ValueError("authority_token_must_match_genesis_bootstrap_authority")
    return token


def _require_verdict(value: object) -> str:
    _reject_float_or_non_finite_decimal(value, "eligibility_verdict")
    if not isinstance(value, str) or value not in ELIGIBILITY_VERDICTS:
        raise ValueError("eligibility_verdict_invalid")
    return value


def _canonical_json_safe(value: object, field_name: str = "payload") -> object:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    _reject_float_or_non_finite_decimal(value, field_name)
    if isinstance(value, Decimal):
        return decimal_to_canonical_string(value)
    if isinstance(value, list):
        return [
            _canonical_json_safe(item, f"{field_name}_item")
            for item in value
        ]
    if isinstance(value, tuple):
        return [
            _canonical_json_safe(item, f"{field_name}_item")
            for item in value
        ]
    if isinstance(value, dict):
        normalized: dict[str, object] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("payload_mapping_keys_must_be_strings")
            normalized[key] = _canonical_json_safe(item, key)
        return normalized
    raise ValueError("payload_value_not_json_safe")


def stable_sha256(payload: dict[str, Any]) -> str:
    canonical_payload = _canonical_json_safe(payload)
    canonical = json.dumps(
        canonical_payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


@dataclass(frozen=True)
class GenesisBootstrapAuthorityCertificate:
    genesis_agent_id: str
    authorized_agent_id: str
    network_id: str
    bootstrap_effective_from_epoch: int
    bootstrap_sunset_epoch: int
    authority_token: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "genesis_agent_id",
            _require_agent_id(self.genesis_agent_id, "genesis_agent_id"),
        )
        object.__setattr__(
            self,
            "authorized_agent_id",
            _require_agent_id(self.authorized_agent_id, "authorized_agent_id"),
        )
        object.__setattr__(
            self,
            "network_id",
            _require_network_id(self.network_id, "network_id"),
        )
        object.__setattr__(
            self,
            "bootstrap_effective_from_epoch",
            _require_epoch(
                self.bootstrap_effective_from_epoch,
                "bootstrap_effective_from_epoch",
            ),
        )
        object.__setattr__(
            self,
            "bootstrap_sunset_epoch",
            _require_epoch(self.bootstrap_sunset_epoch, "bootstrap_sunset_epoch"),
        )
        if self.bootstrap_effective_from_epoch > self.bootstrap_sunset_epoch:
            raise ValueError("bootstrap_effective_epoch_after_sunset")
        object.__setattr__(
            self,
            "authority_token",
            _require_bootstrap_authority_token(self.authority_token),
        )

    def is_active_for_epoch(self, epoch: int) -> bool:
        checked_epoch = _require_epoch(epoch, "epoch")
        return self.bootstrap_effective_from_epoch <= checked_epoch <= self.bootstrap_sunset_epoch

    def to_canonical_record(self) -> dict[str, object]:
        return {
            "authority_token": self.authority_token,
            "authorized_agent_id": self.authorized_agent_id,
            "bootstrap_effective_from_epoch": self.bootstrap_effective_from_epoch,
            "bootstrap_sunset_epoch": self.bootstrap_sunset_epoch,
            "genesis_agent_id": self.genesis_agent_id,
            "network_id": self.network_id,
        }


@dataclass(frozen=True)
class ValidatorEligibilityCertificate:
    agent_id: str
    network_id: str
    epoch: int
    reputation_evidence_root: str | None
    earned_ecu_work_score_root: str | None
    liveness_root: str | None
    bootstrap_authority: GenesisBootstrapAuthorityCertificate | None
    eligibility_verdict: str
    verdict_rationale: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "agent_id", _require_agent_id(self.agent_id, "agent_id"))
        object.__setattr__(
            self,
            "network_id",
            _require_network_id(self.network_id, "network_id"),
        )
        object.__setattr__(self, "epoch", _require_epoch(self.epoch, "epoch"))
        object.__setattr__(
            self,
            "reputation_evidence_root",
            _require_optional_root(self.reputation_evidence_root, "reputation_evidence_root"),
        )
        object.__setattr__(
            self,
            "earned_ecu_work_score_root",
            _require_optional_root(
                self.earned_ecu_work_score_root,
                "earned_ecu_work_score_root",
            ),
        )
        object.__setattr__(
            self,
            "liveness_root",
            _require_optional_root(self.liveness_root, "liveness_root"),
        )
        if (
            self.bootstrap_authority is not None
            and type(self.bootstrap_authority) is not GenesisBootstrapAuthorityCertificate
        ):
            raise ValueError("bootstrap_authority_must_be_certificate_or_none")
        if (
            self.bootstrap_authority is not None
            and self.bootstrap_authority.network_id != self.network_id
        ):
            raise ValueError("bootstrap_authority_network_mismatch")
        object.__setattr__(
            self,
            "eligibility_verdict",
            _require_verdict(self.eligibility_verdict),
        )
        object.__setattr__(
            self,
            "verdict_rationale",
            _require_token(self.verdict_rationale, "verdict_rationale"),
        )
        expected_verdict, expected_rationale = _derive_verdict(
            agent_id=self.agent_id,
            network_id=self.network_id,
            epoch=self.epoch,
            reputation_evidence_root=self.reputation_evidence_root,
            earned_ecu_work_score_root=self.earned_ecu_work_score_root,
            liveness_root=self.liveness_root,
            bootstrap_authority=self.bootstrap_authority,
        )
        if self.eligibility_verdict != expected_verdict:
            raise ValueError("eligibility_verdict_mismatch")
        if self.verdict_rationale != expected_rationale:
            raise ValueError("verdict_rationale_mismatch")

    def to_canonical_record(self) -> dict[str, object]:
        return {
            "bootstrap_authority": (
                None
                if self.bootstrap_authority is None
                else self.bootstrap_authority.to_canonical_record()
            ),
            "cdl_106_dependency": CDL_106_DEPENDENCY,
            "cdl_107_dependency": CDL_107_DEPENDENCY,
            "earned_ecu_work_score_root": self.earned_ecu_work_score_root,
            "eligibility_verdict": self.eligibility_verdict,
            "epoch": self.epoch,
            "liveness_root": self.liveness_root,
            "network_id": self.network_id,
            "reputation_evidence_root": self.reputation_evidence_root,
            "schema_version": VALIDATOR_ELIGIBILITY_CERT_VERSION,
            "validator_agent_id": self.agent_id,
            "verdict_rationale": self.verdict_rationale,
        }

    def certificate_sha256(self) -> str:
        return stable_sha256(self.to_canonical_record())


def _derive_verdict(
    *,
    agent_id: str,
    network_id: str,
    epoch: int,
    reputation_evidence_root: str | None,
    earned_ecu_work_score_root: str | None,
    liveness_root: str | None,
    bootstrap_authority: GenesisBootstrapAuthorityCertificate | None,
) -> tuple[str, str]:
    checked_agent_id = _require_agent_id(agent_id, "agent_id")
    checked_network_id = _require_network_id(network_id, "network_id")
    checked_epoch = _require_epoch(epoch, "epoch")
    if bootstrap_authority is not None:
        if bootstrap_authority.authorized_agent_id != checked_agent_id:
            raise ValueError("bootstrap_authority_agent_mismatch")
        if bootstrap_authority.network_id != checked_network_id:
            raise ValueError("bootstrap_authority_network_mismatch")
        if bootstrap_authority.is_active_for_epoch(checked_epoch):
            if earned_ecu_work_score_root is not None and liveness_root is not None:
                return OFFICIAL, BOOTSTRAP_ACTIVE_RATIONALE
            return PROVISIONAL, PROVISIONAL_EVIDENCE_RATIONALE
    roots_present = (
        reputation_evidence_root is not None,
        earned_ecu_work_score_root is not None,
        liveness_root is not None,
    )
    if all(roots_present):
        return OFFICIAL, OFFICIAL_EVIDENCE_RATIONALE
    if any(roots_present):
        return PROVISIONAL, PROVISIONAL_EVIDENCE_RATIONALE
    return CANDIDATE, CANDIDATE_EVIDENCE_RATIONALE


def evaluate_eligibility(
    *,
    agent_id: str,
    network_id: str,
    epoch: int,
    reputation_evidence_root: str | None = None,
    earned_ecu_work_score_root: str | None = None,
    liveness_root: str | None = None,
    bootstrap_authority: GenesisBootstrapAuthorityCertificate | None = None,
) -> ValidatorEligibilityCertificate:
    checked_agent_id = _require_agent_id(agent_id, "agent_id")
    checked_network_id = _require_network_id(network_id, "network_id")
    checked_epoch = _require_epoch(epoch, "epoch")
    checked_reputation_root = _require_optional_root(
        reputation_evidence_root,
        "reputation_evidence_root",
    )
    checked_work_score_root = _require_optional_root(
        earned_ecu_work_score_root,
        "earned_ecu_work_score_root",
    )
    checked_liveness_root = _require_optional_root(liveness_root, "liveness_root")
    if (
        bootstrap_authority is not None
        and type(bootstrap_authority) is not GenesisBootstrapAuthorityCertificate
    ):
        raise ValueError("bootstrap_authority_must_be_certificate_or_none")
    if (
        bootstrap_authority is not None
        and bootstrap_authority.network_id != checked_network_id
    ):
        raise ValueError("bootstrap_authority_network_mismatch")
    verdict, rationale = _derive_verdict(
        agent_id=checked_agent_id,
        network_id=checked_network_id,
        epoch=checked_epoch,
        reputation_evidence_root=checked_reputation_root,
        earned_ecu_work_score_root=checked_work_score_root,
        liveness_root=checked_liveness_root,
        bootstrap_authority=bootstrap_authority,
    )
    return ValidatorEligibilityCertificate(
        agent_id=checked_agent_id,
        network_id=checked_network_id,
        epoch=checked_epoch,
        reputation_evidence_root=checked_reputation_root,
        earned_ecu_work_score_root=checked_work_score_root,
        liveness_root=checked_liveness_root,
        bootstrap_authority=bootstrap_authority,
        eligibility_verdict=verdict,
        verdict_rationale=rationale,
    )


def require_production_eligibility_activation() -> None:
    raise ValueError(PRODUCTION_ELIGIBILITY_NOT_ACTIVATED_TOKEN)
