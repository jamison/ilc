from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_402_413_sequence_lock_v0.1.md")
CDL_042_PRELOCK_PATH = Path("docs/specs/ilc_cdl_042_agent_identity_namespace_open_prelock_402_v0.1.md")
CDL_045_PRELOCK_PATH = Path("docs/specs/ilc_cdl_045_operational_emergency_response_open_prelock_402_v0.1.md")
PHASE_402_SUBJECT_TOKEN = "phase 402 seq lock and cdl-042 cdl-045 opening"
EXPECTED_CDL_042_ROW = (
    "| CDL-042 | ADM-003 / CDL-040 / CDL-034 / CDL-001 | Agent identity namespace and self-sovereign "
    "ID derivation | open | globally flat namespace with key-derived agent_id, domain-prefixed namespace "
    "with operator-scoped agent_id, hierarchical namespace with epoch-scoped key rotation chain | "
    "globally flat namespace with key-derived agent_id (proposed) | CDL-001 signing-key anchor, ADM-003 "
    "agent-architecture dependency clause, CDL-040 identity-envelope dependency clause, "
    "multi-agent-per-operator uniqueness constraint |"
)
EXPECTED_CDL_045_ROW = (
    "| CDL-045 | CDL-V3 / CDL-V6 / CDL-V4 / SIM-005 | Operational emergency response protocol and "
    "circuit-breaker activation thresholds | open | manual governance-only emergency response with "
    "mandatory CDL-V4 review, automated circuit breaker with CDL-V3 diversity quorum trigger and CDL-V6 "
    "sunset, tiered escalation with automated rate-limit and mandatory governance confirmation | automated "
    "circuit breaker with CDL-V3 diversity quorum trigger and CDL-V6 sunset (proposed) | SIM-005 calibration "
    "anchor, CDL-V3 diversity-quorum dependency clause, CDL-V6 sunset and audit pattern, CDL-V4 mandatory "
    "post hoc review clause |"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_402_commit_ref() -> str:
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
        if PHASE_402_SUBJECT_TOKEN in subject.lower():
            matching.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(SEQUENCE_LOCK_PATH),
        str(CDL_042_PRELOCK_PATH),
        str(CDL_045_PRELOCK_PATH),
        "tests/test_phase_402_cdl_042_and_cdl_045_opening.py",
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching:
        raise AssertionError("phase_402_commit_subject_present_but_no_constitutional_opening_commit")
    raise AssertionError("phase_402_commit_not_present_in_local_history")


def _decision_log_text_at_ref(ref: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{ref}:{DECISION_LOG_PATH}"],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"unable_to_read_decision_log_at_ref:{ref}: {result.stderr.strip()}")
    return result.stdout


def test_sequence_lock_exists_and_contains_required_headings_and_tokens() -> None:
    assert SEQUENCE_LOCK_PATH.exists()
    text = _read(SEQUENCE_LOCK_PATH)

    for heading in (
        "## 1. Window identity and scope",
        "## 2. Inputs and closure inheritance",
        "## 3. V-series carry-forward and SIM carry-forward",
        "## 4. Locked phase table (402-413)",
        "## 5. Constitutional first-action: two-CDL opening batch",
        "## 6. Sequencing constraints and dependency ordering",
        "## 7. D2e deferral, CDL-035 amendment convention, and SIM-008 gate",
        "## 8. Canonical anchors and non-goals",
    ):
        assert heading in text

    for token in (
        "Window 402-413 is the Constitutional Expansion and D2e First Block.",
        "CDL-V1, CDL-V2, CDL-V3, and CDL-V7 runtime lanes are implemented and carry forward without further V-series governance action in this window.",
        "Phase 406 is SIM-008 commissioning and is not a V-series governance or runtime slot.",
        "SIM-007 calibration is carried to Phase 405 for the CDL-035 timed_out amendment lane: recommended_orphan_timeout_epochs: 4; recommended_recovery_policy: stake_full_release.",
        "D2e Agent SDK implementation is gated on CDL-042 ratification in Phase 407 and begins in Phase 410.",
        "The CDL-035 timed_out amendment is opened in Phase 405 as a dedicated amendment row with a new sequential CDL identifier; it references CDL-035 in its related_clause and does not modify the base CDL-035 ratified row.",
        "Treasury governance CDL cluster and mandatory ECU conversion deadline CDL are explicitly deferred to Window 414+ and gated on SIM-008 commissioning in Phase 406.",
        "CDL-040, CDL-041, CDL-043, and CDL-044 are ratified; the node-schema ratification track and retention-epochs amendment are closed as of Window 392-401.",
        "Phase 402 opens CDL-042 and CDL-045 as a two-CDL opening batch.",
    ):
        assert token in text


def test_cdl_042_prelock_exists_and_contains_required_headings_and_tokens() -> None:
    assert CDL_042_PRELOCK_PATH.exists()
    text = _read(CDL_042_PRELOCK_PATH)

    for heading in (
        "## 1. Purpose and scope",
        "## 2. CDL-042 opening state",
        "## 3. Constitutional and architectural dependency anchors",
        "## 4. Self-sovereign ID derivation constraint and candidate option framing",
        "## 5. Multi-agent-per-operator uniqueness constraint",
        "## 6. D2e dependency and sequencing note",
        "## 7. Out-of-scope and deferred tracks",
        "## 8. Canonical anchors",
    ):
        assert heading in text

    for token in (
        "status: open",
        "CDL-042 opens as the agent identity namespace lane, unblocked by CDL-040, CDL-041, and CDL-043 ratification in Phases 393-395.",
        "Agent identity derivation must be deterministic from the signing key with no central registry requirement.",
        "The operator_id may be shared across many agents; agent_id must remain unique per agent.",
        "Phase-403 is the targeted prelock hardening lane for CDL-042.",
        "No runtime implementation occurs in Phase 402.",
    ):
        assert token in text


def test_cdl_045_prelock_exists_and_contains_required_headings_and_tokens() -> None:
    assert CDL_045_PRELOCK_PATH.exists()
    text = _read(CDL_045_PRELOCK_PATH)

    for heading in (
        "## 1. Purpose and scope",
        "## 2. CDL-045 opening state",
        "## 3. Constitutional dependency anchors",
        "## 4. SIM-005 calibration carry-forward",
        "## 5. Circuit-breaker quorum, sunset, and post hoc review framing",
        "## 6. Sequencing and dependency constraints",
        "## 7. Out-of-scope and deferred tracks",
        "## 8. Canonical anchors",
    ):
        assert heading in text

    for token in (
        "status: open",
        "CDL-045 opens as the operational emergency response protocol lane, authorized by SIM-005 results available since Phase 370.",
        "Emergency circuit-breaker invocation must require CDL-V3 diversity quorum and must carry a CDL-V6 automatic sunset obligation.",
        "Mandatory post hoc CDL-V4 review is required after any emergency circuit-breaker invocation.",
        "Phase-404 is the targeted prelock hardening lane for CDL-045.",
        "No runtime implementation occurs in Phase 402.",
    ):
        assert token in text


def test_decision_log_contains_exact_cdl_042_and_cdl_045_opening_rows() -> None:
    # The Phase-402 `CDL-042` and `CDL-045` rows are historical opening references.
    historical_text = _decision_log_text_at_ref(_resolve_phase_402_commit_ref())
    assert EXPECTED_CDL_042_ROW in historical_text
    assert EXPECTED_CDL_045_ROW in historical_text
    rows = parse_decision_register_rows(historical_text)
    assert rows["CDL-042"]["status"] == "open"
    assert rows["CDL-045"]["status"] == "open"


def test_cdl_042_and_cdl_045_rows_appended_after_cdl_044_in_correct_order() -> None:
    lines = _read(DECISION_LOG_PATH).splitlines()
    cdl_044_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-044 "))
    cdl_042_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-042 "))
    cdl_045_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-045 "))
    assert cdl_042_index == cdl_044_index + 1
    assert cdl_045_index == cdl_042_index + 1


def test_phase_402_commit_additive_only_non_target_shield() -> None:
    commit_ref = _resolve_phase_402_commit_ref()
    old_rows = parse_decision_register_rows(_decision_log_text_at_ref(f"{commit_ref}^1"))
    new_rows = parse_decision_register_rows(_decision_log_text_at_ref(commit_ref))
    added_ids = set(new_rows) - set(old_rows)
    assert added_ids == {"CDL-042", "CDL-045"}
    for cdl_id in old_rows:
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_402"


def test_phase_402_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_402_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
