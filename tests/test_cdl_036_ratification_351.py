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
    "docs/specs/ilc_cdl_036_node_dissemination_header_and_fetch_contract_ratification_evidence_351_v0.1.md"
)
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_342_TEST_PATH = Path("tests/test_cdl_036_open_and_node_dissemination_header_fetch_prelock_342.py")
PHASE_343_TEST_PATH = Path("tests/test_cdl_037_open_and_executable_node_safety_contract_prelock_343.py")
PHASE_351_COMMIT_SUBJECT = "docs(g8): phase 351 cdl-036 ratification"

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

_PRE_351_CDL_036_ROW = (
    "| CDL-036 | ADM-001 / CDL-024 | Node dissemination header, payload fetch contract, and transport boundary | "
    "open | full-payload push broadcast, header-first dissemination with fixed orderer, header-first dissemination with CID-addressed pull fetch | "
    "header-first dissemination with CID-addressed pull fetch (proposed) | header schema, fetch semantics, signature scope |"
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


def _resolve_phase_351_commit_ref() -> str:
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
        if subject.strip() == PHASE_351_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(EVIDENCE_PATH),
        "tests/test_cdl_036_ratification_351.py",
        str(PHASE_342_TEST_PATH),
        str(PHASE_343_TEST_PATH),
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_351_commit_subject_present_but_no_qualifying_ratification_commit")
    raise AssertionError("phase_351_commit_not_present_in_local_history")


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
        "header-first dissemination with CID-addressed pull fetch",
        "full-payload push broadcast",
        "header-first dissemination with fixed orderer",
        "docs/specs/ilc_cdl_036_node_dissemination_header_and_fetch_contract_evidence_prelock_342_v0.1.md",
        "docs/specs/ilc_cdl_034_node_schema_core_envelope_and_reserved_fields_ratification_evidence_349_v0.1.md",
        "docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_ratification_evidence_350_v0.1.md",
        "docs/specs/ilc_integration_coherence_report_346_v0.1.md",
        "docs/specs/ilc_antigravity_context_capsule_v0.9.md",
        "docs/specs/ilc_node_schema_ratification_readiness_report_346_v0.1.md",
        "docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md",
        "docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md",
        "Section 6 of the Phase-342 prelock artifact is authoritative for this ratification lane when it is more specific than the compressed CDL row shorthand.",
        "transport header field set",
        "push/pull dissemination conclusion and fetch-boundary note",
        "fetch API and idempotence note",
        "signature scope and payload-reference integrity note",
        "visibility/channel dissemination rule note",
        "orderer-agnostic boundary note",
        "header-first dissemination",
        "CID-addressed pull fetch",
        "content-addressed verification before interpretation",
        "Transport Envelope remains separate from Authored Payload Envelope and Protocol Interpretation Envelope.",
        "candidate header field set: node_id, creator_agent_id, epistemic_type, visibility, channel, epoch_created, payload_cid, signature",
        "payload_cid",
        "The header signature must commit to the payload reference.",
        "signature scope covers header fields plus payload_cid.",
        "header-first dissemination does not authorize full-payload push as the default transport rule.",
        "ILC leans pull, not push.",
        "pull-dominant with soft push-signals",
        "retry and idempotence remain fetch-contract obligations, not authored-payload semantics.",
        "visibility and channel remain routing inputs, not authored-payload mutability permissions.",
        "visibility/channel interaction belongs to Transport Envelope routing semantics only insofar as dissemination policy is concerned.",
        "Narwhal/Tusk/Bullshark remains a reference pattern, not a locked constitutional choice.",
        "No permanent validator-core orderer is ratified in Phase 351.",
        "No transport binding implementation is ratified in Phase 351.",
        "CDL-024 remains authoritative for transport-agnostic wire bindings and is not weakened here.",
        "Phase 343 must keep executable-node transport concerns subordinate to the CDL-036 header/fetch contract.",
        "No runtime implementation of CDL-036 dissemination or fetch logic is ratified in Phase 351.",
    ):
        assert token in text


def test_phase_342_historical_prelock_hardening_patch_is_active() -> None:
    phase_342_text = _read(PHASE_342_TEST_PATH)
    assert 'assert EXPECTED_ROW in historical_text' in phase_342_text
    assert 'assert rows["CDL-036"]["status"] == "open"' not in phase_342_text
    assert (
        'assert row["current_candidate"] == "header-first dissemination with CID-addressed pull fetch (proposed)"'
        not in phase_342_text
    )
    assert 'assert "ratified_phase" not in row' in phase_342_text
    assert 'assert "ratified_date" not in row' in phase_342_text
    assert 'assert "evidence_document" not in row' in phase_342_text
    assert '_decision_log_text_at_ref(_resolve_phase_342_commit_ref())' in phase_342_text
    assert '# The Phase-342 `CDL-036` row is a historical prelock reference.' in phase_342_text


def test_phase_343_cross_cdl_hardening_patch_is_active() -> None:
    phase_343_text = _read(PHASE_343_TEST_PATH)
    assert 'assert rows["CDL-036"]["status"] == "open"' not in phase_343_text
    assert (
        'historical_rows = parse_decision_register_rows(' in phase_343_text
    )
    assert (
        '_decision_log_text_at_ref(_resolve_phase_343_commit_ref())' in phase_343_text
    )


def test_decision_log_cdl_036_is_ratified_with_expected_metadata_and_scope() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    row = rows["CDL-036"]
    assert row["status"] == "ratified"
    assert row["current_candidate"] == "header-first dissemination with CID-addressed pull fetch"
    assert row["ratified_phase"] == "351"
    ratified_date = datetime.date.fromisoformat(row["ratified_date"])
    assert ratified_date.isoformat() == row["ratified_date"]
    assert row["evidence_document"] == str(EVIDENCE_PATH)
    assert_no_non_target_rows_marked_with_phase(rows, phase="351", target_cdls={"CDL-036"})


def test_mutation_scope_guardrail_allows_only_ratification_fields_for_cdl_036() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    old_register = _mini_register(_PRE_351_CDL_036_ROW)
    new_register = _mini_register(_register_row_text(rows["CDL-036"]))
    assert_only_allowed_row_mutations(
        old_register,
        new_register,
        cdl_id="CDL-036",
        allowed_fields=_ALLOWED_FIELDS,
    )


def test_full_non_target_row_mutation_guard_for_phase_351() -> None:
    commit_ref = _resolve_phase_351_commit_ref()
    old_text = _decision_log_text_at_ref(f"{commit_ref}^1")
    new_text = _decision_log_text_at_ref(commit_ref)
    old_rows = parse_decision_register_rows(old_text)
    new_rows = parse_decision_register_rows(new_text)
    assert set(old_rows.keys()) == set(new_rows.keys())

    target_old = _mini_register(_register_row_text(old_rows["CDL-036"]))
    target_new = _mini_register(_register_row_text(new_rows["CDL-036"]))
    assert_only_allowed_row_mutations(
        target_old,
        target_new,
        cdl_id="CDL-036",
        allowed_fields=_ALLOWED_FIELDS,
    )

    for cdl_id in old_rows:
        if cdl_id == "CDL-036":
            continue
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_351"


def test_phase_351_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_351_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
