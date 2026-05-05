from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_phase_1197_repair_doc_records_pass_token_and_guardrails():
    text = _read("docs/specs/ilc_canon_bundle_signing_repair_1197_v0.1.md")

    assert "canon_bundle_signing_repair_pass_phase_1197" in text
    assert "Production validation was not weakened" in text
    assert "No CLI testing bypass was added" in text
    assert "USE_TESTING_CANON_EXPORT_SNAPSHOT = True" in text


def test_phase_1197_testing_snapshot_is_valid_v0_1_shape():
    text = _read("tests/fixtures/canon_bundle_valid_export_v0_1_snapshot.json")

    for required in (
        '"canon_export_format": "v0.1"',
        '"canon_hash": "abc123"',
        '"exported_at":',
        '"meta":',
        '"epochs":',
        '"snapshots":',
        '"balance_count":',
    ):
        assert required in text


def test_phase_1197_affected_tests_use_explicit_testing_snapshot_toggle():
    for relative_path in (
        "tests/test_canon_bundle_audit_artifact.py",
        "tests/test_canon_bundle_pipeline_report.py",
    ):
        text = _read(relative_path)
        assert "USE_TESTING_CANON_EXPORT_SNAPSHOT = True" in text
        assert "canon_bundle_valid_export_v0_1_snapshot.json" in text
        assert 'export = {"canon_hash": "abc123", "canon_export_format": "v0.1"}' not in text


def test_phase_1197_frontier_docs_updated():
    status = _read("docs/phases/STATUS.md")
    planning = _read("docs/PLANNING_INDEX.md")
    walkthrough = _read("docs/phases/phase_1197_canon_bundle_signing_repair_walkthrough.md")

    assert "## Phase 1197" in status
    assert "canon_bundle_signing_repair_pass_phase_1197" in status
    assert (
        "Window 1191-1199 is IN PROGRESS through Phase 1197" in planning
        or "Window 1191-1199 is CLOSED" in planning
    )
    assert "**Status:** complete" in walkthrough
    assert "canon_bundle_signing_repair_pass_phase_1197" in walkthrough
