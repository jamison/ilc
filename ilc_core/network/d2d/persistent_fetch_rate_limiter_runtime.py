from __future__ import annotations

import hashlib
import json
import os
import threading
from pathlib import Path
from typing import Any

from ilc_core.network.d2d.truth_primitive_fetch_runtime import WANT_BLOCK_RATE_LIMIT_PER_MINUTE


PERSISTENT_RATE_LIMITER_VERSION = "persistent_fetch_rate_limiter_runtime_1202.v0.1"
PERSISTENT_RATE_LIMITER_SCHEMA = "ilc.fetch_rate_limiter_state@v1"
PERSISTENT_RATE_LIMITER_AUDIT_HARDENING_TOKEN = (
    "persistent_rate_limiter_audit_hardened_phase_1217"
)


class PersistentFetchRateLimiter:
    """Persistent WANT-BLOCK rate limiter keyed by hashed requester IDs.

    Windows are caller-supplied epoch/window counters. This class deliberately does not use
    wall-clock time as protocol truth.
    """

    def __init__(
        self,
        limit_per_window: int = WANT_BLOCK_RATE_LIMIT_PER_MINUTE,
        max_buckets: int = 10_000,
        *,
        fail_closed: bool = False,
    ) -> None:
        if not isinstance(limit_per_window, int) or limit_per_window < 1:
            raise ValueError("persistent_rate_limiter_invalid_limit")
        if not isinstance(max_buckets, int) or max_buckets < 1:
            raise ValueError("persistent_rate_limiter_invalid_max_buckets")
        self.limit_per_window = limit_per_window
        self.max_buckets = max_buckets
        self.fail_closed = fail_closed
        self._buckets: dict[str, dict[str, int]] = {}
        self._sequence = 0
        self._lock = threading.RLock()

    @staticmethod
    def _hash_requester_id(requester_id: str) -> str:
        if not isinstance(requester_id, str) or requester_id == "":
            raise ValueError("persistent_rate_limiter_invalid_requester_id")
        digest = hashlib.sha256(requester_id.encode("utf-8")).hexdigest()
        return f"sha256:{digest}"

    @staticmethod
    def _validate_window_id(window_id: int) -> int:
        if not isinstance(window_id, int) or isinstance(window_id, bool) or window_id < 0:
            raise ValueError("persistent_rate_limiter_invalid_window_id")
        return window_id

    def check_and_consume(self, requester_id: str, window_id: int) -> bool:
        with self._lock:
            if self.fail_closed:
                return False
            normalized_window_id = self._validate_window_id(window_id)
            requester_hash = self._hash_requester_id(requester_id)
            self._sequence += 1

            bucket = self._buckets.get(requester_hash)
            if bucket is None or bucket["window_id"] != normalized_window_id:
                bucket = {"count": 0, "window_id": normalized_window_id, "last_seen": self._sequence}
            if bucket["count"] >= self.limit_per_window:
                bucket["last_seen"] = self._sequence
                self._buckets[requester_hash] = bucket
                return False

            bucket["count"] += 1
            bucket["last_seen"] = self._sequence
            self._buckets[requester_hash] = bucket
            self._prune_if_needed()
            return True

    def _prune_if_needed(self) -> None:
        while len(self._buckets) > self.max_buckets:
            oldest_key = min(
                self._buckets,
                key=lambda key: (self._buckets[key]["last_seen"], key),
            )
            del self._buckets[oldest_key]

    def _state(self) -> dict[str, Any]:
        with self._lock:
            return {
                "limit_per_window": self.limit_per_window,
                "max_buckets": self.max_buckets,
                "requester_buckets": {
                    requester_hash: dict(bucket)
                    for requester_hash, bucket in self._buckets.items()
                },
                "runtime_version": PERSISTENT_RATE_LIMITER_VERSION,
                "schema": PERSISTENT_RATE_LIMITER_SCHEMA,
                "sequence": self._sequence,
            }

    @staticmethod
    def _dump_state(state: dict[str, Any]) -> str:
        return json.dumps(
            state,
            sort_keys=True,
            allow_nan=False,
            separators=(",", ":"),
        )

    def save(self, path: Path) -> None:
        with self._lock:
            target = Path(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = target.with_name(f".{target.name}.tmp")
            tmp_path.write_text(self._dump_state(self._state()), encoding="utf-8")
            os.replace(tmp_path, target)

    @classmethod
    def fail_closed_limiter(
        cls,
        limit_per_window: int = WANT_BLOCK_RATE_LIMIT_PER_MINUTE,
        max_buckets: int = 10_000,
    ) -> "PersistentFetchRateLimiter":
        return cls(
            limit_per_window=limit_per_window,
            max_buckets=max_buckets,
            fail_closed=True,
        )

    @classmethod
    def load(cls, path: Path) -> "PersistentFetchRateLimiter":
        try:
            raw = Path(path).read_text(encoding="utf-8")
            state = json.loads(raw)
            if not isinstance(state, dict):
                return cls.fail_closed_limiter()
            if state.get("schema") != PERSISTENT_RATE_LIMITER_SCHEMA:
                return cls.fail_closed_limiter()
            if state.get("runtime_version") != PERSISTENT_RATE_LIMITER_VERSION:
                return cls.fail_closed_limiter()

            limiter = cls(
                limit_per_window=cls._load_positive_int(state, "limit_per_window"),
                max_buckets=cls._load_positive_int(state, "max_buckets"),
            )
            sequence = state.get("sequence", 0)
            if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 0:
                return cls.fail_closed_limiter()
            buckets = state.get("requester_buckets")
            if not isinstance(buckets, dict):
                return cls.fail_closed_limiter()
            limiter._sequence = sequence
            limiter._buckets = cls._load_buckets(buckets)
            limiter._prune_if_needed()
            return limiter
        except (OSError, json.JSONDecodeError, ValueError, TypeError):
            return cls.fail_closed_limiter()

    @staticmethod
    def _load_positive_int(state: dict[str, Any], field: str) -> int:
        value = state.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise ValueError(f"persistent_rate_limiter_invalid_state:{field}")
        return value

    @staticmethod
    def _load_buckets(raw_buckets: dict[str, Any]) -> dict[str, dict[str, int]]:
        buckets: dict[str, dict[str, int]] = {}
        for requester_hash, raw_bucket in raw_buckets.items():
            if not isinstance(requester_hash, str) or not requester_hash.startswith("sha256:"):
                raise ValueError("persistent_rate_limiter_invalid_state:requester_hash")
            if not isinstance(raw_bucket, dict):
                raise ValueError("persistent_rate_limiter_invalid_state:bucket")
            count = raw_bucket.get("count")
            window_id = raw_bucket.get("window_id")
            last_seen = raw_bucket.get("last_seen", 0)
            for field, value in (
                ("count", count),
                ("window_id", window_id),
                ("last_seen", last_seen),
            ):
                if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                    raise ValueError(f"persistent_rate_limiter_invalid_state:{field}")
            buckets[requester_hash] = {
                "count": count,
                "window_id": window_id,
                "last_seen": last_seen,
            }
        return buckets
