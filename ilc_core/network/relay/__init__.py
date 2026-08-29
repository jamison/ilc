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
from ilc_core.network.relay.relay_server import (
    RELAY_SERVER_NOT_ACTIVATED,
    RELAY_SERVER_SCHEMA_VERSION,
    RELAY_SERVER_TOKEN,
    RelayForwardReceipt,
    RelayRendezvousServer,
    RelayServerConfig,
    RelayServerError,
    RelayUdpDatagramProtocol,
    RelayUdpForwarder,
)

__all__ = [
    "RELAY_CLIENT_NOT_ACTIVATED",
    "RELAY_CLIENT_SCHEMA_VERSION",
    "RELAY_SERVER_NOT_ACTIVATED",
    "RELAY_SERVER_SCHEMA_VERSION",
    "RELAY_SERVER_TOKEN",
    "RelayAdmissionRequest",
    "RelayClient",
    "RelayClientError",
    "RelayEndpoint",
    "RelayForwardReceipt",
    "RelayKeepaliveReceipt",
    "RelayReleaseReceipt",
    "RelayRendezvousServer",
    "RelayServerConfig",
    "RelayServerError",
    "RelayUdpDatagramProtocol",
    "RelaySlotGrant",
    "RelayUdpForwarder",
]
