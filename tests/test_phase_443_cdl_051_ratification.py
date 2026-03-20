from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
EVIDENCE_PATH = Path(
    "docs/specs/ilc_cdl_051_constitutional_consensus_and_epoch_finality_ratification_evidence_443_v0.1.md"
)
PHASE_442_TEST_PATH = Path(
    "tests/test_phase_442_cdl_051_constitutional_consensus_and_epoch_finality_prelock_hardening.py"
)
PHASE_441_TEST_PATH = Path("tests/test_phase_441_cdl_051_opening.py")
PHASE_443_SUBJECT_TOKEN = "phase 443 cdl-051 constitutional consensus and epoch finality ratification"
REQUIRED_HEADINGS = (
    "## 1. Purpose and scope",
    "## 2. Ratified decision",
    "## 3. Evidence basis",
    "## 4. Section-7 ratification readiness evidence checklist satisfaction",
    "## 5. Conflict-state terminology ratification",
    "## 6. Constitutional dependency closure",
    "## 7. Prototype-default provenance boundary transition",
    "## 8. Out-of-scope and deferred tracks",
    "## 9. Canonical anchors",
)
REQUIRED_TOKENS = (
    "CDL-051 is ratified with the minimal epoch-state and quorum-record constitutional contract"
    " with deterministic fork/tie-break rules candidate.",
    "Defer consensus lane indefinitely is rejected because CDL-051 carries an active constitutional"
    " obligation inherited from CDL-V3, CDL-039, CDL-040, and CDL-045; deferral would leave inherited"
    " quorum and finality obligations ungrounded.",
    "Full production consensus architecture with storage-format cutover is rejected because the"
    " storage-format cutover decision is not constitutionally ripe in Window 441-449 and full production"
    " architecture exceeds the bounded constitutional scope of this lane.",
    "CDL-051 inherits quorum-diversity, brokerless transport, admission control, and emergency-response"
    " constraints from CDL-V3, CDL-039, CDL-040, and CDL-045.",
    "Phase 443 ratification closes the prototype-default provenance boundary established in Phase 441;"
    " consensus constants introduced in Phases 444-446 are now grounded by ratified constitutional law"
    " rather than prototype-local defaults.",
    "Consensus runtime implementation in Phases 444-446 proceeds under ratified CDL-051 constitutional"
    " authority.",
    "CDL-050 remains unopened and unaffected by CDL-051 ratification.",
)
REQUIRED_SECTION_4_ITEMS = (
    "The Phase-441 opening row and opening stub remain the authoritative historical open-state anchor"
    " for CDL-051.",
    "CDL-051 inherits quorum-diversity, brokerless transport, admission control, and emergency-response"
    " constraints from CDL-V3, CDL-039, CDL-040, and CDL-045; this inheritance is reviewed and confirmed"
    " in Phase 442 prelock hardening.",
    "The winning candidate is confirmed: minimal epoch-state and quorum-record constitutional contract"
    " with deterministic fork/tie-break rules; both rejected candidates remain excluded.",
    "The evidence-source ladder is constitutionally published: ratified CDL and active handoffs first,"
    " then active specs and runtime artifacts, then filtered historical extracts, with raw Z_Past_Chats"
    " treated as hypothesis input only.",
    "All pre-ratification consensus prototype defaults introduced in this window must remain separated"
    " from constitutional law and from operator-local or harness-local overrides until CDL-051"
    " ratification in Phase 443.",
)
EXPECTED_CDL_051_RATIFIED_ROW = (
    "| CDL-051 | CDL-V3 / CDL-039 / CDL-040 / CDL-045 | constitutional consensus and epoch-finality"
    " prototype lane for quorum-state, finality, and deterministic fork resolution | ratified | defer"
    " consensus lane indefinitely, minimal epoch-state and quorum-record constitutional contract with"
    " deterministic fork/tie-break rules, full production consensus architecture with storage-format"
    " cutover | minimal epoch-state and quorum-record constitutional contract with deterministic"
    " fork/tie-break rules | consensus state-machine prelock, adversarial scenario matrix,"
    " terminology lock, prototype-default provenance notes, evidence-source ladder | ratified_phase:"
    " 443 | ratified_date: 2026-03-20 | evidence_document:"
    " docs/specs/ilc_cdl_051_constitutional_consensus_and_epoch_finality_ratification_evidence_443_v0.1.md"
    " |"
)
REQUIRED_CONFLICT_TERMS = (
    "epoch",
    "quorum-state",
    "quorum-threshold",
    "finality",
    "fork",
    "fork-resolution rule",
    "epoch-state record",
    "quorum-record",
    "conflict",
)
REQUIRED_CANONICAL_ANCHORS = (
    "docs/specs/ilc_constitutional_decision_log_v0.1.md",
    "docs/specs/ilc_cdl_051_constitutional_consensus_and_epoch_finality_prelock_hardening_442_v0.1.md",
    "docs/specs/ilc_cdl_051_constitutional_consensus_and_epoch_finality_opening_stub_441_v0.1.md",
    "docs/specs/ilc_phase_441_449_sequence_lock_v0.1.md",
    "docs/specs/ilc_cdl_v3_quorum_diversity_ratification_evidence_332_v0.1.md",
    "docs/specs/ilc_cdl_039_p2p_transport_and_topology_privacy_ratification_evidence_379_v0.1.md",
    "docs/specs/ilc_cdl_040_admission_control_and_identity_envelope_ratification_evidence_393_v0.1.md",
    "docs/specs/ilc_cdl_045_operational_emergency_response_ratification_evidence_408_v0.1.md",
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


def _resolve_phase_442_commit_ref() -> str:
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
        if "phase 442 cdl-051 constitutional consensus and epoch finality prelock hardening" in subject.lower():
            matching.append(commit_hash)
    required_paths = {
        "docs/specs/ilc_cdl_051_constitutional_consensus_and_epoch_finality_prelock_hardening_442_v0.1.md",
        "tests/test_phase_442_cdl_051_constitutional_consensus_and_epoch_finality_prelock_hardening.py",
    }
    for commit_ref in matching:
        if required_paths.issubset(_changed_paths_for_commit(commit_ref)):
            return commit_ref
    if matching:
        raise AssertionError("phase_442_commit_subject_present_but_no_hardening_artifact_commit")
    raise AssertionError("phase_442_commit_not_present_in_local_history")


def _resolve_phase_443_commit_ref() -> str:
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
        if PHASE_443_SUBJECT_TOKEN in subject.lower():
            matching.append(commit_hash)
    required = {
        str(DECISION_LOG_PATH),
        str(EVIDENCE_PATH),
        "tests/test_phase_443_cdl_051_ratification.py",
        str(PHASE_441_TEST_PATH),
        str(PHASE_442_TEST_PATH),
    }
    for commit_ref in matching:
        changed = _changed_paths_for_commit(commit_ref)
        if changed == required:
            return commit_ref
    if matching:
        raise AssertionError("phase_443_commit_subject_present_but_no_qualifying_ratification_commit")
    raise AssertionError("phase_443_commit_not_present_in_local_history")


def _extract_section(text: str, heading: str) -> str:
    start = text.index(heading)
    rest = text[start + len(heading) :]
    match = re.search(r"\n## \d+\. ", rest)
    if match:
        return rest[: match.start()]
    return rest


def test_ratification_evidence_contains_required_headings_tokens_and_checklist() -> None:
    assert EVIDENCE_PATH.exists()
    text = _read(EVIDENCE_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text
    for token in REQUIRED_TOKENS:
        assert token in text
    for item in REQUIRED_SECTION_4_ITEMS:
        assert item in text
    section_4 = _extract_section(text, "## 4. Section-7 ratification readiness evidence checklist satisfaction")
    assert len(re.findall(r"^\d+\. ", section_4, flags=re.MULTILINE)) == 5
    section_5 = _extract_section(text, "## 5. Conflict-state terminology ratification")
    for term in REQUIRED_CONFLICT_TERMS:
        assert term in section_5
    for anchor in REQUIRED_CANONICAL_ANCHORS:
        assert anchor in text


def test_cdl_051_row_is_ratified_with_correct_fields() -> None:
    text = _read(DECISION_LOG_PATH)
    rows = parse_decision_register_rows(text)
    assert rows["CDL-051"]["status"] == "ratified"
    assert rows["CDL-051"]["ratified_phase"] == "443"
    assert rows["CDL-051"]["ratified_date"] == "2026-03-20"
    assert (
        rows["CDL-051"]["evidence_document"]
        == "docs/specs/ilc_cdl_051_constitutional_consensus_and_epoch_finality_ratification_evidence_443_v0.1.md"
    )
    assert "minimal epoch-state and quorum-record constitutional contract with deterministic fork/tie-break rules (proposed)" not in text
    assert EXPECTED_CDL_051_RATIFIED_ROW in text


def test_cdl_049_row_unchanged_and_cdl_050_absent() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows["CDL-049"]["status"] == "ratified"
    assert "CDL-050" not in rows


def test_phase_442_prelock_tests_are_historically_hardened() -> None:
    text = _read(PHASE_442_TEST_PATH)
    assert "# The Phase-442 CDL-051 row is a historical prelock reference." in text
    assert text.count("_read_file_at_ref(_resolve_phase_442_commit_ref(), str(DECISION_LOG_PATH))") >= 2
    assert 'rows["CDL-051"]["status"] == "open"' in text
    assert "EXPECTED_CDL_051_ROW in historical_text" in text
    assert text.count("_read(DECISION_LOG_PATH)") == 1


def test_cdl_051_register_order_preserved_after_ratification() -> None:
    lines = _read(DECISION_LOG_PATH).splitlines()
    cdl_049_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-049 "))
    cdl_051_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-051 "))
    assert cdl_049_index + 1 == cdl_051_index
    between = lines[cdl_049_index + 1 : cdl_051_index]
    assert all("CDL-050" not in line for line in between)


def test_phase_443_commit_touches_exactly_required_paths() -> None:
    commit_ref = _resolve_phase_443_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    required = {
        str(DECISION_LOG_PATH),
        str(EVIDENCE_PATH),
        "tests/test_phase_443_cdl_051_ratification.py",
        str(PHASE_441_TEST_PATH),
        str(PHASE_442_TEST_PATH),
    }
    assert changed == required, "phase_443_commit_touched_unexpected_paths"
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)


def test_phase_443_commit_no_non_cdl_051_row_mutation() -> None:
    commit_ref = _resolve_phase_443_commit_ref()
    old_rows = parse_decision_register_rows(_read_file_at_ref(f"{commit_ref}^1", str(DECISION_LOG_PATH)))
    new_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert set(old_rows) == set(new_rows)
    for cdl_id in old_rows:
        if cdl_id == "CDL-051":
            continue
        assert old_rows[cdl_id] == new_rows[cdl_id], f"non_target_row_mutated:{cdl_id}"
    assert new_rows["CDL-051"]["status"] == "ratified"
    assert old_rows["CDL-051"]["status"] == "open"
