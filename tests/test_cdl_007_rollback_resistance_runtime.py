from __future__ import annotations

import pytest

from ilc_core.security.rollback_resistance_runtime import (
    CLAWBACK_NOT_REQUIRED,
    CLAWBACK_REQUIRED,
    FINALIZATION_STATE_ROLLED_BACK,
    RollbackResistanceRuntime,
)
from ilc_core.security.signer_lineage_runtime import SignerLineageRegistry


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


def _event_payload(**overrides: str) -> dict[str, str]:
    payload = {
        "supersession_id": "sup-001",
        "target_window_id": "epoch-window-42",
        "finalization_state": FINALIZATION_STATE_ROLLED_BACK,
        "clawback_policy": CLAWBACK_REQUIRED,
        "canonical_root_key": "root-001",
        "authorizing_lineage_id": "lineage-alpha",
        "authorizing_signer_id": "ops-001",
        "reason_code": "rollback_reorg_detected",
        "event_ts": "2026-02-20T00:30:00Z",
    }
    payload.update(overrides)
    return payload


class TestRollbackSupersessionEventFormatValidation:
    def test_build_event_requires_all_supersession_tokens(self, registry: SignerLineageRegistry) -> None:
        runtime = RollbackResistanceRuntime(registry)
        payload = _event_payload()
        del payload["finalization_state"]

        with pytest.raises(ValueError, match="missing_supersession_tokens:finalization_state"):
            runtime.build_event_from_mapping(payload)

    def test_validate_event_rejects_non_rolled_back_finalization_state(self, registry: SignerLineageRegistry) -> None:
        runtime = RollbackResistanceRuntime(registry)
        event = runtime.build_event_from_mapping(_event_payload(finalization_state="committed"))

        with pytest.raises(ValueError, match="invalid_finalization_state"):
            runtime.validate_supersession_event(event)


class TestClawbackDeclarationTokenValidation:
    @pytest.mark.parametrize("policy", [CLAWBACK_REQUIRED, CLAWBACK_NOT_REQUIRED])
    def test_validate_event_accepts_allowed_clawback_policies(
        self,
        registry: SignerLineageRegistry,
        policy: str,
    ) -> None:
        runtime = RollbackResistanceRuntime(registry)
        event = runtime.build_event_from_mapping(_event_payload(clawback_policy=policy))

        runtime.validate_supersession_event(event)

    def test_validate_event_rejects_invalid_clawback_policy(self, registry: SignerLineageRegistry) -> None:
        runtime = RollbackResistanceRuntime(registry)
        event = runtime.build_event_from_mapping(_event_payload(clawback_policy="invalid_policy"))

        with pytest.raises(ValueError, match="invalid_clawback_policy"):
            runtime.validate_supersession_event(event)


class TestNegativePathReplayRejection:
    def test_apply_supersession_rejects_replayed_identifier(self, registry: SignerLineageRegistry) -> None:
        runtime = RollbackResistanceRuntime(registry)
        event = runtime.build_event_from_mapping(_event_payload())

        runtime.apply_supersession_event(event)

        with pytest.raises(ValueError, match="replayed_supersession_identifier"):
            runtime.apply_supersession_event(event)


class TestNegativePathConflictRejection:
    def test_apply_supersession_rejects_conflicting_chain_for_same_window(self, registry: SignerLineageRegistry) -> None:
        runtime = RollbackResistanceRuntime(registry)

        event_one = runtime.build_event_from_mapping(_event_payload(supersession_id="sup-001"))
        runtime.apply_supersession_event(event_one)

        event_two = runtime.build_event_from_mapping(_event_payload(supersession_id="sup-002"))
        with pytest.raises(ValueError, match="conflicting_supersession_chain"):
            runtime.apply_supersession_event(event_two)
