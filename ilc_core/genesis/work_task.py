# SPDX-License-Identifier: AGPL-3.0-only
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict, field_serializer, field_validator

class EpistemicWorkTask(BaseModel):
    task_id: str
    task_class: Literal[
        "star.map.embedding",
        "contradiction.sweep",
        "graph.compression",
        "stability.simulation",
        "custom",
    ]
    agent_id: str
    region_scope: List[str]
    difficulty_factor: Optional[Decimal] = None
    input_data: Optional[Dict[str, Any]] = None
    output_hash: Optional[str] = None
    verification_method: Literal[
        "hash-match",
        "signature",
        "zk-proof",
        "peer-audit",
        "replayable-simulation",
    ]
    bounty_id: Optional[str] = None
    staking_beneficiary: Optional[str] = None
    ecu_estimate: Optional[Decimal] = Field(default=None, alias="ecu.estimate")
    task_state: Literal[
        "proposed",
        "claimed",
        "completed",
        "audited",
        "rewarded",
        "expired",
    ]
    timestamp_created: int

    # allow both `ecu_estimate` and `ecu.estimate` in input, but always
    # emit `ecu.estimate` on export
    model_config = ConfigDict(
        populate_by_name=True,
        protected_namespaces=(),
    )

    @field_validator("ecu_estimate", mode="before")
    @classmethod
    def _validate_ecu_estimate(cls, value: object) -> Optional[Decimal]:
        return cls._validate_non_negative_decimal(value, "epistemic_work_task_ecu_estimate_invalid")

    @field_validator("difficulty_factor", mode="before")
    @classmethod
    def _validate_difficulty_factor(cls, value: object) -> Optional[Decimal]:
        return cls._validate_non_negative_decimal(value, "epistemic_work_task_difficulty_factor_invalid")

    @classmethod
    def _validate_non_negative_decimal(cls, value: object, token: str) -> Optional[Decimal]:
        if value is None:
            return None
        if isinstance(value, (bool, float)):
            raise ValueError(token)
        if not isinstance(value, (Decimal, int, str)):
            raise ValueError(token)
        try:
            amount = value if isinstance(value, Decimal) else Decimal(str(value))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(token) from exc
        if not amount.is_finite():
            raise ValueError(f"{token}_non_finite")
        if amount < Decimal("0"):
            raise ValueError(f"{token}_negative")
        return amount

    @field_serializer("ecu_estimate")
    def _serialize_ecu_estimate(self, value: Optional[Decimal]) -> Optional[str]:
        return None if value is None else str(value)

    @field_serializer("difficulty_factor")
    def _serialize_difficulty_factor(self, value: Optional[Decimal]) -> Optional[str]:
        return None if value is None else str(value)

def ep_task_to_json(task: EpistemicWorkTask) -> Dict[str, Any]:
    """
    Serialize an EpistemicWorkTask to a JSON-serializable dict
    matching the genesis.epistemic.work.task schema (aliases included).
    """
    return task.model_dump(by_alias=True, mode="json")

def ep_task_from_json(data: Dict[str, Any]) -> EpistemicWorkTask:
    """
    Parse a genesis.epistemic.work.task-style dict into EpistemicWorkTask.
    """
    return EpistemicWorkTask.model_validate(data)
