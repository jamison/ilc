# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Dict, Optional, Sequence, Tuple

from .signer_lineage_runtime import (
    RECOVERED,
    SignerLineageRegistry,
)


COMPROMISE_SUSPECTED = "suspected"
COMPROMISE_CONFIRMED = "confirmed"

TRIGGER_SIGNER_ANOMALY = "signer_anomaly"
TRIGGER_CUSTODY_LOSS = "custody_loss"
TRIGGER_COERCION_SIGNAL = "coercion_signal"
TRIGGER_CRYPTO_COMPROMISE = "crypto_compromise"

FREEZE_AUTHORITY = "freeze_authority"
QUARANTINE_LINEAGE = "quarantine_lineage"
SUSPEND_NEW_CANONICAL_SIGNATURES = "suspend_new_canonical_signatures"

SUPPORTED_TRIGGERS = {
    TRIGGER_SIGNER_ANOMALY,
    TRIGGER_CUSTODY_LOSS,
    TRIGGER_COERCION_SIGNAL,
    TRIGGER_CRYPTO_COMPROMISE,
}

STATE_BY_TRIGGER: Dict[str, str] = {
    TRIGGER_SIGNER_ANOMALY: COMPROMISE_SUSPECTED,
    TRIGGER_CUSTODY_LOSS: COMPROMISE_CONFIRMED,
    TRIGGER_COERCION_SIGNAL: COMPROMISE_CONFIRMED,
    TRIGGER_CRYPTO_COMPROMISE: COMPROMISE_CONFIRMED,
}

REQUIRED_CONTAINMENT_SEQUENCE: Tuple[str, str, str] = (
    FREEZE_AUTHORITY,
    QUARANTINE_LINEAGE,
    SUSPEND_NEW_CANONICAL_SIGNATURES,
)


@dataclass(frozen=True)
class CompromiseDecision:
    lineage_id: str
    compromised_signer_id: str
    trigger_class: str
    compromise_state: str
    reason_code: str
    event_ts: str


@dataclass(frozen=True)
class CompromiseIncidentRecord:
    incident_id: str
    lineage_id: str
    compromised_signer_id: str
    trigger_class: str
    compromise_state: str
    reason_code: str
    containment_actions: Tuple[str, str, str]
    replacement_signer_id: Optional[str]
    recovery_ticket_id: Optional[str]
    recovery_attestation: Optional[str]
    event_ts: str


class KeyCompromiseResponseRuntime:
    """Deterministic compromise-response runtime for CDL-002."""

    def __init__(self, registry: SignerLineageRegistry) -> None:
        self._registry = registry
        self._incidents: list[CompromiseIncidentRecord] = []
        self._incident_counter: int = 0

    @property
    def incidents(self) -> Sequence[CompromiseIncidentRecord]:
        return tuple(self._incidents)

    def detect_compromise(
        self,
        *,
        lineage_id: str,
        compromised_signer_id: str,
        trigger_class: str,
        event_ts: str,
        force_state: Optional[str] = None,
    ) -> CompromiseDecision:
        if trigger_class not in SUPPORTED_TRIGGERS:
            raise ValueError(f"unsupported_trigger_class:{trigger_class}")

        state = force_state or STATE_BY_TRIGGER[trigger_class]
        if state not in {COMPROMISE_SUSPECTED, COMPROMISE_CONFIRMED}:
            raise ValueError(f"invalid_compromise_state:{state}")

        reason_code = self._reason_code(state, trigger_class)
        return CompromiseDecision(
            lineage_id=lineage_id,
            compromised_signer_id=compromised_signer_id,
            trigger_class=trigger_class,
            compromise_state=state,
            reason_code=reason_code,
            event_ts=event_ts,
        )

    def containment_sequence(self) -> Tuple[str, str, str]:
        sequence = tuple(REQUIRED_CONTAINMENT_SEQUENCE)
        self._validate_containment_sequence(sequence)
        return sequence

    def respond_to_compromise(
        self,
        *,
        lineage_id: str,
        compromised_signer_id: str,
        trigger_class: str,
        event_ts: str,
        containment_authorizer_signer_id: str,
        replacement_signer_id: Optional[str] = None,
        recovery_ticket_id: Optional[str] = None,
        recovery_authorizer_signer_id: Optional[str] = None,
        force_state: Optional[str] = None,
    ) -> CompromiseIncidentRecord:
        decision = self.detect_compromise(
            lineage_id=lineage_id,
            compromised_signer_id=compromised_signer_id,
            trigger_class=trigger_class,
            event_ts=event_ts,
            force_state=force_state,
        )

        containment = self.containment_sequence()
        recovery_attestation: Optional[str] = None

        if decision.compromise_state == COMPROMISE_CONFIRMED:
            self._require_recovery_inputs(
                replacement_signer_id=replacement_signer_id,
                recovery_ticket_id=recovery_ticket_id,
                recovery_authorizer_signer_id=recovery_authorizer_signer_id,
            )
            self._execute_confirmed_flow(
                decision=decision,
                containment_authorizer_signer_id=containment_authorizer_signer_id,
                replacement_signer_id=replacement_signer_id,
                recovery_ticket_id=recovery_ticket_id,
                recovery_authorizer_signer_id=recovery_authorizer_signer_id,
            )
            recovery_attestation = self._derive_recovery_attestation(
                lineage_id=lineage_id,
                replacement_signer_id=replacement_signer_id,
                recovery_ticket_id=recovery_ticket_id,
                reason_code=decision.reason_code,
            )

        incident = CompromiseIncidentRecord(
            incident_id=self._derive_incident_id(decision=decision),
            lineage_id=decision.lineage_id,
            compromised_signer_id=decision.compromised_signer_id,
            trigger_class=decision.trigger_class,
            compromise_state=decision.compromise_state,
            reason_code=decision.reason_code,
            containment_actions=containment,
            replacement_signer_id=replacement_signer_id,
            recovery_ticket_id=recovery_ticket_id,
            recovery_attestation=recovery_attestation,
            event_ts=decision.event_ts,
        )
        self._incidents.append(incident)
        return incident

    def _execute_confirmed_flow(
        self,
        *,
        decision: CompromiseDecision,
        containment_authorizer_signer_id: str,
        replacement_signer_id: str,
        recovery_ticket_id: str,
        recovery_authorizer_signer_id: str,
    ) -> None:
        entry = self._registry.entries.get(decision.lineage_id)
        if entry is None:
            raise ValueError(f"unknown_lineage:{decision.lineage_id}")

        if entry.operational_signer_key != decision.compromised_signer_id:
            raise ValueError("compromised_signer_mismatch")

        # phase_1573am_activation_prerequisite_transactional_revoke_recover:
        # before this default-off surface is wired to any live/public signing
        # path, revoke()+recover() must be wrapped in checkpoint/restore or an
        # equivalent transaction. If recover() raises after revoke(), this
        # lineage can remain REVOKED until an operator repairs state.
        self._registry.revoke(
            lineage_id=decision.lineage_id,
            authorizer_signer_id=containment_authorizer_signer_id,
            reason_code=decision.reason_code,
            event_ts=decision.event_ts,
        )

        # ROTATED is non-authoritative. Recover is required to restore canonical authority.
        self._registry.recover(
            lineage_id=decision.lineage_id,
            replacement_signer_id=replacement_signer_id,
            recovery_ticket_id=recovery_ticket_id,
            authorizer_signer_id=recovery_authorizer_signer_id,
            reason_code="recovery_authorized",
            event_ts=decision.event_ts,
        )

        post = self._registry.entries[decision.lineage_id]
        if post.state != RECOVERED:
            raise ValueError("replacement_lineage_not_recovered")

        authority = self._registry.verify_canonical_authority(
            canonical_root_key=post.canonical_root_key,
            lineage_id=decision.lineage_id,
            signer_id=replacement_signer_id,
        )
        if not authority.accepted:
            raise ValueError("replacement_lineage_not_authoritative")

    @staticmethod
    def _validate_containment_sequence(actions: Tuple[str, str, str]) -> None:
        if actions != REQUIRED_CONTAINMENT_SEQUENCE:
            raise ValueError("invalid_containment_sequence")

    @staticmethod
    def _require_recovery_inputs(
        *,
        replacement_signer_id: Optional[str],
        recovery_ticket_id: Optional[str],
        recovery_authorizer_signer_id: Optional[str],
    ) -> None:
        if not replacement_signer_id:
            raise ValueError("missing_replacement_signer_id")
        if not recovery_ticket_id:
            raise ValueError("missing_recovery_ticket_id")
        if not recovery_authorizer_signer_id:
            raise ValueError("missing_recovery_authorizer_signer_id")

    @staticmethod
    def _reason_code(compromise_state: str, trigger_class: str) -> str:
        return f"{compromise_state}_{trigger_class}"

    def _derive_incident_id(self, *, decision: CompromiseDecision) -> str:
        self._incident_counter += 1
        payload = (
            f"{decision.lineage_id}|{decision.compromised_signer_id}|{decision.trigger_class}|"
            f"{decision.compromise_state}|{decision.event_ts}|{self._incident_counter}"
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    @staticmethod
    def _derive_recovery_attestation(
        *,
        lineage_id: str,
        replacement_signer_id: str,
        recovery_ticket_id: str,
        reason_code: str,
    ) -> str:
        payload = (
            f"{lineage_id}|{replacement_signer_id}|{recovery_ticket_id}|{reason_code}"
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()
