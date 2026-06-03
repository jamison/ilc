# SPDX-License-Identifier: AGPL-3.0-only
import json
import os
from typing import Any, Dict

from ilc_core.exceptions import ProtocolSchemaLoadError

def load_protocol_schema(
    path: str = None,
) -> Dict[str, Any]:
    """
    Load the MVP protocol schema (claims, tasks, outcomes, epochs).

    This is intentionally light-weight: it gives other components a
    dictionary describing required protocol objects and fields.

    For now it's only used in tests and documentation examples.
    """
    if path is None:
        # Assuming this file is in ilc_core/protocol/schema.py
        # We need to go up 3 levels: ilc_core/protocol -> ilc_core -> root -> root/protocol
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        path = os.path.join(base_dir, "protocol", "ilc_protocol_mvp.json")

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as exc:
        raise ProtocolSchemaLoadError(f"protocol_schema_not_found:{path}") from exc
    except json.JSONDecodeError as exc:
        raise ProtocolSchemaLoadError(f"protocol_schema_invalid_json:{path}") from exc
