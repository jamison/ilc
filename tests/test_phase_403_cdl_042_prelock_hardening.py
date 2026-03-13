from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
HARDENING_PATH = Path("docs/specs/ilc_cdl_042_agent_identity_namespace_prelock_hardening_403_v0.1.md")
CDL_042_OPEN_PRELOCK_402_PATH = Path("docs/specs/ilc_cdl_042_agent_identity_namespace_open_prelock_402_v0.1.md")
EXPECTED_CDL_042_ROW = (
    "| CDL-042 | ADM-003 / CDL-040 / CDL-034 / CDL-001 | Agent identity namespace and self-sovereign "
    "ID derivation | open | globally flat namespace with key-derived agent_id, domain-prefixed namespace "
    "with operator-scoped agent_id, hierarchical namespace with epoch-scoped key rotation chain | "
    "globally flat namespace with key-derived agent_id (proposed) | CDL-001 signing-key anchor, ADM-003 "
    "agent-architecture dependency clause, CDL-040 identity-envelope dependency clause, "
    "multi-agent-per-operator uniqueness constraint |"
)
PHASE_403_SUBJECT_TOKEN = "phase 403 cdl-042 agent identity namespace prelock hardening"
REQUIRED_HEADINGS = (
    "## 1. Purpose and hardening scope",
    "## 2. CDL-042 current state and Phase-402 opening inheritance",
    "## 3. Candidate option discrimination",
    "## 4. Proposed candidate: globally flat key-derived agent_id specification",
    "## 5. Namespace collision resistance and uniqueness at scale",
    "## 6. Signer-lineage compatibility and key rotation semantics",
    "## 7. D2e SDK integration binding and Phase 407 ratification readiness",
    "## 8. Out-of-scope and deferred tracks",
    "## 9. Canonical anchors",
)
REQUIRED_TOKENS = (
    "status: open",
    "CDL-042 prelock hardening confirms the proposed candidate: globally flat namespace with key-derived agent_id.",
    "agent_id is deterministically derived from the canonical_root_key public bytes as the CDL-001 trust-root anchor, with no external registry or coordinator required.",
    "Namespace collision probability at target network scale is negligible under the proposed derivation scheme.",
    "CDL-001 signer-lineage continuity is preserved: agent_id is bound to the canonical_root_key public bytes; operational_signer_key rotation does not change agent_id.",
    "Domain-prefixed namespace with operator-scoped agent_id is rejected because it requires externally assigned operator_id, introducing a registry or coordination step that violates the no-central-registry requirement.",
    "Hierarchical namespace with epoch-scoped key rotation chain is rejected because it changes agent_id at each key rotation epoch, breaking identity continuity across CDL-001 signer-lineage transitions.",
    "D2e Agent SDK implementation in Phases 410-411 is bound to the CDL-042 agent_id derivation specification locked in this hardening artifact.",
    "Phase 407 is the targeted CDL-042 ratification lane; this hardening artifact constitutes the primary prelock evidence.",
    "No CDL row mutation occurs in Phase 403.",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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


def _resolve_phase_403_commit_ref() -> str:
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
        if PHASE_403_SUBJECT_TOKEN in subject.lower():
            matching.append(commit_hash)

    required_paths = {
        str(HARDENING_PATH),
        "tests/test_phase_403_cdl_042_prelock_hardening.py",
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching:
        raise AssertionError("phase_403_commit_subject_present_but_no_hardening_artifact_commit")
    raise AssertionError("phase_403_commit_not_present_in_local_history")


def test_hardening_artifact_exists_and_contains_required_headings_and_tokens() -> None:
    assert HARDENING_PATH.exists()
    text = _read(HARDENING_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text
    for token in REQUIRED_TOKENS:
        assert token in text


def test_cdl_042_row_remains_open_and_matches_expected_opening_row() -> None:
    text = _read(DECISION_LOG_PATH)
    rows = parse_decision_register_rows(text)
    assert rows["CDL-042"]["status"] == "open"
    assert EXPECTED_CDL_042_ROW in text


def test_phase_402_opening_prelock_stub_is_preserved() -> None:
    assert CDL_042_OPEN_PRELOCK_402_PATH.exists()
    text = _read(CDL_042_OPEN_PRELOCK_402_PATH)
    assert "Phase-403 is the targeted prelock hardening lane for CDL-042." in text
    assert "status: open" in text


def test_cdl_042_and_cdl_045_register_order_preserved() -> None:
    lines = _read(DECISION_LOG_PATH).splitlines()
    cdl_044_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-044 "))
    cdl_042_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-042 "))
    cdl_045_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-045 "))
    assert cdl_042_index == cdl_044_index + 1
    assert cdl_045_index == cdl_042_index + 1


def test_cdl_042_has_no_premature_ratification_metadata() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows["CDL-042"]["status"] != "ratified"
    assert rows["CDL-042"].get("ratified_date") is None


def test_phase_403_commit_no_cdl_row_mutation_and_stub_immutable() -> None:
    commit_ref = _resolve_phase_403_commit_ref()
    old_rows = parse_decision_register_rows(_read_file_at_ref(f"{commit_ref}^1", str(DECISION_LOG_PATH)))
    new_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert set(old_rows) == set(new_rows)
    for cdl_id in old_rows:
        assert old_rows[cdl_id] == new_rows[cdl_id]

    old_stub = _read_file_at_ref(f"{commit_ref}^1", str(CDL_042_OPEN_PRELOCK_402_PATH))
    new_stub = _read_file_at_ref(commit_ref, str(CDL_042_OPEN_PRELOCK_402_PATH))
    assert old_stub == new_stub, "phase_403_commit_modified_phase_402_opening_stub_unlawfully"


def test_phase_403_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_403_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
