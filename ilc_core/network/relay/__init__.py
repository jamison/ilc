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
    relay_slot_claim_datagram,
)
from ilc_core.network.relay.relay_server import (
    RELAY_ABUSE_LIMITS_SCHEMA_VERSION,
    RELAY_SERVER_NOT_ACTIVATED,
    RELAY_SERVER_SCHEMA_VERSION,
    RELAY_SERVER_TOKEN,
    RelayDataPlaneRuntime,
    RelayForwardReceipt,
    RelayRendezvousServer,
    RelayRevocationReceipt,
    RelayServerConfig,
    RelayServerError,
    RelayUdpForwarder,
    RelayUdpPortForwarder,
    build_relay_bootstrap_record,
    parse_relay_bootstrap_capsule,
    sign_relay_bootstrap_record,
    verify_relay_bootstrap_record,
)

__all__ = [
    "RELAY_CLIENT_NOT_ACTIVATED",
    "RELAY_CLIENT_SCHEMA_VERSION",
    "RELAY_ABUSE_LIMITS_SCHEMA_VERSION",
    "RELAY_SERVER_NOT_ACTIVATED",
    "RELAY_SERVER_SCHEMA_VERSION",
    "RELAY_SERVER_TOKEN",
    "RelayAdmissionRequest",
    "RelayClient",
    "RelayClientError",
    "RelayDataPlaneRuntime",
    "RelayEndpoint",
    "RelayForwardReceipt",
    "RelayKeepaliveReceipt",
    "RelayReleaseReceipt",
    "RelayRendezvousServer",
    "RelayRevocationReceipt",
    "RelayServerConfig",
    "RelayServerError",
    "RelaySlotGrant",
    "relay_slot_claim_datagram",
    "RelayUdpForwarder",
    "RelayUdpPortForwarder",
    "build_relay_bootstrap_record",
    "parse_relay_bootstrap_capsule",
    "sign_relay_bootstrap_record",
    "verify_relay_bootstrap_record",
]
