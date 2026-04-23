from __future__ import annotations

from pathlib import Path
import unittest


NETWORK = Path("ilc_consensus/src/network.rs")
NODE = Path("ilc_consensus/src/node.rs")
CLIENT = Path("ilc_consensus/src/testnet_client_main.rs")
HARNESS = Path("tools/testbed/ilc_sim_leakage_01_harness.py")
RUNNER = Path("tools/testbed/ilc_sim_leakage_01_runner.sh")
SPEC = Path("docs/specs/ilc_row_5_layer2_mechanism_implementation_778_v0.1.md")
TYPES = Path("ilc_consensus/src/types.rs")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestPhase778Layer2Implementation(unittest.TestCase):
    def test_spec_exists_with_required_sections_and_token(self) -> None:
        text = _read(SPEC)
        self.assertIn("layer2_batching_multi_relay_implemented", text)
        sections = (
            "## 1. Mechanism decision record",
            "## 2. Batching implementation",
            "## 3. Multi-relay routing implementation",
            "## 4. Relay path selection: testnet allowlist baseline and later runtime target",
            "## 5. ZK compatibility note",
            "## 6. Observability floor non-impact statement",
        )
        for section in sections:
            self.assertIn(section, text)

    def test_spec_records_actual_m009_relay_path_and_excludes_validator_4(self) -> None:
        text = _read(SPEC)
        self.assertIn("2 -> 3 -> 1", text)
        self.assertIn("validator-2", text)
        self.assertIn("validator-3", text)
        self.assertIn("validator-4", text)
        self.assertIn("not part of the honest relay baseline", text)

    def test_zk_note_keeps_transfer_certificate_unchanged(self) -> None:
        text = _read(SPEC)
        self.assertIn("TransferCertificate", text)
        self.assertIn("outside the `TransferCertificate` field structure", text)

    def test_network_adds_testnet_only_relay_wrapper(self) -> None:
        text = _read(NETWORK)
        self.assertIn("RelaySubmit", text)
        self.assertIn("testnet_only", text)
        self.assertIn("remaining_route: Vec<ValidatorID>", text)

    def test_node_adds_relay_forwarding_with_loop_and_cap_guards(self) -> None:
        text = _read(NODE)
        self.assertIn("handle_relay_submit", text)
        self.assertIn("MAX_TESTNET_RELAY_HOPS", text)
        self.assertIn("duplicate validator", text)
        self.assertIn("loops back through validator", text)
        self.assertIn("final relay destination", text)

    def test_client_exposes_batch_and_relay_flags(self) -> None:
        text = _read(CLIENT)
        for marker in (
            "--batch-window-ms",
            "--relay-count",
            "--relay-route",
            "compute_relay_plan",
            "layer2 relay mode enabled",
            "RelaySubmit(testnet_only)",
            "duplicate validator id",
            "duplicate validator address",
        ):
            self.assertIn(marker, text)

    def test_harness_and_runner_support_relay_aware_submission_mode(self) -> None:
        harness = _read(HARNESS)
        runner = _read(RUNNER)
        self.assertIn("SIM_LEAKAGE_USE_LAYER2", harness)
        self.assertIn("--relay-route", harness)
        self.assertIn("--validators", harness)
        self.assertIn("submission_mode", harness)
        self.assertIn("SIM_LEAKAGE_USE_LAYER2", runner)
        self.assertIn("SIM_LEAKAGE_RELAY_ROUTE", runner)

    def test_transfer_certificate_contract_not_extended_with_relay_or_batch_fields(self) -> None:
        text = _read(TYPES)
        self.assertNotIn("relay_count", text)
        self.assertNotIn("batch_window_ms", text)
        self.assertNotIn("remaining_route", text)


if __name__ == "__main__":
    unittest.main()
