"""Phase 830 settlement-path rotation gate tests.

Verifies the pre-deployment wiring introduced in Phase 830:
- SettlementPath enum and settlement_path config field in config.rs
- check_settlement_path_gate function in main.rs
- Operator activation log tokens
- Scope boundary: no live routing, no first-validator deployment, no CDL mutation
"""
from __future__ import annotations

from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_RS = REPO_ROOT / "ilc_consensus" / "src" / "config.rs"
MAIN_RS = REPO_ROOT / "ilc_consensus" / "src" / "main.rs"
WALKTHROUGH = REPO_ROOT / "docs" / "phases" / "phase_830_settlement_path_gate.md"
DESIGN_DOC = REPO_ROOT / "docs" / "specs" / "ilc_settlement_path_rotation_wiring_design_825_v0.1.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestPhase830SettlementPathGate(unittest.TestCase):

    # ------------------------------------------------------------------
    # config.rs
    # ------------------------------------------------------------------

    def test_settlement_path_enum_declared(self) -> None:
        text = _read(CONFIG_RS)
        self.assertIn("pub enum SettlementPath", text)
        self.assertIn("None,", text)
        self.assertIn("MysticetiFastPath,", text)
        self.assertIn("settlement_path_gate_type_825", text)

    def test_settlement_path_field_in_node_config(self) -> None:
        text = _read(CONFIG_RS)
        self.assertIn("pub settlement_path: SettlementPath", text)

    def test_settlement_path_parsed_before_file_io(self) -> None:
        # Within load_node_config, the settlement_path validation must appear
        # before the tls_cert_path load call so unknown values produce errors
        # in deterministic order regardless of file system state.
        text = _read(CONFIG_RS)
        fn_start = text.find("pub fn load_node_config(")
        self.assertGreater(fn_start, 0, "load_node_config not found")
        fn_body = text[fn_start:]
        unknown_val_check = fn_body.find("settlement_path: unknown value")
        tls_cert_load = fn_body.find("load_pem_as_der(&cfg.tls_cert_path)")
        self.assertGreater(
            tls_cert_load, unknown_val_check,
            "settlement_path validation must precede tls_cert_path load within load_node_config",
        )

    def test_settlement_path_default_is_none(self) -> None:
        text = _read(CONFIG_RS)
        self.assertIn('"none" | "" => SettlementPath::None', text)
        self.assertIn('unwrap_or("none")', text)

    def test_config_tests_cover_settlement_path(self) -> None:
        text = _read(CONFIG_RS)
        for marker in (
            "test_settlement_path_defaults_to_none_when_omitted",
            "test_settlement_path_none_string_accepted",
            "test_settlement_path_unknown_value_rejected",
        ):
            self.assertIn(marker, text)

    # ------------------------------------------------------------------
    # main.rs
    # ------------------------------------------------------------------

    def test_check_settlement_path_gate_function_present(self) -> None:
        text = _read(MAIN_RS)
        self.assertIn("fn check_settlement_path_gate(", text)
        self.assertIn("settlement_path_gate_check_830", text)

    def test_gate_emits_none_posture_token(self) -> None:
        text = _read(MAIN_RS)
        self.assertIn("settlement_path_none_posture_preserved", text)

    def test_gate_emits_activation_token(self) -> None:
        text = _read(MAIN_RS)
        self.assertIn("settlement_path_mysticeti_fast_path_activated", text)

    def test_gate_emits_f_zero_sec_warn(self) -> None:
        text = _read(MAIN_RS)
        self.assertIn("sec_warn_settlement_gate_f_zero", text)
        self.assertIn("HIGH-002", text)

    def test_gate_rollback_instruction_in_log(self) -> None:
        text = _read(MAIN_RS)
        self.assertIn("Rollback:", text)
        self.assertIn("settlement_path=none", text)

    def test_gate_requires_non_empty_network_id(self) -> None:
        text = _read(MAIN_RS)
        self.assertIn("non-empty network_id", text)

    def test_gate_called_in_run_function(self) -> None:
        text = _read(MAIN_RS)
        self.assertIn("check_settlement_path_gate(", text)

    def test_main_rs_tests_cover_gate(self) -> None:
        text = _read(MAIN_RS)
        for marker in (
            "test_settlement_gate_none_always_passes",
            "test_settlement_gate_fast_path_requires_non_empty_network_id",
            "test_settlement_gate_fast_path_requires_f_ge_1",
            "test_settlement_gate_fast_path_passes_with_valid_f",
        ):
            self.assertIn(marker, text)

    # ------------------------------------------------------------------
    # Scope boundary
    # ------------------------------------------------------------------

    def test_no_live_routing_wired(self) -> None:
        # The gate must not wire live submission ingress — that requires
        # separate human authorization (first-validator gate).
        main_text = _read(MAIN_RS)
        self.assertNotIn("handle_broadcast_honest(transfer", main_text)
        self.assertNotIn("handle_full_transfer_honest(transfer", main_text)

    def test_rotate_validator_set_remains_isolated(self) -> None:
        # rotate_validator_set must not be called from the gate check.
        gate_fn_start = _read(MAIN_RS).find("fn check_settlement_path_gate(")
        gate_fn_end = _read(MAIN_RS).find("\n#[tokio::main]")
        gate_fn_text = _read(MAIN_RS)[gate_fn_start:gate_fn_end]
        self.assertNotIn("rotate_validator_set", gate_fn_text)

    def test_walkthrough_exists_with_required_tokens(self) -> None:
        text = _read(WALKTHROUGH)
        for token in (
            "settlement_path_gate_830_published",
            "settlement_path_gate_check_830",
            "settlement_path_none_posture_preserved",
            "no_live_routing_in_phase_830",
            "no_first_validator_deployment_in_phase_830",
            "no_cdl_mutation_in_phase_830",
        ):
            self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main()
