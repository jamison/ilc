from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows


EVIDENCE_PATH = Path("docs/specs/ilc_issuance_evidence_closure_b_271_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _working_tree_paths() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain"], check=True, capture_output=True, text=True
    )
    paths: list[str] = []
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        paths.append(line[3:])
    return paths


def test_evidence_artifact_exists() -> None:
    assert EVIDENCE_PATH.exists()


def test_evidence_artifact_has_required_sections() -> None:
    text = _read(EVIDENCE_PATH)
    headings = [
        "## 1. Scope",
        "## 2. CDL-029 allocation split evidence",
        "## 3. CDL-026 C_max evidence",
        "## 4. CDL-028 fee-burn split evidence",
        "## 5. Non-goals",
        "## 6. Canonical anchors",
    ]
    for heading in headings:
        assert heading in text


def test_target_cdl_sections_and_anchors_are_present() -> None:
    text = _read(EVIDENCE_PATH)
    assert "CDL-029" in text
    assert "CDL-026" in text
    assert "CDL-028" in text
    assert "ilc_cdl_025_terminal_issuance_model_ratification_evidence_267_v0.1.md" in text
    assert "ilc_issuance_evidence_closure_a_266_v0.1.md" in text


def test_each_target_cdl_has_ratification_readiness_statement() -> None:
    text = _read(EVIDENCE_PATH)
    assert "CDL-029` is ready to enter a sensitive ratification lane" in text
    assert "CDL-026` is ready to enter a sensitive ratification lane" in text
    assert "CDL-028` is ready to enter a sensitive ratification lane" in text


def test_non_ratifying_boundary_language_is_explicit() -> None:
    text = _read(EVIDENCE_PATH)
    assert "non-ratifying" in text
    assert "no decision-log mutation in this phase" in text


def test_decision_log_rows_not_ratified_in_phase_271() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    for cdl_id in ["CDL-029", "CDL-026", "CDL-028", "CDL-027", "CDL-030", "CDL-031"]:
        assert rows[cdl_id].get("ratified_phase") != "271", cdl_id


def test_decision_log_has_no_phase_271_mutation_marker() -> None:
    text = _read(DECISION_LOG_PATH)
    assert "ratified_phase: 271" not in text


def test_no_runtime_files_touched_in_this_phase() -> None:
    for path in _working_tree_paths():
        assert not path.startswith("ilc_core/"), path
