from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_441_449_sequence_lock_v0.1.md")
OPENING_STUB_PATH = Path("docs/specs/ilc_cdl_051_constitutional_consensus_and_epoch_finality_opening_stub_441_v0.1.md")
PHASE_441_TEST_PATH = Path("tests/test_phase_441_cdl_051_opening.py")
PHASE_441_SUBJECT_TOKEN = "phase 441 window sequence lock and cdl-051 opening"
MAIN_COMMIT_PATHS = {
    str(DECISION_LOG_PATH),
    str(SEQUENCE_LOCK_PATH),
    str(OPENING_STUB_PATH),
    str(PHASE_441_TEST_PATH),
}
EXPECTED_CDL_051_ROW = (
    "| CDL-051 | CDL-V3 / CDL-039 / CDL-040 / CDL-045 | constitutional consensus and epoch-finality prototype lane for quorum-state, finality, and deterministic fork resolution | open | defer consensus lane indefinitely, minimal epoch-state and quorum-record constitutional contract with deterministic fork/tie-break rules, full production consensus architecture with storage-format cutover | minimal epoch-state and quorum-record constitutional contract with deterministic fork/tie-break rules (proposed) | consensus state-machine prelock, adversarial scenario matrix, terminology lock, prototype-default provenance notes, evidence-source ladder |"
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


def _resolve_phase_441_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )

    matching: list[str] = []
    for line in result.stdout.splitlines():
        if "	" not in line:
            continue
        commit_hash, subject = line.split("	", 1)
        if PHASE_441_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)

    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if changed_paths == MAIN_COMMIT_PATHS:
            return commit_ref

    if matching:
        raise AssertionError("phase_441_commit_subject_present_but_no_constitutional_opening_commit")
    raise AssertionError("phase_441_commit_not_present_in_local_history")


def _decision_log_text_at_ref(ref: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{ref}:{DECISION_LOG_PATH}"],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"unable_to_read_decision_log_at_ref:{ref}:{result.stderr.strip()}")
    return result.stdout


def test_sequence_lock_exists_and_contains_required_headings_and_tokens() -> None:
    assert SEQUENCE_LOCK_PATH.exists()
    text = _read(SEQUENCE_LOCK_PATH)

    for heading in (
        "## 1. Window identity and scope",
        "## 2. Inputs and closure inheritance",
        "## 3. CDL-051 opening authorization and constitutional obligation",
        "## 4. Locked phase table (441-449 baseline)",
        "## 5. Constitutional-first sequencing and Treasury non-authorization",
        "## 6. Consensus evidence discipline and prototype-default boundary",
        "## 7. Sensitivity mapping and release-engineering separation",
        "## 8. Canonical anchors and non-goals",
    ):
        assert heading in text

    for token in (
        "Window 441-449 is the Constitutional Consensus and Epoch-Finality Block.",
        "This baseline locks a 9-phase window: 441-449.",
        "CDL-049 remains ratified at Window 441 entry.",
        "CDL-050 remains unopened and not pre-authorized at Window 441 entry.",
        "CDL-051 is the first constitutional action of Window 441.",
        "Window 441-449 constitutionally grounds consensus before runtime implementation.",
        "Phase 442 must publish an evidence-source ladder: ratified CDL and active handoffs first, then active specs/runtime artifacts, then filtered historical extracts, with raw Z_Past_Chats treated as hypothesis input only.",
        "Consensus constants and rule-like defaults introduced before ratification must remain clearly marked as prototype-local rather than constitutional law.",
        "Release engineering packaging/bootstrap remains a parallel administrative track and does not consume numbered phases in this baseline.",
        "CDL-050 remains notionally reserved for the Treasury P_e lane if that lane is ever constitutionally opened.",
        "Capsule v1.8 is the active context capsule at Window 441 entry.",
        "Phase 441 supersedes the Phase-440 next-phase pointer recorded in capsule v1.8.",
    ):
        assert token in text

    assert "| Order | Phase | Topic | Character | Sensitivity |" in text
    for row in (
        "| 1 | 441 | Sequence lock + CDL-051 opening | Foundation / Constitutional | SENSITIVE |",
        "| 2 | 442 | CDL-051 prelock hardening | Constitutional | SENSITIVE |",
        "| 3 | 443 | CDL-051 ratification | Constitutional | SENSITIVE |",
        "| 4 | 444 | Consensus runtime I: epoch-state and quorum-record surfaces | Runtime | SENSITIVE |",
        "| 5 | 445 | Consensus runtime II: deterministic finality evaluator and fork-resolution rules | Runtime | SENSITIVE |",
        "| 6 | 446 | Consensus runtime III: harness integration, network-bridge exercise, and bounded hotspot cleanup | Runtime / Tooling | SENSITIVE |",
        "| 7 | 447 | Consensus findings memo and adversarial regression hardening | Review / Stabilization | SENSITIVE |",
        "| 8 | 448 | Coherence + capsule v1.9 | Synthesis | NON-SENSITIVE |",
        "| 9 | 449 | Closure gate + 450+ handoff | Gate | SENSITIVE |",
    ):
        assert row in text

    for non_goal in (
        "no runtime implementation of consensus logic",
        "no `CDL-050` opening",
        "no DAG-CBOR production cutover",
        "no packaging/bootstrap merge work",
    ):
        assert non_goal in text


def test_cdl_051_opening_stub_exists_and_contains_required_headings_and_tokens() -> None:
    assert OPENING_STUB_PATH.exists()
    text = _read(OPENING_STUB_PATH)

    for heading in (
        "## 1. Purpose and scope",
        "## 2. CDL-051 opening state",
        "## 3. Inherited constitutional anchors",
        "## 4. Window 441-449 sequencing note",
        "## 5. Evidence discipline and prototype-default boundary",
        "## 6. Out-of-scope and deferred tracks",
        "## 7. Canonical anchors",
    ):
        assert heading in text

    for token in (
        "status: open",
        "CDL-051 opens as the constitutional consensus and epoch-finality lane for a deterministic, auditable quorum-state prototype.",
        "CDL-051 inherits quorum-diversity, brokerless transport, admission control, and emergency-response constraints from CDL-V3, CDL-039, CDL-040, and CDL-045 without ratifying a new finality engine in Phase 441.",
        "Phase 442 is the targeted prelock hardening lane for CDL-051.",
        "Phase 443 is the targeted ratification lane for CDL-051.",
        "CDL-050 remains unopened and unaffected by CDL-051.",
        "CDL-051 does not authorize runtime mutation in Phase 441.",
        "Phase 442 must define conflict-state terminology, evidence-source ladder, prototype-default provenance, and explicit non-goals before runtime implementation begins.",
    ):
        assert token in text


def test_decision_log_contains_exact_cdl_051_opening_row() -> None:
    # The Phase-441 CDL-051 opening row is a historical reference.
    text = _decision_log_text_at_ref(_resolve_phase_441_commit_ref())
    rows = parse_decision_register_rows(text)
    assert EXPECTED_CDL_051_ROW in text
    assert rows["CDL-051"]["status"] == "open"


def test_cdl_051_row_appended_after_cdl_049_in_correct_order() -> None:
    # The Phase-441 CDL register order is a historical reference.
    lines = _decision_log_text_at_ref(_resolve_phase_441_commit_ref()).splitlines()
    cdl_049_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-049 "))
    cdl_051_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-051 "))
    assert cdl_051_index == cdl_049_index + 1


def test_decision_log_inventory_still_shows_cdl_049_ratified_and_cdl_050_absent() -> None:
    # The Phase-441 opening inventory state is a historical reference.
    rows = parse_decision_register_rows(_decision_log_text_at_ref(_resolve_phase_441_commit_ref()))
    assert rows["CDL-049"]["status"] == "ratified"
    assert "CDL-050" not in rows
    assert rows["CDL-051"]["status"] == "open"


def test_phase_441_commit_additive_only_non_target_shield() -> None:
    commit_ref = _resolve_phase_441_commit_ref()
    old_rows = parse_decision_register_rows(_decision_log_text_at_ref(f"{commit_ref}^1"))
    new_rows = parse_decision_register_rows(_decision_log_text_at_ref(commit_ref))
    added_ids = set(new_rows) - set(old_rows)
    assert added_ids == {"CDL-051"}
    for cdl_id in old_rows:
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_441"


def test_phase_441_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_441_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
