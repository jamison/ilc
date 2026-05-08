from pathlib import Path


REPORT = Path("docs/specs/ilc_coherence_report_1239_v0.1.md")
CAPSULE = Path("docs/specs/ilc_antigravity_context_capsule_v5.50.md")
STATUS = Path("docs/phases/STATUS.md")
PLANNING_INDEX = Path("docs/PLANNING_INDEX.md")


def test_phase_1239_report_exists_and_records_pass() -> None:
    text = REPORT.read_text(encoding="utf-8")
    assert "coherence_report_1239_verdict=pass" in text
    assert "window_1233_1240_sequence_lock_committed" in text
    assert "sim_fetch_01_fix10_robustness_suite_1238j.v0.1" in text


def test_capsule_v5_50_exists_and_supersedes_v5_49() -> None:
    text = CAPSULE.read_text(encoding="utf-8")
    assert "capsule_v5_50_supersedes_v5_49" in text
    assert "**Supersedes:** `docs/specs/ilc_antigravity_context_capsule_v5.49.md`" in text


def test_capsule_records_current_phase_1238j_frontier() -> None:
    text = CAPSULE.read_text(encoding="utf-8")
    assert "SIM_FETCH_01_HARNESS_VERSION = \"sim_fetch_01_harness_1238j.v0.1\"" in text
    assert "SIM_FETCH_01_FIX10_VERSION = \"sim_fetch_01_fix10_robustness_suite_1238j.v0.1\"" in text
    assert "sim_fetch_01_retry_and_adaptive_recovery_validated_phase_1238j" in text
    assert "stale-directory failures" in text


def test_capsule_records_cdl_087_candidate_not_ratified_boundary() -> None:
    text = CAPSULE.read_text(encoding="utf-8")
    assert "OPEN / PRELOCKED / NOT RATIFIED" in text
    assert "cdl_087_candidate_envelope_identified_not_ratified_phase_1238j" in text
    assert "cdl_087_ratification_deferred_pending_sim_fetch_01" in text
    assert "did not ratify CDL-087" in text


def test_capsule_records_commit_epoch_and_sidecar_boundaries() -> None:
    text = CAPSULE.read_text(encoding="utf-8")
    assert "COMMIT_EPOCH_FINALIZED_ADAPTER_VERSION = \"commit_epoch_finalized_adapter_1236_fix4.v0.1\"" in text
    assert "commit_epoch_production_emission_not_yet_authorized" in text
    assert "SIDECAR_QUERY_RUNTIME_VERSION = \"sidecar_query_runtime_1237.v0.1\"" in text
    assert "No sidecar projection endpoint or network sidecar service" in text


def test_capsule_records_public_rc_profile_split_and_v1_1_requirement() -> None:
    text = CAPSULE.read_text(encoding="utf-8")
    assert "PUBLIC_RC_PACKAGE_PROFILES_VERSION = \"public_rc_package_profiles_1238_post.v0.2\"" in text
    assert "openclaw_skill_local" in text
    assert "openclaw_skill_claimable" in text
    assert "launch_roadmap_v1_1_refresh_required_after_phase_1240" in text


def test_capsule_records_v0_2_signing_deferral_and_immutable_anchor() -> None:
    text = CAPSULE.read_text(encoding="utf-8")
    assert "v0_2_signing_ceremony_deferred_pending_signing_authorization" in text
    assert "v0.2 remains an unsigned 41-node / 73-edge candidate" in text
    assert "5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56" in text
    assert "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c" in text


def test_phase_1239_status_and_planning_index_updated() -> None:
    status = STATUS.read_text(encoding="utf-8")
    planning = PLANNING_INDEX.read_text(encoding="utf-8")
    assert "## Phase 1239" in status
    assert "capsule_v5_50_supersedes_v5_49" in status
    assert "Phase 1239 coherence report + capsule v5.50 complete" in planning
    assert "Capsule v5.50" in planning
    assert "Phase 1240 closure gate remains SENSITIVE" in planning
