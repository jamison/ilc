from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional
from pathlib import Path
import json
import logging

try:
    import yaml
except ImportError:
    yaml = None  # YAML optional

logger = logging.getLogger(__name__)


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
    root = Path(__file__).resolve().parents[1]  # ilc_core/ -> project root
    default_json_path = root / "config" / "hardware_archetypes_mvp.json"
    default_yaml_path = root / "config" / "hardware_archetypes_mvp.yaml"

    if config_path is None:
        requested_path = default_json_path
        fallback_yaml_path = default_yaml_path
    else:
        requested_path = Path(config_path)
        fallback_yaml_path = requested_path.with_suffix(".yaml")

    data: Dict[str, Any] = {}

    if requested_path.suffix in {".yaml", ".yml"}:
        if yaml is not None and requested_path.exists():
            with requested_path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        else:
            fallback_json_path = requested_path.with_suffix(".json")
            if fallback_json_path.exists():
                logger.warning(
                    "hardware_config_yaml_loader_missing_json_fallback path=%s fallback=%s",
                    requested_path,
                    fallback_json_path,
                )
                with fallback_json_path.open("r", encoding="utf-8") as f:
                    data = json.load(f) or {}
            elif config_path is None and default_json_path.exists():
                with default_json_path.open("r", encoding="utf-8") as f:
                    data = json.load(f) or {}
            else:
                return {}
    else:
        if requested_path.exists():
            with requested_path.open("r", encoding="utf-8") as f:
                data = json.load(f) or {}
        elif config_path is None and fallback_yaml_path.exists() and yaml is not None:
            logger.warning(
                "hardware_config_default_json_missing_yaml_fallback path=%s fallback=%s",
                requested_path,
                fallback_yaml_path,
            )
            with fallback_yaml_path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        elif config_path is None:
            raise FileNotFoundError("No hardware archetype config found.")
        else:
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
