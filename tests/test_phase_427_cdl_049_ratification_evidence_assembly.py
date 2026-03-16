from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
EVIDENCE_PATH = Path("docs/specs/ilc_cdl_049_bounded_existential_alignment_ratification_evidence_427_v0.1.md")
SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_424_433_sequence_lock_v0.1.md")
CDL_049_STUB_PATH = Path("docs/specs/ilc_cdl_049_bounded_existential_alignment_opening_stub_424_v0.1.md")
PHASE_425_HARDENING_PATH = Path("docs/specs/ilc_cdl_049_bounded_existential_alignment_prelock_hardening_425_v0.1.md")
PHASE_426_REVIEW_PATH = Path("docs/specs/ilc_treasury_pe_stabilization_governance_review_426_v0.1.md")
PHASE_417_REVIEW_PATH = Path("docs/specs/ilc_popperian_claim_form_governance_review_417_v0.1.md")
WINDOW_423_HANDOFF_PATH = Path("docs/specs/ilc_window_414_423_handoff_423_v0.1.md")
CDL_V7_EVIDENCE_PATH = Path("docs/specs/ilc_cdl_v7_agent_decomposition_criteria_ratification_evidence_335_v0.1.md")
POPPER_ANALYSIS_PATH = Path("docs/specs/ilc_popper_ilc_analysis_v0.1.md")
PHASE_427_SUBJECT_TOKEN = "phase 427 cdl-049 ratification evidence assembly"
REQUIRED_HEADINGS = (
    "## 1. Scope and ratification boundary",
    "## 2. CDL-049 open-state anchor",
    "## 3. Phase 417 MODERATE finding as constitutional evidence",
    "## 4. Phase 425 prelock hardening anchor",
    "## 5. Runtime patch scope contract",
    "## 6. Section-7 ratification readiness evidence checklist satisfaction",
    "## 7. Governance decision tokens",
    "## 8. Non-goals and boundary",
    "## 9. Canonical anchors",
)
REQUIRED_TOKENS = (
    "CDL-049 is ratified as the bounded-existential claim-form alignment lane for popperian_gate_runtime vocabulary correction and active Popperian review corpus alignment.",
    '_ADMISSIBLE_CLAIM_FORMS is narrowed from {"singular", "existential", "falsifiable_positive"} to {"singular", "bounded_existential", "falsifiable_positive"} by CDL-049 ratification.',
    "ilc_popper_ilc_analysis_v0.1.md active vocabulary sections are updated to use bounded_existential where previously the unqualified existential form was used.",
    "Leave runtime and corpus vocabulary unchanged is rejected because the Phase 417 MODERATE finding identifies a real governance and runtime wording gap that CDL-049 is constitutionally obligated to resolve.",
    "Replace popperian_gate_runtime module entirely is rejected because a full module replacement exceeds the scope of CDL-049's narrow vocabulary amendment obligation.",
    "CDL-V7 remains ratified as a historical constitutional artifact and is not reopened or mutated by CDL-049.",
    "docs/specs/ilc_cdl_v7_agent_decomposition_criteria_ratification_evidence_335_v0.1.md is a historical ratification artifact and is not mutated by CDL-049 ratification.",
    "Phase 417 recorded no CDL-047-specific or CDL-048-specific CRITICAL findings; CDL-049 is not affected by the Window 414-423 blocking rule.",
    "No CDL row mutation occurs in Phase 427.",
)
REQUIRED_SECTION_6_ITEMS = (
    "1. The Phase-424 opening row and opening stub remain the authoritative historical open-state anchor for CDL-049.",
    "2. The Phase 425 prelock hardening artifact confirms the winning candidate: narrow existential to bounded_existential in _ADMISSIBLE_CLAIM_FORMS and update ilc_popper_ilc_analysis_v0.1.md active vocabulary sections; both rejected candidates remain excluded.",
    "3. The Phase 417 MODERATE finding is accepted as the constitutional evidence basis for CDL-049 ratification; the runtime vocabulary gap is the identified defect requiring resolution.",
    "4. The runtime patch scope is constitutionally bounded: only _ADMISSIBLE_CLAIM_FORMS is narrowed; popperian_gate_runtime module logic is otherwise unchanged; the ilc_popper_ilc_analysis_v0.1.md vocabulary update is limited to active sections only.",
    "5. CDL-V7 historical ratification evidence (ilc_cdl_v7_agent_decomposition_criteria_ratification_evidence_335_v0.1.md) is read-only and is not mutated by CDL-049 ratification.",
)
REQUIRED_CANONICAL_ANCHORS = (
    "docs/specs/ilc_popperian_claim_form_governance_review_417_v0.1.md",
    "docs/specs/ilc_window_414_423_handoff_423_v0.1.md",
    "docs/specs/ilc_cdl_049_bounded_existential_alignment_opening_stub_424_v0.1.md",
    "docs/specs/ilc_cdl_049_bounded_existential_alignment_prelock_hardening_425_v0.1.md",
    "docs/specs/ilc_treasury_pe_stabilization_governance_review_426_v0.1.md",
    "docs/specs/ilc_cdl_v7_agent_decomposition_criteria_ratification_evidence_335_v0.1.md",
    "ilc_core/consensus/popperian_gate_runtime.py",
    "docs/specs/ilc_popper_ilc_analysis_v0.1.md",
    "docs/specs/ilc_constitutional_decision_log_v0.1.md",
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


def _resolve_phase_427_commit_ref() -> str:
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
        if PHASE_427_SUBJECT_TOKEN in subject.lower():
            matching.append(commit_hash)
    required_paths = {
        str(EVIDENCE_PATH),
        "tests/test_phase_427_cdl_049_ratification_evidence_assembly.py",
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref
    if matching:
        raise AssertionError("phase_427_commit_subject_present_but_no_evidence_artifact_commit")
    raise AssertionError("phase_427_commit_not_present_in_local_history")


def _extract_section(text: str, heading: str) -> str:
    start = text.index(heading)
    rest = text[start + len(heading) :]
    match = re.search(r"\n## \d+\. ", rest)
    if match:
        return rest[: match.start()]
    return rest


def test_evidence_artifact_exists_and_contains_required_headings_tokens_and_checklist() -> None:
    assert EVIDENCE_PATH.exists()
    text = _read(EVIDENCE_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text
    for token in REQUIRED_TOKENS:
        assert token in text
    for item in REQUIRED_SECTION_6_ITEMS:
        assert item in text
    for anchor in REQUIRED_CANONICAL_ANCHORS:
        assert anchor in text
    section_6 = _extract_section(text, "## 6. Section-7 ratification readiness evidence checklist satisfaction")
    assert len(re.findall(r"^\d+\. ", section_6, flags=re.MULTILINE)) == 5


def test_phase_424_opening_stub_and_cdl_049_register_state_preserved() -> None:
    # The Phase-427 CDL-049 open-state check is a historical prelock reference.
    assert CDL_049_STUB_PATH.exists()
    commit_ref = _resolve_phase_427_commit_ref()
    rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert rows["CDL-049"]["status"] == "open"
    assert "ratified_date" not in rows["CDL-049"]
    assert "ratified_phase" not in rows["CDL-049"]


def test_phase_425_prelock_hardening_artifact_preserved() -> None:
    assert PHASE_425_HARDENING_PATH.exists()
    text = _read(PHASE_425_HARDENING_PATH)
    assert "Phase 428 is the targeted CDL-049 ratification lane; this hardening artifact constitutes the primary prelock evidence." in text


def test_governance_decision_tokens_and_runtime_patch_scope_contract_present() -> None:
    text = _read(EVIDENCE_PATH)
    assert '_ADMISSIBLE_CLAIM_FORMS is narrowed from {"singular", "existential", "falsifiable_positive"} to {"singular", "bounded_existential", "falsifiable_positive"} by CDL-049 ratification.' in text
    assert "CDL-V7 remains ratified as a historical constitutional artifact and is not reopened or mutated by CDL-049." in text
    assert "docs/specs/ilc_cdl_v7_agent_decomposition_criteria_ratification_evidence_335_v0.1.md is a historical ratification artifact and is not mutated by CDL-049 ratification." in text


def test_cdl_v7_historical_boundary_and_non_goal_present() -> None:
    text = _read(EVIDENCE_PATH)
    assert "CDL-V7 remains ratified as a historical constitutional artifact and is not reopened or mutated by CDL-049." in text
    assert "No CDL row mutation occurs in Phase 427." in text


def test_phase_427_commit_touched_no_cdl_rows_or_prior_phase_artifacts() -> None:
    commit_ref = _resolve_phase_427_commit_ref()
    old_rows = parse_decision_register_rows(_read_file_at_ref(f"{commit_ref}^1", str(DECISION_LOG_PATH)))
    new_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert set(old_rows) == set(new_rows), "phase_427_commit_modified_decision_log_unlawfully"
    for cdl_id in old_rows:
        assert old_rows[cdl_id] == new_rows[cdl_id], "phase_427_commit_modified_decision_log_unlawfully"

    old_stub = _read_file_at_ref(f"{commit_ref}^1", str(CDL_049_STUB_PATH))
    new_stub = _read_file_at_ref(commit_ref, str(CDL_049_STUB_PATH))
    assert old_stub == new_stub, "phase_427_commit_modified_phase_424_opening_stub_unlawfully"

    old_hardening = _read_file_at_ref(f"{commit_ref}^1", str(PHASE_425_HARDENING_PATH))
    new_hardening = _read_file_at_ref(commit_ref, str(PHASE_425_HARDENING_PATH))
    assert old_hardening == new_hardening, "phase_427_commit_modified_phase_425_hardening_unlawfully"

    old_phase_426 = _read_file_at_ref(f"{commit_ref}^1", str(PHASE_426_REVIEW_PATH))
    new_phase_426 = _read_file_at_ref(commit_ref, str(PHASE_426_REVIEW_PATH))
    assert old_phase_426 == new_phase_426, "phase_427_commit_modified_phase_426_review_unlawfully"

    old_lock = _read_file_at_ref(f"{commit_ref}^1", str(SEQUENCE_LOCK_PATH))
    new_lock = _read_file_at_ref(commit_ref, str(SEQUENCE_LOCK_PATH))
    assert old_lock == new_lock, "phase_427_commit_modified_phase_424_sequence_lock_unlawfully"

    old_phase_417 = _read_file_at_ref(f"{commit_ref}^1", str(PHASE_417_REVIEW_PATH))
    new_phase_417 = _read_file_at_ref(commit_ref, str(PHASE_417_REVIEW_PATH))
    assert old_phase_417 == new_phase_417, "phase_427_commit_modified_phase_417_review_unlawfully"

    old_handoff = _read_file_at_ref(f"{commit_ref}^1", str(WINDOW_423_HANDOFF_PATH))
    new_handoff = _read_file_at_ref(commit_ref, str(WINDOW_423_HANDOFF_PATH))
    assert old_handoff == new_handoff, "phase_427_commit_modified_window_423_handoff_unlawfully"

    old_cdl_v7 = _read_file_at_ref(f"{commit_ref}^1", str(CDL_V7_EVIDENCE_PATH))
    new_cdl_v7 = _read_file_at_ref(commit_ref, str(CDL_V7_EVIDENCE_PATH))
    assert old_cdl_v7 == new_cdl_v7, "phase_427_commit_modified_cdl_v7_historical_evidence_unlawfully"

    old_analysis = _read_file_at_ref(f"{commit_ref}^1", str(POPPER_ANALYSIS_PATH))
    new_analysis = _read_file_at_ref(commit_ref, str(POPPER_ANALYSIS_PATH))
    assert old_analysis == new_analysis, "phase_427_commit_modified_popper_analysis_unlawfully"


def test_phase_427_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_427_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
