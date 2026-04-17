from __future__ import annotations
import json
import subprocess
from pathlib import Path

ARTIFACT_PATH = Path("docs/research/ilc_mysticeti_testnet_M012_full_bft_transfer_v0.1.md")
TEST_PATH = Path("tests/test_phase_M012_full_bft_transfer.py")
HARNESS_PATH = Path("tools/run_mysticeti_testnet_M012.sh")
CONSENSUS_DIR = Path("ilc_consensus")

REQUIRED_HEADINGS = (
    "## 1. Phase scope and design decisions",
    "## 2. Architecture",
    "## 3. keygen binary (keygen_main.rs)",
    "## 4. testnet_client binary (testnet_client_main.rs)",
    "## 5. Workload A harness (run_mysticeti_testnet_M012.sh)",
    "## 6. Build and test",
    "## 7. M-013 prerequisite checklist",
    "## 8. Audit checklist",
)

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")

import unittest

class TestPhaseM012(unittest.TestCase):
    def test_artifact_exists_and_contains_all_required_headings_in_order(self):
        text = _read(ARTIFACT_PATH)
        positions = [text.index(heading) for heading in REQUIRED_HEADINGS]
        self.assertEqual(positions, sorted(positions))

    def test_testnet_client_supports_full_transfer(self):
        client_text = _read(CONSENSUS_DIR / "src" / "testnet_client_main.rs")
        self.assertIn("MsgType::FullTransfer", client_text)
        self.assertIn("listen_addr", client_text)

    def test_harness_supports_m012_modes(self):
        harness_text = _read(HARNESS_PATH)
        self.assertIn("--gen-client-tls", harness_text)
        self.assertIn("--update-configs", harness_text)

    def test_verdict_token_present(self):
        text = _read(ARTIFACT_PATH)
        self.assertIn("`run_m012_full_bft_transfer_verdict=binary_complete`", text)

if __name__ == '__main__':
    unittest.main()
