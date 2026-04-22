from __future__ import annotations

from pathlib import Path
import unittest


LANE_DOC = Path("docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestPhase771LaneDocUpdate(unittest.TestCase):
    def test_sec_004_and_m007_status_lines_updated(self) -> None:
        text = _read(LANE_DOC)
        self.assertIn(
            "SEC-004 CLOSED phase_768 — existing acceptance test retained and passing; historical ValidatorSet resolution confirmed; testnet client epoch fix applied; live settlement wiring deferred pending CDL-017 payload design",
            text,
        )
        self.assertIn(
            "M-007 hooks ACTIVATED phase_769 — admit_validator and eject_validator implemented under CDL-017 authority as local ValidatorSet mutation helpers; production governance delivery deferred",
            text,
        )

    def test_post_m022_activation_record_present(self) -> None:
        text = _read(LANE_DOC)
        self.assertIn("## Post-M-022 Activation Record", text)
        self.assertIn("Phase `768` (commit `25e21b5c`)", text)
        self.assertIn("Phase `769` (commit `48d8152a`)", text)

    def test_lane_doc_records_ratified_cdl_017_and_human_gate(self) -> None:
        text = _read(LANE_DOC)
        self.assertIn(
            "CDL-017 RATIFIED phase_765; first non-Genesis validator deployment remains behind a separate human gate",
            text,
        )
        self.assertIn("This document does not claim that gate has been crossed.", text)

    def test_stale_unimplemented_surface_removed(self) -> None:
        text = _read(LANE_DOC)
        self.assertNotIn("test_admit_validator_is_unimplemented", text)
        self.assertNotIn("test_eject_validator_is_unimplemented", text)
        self.assertIn("test_eject_validator_rejects_invalid_collapse", text)


if __name__ == "__main__":
    unittest.main()
