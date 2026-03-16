from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_424_433_sequence_lock_v0.1.md")
HARDENING_PATH = Path("docs/specs/ilc_cdl_049_bounded_existential_alignment_prelock_hardening_425_v0.1.md")
CDL_049_STUB_PATH = Path("docs/specs/ilc_cdl_049_bounded_existential_alignment_opening_stub_424_v0.1.md")
PHASE_417_REVIEW_PATH = Path("docs/specs/ilc_popperian_claim_form_governance_review_417_v0.1.md")
POPPER_ANALYSIS_PATH = Path("docs/specs/ilc_popper_ilc_analysis_v0.1.md")
CDL_V7_EVIDENCE_PATH = Path("docs/specs/ilc_cdl_v7_agent_decomposition_criteria_ratification_evidence_335_v0.1.md")
EXPECTED_CDL_049_ROW = (
    "| CDL-049 | CDL-V7 | bounded-existential claim-form alignment: narrow unqualified existential to "
    "bounded_existential in popperian_gate_runtime and active Popperian review corpus | open | leave "
    "runtime and corpus vocabulary unchanged, narrow existential to bounded_existential in runtime and active "
    "corpus, replace popperian_gate_runtime module entirely | narrow existential to bounded_existential in "
    "runtime and active corpus (proposed) | Phase 417 MODERATE finding evidence, popperian_gate_runtime "
    "_ADMISSIBLE_CLAIM_FORMS current vocabulary, ilc_popper_ilc_analysis active-section vocabulary audit |"
)
PHASE_425_SUBJECT_TOKEN = "phase 425 cdl-049 bounded existential alignment prelock hardening"
REQUIRED_HEADINGS = (
    "## 1. Scope and non-ratifying boundary",
    "## 2. CDL-049 open-state evidence anchor",
    "## 3. Phase 417 MODERATE finding as constitutional evidence basis",
    "## 4. Winning candidate confirmation and rejected candidates",
    "## 5. Vocabulary propagation scope",
    "## 6. Runtime patch contract",
    "## 7. Section-7 ratification readiness evidence checklist satisfaction",
    "## 8. Non-goals",
)
REQUIRED_TOKENS = (
    "status: open",
    "CDL-049 prelock hardening confirms the winning candidate: narrow existential to bounded_existential in _ADMISSIBLE_CLAIM_FORMS and update ilc_popper_ilc_analysis_v0.1.md active vocabulary sections.",
    "No CDL row mutation occurs in Phase 425.",
    "Phase 428 is the targeted CDL-049 ratification lane; this hardening artifact constitutes the primary prelock evidence.",
    "Leave runtime and corpus vocabulary unchanged is rejected because the Phase 417 MODERATE finding identifies a real governance and runtime wording gap that CDL-049 is constitutionally obligated to resolve.",
    "Replace popperian_gate_runtime module entirely is rejected because a full module replacement exceeds the scope of CDL-049's narrow vocabulary amendment obligation.",
    "Active forward-facing documents and runtime sources must be aligned; historical ratification evidence artifacts, closed-window handoffs, quoted historical source passages, and closed-phase prompts and walkthroughs are read-only and are not mutated.",
    "CDL-V7 remains ratified as a historical constitutional artifact; CDL-049 is a downstream narrowing override that does not reopen CDL-V7 or mutate its historical ratification evidence.",
    "docs/specs/ilc_cdl_v7_agent_decomposition_criteria_ratification_evidence_335_v0.1.md is a historical ratification artifact and is not mutated by CDL-049 prelock hardening.",
    "These prelock inputs do not become constitutional constants until CDL-049 ratification in Phase 428.",
)
REQUIRED_SECTION_7_ITEMS = (
    "1. The Phase-424 opening row and opening stub remain the authoritative historical open-state anchor for CDL-049.",
    '2. The Phase 417 MODERATE finding confirms the runtime vocabulary gap: _ADMISSIBLE_CLAIM_FORMS currently admits unqualified "existential" without a bounded-domain qualifier.',
    "3. The winning candidate is confirmed: narrow existential to bounded_existential in _ADMISSIBLE_CLAIM_FORMS and update ilc_popper_ilc_analysis_v0.1.md active vocabulary sections; both rejected candidates remain excluded.",
    "4. Vocabulary propagation scope is constitutionally bounded: active-corpus and runtime references must be aligned; historical ratification evidence artifacts, closed-window handoffs, quoted historical source passages, and closed-phase prompts and walkthroughs are read-only and are not mutated.",
    "5. CDL-V7 remains ratified as a historical constitutional artifact; CDL-049 is a downstream narrowing override that does not reopen CDL-V7 or mutate its historical ratification evidence.",
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


def _resolve_phase_425_commit_ref() -> str:
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
        if PHASE_425_SUBJECT_TOKEN in subject.lower():
            matching.append(commit_hash)
    required_paths = {
        str(HARDENING_PATH),
        "tests/test_phase_425_cdl_049_bounded_existential_alignment_prelock_hardening.py",
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref
    if matching:
        raise AssertionError("phase_425_commit_subject_present_but_no_hardening_artifact_commit")
    raise AssertionError("phase_425_commit_not_present_in_local_history")


def _extract_section(text: str, heading: str) -> str:
    start = text.index(heading)
    rest = text[start + len(heading) :]
    match = re.search(r"\n## \d+\. ", rest)
    if match:
        return rest[: match.start()]
    return rest


def test_hardening_artifact_exists_and_contains_required_headings_tokens_and_checklist() -> None:
    assert HARDENING_PATH.exists()
    text = _read(HARDENING_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text
    for token in REQUIRED_TOKENS:
        assert token in text
    for item in REQUIRED_SECTION_7_ITEMS:
        assert item in text
    section_7 = _extract_section(text, "## 7. Section-7 ratification readiness evidence checklist satisfaction")
    assert len(re.findall(r"^\d+\. ", section_7, flags=re.MULTILINE)) == 5


def test_phase_424_cdl_049_opening_stub_is_preserved() -> None:
    assert CDL_049_STUB_PATH.exists()
    text = _read(CDL_049_STUB_PATH)
    assert "Phase 425 is the targeted prelock hardening lane for CDL-049." in text
    assert "status: open" in text
    assert (
        "CDL-049 opens as the bounded-existential claim-form alignment lane for "
        "popperian_gate_runtime vocabulary correction and active Popperian review corpus alignment."
    ) in text


def test_cdl_049_register_order_preserved() -> None:
    lines = _read(DECISION_LOG_PATH).splitlines()
    cdl_048_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-048 "))
    cdl_049_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-049 "))
    assert cdl_049_index == cdl_048_index + 1


def test_cdl_049_row_is_open() -> None:
    # The Phase-425 CDL-049 open-state row is a historical prelock reference.
    text = _read_file_at_ref(_resolve_phase_425_commit_ref(), str(DECISION_LOG_PATH))
    rows = parse_decision_register_rows(text)
    assert rows["CDL-049"]["status"] == "open"
    assert EXPECTED_CDL_049_ROW in text


def test_cdl_049_has_no_premature_ratification_metadata() -> None:
    # The Phase-425 CDL-049 pre-ratification state is a historical prelock reference.
    text = _read_file_at_ref(_resolve_phase_425_commit_ref(), str(DECISION_LOG_PATH))
    rows = parse_decision_register_rows(text)
    assert rows["CDL-049"]["status"] != "ratified"
    assert "ratified_date" not in rows["CDL-049"]
    assert "ratified_phase" not in rows["CDL-049"]


def test_phase_425_commit_no_cdl_row_mutation_and_prior_artifacts_immutable() -> None:
    commit_ref = _resolve_phase_425_commit_ref()
    old_rows = parse_decision_register_rows(_read_file_at_ref(f"{commit_ref}^1", str(DECISION_LOG_PATH)))
    new_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert set(old_rows) == set(new_rows), "phase_425_commit_unlawfully_added_removed_or_mutated_cdl_rows"
    for cdl_id in old_rows:
        assert old_rows[cdl_id] == new_rows[cdl_id], "phase_425_commit_unlawfully_added_removed_or_mutated_cdl_rows"

    old_stub = _read_file_at_ref(f"{commit_ref}^1", str(CDL_049_STUB_PATH))
    new_stub = _read_file_at_ref(commit_ref, str(CDL_049_STUB_PATH))
    assert old_stub == new_stub, "phase_425_commit_modified_phase_424_opening_stub_unlawfully"

    old_lock = _read_file_at_ref(f"{commit_ref}^1", str(SEQUENCE_LOCK_PATH))
    new_lock = _read_file_at_ref(commit_ref, str(SEQUENCE_LOCK_PATH))
    assert old_lock == new_lock, "phase_425_commit_modified_phase_424_sequence_lock_unlawfully"

    old_review = _read_file_at_ref(f"{commit_ref}^1", str(PHASE_417_REVIEW_PATH))
    new_review = _read_file_at_ref(commit_ref, str(PHASE_417_REVIEW_PATH))
    assert old_review == new_review, "phase_425_commit_modified_phase_417_review_unlawfully"

    old_analysis = _read_file_at_ref(f"{commit_ref}^1", str(POPPER_ANALYSIS_PATH))
    new_analysis = _read_file_at_ref(commit_ref, str(POPPER_ANALYSIS_PATH))
    assert old_analysis == new_analysis, "phase_425_commit_modified_popper_analysis_unlawfully"

    old_cdl_v7 = _read_file_at_ref(f"{commit_ref}^1", str(CDL_V7_EVIDENCE_PATH))
    new_cdl_v7 = _read_file_at_ref(commit_ref, str(CDL_V7_EVIDENCE_PATH))
    assert old_cdl_v7 == new_cdl_v7, "phase_425_commit_modified_cdl_v7_historical_evidence_unlawfully"


def test_phase_425_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_425_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
