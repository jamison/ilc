"""Phase 1130 — Window 1130-1138 sequence lock tests."""

from __future__ import annotations

import pathlib

from ilc_core.economics.epoch_attribution_settle_runtime import (
    EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1130_1138_sequence_lock_v0.1.md"


def _read() -> str:
    return SEQUENCE_LOCK.read_text(encoding="utf-8")


def test_s1_sequence_lock_exists_with_window_token() -> None:
    assert SEQUENCE_LOCK.exists()
    assert "window_1130_1138_sequence_lock_committed_phase_1130" in _read()


def test_s2_sequence_lock_contains_no_cdl_mutation_token() -> None:
    assert "no_cdl_mutation_this_window" in _read()


def test_s3_sequence_lock_contains_sensitive_closure_token() -> None:
    assert "window_1130_1138_closure_gate_phase_1138_sensitive" in _read()


def test_s4_sequence_lock_lists_all_nine_phases() -> None:
    src = _read()
    for phase in range(1130, 1139):
        assert f"| {phase} |" in src


def test_s5_runtime_version_matches_post_fix1_baseline() -> None:
    assert EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION == (
        "epoch_attribution_settle_runtime_1129_fix1.v0.5"
    )
