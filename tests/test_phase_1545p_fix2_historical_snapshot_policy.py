"""Phase 1545p-Fix2 historical phase-snapshot pytest policy tests."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFTEST_PATH = ROOT / "tests" / "conftest.py"
PYPROJECT_PATH = ROOT / "pyproject.toml"


def _load_conftest_module():
    spec = importlib.util.spec_from_file_location("phase1545p_fix2_conftest", CONFTEST_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_historical_snapshot_policy_lists_observed_third_tranche_wall() -> None:
    conftest = _load_conftest_module()
    files = set(conftest.historical_phase_snapshot_files())
    assert "test_phase_1101_window_945_1101_closure_gate.py" in files
    assert "test_phase_1109_window_1102_1109_closure_gate.py" in files
    assert "test_phase_1147_window_1139_1147_closure_gate.py" in files
    assert "test_phase_1149_atlas_tier2_patch.py" in files
    assert "test_phase_1177_cdl_085_prelock.py" in files
    assert "test_phase_1183_sequence_lock.py" in files
    assert "test_phase_1184_cdl_085_prelock_hardening.py" in files
    assert "test_phase_1199_window_1191_1199_closure_gate.py" in files
    assert "test_phase_1208_window_1200_1208_closure_gate.py" in files
    assert "test_phase_1209_sequence_lock.py" in files
    assert "test_phase_1251_gap14_package_ci_gate.py" in files
    assert "test_phase_1281_window_1281_1288_sequence_lock.py" in files
    assert "test_phase_1282_context_capsule_v5_51_frontier_refresh.py" in files
    assert "test_phase_1295_transport_principal_lifecycle_revocation_replay_preflight.py" in files
    assert "test_phase_1302_window_1289_1302_closure_gate.py" in files
    assert "test_phase_1304_context_capsule_v5_53_frontier_refresh.py" in files
    assert "test_phase_1321_release_key_envelope_procedure_rehearsal.py" in files
    assert "test_phase_1333_source_allowlist_export_execution_gate.py" in files
    assert "test_phase_1362_blocking_authority_vehicle_opening.py" in files
    assert "test_phase_1369_sequence_lock.py" in files
    assert "test_phase_1405_cdl_092_ratification.py" in files
    assert "test_phase_1422_launch_readiness_manifest_schema.py" in files
    assert "test_phase_1434_transport_principal_cdl_opening.py" in files
    assert "test_phase_1504p_window_1498p_closure_gate.py" in files
    assert "test_phase_1515p_window_1515p_1522p_sequence_lock.py" in files
    assert "test_phase_1537p_window_1531p_1537p_closure_gate.py" in files
    assert "test_phase_1545p_window_1538p_1545p_closure_gate.py" in files
    assert "test_phase_436_runtime_tranche_benchmark_harness_and_tranche_completion.py" in files
    assert "test_phase_455_sim_t_comparative_synthesis.py" in files
    assert "test_phase_456_fix_14_cdl_050_blocker_clearance_gate_rerun.py" in files
    assert "test_phase_459_post5_local_hysteretic_oscillator_execution_and_post_window_blocker_reassessment.py" in files
    assert "test_phase_541_cdl_060_ratification_evidence.py" in files
    assert "test_phase_572_three_machine_smoke_harness.py" in files
    assert "test_phase_606_mempalace_internal_retrieval_adoption.py" in files
    assert "test_phase_711_validator_sim_commissioning_and_cdl_039_scope_note.py" in files
    assert "test_phase_712_coherence_report_capsule_v4_6_and_window_707_712_closure_gate.py" in files
    assert "test_phase_751_stale_planning_doc_archival_and_planning_index_advance.py" in files
    assert "test_phase_836_first_validator_entry_conditions_check.py" in files
    assert "test_phase_843_closure_gate.py" in files
    assert "test_phase_M009_mysticeti_testnet_setup.py" in files
    assert "test_phase_high002_phase_b_closure_gate.py" in files
    assert "test_window_1281_1288_prompt_drafts.py" in files
    assert "test_window_1317_1329_prompt_drafts.py" in files
    assert "test_window_1343_1368_prompt_drafts.py" in files


def test_expensive_release_artifact_policy_lists_phase_228_build_probe() -> None:
    conftest = _load_conftest_module()
    files = set(conftest.expensive_release_artifact_files())
    assert "test_genesis_distribution_surface_phase_225.py" in files
    assert "test_genesis_release_artifacts_phase_228.py" in files
    assert "test_reproducible_build_phase_230.py" in files


def test_historical_snapshot_policy_is_filename_exact() -> None:
    conftest = _load_conftest_module()
    assert conftest.is_historical_phase_snapshot_path(
        "tests/test_phase_1101_window_945_1101_closure_gate.py"
    )
    assert conftest.is_historical_phase_snapshot_path("tests/test_phase_1545p_window_1538p_1545p_closure_gate.py")
    assert not conftest.is_historical_phase_snapshot_path("tests/test_phase_1545p_fix2_historical_snapshot_policy.py")
    assert not conftest.is_historical_phase_snapshot_path("tests/test_network.py")


def test_expensive_release_artifact_policy_is_filename_exact() -> None:
    conftest = _load_conftest_module()
    assert conftest.is_expensive_release_artifact_path(
        "tests/test_genesis_distribution_surface_phase_225.py"
    )
    assert conftest.is_expensive_release_artifact_path(
        "tests/test_genesis_release_artifacts_phase_228.py"
    )
    assert not conftest.is_expensive_release_artifact_path("tests/test_network.py")


def test_historical_snapshot_policy_default_off_opt_in(monkeypatch) -> None:
    conftest = _load_conftest_module()
    monkeypatch.delenv(conftest.RUN_HISTORICAL_PHASE_SNAPSHOTS_ENV, raising=False)
    assert conftest.historical_phase_snapshot_tests_enabled() is False
    monkeypatch.setenv(conftest.RUN_HISTORICAL_PHASE_SNAPSHOTS_ENV, "1")
    assert conftest.historical_phase_snapshot_tests_enabled() is True
    monkeypatch.setenv(conftest.RUN_HISTORICAL_PHASE_SNAPSHOTS_ENV, "true")
    assert conftest.historical_phase_snapshot_tests_enabled() is False


def test_expensive_release_artifact_policy_default_off_opt_in(monkeypatch) -> None:
    conftest = _load_conftest_module()
    monkeypatch.delenv(conftest.RUN_EXPENSIVE_RELEASE_ARTIFACT_TESTS_ENV, raising=False)
    assert conftest.expensive_release_artifact_tests_enabled() is False
    monkeypatch.setenv(conftest.RUN_EXPENSIVE_RELEASE_ARTIFACT_TESTS_ENV, "1")
    assert conftest.expensive_release_artifact_tests_enabled() is True
    monkeypatch.setenv(conftest.RUN_EXPENSIVE_RELEASE_ARTIFACT_TESTS_ENV, "true")
    assert conftest.expensive_release_artifact_tests_enabled() is False


def test_pyproject_declares_historical_snapshot_marker() -> None:
    text = PYPROJECT_PATH.read_text(encoding="utf-8")
    assert "historical_phase_snapshot" in text
    assert "ILC_RUN_HISTORICAL_PHASE_SNAPSHOT_TESTS=1" in text
    assert "expensive_release_artifact" in text
    assert "ILC_RUN_EXPENSIVE_RELEASE_ARTIFACT_TESTS=1" in text
