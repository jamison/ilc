from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
V4_PATH = Path("docs/specs/ilc_cdl_v4_reopening_protocol_evidence_prelock_325_v0.1.md")
V5_PATH = Path("docs/specs/ilc_cdl_v5_schema_epoch_translation_evidence_prelock_325_v0.1.md")
V6_PATH = Path("docs/specs/ilc_cdl_v6_genesis_intervention_protocol_evidence_prelock_325_v0.1.md")
V7_PATH = Path("docs/specs/ilc_cdl_v7_agent_decomposition_criteria_evidence_prelock_325_v0.1.md")
PHASE_325_COMMIT_SUBJECT = "docs(g8): phase 325 cdl-v4-v7 open and evidence prelock"

EXPECTED_V4_ROW = (
    "| CDL-V4 | Vulnerability Plan v0.1 / Popper Analysis v0.1 | Minority dissent, appeal, and reopening protocol for ratified CDL decisions | "
    "open | genesis-only reopening, full re-ratification only, minority dissent trigger plus formal reopening protocol | "
    "minority dissent trigger plus formal reopening protocol (proposed) | minority threshold analysis, reopening abuse simulation, Genesis-boundary wording |"
)
EXPECTED_V5_ROW = (
    "| CDL-V5 | CDL-020 / CDL-023 / Vulnerability Plan v0.1 | Schema epoch markers and cross-version translation protocol for centrality comparability | "
    "open | no epoch markers, schema epoch markers only, schema epoch markers plus explicit cross-version translation | "
    "schema epoch markers plus explicit cross-version translation (proposed) | translation invariance test vectors, epoch-marker serialization contract, backward-compatibility thresholds |"
)
EXPECTED_V6_ROW = (
    "| CDL-V6 | Epistemological Foundations v0.1 / Vulnerability Plan v0.1 | Genesis agent intervention protocol for constitutional override and emergency response | "
    "open | informal founder discretion, hard prohibition on intervention, documented Genesis override with sunset and audit trail | "
    "documented Genesis override with sunset and audit trail (proposed) | intervention trigger matrix, audit record schema, sunset/appeal criteria |"
)
EXPECTED_V7_ROW = (
    "| CDL-V7 | Popper Analysis v0.1 / Epistemological Foundations v0.1 | Agent decomposition admissibility criteria for ILC knowledge units | "
    "open | utility-only acceptance, operator discretionary decomposition, Popperian basic-statement gate for agent decomposition | "
    "Popperian basic-statement gate for agent decomposition (proposed) | decomposition test corpus, admissibility counterexamples, cross-agent reproducibility rubric |"
)
EXPECTED_NEW_IDS = {"CDL-V4", "CDL-V5", "CDL-V6", "CDL-V7"}


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


def _resolve_phase_325_commit_ref() -> str:
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
        if subject.strip() == PHASE_325_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(V4_PATH),
        str(V5_PATH),
        str(V6_PATH),
        str(V7_PATH),
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_325_commit_subject_present_but_no_constitutional_opening_commit")
    raise AssertionError("phase_325_commit_not_present_in_local_history")


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
            V4_PATH,
            (
                "CDL-V4",
                "`minority dissent trigger plus formal reopening protocol`",
                "`genesis-only reopening`",
                "`full re-ratification only`",
                "does not ratify the reopening protocol",
                "appeal mechanism includes the formalized reopening protocol",
                "minority threshold analysis",
                "reopening abuse simulation",
                "Genesis-boundary wording",
                "docs/specs/ilc_remaining_vulnerability_mechanisms_plan_v0.1.md",
                "docs/specs/ilc_popper_ilc_analysis_v0.1.md",
                "docs/specs/ilc_epistemological_foundations_canonical_v0.1.md",
            ),
        ),
        (
            V5_PATH,
            (
                "CDL-V5",
                "`schema epoch markers plus explicit cross-version translation`",
                "`no epoch markers`",
                "`schema epoch markers only`",
                "does not ratify the translation protocol",
                "translation invariance test vectors",
                "epoch-marker serialization contract",
                "backward-compatibility thresholds",
                "docs/specs/ilc_remaining_vulnerability_mechanisms_plan_v0.1.md",
                "docs/specs/ilc_d2_schema_baseline_runtime_handoff_310_v0.1.md",
                "docs/specs/ilc_epoch_snapshot_runtime_handoff_314_v0.1.md",
            ),
        ),
        (
            V6_PATH,
            (
                "CDL-V6",
                "`documented Genesis override with sunset and audit trail`",
                "`informal founder discretion`",
                "`hard prohibition on intervention`",
                "does not ratify the intervention protocol",
                "intervention trigger matrix",
                "audit record schema",
                "sunset/appeal criteria",
                "docs/specs/ilc_remaining_vulnerability_mechanisms_plan_v0.1.md",
                "docs/specs/ilc_epistemological_foundations_canonical_v0.1.md",
            ),
        ),
        (
            V7_PATH,
            (
                "CDL-V7",
                "`Popperian basic-statement gate for agent decomposition`",
                "`utility-only acceptance`",
                "`operator discretionary decomposition`",
                "does not ratify the admissibility criteria",
                "decomposition test corpus",
                "admissibility counterexamples",
                "cross-agent reproducibility rubric",
                "docs/specs/ilc_remaining_vulnerability_mechanisms_plan_v0.1.md",
                "docs/specs/ilc_popper_ilc_analysis_v0.1.md",
                "docs/specs/ilc_epistemological_foundations_canonical_v0.1.md",
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
    historical_text = _decision_log_text_at_ref(_resolve_phase_325_commit_ref())
    assert EXPECTED_V4_ROW in text
    # The Phase-325 `CDL-V5` row is a historical prelock reference and later ratification must not invalidate it.
    assert EXPECTED_V5_ROW in historical_text
    assert EXPECTED_V6_ROW in text
    assert EXPECTED_V7_ROW in text

    rows = parse_decision_register_rows(text)
    assert rows["CDL-V4"]["status"] == "open"
    assert rows["CDL-V4"]["current_candidate"] == "minority dissent trigger plus formal reopening protocol (proposed)"
    assert rows["CDL-V5"]["current_candidate"] == "schema epoch markers plus explicit cross-version translation (proposed)"
    assert rows["CDL-V6"]["status"] == "open"
    assert rows["CDL-V6"]["current_candidate"] == "documented Genesis override with sunset and audit trail (proposed)"
    assert rows["CDL-V7"]["status"] == "open"
    assert rows["CDL-V7"]["current_candidate"] == "Popperian basic-statement gate for agent decomposition (proposed)"


def test_new_rows_have_no_ratification_metadata() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    for cdl_id in ("CDL-V4", "CDL-V6", "CDL-V7"):
        row = rows[cdl_id]
        assert row["status"] == "open"
        assert "ratified_phase" not in row, cdl_id
        assert "ratified_date" not in row, cdl_id
        assert "evidence_document" not in row, cdl_id


def test_full_additive_only_non_target_shield_for_phase_325() -> None:
    commit_ref = _resolve_phase_325_commit_ref()

    old_text = _decision_log_text_at_ref(f"{commit_ref}^1")
    new_text = _decision_log_text_at_ref(commit_ref)

    old_rows = parse_decision_register_rows(old_text)
    new_rows = parse_decision_register_rows(new_text)

    added_ids = set(new_rows) - set(old_rows)
    assert added_ids == EXPECTED_NEW_IDS

    for cdl_id in old_rows:
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_325"


def test_new_rows_are_appended_after_cdl_v3_in_raw_line_order() -> None:
    commit_ref = _resolve_phase_325_commit_ref()
    new_text = _decision_log_text_at_ref(commit_ref)
    register_lines = _decision_register_lines(new_text)

    cdl_v3_index = register_lines.index(
        "| CDL-V3 | ADR-0008 / Vulnerability Plan v0.1 | Ratification quorum diversity requirements | open | cluster diversity floor, weighted diversity quorum, supermajority-only governance | cluster diversity floor (proposed) | quorum composition simulation, coordinated voting adversarial tests, governance wording |"
    )
    assert register_lines[cdl_v3_index + 1] == EXPECTED_V4_ROW
    assert register_lines[cdl_v3_index + 2] == EXPECTED_V5_ROW
    assert register_lines[cdl_v3_index + 3] == EXPECTED_V6_ROW
    assert register_lines[cdl_v3_index + 4] == EXPECTED_V7_ROW


def test_phase_325_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_325_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
