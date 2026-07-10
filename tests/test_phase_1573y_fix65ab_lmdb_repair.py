from __future__ import annotations

import json
from pathlib import Path


FIX65A = Path("tools/fix65a_lmdb_graph_projection_repair_1573y.py")
FIX65B = Path("tools/fix65b_section_integrity_audit_1573y.py")
STATUS = Path("docs/phases/STATUS.md")
WALKTHROUGH = Path("docs/phases/phase_1573y_fix65ab_lmdb_coverage_repair_walkthrough.md")
FIX65A_RECEIPT = Path("out/phase_1573y/fix65a_graph_projection_repair.json")
FIX65B_RECEIPT = Path("out/phase_1573y/fix65b_section_integrity_audit.json")


def _load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_repair_scripts_exist_and_are_private_lmdb_maintenance_tools() -> None:
    for path in (FIX65A, FIX65B):
        text = path.read_text(encoding="utf-8")
        assert path.is_file()
        assert "PUBLIC_RC_EXCLUDE" in text
        assert "public RC activation" in text
        assert "GenesisAtlasCandidateStore" in text


def test_repair_scripts_use_sequential_local_write_discipline() -> None:
    combined = FIX65A.read_text(encoding="utf-8") + FIX65B.read_text(encoding="utf-8")

    forbidden_concurrency_surfaces = [
        "ThreadPool",
        "ProcessPool",
        "multiprocessing",
        "concurrent.futures",
        "asyncio.gather",
    ]
    for forbidden in forbidden_concurrency_surfaces:
        assert forbidden not in combined
    assert "sequential_write_discipline" in combined


def test_fix65a_receipt_records_projection_repair() -> None:
    receipt = _load_json(FIX65A_RECEIPT)

    assert receipt["status"] == "PASS"
    assert receipt["write_applied"] is True
    assert receipt["missing_graph_projection_before"] == 2
    assert receipt["missing_graph_projection_after"] == 0
    assert receipt["dangling_edge_count"] == 0
    assert len(receipt["repair_rows"]) == 2
    assert {
        row["graph_projection_after"] for row in receipt["repair_rows"]
    } == {"support_candidate_graph"}


def test_fix65b_receipt_records_section_integrity_and_carry_forward_debt() -> None:
    receipt = _load_json(FIX65B_RECEIPT)

    assert receipt["status"] == "PASS"
    assert receipt["unresolved_cross_section_ref_count"] == 0
    assert receipt["section_count"] >= 5
    assert len(receipt["section_manifest_merkle_root"]) == 64
    assert receipt["automatic_source_sha256_rewrite"] == (
        "not_performed_historical_identity_preserved"
    )
    assert receipt["mismatched_source_sha256_count"] == 965
    assert receipt["missing_source_sha256_count"] == 136


def test_status_tokens_present_after_phase_execution() -> None:
    status = STATUS.read_text(encoding="utf-8")

    assert "fix65a_lmdb_graph_projection_coverage_repair_complete_phase_1573y" in status
    assert "fix65b_section_level_integrity_repair_complete_phase_1573y" in status
    assert "public_path_remains_blocked_phase_1573y" in status


def test_walkthrough_records_non_claims_and_graph_delta() -> None:
    text = WALKTHROUGH.read_text(encoding="utf-8")

    assert "graph_delta" in text
    assert "No public RC activation occurred" in text
    assert "No Genesis signing occurred" in text
    assert "No ellipses" not in text
