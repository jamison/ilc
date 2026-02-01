"""
ILC Node v0 Tests.

Tests for the minimal ILC node runtime with persistent NDJSON event log.
"""

import tempfile
from pathlib import Path

from ilc_core.node.node_v0 import ILCNodeV0


class TestILCNodeV0:
    """Tests for ILCNodeV0 runtime."""

    def test_node_appends_events_to_ndjson(self) -> None:
        """Node appends events to NDJSON file."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            data_dir = Path(tmp_dir) / "data"
            node = ILCNodeV0(node_id="test-node-1", data_dir=data_dir)
            
            # Record two events
            node.record_task_outcome({
                "task_id": "task-1",
                "agent_id": "agent-1",
                "success": True,
            })
            node.record_epoch_summary({
                "epoch": 1,
                "total_tasks": 10,
            })
            
            # Assert file exists and has 2 lines
            assert node.event_log_path.exists()
            with open(node.event_log_path, "r", encoding="utf-8") as f:
                lines = [line for line in f if line.strip()]
            assert len(lines) == 2

    def test_node_iter_events_roundtrip(self) -> None:
        """Events can be read back via iter_events."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            data_dir = Path(tmp_dir) / "data"
            node = ILCNodeV0(node_id="test-node-2", data_dir=data_dir)
            
            # Record events in sequence
            node.record_task_outcome({"task_id": "t1"})
            node.record_epoch_summary({"epoch": 1})
            node.record_claim({"id": "c1", "content": "test claim"})
            node.record_refutation({"id": "r1", "target_id": "c1"})
            
            # Read back and verify kinds
            events = list(node.event_log.iter_events())
            kinds = [e.kind for e in events]
            
            assert kinds == ["task_outcome", "epoch_summary", "claim", "refutation"]

    def test_node_export_event_log_csv(self) -> None:
        """CSV export produces files with headers."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            data_dir = Path(tmp_dir) / "data"
            node = ILCNodeV0(node_id="test-node-3", data_dir=data_dir)
            
            # Record one of each type
            node.record_task_outcome({
                "task_id": "task-1",
                "agent_id": "agent-1",
                "success": True,
            })
            node.record_epoch_summary({
                "epoch": 1,
                "total_tasks": 5,
            })
            node.record_claim({
                "id": "claim-1",
                "agent_id": "agent-1",
                "content": "Test claim content",
            })
            
            # Export to CSV
            tasks_csv = Path(tmp_dir) / "tasks.csv"
            epochs_csv = Path(tmp_dir) / "epochs.csv"
            claims_csv = Path(tmp_dir) / "claims.csv"
            
            counts = node.export_event_log_csv(
                tasks_csv_path=tasks_csv,
                epochs_csv_path=epochs_csv,
                claims_csv_path=claims_csv,
            )
            
            # Verify files exist and have headers
            assert tasks_csv.exists()
            assert epochs_csv.exists()
            assert claims_csv.exists()
            
            with open(tasks_csv, "r", encoding="utf-8") as f:
                header = f.readline()
                assert "task_id" in header
            
            with open(epochs_csv, "r", encoding="utf-8") as f:
                header = f.readline()
                assert "epoch" in header
            
            with open(claims_csv, "r", encoding="utf-8") as f:
                header = f.readline()
                assert "id" in header
            
            # Verify counts
            assert counts["task_outcomes"] == 1
            assert counts["epoch_summaries"] == 1
            assert counts["claims"] == 1
