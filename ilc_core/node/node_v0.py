# SPDX-License-Identifier: AGPL-3.0-or-later
"""
ILC Node v0 Runtime.

Minimal node runtime with persistent NDJSON event log.
Uses existing protocol primitives from ilc_core.protocol.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from ilc_core.protocol.event_log import (
    ProtocolEventLog,
    make_event,
)
from ilc_core.protocol.event_export import export_event_log_to_csv


class ILCNodeV0:
    """
    Minimal ILC node runtime with persistent event logging.
    
    Appends protocol events to an NDJSON file and provides
    CSV export utilities.
    """
    
    def __init__(
        self,
        node_id: str,
        data_dir: Path | str,
        event_log_path: Optional[Path | str] = None,
    ) -> None:
        """
        Initialize ILC Node v0.
        
        Args:
            node_id: Unique identifier for this node.
            data_dir: Directory for persistent data storage.
            event_log_path: Optional custom path for event log.
                           Defaults to data_dir / "event_log.ndjson".
        """
        self.node_id = node_id
        self.data_dir = Path(data_dir)
        
        if event_log_path is None:
            self.event_log_path = self.data_dir / "event_log.ndjson"
        else:
            self.event_log_path = Path(event_log_path)
        
        # Create underlying event log
        self._event_log = ProtocolEventLog(self.event_log_path)
    
    def _record_event(self, kind: str, payload: Dict[str, Any]) -> None:
        """Internal helper to create and append an event."""
        event = make_event(kind=kind, payload=payload, source="node")
        self._event_log.append(event)
    
    def record_task_outcome(self, payload: Dict[str, Any]) -> None:
        """
        Record a task_outcome event.
        
        Args:
            payload: Task outcome data (task_id, agent_id, success, etc).
        """
        self._record_event("task_outcome", payload)
    
    def record_epoch_summary(self, payload: Dict[str, Any]) -> None:
        """
        Record an epoch_summary event.
        
        Args:
            payload: Epoch summary data (epoch, total_tasks, etc).
        """
        self._record_event("epoch_summary", payload)
    
    def record_claim(self, payload: Dict[str, Any]) -> None:
        """
        Record a claim event.
        
        Args:
            payload: Claim data (id, agent_id, content, etc).
        """
        self._record_event("claim", payload)
    
    def record_refutation(self, payload: Dict[str, Any]) -> None:
        """
        Record a refutation event.
        
        Args:
            payload: Refutation data (id, target_id, agent_id, etc).
        """
        self._record_event("refutation", payload)
    
    def export_event_log_csv(
        self,
        tasks_csv_path: Path | str,
        epochs_csv_path: Path | str,
        claims_csv_path: Optional[Path | str] = None,
    ) -> Dict[str, int]:
        """
        Export event log to CSV files.
        
        Args:
            tasks_csv_path: Output path for task outcomes CSV.
            epochs_csv_path: Output path for epoch summaries CSV.
            claims_csv_path: Optional output path for claims CSV.
            
        Returns:
            Dict with counts of exported events by type.
        """
        return export_event_log_to_csv(
            self.event_log_path,
            tasks_csv_path=tasks_csv_path,
            epochs_csv_path=epochs_csv_path,
            claims_csv_path=claims_csv_path,
        )
    
    @property
    def event_log(self) -> ProtocolEventLog:
        """Access the underlying event log for iteration."""
        return self._event_log
