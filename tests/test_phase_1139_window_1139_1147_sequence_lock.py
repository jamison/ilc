"""Phase 1139 - Window 1139-1147 sequence lock tests."""

from __future__ import annotations

import pathlib

from ilc_core.economics.epoch_attribution_settle_runtime import (
    EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1139_1147_sequence_lock_v0.1.md"
GUIDANCE = ROOT / "docs/specs/ilc_window_1139_1147_candidate_phase_grouping_v0.1.md"


def _read_lock() -> str:
    return SEQUENCE_LOCK.read_text(encoding="utf-8")


def test_s1_sequence_lock_exists_with_window_token() -> None:
    assert SEQUENCE_LOCK.exists()
    assert "window_1139_1147_sequence_lock_committed_phase_1139" in _read_lock()


def test_s2_sequence_lock_lists_all_scheduled_phases_and_subphase() -> None:
    src = _read_lock()
    for phase in ("1139", "1140", "1141", "1142", "1142s", "1143", "1144", "1145", "1146", "1147"):
        assert f"| {phase} |" in src


def test_s3_sequence_lock_asserts_no_cdl_or_runtime_mutation() -> None:
    src = _read_lock()
    assert "no_cdl_mutation_this_window" in src
    assert "ilc_core_read_only_this_window" in src
    assert "`ilc_core/` runtime mutation" in src


def test_s4_sensitive_phases_require_human_go_tokens() -> None:
    src = _read_lock()
    assert "genesis_signing_requires_human_go_phase_1142s" in src
    assert "Phase 1142s is SENSITIVE and requires a separate explicit human GO token" in src
    assert "Phase 1147 is SENSITIVE and requires an explicit human GO token" in src


def test_s5_guidance_doc_exists_and_matches_authority_traceability_gate() -> None:
    assert GUIDANCE.exists()
    src = GUIDANCE.read_text(encoding="utf-8")
    assert "authority_traceable_core_nodes ≥ 28/32" in src
    assert "1142s" in src


def test_s6_runtime_version_matches_window_baseline() -> None:
    assert EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION == (
        "epoch_attribution_settle_runtime_1129_fix1.v0.5"
    )


def test_s7_sequence_lock_uses_corrected_run02_baseline_framing() -> None:
    src = _read_lock()
    assert "combinatorial λ₂" in src
    assert "normalized λ₂" in src
    assert "not directly comparable" in src
