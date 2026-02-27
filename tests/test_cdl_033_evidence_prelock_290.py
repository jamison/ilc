"""Contract tests for Phase 290 CDL-033 evidence prelock artifact."""

from pathlib import Path

ARTIFACT_PATH = Path("docs/specs/ilc_cdl_033_openclaw_skill_publication_evidence_prelock_290_v0.1.md")


def _read() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def test_artifact_exists() -> None:
    assert ARTIFACT_PATH.exists()


def test_required_sections_present() -> None:
    text = _read()
    for heading in (
        "## 1. Purpose and non-ratifying boundary",
        "## 2. Evidence chain summary",
        "## 3. OpenClaw skill contract readiness matrix",
        "## 4. ClawHub publication readiness checklist",
        "## 5. Runtime boundary and operational assumptions",
        "## 6. Ratification-entry criteria for phase 291",
        "## 7. Non-goals",
        "## 8. Canonical anchors",
    ):
        assert heading in text


def test_non_ratifying_wording_present() -> None:
    text = _read().lower()
    assert "cdl-033" in text
    assert "remains open" in text
    assert "non-ratifying" in text


def test_phase_291_entry_criteria_present() -> None:
    text = _read().lower()
    assert "ratification-entry criteria for phase 291" in text
    assert "phase-291 entry criteria" in text


def test_boundary_statements_present() -> None:
    text = _read().lower()
    assert "no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`" in text
    assert "no runtime changes in `ilc_core/`" in text
