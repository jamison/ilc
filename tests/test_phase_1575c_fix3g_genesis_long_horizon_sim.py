from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from decimal import Decimal
from pathlib import Path

from ilc_core.epoch.allocation_distributor_runtime import (
    GENESIS_PARTIAL_CAP_EXCESS_TO_PERFORMER_POOL_TOKEN,
)

from tools.genesis_5pct_long_horizon_production_path_sim_fix3g import (
    GENESIS_TARGET_ILC,
    HORIZON_EPOCHS,
    SCENARIO_COUNT,
    _stable_json_bytes,
    run_simulation,
)


JSON_ARTIFACT_PATH = Path(
    "docs/specs/ilc_genesis_5pct_long_horizon_production_path_sim_1575c_fix3g_v0.1.json"
)


@lru_cache(maxsize=1)
def _payload() -> dict[str, object]:
    return run_simulation()


def test_fix3g_long_horizon_sim_is_deterministic() -> None:
    first = _payload()
    second = run_simulation()

    assert first == second
    expected_hash = first["output_sha256"]
    without_hash = dict(first)
    without_hash.pop("output_sha256")
    assert hashlib.sha256(_stable_json_bytes(without_hash)).hexdigest() == expected_hash


def test_fix3g_committed_json_matches_current_replay() -> None:
    committed = json.loads(JSON_ARTIFACT_PATH.read_text(encoding="utf-8"))
    replayed = _payload()

    assert committed["canonical_constants"] == replayed["canonical_constants"]
    assert committed["current_code_findings"] == replayed["current_code_findings"]
    assert committed["scenario_grid"] == replayed["scenario_grid"]
    assert committed["summary"] == replayed["summary"]


def test_fix3g_reaches_genesis_cap_across_full_scenario_grid() -> None:
    payload = _payload()

    assert payload["scenario_grid"]["scenario_count"] == SCENARIO_COUNT
    assert len(payload["scenarios"]) == SCENARIO_COUNT
    assert payload["summary"]["all_scenarios_reach_gmax"] is True
    assert payload["summary"]["not_reached_count"] == 0
    assert payload["summary"]["p10_reach_epoch"] == 13
    assert payload["summary"]["p50_reach_epoch"] == 20
    assert payload["summary"]["p90_reach_epoch"] == 37
    assert all(1 <= row["reach_gmax_epoch"] <= HORIZON_EPOCHS for row in payload["scenarios"])
    assert {row["final_genesis_cumulative_ilc"] for row in payload["scenarios"]} == {
        format(GENESIS_TARGET_ILC.normalize(), "f")
    }


def test_fix3g_records_taper_gap_and_closed_partial_cap_route() -> None:
    payload = _payload()
    findings = payload["current_code_findings"]

    assert findings["taper_multiplier_is_reported_but_not_applied_to_pre_cap_allocation"] is True
    assert findings["partial_cap_epoch_requires_residual_routing"] is False
    assert findings["partial_cap_excess_to_performer_pool_scenario_count"] == 98

    positive_excess_rows = [
        row
        for row in payload["scenarios"]
        if Decimal(row["partial_cap_excess_to_performer_pool_ilc"]) > Decimal("0")
    ]
    assert len(positive_excess_rows) == 98
    assert all(row["partial_cap_excess_route"] == "performer_pool" for row in positive_excess_rows)
    assert all(
        row["partial_cap_excess_token"] == GENESIS_PARTIAL_CAP_EXCESS_TO_PERFORMER_POOL_TOKEN
        for row in positive_excess_rows
    )
    assert all(row["final_genesis_cumulative_ilc"] == "1296000" for row in payload["scenarios"])


def test_fix3g_cap_probe_is_fail_closed_for_every_scenario() -> None:
    payload = _payload()

    assert all(row["cap_probe_verified"] is True for row in payload["scenarios"])
    assert {row["cap_probe_genesis_overhead_ilc"] for row in payload["scenarios"]} == {"0"}
    assert all(len(row["cap_probe_root_hex"]) == 64 for row in payload["scenarios"])


def test_fix3g_records_live_authority_boundary() -> None:
    payload = _payload()
    boundary = payload["authority_boundary"]

    assert boundary["production_emission_not_activated"] is False
    assert boundary["genesis_wallet_write_authorized"] is False
    assert boundary["genesis_settlement_write_authorized"] is True
    assert boundary["genesis_minting_authorized"] is True
    assert boundary["genesis_agent1_agent_id"].startswith("c43f69fcc4dfd021")
