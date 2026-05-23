# SPDX-License-Identifier: AGPL-3.0-or-later
import logging
import os
from typing import Optional

DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
DEFAULT_LOG_LEVEL = "INFO"


def _resolve_log_level(level: Optional[str | int]) -> int:
    if isinstance(level, int):
        return level
    if isinstance(level, str):
        resolved = getattr(logging, level.upper(), None)
        return resolved if isinstance(resolved, int) else logging.INFO
    env_level = os.getenv("ILC_LOG_LEVEL", DEFAULT_LOG_LEVEL)
    resolved = getattr(logging, env_level.upper(), None)
    return resolved if isinstance(resolved, int) else logging.INFO


def configure_logging(level: Optional[str | int] = None) -> None:
    """
    Idempotent logging bootstrap for ILC runtime surfaces.

    - Sets root level from argument or env fallback.
    - Adds a stream handler only when root has no handlers.
    - Safe to call repeatedly without duplicating handlers.
    """
    root = logging.getLogger()
    root.setLevel(_resolve_log_level(level))

    if root.handlers:
        return

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
    root.addHandler(handler)
