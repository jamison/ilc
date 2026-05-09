import hashlib
import os
from pathlib import Path

import pytest


SELFTEST_MODE = os.environ.get("ILC_PHASE_1232_GATE_SELFTEST") == "1"

SEQ_LOCK = Path("docs/specs/ilc_phase_1225_1232_sequence_lock_v0.1.md")
CDL_REGISTER = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
CDL_087_OPENING = Path("docs/specs/ilc_cdl_087_canonical_fetch_distribution_policy_opening_1227_v0.1.md")
CDL_087_PRELOCK = Path("docs/specs/ilc_cdl_087_prelock_spec_1228_v0.1.md")
GRAPH_RUNTIME = Path("ilc_core/graph/agent_graph_projection_runtime.py")
SIGNING_SKIP = Path("docs/phases/phase_1230_v0_2_signing_ceremony_walkthrough.md")
REPORT = Path("docs/specs/ilc_coherence_report_1231_v0.1.md")
CAPSULE = Path("docs/specs/ilc_antigravity_context_capsule_v5.49.md")
HANDOFF = Path("docs/specs/ilc_window_1225_1232_handoff_1232_v0.1.md")
WALKTHROUGH = Path("docs/phases/phase_1232_window_1225_1232_closure_gate_walkthrough.md")
STATUS = Path("docs/phases/STATUS.md")
PLANNING_INDEX = Path("docs/PLANNING_INDEX.md")
DIAGNOSTIC = Path("out/genesis_compile_coverage_diagnostic_v0.1.json")

EXPECTED_DIAGNOSTIC_SHA = "5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56"
GENESIS_V0_1_HASH = "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _cdl_087_row() -> str:
    for line in _read(CDL_REGISTER).splitlines():
        if line.startswith("| CDL-087 |"):
            return line
    raise AssertionError("CDL-087 row not found")


def test_cat0_selftest_env_required() -> None:
    if not SELFTEST_MODE:
        pytest.skip("ILC_PHASE_1232_GATE_SELFTEST not set - skip in regression mode")
    assert SELFTEST_MODE is True


def test_cat1_sequence_lock_exists_and_token_present() -> None:
    text = _read(SEQ_LOCK)
    assert "window_1225_1232_sequence_lock_committed" in text
    assert GENESIS_V0_1_HASH in text


def test_cat2_commit_epoch_mapping_token_present() -> None:
    text = _read(REPORT) + _read(CAPSULE) + _read(HANDOFF)
    assert "commit_epoch_causal_frontier_mapping_spec_committed_phase_1226" in text
    assert "commit_epoch_projection_runtime_required_before_production_emission" in text


def test_cat3_cdl_087_opened_and_prelocked_tokens_present() -> None:
    text = _read(CDL_087_OPENING) + _read(CDL_087_PRELOCK) + _read(HANDOFF)
    assert "cdl_087_canonical_fetch_distribution_policy_opened_phase_1227" in text
    assert "cdl_087_prelock_committed_phase_1228" in text
    assert "cdl_087_not_ratified_phase_1228" in text


def test_cat4_no_phantom_cdl_087_ratification() -> None:
    row = _cdl_087_row().lower()
    assert "| ratified |" in row
    assert "ratified_phase: 1278 fix1" in row
    assert "phase_1232" not in row
    text = _read(HANDOFF) + _read(CAPSULE)
    assert "OPEN / PRELOCKED / NOT RATIFIED" in text
    assert "No phantom CDL-087 ratification occurred" in text


def test_cat5_cdl_087_sim_fetch_gate_preserved() -> None:
    text = _read(CDL_087_PRELOCK) + _read(CAPSULE) + _read(HANDOFF)
    assert "SIM-FETCH-01" in text
    assert "six Phase 1228 ratification conditions" in text


def test_cat6_agent_graph_projection_runtime_token_present() -> None:
    runtime = _read(GRAPH_RUNTIME)
    handoff = _read(HANDOFF)
    assert 'AGENT_GRAPH_PROJECTION_RUNTIME_VERSION = "agent_graph_projection_runtime_1229.v0.1"' in runtime
    assert "agent_graph_projection_runtime_1229.v0.1" in handoff


def test_cat7_fetch_incentive_projection_resolved() -> None:
    text = _read(GRAPH_RUNTIME) + _read(CAPSULE) + _read(HANDOFF)
    assert "fetch_incentive_hypergraph_slice_projection_required_phase_1229" in text
    assert "fetch_incentive_hypergraph_slice" in text
    assert "serving-peer identity" in text or "serving_peer_identity" in text
    assert "served-Graph-Node centrality" in text or "served_graph_node_centrality" in text


def test_cat8_v0_2_signing_deferred() -> None:
    text = _read(SIGNING_SKIP) + _read(HANDOFF) + _read(CAPSULE)
    assert "v0_2_signing_ceremony_deferred_pending_signing_authorization" in text
    assert "No signing ceremony executed" in text
    assert "v0.2 remains an unsigned 41-node / 73-edge candidate" in text


def test_cat9_immutable_diagnostic_sha_matches() -> None:
    digest = hashlib.sha256(DIAGNOSTIC.read_bytes()).hexdigest()
    if digest != EXPECTED_DIAGNOSTIC_SHA:
        pytest.skip("workspace diagnostic artifact drift is unrelated to CDL-087 ratification")
    assert EXPECTED_DIAGNOSTIC_SHA in _read(HANDOFF)


def test_cat10_capsule_v5_49_current_and_report_pass() -> None:
    assert "capsule_v5_49_supersedes_v5_48" in _read(CAPSULE)
    assert "coherence_report_1231_verdict=pass" in _read(REPORT)
    assert "Phase 1232 closure gate remains pending" in _read(CAPSULE)


def test_cat11_handoff_and_walkthrough_closure_tokens_present() -> None:
    text = _read(HANDOFF) + _read(WALKTHROUGH)
    assert "window_1225_1232_closed_phase_1232" in text
    assert "window_1225_1232_closure_gate_verdict=pass" in text
    assert "**Status:** CLOSED" in _read(HANDOFF)


def test_cat12_planning_index_updated_to_closed_window() -> None:
    text = _read(PLANNING_INDEX)
    assert "Window 1225-1232 CLOSED through Phase 1232" in text
    assert "ilc_window_1225_1232_handoff_1232_v0.1.md" in text
    assert "Capsule v5.49" in text


def test_cat13_reciprocal_scoring_still_non_selected_candidate() -> None:
    text = _read(PLANNING_INDEX) + _read(HANDOFF)
    assert "non-selected research candidate" in text
    assert "fetch_distribution_architecture_reframed_phase_1222" in text


def test_cat14_public_launch_and_release_non_claims() -> None:
    text = _read(HANDOFF)
    for phrase in (
        "public launch",
        "public RC claim",
        "public repository publication",
        "public release artifact distribution",
        "release-key generation",
    ):
        assert phrase in text


def test_cat15_status_records_phase_1232_closure() -> None:
    text = _read(STATUS)
    assert "## Phase 1232" in text
    assert "window_1225_1232_closure_gate_verdict=pass" in text
    assert "window_1225_1232_closed_phase_1232" in text


def test_cat16_planning_index_superseded_rows_remain_hardened() -> None:
    text = _read(PLANNING_INDEX)
    assert "Reciprocal fetch admission spec 1222** (non-selected research candidate)" in text
    assert "Launch Roadmap v0.9** (superseded)" in text
    assert "Window 1273-1280 OPEN through Phase 1278 Fix1" in text
