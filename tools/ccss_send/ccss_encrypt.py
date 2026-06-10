#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""CCSS-003 envelope encryption — thin shim over ilc_core.ccss.runtime.

The canonical implementation lives in ilc_core/ccss/runtime.py.
This module re-exports the public surface so tools/ccss_send/ callers
continue to work without changes.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure ilc_core is importable when running from the tools/ directory
_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from ilc_core.ccss.runtime import (  # noqa: E402
    CCSSRuntimeError as CCSSEncryptError,
    seal_message,
)

__all__ = [
    "CCSSEncryptError",
    "seal_message",
]
