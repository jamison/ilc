from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field

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
    difficulty_factor: Optional[float] = None
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
    ecu_estimate: Optional[float] = Field(default=None, alias="ecu.estimate")
    task_state: Literal[
        "proposed",
        "claimed",
        "completed",
        "audited",
        "rewarded",
        "expired",
    ]
    timestamp_created: int

    class Config:
        # allow both `ecu_estimate` and `ecu.estimate` in input, but always
        # emit `ecu.estimate` on export
        populate_by_name = True
        allow_population_by_field_name = True
        protected_namespaces = ()

def ep_task_to_json(task: EpistemicWorkTask) -> Dict[str, Any]:
    """
    Serialize an EpistemicWorkTask to a JSON-serializable dict
    matching the genesis.epistemic.work.task schema (aliases included).
    """
    return task.model_dump(by_alias=True)

def ep_task_from_json(data: Dict[str, Any]) -> EpistemicWorkTask:
    """
    Parse a genesis.epistemic.work.task-style dict into EpistemicWorkTask.
    """
    return EpistemicWorkTask.model_validate(data)
