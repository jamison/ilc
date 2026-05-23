# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

"""
Task abstractions for the ILC economics sandbox.

TaskDescriptor describes a unit of work (task_type, agent_id, payload, meta),
and TaskQueue provides a simple FIFO queue. Simulations use these helpers to
model how tasks might be scheduled and processed without committing to a
network-level job format.

For how this is used in the economics sandbox and how it might map to future
genesis primitives, see docs/protocol_econ_surfaces_mvp.md.
"""
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, List, Optional
from collections import deque
from ilc_core.genesis import EpistemicWorkTask


@dataclass
class TaskDescriptor:
    """
    Minimal description of a unit of work in the sandbox.

    Fields are intentionally generic: task_id, task_type, agent_id, payload, and
    meta. Simulations can attach domain labels, success probabilities, or other
    hints via payload/meta without affecting the queueing logic.

    MVP fields
    ----------
    task_id : str
        Local identifier for the task (not necessarily a graph node id).
        In simulations this can be any stable label like "ballast_3_12".
    task_type : str
        Logical task type, e.g.:
        - "claim.submit"
        - "refute.attempt"
        - "contradiction.sweep"
    agent_id : Optional[str]
        The logical agent responsible for executing this task
        (e.g. "agent:ballast", "agent:gpu:1").
    payload : Dict[str, Any]
        Free-form data needed to execute the task. For claims this might
        include "content" and "parent_id".
    meta : Dict[str, Any]
        Extra metadata for simulators / telemetry (epoch index, domain tag,
        etc.). Not interpreted by TaskQueue itself.
    """
    task_id: str
    task_type: str
    agent_id: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_epistemic_work_task(
        cls,
        task: EpistemicWorkTask,
        *,
        task_type: str = "genesis.epistemic.work.task",
        agent_id_override: Optional[str] = None,
    ) -> TaskDescriptor:
        """
        Convenience helper: wrap an EpistemicWorkTask into a TaskDescriptor
        suitable for enqueuing in TaskQueue.

        - task_id comes from task.task_id
        - agent_id defaults to task.agent_id, but can be overridden
        - payload carries the full serialized EpistemicWorkTask
        - meta is currently empty (can be extended later)
        """
        payload = {"epistemic_work_task": task.model_dump(by_alias=True)}
        return cls(
            task_id=task.task_id,
            task_type=task_type,
            agent_id=agent_id_override or task.agent_id,
            payload=payload,
            meta={},
        )


class TaskQueue:
    """
        - future schedulers / routers
        - optional API endpoints

    This is *not* a distributed queue or a durability layer; it's just
    an in-memory helper for MVP simulations and a future task router.
    """

    def __init__(self) -> None:
        self._q: Deque[TaskDescriptor] = deque()

    # Core API -----------------------------------------------------------
    def add_task(self, task: TaskDescriptor) -> None:
        """Append a task to the back of the queue."""
        self._q.append(task)

    def pop_next(self) -> Optional[TaskDescriptor]:
        """
        Pop the next task in FIFO order.

        Returns None if the queue is empty.
        """
        if not self._q:
            return None
        return self._q.popleft()

    # Convenience methods -----------------------------------------------
    def is_empty(self) -> bool:
        """Return True if there are no tasks pending."""
        return not self._q

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._q)

    def drain(self) -> List[TaskDescriptor]:
        """
        Pop all tasks currently in the queue and return them as a list.

        This is convenient in simulations where we want to snapshot the
        workload and process it in a batch.
        """
        items: List[TaskDescriptor] = []
        while self._q:
            items.append(self._q.popleft())
        return items
