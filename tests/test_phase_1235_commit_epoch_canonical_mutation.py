from __future__ import annotations

import inspect
import json
import subprocess
from decimal import Decimal

import pytest

from ilc_core.consensus.circuit_breaker_interface import (
    CircuitBreakerInterfaceError,
    summarize_circuit_breaker_quorum_state,
)
from ilc_core.consensus.epoch_state_runtime import (
    ConsensusEpochStateValidationError,
    generate_quorum_record,
)
from ilc_core.consensus.finality_evaluator import (
    _aggregate_weights,
    evaluate_epoch_finality,
)
from ilc_core.exceptions import EventLogValidationError
from ilc_core.protocol import event_log
from ilc_core.protocol.event_log import (
    COMMIT_EPOCH_CANONICAL_CONSTRUCTOR_VERSION,
    ProtocolEvent,
    make_canonical_commit_epoch_event,
    make_commit_epoch_event,
    validate_canonical_commit_epoch_payload,
)


def _summary(
    *,
    reward_total: Decimal | int | str = Decimal("12.5000"),
    stake_total: Decimal | int | str = Decimal("3.000"),
) -> dict[str, object]:
    return {
        "task_count": 2,
        "agent_count": 3,
        "reward_total": reward_total,
        "stake_total": stake_total,
    }


def _checksums() -> dict[str, str]:
    return {
        "epoch_events_cid": "bafy-epoch-events",
        "epoch_state_cid": "bafy-epoch-state",
    }


def _canonical_event(**overrides: object) -> ProtocolEvent:
    kwargs = {
        "epoch_index": 7,
        "epoch_id": "epoch-0007",
        "namespace_id": "ilc:test",
        "finalization_state": "committed",
        "summary": _summary(),
        "checksums": _checksums(),
        "source": "phase-1235-test",
    }
    kwargs.update(overrides)
    return make_canonical_commit_epoch_event(**kwargs)


def test_canonical_constructor_produces_commit_epoch_without_created_at():
    evt = _canonical_event()

    assert evt.kind == "commit.epoch"
    assert evt.schema_version == COMMIT_EPOCH_CANONICAL_CONSTRUCTOR_VERSION
    assert evt.payload["schema_version"] == COMMIT_EPOCH_CANONICAL_CONSTRUCTOR_VERSION
    assert "created_at" not in evt.payload
    assert evt.payload["finalization_state"] == "committed"


def test_canonical_validator_accepts_no_wall_clock_payload_and_rejects_created_at():
    evt = _canonical_event()
    validate_canonical_commit_epoch_payload(evt.payload)

    mutated = dict(evt.payload)
    mutated["created_at"] = "2026-05-06T00:00:00+00:00"
    with pytest.raises(EventLogValidationError, match="created_at"):
        validate_canonical_commit_epoch_payload(mutated)


def test_canonical_constructor_signature_has_no_created_at_parameter():
    params = inspect.signature(make_canonical_commit_epoch_event).parameters
    assert "created_at" not in params


def test_canonical_summary_decimals_are_rendered_as_canonical_strings():
    evt = _canonical_event(
        summary=_summary(
            reward_total=Decimal("001.2300"),
            stake_total="0004.5000",
        )
    )

    assert evt.payload["summary"]["reward_total"] == "1.23"
    assert evt.payload["summary"]["stake_total"] == "4.5"
    json.dumps(
        evt.payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def test_canonical_constructor_rejects_float_economic_summary_values():
    with pytest.raises(EventLogValidationError, match="reward_total"):
        _canonical_event(summary=_summary(reward_total=1.0))

    with pytest.raises(EventLogValidationError, match="stake_total"):
        _canonical_event(summary=_summary(stake_total=2.0))


def test_canonical_validator_rejects_float_economic_summary_values():
    payload = _canonical_event().payload
    mutated = {
        **payload,
        "summary": {
            **payload["summary"],
            "reward_total": 1.0,
        },
    }
    with pytest.raises(EventLogValidationError, match="reward_total"):
        validate_canonical_commit_epoch_payload(mutated)


def test_canonical_validator_rejects_bool_integer_fields():
    payload = _canonical_event().payload
    for field_name in ("epoch_index",):
        mutated = {**payload, field_name: True}
        with pytest.raises(EventLogValidationError, match=field_name):
            validate_canonical_commit_epoch_payload(mutated)

    for field_name in ("task_count", "agent_count"):
        mutated = {
            **payload,
            "summary": {
                **payload["summary"],
                field_name: True,
            },
        }
        with pytest.raises(EventLogValidationError, match=field_name):
            validate_canonical_commit_epoch_payload(mutated)


def test_canonical_validator_rejects_malformed_sha256_checksum_refs():
    payload = _canonical_event(
        checksums={
            "epoch_events_cid": "sha256:" + "a" * 64,
            "epoch_state_cid": "sha256:" + "b" * 64,
        }
    ).payload
    mutated = {
        **payload,
        "checksums": {
            **payload["checksums"],
            "epoch_events_cid": "sha256:not-a-valid-digest",
        },
    }
    with pytest.raises(EventLogValidationError, match="epoch_events_cid"):
        validate_canonical_commit_epoch_payload(mutated)


def test_canonical_payload_json_is_deterministic_for_same_inputs():
    first = _canonical_event().payload
    second = _canonical_event().payload

    assert json.dumps(
        first,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ) == json.dumps(
        second,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def test_legacy_commit_epoch_constructor_remains_callable_for_rc_fixtures():
    evt = make_commit_epoch_event(
        epoch_index=7,
        epoch_id="epoch-0007",
        namespace_id="ilc:test",
        created_at="2026-05-06T00:00:00+00:00",
        finalization_state="committed",
        summary=_summary(reward_total=Decimal("1.00"), stake_total=Decimal("2.00")),
        checksums=_checksums(),
    )

    assert evt.kind == "commit.epoch"
    assert evt.payload["created_at"] == "2026-05-06T00:00:00+00:00"
    assert evt.payload["summary"]["reward_total"] == "1"


def test_economic_cycle_runtime_uses_canonical_constructor_not_wall_clock_commit_epoch():
    source = inspect.getsource(__import__("ilc_core.rc.economic_cycle_runtime", fromlist=[""]))

    assert "make_canonical_commit_epoch_event" in source
    assert "make_commit_epoch_event" not in source
    call_block = source.split("event = make_canonical_commit_epoch_event(", 1)[1].split(
        "ledger.apply_epoch_settlement", 1
    )[0]
    assert "created_at" not in call_block


def test_vote_weight_float_rejected_at_consensus_boundaries_and_decimal_finality_survives():
    with pytest.raises(CircuitBreakerInterfaceError, match="vote_weight"):
        summarize_circuit_breaker_quorum_state(
            [
                {
                    "validator_id": "v1",
                    "cluster_id": "c1",
                    "vote_weight": 0.5,
                    "circuit_breaker_requested": True,
                }
            ]
        )

    with pytest.raises(ConsensusEpochStateValidationError, match="vote_weight"):
        generate_quorum_record(
            {
                "attestation_ref": "att-1",
                "block_hash": "block-a",
                "epoch_index": 1,
                "quorum_state_digest": "digest-a",
                "validator_id": "validator-a",
                "vote_weight": 0.5,
            }
        )

    result = evaluate_epoch_finality(
        [
            {"block_hash": "block-a", "epoch_index": 1, "vote_weight": Decimal("0.34")},
            {"block_hash": "block-a", "epoch_index": 1, "vote_weight": Decimal("0.33")},
            {"block_hash": "block-b", "epoch_index": 1, "vote_weight": Decimal("0.33")},
        ],
        {"numerator": 2, "denominator": 3},
    )
    assert result["finality_status"] == "finalized"
    assert result["canonical_block_hash"] == "block-a"


def test_finality_weight_aggregation_uses_decimal_internally():
    aggregate = _aggregate_weights(
        [
            {"block_hash": "block-a", "vote_weight": Decimal("0.1")},
            {"block_hash": "block-a", "vote_weight": Decimal("0.2")},
        ]
    )

    assert aggregate == {"block-a": Decimal("0.3")}


def test_sensitive_runtime_guardrail_still_passes_after_phase_1235_mutation():
    result = subprocess.run(
        [".venv/bin/python", "tools/check_sensitive_runtime_coding_taboos.py"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout
