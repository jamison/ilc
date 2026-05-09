import hashlib
import os
import subprocess
from pathlib import Path

import pytest


SELFTEST_MODE = os.environ.get("ILC_PHASE_1240_GATE_SELFTEST") == "1"

SEQ_LOCK = Path("docs/specs/ilc_phase_1233_1240_sequence_lock_v0.1.md")
CDL_REGISTER = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
CAPSULE = Path("docs/specs/ilc_antigravity_context_capsule_v5.50.md")
REPORT = Path("docs/specs/ilc_coherence_report_1239_v0.1.md")
HANDOFF = Path("docs/specs/ilc_window_1233_1240_handoff_1240_v0.1.md")
WALKTHROUGH = Path("docs/phases/phase_1240_window_1233_1240_closure_gate_walkthrough.md")
STATUS = Path("docs/phases/STATUS.md")
PLANNING_INDEX = Path("docs/PLANNING_INDEX.md")

EXPECTED_DIAGNOSTIC_SHA = "5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56"
DIRTY_DIAGNOSTIC_SHA_AT_PREFLIGHT = "f3235a8f9dcc88d3544f9cacf3f78b29caf17d50686dd46611783c225f0eff3a"
GENESIS_V0_1_HASH = "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"
DIAGNOSTIC_PATH = "out/genesis_compile_coverage_diagnostic_v0.1.json"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _cdl_087_row() -> str:
    for line in _read(CDL_REGISTER).splitlines():
        if line.startswith("| CDL-087 |"):
            return line
    raise AssertionError("CDL-087 row not found")


def _git_show_head_bytes(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"HEAD:{path}"])


def test_cat0_selftest_env_required() -> None:
    if not SELFTEST_MODE:
        pytest.skip("ILC_PHASE_1240_GATE_SELFTEST not set - skip in regression mode")
    assert SELFTEST_MODE is True


def test_cat1_sequence_lock_and_go_token_present() -> None:
    text = _read(SEQ_LOCK) + _read(HANDOFF) + _read(WALKTHROUGH)
    assert "window_1233_1240_sequence_lock_committed" in text
    assert "GO Phase 1240" in text
    assert GENESIS_V0_1_HASH in text


def test_cat2_phase_1233_to_1239_tokens_present() -> None:
    text = _read(HANDOFF) + _read(REPORT) + _read(CAPSULE)
    for token in (
        "window_1233_1240_sequence_lock_committed",
        "commit_epoch_audit_complete_phase_1234",
        "commit_epoch_canonical_constructor_phase_1235.v0.1",
        "commit_epoch_emission_runtime_1236.v0.1",
        "phase_1236_fix6_devnet_end_to_end_harness_complete",
        "l3_sidecar_query_runtime_strike_force_complete_phase_1237",
        "phase_1237_post_fix7_sidecar_audit_hardening_complete",
        "sim_fetch_01_fix10_robustness_suite_1238j.v0.1",
        "capsule_v5_50_supersedes_v5_49",
    ):
        assert token in text


def test_cat3_closure_tokens_present() -> None:
    text = _read(HANDOFF) + _read(WALKTHROUGH)
    assert "window_1233_1240_closed_phase_1240" in text
    assert "window_1233_1240_closure_gate_verdict=pass" in text
    assert "**Status:** CLOSED" in _read(HANDOFF)


def test_cat4_no_phantom_cdl_087_ratification() -> None:
    row = _cdl_087_row().lower()
    assert "| ratified |" in row
    assert "ratified_phase: 1278 fix1" in row
    assert "phase_1240" not in row
    text = _read(HANDOFF) + _read(CAPSULE) + _read(REPORT)
    assert "OPEN / PRELOCKED / NOT RATIFIED" in text
    assert "No phantom CDL-087 ratification occurred" in text
    assert "cdl_087_candidate_envelope_identified_not_ratified_phase_1238j" in text


def test_cat5_sim_fetch_evidence_preserved_without_ratification() -> None:
    text = _read(HANDOFF) + _read(CAPSULE) + _read(REPORT)
    assert "sim_fetch_01_cdl_087_robustness_suite_committed_phase_1238j" in text
    assert "sim_fetch_01_negative_control_validated_phase_1238j" in text
    assert "sim_fetch_01_retry_and_adaptive_recovery_validated_phase_1238j" in text
    assert "does not ratify the CDL" in text


def test_cat6_commit_epoch_production_emission_still_blocked() -> None:
    text = _read(HANDOFF) + _read(CAPSULE)
    assert "commit_epoch_projection_runtime_required_before_production_emission" in text
    assert "commit_epoch_production_emission_not_yet_authorized" in text
    assert "production emission remains gated" in text or "production emission unauthorized" in text


def test_cat7_sidecar_projection_endpoint_still_blocked() -> None:
    text = _read(HANDOFF) + _read(CAPSULE)
    assert "sidecar_projection_endpoint_required_post_cdl_087_ratification" in text
    assert "sidecar_projection_endpoint_requires_transport_principal_if_non_loopback" in text
    assert "No sidecar projection endpoint or network sidecar service" in text


def test_cat8_v0_2_signing_deferred_and_genesis_hash_unchanged() -> None:
    text = _read(HANDOFF) + _read(CAPSULE)
    assert "v0_2_signing_ceremony_deferred_pending_signing_authorization" in text
    assert "v0.2 remains an unsigned 41-node / 73-edge candidate" in text
    assert GENESIS_V0_1_HASH in text


def test_cat9_committed_immutable_diagnostic_sha_matches_head() -> None:
    digest = hashlib.sha256(_git_show_head_bytes(DIAGNOSTIC_PATH)).hexdigest()
    assert digest == EXPECTED_DIAGNOSTIC_SHA
    text = _read(HANDOFF) + _read(WALKTHROUGH)
    assert EXPECTED_DIAGNOSTIC_SHA in text
    assert DIRTY_DIAGNOSTIC_SHA_AT_PREFLIGHT in text
    assert (
        "This closure does not claim working-tree generated artifact cleanliness"
        in text.replace("\n", " ")
    )


def test_cat10_public_rc_and_public_release_non_claims() -> None:
    text = _read(HANDOFF)
    for phrase in (
        "public launch",
        "public RC claim",
        "public repository publication",
        "public release artifact distribution",
        "public P2P exposure",
        "release-key generation",
        "release envelope production",
    ):
        assert phrase in text


def test_cat11_public_rc_roadmap_and_openclaw_carry_forward() -> None:
    text = _read(HANDOFF) + _read(CAPSULE)
    assert "launch_roadmap_v1_1_refresh_required_after_phase_1240" in text
    assert "public_rc_blocker_classification_required_in_roadmap_v1_1" in text
    assert "openclaw_skill_local_profile_is_preview_only" in text
    assert "openclaw_skill_claimable_profile_is_final_public_rc_target" in text
    assert "Gap 14 should run before Gap 10" in text


def test_cat12_mempalace_refresh_required_for_next_window() -> None:
    text = _read(HANDOFF)
    assert "**Disposition:** `required`" in text
    assert "**Active working set impacted:** `yes`" in text
    assert "bash tools/mempalace/build_active_working_set.sh" in text
    assert "MemPalace remains advisory" in text


def test_cat13_planning_index_updated_to_closed_window() -> None:
    text = _read(PLANNING_INDEX)
    assert "Window 1233-1240 CLOSED through Phase 1240" in text
    assert "ilc_window_1233_1240_handoff_1240_v0.1.md" in text
    assert "Window 1273-1280 CLOSED / PASS through Phase 1280" in text
    assert "Capsule v5.50" in text


def test_cat14_status_records_phase_1240_closure() -> None:
    text = _read(STATUS)
    assert "## Phase 1240" in text
    assert "window_1233_1240_closed_phase_1240" in text
    assert "window_1233_1240_closure_gate_verdict=pass" in text
    assert "Window 1273-1280 CLOSED / PASS through Phase 1280" in _read(PLANNING_INDEX)


def test_cat15_no_window_1241_sequence_lock_opened() -> None:
    text = _read(HANDOFF) + _read(PLANNING_INDEX)
    assert "No Window 1241+ phase is opened here" in text
    assert "Window 1273-1280 CLOSED / PASS through Phase 1280" in text
    assert "window_1273_1280_sequence_lock_committed" in text
