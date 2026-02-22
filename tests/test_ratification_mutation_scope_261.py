from __future__ import annotations

from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    ALLOWED_RATIFICATION_MUTATION_FIELDS,
    assert_only_allowed_row_mutations,
    parse_decision_register_rows,
)


MODULE_PATH = Path("ilc_core/testing/ratification_mutation_scope_guardrail.py")
CDL_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")


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


def test_guardrail_module_exists() -> None:
    assert MODULE_PATH.exists()


def test_allowed_field_constant_is_exact_required_set() -> None:
    assert ALLOWED_RATIFICATION_MUTATION_FIELDS == {
        "status",
        "ratified_phase",
        "ratified_date",
        "evidence_document",
    }


def test_positive_path_allows_only_ratification_fields() -> None:
    old = _mini_register(
        "| CDL-032 | ADM-002 | CLI-first Agent SDK interface contract and command surface | open | single CLI entry point | CLI-first | evidence |"
    )
    new = _mini_register(
        "| CDL-032 | ADM-002 | CLI-first Agent SDK interface contract and command surface | ratified | single CLI entry point | CLI-first | evidence | ratified_phase: 253 | ratified_date: 2026-02-21 | evidence_document: docs/specs/ilc_cdl_032_cli_first_sdk_ratification_evidence_253_v0.1.md |"
    )

    assert_only_allowed_row_mutations(old, new, cdl_id="CDL-032")


def test_negative_path_rejects_current_candidate_drift() -> None:
    old = _mini_register(
        "| CDL-032 | ADM-002 | CLI-first Agent SDK interface contract and command surface | open | single CLI entry point | CLI-first (proposed) — see `ilc_adm_002_cli_first_agent_sdk_v0.1.md` | evidence |"
    )
    new = _mini_register(
        "| CDL-032 | ADM-002 | CLI-first Agent SDK interface contract and command surface | open | single CLI entry point | CLI-first | evidence |"
    )

    try:
        assert_only_allowed_row_mutations(old, new, cdl_id="CDL-032")
        assert False, "expected unauthorized mutation assertion"
    except AssertionError as exc:
        message = str(exc)
        assert "CDL-032" in message
        assert "current_candidate" in message


def test_missing_target_row_fails() -> None:
    old = _mini_register(
        "| CDL-032 | ADM-002 | topic | open | options | candidate | evidence |"
    )
    new = _mini_register(
        "| CDL-019 | ADR-0008 | topic | open | options | candidate | evidence |"
    )

    try:
        assert_only_allowed_row_mutations(old, new, cdl_id="CDL-032")
        assert False, "expected target missing assertion"
    except AssertionError as exc:
        assert "decision_register_identity_drift" in str(exc)


def test_additional_target_row_fails() -> None:
    old = _mini_register(
        "| CDL-032 | ADM-002 | topic | open | options | candidate | evidence |"
    )
    new = "\n".join(
        [
            "## Decision Register",
            "",
            "| decision_id | related_clause | decision_topic | status | options | current_candidate | required_artifacts |",
            "|---|---|---|---|---|---|---|",
            "| CDL-032 | ADM-002 | topic | open | options | candidate | evidence |",
            "| CDL-999 | CDP-999 | synthetic | open | opt | cand | evidence |",
            "",
            "## Scoped Ratification Record",
        ]
    )

    try:
        assert_only_allowed_row_mutations(old, new, cdl_id="CDL-032")
        assert False, "expected identity drift assertion"
    except AssertionError as exc:
        text = str(exc)
        assert "decision_register_identity_drift" in text
        assert "CDL-999" in text


def test_parser_reads_cdl_032_row_from_decision_log() -> None:
    text = CDL_LOG_PATH.read_text(encoding="utf-8")
    rows = parse_decision_register_rows(text)
    assert "CDL-032" in rows
    assert rows["CDL-032"]["decision_id"] == "CDL-032"
