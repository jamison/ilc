from __future__ import annotations

import pytest

from ilc_core.security.key_compromise_runtime import (
    TRIGGER_CUSTODY_LOSS,
    KeyCompromiseResponseRuntime,
)
from ilc_core.security.rollback_resistance_runtime import (
    CLAWBACK_REQUIRED,
    FINALIZATION_STATE_ROLLED_BACK,
    RollbackResistanceRuntime,
)
from ilc_core.security.signer_lineage_runtime import REVOKED, SignerLineageRegistry


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


def _rollback_event(*, signer_id: str, supersession_id: str = "sup-001") -> dict[str, str]:
    return {
        "supersession_id": supersession_id,
        "target_window_id": "epoch-window-42",
        "finalization_state": FINALIZATION_STATE_ROLLED_BACK,
        "clawback_policy": CLAWBACK_REQUIRED,
        "canonical_root_key": "root-001",
        "authorizing_lineage_id": "lineage-alpha",
        "authorizing_signer_id": signer_id,
        "reason_code": "rollback_reorg_detected",
        "event_ts": "2026-02-20T00:30:00Z",
    }


def test_compromise_revocation_then_verification_rejection(registry: SignerLineageRegistry) -> None:
    compromise = KeyCompromiseResponseRuntime(registry)
    decision = compromise.detect_compromise(
        lineage_id="lineage-alpha",
        compromised_signer_id="ops-001",
        trigger_class=TRIGGER_CUSTODY_LOSS,
        event_ts="2026-02-20T00:10:00Z",
    )

    registry.revoke(
        lineage_id="lineage-alpha",
        authorizer_signer_id="root-001",
        reason_code=decision.reason_code,
        event_ts=decision.event_ts,
    )

    assert registry.entries["lineage-alpha"].state == REVOKED

    authority = registry.verify_canonical_authority(
        canonical_root_key="root-001",
        lineage_id="lineage-alpha",
        signer_id="ops-001",
    )
    assert authority.accepted is False
    assert authority.reason == "revoked_lineage"


def test_rollback_against_revoked_signer_is_rejected(registry: SignerLineageRegistry) -> None:
    registry.revoke(
        lineage_id="lineage-alpha",
        authorizer_signer_id="root-001",
        reason_code="compromise_confirmed",
        event_ts="2026-02-20T00:11:00Z",
    )

    rollback = RollbackResistanceRuntime(registry)
    event = rollback.build_event_from_mapping(_rollback_event(signer_id="ops-001"))

    with pytest.raises(ValueError, match="unauthorized_supersession_signer:revoked_lineage"):
        rollback.apply_supersession_event(event)


def test_recover_then_valid_future_supersession_is_accepted(registry: SignerLineageRegistry) -> None:
    compromise = KeyCompromiseResponseRuntime(registry)

    incident = compromise.respond_to_compromise(
        lineage_id="lineage-alpha",
        compromised_signer_id="ops-001",
        trigger_class=TRIGGER_CUSTODY_LOSS,
        event_ts="2026-02-20T00:12:00Z",
        containment_authorizer_signer_id="root-001",
        replacement_signer_id="ops-002",
        recovery_ticket_id="ticket-001",
        recovery_authorizer_signer_id="recovery-001",
    )
    assert incident.recovery_attestation is not None

    rollback = RollbackResistanceRuntime(registry)
    event = rollback.build_event_from_mapping(_rollback_event(signer_id="ops-002"))

    rollback.apply_supersession_event(event)

    assert len(rollback.events) == 1
    assert rollback.events[0].supersession_id == "sup-001"


def test_validate_rejects_revoked_signer_unauthorized_supersession_path(
    registry: SignerLineageRegistry,
) -> None:
    registry.revoke(
        lineage_id="lineage-alpha",
        authorizer_signer_id="root-001",
        reason_code="compromise_confirmed",
        event_ts="2026-02-20T00:13:00Z",
    )

    rollback = RollbackResistanceRuntime(registry)
    event = rollback.build_event_from_mapping(_rollback_event(signer_id="ops-001", supersession_id="sup-002"))

    with pytest.raises(ValueError, match="unauthorized_supersession_signer:revoked_lineage"):
        rollback.validate_supersession_event(event)
