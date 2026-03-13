from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_402_413_sequence_lock_v0.1.md")
PRELOCK_PATH = Path("docs/specs/ilc_cdl_046_timed_out_amendment_open_prelock_405_v0.1.md")
SIM_007_RESULTS_PATH = Path("docs/specs/ilc_sim_006_007_commissioning_results_386_v0.1.md")
CDL_045_HARDENING_404_PATH = Path(
    "docs/specs/ilc_cdl_045_operational_emergency_response_prelock_hardening_404_v0.1.md"
)
EXPECTED_CDL_035_BASE_ROW = (
    "| CDL-035 | Node Schema Packet v0.1 / CDL-V7 | Validation lifecycle, gate-verdict attachment, "
    "and quarantine semantics | ratified | inline mutable lifecycle state, attached lifecycle envelope "
    "with unbounded recursive verdict effects, attached lifecycle envelope with bounded operational "
    "relevance | attached lifecycle envelope with bounded operational relevance | validation_state "
    "machine, gate_verdict attachment model, quarantine semantics | ratified_phase: 350 | "
    "ratified_date: 2026-03-04 | evidence_document: "
    "docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_ratification_evidence_350_v0.1.md |"
)
EXPECTED_CDL_046_ROW = (
    "| CDL-046 | CDL-035 / SIM-007 / Phase-402 Sequence Lock 402 v0.1 | timed_out validation-state "
    "amendment for churn and orphan recovery semantics | open | retain CDL-035 bounded lifecycle without "
    "timed_out amendment, open dedicated amendment row with bounded timeout-and-recovery prelock, open "
    "dedicated amendment row with fixed timeout and recovery constants prelock | open dedicated amendment "
    "row with fixed timeout and recovery constants prelock (proposed) | SIM-007 timeout and recovery "
    "calibration anchor, issuance-epoch interpretation lock, CDL-035 bounded lifecycle attachment clause |"
)
PHASE_405_SUBJECT_TOKEN = "phase 405 cdl-035 timed_out amendment open and prelock"
REQUIRED_HEADINGS = (
    "## 1. Purpose and scope",
    "## 2. CDL-046 opening state",
    "## 3. CDL-035 amendment boundary and constitutional anchors",
    "## 4. SIM-007 calibration anchor and issuance-epoch interpretation",
    "## 5. Candidate discrimination and proposed fixed-constant prelock",
    "## 6. Proposed amendment surface: timed_out transition and recovery policy",
    "## 7. Sequencing and ratification readiness plan",
    "## 8. Out-of-scope and deferred tracks",
    "## 9. Canonical anchors",
)
REQUIRED_TOKENS = (
    "status: open",
    "CDL-046 opens as the CDL-035 timed_out amendment lane for churn and orphan recovery semantics.",
    "This amendment uses a dedicated new sequential CDL identifier referencing CDL-035 and does not mutate the base CDL-035 ratified row.",
    "SIM-007 calibrated the amendment basis at issuance_epoch scale: recommended_orphan_timeout_epochs: 4; recommended_recovery_policy: stake_full_release.",
    "SIM-007 epoch context is issuance_epoch; orphan_timeout_epochs = 4 means a 4-month timeout horizon under the canonical 1-month issuance epoch.",
    "The proposed candidate is open dedicated amendment row with fixed timeout and recovery constants prelock.",
    "The prelock candidate binds orphan_timeout_epochs = 4 and recovery_policy = stake_full_release as the proposed fixed constants for later ratification.",
    "Claims remaining orphaned after orphan_timeout_epochs = 4 issuance epochs transition to timed_out and apply recovery_policy = stake_full_release.",
    "Bounded timeout-and-recovery prelock is rejected because SIM-007 already provides direct fixed-constant recommendations at issuance_epoch scale.",
    "Retaining CDL-035 without timed_out amendment is rejected because agent-churn and orphan accumulation evidence now requires explicit timed_out semantics and recovery policy to avoid undefined orphan-state handling.",
    "timed_out transition semantics remain bounded by CDL-035's attached lifecycle envelope with bounded operational relevance.",
    "Phase 409 is the targeted ratification lane for CDL-046; this opening artifact constitutes the primary prelock evidence.",
    "No runtime implementation occurs in Phase 405.",
)
REQUIRED_CANONICAL_ANCHORS = (
    "docs/specs/ilc_phase_402_413_sequence_lock_v0.1.md",
    "docs/specs/ilc_sim_006_007_commissioning_results_386_v0.1.md",
    "docs/specs/ilc_cdl_035_validation_lifecycle_and_gate_verdict_attachment_ratification_evidence_350_v0.1.md",
    "docs/specs/ilc_constitutional_decision_log_v0.1.md",
)
SEQUENCE_LOCK_TOKEN = (
    "The CDL-035 timed_out amendment is opened in Phase 405 as a dedicated amendment row with a new "
    "sequential CDL identifier; it references CDL-035 in its related_clause and does not modify the base "
    "CDL-035 ratified row."
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


def _resolve_phase_405_commit_ref() -> str:
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
        if PHASE_405_SUBJECT_TOKEN in subject.lower():
            matching.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(PRELOCK_PATH),
        "tests/test_phase_405_cdl_046_timed_out_amendment_open_prelock.py",
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching:
        raise AssertionError("phase_405_commit_subject_present_but_no_constitutional_open_prelock_commit")
    raise AssertionError("phase_405_commit_not_present_in_local_history")


def _decision_log_text_at_ref(ref: str) -> str:
    return _read_file_at_ref(ref, str(DECISION_LOG_PATH))


def test_prelock_exists_and_contains_required_headings_tokens_and_anchors() -> None:
    assert PRELOCK_PATH.exists()
    text = _read(PRELOCK_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text
    for token in REQUIRED_TOKENS:
        assert token in text
    for anchor in REQUIRED_CANONICAL_ANCHORS:
        assert anchor in text


def test_decision_log_contains_exact_cdl_046_opening_row() -> None:
    text = _read(DECISION_LOG_PATH)
    rows = parse_decision_register_rows(text)
    assert EXPECTED_CDL_046_ROW in text
    assert rows["CDL-046"]["status"] == "open"


def test_cdl_035_base_row_remains_ratified_and_exact() -> None:
    text = _read(DECISION_LOG_PATH)
    rows = parse_decision_register_rows(text)
    assert rows["CDL-035"]["status"] == "ratified"
    assert EXPECTED_CDL_035_BASE_ROW in text


def test_cdl_046_row_is_appended_after_cdl_045_and_sequence_lock_convention_remains_present() -> None:
    text = _read(DECISION_LOG_PATH)
    lines = text.splitlines()
    cdl_045_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-045 "))
    cdl_046_index = next(i for i, line in enumerate(lines) if line.startswith("| CDL-046 "))
    assert cdl_046_index == cdl_045_index + 1
    assert SEQUENCE_LOCK_TOKEN in _read(SEQUENCE_LOCK_PATH)


def test_cdl_046_has_no_premature_ratification_metadata() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows["CDL-046"]["status"] != "ratified"
    assert "ratified_phase" not in rows["CDL-046"]


def test_phase_405_commit_additive_only_non_target_row_shield_and_prior_artifacts_immutable() -> None:
    commit_ref = _resolve_phase_405_commit_ref()
    old_rows = parse_decision_register_rows(_decision_log_text_at_ref(f"{commit_ref}^1"))
    new_rows = parse_decision_register_rows(_decision_log_text_at_ref(commit_ref))
    assert "CDL-046" not in old_rows
    assert "CDL-046" in new_rows
    added_ids = set(new_rows) - set(old_rows)
    assert added_ids == {"CDL-046"}
    for cdl_id in old_rows:
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_405"

    old_sequence_lock = _read_file_at_ref(f"{commit_ref}^1", str(SEQUENCE_LOCK_PATH))
    new_sequence_lock = _read_file_at_ref(commit_ref, str(SEQUENCE_LOCK_PATH))
    assert old_sequence_lock == new_sequence_lock, "phase_405_commit_modified_phase_402_sequence_lock_unlawfully"

    old_sim_007 = _read_file_at_ref(f"{commit_ref}^1", str(SIM_007_RESULTS_PATH))
    new_sim_007 = _read_file_at_ref(commit_ref, str(SIM_007_RESULTS_PATH))
    assert old_sim_007 == new_sim_007, "phase_405_commit_modified_phase_386_sim_007_results_unlawfully"

    old_cdl_045_hardening = _read_file_at_ref(f"{commit_ref}^1", str(CDL_045_HARDENING_404_PATH))
    new_cdl_045_hardening = _read_file_at_ref(commit_ref, str(CDL_045_HARDENING_404_PATH))
    assert (
        old_cdl_045_hardening == new_cdl_045_hardening
    ), "phase_405_commit_modified_phase_404_cdl_045_hardening_artifact_unlawfully"


def test_phase_405_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_405_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
