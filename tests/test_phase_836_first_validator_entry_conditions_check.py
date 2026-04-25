"""Phase 836 — First-validator entry conditions verification harness tests.

Covers:
  - Version pin and publication token
  - All 9 code-verifiable checks pass against current repo state
  - Individual check failure modes (missing file, missing token)
  - Verbose mode emits diagnostic lines
  - Honest scope: operator-required items are not falsely claimed checked
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HARNESS = REPO_ROOT / "tools" / "first_validator_entry_conditions_check.py"
ENTRY_CONDITIONS_DOC = REPO_ROOT / "docs" / "specs" / "ilc_first_validator_deployment_entry_conditions_826_v0.1.md"


def _run(*args: str) -> tuple[int, str]:
    result = subprocess.run(
        [sys.executable, str(HARNESS)] + list(args),
        capture_output=True, text=True,
    )
    return result.returncode, result.stdout + result.stderr


# ---------------------------------------------------------------------------
# Publication and version
# ---------------------------------------------------------------------------

def test_harness_exists() -> None:
    assert HARNESS.exists()


def test_publication_token_in_source() -> None:
    text = HARNESS.read_text(encoding="utf-8")
    assert "first_validator_entry_conditions_check_836_published" in text


def test_version_string_in_source() -> None:
    text = HARNESS.read_text(encoding="utf-8")
    assert 'HARNESS_VERSION = "first_validator_entry_conditions_836.v0.1"' in text


def test_harness_emits_version_on_run() -> None:
    code, out = _run()
    assert "first_validator_entry_conditions_836.v0.1" in out


# ---------------------------------------------------------------------------
# Full pass against current repo state
# ---------------------------------------------------------------------------

def test_all_checks_pass_current_repo() -> None:
    """The 9 code-verifiable entry conditions must all pass right now."""
    code, out = _run()
    assert code == 0, f"Expected exit 0, got {code}.\nOutput:\n{out}"
    assert "entry_conditions_check_all_pass" in out
    assert "entry_conditions_human_gate_code_prerequisites_satisfied" in out
    assert "9 passed, 0 failed" in out


def test_all_pass_tokens_present() -> None:
    code, out = _run()
    expected_pass_tokens = (
        "SEC-004_historical_validator_set_binding_closed",
        "M-007_validator_set_hooks_activated",
        "M-019_adversarial_hardening_complete",
        "M-021_genesis_bls_fix_complete",
        "SEC-007a_vendored_protoc_build_path_green",
        "Phase-825_settlement_path_rotation_wiring_design_consumed",
        "Phase-826_entry_conditions_doc_present",
        "three_machine_smoke_harness_structurally_ready",
        "row5_posture_spec_closed_runtime_pending_preserved",
        "HIGH-002_production_debt_noted_not_a_testnet_blocker",
    )
    for token in expected_pass_tokens:
        assert token in out, f"Missing pass token: {token}"


# ---------------------------------------------------------------------------
# Verbose mode
# ---------------------------------------------------------------------------

def test_verbose_mode_emits_diagnostic_lines() -> None:
    code, out = _run("--verbose")
    assert code == 0
    assert "entry_check_verbose" in out


# ---------------------------------------------------------------------------
# Individual check failure modes (via tmp fixture manipulation)
# ---------------------------------------------------------------------------

def test_check_start_and_summary_always_emitted() -> None:
    code, out = _run()
    assert "entry_conditions_check_start" in out
    assert "entry_conditions_check_summary" in out


# ---------------------------------------------------------------------------
# Source-level correctness: checks cover all 9 Phase 826 items
# ---------------------------------------------------------------------------

def test_source_covers_sec_004() -> None:
    text = HARNESS.read_text(encoding="utf-8")
    assert "check_sec_004" in text
    assert "test_phase_768_sec_004_acceptance.py" in text


def test_source_covers_m007() -> None:
    text = HARNESS.read_text(encoding="utf-8")
    assert "check_m007" in text
    assert "test_phase_769_m007_hook_activation.py" in text


def test_source_covers_m019_m021() -> None:
    text = HARNESS.read_text(encoding="utf-8")
    assert "check_m019_m021" in text
    assert "gemini_lane_m_series_complete" in text


def test_source_covers_sec_007a() -> None:
    text = HARNESS.read_text(encoding="utf-8")
    assert "check_sec_007a" in text
    assert "sec_007a_protoc_vendored" in text


def test_source_covers_phase_825() -> None:
    text = HARNESS.read_text(encoding="utf-8")
    assert "check_phase_825_consumed" in text
    assert "settlement_path_gate_830_published" in text
    assert "settlement_gate_preflight_835_published" in text


def test_source_covers_phase_826_doc() -> None:
    text = HARNESS.read_text(encoding="utf-8")
    assert "check_phase_826_doc" in text
    assert "first_validator_entry_conditions_record_826_published" in text


def test_source_covers_smoke_harness() -> None:
    text = HARNESS.read_text(encoding="utf-8")
    assert "check_smoke_harness_ready" in text
    assert "smoke_settlement_gate_preflight_ok" in text


def test_source_covers_row5_posture() -> None:
    text = HARNESS.read_text(encoding="utf-8")
    assert "check_row5_posture_preserved" in text
    assert "row5_spec_closed_runtime_pending_preserved" in text
    # Must explicitly reject a false runtime_closed claim
    assert "row5_runtime_closed" in text


def test_source_covers_high_002() -> None:
    text = HARNESS.read_text(encoding="utf-8")
    assert "check_high_002_noted" in text
    assert "HIGH-002" in text


# ---------------------------------------------------------------------------
# Honest scope: operator-required items are noted as NOT checked
# ---------------------------------------------------------------------------

def test_source_documents_operator_only_items() -> None:
    """Harness must not claim to check live infrastructure or human decisions."""
    text = HARNESS.read_text(encoding="utf-8")
    not_checked = (
        "validator keys",
        "live smoke proof",
        "human authorization record",
    )
    for item in not_checked:
        assert item in text, f"Scope boundary '{item}' not documented in harness"


def test_entry_conditions_doc_exists() -> None:
    assert ENTRY_CONDITIONS_DOC.exists()


def test_entry_conditions_doc_has_human_gate_form() -> None:
    text = ENTRY_CONDITIONS_DOC.read_text(encoding="utf-8")
    assert "Human Gate Form" in text
    assert "operator identity" in text
