from __future__ import annotations

from pathlib import Path
import unittest


FAST_PATH = Path("ilc_consensus/src/fast_path.rs")
CLIENT = Path("ilc_consensus/src/testnet_client_main.rs")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestPhase768Sec004Acceptance(unittest.TestCase):
    def test_sec_004_acceptance_test_exists(self) -> None:
        text = _read(FAST_PATH)
        self.assertIn(
            "fn test_ejected_validator_sig_rejected_after_epoch_boundary()",
            text,
        )

    def test_sec_004_acceptance_test_covers_historical_boundary_cases(self) -> None:
        text = _read(FAST_PATH)
        markers = (
            "epoch-1 cert with V3 sig must be accepted before the ejection boundary",
            "epoch-1 cert with V3 sig must remain accepted after the epoch-2 rotation",
            "epoch-2 cert with ejected V3 sig must be rejected",
            "epoch-2 cert with a valid post-ejection quorum must be accepted",
        )
        for marker in markers:
            self.assertIn(marker, text)

    def test_full_transfer_client_no_longer_hardcodes_cert_epoch(self) -> None:
        text = _read(CLIENT)
        self.assertNotIn("epoch: EpochSeq(1)", text)
        self.assertIn("let cert_epoch = EpochSeq(args.start_epoch.max(1));", text)
        self.assertIn("epoch: cert_epoch", text)

    def test_client_fix_is_anchored_to_phase_768_audit_finding(self) -> None:
        text = _read(CLIENT)
        self.assertIn("Phase 768 / Audit Finding D (M-015)", text)


if __name__ == "__main__":
    unittest.main()
