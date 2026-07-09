# SPDX-License-Identifier: AGPL-3.0-only
"""PUBLIC_RC_EXCLUDE: private_maintenance_task_executor
PUBLIC_RC_EXCLUDE_REASON: Private deterministic maintenance executor. No live LLM calls, public endpoint, or credit minting.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Mapping

from ilc_core.harness.idle_capacity_scheduler import ScheduledMaintenanceTask
from ilc_core.private_json_guardrails import canonical_json, freeze_json_value, reject_float, thaw_json_value

MAINTENANCE_TASK_EXECUTOR_NOT_ACTIVATED = True
MAX_ARTIFACT_FIELDS = 64


def _canonical_json(payload: Mapping[str, object]) -> str:
    return canonical_json(payload, float_token="maintenance_executor_float_not_allowed")


@dataclass(frozen=True)
class QueryResponseArtifact:
    artifact_id: str
    task_id: str
    query_node: Mapping[object, object]
    response_node: Mapping[object, object]
    processing_capacity_tier: str
    canonical_json: str
    sha256: str
    public_rc_exclude: bool = True


class MaintenanceTaskExecutor:
    """Executes deterministic private maintenance fixtures into query-response artifacts."""

    def __init__(self, *, processing_capacity_tier: str = "local_fixture_tier_0") -> None:
        if processing_capacity_tier == "":
            raise ValueError("maintenance_executor_missing_capacity_tier")
        self._processing_capacity_tier = processing_capacity_tier

    def execute(
        self,
        *,
        task: ScheduledMaintenanceTask,
        query_payload: Mapping[str, object],
        response_payload: Mapping[str, object],
    ) -> QueryResponseArtifact:
        if len(query_payload) > MAX_ARTIFACT_FIELDS or len(response_payload) > MAX_ARTIFACT_FIELDS:
            raise ValueError("maintenance_executor_artifact_field_cap_exceeded")
        reject_float(query_payload, "maintenance_executor_float_not_allowed")
        reject_float(response_payload, "maintenance_executor_float_not_allowed")

        artifact_id = f"qr:{task.task_id}"
        query_node = {
            "node_id": f"{artifact_id}:query",
            "payload": dict(query_payload),
            "truth_primitive": "assert.truth",
        }
        response_node = {
            "node_id": f"{artifact_id}:response",
            "payload": dict(response_payload),
            "truth_primitive": "validate.claim",
        }
        envelope = {
            "artifact_id": artifact_id,
            "processing_capacity_tier": self._processing_capacity_tier,
            "production_graph_write": False,
            "public_rc_exclude": True,
            "query_node": query_node,
            "response_node": response_node,
            "task_id": task.task_id,
        }
        canonical_json = _canonical_json(envelope)
        return QueryResponseArtifact(
            artifact_id=artifact_id,
            task_id=task.task_id,
            query_node=freeze_json_value(query_node),  # type: ignore[arg-type]
            response_node=freeze_json_value(response_node),  # type: ignore[arg-type]
            processing_capacity_tier=self._processing_capacity_tier,
            canonical_json=canonical_json,
            sha256=hashlib.sha256(canonical_json.encode("utf-8")).hexdigest(),
        )


def verify_query_response_artifact(artifact: QueryResponseArtifact) -> bool:
    envelope = {
        "artifact_id": artifact.artifact_id,
        "processing_capacity_tier": artifact.processing_capacity_tier,
        "production_graph_write": False,
        "public_rc_exclude": True,
        "query_node": thaw_json_value(artifact.query_node),
        "response_node": thaw_json_value(artifact.response_node),
        "task_id": artifact.task_id,
    }
    canonical_json = _canonical_json(envelope)
    return (
        canonical_json == artifact.canonical_json
        and hashlib.sha256(canonical_json.encode("utf-8")).hexdigest() == artifact.sha256
        and artifact.public_rc_exclude is True
    )
