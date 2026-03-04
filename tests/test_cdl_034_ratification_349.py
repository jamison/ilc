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
    "docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_ratification_evidence_349_v0.1.md"
)
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_340_TEST_PATH = Path("tests/test_cdl_034_open_and_node_schema_core_prelock_340.py")
PHASE_349_COMMIT_SUBJECT = "docs(g8): phase 349 cdl-034 ratification"

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

_PRE_349_CDL_034_ROW = (
    "| CDL-034 | ADM-001 / Node Schema Packet v0.1 | Unified node schema envelope, reserved fields, and primitive/core field taxonomy | "
    "open | single-envelope flat schema, two-envelope authored/runtime split, three-envelope authored/protocol/transport split | "
    "three-envelope authored/protocol/transport split (proposed) | envelope contract, reserved-field collision rules, primitive_type taxonomy |"
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


def _resolve_phase_349_commit_ref() -> str:
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
        if subject.strip() == PHASE_349_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(EVIDENCE_PATH),
        "tests/test_cdl_034_ratification_349.py",
        str(PHASE_340_TEST_PATH),
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_349_commit_subject_present_but_no_qualifying_ratification_commit")
    raise AssertionError("phase_349_commit_not_present_in_local_history")


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
        "three-envelope authored/protocol/transport split",
        "single-envelope flat schema",
        "two-envelope authored/runtime split",
        "docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_evidence_prelock_340_v0.1.md",
        "docs/specs/ilc_integration_coherence_report_346_v0.1.md",
        "docs/specs/ilc_antigravity_context_capsule_v0.9.md",
        "docs/specs/ilc_node_schema_ratification_readiness_report_346_v0.1.md",
        "docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md",
        "Section 6 of the Phase-340 prelock artifact is authoritative for this ratification lane when it is more specific than the compressed CDL row shorthand.",
        "three-envelope comparison and boundary rationale",
        "reserved-field set and collision matrix",
        "primitive_type candidate taxonomy and edge-boundary note",
        "confidence and uncertainty_note disposition note",
        "gate_routing derivation and placement note",
        "The three-envelope model is the anchor invariant for CDL-034.",
        "Authored Payload Envelope",
        "Protocol Interpretation Envelope",
        "Transport Envelope",
        "Node is the canonical graph-object term.",
        "Agent Profile is distinct from Node and is not a synonym for a graph claim object.",
        "Quorum Record is distinct from Node and records evaluation outcomes by reference.",
        "reserved fields may not be shadowed by meta keys or user tags.",
        "custom-extension namespace uses meta plus namespaced user_tags and has no routing authority.",
        "confidence and uncertainty_note belong to Authored Payload Envelope.",
        "confidence and uncertainty_note remain non-routing and non-economic metadata unless a later CDL ratifies otherwise.",
        "visibility belongs to Authored Payload Envelope.",
        "gate_routing is protocol-derived and not submitter-controlled authored payload.",
        "gate_routing belongs to Protocol Interpretation Envelope if materialized at all.",
        "refutation is not a default primitive_type.",
        "no in-place historical payload mutation is authorized.",
        "No runtime implementation of CDL-034 node schema logic is ratified in Phase 349.",
    ):
        assert token in text


def test_historical_prelock_hardening_patch_is_active() -> None:
    text = _read(PHASE_340_TEST_PATH)
    assert 'assert EXPECTED_ROW in historical_text' in text
    assert 'assert rows["CDL-034"]["status"] == "open"' not in text
    assert 'assert rows["CDL-034"]["current_candidate"] == "three-envelope authored/protocol/transport split (proposed)"' not in text
    assert '_decision_log_text_at_ref(_resolve_phase_340_commit_ref())' in text
    assert '# The Phase-340 `CDL-034` row is a historical prelock reference.' in text


def test_decision_log_cdl_034_is_ratified_with_expected_metadata() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    row = rows["CDL-034"]
    assert row["status"] == "ratified"
    assert row["current_candidate"] == "three-envelope authored/protocol/transport split"
    assert row["ratified_phase"] == "349"
    ratified_date = datetime.date.fromisoformat(row["ratified_date"])
    assert ratified_date.isoformat() == row["ratified_date"]
    assert row["evidence_document"] == str(EVIDENCE_PATH)


def test_mutation_scope_guardrail_allows_only_ratification_fields_for_cdl_034() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    old_register = _mini_register(_PRE_349_CDL_034_ROW)
    new_register = _mini_register(_register_row_text(rows["CDL-034"]))
    assert_only_allowed_row_mutations(
        old_register,
        new_register,
        cdl_id="CDL-034",
        allowed_fields=_ALLOWED_FIELDS,
    )


def test_non_target_rows_not_ratified_in_phase_349() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert_no_non_target_rows_marked_with_phase(rows, phase="349", target_cdls={"CDL-034"})


def test_full_non_target_row_mutation_guard_for_phase_349() -> None:
    commit_ref = _resolve_phase_349_commit_ref()
    old_text = _decision_log_text_at_ref(f"{commit_ref}^1")
    new_text = _decision_log_text_at_ref(commit_ref)
    old_rows = parse_decision_register_rows(old_text)
    new_rows = parse_decision_register_rows(new_text)
    assert set(old_rows.keys()) == set(new_rows.keys())

    target_old = _mini_register(_register_row_text(old_rows["CDL-034"]))
    target_new = _mini_register(_register_row_text(new_rows["CDL-034"]))
    assert_only_allowed_row_mutations(
        target_old,
        target_new,
        cdl_id="CDL-034",
        allowed_fields=_ALLOWED_FIELDS,
    )

    for cdl_id in old_rows:
        if cdl_id == "CDL-034":
            continue
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_349"


def test_phase_349_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_349_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
