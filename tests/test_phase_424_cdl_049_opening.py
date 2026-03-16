from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_424_433_sequence_lock_v0.1.md")
OPENING_STUB_PATH = Path("docs/specs/ilc_cdl_049_bounded_existential_alignment_opening_stub_424_v0.1.md")
POPPERIAN_GATE_PATH = Path("ilc_core/consensus/popperian_gate_runtime.py")
PHASE_424_SUBJECT_TOKEN = "phase 424 window sequence lock and cdl-049 opening"
EXPECTED_CDL_049_ROW = (
    "| CDL-049 | CDL-V7 | bounded-existential claim-form alignment: narrow unqualified existential to "
    "bounded_existential in popperian_gate_runtime and active Popperian review corpus | open | leave "
    "runtime and corpus vocabulary unchanged, narrow existential to bounded_existential in runtime and active "
    "corpus, replace popperian_gate_runtime module entirely | narrow existential to bounded_existential in "
    "runtime and active corpus (proposed) | Phase 417 MODERATE finding evidence, popperian_gate_runtime "
    "_ADMISSIBLE_CLAIM_FORMS current vocabulary, ilc_popper_ilc_analysis active-section vocabulary audit |"
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


def _resolve_phase_424_commit_ref() -> str:
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
        if PHASE_424_SUBJECT_TOKEN in subject.lower():
            matching.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(SEQUENCE_LOCK_PATH),
        str(OPENING_STUB_PATH),
        "tests/test_phase_424_cdl_049_opening.py",
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching:
        raise AssertionError("phase_424_commit_subject_present_but_no_constitutional_opening_commit")
    raise AssertionError("phase_424_commit_not_present_in_local_history")


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


def test_sequence_lock_exists_and_contains_required_headings_and_tokens() -> None:
    assert SEQUENCE_LOCK_PATH.exists()
    text = _read(SEQUENCE_LOCK_PATH)

    for heading in (
        "## 1. Window identity and scope",
        "## 2. Inputs and closure inheritance",
        "## 3. CDL-049 opening authorization and constitutional obligation",
        "## 4. Locked phase table (424-433)",
        "## 5. Constitutional first action: CDL-049 single-CDL opening",
        "## 6. Sequencing constraints and Phase-426 governance review boundary",
        "## 7. D2e CLI track independence and conditional tail policy",
        "## 8. Canonical anchors and non-goals",
    ):
        assert heading in text

    assert "| Order | Phase | Topic | Character | Sensitivity |" in text
    assert "Non-goals in Phase 424:" in text
    for non_goal in (
        "no prelock hardening for CDL-049",
        "no ratification of CDL-049",
        "no runtime mutation in Phase 424",
    ):
        assert non_goal in text

    for token in (
        "Window 424-433 is the Bounded-Existential Claim-Form Alignment and Treasury P_e Governance Stabilization Block.",
        "CDL-047 and CDL-048 are ratified at Window 424-433 entry.",
        "Phase 417 identified a MODERATE finding: popperian_gate_runtime.py admits unqualified existential as a claim form; CDL-049 must narrow this to bounded_existential.",
        'D2e Agent CLI (d2e_agent_cli_420.v0.1) and D2e Lifecycle CLI (d2e_lifecycle_cli_421.v0.1) carry forward without additional CLI implementation in Phase 424.',
        "CDL-049 is constitutionally obligated by the Phase 423 handoff and is the first constitutional action of Window 424.",
        "Phase 426 is a non-ratifying governance review and does not itself open, amend, or ratify any CDL row.",
        "CDL-050 is not pre-authorized and may open only if Phase 426 determines that a new CDL lane is required for Treasury P_e trigger and limit constants.",
        "Phase 424 opens CDL-049 as a single-CDL opening.",
        "CRITICAL findings in Phase 426 P_e assessment affect only Phases 429-431 and do not block CDL-049 ratification in Phase 428.",
    ):
        assert token in text


def test_cdl_049_opening_stub_exists_and_contains_required_headings_and_tokens() -> None:
    assert OPENING_STUB_PATH.exists()
    text = _read(OPENING_STUB_PATH)

    for heading in (
        "## 1. Purpose and scope",
        "## 2. CDL-049 opening state",
        "## 3. Bounded-existential alignment scope and CDL-V7 inheritance",
        "## 4. Phase 417 MODERATE finding as constitutional evidence",
        "## 5. Upstream dependencies and sequencing note",
        "## 6. Out-of-scope and deferred tracks",
        "## 7. Canonical anchors",
    ):
        assert heading in text

    for token in (
        "status: open",
        "CDL-049 opens as the bounded-existential claim-form alignment lane for popperian_gate_runtime vocabulary correction and active Popperian review corpus alignment.",
        "Phase 417 identified that popperian_gate_runtime.py admits unqualified existential as a claim form; CDL-049 narrows this to bounded_existential.",
        "The winning candidate is: narrow existential to bounded_existential in _ADMISSIBLE_CLAIM_FORMS and update ilc_popper_ilc_analysis_v0.1.md active vocabulary sections.",
        "Phase 425 is the targeted prelock hardening lane for CDL-049.",
        "No ratification or runtime implementation occurs in Phase 424.",
        "ilc_cdl_v7_agent_decomposition_criteria_ratification_evidence_335_v0.1.md is a historical ratification artifact and is not mutated by CDL-049.",
    ):
        assert token in text


def test_decision_log_contains_exact_cdl_049_opening_row() -> None:
    # The Phase-424 CDL-049 row is a historical prelock reference.
    text = _decision_log_text_at_ref(_resolve_phase_424_commit_ref())
    rows = parse_decision_register_rows(text)
    assert EXPECTED_CDL_049_ROW in text
    assert rows["CDL-049"]["status"] == "open"


def test_cdl_049_row_appended_after_cdl_048_in_correct_order() -> None:
    lines = _read(DECISION_LOG_PATH).splitlines()
    cdl_048_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-048 "))
    cdl_049_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-049 "))
    assert cdl_049_index == cdl_048_index + 1


def test_popperian_gate_runtime_has_not_been_mutated() -> None:
    # The Phase-424 popperian_gate_runtime pre-mutation state is a historical prelock reference.
    commit_ref = _resolve_phase_424_commit_ref()
    text = _read_file_at_ref(commit_ref, str(POPPERIAN_GATE_PATH))
    assert '"existential"' in text
    assert '"bounded_existential"' not in text


def test_phase_424_commit_additive_only_non_target_shield() -> None:
    commit_ref = _resolve_phase_424_commit_ref()
    old_rows = parse_decision_register_rows(_decision_log_text_at_ref(f"{commit_ref}^1"))
    new_rows = parse_decision_register_rows(_decision_log_text_at_ref(commit_ref))
    added_ids = set(new_rows) - set(old_rows)
    assert added_ids == {"CDL-049"}
    for cdl_id in old_rows:
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_424"


def test_phase_424_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_424_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
