"""Phase 1109 — Window 1102-1109 closure gate."""

import dataclasses
import os
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

from ilc_core.economics.epoch_attribution_settle_runtime import (
    AttributionEvent,
    CDL_083_DEPENDENCY,
    CDL_HCON_02_DEPENDENCY,
    EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
    HCON02_QUORUM_FLOOR,
    HCON02_VOTE_THRESHOLD_DENOMINATOR,
    HCON02_VOTE_THRESHOLD_NUMERATOR,
    evaluate_ejected_stake_vote,
    settle_attribution_batch,
)
from ilc_core.types import EdgeType, EpochAttributionBatch


SELFTEST_MODE = os.environ.get("ILC_PHASE_1109_GATE_SELFTEST") == "1"


def _read(path: str) -> str:
    return Path(path).read_text()


def _settle_refutation(refuting_agent_id: str) -> list[tuple[str, Decimal]]:
    event = AttributionEvent(
        edge_type=EdgeType.REFUTATION,
        target_creator_id="target_creator",
        star_node_id=None,
        epoch=1,
        refuting_agent_id=refuting_agent_id,
    )
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(event)
    batch.seal()
    return settle_attribution_batch(batch, stake_map={})


def test_cat0_selftest_env_recognized():
    assert isinstance(SELFTEST_MODE, bool)


def test_cat1_sequence_lock_exists():
    assert Path("docs/specs/ilc_phase_1102_1109_sequence_lock_v0.1.md").exists()


def test_cat1_sequence_lock_tokens_present():
    content = _read("docs/specs/ilc_phase_1102_1109_sequence_lock_v0.1.md")
    assert "window_1102_1109_sequence_lock_committed_phase_1102" in content
    assert "cdl_083_q1_q5_pre_authorized_human_gate_complete" in content


def test_cat2_cdl083_spec_exists_and_ratified():
    spec = Path("docs/specs/ilc_cdl_083_h_con_02_panel_quorum_ejected_stake_opening_1103_v0.1.md")
    assert spec.exists()
    content = spec.read_text()
    assert "**Status:** RATIFIED" in content
    assert "cdl_083_ratified_phase_1105" in content


def test_cat2_cdl083_prelock_tokens_present():
    content = _read("docs/specs/ilc_cdl_083_h_con_02_panel_quorum_ejected_stake_opening_1103_v0.1.md")
    assert "cdl_083_prelock_asserts_open_at_phase_1103_commit_da10991f" in content


def test_cat2_cdl083_was_open_at_introducing_commit():
    result = subprocess.run(
        [
            "git",
            "show",
            "da10991f:docs/specs/ilc_cdl_083_h_con_02_panel_quorum_ejected_stake_opening_1103_v0.1.md",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "**Status:** OPEN" in result.stdout


def test_cat2_cdl083_log_row_ratified():
    content = _read("docs/specs/ilc_constitutional_decision_log_v0.1.md")
    assert "CDL-083" in content
    assert "ratified_phase: 1105" in content


def test_cat3_runtime_version_and_dependency_tokens():
    assert EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION == "epoch_attribution_settle_runtime_1114.v0.3"
    assert CDL_083_DEPENDENCY == "cdl_083_h_con_02_ratified_1105.v0.1"
    assert CDL_HCON_02_DEPENDENCY == "h_con_02_cdl_required_before_ejected_stake_treasury_executes"


def test_cat3_hcon02_quorum_constants():
    assert HCON02_QUORUM_FLOOR == Decimal("0.50")
    assert isinstance(HCON02_QUORUM_FLOOR, Decimal)
    assert HCON02_VOTE_THRESHOLD_NUMERATOR == 2
    assert HCON02_VOTE_THRESHOLD_DENOMINATOR == 3


def test_cat3_attribution_event_refuting_agent_field_present():
    field_names = [field.name for field in dataclasses.fields(AttributionEvent)]
    assert "refuting_agent_id" in field_names


def test_cat3_refutation_pays_refuting_agent_not_target_creator():
    payouts = _settle_refutation("X")
    assert payouts == [("X", Decimal("0.20"))]
    assert all(agent_id != "target_creator" for agent_id, _ in payouts)


def test_cat4_ejected_stake_vote_importable():
    assert callable(evaluate_ejected_stake_vote)


def test_cat4_exact_2_of_3_vote_passes():
    approved, payouts = evaluate_ejected_stake_vote(
        Decimal("100"),
        {"a": Decimal("50"), "b": Decimal("50")},
        approve_votes=2,
        participating_voters=3,
    )
    assert approved
    assert len(payouts) == 2


def test_cat4_quorum_floor_failure_returns_false_empty():
    assert evaluate_ejected_stake_vote(
        Decimal("100"),
        {"a": Decimal("25"), "b": Decimal("25"), "c": Decimal("25"), "d": Decimal("25")},
        approve_votes=1,
        participating_voters=1,
    ) == (False, [])


def test_cat4_empty_members_vote_pass_returns_empty_payouts():
    assert evaluate_ejected_stake_vote(
        Decimal("100"),
        {},
        approve_votes=2,
        participating_voters=2,
    ) == (True, [])


def test_cat4_ejected_stake_payouts_are_decimal():
    _, payouts = evaluate_ejected_stake_vote(
        Decimal("100"),
        {"a": Decimal("50"), "b": Decimal("50")},
        approve_votes=2,
        participating_voters=2,
    )
    assert payouts
    assert all(isinstance(amount, Decimal) for _, amount in payouts)


def test_cat4_audit_single_member_one_voter_hard_minimum_blocks():
    assert evaluate_ejected_stake_vote(
        Decimal("100"),
        {"a": Decimal("1")},
        approve_votes=1,
        participating_voters=1,
    ) == (False, [])


def test_cat4_audit_zero_zero_votes_fail_quorum():
    assert evaluate_ejected_stake_vote(
        Decimal("100"),
        {"a": Decimal("1")},
        approve_votes=0,
        participating_voters=0,
    ) == (False, [])


def test_cat4_audit_zero_stake_member_gets_zero_payout_entry():
    approved, payouts = evaluate_ejected_stake_vote(
        Decimal("100"),
        {"a": Decimal("0"), "b": Decimal("100")},
        approve_votes=2,
        participating_voters=2,
    )
    assert approved
    assert dict(payouts)["a"] == Decimal("0")
    assert dict(payouts)["b"] == Decimal("100")


def test_cat5_phase1107_evidence_file_exists():
    assert Path("tests/test_phase_1107_h_con_02_panel_quorum_settle.py").exists()


def test_cat5_phase1107_evidence_tests_pass():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_phase_1107_h_con_02_panel_quorum_settle.py",
            "-q",
            "--tb=short",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    combined = result.stdout + result.stderr
    assert result.returncode == 0, combined
    assert "30 passed" in combined


def test_cat6_coherence_report_1108_pass_token():
    content = _read("docs/specs/ilc_integration_coherence_report_1108_v0.1.md")
    assert "coherence_report_1108_verdict=pass" in content


def test_cat6_capsule_v534_tokens_present():
    content = _read("docs/specs/ilc_antigravity_context_capsule_v5.34.md")
    assert "capsule_v5_34_supersedes_v5_33" in content
    assert "window_1102_1109_complete" in content


def test_cat6_hypergraph_planning_alignment_tokens_present():
    content = _read("docs/research/ilc_morphogenetic_hypergraph_planning_classification_v0.1.md")
    assert "RATIFIED Phase 943" in content
    assert "CDL-083" in content


def test_cat7_window_handoff_exists_and_closure_tokens_present():
    handoff = Path("docs/specs/ilc_window_1102_1109_handoff_1109_v0.1.md")
    assert handoff.exists()
    content = handoff.read_text()
    assert "window_1102_1109_closed_phase_1109" in content
    assert "cdl_084_provenance_primary_obligation_window_1110_plus" in content
