from __future__ import annotations

import json
from pathlib import Path


REPORT_PATH = Path("out/genesis_atlas_fix62a_attribution_substrate_closure_v0.1.json")
QUEUE_PATH = Path("docs/specs/ilc_fix62a_manual_graph_finish_queue_v0.1.json")
REPORT_MD_PATH = Path("docs/specs/ilc_fix62a_attribution_substrate_closure_report_v0.1.md")
WALKTHROUGH_PATH = Path("docs/phases/phase_1545p_fix62a_attribution_substrate_closure_walkthrough.md")
EVALUATOR_PATH = Path("tools/evaluators/sim_genesis_atlas_fix62a_attribution_substrate_closure.py")
STATUS_PATH = Path("docs/phases/STATUS.md")


def _load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_fix62a_outputs_exist_and_are_valid_json() -> None:
    assert REPORT_PATH.exists()
    assert QUEUE_PATH.exists()
    report = _load_json(REPORT_PATH)
    queue = _load_json(QUEUE_PATH)
    assert report["phase"] == "1545p-Fix62a"
    assert report["status"] == "PASS"
    assert queue["phase"] == "1545p-Fix62a"
    assert queue["entry_count"] == len(queue["entries"])


def test_fix62a_creator_substrate_closed_for_public_eligible_nodes() -> None:
    report = _load_json(REPORT_PATH)
    assert report["post_closure_creator_missing_public_eligible"] == 0
    assert report["public_eligible_node_count"] >= 15572
    assert report["public_eligible_with_creator_after"] >= report["public_eligible_node_count"]


def test_fix62a_runtime_bindings_and_manual_queue_present() -> None:
    report = _load_json(REPORT_PATH)
    queue = _load_json(QUEUE_PATH)
    assert report["runtime_binding_semantics_present_count"] >= 10
    assert report["manual_queue"]["entry_count"] > 1000
    assert "authority_forward_trace_missing" in report["manual_queue"]["reason_counts"]
    assert all(entry["batch_id"].startswith("fix62a_batch_") for entry in queue["entries"][:25])


def test_fix62a_uses_safe_writer_not_raw_adapter_mutation() -> None:
    source = EVALUATOR_PATH.read_text(encoding="utf-8")
    assert "AtlasLmdbSafeWriter" in source
    assert ".put_nodes(" not in source
    assert ".put_edges(" not in source
    assert ".replace_edges(" not in source
    assert "update_node_fields(" in source


def test_fix62a_docs_preserve_non_activation_boundary() -> None:
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


def test_fix62a_status_tokens_present() -> None:
    text = STATUS_PATH.read_text(encoding="utf-8")
    assert "fix62a_attribution_substrate_closure_complete" in text
    assert "fix62a_creator_resolution_manifest_materialized" in text
    assert "fix62a_manual_graph_finish_queue_produced" in text
    assert "fix62a_complete" in text
