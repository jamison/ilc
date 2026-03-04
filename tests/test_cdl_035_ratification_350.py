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


EVIDENCE_PATH = Path(
    "docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_ratification_evidence_350_v0.1.md"
)
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_341_TEST_PATH = Path("tests/test_cdl_035_open_and_validation_lifecycle_prelock_341.py")
PHASE_342_TEST_PATH = Path("tests/test_cdl_036_open_and_node_dissemination_header_fetch_prelock_342.py")
PHASE_350_COMMIT_SUBJECT = "docs(g8): phase 350 cdl-035 ratification"

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

_PRE_350_CDL_035_ROW = (
    "| CDL-035 | Node Schema Packet v0.1 / CDL-V7 | Validation lifecycle, gate-verdict attachment, and quarantine semantics | "
    "open | inline mutable lifecycle state, attached lifecycle envelope with unbounded recursive verdict effects, "
    "attached lifecycle envelope with bounded operational relevance | attached lifecycle envelope with bounded operational relevance (proposed) | "
    "validation_state machine, gate_verdict attachment model, quarantine semantics |"
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


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_350_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matching_commits: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_350_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(EVIDENCE_PATH),
        "tests/test_cdl_035_ratification_350.py",
        str(PHASE_341_TEST_PATH),
        str(PHASE_342_TEST_PATH),
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_350_commit_subject_present_but_no_qualifying_ratification_commit")
    raise AssertionError("phase_350_commit_not_present_in_local_history")


def _decision_log_text_at_ref(ref: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{ref}:{DECISION_LOG_PATH}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"unable_to_read_decision_log_at_ref:{ref}: {result.stderr.strip()}")
    return result.stdout


def test_ratification_evidence_file_exists_and_has_required_content() -> None:
    assert EVIDENCE_PATH.exists()
    text = _read(EVIDENCE_PATH)
    headings = [
        "## 1. Purpose and scope",
        "## 2. Ratified decision",
        "## 3. Evidence basis",
        "## 4. Section-6 authoritative evidence checklist satisfaction",
        "## 5. Governance tokens",
        "## 6. Carry-forward constraints",
        "## 7. Prelock hardening requirement",
        "## 8. Runtime deferral boundary",
        "## 9. Canonical anchors",
    ]
    for heading in headings:
        assert heading in text
    for token in (
        "attached lifecycle envelope with bounded operational relevance",
        "inline mutable lifecycle state",
        "attached lifecycle envelope with unbounded recursive verdict effects",
        "docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_evidence_prelock_341_v0.1.md",
        "docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_ratification_evidence_349_v0.1.md",
        "docs/specs/ilc_integration_coherence_report_346_v0.1.md",
        "docs/specs/ilc_antigravity_context_capsule_v0.9.md",
        "docs/specs/ilc_node_schema_ratification_readiness_report_346_v0.1.md",
        "docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md",
        "docs/specs/ilc_popper_ilc_analysis_v0.1.md",
        "Section 6 of the Phase-341 prelock artifact is authoritative for this ratification lane when it is more specific than the compressed CDL row shorthand.",
        "validation_state state-machine table",
        "gate-verdict attachment-by-reference model",
        "recursive challenge operational bound",
        "quarantine semantics and payout-freeze note",
        "CDL-V1 / CDL-V3 / CDL-V7 dependency note",
        "validation_state is a state machine, not loose status vocabulary.",
        "validation_state provisionally belongs to Protocol Interpretation Envelope.",
        "quarantine_state provisionally belongs to Protocol Interpretation Envelope.",
        "gate verdicts attach by reference and do not mutate Authored Payload Envelope.",
        "gate verdict objects remain challengeable objective graph objects under CDL-V7.",
        "operational_verdict_depth_max = 2",
        "The operational bound constrains protocol effect, not graph expressibility.",
        "deeper chains may exist on graph but do not automatically alter node status until collapsed back into first-order evidentiary claims.",
        "quarantine freezes public corroboration and payout eligibility pending eligible verdict resolution.",
        "quarantine freezes public reuse eligibility pending eligible verdict resolution.",
        "No quorum thresholds are ratified in Phase 350.",
        "No reputation defaults are ratified in Phase 350.",
        "Phase 345 may not treat L-tier quorum levels as reputation tiers.",
        "No runtime implementation of CDL-035 validation lifecycle logic is ratified in Phase 350.",
    ):
        assert token in text


def test_historical_prelock_and_cross_cdl_hardening_patches_are_active() -> None:
    phase_341_text = _read(PHASE_341_TEST_PATH)
    assert 'assert EXPECTED_ROW in historical_text' in phase_341_text
    assert 'assert rows["CDL-035"]["status"] == "open"' not in phase_341_text
    assert (
        'assert row["current_candidate"] == "attached lifecycle envelope with bounded operational relevance (proposed)"'
        not in phase_341_text
    )
    assert 'assert "ratified_phase" not in historical_rows["CDL-035"]' in phase_341_text
    assert 'assert "ratified_date" not in historical_rows["CDL-035"]' in phase_341_text
    assert 'assert "evidence_document" not in historical_rows["CDL-035"]' in phase_341_text
    assert '_decision_log_text_at_ref(_resolve_phase_341_commit_ref())' in phase_341_text
    assert '# The Phase-341 `CDL-035` row is a historical prelock reference.' in phase_341_text

    phase_342_text = _read(PHASE_342_TEST_PATH)
    assert 'assert rows["CDL-035"]["status"] == "open"' not in phase_342_text
    assert 'parse_decision_register_rows(' in phase_342_text
    assert '_decision_log_text_at_ref(_resolve_phase_342_commit_ref())' in phase_342_text


def test_decision_log_cdl_035_is_ratified_with_expected_metadata_and_scope() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    row = rows["CDL-035"]
    assert row["status"] == "ratified"
    assert row["current_candidate"] == "attached lifecycle envelope with bounded operational relevance"
    assert row["ratified_phase"] == "350"
    ratified_date = datetime.date.fromisoformat(row["ratified_date"])
    assert ratified_date.isoformat() == row["ratified_date"]
    assert row["evidence_document"] == str(EVIDENCE_PATH)
    assert_no_non_target_rows_marked_with_phase(rows, phase="350", target_cdls={"CDL-035"})


def test_mutation_scope_guardrail_allows_only_ratification_fields_for_cdl_035() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    old_register = _mini_register(_PRE_350_CDL_035_ROW)
    new_register = _mini_register(_register_row_text(rows["CDL-035"]))
    assert_only_allowed_row_mutations(
        old_register,
        new_register,
        cdl_id="CDL-035",
        allowed_fields=_ALLOWED_FIELDS,
    )


def test_ratification_pattern_matches_prior_subject_qualified_cdls() -> None:
    phase_349_text = _read(Path("tests/test_cdl_034_ratification_349.py"))
    assert "assert_only_allowed_row_mutations" in phase_349_text
    assert "raise AssertionError(\"phase_349_commit_not_present_in_local_history\")" in phase_349_text


def test_full_non_target_row_mutation_guard_for_phase_350() -> None:
    commit_ref = _resolve_phase_350_commit_ref()
    old_text = _decision_log_text_at_ref(f"{commit_ref}^1")
    new_text = _decision_log_text_at_ref(commit_ref)
    old_rows = parse_decision_register_rows(old_text)
    new_rows = parse_decision_register_rows(new_text)
    assert set(old_rows.keys()) == set(new_rows.keys())

    target_old = _mini_register(_register_row_text(old_rows["CDL-035"]))
    target_new = _mini_register(_register_row_text(new_rows["CDL-035"]))
    assert_only_allowed_row_mutations(
        target_old,
        target_new,
        cdl_id="CDL-035",
        allowed_fields=_ALLOWED_FIELDS,
    )

    for cdl_id in old_rows:
        if cdl_id == "CDL-035":
            continue
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_350"


def test_phase_350_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_350_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
