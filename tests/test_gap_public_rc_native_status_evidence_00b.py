from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pytest

from ilc_core.consensus import submit_ingress_endpoint_assertion as endpoint
from ilc_core.consensus.submit_ingress_endpoint_assertion import (
    PublicSubmitIngressEndpointAssertion,
    canonical_endpoint_assertion_payload,
)
from ilc_core.epistemic import truth_primitive_submission_runtime as truth_runtime
from ilc_core.epoch.genesis_settlement_destination import (
    GENESIS_CAPSULE_SIGNING_PK_HEX,
    GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX,
)
from ilc_core.identity.bls_backend import verify_endpoint_assertion_bytes
from tools.native_status_evidence import assemble_00b as assemble_00b_module
from tools.native_status_evidence.assemble_00b import (
    ASSERTIONS_VERIFIED,
    DEFAULT_OUTPUT_PATH,
    ENDPOINT_ASSERTION_PATH,
    NETWORK_ID,
    NON_CLAIMS,
    OUTPUT_TOKEN,
    SCHEMA_VERSION,
    SOURCE_00A_PATH,
    NativeStatusEvidence00bError,
    assemble_evidence,
    sha256_file,
    verify_endpoint_assertion,
)


def _evidence() -> dict[str, object]:
    return json.loads(DEFAULT_OUTPUT_PATH.read_text(encoding="utf-8"))


def _endpoint_record() -> dict[str, object]:
    return json.loads(ENDPOINT_ASSERTION_PATH.read_text(encoding="utf-8"))


def test_all_guards_are_false() -> None:
    assert endpoint.PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NOT_ACTIVATED is False
    assert truth_runtime.NATIVE_SUBMISSION_SIG_VERIFICATION_NOT_ACTIVATED is False
    assert endpoint.PUBLIC_RC_NATIVE_SUBMIT_INGRESS_CDL_NOT_RATIFIED is False


def test_endpoint_assertion_json_exists() -> None:
    assert ENDPOINT_ASSERTION_PATH.exists()
    assert isinstance(_endpoint_record(), dict)


def test_endpoint_assertion_has_required_fields() -> None:
    record = _endpoint_record()
    for field in ("bls_signature_hex", "bls_public_key_hex", "serving_agent_id", "network_id"):
        assert isinstance(record.get(field), str)
        assert record[field]


def test_endpoint_assertion_bls_public_key_matches_constant() -> None:
    record = _endpoint_record()
    assert record["bls_public_key_hex"] == GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX


def test_endpoint_assertion_bls_verifies_offline() -> None:
    assertion = PublicSubmitIngressEndpointAssertion.from_dict(_endpoint_record())
    payload = canonical_endpoint_assertion_payload(assertion)
    assert (
        verify_endpoint_assertion_bytes(
            assertion.bls_public_key_hex,
            payload,
            assertion.bls_signature_hex,
            assertion.network_id,
        )
        is True
    )


def test_tampered_endpoint_assertion_rejected() -> None:
    assertion = PublicSubmitIngressEndpointAssertion.from_dict(_endpoint_record())
    payload = bytearray(canonical_endpoint_assertion_payload(assertion))
    payload[0] ^= 0x01
    assert (
        verify_endpoint_assertion_bytes(
            assertion.bls_public_key_hex,
            bytes(payload),
            assertion.bls_signature_hex,
            assertion.network_id,
        )
        is False
    )


def test_evidence_receipt_00b_exists() -> None:
    assert DEFAULT_OUTPUT_PATH.exists()
    assert isinstance(_evidence(), dict)


def test_evidence_receipt_required_fields() -> None:
    ev = _evidence()
    assert ev["schema_version"] == SCHEMA_VERSION
    assert ev["produced_by"] == "GAP-PUBLIC-RC-NATIVE-STATUS-EVIDENCE-00b"
    assert ev["result"] == "pass"
    assert ev["output_token"] == OUTPUT_TOKEN
    for field in (
        "source_evidence_00a",
        "endpoint_assertion",
        "signed_submission",
        "unsigned_rejection",
        "assertions_verified",
        "non_claims",
        "package",
    ):
        assert field in ev


def test_evidence_receipt_endpoint_assertion_verified() -> None:
    ev = _evidence()
    endpoint_ev = ev["endpoint_assertion"]
    assert endpoint_ev["bls_verification"] == "verified"
    assert endpoint_ev["tampered_payload_rejected"] is True


def test_evidence_receipt_source_binding() -> None:
    ev = _evidence()
    source = ev["source_evidence_00a"]
    assert source["path"] == SOURCE_00A_PATH.as_posix()
    assert source["sha256"] == sha256_file(SOURCE_00A_PATH)


def test_evidence_receipt_non_claims_present() -> None:
    ev = _evidence()
    assert ev["non_claims"] == NON_CLAIMS


def test_evidence_receipt_assertions_verified() -> None:
    ev = _evidence()
    assert ev["assertions_verified"] == ASSERTIONS_VERIFIED


def test_evidence_receipt_node_id_is_cid_v1() -> None:
    ev = _evidence()
    signed = ev["signed_submission"]
    assert signed["node_id"].startswith("bafy")
    assert signed["node_id_cid_version"] == 1
    assert signed["graph_persistence"] == "persisted"
    assert signed["write_receipt"]["node_id"] == signed["node_id"]


def test_evidence_receipt_unsigned_rejection_confirmed() -> None:
    ev = _evidence()
    unsigned = ev["unsigned_rejection"]
    assert unsigned["token"] == "native_submit_sig_unsigned_placeholder_rejected"
    assert unsigned["confirmed"] is True


def test_no_genesis_key_used_as_test_agent() -> None:
    ev = _evidence()
    prefix = ev["signed_submission"]["test_agent_id_prefix"]
    assert prefix != GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX[:20]
    assert prefix != GENESIS_CAPSULE_SIGNING_PK_HEX[:20]


def test_assemble_evidence_fresh_tmp_store(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prior_store_path = "/preexisting/truth-graph.lmdb"
    monkeypatch.setenv("ILC_TRUTH_GRAPH_STORE_PATH", prior_store_path)
    output_path = tmp_path / "native_status_evidence_00b.json"
    store_path = tmp_path / "truth_graph.lmdb"
    ev = assemble_evidence(
        output_path=output_path,
        store_path=store_path,
        produced_at_utc="2026-09-29T00:00:00Z",
    )
    assert output_path.exists()
    assert store_path.exists()
    assert ev["result"] == "pass"
    assert re.fullmatch(r"[0-9a-f]{20}", ev["signed_submission"]["test_agent_id_prefix"])
    assert os.environ["ILC_TRUTH_GRAPH_STORE_PATH"] == prior_store_path


def test_assemble_evidence_exception_does_not_create_graph_store_env(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ILC_TRUTH_GRAPH_STORE_PATH", raising=False)

    def _fail_after_store_setup(_ikm_hex: str) -> tuple[str, str]:
        raise RuntimeError("synthetic_key_generation_failure")

    monkeypatch.setattr(assemble_00b_module, "keypair_from_ikm_hex", _fail_after_store_setup)

    with pytest.raises(RuntimeError, match="synthetic_key_generation_failure"):
        assemble_evidence(
            output_path=tmp_path / "native_status_evidence_00b.json",
            store_path=tmp_path / "truth_graph.lmdb",
            produced_at_utc="2026-09-29T00:00:00Z",
        )

    assert "ILC_TRUTH_GRAPH_STORE_PATH" not in os.environ


def test_verify_endpoint_assertion_rejects_signature_tamper(tmp_path: Path) -> None:
    record = _endpoint_record()
    record["bls_signature_hex"] = "00" * 96
    tampered_path = tmp_path / "endpoint_assertion.json"
    tampered_path.write_text(json.dumps(record, sort_keys=True), encoding="utf-8")

    with pytest.raises(NativeStatusEvidence00bError, match="endpoint_assertion_bls_not_verified_00b"):
        verify_endpoint_assertion(tampered_path)


def test_assemble_rejects_bad_00a_token(tmp_path: Path) -> None:
    source = json.loads(SOURCE_00A_PATH.read_text(encoding="utf-8"))
    source["output_token"] = "wrong"
    source_path = tmp_path / "00a.json"
    source_path.write_text(json.dumps(source, sort_keys=True), encoding="utf-8")

    with pytest.raises(NativeStatusEvidence00bError, match="source_00a_output_token_invalid_00b"):
        assemble_evidence(
            output_path=tmp_path / "out.json",
            store_path=tmp_path / "truth_graph.lmdb",
            source_00a_path=source_path,
        )
