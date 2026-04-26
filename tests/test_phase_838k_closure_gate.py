"""Phase 838k — CDL-069 ratification window closure gate.

Asserts:
  1. CDL-069 is ratified in the constitutional decision log.
  2. All three CDL-069 runtime version tokens are present.
  3. All three CDL-069 dependency tokens are present.
  4. The ratification evidence document exists.
  5. The ratification readiness dossier exists.
  6. The coherence report exists.
  7. The capsule v5.17 exists.
  8. All 213 phase-838 runtime tests pass (selftest guard).
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Selftest guard — skip expensive test execution when running nested
# ---------------------------------------------------------------------------
_SELFTEST = os.environ.get("ILC_PHASE_838K_GATE_SELFTEST") == "1"

REPO_ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# 1. CDL-069 ratified in decision log
# ---------------------------------------------------------------------------

def test_cdl_069_ratified_in_decision_log() -> None:
    cdl_log = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
    text = cdl_log.read_text()
    # Find the CDL-069 row and assert status is 'ratified'
    for line in text.splitlines():
        if "| CDL-069 |" in line:
            assert "| ratified |" in line, (
                f"CDL-069 row does not show status=ratified:\n{line}"
            )
            assert "ratified_phase: 838j" in line
            assert "ratified_date: 2026-04-26" in line
            return
    pytest.fail("CDL-069 row not found in decision log")


# ---------------------------------------------------------------------------
# 2. Runtime version tokens
# ---------------------------------------------------------------------------

def test_genesis_record_schema_version_token() -> None:
    from ilc_core.identity.genesis_record_schema import GENESIS_RECORD_SCHEMA_VERSION
    assert GENESIS_RECORD_SCHEMA_VERSION == "genesis_record_schema_838e.v0.1"


def test_endorsement_packet_schema_version_token() -> None:
    from ilc_core.identity.endorsement_packet_schema import ENDORSEMENT_PACKET_SCHEMA_VERSION
    assert ENDORSEMENT_PACKET_SCHEMA_VERSION == "endorsement_packet_schema_838f.v0.1"


def test_epoch_endorsement_runtime_version_token() -> None:
    from ilc_core.identity.epoch_endorsement_runtime import EPOCH_ENDORSEMENT_RUNTIME_VERSION
    assert EPOCH_ENDORSEMENT_RUNTIME_VERSION == "epoch_endorsement_runtime_838c.v0.1"


# ---------------------------------------------------------------------------
# 3. CDL-069 dependency tokens
# ---------------------------------------------------------------------------

def test_genesis_record_schema_cdl_069_dependency() -> None:
    from ilc_core.identity.genesis_record_schema import CDL_069_DEPENDENCY
    assert CDL_069_DEPENDENCY == "cdl_069_opens_phase_838"


def test_endorsement_packet_schema_cdl_069_dependency() -> None:
    from ilc_core.identity.endorsement_packet_schema import CDL_069_DEPENDENCY
    assert CDL_069_DEPENDENCY == "cdl_069_opens_phase_838"


def test_epoch_endorsement_runtime_cdl_069_dependency() -> None:
    from ilc_core.identity.epoch_endorsement_runtime import CDL_069_DEPENDENCY
    assert CDL_069_DEPENDENCY == "cdl_069_opens_phase_838"


# ---------------------------------------------------------------------------
# 4–7. Required documents exist
# ---------------------------------------------------------------------------

def test_ratification_evidence_document_exists() -> None:
    path = REPO_ROOT / "docs/specs/ilc_cdl_069_pq_identity_and_epoch_endorsement_protocol_ratification_evidence_838j_v0.1.md"
    assert path.exists(), f"Ratification evidence document missing: {path}"
    text = path.read_text()
    assert "cdl_069_ratification_evidence_complete" in text
    assert "cdl_069_commit_1_does_not_mutate_decision_log" in text


def test_ratification_readiness_dossier_exists() -> None:
    path = REPO_ROOT / "docs/specs/ilc_cdl_069_ratification_readiness_dossier_838j_v0.1.md"
    assert path.exists(), f"Ratification readiness dossier missing: {path}"
    text = path.read_text()
    assert "cdl_069_ratification_readiness_verdict=ready_for_ratification" in text


def test_coherence_report_838_exists() -> None:
    path = REPO_ROOT / "docs/specs/ilc_integration_coherence_report_838_v0.1.md"
    assert path.exists(), f"Coherence report missing: {path}"
    text = path.read_text()
    assert "cdl_069_ratification_838_coherence_published" in text
    assert "phase_838_test_count_213_all_pass" in text


def test_capsule_v5_17_exists() -> None:
    path = REPO_ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.17.md"
    assert path.exists(), f"Capsule v5.17 missing: {path}"
    text = path.read_text()
    assert "capsule_v5_17_supersedes_v5_16" in text
    assert "cdl_069_ratified_recorded_in_capsule_v5_17" in text


# ---------------------------------------------------------------------------
# 8. Phase 838 runtime tests all pass
# ---------------------------------------------------------------------------

@pytest.mark.skipif(_SELFTEST, reason="selftest guard: skip nested test run")
def test_phase_838_runtime_tests_all_pass() -> None:
    """Run all three phase-838 test suites and assert 213 tests pass."""
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/test_phase_838c_epoch_endorsement_runtime.py",
            "tests/test_phase_838e_genesis_record_schema.py",
            "tests/test_phase_838f_endorsement_packet_schema.py",
            "-q", "--tb=short",
            f"--rootdir={REPO_ROOT}",
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env={**os.environ, "ILC_PHASE_838K_GATE_SELFTEST": "1"},
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, f"Phase 838 runtime tests failed:\n{output}"
    assert "213 passed" in output, (
        f"Expected '213 passed' in test output, got:\n{output}"
    )
