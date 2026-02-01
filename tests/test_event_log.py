"""
Tests for ILC Event Log and commit.epoch support.
"""

import json
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from ilc_core.protocol.event_log import (
    ProtocolEvent,
    ProtocolEventLog,
    make_commit_epoch_event,
    validate_commit_epoch_payload,
)


class TestEventLog:
    def test_append_and_iter(self):
        with TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "events.ndjson"
            log = ProtocolEventLog(log_path)

            evt1 = ProtocolEvent(
                kind="task_outcome",
                payload={"task_id": "1"},
                received_at="2026-02-01T12:00:00Z"
            )
            log.append(evt1)

            events = list(log.iter_events())
            assert len(events) == 1
            assert events[0].kind == "task_outcome"
            assert events[0].payload["task_id"] == "1"


class TestCommitEpochEvent:
    def test_valid_commit_epoch_construct(self):
        """Ensure make_commit_epoch_event creates a valid event."""
        evt = make_commit_epoch_event(
            epoch_index=42,
            epoch_id="epoch_42_QmNodeID",
            namespace_id="QmNodeID",
            created_at="2026-02-01T12:00:00Z",
            finalization_state="committed",
            summary={
                "task_count": 150,
                "agent_count": 5,
                "reward_total": 100.5,
                "stake_total": 5000.0
            },
            checksums={
                "epoch_events_cid": "bafkqevents",
                "epoch_state_cid": "bafkqstate"
            }
        )
        
        assert evt.kind == "commit.epoch"
        assert evt.payload["epoch_index"] == 42
        assert evt.payload["finalization_state"] == "committed"

    def test_validation_passes_valid_payload(self):
        payload = {
            "event_kind": "commit.epoch",
            "epoch_index": 1,
            "epoch_id": "e1-node1",
            "namespace_id": "node1",
            "created_at": "2026-02-01T12:00:00Z",
            "finalization_state": "committed",
            "summary": {
                "task_count": 10,
                "agent_count": 2,
                "reward_total": 50.0,
                "stake_total": 1000.0
            },
            "checksums": {
                "epoch_events_cid": "cid1",
                "epoch_state_cid": "cid2"
            }
        }
        # Should not raise
        validate_commit_epoch_payload(payload)

    def test_validation_rejects_missing_fields(self):
        payload = {
            "event_kind": "commit.epoch",
            # Missing epoch_index, etc.
        }
        with pytest.raises(ValueError, match="Missing required top-level fields"):
            validate_commit_epoch_payload(payload)

    def test_validation_rejects_invalid_state(self):
        payload = {
            "event_kind": "commit.epoch",
            "epoch_index": 1,
            "epoch_id": "e1",
            "namespace_id": "n1",
            "created_at": "now",
            "finalization_state": "invalid_state",  # Wrong enum
            "summary": {},
            "checksums": {}
        }
        with pytest.raises(ValueError, match="Invalid finalization_state"):
            validate_commit_epoch_payload(payload)

    def test_emit_to_ndjson(self):
        """Test full cycle: construct -> emit -> file -> read back."""
        with TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "commit_log.ndjson"
            log = ProtocolEventLog(log_path)

            evt = make_commit_epoch_event(
                epoch_index=100,
                epoch_id="epoch_100",
                namespace_id="node_x",
                created_at="2026-02-01T12:00:00Z",
                finalization_state="committed",
                summary={
                    "task_count": 0,
                    "agent_count": 0,
                    "reward_total": 0,
                    "stake_total": 0
                },
                checksums={
                    "epoch_events_cid": "cid_events",
                    "epoch_state_cid": "cid_state"
                }
            )
            log.append(evt)

            # Read back manually to check raw JSON structure
            with open(log_path, "r") as f:
                line = f.readline()
                data = json.loads(line)
                assert data["kind"] == "commit.epoch"
                assert data["payload"]["event_kind"] == "commit.epoch"
                assert data["payload"]["epoch_index"] == 100
