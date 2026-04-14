from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "docs/specs/ilc_transport_drill_execution_report_668_v0.1.md"
METRICS_PATH = ROOT / "docs/specs/ilc_transport_drill_metrics_668_v0.1.json"
BLOCKED_RESULTS_PATH = ROOT / "out/testbed/transport_maturity/phase_668_blocked_results.json"
TEST_PATH = ROOT / "tests/test_phase_668_transport_drill_execution.py"
WALKTHROUGH_PATH = ROOT / "docs/phases/phase_668_g8_transport_drill_execution_and_failure_harvest_walkthrough.md"
STATUS_PATH = ROOT / "docs/phases/STATUS.md"
DECISION_LOG_PATH = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"


REQUIRED_HEADINGS = [
    "## 1. Purpose and execution posture",
    "## 2. Scenario matrix and environment notes",
    "## 3. Closure-tier results",
    "## 4. Stretch-tier results",
    "## 5. Failure taxonomy and operator notes",
    "## 6. Provisional maturity posture",
]

REQUIRED_TOKENS = [
    "vpn_firewall_posture_recorded_before_live_runs",
    "tier_b_three_machine_evidence_present_or_honest_gap_recorded",
    "tier_c_vpn_evidence_present_or_honest_gap_recorded",
    "push_path_boundedness_checked",
    "pull_only_heavy_payload_checked",
    "fallback_activation_checked",
    "partition_and_recovery_checked",
    "restart_and_rejoin_checked",
    "row_9_not_closed_in_668",
]

REQUIRED_SCENARIOS = [
    "bootstrap",
    "steady-state dissemination",
    "churn",
    "partition/heal/recovery",
    "HTTP/2 fallback activation",
    "restart/rejoin",
    "bounded push correctness",
    "pull-only heavy payload correctness",
]

MAIN_COMMIT_SUBJECT_TOKENS = ("phase 668", "transport drill execution report")
BACKFILL_COMMIT_SUBJECT_TOKENS = ("phase 668", "walkthrough", "backfill")
MAIN_PATH_SET = {
    "docs/specs/ilc_transport_drill_execution_report_668_v0.1.md",
    "docs/specs/ilc_transport_drill_metrics_668_v0.1.json",
    "tools/testbed/collect_transport_maturity_metrics.py",
    "tests/test_phase_668_transport_drill_execution.py",
}
BACKFILL_PATH_SET = {
    "docs/phases/phase_668_g8_transport_drill_execution_and_failure_harvest_walkthrough.md",
    "docs/phases/STATUS.md",
}


def _read_report() -> str:
    return REPORT_PATH.read_text(encoding="utf-8")


def _read_metrics_text() -> str:
    return METRICS_PATH.read_text(encoding="utf-8")


def _load_metrics() -> dict:
    return json.loads(_read_metrics_text())


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


def _current_changed_paths() -> set[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return {line[3:] for line in result.stdout.splitlines() if line.strip()}


def test_execution_report_exists_and_contains_required_headings() -> None:
    text = _read_report()
    assert REPORT_PATH.exists()
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_execution_report_contains_required_tokens() -> None:
    text = _read_report()
    for token in REQUIRED_TOKENS:
        assert token in text


def test_metrics_json_exists_and_is_canonical_json() -> None:
    text = _read_metrics_text()
    payload = _load_metrics()
    assert METRICS_PATH.exists()
    assert json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False) == text.strip()


def test_metrics_json_records_required_schema_elements() -> None:
    payload = _load_metrics()
    assert isinstance(payload.get("results"), list)
    assert payload["results"]
    sample = payload["results"][0]
    for key in (
        "topology_tier",
        "scenario_id",
        "run_id",
        "pass",
        "timing_measurements",
        "operator_intervention",
        "counts_toward",
    ):
        assert key in sample


def test_report_covers_all_required_scenario_families() -> None:
    text = _read_report()
    for scenario in REQUIRED_SCENARIOS:
        assert scenario in text


def test_report_distinguishes_closure_tier_from_stretch_tier() -> None:
    text = _read_report()
    payload = _load_metrics()
    assert "Closure-tier result summary" in text
    assert "Stretch-tier work" in text
    counts_toward = {row["counts_toward"] for row in payload["results"]}
    assert {"closure_tier", "stretch_tier"} <= counts_toward


def test_report_records_vpn_posture_and_evidence_gaps_honestly() -> None:
    text = _read_report()
    assert "ssh_agent_identity_missing:run_ssh_add ~/.ssh/id_ed25519" in text
    assert "VPN and firewall posture remained unverified" in text
    assert "honest Tier B evidence gap" in text
    assert "honest Tier C evidence gap" in text


def test_report_explicitly_preserves_row9_as_not_closed() -> None:
    text = _read_report()
    assert "row 9 remains open in this phase" in text
    assert "row_9_not_closed_in_668" in text


def test_decision_log_remains_unchanged() -> None:
    subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH.relative_to(ROOT))],
        cwd=ROOT,
        check=True,
    )


def test_main_and_backfill_commit_path_sets_obey_phase_scope() -> None:
    try:
        assert _paths_for_subject_tokens(MAIN_COMMIT_SUBJECT_TOKENS) == MAIN_PATH_SET
    except AssertionError as exc:
        if not str(exc).startswith("commit_not_found:"):
            raise
        assert _current_changed_paths() == MAIN_PATH_SET

    try:
        assert _paths_for_subject_tokens(BACKFILL_COMMIT_SUBJECT_TOKENS) == BACKFILL_PATH_SET
    except AssertionError as exc:
        if not str(exc).startswith("commit_not_found:"):
            raise
