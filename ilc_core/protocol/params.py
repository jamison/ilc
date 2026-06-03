# SPDX-License-Identifier: AGPL-3.0-only
from dataclasses import dataclass
from typing import Optional, Any, Dict
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
    
    # Phase 61B: Econ Params (Placeholders for demo)
    burn_rate: float = 0.0
    pb_rate: float = 0.0

    # Phase 63C: Closed-loop knobs
    base_reward: float = 1.0
    qa_min_score: float = 0.0
    toll_per_task: float = 0.0
    competence_kappa: float = 1.0  # Power law exponent for score->reward (was kappa)
    competence_mult_enabled: bool = False
    competence_mult_min_floor: float = 1.0
    competence_mult_max_cap: float = 1.0
    qa_enabled: bool = True  # Toggle for QA filtering. If False, all suggestions pass.

def parse_bool(value: Any, default: bool = False) -> bool:
    """
    Robust boolean parser.
    Handles None, bool, int, float, and strings like "true"/"false"/"0", etc.
    """
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        v_lower = value.strip().lower()
        if v_lower in ("true", "1", "yes", "y", "on"):
            return True
        if v_lower in ("false", "0", "no", "n", "off", ""):
            return False
        # Fallback
        return default
    # Fallback for non-string values
    return default

def _normalize_bool_field(key: str, value: Any) -> bool:
    """Normalize a boolean field value with key-specific defaults."""
    if key == "qa_enabled":
        if value is None:
            return True
        return parse_bool(value, default=True)
    return parse_bool(value, default=False)


def _normalize_float_field(value: Any) -> Any:
    """Normalize a float field value with fallback to raw on coercion failure."""
    try:
        return float(value)
    except (ValueError, TypeError):
        if value is not None:
            return value
    return value


def normalize_protocol_overrides(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize legacy parameter keys to canonical fields and coerce types.
    """
    normalized: Dict[str, Any] = {}
    
    # Mappings: legacy -> canonical
    # canonical -> canonical (identity) is implicit if we iterate raw and don't match legacy
    # But we want to handle type coercion too.
    
    # Explicit mapping for renames
    key_map = {
        "ce_enabled": "competence_mult_enabled",
        "ce_min_floor": "competence_mult_min_floor",
        "ce_max_cap": "competence_mult_max_cap",
        "toll": "toll_per_task",
        "kappa": "competence_kappa",
        "qa": "qa_min_score",
        # Keep canonicals too just in case we need to explicit map them? 
        # No, we'll handle pass-through.
    }
    
    # Fields that need specific type coercion
    bool_fields = {"competence_mult_enabled", "qa_enabled"}
    float_fields = {
        "toll_per_task", "competence_kappa", "qa_min_score", 
        "base_reward", "burn_rate", "pb_rate",
        "competence_mult_min_floor", "competence_mult_max_cap",
        "weight_supports", "weight_refutes", "weight_equivalent", "weight_depends_on"
    }
    
    for k, v in raw.items():
        # 1. Map Keys
        canonical_k = key_map.get(k, k)
        
        # 2. Map Values / Coerce
        if canonical_k in bool_fields:
            normalized[canonical_k] = _normalize_bool_field(canonical_k, v)
        elif canonical_k in float_fields:
            normalized[canonical_k] = _normalize_float_field(v)
        else:
            # Pass through string fields or unknowns
            normalized[canonical_k] = v
            
    return normalized

def load_protocol_params(path: Optional[PathLike] = None) -> ProtocolParams:
    """
    Load ProtocolParams from a JSON file if provided; otherwise return defaults.
    Uses normalization to handle legacy keys and safe parsing.
    """
    if path is None:
        return ProtocolParams()

    p = Path(path)
    if not p.exists():
        return ProtocolParams()

    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # Normalize
    data = normalize_protocol_overrides(data)

    # Construct. defaults are handled by dataclass if missing from dict.
    # Note: data coming from normalize_protocol_overrides has canonical keys and coerced types.
    # We can perform a dict unpack with filter? 
    # Or explicitly map like before (safer for MVP expliciteness).
    
    # We can use fields() or explicit args. Explicit is robust.
    return ProtocolParams(
        local_influence_algorithm_id=data.get(
            "local_influence_algorithm_id",
            "algo.local_influence.v0_toy",
        ),
        weight_supports=float(data.get("weight_supports", 1.0)),
        weight_refutes=float(data.get("weight_refutes", 1.0)),
        weight_equivalent=float(data.get("weight_equivalent", 0.0)),
        weight_depends_on=float(data.get("weight_depends_on", 0.0)),
        burn_rate=float(data.get("burn_rate", 0.0)),
        pb_rate=float(data.get("pb_rate", 0.0)),
        base_reward=float(data.get("base_reward", 1.0)),
        qa_min_score=float(data.get("qa_min_score", 0.0)),
        toll_per_task=float(data.get("toll_per_task", 0.0)),
        competence_kappa=float(data.get("competence_kappa", 1.0)), # Renamed
        
        competence_mult_enabled=parse_bool(data.get("competence_mult_enabled", False)),
        competence_mult_min_floor=float(data.get("competence_mult_min_floor", 1.0)),
        competence_mult_max_cap=float(data.get("competence_mult_max_cap", 1.0)),
        
        qa_enabled=parse_bool(data.get("qa_enabled", True), default=True),
    )
