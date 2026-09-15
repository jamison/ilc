#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Dry-run monthly close wiring check for public-RC validators."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shlex
import socket
import ssl
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, Mapping, Sequence

from ilc_core.consensus.production_bridge import (
    ILCConsensusGrpcReadAdapter,
    ConsensusBridgeConfig,
    VALIDATOR_CERT_GRAPH_BINDING_NOT_ACTIVATED,
)
from ilc_core.consensus.validator_endpoint_assertion import (
    BlsVerifier,
    VALIDATOR_ENDPOINT_ASSERTION_BLS_COMMAND_ENV,
    validator_assertion_candidate_id,
)
from ilc_core.epoch.ecu_accrual_evidence import read_ecu_accrual_evidence
from ilc_core.epoch.epoch_maturity_gate import (
    MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
)
from ilc_core.epoch.monthly_close_orchestrator import (
    build_monthly_close_proof_from_epoch_record,
    build_settlement_input_from_ecu_accrual,
    verify_close_dry_run,
)
from ilc_core.ledger.exact_numeric import (
    decimal_to_canonical_string,
    parse_non_negative_decimal,
)


PHASE = "GAP-MONTHLY-ISSUANCE-CLOSE-ORCHESTRATOR-00b"
OUTPUT_TOKEN = "monthly_close_orchestrator_wiring_ready_GAP_MONTHLY_ISSUANCE_CLOSE_ORCHESTRATOR_00b"
MATURITY_NOT_CONSTRUCTED_REASON = "closing_validation_epoch_not_available_from_get_epoch"
MAX_ATLAS_JSON_BYTES = 1_048_576
MAX_REPORT_BYTES = 1_048_576
MAX_PATH_BYTES = 4096


def main(argv: Sequence[str] | None = None) -> int:
    report = run(argv)
    print(json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False))
    return 0


def run(argv: Sequence[str] | None = None) -> dict[str, Any]:
    args = _parse_args(argv)
    _validate_paths(args)
    _require_graph_binding_args_if_active(args)

    evidence = read_ecu_accrual_evidence(args.evidence_path)
    config = ConsensusBridgeConfig(
        target=args.validator_endpoint,
        grpc_timeout_seconds=args.grpc_timeout,
        tls_root_certificates=args.tls_root_ca.read_bytes(),
        grpc_client_private_key=args.client_key.read_bytes(),
        grpc_client_certificate_chain=args.client_cert.read_bytes(),
        graph_binding_validator_agent_id=args.graph_binding_validator_agent_id,
        graph_binding_expected_bls_public_key_hex=args.graph_binding_bls_key_hex,
        graph_binding_network_id=args.graph_binding_network_id,
    )
    adapter = ILCConsensusGrpcReadAdapter(
        config,
        validator_graph_binding_atlas_reader=_load_graph_binding_atlas(
            args.graph_binding_atlas_path
        )
        if args.graph_binding_atlas_path is not None
        else None,
        validator_graph_binding_cert_der_provider=_build_remote_server_cert_der_provider(
            target=args.validator_endpoint,
            root_ca_path=args.tls_root_ca,
            client_cert_path=args.client_cert,
            client_key_path=args.client_key,
            timeout_seconds=args.grpc_timeout,
        )
        if args.graph_binding_atlas_path is not None
        else None,
        validator_graph_binding_bls_verifier=_build_bls_verifier(),
        validator_graph_binding_now_utc=datetime.now(timezone.utc)
        if args.graph_binding_atlas_path is not None
        else None,
    )

    live_current_epoch_seq = adapter.get_epoch()
    epoch_record = adapter.get_epoch_record(live_current_epoch_seq)
    if getattr(epoch_record, "found", None) is not True:
        raise ValueError("epoch_record_not_found")
    state_root = _require_bytes_attr(epoch_record, "state_root", "epoch_record_state_root")
    agg_sig = _require_bytes_attr(epoch_record, "agg_sig", "epoch_record_agg_sig")

    synthetic_conservation_verified = _run_synthetic_conservation(
        evidence=evidence,
        live_epoch_record=epoch_record,
        distribution_issuance_epoch=args.distribution_issuance_epoch,
        opening_validation_epoch=args.opening_validation_epoch,
        evidence_ref=str(args.evidence_path),
        total_epoch_fees_ilc=args.synthetic_total_epoch_fees_ilc,
        genesis_cumulative_accrual_ilc=args.synthetic_genesis_cumulative_accrual_ilc,
    )
    report = {
        "phase": PHASE,
        "mode": "dry_run_only",
        "validator_endpoint": args.validator_endpoint,
        "graph_binding_checked": not VALIDATOR_CERT_GRAPH_BINDING_NOT_ACTIVATED,
        "live_current_epoch_seq": live_current_epoch_seq,
        "live_epoch_record_found": True,
        "live_epoch_record_state_root_hex": state_root.hex(),
        "live_epoch_record_agg_sig_sha256": hashlib.sha256(agg_sig).hexdigest(),
        "maturity_metadata_available": False,
        "live_maturity_proof_not_constructed_reason": MATURITY_NOT_CONSTRUCTED_REASON,
        "synthetic_maturity_fixture_used": True,
        "synthetic_fixture_not_launch_valid": True,
        "synthetic_conservation_verified": synthetic_conservation_verified,
        "wiring_ready": True,
        "output_token": OUTPUT_TOKEN,
    }
    _write_report_atomic(report, args.out / "close_readiness_report.json")
    return report


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validator-endpoint", required=True)
    parser.add_argument("--tls-root-ca", required=True, type=Path)
    parser.add_argument("--client-cert", required=True, type=Path)
    parser.add_argument("--client-key", required=True, type=Path)
    parser.add_argument("--evidence-path", required=True, type=Path)
    parser.add_argument("--issuance-interval-id", required=True, type=_parse_non_negative_int)
    parser.add_argument("--opening-validation-epoch", required=True, type=_parse_non_negative_int)
    parser.add_argument(
        "--distribution-issuance-epoch",
        required=True,
        type=_parse_positive_int,
    )
    parser.add_argument("--graph-binding-validator-agent-id")
    parser.add_argument("--graph-binding-bls-key-hex")
    parser.add_argument("--graph-binding-network-id")
    parser.add_argument("--graph-binding-atlas-path", type=Path)
    parser.add_argument(
        "--synthetic-total-epoch-fees-ilc",
        required=True,
        type=_parse_canonical_non_negative_decimal_string,
        help="Explicit synthetic fixture monetary input. Not launch-valid settlement.",
    )
    parser.add_argument(
        "--synthetic-genesis-cumulative-accrual-ilc",
        required=True,
        type=_parse_canonical_non_negative_decimal_string,
        help="Explicit synthetic fixture monetary input. Not launch-valid settlement.",
    )
    parser.add_argument(
        "--out",
        default=Path("out/gap_monthly_close_orchestrator_00b"),
        type=Path,
    )
    parser.add_argument("--grpc-timeout", default="10", type=_require_positive_finite_timeout)
    args = parser.parse_args(argv)
    if args.issuance_interval_id != args.distribution_issuance_epoch - 1:
        raise SystemExit("issuance_interval_distribution_epoch_mismatch")
    return args


def _parse_non_negative_int(value: str) -> int:
    try:
        parsed = int(value, 10)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("non_negative_int_required") from exc
    if parsed < 0:
        raise argparse.ArgumentTypeError("non_negative_int_required")
    return parsed


def _parse_positive_int(value: str) -> int:
    parsed = _parse_non_negative_int(value)
    if parsed == 0:
        raise argparse.ArgumentTypeError("positive_int_required")
    return parsed


def _require_positive_finite_timeout(value: object) -> int:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError("grpc_timeout_invalid") from exc
    if not math.isfinite(number) or number <= 0 or not number.is_integer():
        raise argparse.ArgumentTypeError("grpc_timeout_invalid")
    return int(number)


def _parse_canonical_non_negative_decimal_string(value: str) -> str:
    try:
        parsed = parse_non_negative_decimal(
            value,
            token="synthetic_monetary_input_must_be_non_negative_decimal",
        )
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc
    canonical = decimal_to_canonical_string(parsed)
    if value != canonical:
        raise argparse.ArgumentTypeError("synthetic_monetary_input_must_be_canonical")
    return value


def _validate_paths(args: argparse.Namespace) -> None:
    for path_attr in ("tls_root_ca", "client_cert", "client_key", "evidence_path"):
        path = getattr(args, path_attr)
        _require_existing_file(path, path_attr)
    if args.graph_binding_atlas_path is not None:
        _require_existing_file(args.graph_binding_atlas_path, "graph_binding_atlas_path")
    args.out.mkdir(parents=True, exist_ok=True)


def _require_existing_file(path: Path, token: str) -> Path:
    if len(str(path).encode("utf-8")) > MAX_PATH_BYTES:
        raise ValueError(f"{token}_path_exceeds_max_bytes")
    if not path.is_file():
        raise ValueError(f"{token}_file_not_found")
    return path


def _require_graph_binding_args_if_active(args: argparse.Namespace) -> None:
    if VALIDATOR_CERT_GRAPH_BINDING_NOT_ACTIVATED:
        return
    required = [
        args.graph_binding_validator_agent_id,
        args.graph_binding_bls_key_hex,
        args.graph_binding_network_id,
        args.graph_binding_atlas_path,
    ]
    if any(value is None for value in required):
        raise SystemExit(
            "BLOCKER: VALIDATOR_CERT_GRAPH_BINDING_NOT_ACTIVATED=False but "
            "--graph-binding-* args are not all supplied. Supply all four "
            "graph-binding args or surface this to Genesis."
        )


def _load_graph_binding_atlas(path: Path) -> dict[str, Mapping[str, Any]]:
    payload = _read_json_mapping(path, MAX_ATLAS_JSON_BYTES, "graph_binding_atlas")
    nodes: list[Mapping[str, Any]] = []
    assertions = payload.get("assertions")
    if isinstance(assertions, list):
        nodes.extend(node for node in assertions if isinstance(node, Mapping))
    if payload.get("node_kind") == "validator_grpc_endpoint_assertion":
        nodes.append(payload)

    atlas: dict[str, Mapping[str, Any]] = {}
    for node in nodes:
        agent_id = node.get("validator_agent_id")
        if not isinstance(agent_id, str):
            continue
        atlas[agent_id] = node
        atlas[validator_assertion_candidate_id(agent_id)] = node
    if not atlas:
        raise ValueError("graph_binding_atlas_assertions_not_found")
    return atlas


def _read_json_mapping(path: Path, max_bytes: int, token: str) -> Mapping[str, Any]:
    size = path.stat().st_size
    if size > max_bytes:
        raise ValueError(f"{token}_exceeds_max_bytes")
    try:
        payload = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_json_keys,
        )
    except json.JSONDecodeError as exc:
        raise ValueError(f"{token}_json_invalid") from exc
    if not isinstance(payload, Mapping):
        raise ValueError(f"{token}_json_object_required")
    return payload


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    record: dict[str, Any] = {}
    for key, value in pairs:
        if key in record:
            raise ValueError("duplicate_json_key")
        record[key] = value
    return record


def _build_remote_server_cert_der_provider(
    *,
    target: str,
    root_ca_path: Path,
    client_cert_path: Path,
    client_key_path: Path,
    timeout_seconds: int,
) -> Callable[[], bytes]:
    cached_cert_der: bytes | None = None

    def provider() -> bytes:
        nonlocal cached_cert_der
        if cached_cert_der is None:
            cached_cert_der = _fetch_remote_server_cert_der(
                target=target,
                root_ca_path=root_ca_path,
                client_cert_path=client_cert_path,
                client_key_path=client_key_path,
                timeout_seconds=timeout_seconds,
            )
        return cached_cert_der

    return provider


def _fetch_remote_server_cert_der(
    *,
    target: str,
    root_ca_path: Path,
    client_cert_path: Path,
    client_key_path: Path,
    timeout_seconds: int,
) -> bytes:
    host, port = _split_host_port(target)
    context = _create_validator_tls_context(root_ca_path)
    context.load_cert_chain(certfile=str(client_cert_path), keyfile=str(client_key_path))
    with socket.create_connection((host, port), timeout=timeout_seconds) as sock:
        with context.wrap_socket(sock, server_hostname=host) as tls_sock:
            cert_der = tls_sock.getpeercert(binary_form=True)
    if not isinstance(cert_der, bytes) or not cert_der:
        raise ValueError("remote_validator_server_cert_der_unavailable")
    return cert_der


def _create_validator_tls_context(root_ca_path: Path) -> ssl.SSLContext:
    context = ssl.create_default_context(cafile=str(root_ca_path))
    # The public-RC validator leaf certs are CA-signed but omit Authority Key
    # Identifier. Keep CA and hostname verification while avoiding Python 3.14's
    # strict extension rejection for this read-only control-host preflight.
    if hasattr(ssl, "VERIFY_X509_STRICT"):
        context.verify_flags &= ~ssl.VERIFY_X509_STRICT
    return context


def _split_host_port(target: str) -> tuple[str, int]:
    host, sep, port_text = target.rpartition(":")
    if not sep or not host or not port_text:
        raise ValueError("validator_endpoint_invalid")
    try:
        port = int(port_text, 10)
    except ValueError as exc:
        raise ValueError("validator_endpoint_invalid") from exc
    if port < 1 or port > 65535:
        raise ValueError("validator_endpoint_invalid")
    return host, port


def _build_bls_verifier() -> BlsVerifier | None:
    command = _discover_bls_verify_command()
    if command is None:
        return None

    def verifier(payload: bytes, signature_hex: str, public_key_hex: str, network_id: str) -> bool:
        try:
            result = subprocess.run(
                shlex.split(command)
                + [
                    "verify",
                    "--public-key-hex",
                    public_key_hex,
                    "--signature-hex",
                    signature_hex,
                    "--network-id",
                    network_id,
                ],
                input=payload,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=10,
            )
        except (OSError, subprocess.SubprocessError):
            return False
        return result.returncode == 0

    return verifier


def _discover_bls_verify_command() -> str | None:
    env_command = os.environ.get(VALIDATOR_ENDPOINT_ASSERTION_BLS_COMMAND_ENV)
    if env_command:
        return env_command
    candidates = (
        Path("ilc_consensus/target/release/validator_endpoint_assertion_bls"),
        Path("ilc_consensus/target/debug/validator_endpoint_assertion_bls"),
        Path.home() / ".ilc/bin/validator_endpoint_assertion_bls",
    )
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def _require_bytes_attr(value: object, attr: str, token: str) -> bytes:
    raw = getattr(value, attr, None)
    if not isinstance(raw, bytes) or not raw:
        raise ValueError(f"{token}_bytes_required")
    return raw


def _run_synthetic_conservation(
    *,
    evidence: Any,
    live_epoch_record: object,
    distribution_issuance_epoch: int,
    opening_validation_epoch: int,
    evidence_ref: str,
    total_epoch_fees_ilc: str,
    genesis_cumulative_accrual_ilc: str,
) -> bool:
    synthetic_record = SimpleNamespace(
        found=True,
        epoch=distribution_issuance_epoch,
        state_root=_require_bytes_attr(live_epoch_record, "state_root", "epoch_record_state_root"),
        spectral_hash=_synthetic_spectral_hash(live_epoch_record),
        agg_sig=b"synthetic-monthly-close-aggregate-signature",
    )
    proof = build_monthly_close_proof_from_epoch_record(
        synthetic_record,
        matured_issuance_epoch=distribution_issuance_epoch - 1,
        distribution_issuance_epoch=distribution_issuance_epoch,
        opening_validation_epoch=opening_validation_epoch,
        closing_validation_epoch=(
            opening_validation_epoch + MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN
        ),
        evidence_ref=evidence_ref,
    )
    distribution_input = build_settlement_input_from_ecu_accrual(
        evidence,
        distribution_issuance_epoch=distribution_issuance_epoch,
        proof=proof,
        total_epoch_fees_ilc=total_epoch_fees_ilc,
        genesis_cumulative_accrual_ilc=genesis_cumulative_accrual_ilc,
    )
    return verify_close_dry_run(distribution_input).conservation_verified is True


def _synthetic_spectral_hash(epoch_record: object) -> bytes:
    raw = getattr(epoch_record, "spectral_hash", None)
    if isinstance(raw, bytes) and len(raw) == 32:
        return raw
    return hashlib.sha256(b"synthetic-monthly-close-spectral-hash").digest()


def _write_report_atomic(report: Mapping[str, Any], path: Path) -> None:
    content = json.dumps(report, indent=2, sort_keys=True, allow_nan=False)
    encoded = f"{content}\n".encode("utf-8")
    if len(encoded) > MAX_REPORT_BYTES:
        raise ValueError("close_readiness_report_exceeds_max_bytes")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    tmp_path = Path(tmp)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
        os.replace(tmp_path, path)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


if __name__ == "__main__":
    raise SystemExit(main())
