import json

import pytest

from ilc_core.harness.consent_gate import ConsentDecision, ConsentGate
from ilc_core.harness.local_node_capture import LocalNodeCapture


def test_local_node_capture_requires_consent_and_is_deterministic() -> None:
    gate = ConsentGate(
        [
            ConsentDecision(
                subject_id="agent-1",
                purpose="private_query_response_artifact",
                allowed=True,
                decision_id="consent-1",
            )
        ]
    )
    capture = LocalNodeCapture(
        purpose="private_query_response_artifact",
        consent_gate=gate,
    )

    first = capture.capture(
        capture_id="capture-1",
        node_id="node-1",
        subject_id="agent-1",
        payload={"z": "last", "a": "first"},
    )
    second = capture.capture(
        capture_id="capture-1",
        node_id="node-1",
        subject_id="agent-1",
        payload={"a": "first", "z": "last"},
    )

    assert first.sha256 == second.sha256
    assert first.production_graph_write is False
    assert first.public_rc_exclude is True
    assert json.loads(first.canonical_json)["production_graph_write"] is False


def test_consent_gate_denies_missing_or_negative_decisions() -> None:
    gate = ConsentGate.from_fixture(
        [
            {
                "subject_id": "agent-1",
                "purpose": "private_query_response_artifact",
                "allowed": False,
                "decision_id": "deny-1",
            }
        ]
    )
    capture = LocalNodeCapture(
        purpose="private_query_response_artifact",
        consent_gate=gate,
    )

    with pytest.raises(ValueError) as exc:
        capture.capture(
            capture_id="capture-1",
            node_id="node-1",
            subject_id="agent-1",
            payload={"field": "value"},
        )

    assert str(exc.value) == "consent_gate_denied"
