import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs" / "phases" / "STATUS.md"
SIM = ROOT / "out" / "genesis_authority_sim_battery_fix52_v0.1.json"
FIX51 = ROOT / "out" / "atlas_research" / "genesis_atlas_enriched_candidate_fix51.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_fix52_status_token_present() -> None:
    status = STATUS.read_text(encoding="utf-8")
    assert "fix52_authority_exclusion_verified" in status
    assert "fix52_complete" in status
    assert "public_path_remains_blocked_phase_1545p_fix52" in status


def test_fix52_sim_output_exists_and_is_not_fail() -> None:
    result = _load(SIM)
    assert result["overall_verdict"] in {"pass", "warn"}
    assert result["sim_battery_id"] == "genesis_authority_sim_battery_fix52_v0.1"


def test_fix52_suite_a_excludes_gap_nodes_from_authority_traces() -> None:
    result = _load(SIM)["authority_exclusion_result"]
    assert result["status"] == "pass"
    assert result["gap_nodes_in_authority_trace_count"] == 0
    assert result["gap_edges_in_authority_trace_count"] == 0


def test_fix52_suite_b_has_no_cycles_or_reverse_paths() -> None:
    result = _load(SIM)["fake_bridge_result"]
    assert result["status"] == "pass"
    assert result["cycle_count"] == 0
    assert result["reverse_path_count"] == 0
    assert result["path_length_violation_count"] == 0


def test_fix52_suite_e_negative_controls_all_pass() -> None:
    controls = _load(SIM)["negative_control_results"]
    assert len(controls) == 7
    assert all(control["status"] == "pass" for control in controls)
    assert all(control["actual_error_count"] > 0 for control in controls)


def test_fix52_authority_validator_passes_on_fix51_candidate() -> None:
    result = subprocess.run(
        ["python3", "tools/validate_authority_graph_invariants.py", str(FIX51)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "VALID:" in result.stdout


def test_fix52_does_not_mutate_fix51_candidate_counts() -> None:
    fix51 = _load(FIX51)
    result = _load(SIM)
    assert result["input_candidate_path"] == "out/atlas_research/genesis_atlas_enriched_candidate_fix51.json"
    assert len(fix51["nodes"]) == 15677
    assert len(fix51["edges"]) == 74887
