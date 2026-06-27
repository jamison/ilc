"""Compatibility entry point for the Phase 1568 prompt verification command."""

from __future__ import annotations

import importlib.util
from pathlib import Path


_SOURCE = Path(__file__).with_name("test_phase_1568_block6_rehearsal_evidence.py")
_SPEC = importlib.util.spec_from_file_location("_phase_1568_rehearsal_evidence", _SOURCE)
assert _SPEC is not None
assert _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

for _name in dir(_MODULE):
    if _name.startswith("test_"):
        globals()[_name] = getattr(_MODULE, _name)
