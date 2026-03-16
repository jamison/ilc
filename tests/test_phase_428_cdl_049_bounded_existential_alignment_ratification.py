from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
EVIDENCE_PATH = Path("docs/specs/ilc_cdl_049_bounded_existential_alignment_ratification_evidence_427_v0.1.md")
POPPERIAN_GATE_PATH = Path("ilc_core/consensus/popperian_gate_runtime.py")
POPPER_ANALYSIS_PATH = Path("docs/specs/ilc_popper_ilc_analysis_v0.1.md")
SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_424_433_sequence_lock_v0.1.md")
CDL_049_STUB_PATH = Path("docs/specs/ilc_cdl_049_bounded_existential_alignment_opening_stub_424_v0.1.md")
PHASE_425_HARDENING_PATH = Path("docs/specs/ilc_cdl_049_bounded_existential_alignment_prelock_hardening_425_v0.1.md")
CDL_V7_EVIDENCE_PATH = Path("docs/specs/ilc_cdl_v7_agent_decomposition_criteria_ratification_evidence_335_v0.1.md")
PHASE_424_TEST_PATH = Path("tests/test_phase_424_cdl_049_opening.py")
PHASE_425_TEST_PATH = Path("tests/test_phase_425_cdl_049_bounded_existential_alignment_prelock_hardening.py")
PHASE_427_TEST_PATH = Path("tests/test_phase_427_cdl_049_ratification_evidence_assembly.py")
PHASE_428_TEST_PATH_SELF = Path("tests/test_phase_428_cdl_049_bounded_existential_alignment_ratification.py")
PHASE_428_RUNTIME_SUBJECT_TOKEN = "phase 428 cdl-049 popperian gate vocabulary narrowing and historicalization"
PHASE_428_CDL_SUBJECT_TOKEN = "phase 428 cdl-049 bounded existential alignment ratification"
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
REQUIRED_SECTION_7_TOKENS = (
    "CDL-049 is ratified as the bounded-existential claim-form alignment lane for popperian_gate_runtime vocabulary correction and active Popperian review corpus alignment.",
    '_ADMISSIBLE_CLAIM_FORMS is narrowed from {"singular", "existential", "falsifiable_positive"} to {"singular", "bounded_existential", "falsifiable_positive"} by CDL-049 ratification.',
    "CDL-V7 remains ratified as a historical constitutional artifact and is not reopened or mutated by CDL-049.",
    "docs/specs/ilc_cdl_v7_agent_decomposition_criteria_ratification_evidence_335_v0.1.md is a historical ratification artifact and is not mutated by CDL-049 ratification.",
    "ilc_popper_ilc_analysis_v0.1.md active vocabulary sections are updated to use bounded_existential where previously the unqualified existential form was used.",
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
RUNTIME_COMMIT_PATHS = {
    str(POPPERIAN_GATE_PATH),
    str(POPPER_ANALYSIS_PATH),
    str(PHASE_428_TEST_PATH_SELF),
    str(PHASE_427_TEST_PATH),
    str(PHASE_425_TEST_PATH),
    str(PHASE_424_TEST_PATH),
}


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


def _extract_section(text: str, heading: str) -> str:
    start = text.index(heading)
    rest = text[start + len(heading) :]
    match = re.search(r"\n## \d+\. ", rest)
    if match:
        return rest[: match.start()]
    return rest


def _resolve_phase_424_commit_ref() -> str:
    subject_token = "phase 424 window sequence lock and cdl-049 opening"
    required_paths = {
        str(DECISION_LOG_PATH),
        str(SEQUENCE_LOCK_PATH),
        str(CDL_049_STUB_PATH),
        str(PHASE_424_TEST_PATH),
    }
    result = subprocess.run(["git", "log", "--format=%H%x09%s"], capture_output=True, text=True, check=True)
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject_token in subject.lower():
            matches.append(commit_hash)
    for commit_ref in matches:
        if required_paths.issubset(_changed_paths_for_commit(commit_ref)):
            return commit_ref
    if matches:
        raise AssertionError("phase_424_commit_subject_present_but_no_constitutional_opening_commit")
    raise AssertionError("phase_424_commit_not_present_in_local_history")


def _resolve_phase_425_commit_ref() -> str:
    subject_token = "phase 425 cdl-049 bounded existential alignment prelock hardening"
    required_paths = {str(PHASE_425_HARDENING_PATH), str(PHASE_425_TEST_PATH)}
    result = subprocess.run(["git", "log", "--format=%H%x09%s"], capture_output=True, text=True, check=True)
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject_token in subject.lower():
            matches.append(commit_hash)
    for commit_ref in matches:
        if required_paths.issubset(_changed_paths_for_commit(commit_ref)):
            return commit_ref
    if matches:
        raise AssertionError("phase_425_commit_subject_present_but_no_hardening_artifact_commit")
    raise AssertionError("phase_425_commit_not_present_in_local_history")


def _resolve_phase_427_commit_ref() -> str:
    subject_token = "phase 427 cdl-049 ratification evidence assembly"
    required_paths = {str(EVIDENCE_PATH), str(PHASE_427_TEST_PATH)}
    result = subprocess.run(["git", "log", "--format=%H%x09%s"], capture_output=True, text=True, check=True)
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject_token in subject.lower():
            matches.append(commit_hash)
    for commit_ref in matches:
        if required_paths.issubset(_changed_paths_for_commit(commit_ref)):
            return commit_ref
    if matches:
        raise AssertionError("phase_427_commit_subject_present_but_no_evidence_artifact_commit")
    raise AssertionError("phase_427_commit_not_present_in_local_history")


def _resolve_phase_428_runtime_commit_ref() -> str:
    result = subprocess.run(["git", "log", "--format=%H%x09%s"], capture_output=True, text=True, check=True)
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if PHASE_428_RUNTIME_SUBJECT_TOKEN in subject.lower():
            matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == RUNTIME_COMMIT_PATHS:
            return commit_ref
    if matches:
        raise AssertionError("phase_428_runtime_commit_subject_present_but_no_qualifying_commit")
    raise AssertionError("phase_428_runtime_commit_not_present_in_local_history")


def _resolve_phase_428_cdl_commit_ref() -> str:
    result = subprocess.run(["git", "log", "--format=%H%x09%s"], capture_output=True, text=True, check=True)
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if PHASE_428_CDL_SUBJECT_TOKEN in subject.lower():
            matches.append(commit_hash)
    expected = {str(DECISION_LOG_PATH)}
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected:
            return commit_ref
    if matches:
        raise AssertionError("phase_428_cdl_commit_subject_present_but_no_qualifying_commit")
    raise AssertionError("phase_428_cdl_commit_not_present_in_local_history")


def _assert_phase_428_runtime_mutation_scope(commit_ref: str) -> None:
    changed_paths = _changed_paths_for_commit(commit_ref)
    expected_runtime_paths = RUNTIME_COMMIT_PATHS
    assert changed_paths == expected_runtime_paths, "phase_428_runtime_commit_touched_unexpected_paths"
    assert str(POPPERIAN_GATE_PATH) in changed_paths, "phase_428_runtime_commit_did_not_touch_popperian_gate_runtime"
    assert str(POPPER_ANALYSIS_PATH) in changed_paths, "phase_428_runtime_commit_did_not_touch_popper_analysis"
    assert str(DECISION_LOG_PATH) not in changed_paths, "phase_428_runtime_commit_unlawfully_touched_cdl"
    for path in changed_paths:
        if path.startswith("ilc_core/"):
            assert path == str(POPPERIAN_GATE_PATH), "phase_428_runtime_commit_unlawfully_touched_ilc_core_file"


def test_ratification_evidence_exists_and_contains_required_section_7_governance_tokens() -> None:
    assert EVIDENCE_PATH.exists()
    text = _read(EVIDENCE_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text
    section_7 = _extract_section(text, "## 7. Governance decision tokens")
    for token in REQUIRED_SECTION_7_TOKENS:
        assert token in section_7
    for anchor in REQUIRED_CANONICAL_ANCHORS:
        assert anchor in text


def test_cdl_049_open_state_at_phase_427_historical_commit() -> None:
    commit_ref = _resolve_phase_427_commit_ref()
    rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert rows["CDL-049"]["status"] == "open"
    assert "ratified_date" not in rows["CDL-049"]
    assert "ratified_phase" not in rows["CDL-049"]


def test_popperian_gate_runtime_pre_ratification_vocabulary_at_phase_424_commit() -> None:
    commit_ref = _resolve_phase_424_commit_ref()
    text = _read_file_at_ref(commit_ref, str(POPPERIAN_GATE_PATH))
    assert '"existential"' in text
    assert '"bounded_existential"' not in text


def test_phase_425_prelock_forward_obligation_token_present() -> None:
    assert PHASE_425_HARDENING_PATH.exists()
    text = _read(PHASE_425_HARDENING_PATH)
    assert "Phase 428 is the targeted CDL-049 ratification lane; this hardening artifact constitutes the primary prelock evidence." in text


def test_cdl_v7_historical_boundary_intact() -> None:
    assert CDL_V7_EVIDENCE_PATH.exists()
    text = _read(CDL_V7_EVIDENCE_PATH)
    assert "CDL-V7" in text
    assert "ratified" in text
    assert "ilc_cdl_v7_agent_decomposition_criteria_ratification_evidence_335_v0.1.md is a historical ratification artifact and is not mutated by CDL-049 ratification." in _read(EVIDENCE_PATH)


def test_phase_428_cdl_commit_ratification_and_non_target_shield() -> None:
    commit_ref = _resolve_phase_428_cdl_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == {str(DECISION_LOG_PATH)}, "phase_428_cdl_commit_touched_unexpected_paths"
    new_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    old_rows = parse_decision_register_rows(_read_file_at_ref(f"{commit_ref}^1", str(DECISION_LOG_PATH)))
    assert new_rows["CDL-049"]["status"] == "ratified"
    assert new_rows["CDL-049"]["ratified_phase"] == "428"
    assert new_rows["CDL-049"].get("ratified_date")
    assert new_rows["CDL-049"]["evidence_document"] == str(EVIDENCE_PATH)
    assert "(proposed)" not in new_rows["CDL-049"]["current_candidate"]
    assert set(old_rows) == set(new_rows), "phase_428_cdl_commit_unlawfully_added_or_removed_cdl_rows"
    for cdl_id in old_rows:
        if cdl_id == "CDL-049":
            continue
        assert old_rows[cdl_id] == new_rows[cdl_id], f"phase_428_cdl_commit_unlawfully_mutated_{cdl_id}"
    old_evidence = _read_file_at_ref(f"{commit_ref}^1", str(EVIDENCE_PATH))
    new_evidence = _read_file_at_ref(commit_ref, str(EVIDENCE_PATH))
    assert old_evidence == new_evidence, "phase_428_cdl_commit_modified_phase_427_evidence_artifact_unlawfully"


def test_phase_428_runtime_commit_mutation_scope_vocab_narrowing_and_historicalization() -> None:
    commit_ref = _resolve_phase_428_runtime_commit_ref()
    _assert_phase_428_runtime_mutation_scope(commit_ref)

    gate_text = _read(POPPERIAN_GATE_PATH)
    assert '    "bounded_existential",' in gate_text, "phase_428_popperian_gate_not_updated_to_bounded_existential"
    assert '    "existential",' not in gate_text, "phase_428_popperian_gate_still_has_bare_existential"

    analysis_text = _read(POPPER_ANALYSIS_PATH)
    assert "the singular bounded_existential claims that can potentially falsify a theory" in analysis_text, "phase_428_popper_analysis_missing_updated_claim_form_summary"
    assert "(singular and bounded_existential in structure)" in analysis_text, "phase_428_popper_analysis_missing_updated_parenthetical_claim_form"
    assert "**(a) Formal**: singular and bounded_existential in structure" in analysis_text, "phase_428_popper_analysis_missing_updated_formal_clause"
    assert "**Formally singular and bounded_existential**" in analysis_text, "phase_428_popper_analysis_missing_updated_knowledge_unit_clause"
    assert "Grounded in Popper's basic statement requirements: singular, bounded_existential, intersubjectively testable, falsifiable by counter-instance." in analysis_text, "phase_428_popper_analysis_missing_updated_disposition_clause"
    assert '"This algorithm is generally better" is not — it is universal, not singular; vague, not bounded_existential.' in analysis_text, "phase_428_popper_analysis_missing_updated_negative_claim_form_example"
    assert "the singular existential claims that can potentially falsify a theory" not in analysis_text, "phase_428_popper_analysis_still_has_legacy_claim_form_summary"
    assert "(singular and existential in structure)" not in analysis_text, "phase_428_popper_analysis_still_has_legacy_parenthetical_claim_form"
    assert "**(a) Formal**: singular and existential in structure" not in analysis_text, "phase_428_popper_analysis_still_has_legacy_formal_clause"
    assert "**Formally singular and existential**" not in analysis_text, "phase_428_popper_analysis_still_has_legacy_knowledge_unit_clause"
    assert "Grounded in Popper's basic statement requirements: singular, existential, intersubjectively testable, falsifiable by counter-instance." not in analysis_text, "phase_428_popper_analysis_still_has_legacy_disposition_clause"
    assert '"This algorithm is generally better" is not — it is universal, not singular; vague, not existential.' not in analysis_text, "phase_428_popper_analysis_still_has_legacy_negative_claim_form_example"

    phase_424_text = _read_file_at_ref(commit_ref, str(PHASE_424_TEST_PATH))
    assert "# The Phase-424 CDL-049 row is a historical prelock reference." in phase_424_text
    assert "# The Phase-424 popperian_gate_runtime pre-mutation state is a historical prelock reference." in phase_424_text
    assert "_read_file_at_ref" in phase_424_text

    phase_425_text = _read_file_at_ref(commit_ref, str(PHASE_425_TEST_PATH))
    assert "# The Phase-425 CDL-049 open-state row is a historical prelock reference." in phase_425_text
    assert "# The Phase-425 CDL-049 pre-ratification state is a historical prelock reference." in phase_425_text

    phase_427_text = _read_file_at_ref(commit_ref, str(PHASE_427_TEST_PATH))
    assert "# The Phase-427 CDL-049 open-state check is a historical prelock reference." in phase_427_text

    old_cdl_v7 = _read_file_at_ref(f"{commit_ref}^1", str(CDL_V7_EVIDENCE_PATH))
    new_cdl_v7 = _read_file_at_ref(commit_ref, str(CDL_V7_EVIDENCE_PATH))
    assert old_cdl_v7 == new_cdl_v7, "phase_428_runtime_commit_modified_cdl_v7_evidence_unlawfully"
