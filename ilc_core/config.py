import logging
from pathlib import Path
from typing import TypeAlias, cast

try:
    import yaml
except ImportError:
    yaml = None

import json

logger = logging.getLogger(__name__)

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | dict[str, "JsonValue"] | list["JsonValue"]
GovernanceConfig: TypeAlias = dict[str, JsonValue]


def _coerce_governance_config(value: object) -> GovernanceConfig:
    if isinstance(value, dict):
        return cast(GovernanceConfig, value)
    return {}


def load_governance_config(path: str | None = None) -> GovernanceConfig:
    """
    Load Governance config from YAML/JSON.

    If path is None, default to config/governance_mvp.yaml relative to project root.
    """
    user_supplied = path is not None
    if path is None:
        root = Path(__file__).resolve().parents[1]
        # Default to YAML if available, else JSON
        if yaml:
            path = root / "config" / "governance_mvp.yaml"
        else:
            path = root / "config" / "governance_mvp.json"
    else:
        path = Path(path)

    if not path.exists():
        if user_supplied:
            logger.error("Config path not found: %s", path)
            raise FileNotFoundError(f"config_not_found:{path}")
        return {}

    if path.suffix in {".yaml", ".yml"}:
        if yaml:
            with path.open("r", encoding="utf-8") as f:
                return _coerce_governance_config(yaml.safe_load(f) or {})
        else:
            logger.warning("PyYAML not installed. Cannot load %s.", path)
            return {}
            
    elif path.suffix == ".json":
        with path.open("r", encoding="utf-8") as f:
            return _coerce_governance_config(json.load(f) or {})
    else:
        if user_supplied:
            logger.warning("Unsupported config extension for path: %s", path)
        return {}
