# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from pathlib import Path

import lmdb
import pytest

from ilc_core.value_action.action_nonce_store import (
    ACTION_NONCE_STORE_VERSION,
    ActionNonceStore,
    NonceReplayError,
    _encode_counter,
)

AGENT_A = "a" * 96
AGENT_B = "b" * 96
MODULE_PATH = Path("ilc_core/value_action/action_nonce_store.py")


@pytest.fixture
def lmdb_env(tmp_path: Path):
    env = lmdb.open(str(tmp_path / "nonce-store.lmdb"), max_dbs=4, map_size=8 * 1024 * 1024)
    try:
        yield env
    finally:
        env.close()


def _nonce(agent_id: str, counter: int) -> str:
    return f"{agent_id}:nonce:{counter:020d}"


def test_sequential_nonces_are_distinct(lmdb_env) -> None:
    store = ActionNonceStore(lmdb_env)

    assert store.next_nonce(AGENT_A) == _nonce(AGENT_A, 1)
    assert store.next_nonce(AGENT_A) == _nonce(AGENT_A, 2)


def test_nonce_replay_raises(lmdb_env) -> None:
    store = ActionNonceStore(lmdb_env)
    nonce = store.next_nonce(AGENT_A)
    store.consume_nonce(AGENT_A, nonce)

    with pytest.raises(NonceReplayError, match="nonce_replay_rejected"):
        store.consume_nonce(AGENT_A, nonce)


def test_store_survives_reinstantiation(tmp_path: Path) -> None:
    path = tmp_path / "durable-nonce-store.lmdb"
    env = lmdb.open(str(path), max_dbs=4, map_size=8 * 1024 * 1024)
    ActionNonceStore(env).next_nonce(AGENT_A)
    env.close()

    env2 = lmdb.open(str(path), max_dbs=4, map_size=8 * 1024 * 1024)
    try:
        assert ActionNonceStore(env2).peek_counter(AGENT_A) == 1
    finally:
        env2.close()


def test_multiple_agents_independent_counters(lmdb_env) -> None:
    store = ActionNonceStore(lmdb_env)

    assert store.next_nonce(AGENT_A) == _nonce(AGENT_A, 1)
    assert store.next_nonce(AGENT_B) == _nonce(AGENT_B, 1)
    assert store.peek_counter(AGENT_A) == 1
    assert store.peek_counter(AGENT_B) == 1


def test_consume_valid_first_nonce_then_replay_fails(lmdb_env) -> None:
    store = ActionNonceStore(lmdb_env)
    nonce = _nonce(AGENT_A, 1)

    store.consume_nonce(AGENT_A, nonce)
    with pytest.raises(NonceReplayError, match="nonce_replay_rejected"):
        store.consume_nonce(AGENT_A, nonce)


def test_consume_out_of_sequence_rejected(lmdb_env) -> None:
    store = ActionNonceStore(lmdb_env)

    with pytest.raises(NonceReplayError, match="nonce_out_of_sequence_rejected"):
        store.consume_nonce(AGENT_A, _nonce(AGENT_A, 2))


def test_skipped_issued_nonce_cannot_be_consumed_out_of_order(lmdb_env) -> None:
    store = ActionNonceStore(lmdb_env)
    store.next_nonce(AGENT_A)
    store.next_nonce(AGENT_A)

    with pytest.raises(NonceReplayError, match="nonce_out_of_sequence_rejected"):
        store.consume_nonce(AGENT_A, _nonce(AGENT_A, 2))

    store.consume_nonce(AGENT_A, _nonce(AGENT_A, 1))
    store.consume_nonce(AGENT_A, _nonce(AGENT_A, 2))
    assert store.peek_counter(AGENT_A) == 2


def test_counter_increments_atomically(lmdb_env) -> None:
    store = ActionNonceStore(lmdb_env)
    issued = [store.next_nonce(AGENT_A) for _ in range(5)]

    assert issued == [_nonce(AGENT_A, counter) for counter in range(1, 6)]
    assert store.peek_counter(AGENT_A) == 5


def test_peek_does_not_mutate_counter(lmdb_env) -> None:
    store = ActionNonceStore(lmdb_env)
    store.next_nonce(AGENT_A)

    assert store.peek_counter(AGENT_A) == 1
    assert store.peek_counter(AGENT_A) == 1
    assert store.next_nonce(AGENT_A) == _nonce(AGENT_A, 2)


def test_next_after_external_consume_skips_consumed_nonce(lmdb_env) -> None:
    store = ActionNonceStore(lmdb_env)
    store.consume_nonce(AGENT_A, _nonce(AGENT_A, 1))

    assert store.next_nonce(AGENT_A) == _nonce(AGENT_A, 2)


def test_next_nonce_counter_exhaustion_has_stable_token(lmdb_env) -> None:
    store = ActionNonceStore(lmdb_env)
    issued_key = AGENT_A.encode("ascii") + b":issued_counter"
    with store.lmdb_env.begin(write=True) as txn:
        txn.put(issued_key, _encode_counter(2**64 - 1), db=store._issued_db)

    with pytest.raises(NonceReplayError, match="action_nonce_counter_exhausted"):
        store.next_nonce(AGENT_A)


def test_nonce_counter_above_u64_rejected(lmdb_env) -> None:
    with pytest.raises(ValueError, match="invalid_action_nonce_counter_overflow"):
        ActionNonceStore(lmdb_env).consume_nonce(AGENT_A, _nonce(AGENT_A, 2**64))


@pytest.mark.parametrize(
    "bad_nonce, token",
    [
        ("", "invalid_action_nonce_agent_mismatch"),
        (f"{AGENT_A}:nonce:1", "invalid_action_nonce_format"),
        (f"{AGENT_A}:nonce:{0:020d}", "invalid_action_nonce_zero"),
        (f"{AGENT_B}:nonce:{1:020d}", "invalid_action_nonce_agent_mismatch"),
    ],
)
def test_invalid_nonce_formats_rejected(lmdb_env, bad_nonce: str, token: str) -> None:
    with pytest.raises(ValueError, match=token):
        ActionNonceStore(lmdb_env).consume_nonce(AGENT_A, bad_nonce)


def test_invalid_agent_id_rejected(lmdb_env) -> None:
    store = ActionNonceStore(lmdb_env)

    with pytest.raises(ValueError, match="invalid_action_nonce_agent_id"):
        store.next_nonce("A" * 96)


def test_no_prng_or_float_or_production_asserts() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert "import random" not in source
    assert "SystemRandom" not in source
    assert "float" not in source
    assert "\nassert " not in source
    assert ACTION_NONCE_STORE_VERSION == "action_nonce_store_03.v0.1"
