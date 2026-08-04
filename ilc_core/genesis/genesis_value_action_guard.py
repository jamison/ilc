# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from ilc_core.epoch.genesis_settlement_destination import GENESIS_AGENT1_AGENT_ID

GENESIS_VALUE_GUARD_VERSION = "genesis_value_action_guard_GAP_GENESIS_VALUE_02_v0_1"
CDL_110_DEPENDENCY = "cdl_110_genesis_value_spend_guard_ratified"
GENESIS_VALUE_CERTIFICATE_SCHEMA_VERSION = "genesis_value_action_policy_certificate.v1"
GENESIS_VALUE_NETWORK_ID = "ilc-rc01"
GENESIS_VALUE_NONCE_DOMAIN = "ilc:genesis-value-action:v1"
GENESIS_VALUE_ALLOWED_RECIPIENT_POLICY = "graph_context_required"
GENESIS_VALUE_GUARDIAN_THRESHOLD = 2
GENESIS_VALUE_GUARDIAN_KEY_COUNT = 3
GENESIS_VALUE_GUARDIAN_SIGNATURE_SCHEME = "Ed25519-COSE-Sign1"
GENESIS_VALUE_MAX_POLICY_WINDOW_EPOCHS = 4
GENESIS_VALUE_MAX_PER_TRANSFER_MICRO_ECU = 1_000_000_000
GENESIS_VALUE_MAX_PER_EPOCH_MICRO_ECU = 5_000_000_000
GENESIS_VALUE_MAX_PER_TRANSFER_MICRO_ILC = 1_000_000_000
GENESIS_VALUE_MAX_PER_EPOCH_MICRO_ILC = 5_000_000_000

_U64_MAX = 18_446_744_073_709_551_615
_ALLOWED_ACTION_CLASSES = frozenset({"CONTRIBUTION", "PAYMENT"})
_UNITS = frozenset({"ECU", "ILC"})


class GenesisValueGuardError(ValueError):
    """Raised when Genesis source-agent value movement violates CDL-110."""

    def __init__(self, token: str) -> None:
        self.token = token
        super().__init__(token)


@dataclass(frozen=True)
class GenesisValueActionPolicyCertificate:
    schema_version: str
    certificate_id: str
    genesis_agent_id: str
    network_id: str
    effective_epoch_start: int
    effective_epoch_end: int
    allowed_action_classes: frozenset[str]
    allowed_recipient_policy: str
    per_transfer_cap_micro_ecu: int
    per_epoch_cap_micro_ecu: int
    per_transfer_cap_micro_ilc: int
    per_epoch_cap_micro_ilc: int
    nonce_domain: str
    guardian_public_key_root: str
    guardian_threshold: int
    guardian_key_count: int
    guardian_signature_scheme: str
    certificate_payload_sha256: str
    certificate_sig: Mapping[str, object]


def validate_genesis_value_certificate(
    cert: GenesisValueActionPolicyCertificate,
) -> None:
    """Validate the CDL-110 Genesis value policy certificate fields."""
    if not isinstance(cert, GenesisValueActionPolicyCertificate):
        raise GenesisValueGuardError("genesis_value_certificate_invalid_type")
    if cert.schema_version != GENESIS_VALUE_CERTIFICATE_SCHEMA_VERSION:
        raise GenesisValueGuardError("genesis_value_certificate_schema_version_invalid")
    _require_canonical_string(
        cert.certificate_id,
        "genesis_value_certificate_id_invalid",
    )
    if cert.genesis_agent_id != GENESIS_AGENT1_AGENT_ID:
        raise GenesisValueGuardError("genesis_value_certificate_agent_mismatch")
    if cert.network_id != GENESIS_VALUE_NETWORK_ID:
        raise GenesisValueGuardError("genesis_value_certificate_network_mismatch")

    start = _require_u64(
        cert.effective_epoch_start,
        "genesis_value_certificate_epoch_start_invalid",
    )
    end = _require_u64(
        cert.effective_epoch_end,
        "genesis_value_certificate_epoch_end_invalid",
    )
    if end < start:
        raise GenesisValueGuardError("genesis_value_certificate_epoch_order_invalid")
    if end - start + 1 > GENESIS_VALUE_MAX_POLICY_WINDOW_EPOCHS:
        raise GenesisValueGuardError("genesis_value_certificate_window_too_long")

    if not isinstance(cert.allowed_action_classes, frozenset):
        raise GenesisValueGuardError("genesis_value_certificate_action_classes_not_frozenset")
    if not cert.allowed_action_classes:
        raise GenesisValueGuardError("genesis_value_certificate_action_classes_empty")
    if not cert.allowed_action_classes.issubset(_ALLOWED_ACTION_CLASSES):
        raise GenesisValueGuardError("genesis_value_certificate_action_class_invalid")
    if cert.allowed_recipient_policy != GENESIS_VALUE_ALLOWED_RECIPIENT_POLICY:
        raise GenesisValueGuardError("genesis_value_certificate_recipient_policy_invalid")

    _validate_caps(cert)

    if cert.nonce_domain != GENESIS_VALUE_NONCE_DOMAIN:
        raise GenesisValueGuardError("genesis_value_certificate_nonce_domain_invalid")
    _require_sha256_hex(
        cert.guardian_public_key_root,
        "genesis_value_certificate_guardian_root_invalid",
    )
    if cert.guardian_threshold != GENESIS_VALUE_GUARDIAN_THRESHOLD:
        raise GenesisValueGuardError("genesis_value_certificate_guardian_threshold_invalid")
    if cert.guardian_key_count != GENESIS_VALUE_GUARDIAN_KEY_COUNT:
        raise GenesisValueGuardError("genesis_value_certificate_guardian_key_count_invalid")
    if cert.guardian_signature_scheme != GENESIS_VALUE_GUARDIAN_SIGNATURE_SCHEME:
        raise GenesisValueGuardError("genesis_value_certificate_signature_scheme_invalid")
    _require_sha256_hex(
        cert.certificate_payload_sha256,
        "genesis_value_certificate_payload_sha256_invalid",
    )
    if compute_certificate_payload_sha256(cert) != cert.certificate_payload_sha256:
        raise GenesisValueGuardError("genesis_value_certificate_payload_sha256_mismatch")
    _validate_certificate_sig(cert.certificate_sig)


def compute_certificate_payload_sha256(
    cert: GenesisValueActionPolicyCertificate,
) -> str:
    """Return SHA-256 over the canonical CDL-110 certificate payload."""
    return hashlib.sha256(_json_bytes(canonical_certificate_payload(cert))).hexdigest()


def canonical_certificate_payload(
    cert: GenesisValueActionPolicyCertificate,
) -> dict[str, object]:
    """Return the certificate payload covered by guardian signatures."""
    return {
        "allowed_action_classes": sorted(cert.allowed_action_classes),
        "allowed_recipient_policy": cert.allowed_recipient_policy,
        "certificate_id": cert.certificate_id,
        "effective_epoch_end": cert.effective_epoch_end,
        "effective_epoch_start": cert.effective_epoch_start,
        "genesis_agent_id": cert.genesis_agent_id,
        "guardian_key_count": cert.guardian_key_count,
        "guardian_public_key_root": cert.guardian_public_key_root,
        "guardian_signature_scheme": cert.guardian_signature_scheme,
        "guardian_threshold": cert.guardian_threshold,
        "network_id": cert.network_id,
        "nonce_domain": cert.nonce_domain,
        "per_epoch_cap_micro_ecu": cert.per_epoch_cap_micro_ecu,
        "per_epoch_cap_micro_ilc": cert.per_epoch_cap_micro_ilc,
        "per_transfer_cap_micro_ecu": cert.per_transfer_cap_micro_ecu,
        "per_transfer_cap_micro_ilc": cert.per_transfer_cap_micro_ilc,
        "schema_version": cert.schema_version,
    }


def enforce_genesis_value_guard(
    *,
    source_agent_id: str,
    certificate: GenesisValueActionPolicyCertificate | None,
    action_class: str,
    amount_micro_unit: int,
    current_epoch: int | None,
    recipient_agent_id: str,
    graph_context_anchor: str | None,
    consent_or_agreement_reference: str | None,
    unit: str,
    current_epoch_spent_micro_unit: int | None,
    network_id: str = GENESIS_VALUE_NETWORK_ID,
) -> None:
    """Fail closed for Genesis source-agent value movement outside CDL-110."""
    if source_agent_id != GENESIS_AGENT1_AGENT_ID:
        return
    if certificate is None:
        raise GenesisValueGuardError("genesis_value_certificate_required")
    validate_genesis_value_certificate(certificate)
    if network_id != certificate.network_id:
        raise GenesisValueGuardError("genesis_value_certificate_network_mismatch")
    if certificate.genesis_agent_id != source_agent_id:
        raise GenesisValueGuardError("genesis_value_certificate_agent_mismatch")

    epoch = _require_u64(current_epoch, "genesis_value_current_epoch_invalid")
    if epoch < certificate.effective_epoch_start:
        raise GenesisValueGuardError("genesis_value_certificate_not_yet_active")
    if epoch > certificate.effective_epoch_end:
        raise GenesisValueGuardError("genesis_value_certificate_expired")

    if action_class not in certificate.allowed_action_classes:
        raise GenesisValueGuardError("genesis_value_certificate_action_class_not_allowed")
    amount = _require_u64(amount_micro_unit, "genesis_value_amount_micro_unit_invalid")
    if amount == 0:
        raise GenesisValueGuardError("genesis_value_amount_micro_unit_non_positive")
    spent = _require_u64(
        current_epoch_spent_micro_unit,
        "genesis_value_epoch_spend_required",
    )

    if not isinstance(recipient_agent_id, str) or not recipient_agent_id:
        raise GenesisValueGuardError("genesis_value_recipient_agent_id_invalid")
    if not _present(graph_context_anchor):
        raise GenesisValueGuardError("genesis_value_graph_context_required")
    if action_class == "PAYMENT" and not _present(consent_or_agreement_reference):
        raise GenesisValueGuardError("genesis_value_payment_consent_required")
    if unit not in _UNITS:
        raise GenesisValueGuardError("genesis_value_unit_invalid")

    per_transfer_cap, per_epoch_cap = _caps_for_unit(certificate, unit)
    if amount > per_transfer_cap:
        raise GenesisValueGuardError("genesis_value_per_transfer_cap_exceeded")
    if spent > per_epoch_cap or amount > per_epoch_cap - spent:
        raise GenesisValueGuardError("genesis_value_per_epoch_cap_exceeded")


def _validate_caps(cert: GenesisValueActionPolicyCertificate) -> None:
    ecu_transfer = _require_u64(
        cert.per_transfer_cap_micro_ecu,
        "genesis_value_certificate_per_transfer_cap_micro_ecu_invalid",
    )
    ecu_epoch = _require_u64(
        cert.per_epoch_cap_micro_ecu,
        "genesis_value_certificate_per_epoch_cap_micro_ecu_invalid",
    )
    ilc_transfer = _require_u64(
        cert.per_transfer_cap_micro_ilc,
        "genesis_value_certificate_per_transfer_cap_micro_ilc_invalid",
    )
    ilc_epoch = _require_u64(
        cert.per_epoch_cap_micro_ilc,
        "genesis_value_certificate_per_epoch_cap_micro_ilc_invalid",
    )
    if ecu_transfer > GENESIS_VALUE_MAX_PER_TRANSFER_MICRO_ECU:
        raise GenesisValueGuardError("genesis_value_certificate_ecu_transfer_cap_too_high")
    if ecu_epoch > GENESIS_VALUE_MAX_PER_EPOCH_MICRO_ECU:
        raise GenesisValueGuardError("genesis_value_certificate_ecu_epoch_cap_too_high")
    if ilc_transfer > GENESIS_VALUE_MAX_PER_TRANSFER_MICRO_ILC:
        raise GenesisValueGuardError("genesis_value_certificate_ilc_transfer_cap_too_high")
    if ilc_epoch > GENESIS_VALUE_MAX_PER_EPOCH_MICRO_ILC:
        raise GenesisValueGuardError("genesis_value_certificate_ilc_epoch_cap_too_high")
    if ecu_epoch < ecu_transfer:
        raise GenesisValueGuardError("genesis_value_certificate_ecu_epoch_cap_below_transfer")
    if ilc_epoch < ilc_transfer:
        raise GenesisValueGuardError("genesis_value_certificate_ilc_epoch_cap_below_transfer")


def _caps_for_unit(
    cert: GenesisValueActionPolicyCertificate,
    unit: str,
) -> tuple[int, int]:
    if unit == "ECU":
        return cert.per_transfer_cap_micro_ecu, cert.per_epoch_cap_micro_ecu
    if unit == "ILC":
        return cert.per_transfer_cap_micro_ilc, cert.per_epoch_cap_micro_ilc
    raise GenesisValueGuardError("genesis_value_unit_invalid")


def _validate_certificate_sig(value: Mapping[str, object]) -> None:
    if not isinstance(value, Mapping):
        raise GenesisValueGuardError("genesis_value_certificate_signature_bundle_invalid")
    if value.get("threshold") != GENESIS_VALUE_GUARDIAN_THRESHOLD:
        raise GenesisValueGuardError("genesis_value_certificate_signature_threshold_invalid")
    signatures = value.get("signatures")
    if not isinstance(signatures, Sequence) or isinstance(signatures, (str, bytes)):
        raise GenesisValueGuardError("genesis_value_certificate_signatures_invalid")
    if len(signatures) < GENESIS_VALUE_GUARDIAN_THRESHOLD:
        raise GenesisValueGuardError("genesis_value_certificate_signatures_insufficient")
    for signature in signatures:
        if not isinstance(signature, Mapping) or not signature:
            raise GenesisValueGuardError("genesis_value_certificate_signature_entry_invalid")


def _require_u64(value: object, token: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise GenesisValueGuardError(token)
    if value < 0 or value > _U64_MAX:
        raise GenesisValueGuardError(token)
    return value


def _require_canonical_string(value: object, token: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise GenesisValueGuardError(token)
    return value


def _require_sha256_hex(value: object, token: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise GenesisValueGuardError(token)
    try:
        int(value, 16)
    except ValueError as exc:
        raise GenesisValueGuardError(token) from exc
    if value.lower() != value:
        raise GenesisValueGuardError(token)
    return value


def _present(value: str | None) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode(
        "utf-8"
    )


__all__ = [
    "CDL_110_DEPENDENCY",
    "GENESIS_VALUE_ALLOWED_RECIPIENT_POLICY",
    "GENESIS_VALUE_CERTIFICATE_SCHEMA_VERSION",
    "GENESIS_VALUE_GUARD_VERSION",
    "GENESIS_VALUE_NETWORK_ID",
    "GENESIS_VALUE_NONCE_DOMAIN",
    "GenesisValueActionPolicyCertificate",
    "GenesisValueGuardError",
    "canonical_certificate_payload",
    "compute_certificate_payload_sha256",
    "enforce_genesis_value_guard",
    "validate_genesis_value_certificate",
]
