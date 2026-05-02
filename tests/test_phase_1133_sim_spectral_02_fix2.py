"""Phase 1133 Fix2 — SIM-SPECTRAL-02 ancestor-edge topology tests."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
HARNESS = ROOT / "tools/sim_spectral_02.py"
DIAGNOSTIC = ROOT / "out/sim_spectral_02_fix2_diagnostic.json"
NOTES = ROOT / "docs/sims/sim_spectral_02/fix2_diagnostic_notes_1133.md"


def _load_diagnostic() -> list[dict[str, object]]:
    data = json.loads(DIAGNOSTIC.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    return data


def test_f1_harness_accepts_ancestor_edge_topology(tmp_path: pathlib.Path) -> None:
    output = tmp_path / "ancestor_edge.json"
    subprocess.run(
        [
            sys.executable,
            str(HARNESS),
            "--scenario",
            "S1",
            "--k",
            "0.7",
            "--weight-profile",
            "observed_provenance_only",
            "--seed",
            "42",
            "--epochs",
            "5",
            "--s1-topology",
            "ancestor-edge",
            "--s1-topology-epoch",
            "100",
            "--output",
            str(output),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["laplacian_source"] == "ancestor_edge"


def test_f2_fix2_diagnostic_exists_with_12_entries() -> None:
    assert DIAGNOSTIC.exists()
    assert len(_load_diagnostic()) == 12


def test_f3_all_diagnostic_entries_use_ancestor_edge_source() -> None:
    assert {entry["laplacian_source"] for entry in _load_diagnostic()} == {"ancestor_edge"}


def test_f4_topology_diagnostics_have_no_self_loops_and_pass_clique_guard() -> None:
    for entry in _load_diagnostic():
        diagnostics = entry["topology_diagnostics"]
        assert isinstance(diagnostics, dict)
        assert diagnostics["self_loops"] == 0
        assert diagnostics["clique_guard_ok"] is True


def test_f5_fix2_notes_exist_with_completion_token() -> None:
    assert NOTES.exists()
    assert "sim_spectral_02_fix2_diagnostic_complete_phase_1133" in NOTES.read_text(
        encoding="utf-8"
    )


def test_f6_compute_x_handles_negative_jitter_safely() -> None:
    from tools.sim_spectral_02 import compute_x

    # Normally this would raise ValueError if x > 1.0
    x_val = compute_x(-1e-15, k=1.0)
    assert 0.0 <= x_val <= 1.0
    assert x_val == 1.0


def test_f7_normalized_lambda2_yields_correct_bounds() -> None:
    import numpy as np
    from tools.sim_spectral_02 import _normalized_lambda2, compute_structural_impedance

    # Combinatorial laplacian of a 3-node ring
    L_comb = np.array(
        [
            [2.0, -1.0, -1.0],
            [-1.0, 2.0, -1.0],
            [-1.0, -1.0, 2.0],
        ]
    )

    lambda2_norm = _normalized_lambda2(L_comb)

    # Normalized laplacian lambda2 should be <= 2.0. For complete graph it's 1.5.
    assert 0.0 < lambda2_norm <= 2.0

    # Test impedance check
    impedance = compute_structural_impedance(lambda2_norm, theta_floor=0.001)
    # Since lambda2_norm is around 1.5, which is > 0.001, impedance should be 0.0
    assert impedance == 0.0


def test_f8_run_simulation_applies_greek_calibration_parameters(tmp_path: pathlib.Path) -> None:
    output_1 = tmp_path / "sim_vt_1.json"
    output_2 = tmp_path / "sim_vt_2.json"

    base_args = [
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
        "2",
        "--s1-topology",
        "synthetic",
    ]

    # Run with default alpha=1
    subprocess.run(base_args + ["--alpha", "1.0", "--output", str(output_1)], cwd=ROOT, check=True)
    data_1 = json.loads(output_1.read_text(encoding="utf-8"))
    vt_1 = data_1["v_t_per_epoch"][0]

    # Run with alpha=10
    subprocess.run(base_args + ["--alpha", "10.0", "--output", str(output_2)], cwd=ROOT, check=True)
    data_2 = json.loads(output_2.read_text(encoding="utf-8"))
    vt_2 = data_2["v_t_per_epoch"][0]

    assert vt_2 > vt_1
