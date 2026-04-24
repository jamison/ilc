from pathlib import Path
import json
import unittest


ROOT = Path("/Users/jamstar/Documents/ILC_Main/01_Current")


class TestWindowBScopeB1B4HoldPoint(unittest.TestCase):
    def test_required_artifacts_exist(self) -> None:
        required = [
            ROOT / "docs/specs/ilc_phase_b1_b5_sequence_lock_v0.1.md",
            ROOT / "docs/phases/phase_b1_row5_b_scope_sequence_lock.md",
            ROOT / "docs/phases/phase_b2_row5_mechanism_family_analysis.md",
            ROOT / "docs/research/program_row5_privacy.md",
            ROOT / "tools/testbed/sim_leakage_autoresearch.py",
            ROOT / "tools/testbed/sim_leakage_02_runner.py",
            ROOT / "tests/test_sim_leakage_02_autoresearch.py",
            ROOT / "docs/research/ilc_sim_leakage_02_autoresearch_results_b3_v0.1.md",
            ROOT / "docs/phases/phase_b3_row5_sim_leakage_02.md",
            ROOT / "docs/specs/ilc_row5_mechanism_selection_recommendation_b4_v0.1.md",
            ROOT / "docs/phases/phase_b4_row5_mechanism_selection_recommendation.md",
            ROOT / "tools/testbed/sim_leakage_02_autoresearch_results.jsonl",
            ROOT / "tools/testbed/sim_leakage_02_pareto_frontier.json",
        ]
        for path in required:
            self.assertTrue(path.exists(), path)

    def test_hold_point_tokens_and_phrase_are_present(self) -> None:
        evidence = (ROOT / "docs/research/ilc_sim_leakage_02_autoresearch_results_b3_v0.1.md").read_text()
        recommendation = (ROOT / "docs/specs/ilc_row5_mechanism_selection_recommendation_b4_v0.1.md").read_text()
        self.assertIn("row5_sim_leakage_02_autoresearch_complete", evidence)
        self.assertIn("row5_mechanism_selection_human_gate_pending", recommendation)
        self.assertIn("simulation-derived bar recommendation", evidence)
        self.assertIn("simulation-derived bar recommendation", recommendation)

    def test_results_log_has_full_run(self) -> None:
        lines = [
            json.loads(line)
            for line in (ROOT / "tools/testbed/sim_leakage_02_autoresearch_results.jsonl").read_text().splitlines()
            if line.strip()
        ]
        self.assertEqual(lines[0]["entry_type"], "run_metadata")
        iterations = [line for line in lines[1:] if "iteration" in line]
        self.assertEqual(len(iterations), 120)

    def test_historical_b4_artifacts_remain_present(self) -> None:
        recommendation = (ROOT / "docs/specs/ilc_row5_mechanism_selection_recommendation_b4_v0.1.md").read_text()
        self.assertIn("row5_mechanism_selection_human_gate_pending", recommendation)
        self.assertIn("Mixing layer", recommendation)


if __name__ == "__main__":
    unittest.main()
