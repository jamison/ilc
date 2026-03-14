from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
HARDENING_PATH = Path("docs/specs/ilc_cdl_045_operational_emergency_response_prelock_hardening_404_v0.1.md")
CDL_045_OPEN_PRELOCK_402_PATH = Path("docs/specs/ilc_cdl_045_operational_emergency_response_open_prelock_402_v0.1.md")
CDL_042_HARDENING_403_PATH = Path("docs/specs/ilc_cdl_042_agent_identity_namespace_prelock_hardening_403_v0.1.md")
EXPECTED_CDL_045_ROW = (
    "| CDL-045 | CDL-V3 / CDL-V6 / CDL-V4 / SIM-005 | Operational emergency response protocol and "
    "circuit-breaker activation thresholds | open | manual governance-only emergency response with "
    "mandatory CDL-V4 review, automated circuit breaker with CDL-V3 diversity quorum trigger and CDL-V6 "
    "sunset, tiered escalation with automated rate-limit and mandatory governance confirmation | automated "
    "circuit breaker with CDL-V3 diversity quorum trigger and CDL-V6 sunset (proposed) | SIM-005 calibration "
    "anchor, CDL-V3 diversity-quorum dependency clause, CDL-V6 sunset and audit pattern, CDL-V4 mandatory "
    "post hoc review clause |"
)
PHASE_404_SUBJECT_TOKEN = "phase 404 cdl-045 operational emergency response prelock hardening"
REQUIRED_HEADINGS = (
    "## 1. Purpose and hardening scope",
    "## 2. CDL-045 current state and Phase-402 opening inheritance",
    "## 3. Candidate option discrimination",
    "## 4. Proposed candidate: automated circuit breaker with CDL-V3 quorum and CDL-V6 sunset",
    "## 5. CDL-V3 quorum dependency and invocation authorization",
    "## 6. CDL-V6 sunset obligation and CDL-V4 post hoc review requirement",
    "## 7. SIM-005 as contextual evidence and Phase 408 calibration deferral",
    "## 8. Out-of-scope and deferred tracks",
    "## 9. Canonical anchors",
)
REQUIRED_TOKENS = (
    "status: open",
    "CDL-045 prelock hardening confirms the proposed candidate: automated circuit breaker with CDL-V3 diversity quorum trigger and CDL-V6 sunset.",
    "Emergency circuit-breaker invocation requires CDL-V3 cluster diversity quorum authorization; no single-cluster operator coalition can trigger a network-wide emergency shutdown.",
    "Every circuit-breaker invocation carries an automatic CDL-V6 sunset obligation; the network cannot remain in emergency state indefinitely.",
    "Resumption of normal operation requires a positive governance action through CDL-V6 sunset review, not merely the expiry of an implicit timer.",
    "Mandatory post hoc CDL-V4 review is required after every circuit-breaker invocation; emergency status does not waive governance review.",
    "Manual governance-only emergency response is rejected because human deliberation speed may be insufficient during fast-propagating failure modes at SIM-005 stress conditions.",
    "Tiered escalation with automated rate-limit and mandatory governance confirmation is rejected because multi-tier threshold design introduces unbounded governance complexity and attack surfaces without calibrated simulation evidence for tier boundaries.",
    "SIM-005 parameters are contextual evidence for failure-mode background; circuit-breaker activation thresholds require dedicated calibration and are deferred to Phase 408 ratification.",
    "SIM-005 modeled a maximum unresolved orphan backlog rate of 0.338 under representative stress conditions; this propagation speed motivates automated response capability rather than manual-only governance deliberation.",
    "Phase 408 is the targeted CDL-045 ratification lane; this hardening artifact constitutes the primary prelock evidence.",
    "No CDL row mutation occurs in Phase 404.",
    "The Phase-397 runtime handoff confirms this dependency is computationally available in the current system: diversity-floor enforcement is deterministic, runtime-bound, and implemented as the ratified enforcement primitive for diversity-sensitive governance checks.",
)
REQUIRED_CANONICAL_ANCHORS = (
    "docs/specs/ilc_cdl_v3_quorum_diversity_ratification_evidence_332_v0.1.md",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_file_at_ref(ref: str, path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"unable_to_read_file_at_ref:{ref}:{path}:{result.stderr.strip()}")
    return result.stdout


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_404_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )

    matching: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if PHASE_404_SUBJECT_TOKEN in subject.lower():
            matching.append(commit_hash)

    required_paths = {
        str(HARDENING_PATH),
        "tests/test_phase_404_cdl_045_prelock_hardening.py",
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching:
        raise AssertionError("phase_404_commit_subject_present_but_no_hardening_artifact_commit")
    raise AssertionError("phase_404_commit_not_present_in_local_history")


def test_hardening_artifact_exists_and_contains_required_headings_and_tokens() -> None:
    assert HARDENING_PATH.exists()
    text = _read(HARDENING_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text
    for token in REQUIRED_TOKENS:
        assert token in text
    for anchor in REQUIRED_CANONICAL_ANCHORS:
        assert anchor in text


def test_cdl_045_row_remains_open_and_matches_expected_opening_row() -> None:
    # The Phase-404 `CDL-045` row is a historical prelock reference.
    historical_text = _read_file_at_ref(_resolve_phase_404_commit_ref(), str(DECISION_LOG_PATH))
    rows = parse_decision_register_rows(historical_text)
    assert rows["CDL-045"]["status"] == "open"
    assert EXPECTED_CDL_045_ROW in historical_text


def test_phase_402_opening_prelock_stub_is_preserved() -> None:
    assert CDL_045_OPEN_PRELOCK_402_PATH.exists()
    text = _read(CDL_045_OPEN_PRELOCK_402_PATH)
    assert "Phase-404 is the targeted prelock hardening lane for CDL-045." in text
    assert "status: open" in text


def test_cdl_042_and_cdl_045_register_order_preserved() -> None:
    lines = _read(DECISION_LOG_PATH).splitlines()
    cdl_044_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-044 "))
    cdl_042_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-042 "))
    cdl_045_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-045 "))
    assert cdl_042_index == cdl_044_index + 1
    assert cdl_045_index == cdl_042_index + 1


def test_cdl_045_has_no_premature_ratification_metadata() -> None:
    # The Phase-404 `CDL-045` row is a historical prelock reference.
    historical_text = _read_file_at_ref(_resolve_phase_404_commit_ref(), str(DECISION_LOG_PATH))
    rows = parse_decision_register_rows(historical_text)
    assert rows["CDL-045"]["status"] != "ratified"
    assert "ratified_phase" not in rows["CDL-045"]


def test_phase_404_commit_no_cdl_row_mutation_and_prior_artifacts_immutable() -> None:
    commit_ref = _resolve_phase_404_commit_ref()
    old_rows = parse_decision_register_rows(_read_file_at_ref(f"{commit_ref}^1", str(DECISION_LOG_PATH)))
    new_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert set(old_rows) == set(new_rows)
    for cdl_id in old_rows:
        assert old_rows[cdl_id] == new_rows[cdl_id]

    old_stub = _read_file_at_ref(f"{commit_ref}^1", str(CDL_045_OPEN_PRELOCK_402_PATH))
    new_stub = _read_file_at_ref(commit_ref, str(CDL_045_OPEN_PRELOCK_402_PATH))
    assert old_stub == new_stub, "phase_404_commit_modified_phase_402_opening_stub_unlawfully"

    old_cdl_042_hardening = _read_file_at_ref(f"{commit_ref}^1", str(CDL_042_HARDENING_403_PATH))
    new_cdl_042_hardening = _read_file_at_ref(commit_ref, str(CDL_042_HARDENING_403_PATH))
    assert (
        old_cdl_042_hardening == new_cdl_042_hardening
    ), "phase_404_commit_modified_phase_403_cdl_042_hardening_artifact_unlawfully"


def test_phase_404_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_404_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
