import json
import os
from pathlib import Path

import pytest

from ilc_core.network.d2d.persistent_fetch_rate_limiter_runtime import (
    PERSISTENT_RATE_LIMITER_SCHEMA,
    PERSISTENT_RATE_LIMITER_VERSION,
    PersistentFetchRateLimiter,
)
from ilc_core.network.d2d.truth_primitive_fetch_runtime import WANT_BLOCK_RATE_LIMIT_PER_MINUTE


def test_basic_rate_limiting() -> None:
    limiter = PersistentFetchRateLimiter(limit_per_window=2)
    assert limiter.check_and_consume("requester-a", 1) is True
    assert limiter.check_and_consume("requester-a", 1) is True
    assert limiter.check_and_consume("requester-a", 1) is False


def test_window_reset() -> None:
    limiter = PersistentFetchRateLimiter(limit_per_window=1)
    assert limiter.check_and_consume("requester-a", 1) is True
    assert limiter.check_and_consume("requester-a", 1) is False
    assert limiter.check_and_consume("requester-a", 2) is True


def test_max_buckets_cap() -> None:
    limiter = PersistentFetchRateLimiter(limit_per_window=1, max_buckets=2)
    assert limiter.check_and_consume("requester-a", 1) is True
    assert limiter.check_and_consume("requester-b", 1) is True
    assert limiter.check_and_consume("requester-c", 1) is True
    assert len(limiter._buckets) == 2


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    state_path = tmp_path / "limiter.json"
    limiter = PersistentFetchRateLimiter(limit_per_window=2)
    assert limiter.check_and_consume("requester-a", 7) is True
    limiter.save(state_path)

    loaded = PersistentFetchRateLimiter.load(state_path)
    assert loaded.check_and_consume("requester-a", 7) is True
    assert loaded.check_and_consume("requester-a", 7) is False


def test_missing_state_fails_closed(tmp_path: Path) -> None:
    loaded = PersistentFetchRateLimiter.load(tmp_path / "missing.json")
    assert loaded.fail_closed is True
    assert loaded.check_and_consume("requester-a", 1) is False


def test_corrupt_state_fails_closed(tmp_path: Path) -> None:
    state_path = tmp_path / "limiter.json"
    state_path.write_text("{not valid json", encoding="utf-8")
    loaded = PersistentFetchRateLimiter.load(state_path)
    assert loaded.fail_closed is True
    assert loaded.check_and_consume("requester-a", 1) is False


def test_schema_version_mismatch_fails_closed(tmp_path: Path) -> None:
    state_path = tmp_path / "limiter.json"
    state_path.write_text(
        json.dumps(
            {
                "schema": "wrong",
                "runtime_version": PERSISTENT_RATE_LIMITER_VERSION,
                "limit_per_window": 10,
                "max_buckets": 10,
                "requester_buckets": {},
                "sequence": 0,
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    loaded = PersistentFetchRateLimiter.load(state_path)
    assert loaded.fail_closed is True
    assert loaded.check_and_consume("requester-a", 1) is False


def test_atomic_write(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    state_path = tmp_path / "limiter.json"
    state_path.write_text("old", encoding="utf-8")
    calls: list[tuple[Path, Path]] = []

    def fake_replace(src: str | Path, dst: str | Path) -> None:
        calls.append((Path(src), Path(dst)))

    monkeypatch.setattr(os, "replace", fake_replace)
    limiter = PersistentFetchRateLimiter()
    limiter.check_and_consume("requester-a", 1)
    limiter.save(state_path)

    assert calls == [(tmp_path / ".limiter.json.tmp", state_path)]
    assert state_path.read_text(encoding="utf-8") == "old"
    assert (tmp_path / ".limiter.json.tmp").exists()


def test_requester_ids_hashed(tmp_path: Path) -> None:
    state_path = tmp_path / "limiter.json"
    raw_requester_id = "raw-requester-secret"
    limiter = PersistentFetchRateLimiter()
    limiter.check_and_consume(raw_requester_id, 1)
    limiter.save(state_path)
    text = state_path.read_text(encoding="utf-8")
    assert raw_requester_id not in text
    assert "sha256:" in text


def test_deterministic_serialization(tmp_path: Path) -> None:
    first_path = tmp_path / "first.json"
    second_path = tmp_path / "second.json"
    first = PersistentFetchRateLimiter()
    second = PersistentFetchRateLimiter()
    for limiter in (first, second):
        limiter.check_and_consume("requester-a", 1)
        limiter.check_and_consume("requester-b", 1)

    first.save(first_path)
    second.save(second_path)
    assert first_path.read_bytes() == second_path.read_bytes()


def test_invalid_window_id_rejected() -> None:
    limiter = PersistentFetchRateLimiter()
    with pytest.raises(ValueError, match="persistent_rate_limiter_invalid_window_id"):
        limiter.check_and_consume("requester-a", -1)


def test_invalid_requester_id_rejected() -> None:
    limiter = PersistentFetchRateLimiter()
    with pytest.raises(ValueError, match="persistent_rate_limiter_invalid_requester_id"):
        limiter.check_and_consume("", 1)


def test_runtime_version_token() -> None:
    assert PERSISTENT_RATE_LIMITER_VERSION == "persistent_fetch_rate_limiter_runtime_1202.v0.1"
    assert "1202" in PERSISTENT_RATE_LIMITER_VERSION
    assert PERSISTENT_RATE_LIMITER_SCHEMA == "ilc.fetch_rate_limiter_state@v1"
    assert WANT_BLOCK_RATE_LIMIT_PER_MINUTE == 10
