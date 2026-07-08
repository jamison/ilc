import json
from pathlib import Path

from ilc_core.sim.sim_fetch_01.werner_capture_sim_fetch_rerun import (
    NO_CDL_096_OPENING_PHASE_1508P_TOKEN,
    NO_WERNER_FLOW_GOVERNOR_ACTIVATION_PHASE_1508P_TOKEN,
    OBL_037_WERNER_SIM_FETCH_RERUN_TOKEN,
    WERNER_CAPTURE_PACKAGE_REPLAYED_TOKEN,
    WERNER_CONDITION_1_TOPOLOGY_PRESSURE_COVERED_TOKEN,
    WERNER_ROUTED_SIM_FETCH_PASS_TOKEN,
    analyze_capture_package,
    build_sim_fetch_config_from_capture,
)
from ilc_core.sim.sim_fetch_01.werner_topology_capture_schema import (
    validate_werner_topology_capture_package,
)


ROOT = Path(__file__).resolve().parents[1]
CAPTURE = ROOT / "docs/sims/ilc_werner_topology_capture_run_1507p_v0.1.json"
RESULT = ROOT / "docs/sims/ilc_werner_sim_fetch_rerun_1508p_v0.1.json"
REPORT = ROOT / "docs/sims/ilc_werner_sim_fetch_rerun_1508p_v0.1.md"
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1508p_g9_werner_sim_fetch_rerun.md"
REGISTER = ROOT / "docs/specs/ilc_open_obligation_register_v0.1.md"
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1505p_1514p_sequence_lock_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1508p_werner_sim_fetch_rerun_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
AGENTS = ROOT / "AGENTS.md"
MODULE = ROOT / "ilc_core/sim/sim_fetch_01/werner_capture_sim_fetch_rerun.py"


def _capture() -> dict:
    return json.loads(CAPTURE.read_text())


def _result() -> dict:
    return json.loads(RESULT.read_text())


def _row_for(obligation_id: str) -> str:
    for line in REGISTER.read_text().splitlines():
        if line.startswith(f"| {obligation_id} |"):
            return line
    raise AssertionError(f"missing row {obligation_id}")


def test_capture_analysis_and_derived_config_are_bound_to_phase_1507p_package() -> None:
    capture = _capture()
    validate_werner_topology_capture_package(capture)
    analysis = analyze_capture_package(capture)
    config = build_sim_fetch_config_from_capture(capture)

    assert analysis["condition_1_package_verdict"] == "pass"
    assert analysis["node_count"] == 4
    assert analysis["window_count"] == 3
    assert analysis["total_edge_count"] == 12
    assert analysis["success_edge_count"] == 12
    assert analysis["success_rate"] == "1.000000"
    assert config["n_serving_peers"] == 4
    assert config["n_epochs"] == 3
    assert config["tier_b_artifact_count"] == 12
    assert config["werner_pressure_tiers"] == ["B"]


def test_rerun_result_records_scenario_a_with_routed_pass() -> None:
    result = _result()
    evaluation = result["sim_evaluation"]

    assert result["condition_1_outcome"] == "scenario_a_covered"
    assert result["condition_1_outcome_token"] == (
        WERNER_CONDITION_1_TOPOLOGY_PRESSURE_COVERED_TOKEN
    )
    assert evaluation["routed_sim_fetch_verdict"] == "pass"
    assert evaluation["routed_werner_pressure_pass"] is True
    assert evaluation["routed_effective_tier_ab_failure_rate"] == "0.000000"
    assert evaluation["routed_holder_hit_rate"] == "1.000000"
    assert evaluation["routed_retry_exhausted_count"] == 0
    assert evaluation["werner_ecu_pressure_mint_authorized"] is False
    assert evaluation["werner_ilc_settlement_authorized"] is False
    assert evaluation["aggregate_null_model_verdict"] == "fail"


def test_rerun_export_is_canonical_and_float_free() -> None:
    body = RESULT.read_text().strip()
    payload = json.loads(body)

    assert json.dumps(payload, sort_keys=True, allow_nan=False, separators=(",", ":")) == body

    def walk(value: object) -> None:
        assert not isinstance(value, float)
        if isinstance(value, dict):
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(payload)


def test_tokens_register_and_frontier_are_updated() -> None:
    texts = {
        "report": REPORT.read_text(),
        "prompt": PROMPT.read_text(),
        "register": REGISTER.read_text(),
        "sequence_lock": SEQUENCE_LOCK.read_text(),
        "walkthrough": WALKTHROUGH.read_text(),
        "status": STATUS.read_text(),
        "planning_index": PLANNING_INDEX.read_text(),
        "agents": AGENTS.read_text(),
    }
    tokens = [
        OBL_037_WERNER_SIM_FETCH_RERUN_TOKEN,
        WERNER_CAPTURE_PACKAGE_REPLAYED_TOKEN,
        WERNER_ROUTED_SIM_FETCH_PASS_TOKEN,
        WERNER_CONDITION_1_TOPOLOGY_PRESSURE_COVERED_TOKEN,
        NO_CDL_096_OPENING_PHASE_1508P_TOKEN,
        NO_WERNER_FLOW_GOVERNOR_ACTIVATION_PHASE_1508P_TOKEN,
    ]
    result_text = RESULT.read_text()
    for token in tokens:
        assert token in result_text
        assert token in texts["report"]
        assert token in texts["walkthrough"]
        assert token in texts["status"]
        assert token in texts["sequence_lock"]

    assert "| closed |" in _row_for("OBL-004")
    assert "| closed |" in _row_for("OBL-037")
    assert "| open |" in _row_for("OBL-038")
    assert "1509p" in _row_for("OBL-038")
    # HISTORICAL_SNAPSHOT: exact current-marker cardinality is not a live invariant.
    assert texts["planning_index"].count("⬅ CURRENT") >= 1


def test_rerun_module_preserves_private_non_authorizing_boundary() -> None:
    source = MODULE.read_text()

    forbidden = [
        "import random",
        "datetime.now",
        "time.time",
        "requests.",
        "socket.",
        "mint_ecu",
        "settle_ilc",
        "ILC_CDL_MUTATION_AUTHORIZED",
        "RUST_P2P_BRIDGE_NOT_ACTIVATED = False",
    ]
    for phrase in forbidden:
        assert phrase not in source

    assert "os.replace" in source
    assert "allow_nan=False" not in source
