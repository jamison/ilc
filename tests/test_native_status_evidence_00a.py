import copy
import json
import re
from pathlib import Path

import pytest

from tools.native_status_evidence.assemble_00a import (
    ASSERTIONS_VERIFIED,
    EXPECTED_SOURCE_SHA256,
    NON_CLAIMS,
    OUTPUT_PATH,
    OUTPUT_TOKEN,
    SCHEMA_VERSION,
    NativeStatusEvidence00aError,
    assemble_evidence,
    load_source,
)


def _evidence():
    return json.loads(OUTPUT_PATH.read_text())


def _source():
    return load_source()


def test_schema_structure():
    ev = _evidence()
    assert ev["schema_version"] == SCHEMA_VERSION
    assert ev["produced_by"] == "GAP-PUBLIC-RC-NATIVE-STATUS-EVIDENCE-00a"
    assert ev["result"] == "pass"
    assert ev["output_token"] == OUTPUT_TOKEN


def test_source_binding():
    ev = _evidence()
    assert ev["source_evidence"]["sha256"] == EXPECTED_SOURCE_SHA256
    assert ev["source_evidence"]["phase"] == "1603"


def test_assertion_and_non_claim_coverage():
    ev = _evidence()
    assert ev["assertions_verified"] == ASSERTIONS_VERIFIED
    assert ev["non_claims"] == NON_CLAIMS


def test_field_values():
    ev = _evidence()
    assert re.fullmatch(r"[0-9a-f]{96}", ev["agent_id"])
    assert ev["agent_id_valid"] is True
    assert ev["graph_node"]["node_id"].startswith("bafy")
    assert ev["graph_node"]["node_id_cid_version"] == 1
    assert ev["graph_node"]["graph_persistence"] == "persisted"
    assert ev["graph_node"]["primitive_type"] == "observation"
    assert ev["graph_node"]["source_refs_count"] == 1
    assert ev["ecu_status"]["ok"] is True
    assert ev["ecu_status"]["balance_ecu_source"] == "rust_balance_store_committed_aggregate"
    assert ev["ecu_status"]["pending_attribution_quote"] == "0"
    assert ev["ecu_status"]["committed_ecu_balance"] == "0"


def test_adversarial_result_not_pass():
    src = copy.deepcopy(_source())
    src["result"] = "fail"
    with pytest.raises(NativeStatusEvidence00aError, match="source_evidence_result_not_pass_00a"):
        assemble_evidence(src)


def test_adversarial_agent_id_invalid():
    src = copy.deepcopy(_source())
    src["agent_id"] = "z" * 96
    with pytest.raises(NativeStatusEvidence00aError, match="agent_id_invalid_in_source_evidence_00a"):
        assemble_evidence(src)


def test_adversarial_graph_persistence_not_persisted():
    src = copy.deepcopy(_source())
    src["submit"]["graph_persistence"] = "failed"
    with pytest.raises(NativeStatusEvidence00aError, match="graph_persistence_not_persisted_00a"):
        assemble_evidence(src)


def test_adversarial_balance_source_invalid():
    src = copy.deepcopy(_source())
    src["ecu_status"]["balance_ecu_source"] = "local_zero_state_no_source_configured"
    with pytest.raises(NativeStatusEvidence00aError, match="balance_ecu_source_invalid_00a"):
        assemble_evidence(src)


def test_adversarial_stale_marker_present():
    src = copy.deepcopy(_source())
    src["extra_marker"] = "python_in_memory_ecu_python_rust_balance_bridge_missing_phase_1597"
    with pytest.raises(NativeStatusEvidence00aError, match="stale_rust_bridge_marker_present_00a"):
        assemble_evidence(src)


def test_adversarial_source_schema_mismatch():
    src = copy.deepcopy(_source())
    src["schema_version"] = "phase_1603_public_user_smoke.v0.1"
    with pytest.raises(NativeStatusEvidence00aError, match="source_evidence_schema_mismatch_00a"):
        assemble_evidence(src)


def test_adversarial_primitive_type_invalid():
    src = copy.deepcopy(_source())
    src["submit"]["node_primitive_type"] = "claim"
    with pytest.raises(NativeStatusEvidence00aError, match="node_primitive_type_invalid_00a"):
        assemble_evidence(src)


def test_adversarial_source_refs_count_invalid():
    src = copy.deepcopy(_source())
    src["submit"]["source_refs"] = []
    with pytest.raises(NativeStatusEvidence00aError, match="source_refs_count_invalid_00a"):
        assemble_evidence(src)


def test_adversarial_gossip_delivery_unexpected():
    src = copy.deepcopy(_source())
    src["submit"]["gossip_delivery"] = "delivered"
    with pytest.raises(NativeStatusEvidence00aError, match="gossip_delivery_unexpected_00a"):
        assemble_evidence(src)


def test_adversarial_package_identity_invalid():
    src = copy.deepcopy(_source())
    src["package"]["version"] = "0.4.30"
    with pytest.raises(NativeStatusEvidence00aError, match="package_identity_invalid_00a"):
        assemble_evidence(src)


def test_adversarial_clean_venv_check_invalid():
    src = copy.deepcopy(_source())
    src["package"]["repo_import_leak_checked"] = False
    with pytest.raises(
        NativeStatusEvidence00aError,
        match="clean_venv_or_repo_import_leak_check_invalid_00a",
    ):
        assemble_evidence(src)


def test_adversarial_source_sha_mismatch():
    src = copy.deepcopy(_source())
    with pytest.raises(NativeStatusEvidence00aError, match="source_evidence_sha256_mismatch_00a"):
        assemble_evidence(src, source_sha256="0" * 64)
