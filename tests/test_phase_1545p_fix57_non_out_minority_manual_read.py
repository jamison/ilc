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
    assert data["manual_reviewed_entries"] == 337
    assert data["assisted_triage_entries"] == 95
    assert data["pending_deep_manual_confirmation_entries"] == 95
    assert data["pending_entries"] == 0
    assert data["full_non_out_pass_status"] == "assisted_triage_complete_deep_manual_confirmation_pending"
    assert len(data["entries"]) == 432


def test_fix57_non_out_edges_are_support_only_and_marked_by_confidence_boundary() -> None:
    data = _ledger()
    allowed_edge_types = {
        "CLASSIFIED_BY",
        "DERIVED_FROM",
        "EVIDENCES",
        "IMPLEMENTS",
        "REFERENCES_AUTHORITY",
        "TESTS",
        "CARRIES_FORWARD",
    }
    confirmed = [row for row in data["entries"] if row.get("deep_manual_confirmation_status") == "confirmed"]
    assisted = [row for row in data["entries"] if row.get("deep_manual_confirmation_status") == "pending"]
    assert len(confirmed) == 337
    assert len(assisted) == 95
    recommended_edges = [edge for row in data["entries"] for edge in row["recommended_edges"]]
    assert len(recommended_edges) == 1459
    for edge in recommended_edges:
        assert edge["edge_type"] in allowed_edge_types
        assert edge["edge_type"] != "GOVERNS"
        assert edge["candidate_status"] in {
            "recommended_not_applied",
            "assisted_triage_not_applied_pending_deep_manual_confirmation",
            "manual_confirmed_support_only_not_applied",
            "deep_manual_confirmed_not_applied",
        }
        assert edge["annotation_phase"].startswith("phase_1545p_fix57")
        assert edge["annotation_method"] in {
            "manual_reviewed",
            "assisted_triage",
            "deep_manual_direct_read",
            "deep_manual_reviewed",
            "semantic_node_context_review",
        }
        assert edge["edge_id"].startswith("edge:")
        assert edge["evidence"]


def test_fix57_non_out_all_assisted_rows_wait_for_deep_manual_confirmation() -> None:
    data = _ledger()
    pending = [row for row in data["entries"] if row["manual_status"] == "pending"]
    assert pending == []
    assert data["full_pass_summary"]["file_direct_reads"] == 299
    assert data["full_pass_summary"]["semantic_node_classifications"] == 133
    assert data["full_pass_summary"]["reviewed_with_no_new_safe_edge"] == 52
    assert data["full_pass_summary"]["governs_recommendations"] == 0
    pending_assisted = [row for row in data["entries"] if row.get("deep_manual_confirmation_status") == "pending"]
    assert len(pending_assisted) == 95
    for row in pending_assisted:
        assert row["manual_status"] == "assisted_triage_pending_deep_manual_confirmation"
        assert row["deep_manual_confirmation_status"] == "pending"
    assert len(data["deep_manual_confirmation_batches"]) == 35
    assert data["deep_manual_confirmation_batches"][-1]["batch_id"] == "batch_036_artifact_target_diagnostic_gap"


def test_fix57_non_out_prompt_registers_lmdb_nodes_and_no_completion_token() -> None:
    prompt = PROMPT_PATH.read_text(encoding="utf-8")
    assert "## LMDB Node Registration" in prompt
    assert "Do not mutate LMDB" in prompt
    assert "Do not emit `fix57_complete`" in prompt
    assert "docs/specs/ilc_fix57_non_out_minority_manual_read_ledger_v0.1.json" in prompt
    assert "docs/phases/phase_1545p_fix57_non_out_minority_manual_read_walkthrough.md" in prompt


def test_fix57_non_out_report_and_walkthrough_record_full_pass() -> None:
    report = REPORT_PATH.read_text(encoding="utf-8")
    walkthrough = WALKTHROUGH_PATH.read_text(encoding="utf-8")
    assert "Total non-out entries: `432`" in report
    assert "Deep-manual confirmed entries: `337`" in report
    assert "Assisted-triage entries pending deep confirmation: `95`" in report
    assert "Total support-only edge recommendations currently recorded: `1459`" in report
    assert "Honesty Correction" in report
    assert "Deep-manual confirmed rows | `337`" in walkthrough
    assert "Assisted-triage rows pending deep confirmation | `95`" in walkthrough
    assert "fix57_complete is not emitted" in walkthrough
    assert "No LMDB mutation occurred" in walkthrough


def test_fix57_non_out_status_tokens() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    assert "Phase 1545p-Fix57 - Non-Out Public-Eligible Minority Manual Read" in status
    assert "fix57_non_out_minority_queue_grouped_phase_1545p_fix57" in status
    assert "fix57_non_out_batch001_atlas_fix18_fix21_manual_read_complete" in status
    assert "fix57_non_out_assisted_triage_complete_deep_manual_pending" in status
    assert "fix57_complete_not_emitted_phase_1545p_fix57_non_out" in status
    assert "public_path_remains_blocked_phase_1545p_fix57_non_out" in status
