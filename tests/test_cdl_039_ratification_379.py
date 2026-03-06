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
    "docs/specs/ilc_cdl_039_p2p_transport_and_topology_privacy_ratification_evidence_379_v0.1.md"
)
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_359_TEST_PATH = Path("tests/test_cdl_039_open_and_p2p_transport_baseline_prelock_359.py")
PHASE_372_TEST_PATH = Path("tests/test_cdl_039_topology_privacy_hardening_prelock_372.py")
PHASE_373_TEST_PATH = Path("tests/test_cdl_039_adversarial_review_and_evidence_freeze_373.py")
PHASE_374_TEST_PATH = Path("tests/test_cdl_039_prelock_finalization_374.py")
PHASE_379_COMMIT_SUBJECT = "docs(g8): phase 379 cdl-039 ratification"

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

_PRE_379_CDL_039_ROW = (
    "| CDL-039 | ADR-0011 / Open Requirements 354 v0.1 | P2P transport baseline, no-central-broker invariant, and gossip-topology privacy constraints | "
    "open | centrally coordinated relay transport, federated relay mesh, brokerless peer-to-peer gossip baseline | "
    "brokerless peer-to-peer gossip baseline (proposed) | no-central-broker invariant, topology-privacy constraints, partition evidence requirements |"
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


def _extract_calibration_section(text: str) -> str:
    lines = text.splitlines()
    start = None
    end = None
    for idx, line in enumerate(lines):
        if line.startswith("## ") and "calibration" in line.lower():
            start = idx
            continue
        if start is not None and line.startswith("## "):
            end = idx
            break
    if start is None:
        raise AssertionError("calibration_section_not_found")
    if end is None:
        end = len(lines)
    return "\n".join(lines[start:end])


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_379_commit_ref() -> str:
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
        if subject.strip() == PHASE_379_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(EVIDENCE_PATH),
        "tests/test_cdl_039_ratification_379.py",
        str(PHASE_359_TEST_PATH),
        str(PHASE_372_TEST_PATH),
        str(PHASE_373_TEST_PATH),
        str(PHASE_374_TEST_PATH),
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_379_commit_subject_present_but_no_qualifying_ratification_commit")
    raise AssertionError("phase_379_commit_not_present_in_local_history")


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


def test_ratification_evidence_exists_and_has_required_content() -> None:
    assert EVIDENCE_PATH.exists()
    text = _read(EVIDENCE_PATH)
    for heading in (
        "## 1. Purpose and scope",
        "## 2. Ratified decision",
        "## 3. Evidence basis",
        "## 4. Section-3 authoritative evidence checklist satisfaction",
        "## 5. Calibration constants resolution",
        "## 6. CDL-036 reconciliation clause",
        "## 7. Carry-forward constraints",
        "## 8. Runtime deferral boundary",
        "## 9. Canonical anchors",
    ):
        assert heading in text
    for token in (
        "CDL-039 ratification removes creator_agent_id from the CDL-036 Transport Envelope candidate header field set; authorship attribution is resolved exclusively from the Authored Payload envelope and Protocol Interpretation envelope.",
        "Calibration constants section is authoritative for Phase-391 section-scoped parsing.",
        "No runtime implementation of CDL-039 transport invariants is ratified in Phase 379.",
        "D2d runtime enforcement remains implementation work in phases 380-382.",
        "All CDL-039 prelock artifacts remain historical-open references after ratification.",
        "docs/specs/ilc_cdl_039_open_and_p2p_transport_baseline_prelock_359_v0.1.md",
        "docs/specs/ilc_cdl_039_topology_privacy_hardening_prelock_372_v0.1.md",
        "docs/specs/ilc_cdl_039_adversarial_review_and_evidence_freeze_373_v0.1.md",
        "docs/specs/ilc_cdl_039_prelock_finalization_374_v0.1.md",
        "docs/specs/ilc_phase_378_391_sequence_lock_v0.1.md",
        "docs/specs/ilc_antigravity_context_capsule_v1.2.md",
    ):
        assert token in text


def test_calibration_section_is_structured_and_resolves_all_parameter_groups() -> None:
    text = _read(EVIDENCE_PATH)
    section = _extract_calibration_section(text)
    for token in (
        "R_partition_cross_ref",
        "H_release",
        "timeout_policy / stake_recovery_policy",
        "retention_epochs",
    ):
        assert token in section
    assert "bounded_range" not in section
    assert "retention_epochs operational value requires a named subsequent CDL amendment before deployment" in section


def test_all_four_prelock_tests_are_historicalized() -> None:
    phase_359_text = _read(PHASE_359_TEST_PATH)
    assert '# The Phase-359 `CDL-039` row is a historical prelock reference.' in phase_359_text
    assert 'assert EXPECTED_ROW in historical_text' in phase_359_text
    assert 'parse_decision_register_rows(_decision_log_text_at_ref(_resolve_phase_359_commit_ref()))' in phase_359_text
    assert 'rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))' not in phase_359_text

    phase_372_text = _read(PHASE_372_TEST_PATH)
    assert '# The Phase-372 `CDL-039` row is a historical prelock reference.' in phase_372_text
    assert '_decision_log_text_at_ref(_resolve_phase_372_commit_ref_or_fail())' in phase_372_text

    phase_373_text = _read(PHASE_373_TEST_PATH)
    assert '# The Phase-373 `CDL-039` row is a historical prelock reference.' in phase_373_text
    assert '_decision_log_text_at_ref(_resolve_phase_373_commit_ref_or_fail())' in phase_373_text

    phase_374_text = _read(PHASE_374_TEST_PATH)
    assert '# The Phase-374 `CDL-039` row is a historical prelock reference.' in phase_374_text
    assert '_decision_log_text_at_ref(_resolve_phase_374_commit_ref_or_fail())' in phase_374_text


def test_decision_log_cdl_039_is_ratified_with_expected_metadata_and_scope() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    row = rows["CDL-039"]
    assert row["status"] == "ratified"
    assert row["current_candidate"] == "brokerless peer-to-peer gossip baseline"
    assert row["ratified_phase"] == "379"
    ratified_date = datetime.date.fromisoformat(row["ratified_date"])
    assert ratified_date.isoformat() == row["ratified_date"]
    assert row["evidence_document"] == str(EVIDENCE_PATH)
    assert_no_non_target_rows_marked_with_phase(rows, phase="379", target_cdls={"CDL-039"})


def test_mutation_scope_guardrail_allows_only_ratification_fields_for_cdl_039() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    old_register = _mini_register(_PRE_379_CDL_039_ROW)
    new_register = _mini_register(_register_row_text(rows["CDL-039"]))
    assert_only_allowed_row_mutations(
        old_register,
        new_register,
        cdl_id="CDL-039",
        allowed_fields=_ALLOWED_FIELDS,
    )


def test_full_non_target_row_mutation_guard_for_phase_379() -> None:
    commit_ref = _resolve_phase_379_commit_ref()
    old_text = _decision_log_text_at_ref(f"{commit_ref}^1")
    new_text = _decision_log_text_at_ref(commit_ref)
    old_rows = parse_decision_register_rows(old_text)
    new_rows = parse_decision_register_rows(new_text)
    assert set(old_rows.keys()) == set(new_rows.keys())

    target_old = _mini_register(_register_row_text(old_rows["CDL-039"]))
    target_new = _mini_register(_register_row_text(new_rows["CDL-039"]))
    assert_only_allowed_row_mutations(
        target_old,
        target_new,
        cdl_id="CDL-039",
        allowed_fields=_ALLOWED_FIELDS,
    )

    for cdl_id in old_rows:
        if cdl_id == "CDL-039":
            continue
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_379"


def test_phase_379_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_379_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
