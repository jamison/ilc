import json
from copy import deepcopy
from pathlib import Path

import pytest

from ilc_core.sim.sim_fetch_01.werner_topology_capture_schema import (
    CAPTURE_MODE_OPTION_A,
    CAPTURE_MODE_OPTION_B,
    NO_CDL_096_OPENING_PHASE_1506P_TOKEN,
    NO_WERNER_CAPTURE_RUN_PHASE_1506P_TOKEN,
    OBL_035_WERNER_DATA_CAPTURE_SCHEMA_TOKEN,
    PHASE_1506P_FOUR_NODE_TAILSCALE_TOPOLOGY_TOKEN,
    TOPOLOGY_SOURCE_NETWORK_LEVEL_SIMULATOR,
    WERNER_CAPTURE_OPTION_B_TOKEN,
    WERNER_CAPTURE_SCHEMA_VALIDATOR_TOKEN,
    build_option_a_network_level_fixture,
    build_option_b_live_private_testbed_fixture,
    export_werner_topology_capture_json,
    validate_werner_topology_capture_package,
)


ROOT = Path(__file__).resolve().parents[1]
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1506p_g9_werner_topology_data_capture_schema.md"
SPEC = ROOT / "docs/specs/ilc_werner_topology_data_capture_schema_1506p_v0.1.md"
REGISTER = ROOT / "docs/specs/ilc_open_obligation_register_v0.1.md"
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1505p_1514p_sequence_lock_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1506p_werner_topology_data_capture_schema_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
AGENTS = ROOT / "AGENTS.md"
MODULE = ROOT / "ilc_core/sim/sim_fetch_01/werner_topology_capture_schema.py"


def _row_for(obligation_id: str) -> str:
    for line in REGISTER.read_text().splitlines():
        if line.startswith(f"| {obligation_id} |"):
            return line
    raise AssertionError(f"missing row {obligation_id}")


def test_option_b_fixture_validates_four_node_tailscale_topology() -> None:
    fixture = build_option_b_live_private_testbed_fixture()
    summary = validate_werner_topology_capture_package(fixture)

    assert summary["capture_mode"] == CAPTURE_MODE_OPTION_B
    assert summary["topology_source"] == "live_private_testbed"
    assert summary["node_count"] == 4
    assert summary["window_count"] == 3

    node_ids = {node["node_id"] for node in fixture["nodes"]}
    assert node_ids == {"main-computer", "ilc-node-2", "ilc-node-3", "ilc-node-6"}
    assert {node["tailscale_name"] for node in fixture["nodes"]} == node_ids
    assert fixture["provenance"]["node_config_provenance"] == (
        "three_vps_plus_main_computer_tailscale_topology"
    )
    for key in ("no_public_endpoint", "no_real_ecu", "no_ilc_settlement", "no_production_key"):
        assert fixture["provenance"][key] is True

    tokens = set(fixture["tokens"])
    assert WERNER_CAPTURE_OPTION_B_TOKEN in tokens
    assert PHASE_1506P_FOUR_NODE_TAILSCALE_TOPOLOGY_TOKEN in tokens
    assert NO_WERNER_CAPTURE_RUN_PHASE_1506P_TOKEN in tokens
    assert NO_CDL_096_OPENING_PHASE_1506P_TOKEN in tokens


def test_canonical_export_is_stable_bounded_and_float_safe() -> None:
    fixture = build_option_b_live_private_testbed_fixture()
    body = export_werner_topology_capture_json(fixture)

    reparsed = json.loads(body)
    assert json.dumps(
        reparsed,
        sort_keys=True,
        allow_nan=False,
        separators=(",", ":"),
    ) == body
    assert reparsed["capture_mode"] == CAPTURE_MODE_OPTION_B

    with pytest.raises(ValueError, match="werner_capture_float_forbidden"):
        modified = deepcopy(fixture)
        modified["observation_windows"][0]["pressure_by_node"][0]["fetch_count"] = 1.5
        validate_werner_topology_capture_package(modified)

    with pytest.raises(ValueError, match="werner_capture_json_max_bytes_exceeded"):
        export_werner_topology_capture_json(fixture, max_bytes=16)


def test_validator_rejects_below_contract_and_mode_mismatch() -> None:
    fixture = build_option_b_live_private_testbed_fixture()

    too_few_windows = deepcopy(fixture)
    too_few_windows["observation_windows"] = too_few_windows["observation_windows"][:2]
    with pytest.raises(ValueError, match="werner_capture_minimum_three_windows_required"):
        validate_werner_topology_capture_package(too_few_windows)

    too_few_nodes = deepcopy(fixture)
    too_few_nodes["nodes"] = too_few_nodes["nodes"][:3]
    with pytest.raises(ValueError, match="werner_capture_minimum_four_nodes_required"):
        validate_werner_topology_capture_package(too_few_nodes)

    mode_mismatch = deepcopy(fixture)
    mode_mismatch["topology_source"] = TOPOLOGY_SOURCE_NETWORK_LEVEL_SIMULATOR
    with pytest.raises(ValueError, match="werner_capture_mode_source_mismatch"):
        validate_werner_topology_capture_package(mode_mismatch)

    missing_token = deepcopy(fixture)
    missing_token["tokens"] = [
        token for token in missing_token["tokens"] if token != WERNER_CAPTURE_OPTION_B_TOKEN
    ]
    with pytest.raises(ValueError, match=WERNER_CAPTURE_OPTION_B_TOKEN):
        validate_werner_topology_capture_package(missing_token)


def test_option_a_fixture_validates_but_is_not_selected_for_phase_1506p() -> None:
    fixture = build_option_a_network_level_fixture(node_count=4, window_count=3)
    summary = validate_werner_topology_capture_package(fixture)

    assert summary["capture_mode"] == CAPTURE_MODE_OPTION_A
    assert summary["topology_source"] == TOPOLOGY_SOURCE_NETWORK_LEVEL_SIMULATOR
    assert WERNER_CAPTURE_OPTION_B_TOKEN not in fixture["tokens"]
    assert PHASE_1506P_FOUR_NODE_TAILSCALE_TOPOLOGY_TOKEN not in fixture["tokens"]


def test_docs_status_register_record_tokens_and_nonclaims() -> None:
    texts = {
        "prompt": PROMPT.read_text(),
        "spec": SPEC.read_text(),
        "register": REGISTER.read_text(),
        "sequence_lock": SEQUENCE_LOCK.read_text(),
        "walkthrough": WALKTHROUGH.read_text(),
        "status": STATUS.read_text(),
        "planning_index": PLANNING_INDEX.read_text(),
        "agents": AGENTS.read_text(),
    }

    required_tokens = [
        OBL_035_WERNER_DATA_CAPTURE_SCHEMA_TOKEN,
        WERNER_CAPTURE_SCHEMA_VALIDATOR_TOKEN,
        WERNER_CAPTURE_OPTION_B_TOKEN,
        PHASE_1506P_FOUR_NODE_TAILSCALE_TOPOLOGY_TOKEN,
        NO_WERNER_CAPTURE_RUN_PHASE_1506P_TOKEN,
        NO_CDL_096_OPENING_PHASE_1506P_TOKEN,
    ]
    for token in required_tokens:
        assert token in texts["spec"]
        assert token in texts["walkthrough"]
        assert token in texts["status"]
        assert token in texts["sequence_lock"]

    assert "Option B" in texts["spec"]
    assert "three VPS nodes plus the main computer" in texts["walkthrough"]
    assert "GO Phase 1514p" in texts["sequence_lock"]
    # HISTORICAL_SNAPSHOT: exact current-marker cardinality is not a live invariant.
    assert texts["planning_index"].count("⬅ CURRENT") >= 1

    row_035 = _row_for("OBL-035")
    row_036 = _row_for("OBL-036")
    assert "| closed |" in row_035
    assert OBL_035_WERNER_DATA_CAPTURE_SCHEMA_TOKEN in row_035
    assert "| open |" in row_036
    assert "1507p" in row_036


def test_module_has_no_capture_or_runtime_activation_surface() -> None:
    text = MODULE.read_text()

    forbidden = [
        "import random",
        "time.time",
        "datetime.now",
        "requests.",
        "socket.",
        "mint_ecu",
        "settle_ilc",
        "ILC_CDL_MUTATION_AUTHORIZED",
        "RUST_P2P_BRIDGE_NOT_ACTIVATED = False",
    ]
    for phrase in forbidden:
        assert phrase not in text

    assert "sort_keys=True" in text
    assert "allow_nan=False" in text
    assert "PUBLIC_RC_EXCLUDE" in text
