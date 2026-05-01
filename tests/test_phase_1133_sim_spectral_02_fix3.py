"""Phase 1133 Fix3 — SIM-SPECTRAL-02 homoiconic Genesis seed tests."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
DIAGNOSTIC = ROOT / "out/sim_spectral_02_fix3_diagnostic.json"
NOTES = ROOT / "docs/sims/sim_spectral_02/fix3_diagnostic_notes_1133.md"
HARNESS = ROOT / "tools/sim_spectral_02.py"


def _load() -> list[dict[str, object]]:
    data = json.loads(DIAGNOSTIC.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    return data


def _by_scenario() -> dict[str, dict[str, object]]:
    return {str(entry["scenario"]): entry for entry in _load()}


def test_g1_harness_accepts_homoiconic_knowledge_work_model() -> None:
    output = ROOT / "out/tmp_fix3_cli_test.json"
    try:
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
                "1",
                "--knowledge-work-model",
                "homoiconic",
                "--output",
                str(output),
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        payload = json.loads(output.read_text(encoding="utf-8"))
        assert payload["knowledge_work_model"] == "homoiconic"
    finally:
        output.unlink(missing_ok=True)


def test_g2_fix3_diagnostic_has_four_entries() -> None:
    assert DIAGNOSTIC.exists()
    assert len(_load()) == 4


def test_g3_all_entries_record_three_genesis_nodes() -> None:
    for entry in _load():
        data_classes = entry["data_classes"]
        assert isinstance(data_classes, dict)
        assert data_classes["genesis_nodes_count"] == 3


def test_g4_homoiconic_data_class_labels_are_present() -> None:
    for entry in _load():
        data_classes = entry["data_classes"]
        assert isinstance(data_classes, dict)
        assert data_classes["survived_refutations"] == "SYNTHETIC_HOMOICONIC"
        assert data_classes["reuse_count"] == "SYNTHETIC_HOMOICONIC"
        assert data_classes["validation_integrity"] == "SYNTHETIC_HOMOICONIC"


def test_g5_s1_validation_exceeds_s4_and_s3_reuse_spikes() -> None:
    entries = _by_scenario()
    s1 = entries["S1"]["knowledge_work_diagnostics"]
    s3 = entries["S3"]["knowledge_work_diagnostics"]
    s4 = entries["S4"]["knowledge_work_diagnostics"]
    assert isinstance(s1, dict)
    assert isinstance(s3, dict)
    assert isinstance(s4, dict)
    assert s1["mean_validation_integrity"] > s4["mean_validation_integrity"]
    assert s3["mean_reuse_count"] > s1["mean_reuse_count"]


def test_g6_fix3_notes_have_completion_token() -> None:
    assert NOTES.exists()
    assert "sim_spectral_02_fix3_diagnostic_complete_phase_1133" in NOTES.read_text(
        encoding="utf-8"
    )
