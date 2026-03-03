from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
ARTIFACT_PATH = Path(
    "docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_evidence_prelock_340_v0.1.md"
)
PHASE_340_COMMIT_SUBJECT = "docs(g8): phase 340 cdl-034 open and node schema core prelock"
EXPECTED_ROW = (
    "| CDL-034 | ADM-001 / Node Schema Packet v0.1 | Unified node schema envelope, reserved fields, and primitive/core field taxonomy | "
    "open | single-envelope flat schema, two-envelope authored/runtime split, three-envelope authored/protocol/transport split | "
    "three-envelope authored/protocol/transport split (proposed) | envelope contract, reserved-field collision rules, primitive_type taxonomy |"
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


def _resolve_phase_340_commit_ref() -> str:
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
        if subject.strip() == PHASE_340_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(ARTIFACT_PATH),
        "tests/test_cdl_034_open_and_node_schema_core_prelock_340.py",
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_340_commit_subject_present_but_no_constitutional_opening_commit")
    raise AssertionError("phase_340_commit_not_present_in_local_history")


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


def _decision_register_lines(text: str) -> list[str]:
    lines = text.splitlines()
    start = None
    for idx, line in enumerate(lines):
        if line.startswith("| decision_id | related_clause | decision_topic | status | options | current_candidate | required_artifacts |"):
            start = idx + 2
            break
    if start is None:
        raise AssertionError("decision_register_header_not_found")

    register_lines: list[str] = []
    for line in lines[start:]:
        if not line.startswith("|"):
            break
        register_lines.append(line)
    return register_lines


def test_artifact_exists_and_has_required_sections() -> None:
    assert ARTIFACT_PATH.exists()
    text = _read(ARTIFACT_PATH)
    for heading in (
        "## 1. Purpose and scope",
        "## 2. CDL-034 state and option inventory",
        "## 3. Three-envelope model and authored payload boundary",
        "## 4. Reserved fields, extension namespace, and collision rules",
        "## 5. Primitive/core field taxonomy and epistemic-lane boundary",
        "## 6. Evidence prelock requirements for CDL-034",
        "## 7. Carry-forward constraints for later node-schema lanes",
        "## 8. Non-goals and canonical anchors",
    ):
        assert heading in text


def test_artifact_has_required_tokens_and_authoritative_items() -> None:
    text = _read(ARTIFACT_PATH)
    for token in (
        "CDL-034",
        "status: open",
        "three-envelope authored/protocol/transport split",
        "single-envelope flat schema",
        "two-envelope authored/runtime split",
        "Authored Payload Envelope",
        "Protocol Interpretation Envelope",
        "Transport Envelope",
        "The three-envelope model is the anchor invariant for CDL-034.",
        "Node is the canonical graph-object term.",
        "Agent Profile is distinct from Node and is not a synonym for a graph claim object.",
        "Quorum Record is distinct from Node and records evaluation outcomes by reference.",
        "confidence",
        "uncertainty_note",
        "confidence and uncertainty_note remain authored metadata pending ratification.",
        "confidence and uncertainty_note provisionally belong to Authored Payload Envelope.",
        "confidence and uncertainty_note are non-routing and non-economic pre-ratification authored metadata.",
        "gate_routing is protocol-derived and not submitter-controlled authored payload.",
        "gate_routing provisionally belongs to Protocol Interpretation Envelope if materialized at all.",
        "visibility provisionally belongs to Authored Payload Envelope.",
        "single-primary-epistemic-lane rule",
        "reserved fields may not be shadowed by meta keys or user tags.",
        "custom-extension namespace uses meta plus namespaced user_tags and has no routing authority.",
        "no in-place historical payload mutation is authorized.",
        "refutation is not a default primitive_type.",
        "Schema changes still require CDL opening, evidence prelock, ratification, and closure-gate process.",
        "Section 6 is authoritative for later ratification when it is more specific than the compressed CDL row shorthand.",
        "three-envelope comparison and boundary rationale",
        "reserved-field set and collision matrix",
        "primitive_type candidate taxonomy and edge-boundary note",
        "confidence and uncertainty_note disposition note",
        "gate_routing derivation and placement note",
        "Phase 341 must treat validation_state and gate verdicts as Protocol Interpretation Envelope attachments by reference, not mutations of Authored Payload Envelope.",
        "Phase 344 must treat promotion as successor public node plus promotion_receipt, never in-place visibility mutation.",
        "Phase 344 must cross-reference the CDL-034 reserved-field and custom-extension model.",
        "Phase 339 role split remains authoritative for schema-evolution monitoring and may not be weakened here.",
        "docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md",
        "docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md",
        "docs/specs/ilc_node_schema_concretization_proposals_v0.1.md",
        "docs/specs/ilc_phase_338_347_sequence_lock_v0.1.md",
        "docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md",
    ):
        assert token in text


def test_decision_log_contains_exact_new_row() -> None:
    text = _read(DECISION_LOG_PATH)
    assert EXPECTED_ROW in text
    rows = parse_decision_register_rows(text)
    assert rows["CDL-034"]["status"] == "open"
    assert rows["CDL-034"]["current_candidate"] == "three-envelope authored/protocol/transport split (proposed)"


def test_new_row_has_no_ratification_metadata() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    row = rows["CDL-034"]
    assert row["status"] == "open"
    assert "ratified_phase" not in row
    assert "ratified_date" not in row
    assert "evidence_document" not in row


def test_new_row_is_appended_after_cdl_v7_in_raw_line_order() -> None:
    text = _read(DECISION_LOG_PATH)
    register_lines = _decision_register_lines(text)
    v7_index = next(i for i, line in enumerate(register_lines) if line.startswith("| CDL-V7 |"))
    assert register_lines[v7_index + 1] == EXPECTED_ROW


def test_full_additive_only_non_target_shield_for_phase_340() -> None:
    commit_ref = _resolve_phase_340_commit_ref()
    old_rows = parse_decision_register_rows(_decision_log_text_at_ref(f"{commit_ref}^1"))
    new_rows = parse_decision_register_rows(_decision_log_text_at_ref(commit_ref))
    added_ids = set(new_rows) - set(old_rows)
    assert added_ids == {"CDL-034"}
    for cdl_id in old_rows:
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_340"


def test_phase_340_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_340_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
