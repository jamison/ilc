# SPDX-License-Identifier: AGPL-3.0-only
"""LMDB-backed monotonic per-agent nonce store for value actions."""
from __future__ import annotations

import re
import struct

ACTION_NONCE_STORE_VERSION = "action_nonce_store_03.v0.1"

_ISSUED_DB_NAME = b"action_nonce_issued"
_CONSUMED_DB_NAME = b"action_nonce_consumed"
_ISSUED_COUNTER_SUFFIX = b":issued_counter"
_CONSUMED_COUNTER_SUFFIX = b":consumed_counter"
_PACKING_FMT = ">Q"
_PACKING_SIZE = struct.calcsize(_PACKING_FMT)
_MAX_COUNTER = 2**64 - 1
_AGENT_ID_RE = re.compile(r"^[0-9a-f]{96}$")
_NONCE_COUNTER_DIGITS = 20
_NONCE_SEPARATOR = ":nonce:"


class NonceReplayError(ValueError):
    """Raised when a value-action nonce is replayed or out of sequence."""


class ActionNonceStore:
    """Per-agent monotonic nonce store backed by caller-provided LMDB env."""

    def __init__(self, lmdb_env: object) -> None:
        self._env = lmdb_env
        self._issued_db = self._env.open_db(_ISSUED_DB_NAME, create=True)
        self._consumed_db = self._env.open_db(_CONSUMED_DB_NAME, create=True)

    def next_nonce(self, agent_id: str) -> str:
        """Atomically issue the next local nonce for agent_id."""
        _require_agent_id(agent_id)
        issued_key = _counter_key(agent_id, _ISSUED_COUNTER_SUFFIX)
        consumed_key = _counter_key(agent_id, _CONSUMED_COUNTER_SUFFIX)
        with self._env.begin(write=True) as txn:
            issued = _decode_counter(txn.get(issued_key, db=self._issued_db))
            consumed = _decode_counter(txn.get(consumed_key, db=self._consumed_db))
            next_counter = max(issued, consumed) + 1
            if next_counter > _MAX_COUNTER:
                raise NonceReplayError("action_nonce_counter_exhausted")
            txn.put(
                issued_key,
                _encode_counter(next_counter),
                db=self._issued_db,
            )
        return _format_nonce(agent_id, next_counter)

    def consume_nonce(self, agent_id: str, nonce: str) -> None:
        """Atomically mark nonce consumed, rejecting replay and gaps."""
        with self._env.begin(write=True) as txn:
            self.consume_nonce_in_txn(txn, agent_id, nonce)

    def consume_nonce_in_txn(self, txn: object, agent_id: str, nonce: str) -> None:
        """Mark nonce consumed inside a caller-owned LMDB write transaction.

        Consumption is intentionally strict-sequential: nonce N+1 is rejected
        until nonce N is consumed, so failed/skipped value actions cannot leave
        an accepted gap in the per-agent action stream.
        """
        _require_agent_id(agent_id)
        counter = _parse_nonce(agent_id, nonce)
        nonce_key = nonce.encode("ascii")
        consumed_key = _counter_key(agent_id, _CONSUMED_COUNTER_SUFFIX)
        if txn.get(nonce_key, db=self._consumed_db) is not None:
            raise NonceReplayError("nonce_replay_rejected")
        consumed = _decode_counter(txn.get(consumed_key, db=self._consumed_db))
        if counter != consumed + 1:
            raise NonceReplayError("nonce_out_of_sequence_rejected")
        txn.put(nonce_key, b"1", db=self._consumed_db)
        txn.put(
            consumed_key,
            _encode_counter(counter),
            db=self._consumed_db,
        )

    def peek_counter(self, agent_id: str) -> int:
        """Return max issued-or-consumed counter without mutation."""
        _require_agent_id(agent_id)
        issued_key = _counter_key(agent_id, _ISSUED_COUNTER_SUFFIX)
        consumed_key = _counter_key(agent_id, _CONSUMED_COUNTER_SUFFIX)
        with self._env.begin(write=False) as txn:
            issued = _decode_counter(txn.get(issued_key, db=self._issued_db))
            consumed = _decode_counter(txn.get(consumed_key, db=self._consumed_db))
        return max(issued, consumed)

    @property
    def lmdb_env(self) -> object:
        """Return the caller-owned LMDB environment bound to this store."""
        return self._env


def _require_agent_id(agent_id: str) -> None:
    if not isinstance(agent_id, str) or _AGENT_ID_RE.fullmatch(agent_id) is None:
        raise ValueError("invalid_action_nonce_agent_id")


def _format_nonce(agent_id: str, counter: int) -> str:
    return f"{agent_id}{_NONCE_SEPARATOR}{counter:0{_NONCE_COUNTER_DIGITS}d}"


def _parse_nonce(agent_id: str, nonce: str) -> int:
    if not isinstance(nonce, str):
        raise ValueError("invalid_action_nonce_format")
    prefix = f"{agent_id}{_NONCE_SEPARATOR}"
    if not nonce.startswith(prefix):
        raise ValueError("invalid_action_nonce_agent_mismatch")
    raw_counter = nonce[len(prefix):]
    if len(raw_counter) != _NONCE_COUNTER_DIGITS or not raw_counter.isdecimal():
        raise ValueError("invalid_action_nonce_format")
    counter = int(raw_counter)
    if counter <= 0:
        raise ValueError("invalid_action_nonce_zero")
    if counter > _MAX_COUNTER:
        raise ValueError("invalid_action_nonce_counter_overflow")
    if nonce != _format_nonce(agent_id, counter):
        raise ValueError("invalid_action_nonce_format")
    return counter


def _counter_key(agent_id: str, suffix: bytes) -> bytes:
    return agent_id.encode("ascii") + suffix


def _encode_counter(counter: int) -> bytes:
    if not isinstance(counter, int) or isinstance(counter, bool) or counter < 0:
        raise ValueError("invalid_action_nonce_counter")
    if counter > _MAX_COUNTER:
        raise ValueError("invalid_action_nonce_counter_overflow")
    return struct.pack(_PACKING_FMT, counter)


def _decode_counter(raw: bytes | None) -> int:
    if raw is None:
        return 0
    if len(raw) != _PACKING_SIZE:
        raise ValueError("invalid_action_nonce_counter_bytes")
    return struct.unpack(_PACKING_FMT, raw)[0]


__all__ = [
    "ACTION_NONCE_STORE_VERSION",
    "ActionNonceStore",
    "NonceReplayError",
]
