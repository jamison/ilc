from __future__ import annotations

from pathlib import Path
import unittest


ARTIFACT = Path("docs/research/ilc_sim_leakage_01_run2_post_both_layers_results_779_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestPhase779SimRun2(unittest.TestCase):
    def test_artifact_exists_with_required_sections(self) -> None:
        text = _read(ARTIFACT)
        for heading in (
            "## 1. Run configuration (batch window, relay count, relay path)",
            "## 2. Variant A recall (post-both-layers)",
            "## 3. Variant B recall (post-both-layers)",
            "## 4. Variant C recall (post-both-layers)",
            "## 5. Band assessment (each variant vs. threshold)",
            "## 6. Batching calibration result",
            "## 7. Residual gap (if any)",
        ):
            self.assertIn(heading, text)

    def test_completion_and_result_tokens_present(self) -> None:
        text = _read(ARTIFACT)
        for marker in (
            "sim_leakage_01_run2_post_both_layers_complete",
            "run2_relay_path=2->3->1",
            "variant_a_post_both_layers_recall_500ms=0.8888888888888888",
            "variant_a_post_both_layers_recall_1000ms=0.7777777777777778",
            "variant_b_structural_recall_exceeds_threshold=1.0",
            "variant_c_structural_recall_exceeds_threshold=1.0",
            "run2_recommended_batch_window=none_liveness_not_met",
        ):
            self.assertIn(marker, text)

    def test_artifact_explicitly_uses_relay_aware_path(self) -> None:
        text = _read(ARTIFACT)
        self.assertIn("Run 2 used the real relay-aware submission path introduced in Phase 778", text)
        self.assertIn("Legacy direct-broadcast path", text)
        self.assertIn("not used in Run 2", text)

    def test_both_batch_windows_and_liveness_shortfall_are_recorded(self) -> None:
        text = _read(ARTIFACT)
        self.assertIn("`500ms`", text)
        self.assertIn("`1000ms`", text)
        self.assertIn("validator-1 only logged `18` final-destination acknowledgements out of `20`", text)
        self.assertIn("no recommended default is justified from this window", text)

    def test_variant_b_and_c_are_honestly_recorded_as_structural_failures(self) -> None:
        text = _read(ARTIFACT)
        self.assertIn("Recall (structural) | `1.0`", text)
        self.assertIn("**FAIL (structural)**", text)
        self.assertIn("Layer-1 and Layer-2 do not change the gRPC `GetBalance` surface", text)
        self.assertIn("Layer-2 changes the submission path, but it does not anonymize the public epoch-lineage surface", text)


if __name__ == "__main__":
    unittest.main()
