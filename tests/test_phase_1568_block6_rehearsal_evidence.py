"""Phase 1568 Block 6 private rehearsal evidence checks."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NAMESPACE = "block6_rehearsal_2026_06_27_v0_1"
REQUIRED_TOKENS = {
    "block6_private_rehearsal_executed_phase_1568",
    "accelerated_epoch_lane_rehearsal_pass_phase_1568",
    "wall_clock_soak_lane_evidence_committed_phase_1568",
    "openclaw_harness_lane_rehearsal_pass_phase_1568",
    "codex_local_harness_lane_rehearsal_pass_phase_1568",
    "emission_round_trip_rehearsal_pass_phase_1568",
    "validator_admission_ejection_rehearsal_pass_phase_1568",
    "treasury_reward_ejected_stake_rehearsal_pass_phase_1568",
    "bundle_verification_rehearsal_pass_phase_1568",
    "bounty_accounting_rehearsal_pass_phase_1568",
    "per_agent_balance_view_confirmed_phase_1568",
    "decimal_safety_no_non_finite_leakage_phase_1568",
    "rehearsal_economics_not_production_phase_1568",
    "clawhub_not_published_phase_1568",
    "public_path_remains_blocked_phase_1568",
}


def _json(path: str) -> dict[str, object]:
    payload = json.loads((ROOT / path).read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_phase_1568_accelerated_epoch_lane_passes_with_default_off_guard() -> None:
    lane1 = _json(
        "docs/sims/ilc_block6_rehearsal_evidence_1568_lane1_accelerated_epoch_v0.1.json"
    )

    assert lane1["rehearsal_namespace_id"] == NAMESPACE
    assert lane1["epoch_batch_count"] == 100
    assert lane1["verdict"] == "pass"
    assert lane1["conservation_pass"] is True
    assert lane1["decimal_safety_pass"] is True
    assert lane1["production_emission_activated_any"] is False
    assert len(lane1["event_batch_roots"]) == 100


def test_phase_1568_harness_lane_is_private_and_namespace_local() -> None:
    lane3 = _json("docs/sims/ilc_block6_rehearsal_evidence_1568_lane3_harnesses_v0.1.json")

    assert lane3["rehearsal_namespace_id"] == NAMESPACE
    assert lane3["verdict"] == "pass"
    assert lane3["clawhub_published"] is False
    openclaw = lane3["openclaw_ilc_local_skill"]
    assert isinstance(openclaw, dict)
    assert openclaw["eligible"] is True
    assert openclaw["command_visible"] is True
    codex_harness = lane3["codex_local_harness"]
    assert isinstance(codex_harness, dict)
    assert codex_harness["rehearsal_namespace_only"] is True
    assert codex_harness["private_key_access"] is False
    assert codex_harness["production_endpoint_access"] is False
    balance_checks = lane3["balance_report_checks"]
    assert isinstance(balance_checks, dict)
    assert sorted(balance_checks) == ["ilc-node-2", "ilc-node-3", "ilc-node-6"]
    assert all(check["ok"] is True for check in balance_checks.values())
    assert all(
        check["balance_status"] == "not_settled_no_ledger_write"
        for check in balance_checks.values()
    )


def test_phase_1568_aggregate_evidence_preserves_non_authorization_boundary() -> None:
    evidence = _json("docs/sims/ilc_block6_rehearsal_evidence_1568_v0.1.json")

    assert evidence["rehearsal_namespace_id"] == NAMESPACE
    assert evidence["phase"] == "1568"
    assert evidence["decimal_safety_no_non_finite_leakage"] is True
    assert evidence["rehearsal_economics_not_production"] is True
    assert evidence["lane2"]["multi_day_soak_complete"] is False
    assert set(evidence["lane3"]["balance_report_nodes_passed"]) == {
        "ilc-node-2",
        "ilc-node-3",
        "ilc-node-6",
    }
    guards = evidence["default_off_guards"]
    assert isinstance(guards, dict)
    assert all(guards.values())
    non_auth = evidence["non_authorization"]
    assert isinstance(non_auth, dict)
    assert not any(non_auth.values())


def test_phase_1568_obl_surface_round_trips_pass_without_activation() -> None:
    evidence = _json("docs/sims/ilc_block6_rehearsal_evidence_1568_v0.1.json")
    lane4 = evidence["lane4"]
    assert isinstance(lane4, dict)

    expected_surfaces = {
        "bounty_accounting",
        "bundle_verification",
        "ejected_stake_distribution",
        "emission_round_trip",
        "treasury_validator_reward",
        "validator_admission_ejection",
    }
    assert set(lane4) == expected_surfaces
    assert all(surface["verdict"] == "pass" for surface in lane4.values())
    assert lane4["bundle_verification"]["layer_count"] == 4
    assert lane4["emission_round_trip"]["production_emission_activated_any"] is False
    assert (
        lane4["validator_admission_ejection"]["production_validator_admission_activated"]
        is False
    )
    assert (
        lane4["treasury_validator_reward"]["production_treasury_distribution_activated"]
        is False
    )
    assert (
        lane4["ejected_stake_distribution"][
            "production_ejected_stake_distribution_activated"
        ]
        is False
    )
    assert lane4["bounty_accounting"]["production_bounty_activated"] is False


def test_phase_1568_status_tokens_are_present() -> None:
    status = (ROOT / "docs/phases/STATUS.md").read_text(encoding="utf-8")

    missing = sorted(token for token in REQUIRED_TOKENS if token not in status)
    assert missing == []
