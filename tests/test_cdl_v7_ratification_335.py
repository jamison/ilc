from __future__ import annotations

import datetime
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    assert_no_non_target_rows_marked_with_phase,
    assert_only_allowed_row_mutations,
    parse_decision_register_rows,
)


EVIDENCE_PATH = Path("docs/specs/ilc_cdl_v7_agent_decomposition_criteria_ratification_evidence_335_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_325_TEST_PATH = Path("tests/test_cdl_v_batch_b_open_and_evidence_prelock_325.py")
PHASE_333_TEST_PATH = Path("tests/test_cdl_v5_ratification_333.py")
PHASE_334_TEST_PATH = Path("tests/test_cdl_v4_v6_dual_ratification_334.py")
PHASE_335_COMMIT_SUBJECT = "docs(g8): phase 335 cdl-v7 ratification"

_BASE_HEADERS = [
    "decision_id",
    "related_clause",
    "decision_topic",
    "status",
    "options",
    "current_candidate",
    "required_artifacts",
]

_PRE_335_CDL_V7_ROW = (
    "| CDL-V7 | Popper Analysis v0.1 / Epistemological Foundations v0.1 | Agent decomposition admissibility criteria for ILC knowledge units | "
    "open | utility-only acceptance, operator discretionary decomposition, Popperian basic-statement gate for agent decomposition | "
    "Popperian basic-statement gate for agent decomposition (proposed) | decomposition test corpus, admissibility counterexamples, cross-agent reproducibility rubric |"
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


def _resolve_phase_335_commit_ref() -> str:
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
        if subject.strip() == PHASE_335_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(EVIDENCE_PATH),
        str(PHASE_325_TEST_PATH),
        str(PHASE_333_TEST_PATH),
        str(PHASE_334_TEST_PATH),
        "tests/test_cdl_v7_ratification_335.py",
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_335_commit_subject_present_but_no_qualifying_ratification_commit")
    raise AssertionError("phase_335_commit_not_present_in_local_history")


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
        "## 2. Evidence chain summary",
        "## 3. CDL-V7 option inventory and selection statement",
        "## 4. Section-3 authoritative evidence checklist satisfaction",
        "## 5. Cross-agent reproducibility protocol",
        "## 6. Graph-entry and reuse-value admissibility tie-back",
        "## 7. Ratification record",
        "## 8. Mutation protocol confirmation",
        "## 9. Historical-prelock preservation note",
        "## 10. Non-goals",
        "## 11. Canonical anchors",
    ]
    for heading in headings:
        assert heading in text
    for token in (
        "`Popperian basic-statement gate for agent decomposition`",
        "`utility-only acceptance`",
        "`operator discretionary decomposition`",
        "docs/specs/ilc_phase_328_337_sequence_lock_v0.1.md",
        "docs/specs/ilc_cdl_v7_agent_decomposition_criteria_evidence_prelock_325_v0.1.md",
        "docs/specs/ilc_cdl_v5_schema_epoch_translation_ratification_evidence_333_v0.1.md",
        "docs/specs/ilc_cdl_v_ratification_sequencing_326_v0.1.md",
        "docs/specs/ilc_integration_coherence_report_326_v0.1.md",
        "docs/specs/ilc_antigravity_context_capsule_v0.7.md",
        "docs/specs/ilc_remaining_vulnerability_mechanisms_plan_v0.1.md",
        "docs/specs/ilc_popper_ilc_analysis_v0.1.md",
        "docs/specs/ilc_epistemological_foundations_canonical_v0.1.md",
        "Section 3 of the Phase-325 `CDL-V7` prelock artifact is authoritative for this ratification lane.",
        "`decomposition test corpus covering singular, existential, and falsifiable claim forms`",
        "`admissibility counterexamples demonstrating what must be rejected and why`",
        "`cross-agent reproducibility rubric showing that decomposition outcomes are intersubjectively stable`",
        "`explicit tie-back to graph-entry rules and reuse-value admissibility`",
    ):
        assert token in text


def test_reproducibility_protocol_and_governance_tokens_are_present() -> None:
    text = _read(EVIDENCE_PATH)
    for token in (
        "downstream step in the `CDL-V5 -> CDL-V7` sequence",
        "Phase-333 `CDL-V5` ratification supplies the schema-epoch comparability prerequisite consumed by the cross-agent reproducibility rubric.",
        "graph-entry eligibility is limited to knowledge units that satisfy the ratified Popperian basic-statement gate",
        "reuse-value admissibility is denied to decomposition outputs that fail the gate even if utility appears high",
        "minimum of three independent agent decomposition runs",
        "benchmark corpus partitions: singular, existential, falsifiable-positive, inadmissible-counterexample",
        "admissibility-decision agreement threshold: >= 0.85 across the full corpus",
        "counterexample rejection threshold: 1.00 on the inadmissible-counterexample set",
        "any candidate failing these thresholds is non-ratifiable",
        "This evidence artifact treats the reproducibility rubric as a concrete tolerance-bound evaluation protocol rather than abstract agreement language.",
    ):
        assert token in text


def test_triple_layer_hardening_is_active() -> None:
    phase_325_text = _read(PHASE_325_TEST_PATH)
    assert "assert EXPECTED_V7_ROW in historical_text" in phase_325_text
    assert 'assert rows["CDL-V7"]["status"] == "open"' not in phase_325_text
    assert "historical_rows = parse_decision_register_rows(historical_text)" in phase_325_text
    assert 'for cdl_id in ("CDL-V4", "CDL-V5", "CDL-V6", "CDL-V7")' in phase_325_text
    assert 'for cdl_id in ("CDL-V7",)' not in phase_325_text
    assert "# The Phase-325 `CDL-V7` row is a historical prelock reference" in phase_325_text

    phase_333_text = _read(PHASE_333_TEST_PATH)
    assert "assert EXPECTED_V7_ROW in historical_text" in phase_333_text
    assert 'assert \'assert rows["CDL-V7"]["status"] == "open"\' not in text' in phase_333_text
    assert '"historical_rows = parse_decision_register_rows(historical_text)" in text' in phase_333_text
    assert 'assert \'for cdl_id in ("CDL-V4", "CDL-V5", "CDL-V6", "CDL-V7")\' in text' in phase_333_text
    assert 'assert \'for cdl_id in ("CDL-V7",)\' not in text' in phase_333_text
    assert '"# The Phase-325 `CDL-V7` row is a historical prelock reference" in text' in phase_333_text

    phase_334_text = _read(PHASE_334_TEST_PATH)
    assert 'assert \'for cdl_id in ("CDL-V4", "CDL-V5", "CDL-V6", "CDL-V7")\' in text' in phase_334_text
    assert 'assert \'for cdl_id in ("CDL-V7",)\' not in text' in phase_334_text
    assert '"# The Phase-325 `CDL-V7` row is a historical prelock reference" in text' in phase_334_text


def test_decision_log_cdl_v7_is_ratified_with_expected_metadata() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    row = rows["CDL-V7"]
    assert row["status"] == "ratified"
    assert row["ratified_phase"] == "335"
    ratified_date = datetime.date.fromisoformat(row["ratified_date"])
    assert ratified_date.isoformat() == row["ratified_date"]
    assert (
        row["evidence_document"]
        == "docs/specs/ilc_cdl_v7_agent_decomposition_criteria_ratification_evidence_335_v0.1.md"
    )


def test_mutation_scope_and_non_target_rows_for_phase_335() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    old_register = _mini_register(_PRE_335_CDL_V7_ROW)
    new_register = _mini_register(_register_row_text(rows["CDL-V7"]))
    assert_only_allowed_row_mutations(old_register, new_register, cdl_id="CDL-V7")
    assert_no_non_target_rows_marked_with_phase(rows, phase="335", target_cdls={"CDL-V7"})


def test_full_non_target_row_mutation_guard_for_phase_335() -> None:
    commit_ref = _resolve_phase_335_commit_ref()

    old_text = _decision_log_text_at_ref(f"{commit_ref}^1")
    new_text = _decision_log_text_at_ref(commit_ref)

    old_rows = parse_decision_register_rows(old_text)
    new_rows = parse_decision_register_rows(new_text)

    assert set(old_rows.keys()) == set(new_rows.keys())

    target_old = _mini_register(_register_row_text(old_rows["CDL-V7"]))
    target_new = _mini_register(_register_row_text(new_rows["CDL-V7"]))
    assert_only_allowed_row_mutations(target_old, target_new, cdl_id="CDL-V7")

    for cdl_id in old_rows:
        if cdl_id == "CDL-V7":
            continue
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_335"


def test_phase_335_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_335_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
