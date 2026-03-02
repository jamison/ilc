from __future__ import annotations

import datetime
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    assert_no_non_target_rows_marked_with_phase,
    assert_only_allowed_row_mutations,
    parse_decision_register_rows,
)


V4_EVIDENCE_PATH = Path("docs/specs/ilc_cdl_v4_reopening_protocol_ratification_evidence_334_v0.1.md")
V6_EVIDENCE_PATH = Path("docs/specs/ilc_cdl_v6_genesis_intervention_protocol_ratification_evidence_334_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_325_TEST_PATH = Path("tests/test_cdl_v_batch_b_open_and_evidence_prelock_325.py")
PHASE_333_TEST_PATH = Path("tests/test_cdl_v5_ratification_333.py")
PHASE_334_COMMIT_SUBJECT = "docs(g8): phase 334 cdl-v4-v6 dual ratification"

_BASE_HEADERS = [
    "decision_id",
    "related_clause",
    "decision_topic",
    "status",
    "options",
    "current_candidate",
    "required_artifacts",
]

_PRE_334_CDL_V4_ROW = (
    "| CDL-V4 | Vulnerability Plan v0.1 / Popper Analysis v0.1 | Minority dissent, appeal, and reopening protocol for ratified CDL decisions | "
    "open | genesis-only reopening, full re-ratification only, minority dissent trigger plus formal reopening protocol | "
    "minority dissent trigger plus formal reopening protocol (proposed) | minority threshold analysis, reopening abuse simulation, Genesis-boundary wording |"
)

_PRE_334_CDL_V6_ROW = (
    "| CDL-V6 | Epistemological Foundations v0.1 / Vulnerability Plan v0.1 | Genesis agent intervention protocol for constitutional override and emergency response | "
    "open | informal founder discretion, hard prohibition on intervention, documented Genesis override with sunset and audit trail | "
    "documented Genesis override with sunset and audit trail (proposed) | intervention trigger matrix, audit record schema, sunset/appeal criteria |"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _mini_register(row: str) -> str:
    return "\n".join(
        [
            "## Decision Register",
            "",
            "| decision_id | related_clause | decision_topic | status | options | current_candidate | required_artifacts |",
            "|---|---|---|---|---|---|---|",
            row,
            "",
            "## Scoped Ratification Record",
        ]
    )


def _register_row_text(row: dict[str, str]) -> str:
    cells = [row[header] for header in _BASE_HEADERS]
    if "ratified_phase" in row:
        cells.append(f"ratified_phase: {row['ratified_phase']}")
    if "ratified_date" in row:
        cells.append(f"ratified_date: {row['ratified_date']}")
    if "evidence_document" in row:
        cells.append(f"evidence_document: {row['evidence_document']}")
    return "| " + " | ".join(cells) + " |"


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_334_commit_ref() -> str:
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
        if subject.strip() == PHASE_334_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(V4_EVIDENCE_PATH),
        str(V6_EVIDENCE_PATH),
        str(PHASE_325_TEST_PATH),
        str(PHASE_333_TEST_PATH),
        "tests/test_cdl_v4_v6_dual_ratification_334.py",
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_334_commit_subject_present_but_no_qualifying_dual_ratification_commit")
    raise AssertionError("phase_334_commit_not_present_in_local_history")


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


def test_ratification_evidence_files_exist_and_have_required_content() -> None:
    cases = [
        (
            V4_EVIDENCE_PATH,
            (
                "## 1. Purpose and scope",
                "## 2. Evidence chain summary",
                "## 3. `CDL-V4` option inventory and selection statement",
                "## 4. Section-3 authoritative evidence checklist satisfaction",
                "## 5. Boundary and escalation semantics",
                "## 6. Ratification record",
                "## 7. Mutation protocol confirmation",
                "## 8. Historical-prelock preservation note",
                "## 9. Non-goals",
                "## 10. Canonical anchors",
                "`minority dissent trigger plus formal reopening protocol`",
                "`genesis-only reopening`",
                "`full re-ratification only`",
                "Section 3 of `docs/specs/ilc_cdl_v4_reopening_protocol_evidence_prelock_325_v0.1.md` is authoritative",
                "`minority threshold analysis across multiple quorum compositions`",
                "`reopening abuse simulation showing resistance to spam or griefing challenges`",
                "`Genesis-boundary wording clarifying when reopening remains ordinary governance and when Genesis escalation is justified`",
                "`explicit procedural steps for initiating, reviewing, and closing a reopened decision`",
                "applies retroactively to previously ratified CDL decisions",
                "must satisfy the currently ratified CDL-V3 diversity requirement",
                "ordinary reopening is the default governance path",
                "ratifies CDL-V4 together with CDL-V6 to close the coupled governance boundary",
                "docs/specs/ilc_cdl_v3_quorum_diversity_ratification_evidence_332_v0.1.md",
            ),
        ),
        (
            V6_EVIDENCE_PATH,
            (
                "## 1. Purpose and scope",
                "## 2. Evidence chain summary",
                "## 3. `CDL-V6` option inventory and selection statement",
                "## 4. Section-3 authoritative evidence checklist satisfaction",
                "## 5. Boundary and anti-circumvention semantics",
                "## 6. Ratification record",
                "## 7. Mutation protocol confirmation",
                "## 8. Historical-prelock preservation note",
                "## 9. Non-goals",
                "## 10. Canonical anchors",
                "`documented Genesis override with sunset and audit trail`",
                "`informal founder discretion`",
                "`hard prohibition on intervention`",
                "Section 3 of `docs/specs/ilc_cdl_v6_genesis_intervention_protocol_evidence_prelock_325_v0.1.md` is authoritative",
                "`intervention trigger matrix covering capture, constitutional violation, and emergency-response cases`",
                "`audit record schema defining mandatory documentation for any Genesis override`",
                "`sunset/appeal criteria explaining how extraordinary intervention authority expires or is challenged`",
                "`explicit boundary analysis distinguishing intervention from ordinary governance operations`",
                "may not be used to bypass CDL-V4 ordinary reopening",
                "capture, constitutional violation, or time-critical emergency",
                "mandatory post hoc CDL-V4 review once ordinary governance is available",
                "ratifies CDL-V6 together with CDL-V4 to close the coupled governance boundary",
                "docs/specs/ilc_cdl_v4_reopening_protocol_evidence_prelock_325_v0.1.md",
            ),
        ),
    ]
    for path, tokens in cases:
        assert path.exists(), path
        text = _read(path)
        for token in tokens:
            assert token in text, (path, token)


def test_phase_325_historical_prelock_hardening_patch_is_active() -> None:
    text = _read(PHASE_325_TEST_PATH)
    assert "assert EXPECTED_V4_ROW in historical_text" in text
    assert "assert EXPECTED_V5_ROW in historical_text" in text
    assert "assert EXPECTED_V6_ROW in historical_text" in text
    assert "assert EXPECTED_V7_ROW in historical_text" in text
    assert 'assert rows["CDL-V4"]["status"] == "open"' not in text
    assert 'assert rows["CDL-V5"]["status"] == "open"' not in text
    assert 'assert rows["CDL-V6"]["status"] == "open"' not in text
    assert 'assert rows["CDL-V7"]["status"] == "open"' not in text
    assert 'for cdl_id in ("CDL-V4", "CDL-V5", "CDL-V6", "CDL-V7")' in text
    assert 'for cdl_id in ("CDL-V4", "CDL-V6", "CDL-V7")' not in text
    assert 'for cdl_id in ("CDL-V7",)' not in text
    assert '# The Phase-325 `CDL-V4` row is a historical prelock reference' in text
    assert '# The Phase-325 `CDL-V5` row is a historical prelock reference' in text
    assert '# The Phase-325 `CDL-V6` row is a historical prelock reference' in text
    assert '# The Phase-325 `CDL-V7` row is a historical prelock reference' in text


def test_phase_333_regression_hardening_patch_is_active() -> None:
    text = _read(PHASE_333_TEST_PATH)
    assert "assert EXPECTED_V4_ROW in historical_text" in text
    assert "assert EXPECTED_V5_ROW in historical_text" in text
    assert "assert EXPECTED_V6_ROW in historical_text" in text
    assert "assert EXPECTED_V7_ROW in historical_text" in text
    assert 'assert \'assert rows["CDL-V4"]["status"] == "open"\' not in text' in text
    assert 'assert \'assert rows["CDL-V5"]["status"] == "open"\' not in text' in text
    assert 'assert \'assert rows["CDL-V6"]["status"] == "open"\' not in text' in text
    assert 'assert \'assert rows["CDL-V7"]["status"] == "open"\' not in text' in text
    assert '"historical_rows = parse_decision_register_rows(historical_text)" in text' in text
    assert 'assert \'for cdl_id in ("CDL-V4", "CDL-V5", "CDL-V6", "CDL-V7")\' in text' in text
    assert 'assert \'for cdl_id in ("CDL-V4", "CDL-V6", "CDL-V7")\' not in text' in text
    assert 'assert \'for cdl_id in ("CDL-V7",)\' not in text' in text
    assert '"# The Phase-325 `CDL-V7` row is a historical prelock reference" in text' in text


def test_decision_log_cdl_v4_and_v6_ratified_with_expected_metadata() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))

    v4 = rows["CDL-V4"]
    assert v4["status"] == "ratified"
    assert v4["ratified_phase"] == "334"
    v4_date = datetime.date.fromisoformat(v4["ratified_date"])
    assert v4_date.isoformat() == v4["ratified_date"]
    assert (
        v4["evidence_document"]
        == "docs/specs/ilc_cdl_v4_reopening_protocol_ratification_evidence_334_v0.1.md"
    )

    v6 = rows["CDL-V6"]
    assert v6["status"] == "ratified"
    assert v6["ratified_phase"] == "334"
    v6_date = datetime.date.fromisoformat(v6["ratified_date"])
    assert v6_date.isoformat() == v6["ratified_date"]
    assert (
        v6["evidence_document"]
        == "docs/specs/ilc_cdl_v6_genesis_intervention_protocol_ratification_evidence_334_v0.1.md"
    )


def test_mutation_scope_and_non_target_rows_for_phase_334() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))

    v4_old = _mini_register(_PRE_334_CDL_V4_ROW)
    v4_new = _mini_register(_register_row_text(rows["CDL-V4"]))
    assert_only_allowed_row_mutations(v4_old, v4_new, cdl_id="CDL-V4")

    v6_old = _mini_register(_PRE_334_CDL_V6_ROW)
    v6_new = _mini_register(_register_row_text(rows["CDL-V6"]))
    assert_only_allowed_row_mutations(v6_old, v6_new, cdl_id="CDL-V6")

    assert_no_non_target_rows_marked_with_phase(
        rows,
        phase="334",
        target_cdls={"CDL-V4", "CDL-V6"},
    )


def test_full_non_target_row_mutation_guard_for_phase_334() -> None:
    commit_ref = _resolve_phase_334_commit_ref()

    old_text = _decision_log_text_at_ref(f"{commit_ref}^1")
    new_text = _decision_log_text_at_ref(commit_ref)

    old_rows = parse_decision_register_rows(old_text)
    new_rows = parse_decision_register_rows(new_text)

    assert set(old_rows.keys()) == set(new_rows.keys())
    assert old_rows["CDL-V4"]["status"] == "open"
    assert new_rows["CDL-V4"]["status"] == "ratified"
    assert old_rows["CDL-V6"]["status"] == "open"
    assert new_rows["CDL-V6"]["status"] == "ratified"

    v4_old = _mini_register(_register_row_text(old_rows["CDL-V4"]))
    v4_new = _mini_register(_register_row_text(new_rows["CDL-V4"]))
    assert_only_allowed_row_mutations(v4_old, v4_new, cdl_id="CDL-V4")

    v6_old = _mini_register(_register_row_text(old_rows["CDL-V6"]))
    v6_new = _mini_register(_register_row_text(new_rows["CDL-V6"]))
    assert_only_allowed_row_mutations(v6_old, v6_new, cdl_id="CDL-V6")

    for cdl_id in old_rows:
        if cdl_id in {"CDL-V4", "CDL-V6"}:
            continue
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_334"


def test_phase_334_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_334_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
