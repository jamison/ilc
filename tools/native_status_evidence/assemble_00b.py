#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Assemble GAP-PUBLIC-RC-NATIVE-STATUS-EVIDENCE-00b signed-peer evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import shutil
import tempfile
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path
from typing import Any

from ilc_core.consensus.submit_ingress_endpoint_assertion import (
    PUBLIC_RC_NATIVE_SUBMIT_INGRESS_CDL_NOT_RATIFIED,
    PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NOT_ACTIVATED,
    PublicSubmitIngressEndpointAssertion,
    assertion_content_sha256,
    canonical_endpoint_assertion_payload,
)
from ilc_core.epistemic.node_submission_runtime import EpistemicSubmissionError
from ilc_core.epistemic.truth_primitive_graph_store import (
    node_id_from_submission,
    write_truth_primitive_result,
)
from ilc_core.epistemic.truth_primitive_submission_runtime import (
    NATIVE_SUBMISSION_SIG_VERIFICATION_NOT_ACTIVATED,
    validate_truth_primitive_submission,
)
from ilc_core.epoch.genesis_settlement_destination import (
    GENESIS_CAPSULE_SIGNING_PK_HEX,
    GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX,
)
from ilc_core.identity.bls_backend import (
    keypair_from_ikm_hex,
    sign_native_submit_bytes,
    verify_endpoint_assertion_bytes,
)
from ilc_core.storage.truth_primitive_graph_lmdb_adapter import TruthPrimitiveGraphStore


PHASE = "GAP-PUBLIC-RC-NATIVE-STATUS-EVIDENCE-00b"
SCHEMA_VERSION = "native_status_evidence_00b.v0.1"
OUTPUT_TOKEN = "native_status_evidence_assembled_GAP_PUBLIC_RC_NATIVE_STATUS_EVIDENCE_00b"
NETWORK_ID = "ilc-public-rc-01-testnet-harness"
OUT_DIR = Path("out/gap_public_rc_native_status_evidence_00b")
DEFAULT_STORE_PATH = OUT_DIR / "truth_graph.lmdb"
DEFAULT_OUTPUT_PATH = OUT_DIR / "native_status_evidence_00b.json"
SOURCE_00A_PATH = Path("out/gap_public_rc_native_status_evidence_00a/native_status_evidence_00a.json")
ENDPOINT_ASSERTION_PATH = Path(
    "out/gap_public_rc_native_submit_ingress_guard_clear_00/endpoint_assertion.json"
)

ASSERTIONS_VERIFIED = [
    "all_three_guards_are_false",
    "endpoint_assertion_bls_verifies_offline",
    "tampered_endpoint_assertion_rejected",
    "signed_submission_produces_cid_node",
    "unsigned_submission_rejected_with_correct_token",
]

NON_CLAIMS = [
    "no_native_network_ingress_claim",
    "no_live_validator_acceptance_claim",
    "no_nonzero_ecu_claim",
    "no_monthly_close_claim",
    "no_ecu_minting",
    "no_ilc_minting",
    "no_settlement_claim",
    "test_agent_is_ephemeral_not_genesis",
]


class NativeStatusEvidence00bError(ValueError):
    """Named-token assembly failure."""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def package_version() -> str:
    """Return the source package version for this repo-local evidence phase."""

    if Path("pyproject.toml").exists():
        pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
        for line in pyproject.splitlines():
            stripped = line.strip()
            if stripped.startswith("version = "):
                return stripped.split("=", 1)[1].strip().strip('"')
    try:
        return metadata.version("ilc-core")
    except metadata.PackageNotFoundError:
        pass
    raise NativeStatusEvidence00bError("ilc_core_package_version_unavailable_00b")


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise NativeStatusEvidence00bError(f"{path.as_posix()}_not_object_00b")
    return payload


def _canonical_native_submit_bytes(envelope: dict[str, Any]) -> bytes:
    return json.dumps(
        {key: value for key, value in envelope.items() if key != "sig"},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _assert_guard_state() -> dict[str, bool]:
    guard_states = {
        "PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NOT_ACTIVATED": (
            PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NOT_ACTIVATED
        ),
        "NATIVE_SUBMISSION_SIG_VERIFICATION_NOT_ACTIVATED": (
            NATIVE_SUBMISSION_SIG_VERIFICATION_NOT_ACTIVATED
        ),
        "PUBLIC_RC_NATIVE_SUBMIT_INGRESS_CDL_NOT_RATIFIED": (
            PUBLIC_RC_NATIVE_SUBMIT_INGRESS_CDL_NOT_RATIFIED
        ),
    }
    if any(guard_states.values()):
        raise NativeStatusEvidence00bError(f"native_ingress_guard_not_false_00b:{guard_states}")
    return guard_states


def verify_endpoint_assertion(
    assertion_path: Path = ENDPOINT_ASSERTION_PATH,
) -> tuple[PublicSubmitIngressEndpointAssertion, str, bool, bool]:
    record = _load_json(assertion_path)
    assertion = PublicSubmitIngressEndpointAssertion.from_dict(record)
    payload_bytes = canonical_endpoint_assertion_payload(assertion)
    content_sha256 = assertion_content_sha256(assertion)
    if hashlib.sha256(payload_bytes).hexdigest() != content_sha256:
        raise NativeStatusEvidence00bError("endpoint_assertion_content_sha_mismatch_00b")
    verified = verify_endpoint_assertion_bytes(
        assertion.bls_public_key_hex,
        payload_bytes,
        assertion.bls_signature_hex,
        assertion.network_id,
    )
    tampered = bytearray(payload_bytes)
    tampered[0] ^= 0x01
    tampered_rejected = not verify_endpoint_assertion_bytes(
        assertion.bls_public_key_hex,
        bytes(tampered),
        assertion.bls_signature_hex,
        assertion.network_id,
    )
    if not verified:
        raise NativeStatusEvidence00bError("endpoint_assertion_bls_not_verified_00b")
    if not tampered_rejected:
        raise NativeStatusEvidence00bError("endpoint_assertion_tamper_not_rejected_00b")
    return assertion, content_sha256, verified, tampered_rejected


def build_signed_envelope(
    *,
    secret_key_hex: str,
    agent_id: str,
    epoch: int = 0,
    claim: str = "native status evidence 00b signed submission",
) -> dict[str, Any]:
    envelope: dict[str, Any] = {
        "v": 1,
        "primitive": "assert.truth",
        "agent_id": agent_id,
        "epoch": epoch,
        "payload": {
            "content": {
                "claim": claim,
                "source": "GAP-PUBLIC-RC-NATIVE-STATUS-EVIDENCE-00b",
            },
            "primitive_type": "observation",
            "epistemic_type": "objective",
            "parent_node_ids": [],
        },
        "sig": "UNSIGNED",
    }
    canonical = _canonical_native_submit_bytes(envelope)
    envelope["sig"] = {
        "schema_version": "native_submit_sig.v0.1",
        "verifier_profile": "native_submit_sig_profile.v0.1",
        "dst": f"ILC_NATIVE_TRUTH_SUBMIT_V1:{NETWORK_ID}",
        "payload_sha256": hashlib.sha256(canonical).hexdigest(),
        "signature_hex": sign_native_submit_bytes(secret_key_hex, canonical, NETWORK_ID),
        "key_ref": agent_id,
    }
    return envelope


def build_unsigned_envelope(*, agent_id: str) -> dict[str, Any]:
    return {
        "v": 1,
        "primitive": "assert.truth",
        "agent_id": agent_id,
        "epoch": 1,
        "payload": {
            "content": {"claim": "native status evidence 00b unsigned rejection"},
            "primitive_type": "observation",
            "epistemic_type": "objective",
            "parent_node_ids": [],
        },
        "sig": "UNSIGNED",
    }


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp_name, path)
    finally:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass


def assemble_evidence(
    *,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    store_path: Path = DEFAULT_STORE_PATH,
    source_00a_path: Path = SOURCE_00A_PATH,
    endpoint_assertion_path: Path = ENDPOINT_ASSERTION_PATH,
    reset_store: bool = True,
    produced_at_utc: str | None = None,
) -> dict[str, Any]:
    guard_states = _assert_guard_state()
    source_sha256 = sha256_file(source_00a_path)
    source_00a = _load_json(source_00a_path)
    if source_00a.get("output_token") != "native_status_evidence_assembled_GAP_PUBLIC_RC_NATIVE_STATUS_EVIDENCE_00a":
        raise NativeStatusEvidence00bError("source_00a_output_token_invalid_00b")

    assertion, endpoint_sha256, verified, tampered_rejected = verify_endpoint_assertion(
        endpoint_assertion_path
    )
    if assertion.bls_public_key_hex != GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX:
        raise NativeStatusEvidence00bError("endpoint_assertion_public_key_mismatch_00b")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    store_path.parent.mkdir(parents=True, exist_ok=True)
    if reset_store and store_path.exists():
        shutil.rmtree(store_path)
    os.environ["ILC_TRUTH_GRAPH_STORE_PATH"] = str(store_path)

    secret_key_hex, test_agent_id = keypair_from_ikm_hex(secrets.token_hex(32))
    if test_agent_id in {
        GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX,
        GENESIS_CAPSULE_SIGNING_PK_HEX,
        assertion.serving_agent_id,
    }:
        raise NativeStatusEvidence00bError("test_agent_reserved_key_collision_00b")

    signed_envelope = build_signed_envelope(
        secret_key_hex=secret_key_hex,
        agent_id=test_agent_id,
    )
    store = TruthPrimitiveGraphStore(store_path)
    try:
        result = validate_truth_primitive_submission(signed_envelope)
        write_receipt = write_truth_primitive_result(store, signed_envelope, result)
    finally:
        store.close()

    node_id = write_receipt.get("node_id")
    if not isinstance(node_id, str) or not node_id.startswith("bafy"):
        raise NativeStatusEvidence00bError("signed_submission_node_id_not_cid_v1_00b")
    if node_id_from_submission(signed_envelope, result) != node_id:
        raise NativeStatusEvidence00bError("signed_submission_node_id_not_deterministic_00b")

    unsigned_token = ""
    try:
        validate_truth_primitive_submission(build_unsigned_envelope(agent_id=test_agent_id))
        raise NativeStatusEvidence00bError("unsigned_submission_unexpectedly_accepted_00b")
    except EpistemicSubmissionError as exc:
        unsigned_token = exc.token
    if unsigned_token != "native_submit_sig_unsigned_placeholder_rejected":
        raise NativeStatusEvidence00bError("unsigned_submission_wrong_token_00b")

    evidence = {
        "schema_version": SCHEMA_VERSION,
        "produced_by": PHASE,
        "produced_at_utc": produced_at_utc or _utc_now(),
        "result": "pass",
        "source_evidence_00a": {
            "path": source_00a_path.as_posix(),
            "sha256": source_sha256,
        },
        "endpoint_assertion": {
            "assertion_content_sha256": endpoint_sha256,
            "bls_public_key_hex_prefix": assertion.bls_public_key_hex[:20],
            "bls_verification": "verified" if verified else "failed",
            "tampered_payload_rejected": tampered_rejected,
        },
        "signed_submission": {
            "test_agent_id_prefix": test_agent_id[:20],
            "node_id": node_id,
            "node_id_cid_version": 1,
            "graph_persistence": "persisted",
            "write_receipt": write_receipt,
        },
        "unsigned_rejection": {
            "token": unsigned_token,
            "confirmed": True,
        },
        "assertions_verified": list(ASSERTIONS_VERIFIED),
        "guard_states": guard_states,
        "phase_local_lmdb_path": store_path.as_posix(),
        "non_claims": list(NON_CLAIMS),
        "output_token": OUTPUT_TOKEN,
        "package": {
            "name": "ilc-core",
            "version": package_version(),
        },
    }
    _write_json_atomic(output_path, evidence)
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=DEFAULT_OUTPUT_PATH, type=Path)
    parser.add_argument("--store-path", default=DEFAULT_STORE_PATH, type=Path)
    parser.add_argument("--no-reset-store", action="store_true")
    args = parser.parse_args()
    evidence = assemble_evidence(
        output_path=args.output,
        store_path=args.store_path,
        reset_store=not args.no_reset_store,
    )
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
