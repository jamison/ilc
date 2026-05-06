from pathlib import Path


REPORT = Path("docs/specs/ilc_coherence_report_1231_v0.1.md")
CAPSULE = Path("docs/specs/ilc_antigravity_context_capsule_v5.49.md")
STATUS = Path("docs/phases/STATUS.md")
PLANNING_INDEX = Path("docs/PLANNING_INDEX.md")


def test_phase_1231_report_exists_and_records_pass() -> None:
    text = REPORT.read_text(encoding="utf-8")
    assert "coherence_report_1231_verdict=pass" in text
    assert "commit_epoch_causal_frontier_mapping_spec_committed_phase_1226" in text
    assert "agent_graph_projection_runtime_1229.v0.1" in text


def test_capsule_v5_49_exists_and_supersedes_v5_48() -> None:
    text = CAPSULE.read_text(encoding="utf-8")
    assert "capsule_v5_49_supersedes_v5_48" in text
    assert "**Supersedes:** `docs/specs/ilc_antigravity_context_capsule_v5.48.md`" in text


def test_capsule_records_cdl_087_and_sim_fetch_gate() -> None:
    text = CAPSULE.read_text(encoding="utf-8")
    assert "CDL-087 status:" in text
    assert "OPEN / PRELOCKED / NOT RATIFIED" in text
    assert "SIM-FETCH-01" in text
    assert "cdl_087_prelock_committed_phase_1228" in text


def test_capsule_records_phase_1229_projection_runtime_and_incentive_slice() -> None:
    text = CAPSULE.read_text(encoding="utf-8")
    assert "AGENT_GRAPH_PROJECTION_RUNTIME_VERSION" in text
    assert "agent_graph_projection_runtime_1229.v0.1" in text
    assert "fetch_incentive_hypergraph_slice" in text
    assert "fetch_incentive_hypergraph_slice_projection_required_phase_1229" in text


def test_capsule_records_v0_2_signing_deferral_and_immutable_sha() -> None:
    text = CAPSULE.read_text(encoding="utf-8")
    assert "v0_2_signing_ceremony_deferred_pending_signing_authorization" in text
    assert "v0.2 remains an unsigned 41-node / 73-edge candidate" in text
    assert "5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56" in text


def test_capsule_records_mempalace_disposition() -> None:
    text = CAPSULE.read_text(encoding="utf-8")
    assert "MemPalace remains advisory-only" in text
    assert "no callable MemPalace tool is exposed" in text


def test_phase_1231_status_and_planning_index_updated() -> None:
    status = STATUS.read_text(encoding="utf-8")
    planning = PLANNING_INDEX.read_text(encoding="utf-8")
    assert "## Phase 1231" in status
    assert "capsule_v5_49_supersedes_v5_48" in status
    assert (
        "Window 1225-1232 in progress through Phase 1231" in planning
        or "Window 1225-1232 CLOSED through Phase 1232" in planning
    )
    assert "Capsule v5.49" in planning
