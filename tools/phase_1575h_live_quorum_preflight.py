#!/usr/bin/env python3
"""Read-only live-quorum preflight for Phase 1575h.

This tool is intentionally non-activating. It checks repo tokens, runtime guard
constants, rehearsal evidence, VPS reachability, service listeners, and
validator-harness quorum liveness without starting processes, deleting DBs, or
sending epoch checkpoints.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import socket
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PHASE = "1575h-readiness"
SCHEMA_VERSION = "ilc.phase1575h.live_quorum_preflight.v1"

REQUIRED_STATUS_TOKENS = (
    "public_rc_live_phase_1575c",
    "two_single_lock_guards_cleared_phase_1575g",
    "economic_guards_cleared_phase_1575g",
    "epoch_0_to_1_private_rehearsal_passed_phase_1575b_fix9",
    "economic_activation_certificate_complete_phase_1575b",
    "phase_1575h_fix1_security_preflight_committed",
    "phase_1575h_fix1a_low_findings_closed",
    "phase_1575h_fix2_remaining_security_findings_closed",
)

GUARD_EXPECTATIONS = (
    (
        "PRODUCTION_EMISSION_NOT_ACTIVATED",
        Path("ilc_core/epoch/epoch_emission_production_path.py"),
        False,
    ),
    (
        "CONVERSION_CANDIDATE_RUNTIME_NOT_ACTIVATED",
        Path("ilc_core/ledger/conversion_candidate_runtime.py"),
        False,
    ),
    (
        "TREASURY_DISTRIBUTION_NOT_ACTIVATED",
        Path("ilc_core/epoch/treasury_validator_reward_production_path.py"),
        True,
    ),
    (
        "VALIDATOR_ADMISSION_NOT_ACTIVATED",
        Path("ilc_core/validator/validator_admission_ejection_production_path.py"),
        True,
    ),
    (
        "PRODUCTIVE_ECU_EXPANSION_NOT_ACTIVATED",
        Path("ilc_core/economics/productive_ecu_expansion_bounty_runtime.py"),
        True,
    ),
    (
        "EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED",
        Path("ilc_core/epoch/ejected_stake_distribution_production_path.py"),
        True,
    ),
)

REHEARSAL_EVIDENCE_PATH = Path(
    "out/block6_epoch_0_to_1_private_transition_rehearsal_fix9/evidence_records.json"
)

VPS_ALIASES = ("ilc-node-2", "ilc-node-3")


@dataclass(frozen=True)
class ValidatorEndpoint:
    validator_id: int
    host_label: str
    host: str
    quic_port: int
    grpc_port: int | None = None


PHASE1360_VALIDATORS = (
    ValidatorEndpoint(1, "ilc-node-2", "100.112.32.42", 50155, 50165),
    ValidatorEndpoint(2, "ilc-node-2", "100.112.32.42", 50152, 50162),
    ValidatorEndpoint(3, "ilc-node-3", "100.91.33.46", 50153, None),
    ValidatorEndpoint(4, "ilc-node-6", "100.72.17.38", 50154, None),
)

SERVING_RECEIVERS = (
    ("ilc-node-2", "100.112.32.42", 8443),
    ("ilc-node-3", "100.91.33.46", 8443),
)


def stable_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = stable_json(data) + "\n"
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        os.chmod(tmp_name, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def run_command(argv: list[str], *, timeout_seconds: int) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            argv,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
        )
        return {
            "argv": argv,
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "argv": argv,
            "returncode": None,
            "stdout": (exc.stdout or "").strip() if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "").strip() if isinstance(exc.stderr, str) else "",
            "timed_out": True,
        }


def ssh_command(alias: str, command: str, *, timeout_seconds: int) -> dict[str, Any]:
    return run_command(
        [
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=8",
            "-o",
            "ConnectionAttempts=1",
            alias,
            command,
        ],
        timeout_seconds=timeout_seconds,
    )


def tcp_probe(host: str, port: int, *, timeout_seconds: float = 3.0) -> dict[str, Any]:
    try:
        with socket.create_connection((host, port), timeout=timeout_seconds):
            return {"host": host, "port": port, "open": True, "error": None}
    except OSError as exc:
        return {"host": host, "port": port, "open": False, "error": type(exc).__name__}


def udp_listener_probe(endpoint: ValidatorEndpoint) -> dict[str, Any]:
    """Check the remote QUIC UDP listener from the host that owns the socket."""
    command = (
        "ss -lunp 2>/dev/null | "
        f"awk '$4 ~ /:{endpoint.quic_port}$/ {{ print; found=1 }} END {{ exit found ? 0 : 1 }}'"
    )
    result = ssh_command(endpoint.host_label, command, timeout_seconds=12)
    return {
        "host": endpoint.host,
        "port": endpoint.quic_port,
        "transport": "udp",
        "probe_method": "remote_ss_udp_listener",
        "open": result["returncode"] == 0 and not result["timed_out"],
        "command": result,
    }


def bool_constant_from_file(path: Path, name: str) -> bool | None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            continue
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, bool):
            return node.value.value
    return None


def status_token_checks(repo_root: Path) -> dict[str, Any]:
    text = (repo_root / "docs/phases/STATUS.md").read_text(encoding="utf-8")
    tokens = {
        token: {"present": token in text}
        for token in REQUIRED_STATUS_TOKENS
    }
    return {
        "tokens": tokens,
        "passed": all(record["present"] for record in tokens.values()),
    }


def guard_checks(repo_root: Path) -> dict[str, Any]:
    records: dict[str, Any] = {}
    for name, rel_path, expected in GUARD_EXPECTATIONS:
        path = repo_root / rel_path
        actual = bool_constant_from_file(path, name) if path.exists() else None
        records[name] = {
            "path": str(rel_path),
            "expected": expected,
            "actual": actual,
            "passed": actual is expected,
        }
    return {
        "guards": records,
        "passed": all(record["passed"] for record in records.values()),
    }


def rehearsal_check(repo_root: Path) -> dict[str, Any]:
    path = repo_root / REHEARSAL_EVIDENCE_PATH
    if not path.exists():
        return {"path": str(REHEARSAL_EVIDENCE_PATH), "passed": False, "reason": "missing"}
    payload = json.loads(path.read_text(encoding="utf-8"))
    passed = payload.get("epoch_0_to_1_private_transition_rehearsal") == "passed"
    return {
        "path": str(REHEARSAL_EVIDENCE_PATH),
        "phase": payload.get("phase"),
        "epoch_0_to_1_private_transition_rehearsal": payload.get(
            "epoch_0_to_1_private_transition_rehearsal"
        ),
        "passed": passed,
    }


def quorum_threshold(n: int) -> int:
    if n <= 0:
        raise ValueError("validator_count_must_be_positive")
    return 2 * ((n - 1) // 3) + 1


def validator_endpoint_checks() -> dict[str, Any]:
    records = []
    for endpoint in PHASE1360_VALIDATORS:
        quic = udp_listener_probe(endpoint)
        grpc = tcp_probe(endpoint.host, endpoint.grpc_port) if endpoint.grpc_port else None
        records.append(
            {
                "validator_id": endpoint.validator_id,
                "host_label": endpoint.host_label,
                "host": endpoint.host,
                "quic": quic,
                "grpc": grpc,
            }
        )
    open_quic = [record for record in records if record["quic"]["open"]]
    threshold = quorum_threshold(len(PHASE1360_VALIDATORS))
    return {
        "validator_count": len(PHASE1360_VALIDATORS),
        "quorum_threshold": threshold,
        "open_quic_count": len(open_quic),
        "quorum_reachable": len(open_quic) >= threshold,
        "validators": records,
    }


def serving_receiver_checks() -> dict[str, Any]:
    records = []
    for label, host, port in SERVING_RECEIVERS:
        probe = tcp_probe(host, port)
        records.append({"host_label": label, "probe": probe})
    return {
        "active_receiver_count": sum(1 for record in records if record["probe"]["open"]),
        "receivers": records,
        "peer_set_minimum_plausible": any(record["probe"]["open"] for record in records),
    }


def vps_checks(*, include_ssh: bool) -> dict[str, Any]:
    if not include_ssh:
        return {"skipped": True, "reason": "ssh_checks_disabled"}
    records = {}
    command = (
        "hostname; date -u; uptime; df -h /; "
        "pgrep -fa 'validator_harness' || true; "
        "pgrep -fa 'openclaw|openclaw-node' || true; "
        "pgrep -fa 'genesis_serving_receiver.py' || true; "
        "ss -ltnp 2>/dev/null | egrep '5015|5016|8443|18789|18790' || true"
    )
    for alias in VPS_ALIASES:
        result = ssh_command(alias, command, timeout_seconds=15)
        records[alias] = {
            "reachable": result["returncode"] == 0 and not result["timed_out"],
            "command": result,
        }
    return {
        "skipped": False,
        "hosts": records,
        "all_required_vps_reachable": all(record["reachable"] for record in records.values()),
    }


def source_commit(repo_root: Path) -> str:
    result = run_command(["git", "rev-parse", "HEAD"], timeout_seconds=5)
    if result["returncode"] != 0:
        return "unknown"
    return result["stdout"].strip()


def build_evidence(repo_root: Path, *, include_ssh: bool) -> dict[str, Any]:
    status = status_token_checks(repo_root)
    guards = guard_checks(repo_root)
    rehearsal = rehearsal_check(repo_root)
    vps = vps_checks(include_ssh=include_ssh)
    receivers = serving_receiver_checks()
    validators = validator_endpoint_checks()
    vps_ready = vps.get("all_required_vps_reachable") is True
    repo_ready = status["passed"] and guards["passed"] and rehearsal["passed"]
    quorum_ready = validators["quorum_reachable"]
    ready_for_1575h = bool(repo_ready and vps_ready and receivers["peer_set_minimum_plausible"] and quorum_ready)
    if ready_for_1575h:
        recommendation = "operator_may_consider_sensitive_1575h_go_after_final_human_review"
    elif not quorum_ready:
        recommendation = "blocked_start_or_verify_live_validator_quorum_before_1575h"
    else:
        recommendation = "blocked_resolve_failed_preflight_checks_before_1575h"
    return {
        "schema_version": SCHEMA_VERSION,
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_commit": source_commit(repo_root),
        "activation_boundary": {
            "read_only_preflight": True,
            "started_validator_processes": False,
            "deleted_validator_databases": False,
            "sent_epoch_checkpoint": False,
            "executed_epoch_0_to_1_transition": False,
            "minted_ecu": False,
            "settled_ilc": False,
            "wrote_wallets": False,
        },
        "status_token_check": status,
        "guard_check": guards,
        "rehearsal_check": rehearsal,
        "vps_check": vps,
        "serving_receiver_check": receivers,
        "validator_quorum_check": validators,
        "ready_for_1575h": ready_for_1575h,
        "recommendation": recommendation,
        "non_claims": {
            "no_epoch_transition": True,
            "no_epoch_checkpoint_sent": True,
            "no_process_start": True,
            "no_db_wipe": True,
            "no_public_mirror_push": True,
            "no_public_p2p_activation": True,
        },
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("out/block6_1575h_live_quorum_preflight/evidence_records.json"),
    )
    parser.add_argument("--no-ssh", action="store_true", help="Skip SSH-based VPS checks")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    repo_root = args.repo_root.resolve()
    evidence = build_evidence(repo_root, include_ssh=not args.no_ssh)
    output = args.output if args.output.is_absolute() else repo_root / args.output
    atomic_write_json(output, evidence)
    print(f"phase_1575h_live_quorum_preflight_written:{output}")
    print(f"ready_for_1575h={str(evidence['ready_for_1575h']).lower()}")
    print(f"recommendation={evidence['recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
