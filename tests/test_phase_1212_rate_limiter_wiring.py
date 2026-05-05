import json
from pathlib import Path

import pytest

from ilc_core.network.d2d.http_fetch_transport_runtime import (
    FetchTransportConfig,
    HttpFetchTransportRuntime,
    PERSISTENT_RATE_LIMITER_TRANSPORT_WIRING_TOKEN,
    PERSISTENT_RATE_LIMITER_STATE_SAVE_FAILED_TOKEN,
    RECIPROCAL_FETCH_ADMISSION_CARRY_FORWARD,
    TRANSPORT_ABUSE_CIRCUIT_BREAKER_TOKEN,
)
from ilc_core.network.d2d.persistent_fetch_rate_limiter_runtime import (
    PersistentFetchRateLimiter,
)
from ilc_core.network.d2d.truth_primitive_fetch_runtime import WANT_BLOCK_RATE_LIMIT_PER_MINUTE


class _Store:
    def __init__(self, record: dict | None = None) -> None:
        self.record = record or {"node_id": "n1", "primitive": "assert.truth"}

    def get_node(self, node_id: str) -> dict:
        return dict(self.record, node_id=node_id)


def _body(node_id: str = "n1", requester_id: str = "agent-1") -> bytes:
    return json.dumps(
        {"node_id": node_id, "requester_id": requester_id},
        sort_keys=True,
    ).encode()


def _valid_persistent_state(path: Path, *, limit: int = WANT_BLOCK_RATE_LIMIT_PER_MINUTE) -> None:
    PersistentFetchRateLimiter(limit_per_window=limit).save(path)


def _decode(resp_body: bytes) -> dict:
    return json.loads(resp_body.decode())


def test_default_config_uses_in_memory_limiter(tmp_path):
    config = FetchTransportConfig(store_path="", persistent_limiter_path=None)
    runtime = HttpFetchTransportRuntime(config)
    runtime._store = _Store()

    assert runtime._persistent_rate_limiter is None
    status, _ = runtime.handle_want_block(_body())
    assert status == 200
    assert config.event_log == []


def test_persistent_config_loads_limiter(tmp_path):
    path = tmp_path / "fetch_limiter.json"
    _valid_persistent_state(path)
    config = FetchTransportConfig(persistent_limiter_path=path, rate_limit_window_id=12)
    runtime = HttpFetchTransportRuntime(config)
    runtime._store = _Store()

    assert runtime._persistent_rate_limiter is not None
    status, _ = runtime.handle_want_block(_body())
    assert status == 200
    assert path.exists()


def test_persistent_limiter_survives_reload(tmp_path):
    path = tmp_path / "fetch_limiter.json"
    _valid_persistent_state(path, limit=1)

    first = HttpFetchTransportRuntime(
        FetchTransportConfig(persistent_limiter_path=path, rate_limit_window_id=7)
    )
    first._store = _Store()
    status, _ = first.handle_want_block(_body(requester_id="same-agent"))
    assert status == 200

    second = HttpFetchTransportRuntime(
        FetchTransportConfig(persistent_limiter_path=path, rate_limit_window_id=7)
    )
    second._store = _Store()
    status, body = second.handle_want_block(_body(requester_id="same-agent"))
    assert status == 429
    assert _decode(body)["token"] == "fetch_rate_limit_exceeded"


def test_want_have_unaffected_by_persistent_fail_closed_limiter(tmp_path):
    path = tmp_path / "missing.json"
    config = FetchTransportConfig(persistent_limiter_path=path, rate_limit_window_id=1)
    runtime = HttpFetchTransportRuntime(config)
    runtime._store = _Store()

    status, body = runtime.handle_want_have(_body())
    assert status == 200
    assert _decode(body) == {"have": True, "node_id": "n1"}


def test_429_token_unchanged_with_persistent_limiter(tmp_path):
    path = tmp_path / "fetch_limiter.json"
    _valid_persistent_state(path, limit=1)
    runtime = HttpFetchTransportRuntime(
        FetchTransportConfig(persistent_limiter_path=path, rate_limit_window_id=4)
    )
    runtime._store = _Store()

    assert runtime.handle_want_block(_body(requester_id="agent-x"))[0] == 200
    status, body = runtime.handle_want_block(_body(requester_id="agent-x"))
    assert status == 429
    assert _decode(body)["token"] == "fetch_rate_limit_exceeded"


def test_persistent_limiter_load_failure_emits_degradation_token(tmp_path):
    path = tmp_path / "corrupt.json"
    path.write_text("{not-json", encoding="utf-8")
    config = FetchTransportConfig(persistent_limiter_path=path, rate_limit_window_id=2)
    runtime = HttpFetchTransportRuntime(config)
    runtime._store = _Store()

    assert runtime._persistent_rate_limiter is not None
    assert runtime._persistent_rate_limiter.fail_closed is True
    assert {
        "event": "fetch_rate_limiter_degraded",
        "token": "persistent_rate_limiter_state_reset_on_load_failure",
    } in config.event_log

    status, body = runtime.handle_want_block(_body())
    assert status == 429
    assert _decode(body)["token"] == "fetch_rate_limit_exceeded"


def test_invalid_persistent_window_id_rejected(tmp_path):
    path = tmp_path / "fetch_limiter.json"
    _valid_persistent_state(path)

    with pytest.raises(ValueError, match="fetch_rate_limit_window_id_invalid"):
        HttpFetchTransportRuntime(
            FetchTransportConfig(persistent_limiter_path=path, rate_limit_window_id=-1)
        )


def test_phase_1212_policy_boundary_tokens_present():
    assert (
        PERSISTENT_RATE_LIMITER_TRANSPORT_WIRING_TOKEN
        == "persistent_rate_limiter_transport_wiring_committed_phase_1212"
    )
    assert (
        TRANSPORT_ABUSE_CIRCUIT_BREAKER_TOKEN
        == "transport_abuse_circuit_breaker_not_final_scaling_policy"
    )
    assert RECIPROCAL_FETCH_ADMISSION_CARRY_FORWARD == "reciprocal_fetch_admission_model_required"


def test_persistent_limiter_save_failure_fails_closed(monkeypatch, tmp_path):
    path = tmp_path / "fetch_limiter.json"
    _valid_persistent_state(path, limit=2)
    config = FetchTransportConfig(persistent_limiter_path=path, rate_limit_window_id=5)
    runtime = HttpFetchTransportRuntime(config)
    runtime._store = _Store()

    def _raise_os_error(_path):
        raise OSError("simulated write failure")

    monkeypatch.setattr(runtime._persistent_rate_limiter, "save", _raise_os_error)
    status, body = runtime.handle_want_block(_body(requester_id="agent-save-fail"))

    assert status == 429
    assert _decode(body)["token"] == "fetch_rate_limit_exceeded"
    assert {
        "event": "fetch_rate_limiter_degraded",
        "token": PERSISTENT_RATE_LIMITER_STATE_SAVE_FAILED_TOKEN,
    } in config.event_log
