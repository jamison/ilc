from __future__ import annotations

from pathlib import Path


SPEC = Path("docs/specs/ilc_phase_1236_fix1_commit_epoch_full_emission_connector_spec_v0.1.md")


def _text() -> str:
    assert SPEC.exists()
    return SPEC.read_text()


def test_fix1_spec_exists_and_has_token():
    text = _text()

    assert "phase_1236_fix1_commit_epoch_full_connector_spec_committed" in text
    assert "commit_epoch_projection_runtime_required_before_production_emission" in text


def test_fix1_spec_defines_all_connector_layers():
    text = _text()

    for marker in (
        "Layer A — Canonical Event Builder",
        "Layer B — Quorum-Proof Projection Builder",
        "Layer C — Causal-Frontier Projection Builder",
        "Layer D — Consensus-State Adapter",
        "Layer E — Test/Devnet Emission Harness",
        "Layer F — Production Consensus Emission",
    ):
        assert marker in text


def test_fix1_spec_names_cross_layer_consensus_sources():
    text = _text()

    for marker in (
        "EpochSettlementRecord",
        "EpochCheckpoint",
        "StoredCheckpoint",
        "EpochStore",
        "ILCAppReadService",
    ):
        assert marker in text


def test_fix1_spec_preserves_no_wall_clock_and_decimal_guards():
    text = _text()

    assert "no wall-clock timestamp is a protocol input" in text
    assert "timestamp_policy" in text
    assert "epoch_sequence_only_no_wall_clock" in text
    assert "finite non-negative `Decimal`" in text
    assert "no float compatibility path" in text


def test_fix1_spec_keeps_production_emission_gated():
    text = _text()

    assert "Production emission requires a later sensitive phase" in text
    assert "commit_epoch_production_emission_not_yet_authorized" in text
    assert "closing `commit_epoch_projection_runtime_required_before_production_emission`" in text


def test_fix1_spec_has_ordered_fixn_sequence():
    text = _text()

    for marker in (
        "| Fix1 | Full connector specification |",
        "| Fix2 | Implement Layer B quorum-proof projection builder |",
        "| Fix3 | Implement Layer C causal-frontier projection builder |",
        "| Fix4 | Implement Layer D fixture adapter from Python epoch/finality records |",
        "| Fix5 | Add Rust fixture mapping tests",
        "| Fix6 | Add devnet/test harness",
    ):
        assert marker in text


def test_fix1_spec_bans_live_consensus_writes_and_python_write_authority():
    text = _text()

    assert "Python write access to Rust consensus" in text
    assert "It must not create a Python write path into Rust consensus" in text
    assert "live consensus writing" in text
