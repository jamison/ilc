# SPDX-License-Identifier: AGPL-3.0-only
"""CDL-112 ConnectivityAdvertisement protocol sidecar.

This sidecar owns the signed reachability advertisement and revocation schemas.
It does not grant validator admission, endpoint authority, relay incentives, or
settlement eligibility.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from ilc_core.crypto.pq_signature_verify import (
    _MLDSA_PK_HEX_LENGTH,
    _MLDSA_SIG_HEX_LENGTH,
)
from ilc_core.network.connectivity_mode import ConnectivityMode, ConnectivityReceipt
from ilc_core.network.d2d.peer_advertisement import (
    MAX_CONTENT_AVAILABILITY_COUNT,
    MAX_PEER_ADVERTISEMENT_EPOCH,
    MAX_PEER_TIMESTAMP_FUTURE_SKEW_EPOCHS,
    MAX_TTL_EPOCHS,
    TransportEndpoint,
)


CONNECTIVITY_ADVERTISEMENT_SCHEMA_VERSION = "connectivity_advertisement_cdl112.v0.1"
CONNECTIVITY_ADVERTISEMENT_SIDECAR_VERSION = (
    "connectivity_advertisement_sidecar_GAP_PEER_CONNECTIVITY_ADVERTISEMENT_IMPL_00.v0.1"
)
CONNECTIVITY_ADVERTISEMENT_TOMBSTONE_SCHEMA_VERSION = (
    "connectivity_advertisement_tombstone_cdl112.v0.1"
)
CONNECTIVITY_ADVERTISEMENT_GOSSIP_SCHEMA_VERSION = (
    "connectivity_advertisement_gossip_message_cdl112.v0.1"
)
CONNECTIVITY_ADVERTISEMENT_TOMBSTONE_GOSSIP_SCHEMA_VERSION = (
    "connectivity_advertisement_tombstone_gossip_message_cdl112.v0.1"
)
CONNECTIVITY_ADVERTISEMENT_GOSSIP_MESSAGE_TYPE = "connectivity_advertisement"
CONNECTIVITY_ADVERTISEMENT_TOMBSTONE_GOSSIP_MESSAGE_TYPE = (
    "connectivity_advertisement_tombstone"
)
CONNECTIVITY_ADVERTISEMENT_RUNTIME_TOKEN = (
    "connectivity_advertisement_runtime_committed_GAP_PEER_CONNECTIVITY_ADVERTISEMENT_IMPL_00"
)
CONNECTIVITY_ADVERTISEMENT_NOT_ACTIVATED = False
CONNECTIVITY_ADVERTISEMENT_VERIFICATION_CONTEXT = "mldsa65_signature_verified_cdl112"
CONNECTIVITY_ADVERTISEMENT_TOMBSTONE_VERIFICATION_CONTEXT = (
    "mldsa65_tombstone_signature_verified_cdl112"
)
CONNECTIVITY_ADVERTISEMENT_AUTHORITY_GATE = (
    "CDL-112 ratified GAP-CDL-112-RATIFY-00; "
    "CONNECTIVITY_ADVERTISEMENT_NOT_ACTIVATED=False; "
    "activated GAP-CONNECTIVITY-ADVERTISEMENT-ACTIVATE-00"
)
MAX_CANDIDATE_ENDPOINTS = 3

_SHA384_HEX_RE = re.compile(r"^[0-9a-f]{96}$")
_LOWER_HEX_RE = re.compile(r"^[0-9a-f]+$")
_MAX_PROTOCOL_VERSION_CHARS = 64
_MAX_KEY_BINDING_REF_CHARS = 256
_MAX_RELAY_SLOT_REF_CHARS = 256
_RELAY_MODES = frozenset(
    {
        ConnectivityMode.RELAY_REACHABLE,
        ConnectivityMode.VALIDATOR_OBSERVER_RELAY,
        ConnectivityMode.VALIDATOR_RELAY,
    }
)
_DIRECT_MODES = frozenset(
    {
        ConnectivityMode.NAT_TRAVERSED_DIRECT,
        ConnectivityMode.DIRECT_PUBLIC,
        ConnectivityMode.VALIDATOR_OBSERVER_DIRECT,
        ConnectivityMode.VALIDATOR_DIRECT,
    }
)
_NON_ADVERTISING_MODES = frozenset(
    {
        ConnectivityMode.LOCAL_ONLY,
        ConnectivityMode.OUTBOUND_ONLY,
    }
)


class ConnectivityAdvertisementValidationError(ValueError):
    """Stable validation error for malformed CDL-112 advertisements."""


@dataclass(frozen=True)
class ConnectivityAdvertisement:
    agent_id: str
    transport_endpoint: TransportEndpoint
    protocol_version: str
    installed_slices_digest: str
    content_availability_count: int
    peer_timestamp_epoch: int
    ttl_epochs: int
    connectivity_mode: ConnectivityMode
    relay_endpoint: TransportEndpoint | None
    candidate_list: tuple[TransportEndpoint, ...]
    probe_receipt_ref: str | None
    relay_slot_ref: str | None
    ml_dsa_signature: str
    key_binding_ref: str
    schema_version: str = CONNECTIVITY_ADVERTISEMENT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _require_sha384_hex(self.agent_id, "connectivity_advertisement_agent_id_invalid")
        _require_sha384_hex(
            self.installed_slices_digest,
            "connectivity_advertisement_installed_slices_digest_invalid",
        )
        _require_string(
            self.protocol_version,
            "connectivity_advertisement_protocol_version_invalid",
            max_chars=_MAX_PROTOCOL_VERSION_CHARS,
        )
        _require_uint64(
            self.content_availability_count,
            "connectivity_advertisement_content_availability_count_invalid",
            max_value=MAX_CONTENT_AVAILABILITY_COUNT,
        )
        _require_uint64(
            self.peer_timestamp_epoch,
            "connectivity_advertisement_timestamp_epoch_invalid",
            max_value=MAX_PEER_ADVERTISEMENT_EPOCH,
        )
        _require_uint64(
            self.ttl_epochs,
            "connectivity_advertisement_ttl_epochs_invalid",
            min_value=1,
            max_value=MAX_TTL_EPOCHS,
        )
        mode = _coerce_mode(self.connectivity_mode)
        object.__setattr__(self, "connectivity_mode", mode)
        _require_lower_hex_exact(
            self.ml_dsa_signature,
            _MLDSA_SIG_HEX_LENGTH,
            "connectivity_advertisement_signature_invalid",
        )
        _require_string(
            self.key_binding_ref,
            "connectivity_advertisement_key_binding_ref_invalid",
            max_chars=_MAX_KEY_BINDING_REF_CHARS,
        )
        if self.schema_version != CONNECTIVITY_ADVERTISEMENT_SCHEMA_VERSION:
            raise ConnectivityAdvertisementValidationError(
                "connectivity_advertisement_schema_version_unsupported"
            )
        if self.probe_receipt_ref is not None:
            _require_sha384_hex(
                self.probe_receipt_ref,
                "connectivity_advertisement_probe_receipt_ref_invalid",
            )
        if self.relay_slot_ref is not None:
            _require_string(
                self.relay_slot_ref,
                "connectivity_advertisement_relay_slot_ref_invalid",
                max_chars=_MAX_RELAY_SLOT_REF_CHARS,
            )
        if not isinstance(self.transport_endpoint, TransportEndpoint):
            raise ConnectivityAdvertisementValidationError(
                "connectivity_advertisement_transport_endpoint_invalid"
            )
        if self.relay_endpoint is not None and not isinstance(
            self.relay_endpoint,
            TransportEndpoint,
        ):
            raise ConnectivityAdvertisementValidationError(
                "connectivity_advertisement_relay_endpoint_invalid"
            )
        if not isinstance(self.candidate_list, tuple):
            try:
                object.__setattr__(self, "candidate_list", tuple(self.candidate_list))
            except TypeError as exc:
                raise ConnectivityAdvertisementValidationError(
                    "connectivity_advertisement_candidate_list_invalid"
                ) from exc
        _validate_candidate_list(self.transport_endpoint, self.candidate_list)
        _validate_mode_endpoint_consistency(
            mode,
            relay_endpoint=self.relay_endpoint,
            relay_slot_ref=self.relay_slot_ref,
        )

    def body_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "candidate_list": [endpoint.to_dict() for endpoint in self.candidate_list],
            "connectivity_mode": self.connectivity_mode.value,
            "content_availability_count": self.content_availability_count,
            "installed_slices_digest": self.installed_slices_digest,
            "peer_timestamp_epoch": self.peer_timestamp_epoch,
            "probe_receipt_ref": self.probe_receipt_ref,
            "protocol_version": self.protocol_version,
            "relay_endpoint": (
                None if self.relay_endpoint is None else self.relay_endpoint.to_dict()
            ),
            "relay_slot_ref": self.relay_slot_ref,
            "schema_version": self.schema_version,
            "transport_endpoint": self.transport_endpoint.to_dict(),
            "ttl_epochs": self.ttl_epochs,
        }

    def to_canonical_json(self) -> bytes:
        """Return the canonical ML-DSA signature preimage for the body only."""

        return json.dumps(
            self.body_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")

    def to_dict(self) -> dict[str, Any]:
        return {
            "body": self.body_dict(),
            "key_binding_ref": self.key_binding_ref,
            "ml_dsa_signature": self.ml_dsa_signature,
            "schema_version": self.schema_version,
        }

    def verify(
        self,
        ml_dsa_verify_fn: Callable[[bytes, str, str], bool],
        *,
        pubkey_hex: str,
    ) -> bool:
        """Verify the ML-DSA-65 signature against an explicit bound public key."""

        try:
            _require_lower_hex_exact(
                pubkey_hex,
                _MLDSA_PK_HEX_LENGTH,
                "connectivity_advertisement_pubkey_invalid",
            )
            return bool(
                ml_dsa_verify_fn(
                    self.to_canonical_json(),
                    self.ml_dsa_signature,
                    pubkey_hex,
                )
            )
        except Exception:  # noqa: BLE001 - verification must fail closed.
            return False

    def is_expired(self, current_epoch: int) -> bool:
        current = _require_uint64(
            current_epoch,
            "connectivity_advertisement_current_epoch_invalid",
            max_value=MAX_PEER_ADVERTISEMENT_EPOCH,
        )
        return self.peer_timestamp_epoch + self.ttl_epochs <= current

    @property
    def endpoint_url(self) -> str:
        return self.transport_endpoint.to_url()

    @classmethod
    def from_dict(
        cls,
        value: Mapping[str, Any],
        *,
        allow_private_address_literals: bool = False,
    ) -> "ConnectivityAdvertisement":
        if not isinstance(value, Mapping):
            raise ConnectivityAdvertisementValidationError(
                "connectivity_advertisement_not_mapping"
            )
        allowed = {"body", "key_binding_ref", "ml_dsa_signature", "schema_version"}
        _reject_missing_or_extra(value, allowed, "connectivity_advertisement")
        schema_version = _require_string(
            value.get("schema_version"),
            "connectivity_advertisement_schema_version_invalid",
            max_chars=80,
        )
        if schema_version != CONNECTIVITY_ADVERTISEMENT_SCHEMA_VERSION:
            raise ConnectivityAdvertisementValidationError(
                "connectivity_advertisement_schema_version_unsupported"
            )
        body = value.get("body")
        if not isinstance(body, Mapping):
            raise ConnectivityAdvertisementValidationError(
                "connectivity_advertisement_body_invalid"
            )
        allowed_body = {
            "agent_id",
            "candidate_list",
            "connectivity_mode",
            "content_availability_count",
            "installed_slices_digest",
            "peer_timestamp_epoch",
            "probe_receipt_ref",
            "protocol_version",
            "relay_endpoint",
            "relay_slot_ref",
            "schema_version",
            "transport_endpoint",
            "ttl_epochs",
        }
        _reject_missing_or_extra(body, allowed_body, "connectivity_advertisement_body")
        if body.get("schema_version") != schema_version:
            raise ConnectivityAdvertisementValidationError(
                "connectivity_advertisement_schema_version_mismatch"
            )
        mode = _coerce_mode(body.get("connectivity_mode"))
        relay_endpoint = _optional_endpoint_from_mapping(
            body.get("relay_endpoint"),
            allow_private_address_literals=allow_private_address_literals,
            token="connectivity_advertisement_relay_endpoint_invalid",
        )
        candidates = _candidate_list_from_sequence(
            body.get("candidate_list"),
            allow_private_address_literals=allow_private_address_literals,
        )
        probe_receipt_ref = body.get("probe_receipt_ref")
        relay_slot_ref = body.get("relay_slot_ref")
        return cls(
            agent_id=_require_sha384_hex(
                body.get("agent_id"),
                "connectivity_advertisement_agent_id_invalid",
            ),
            transport_endpoint=TransportEndpoint.from_mapping(
                body.get("transport_endpoint"),
                allow_private_address_literals=allow_private_address_literals,
            ),
            protocol_version=_require_string(
                body.get("protocol_version"),
                "connectivity_advertisement_protocol_version_invalid",
                max_chars=_MAX_PROTOCOL_VERSION_CHARS,
            ),
            installed_slices_digest=_require_sha384_hex(
                body.get("installed_slices_digest"),
                "connectivity_advertisement_installed_slices_digest_invalid",
            ),
            content_availability_count=_require_uint64(
                body.get("content_availability_count"),
                "connectivity_advertisement_content_availability_count_invalid",
                max_value=MAX_CONTENT_AVAILABILITY_COUNT,
            ),
            peer_timestamp_epoch=_require_uint64(
                body.get("peer_timestamp_epoch"),
                "connectivity_advertisement_timestamp_epoch_invalid",
                max_value=MAX_PEER_ADVERTISEMENT_EPOCH,
            ),
            ttl_epochs=_require_uint64(
                body.get("ttl_epochs"),
                "connectivity_advertisement_ttl_epochs_invalid",
                min_value=1,
                max_value=MAX_TTL_EPOCHS,
            ),
            connectivity_mode=mode,
            relay_endpoint=relay_endpoint,
            candidate_list=candidates,
            probe_receipt_ref=(
                None
                if probe_receipt_ref is None
                else _require_sha384_hex(
                    probe_receipt_ref,
                    "connectivity_advertisement_probe_receipt_ref_invalid",
                )
            ),
            relay_slot_ref=(
                None
                if relay_slot_ref is None
                else _require_string(
                    relay_slot_ref,
                    "connectivity_advertisement_relay_slot_ref_invalid",
                    max_chars=_MAX_RELAY_SLOT_REF_CHARS,
                )
            ),
            ml_dsa_signature=_require_lower_hex_exact(
                value.get("ml_dsa_signature"),
                _MLDSA_SIG_HEX_LENGTH,
                "connectivity_advertisement_signature_invalid",
            ),
            key_binding_ref=_require_string(
                value.get("key_binding_ref"),
                "connectivity_advertisement_key_binding_ref_invalid",
                max_chars=_MAX_KEY_BINDING_REF_CHARS,
            ),
            schema_version=schema_version,
        )


@dataclass(frozen=True)
class VerifiedConnectivityAdvertisement:
    """Verifier-approved envelope required before registry insertion."""

    advertisement: ConnectivityAdvertisement
    verification_context: str = CONNECTIVITY_ADVERTISEMENT_VERIFICATION_CONTEXT


@dataclass(frozen=True)
class ConnectivityAdvertisementTombstone:
    agent_id: str
    revocation_epoch: int
    ml_dsa_signature: str
    key_binding_ref: str
    schema_version: str = CONNECTIVITY_ADVERTISEMENT_TOMBSTONE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _require_sha384_hex(
            self.agent_id,
            "connectivity_advertisement_tombstone_agent_id_invalid",
        )
        _require_uint64(
            self.revocation_epoch,
            "connectivity_advertisement_tombstone_revocation_epoch_invalid",
            max_value=MAX_PEER_ADVERTISEMENT_EPOCH,
        )
        _require_lower_hex_exact(
            self.ml_dsa_signature,
            _MLDSA_SIG_HEX_LENGTH,
            "connectivity_advertisement_tombstone_signature_invalid",
        )
        _require_string(
            self.key_binding_ref,
            "connectivity_advertisement_tombstone_key_binding_ref_invalid",
            max_chars=_MAX_KEY_BINDING_REF_CHARS,
        )
        if self.schema_version != CONNECTIVITY_ADVERTISEMENT_TOMBSTONE_SCHEMA_VERSION:
            raise ConnectivityAdvertisementValidationError(
                "connectivity_advertisement_tombstone_schema_version_unsupported"
            )

    def body_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "revocation_epoch": self.revocation_epoch,
            "revoke": True,
        }

    def to_canonical_json(self) -> bytes:
        return json.dumps(
            self.body_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")

    def to_dict(self) -> dict[str, Any]:
        return {
            "body": self.body_dict(),
            "key_binding_ref": self.key_binding_ref,
            "ml_dsa_signature": self.ml_dsa_signature,
            "schema_version": self.schema_version,
        }

    def verify(
        self,
        ml_dsa_verify_fn: Callable[[bytes, str, str], bool],
        *,
        pubkey_hex: str,
    ) -> bool:
        try:
            _require_lower_hex_exact(
                pubkey_hex,
                _MLDSA_PK_HEX_LENGTH,
                "connectivity_advertisement_tombstone_pubkey_invalid",
            )
            return bool(
                ml_dsa_verify_fn(
                    self.to_canonical_json(),
                    self.ml_dsa_signature,
                    pubkey_hex,
                )
            )
        except Exception:  # noqa: BLE001 - verification must fail closed.
            return False

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "ConnectivityAdvertisementTombstone":
        if not isinstance(value, Mapping):
            raise ConnectivityAdvertisementValidationError(
                "connectivity_advertisement_tombstone_not_mapping"
            )
        allowed = {"body", "key_binding_ref", "ml_dsa_signature", "schema_version"}
        _reject_missing_or_extra(value, allowed, "connectivity_advertisement_tombstone")
        schema_version = _require_string(
            value.get("schema_version"),
            "connectivity_advertisement_tombstone_schema_version_invalid",
            max_chars=80,
        )
        if schema_version != CONNECTIVITY_ADVERTISEMENT_TOMBSTONE_SCHEMA_VERSION:
            raise ConnectivityAdvertisementValidationError(
                "connectivity_advertisement_tombstone_schema_version_unsupported"
            )
        body = value.get("body")
        if not isinstance(body, Mapping):
            raise ConnectivityAdvertisementValidationError(
                "connectivity_advertisement_tombstone_body_invalid"
            )
        allowed_body = {"agent_id", "revocation_epoch", "revoke"}
        _reject_missing_or_extra(body, allowed_body, "connectivity_advertisement_tombstone_body")
        if body.get("revoke") is not True:
            raise ConnectivityAdvertisementValidationError(
                "connectivity_advertisement_tombstone_revoke_flag_invalid"
            )
        return cls(
            agent_id=_require_sha384_hex(
                body.get("agent_id"),
                "connectivity_advertisement_tombstone_agent_id_invalid",
            ),
            revocation_epoch=_require_uint64(
                body.get("revocation_epoch"),
                "connectivity_advertisement_tombstone_revocation_epoch_invalid",
                max_value=MAX_PEER_ADVERTISEMENT_EPOCH,
            ),
            ml_dsa_signature=_require_lower_hex_exact(
                value.get("ml_dsa_signature"),
                _MLDSA_SIG_HEX_LENGTH,
                "connectivity_advertisement_tombstone_signature_invalid",
            ),
            key_binding_ref=_require_string(
                value.get("key_binding_ref"),
                "connectivity_advertisement_tombstone_key_binding_ref_invalid",
                max_chars=_MAX_KEY_BINDING_REF_CHARS,
            ),
            schema_version=schema_version,
        )


@dataclass(frozen=True)
class VerifiedConnectivityAdvertisementTombstone:
    """Verifier-approved tombstone envelope required before registry removal."""

    tombstone: ConnectivityAdvertisementTombstone
    verification_context: str = CONNECTIVITY_ADVERTISEMENT_TOMBSTONE_VERIFICATION_CONTEXT


class ConnectivityAdvertisementValidator:
    """Parse and verify CDL-112 advertisements before registry insertion."""

    def __init__(
        self,
        *,
        ml_dsa_verify_fn: Callable[[bytes, str, str], bool],
        pubkey_hex: str,
        current_epoch: int,
        allow_private_address_literals: bool = False,
    ) -> None:
        if not callable(ml_dsa_verify_fn):
            raise ConnectivityAdvertisementValidationError(
                "connectivity_advertisement_verify_fn_required"
            )
        self._verify_fn = ml_dsa_verify_fn
        self._pubkey_hex = _require_lower_hex_exact(
            pubkey_hex,
            _MLDSA_PK_HEX_LENGTH,
            "connectivity_advertisement_pubkey_invalid",
        )
        self._current_epoch = _require_uint64(
            current_epoch,
            "connectivity_advertisement_current_epoch_invalid",
            max_value=MAX_PEER_ADVERTISEMENT_EPOCH,
        )
        self._allow_private_address_literals = allow_private_address_literals

    def validate(
        self,
        value: Mapping[str, Any] | ConnectivityAdvertisement,
    ) -> VerifiedConnectivityAdvertisement:
        if isinstance(value, ConnectivityAdvertisement):
            advertisement = value
        else:
            advertisement = ConnectivityAdvertisement.from_dict(
                value,
                allow_private_address_literals=self._allow_private_address_literals,
            )
        if (
            advertisement.peer_timestamp_epoch
            > self._current_epoch + MAX_PEER_TIMESTAMP_FUTURE_SKEW_EPOCHS
        ):
            raise ConnectivityAdvertisementValidationError(
                "connectivity_advertisement_timestamp_future_skew"
            )
        if advertisement.is_expired(self._current_epoch):
            raise ConnectivityAdvertisementValidationError(
                "connectivity_advertisement_expired"
            )
        if not advertisement.verify(self._verify_fn, pubkey_hex=self._pubkey_hex):
            raise ConnectivityAdvertisementValidationError(
                "connectivity_advertisement_signature_invalid"
            )
        return VerifiedConnectivityAdvertisement(advertisement=advertisement)

    def validate_tombstone(
        self,
        value: Mapping[str, Any] | ConnectivityAdvertisementTombstone,
    ) -> VerifiedConnectivityAdvertisementTombstone:
        if isinstance(value, ConnectivityAdvertisementTombstone):
            tombstone = value
        else:
            tombstone = ConnectivityAdvertisementTombstone.from_dict(value)
        if tombstone.revocation_epoch > self._current_epoch:
            raise ConnectivityAdvertisementValidationError(
                "connectivity_advertisement_tombstone_future_epoch"
            )
        if not tombstone.verify(self._verify_fn, pubkey_hex=self._pubkey_hex):
            raise ConnectivityAdvertisementValidationError(
                "connectivity_advertisement_tombstone_signature_invalid"
            )
        return VerifiedConnectivityAdvertisementTombstone(tombstone=tombstone)


def connectivity_advertisement_from_receipt(
    receipt: ConnectivityReceipt,
    *,
    agent_id: str,
    protocol_version: str,
    installed_slices_digest: str,
    content_availability_count: int,
    peer_timestamp_epoch: int,
    ttl_epochs: int,
    ml_dsa_signature: str,
    key_binding_ref: str,
    probe_receipt_ref: str | None = None,
    relay_slot_ref: str | None = None,
    candidate_list: Sequence[Mapping[str, Any] | TransportEndpoint] = (),
    allow_private_address_literals: bool = False,
) -> ConnectivityAdvertisement:
    """Build an advertisement from a local ConnectivityReceipt.

    LOCAL_ONLY and OUTBOUND_ONLY receipts intentionally cannot be advertised as
    reachable transport endpoints.
    """

    if not isinstance(receipt, ConnectivityReceipt):
        raise ConnectivityAdvertisementValidationError(
            "connectivity_advertisement_receipt_required"
        )
    mode = receipt.mode
    relay_endpoint = (
        _endpoint_from_host_port(
            receipt.relay_endpoint,
            allow_private_address_literals=allow_private_address_literals,
            token="connectivity_advertisement_relay_endpoint_invalid",
        )
        if receipt.relay_endpoint is not None
        else None
    )
    observed_endpoint = (
        _endpoint_from_host_port(
            receipt.observed_endpoint,
            allow_private_address_literals=allow_private_address_literals,
            token="connectivity_advertisement_transport_endpoint_invalid",
        )
        if receipt.observed_endpoint is not None
        else None
    )
    if mode in _RELAY_MODES:
        transport_endpoint = relay_endpoint
    elif mode in _DIRECT_MODES:
        transport_endpoint = observed_endpoint
    else:
        transport_endpoint = None
    if transport_endpoint is None:
        raise ConnectivityAdvertisementValidationError(
            "connectivity_advertisement_receipt_endpoint_required"
        )
    candidates = tuple(
        endpoint
        if isinstance(endpoint, TransportEndpoint)
        else TransportEndpoint.from_mapping(
            endpoint,
            allow_private_address_literals=allow_private_address_literals,
        )
        for endpoint in candidate_list
    )
    return ConnectivityAdvertisement(
        agent_id=agent_id,
        transport_endpoint=transport_endpoint,
        protocol_version=protocol_version,
        installed_slices_digest=installed_slices_digest,
        content_availability_count=content_availability_count,
        peer_timestamp_epoch=peer_timestamp_epoch,
        ttl_epochs=ttl_epochs,
        connectivity_mode=mode,
        relay_endpoint=relay_endpoint,
        candidate_list=candidates,
        probe_receipt_ref=probe_receipt_ref,
        relay_slot_ref=relay_slot_ref,
        ml_dsa_signature=ml_dsa_signature,
        key_binding_ref=key_binding_ref,
    )


def connectivity_advertisement_sidecar_manifest() -> dict[str, Any]:
    return {
        "authority_gate": CONNECTIVITY_ADVERTISEMENT_AUTHORITY_GATE,
        "candidate_endpoint_cap": MAX_CANDIDATE_ENDPOINTS,
        "component": "connectivity_advertisement_protocol_sidecar",
        "connectivity_advertisement_activated": True,
        "contract_version": CONNECTIVITY_ADVERTISEMENT_SIDECAR_VERSION,
        "public_gossip_propagation_enabled": True,
        "public_serving_enabled": False,
        "schema_version": CONNECTIVITY_ADVERTISEMENT_SCHEMA_VERSION,
        "sidecar_id": "connectivity-advertisement",
        "tombstone_schema_version": CONNECTIVITY_ADVERTISEMENT_TOMBSTONE_SCHEMA_VERSION,
        "token": CONNECTIVITY_ADVERTISEMENT_RUNTIME_TOKEN,
    }


def build_connectivity_advertisement_gossip_message(
    advertisement: ConnectivityAdvertisement,
) -> dict[str, Any]:
    if not isinstance(advertisement, ConnectivityAdvertisement):
        raise ConnectivityAdvertisementValidationError(
            "connectivity_advertisement_gossip_advertisement_invalid"
        )
    return {
        "advertisement": advertisement.to_dict(),
        "claimed_actor": advertisement.agent_id,
        "message_type": CONNECTIVITY_ADVERTISEMENT_GOSSIP_MESSAGE_TYPE,
        "schema_version": CONNECTIVITY_ADVERTISEMENT_GOSSIP_SCHEMA_VERSION,
    }


def build_connectivity_advertisement_tombstone_gossip_message(
    tombstone: ConnectivityAdvertisementTombstone,
) -> dict[str, Any]:
    if not isinstance(tombstone, ConnectivityAdvertisementTombstone):
        raise ConnectivityAdvertisementValidationError(
            "connectivity_advertisement_tombstone_gossip_tombstone_invalid"
        )
    return {
        "claimed_actor": tombstone.agent_id,
        "message_type": CONNECTIVITY_ADVERTISEMENT_TOMBSTONE_GOSSIP_MESSAGE_TYPE,
        "schema_version": CONNECTIVITY_ADVERTISEMENT_TOMBSTONE_GOSSIP_SCHEMA_VERSION,
        "tombstone": tombstone.to_dict(),
    }


def encode_connectivity_advertisement_gossip_payload(
    message: Mapping[str, Any],
) -> bytes:
    _validate_connectivity_gossip_message(
        message,
        schema_version=CONNECTIVITY_ADVERTISEMENT_GOSSIP_SCHEMA_VERSION,
        message_type=CONNECTIVITY_ADVERTISEMENT_GOSSIP_MESSAGE_TYPE,
        payload_key="advertisement",
    )
    return json.dumps(
        dict(message),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def encode_connectivity_advertisement_tombstone_gossip_payload(
    message: Mapping[str, Any],
) -> bytes:
    _validate_connectivity_gossip_message(
        message,
        schema_version=CONNECTIVITY_ADVERTISEMENT_TOMBSTONE_GOSSIP_SCHEMA_VERSION,
        message_type=CONNECTIVITY_ADVERTISEMENT_TOMBSTONE_GOSSIP_MESSAGE_TYPE,
        payload_key="tombstone",
    )
    return json.dumps(
        dict(message),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def decode_connectivity_advertisement_gossip_payload(payload: bytes | str) -> dict[str, Any]:
    message = _decode_connectivity_json_payload(
        payload,
        token="connectivity_advertisement_gossip_payload_invalid",
    )
    _validate_connectivity_gossip_message(
        message,
        schema_version=CONNECTIVITY_ADVERTISEMENT_GOSSIP_SCHEMA_VERSION,
        message_type=CONNECTIVITY_ADVERTISEMENT_GOSSIP_MESSAGE_TYPE,
        payload_key="advertisement",
    )
    return message


def decode_connectivity_advertisement_tombstone_gossip_payload(
    payload: bytes | str,
) -> dict[str, Any]:
    message = _decode_connectivity_json_payload(
        payload,
        token="connectivity_advertisement_tombstone_gossip_payload_invalid",
    )
    _validate_connectivity_gossip_message(
        message,
        schema_version=CONNECTIVITY_ADVERTISEMENT_TOMBSTONE_GOSSIP_SCHEMA_VERSION,
        message_type=CONNECTIVITY_ADVERTISEMENT_TOMBSTONE_GOSSIP_MESSAGE_TYPE,
        payload_key="tombstone",
    )
    return message


def _reject_missing_or_extra(
    value: Mapping[str, Any],
    allowed: set[str],
    prefix: str,
) -> None:
    missing = sorted(allowed.difference(value))
    if missing:
        raise ConnectivityAdvertisementValidationError(f"{prefix}_missing_fields:{missing}")
    extra = sorted(set(value).difference(allowed))
    if extra:
        raise ConnectivityAdvertisementValidationError(f"{prefix}_unknown_fields:{extra}")


def _decode_connectivity_json_payload(payload: bytes | str, *, token: str) -> dict[str, Any]:
    try:
        raw = payload.encode("utf-8") if isinstance(payload, str) else payload
        if not isinstance(raw, bytes):
            raise ConnectivityAdvertisementValidationError(token)
        decoded = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ConnectivityAdvertisementValidationError(token) from exc
    if not isinstance(decoded, dict):
        raise ConnectivityAdvertisementValidationError(token)
    return decoded


def _validate_connectivity_gossip_message(
    message: Mapping[str, Any],
    *,
    schema_version: str,
    message_type: str,
    payload_key: str,
) -> None:
    if not isinstance(message, Mapping):
        raise ConnectivityAdvertisementValidationError(
            f"{message_type}_gossip_message_invalid"
        )
    allowed = {"claimed_actor", "message_type", "schema_version", payload_key}
    _reject_missing_or_extra(message, allowed, message_type)
    if message.get("schema_version") != schema_version:
        raise ConnectivityAdvertisementValidationError(
            f"{message_type}_gossip_schema_version_invalid"
        )
    if message.get("message_type") != message_type:
        raise ConnectivityAdvertisementValidationError(
            f"{message_type}_gossip_message_type_invalid"
        )
    _require_sha384_hex(message.get("claimed_actor"), f"{message_type}_claimed_actor_invalid")
    if not isinstance(message.get(payload_key), Mapping):
        raise ConnectivityAdvertisementValidationError(
            f"{message_type}_gossip_payload_invalid"
        )


def _coerce_mode(value: ConnectivityMode | str | object) -> ConnectivityMode:
    if isinstance(value, ConnectivityMode):
        return value
    if isinstance(value, str):
        try:
            return ConnectivityMode(value)
        except ValueError as exc:
            raise ConnectivityAdvertisementValidationError(
                "connectivity_advertisement_mode_invalid"
            ) from exc
    raise ConnectivityAdvertisementValidationError(
        "connectivity_advertisement_mode_invalid"
    )


def _candidate_list_from_sequence(
    value: object,
    *,
    allow_private_address_literals: bool,
) -> tuple[TransportEndpoint, ...]:
    if not isinstance(value, list):
        raise ConnectivityAdvertisementValidationError(
            "connectivity_advertisement_candidate_list_invalid"
        )
    if len(value) > MAX_CANDIDATE_ENDPOINTS:
        raise ConnectivityAdvertisementValidationError(
            "connectivity_advertisement_candidate_list_exceeds_max_3"
        )
    return tuple(
        TransportEndpoint.from_mapping(
            item,
            allow_private_address_literals=allow_private_address_literals,
        )
        for item in value
    )


def _optional_endpoint_from_mapping(
    value: object,
    *,
    allow_private_address_literals: bool,
    token: str,
) -> TransportEndpoint | None:
    if value is None:
        return None
    try:
        return TransportEndpoint.from_mapping(
            value,
            allow_private_address_literals=allow_private_address_literals,
        )
    except Exception as exc:
        raise ConnectivityAdvertisementValidationError(token) from exc


def _validate_candidate_list(
    transport_endpoint: TransportEndpoint,
    candidate_list: tuple[TransportEndpoint, ...],
) -> None:
    if len(candidate_list) > MAX_CANDIDATE_ENDPOINTS:
        raise ConnectivityAdvertisementValidationError(
            "connectivity_advertisement_candidate_list_exceeds_max_3"
        )
    seen = {transport_endpoint.to_url()}
    for endpoint in candidate_list:
        if not isinstance(endpoint, TransportEndpoint):
            raise ConnectivityAdvertisementValidationError(
                "connectivity_advertisement_candidate_list_invalid"
            )
        url = endpoint.to_url()
        if url in seen:
            raise ConnectivityAdvertisementValidationError(
                "connectivity_advertisement_candidate_endpoint_duplicate"
            )
        seen.add(url)


def _validate_mode_endpoint_consistency(
    mode: ConnectivityMode,
    *,
    relay_endpoint: TransportEndpoint | None,
    relay_slot_ref: str | None,
) -> None:
    if mode in _RELAY_MODES and relay_endpoint is None:
        raise ConnectivityAdvertisementValidationError(
            "connectivity_advertisement_relay_mode_requires_relay_endpoint"
        )
    if mode in _NON_ADVERTISING_MODES:
        raise ConnectivityAdvertisementValidationError(
            "connectivity_advertisement_mode_not_advertisable"
        )
    if mode not in _RELAY_MODES and relay_endpoint is not None:
        raise ConnectivityAdvertisementValidationError(
            "connectivity_advertisement_non_relay_mode_relay_endpoint_forbidden"
        )
    if mode not in _RELAY_MODES and relay_slot_ref is not None:
        raise ConnectivityAdvertisementValidationError(
            "connectivity_advertisement_non_relay_mode_slot_ref_forbidden"
        )


def _endpoint_from_host_port(
    value: str | None,
    *,
    allow_private_address_literals: bool,
    token: str,
) -> TransportEndpoint:
    if not isinstance(value, str) or not value.strip():
        raise ConnectivityAdvertisementValidationError(token)
    host, port_text = _split_host_port(value, token)
    try:
        port = int(port_text)
    except ValueError as exc:
        raise ConnectivityAdvertisementValidationError(token) from exc
    return TransportEndpoint.from_mapping(
        {"host": host, "port": port, "scheme": "https"},
        allow_private_address_literals=allow_private_address_literals,
    )


def _split_host_port(value: str, token: str) -> tuple[str, str]:
    stripped = value.strip()
    if stripped.startswith("["):
        closing = stripped.find("]")
        if closing <= 1 or closing + 1 >= len(stripped) or stripped[closing + 1] != ":":
            raise ConnectivityAdvertisementValidationError(token)
        return stripped[1:closing], stripped[closing + 2 :]
    host, separator, port_text = stripped.rpartition(":")
    if not separator or not host or not port_text or ":" in host:
        raise ConnectivityAdvertisementValidationError(token)
    return host, port_text


def _require_string(value: object, token: str, *, max_chars: int) -> str:
    if not isinstance(value, str):
        raise ConnectivityAdvertisementValidationError(token)
    normalized = value.strip()
    if (
        value != normalized
        or not normalized
        or len(normalized) > max_chars
        or any(char.isspace() for char in normalized)
    ):
        raise ConnectivityAdvertisementValidationError(token)
    return normalized


def _require_uint64(
    value: object,
    token: str,
    *,
    min_value: int = 0,
    max_value: int,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < min_value
        or value > max_value
    ):
        raise ConnectivityAdvertisementValidationError(token)
    return value


def _require_sha384_hex(value: object, token: str) -> str:
    if not isinstance(value, str) or _SHA384_HEX_RE.fullmatch(value) is None:
        raise ConnectivityAdvertisementValidationError(token)
    return value


def _require_lower_hex_exact(value: object, expected_length: int, token: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != expected_length
        or _LOWER_HEX_RE.fullmatch(value) is None
    ):
        raise ConnectivityAdvertisementValidationError(token)
    return value


__all__ = [
    "CONNECTIVITY_ADVERTISEMENT_AUTHORITY_GATE",
    "CONNECTIVITY_ADVERTISEMENT_GOSSIP_MESSAGE_TYPE",
    "CONNECTIVITY_ADVERTISEMENT_GOSSIP_SCHEMA_VERSION",
    "CONNECTIVITY_ADVERTISEMENT_NOT_ACTIVATED",
    "CONNECTIVITY_ADVERTISEMENT_RUNTIME_TOKEN",
    "CONNECTIVITY_ADVERTISEMENT_SCHEMA_VERSION",
    "CONNECTIVITY_ADVERTISEMENT_SIDECAR_VERSION",
    "CONNECTIVITY_ADVERTISEMENT_TOMBSTONE_GOSSIP_MESSAGE_TYPE",
    "CONNECTIVITY_ADVERTISEMENT_TOMBSTONE_GOSSIP_SCHEMA_VERSION",
    "CONNECTIVITY_ADVERTISEMENT_TOMBSTONE_SCHEMA_VERSION",
    "CONNECTIVITY_ADVERTISEMENT_TOMBSTONE_VERIFICATION_CONTEXT",
    "CONNECTIVITY_ADVERTISEMENT_VERIFICATION_CONTEXT",
    "ConnectivityAdvertisement",
    "ConnectivityAdvertisementTombstone",
    "ConnectivityAdvertisementValidationError",
    "ConnectivityAdvertisementValidator",
    "MAX_CANDIDATE_ENDPOINTS",
    "VerifiedConnectivityAdvertisement",
    "VerifiedConnectivityAdvertisementTombstone",
    "build_connectivity_advertisement_gossip_message",
    "build_connectivity_advertisement_tombstone_gossip_message",
    "connectivity_advertisement_from_receipt",
    "connectivity_advertisement_sidecar_manifest",
    "decode_connectivity_advertisement_gossip_payload",
    "decode_connectivity_advertisement_tombstone_gossip_payload",
    "encode_connectivity_advertisement_gossip_payload",
    "encode_connectivity_advertisement_tombstone_gossip_payload",
]
