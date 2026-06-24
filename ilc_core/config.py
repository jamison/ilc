# SPDX-License-Identifier: AGPL-3.0-only
import logging
from pathlib import Path
from typing import TypeAlias, cast

try:
    import yaml
except ImportError:
    yaml = None

import json
from ilc_core.exceptions import ConfigNotFoundError

logger = logging.getLogger(__name__)

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | dict[str, "JsonValue"] | list["JsonValue"]
GovernanceConfig: TypeAlias = dict[str, JsonValue]


def _coerce_governance_config(value: object) -> GovernanceConfig:
    if isinstance(value, dict):
        return cast(GovernanceConfig, value)
    return {}


def _default_governance_config_path() -> Path:
    root = Path(__file__).resolve().parents[1]
    return root / "config" / "governance_mvp.json"


def load_governance_config(path: str | None = None) -> GovernanceConfig:
    """
    Load Governance config from YAML/JSON.

    If path is None, default to config/governance_mvp.json relative to project root.
    """
    user_supplied = path is not None
    if path is None:
        path_obj = _default_governance_config_path()
    else:
        path_obj = Path(path)

    if not path_obj.exists():
        if user_supplied:
            logger.error("governance_config_path_not_found path=%s", path_obj)
            raise ConfigNotFoundError(str(path_obj), message=f"config_not_found:{path_obj}")
        logger.warning(
            "governance_config_default_missing path=%s fallback=empty_config",
            path_obj,
        )
        return {}

    if path_obj.suffix in {".yaml", ".yml"}:
        if yaml:
            with path_obj.open("r", encoding="utf-8") as f:
                return _coerce_governance_config(yaml.safe_load(f) or {})
        else:
            fallback_json_path = path_obj.with_suffix(".json")
            if fallback_json_path.exists():
                logger.warning(
                    "governance_config_yaml_loader_missing_json_fallback path=%s fallback=%s",
                    path_obj,
                    fallback_json_path,
                )
                with fallback_json_path.open("r", encoding="utf-8") as f:
                    return _coerce_governance_config(json.load(f) or {})
            logger.warning(
                "governance_config_yaml_loader_missing path=%s fallback=empty_config",
                path_obj,
            )
            return {}
            
    elif path_obj.suffix == ".json":
        with path_obj.open("r", encoding="utf-8") as f:
            return _coerce_governance_config(json.load(f) or {})
    else:
        logger.warning(
            "governance_config_unsupported_extension path=%s suffix=%s user_supplied=%s fallback=empty_config",
            path_obj,
            path_obj.suffix,
            user_supplied,
        )
        return {}
