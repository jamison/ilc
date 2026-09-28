#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Run the GAP-PUBLIC-RC-MULTI-AGENT-NATIVE-INGRESS-SMOKE-00 checks."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import shutil
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ilc_core.consensus.submit_ingress_endpoint_assertion import (
    PUBLIC_RC_NATIVE_SUBMIT_INGRESS_CDL_NOT_RATIFIED,
    PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NOT_ACTIVATED,
)
from ilc_core.epistemic.node_submission_runtime import EpistemicSubmissionError
from ilc_core.epistemic.truth_primitive_graph_store import (
    node_id_from_submission,
    write_truth_primitive_result,
)
from ilc_core.epistemic.truth_primitive_submission_runtime import (
    NATIVE_SUBMISSION_SIG_VERIFICATION_NOT_ACTIVATED,
    TruthPrimitiveResult,
    validate_truth_primitive_submission,
)
from ilc_core.identity.bls_backend import keypair_from_ikm_hex, sign_native_submit_bytes
from ilc_core.storage.truth_primitive_graph_lmdb_adapter import TruthPrimitiveGraphStore


PHASE = "GAP-PUBLIC-RC-MULTI-AGENT-NATIVE-INGRESS-SMOKE-00"
NETWORK_ID = "ilc-public-rc-01-testnet-harness"
OUT_DIR = Path("out/gap_public_rc_multi_agent_native_ingress_smoke_00")
DEFAULT_STORE_PATH = OUT_DIR / "truth_graph.lmdb"
DEFAULT_EVIDENCE_PATH = OUT_DIR / "smoke_evidence.json"


def _canonical_bytes(envelope: dict[str, Any]) -> bytes:
    return json.dumps(
        {key: value for key, value in envelope.items() if key != "sig"},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _keypair() -> tuple[str, str]:
    return keypair_from_ikm_hex(secrets.token_hex(32))


def _payload(claim: str) -> dict[str, Any]:
    return {
        "content": {
            "claim": claim,
            "source": "multi_agent_native_ingress_smoke_00",
        },
        "primitive_type": "observation",
        "epistemic_type": "objective",
        "parent_node_ids": [],
    }


def build_signed_envelope(
    *,
    secret_key_hex: str,
    agent_id: str,
    claim: str,
    epoch: int,
    signature_override: str | None = None,
    key_ref_override: str | None = None,
) -> dict[str, Any]:
    envelope: dict[str, Any] = {
        "v": 1,
        "primitive": "assert.truth",
        "agent_id": agent_id,
        "epoch": epoch,
        "payload": _payload(claim),
        "sig": "UNSIGNED",
    }
    canonical = _canonical_bytes(envelope)
    signature_hex = signature_override
    if signature_hex is None:
        signature_hex = sign_native_submit_bytes(secret_key_hex, canonical, NETWORK_ID)
    envelope["sig"] = {
        "schema_version": "native_submit_sig.v0.1",
        "verifier_profile": "native_submit_sig_profile.v0.1",
        "dst": f"ILC_NATIVE_TRUTH_SUBMIT_V1:{NETWORK_ID}",
        "payload_sha256": hashlib.sha256(canonical).hexdigest(),
        "signature_hex": signature_hex,
        "key_ref": key_ref_override or agent_id,
    }
    return envelope


def _assert_token(exc: EpistemicSubmissionError, token: str) -> str:
    if exc.token != token:
        raise AssertionError(f"expected {token}, got {exc.token}: {exc}") from exc
    return exc.token


def _persist(
    store: TruthPrimitiveGraphStore,
    envelope: dict[str, Any],
) -> tuple[TruthPrimitiveResult, dict[str, Any]]:
    result = validate_truth_primitive_submission(envelope)
    receipt = write_truth_primitive_result(store, envelope, result)
    node_id = receipt.get("node_id")
    if not isinstance(node_id, str) or not node_id.startswith("bafyrei"):
        raise AssertionError(f"expected CIDv1 node_id, got {node_id!r}")
    return result, receipt


def _scenario(
    number: int,
    name: str,
    *,
    passed: bool,
    **extra: Any,
) -> dict[str, Any]:
    return {"scenario": number, "name": name, "pass": passed, **extra}


def run_smoke(
    *,
    out_dir: Path = OUT_DIR,
    store_path: Path | None = None,
    reset_store: bool = True,
    write_evidence: bool = True,
) -> dict[str, Any]:
    store_path = store_path or out_dir / "truth_graph.lmdb"
    out_dir.mkdir(parents=True, exist_ok=True)
    if reset_store and store_path.exists():
        shutil.rmtree(store_path)
    store_path.parent.mkdir(parents=True, exist_ok=True)
    os.environ["ILC_TRUTH_GRAPH_STORE_PATH"] = str(store_path)

    guard_states = {
        "NATIVE_SUBMISSION_SIG_VERIFICATION_NOT_ACTIVATED": NATIVE_SUBMISSION_SIG_VERIFICATION_NOT_ACTIVATED,
        "PUBLIC_RC_NATIVE_SUBMIT_INGRESS_CDL_NOT_RATIFIED": PUBLIC_RC_NATIVE_SUBMIT_INGRESS_CDL_NOT_RATIFIED,
        "PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NOT_ACTIVATED": PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NOT_ACTIVATED,
    }
    if any(guard_states.values()):
        raise RuntimeError(f"native_ingress_guard_not_cleared:{guard_states}")

    sk_a, pk_a = _keypair()
    sk_b, pk_b = _keypair()
    if pk_a == pk_b:
        raise RuntimeError("agent_key_collision")

    scenario_results: list[dict[str, Any]] = []
    store = TruthPrimitiveGraphStore(store_path)
    try:
        envelope_a = build_signed_envelope(
            secret_key_hex=sk_a,
            agent_id=pk_a,
            claim="Agent A smoke claim",
            epoch=0,
        )
        result_a, receipt_a = _persist(store, envelope_a)
        scenario_results.append(
            _scenario(
                1,
                "agent_a_accept",
                passed=receipt_a["nodes_written"] == 1,
                node_id=receipt_a["node_id"],
                nodes_written=receipt_a["nodes_written"],
                edges_written=receipt_a["edges_written"],
                graph_persistence="persisted",
            )
        )

        envelope_b = build_signed_envelope(
            secret_key_hex=sk_b,
            agent_id=pk_b,
            claim="Agent B smoke claim",
            epoch=0,
        )
        _result_b, receipt_b = _persist(store, envelope_b)
        scenario_results.append(
            _scenario(
                2,
                "agent_b_accept",
                passed=receipt_b["nodes_written"] == 1 and receipt_b["node_id"] != receipt_a["node_id"],
                node_id=receipt_b["node_id"],
                nodes_written=receipt_b["nodes_written"],
                edges_written=receipt_b["edges_written"],
                graph_persistence="persisted",
            )
        )

        idempotent_receipt = write_truth_primitive_result(store, envelope_a, result_a)
        scenario_results.append(
            _scenario(
                3,
                "graph_write_idempotent",
                passed=(
                    idempotent_receipt["node_id"] == receipt_a["node_id"]
                    and idempotent_receipt["nodes_written"] == 0
                ),
                node_id=idempotent_receipt["node_id"],
                nodes_written=idempotent_receipt["nodes_written"],
            )
        )

        invalid_sig = build_signed_envelope(
            secret_key_hex=sk_a,
            agent_id=pk_a,
            claim="Agent A invalid signature adversarial claim",
            epoch=1,
            signature_override="00" * 96,
        )
        try:
            validate_truth_primitive_submission(invalid_sig)
            raise AssertionError("invalid signature unexpectedly accepted")
        except EpistemicSubmissionError as exc:
            token = _assert_token(exc, "native_submit_sig_bls_verification_failed_CDL_118")
        scenario_results.append(
            _scenario(4, "invalid_sig_rejected", passed=True, rejection_token=token)
        )

        key_ref_mismatch = build_signed_envelope(
            secret_key_hex=sk_a,
            agent_id=pk_a,
            claim="Agent A key ref mismatch adversarial claim",
            epoch=2,
            key_ref_override=pk_b,
        )
        try:
            validate_truth_primitive_submission(key_ref_mismatch)
            raise AssertionError("key_ref mismatch unexpectedly accepted")
        except EpistemicSubmissionError as exc:
            token = _assert_token(exc, "native_submit_sig_key_ref_agent_id_mismatch_CDL_118")
        scenario_results.append(
            _scenario(5, "key_ref_mismatch_rejected", passed=True, rejection_token=token)
        )

        sig_length_invalid = build_signed_envelope(
            secret_key_hex=sk_a,
            agent_id=pk_a,
            claim="Agent A signature length adversarial claim",
            epoch=3,
            signature_override="00" * 95,
        )
        try:
            validate_truth_primitive_submission(sig_length_invalid)
            raise AssertionError("short signature unexpectedly accepted")
        except EpistemicSubmissionError as exc:
            token = _assert_token(exc, "native_submit_sig_signature_hex_length_invalid_CDL_118")
        scenario_results.append(
            _scenario(6, "sig_length_invalid_rejected", passed=True, rejection_token=token)
        )

        try:
            validate_truth_primitive_submission(envelope_a)
            raise AssertionError("replay unexpectedly accepted")
        except EpistemicSubmissionError as exc:
            token = _assert_token(exc, "native_submit_sig_replay_rejected_CDL_118")
        scenario_results.append(
            _scenario(7, "replay_rejected", passed=True, rejection_token=token)
        )

        deterministic_node_id = node_id_from_submission(envelope_a, result_a)
        scenario_results.append(
            _scenario(
                8,
                "node_id_deterministic",
                passed=deterministic_node_id == receipt_a["node_id"],
                node_id=deterministic_node_id,
                node_id_matches=True,
            )
        )
    finally:
        store.close()

    all_scenarios_pass = all(bool(row.get("pass")) for row in scenario_results)
    evidence = {
        "phase": PHASE,
        "network_id": NETWORK_ID,
        "executed_at_iso": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "guard_states_at_run": guard_states,
        "lmdb_store_path": str(store_path),
        "agent_a_pk_hex": pk_a,
        "agent_b_pk_hex": pk_b,
        "scenario_results": scenario_results,
        "all_scenarios_pass": all_scenarios_pass,
        "token": "multi_agent_native_ingress_smoke_complete_GAP_PUBLIC_RC_MULTI_AGENT_NATIVE_INGRESS_SMOKE_00",
    }
    if not all_scenarios_pass:
        raise AssertionError("one_or_more_smoke_scenarios_failed")
    if write_evidence:
        evidence_path = out_dir / "smoke_evidence.json"
        _atomic_write_json(evidence_path, evidence)
    return evidence


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, sort_keys=True, indent=2)
            handle.write("\n")
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--store-path", type=Path, default=None)
    parser.add_argument("--no-reset-store", action="store_true")
    args = parser.parse_args()

    evidence = run_smoke(
        out_dir=args.out_dir,
        store_path=args.store_path,
        reset_store=not args.no_reset_store,
        write_evidence=True,
    )
    print(json.dumps(evidence, sort_keys=True, separators=(",", ":"), allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
