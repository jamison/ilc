#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Run GAP-PUBLIC-RC-NATIVE-INGRESS-VPS-SMOKE-00 over ADR-0045 native QUIC."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ilc_core.consensus.binary_paths import installed_consensus_binary_command
from ilc_core.consensus.submit_ingress_endpoint_assertion import (
    PUBLIC_RC_NATIVE_SUBMIT_INGRESS_CDL_NOT_RATIFIED,
    PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NOT_ACTIVATED,
)
from ilc_core.epistemic.truth_primitive_submission_runtime import (
    NATIVE_SUBMISSION_SIG_VERIFICATION_NOT_ACTIVATED,
)
from ilc_core.identity.bls_backend import keypair_from_ikm_hex, sign_native_submit_bytes


PHASE = "GAP-PUBLIC-RC-NATIVE-INGRESS-VPS-SMOKE-00"
DEFAULT_OUT_DIR = Path("out/gap_public_rc_native_ingress_vps_smoke_00")
DEFAULT_EVIDENCE_PATH = DEFAULT_OUT_DIR / "smoke_evidence.json"
EXPECTED_TRANSPORT = "native_quic_bridge"
UNSIGNED_REJECTION_TOKEN = "native_submit_sig_unsigned_placeholder_rejected"


def _canonical_bytes(envelope: dict[str, Any]) -> bytes:
    return json.dumps(
        {key: value for key, value in envelope.items() if key != "sig"},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _single_line_json(envelope: dict[str, Any]) -> bytes:
    return json.dumps(
        envelope,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _build_payload(claim: str) -> dict[str, Any]:
    return {
        "content": {
            "claim": claim,
            "source": PHASE,
        },
        "primitive_type": "observation",
        "epistemic_type": "objective",
        "parent_node_ids": [],
    }


def _build_signed_envelope(
    *,
    secret_key_hex: str,
    public_key_hex: str,
    network_id: str,
    claim: str,
) -> dict[str, Any]:
    envelope: dict[str, Any] = {
        "v": 1,
        "agent_id": public_key_hex,
        "epoch": 0,
        "primitive": "assert.truth",
        "payload": _build_payload(claim),
    }
    canonical = _canonical_bytes(envelope)
    envelope["sig"] = {
        "schema_version": "native_submit_sig.v0.1",
        "verifier_profile": "native_submit_sig_profile.v0.1",
        "dst": f"ILC_NATIVE_TRUTH_SUBMIT_V1:{network_id}",
        "payload_sha256": hashlib.sha256(canonical).hexdigest(),
        "signature_hex": sign_native_submit_bytes(secret_key_hex, canonical, network_id),
        "key_ref": public_key_hex,
    }
    return envelope


def _build_unsigned_envelope(*, public_key_hex: str) -> dict[str, Any]:
    return {
        "v": 1,
        "agent_id": public_key_hex,
        "epoch": 0,
        "primitive": "assert.truth",
        "payload": _build_payload("VPS network acceptance unsigned rejection probe"),
        "sig": "UNSIGNED",
    }


def _load_receiver(path: Path) -> dict[str, str | None]:
    data = json.loads(path.read_text(encoding="utf-8"))
    uri = data.get("vps_endpoint")
    if data.get("transport") != EXPECTED_TRANSPORT:
        raise SystemExit(f"invalid_transport:{data.get('transport')!r}")
    if data.get("quic_blocker") is not None:
        raise SystemExit(f"unexpected_quic_blocker:{data.get('quic_blocker')!r}")
    if not isinstance(uri, str):
        raise SystemExit("vps_endpoint_missing")
    parsed = urlparse(uri)
    if parsed.scheme != "quic" or not parsed.hostname or parsed.port is None:
        raise SystemExit(f"vps_endpoint_invalid:{uri!r}")
    fingerprint = data.get("tls_fingerprint_sha256_der")
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        raise SystemExit("tls_fingerprint_sha256_der_invalid")
    return {
        "uri": uri,
        "endpoint": f"{parsed.hostname}:{parsed.port}",
        "transport": data.get("transport"),
        "quic_blocker": data.get("quic_blocker"),
        "tls_fingerprint_sha256_der": fingerprint,
    }


def _client_command() -> list[str]:
    installed = installed_consensus_binary_command("ilc_native_submit_client")
    if installed is not None:
        return list(installed)
    for candidate in (
        Path("ilc_consensus/target/release/ilc_native_submit_client"),
        Path("ilc_consensus/target/debug/ilc_native_submit_client"),
    ):
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return [str(candidate)]
    found = shutil.which("ilc_native_submit_client")
    if found:
        return [found]
    raise SystemExit("ilc_native_submit_client_not_found")


def _run_client(
    *,
    client_command: list[str],
    endpoint: str,
    fingerprint: str,
    envelope: dict[str, Any],
) -> dict[str, Any]:
    argv = [
        *client_command,
        "--endpoint",
        endpoint,
        "--expected-tls-fingerprint",
        fingerprint,
    ]
    body = _single_line_json(envelope)
    completed = subprocess.run(
        argv,
        input=body,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=20,
    )
    stdout = completed.stdout.decode("utf-8", errors="replace").strip()
    stderr = completed.stderr.decode("utf-8", errors="replace").strip()
    parsed: Any = None
    if stdout:
        parsed = json.loads(stdout)
    return {
        "argv": [Path(argv[0]).name, *argv[1:]],
        "exit_code": completed.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "response": parsed,
    }


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


def run_smoke(
    *,
    receiver_evidence_json: Path,
    network_id: str,
    output_dir: Path,
) -> dict[str, Any]:
    receiver = _load_receiver(receiver_evidence_json)
    guard_states = {
        "NATIVE_SUBMISSION_SIG_VERIFICATION_NOT_ACTIVATED": NATIVE_SUBMISSION_SIG_VERIFICATION_NOT_ACTIVATED,
        "PUBLIC_RC_NATIVE_SUBMIT_INGRESS_CDL_NOT_RATIFIED": PUBLIC_RC_NATIVE_SUBMIT_INGRESS_CDL_NOT_RATIFIED,
        "PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NOT_ACTIVATED": PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NOT_ACTIVATED,
    }
    if any(guard_states.values()):
        raise SystemExit(f"native_ingress_guard_not_cleared:{guard_states}")

    secret_key_hex, public_key_hex = keypair_from_ikm_hex(secrets.token_hex(32))
    client_command = _client_command()

    signed = _build_signed_envelope(
        secret_key_hex=secret_key_hex,
        public_key_hex=public_key_hex,
        network_id=network_id,
        claim="VPS network acceptance smoke claim",
    )
    signed_result = _run_client(
        client_command=client_command,
        endpoint=str(receiver["endpoint"]),
        fingerprint=str(receiver["tls_fingerprint_sha256_der"]),
        envelope=signed,
    )
    signed_response = signed_result["response"]
    if not isinstance(signed_response, dict):
        raise SystemExit("signed_response_not_json_object")
    receipt = signed_response.get("receipt")
    if (
        signed_result["exit_code"] != 0
        or signed_response.get("ok") is not True
        or not isinstance(signed_response.get("node_id"), str)
        or not signed_response["node_id"].startswith("bafyrei")
        or not isinstance(receipt, dict)
        or receipt.get("nodes_written", 0) < 1
        or receipt.get("native_submit_replay_written") != 1
    ):
        raise SystemExit(f"signed_scenario_failed:{signed_result}")

    unsigned = _build_unsigned_envelope(public_key_hex=public_key_hex)
    unsigned_result = _run_client(
        client_command=client_command,
        endpoint=str(receiver["endpoint"]),
        fingerprint=str(receiver["tls_fingerprint_sha256_der"]),
        envelope=unsigned,
    )
    unsigned_response = unsigned_result["response"]
    if not isinstance(unsigned_response, dict):
        raise SystemExit("unsigned_response_not_json_object")
    if (
        unsigned_result["exit_code"] != 1
        or unsigned_response.get("ok") is not False
        or unsigned_response.get("error") != UNSIGNED_REJECTION_TOKEN
    ):
        raise SystemExit(f"unsigned_scenario_failed:{unsigned_result}")

    node_id = signed_response["node_id"]
    scenario_results = [
        {
            "scenario": 1,
            "name": "signed_accepted",
            "exit_code": signed_result["exit_code"],
            "node_id": node_id,
            "nodes_written": receipt["nodes_written"],
            "edges_written": receipt.get("edges_written"),
            "native_submit_replay_written": receipt["native_submit_replay_written"],
            "graph_persistence": "persisted",
            "pass": True,
            "client_stdout": signed_result["stdout"],
            "client_stderr": signed_result["stderr"],
        },
        {
            "scenario": 2,
            "name": "unsigned_rejected",
            "exit_code": unsigned_result["exit_code"],
            "rejection_token": unsigned_response["error"],
            "pass": True,
            "client_stdout": unsigned_result["stdout"],
            "client_stderr": unsigned_result["stderr"],
        },
    ]
    evidence = {
        "phase": PHASE,
        "network_id": network_id,
        "executed_at_iso": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "receiver_evidence_json": str(receiver_evidence_json),
        "target_receiver_uri": receiver["uri"],
        "transport_profile": EXPECTED_TRANSPORT,
        "quic_blocker": receiver["quic_blocker"],
        "native_quic_client_evidence": " ".join(signed_result["argv"]),
        "guard_states_at_run": guard_states,
        "smoke_agent_pk_hex": public_key_hex,
        "scenario_results": scenario_results,
        "all_scenarios_pass": True,
        "non_claims": [
            "no_vps_lmdb_mutation_on_local_machine",
            "no_ilc_mint",
            "no_ecu_mint",
            "no_wallet_write",
            "no_epoch_transition",
            "no_settlement_commit",
            "no_package_publish",
            "no_public_mirror_push",
        ],
        "tokens": [
            "native_ingress_vps_smoke_signed_accepted_GAP_PUBLIC_RC_NATIVE_INGRESS_VPS_SMOKE_00",
            "native_ingress_vps_smoke_unsigned_rejected_GAP_PUBLIC_RC_NATIVE_INGRESS_VPS_SMOKE_00",
            "native_ingress_vps_network_acceptance_smoke_complete_GAP_PUBLIC_RC_NATIVE_INGRESS_VPS_SMOKE_00",
        ],
    }
    _atomic_write_json(output_dir / "smoke_evidence.json", evidence)
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receiver-evidence-json", type=Path, required=True)
    parser.add_argument("--network-id", required=True)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()
    evidence = run_smoke(
        receiver_evidence_json=args.receiver_evidence_json,
        network_id=args.network_id,
        output_dir=args.output_dir,
    )
    print(json.dumps(evidence, sort_keys=True, separators=(",", ":"), allow_nan=False))
    print("all_scenarios_pass: true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
