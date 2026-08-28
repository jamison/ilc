# SPDX-License-Identifier: AGPL-3.0-only
"""Relay/rendezvous client package.

The relay client remains inactive until the relay deployment phase clears the
guard in :mod:`ilc_core.network.relay.relay_client`.
"""

from ilc_core.network.relay.relay_client import (
    RELAY_CLIENT_NOT_ACTIVATED,
    RELAY_CLIENT_SCHEMA_VERSION,
    RelayAdmissionRequest,
    RelayClient,
    RelayClientError,
    RelayEndpoint,
    RelayKeepaliveReceipt,
    RelayReleaseReceipt,
    RelaySlotGrant,
)

__all__ = [
    "RELAY_CLIENT_NOT_ACTIVATED",
    "RELAY_CLIENT_SCHEMA_VERSION",
    "RelayAdmissionRequest",
    "RelayClient",
    "RelayClientError",
    "RelayEndpoint",
    "RelayKeepaliveReceipt",
    "RelayReleaseReceipt",
    "RelaySlotGrant",
]
