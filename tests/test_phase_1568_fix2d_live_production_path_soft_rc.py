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
    "live_cdl048_four_issuance_epoch_conversion_exercised_phase_1568_fix2d",
}


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_fix2d_rerun_004_records_partial_live_rehearsal_without_complete_token() -> None:
    evidence = _json(EVIDENCE)
    status_text = STATUS.read_text(encoding="utf-8")

    assert evidence["attempt_id"] == "fix2d_rerun_004"
    assert evidence["outcome"] == "partial_live_rehearsal_fail_full_fix2d"
    assert evidence["status_token"] == "phase_1568_live_rehearsal_rerun_fail_phase_1568_fix2d"
    assert "phase_1568_live_rehearsal_rerun_fail_phase_1568_fix2d" in status_text
    for token in PASS_TOKENS:
        assert token not in status_text


def test_fix2d_rerun_004_verifies_live_transport_and_root_evidence() -> None:
    evidence = _json(EVIDENCE)
    settlement = evidence["settlement_verification"]
    d2d = evidence["d2d_delivery"]

    assert evidence["stage_results"]["seven_agent_live_node_submission"] == "pass"
    assert evidence["stage_results"]["settlement_root_verification"] == "pass_four_machine_match"
    assert d2d["agent_submission_endpoint_deliveries"] == 35
    assert d2d["panel_verdict_endpoint_deliveries"] == 5
    assert d2d["ecu_claim_endpoint_deliveries"] == 5
    assert settlement["all_four_machine_roots_match"] is True
    assert {row["settlement_root_hex"] for row in settlement["remote_verified"].values()} == {
        settlement["settlement_root_hex"]
    }


def test_fix2d_rerun_004_keeps_value_writes_and_public_path_blocked() -> None:
    evidence = _json(EVIDENCE)
    economics = evidence["economics"]
    non_claims = evidence["non_claims"]

    assert economics["quote_only"] is True
    assert economics["activation_requested"] is False
    assert economics["cdl048_wallet_write_authorized"] is False
    assert economics["no_wallet_write_activated"] is True
    assert economics["no_treasury_write_activated"] is True
    assert all(value is False for value in non_claims.values())


def test_fix2d_per_agent_economics_and_traces_are_complete_for_seven_agents() -> None:
    per_agent = _json(PER_AGENT)
    traces = _json(TRACES)

    assert per_agent["claim_total_ecu"] == "2.85"
    assert len(per_agent["agents"]) == 7
    assert {row["submission_status"] for row in per_agent["agents"]} == {"accepted"}
    assert sum(1 for row in per_agent["agents"] if row["claim_kind"] == "direct") == 1
    assert sum(1 for row in per_agent["agents"] if row["claim_kind"] == "passive") == 6
    assert traces["trace_count"] == 7
    assert len(traces["traces"]) == 7


def test_fix2d_graph_delta_is_disposable_not_canonical_atlas_history() -> None:
    graph_delta = _json(GRAPH_DELTA)

    assert graph_delta["atlas_base_graph"]["canonical_value_graph_mutated"] is False
    assert graph_delta["disposable_rehearsal_graph"]["node_count"] == 7
    assert graph_delta["disposable_rehearsal_graph"]["edge_count"] == 6
    assert graph_delta["laplacian_boundary"]["settlement_use"] is False
    assert graph_delta["werner_pressure_boundary"]["settlement_use"] is False


def test_fix2d_report_and_walkthrough_record_blockers_and_nonclaims() -> None:
    report = REPORT.read_text(encoding="utf-8")
    walkthrough = WALKTHROUGH.read_text(encoding="utf-8")

    for text in (report, walkthrough):
        assert "FULL FIX2D FAIL" in text
        assert "CDL-048" in text
        assert "quote-only" in text
        assert "No public RC" in text or "does not activate public RC" in text
        assert "Genesis signing" in text
