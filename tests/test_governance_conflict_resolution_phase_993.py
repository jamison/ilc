from pathlib import Path


DECISION_LOG = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
RATIFICATION = Path("docs/specs/ilc_governance_conflict_set_ratification_v0.1.md")
REMINDER = Path("docs/architecture/governance_conflict_resolution_reminder_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_993_scoped_cdl_entries_are_ratified() -> None:
    text = _read(DECISION_LOG)
    required_rows = (
        "| CDL-003 | CDP-003 | Founder fade-out mechanics | ratified |",
        "| CDL-004 | CDP-003/CDP-008 | Founder operational caps | ratified |",
        "| CDL-005 | CDP-007 | Issuance/cap constitutional wording | ratified |",
        "| CDL-006 | CDP-004/CDP-005 | Governance override/challenge process | ratified |",
        "| CDL-008 | CDP-010 | Layer boundary: fixed core vs policy-loaded layers | ratified |",
        "| CDL-009 | CDP-009 | Fork legitimacy/user signaling | ratified |",
        "| CDL-010 | CDP-003 | Pseudonymity/accountability balance | ratified |",
    )
    for row in required_rows:
        assert row in text


def test_phase_993_ratification_mapping_has_all_raw_cluster_rows() -> None:
    text = _read(RATIFICATION)
    for raw_row in (
        "raw-012616",
        "raw-012647",
        "raw-012640",
        "raw-012888",
        "raw-012660",
        "raw-012615",
        "raw-012645",
    ):
        assert raw_row in text


def test_phase_993_reminder_core_checklist_is_completed() -> None:
    text = _read(REMINDER)
    assert "Status: Core set resolved (Phase 993)" in text
    for completed_item in (
        "- [x] Ratify `CDL-006` governance override/challenge model and publish chosen rationale.",
        "- [x] Ratify founder-boundary cluster: `CDL-003`, `CDL-004`, `CDL-010`.",
        "- [x] Ratify constitutional/economic boundary cluster: `CDL-005`, `CDL-008`, `CDL-009`.",
    ):
        assert completed_item in text
