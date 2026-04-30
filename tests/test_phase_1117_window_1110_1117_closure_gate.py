import os
import subprocess
import sys
from dataclasses import fields
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.economics.epoch_attribution_settle_runtime import (
    AttributionEvent,
    CDL_081_DEPENDENCY,
    CDL_083_DEPENDENCY,
    CDL_084_DEPENDENCY,
    CDL_HCON_02_DEPENDENCY,
    EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
    settle_attribution_batch,
)
from ilc_core.types import (
    CDL_084_TYPES_DEPENDENCY,
    EdgeType,
    EpochAttributionBatch,
    PROVENANCE_DECAY_ALPHA,
    PROVENANCE_MAX_DEPTH,
    REUSE_ATTRIBUTION_RATE,
)


SELFTEST_MODE = os.environ.get("ILC_PHASE_1117_GATE_SELFTEST") == "1"


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _provenance_event(chain, epoch: int = 1) -> AttributionEvent:
    return AttributionEvent(
        edge_type=EdgeType.PROVENANCE,
        target_creator_id="target_creator",
        star_node_id=None,
        epoch=epoch,
        provenance_chain=chain,
    )


def _settle_event(event: AttributionEvent):
    batch = EpochAttributionBatch(epoch=event.epoch)
    batch.add_event(event)
    batch.seal()
    return settle_attribution_batch(batch, stake_map={})


def test_cat0_selftest_env_recognized():
    assert isinstance(SELFTEST_MODE, bool)


def test_cat1_sequence_lock_file_exists():
    assert (ROOT / "docs/specs/ilc_phase_1110_1117_sequence_lock_v0.1.md").exists()


def test_cat1_sequence_lock_contains_window_and_q1_tokens():
    src = _read("docs/specs/ilc_phase_1110_1117_sequence_lock_v0.1.md")
    assert "window_1110_1117_sequence_lock_committed_phase_1110" in src
    assert "q1_provenance_triggers_ecu_caller_only_contract" in src


def test_cat1_sequence_lock_contains_float_kill_token():
    src = _read("docs/specs/ilc_phase_1110_1117_sequence_lock_v0.1.md")
    assert "q9_float_kill_decimal_literal_0_5" in src


def test_cat2_cdl_084_spec_exists_and_is_ratified():
    src = _read("docs/specs/ilc_cdl_084_provenance_chain_attribution_opening_1111_v0.1.md")
    assert "**Status:** RATIFIED" in src


def test_cat2_cdl_084_spec_contains_open_token():
    src = _read("docs/specs/ilc_cdl_084_provenance_chain_attribution_opening_1111_v0.1.md")
    assert "cdl_084_open_phase_1111" in src


def test_cat2_cdl_084_spec_contains_ratified_token():
    src = _read("docs/specs/ilc_cdl_084_provenance_chain_attribution_opening_1111_v0.1.md")
    assert "cdl_084_ratified_phase_1113" in src


def test_cat2_cdl_log_row_contains_ratified_phase_1113():
    src = _read("docs/specs/ilc_constitutional_decision_log_v0.1.md")
    row = next(line for line in src.splitlines() if line.startswith("| CDL-084 |"))
    assert "ratified_phase: 1113" in row


def test_cat2_cdl_084_evidence_spec_exists():
    assert (
        ROOT
        / "docs/specs/ilc_cdl_084_provenance_chain_attribution_ratification_evidence_1112_v0.1.md"
    ).exists()


def test_cat3_prelock_hardening_doc_exists():
    assert (ROOT / "docs/specs/ilc_cdl_084_prelock_hardening_1112_v0.1.md").exists()


def test_cat3_prelock_hardening_doc_contains_token():
    src = _read("docs/specs/ilc_cdl_084_prelock_hardening_1112_v0.1.md")
    assert "cdl_084_prelock_hardened_phase_1112" in src


def test_cat3_historical_phase_1111_commit_was_open():
    result = subprocess.run(
        [
            "git",
            "show",
            "2066f75d:docs/specs/ilc_cdl_084_provenance_chain_attribution_opening_1111_v0.1.md",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "**Status:** OPEN" in result.stdout


def test_cat4_provenance_alpha_is_decimal_not_float():
    assert PROVENANCE_DECAY_ALPHA == Decimal("0.45")
    assert isinstance(PROVENANCE_DECAY_ALPHA, Decimal)
    assert not isinstance(PROVENANCE_DECAY_ALPHA, float)


def test_cat4_provenance_max_depth_is_int_three():
    assert PROVENANCE_MAX_DEPTH == 3
    assert type(PROVENANCE_MAX_DEPTH) is int


def test_cat4_types_dependency_token_is_ratified_1113():
    assert CDL_084_TYPES_DEPENDENCY == "cdl_084_provenance_chain_attribution_ratified_1113.v0.1"


def test_cat4_runtime_dependency_token_is_ratified_1113():
    assert CDL_084_DEPENDENCY == "cdl_084_provenance_chain_attribution_ratified_1113.v0.1"
    assert CDL_081_DEPENDENCY == "cdl_081_hyperedge_ecu_attribution_ratified_943.v0.1"
    assert CDL_HCON_02_DEPENDENCY == "h_con_02_cdl_required_before_ejected_stake_treasury_executes"
    assert CDL_083_DEPENDENCY == "cdl_083_h_con_02_ratified_1105.v0.1"


def test_cat4_runtime_version_is_phase_1126_v0_4():
    assert EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION == "epoch_attribution_settle_runtime_1129_fix1.v0.5"


def test_cat4_attribution_event_has_provenance_chain_field():
    assert "provenance_chain" in {field.name for field in fields(AttributionEvent)}


def test_cat4_decimal_exponent_arithmetic_is_exact():
    assert PROVENANCE_DECAY_ALPHA**1 == Decimal("0.45")
    assert PROVENANCE_DECAY_ALPHA**2 == Decimal("0.2025")
    assert PROVENANCE_DECAY_ALPHA**3 == Decimal("0.091125")


def test_cat5_three_hop_provenance_payouts_are_geometric():
    payouts = _settle_event(
        _provenance_event((("n1", "c1"), ("n2", "c2"), ("n3", "c3")))
    )
    assert len(payouts) == 3
    assert payouts[0] == ("c1", REUSE_ATTRIBUTION_RATE * PROVENANCE_DECAY_ALPHA**1)
    assert payouts[1] == ("c2", REUSE_ATTRIBUTION_RATE * PROVENANCE_DECAY_ALPHA**2)
    assert payouts[2] == ("c3", REUSE_ATTRIBUTION_RATE * PROVENANCE_DECAY_ALPHA**3)


def test_cat5_provenance_payout_amounts_are_decimal():
    payouts = _settle_event(
        _provenance_event((("n1", "c1"), ("n2", "c2"), ("n3", "c3")))
    )
    assert all(isinstance(amount, Decimal) for _, amount in payouts)


def test_cat5_four_hop_chain_truncates_to_max_depth():
    payouts = _settle_event(
        _provenance_event((("n1", "c1"), ("n2", "c2"), ("n3", "c3"), ("n4", "c4")))
    )
    assert payouts == [
        ("c1", Decimal("0.0900")),
        ("c2", Decimal("0.040500")),
        ("c3", Decimal("0.01822500")),
    ]


def test_cat5_none_chain_raises_missing_chain_token():
    with pytest.raises(ValueError, match="provenance_event_missing_chain"):
        _settle_event(_provenance_event(None))


def test_cat5_duplicate_node_id_raises_duplicate_node_token():
    with pytest.raises(ValueError, match="provenance_chain_contains_duplicate_node_id"):
        _settle_event(_provenance_event((("n1", "c1"), ("n1", "c2"))))


def test_cat5_attestation_event_is_still_silently_ignored():
    payouts = _settle_event(
        AttributionEvent(
            edge_type=EdgeType.ATTESTATION,
            target_creator_id="target_creator",
            star_node_id=None,
            epoch=1,
        )
    )
    assert payouts == []


def test_cat5_epoch_boundary_event_is_still_silently_ignored():
    payouts = _settle_event(
        AttributionEvent(
            edge_type=EdgeType.EPOCH_BOUNDARY,
            target_creator_id="target_creator",
            star_node_id=None,
            epoch=1,
        )
    )
    assert payouts == []


def test_cat5_duplicate_creator_uses_nearest_hop_wins():
    payouts = _settle_event(
        _provenance_event((("n1", "c1"), ("n2", "c2"), ("n3", "c1")))
    )
    assert payouts == [("c1", Decimal("0.0900")), ("c2", Decimal("0.040500"))]


def test_cat6_phase_1115_evidence_test_file_exists_and_has_31_tests():
    path = ROOT / "tests/test_phase_1115_cdl_084_provenance_chain_attribution.py"
    src = path.read_text(encoding="utf-8")
    test_count = sum(1 for line in src.splitlines() if line.startswith("def test_"))
    assert test_count >= 30
    assert test_count == 31


def test_cat6_phase_1115_evidence_tests_pass_in_subprocess():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_phase_1115_cdl_084_provenance_chain_attribution.py",
            "-q",
            "--tb=short",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "31 passed" in result.stdout + result.stderr


def test_cat7_coherence_report_exists_and_has_pass_verdict():
    src = _read("docs/specs/ilc_integration_coherence_report_1116_v0.1.md")
    assert "coherence_report_1116_verdict=pass" in src


def test_cat7_capsule_v5_35_exists_and_has_supersession_token():
    src = _read("docs/specs/ilc_antigravity_context_capsule_v5.35.md")
    assert "capsule_v5_35_supersedes_v5_34" in src


def test_cat7_capsule_contains_cdl_084_ratified_token():
    src = _read("docs/specs/ilc_antigravity_context_capsule_v5.35.md")
    assert "cdl_084_ratified_phase_1113" in src


def test_cat7_capsule_contains_sim_provenance_obligation_token():
    src = _read("docs/specs/ilc_antigravity_context_capsule_v5.35.md")
    assert "sim_provenance_01_required_before_alpha_locked" in src


def test_cat7_capsule_contains_sim_spectral_sequence_token():
    src = _read("docs/specs/ilc_antigravity_context_capsule_v5.35.md")
    assert "sim_spectral_02_sequenced_after_sim_provenance_01" in src


def test_cat7_capsule_contains_sim_ecu_stability_candidate():
    src = _read("docs/specs/ilc_antigravity_context_capsule_v5.35.md")
    assert "SIM-ECU-STABILITY-01" in src


def test_cat7_hypergraph_planning_doc_contains_cdl_084_ratified_entry():
    src = _read("docs/research/ilc_morphogenetic_hypergraph_planning_classification_v0.1.md")
    assert "CDL-084" in src
    assert "RATIFIED Phase 1113" in src


def test_cat7_hypergraph_planning_doc_contains_sim_ecu_stability_candidate():
    src = _read("docs/research/ilc_morphogenetic_hypergraph_planning_classification_v0.1.md")
    assert "SIM-ECU-STABILITY-01" in src
