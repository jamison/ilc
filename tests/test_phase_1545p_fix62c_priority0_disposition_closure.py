from __future__ import annotations

import json
from pathlib import Path


REPORT_PATH = Path("out/genesis_atlas_fix62c_priority0_disposition_v0.1.json")
LEDGER_PATH = Path("docs/specs/ilc_fix62c_priority0_disposition_ledger_v0.1.json")
QUEUE_PATH = Path("docs/specs/ilc_fix62c_manual_graph_finish_queue_v0.1.json")
REPORT_MD_PATH = Path("docs/specs/ilc_fix62c_priority0_disposition_report_v0.1.md")
WALKTHROUGH_PATH = Path("docs/phases/phase_1545p_fix62c_priority0_disposition_walkthrough.md")
EVALUATOR_PATH = Path("tools/evaluators/sim_genesis_atlas_fix62c_priority0_disposition_closure.py")
STATUS_PATH = Path("docs/phases/STATUS.md")


def _load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_fix62c_outputs_exist_and_are_valid_json() -> None:
    assert REPORT_PATH.exists()
    assert LEDGER_PATH.exists()
    assert QUEUE_PATH.exists()
    report = _load_json(REPORT_PATH)
    ledger = _load_json(LEDGER_PATH)
    queue = _load_json(QUEUE_PATH)
    assert report["phase"] == "1545p-Fix62c"
    assert report["status"] == "PASS"
    assert ledger["phase"] == "1545p-Fix62c"
    assert queue["phase"] == "1545p-Fix62c"
    assert queue["entry_count"] == len(queue["entries"])


def test_fix62c_closes_all_residual_priority0_entries() -> None:
    ledger = _load_json(LEDGER_PATH)
    queue = _load_json(QUEUE_PATH)
    assert ledger["priority0_count"] == 9
    assert ledger["disposition_counts"] == {
        "support_material_root_classified": 4,
        "support_stub_classified": 1,
        "typed_trace_resolved_existing_same_authority": 1,
        "typed_trace_resolved_existing_supersession": 3,
    }
    assert queue["entry_count"] == 4570
    assert queue["priority_counts"].get("0", 0) == 0
    assert all(entry["priority"] != 0 for entry in queue["entries"])


def test_fix62c_support_edges_are_classification_not_root_governs() -> None:
    ledger = _load_json(LEDGER_PATH)
    support_targets = {
        "cdl:021",
        "artifact:generated_evidence_material_root_1545p_fix22",
        "artifact:genesis_private_local_material_root_1545p_fix22",
        "artifact:genesis_source_tree_manifest_candidate_1545p_fix38",
        "artifact:public_release_candidate_material_root_1545p_fix22",
    }
    observed = {
        item["source"]: item
        for item in ledger["support_classification_edges"]
    }
    assert set(observed) == support_targets
    for item in observed.values():
        assert item["edge_type"] == "CLASSIFIED_BY"
        assert item["target"] == "policy:full_repo_genesis_atlas_candidate_unsigned_support_only_phase_1545p_fix22"

    source = EVALUATOR_PATH.read_text(encoding="utf-8")
    assert '"GOVERNS"' not in source
    assert "artifact:genesis_intent_attestation_init_authority_map" in source


def test_fix62c_uses_safe_writer_not_raw_adapter_mutation() -> None:
    source = EVALUATOR_PATH.read_text(encoding="utf-8")
    assert "AtlasLmdbSafeWriter" in source
    assert ".put_nodes(" not in source
    assert ".put_edges(" not in source
    assert ".replace_edges(" not in source
    assert "apply_plan(" in source
    assert "write_preimages(" in source
    assert "write_metadata(" in source


def test_fix62c_preimages_and_queue_metadata_are_phase_local() -> None:
    source = EVALUATOR_PATH.read_text(encoding="utf-8")
    assert "v0.4.fix62c_priority0_disposition" in source
    assert "return fix62b._queue_payload" not in source
    queue = _load_json(QUEUE_PATH)
    assert queue["source_queue"] == "docs/specs/ilc_fix62b_manual_graph_finish_queue_v0.1.json"


def test_fix62c_docs_preserve_non_activation_boundary() -> None:
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


def test_fix62c_status_tokens_present() -> None:
    text = STATUS_PATH.read_text(encoding="utf-8")
    assert "fix62c_priority0_disposition_closure_complete" in text
    assert "fix62c_priority0_queue_cleared" in text
    assert "fix62c_support_classification_edges_applied" in text
    assert "fix62c_complete" in text
