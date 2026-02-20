from __future__ import annotations

import pytest

from ilc_core.security.key_compromise_runtime import (
    COMPROMISE_CONFIRMED,
    COMPROMISE_SUSPECTED,
    FREEZE_AUTHORITY,
    QUARANTINE_LINEAGE,
    SUSPEND_NEW_CANONICAL_SIGNATURES,
    TRIGGER_COERCION_SIGNAL,
    TRIGGER_CRYPTO_COMPROMISE,
    TRIGGER_CUSTODY_LOSS,
    TRIGGER_SIGNER_ANOMALY,
    KeyCompromiseResponseRuntime,
)
from ilc_core.security.signer_lineage_runtime import RECOVERED, SignerLineageRegistry


@pytest.fixture
def registry() -> SignerLineageRegistry:
    reg = SignerLineageRegistry()
    reg.register(
        lineage_id="lineage-alpha",
        canonical_root_key="root-001",
        authority_recovery_key="recovery-001",
        operational_signer_key="ops-001",
        authorizer_signer_id="root-001",
        reason_code="genesis_register",
        event_ts="2026-02-20T00:00:00Z",
    )
    return reg


class TestCompromiseTriggerDetection:
    @pytest.mark.parametrize(
        ("trigger", "expected_state", "expected_reason"),
        [
            (TRIGGER_SIGNER_ANOMALY, COMPROMISE_SUSPECTED, "suspected_signer_anomaly"),
            (TRIGGER_CUSTODY_LOSS, COMPROMISE_CONFIRMED, "confirmed_custody_loss"),
            (TRIGGER_COERCION_SIGNAL, COMPROMISE_CONFIRMED, "confirmed_coercion_signal"),
            (TRIGGER_CRYPTO_COMPROMISE, COMPROMISE_CONFIRMED, "confirmed_crypto_compromise"),
        ],
    )
    def test_detect_compromise_supports_all_required_trigger_classes(
        self,
        registry: SignerLineageRegistry,
        trigger: str,
        expected_state: str,
        expected_reason: str,
    ) -> None:
        runtime = KeyCompromiseResponseRuntime(registry)

        decision = runtime.detect_compromise(
            lineage_id="lineage-alpha",
            compromised_signer_id="ops-001",
            trigger_class=trigger,
            event_ts="2026-02-20T00:10:00Z",
        )

        assert decision.compromise_state == expected_state
        assert decision.reason_code == expected_reason


class TestContainmentActionSequencing:
    def test_containment_sequence_is_strict_and_ordered(self, registry: SignerLineageRegistry) -> None:
        runtime = KeyCompromiseResponseRuntime(registry)

        sequence = runtime.containment_sequence()

        assert sequence == (
            FREEZE_AUTHORITY,
            QUARANTINE_LINEAGE,
            SUSPEND_NEW_CANONICAL_SIGNATURES,
        )
        assert len(sequence) == 3

    def test_incident_record_emits_ordered_containment_actions(self, registry: SignerLineageRegistry) -> None:
        runtime = KeyCompromiseResponseRuntime(registry)

        incident = runtime.respond_to_compromise(
            lineage_id="lineage-alpha",
            compromised_signer_id="ops-001",
            trigger_class=TRIGGER_SIGNER_ANOMALY,
            event_ts="2026-02-20T00:10:00Z",
            containment_authorizer_signer_id="root-001",
        )

        assert incident.compromise_state == COMPROMISE_SUSPECTED
        assert incident.containment_actions == (
            FREEZE_AUTHORITY,
            QUARANTINE_LINEAGE,
            SUSPEND_NEW_CANONICAL_SIGNATURES,
        )


class TestRecoverySequenceIntegrity:
    def test_confirmed_compromise_uses_revoke_then_recover_and_restores_authority(
        self,
        registry: SignerLineageRegistry,
    ) -> None:
        runtime = KeyCompromiseResponseRuntime(registry)

        incident = runtime.respond_to_compromise(
            lineage_id="lineage-alpha",
            compromised_signer_id="ops-001",
            trigger_class=TRIGGER_CUSTODY_LOSS,
            event_ts="2026-02-20T00:11:00Z",
            containment_authorizer_signer_id="root-001",
            replacement_signer_id="ops-002",
            recovery_ticket_id="ticket-001",
            recovery_authorizer_signer_id="recovery-001",
        )

        assert incident.compromise_state == COMPROMISE_CONFIRMED
        assert registry.entries["lineage-alpha"].state == RECOVERED

        # ROTATED is intentionally non-authoritative; replacement is authoritative only after recover.
        auth = registry.verify_canonical_authority(
            canonical_root_key="root-001",
            lineage_id="lineage-alpha",
            signer_id="ops-002",
        )
        assert auth.accepted is True
        assert auth.reason == "accepted"

        event_names = [record.event_name for record in registry.transition_log[-2:]]
        assert event_names == ["revoke", "recover"]


class TestIncidentAuditRecordEmission:
    def test_incident_record_has_deterministic_reason_code_and_attestation(
        self,
        registry: SignerLineageRegistry,
    ) -> None:
        runtime = KeyCompromiseResponseRuntime(registry)

        incident = runtime.respond_to_compromise(
            lineage_id="lineage-alpha",
            compromised_signer_id="ops-001",
            trigger_class=TRIGGER_COERCION_SIGNAL,
            event_ts="2026-02-20T00:12:00Z",
            containment_authorizer_signer_id="root-001",
            replacement_signer_id="ops-003",
            recovery_ticket_id="ticket-002",
            recovery_authorizer_signer_id="recovery-001",
        )

        assert incident.reason_code == "confirmed_coercion_signal"
        assert incident.incident_id
        assert incident.recovery_attestation

        # Deterministic reason code is reproduced by detection pipeline for same trigger/state.
        decision = runtime.detect_compromise(
            lineage_id="lineage-alpha",
            compromised_signer_id="ops-003",
            trigger_class=TRIGGER_COERCION_SIGNAL,
            event_ts="2026-02-20T00:13:00Z",
        )
        assert decision.reason_code == incident.reason_code
