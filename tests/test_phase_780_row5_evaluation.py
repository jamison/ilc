from __future__ import annotations

from pathlib import Path
import unittest


ARTIFACT = Path("docs/specs/ilc_row_5_evaluation_780_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestPhase780Row5Evaluation(unittest.TestCase):
    def test_artifact_exists_with_required_sections(self) -> None:
        text = _read(ARTIFACT)
        for heading in (
            "## 1. Run 2 recall summary (all three variants)",
            "## 2. Band assessment (pass / fail per variant)",
            "## 3. Verdict",
            "## 4. Residual gap (if non-closure)",
            "## 5. ZK nullifier long-term path",
            "## 6. Observability floor confirmation",
        ):
            self.assertIn(heading, text)

    def test_exactly_one_verdict_token_is_present(self) -> None:
        text = _read(ARTIFACT)
        self.assertIn("row_5_honest_nonclosure_verdict=bands_not_met", text)
        self.assertNotIn("row_5_closure_verdict=pass", text)

    def test_residual_recall_values_are_recorded(self) -> None:
        text = _read(ARTIFACT)
        self.assertIn("Variant A residual recall: `0.7777777777777778`", text)
        self.assertIn("Variant B residual structural recall: `1.0`", text)
        self.assertIn("Variant C residual structural recall: `1.0`", text)
        self.assertIn("`0 / 3` bands met", text)
        self.assertIn("variant_a_scoring_posture=conservative_upper_bound_from_order_and_version_alignment", text)
        self.assertIn("even the upper-bound", text)
        self.assertIn("order/version score fails the commissioned band", text)

    def test_row5_remains_pending_and_zk_path_is_named(self) -> None:
        text = _read(ARTIFACT)
        self.assertIn("`spec_closed_runtime_pending`", text)
        self.assertNotIn("`runtime_closed`", text)
        self.assertIn("ZK nullifier / selective disclosure overlay", text)
        self.assertIn("This path is named here explicitly. It is **not** implemented in this window.", text)


if __name__ == "__main__":
    unittest.main()
