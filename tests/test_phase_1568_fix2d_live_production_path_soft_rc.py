from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/sims/ilc_block6_live_rehearsal_1568_fix2d_evidence_v0.1.json"
PER_AGENT = ROOT / "docs/sims/ilc_block6_live_rehearsal_1568_fix2d_per_agent_economics_v0.1.json"
GRAPH_DELTA = ROOT / "docs/sims/ilc_block6_live_rehearsal_1568_fix2d_graph_delta_v0.1.json"
TRACES = ROOT / "docs/sims/ilc_block6_live_rehearsal_1568_fix2d_forward_backward_traces_v0.1.json"
REPORT = ROOT / "docs/specs/ilc_block6_live_rehearsal_1568_fix2d_report_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1568_fix2d_live_production_path_soft_rc_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"


PASS_TOKENS = {
    "phase_1568_fix2d_live_production_path_soft_rc_complete",
    "phase_1568_live_rehearsal_rerun_pass_phase_1568_fix2",
    "four_machine_live_rehearsal_executed_phase_1568_fix2d",
    "seven_agent_live_node_submission_executed_phase_1568_fix2d",
    "live_review_jury_path_exercised_phase_1568_fix2d",
    "live_ecu_claim_and_lot_creation_exercised_phase_1568_fix2d",
    "live_cdl048_four_issuance_epoch_conversion_exercised_phase_1568_fix2d",
    "live_ilc_allocation_event_and_settlement_root_verified_phase_1568_fix2d",
}


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_fix2d_records_failed_live_rehearsal_without_pass_claims() -> None:
    evidence = _json(EVIDENCE)
    status_text = STATUS.read_text(encoding="utf-8")

    assert evidence["outcome"] == "fail"
    assert evidence["status_token"] == "phase_1568_live_rehearsal_rerun_fail_phase_1568_fix2d"
    assert "phase_1568_live_rehearsal_rerun_fail_phase_1568_fix2d" in status_text
    for token in PASS_TOKENS:
        assert token not in status_text


def test_fix2d_blockers_name_signature_schema_and_quote_boundaries() -> None:
    blockers = _json(EVIDENCE)["blockers"]
    tokens = {row["token"] for row in blockers}

    assert "agent_loop_real_signature_required_for_live_rehearsal" in tokens
    assert "scenario_outsider_missing" in tokens
    assert "quote_only_or_default_off_economics_path" in tokens


def test_fix2d_per_agent_economics_are_zero_because_no_live_submission_completed() -> None:
    per_agent = _json(PER_AGENT)

    assert len(per_agent["agents"]) == 7
    assert {row["status"] for row in per_agent["agents"]} == {
        "not_submitted_due_to_signature_blocker"
    }
    assert per_agent["economics"]["ecu_claim_total"] == "0"
    assert per_agent["economics"]["settlement_root_verified"] is False


def test_fix2d_graph_delta_and_traces_do_not_invent_rehearsal_state() -> None:
    graph_delta = _json(GRAPH_DELTA)
    traces = _json(TRACES)

    assert graph_delta["disposable_rehearsal_graph"]["node_delta"] == 0
    assert graph_delta["disposable_rehearsal_graph"]["edge_delta"] == 0
    assert graph_delta["werner_pressure_boundary"]["settlement_use"] is False
    assert traces["trace_count"] == 0
    assert traces["traces"] == []


def test_fix2d_report_and_walkthrough_preserve_non_claims() -> None:
    report = REPORT.read_text(encoding="utf-8")
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")

    assert "No pass tokens are emitted" in report
    assert "Withheld: all Fix2d pass tokens" in walkthrough
    assert "No public RC, production minting, wallet mutation" in report
    assert "jury non-response penalties" in walkthrough
