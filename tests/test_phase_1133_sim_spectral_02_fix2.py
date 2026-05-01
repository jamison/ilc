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
