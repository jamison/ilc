"""Phase 1144 — SIM-SPECTRAL-03 Genesis-seed harness tests."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "docs/sims/sim_spectral_03/program.md"
PROGRAM_DIR = ROOT / "docs/sims/sim_spectral_03"
HARNESS = ROOT / "tools/sim_spectral_02.py"
STAR_MAP = ROOT / "out/genesis_core_star_map_v0.1.json"


def test_p1_program_exists_with_phase_1144_token() -> None:
    assert PROGRAM.exists()
    assert "sim_spectral_03_program_committed_phase_1144" in PROGRAM.read_text(
        encoding="utf-8"
    )


def test_p2_sim_spectral_03_directory_exists() -> None:
    assert PROGRAM_DIR.is_dir()


def test_p3_harness_loads_signed_genesis_star_map() -> None:
    from tools.sim_spectral_02 import load_s1_star_map_topology

    laplacian, diagnostics = load_s1_star_map_topology(STAR_MAP)

    assert laplacian.shape == (32, 32)
    assert diagnostics["node_count"] == 32
    assert diagnostics["edge_count"] == 55
    assert diagnostics["source_file"].endswith("out/genesis_core_star_map_v0.1.json")


def test_p4_harness_dry_run_uses_genesis_star_map_topology(tmp_path: pathlib.Path) -> None:
    output = tmp_path / "sim_spectral_03_s1_dry_run.json"
    subprocess.run(
        [
            sys.executable,
            str(HARNESS),
            "--scenario",
            "S1",
            "--k",
            "0.7",
            "--weight-profile",
            "uniform_available",
            "--seed",
            "42",
            "--epochs",
            "3",
            "--s1-topology-file",
            str(STAR_MAP),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["node_count"] == 32
    assert data["laplacian_source"] == "genesis_star_map"
    assert data["s1_topology"] == "genesis-star-map"
    assert data["topology_diagnostics"]["edge_count"] == 55


def test_p5_star_map_topology_file_fails_closed_for_non_s1(tmp_path: pathlib.Path) -> None:
    output = tmp_path / "sim_spectral_03_s3_rejected.json"
    result = subprocess.run(
        [
            sys.executable,
            str(HARNESS),
            "--scenario",
            "S3",
            "--k",
            "0.7",
            "--weight-profile",
            "uniform_available",
            "--seed",
            "42",
            "--epochs",
            "3",
            "--s1-topology-file",
            str(STAR_MAP),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "sim_spectral_02_s1_topology_file_only_valid_for_s1" in result.stderr
