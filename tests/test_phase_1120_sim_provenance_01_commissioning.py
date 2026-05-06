from __future__ import annotations

import importlib.util
import json
from decimal import Decimal
from pathlib import Path

from ilc_core.economics.epoch_attribution_settle_runtime import (
    AttributionEvent,
    EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
    settle_attribution_batch,
)
from ilc_core.types import (
    EdgeType,
    EpochAttributionBatch,
    PROVENANCE_DECAY_ALPHA,
    REUSE_ATTRIBUTION_RATE,
)


ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "docs/sims/sim_provenance_01/program.md"
RESULTS = ROOT / "docs/sims/sim_provenance_01/results_phase_1120_run_01.md"
HARNESS = ROOT / "tools/sim_provenance_01.py"
SUMMARY = ROOT / "out/sim_provenance_01_summary.json"
TIME_SERIES = ROOT / "out/sim_provenance_01_time_series.json"


def _load_harness():
    spec = importlib.util.spec_from_file_location("sim_provenance_01", HARNESS)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# G1 — Program artifact


def test_g1_program_exists_with_title() -> None:
    assert PROGRAM.exists()
    assert PROGRAM.read_text(encoding="utf-8").startswith(
        "# SIM-PROVENANCE-01: PROVENANCE Decay Alpha Calibration"
    )


def test_g1_program_records_cdl_084_tokens() -> None:
    text = PROGRAM.read_text(encoding="utf-8")
    assert "q2_geometric_decay_alpha_decimal_0_5_provisional" in text
    assert "q8_epoch_mint_source_sim_provenance_01_required" in text


def test_g1_program_requires_time_series_for_sim_spectral_02() -> None:
    text = PROGRAM.read_text(encoding="utf-8")
    assert "TIME SERIES" in text
    assert "SIM-SPECTRAL-02" in text


# G2 — Results artifact


def test_g2_results_exists_with_completion_token() -> None:
    assert RESULTS.exists()
    text = RESULTS.read_text(encoding="utf-8")
    assert "sim_provenance_01_results_recorded_phase_1120" in text


def test_g2_results_records_hard_metric_and_recommendation() -> None:
    text = RESULTS.read_text(encoding="utf-8")
    assert "## Hard Metric" in text
    assert "Recommended alpha for Run 01: `0.45`" in text
    assert "does not lock alpha" in text


# G3 — Harness artifact


def test_g3_harness_exists_and_imports() -> None:
    assert HARNESS.exists()
    module = _load_harness()
    assert module.N_EPOCHS == 200
    assert module.EVENTS_PER_EPOCH == 50


def test_g3_harness_exposes_expected_parameters() -> None:
    module = _load_harness()
    assert hasattr(module, "ALPHA")
    assert hasattr(module, "ALPHA_SWEEP")
    assert hasattr(module, "CHAIN_DEPTH_WEIGHTS")
    assert hasattr(module, "CREATOR_OVERLAP_RATE")


def test_g3_harness_writes_canonical_json() -> None:
    text = HARNESS.read_text(encoding="utf-8")
    assert "sort_keys=True" in text
    assert "allow_nan=False" in text


# G4 — Decimal alpha discipline


def test_g4_harness_alpha_candidates_are_decimal() -> None:
    module = _load_harness()
    assert isinstance(module.ALPHA, Decimal)
    assert all(isinstance(alpha, Decimal) for alpha in module.ALPHA_SWEEP)
    assert [str(alpha) for alpha in module.ALPHA_SWEEP] == [
        "0.3",
        "0.35",
        "0.4",
        "0.45",
        "0.5",
        "0.55",
        "0.6",
        "0.65",
        "0.7",
    ]


def test_g4_production_provenance_alpha_locked_decimal_0_45() -> None:
    assert isinstance(PROVENANCE_DECAY_ALPHA, Decimal)
    assert PROVENANCE_DECAY_ALPHA == Decimal("0.45")


# G5 — Production settlement path unchanged


def test_g5_settle_runtime_version_is_phase_1126_v0_4() -> None:
    # Originally pinned to v0.5 (epoch_attribution_settle_runtime_1129_fix1.v0.5)
    # at commissioning time. Runtime was upgraded to v0.7 in Phase 1210.
    assert (
        EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION
        == "epoch_attribution_settle_runtime_1210.v0.7"
    )


def test_g5_single_hop_provenance_payout_uses_production_alpha() -> None:
    batch = EpochAttributionBatch(epoch=1120)
    batch.add_event(
        AttributionEvent(
            edge_type=EdgeType.PROVENANCE,
            target_creator_id="target",
            star_node_id=None,
            epoch=1120,
            provenance_chain=(("node_parent", "creator_parent"),),
        )
    )
    batch.seal()
    payouts = settle_attribution_batch(batch, stake_map={})
    assert payouts == [("creator_parent", REUSE_ATTRIBUTION_RATE * PROVENANCE_DECAY_ALPHA)]


def test_g5_three_hop_provenance_decay_mapping_unchanged() -> None:
    batch = EpochAttributionBatch(epoch=1120)
    batch.add_event(
        AttributionEvent(
            edge_type=EdgeType.PROVENANCE,
            target_creator_id="target",
            star_node_id=None,
            epoch=1120,
            provenance_chain=(
                ("node_1", "creator_1"),
                ("node_2", "creator_2"),
                ("node_3", "creator_3"),
            ),
        )
    )
    batch.seal()
    assert settle_attribution_batch(batch, stake_map={}) == [
        ("creator_1", Decimal("0.0900")),
        ("creator_2", Decimal("0.040500")),
        ("creator_3", Decimal("0.01822500")),
    ]


# G6 — Machine outputs


def test_g6_summary_output_exists_with_recommendation() -> None:
    assert SUMMARY.exists()
    payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert payload["recommended_alpha"] == "0.45"
    assert payload["provisional_alpha_passes"] is True
    assert payload["provisional_alpha_keep"] is False


def test_g6_time_series_output_shape_is_node_by_epoch() -> None:
    assert TIME_SERIES.exists()
    payload = json.loads(TIME_SERIES.read_text(encoding="utf-8"))
    assert len(payload) == 100
    assert all(len(series) == 200 for series in payload.values())
    assert all(isinstance(value, int) for series in payload.values() for value in series)


# G7 — SIM-SPECTRAL-02 handoff language


def test_g7_results_records_sim_spectral_02_input_shape() -> None:
    text = RESULTS.read_text(encoding="utf-8")
    assert "SIM-SPECTRAL-02 input requirement" in text
    assert "`100` nodes × `200` epochs" in text


def test_g7_program_preserves_canon_boundary() -> None:
    text = PROGRAM.read_text(encoding="utf-8")
    assert "must not lock alpha" in text
    assert "PROVENANCE_DECAY_ALPHA" in text
    assert "remains constitutionally provisional" in text


# G8 — Guardrails and non-regression checks


def test_g8_no_predictable_prng_import_in_active_ilc_core_paths() -> None:
    violations: list[str] = []
    for path in (ROOT / "ilc_core").rglob("*.py"):
        relative = path.relative_to(ROOT)
        if "analysis" in relative.parts or "sim" in relative.parts:
            continue
        if relative.as_posix() in {
            "ilc_core/node/devnet.py",
            "ilc_core/mining/benchmark.py",
        }:
            continue
        text = path.read_text(encoding="utf-8")
        if "import random" in text or "from random import" in text:
            violations.append(relative.as_posix())
    assert violations == []


def test_g8_settlement_runtime_has_no_random_or_float_casts() -> None:
    text = (ROOT / "ilc_core/economics/epoch_attribution_settle_runtime.py").read_text(
        encoding="utf-8"
    )
    assert "import random" not in text
    assert "from random import" not in text
    assert "float(" not in text


def test_g8_server_rejects_non_finite_decimal_inputs() -> None:
    text = (ROOT / "ilc_core/server.py").read_text(encoding="utf-8")
    assert "Decimal(str(raw))" in text
    assert "amount.is_finite()" in text
    assert "non_finite" in text


def test_g8_harness_random_is_explicitly_simulation_only() -> None:
    text = HARNESS.read_text(encoding="utf-8")
    assert "import random  # simulation-only PRNG" in text
    assert "not ilc_core/" in text


def test_g8_results_keep_alpha_distinct_from_constitutional_lock() -> None:
    text = RESULTS.read_text(encoding="utf-8")
    assert "SIM recommendation only" in text
    assert "does not change `PROVENANCE_DECAY_ALPHA`" in text
