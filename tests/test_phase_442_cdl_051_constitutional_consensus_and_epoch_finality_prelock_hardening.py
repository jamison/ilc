from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_441_449_sequence_lock_v0.1.md")
HARDENING_PATH = Path(
    "docs/specs/ilc_cdl_051_constitutional_consensus_and_epoch_finality_prelock_hardening_442_v0.1.md"
)
CDL_051_STUB_PATH = Path(
    "docs/specs/ilc_cdl_051_constitutional_consensus_and_epoch_finality_opening_stub_441_v0.1.md"
)
CDL_V3_EVIDENCE_PATH = Path("docs/specs/ilc_cdl_v3_quorum_diversity_ratification_evidence_332_v0.1.md")
CDL_039_EVIDENCE_PATH = Path(
    "docs/specs/ilc_cdl_039_p2p_transport_and_topology_privacy_ratification_evidence_379_v0.1.md"
)
CDL_040_EVIDENCE_PATH = Path(
    "docs/specs/ilc_cdl_040_admission_control_and_identity_envelope_ratification_evidence_393_v0.1.md"
)
CDL_045_EVIDENCE_PATH = Path(
    "docs/specs/ilc_cdl_045_operational_emergency_response_ratification_evidence_408_v0.1.md"
)
EXPECTED_CDL_051_ROW = (
    "| CDL-051 | CDL-V3 / CDL-039 / CDL-040 / CDL-045 | constitutional consensus and epoch-finality"
    " prototype lane for quorum-state, finality, and deterministic fork resolution | open | defer"
    " consensus lane indefinitely, minimal epoch-state and quorum-record constitutional contract with"
    " deterministic fork/tie-break rules, full production consensus architecture with storage-format"
    " cutover | minimal epoch-state and quorum-record constitutional contract with deterministic"
    " fork/tie-break rules (proposed) | consensus state-machine prelock, adversarial scenario matrix,"
    " terminology lock, prototype-default provenance notes, evidence-source ladder |"
)
PHASE_442_SUBJECT_TOKEN = "phase 442 cdl-051 constitutional consensus and epoch finality prelock hardening"
REQUIRED_HEADINGS = (
    "## 1. Scope and non-ratifying boundary",
    "## 2. CDL-051 open-state evidence anchor",
    "## 3. Inherited constitutional anchors review",
    "## 4. Winning candidate confirmation and rejected candidates",
    "## 5. Conflict-state terminology lock",
    "## 6. Evidence-source ladder and prototype-default provenance boundary",
    "## 7. Section-7 ratification readiness evidence checklist satisfaction",
    "## 8. Non-goals",
)
REQUIRED_TOKENS = (
    "status: open",
    "CDL-051 prelock hardening confirms the winning candidate: minimal epoch-state and quorum-record"
    " constitutional contract with deterministic fork/tie-break rules.",
    "No CDL row mutation occurs in Phase 442.",
    "Phase 443 is the targeted CDL-051 ratification lane; this hardening artifact constitutes the"
    " primary prelock evidence.",
    "Defer consensus lane indefinitely is rejected because CDL-051 carries an active constitutional"
    " obligation inherited from CDL-V3, CDL-039, CDL-040, and CDL-045; deferral would leave inherited"
    " quorum and finality obligations ungrounded.",
    "Full production consensus architecture with storage-format cutover is rejected because the"
    " storage-format cutover decision is not constitutionally ripe in Window 441-449 and full production"
    " architecture exceeds the bounded constitutional scope of this lane.",
    "Consensus constants and rule-like defaults introduced before ratification must remain clearly"
    " marked as prototype-local rather than constitutional law.",
    "Any pre-ratification consensus prototype must separate ratified constitutional obligations from"
    " operator-local or harness-local defaults.",
    "Raw Z_Past_Chats are treated as hypothesis input only and do not constitute constitutional evidence.",
    "These prelock inputs do not become constitutional constants until CDL-051 ratification in Phase 443.",
)
REQUIRED_SECTION_7_ITEMS = (
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
REQUIRED_CONFLICT_TERMS = (
    "**epoch**:",
    "**quorum-state**:",
    "**quorum-threshold**:",
    "**finality**:",
    "**fork**:",
    "**fork-resolution rule**:",
    "**epoch-state record**:",
    "**quorum-record**:",
    "**conflict**:",
)
REQUIRED_TIER_LABELS = (
    "Tier 1 — Ratified constitutional decisions (CDL-V3, CDL-039, CDL-040, CDL-045) and active window handoffs",
    "Tier 2 — Active specs and runtime artifacts (sequence lock, CDL-051 stub, this hardening artifact, test files)",
    "Tier 3 — Filtered historical extracts (prior phase walkthroughs, prior window handoffs, evidence assembly reports)",
    "Tier 4 — Raw Z_Past_Chats: hypothesis input only; zero constitutional authority; must not be cited as binding design constraints.",
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
        if PHASE_442_SUBJECT_TOKEN in subject.lower():
            matching.append(commit_hash)
    required_paths = {
        str(HARDENING_PATH),
        "tests/test_phase_442_cdl_051_constitutional_consensus_and_epoch_finality_prelock_hardening.py",
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref
    if matching:
        raise AssertionError("phase_442_commit_subject_present_but_no_hardening_artifact_commit")
    raise AssertionError("phase_442_commit_not_present_in_local_history")


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
    section_5 = _extract_section(text, "## 5. Conflict-state terminology lock")
    for term in REQUIRED_CONFLICT_TERMS:
        assert term in section_5
    section_6 = _extract_section(text, "## 6. Evidence-source ladder and prototype-default provenance boundary")
    for label in REQUIRED_TIER_LABELS:
        assert label in section_6


def test_phase_441_cdl_051_opening_stub_is_preserved() -> None:
    assert CDL_051_STUB_PATH.exists()
    text = _read(CDL_051_STUB_PATH)
    assert "Phase 442 is the targeted prelock hardening lane for CDL-051." in text
    assert "status: open" in text
    assert (
        "CDL-051 opens as the constitutional consensus and epoch-finality lane for a deterministic,"
        " auditable quorum-state prototype."
    ) in text


def test_cdl_051_register_order_preserved() -> None:
    # The Phase-442 CDL register order is a historical reference.
    text = _read_file_at_ref(_resolve_phase_442_commit_ref(), str(DECISION_LOG_PATH))
    lines = text.splitlines()
    cdl_049_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-049 "))
    cdl_051_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-051 "))
    rows = parse_decision_register_rows(text)
    assert cdl_051_index == cdl_049_index + 1
    assert "CDL-050" not in rows


def test_cdl_051_row_is_open() -> None:
    # The Phase-442 CDL-051 row is a historical prelock reference.
    historical_text = _read_file_at_ref(_resolve_phase_442_commit_ref(), str(DECISION_LOG_PATH))
    rows = parse_decision_register_rows(historical_text)
    assert rows["CDL-051"]["status"] == "open"
    assert EXPECTED_CDL_051_ROW in historical_text


def test_cdl_051_has_no_premature_ratification_metadata() -> None:
    # The Phase-442 CDL-051 row is a historical prelock reference.
    historical_text = _read_file_at_ref(_resolve_phase_442_commit_ref(), str(DECISION_LOG_PATH))
    rows = parse_decision_register_rows(historical_text)
    assert rows["CDL-051"]["status"] != "ratified"
    assert "ratified_date" not in rows["CDL-051"]
    assert "ratified_phase" not in rows["CDL-051"]


def test_phase_442_commit_no_cdl_row_mutation_and_prior_artifacts_immutable() -> None:
    commit_ref = _resolve_phase_442_commit_ref()
    old_rows = parse_decision_register_rows(_read_file_at_ref(f"{commit_ref}^1", str(DECISION_LOG_PATH)))
    new_rows = parse_decision_register_rows(_read_file_at_ref(commit_ref, str(DECISION_LOG_PATH)))
    assert set(old_rows) == set(new_rows), "phase_442_commit_unlawfully_added_removed_or_mutated_cdl_rows"
    for cdl_id in old_rows:
        assert (
            old_rows[cdl_id] == new_rows[cdl_id]
        ), "phase_442_commit_unlawfully_added_removed_or_mutated_cdl_rows"

    old_stub = _read_file_at_ref(f"{commit_ref}^1", str(CDL_051_STUB_PATH))
    new_stub = _read_file_at_ref(commit_ref, str(CDL_051_STUB_PATH))
    assert old_stub == new_stub, "phase_442_commit_modified_phase_441_opening_stub_unlawfully"

    old_lock = _read_file_at_ref(f"{commit_ref}^1", str(SEQUENCE_LOCK_PATH))
    new_lock = _read_file_at_ref(commit_ref, str(SEQUENCE_LOCK_PATH))
    assert old_lock == new_lock, "phase_442_commit_modified_phase_441_sequence_lock_unlawfully"

    old_cdl_v3 = _read_file_at_ref(f"{commit_ref}^1", str(CDL_V3_EVIDENCE_PATH))
    new_cdl_v3 = _read_file_at_ref(commit_ref, str(CDL_V3_EVIDENCE_PATH))
    assert old_cdl_v3 == new_cdl_v3, "phase_442_commit_modified_cdl_v3_historical_evidence_unlawfully"

    old_cdl_039 = _read_file_at_ref(f"{commit_ref}^1", str(CDL_039_EVIDENCE_PATH))
    new_cdl_039 = _read_file_at_ref(commit_ref, str(CDL_039_EVIDENCE_PATH))
    assert old_cdl_039 == new_cdl_039, "phase_442_commit_modified_cdl_039_historical_evidence_unlawfully"

    old_cdl_040 = _read_file_at_ref(f"{commit_ref}^1", str(CDL_040_EVIDENCE_PATH))
    new_cdl_040 = _read_file_at_ref(commit_ref, str(CDL_040_EVIDENCE_PATH))
    assert old_cdl_040 == new_cdl_040, "phase_442_commit_modified_cdl_040_historical_evidence_unlawfully"

    old_cdl_045 = _read_file_at_ref(f"{commit_ref}^1", str(CDL_045_EVIDENCE_PATH))
    new_cdl_045 = _read_file_at_ref(commit_ref, str(CDL_045_EVIDENCE_PATH))
    assert old_cdl_045 == new_cdl_045, "phase_442_commit_modified_cdl_045_historical_evidence_unlawfully"


def test_phase_442_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_442_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
