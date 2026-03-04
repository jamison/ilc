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
    "docs/specs/ilc_cdl_037_executable_node_descriptor_and_safety_contract_ratification_evidence_352_v0.1.md"
)
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_343_TEST_PATH = Path("tests/test_cdl_037_open_and_executable_node_safety_contract_prelock_343.py")
PHASE_344_TEST_PATH = Path("tests/test_cdl_038_open_and_promotion_continuity_prelock_344.py")
PHASE_352_COMMIT_SUBJECT = "docs(g8): phase 352 cdl-037 ratification"

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

_PRE_352_CDL_037_ROW = (
    "| CDL-037 | CDL-034 / CDL-V7 | Executable node descriptor, safety contract, and agent-side sandboxing | "
    "open | raw executable payload embedded in authored envelope, structured descriptor without sandboxing, structured descriptor with sandboxed runtime binding | "
    "structured descriptor with sandboxed runtime binding (proposed) | executable descriptor schema, safety contract model, sandbox boundary semantics |"
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


def _resolve_phase_352_commit_ref() -> str:
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
        if subject.strip() == PHASE_352_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(EVIDENCE_PATH),
        "tests/test_cdl_037_ratification_352.py",
        str(PHASE_343_TEST_PATH),
        str(PHASE_344_TEST_PATH),
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_352_commit_subject_present_but_no_qualifying_ratification_commit")
    raise AssertionError("phase_352_commit_not_present_in_local_history")


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
        "structured descriptor with sandboxed runtime binding",
        "raw executable payload embedded in authored envelope",
        "structured descriptor without sandboxing",
        "docs/specs/ilc_cdl_037_executable_node_descriptor_and_safety_contract_evidence_prelock_343_v0.1.md",
        "docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_ratification_evidence_349_v0.1.md",
        "docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_ratification_evidence_350_v0.1.md",
        "docs/specs/ilc_cdl_036_node_dissemination_header_and_fetch_contract_ratification_evidence_351_v0.1.md",
        "docs/specs/ilc_integration_coherence_report_346_v0.1.md",
        "docs/specs/ilc_antigravity_context_capsule_v0.9.md",
        "docs/specs/ilc_node_schema_ratification_readiness_report_346_v0.1.md",
        "docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md",
        "docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md",
        "docs/specs/ilc_popper_ilc_analysis_v0.1.md",
        "Section 6 of the Phase-343 prelock artifact is authoritative for this ratification lane when it is more specific than the compressed CDL row shorthand.",
        "executable descriptor candidate field set",
        "sandboxed runtime binding contract",
        "safety contract model and genesis-trust boundary",
        "CDL-V7 decomposition gate for executable descriptors",
        "CDL-034 authored-envelope boundary preservation note",
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
        "CDL-035 remains authoritative for validation_state semantics and is not weakened here.",
        "CDL-036 remains authoritative for transport boundary semantics and is not weakened here.",
        "Phase 353 must keep promotion continuity subordinate to the ratified CDL-037 executable-node contract.",
        "No runtime implementation of executable-node logic is ratified in Phase 352.",
    ):
        assert token in text


def test_phase_343_historical_prelock_hardening_patch_is_active() -> None:
    phase_343_text = _read(PHASE_343_TEST_PATH)
    assert 'assert EXPECTED_ROW in historical_text' in phase_343_text
    assert 'assert rows["CDL-037"]["status"] == "open"' not in phase_343_text
    assert (
        'assert row["current_candidate"] == "structured descriptor with sandboxed runtime binding (proposed)"'
        not in phase_343_text
    )
    assert 'assert "ratified_phase" not in row' in phase_343_text
    assert 'assert "ratified_date" not in row' in phase_343_text
    assert 'assert "evidence_document" not in row' in phase_343_text
    assert '_decision_log_text_at_ref(_resolve_phase_343_commit_ref())' in phase_343_text
    assert '# The Phase-343 `CDL-037` row is a historical prelock reference.' in phase_343_text


def test_phase_344_cross_cdl_hardening_patch_is_active() -> None:
    phase_344_text = _read(PHASE_344_TEST_PATH)
    assert 'assert rows["CDL-037"]["status"] == "open"' not in phase_344_text
    assert 'assert rows["CDL-038"]["status"] == "open"' not in phase_344_text
    assert (
        'historical_rows = parse_decision_register_rows(' in phase_344_text
    )
    assert (
        '_decision_log_text_at_ref(_resolve_phase_344_commit_ref())' in phase_344_text
    )
    assert 'assert historical_rows["CDL-038"]["status"] == "open"' in phase_344_text
    assert 'assert "ratified_phase" not in historical_rows["CDL-038"]' in phase_344_text
    assert 'assert "ratified_date" not in historical_rows["CDL-038"]' in phase_344_text
    assert 'assert "evidence_document" not in historical_rows["CDL-038"]' in phase_344_text


def test_decision_log_cdl_037_is_ratified_with_expected_metadata_and_scope() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    row = rows["CDL-037"]
    assert row["status"] == "ratified"
    assert row["current_candidate"] == "structured descriptor with sandboxed runtime binding"
    assert row["ratified_phase"] == "352"
    ratified_date = datetime.date.fromisoformat(row["ratified_date"])
    assert ratified_date.isoformat() == row["ratified_date"]
    assert row["evidence_document"] == str(EVIDENCE_PATH)
    assert_no_non_target_rows_marked_with_phase(rows, phase="352", target_cdls={"CDL-037"})


def test_mutation_scope_guardrail_allows_only_ratification_fields_for_cdl_037() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    old_register = _mini_register(_PRE_352_CDL_037_ROW)
    new_register = _mini_register(_register_row_text(rows["CDL-037"]))
    assert_only_allowed_row_mutations(
        old_register,
        new_register,
        cdl_id="CDL-037",
        allowed_fields=_ALLOWED_FIELDS,
    )


def test_full_non_target_row_mutation_guard_for_phase_352() -> None:
    commit_ref = _resolve_phase_352_commit_ref()
    old_text = _decision_log_text_at_ref(f"{commit_ref}^1")
    new_text = _decision_log_text_at_ref(commit_ref)
    old_rows = parse_decision_register_rows(old_text)
    new_rows = parse_decision_register_rows(new_text)
    assert set(old_rows.keys()) == set(new_rows.keys())

    target_old = _mini_register(_register_row_text(old_rows["CDL-037"]))
    target_new = _mini_register(_register_row_text(new_rows["CDL-037"]))
    assert_only_allowed_row_mutations(
        target_old,
        target_new,
        cdl_id="CDL-037",
        allowed_fields=_ALLOWED_FIELDS,
    )

    for cdl_id in old_rows:
        if cdl_id == "CDL-037":
            continue
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_352"


def test_phase_352_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_352_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
