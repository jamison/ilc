import unittest
import os
import re
from pathlib import Path

RESULTS_DOC_PATH = "docs/research/ilc_mysticeti_workload_b_results_M014_v0.1.md"

class TestM014WorkloadBResults(unittest.TestCase):
    def setUp(self):
        self.doc_path = Path(RESULTS_DOC_PATH)

    def test_01_results_doc_exists(self):
        self.assertTrue(self.doc_path.exists(), f"Missing results doc at {RESULTS_DOC_PATH}")

    def test_02_literal_censor_log_line_present(self):
        content = self.doc_path.read_text()
        self.assertIn("[m014_censor] validator_id=2 dropped EpochSettlementTx from validator_id=5", content, "Missing literal censorship log evidence")

    def test_03_commit_log_line_present(self):
        content = self.doc_path.read_text()
        self.assertIn("epoch_record_committed:epoch=1", content, "Missing literal epoch commit commitment from non-censored validators")

    def test_04_deviation_acknowledged(self):
        content = self.doc_path.read_text()
        self.assertIn("f=1", content, "Must clearly mention the test was f=1")
        self.assertIn("deviation", content.lower(), "Must explicitly declare f=1 was a deviation from Phase 690 f=2 spec")

    def test_05_explicit_verdict_token_present(self):
        content = self.doc_path.read_text()
        verdict_found = "PASS" in content or "FAIL" in content
        self.assertTrue(verdict_found, "Must contain an explicit PASS or FAIL verdict token")

    def test_06_tla_plus_liveness_reference_present(self):
        content = self.doc_path.read_text()
        self.assertIn("TLA+", content, "Missing TLA+ reference")
        self.assertIn("Liveness", content, "Missing Spec A Liveness connection string")

    def test_07_finality_within_5_claim_present(self):
        content = self.doc_path.read_text()
        self.assertTrue(
            "≤5" in content or "within 5" in content.lower(),
            "Finality timeline delta <= 5 not explicitly demonstrated"
        )

if __name__ == '__main__':
    unittest.main()
