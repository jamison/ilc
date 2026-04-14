from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs/specs/ilc_transport_harness_and_vpn_canary_pack_667_v0.1.md"
TOPOLOGY_TOOL = ROOT / "tools/testbed/render_transport_maturity_topologies.py"
CANARY_TOOL = ROOT / "tools/testbed/run_transport_maturity_canary.py"
METRICS_TOOL = ROOT / "tools/testbed/collect_transport_maturity_metrics.py"


REQUIRED_HEADINGS = [
    "## 1. Purpose and harness boundaries",
    "## 2. Topology tiers",
    "## 3. Tooling surfaces and file layout",
    "## 4. VPN and firewall posture rules",
    "## 5. Metrics and artifact flow",
    "## 6. OpenClaw overlay boundary",
]

REQUIRED_TOKENS = [
    "tier_a_local_debug_not_closure_grade",
    "tier_b_three_machine_baseline_is_closure_grade",
    "tier_c_vpn_backed_runs_are_required_where_feasible",
    "vpn_port_posture_fail_closed",
    "machine_readable_metrics_emitted_by_default",
    "openclaw_overlay_optional_not_base_dependency",
    "dynamic_discovery_not_added_in_667",
    "approved_inventory_and_explicit_promotion_preserved",
]

ALLOWED_PREFIXES = (
    "docs/specs/ilc_transport_harness_and_vpn_canary_pack_667_v0.1.md",
    "tools/testbed/",
    "tests/test_phase_667_transport_harness_and_vpn_canary_pack.py",
)


def _read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_harness_doc_exists_and_contains_required_headings() -> None:
    text = _read_doc()
    assert DOC_PATH.exists()
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_harness_doc_contains_required_tokens() -> None:
    text = _read_doc()
    for token in REQUIRED_TOKENS:
        assert token in text


def test_required_tooling_files_exist() -> None:
    assert TOPOLOGY_TOOL.exists()
    assert CANARY_TOOL.exists()
    assert METRICS_TOOL.exists()


def test_topology_tool_supports_tier_a_tier_b_and_tier_c() -> None:
    result = subprocess.run(
        ["python3", str(TOPOLOGY_TOOL), "--stdout"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert {"tier_a", "tier_b", "tier_c"} <= set(payload["topologies"])


def test_canary_runner_exposes_fail_closed_posture_for_missing_required_inputs() -> None:
    result = subprocess.run(
        ["python3", str(CANARY_TOOL), "--execute", "--allow-live"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "vpn_port_posture_fail_closed" in result.stderr


def test_metrics_collector_emits_stable_machine_readable_shape() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        (tmp_path / "sample.json").write_text(
            json.dumps(
                {
                    "results": [
                        {
                            "counts_toward": "closure_tier",
                            "notes": [],
                            "operator_intervention": [],
                            "pass": True,
                            "run_id": "sample-run",
                            "scenario_id": "bootstrap",
                            "timing_measurements": {"bootstrap_seconds": 12},
                            "topology_tier": "tier_b",
                        }
                    ]
                },
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n",
            encoding="utf-8",
        )
        output_path = tmp_path / "metrics.json"
        subprocess.run(
            ["python3", str(METRICS_TOOL), "--input", str(tmp_path), "--output", str(output_path)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        assert payload["source_count"] == 1
        assert payload["results"][0]["scenario_id"] == "bootstrap"
        assert payload["results"][0]["topology_tier"] == "tier_b"


def test_no_dynamic_discovery_claims_are_introduced_in_scoped_tooling() -> None:
    for path in (TOPOLOGY_TOOL, CANARY_TOOL, METRICS_TOOL):
        text = path.read_text(encoding="utf-8").lower()
        assert "dht" not in text
        assert "swarm" not in text
        assert "dynamic discovery" not in text


def test_base_harness_does_not_require_openclaw() -> None:
    for path in (TOPOLOGY_TOOL, CANARY_TOOL, METRICS_TOOL):
        text = path.read_text(encoding="utf-8").lower()
        assert "import openclaw" not in text
    result = subprocess.run(
        ["python3", str(CANARY_TOOL), "--plan", "closure_tier"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "openclaw" not in result.stdout.lower()


def test_discovery_admission_boundary_remains_preserved() -> None:
    text = _read_doc()
    assert "approved-inventory and explicit-promotion posture" in text
    assert "avoid any discovery-surface expansion" in text


def test_mutations_stay_within_allowed_scoped_paths() -> None:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    changed_paths = [line[3:] for line in result.stdout.splitlines() if line.strip()]
    assert changed_paths
    for path in changed_paths:
        assert path.startswith(ALLOWED_PREFIXES)
