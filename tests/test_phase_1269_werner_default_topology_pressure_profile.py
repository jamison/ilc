from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.sim.sim_fetch_01.werner_topology_pressure_profile import (
    NO_WERNER_ECU_MINTING_OR_ILC_SETTLEMENT_TOKEN,
    TOPOLOGY_PRESSURE_MODEL_WERNER_V1,
    TOPOLOGY_PRESSURE_MODEL_WERNER_V1_TOKEN,
    WERNER_DEFAULT_TOPOLOGY_PRESSURE_PROFILE_VERSION,
    WERNER_NONE_PROFILE_CONTROL_TOKEN,
    build_werner_topology_pressure_profile_config,
    export_werner_topology_pressure_profile_json,
    run_werner_topology_pressure_profile,
)


MODULE_PATH = Path("ilc_core/sim/sim_fetch_01/werner_topology_pressure_profile.py")
SPEC_PATH = Path("docs/specs/ilc_werner_default_topology_pressure_profile_1269_v0.1.md")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_1269_werner_default_topology_pressure_profile_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
ROADMAP_PATH = Path("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md")
CDL_REGISTER_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")

REQUIRED_TOKENS = (
    "werner_default_topology_pressure_profile_phase_1269.v0.1",
    "topology_pressure_model_werner_v1_profile_recorded_phase_1269",
    "werner_none_profile_control_preserved_phase_1269",
    "no_werner_ecu_minting_or_ilc_settlement_phase_1269",
)

BASE_SCENARIO: dict[str, object] = {
    "n_serving_peers": 5,
    "n_epochs": 4,
    "n_agents": 30,
    "tier_a_artifact_count": 1,
    "tier_b_artifact_count": 20,
    "tier_c_artifact_count": 1,
    "tier_a_request_rate": "0.00",
    "tier_b_request_rate": "1.00",
    "tier_c_request_rate": "0.00",
    "cache_capacity_per_peer": 50,
    "max_requests_per_epoch": 500,
    "seed": 123,
    "zipf_exponent_tier_b": "0.5",
    "directory_staleness_rate": "0",
    "tier_b_exact_holder_count_per_artifact": 3,
    "max_retry_hops": 1,
    "werner_smoothing_alpha": "0.25",
    "werner_heat_signal_threshold": 20,
    "werner_cooling_signal_threshold": 2,
    "werner_pressure_tiers": ["B", "C"],
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1269_werner_v1_profile_config_is_explicit_and_non_authorizing() -> None:
    config = build_werner_topology_pressure_profile_config(BASE_SCENARIO)

    assert config["topology_pressure_model"] == TOPOLOGY_PRESSURE_MODEL_WERNER_V1
    assert config["werner_overlay_enabled"] is True
    assert config["werner_smoothing_alpha"] == "0.25"
    assert config["werner_pressure_tiers"] == ["B", "C"]


def test_phase_1269_werner_v1_profile_run_preserves_false_economic_flags() -> None:
    payload = run_werner_topology_pressure_profile(BASE_SCENARIO)
    metrics = payload["profile_metrics"]

    assert payload["version"] == WERNER_DEFAULT_TOPOLOGY_PRESSURE_PROFILE_VERSION
    assert payload["topology_pressure_model"] == TOPOLOGY_PRESSURE_MODEL_WERNER_V1
    assert metrics["werner_overlay_enabled"] is True
    assert metrics["werner_heat_signal_count_by_tier"]["B"] > 0
    assert Decimal(metrics["werner_ecu_pressure_signal_by_tier"]["B"]) > Decimal("0")
    assert metrics["werner_ecu_pressure_mint_authorized"] is False
    assert metrics["werner_ilc_settlement_authorized"] is False
    assert payload["authorization"] == {
        "cdl_087_authorized": False,
        "ecu_mint_authorized": False,
        "ilc_settlement_authorized": False,
        "public_claimability_authorized": False,
        "runtime_policy_authorized": False,
    }
    assert payload["sim_result"]["cdl_087_ratification_authorized"] is False

    for token in REQUIRED_TOKENS:
        assert token in payload["tokens"]


def test_phase_1269_none_profile_control_is_preserved() -> None:
    payload = run_werner_topology_pressure_profile(
        BASE_SCENARIO,
        topology_pressure_model="none",
    )
    metrics = payload["profile_metrics"]

    assert payload["topology_pressure_model"] == "none"
    assert payload["profile_config"]["werner_overlay_enabled"] is False
    assert metrics["werner_overlay_enabled"] is False
    assert metrics["werner_raw_pressure_by_epoch_by_tier"]["B"] == []
    assert metrics["werner_topology_recommendation_by_tier"]["B"] == "not_evaluated"
    assert WERNER_NONE_PROFILE_CONTROL_TOKEN in payload["tokens"]


def test_phase_1269_profile_rejects_float_and_unknown_profile() -> None:
    with pytest.raises(ValueError, match="werner_profile_float_forbidden"):
        build_werner_topology_pressure_profile_config(
            {**BASE_SCENARIO, "werner_smoothing_alpha": 0.5}
        )
    with pytest.raises(ValueError, match="werner_profile_topology_pressure_model_unsupported"):
        build_werner_topology_pressure_profile_config(
            BASE_SCENARIO,
            topology_pressure_model="heat_mint",
        )


def test_phase_1269_canonical_export_is_stable_bounded_and_float_safe() -> None:
    payload = run_werner_topology_pressure_profile(BASE_SCENARIO)
    exported = export_werner_topology_pressure_profile_json(payload)

    assert exported == json.dumps(
        json.loads(exported),
        sort_keys=True,
        allow_nan=False,
        separators=(",", ":"),
    )
    assert json.loads(exported)["topology_pressure_model"] == "werner_v1"

    with pytest.raises(ValueError, match="werner_profile_float_forbidden"):
        export_werner_topology_pressure_profile_json({"bad": 1.0})
    with pytest.raises(ValueError, match="werner_profile_json_max_bytes_exceeded"):
        export_werner_topology_pressure_profile_json(payload, max_bytes=16)


def test_phase_1269_module_uses_canonical_json_and_no_runtime_policy_surface() -> None:
    source = _read(MODULE_PATH)

    assert "json.dumps(" in source
    assert "sort_keys=True" in source
    assert "allow_nan=False" in source
    for forbidden in (
        "mint_ecu(",
        "settle_ilc(",
        "wallet",
        "ThreadingHTTPServer",
        "BaseHTTPRequestHandler",
        "socket",
        "time.time",
        "datetime.now",
        "random.",
    ):
        assert forbidden not in source


def test_phase_1269_docs_status_planning_and_roadmap_record_required_tokens() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)
    planning = _read(PLANNING_INDEX_PATH)
    roadmap = _read(ROADMAP_PATH)

    for text in (spec, walkthrough, status, planning, roadmap):
        for token in REQUIRED_TOKENS:
            assert token in text

    assert "Window 1265-1272 CLOSED / PASS through Phase 1272" in planning
    assert "public_rc_remains_blocked_after_phase_1271" in roadmap
    assert "Phase 1270 - Gap 13 claimability conversion-sweeper preflight" in status
    assert "phase_1270_requires_explicit_go_gap13_claimability_preflight" in status


def test_phase_1269_records_broad_discovery_and_public_non_claims() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)
    register = _read(CDL_REGISTER_PATH)

    for text in (spec, walkthrough):
        assert "Exact-token" in text
        assert "Concept discovery" in text
        assert "Contradiction" in text
        assert "Source expansion" in text
        assert "Werner" in text
        assert "topology_pressure_model" in text
        assert "Decimal" in text
        assert "canonical JSON" in text
        assert "ECU" in text
        assert "ILC" in text
        assert "public claimability" in text

    assert TOPOLOGY_PRESSURE_MODEL_WERNER_V1_TOKEN in spec
    assert NO_WERNER_ECU_MINTING_OR_ILC_SETTLEMENT_TOKEN in spec

    cdl087_rows = [line for line in register.splitlines() if line.startswith("| CDL-087 |")]
    assert len(cdl087_rows) == 1
    assert "| ratified |" in cdl087_rows[0]
    assert "ratified_phase: 1278 Fix1" in cdl087_rows[0]


def test_phase_1269_graph_delta_is_recorded() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)

    expected = (
        "graph_delta=load_bearing_code_added:ilc_core/sim/sim_fetch_01/werner_topology_pressure_profile.py -> sim_fetch/werner",
        "graph_delta=load_bearing_spec_added:docs/specs/ilc_werner_default_topology_pressure_profile_1269_v0.1.md -> planning/werner",
        "graph_delta=support_tests_added:tests/test_phase_1269_werner_default_topology_pressure_profile.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1269_werner_default_topology_pressure_profile_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
    )
    for graph_delta in expected:
        assert graph_delta in spec
        assert graph_delta in walkthrough
        assert graph_delta in status
