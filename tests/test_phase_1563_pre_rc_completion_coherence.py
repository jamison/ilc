"""Phase 1563 pre-RC completion coherence and capsule tests.

PUBLIC_RC_EXCLUDE: phase_1563_private_coherence_selftest
PUBLIC_RC_EXCLUDE_REASON: Private pre-RC coherence validation. Does not authorize public RC or runtime activation.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/specs/ilc_window_1556_1564_coherence_report_1563_v0.1.md"
CAPSULE = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.70_pre_block6.md"
STATUS = ROOT / "docs/phases/STATUS.md"


def test_coherence_report_exists() -> None:
    assert REPORT.exists()


def test_capsule_exists_with_correct_version() -> None:
    assert CAPSULE.exists()
    assert "v5.70" in CAPSULE.read_text(encoding="utf-8")


def test_phase_1556_through_1562_tokens_present_in_status() -> None:
    status = STATUS.read_text(encoding="utf-8")
    for token in (
        "pre_rc_completion_sequence_lock_committed_phase_1556",
        "hb_001_genesis_authority_assertion_builder_wired_phase_1557",
        "hb_003_layer_0_bundle_truth_primitive_schema_embedded_phase_1558",
        "hb_002_minimal_serving_receipt_implemented_phase_1559",
        "agent_init_ceremony_live_executed_phase_1560",
        "ecu_live_smoke_test_executed_phase_1561",
        "production_emission_not_activated_confirmed_phase_1561",
        "invitation_provenance_chain_runtime_implemented_phase_1562",
    ):
        assert token in status


def test_open_obligations_noted_with_correct_state() -> None:
    report = REPORT.read_text(encoding="utf-8")
    assert "OBL-002" in report
    assert re.search(r"OBL-002[\s\S]{0,240}permanent", report, re.IGNORECASE)
    assert "OBL-030" in report
    assert re.search(r"OBL-030[\s\S]{0,240}open", report, re.IGNORECASE)


def test_no_premature_public_rc_claim() -> None:
    combined = REPORT.read_text(encoding="utf-8") + CAPSULE.read_text(encoding="utf-8")
    forbidden_patterns = (
        r"public_rc_authorized",
        r"guard_cleared",
        r"NOT_ACTIVATED.*False",
    )
    for pattern in forbidden_patterns:
        assert re.search(pattern, combined) is None


def test_capsule_notes_plain_integer_numbering() -> None:
    capsule = CAPSULE.read_text(encoding="utf-8").lower()
    assert "plain integer" in capsule or "plain-integer" in capsule


def test_phase_1562_node6_boundary_carried_forward() -> None:
    report = REPORT.read_text(encoding="utf-8")
    capsule = CAPSULE.read_text(encoding="utf-8")

    assert "node6 receiver-only boundary" in report
    assert "node6 receiver-only" in capsule
    assert "fabricating an `invitee_agent_id`" in report
