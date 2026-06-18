import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "docs/specs/ilc_fix57_non_out_minority_manual_read_ledger_v0.1.json"
REPORT_PATH = ROOT / "docs/specs/ilc_fix57_non_out_minority_manual_read_report_v0.1.md"
PROMPT_PATH = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix57_g10_non_out_minority_manual_read.md"
WALKTHROUGH_PATH = ROOT / "docs/phases/phase_1545p_fix57_non_out_minority_manual_read_walkthrough.md"
STATUS_PATH = ROOT / "docs/phases/STATUS.md"


def _ledger() -> dict:
    return json.loads(LEDGER_PATH.read_text(encoding="utf-8"))


def test_fix57_non_out_ledger_counts_and_deferred_raw_out_boundary() -> None:
    data = _ledger()
    assert data["schema_version"] == "ilc_fix57_non_out_minority_manual_read_ledger.v0.1"
    assert data["phase"] == "1545p-Fix57-non-out-manual-read"
    assert data["source_cluster"] == "out/genesis_atlas_fix56_fiedler_public_eligible_minority_cluster_v0.1.json"
    assert data["raw_out_full_pass_deferred"] is True
    assert data["total_non_out_entries"] == 432
    assert data["manual_reviewed_entries"] == 13
    assert data["pending_entries"] == 419
    assert len(data["entries"]) == 432


def test_fix57_non_out_batch001_edges_are_support_only_recommendations() -> None:
    data = _ledger()
    allowed_edge_types = {"DERIVED_FROM", "EVIDENCES", "TESTS", "IMPLEMENTS"}
    reviewed = [row for row in data["entries"] if row["manual_status"] == "manual_reviewed_batch_001"]
    assert len(reviewed) == 13
    recommended_edges = [edge for row in reviewed for edge in row["recommended_edges"]]
    assert len(recommended_edges) == 15
    for edge in recommended_edges:
        assert edge["edge_type"] in allowed_edge_types
        assert edge["edge_type"] != "GOVERNS"
        assert edge["candidate_status"] == "recommended_not_applied"
        assert edge["annotation_phase"] == "phase_1545p_fix57_non_out_manual_read"
        assert edge["annotation_method"] == "manual_reviewed"
        assert edge["edge_id"].startswith("edge:")
        assert "Direct read:" in edge["evidence"]


def test_fix57_non_out_pending_entries_have_no_silent_edge_application() -> None:
    data = _ledger()
    pending = [row for row in data["entries"] if row["manual_status"] == "pending"]
    assert len(pending) == 419
    for row in pending:
        assert row["recommended_edges"] == []


def test_fix57_non_out_prompt_registers_lmdb_nodes_and_no_completion_token() -> None:
    prompt = PROMPT_PATH.read_text(encoding="utf-8")
    assert "## LMDB Node Registration" in prompt
    assert "Do not mutate LMDB" in prompt
    assert "Do not emit `fix57_complete`" in prompt
    assert "docs/specs/ilc_fix57_non_out_minority_manual_read_ledger_v0.1.json" in prompt
    assert "docs/phases/phase_1545p_fix57_non_out_minority_manual_read_walkthrough.md" in prompt


def test_fix57_non_out_report_and_walkthrough_record_batch001() -> None:
    report = REPORT_PATH.read_text(encoding="utf-8")
    walkthrough = WALKTHROUGH_PATH.read_text(encoding="utf-8")
    assert "Total non-out entries: `432`" in report
    assert "Manual-reviewed entries in this tranche: `13`" in report
    assert "Pending entries: `419`" in report
    assert "Batch 001 Findings" in report
    assert "Batch 001 Direct-Read Files" in walkthrough
    assert "fix57_complete is not emitted" in walkthrough
    assert "No LMDB mutation occurred" in walkthrough


def test_fix57_non_out_status_tokens() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    assert "Phase 1545p-Fix57 - Non-Out Public-Eligible Minority Manual Read" in status
    assert "fix57_non_out_minority_queue_grouped_phase_1545p_fix57" in status
    assert "fix57_non_out_batch001_atlas_fix18_fix21_manual_read_complete" in status
    assert "fix57_complete_not_emitted_phase_1545p_fix57_non_out" in status
    assert "public_path_remains_blocked_phase_1545p_fix57_non_out" in status
