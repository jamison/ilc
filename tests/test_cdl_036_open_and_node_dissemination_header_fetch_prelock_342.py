from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
ARTIFACT_PATH = Path(
    "docs/specs/ilc_cdl_036_node_dissemination_header_and_fetch_contract_evidence_prelock_342_v0.1.md"
)
PHASE_342_COMMIT_SUBJECT = "docs(g8): phase 342 cdl-036 open and node dissemination header/fetch prelock"
EXPECTED_ROW = (
    "| CDL-036 | ADM-001 / CDL-024 | Node dissemination header, payload fetch contract, and transport boundary | "
    "open | full-payload push broadcast, header-first dissemination with fixed orderer, header-first dissemination with CID-addressed pull fetch | "
    "header-first dissemination with CID-addressed pull fetch (proposed) | header schema, fetch semantics, signature scope |"
)
# The Phase-342 `CDL-036` row is a historical prelock reference.


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


def _resolve_phase_342_commit_ref() -> str:
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
        if subject.strip() == PHASE_342_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(ARTIFACT_PATH),
        "tests/test_cdl_036_open_and_node_dissemination_header_fetch_prelock_342.py",
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_342_commit_subject_present_but_no_constitutional_opening_commit")
    raise AssertionError("phase_342_commit_not_present_in_local_history")


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
        "## 2. CDL-036 state and option inventory",
        "## 3. Header-first dissemination and transport-envelope boundary",
        "## 4. Fetch contract, payload reference, and signature scope",
        "## 5. Visibility, channel interaction, and orderer-agnostic boundary",
        "## 6. Evidence prelock requirements for CDL-036",
        "## 7. Carry-forward constraints for later node-schema lanes",
        "## 8. Non-goals and canonical anchors",
    ):
        assert heading in text
    for token in (
        "CDL-036",
        "status: open",
        "full-payload push broadcast",
        "header-first dissemination with fixed orderer",
        "header-first dissemination with CID-addressed pull fetch",
        "header-first dissemination",
        "CID-addressed pull fetch",
        "content-addressed verification before interpretation",
        "Transport Envelope remains separate from Authored Payload Envelope and Protocol Interpretation Envelope.",
        "header schema",
        "candidate header field set: node_id, creator_agent_id, epistemic_type, visibility, channel, epoch_created, payload_cid, signature",
        "payload_cid",
        "The header signature must commit to the payload reference.",
        "signature scope covers header fields plus payload_cid.",
        "header-first dissemination does not authorize full-payload push as the default transport rule.",
        "ILC leans pull, not push.",
        "pull-dominant with soft push-signals",
        "visibility and channel remain routing inputs, not authored-payload mutability permissions.",
        "visibility/channel interaction belongs to Transport Envelope routing semantics only insofar as dissemination policy is concerned.",
        "retry and idempotence remain fetch-contract obligations, not authored-payload semantics.",
        "Narwhal/Tusk/Bullshark remains a reference pattern, not a locked constitutional choice.",
        "No permanent validator-core orderer is ratified in Phase 342.",
        "No transport binding implementation is ratified in Phase 342.",
        "CDL-024 remains authoritative for transport-agnostic wire bindings and is not weakened here.",
        "Phase 341 remains authoritative for validation-lifecycle attachments and may not be collapsed into transport semantics.",
        "Phase 343 must keep executable-node transport concerns subordinate to the CDL-036 header/fetch contract.",
        "Section 6 is authoritative for later ratification when it is more specific than the compressed CDL row shorthand.",
        "transport header field set",
        "push/pull dissemination conclusion and fetch-boundary note",
        "fetch API and idempotence note",
        "signature scope and payload-reference integrity note",
        "visibility/channel dissemination rule note",
        "orderer-agnostic boundary note",
        "docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_evidence_prelock_340_v0.1.md",
        "docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_evidence_prelock_341_v0.1.md",
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
        "Transport Envelope remains separate from Authored Payload Envelope and Protocol Interpretation Envelope.",
        "candidate header field set: node_id, creator_agent_id, epistemic_type, visibility, channel, epoch_created, payload_cid, signature",
        "The header signature must commit to the payload reference.",
        "signature scope covers header fields plus payload_cid.",
        "ILC leans pull, not push.",
        "pull-dominant with soft push-signals",
        "No permanent validator-core orderer is ratified in Phase 342.",
        "No transport binding implementation is ratified in Phase 342.",
    ):
        assert token in text


def test_decision_log_contains_exact_new_row_and_open_state() -> None:
    historical_text = _decision_log_text_at_ref(_resolve_phase_342_commit_ref())
    assert EXPECTED_ROW in historical_text
    historical_rows = parse_decision_register_rows(historical_text)
    row = historical_rows["CDL-036"]
    assert row["status"] == "open"
    assert "ratified_phase" not in row
    assert "ratified_date" not in row
    assert "evidence_document" not in row


def test_mutation_scope_for_cdl_036_is_additive_only() -> None:
    historical_rows = parse_decision_register_rows(
        _decision_log_text_at_ref(_resolve_phase_342_commit_ref())
    )
    assert historical_rows["CDL-036"]["status"] == "open"
    assert historical_rows["CDL-035"]["status"] == "open"
    assert "ratified_phase" not in historical_rows["CDL-036"]


def test_new_row_is_appended_after_cdl_035_in_raw_line_order() -> None:
    historical_text = _decision_log_text_at_ref(_resolve_phase_342_commit_ref())
    register_lines = _decision_register_lines(historical_text)
    cdl_035_index = next(i for i, line in enumerate(register_lines) if line.startswith("| CDL-035 |"))
    assert register_lines[cdl_035_index + 1] == EXPECTED_ROW


def test_full_additive_only_non_target_shield_for_phase_342() -> None:
    commit_ref = _resolve_phase_342_commit_ref()
    old_rows = parse_decision_register_rows(_decision_log_text_at_ref(f"{commit_ref}^1"))
    new_rows = parse_decision_register_rows(_decision_log_text_at_ref(commit_ref))
    added_ids = set(new_rows) - set(old_rows)
    assert added_ids == {"CDL-036"}
    for cdl_id in old_rows:
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_342"


def test_phase_342_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_342_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
