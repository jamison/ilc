from __future__ import annotations

from pathlib import Path
import unittest


COHERENCE_PATH = Path("docs/specs/ilc_coherence_report_781_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v5.7.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split())


class TestPhase781CoherenceAndCapsule(unittest.TestCase):
    def test_output_files_exist(self) -> None:
        self.assertTrue(COHERENCE_PATH.exists())
        self.assertTrue(CAPSULE_PATH.exists())

    def test_coherence_report_records_window_delta(self) -> None:
        text = _read(COHERENCE_PATH)
        self.assertIn("BUG-001 through BUG-006 remained verified on committed head", text)
        self.assertIn("Phase 776 removed plaintext AgentID bytes from runtime logs", text)
        self.assertIn("Phase 778 added testnet-only Layer-2 relay forwarding", text)
        self.assertIn("Phase 777 and Phase 779 executed the two required SIM-LEAKAGE reruns", text)

    def test_coherence_report_records_honest_nonclosure(self) -> None:
        text = _read(COHERENCE_PATH)
        self.assertIn("row_5_honest_nonclosure_verdict=bands_not_met", text)
        self.assertIn("row `5` remains `spec_closed_runtime_pending`", text)
        self.assertIn("No recommended default batch window is justified from this window", text)

    def test_coherence_report_records_unchanged_surfaces(self) -> None:
        text = _normalized(_read(COHERENCE_PATH))
        self.assertIn("row `8`, which remains inherited with no candidate evaluation", text)
        self.assertIn("Option B, which remains `no-go`", text)
        self.assertIn("H-series frontier, which remains unchanged by this window", text)
        self.assertIn("no constitutional decision-log mutation occurred anywhere in Window 775-782", text)

    def test_capsule_v57_supersedes_v56_and_updates_row5_line(self) -> None:
        text = _read(CAPSULE_PATH)
        self.assertIn("Supersedes: docs/specs/ilc_antigravity_context_capsule_v5.6.md", text)
        self.assertIn("`capsule_v5_7_supersedes_v5_6`", text)
        self.assertIn(
            "row `5` remains `spec_closed_runtime_pending — two-layer remediation applied; 0/3 bands met; Variant A/B/C residual gaps documented`",
            text,
        )

    def test_capsule_does_not_advance_row8_option_b_or_h_series(self) -> None:
        text = _read(CAPSULE_PATH)
        self.assertIn("row `8` remains inherited with no candidate evaluation", text)
        self.assertIn("Option B remains `no-go`", text)
        self.assertIn("hypergraph H-lane posture is unchanged in this window", text)


if __name__ == "__main__":
    unittest.main()
