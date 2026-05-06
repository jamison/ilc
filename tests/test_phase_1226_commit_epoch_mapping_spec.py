from pathlib import Path


SPEC = Path("docs/specs/ilc_commit_epoch_causal_frontier_mapping_spec_1226_v0.1.md")
WALKTHROUGH = Path("docs/phases/phase_1226_commit_epoch_causal_frontier_mapping_spec_walkthrough.md")
STATUS = Path("docs/phases/STATUS.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1226_spec_exists_and_token_present():
    text = _read(SPEC)

    assert "commit_epoch_causal_frontier_mapping_spec_committed_phase_1226" in text
    assert "Consumes:" in text
    assert "commit_epoch_causal_frontier_mapping_spec_required" in text


def test_phase_1226_no_wall_clock_and_no_float_invariants():
    text = _read(SPEC)

    assert "No wall-clock time" in text
    assert "datetime.now()" in text
    assert "time.time()" in text
    assert "No float economics" in text
    assert "no Python `float`" in text
    assert "no IEEE-754" in text


def test_phase_1226_agent_submission_boundary_preserved():
    text = _read(SPEC)

    assert "commit_epoch_agent_submission_rejected" in text
    assert "No agent may submit a `commit.epoch` envelope" in text
    assert "Genesis epoch-zero does not create an agent-issuer exception" in text
    assert "`AgentID` must not appear in the canonical `issuer` field" in text


def test_phase_1226_rust_bridge_sources_are_correct():
    text = _read(SPEC)

    assert "`EpochSettlementRecord` | `ilc_consensus/src/types.rs`" in text
    assert "`EpochCheckpoint` | `ilc_consensus/src/types.rs`" in text
    assert "`StoredCheckpoint` | `ilc_consensus/src/epoch_settlement.rs`" in text
    assert "`ApplicationInterface` / `ILCAppReadService`" in text
    assert "Read-only bridge to Python" in text


def test_phase_1226_subordinates_historical_drafts():
    text = _read(SPEC)

    assert "Historical Draft Files" in text
    assert "commit_epoch_event_schema_v0.1.md" in text
    assert "created_at" in text
    assert "wall-clock" in text
    assert "commit_epoch_economics_v0.1.md" in text
    assert "JSON numeric reward/stake examples" in text
    assert "not governing sources" in text


def test_phase_1226_constitutional_routing_recorded():
    text = _read(SPEC)

    assert "commit_epoch_mapping_governed_by_cdl_051_no_new_cdl_required" in text
    assert "commit_epoch_projection_runtime_required_before_production_emission" in text
    assert "This is not a request for a new constitutional act by default" in text


def test_phase_1226_fix1_uses_dag_hypergraph_frontier_cut():
    text = _read(SPEC)

    assert "canonical minimal cut of the finalized" in text
    assert "epoch-N consensus DAG/hypergraph" in text
    assert "causally" in text
    assert "covered by at least one `q ∈ Q`" in text
    assert "quorum-certificate hyperedges" in text
    assert "Causal ordering preservation" in text
    assert "structure-preserving projection property" in text


def test_phase_1226_walkthrough_and_status_advanced():
    walkthrough = _read(WALKTHROUGH)
    status = _read(STATUS)

    assert "**Status:** complete" in walkthrough
    assert "commit_epoch_causal_frontier_mapping_spec_committed_phase_1226" in walkthrough
    assert "## Phase 1226" in status
    assert "Phase 1227 — CDL-087 opening" in status
