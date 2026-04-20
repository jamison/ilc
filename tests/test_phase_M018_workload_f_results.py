import os
import json
import unittest

class TestPhaseM018WorkloadF(unittest.TestCase):
    def setUp(self):
        self.doc_path = "docs/research/ilc_mysticeti_workload_f_results_M018_v0.1.md"
        self.report_path = "docs/research/ilc_m018_auditability_report.json"
        self.runner_script = "tools/testbed/ilc_loopback_m018_runner.sh"
        self.doc_content = ""
        if os.path.exists(self.doc_path):
            with open(self.doc_path, "r") as f:
                self.doc_content = f.read()
        self.report = {}
        if os.path.exists(self.report_path):
            with open(self.report_path, "r") as f:
                self.report = json.load(f)
        self.runner_content = ""
        if os.path.exists(self.runner_script):
            with open(self.runner_script, "r") as f:
                self.runner_content = f.read()

    def test_results_doc_exists(self):
        self.assertTrue(os.path.exists(self.doc_path))

    def test_results_doc_verdict_pass(self):
        self.assertIn("run_m018_workload_f_verdict=pass", self.doc_content)

    def test_auditability_report_exists_and_parseable(self):
        self.assertTrue(os.path.exists(self.report_path))
        self.assertIsInstance(self.report, dict)

    def test_report_sec_009_implemented(self):
        self.assertTrue(self.report.get("sec_009", {}).get("bls_verification_implemented", False))

    def test_report_forged_rejected(self):
        self.assertTrue(self.report.get("sec_009", {}).get("forged_epoch_rejected", False))

    def test_report_agg_sig_stored(self):
        self.assertTrue(self.report.get("sec_009", {}).get("agg_sig_stored_in_lmdb", False))

    def test_report_recovery_path_verified(self):
        self.assertTrue(self.report.get("sec_009", {}).get("recovery_path_verified", False))

    def test_report_grpc_activated(self):
        self.assertTrue(self.report.get("grpc", {}).get("server_activated", False))

    def test_report_chain_complete(self):
        self.assertTrue(self.report.get("grpc", {}).get("chain_complete", False))

    def test_report_epochs_returned(self):
        self.assertEqual(self.report.get("grpc", {}).get("epochs_returned", 0), 20)

    def test_report_agg_sig_in_grpc_response(self):
        self.assertTrue(self.report.get("grpc", {}).get("agg_sig_bytes_in_response", False))

    def test_report_row7_closed(self):
        self.assertTrue(self.report.get("row_7", {}).get("accessibility_component_closed", False))

    def test_report_adr_0031_edge_record(self):
        self.assertTrue(self.report.get("adr_0031", {}).get("edge_record_in_proto", False))

    def test_report_adr_0031_include_edges_field(self):
        self.assertTrue(self.report.get("adr_0031", {}).get("include_edges_field_in_get_epoch_chain_request", False))

    def test_runner_emits_verdict_token(self):
        self.assertIn("run_m018_workload_f_verdict=pass", self.runner_content)

    def test_overall_verdict_field(self):
        self.assertEqual(self.report.get("overall_verdict", ""), "workload_f_auditability_pass")

if __name__ == '__main__':
    unittest.main()
