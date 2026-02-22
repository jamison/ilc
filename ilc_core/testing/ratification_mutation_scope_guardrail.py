from __future__ import annotations

from typing import Dict, Iterable


ALLOWED_RATIFICATION_MUTATION_FIELDS = frozenset(
    {"status", "ratified_phase", "ratified_date", "evidence_document"}
)


def _split_markdown_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def _find_decision_register_table(lines: list[str]) -> tuple[int, list[str]]:
    for idx, line in enumerate(lines):
        cells = _split_markdown_row(line)
        if not cells:
            continue
        if [c.lower() for c in cells] == [
            "decision_id",
            "related_clause",
            "decision_topic",
            "status",
            "options",
            "current_candidate",
            "required_artifacts",
        ]:
            return idx, cells
    raise AssertionError("decision_register_header_not_found")


def parse_decision_register_rows(markdown_content: str) -> Dict[str, Dict[str, str]]:
    """Parse Decision Register rows keyed by decision_id.

    Parses the first Decision Register table and normalizes extra ratification
    cells like `ratified_phase: 251` into explicit key/value pairs.
    """

    lines = markdown_content.splitlines()
    header_index, headers = _find_decision_register_table(lines)

    rows: Dict[str, Dict[str, str]] = {}
    for line in lines[header_index + 2 :]:
        if not line.strip().startswith("|"):
            break

        cells = _split_markdown_row(line)
        if not cells:
            break
        if all(set(cell) <= {"-", ":", " "} for cell in cells):
            continue

        if len(cells) < len(headers):
            raise AssertionError("decision_register_row_column_count_too_small")

        row = {headers[i]: cells[i] for i in range(len(headers))}
        for extra_cell in cells[len(headers) :]:
            if not extra_cell:
                continue
            if ":" not in extra_cell:
                continue
            key, value = extra_cell.split(":", 1)
            row[key.strip()] = value.strip()

        decision_id = row.get("decision_id", "")
        if not decision_id.startswith("CDL-"):
            continue
        rows[decision_id] = row

    if not rows:
        raise AssertionError("decision_register_rows_not_found")
    return rows


def diff_row_fields(
    old_row: Dict[str, str],
    new_row: Dict[str, str],
) -> set[str]:
    """Return the set of field names whose values changed."""

    keys = set(old_row.keys()) | set(new_row.keys())
    changed = set()
    for key in keys:
        if old_row.get(key) != new_row.get(key):
            changed.add(key)
    return changed


def _assert_register_identity_unchanged(
    old_rows: Dict[str, Dict[str, str]],
    new_rows: Dict[str, Dict[str, str]],
) -> None:
    if set(old_rows.keys()) != set(new_rows.keys()):
        missing = sorted(set(old_rows.keys()) - set(new_rows.keys()))
        added = sorted(set(new_rows.keys()) - set(old_rows.keys()))
        raise AssertionError(
            "decision_register_identity_drift "
            f"missing={missing} added={added}"
        )


def assert_allowed_row_mutation(
    cdl_id: str,
    old_row: Dict[str, str],
    new_row: Dict[str, str],
    allowed_fields: Iterable[str] = ALLOWED_RATIFICATION_MUTATION_FIELDS,
) -> None:
    changed = diff_row_fields(old_row, new_row)
    unauthorized = changed - set(allowed_fields)
    if unauthorized:
        raise AssertionError(
            f"{cdl_id}: unauthorized_mutation_fields={sorted(unauthorized)}"
        )


def assert_only_allowed_row_mutations(
    old_markdown: str,
    new_markdown: str,
    cdl_id: str,
    allowed_fields: Iterable[str] = ALLOWED_RATIFICATION_MUTATION_FIELDS,
    enforce_register_identity: bool = True,
) -> None:
    """Assert only the allowed ratification fields changed for one CDL row."""

    old_rows = parse_decision_register_rows(old_markdown)
    new_rows = parse_decision_register_rows(new_markdown)

    if enforce_register_identity:
        _assert_register_identity_unchanged(old_rows, new_rows)

    if cdl_id not in old_rows:
        raise AssertionError(f"target_cdl_missing_in_old_register: {cdl_id}")
    if cdl_id not in new_rows:
        raise AssertionError(f"target_cdl_missing_in_new_register: {cdl_id}")

    assert_allowed_row_mutation(
        cdl_id=cdl_id,
        old_row=old_rows[cdl_id],
        new_row=new_rows[cdl_id],
        allowed_fields=allowed_fields,
    )
