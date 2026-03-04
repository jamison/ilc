from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
ARTIFACT_PATH = Path(
    "docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_evidence_prelock_341_v0.1.md"
)
PHASE_341_COMMIT_SUBJECT = "docs(g8): phase 341 cdl-035 open and validation lifecycle prelock"
# The Phase-341 `CDL-035` row is a historical prelock reference.
EXPECTED_ROW = (
    "| CDL-035 | Node Schema Packet v0.1 / CDL-V7 | Validation lifecycle, gate-verdict attachment, and quarantine semantics | "
    "open | inline mutable lifecycle state, attached lifecycle envelope with unbounded recursive verdict effects, "
    "attached lifecycle envelope with bounded operational relevance | attached lifecycle envelope with bounded operational relevance (proposed) | "
    "validation_state machine, gate_verdict attachment model, quarantine semantics |"
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


def _resolve_phase_341_commit_ref() -> str:
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
        if subject.strip() == PHASE_341_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(ARTIFACT_PATH),
        "tests/test_cdl_035_open_and_validation_lifecycle_prelock_341.py",
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_341_commit_subject_present_but_no_constitutional_opening_commit")
    raise AssertionError("phase_341_commit_not_present_in_local_history")


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
        "## 2. CDL-035 state and option inventory",
        "## 3. Validation state machine and protocol-envelope boundary",
        "## 4. Gate-verdict attachment and recursive challenge bound",
        "## 5. Quarantine semantics and economic effects",
        "## 6. Evidence prelock requirements for CDL-035",
        "## 7. Carry-forward constraints for later node-schema lanes",
        "## 8. Non-goals and canonical anchors",
    ):
        assert heading in text
    for token in (
        "CDL-035",
        "status: open",
        "inline mutable lifecycle state",
        "attached lifecycle envelope with unbounded recursive verdict effects",
        "attached lifecycle envelope with bounded operational relevance",
        "validation_state is a state machine, not loose status vocabulary.",
        "validation_state provisionally belongs to Protocol Interpretation Envelope.",
        "candidate state vocabulary: proposed, under_review, corroborated, quarantined, finalized, diverged",
        "quarantine_state provisionally belongs to Protocol Interpretation Envelope.",
        "gate verdicts attach by reference and do not mutate Authored Payload Envelope.",
        "gate verdict objects remain challengeable objective graph objects under CDL-V7.",
        "gate_verdict_refs",
        "operational_verdict_depth_max = 2",
        "challenge chains may exist on graph beyond the operational bound.",
        "The operational bound constrains protocol effect, not graph expressibility.",
        "deeper chains may exist on graph but do not automatically alter node status until collapsed back into first-order evidentiary claims.",
        "Only the latest eligible verdict inside the bounded operational window may affect validation_state, payout eligibility, or quarantine/corroboration status.",
        "quarantine freezes public corroboration and payout eligibility pending eligible verdict resolution.",
        "quarantine freezes public reuse eligibility pending eligible verdict resolution.",
        "quarantine does not rewrite authored payload history.",
        "CDL-V1 temporal decay remains damping support, not the sole convergence mechanism.",
        "CDL-V3 remains authoritative for diversity and anti-cluster constraints; this phase does not redefine them.",
        "CDL-V7 remains authoritative for decomposition admissibility and challengeable gate-verdict objects.",
        "No quorum thresholds are ratified in Phase 341.",
        "No reputation defaults are ratified in Phase 341.",
        "Phase 345 may not treat L-tier quorum levels as reputation tiers.",
        "Phase 342 must keep transport/header semantics separate from validation-lifecycle attachments.",
        "Phase 345 must treat reputation as derived from lifecycle outputs and must not materialize mutable inline node-level reputation.",
        "Section 6 is authoritative for later ratification when it is more specific than the compressed CDL row shorthand.",
        "validation_state state-machine table",
        "gate-verdict attachment-by-reference model",
        "recursive challenge operational bound",
        "quarantine semantics and payout-freeze note",
        "CDL-V1 / CDL-V3 / CDL-V7 dependency note",
        "docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_evidence_prelock_340_v0.1.md",
        "docs/specs/ilc_node_schema_architectural_synthesis_v0.1.md",
        "docs/specs/ilc_node_schema_concretization_proposals_v0.1.md",
        "docs/specs/ilc_phase_338_347_sequence_lock_v0.1.md",
        "docs/specs/ilc_popper_ilc_analysis_v0.1.md",
        "docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md",
        "Phase 340 remains authoritative for the authored/protocol/transport boundary and may not be weakened here.",
    ):
        assert token in text


def test_artifact_boundary_tokens_are_explicit() -> None:
    text = _read(ARTIFACT_PATH)
    for token in (
        "validation_state provisionally belongs to Protocol Interpretation Envelope.",
        "quarantine_state provisionally belongs to Protocol Interpretation Envelope.",
        "gate verdicts attach by reference and do not mutate Authored Payload Envelope.",
        "gate verdict objects remain challengeable objective graph objects under CDL-V7.",
        "operational_verdict_depth_max = 2",
        "The operational bound constrains protocol effect, not graph expressibility.",
        "deeper chains may exist on graph but do not automatically alter node status until collapsed back into first-order evidentiary claims.",
        "No quorum thresholds are ratified in Phase 341.",
        "No reputation defaults are ratified in Phase 341.",
        "Phase 345 may not treat L-tier quorum levels as reputation tiers.",
    ):
        assert token in text


def test_decision_log_contains_exact_new_row_and_open_state() -> None:
    historical_text = _decision_log_text_at_ref(_resolve_phase_341_commit_ref())
    assert EXPECTED_ROW in historical_text
    historical_rows = parse_decision_register_rows(historical_text)
    assert historical_rows["CDL-035"]["status"] == "open"
    assert (
        historical_rows["CDL-035"]["current_candidate"]
        == "attached lifecycle envelope with bounded operational relevance (proposed)"
    )
    assert "ratified_phase" not in historical_rows["CDL-035"]
    assert "ratified_date" not in historical_rows["CDL-035"]
    assert "evidence_document" not in historical_rows["CDL-035"]


def test_mutation_scope_for_cdl_035_is_additive_only() -> None:
    historical_rows = parse_decision_register_rows(
        _decision_log_text_at_ref(_resolve_phase_341_commit_ref())
    )
    assert historical_rows["CDL-035"]["status"] == "open"
    assert "ratified_phase" not in historical_rows["CDL-035"]
    assert historical_rows["CDL-034"]["status"] == "open"


def test_new_row_is_appended_after_cdl_034_in_raw_line_order() -> None:
    historical_text = _decision_log_text_at_ref(_resolve_phase_341_commit_ref())
    register_lines = _decision_register_lines(historical_text)
    cdl_034_index = next(i for i, line in enumerate(register_lines) if line.startswith("| CDL-034 |"))
    assert register_lines[cdl_034_index + 1] == EXPECTED_ROW


def test_full_additive_only_non_target_shield_for_phase_341() -> None:
    commit_ref = _resolve_phase_341_commit_ref()
    old_rows = parse_decision_register_rows(_decision_log_text_at_ref(f"{commit_ref}^1"))
    new_rows = parse_decision_register_rows(_decision_log_text_at_ref(commit_ref))
    added_ids = set(new_rows) - set(old_rows)
    assert added_ids == {"CDL-035"}
    for cdl_id in old_rows:
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_341"


def test_phase_341_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_341_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
