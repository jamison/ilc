from dataclasses import dataclass
from typing import Optional
import json
from pathlib import Path
from os import PathLike

@dataclass
class ProtocolParams:
    """
    Minimal protocol parameter set for MVP.

    This will be extended over time (fees, slashing fractions, ECU weights, etc.).
    """
    local_influence_algorithm_id: str = "algo.local_influence.v0_toy"

    # Optional toy weights to pass to the local influence function
    weight_supports: float = 1.0
    weight_refutes: float = 1.0
    weight_equivalent: float = 0.0
    weight_depends_on: float = 0.0

def load_protocol_params(path: Optional[PathLike] = None) -> ProtocolParams:
    """
    Load ProtocolParams from a JSON file if provided; otherwise return defaults.

    Expected JSON structure:
        {
            "local_influence_algorithm_id": "...",
            "weight_supports": 1.0,
            ...
        }
    """
    if path is None:
        return ProtocolParams()

    p = Path(path)
    if not p.exists():
        return ProtocolParams()

    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return ProtocolParams(
        local_influence_algorithm_id=data.get(
            "local_influence_algorithm_id",
            "algo.local_influence.v0_toy",
        ),
        weight_supports=float(data.get("weight_supports", 1.0)),
        weight_refutes=float(data.get("weight_refutes", 1.0)),
        weight_equivalent=float(data.get("weight_equivalent", 0.0)),
        weight_depends_on=float(data.get("weight_depends_on", 0.0)),
    )
