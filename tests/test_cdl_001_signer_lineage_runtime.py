from __future__ import annotations

from ilc_core.security.signer_lineage_runtime import (
    ACTIVE,
    RECOVERED,
    REVOKED,
    ROTATED,
    SignerLineageRegistry,
)


class TestLineageChainValidation:
    def test_lineage_chain_validation_accepts_trust_root_and_operational_signer(self) -> None:
        registry = SignerLineageRegistry()
        registry.register(
            lineage_id="lineage-alpha",
            canonical_root_key="root-001",
            authority_recovery_key="recovery-001",
            operational_signer_key="ops-001",
            authorizer_signer_id="root-001",
            reason_code="genesis_register",
            event_ts="2026-02-20T00:00:00Z",
        )

        result = registry.validate_lineage_chain(
            canonical_root_key="root-001",
            lineage_id="lineage-alpha",
            operational_signer_key="ops-001",
        )

        assert result.accepted is True
        assert result.reason == "lineage_chain_valid"

    def test_lineage_chain_validation_rejects_non_anchored_lineage(self) -> None:
        registry = SignerLineageRegistry()
        registry.register(
            lineage_id="lineage-alpha",
            canonical_root_key="root-001",
            authority_recovery_key="recovery-001",
            operational_signer_key="ops-001",
            authorizer_signer_id="root-001",
            reason_code="genesis_register",
            event_ts="2026-02-20T00:00:00Z",
        )

        result = registry.validate_lineage_chain(
            canonical_root_key="root-foreign",
            lineage_id="lineage-alpha",
            operational_signer_key="ops-001",
        )

        assert result.accepted is False
        assert result.reason == "non_anchored_lineage"


class TestRevokedLineageSignerRejection:
    def test_canonical_verification_rejects_revoked_lineage(self) -> None:
        registry = SignerLineageRegistry()
        registry.register(
            lineage_id="lineage-alpha",
            canonical_root_key="root-001",
            authority_recovery_key="recovery-001",
            operational_signer_key="ops-001",
            authorizer_signer_id="root-001",
            reason_code="genesis_register",
            event_ts="2026-02-20T00:00:00Z",
        )
        registry.revoke(
            lineage_id="lineage-alpha",
            authorizer_signer_id="root-001",
            reason_code="compromise_confirmed",
            event_ts="2026-02-20T00:05:00Z",
        )

        result = registry.verify_canonical_authority(
            canonical_root_key="root-001",
            lineage_id="lineage-alpha",
            signer_id="ops-001",
        )

        assert result.accepted is False
        assert result.reason == "revoked_lineage"


class TestLifecycleTransitionCoverage:
    def test_lifecycle_transition_active_rotated_revoked_recovered(self) -> None:
        registry = SignerLineageRegistry()

        registry.register(
            lineage_id="lineage-alpha",
            canonical_root_key="root-001",
            authority_recovery_key="recovery-001",
            operational_signer_key="ops-001",
            authorizer_signer_id="root-001",
            reason_code="genesis_register",
            event_ts="2026-02-20T00:00:00Z",
        )
        assert registry.entries["lineage-alpha"].state == ACTIVE

        registry.rotate(
            lineage_id="lineage-alpha",
            replacement_signer_id="ops-002",
            authorizer_signer_id="root-001",
            reason_code="scheduled_rotation",
            event_ts="2026-02-20T00:01:00Z",
        )
        assert registry.entries["lineage-alpha"].state == ROTATED

        registry.revoke(
            lineage_id="lineage-alpha",
            authorizer_signer_id="root-001",
            reason_code="compromise_confirmed",
            event_ts="2026-02-20T00:02:00Z",
        )
        assert registry.entries["lineage-alpha"].state == REVOKED

        checkpoint = registry.create_checkpoint()

        registry.recover(
            lineage_id="lineage-alpha",
            replacement_signer_id="ops-003",
            recovery_ticket_id="ticket-001",
            authorizer_signer_id="recovery-001",
            reason_code="recovery_authorized",
            event_ts="2026-02-20T00:03:00Z",
        )
        assert registry.entries["lineage-alpha"].state == RECOVERED

        # Reversible checkpoint allows fallback to a known-valid registry state.
        registry.restore_checkpoint(checkpoint)
        assert registry.entries["lineage-alpha"].state == REVOKED

    def test_append_only_transition_log_is_replayable(self) -> None:
        registry = SignerLineageRegistry()
        registry.register(
            lineage_id="lineage-alpha",
            canonical_root_key="root-001",
            authority_recovery_key="recovery-001",
            operational_signer_key="ops-001",
            authorizer_signer_id="root-001",
            reason_code="genesis_register",
            event_ts="2026-02-20T00:00:00Z",
        )
        registry.rotate(
            lineage_id="lineage-alpha",
            replacement_signer_id="ops-002",
            authorizer_signer_id="root-001",
            reason_code="scheduled_rotation",
            event_ts="2026-02-20T00:01:00Z",
        )
        registry.revoke(
            lineage_id="lineage-alpha",
            authorizer_signer_id="root-001",
            reason_code="compromise_confirmed",
            event_ts="2026-02-20T00:02:00Z",
        )

        replayed = SignerLineageRegistry.replay_from_log(registry.transition_log)

        assert len(registry.transition_log) == 3
        assert len(replayed.transition_log) == 3
        assert replayed.entries["lineage-alpha"].state == REVOKED


class TestVerifyCanonicalAuthorityStateGating:
    """Verify that only ACTIVE and RECOVERED states confer canonical signing authority."""

    def _base_registry(self) -> SignerLineageRegistry:
        registry = SignerLineageRegistry()
        registry.register(
            lineage_id="lineage-alpha",
            canonical_root_key="root-001",
            authority_recovery_key="recovery-001",
            operational_signer_key="ops-001",
            authorizer_signer_id="root-001",
            reason_code="genesis_register",
            event_ts="2026-02-20T00:00:00Z",
        )
        return registry

    def test_verify_canonical_authority_accepts_active_state(self) -> None:
        registry = self._base_registry()
        assert registry.entries["lineage-alpha"].state == ACTIVE

        result = registry.verify_canonical_authority(
            canonical_root_key="root-001",
            lineage_id="lineage-alpha",
            signer_id="ops-001",
        )

        assert result.accepted is True
        assert result.reason == "accepted"

    def test_verify_canonical_authority_rejects_rotated_state(self) -> None:
        registry = self._base_registry()
        registry.rotate(
            lineage_id="lineage-alpha",
            replacement_signer_id="ops-002",
            authorizer_signer_id="root-001",
            reason_code="scheduled_rotation",
            event_ts="2026-02-20T00:01:00Z",
        )
        assert registry.entries["lineage-alpha"].state == ROTATED

        result = registry.verify_canonical_authority(
            canonical_root_key="root-001",
            lineage_id="lineage-alpha",
            signer_id="ops-002",
        )

        assert result.accepted is False
        assert result.reason == "lineage_not_canonical_authority_state"

    def test_verify_canonical_authority_accepts_recovered_state(self) -> None:
        registry = self._base_registry()
        registry.revoke(
            lineage_id="lineage-alpha",
            authorizer_signer_id="root-001",
            reason_code="compromise_confirmed",
            event_ts="2026-02-20T00:01:00Z",
        )
        registry.recover(
            lineage_id="lineage-alpha",
            replacement_signer_id="ops-002",
            recovery_ticket_id="ticket-001",
            authorizer_signer_id="recovery-001",
            reason_code="recovery_authorized",
            event_ts="2026-02-20T00:02:00Z",
        )
        assert registry.entries["lineage-alpha"].state == RECOVERED

        result = registry.verify_canonical_authority(
            canonical_root_key="root-001",
            lineage_id="lineage-alpha",
            signer_id="ops-002",
        )

        assert result.accepted is True
        assert result.reason == "accepted"

