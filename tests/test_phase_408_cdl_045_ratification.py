from __future__ import annotations

import datetime
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    ALLOWED_RATIFICATION_MUTATION_FIELDS,
    assert_head_commit_touched_no_runtime_files,
    assert_no_non_target_rows_marked_with_phase,
    assert_only_allowed_row_mutations,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
EVIDENCE_PATH = Path("docs/specs/ilc_cdl_045_operational_emergency_response_ratification_evidence_408_v0.1.md")
PHASE_404_TEST_PATH = Path("tests/test_phase_404_cdl_045_prelock_hardening.py")
PHASE_402_TEST_PATH = Path("tests/test_phase_402_cdl_042_and_cdl_045_opening.py")
PHASE_407_TEST_PATH = Path("tests/test_phase_407_cdl_042_ratification.py")
PHASE_408_COMMIT_SUBJECT = "docs(g8): phase 408 cdl-045 operational emergency response ratification"

REQUIRED_HEADINGS = (
    "## 1. Purpose and scope",
    "## 2. Ratified decision",
    "## 3. Evidence basis",
    "## 4. Section-7 ratification readiness evidence checklist satisfaction",
    "## 5. Automated circuit breaker specification",
    "## 6. Constitutional dependency closure",
    "## 7. SIM-005 calibration carry-forward and implementation deferral",
    "## 8. Out-of-scope and deferred tracks",
    "## 9. Canonical anchors",
)

REQUIRED_TOKENS = (
    "CDL-045 is ratified with the automated circuit breaker with CDL-V3 diversity quorum trigger and CDL-V6 sunset candidate.",
    "Emergency circuit-breaker invocation requires CDL-V3 cluster diversity quorum authorization; no single-cluster operator coalition can trigger a network-wide emergency shutdown.",
    "Every circuit-breaker invocation carries an automatic CDL-V6 sunset obligation; the network cannot remain in emergency state indefinitely.",
    "Resumption of normal operation requires a positive governance action through CDL-V6 sunset review, not merely the expiry of an implicit timer.",
    "Mandatory post hoc CDL-V4 review is required after every circuit-breaker invocation; emergency status does not waive governance review.",
    "Manual governance-only emergency response is rejected because human deliberation speed may be insufficient during fast-propagating failure modes at SIM-005 stress conditions.",
    "Tiered escalation with automated rate-limit and mandatory governance confirmation is rejected because multi-tier threshold design introduces unbounded governance complexity and attack surfaces without calibrated simulation evidence for tier boundaries.",
    "Exact circuit-breaker activation thresholds, detection horizons, and cooldown windows are deferred to D2e Agent SDK implementation in Phases 410-411.",
    "SIM-005 modeled a maximum unresolved orphan backlog rate of 0.338 under representative stress conditions and a 2-minute timeout horizon at validation-epoch scale; these results justify automated emergency response capability but do not directly calibrate CDL-045 trigger thresholds.",
)

REQUIRED_CANONICAL_ANCHORS = (
    "docs/specs/ilc_sim_005_agent_death_orphaning_commissioning_results_370_v0.1.md",
)

_BASE_HEADERS = [
    "decision_id",
    "related_clause",
    "decision_topic",
    "status",
    "options",
    "current_candidate",
    "required_artifacts",
]

_ALLOWED_FIELDS = set(ALLOWED_RATIFICATION_MUTATION_FIELDS) | {"current_candidate"}

_PRE_408_CDL_045_ROW = (
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


def _mini_register(row: str) -> str:
    return "\n".join(
        [
            "## Decision Register",
            "",
            "| decision_id | related_clause | decision_topic | status | options | current_candidate | required_artifacts |",
            "|---|---|---|---|---|---|---|",
            row,
            "",
            "## Scoped Ratification Record",
        ]
    )


def _register_row_text(row: dict[str, str]) -> str:
    cells = [row[header] for header in _BASE_HEADERS]
    if "ratified_phase" in row:
        cells.append(f"ratified_phase: {row['ratified_phase']}")
    if "ratified_date" in row:
        cells.append(f"ratified_date: {row['ratified_date']}")
    if "evidence_document" in row:
        cells.append(f"evidence_document: {row['evidence_document']}")
    return "| " + " | ".join(cells) + " |"


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


def _resolve_phase_408_commit_ref() -> str:
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
        if subject.strip() == PHASE_408_COMMIT_SUBJECT:
            matching.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(EVIDENCE_PATH),
        "tests/test_phase_408_cdl_045_ratification.py",
        "tests/test_phase_404_cdl_045_prelock_hardening.py",
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching:
        raise AssertionError("phase_408_commit_subject_present_but_no_ratification_mutation_commit")
    raise AssertionError("phase_408_commit_not_present_in_local_history")


def test_ratification_evidence_contains_required_headings_and_tokens() -> None:
    assert EVIDENCE_PATH.exists()
    text = _read(EVIDENCE_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text
    for token in REQUIRED_TOKENS:
        assert token in text
    for anchor in REQUIRED_CANONICAL_ANCHORS:
        assert anchor in text


def test_cdl_045_row_is_ratified_with_correct_fields() -> None:
    text = _read(DECISION_LOG_PATH)
    rows = parse_decision_register_rows(text)
    row = rows["CDL-045"]
    assert row["status"] == "ratified"
    assert row["current_candidate"] == "automated circuit breaker with CDL-V3 diversity quorum trigger and CDL-V6 sunset"
    assert row["ratified_phase"] == "408"
    ratified_date = datetime.date.fromisoformat(row["ratified_date"])
    assert ratified_date.isoformat() == "2026-03-14"
    assert row["evidence_document"] == str(EVIDENCE_PATH)
    assert "automated circuit breaker with CDL-V3 diversity quorum trigger and CDL-V6 sunset (proposed)" not in text
    assert "automated circuit breaker with CDL-V3 diversity quorum trigger and CDL-V6 sunset" in text
    assert_no_non_target_rows_marked_with_phase(rows, phase="408", target_cdls={"CDL-045"})


def test_cdl_042_and_cdl_046_rows_unchanged() -> None:
    # The Phase-408 `CDL-046` neighbor-state check is a historical ratification reference.
    historical_text = _read_file_at_ref(_resolve_phase_408_commit_ref(), str(DECISION_LOG_PATH))
    historical_rows = parse_decision_register_rows(historical_text)
    assert historical_rows["CDL-046"]["status"] == "open"
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows["CDL-042"]["status"] == "ratified"


def test_phase_404_phase_402_and_phase_407_open_assertions_are_hardened() -> None:
    phase_404_text = _read(PHASE_404_TEST_PATH)
    assert '# The Phase-404 `CDL-045` row is a historical prelock reference.' in phase_404_text
    assert phase_404_text.count("_read_file_at_ref(_resolve_phase_404_commit_ref(), str(DECISION_LOG_PATH))") >= 2
    assert "rows = parse_decision_register_rows(historical_text)" in phase_404_text
    assert "EXPECTED_CDL_045_ROW in historical_text" in phase_404_text
    assert 'rows["CDL-045"]["status"] == "open"' in phase_404_text
    assert phase_404_text.count("_read(DECISION_LOG_PATH)") == 1

    phase_402_text = _read(PHASE_402_TEST_PATH)
    assert '# The Phase-402 `CDL-042` and `CDL-045` rows are historical opening references.' in phase_402_text
    assert "_decision_log_text_at_ref(_resolve_phase_402_commit_ref())" in phase_402_text
    assert "EXPECTED_CDL_045_ROW in historical_text" in phase_402_text
    assert 'rows["CDL-045"]["status"] == "open"' in phase_402_text
    assert phase_402_text.count("_read(DECISION_LOG_PATH)") == 1

    phase_407_text = _read(PHASE_407_TEST_PATH)
    assert '# The Phase-407 `CDL-045` and `CDL-046` neighbor-state checks are historical ratification references.' in phase_407_text
    assert "_read_file_at_ref(_resolve_phase_407_commit_ref(), str(DECISION_LOG_PATH))" in phase_407_text
    assert "historical_rows = parse_decision_register_rows(historical_text)" in phase_407_text
    assert 'historical_rows["CDL-045"]["status"] == "open"' in phase_407_text
    assert 'historical_rows["CDL-046"]["status"] == "open"' in phase_407_text


def test_cdl_045_register_order_preserved_after_ratification() -> None:
    lines = _read(DECISION_LOG_PATH).splitlines()
    cdl_044_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-044 "))
    cdl_042_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-042 "))
    cdl_045_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-045 "))
    cdl_046_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-046 "))
    assert cdl_042_index == cdl_044_index + 1
    assert cdl_045_index == cdl_042_index + 1
    assert cdl_046_index == cdl_045_index + 1


def test_phase_408_commit_touches_exactly_required_paths() -> None:
    commit_ref = _resolve_phase_408_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    required = {
        str(DECISION_LOG_PATH),
        str(EVIDENCE_PATH),
        "tests/test_phase_408_cdl_045_ratification.py",
        "tests/test_phase_404_cdl_045_prelock_hardening.py",
    }
    assert required.issubset(changed)
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)


def test_phase_408_commit_no_non_cdl_045_row_mutation() -> None:
    commit_ref = _resolve_phase_408_commit_ref()
    old_rows = parse_decision_register_rows(_read_file_at_ref(f"{commit_ref}^1", str(DECISION_LOG_PATH)))
    new_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert set(old_rows) == set(new_rows)

    target_old = _mini_register(_register_row_text(old_rows["CDL-045"]))
    target_new = _mini_register(_register_row_text(new_rows["CDL-045"]))
    assert_only_allowed_row_mutations(
        target_old,
        target_new,
        cdl_id="CDL-045",
        allowed_fields=_ALLOWED_FIELDS,
    )

    for cdl_id in old_rows:
        if cdl_id == "CDL-045":
            continue
        assert old_rows[cdl_id] == new_rows[cdl_id], f"non_target_row_mutated:{cdl_id}"

    assert old_rows["CDL-045"]["status"] == "open"
    assert new_rows["CDL-045"]["status"] == "ratified"
