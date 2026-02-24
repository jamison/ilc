from __future__ import annotations

from pathlib import Path
import re


OPEN_CDL_TRIAGE = Path("docs/specs/ilc_phase_226_open_cdl_security_triage_v0.1.md")
BACKLOG_QUEUE = Path("docs/specs/ilc_phase_226_decision_log_backlog_queue_v0.1.md")
DREDGE_MATRIX = Path("docs/research/constitution_dredge_matrix_v0.2.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _parse_markdown_table_rows(path: Path) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| raw-"):
            parts = [p.strip() for p in line.strip().strip("|").split("|")]
            if len(parts) >= 8:
                rows.append(parts[:8])
    return rows


def test_phase_226_open_cdl_triage_has_required_sections_and_verdicts() -> None:
    text = _read(OPEN_CDL_TRIAGE)

    assert "## 2. CDL-001 Triaging Record" in text
    assert "## 3. CDL-002 Triaging Record" in text
    assert "## 4. CDL-007 Triaging Record" in text

    verdicts = re.findall(r"^verdict:\s*(genesis_blocker|post_genesis_defer)\s*$", text, flags=re.MULTILINE)
    assert len(verdicts) == 3
    assert set(verdicts).issubset({"genesis_blocker", "post_genesis_defer"})

    assert "- remediation_required" in text or "- formal_noop_closure_required" in text


def test_phase_226_open_cdl_triage_rubric_criteria_are_explicit() -> None:
    text = _read(OPEN_CDL_TRIAGE)
    required_terms = (
        "first-run breakage",
        "key/data loss risk",
        "exploitable rollback/state-corruption risk",
        "no viable mitigation",
    )
    for term in required_terms:
        assert term in text


def test_phase_226_backlog_queue_has_required_counts_and_row_coverage() -> None:
    text = _read(BACKLOG_QUEUE)

    total_matrix_match = re.search(r"total matrix rows:\s*`(\d+)`", text)
    decision_log_match = re.search(r"total rows with `action = decision_log`:\s*`(\d+)`", text)
    cdl_count_match = re.search(r"total existing `CDL-\*` rows in decision log register:\s*`(\d+)`", text)
    pending_match = re.search(r"resulting pending backlog count used for queueing:\s*`(\d+)`", text)

    assert total_matrix_match and decision_log_match and cdl_count_match and pending_match

    total_matrix = int(total_matrix_match.group(1))
    decision_log_rows = int(decision_log_match.group(1))
    cdl_count = int(cdl_count_match.group(1))
    pending_count = int(pending_match.group(1))

    matrix_rows_actual = sum(
        1 for line in DREDGE_MATRIX.read_text(encoding="utf-8").splitlines() if line.startswith("| raw-")
    )
    decision_log_rows_actual = sum(
        1
        for line in DREDGE_MATRIX.read_text(encoding="utf-8").splitlines()
        if line.startswith("| raw-") and line.rstrip().endswith("| decision_log |")
    )
    table_rows = _parse_markdown_table_rows(BACKLOG_QUEUE)

    assert total_matrix == matrix_rows_actual
    assert decision_log_rows == decision_log_rows_actual
    # Historical snapshot count captured during Phase 226 triage.
    assert cdl_count == 16
    assert pending_count == len(table_rows)


def test_phase_226_backlog_queue_two_pass_and_quality_summary_present() -> None:
    text = _read(BACKLOG_QUEUE)

    assert "Pass 1 (coverage)" in text
    assert "Pass 2 (reasoning depth)" in text
    assert "## 6. Backlog quality summary" in text
    assert "row-specific rationale rows" in text
    assert "shared-rationale rows" in text


def test_phase_226_must_rows_use_row_specific_rationale() -> None:
    rows = _parse_markdown_table_rows(BACKLOG_QUEUE)
    must_rows = [row for row in rows if row[2] == "must"]
    assert must_rows

    for row in must_rows:
        rationale = row[6]
        assert not rationale.startswith("SR-")


def test_phase_226_backlog_table_header_includes_required_columns() -> None:
    text = _read(BACKLOG_QUEUE)
    header = "| raw_id | topic | strength | source | topic_cluster | proposed_queue_class | rationale | recommended_phase_window |"
    assert header in text
    assert "not entered into ratified decision register in this phase" in text
