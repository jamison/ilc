"""Phase 1128 — coherence report and capsule v5.37 tests."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from ilc_core.types import PROVENANCE_DECAY_ALPHA


CAPSULE = Path("docs/specs/ilc_antigravity_context_capsule_v5.37.md")
COHERENCE = Path("docs/specs/ilc_integration_coherence_report_1128_v0.1.md")


def test_h1_capsule_v5_37_exists_with_supersession_token() -> None:
    assert CAPSULE.exists()
    assert "capsule_v5_37_supersedes_v5_36" in CAPSULE.read_text(encoding="utf-8")


def test_h2_capsule_records_alpha_locked_phase_1126() -> None:
    text = CAPSULE.read_text(encoding="utf-8")
    assert "cdl_084_q2_alpha_locked_decimal_0_45_phase_1126" in text


def test_h3_capsule_records_new_q2_token() -> None:
    text = CAPSULE.read_text(encoding="utf-8")
    assert "q2_geometric_decay_alpha_decimal_0_45_locked" in text


def test_h4_provenance_decay_alpha_locked_decimal_0_45() -> None:
    assert isinstance(PROVENANCE_DECAY_ALPHA, Decimal)
    assert PROVENANCE_DECAY_ALPHA == Decimal("0.45")


def test_h5_coherence_report_exists_with_pass_verdict() -> None:
    assert COHERENCE.exists()
    assert "coherence_report_1128_verdict=pass" in COHERENCE.read_text(encoding="utf-8")


def test_h6_coherence_references_prelock_doc_and_new_q2_token() -> None:
    text = COHERENCE.read_text(encoding="utf-8")
    assert "ilc_cdl_084_q2_amendment_prelock_1125" in text
    assert "q2_geometric_decay_alpha_decimal_0_45_locked" in text
