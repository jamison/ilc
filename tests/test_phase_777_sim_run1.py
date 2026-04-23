from __future__ import annotations

from pathlib import Path
import unittest


ARTIFACT = Path("docs/research/ilc_sim_leakage_01_run1_post_layer1_results_777_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestPhase777SimRun1(unittest.TestCase):
    def test_artifact_exists_with_required_sections(self) -> None:
        text = _read(ARTIFACT)
        for heading in (
            "## 1. Run configuration",
            "## 2. Variant A recall (post-Layer-1)",
            "## 3. Variant B recall (post-Layer-1)",
            "## 4. Variant C recall (post-Layer-1)",
            "## 5. Layer-1 contribution assessment",
            "## 6. Residual gap for Layer-2",
        ):
            self.assertIn(heading, text)

    def test_completion_token_present(self) -> None:
        text = _read(ARTIFACT)
        self.assertIn("sim_leakage_01_run1_post_layer1_complete", text)

    def test_all_three_variant_recall_values_are_recorded(self) -> None:
        text = _read(ARTIFACT)
        for marker in (
            "variant_a_post_layer1_recall=1.0",
            "variant_b_post_layer1_recall_observed=0.0",
            "variant_b_post_layer1_recall_structural=1.0",
            "variant_c_post_layer1_recall_structural=1.0",
        ):
            self.assertIn(marker, text)

    def test_variant_a_feature_set_is_explicit(self) -> None:
        text = _read(ARTIFACT)
        for marker in (
            "node-local validator vantage",
            "event order",
            "`object_ref.version`",
            "constant token `[redacted:agent_id]`",
        ):
            self.assertIn(marker, text)

    def test_variant_a_records_constant_redaction_mode(self) -> None:
        text = _read(ARTIFACT)
        self.assertIn("variant_a_post_layer1_mode=constant_redaction_token", text)
        self.assertIn("plaintext AgentID bytes no longer survive", text)

    def test_variant_b_and_c_are_explicitly_unchanged_by_layer1(self) -> None:
        text = _read(ARTIFACT)
        self.assertIn("Layer-1 does not touch the gRPC balance surface", text)
        self.assertIn("Layer-1 does not touch the epoch-lineage surface either", text)
        self.assertIn("FAIL (structural)", text)


if __name__ == "__main__":
    unittest.main()
