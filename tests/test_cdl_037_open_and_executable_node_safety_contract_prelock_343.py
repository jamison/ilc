from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
ARTIFACT_PATH = Path(
    "docs/specs/ilc_cdl_037_executable_node_descriptor_and_safety_contract_evidence_prelock_343_v0.1.md"
)
PHASE_343_COMMIT_SUBJECT = "docs(g8): phase 343 cdl-037 open and executable node safety contract prelock"
EXPECTED_ROW = (
    "| CDL-037 | CDL-034 / CDL-V7 | Executable node descriptor, safety contract, and agent-side sandboxing | "
    "open | raw executable payload embedded in authored envelope, structured descriptor without sandboxing, structured descriptor with sandboxed runtime binding | "
    "structured descriptor with sandboxed runtime binding (proposed) | executable descriptor schema, safety contract model, sandbox boundary semantics |"
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


def _resolve_phase_343_commit_ref() -> str:
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
        if subject.strip() == PHASE_343_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(ARTIFACT_PATH),
        "tests/test_cdl_037_open_and_executable_node_safety_contract_prelock_343.py",
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_343_commit_subject_present_but_no_constitutional_opening_commit")
    raise AssertionError("phase_343_commit_not_present_in_local_history")


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
        "## 2. CDL-037 state and option inventory",
        "## 3. Executable descriptor boundary and authored-envelope placement",
        "## 4. Safety contract model and agent-side sandboxing",
        "## 5. Genesis-trusted vs non-genesis executable descriptors",
        "## 6. Evidence prelock requirements for CDL-037",
        "## 7. Carry-forward constraints for later node-schema lanes",
        "## 8. Non-goals and canonical anchors",
    ):
        assert heading in text
    for token in (
        "CDL-037",
        "status: open",
        "raw executable payload embedded in authored envelope",
        "structured descriptor without sandboxing",
        "structured descriptor with sandboxed runtime binding",
        "Nodes recommend logic; they do not self-authorize execution.",
        "The executable descriptor is Authored Payload content.",
        "Execution context belongs to the Transport/Runtime layer, not the Authored Payload Envelope.",
        "The three-envelope boundary established in Phase 340 must not be weakened here.",
        "agent-side sandboxing is a safety-contract obligation",
        "genesis-trusted executable descriptor",
        "non-genesis executable descriptor",
        "Genesis-trusted descriptors carry bootstrap authority that non-genesis descriptors cannot claim.",
        "A proposed executable descriptor is an objective graph object challengeable under CDL-V7.",
        "The executable descriptor must satisfy the CDL-V7 Popperian basic-statement gate before acquiring protocol effect.",
        "declared inputs",
        "declared outputs",
        "declared side effects",
        "safety assertions",
        "determinism guarantees",
        "bounded resource guarantees",
        "No runtime implementation of executable-node logic is ratified in Phase 343.",
        "Phase 344 must cross-reference CDL-037 for the executable-node promotion case.",
        "Phase 345 must not treat executable-node trust levels as reputation defaults.",
        "Section 6 is authoritative for later ratification when it is more specific than the compressed CDL row shorthand.",
        "executable descriptor candidate field set",
        "sandboxed runtime binding contract",
        "safety contract model and genesis-trust boundary",
        "CDL-V7 decomposition gate for executable descriptors",
        "CDL-034 authored-envelope boundary preservation note",
        "docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_evidence_prelock_340_v0.1.md",
        "docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_evidence_prelock_341_v0.1.md",
        "docs/specs/ilc_cdl_036_node_dissemination_header_and_fetch_contract_evidence_prelock_342_v0.1.md",
        "docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md",
        "docs/specs/ilc_node_schema_concretization_proposals_v0.1.md",
        "docs/specs/ilc_phase_338_347_sequence_lock_v0.1.md",
        "docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md",
        "docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md",
    ):
        assert token in text


def test_artifact_boundary_tokens_are_explicit() -> None:
    text = _read(ARTIFACT_PATH)
    for token in (
        "The executable descriptor is Authored Payload content.",
        "Execution context belongs to the Transport/Runtime layer, not the Authored Payload Envelope.",
        "The three-envelope boundary established in Phase 340 must not be weakened here.",
        "Nodes recommend logic; they do not self-authorize execution.",
        "agent-side sandboxing is a safety-contract obligation",
        "Genesis-trusted descriptors carry bootstrap authority that non-genesis descriptors cannot claim.",
        "A proposed executable descriptor is an objective graph object challengeable under CDL-V7.",
        "The executable descriptor must satisfy the CDL-V7 Popperian basic-statement gate before acquiring protocol effect.",
    ):
        assert token in text


def test_decision_log_contains_exact_new_row_and_open_state() -> None:
    text = _read(DECISION_LOG_PATH)
    assert EXPECTED_ROW in text
    rows = parse_decision_register_rows(text)
    row = rows["CDL-037"]
    assert row["status"] == "open"
    assert row["current_candidate"] == "structured descriptor with sandboxed runtime binding (proposed)"
    assert "ratified_phase" not in row
    assert "ratified_date" not in row
    assert "evidence_document" not in row


def test_mutation_scope_for_cdl_037_is_additive_only() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows["CDL-037"]["status"] == "open"
    historical_rows = parse_decision_register_rows(
        _decision_log_text_at_ref(_resolve_phase_343_commit_ref())
    )
    assert historical_rows["CDL-036"]["status"] == "open"
    assert "ratified_phase" not in rows["CDL-037"]


def test_new_row_is_appended_after_cdl_036_in_raw_line_order() -> None:
    text = _read(DECISION_LOG_PATH)
    register_lines = _decision_register_lines(text)
    cdl_036_index = next(i for i, line in enumerate(register_lines) if line.startswith("| CDL-036 |"))
    assert register_lines[cdl_036_index + 1] == EXPECTED_ROW


def test_full_additive_only_non_target_shield_for_phase_343() -> None:
    commit_ref = _resolve_phase_343_commit_ref()
    old_rows = parse_decision_register_rows(_decision_log_text_at_ref(f"{commit_ref}^1"))
    new_rows = parse_decision_register_rows(_decision_log_text_at_ref(commit_ref))
    added_ids = set(new_rows) - set(old_rows)
    assert added_ids == {"CDL-037"}
    for cdl_id in old_rows:
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_343"


def test_phase_343_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_343_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
