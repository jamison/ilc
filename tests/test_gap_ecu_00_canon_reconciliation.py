from pathlib import Path


SPEC = Path(
    "docs/specs/ilc_ecu_backward_attribution_canon_reconciliation_GAP_ECU_00_v0.1.md"
)
WALKTHROUGH = Path("docs/phases/phase_gap_ecu_00_ecu_canon_reconciliation_walkthrough.md")
STATUS = Path("docs/phases/STATUS.md")


def test_gap_ecu_00_spec_contains_patent_and_gate_boundaries():
    text = SPEC.read_text(encoding="utf-8")
    assert "64/231,846" in text
    assert "official_written_filing_receipts_received = False" in text
    assert "public_path_remains_blocked = True" in text
    assert "public disclosure gate remains in force" in text
    assert "does not authorize public disclosure" in text


def test_gap_ecu_00_spec_lists_exact_nine_backward_attribution_surfaces():
    text = SPEC.read_text(encoding="utf-8")
    expected = [
        "Triggering events",
        "Eligible upstream artifacts",
        "Typed path semantics",
        "Provenance-distance score",
        "Decay rule",
        "Bidirectional coefficients",
        "Depth and dominance bounds",
        "Refutation interaction",
        "Audit surface",
    ]
    for item in expected:
        assert item in text
    section = text.split("## 4. Nine Open Backward-Attribution CDL Parameter Surfaces", 1)[1]
    section = section.split("## 5. Public Claim Audit", 1)[0]
    assert section.count("| ") >= 10
    assert "The count from Phase 1492p section 3.1 is exactly nine." in section


def test_gap_ecu_00_spec_preserves_live_vs_unimplemented_boundary():
    text = SPEC.read_text(encoding="utf-8")
    assert "Current live `ProtocolECU` settlement supports REUSE" in text
    assert "Full backward attribution" in text
    assert "Not implemented" in text or "not implemented" in text
    assert "No CDL opened yet" in text
    assert "GAP-ECU-06" in text


def test_gap_ecu_00_node_value_kernel_is_not_settlement_formula():
    text = SPEC.read_text(encoding="utf-8")
    assert "`node_value_kernel.py` is not the ECU settlement formula." in text
    assert "not imported by `epoch_attribution_settle_runtime.py`" in text
    assert "ilc_core/analysis/node_value_kernel.py" in text


def test_gap_ecu_00_cdl083_cdl084_no_double_pay_constraint_recorded():
    text = SPEC.read_text(encoding="utf-8")
    assert "CDL-083 REFUTATION remains valid" in text
    assert "CDL-084 PROVENANCE remains valid" in text
    assert "no-double-pay requirement" in text
    assert "PROVENANCE_DECAY_ALPHA = Decimal(\"0.45\")" in text
    assert "PROVENANCE_MAX_DEPTH = 3" in text


def test_gap_ecu_00_status_and_walkthrough_tokens():
    status = STATUS.read_text(encoding="utf-8")
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")
    token = "ecu_canon_reconciliation_committed_GAP_ECU_00"
    assert token in status
    assert token in walkthrough
    assert "No runtime code" in status
    assert "This phase did not open a CDL" in walkthrough
