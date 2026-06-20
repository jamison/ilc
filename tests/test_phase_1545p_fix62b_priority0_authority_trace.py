from __future__ import annotations

import json
from pathlib import Path


REPORT_PATH = Path("out/genesis_atlas_fix62b_priority0_authority_trace_v0.1.json")
LEDGER_PATH = Path("docs/specs/ilc_fix62b_priority0_authority_trace_ledger_v0.1.json")
QUEUE_PATH = Path("docs/specs/ilc_fix62b_manual_graph_finish_queue_v0.1.json")
REPORT_MD_PATH = Path("docs/specs/ilc_fix62b_priority0_authority_trace_report_v0.1.md")
WALKTHROUGH_PATH = Path("docs/phases/phase_1545p_fix62b_priority0_authority_trace_walkthrough.md")
EVALUATOR_PATH = Path("tools/evaluators/sim_genesis_atlas_fix62b_priority0_authority_trace.py")
STATUS_PATH = Path("docs/phases/STATUS.md")


def _load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_fix62b_outputs_exist_and_are_valid_json() -> None:
    assert REPORT_PATH.exists()
    assert LEDGER_PATH.exists()
    assert QUEUE_PATH.exists()
    report = _load_json(REPORT_PATH)
    ledger = _load_json(LEDGER_PATH)
    queue = _load_json(QUEUE_PATH)
    assert report["phase"] == "1545p-Fix62b"
    assert report["status"] == "PASS"
    assert ledger["phase"] == "1545p-Fix62b"
    assert queue["phase"] == "1545p-Fix62b"
    assert queue["entry_count"] == len(queue["entries"])


def test_fix62b_priority0_ledger_has_all_dispositions() -> None:
    ledger = _load_json(LEDGER_PATH)
    dispositions = ledger["priority0_dispositions"]
    assert ledger["priority0_count"] == 54
    assert len(dispositions) == 54
    assert ledger["disposition_counts"]["authority_forward_resolved"] >= 5
    assert ledger["disposition_counts"]["typed_trace_resolved"] >= 20
    assert ledger["disposition_counts"]["deferred_no_authority_promotion"] >= 1
    assert all(item["disposition"] for item in dispositions)


def test_fix62b_applies_bounded_authority_edges() -> None:
    report = _load_json(REPORT_PATH)
    ledger = _load_json(LEDGER_PATH)
    accepted = report["edge_receipt"]["accepted_edge_count"]
    skipped = report["edge_receipt"]["skipped_edge_count"]
    assert report["edge_repair_semantics_present_count"] == ledger["edge_repair_count"]
    assert accepted + skipped <= ledger["edge_repair_count"]
    direct_targets = {
        item["target"]
        for item in ledger["edge_repairs"]
        if item["source"] == "artifact:genesis_intent_attestation_init_authority_map"
        and item["edge_type"] == "GOVERNS"
    }
    assert "cdl:020" in direct_targets
    assert "cdl:024" in direct_targets
    assert "cdl:032" in direct_targets
    assert "cdl:033" in direct_targets
    assert "cdl:082" in direct_targets
    assert "cdl:085_prelock_spec" not in direct_targets
    assert "cdl:021" not in direct_targets


def test_fix62b_uses_safe_writer_not_raw_adapter_mutation() -> None:
    source = EVALUATOR_PATH.read_text(encoding="utf-8")
    assert "AtlasLmdbSafeWriter" in source
    assert ".put_nodes(" not in source
    assert ".put_edges(" not in source
    assert ".replace_edges(" not in source
    assert "apply_plan(" in source
    assert "write_preimages(" in source
    assert "write_metadata(" in source


def test_fix62b_docs_preserve_non_activation_boundary() -> None:
    combined = "\n".join(
        [
            REPORT_MD_PATH.read_text(encoding="utf-8"),
            WALKTHROUGH_PATH.read_text(encoding="utf-8"),
        ]
    )
    assert "No Genesis signing occurred." in combined
    assert "No public RC activation occurred." in combined
    assert "No ECU minting, settlement, or entitlement was authorized." in combined
    assert "does not sign, publish" in combined


def test_fix62b_status_tokens_present() -> None:
    text = STATUS_PATH.read_text(encoding="utf-8")
    assert "fix62b_priority0_authority_trace_complete" in text
    assert "fix62b_priority0_manual_ledger_materialized" in text
    assert "fix62b_lmdb_edges_applied" in text
    assert "fix62b_complete" in text
