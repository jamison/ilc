# SPDX-License-Identifier: AGPL-3.0-or-later
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


def _load_json_config(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f) or {}


def _try_load_yaml_config(path: Path) -> Dict[str, Any] | None:
    if yaml is None or not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


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

    data: Dict[str, Any]
    if requested_path.suffix in {".yaml", ".yml"}:
        yaml_data = _try_load_yaml_config(requested_path)
        if yaml_data is not None:
            data = yaml_data
        else:
            fallback_json_path = requested_path.with_suffix(".json")
            if fallback_json_path.exists():
                logger.warning(
                    "hardware_config_yaml_loader_missing_json_fallback path=%s fallback=%s",
                    requested_path,
                    fallback_json_path,
                )
                data = _load_json_config(fallback_json_path)
            elif config_path is None and default_json_path.exists():
                data = _load_json_config(default_json_path)
            else:
                return {}
    elif requested_path.exists():
        data = _load_json_config(requested_path)
    elif config_path is None:
        yaml_data = _try_load_yaml_config(fallback_yaml_path)
        if yaml_data is None:
            raise FileNotFoundError("No hardware archetype config found.")
        logger.warning(
            "hardware_config_default_json_missing_yaml_fallback path=%s fallback=%s",
            requested_path,
            fallback_yaml_path,
        )
        data = yaml_data
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
