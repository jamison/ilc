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


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
EVIDENCE_PATH = Path("docs/specs/ilc_cdl_042_agent_identity_namespace_ratification_evidence_407_v0.1.md")
PHASE_403_TEST_PATH = Path("tests/test_phase_403_cdl_042_prelock_hardening.py")
PHASE_407_SUBJECT_TOKEN = "phase 407 cdl-042 agent identity namespace ratification"

REQUIRED_HEADINGS = (
    "## 1. Purpose and scope",
    "## 2. Ratified decision",
    "## 3. Evidence basis",
    "## 4. Section-7 ratification readiness evidence checklist satisfaction",
    "## 5. Agent identity derivation specification",
    "## 6. Scope boundary and dependency closure",
    "## 7. D2e Agent SDK carry-forward binding",
    "## 8. Out-of-scope and deferred tracks",
    "## 9. Canonical anchors",
)

REQUIRED_TOKENS = (
    "CDL-042 is ratified with the globally flat key-derived agent_id candidate.",
    "agent_id is deterministically derived from the canonical_root_key public bytes as the CDL-001 trust-root anchor, with no external registry or coordinator required.",
    "CDL-001 signer-lineage continuity is preserved: agent_id is bound to the canonical_root_key public bytes; operational_signer_key rotation does not change agent_id.",
    "D2e Agent SDK implementation in Phases 410-411 is now authorized to use the ratified CDL-042 agent_id derivation specification.",
    "Domain-prefixed namespace with operator-scoped agent_id is rejected because it requires externally assigned operator_id, introducing a registry or coordination step that violates the no-central-registry requirement.",
    "Hierarchical namespace with epoch-scoped key rotation chain is rejected because it changes agent_id at each key rotation epoch, breaking identity continuity across CDL-001 signer-lineage transitions.",
    "No D2e identity implementation may substitute operator-scoped, epoch-scoped, registry-issued, or runtime-discretionary identity derivation without opening a new constitutional lane.",
)

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

_PRE_407_CDL_042_ROW = (
    "| CDL-042 | ADM-003 / CDL-040 / CDL-034 / CDL-001 | Agent identity namespace and self-sovereign "
    "ID derivation | open | globally flat namespace with key-derived agent_id, domain-prefixed namespace "
    "with operator-scoped agent_id, hierarchical namespace with epoch-scoped key rotation chain | "
    "globally flat namespace with key-derived agent_id (proposed) | CDL-001 signing-key anchor, ADM-003 "
    "agent-architecture dependency clause, CDL-040 identity-envelope dependency clause, "
    "multi-agent-per-operator uniqueness constraint |"
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


def _read_file_at_ref(ref: str, path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"unable_to_read_file_at_ref:{ref}:{path}:{result.stderr.strip()}")
    return result.stdout


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_407_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )

    matching: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if PHASE_407_SUBJECT_TOKEN in subject.lower():
            matching.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(EVIDENCE_PATH),
        "tests/test_phase_407_cdl_042_ratification.py",
        "tests/test_phase_403_cdl_042_prelock_hardening.py",
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching:
        raise AssertionError("phase_407_commit_subject_present_but_no_ratification_mutation_commit")
    raise AssertionError("phase_407_commit_not_present_in_local_history")


def test_ratification_evidence_contains_required_headings_and_tokens() -> None:
    assert EVIDENCE_PATH.exists()
    text = _read(EVIDENCE_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text
    for token in REQUIRED_TOKENS:
        assert token in text


def test_cdl_042_row_is_ratified_with_correct_fields() -> None:
    text = _read(DECISION_LOG_PATH)
    rows = parse_decision_register_rows(text)
    row = rows["CDL-042"]
    assert row["status"] == "ratified"
    assert row["current_candidate"] == "globally flat namespace with key-derived agent_id"
    assert row["ratified_phase"] == "407"
    ratified_date = datetime.date.fromisoformat(row["ratified_date"])
    assert ratified_date.isoformat() == "2026-03-13"
    assert row["evidence_document"] == str(EVIDENCE_PATH)
    assert "globally flat namespace with key-derived agent_id (proposed)" not in text
    assert "globally flat namespace with key-derived agent_id" in text
    assert_no_non_target_rows_marked_with_phase(rows, phase="407", target_cdls={"CDL-042"})


def test_cdl_045_and_cdl_046_rows_unchanged() -> None:
    # The Phase-407 `CDL-045` and `CDL-046` neighbor-state checks are historical ratification references.
    historical_text = _read_file_at_ref(_resolve_phase_407_commit_ref(), str(DECISION_LOG_PATH))
    historical_rows = parse_decision_register_rows(historical_text)
    assert historical_rows["CDL-045"]["status"] == "open"
    assert historical_rows["CDL-046"]["status"] == "open"


def test_phase_403_cdl_042_row_open_assertion_is_hardened() -> None:
    text = _read(PHASE_403_TEST_PATH)
    assert '# The Phase-403 `CDL-042` row is a historical prelock reference.' in text
    assert text.count("_read_file_at_ref(_resolve_phase_403_commit_ref(), str(DECISION_LOG_PATH))") >= 2
    assert "rows = parse_decision_register_rows(historical_text)" in text
    assert "EXPECTED_CDL_042_ROW in historical_text" in text
    assert 'rows["CDL-042"]["status"] == "open"' in text
    assert text.count("_read(DECISION_LOG_PATH)") == 1


def test_cdl_042_register_order_preserved_after_ratification() -> None:
    lines = _read(DECISION_LOG_PATH).splitlines()
    cdl_044_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-044 "))
    cdl_042_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-042 "))
    cdl_045_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-045 "))
    assert cdl_042_index == cdl_044_index + 1
    assert cdl_045_index == cdl_042_index + 1


def test_phase_407_commit_touches_exactly_required_paths() -> None:
    commit_ref = _resolve_phase_407_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    required = {
        str(DECISION_LOG_PATH),
        str(EVIDENCE_PATH),
        "tests/test_phase_407_cdl_042_ratification.py",
        "tests/test_phase_403_cdl_042_prelock_hardening.py",
    }
    assert required.issubset(changed)
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)


def test_phase_407_commit_no_non_cdl_042_row_mutation() -> None:
    commit_ref = _resolve_phase_407_commit_ref()
    old_rows = parse_decision_register_rows(_read_file_at_ref(f"{commit_ref}^1", str(DECISION_LOG_PATH)))
    new_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert set(old_rows) == set(new_rows)

    target_old = _mini_register(_register_row_text(old_rows["CDL-042"]))
    target_new = _mini_register(_register_row_text(new_rows["CDL-042"]))
    assert_only_allowed_row_mutations(
        target_old,
        target_new,
        cdl_id="CDL-042",
        allowed_fields=_ALLOWED_FIELDS,
    )

    for cdl_id in old_rows:
        if cdl_id == "CDL-042":
            continue
        assert old_rows[cdl_id] == new_rows[cdl_id], f"non_target_row_mutated:{cdl_id}"

    assert old_rows["CDL-042"]["status"] == "open"
    assert new_rows["CDL-042"]["status"] == "ratified"
