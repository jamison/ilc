import json
from pathlib import Path

from ilc_core.sim.sim_fetch_01.werner_topology_capture_schema import (
    CAPTURE_MODE_OPTION_B,
    validate_werner_topology_capture_package,
)
from ilc_core.sim.sim_fetch_01.werner_topology_capture_run import (
    NO_CDL_096_OPENING_PHASE_1507P_TOKEN,
    NO_WERNER_SIM_FETCH_RERUN_PHASE_1507P_TOKEN,
    OBL_036_WERNER_CAPTURE_RUN_TOKEN,
    PHASE_1507P_CURRENT_TAILSCALE_IPS_USED_TOKEN,
    PHASE_1507P_STALE_SSH_ALIASES_DETECTED_TOKEN,
    WERNER_CAPTURE_DATA_PACKAGE_TOKEN,
    WERNER_LIVE_TAILSCALE_CAPTURE_TOKEN,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/sims/ilc_werner_topology_capture_run_1507p_v0.1.json"
REPORT = ROOT / "docs/sims/ilc_werner_topology_capture_run_1507p_v0.1.md"
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1507p_g9_werner_multi_node_capture_run.md"
REGISTER = ROOT / "docs/specs/ilc_open_obligation_register_v0.1.md"
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1505p_1514p_sequence_lock_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1507p_werner_multi_node_capture_run_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
AGENTS = ROOT / "AGENTS.md"
RUNNER = ROOT / "ilc_core/sim/sim_fetch_01/werner_topology_capture_run.py"


def _payload() -> dict:
    return json.loads(DATA.read_text())


def _row_for(obligation_id: str) -> str:
    for line in REGISTER.read_text().splitlines():
        if line.startswith(f"| {obligation_id} |"):
            return line
    raise AssertionError(f"missing row {obligation_id}")


def test_capture_package_validates_against_phase_1506p_schema() -> None:
    payload = _payload()
    summary = validate_werner_topology_capture_package(payload)

    assert summary["capture_mode"] == CAPTURE_MODE_OPTION_B
    assert summary["topology_source"] == "live_private_testbed"
    assert summary["node_count"] == 4
    assert summary["window_count"] == 3
    assert payload["capture_summary"]["capture_kind"] == "live_private_tailscale_probe"
    assert payload["capture_summary"]["stale_ssh_config_aliases_detected"] is True
    assert payload["capture_summary"]["ssh_aliases_not_used"] is True


def test_capture_package_is_canonical_json_and_has_no_float_values() -> None:
    body = DATA.read_text().strip()
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


def test_capture_nodes_windows_edges_and_pressure_contract() -> None:
    payload = _payload()
    node_ids = {node["node_id"] for node in payload["nodes"]}

    assert node_ids == {"main-computer", "ilc-node-2", "ilc-node-3", "ilc-node-6"}
    assert {node["tailscale_online"] for node in payload["nodes"]} == {True}
    assert len(payload["observation_windows"]) == 3

    for window in payload["observation_windows"]:
        assert len(window["edges"]) == 4
        assert len(window["pressure_by_node"]) == 4
        assert {item["node_id"] for item in window["pressure_by_node"]} == node_ids
        assert {edge["success"] for edge in window["edges"]} == {True}
        for edge in window["edges"]:
            assert edge["transport_scope"] == "private_tailscale"
            assert edge["artifact_or_request_class"] == "tailscale_private_topology_probe"
            assert edge["edge_type"] == "fetch"


def test_phase_1507_tokens_are_recorded_across_artifacts() -> None:
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
        OBL_036_WERNER_CAPTURE_RUN_TOKEN,
        WERNER_CAPTURE_DATA_PACKAGE_TOKEN,
        WERNER_LIVE_TAILSCALE_CAPTURE_TOKEN,
        PHASE_1507P_CURRENT_TAILSCALE_IPS_USED_TOKEN,
        PHASE_1507P_STALE_SSH_ALIASES_DETECTED_TOKEN,
        NO_WERNER_SIM_FETCH_RERUN_PHASE_1507P_TOKEN,
        NO_CDL_096_OPENING_PHASE_1507P_TOKEN,
    ]
    for token in tokens:
        assert token in DATA.read_text()
        assert token in texts["report"]
        assert token in texts["walkthrough"]
        assert token in texts["status"]
        assert token in texts["sequence_lock"]

    # HISTORICAL_SNAPSHOT: exact current-marker cardinality is not a live invariant.
    assert texts["planning_index"].count("⬅ CURRENT") >= 1
    assert "| closed |" in _row_for("OBL-036")
    assert "| open |" in _row_for("OBL-037")
    assert "1508p" in _row_for("OBL-037")


def test_capture_runner_does_not_disable_ssh_or_runtime_guards() -> None:
    text = RUNNER.read_text()

    forbidden = [
        "StrictHostKeyChecking=no",
        "shell=True",
        "import random",
        "datetime.now",
        "time.time",
        "verify=False",
        "ILC_CDL_MUTATION_AUTHORIZED",
        "RUST_P2P_BRIDGE_NOT_ACTIVATED = False",
        "mint_ecu",
        "settle_ilc",
    ]
    for phrase in forbidden:
        assert phrase not in text

    assert "StrictHostKeyChecking=yes" in text
    assert "timeout=" in text
    assert "os.replace" in text
