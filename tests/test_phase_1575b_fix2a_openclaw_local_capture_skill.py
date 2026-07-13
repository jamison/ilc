from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.sidecars.openclaw_local_capture import (
    ALLOWED_CANDIDATE_NODE_TYPES,
    ALLOWED_CONSENT_ACTIONS,
    ESTIMATE_SCHEMA_VERSION,
    SCORE_FIELDS,
    build_capture_envelope,
    build_estimate_record,
    evaluate_consent_gate,
    raw_payload_sha256,
)


def _payload(order: str) -> dict[str, object]:
    if order == "ab":
        return {"a": "one", "b": {"c": 2}, "candidate_node_type": "claim_candidate"}
    return {"candidate_node_type": "claim_candidate", "b": {"c": 2}, "a": "one"}


def test_canonical_payload_hash_is_stable_across_key_order() -> None:
    assert raw_payload_sha256(_payload("ab")) == raw_payload_sha256(_payload("ba"))


def test_envelope_fields_are_not_in_raw_payload_hash() -> None:
    payload = _payload("ab")
    first = build_capture_envelope(
        raw_payload=payload,
        payload_kind="reply",
        operator_agent_id="operator:one",
        local_agent_id="agent:one",
        provider_id="provider:a",
        session_id="session-a",
    )
    second = build_capture_envelope(
        raw_payload=payload,
        payload_kind="reply",
        operator_agent_id="operator:two",
        local_agent_id="agent:two",
        provider_id="provider:b",
        session_id="session-b",
    )
    assert first.raw_payload_sha256 == second.raw_payload_sha256
    assert first.capture_id != second.capture_id


@pytest.mark.parametrize(
    "bad_payload",
    [
        {"candidate_node_type": "claim_candidate", "x": 1.5},
        {"candidate_node_type": "claim_candidate", "x": float("nan")},
        {"candidate_node_type": "claim_candidate", "x": float("inf")},
        {"candidate_node_type": "claim_candidate", "x": True},
    ],
)
def test_float_nan_infinity_and_bool_inputs_are_rejected(bad_payload: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        raw_payload_sha256(bad_payload)


def test_consent_gate_rejects_submission_without_consent() -> None:
    envelope = build_capture_envelope(
        raw_payload=_payload("ab"),
        payload_kind="reply",
        operator_agent_id="operator:one",
        local_agent_id="agent:one",
        provider_id="provider:a",
        session_id="session-a",
        consent_state="needs_review",
    )
    decision = evaluate_consent_gate(envelope, action="submit")
    assert decision["allowed"] is False
    assert decision["public_submission_performed"] is False


def test_consent_gate_allows_only_submission_intent_when_approved() -> None:
    envelope = build_capture_envelope(
        raw_payload=_payload("ab"),
        payload_kind="reply",
        operator_agent_id="operator:one",
        local_agent_id="agent:one",
        provider_id="provider:a",
        session_id="session-a",
        consent_state="approved_for_public_submission",
    )
    decision = evaluate_consent_gate(envelope, action="submit")
    assert decision["allowed"] is True
    assert decision["authority"] == "submission_intent_only"
    assert decision["public_submission_performed"] is False


def test_consent_gate_rejects_unknown_actions() -> None:
    envelope = build_capture_envelope(
        raw_payload=_payload("ab"),
        payload_kind="reply",
        operator_agent_id="operator:one",
        local_agent_id="agent:one",
        provider_id="provider:a",
        session_id="session-a",
        consent_state="approved_for_public_submission",
    )
    with pytest.raises(ValueError):
        evaluate_consent_gate(envelope, action="publish-now")
    assert "submit" in ALLOWED_CONSENT_ACTIONS


def test_ecu_estimate_schema_is_decimal_non_binding_and_complete() -> None:
    envelope = build_capture_envelope(
        raw_payload=_payload("ab"),
        payload_kind="reply",
        operator_agent_id="operator:one",
        local_agent_id="agent:one",
        provider_id="provider:a",
        session_id="session-a",
    )
    estimate = build_estimate_record(envelope)
    assert estimate["estimate_schema"] == ESTIMATE_SCHEMA_VERSION
    assert estimate["estimate_label"] == "non_binding_private_projection"
    assert estimate["not_wallet_balance"] is True
    scores = estimate["score_fields"]
    assert set(scores) == set(SCORE_FIELDS)
    for value in scores.values():
        parsed = Decimal(value)
        assert Decimal("0") <= parsed <= Decimal("1")
    estimate_range = estimate["ecu_range"]
    assert set(estimate_range) == {"ceiling", "floor"}
    floor = Decimal(estimate_range["floor"])
    ceiling = Decimal(estimate_range["ceiling"])
    assert Decimal("0") <= floor <= ceiling <= Decimal("1")
    assert ceiling > Decimal("0")


def test_ecu_estimate_range_drops_when_local_duplicate_exists() -> None:
    envelope = build_capture_envelope(
        raw_payload=_payload("ab"),
        payload_kind="reply",
        operator_agent_id="operator:one",
        local_agent_id="agent:one",
        provider_id="provider:a",
        session_id="session-a",
    )
    first = build_estimate_record(envelope, local_duplicate_count=0)
    duplicate = build_estimate_record(envelope, local_duplicate_count=1)
    assert Decimal(first["ecu_range"]["ceiling"]) > Decimal(duplicate["ecu_range"]["ceiling"])


def test_estimate_rejects_malformed_mapping_envelope() -> None:
    with pytest.raises(ValueError):
        build_estimate_record({"candidate_node_type": "claim_candidate", "payload_kind": "reply"})


def test_candidate_classification_allowlist_rejects_unknown_classes() -> None:
    with pytest.raises(ValueError):
        build_capture_envelope(
            raw_payload={"candidate_node_type": "unknown_candidate", "text": "x"},
            payload_kind="reply",
            operator_agent_id="operator:one",
            local_agent_id="agent:one",
            provider_id="provider:a",
            session_id="session-a",
        )
    assert "claim_candidate" in ALLOWED_CANDIDATE_NODE_TYPES


def test_operator_and_local_agent_ids_are_preserved_separately() -> None:
    envelope = build_capture_envelope(
        raw_payload=_payload("ab"),
        payload_kind="reply",
        operator_agent_id="operator:one",
        local_agent_id="agent:one",
        provider_id="provider:a",
        session_id="session-a",
        created_epoch=0,
    )
    data = envelope.to_dict()
    assert data["operator_agent_id"] == "operator:one"
    assert data["local_agent_id"] == "agent:one"
    assert data["created_epoch"] == 0


def test_rehearsal_tool_writes_deterministic_evidence() -> None:
    subprocess.run([sys.executable, "tools/openclaw_local_capture_rehearsal.py"], check=True)
    path = Path("out/block6_openclaw_local_capture_fix2a/evidence_records.json")
    first = path.read_bytes()
    first_hash = hashlib.sha256(first).hexdigest()
    subprocess.run([sys.executable, "tools/openclaw_local_capture_rehearsal.py"], check=True)
    second = path.read_bytes()
    assert hashlib.sha256(second).hexdigest() == first_hash
    data = json.loads(second)
    assert data["no_publication_performed"] is True
    assert data["no_public_graph_submission"] is True
