from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
V1_PATH = Path("docs/specs/ilc_cdl_v1_temporal_decay_evidence_prelock_324_v0.1.md")
V2_PATH = Path("docs/specs/ilc_cdl_v2_sybil_resistance_evidence_prelock_324_v0.1.md")
V3_PATH = Path("docs/specs/ilc_cdl_v3_quorum_diversity_evidence_prelock_324_v0.1.md")
PHASE_324_COMMIT_SUBJECT = "docs(g8): phase 324 cdl-v1-v3 open and evidence prelock"

EXPECTED_V1_ROW = (
    "| CDL-V1 | CDL-019 / Vulnerability Plan v0.1 | Temporal decay governance parameter for reuse centrality | "
    "open | no temporal decay, epoch-step decay, exponential half-life decay | "
    "exponential half-life decay (proposed) | decay sensitivity analysis, lock-in simulation, monitoring thresholds |"
)
EXPECTED_V2_ROW = (
    "| CDL-V2 | CDL-001 / CDL-033 / Vulnerability Plan v0.1 | Sybil resistance mechanism for participant identity and reuse validation | "
    "open | proof-of-personhood gate, stake-based participation cost, hybrid heuristic resistance | "
    "hybrid heuristic resistance (proposed) | sybil threat model, synthetic graph simulations, operator response thresholds |"
)
EXPECTED_V3_ROW = (
    "| CDL-V3 | ADR-0008 / Vulnerability Plan v0.1 | Ratification quorum diversity requirements | "
    "open | cluster diversity floor, weighted diversity quorum, supermajority-only governance | "
    "cluster diversity floor (proposed) | quorum composition simulation, coordinated voting adversarial tests, governance wording |"
)
EXPECTED_NEW_IDS = {"CDL-V1", "CDL-V2", "CDL-V3"}


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


def _resolve_phase_324_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matching_commits: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_324_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(V1_PATH),
        str(V2_PATH),
        str(V3_PATH),
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_324_commit_subject_present_but_no_constitutional_opening_commit")
    raise AssertionError("phase_324_commit_not_present_in_local_history")


def _decision_log_text_at_ref(ref: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{ref}:{DECISION_LOG_PATH}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"unable_to_read_decision_log_at_ref:{ref}: {result.stderr.strip()}")
    return result.stdout


def _decision_register_lines(text: str) -> list[str]:
    lines = text.splitlines()
    start = None
    for idx, line in enumerate(lines):
        if line.startswith("| decision_id | related_clause | decision_topic | status | options | current_candidate | required_artifacts |"):
            start = idx + 2
            break
    if start is None:
        raise AssertionError("decision_register_header_not_found")

    register_lines: list[str] = []
    for line in lines[start:]:
        if not line.startswith("|"):
            break
        register_lines.append(line)
    return register_lines


def test_evidence_prelock_files_exist_and_have_required_tokens() -> None:
    cases = [
        (
            V1_PATH,
            (
                "CDL-V1",
                "`exponential half-life decay`",
                "`no temporal decay`",
                "`epoch-step decay`",
                "does not ratify the decay parameter",
                "decay sensitivity analysis",
                "lock-in displacement simulation",
                "monitoring threshold proposal",
                "docs/specs/ilc_remaining_vulnerability_mechanisms_plan_v0.1.md",
                "docs/specs/ilc_epistemological_foundations_canonical_v0.1.md",
            ),
        ),
        (
            V2_PATH,
            (
                "CDL-V2",
                "`hybrid heuristic resistance`",
                "`proof-of-personhood gate`",
                "`stake-based participation cost`",
                "does not ratify the anti-sybil mechanism",
                "sybil threat model",
                "synthetic graph simulation",
                "monitoring/operator threshold proposal",
                "docs/specs/ilc_remaining_vulnerability_mechanisms_plan_v0.1.md",
                "docs/specs/ilc_d2e_04_identity_subsystem_handoff_294_v0.1.md",
            ),
        ),
        (
            V3_PATH,
            (
                "CDL-V3",
                "`cluster diversity floor`",
                "`weighted diversity quorum`",
                "`supermajority-only governance`",
                "does not ratify quorum diversity policy",
                "quorum composition simulation",
                "coordinated voting adversarial tests",
                "governance wording",
                "docs/specs/ilc_remaining_vulnerability_mechanisms_plan_v0.1.md",
                "docs/specs/ilc_popper_ilc_analysis_v0.1.md",
            ),
        ),
    ]
    for path, tokens in cases:
        assert path.exists(), path
        text = _read(path)
        for token in tokens:
            assert token in text, (path, token)


def test_decision_log_contains_exact_new_rows() -> None:
    text = _read(DECISION_LOG_PATH)
    historical_text = _decision_log_text_at_ref(_resolve_phase_324_commit_ref())
    # The Phase-324 `CDL-V1` row is a historical prelock reference and later ratification must not invalidate it.
    assert EXPECTED_V1_ROW in historical_text
    # The Phase-324 `CDL-V2` row is a historical prelock reference and later ratification must not invalidate it.
    assert EXPECTED_V2_ROW in historical_text
    assert EXPECTED_V3_ROW in text

    rows = parse_decision_register_rows(text)
    assert rows["CDL-V1"]["current_candidate"] == "exponential half-life decay (proposed)"
    assert rows["CDL-V2"]["current_candidate"] == "hybrid heuristic resistance (proposed)"
    assert rows["CDL-V3"]["status"] == "open"
    assert rows["CDL-V3"]["current_candidate"] == "cluster diversity floor (proposed)"


def test_new_rows_have_no_ratification_metadata() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    for cdl_id in ("CDL-V3",):
        row = rows[cdl_id]
        assert row["status"] == "open"
        assert "ratified_phase" not in row, cdl_id
        assert "ratified_date" not in row, cdl_id
        assert "evidence_document" not in row, cdl_id


def test_full_additive_only_non_target_shield_for_phase_324() -> None:
    commit_ref = _resolve_phase_324_commit_ref()

    old_text = _decision_log_text_at_ref(f"{commit_ref}^1")
    new_text = _decision_log_text_at_ref(commit_ref)

    old_rows = parse_decision_register_rows(old_text)
    new_rows = parse_decision_register_rows(new_text)

    added_ids = set(new_rows) - set(old_rows)
    assert added_ids == EXPECTED_NEW_IDS

    for cdl_id in old_rows:
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_324"


def test_new_rows_are_appended_after_cdl_033_in_raw_line_order() -> None:
    commit_ref = _resolve_phase_324_commit_ref()
    new_text = _decision_log_text_at_ref(commit_ref)
    register_lines = _decision_register_lines(new_text)

    cdl_033_index = register_lines.index(
        "| CDL-033 | ADM-002 / CDL-032 | OpenClaw skill specification and ClawHub publication contract | ratified | skill-only, skill + dedicated agent, full fleet config | skill-only initial (proposed) — dedicated agent config deferred to Phase B | SKILL.md spec, ClawHub PR, working CLI binary (CDL-032 prerequisite) | ratified_phase: 291 | ratified_date: 2026-02-24 | evidence_document: docs/specs/ilc_cdl_033_openclaw_skill_publication_ratification_evidence_291_v0.1.md |"
    )
    assert register_lines[cdl_033_index + 1] == EXPECTED_V1_ROW
    assert register_lines[cdl_033_index + 2] == EXPECTED_V2_ROW
    assert register_lines[cdl_033_index + 3] == EXPECTED_V3_ROW


def test_phase_324_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_324_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
