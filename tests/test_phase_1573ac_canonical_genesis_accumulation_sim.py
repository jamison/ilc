from __future__ import annotations

import hashlib
import json
from pathlib import Path

from simulations.sim_genesis_accumulation_canonical_1573ac import (
    SCENARIO_COUNT,
    run_simulation,
)


ARTIFACT_PATH = Path("docs/specs/ilc_genesis_accumulation_canonical_sim_1573ac_v0.1.md")
JSON_ARTIFACT_PATH = Path("docs/specs/ilc_genesis_accumulation_canonical_sim_1573ac_v0.1.json")


def _canonical_bytes(value: dict[str, object]) -> bytes:
    without_hash = dict(value)
    expected_hash = without_hash.pop("output_sha256")
    canonical = json.dumps(without_hash, sort_keys=True, separators=(",", ":")).encode("utf-8")
    assert hashlib.sha256(canonical).hexdigest() == expected_hash
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def test_phase_1573ac_deterministic_rerun_produces_identical_hash() -> None:
    first = run_simulation()
    second = run_simulation()
    committed = json.loads(JSON_ARTIFACT_PATH.read_text(encoding="utf-8"))

    assert first == second
    assert committed == first
    assert first["output_sha256"] == "47b4efc5db83916a00b1ec71e86412613b9f5801212312eaa76a333b2ecd6d2f"
    assert _canonical_bytes(first) == _canonical_bytes(second)


def test_phase_1573ac_scenario_count_matches_declared_grid() -> None:
    payload = run_simulation()

    assert payload["scenario_grid"]["scenario_count"] == SCENARIO_COUNT
    assert len(payload["scenarios"]) == SCENARIO_COUNT
    assert payload["summary"]["reach_count"] == SCENARIO_COUNT
    assert payload["summary"]["not_reached_count"] == 0


def test_phase_1573ac_p50_reach_epoch_is_in_expected_range() -> None:
    payload = run_simulation()

    assert 15 <= payload["summary"]["p50_reach_epoch"] <= 50
    assert payload["summary"]["p10_reach_epoch"] == 15
    assert payload["summary"]["p50_reach_epoch"] == 22
    assert payload["summary"]["p90_reach_epoch"] == 42


def test_phase_1573ac_no_scenario_reaches_gmax_before_epoch_one() -> None:
    payload = run_simulation()

    assert all(scenario["reach_gmax_epoch"] >= 1 for scenario in payload["scenarios"])


def test_phase_1573ac_artifact_labels_all_assumption_classes() -> None:
    text = ARTIFACT_PATH.read_text(encoding="utf-8")

    assert "Canonical" in text
    assert "Derived" in text
    assert "Exploratory" in text
    assert "issued_to_date` denominator mode is explicitly superseded" in text
    assert "not safe to present the p10/p50/p90 values as guaranteed production timelines" in text
