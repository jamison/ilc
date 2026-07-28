from __future__ import annotations

from pathlib import Path

from ilc_core.reputation.temporal_decay_runtime import CDL_V1_RUNTIME_VERSION


ROOT = Path(__file__).resolve().parents[1]
ATTESTATION = ROOT / "docs/specs/ilc_decay_bridge_audit_attestation_1577d_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PRODUCTION_BRIDGE = ROOT / "ilc_core/consensus/production_bridge.py"
ATTRIBUTION_BRIDGE = ROOT / "ilc_core/consensus/attribution_batch_bridge.py"
BALANCE_STORE = ROOT / "ilc_consensus/src/balance_store.rs"
CDL071 = ROOT / "docs/specs/ilc_cdl_071_temporal_tier_reconciliation_opening_850_v0.1.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_attestation_records_three_distinct_decay_surfaces() -> None:
    text = _read(ATTESTATION)

    assert "CDL-V1 temporal decay" in text
    assert "CDL-084 provenance decay" in text
    assert "CDL-048 anti-hoarding pressure" in text
    assert "PROVENANCE_DECAY_ALPHA" in text
    assert "mandatory ECU-to-ILC conversion" in text


def test_cdl_v1_is_reputation_decay_not_balance_demurrage() -> None:
    cdl071 = _read(CDL071)
    attestation = _read(ATTESTATION)

    assert CDL_V1_RUNTIME_VERSION == "cdl_v1_temporal_decay_runtime_388.v0.1"
    assert "Exponential half-life decay for reuse centrality reputation" in cdl071
    assert "Reputation scores (reuse centrality)" in cdl071
    assert "cdl_v1_reputation_decay_not_raw_balance_decay_confirmed_phase_1577d" in attestation


def test_python_to_rust_attribution_bridge_does_not_apply_hidden_decay() -> None:
    bridge = _read(ATTRIBUTION_BRIDGE)
    attestation = _read(ATTESTATION)

    assert "ATTRIBUTION_BATCH_BRIDGE_VERSION" in bridge
    assert "temporal_decay_runtime" not in bridge
    assert "compute_decay_multiplier" not in bridge
    assert "It performs exact Decimal validation and micro-ECU flooring, not temporal balance decay." in attestation


def test_rust_balance_store_is_commit_layer_not_economics_engine() -> None:
    balance_store = _read(BALANCE_STORE)
    production_bridge = _read(PRODUCTION_BRIDGE)
    attestation = _read(ATTESTATION)

    assert "pub fn apply_attribution(&self, batch: AttributionBatch)" in balance_store
    assert "checked_add(amount)" in balance_store
    assert "PRODUCTION_BRIDGE_ACTIVE = True" in production_bridge
    assert "PRODUCTION_BRIDGE_ACTIVATED_PHASE_1587_TOKEN" in production_bridge
    assert "rust_balance_store_commit_layer_confirmed_phase_1577d" in attestation
    assert "no_balance_demurrage_rule_added_phase_1577d" in attestation


def test_status_records_phase_completion_tokens() -> None:
    status = _read(STATUS)

    for token in (
        "decay_bridge_audit_complete_phase_1577d",
        "cdl_v1_reputation_decay_not_raw_balance_decay_confirmed_phase_1577d",
        "rust_balance_store_commit_layer_confirmed_phase_1577d",
        "no_balance_demurrage_rule_added_phase_1577d",
    ):
        assert token in status
