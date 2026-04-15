from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs/specs/ilc_transport_maturity_contract_666_v0.1.md"
JSON_PATH = ROOT / "docs/specs/ilc_transport_maturity_contract_666_v0.1.json"
DECISION_LOG_PATH = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"


REQUIRED_HEADINGS = [
    "## 1. Purpose and row-9 decision rule",
    "## 2. Inherited transport posture",
    "## 3. Closure tier",
    "## 4. Stretch tier",
    "## 5. Scenario families and evidence schema",
    "## 6. Operator burden contract",
    "## 7. Broad timing bands and deferred long-tail work",
    "## 8. What this phase does not claim",
]

REQUIRED_TOKENS = [
    "row_9_target_bounded_public_participant_maturity",
    "row_9_closure_tier_and_stretch_tier_defined",
    "five_node_three_machine_minimum",
    "selected_vpn_backed_evidence_required",
    "three_clean_repetitions_plus_one_soak_run",
    "documented_manual_bootstrap_allowed_but_heroics_forbidden",
    "static_peer_registry_v1_acceptable_for_row_9",
    "dynamic_discovery_not_required_for_row_9",
    "openclaw_overlay_harness_allowed_not_required_for_transport_correctness",
    "threshold_bands_broad_not_slo_theater",
]

REQUIRED_TOP_LEVEL_KEYS = [
    "row_id",
    "target",
    "closure_tier",
    "stretch_tier",
    "topology_minimum",
    "repeatability_bar",
    "scenario_families",
    "timing_bands",
    "operator_burden",
    "deferred_long_tail",
    "openclaw_role",
]

MAIN_COMMIT_SUBJECT_TOKENS = ("phase 666", "transport maturity contract")
MAIN_PATH_SET = {
    "docs/specs/ilc_transport_maturity_contract_666_v0.1.md",
    "docs/specs/ilc_transport_maturity_contract_666_v0.1.json",
    "tests/test_phase_666_transport_maturity_contract.py",
}


def _read_contract() -> str:
    return CONTRACT_PATH.read_text(encoding="utf-8")


def _read_json_text() -> str:
    return JSON_PATH.read_text(encoding="utf-8")


def _load_json() -> dict:
    return json.loads(_read_json_text())


def _paths_for_subject_tokens(subject_tokens: tuple[str, ...]) -> set[str]:
    log = subprocess.run(
        ["git", "log", "--format=%H%x00%s"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    for line in log.stdout.splitlines():
        commit, subject = line.split("\x00", 1)
        lowered = subject.lower()
        if all(token in lowered for token in subject_tokens):
            show = subprocess.run(
                ["git", "show", "--name-only", "--format=", commit],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            return {entry.strip() for entry in show.stdout.splitlines() if entry.strip()}
    raise AssertionError(f"commit_not_found:{subject_tokens}")


def test_contract_exists_and_contains_required_headings() -> None:
    text = _read_contract()
    assert CONTRACT_PATH.exists()
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_contract_contains_required_tokens() -> None:
    text = _read_contract()
    for token in REQUIRED_TOKENS:
        assert token in text


def test_json_exists_and_is_canonical_json() -> None:
    text = _read_json_text()
    payload = _load_json()
    assert JSON_PATH.exists()
    assert json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False) == text.strip()


def test_json_contains_required_top_level_keys() -> None:
    payload = _load_json()
    for key in REQUIRED_TOP_LEVEL_KEYS:
        assert key in payload


def test_contract_sets_row9_target_to_bounded_public_participant_maturity() -> None:
    text = _read_contract()
    payload = _load_json()
    assert "bounded public-participant maturity" in text
    assert payload["target"] == "bounded_public_participant_maturity"


def test_contract_sets_five_node_three_machine_minimum_and_vpn_rule() -> None:
    text = _read_contract()
    payload = _load_json()
    assert "five nodes across three machines" in text
    assert payload["topology_minimum"]["nodes"] == 5
    assert payload["topology_minimum"]["machines"] == 3
    assert payload["topology_minimum"]["selected_vpn_backed_evidence_required"] is True


def test_contract_sets_three_clean_repetitions_plus_one_soak_run_rule() -> None:
    text = _read_contract()
    payload = _load_json()
    assert "three clean repetitions plus one soak run" in text
    assert payload["repeatability_bar"]["clean_repetitions"] == 3
    assert payload["repeatability_bar"]["soak_runs"] == 1


def test_contract_preserves_static_peer_registry_and_defers_dynamic_discovery() -> None:
    text = _read_contract()
    assert "static peer registry v1 remains acceptable for row 9" in text
    assert "dynamic discovery" in text
    assert "not required for row 9" in text


def test_contract_records_operator_burden_categories_and_forbids_heroics() -> None:
    text = _read_contract()
    payload = _load_json()
    assert "Initial curated control-plane setup" in text
    assert "Ordinary join, restart, rejoin, and fallback" in text
    assert "Pathological rescue or heroics" in text
    assert "heroics are forbidden for row-9 closure" in text
    assert payload["operator_burden"]["categories"]["heroics"]["allowed"] is False


def test_decision_log_and_ilc_core_remain_unchanged() -> None:
    subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH.relative_to(ROOT))],
        cwd=ROOT,
        check=True,
    )
    assert _paths_for_subject_tokens(MAIN_COMMIT_SUBJECT_TOKENS) == MAIN_PATH_SET
