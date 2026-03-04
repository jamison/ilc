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
    "docs/specs/ilc_cdl_038_private_to_public_promotion_and_promotion_receipt_ratification_evidence_353_v0.1.md"
)
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_344_TEST_PATH = Path("tests/test_cdl_038_open_and_promotion_continuity_prelock_344.py")
PHASE_353_COMMIT_SUBJECT = "docs(g8): phase 353 cdl-038 ratification"

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

_PRE_353_CDL_038_ROW = (
    "| CDL-038 | CDL-034 / CDL-035 | Private-to-public promotion, promotion_receipt provenance, and visibility-change continuity | "
    "open | in-place visibility mutation on original node, successor-node plus promotion_receipt, successor-node plus promotion_receipt with automatic reputation carry-forward | "
    "successor-node plus promotion_receipt without automatic reputation carry-forward (proposed) | promotion_receipt schema, disclosed lineage rules, carry-forward boundary |"
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


def _resolve_phase_353_commit_ref() -> str:
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
        if subject.strip() == PHASE_353_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(EVIDENCE_PATH),
        "tests/test_cdl_038_ratification_353.py",
        str(PHASE_344_TEST_PATH),
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_353_commit_subject_present_but_no_qualifying_ratification_commit")
    raise AssertionError("phase_353_commit_not_present_in_local_history")


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
        "successor-node plus promotion_receipt without automatic reputation carry-forward",
        "in-place visibility mutation on original node",
        "successor-node plus promotion_receipt with automatic reputation carry-forward",
        "docs/specs/ilc_cdl_038_private_to_public_promotion_and_promotion_receipt_evidence_prelock_344_v0.1.md",
        "docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_ratification_evidence_349_v0.1.md",
        "docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_ratification_evidence_350_v0.1.md",
        "docs/specs/ilc_cdl_036_node_dissemination_header_and_fetch_contract_ratification_evidence_351_v0.1.md",
        "docs/specs/ilc_cdl_037_executable_node_descriptor_and_safety_contract_ratification_evidence_352_v0.1.md",
        "docs/specs/ilc_reputation_and_agent_profile_adjoint_contract_345_v0.1.md",
        "docs/specs/ilc_integration_coherence_report_346_v0.1.md",
        "docs/specs/ilc_antigravity_context_capsule_v0.9.md",
        "docs/specs/ilc_node_schema_ratification_readiness_report_346_v0.1.md",
        "docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md",
        "docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md",
        "Section 6 of the Phase-344 prelock artifact is authoritative for this ratification lane when it is more specific than the compressed CDL row shorthand.",
        "successor-node model and authored-payload immutability contract",
        "promotion_receipt candidate schema",
        "carry-forward restrictions (corroboration, reuse credit)",
        "disclosed lineage and audit history rules",
        "CDL-034 reserved-field cross-reference and CDL-035 validation_state interaction",
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
        "CDL-034 remains authoritative for reserved-field collision rules and is not weakened here.",
        "CDL-035 remains authoritative for validation_state semantics and is not weakened here.",
        "Phase 345 must not treat a successfully promoted node as having automatic reputation advantage.",
        "CDL-037 remains authoritative for executable-node safety constraints and is not weakened here.",
        "Promotion preserves provenance continuity, not public legitimacy or reward continuity.",
        "No runtime implementation of promotion logic is ratified in Phase 353.",
    ):
        assert token in text


def test_evidence_boundary_tokens_are_explicit() -> None:
    text = _read(EVIDENCE_PATH)
    for token in (
        "Promotion changes visibility only by creating a successor public node plus a promotion_receipt, never by mutating the original node.",
        "The original private node remains immutable after promotion.",
        "promotion_receipt must carry: original node CID, public successor node CID, disclosed lineage reference, epoch of promotion.",
        "No automatic public corroboration or reuse credit carry-forward is allowed.",
        "No automatic reputation carry-forward is allowed.",
        "A promoted public successor node starts in proposed validation_state; it does not inherit the original node's validation_state.",
        "CDL-034 remains authoritative for reserved-field collision rules and is not weakened here.",
        "Promotion preserves provenance continuity, not public legitimacy or reward continuity.",
    ):
        assert token in text


def test_phase_344_historical_prelock_hardening_patch_is_active() -> None:
    phase_344_text = _read(PHASE_344_TEST_PATH)
    assert 'assert EXPECTED_ROW in historical_text' in phase_344_text
    assert 'assert rows["CDL-038"]["status"] == "open"' not in phase_344_text
    assert (
        'assert row["current_candidate"] == "successor-node plus promotion_receipt without automatic reputation carry-forward (proposed)"'
        not in phase_344_text
    )
    assert 'assert "ratified_phase" not in row' in phase_344_text
    assert 'assert "ratified_date" not in row' in phase_344_text
    assert 'assert "evidence_document" not in row' in phase_344_text
    assert 'assert historical_rows["CDL-038"]["status"] == "open"' in phase_344_text
    assert 'assert historical_rows["CDL-037"]["status"] == "open"' in phase_344_text
    assert '_decision_log_text_at_ref(_resolve_phase_344_commit_ref())' in phase_344_text
    assert '# The Phase-344 `CDL-038` row is a historical prelock reference.' in phase_344_text


def test_decision_log_cdl_038_is_ratified_with_expected_metadata_and_scope() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    row = rows["CDL-038"]
    assert row["status"] == "ratified"
    assert row["current_candidate"] == "successor-node plus promotion_receipt without automatic reputation carry-forward"
    assert row["ratified_phase"] == "353"
    ratified_date = datetime.date.fromisoformat(row["ratified_date"])
    assert ratified_date.isoformat() == row["ratified_date"]
    assert row["evidence_document"] == str(EVIDENCE_PATH)
    assert_no_non_target_rows_marked_with_phase(rows, phase="353", target_cdls={"CDL-038"})


def test_mutation_scope_guardrail_allows_only_ratification_fields_for_cdl_038() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    old_register = _mini_register(_PRE_353_CDL_038_ROW)
    new_register = _mini_register(_register_row_text(rows["CDL-038"]))
    assert_only_allowed_row_mutations(
        old_register,
        new_register,
        cdl_id="CDL-038",
        allowed_fields=_ALLOWED_FIELDS,
    )


def test_full_non_target_row_mutation_guard_for_phase_353() -> None:
    commit_ref = _resolve_phase_353_commit_ref()
    old_text = _decision_log_text_at_ref(f"{commit_ref}^1")
    new_text = _decision_log_text_at_ref(commit_ref)
    old_rows = parse_decision_register_rows(old_text)
    new_rows = parse_decision_register_rows(new_text)
    assert set(old_rows.keys()) == set(new_rows.keys())

    target_old = _mini_register(_register_row_text(old_rows["CDL-038"]))
    target_new = _mini_register(_register_row_text(new_rows["CDL-038"]))
    assert_only_allowed_row_mutations(
        target_old,
        target_new,
        cdl_id="CDL-038",
        allowed_fields=_ALLOWED_FIELDS,
    )

    for cdl_id in old_rows:
        if cdl_id == "CDL-038":
            continue
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_353"


def test_phase_353_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_353_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
