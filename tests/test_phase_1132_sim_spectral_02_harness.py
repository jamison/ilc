"""Phase 1132 — SIM-SPECTRAL-02 harness tests."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "docs/sims/sim_spectral_02/program.md"
HARNESS = ROOT / "tools/sim_spectral_02.py"


def _load_harness():
    spec = importlib.util.spec_from_file_location("sim_spectral_02", HARNESS)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_h1_program_exists_with_opening_token() -> None:
    assert PROGRAM.exists()
    assert "sim_spectral_02_program_committed" in PROGRAM.read_text(encoding="utf-8")


def test_h2_harness_is_importable() -> None:
    module = _load_harness()
    assert hasattr(module, "run_simulation")


def test_h3_harness_cli_accepts_required_arguments(tmp_path: pathlib.Path) -> None:
    output = tmp_path / "result.json"
    result = subprocess.run(
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
            "5",
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.returncode == 0
    assert output.exists()


def test_h4_harness_output_has_required_json_keys(tmp_path: pathlib.Path) -> None:
    output = tmp_path / "result.json"
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
            "5",
            "--output",
            str(output),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(output.read_text(encoding="utf-8"))
    for key in {
        "scenario",
        "k",
        "seed",
        "el_x_per_epoch",
        "rolling_slope",
        "structural_impedance_per_epoch",
    }:
        assert key in data


def test_h5_compute_x_exponential_bounds() -> None:
    module = _load_harness()
    assert module.compute_x(durability=0.0, k=0.7) == 1.0
    assert 0.0 < module.compute_x(durability=10.0, k=0.7) < 1.0


def test_h6_compute_structural_impedance_is_bounded() -> None:
    module = _load_harness()
    assert module.compute_structural_impedance(lambda2=0.0, theta_floor=0.001) == 1.0
    assert module.compute_structural_impedance(lambda2=0.002, theta_floor=0.001) == 0.0
