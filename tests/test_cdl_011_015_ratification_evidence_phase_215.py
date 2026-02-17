from __future__ import annotations

from pathlib import Path
import re


DECISION_LOG = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
EVIDENCE_BUNDLE = Path("docs/specs/ilc_cdl_011_015_ratification_evidence_bundle_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _status_for_decision(text: str, decision_id: str) -> str:
    pattern = rf"^\| {re.escape(decision_id)} \| .* \| (open|ratified) \|"
    match = re.search(pattern, text, re.MULTILINE)
    if match is None:
        raise AssertionError(f"Missing decision row for {decision_id}")
    return match.group(1)


def test_phase_215_target_rows_are_ratified() -> None:
    text = _read(DECISION_LOG)
    for decision_id in ("CDL-011", "CDL-012", "CDL-013", "CDL-014", "CDL-015"):
        assert _status_for_decision(text, decision_id) == "ratified"


def test_phase_215_non_target_rows_keep_expected_statuses() -> None:
    text = _read(DECISION_LOG)
    expected = {
        "CDL-001": "open",
        "CDL-002": "open",
        "CDL-003": "ratified",
        "CDL-004": "ratified",
        "CDL-005": "ratified",
        "CDL-006": "ratified",
        "CDL-007": "open",
        "CDL-008": "ratified",
        "CDL-009": "ratified",
        "CDL-010": "ratified",
    }
    for decision_id, expected_status in expected.items():
        assert _status_for_decision(text, decision_id) == expected_status


def test_phase_215_decision_log_has_scoped_ratification_record() -> None:
    text = _read(DECISION_LOG)
    assert "## Scoped Ratification Record (Phase 215)" in text
    for decision_id, candidate in (
        ("CDL-011", "balanced composite"),
        ("CDL-012", "usage+freshness"),
        ("CDL-013", "decay-non-genesis-only"),
        ("CDL-014", "counterfactual path-lift"),
        ("CDL-015", "strict phase gate"),
    ):
        assert f"- `{decision_id}`: selected `{candidate}`" in text
    assert "docs/specs/ilc_cdl_011_015_ratification_evidence_bundle_v0.1.md" in text


def test_phase_215_evidence_bundle_has_required_per_decision_sections() -> None:
    text = _read(EVIDENCE_BUNDLE)
    assert "## 3. Decision Evidence Matrix" in text
    assert "## 4. Decision-Level Evidence" in text

    for heading in (
        "### 4.1 CDL-011",
        "### 4.2 CDL-012",
        "### 4.3 CDL-013",
        "### 4.4 CDL-014",
        "### 4.5 CDL-015",
    ):
        assert heading in text

    required_subsections = (
        "#### Intent",
        "#### Candidate option and rationale",
        "#### Implementation artifacts",
        "#### Verification artifacts",
        "#### Verification evidence (commands/results)",
        "#### Ratification verdict",
        "#### Residual gap and next remediation phase",
    )
    for subsection in required_subsections:
        assert text.count(subsection) == 5


def test_phase_215_evidence_bundle_verdicts_and_matrix_rows() -> None:
    text = _read(EVIDENCE_BUNDLE)
    for decision_id in ("CDL-011", "CDL-012", "CDL-013", "CDL-014", "CDL-015"):
        assert f"| `{decision_id}` |" in text
    assert text.count("| `ratified` |") >= 5
    assert "## 6. Ratification Conclusion" in text
    assert "CDL-011` through `CDL-015` satisfy the ratification sufficiency contract" in text
