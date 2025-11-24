from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional
from pathlib import Path
import json

try:
    import yaml
except ImportError:
    yaml = None  # YAML optional


@dataclass
class HardwareArchetype:
    name: str
    base_potential: float
    stake_fraction_min: float
    stake_fraction_max: float


def load_hardware_archetypes(
    config_path: Optional[str] = None,
) -> Dict[str, HardwareArchetype]:
    """
    Load hardware archetypes from config/hardware_archetypes_mvp.yaml (or JSON fallback).

    NOTE: This is a simulation / L2 helper. The core L1 protocol does not
    branch on hardware type – it only sees benchmark potential, stake, and
    epistemic results.
    """
    if config_path is None:
        root = Path(__file__).resolve().parents[1]  # ilc_core/ -> project root
        yaml_path = root / "config" / "hardware_archetypes_mvp.yaml"
        json_path = root / "config" / "hardware_archetypes_mvp.json"
    else:
        yaml_path = Path(config_path)
        json_path = yaml_path.with_suffix(".json")

    data: Dict[str, Any] = {}

    if yaml is not None and yaml_path.exists():
        with yaml_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    elif json_path.exists():
        with json_path.open("r", encoding="utf-8") as f:
            data = json.load(f) or {}
    else:
        # If neither exists, we might just return empty or raise.
        # For MVP, let's raise if we expected default config to be there.
        # But if we are in a test env where config doesn't exist, empty is safer.
        # Let's check if we are using default path and it's missing.
        if config_path is None and not yaml_path.exists() and not json_path.exists():
             raise FileNotFoundError("No hardware archetype config found.")
        return {}

    raw = data.get("hardware_archetypes", {})
    archetypes: Dict[str, HardwareArchetype] = {}
    for name, cfg in raw.items():
        archetypes[name] = HardwareArchetype(
            name=name,
            base_potential=float(cfg.get("base_potential", 0.0)),
            stake_fraction_min=float(cfg.get("stake_fraction_min", 0.05)),
            stake_fraction_max=float(cfg.get("stake_fraction_max", 0.25)),
        )
    return archetypes


from .agent import EveAgent  # import at bottom to avoid circular import if needed


def configure_agent_from_archetype(agent: EveAgent, archetype: HardwareArchetype) -> None:
    """
    Apply an archetype to an EveAgent instance.

    This is *not* a protocol-level rule – it's a sim/helper function:

    - Sets trust_vector["potential"] to archetype.base_potential.
    - Installs strategy_* attributes that auto_mine_claim() can optionally read.
    """
    agent.trust_vector["potential"] = archetype.base_potential

    # Strategy tuning knobs for auto_mine_claim()
    setattr(agent, "strategy_stake_fraction_min", archetype.stake_fraction_min)
    setattr(agent, "strategy_stake_fraction_max", archetype.stake_fraction_max)
