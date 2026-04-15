from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = ROOT / "docs/specs/ilc_transport_hardening_and_maturity_decision_669_v0.1.md"
DECISION_LOG_PATH = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"


REQUIRED_HEADINGS = [
    "## 1. Purpose and hardening posture",
    "## 2. Failure classes addressed",
    "## 3. Changes made and why",
    "## 4. Closure-tier rerun results",
    "## 5. Maturity decision and residual risks",
    "## 6. Stretch-tier carry-forward",
]

REQUIRED_TOKENS = [
    "highest_value_failures_addressed_before_long_tail_polish",
    "row_9_closure_candidate_if_and_only_if_closure_tier_passes_after_hardening",
    "stretch_tier_findings_block_only_if_core_failure",
    "residual_risks_recorded_honestly",
    "dynamic_discovery_still_deferred_after_669",
    "openclaw_overlay_not_required_for_base_transport_correctness",
]


def _read_artifact() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def test_artifact_exists_and_contains_required_headings() -> None:
    text = _read_artifact()
    assert ARTIFACT_PATH.exists()
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_artifact_contains_required_decision_tokens() -> None:
    text = _read_artifact()
    for token in REQUIRED_TOKENS:
        assert token in text


def test_artifact_records_five_node_and_selected_443_hardening() -> None:
    text = _read_artifact()
    assert "five-node closure-tier topology extension" in text
    assert "selected `443` proof on real VPS nodes" in text
    assert "DigitalOcean VPS hosts now run one selected primary node on `TCP 443`" in text


def test_artifact_records_all_required_scenario_families_as_satisfied() -> None:
    text = _read_artifact()
    for scenario in (
        "bootstrap: satisfied",
        "steady-state dissemination: satisfied",
        "churn: satisfied",
        "partition/heal/recovery: satisfied",
        "HTTP/2 fallback activation: satisfied",
        "restart/rejoin: satisfied",
        "bounded push correctness: satisfied",
        "pull-only heavy payload correctness: satisfied",
    ):
        assert scenario in text


def test_artifact_contains_clear_row9_closure_candidate_decision() -> None:
    text = _read_artifact()
    assert "row 9 is a closure candidate for Phase 670" in text


def test_artifact_records_repeatability_soak_and_selected_tier_c_evidence() -> None:
    text = _read_artifact()
    assert "three clean closure-tier repetitions completed" in text
    assert "one soak run completed at 300 seconds" in text
    assert "selected Tier C VPN-backed realism proof" in text


def test_stretch_tier_findings_remain_non_blocking() -> None:
    text = _read_artifact()
    assert "stretch-tier work remains non-blocking" in text
    assert "no stretch-tier finding in this window invalidated the closure-tier claim" in text


def test_decision_log_remains_unchanged() -> None:
    subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH.relative_to(ROOT))],
        cwd=ROOT,
        check=True,
    )
