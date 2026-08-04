# SPDX-License-Identifier: AGPL-3.0-only
"""Atomic double-entry settled-ILC transfer ledger for the live-RC lane."""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Protocol

from ilc_core.ledger.exact_numeric import (
    decimal_to_canonical_string,
    parse_non_negative_decimal,
)
import ilc_core.value_action.ilc_transfer_intent as transfer_intent
from ilc_core.value_action.action_nonce_store import ActionNonceStore
from ilc_core.value_action.ilc_transfer_intent import AgentActionEnvelope, validate_envelope

ILC_TRANSFER_LEDGER_VERSION = "ilc_transfer_ledger_04.v0.1"

_BALANCES_DB = b"ilc_transfer_balances"
_TRANSFERS_DB = b"ilc_transfer_records"


class InsufficientBalanceError(ValueError):
    """Raised when sender balance cannot fund a settled ILC transfer."""


class EnvelopeSignatureVerifier(Protocol):
    """Minimal verifier interface accepted by the value-moving ledger boundary."""

    def verify_envelope_signature(
        self,
        env: AgentActionEnvelope,
        public_key_bytes: bytes,
        *,
        external_aad: bytes = b"",
    ) -> bool:
        """Return True only when env's COSE signature verifies for public_key_bytes."""


class EnvelopeSignerAuthority(Protocol):
    """Minimal authority interface for AgentID-to-signing-key authorization."""

    def is_signer_authorized(
        self,
        agent_id: str,
        public_key_bytes: bytes,
        *,
        action_scope: str,
    ) -> bool:
        """Return True only when public_key_bytes may authorize agent_id actions."""


@dataclass(frozen=True)
class ILCTransferLedgerEntry:
    transfer_id: str
    sender_agent_id: str
    recipient_agent_id: str
    amount_ilc: Decimal
    nonce: str
    epoch: int
    sender_balance_before_ilc: Decimal
    sender_balance_after_ilc: Decimal
    recipient_balance_before_ilc: Decimal
    recipient_balance_after_ilc: Decimal
    record_sha256: str
    memo: str | None = None
    graph_context_anchor: str | None = None


class ILCTransferLedger:
    """Caller-env LMDB ledger for atomic agent-id settled ILC transfers."""

    def __init__(self, lmdb_env: object) -> None:
        self._env = lmdb_env
        self._balances_db = self._env.open_db(_BALANCES_DB, create=True)
        self._transfers_db = self._env.open_db(_TRANSFERS_DB, create=True)

    def get_balance(self, agent_id: str) -> Decimal:
        """Return current settled transfer balance for an AgentID."""
        transfer_intent._require_agent_id(agent_id, "invalid_ilc_transfer_agent_id")
        with self._env.begin(db=self._balances_db) as txn:
            return _decode_balance(txn.get(_key(agent_id)))

    def seed_balance_for_test(self, agent_id: str, amount_ilc: Decimal) -> None:
        """Seed LMDB balance for deterministic tests only, never production flow."""
        if os.environ.get("ILC_TEST_BALANCE_SEED_AUTHORIZED") != "1":
            raise ValueError("test_balance_seed_not_authorized")
        transfer_intent._require_agent_id(agent_id, "invalid_ilc_transfer_agent_id")
        with self._env.begin(write=True, db=self._balances_db) as txn:
            txn.put(_key(agent_id), _encode_balance(amount_ilc))

    def execute_transfer(
        self,
        env: AgentActionEnvelope,
        nonce_store: ActionNonceStore,
        *,
        signature_verifier: EnvelopeSignatureVerifier | None = None,
        signer_authority: EnvelopeSignerAuthority | None = None,
        sender_public_key_bytes: bytes | None = None,
        external_aad: bytes = b"",
    ) -> ILCTransferLedgerEntry:
        """Atomically debit sender, credit recipient, consume nonce, and record."""
        if transfer_intent.ILC_TRANSFER_ENABLED is not True:
            raise ValueError("transfer_not_enabled")
        validate_envelope(env)
        _verify_transfer_signature(
            env,
            signature_verifier=signature_verifier,
            signer_authority=signer_authority,
            sender_public_key_bytes=sender_public_key_bytes,
            external_aad=external_aad,
        )
        if nonce_store.lmdb_env is not self._env:
            raise ValueError("transfer_nonce_store_env_mismatch")

        sender_key = _key(env.sender_agent_id)
        recipient_key = _key(env.recipient_agent_id)
        with self._env.begin(write=True) as txn:
            sender_before = _decode_balance(txn.get(sender_key, db=self._balances_db))
            recipient_before = _decode_balance(
                txn.get(recipient_key, db=self._balances_db)
            )
            if sender_before < env.amount_ilc:
                raise InsufficientBalanceError("insufficient_balance")

            nonce_store.consume_nonce_in_txn(txn, env.sender_agent_id, env.nonce)

            sender_after = sender_before - env.amount_ilc
            recipient_after = recipient_before + env.amount_ilc
            txn.put(
                sender_key,
                _encode_balance(sender_after),
                db=self._balances_db,
            )
            txn.put(
                recipient_key,
                _encode_balance(recipient_after),
                db=self._balances_db,
            )

            record = _record_payload(
                env=env,
                sender_before=sender_before,
                sender_after=sender_after,
                recipient_before=recipient_before,
                recipient_after=recipient_after,
            )
            # transfer_id identifies the balance-effect body. record_sha256
            # authenticates the stored envelope that carries that id.
            transfer_id = _sha256_hex(record)
            if txn.get(transfer_id.encode("ascii"), db=self._transfers_db) is not None:
                raise ValueError("transfer_record_duplicate")
            record_with_id = dict(record)
            record_with_id["transfer_id"] = transfer_id
            record_with_id["record_sha256"] = _sha256_hex(record_with_id)
            txn.put(
                transfer_id.encode("ascii"),
                _json_bytes(record_with_id),
                db=self._transfers_db,
            )

        return _entry_from_record(record_with_id)

    def get_transfer_record(self, transfer_id: str) -> ILCTransferLedgerEntry | None:
        """Return a recorded transfer entry by deterministic transfer id."""
        _require_sha256_hex(transfer_id, "invalid_transfer_id")
        with self._env.begin(db=self._transfers_db) as txn:
            raw = txn.get(transfer_id.encode("ascii"))
        if raw is None:
            return None
        decoded = json.loads(raw.decode("utf-8"))
        if not isinstance(decoded, dict):
            raise ValueError("invalid_transfer_record_payload")
        _verify_record_sha256(decoded)
        return _entry_from_record(decoded)


def _key(value: str) -> bytes:
    return value.encode("ascii")


def _verify_transfer_signature(
    env: AgentActionEnvelope,
    *,
    signature_verifier: EnvelopeSignatureVerifier | None,
    signer_authority: EnvelopeSignerAuthority | None,
    sender_public_key_bytes: bytes | None,
    external_aad: bytes,
) -> None:
    if signature_verifier is None:
        raise ValueError("transfer_signature_verifier_required")
    if signer_authority is None:
        raise ValueError("transfer_signer_authority_required")
    if env.cose_signature is None:
        raise ValueError("transfer_signature_required")
    if not isinstance(sender_public_key_bytes, bytes) or len(sender_public_key_bytes) != 32:
        raise ValueError("invalid_sender_public_key_bytes")
    if not isinstance(external_aad, bytes):
        raise ValueError("invalid_transfer_external_aad")
    try:
        authorized = signer_authority.is_signer_authorized(
            env.sender_agent_id,
            sender_public_key_bytes,
            action_scope="ILC_TRANSFER",
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("transfer_signer_authority_invalid") from exc
    if authorized is not True:
        raise ValueError("transfer_signer_not_authorized")
    try:
        verified = signature_verifier.verify_envelope_signature(
            env,
            sender_public_key_bytes,
            external_aad=external_aad,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("transfer_signature_invalid") from exc
    if verified is not True:
        raise ValueError("transfer_signature_invalid")


def _encode_balance(value: Decimal) -> bytes:
    if not isinstance(value, Decimal):
        raise TypeError("invalid_ilc_balance_type")
    if value < Decimal("0"):
        raise ValueError("invalid_ilc_balance_negative")
    return decimal_to_canonical_string(value).encode("ascii")


def _decode_balance(raw: bytes | None) -> Decimal:
    if raw is None:
        return Decimal("0")
    try:
        rendered = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("invalid_ilc_balance_encoding") from exc
    return parse_non_negative_decimal(rendered, token="invalid_ilc_balance")


def _record_payload(
    *,
    env: AgentActionEnvelope,
    sender_before: Decimal,
    sender_after: Decimal,
    recipient_before: Decimal,
    recipient_after: Decimal,
) -> dict[str, Any]:
    return {
        "amount_ilc": decimal_to_canonical_string(env.amount_ilc),
        "epoch": env.epoch,
        "graph_context_anchor": env.graph_context_anchor,
        "memo": env.memo,
        "nonce": env.nonce,
        "recipient_agent_id": env.recipient_agent_id,
        "recipient_balance_after_ilc": decimal_to_canonical_string(recipient_after),
        "recipient_balance_before_ilc": decimal_to_canonical_string(recipient_before),
        "schema_version": ILC_TRANSFER_LEDGER_VERSION,
        "sender_agent_id": env.sender_agent_id,
        "sender_balance_after_ilc": decimal_to_canonical_string(sender_after),
        "sender_balance_before_ilc": decimal_to_canonical_string(sender_before),
    }


def _entry_from_record(record: dict[str, Any]) -> ILCTransferLedgerEntry:
    return ILCTransferLedgerEntry(
        transfer_id=_require_sha256_hex(record.get("transfer_id"), "invalid_transfer_id"),
        sender_agent_id=str(record["sender_agent_id"]),
        recipient_agent_id=str(record["recipient_agent_id"]),
        amount_ilc=parse_non_negative_decimal(
            record["amount_ilc"],
            token="invalid_transfer_record_amount",
        ),
        nonce=str(record["nonce"]),
        epoch=_require_epoch(record["epoch"]),
        sender_balance_before_ilc=parse_non_negative_decimal(
            record["sender_balance_before_ilc"],
            token="invalid_transfer_record_balance",
        ),
        sender_balance_after_ilc=parse_non_negative_decimal(
            record["sender_balance_after_ilc"],
            token="invalid_transfer_record_balance",
        ),
        recipient_balance_before_ilc=parse_non_negative_decimal(
            record["recipient_balance_before_ilc"],
            token="invalid_transfer_record_balance",
        ),
        recipient_balance_after_ilc=parse_non_negative_decimal(
            record["recipient_balance_after_ilc"],
            token="invalid_transfer_record_balance",
        ),
        record_sha256=_require_sha256_hex(
            record.get("record_sha256"),
            "invalid_transfer_record_sha256",
        ),
        memo=record.get("memo"),
        graph_context_anchor=record.get("graph_context_anchor"),
    )


def _require_epoch(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError("invalid_transfer_record_epoch")
    return value


def _require_sha256_hex(value: object, token: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(token)
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(token) from exc
    if value.lower() != value:
        raise ValueError(token)
    return value


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode(
        "utf-8"
    )


def _sha256_hex(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_json_bytes(payload)).hexdigest()


def _verify_record_sha256(record: dict[str, Any]) -> None:
    expected = _require_sha256_hex(
        record.get("record_sha256"),
        "invalid_transfer_record_sha256",
    )
    # Stored records use two hash layers: transfer_id is SHA-256(body), while
    # record_sha256 is SHA-256(body + transfer_id). Rebuild the second layer.
    body = {key: value for key, value in record.items() if key != "record_sha256"}
    if _sha256_hex(body) != expected:
        raise ValueError("transfer_record_sha256_mismatch")


__all__ = [
    "ILC_TRANSFER_LEDGER_VERSION",
    "EnvelopeSignerAuthority",
    "EnvelopeSignatureVerifier",
    "ILCTransferLedger",
    "ILCTransferLedgerEntry",
    "InsufficientBalanceError",
]
