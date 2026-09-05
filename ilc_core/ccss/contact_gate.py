# SPDX-License-Identifier: AGPL-3.0-only
"""Local-only CCSS ContactGate evaluator.

Phase 1573t rehearses recipient-side admission policy for sealed CCSS
messages. This module is deterministic, has no network calls, performs no
graph writes, and does not activate public relay serving.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import hmac
import string
from typing import Any


CONTACT_GATE_RUNTIME_VERSION = "contact_gate_runtime_1573t.v0.1"
CONTACT_GATE_PUBLIC_SERVING_NOT_ACTIVATED = True

CONTACT_GATE_ADMISSION_MODES: frozenset[str] = frozenset(
    {
        "public_open",
        "contacts_only",
        "capability_required",
        "stake_or_rate_limited_open",
        "private_invite_only",
        "closed",
    }
)

CONTACT_GATE_SECRET_FIELD_NAMES: frozenset[str] = frozenset(
    {
        "known_contact_ids",
        "allowed_contact_ids",
        "allowlist",
        "denylist",
        "raw_capability_id",
        "private_invite_secret",
        "expected_invite_context_commitment",
        "capability_context_commitment",
    }
)

_NULLIFIER_PREFIX = b"ilc-contact-gate-nullifier-v1:"
_CONTACT_ID_DIGEST_PREFIX = b"ilc-contact-gate-contact-id-v1:"


class ContactGateError(ValueError):
    """Stable exception for ContactGate policy/input failures."""

    def __init__(self, token: str) -> None:
        super().__init__(token)
        self.token = token


def _require_mapping(value: Any, *, token: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ContactGateError(token)
    return value


def _require_string(value: Any, *, token: str) -> str:
    if not isinstance(value, str) or not value:
        raise ContactGateError(token)
    return value


def _coerce_commitment(value: Any, *, field: str) -> bytes:
    if isinstance(value, bytes):
        if not value:
            raise ContactGateError(f"ccss_contact_gate_{field}_empty")
        return value
    if isinstance(value, str) and value:
        normalized = value[2:] if value.startswith("0x") else value
        try:
            raw = bytes.fromhex(normalized)
        except ValueError:
            hex_chars = set(string.hexdigits)
            if value.startswith("0x") or all(char in hex_chars for char in normalized):
                raise ContactGateError(f"ccss_contact_gate_{field}_invalid_hex")
            raw = value.encode("utf-8")
        if not raw:
            raise ContactGateError(f"ccss_contact_gate_{field}_empty")
        return raw
    raise ContactGateError(f"ccss_contact_gate_{field}_missing")


def _constant_time_match(left: Any, right: Any, *, field: str) -> bool:
    return hmac.compare_digest(
        _coerce_commitment(left, field=f"{field}_left"),
        _coerce_commitment(right, field=f"{field}_right"),
    )


def _safe_contact_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, Sequence) or isinstance(value, (bytes, bytearray, str)):
        raise ContactGateError("ccss_contact_gate_known_contacts_invalid")
    contacts: list[str] = []
    for item in value:
        contacts.append(_require_string(item, token="ccss_contact_gate_contact_id_invalid"))
    return tuple(contacts)


def _contact_id_digest(contact_id: str) -> bytes:
    return hashlib.sha256(
        _CONTACT_ID_DIGEST_PREFIX
        + _require_string(contact_id, token="ccss_contact_gate_contact_id_invalid").encode(
            "utf-8"
        )
    ).digest()


def _constant_time_contact_membership(sender_contact_id: Any, known_contacts: Any) -> bool:
    contacts = _safe_contact_tuple(known_contacts)
    candidate = (
        _contact_id_digest(sender_contact_id)
        if isinstance(sender_contact_id, str) and sender_contact_id
        else _contact_id_digest("ilc-contact-gate-invalid-sender")
    )
    matched = 0
    for contact_id in contacts:
        matched |= int(hmac.compare_digest(candidate, _contact_id_digest(contact_id)))
    return bool(matched)


def _verdict(
    *,
    accepted: bool,
    admission_mode: str,
    verdict_token: str,
    gate_id: str,
) -> dict[str, Any]:
    return {
        "accepted": accepted,
        "admission_mode": admission_mode,
        "gate_id": gate_id,
        "ok": True,
        "private_rule_disclosed": False,
        "public_serving_activated": False,
        "relay_visible_fields": ["opaque_bundle_metadata_only"],
        "verdict_token": verdict_token,
        "version": CONTACT_GATE_RUNTIME_VERSION,
    }


def evaluate_contact_gate(
    policy: Mapping[str, Any],
    inbound_context: Mapping[str, Any],
) -> dict[str, Any]:
    """Evaluate a local ContactGate policy against an inbound sealed-message context.

    The returned verdict is intentionally sanitized. It never includes the
    policy allowlist, denylist, raw capability IDs, expected capability
    commitments, invite commitments, sender identity, recipient identity, or
    private gate rules.
    """

    policy_map = _require_mapping(policy, token="ccss_contact_gate_policy_invalid")
    context_map = _require_mapping(
        inbound_context,
        token="ccss_contact_gate_inbound_context_invalid",
    )
    admission_mode = _require_string(
        policy_map.get("admission_mode"),
        token="ccss_contact_gate_admission_mode_missing",
    )
    if admission_mode not in CONTACT_GATE_ADMISSION_MODES:
        raise ContactGateError(f"ccss_contact_gate_admission_mode_invalid:{admission_mode}")

    gate_id = _require_string(
        policy_map.get("gate_id", "contact_gate:local_rehearsal"),
        token="ccss_contact_gate_gate_id_invalid",
    )

    if admission_mode == "public_open":
        return _verdict(
            accepted=True,
            admission_mode=admission_mode,
            gate_id=gate_id,
            verdict_token="ccss_contact_gate_accept_public_open",
        )

    if admission_mode == "closed":
        return _verdict(
            accepted=False,
            admission_mode=admission_mode,
            gate_id=gate_id,
            verdict_token="ccss_contact_gate_reject_closed",
        )

    if admission_mode == "stake_or_rate_limited_open":
        return _verdict(
            accepted=False,
            admission_mode=admission_mode,
            gate_id=gate_id,
            verdict_token="ccss_contact_gate_stake_rate_limited_not_activated_phase_1573t",
        )

    if admission_mode == "contacts_only":
        accepted = _constant_time_contact_membership(
            context_map.get("sender_contact_id"),
            policy_map.get("known_contact_ids", policy_map.get("allowed_contact_ids")),
        )
        return _verdict(
            accepted=accepted,
            admission_mode=admission_mode,
            gate_id=gate_id,
            verdict_token=(
                "ccss_contact_gate_accept_known_contact"
                if accepted
                else "ccss_contact_gate_reject_unknown_contact"
            ),
        )

    if admission_mode == "capability_required":
        accepted = _constant_time_match(
            policy_map.get("capability_context_commitment"),
            context_map.get("capability_context_commitment"),
            field="capability_context_commitment",
        )
        return _verdict(
            accepted=accepted,
            admission_mode=admission_mode,
            gate_id=gate_id,
            verdict_token=(
                "ccss_contact_gate_accept_capability"
                if accepted
                else "ccss_contact_gate_reject_capability_mismatch"
            ),
        )

    if admission_mode == "private_invite_only":
        expected = policy_map.get(
            "expected_invite_context_commitment",
            policy_map.get("capability_context_commitment"),
        )
        supplied = context_map.get(
            "invite_context_commitment",
            context_map.get("capability_context_commitment"),
        )
        accepted = _constant_time_match(
            expected,
            supplied,
            field="invite_context_commitment",
        )
        return _verdict(
            accepted=accepted,
            admission_mode=admission_mode,
            gate_id=gate_id,
            verdict_token=(
                "ccss_contact_gate_accept_private_invite"
                if accepted
                else "ccss_contact_gate_reject_private_invite_mismatch"
            ),
        )

    raise ContactGateError(f"ccss_contact_gate_unhandled_mode:{admission_mode}")


def make_contact_gate_nullifier(
    *,
    gate_id: str,
    sender_context_commitment: bytes | str,
    sealed_nonce: bytes | str,
) -> str:
    """Create a deterministic local nullifier for replay/spam accounting."""

    gate_id_bytes = _require_string(
        gate_id,
        token="ccss_contact_gate_gate_id_invalid",
    ).encode("utf-8")
    sender_bytes = _coerce_commitment(
        sender_context_commitment,
        field="sender_context_commitment",
    )
    nonce_bytes = _coerce_commitment(sealed_nonce, field="sealed_nonce")
    return hashlib.sha256(
        _NULLIFIER_PREFIX + gate_id_bytes + b":" + sender_bytes + b":" + nonce_bytes
    ).hexdigest()


def assert_no_private_gate_fields(verdict: Mapping[str, Any]) -> None:
    """Fail if a verdict leaks private gate policy fields."""

    verdict_map = _require_mapping(verdict, token="ccss_contact_gate_verdict_invalid")
    leaked = sorted(CONTACT_GATE_SECRET_FIELD_NAMES.intersection(verdict_map.keys()))
    if leaked:
        raise ContactGateError(
            "ccss_contact_gate_private_field_leaked:" + ",".join(leaked)
        )


__all__ = [
    "CONTACT_GATE_ADMISSION_MODES",
    "CONTACT_GATE_PUBLIC_SERVING_NOT_ACTIVATED",
    "CONTACT_GATE_RUNTIME_VERSION",
    "CONTACT_GATE_SECRET_FIELD_NAMES",
    "ContactGateError",
    "assert_no_private_gate_fields",
    "evaluate_contact_gate",
    "make_contact_gate_nullifier",
]
