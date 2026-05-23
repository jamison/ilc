# SPDX-License-Identifier: AGPL-3.0-or-later
import json
import logging
from importlib import resources
from typing import Dict, TypeAlias

ReplayProofSchemaMap: TypeAlias = Dict[str, object]

logger = logging.getLogger(__name__)


def load_replay_proof_schema(schema_filename: str) -> ReplayProofSchemaMap:
    """
    Load a replay-proof schema from packaged protocol schema resources.

    Returns an empty mapping when the resource cannot be loaded or parsed.
    Callers are expected to fail closed when schema loading fails.
    """
    try:
        schema_text = (
            resources.files("ilc_core.protocol.schemas")
            .joinpath(schema_filename)
            .read_text(encoding="utf-8")
        )
        parsed = json.loads(schema_text)
        if isinstance(parsed, dict):
            return parsed
        logger.debug(
            "replay_proof_schema_not_object: %s (%s)",
            schema_filename,
            type(parsed).__name__,
        )
        return {}
    except (
        FileNotFoundError,
        ModuleNotFoundError,
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        TypeError,
    ) as exc:
        logger.debug(
            "replay_proof_schema_load_failed: %s (%s)",
            schema_filename,
            exc,
            exc_info=True,
        )
        return {}
