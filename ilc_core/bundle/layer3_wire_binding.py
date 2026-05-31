"""PUBLIC_RC_EXCLUDE: adr_0009_layer3_private_implementation
PUBLIC_RC_EXCLUDE_REASON: Private ADR-0009 Layer 3 descriptor/verifier. Does not open live network transport or publish protocol bundles.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Mapping

from ilc_core.private_json_guardrails import canonical_json, reject_float, require_digest_ref

ADR_0009_LAYER3_NOT_PUBLIC_DISTRIBUTION = True


def _reject_float(value: object, token: str) -> None:
    reject_float(value, token)


def _canonical_json(payload: Mapping[str, object]) -> str:
    return canonical_json(payload, float_token="layer3_wire_binding_float_not_allowed")


def _require_non_empty_string(value: str, token: str) -> None:
    if not isinstance(value, str) or value == "":
        raise ValueError(token)


def _require_digest(value: str, missing_token: str, invalid_token: str) -> None:
    if not isinstance(value, str) or value == "":
        raise ValueError(missing_token)
    require_digest_ref(value, invalid_token)


def _require_epoch_number(value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError("layer3_wire_binding_invalid_epoch_number")


@dataclass(frozen=True)
class Layer3WireBinding:
    message_type: str
    layer0_schema_ref: str
    sender_agent_id: str
    epoch_number: int
    payload_digest: str
    signature_ref: str
    canonical_json: str
    sha256: str
    public_rc_exclude: bool = True


def generate_layer3_wire_binding(
    *,
    message_type: str,
    layer0_schema_ref: str,
    sender_agent_id: str,
    epoch_number: int,
    payload_digest: str,
    signature_ref: str,
) -> Layer3WireBinding:
    _require_non_empty_string(message_type, "layer3_wire_binding_missing_message_type")
    _require_non_empty_string(layer0_schema_ref, "layer3_wire_binding_missing_layer0_schema_ref")
    _require_non_empty_string(sender_agent_id, "layer3_wire_binding_missing_sender_agent_id")
    _require_epoch_number(epoch_number)
    _require_digest(
        payload_digest,
        "layer3_wire_binding_missing_payload_digest",
        "layer3_wire_binding_invalid_payload_digest",
    )
    _require_non_empty_string(signature_ref, "layer3_wire_binding_missing_signature_ref")

    envelope = {
        "epoch_number": epoch_number,
        "layer": 3,
        "layer0_schema_ref": layer0_schema_ref,
        "message_type": message_type,
        "payload_digest": payload_digest,
        "public_rc_exclude": True,
        "sender_agent_id": sender_agent_id,
        "signature_ref": signature_ref,
    }
    canonical_json = _canonical_json(envelope)
    return Layer3WireBinding(
        message_type=message_type,
        layer0_schema_ref=layer0_schema_ref,
        sender_agent_id=sender_agent_id,
        epoch_number=epoch_number,
        payload_digest=payload_digest,
        signature_ref=signature_ref,
        canonical_json=canonical_json,
        sha256=hashlib.sha256(canonical_json.encode("utf-8")).hexdigest(),
    )


def verify_layer3_wire_binding(binding: Layer3WireBinding) -> bool:
    rebuilt = generate_layer3_wire_binding(
        message_type=binding.message_type,
        layer0_schema_ref=binding.layer0_schema_ref,
        sender_agent_id=binding.sender_agent_id,
        epoch_number=binding.epoch_number,
        payload_digest=binding.payload_digest,
        signature_ref=binding.signature_ref,
    )
    return (
        rebuilt.canonical_json == binding.canonical_json
        and rebuilt.sha256 == binding.sha256
        and binding.public_rc_exclude is True
    )


__all__ = [
    "ADR_0009_LAYER3_NOT_PUBLIC_DISTRIBUTION",
    "Layer3WireBinding",
    "generate_layer3_wire_binding",
    "verify_layer3_wire_binding",
]
