"""Phase 1135 Fix1 — homoiconic Run 02 rerun evidence tests."""

from __future__ import annotations

import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
RUN02 = ROOT / "out/sim_spectral_02_run02_summary.json"
FLAT_BASELINE = ROOT / "out/sim_spectral_02_run02_flat_baseline_1135.json"
NOTES = ROOT / "docs/sims/sim_spectral_02/run02_raw_notes_1135.md"


def _load(path: pathlib.Path) -> list[dict[str, object]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    return data


def test_f1_flat_baseline_is_preserved_with_333_entries() -> None:
    assert FLAT_BASELINE.exists()
    assert len(_load(FLAT_BASELINE)) == 333


def test_f2_current_run02_is_homoiconic_333_entry_matrix() -> None:
    entries = _load(RUN02)
    assert len(entries) == 333
    assert {entry["knowledge_work_model"] for entry in entries} == {"homoiconic"}


def test_f3_homoiconic_data_class_labels_present_in_current_run02() -> None:
    for entry in _load(RUN02):
        data_classes = entry["data_classes"]
        assert isinstance(data_classes, dict)
        assert data_classes["genesis_nodes_count"] == 3
        assert data_classes["reuse_count"] == "SYNTHETIC_HOMOICONIC"
        assert data_classes["validation_integrity"] == "SYNTHETIC_HOMOICONIC"


def test_f4_notes_record_homoiconic_fix1_token_and_baseline_path() -> None:
    text = NOTES.read_text(encoding="utf-8")
    assert "sim_spectral_02_run02_fix1_homoiconic_complete_phase_1135" in text
    assert "out/sim_spectral_02_run02_flat_baseline_1135.json" in text


def test_f5_notes_call_out_gaming_resistance_as_phase_1136_issue() -> None:
    text = NOTES.read_text(encoding="utf-8")
    assert "gaming resistance" in text
    assert "material gameability evidence" in text


def test_f6_notes_distinguish_genesis_exemption_from_5_percent_cap() -> None:
    text = NOTES.read_text(encoding="utf-8")
    assert "genesis_exempt = true" in text
    assert "theta_hard = 1/20 = 0.05" in text
    assert "do not cap Genesis epistemic centrality directly" in text
