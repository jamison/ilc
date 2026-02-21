"""
Phase 251 — Security CDL Ratification Tests

Verifies:
- ratification evidence document exists
- per-CDL evidence tables present for CDL-001, CDL-002, CDL-007
- CDL-001/002/007 status is ratified in decision log
- each ratified CDL has ratified_phase and evidence_document fields
- CDL-019 remains open
- CDL-025 through CDL-031 unchanged (open)
- CDL-032 unchanged (open)
- CDL-033 unchanged (open)
- no ratification language for unrelated CDLs
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
EVIDENCE_DOC = REPO_ROOT / "docs/specs/ilc_security_cdl_ratification_evidence_251_v0.1.md"
CDL_LOG = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"


class TestEvidenceDocumentExists:
    def test_ratification_evidence_doc_exists(self):
        assert EVIDENCE_DOC.exists(), f"Ratification evidence document not found: {EVIDENCE_DOC}"


class TestPerCDLEvidenceTables:
    def setup_method(self):
        self.text = EVIDENCE_DOC.read_text()

    def test_cdl_001_evidence_table_present(self):
        assert "CDL-001" in self.text, "CDL-001 section missing from evidence doc"
        assert "ilc_cdl_001_signer_lineage_trust_root_contract_v0.1.md" in self.text

    def test_cdl_002_evidence_table_present(self):
        assert "CDL-002" in self.text, "CDL-002 section missing from evidence doc"
        assert "ilc_cdl_002_key_compromise_response_contract_v0.1.md" in self.text

    def test_cdl_007_evidence_table_present(self):
        assert "CDL-007" in self.text, "CDL-007 section missing from evidence doc"
        assert "ilc_cdl_007_rollback_resistance_baseline_contract_v0.1.md" in self.text

    def test_evidence_doc_includes_phase_244_gate_reference(self):
        assert "run_phase_244_security_runtime_gate.py" in self.text

    def test_evidence_doc_includes_cross_cdl_test_reference(self):
        assert "test_security_runtime_cross_cdl_interactions_244.py" in self.text

    def test_evidence_doc_includes_phase_248_coherence_reference(self):
        assert "ilc_integration_coherence_report_248_v0.1.md" in self.text

    def test_evidence_doc_includes_boundary_statement(self):
        assert "No runtime implementation was introduced" in self.text


class TestCDLStatusRatified:
    def setup_method(self):
        self.text = CDL_LOG.read_text()

    def test_cdl_001_status_is_ratified(self):
        # Find the CDL-001 row and confirm ratified
        lines = self.text.splitlines()
        cdl_001_line = next((l for l in lines if l.startswith("| CDL-001 ")), None)
        assert cdl_001_line is not None, "CDL-001 row not found"
        assert "ratified" in cdl_001_line, f"CDL-001 not ratified; row: {cdl_001_line}"

    def test_cdl_002_status_is_ratified(self):
        lines = self.text.splitlines()
        cdl_002_line = next((l for l in lines if l.startswith("| CDL-002 ")), None)
        assert cdl_002_line is not None, "CDL-002 row not found"
        assert "ratified" in cdl_002_line, f"CDL-002 not ratified; row: {cdl_002_line}"

    def test_cdl_007_status_is_ratified(self):
        lines = self.text.splitlines()
        cdl_007_line = next((l for l in lines if l.startswith("| CDL-007 ")), None)
        assert cdl_007_line is not None, "CDL-007 row not found"
        assert "ratified" in cdl_007_line, f"CDL-007 not ratified; row: {cdl_007_line}"

    def test_cdl_001_has_ratified_phase(self):
        lines = self.text.splitlines()
        cdl_001_line = next((l for l in lines if l.startswith("| CDL-001 ")), None)
        assert "ratified_phase: 251" in cdl_001_line

    def test_cdl_002_has_ratified_phase(self):
        lines = self.text.splitlines()
        cdl_002_line = next((l for l in lines if l.startswith("| CDL-002 ")), None)
        assert "ratified_phase: 251" in cdl_002_line

    def test_cdl_007_has_ratified_phase(self):
        lines = self.text.splitlines()
        cdl_007_line = next((l for l in lines if l.startswith("| CDL-007 ")), None)
        assert "ratified_phase: 251" in cdl_007_line

    def test_cdl_001_has_evidence_document(self):
        lines = self.text.splitlines()
        cdl_001_line = next((l for l in lines if l.startswith("| CDL-001 ")), None)
        assert "evidence_document" in cdl_001_line
        assert "ilc_security_cdl_ratification_evidence_251_v0.1.md" in cdl_001_line

    def test_cdl_002_has_evidence_document(self):
        lines = self.text.splitlines()
        cdl_002_line = next((l for l in lines if l.startswith("| CDL-002 ")), None)
        assert "evidence_document" in cdl_002_line
        assert "ilc_security_cdl_ratification_evidence_251_v0.1.md" in cdl_002_line

    def test_cdl_007_has_evidence_document(self):
        lines = self.text.splitlines()
        cdl_007_line = next((l for l in lines if l.startswith("| CDL-007 ")), None)
        assert "evidence_document" in cdl_007_line
        assert "ilc_security_cdl_ratification_evidence_251_v0.1.md" in cdl_007_line


class TestUnchangedCDLs:
    def setup_method(self):
        self.text = CDL_LOG.read_text()
        self.lines = self.text.splitlines()

    def _get_row(self, cdl_id: str) -> str:
        row = next((l for l in self.lines if l.startswith(f"| {cdl_id} ")), None)
        assert row is not None, f"{cdl_id} row not found in decision log"
        return row

    def test_cdl_019_remains_open(self):
        row = self._get_row("CDL-019")
        assert "| open |" in row or "open" in row.split("|")[3].strip(), \
            f"CDL-019 should be open; row: {row}"

    def test_cdl_025_remains_open(self):
        row = self._get_row("CDL-025")
        assert "open" in row

    def test_cdl_026_remains_open(self):
        row = self._get_row("CDL-026")
        assert "open" in row

    def test_cdl_027_remains_open(self):
        row = self._get_row("CDL-027")
        assert "open" in row

    def test_cdl_028_remains_open(self):
        row = self._get_row("CDL-028")
        assert "open" in row

    def test_cdl_029_remains_open(self):
        row = self._get_row("CDL-029")
        assert "open" in row

    def test_cdl_030_remains_open(self):
        row = self._get_row("CDL-030")
        assert "open" in row

    def test_cdl_031_remains_open(self):
        row = self._get_row("CDL-031")
        assert "open" in row

    def test_cdl_032_remains_open(self):
        row = self._get_row("CDL-032")
        assert "open" in row

    def test_cdl_033_remains_open(self):
        row = self._get_row("CDL-033")
        assert "open" in row


class TestNoSpuriousRatification:
    def setup_method(self):
        self.text = CDL_LOG.read_text()
        self.lines = self.text.splitlines()

    def test_no_ratification_language_for_cdl_019(self):
        row = next((l for l in self.lines if l.startswith("| CDL-019 ")), None)
        assert row is not None
        assert "ratified_phase: 251" not in row

    def test_no_ratification_language_for_cdl_025_031(self):
        for cdl_id in ["CDL-025", "CDL-026", "CDL-027", "CDL-028", "CDL-029", "CDL-030", "CDL-031"]:
            row = next((l for l in self.lines if l.startswith(f"| {cdl_id} ")), None)
            assert row is not None, f"{cdl_id} row not found"
            assert "ratified_phase: 251" not in row, f"{cdl_id} should not have ratified_phase from 251"

    def test_no_ratification_language_for_cdl_032(self):
        row = next((l for l in self.lines if l.startswith("| CDL-032 ")), None)
        assert row is not None
        assert "ratified_phase: 251" not in row

    def test_no_ratification_language_for_cdl_033(self):
        row = next((l for l in self.lines if l.startswith("| CDL-033 ")), None)
        assert row is not None
        assert "ratified_phase: 251" not in row
