# SPDX-License-Identifier: AGPL-3.0-only
"""Default-off invite enforcement gate for agent enrollment.

Phase 1576n implements the enforcement boundary without activating it. The guard
must remain False until a later SENSITIVE public-RC guard-clearance phase.
"""

from __future__ import annotations

from typing import Callable, Mapping

from ilc_core.epoch.genesis_settlement_destination import GENESIS_AGENT1_AGENT_ID
from ilc_core.genesis.invite_nullifier_registry import InviteNullifierRegistry

INVITE_ENFORCEMENT_RUNTIME_VERSION = "invite_enforcement_gate_1576n.v0.1"
INVITE_ENFORCEMENT_ENABLED: bool = True


def is_enrollment_invite_enforced() -> bool:
    """Return the live invite-enforcement guard state."""

    return bool(INVITE_ENFORCEMENT_ENABLED)


def require_invite_for_enrollment(
    agent_id: str,
    invite_redemption_record: object | Mapping[str, object] | None,
    *,
    nullifier_registry: InviteNullifierRegistry | None = None,
    register_nullifier: bool = False,
    invite_pop_verifier: Callable[..., bool] | None = None,
    require_redeemer_key_binding: bool = True,
) -> None:
    """Require a valid invite redemption record for new agent enrollment.

    The gate is a no-op while ``INVITE_ENFORCEMENT_ENABLED`` is False. When the
    guard is later cleared, Genesis Agent 1 remains exempt because its identity
    predates invite-gated enrollment.
    """

    if not INVITE_ENFORCEMENT_ENABLED:
        return
    if agent_id == GENESIS_AGENT1_AGENT_ID:
        return
    if invite_redemption_record is None:
        raise ValueError("invite_required_for_enrollment")

    from ilc_core.genesis.invitation_provenance_record import (
        validate_invite_redemption_record,
        verify_invite_redemption_redeemer_key_binding,
    )

    record = validate_invite_redemption_record(invite_redemption_record)
    if not isinstance(agent_id, str) or not agent_id:
        raise ValueError("invite_enrollment_agent_id_required")
    if record.redeemer_agent_id != agent_id:
        raise ValueError("invite_redeemer_agent_id_mismatch")
    if register_nullifier and nullifier_registry is None:
        raise ValueError("invite_nullifier_registry_required_for_registration")
    if nullifier_registry is not None and nullifier_registry.is_known(record.redemption_nullifier):
        raise ValueError("invite_nullifier_already_used_for_enrollment")
    if require_redeemer_key_binding:
        verify_invite_redemption_redeemer_key_binding(
            record,
            invite_pop_verifier=invite_pop_verifier,
        )
    if register_nullifier and nullifier_registry is not None:
        nullifier_registry.register_nullifier(record.redemption_nullifier)


__all__ = [
    "INVITE_ENFORCEMENT_ENABLED",
    "INVITE_ENFORCEMENT_RUNTIME_VERSION",
    "is_enrollment_invite_enforced",
    "require_invite_for_enrollment",
]
