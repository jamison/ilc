from __future__ import annotations

import inspect
import json
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.protocol.commit_epoch_emission_runtime import (
    CDL_051_DEPENDENCY,
    COMMIT_EPOCH_CANONICAL_DEPENDENCY,
    COMMIT_EPOCH_EMISSION_RUNTIME_VERSION,
    build_commit_epoch_event,
)
from ilc_core.protocol.event_log import (
    COMMIT_EPOCH_CANONICAL_CONSTRUCTOR_VERSION,
    ProtocolEvent,
    validate_canonical_commit_epoch_payload,
)

RUNTIME_PATH = Path("ilc_core/protocol/commit_epoch_emission_runtime.py")


def _quorum_records() -> list[dict[str, object]]:
    return [
        {
            "block_hash": "block-alpha",
            "epoch_index": 12,
            "quorum_state_digest": "quorum-state-alpha",
            "vote_weight": 1,
        },
        {
            "block_hash": "block-alpha",
            "epoch_index": 12,
            "quorum_state_digest": "quorum-state-beta",
            "vote_weight": 1,
        },
    ]


def _event(**overrides: object) -> ProtocolEvent:
    kwargs = {
        "epoch_index": 12,
        "epoch_id": "epoch-0012",
        "namespace_id": "ilc:test",
        "finalization_state": "committed",
        "quorum_records": _quorum_records(),
        "epoch_state_digest": "state-digest-12",
        "epoch_events_digest": "events-digest-12",
        "reward_total": Decimal("10.50"),
        "stake_total": Decimal("20"),
        "task_count": 3,
        "agent_count": 2,
    }
    kwargs.update(overrides)
    return build_commit_epoch_event(**kwargs)


def test_build_commit_epoch_event_produces_valid_protocol_event():
    event = _event()

    assert isinstance(event, ProtocolEvent)
    assert event.kind == "commit.epoch"
    assert event.source == "protocol:commit_epoch_emission_runtime"
    validate_canonical_commit_epoch_payload(event.payload)


def test_output_payload_contains_no_created_at_field():
    event = _event()

    assert "created_at" not in event.payload
    assert event.payload["schema_version"] == COMMIT_EPOCH_CANONICAL_CONSTRUCTOR_VERSION


def test_epoch_state_cid_derived_from_digest_argument_not_wall_clock():
    event = _event(epoch_state_digest="abc123", epoch_events_digest="def456")

    assert event.payload["checksums"]["epoch_state_cid"] == "sha256:abc123"
    assert event.payload["checksums"]["epoch_events_cid"] == "sha256:def456"


def test_reward_total_float_input_raises_value_error():
    with pytest.raises(ValueError, match="reward_total_must_be_non_negative_finite_decimal"):
        _event(reward_total=1.5)


def test_stake_total_non_finite_decimal_raises_value_error():
    with pytest.raises(ValueError, match="stake_total_must_be_non_negative_finite_decimal"):
        _event(stake_total=Decimal("NaN"))


def test_invalid_finalization_state_raises_value_error():
    with pytest.raises(ValueError, match="finalization_state_invalid"):
        _event(finalization_state="finalized")


def test_negative_epoch_index_raises_value_error():
    with pytest.raises(ValueError, match="epoch_index_must_be_non_negative_int"):
        _event(epoch_index=-1)


def test_non_integer_epoch_index_raises_value_error():
    with pytest.raises(ValueError, match="epoch_index_must_be_non_negative_int"):
        _event(epoch_index="12")


def test_canonical_json_of_event_is_deterministic_for_identical_inputs():
    first_payload = json.dumps(
        _event().payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    second_payload = json.dumps(
        _event().payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    assert first_payload == second_payload


def test_version_and_dependency_tokens_present():
    assert COMMIT_EPOCH_EMISSION_RUNTIME_VERSION == "commit_epoch_emission_runtime_1236.v0.1"
    assert CDL_051_DEPENDENCY == "cdl_051_constitutional_consensus_and_epoch_finality_443.v0.1"
    assert COMMIT_EPOCH_CANONICAL_DEPENDENCY == COMMIT_EPOCH_CANONICAL_CONSTRUCTOR_VERSION


def test_module_does_not_use_wall_clock_or_legacy_constructor_or_io():
    import ilc_core.protocol.commit_epoch_emission_runtime as runtime

    source = inspect.getsource(runtime)
    assert "datetime.now" not in source
    assert "time.time" not in source
    assert "make_commit_epoch_event" not in source
    assert "import random" not in source
    assert "random." not in source
    assert ".open(" not in source
    assert "requests" not in source
    assert RUNTIME_PATH.exists()
