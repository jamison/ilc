from __future__ import annotations

from pathlib import Path
import unittest


COHERENCE_PATH = Path("docs/specs/ilc_coherence_report_773_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v5.6.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split())


class TestPhase773CoherenceAndCapsule(unittest.TestCase):
    def test_output_files_exist(self) -> None:
        self.assertTrue(COHERENCE_PATH.exists())
        self.assertTrue(CAPSULE_PATH.exists())

    def test_coherence_report_records_window_delta(self) -> None:
        text = _read(COHERENCE_PATH)
        self.assertIn("SEC-004 acceptance test was preserved and re-verified", text)
        self.assertIn("testnet client no longer hardcodes `epoch: EpochSeq(1)`", text)
        self.assertIn("M-007 `admit_validator` and `eject_validator` are now live", text)
        self.assertIn("integration gate re-ran the Rust and Python evidence suite", text)

    def test_coherence_report_records_non_conflation_obligations(self) -> None:
        text = _normalized(_read(COHERENCE_PATH))
        self.assertIn(
            "SEC-004 acceptance-test passage is not proof that live `rotate_validator_set` wiring exists",
            text,
        )
        self.assertIn(
            "M-007 hook activation is not first non-Genesis validator admission.",
            text,
        )
        self.assertIn(
            "Row `5`, row `8`, and Option B are unaffected by this window.",
            text,
        )

    def test_capsule_v56_supersedes_v55_and_updates_status_lines(self) -> None:
        text = _read(CAPSULE_PATH)
        self.assertIn(
            "Supersedes: docs/specs/ilc_antigravity_context_capsule_v5.5.md",
            text,
        )
        self.assertIn("`capsule_v5_6_supersedes_v5_5`", text)
        self.assertIn(
            "M-007 `admit_validator` / `eject_validator` hooks are now activated as local",
            text,
        )
        self.assertIn(
            "`SEC-004` is now closed at the acceptance-bar scope in Phase `768`",
            text,
        )

    def test_capsule_preserves_explicit_deferrals(self) -> None:
        text = _normalized(_read(CAPSULE_PATH))
        self.assertIn("live settlement-path wiring for `rotate_validator_set` remains deferred", text)
        self.assertIn(
            "production governance delivery for validator admission and ejection remains deferred",
            text,
        )
        self.assertIn("first non-Genesis validator deployment remains a separate human gate", text)

    def test_capsule_does_not_advance_row5_row8_or_option_b(self) -> None:
        text = _read(CAPSULE_PATH)
        self.assertIn("row `5` remains honest-fail `spec_closed_runtime_pending`", text)
        self.assertIn("row `8` remains inherited with no candidate evaluation", text)
        self.assertIn("Option B remains `no-go`", text)

    def test_capsule_records_h_series_as_unchanged_in_this_window(self) -> None:
        coherence = _normalized(_read(COHERENCE_PATH))
        capsule = _normalized(_read(CAPSULE_PATH))
        self.assertIn("H-series posture stays unchanged in this window.", coherence)
        self.assertIn("no new H-lane surface changed in this window", capsule)


if __name__ == "__main__":
    unittest.main()
