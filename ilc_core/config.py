import os
from pathlib import Path
from typing import Any, Dict

try:
    import yaml
except ImportError:
    yaml = None

import json


def load_governance_config(path: str | None = None) -> Dict[str, Any]:
    """
    Load Governance config from YAML/JSON.

    If path is None, default to config/governance_mvp.yaml relative to project root.
    """
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
        return {}

    if path.suffix in {".yaml", ".yml"}:
        if yaml:
            with path.open("r") as f:
                return yaml.safe_load(f) or {}
        else:
            # Fallback: if user has no yaml, warn or return empty?
            # For MVP, let's just print a warning and return empty, 
            # or try to parse simple YAML as JSON if it happens to be compatible (unlikely).
            print(f"[Config] Warning: PyYAML not installed. Cannot load {path}.")
            return {}
            
    elif path.suffix == ".json":
        with path.open("r") as f:
            return json.load(f) or {}
    else:
        return {}
