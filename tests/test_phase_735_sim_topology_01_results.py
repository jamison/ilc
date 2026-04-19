from __future__ import annotations

import re
import subprocess
from pathlib import Path


COMMISSION_PATH = Path("docs/specs/ilc_sim_topology_01_commissioning_711_v0.1.md")
RESULTS_PATH = Path("docs/research/ilc_sim_topology_01_results_v0.1.md")
SIM_PATH = Path("simulations/sim_topology_01_topology_shuffle_sizing.py")
REQUIRED_HEADINGS = (
    "## 1. Calibrated questions and inputs",
    "## 2. Connectivity results",
    "## 3. Privacy results (CDL-039 topology-inference boundary)",
    "## 4. Recovery timing",
    "## 5. Epoch-hash vs VRF comparison",
    "## 6. Q6 diversity metric thresholds",
    "## 7. Verdict",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_commission_brief_exists_and_contains_required_token() -> None:
    text = _read(COMMISSION_PATH)
    assert "sim_topology_01_commissioned" in text


def test_results_doc_exists() -> None:
    assert RESULTS_PATH.exists()


def test_results_doc_contains_required_headings_in_order() -> None:
    text = _read(RESULTS_PATH)
    positions = [text.index(heading) for heading in REQUIRED_HEADINGS]
    assert positions == sorted(positions)


def test_results_doc_contains_complete_and_verdict_tokens() -> None:
    text = _read(RESULTS_PATH)
    assert "sim_topology_01_results_complete" in text
    assert re.search(r"sim_topology_01_verdict=(pass|partial_complete|fail)", text)


def test_results_doc_contains_numeric_k_recommendation() -> None:
    text = _read(RESULTS_PATH)
    assert re.search(r"recommended_k_degree\s+\d+", text)


def test_results_doc_contains_numeric_distinct_cluster_floor_recommendation() -> None:
    text = _read(RESULTS_PATH)
    assert re.search(r"distinct_cluster_floor_recommendation\s+\d+", text)


def test_results_doc_contains_numeric_cluster_share_ceiling_recommendation() -> None:
    text = _read(RESULTS_PATH)
    assert re.search(r"max_cluster_share_ceiling_recommendation\s+\d+", text)


def test_results_doc_records_threshold_sweep_and_phase_710_placeholder_revision() -> None:
    text = _read(RESULTS_PATH)
    assert "Phase 710 placeholder" in text
    assert "distinct_cluster_floor=2" in text
    assert "max_cluster_share_ceiling=50" in text
    assert "distinct_cluster_floor=4" in text
    assert "max_cluster_share_ceiling=33" in text


def test_simulation_file_is_importable_with_no_side_effects() -> None:
    result = subprocess.run(
        ["python3", "-c", "import simulations.sim_topology_01_topology_shuffle_sizing"],
        capture_output=True,
        check=True,
        text=True,
    )
    assert result.stdout == ""
