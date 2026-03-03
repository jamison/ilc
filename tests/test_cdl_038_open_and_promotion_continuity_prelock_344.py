from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
ARTIFACT_PATH = Path(
    "docs/specs/ilc_cdl_038_private_to_public_promotion_and_promotion_receipt_evidence_prelock_344_v0.1.md"
)
PHASE_344_COMMIT_SUBJECT = "docs(g8): phase 344 cdl-038 open and promotion continuity prelock"
EXPECTED_ROW = (
    "| CDL-038 | CDL-034 / CDL-035 | Private-to-public promotion, promotion_receipt provenance, and visibility-change continuity | "
    "open | in-place visibility mutation on original node, successor-node plus promotion_receipt, successor-node plus promotion_receipt with automatic reputation carry-forward | "
    "successor-node plus promotion_receipt without automatic reputation carry-forward (proposed) | promotion_receipt schema, disclosed lineage rules, carry-forward boundary |"
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


def _resolve_phase_344_commit_ref() -> str:
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
        if subject.strip() == PHASE_344_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(ARTIFACT_PATH),
        "tests/test_cdl_038_open_and_promotion_continuity_prelock_344.py",
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_344_commit_subject_present_but_no_constitutional_opening_commit")
    raise AssertionError("phase_344_commit_not_present_in_local_history")


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


def test_artifact_contract_tokens_and_authoritative_items() -> None:
    assert ARTIFACT_PATH.exists()
    text = _read(ARTIFACT_PATH)
    for heading in (
        "## 1. Purpose and scope",
        "## 2. CDL-038 state and option inventory",
        "## 3. Successor-node model and authored-payload immutability",
        "## 4. promotion_receipt schema and provenance continuity",
        "## 5. Carry-forward restrictions and disclosed lineage",
        "## 6. Evidence prelock requirements for CDL-038",
        "## 7. Carry-forward constraints for later node-schema lanes",
        "## 8. Non-goals and canonical anchors",
    ):
        assert heading in text
    for token in (
        "CDL-038",
        "status: open",
        "in-place visibility mutation on original node",
        "successor-node plus promotion_receipt",
        "successor-node plus promotion_receipt with automatic reputation carry-forward",
        "Promotion changes visibility only by creating a successor public node plus a promotion_receipt, never by mutating the original node.",
        "The original private node remains immutable after promotion.",
        "promotion_receipt",
        "promotion_receipt must carry: original node CID, public successor node CID, disclosed lineage reference, epoch of promotion.",
        "No automatic public corroboration or reuse credit carry-forward is allowed.",
        "No automatic reputation carry-forward is allowed.",
        "Disclosed lineage is required; anonymous laundering of private work into public credit is not permitted.",
        "Promotion is a one-way visibility transition.",
        "A promoted public successor node starts in proposed validation_state; it does not inherit the original node's validation_state.",
        "promotion_receipt is a reserved field under CDL-034; reserved-field collision rules apply.",
        "Phase 345 must not treat a successfully promoted node as having automatic reputation advantage.",
        "No runtime implementation of promotion logic is ratified in Phase 344.",
        "Section 6 is authoritative for later ratification when it is more specific than the compressed CDL row shorthand.",
        "successor-node model and authored-payload immutability contract",
        "promotion_receipt candidate schema",
        "carry-forward restrictions (corroboration, reuse credit)",
        "disclosed lineage and audit history rules",
        "CDL-034 reserved-field cross-reference and CDL-035 validation_state interaction",
        "docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_evidence_prelock_340_v0.1.md",
        "docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_evidence_prelock_341_v0.1.md",
        "docs/specs/ilc_cdl_037_executable_node_descriptor_and_safety_contract_evidence_prelock_343_v0.1.md",
        "docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md",
        "docs/specs/ilc_node_schema_concretization_proposals_v0.1.md",
        "docs/specs/ilc_phase_338_347_sequence_lock_v0.1.md",
    ):
        assert token in text


def test_artifact_boundary_tokens_are_explicit() -> None:
    text = _read(ARTIFACT_PATH)
    for token in (
        "Promotion changes visibility only by creating a successor public node plus a promotion_receipt, never by mutating the original node.",
        "The original private node remains immutable after promotion.",
        "promotion_receipt must carry: original node CID, public successor node CID, disclosed lineage reference, epoch of promotion.",
        "No automatic public corroboration or reuse credit carry-forward is allowed.",
        "No automatic reputation carry-forward is allowed.",
        "A promoted public successor node starts in proposed validation_state; it does not inherit the original node's validation_state.",
    ):
        assert token in text


def test_decision_log_contains_exact_new_row_and_open_state() -> None:
    text = _read(DECISION_LOG_PATH)
    assert EXPECTED_ROW in text
    rows = parse_decision_register_rows(text)
    row = rows["CDL-038"]
    assert row["status"] == "open"
    assert row["current_candidate"] == "successor-node plus promotion_receipt without automatic reputation carry-forward (proposed)"
    assert "ratified_phase" not in row
    assert "ratified_date" not in row
    assert "evidence_document" not in row


def test_mutation_scope_for_cdl_038_is_additive_only() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows["CDL-038"]["status"] == "open"
    assert rows["CDL-037"]["status"] == "open"
    assert "ratified_phase" not in rows["CDL-038"]


def test_new_row_is_appended_after_cdl_037_in_raw_line_order() -> None:
    text = _read(DECISION_LOG_PATH)
    register_lines = _decision_register_lines(text)
    cdl_037_index = next(i for i, line in enumerate(register_lines) if line.startswith("| CDL-037 |"))
    assert register_lines[cdl_037_index + 1] == EXPECTED_ROW


def test_full_additive_only_non_target_shield_for_phase_344() -> None:
    commit_ref = _resolve_phase_344_commit_ref()
    old_rows = parse_decision_register_rows(_decision_log_text_at_ref(f"{commit_ref}^1"))
    new_rows = parse_decision_register_rows(_decision_log_text_at_ref(commit_ref))
    added_ids = set(new_rows) - set(old_rows)
    assert added_ids == {"CDL-038"}
    for cdl_id in old_rows:
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_344"


def test_phase_344_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_344_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
