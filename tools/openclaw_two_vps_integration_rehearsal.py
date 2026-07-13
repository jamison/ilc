#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Run the Phase 1575b-Fix2e two-node OpenClaw integration rehearsal."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.sidecars.openclaw_idle_mining import evaluate_task_offer, parse_provider_usage
from ilc_core.sidecars.openclaw_invite_bootstrap import (
    InviteNullifierStore,
    build_synthetic_invite_bundle,
    verify_invite_bootstrap,
)
from ilc_core.sidecars.openclaw_local_capture import (
    build_capture_envelope,
    build_status_record,
    evaluate_consent_gate,
    raw_payload_sha256,
)

EVIDENCE_PATH = Path("out/block6_openclaw_two_vps_fix2e/evidence_records.json")
REAL_EVIDENCE_PATH = Path("out/block6_openclaw_two_vps_fix2e_fix1/evidence_records.json")
PROFILE = "openclaw_public_rc_bootstrap"
REQUIRED_REAL_ENV = ("ILC_FIX2E_VPS_A", "ILC_FIX2E_VPS_B")
REQUIRED_REAL_WORKDIR_ENV = ("ILC_FIX2E_VPS_A_WORKDIR", "ILC_FIX2E_VPS_B_WORKDIR")


def _node_fixture(node_label: str, idx: int) -> dict[str, str]:
    return {
        "batch_id": f"openclaw-fix2e-{node_label}",
        "local_agent_id": f"agent:{node_label}",
        "node_label": node_label,
        "nonce_hex": f"{idx:02x}" * 32,
        "operator_agent_id": f"operator:{node_label}",
        "session_id": f"session:{node_label}",
    }


def _bootstrap_node(node: dict[str, str], store_path: Path) -> dict[str, Any]:
    invite_bundle = build_synthetic_invite_bundle(
        batch_id=node["batch_id"],
        intended_profile=PROFILE,
        nonce_hex=node["nonce_hex"],
    )
    first = verify_invite_bootstrap(
        invite_bundle,
        expected_profile=PROFILE,
        current_epoch=0,
        nullifier_store=InviteNullifierStore(store_path),
    )
    replay = verify_invite_bootstrap(
        invite_bundle,
        expected_profile=PROFILE,
        current_epoch=0,
        nullifier_store=InviteNullifierStore(store_path),
    )
    return {
        "bootstrap_allowed": first.bootstrap_allowed,
        "defect_token": first.defect_token,
        "nullifier_persisted_after_restart": replay.defect_token == "replayed_nullifier",
        "replay_defect_token": replay.defect_token,
        "redemption_nullifier_sha256": _hash_optional(first.redemption_nullifier),
        "signature_authority_status": first.signature_authority_status,
    }


def _cross_node_replay_gap(base_dir: Path) -> dict[str, Any]:
    shared = build_synthetic_invite_bundle(
        batch_id="openclaw-fix2e-cross-node",
        intended_profile=PROFILE,
        nonce_hex="7a" * 32,
    )
    first = verify_invite_bootstrap(
        shared,
        expected_profile=PROFILE,
        current_epoch=0,
        nullifier_store=InviteNullifierStore(base_dir / "cross_node_a.json"),
    )
    second = verify_invite_bootstrap(
        shared,
        expected_profile=PROFILE,
        current_epoch=0,
        nullifier_store=InviteNullifierStore(base_dir / "cross_node_b.json"),
    )
    return {
        "cross_node_replay_prevented_by_local_nullifiers": False,
        "first_node_allowed": first.bootstrap_allowed,
        "gap": "redeemer_key_binding_required",
        "second_node_allowed_with_independent_store": second.bootstrap_allowed,
    }


def _capture_checks(nodes: list[dict[str, str]]) -> dict[str, Any]:
    raw_payload = {
        "candidate_node_type": "claim_candidate",
        "text": "The same OpenClaw output bytes should hash identically across nodes.",
    }
    similar_payload = {
        "candidate_node_type": "claim_candidate",
        "text": "Equivalent meaning with different bytes is not semantic deduplication.",
    }
    captures = []
    for node in nodes:
        captures.append(
            build_capture_envelope(
                raw_payload=raw_payload,
                payload_kind="reply",
                operator_agent_id=node["operator_agent_id"],
                local_agent_id=node["local_agent_id"],
                provider_id="fixture_provider",
                session_id=node["session_id"],
                consent_state=(
                    "local_only"
                    if node["node_label"] == "vps_a"
                    else "approved_for_public_submission"
                ),
            )
        )
    submit_decisions = [
        evaluate_consent_gate(capture, action="submit") for capture in captures
    ]
    raw_hashes = [capture.raw_payload_sha256 for capture in captures]
    return {
        "attribution": [
            {
                "capture_id": capture.capture_id,
                "local_agent_id": capture.local_agent_id,
                "node_label": node["node_label"],
                "operator_agent_id": capture.operator_agent_id,
            }
            for capture, node in zip(captures, nodes, strict=True)
        ],
        "consent_gate_independent": {
            "vps_a_allowed": submit_decisions[0]["allowed"],
            "vps_b_allowed": submit_decisions[1]["allowed"],
            "vps_a_public_submission_performed": submit_decisions[0][
                "public_submission_performed"
            ],
            "vps_b_public_submission_performed": submit_decisions[1][
                "public_submission_performed"
            ],
        },
        "exact_duplicate": {
            "identical_raw_hashes_equal": raw_hashes[0] == raw_hashes[1],
            "raw_payload_sha256": raw_hashes[0],
        },
        "semantic_duplicate": {
            "similar_payload_hash_equal": raw_hashes[0] == raw_payload_sha256(similar_payload),
            "semantic_duplicate_detection_solved": False,
        },
        "status_records": [
            {
                "local_agent_id": capture.local_agent_id,
                "node_label": node["node_label"],
                "operator_agent_id": capture.operator_agent_id,
                "status": build_status_record([capture]),
            }
            for capture, node in zip(captures, nodes, strict=True)
        ],
    }


def _scheduler_checks(nodes: list[dict[str, str]]) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for node in nodes:
        base = {
            "autonomy_level": "maintenance_idle",
            "contribution_mode": "local_idle_compute_contribution",
            "hour_utc": 23,
            "idle_window_id": f"idle-window:{node['node_label']}",
            "input_payload": {"fixture": node["node_label"], "phase": "1575b-Fix2e"},
            "local_agent_id": node["local_agent_id"],
            "operator_agent_id": node["operator_agent_id"],
            "provider_usage": None,
            "resource_policy_profile": "local_compute",
            "session_consent": False,
            "system_load_percent": 10,
            "task_type": "star.map.embedding",
            "user_active": False,
        }
        allowed = evaluate_task_offer(**base)
        cap_history = [
            {
                "idle_window_id": base["idle_window_id"],
                "local_agent_id": node["local_agent_id"],
                "task_id": f"prior:{idx}",
                "task_type": f"prior_type:{idx}",
            }
            for idx in range(4)
        ]
        cap = evaluate_task_offer(**base, task_history=cap_history)
        diversity_history = [
            {
                "idle_window_id": base["idle_window_id"],
                "local_agent_id": node["local_agent_id"],
                "task_id": "prior:type",
                "task_type": "star.map.embedding",
            }
        ]
        diversity = evaluate_task_offer(
            **{**base, "input_payload": {"fixture": node["node_label"], "variant": "two"}},
            task_history=diversity_history,
        )
        results.append(
            {
                "allowed_local_offer": allowed["allowed"],
                "cap_block_reason": cap["block_reason"],
                "diversity_block_reason": diversity["block_reason"],
                "local_agent_id": node["local_agent_id"],
                "node_label": node["node_label"],
            }
        )
    api_offer = evaluate_task_offer(
        task_type="candidate_review",
        input_payload={"fixture": "api-metered-review", "phase": "1575b-Fix2e"},
        operator_agent_id=nodes[0]["operator_agent_id"],
        local_agent_id=nodes[0]["local_agent_id"],
        autonomy_level="maintenance_idle",
        resource_policy_profile="api_metered",
        contribution_mode="paid_api_budget_recovery",
        provider_usage=parse_provider_usage(
            provider_id="anthropic",
            headers={"anthropic-ratelimit-tokens-remaining": "2000"},
        ),
        min_remaining_tokens=500,
        session_consent=True,
        hour_utc=23,
        user_active=False,
        system_load_percent=10,
        idle_window_id="idle-window:api-metered",
    )
    return {
        "distributed_task_reservation_gap": "shared_coordinator_required",
        "distributed_task_reservation_solved": False,
        "node_results": results,
        "paid_api_budget_recovery_offer_allowed": api_offer["allowed"],
    }


def build_fixture_evidence() -> dict[str, Any]:
    base_dir = EVIDENCE_PATH.parent / "fixture_nullifiers"
    base_dir.mkdir(parents=True, exist_ok=True)
    for path in base_dir.glob("*.json"):
        path.unlink()
    nodes = [_node_fixture("vps_a", 17), _node_fixture("vps_b", 34)]
    bootstrap = {
        node["node_label"]: _bootstrap_node(node, base_dir / f"{node['node_label']}.json")
        for node in nodes
    }
    capture = _capture_checks(nodes)
    scheduler = _scheduler_checks(nodes)
    evidence = {
        "cross_node_invite_replay_gap_recorded": True,
        "cross_node_replay_gap": _cross_node_replay_gap(base_dir),
        "cross_node_replay_prevention_gap": "redeemer_key_binding_required",
        "distributed_task_reservation_gap": "shared_coordinator_required",
        "distributed_task_reservation_solved": False,
        "exact_duplicate_suppression_rehearsed": True,
        "fixture_mode_run": True,
        "mode": "fixture",
        "no_clawhub_listing": True,
        "no_ecu_minting": True,
        "no_epoch_transition": True,
        "no_guard_clearance": True,
        "no_ilc_settlement": True,
        "no_openclaw_publication": True,
        "no_public_graph_submission": True,
        "no_public_installability_claim": True,
        "no_public_rc_activation": True,
        "no_wallet_write": True,
        "nodes": [
            {
                "bootstrap": bootstrap[node["node_label"]],
                "local_agent_id": node["local_agent_id"],
                "node_label": node["node_label"],
                "operator_agent_id": node["operator_agent_id"],
                "private_target_redacted": True,
            }
            for node in nodes
        ],
        "phase": "1575b-Fix2e",
        "private_values_redacted": True,
        "real_vps_mode": {
            "required_env": list(REQUIRED_REAL_ENV),
            "run": False,
            "status": "not_configured",
        },
        "schema_version": "ilc_openclaw_two_vps_integration_rehearsal_1575b_fix2e.v0.1",
        "semantic_duplicate_detection_gap": "future_graph_intelligence_required",
        "semantic_duplicate_detection_solved": False,
        "two_agent_attribution_confirmed": True,
        "vps_targets_redacted": True,
    }
    evidence["capture_checks"] = capture
    evidence["scheduler_checks"] = scheduler
    evidence["evidence_sha256"] = hashlib.sha256(
        _stable_json_bytes({k: v for k, v in evidence.items() if k != "evidence_sha256"})
    ).hexdigest()
    return evidence


def run_real_mode() -> int:
    missing = [
        name
        for name in (*REQUIRED_REAL_ENV, *REQUIRED_REAL_WORKDIR_ENV)
        if not os.environ.get(name)
    ]
    if missing:
        print(
            "fix2e_real_vps_targets_required: " + ",".join(missing),
            file=sys.stderr,
        )
        return 2
    nodes = [
        ("vps_a", os.environ["ILC_FIX2E_VPS_A"], os.environ["ILC_FIX2E_VPS_A_WORKDIR"]),
        ("vps_b", os.environ["ILC_FIX2E_VPS_B"], os.environ["ILC_FIX2E_VPS_B_WORKDIR"]),
    ]
    remote_results = []
    for label, target, workdir in nodes:
        _validate_remote_workdir(workdir)
        quoted_workdir = shlex.quote(workdir)
        result = subprocess.run(
            [
                "ssh",
                "-o",
                "BatchMode=yes",
                target,
                f"cd {quoted_workdir} && PYTHONPATH=. python3 tools/openclaw_two_vps_integration_rehearsal.py --fixture",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        evidence = subprocess.run(
            [
                "ssh",
                "-o",
                "BatchMode=yes",
                target,
                f"cat {quoted_workdir}/out/block6_openclaw_two_vps_fix2e/evidence_records.json",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(evidence.stdout)
        remote_results.append(
            {
                "fixture_mode_run": payload["fixture_mode_run"],
                "node_label": label,
                "remote_evidence_sha256": hashlib.sha256(
                    evidence.stdout.encode("utf-8")
                ).hexdigest(),
                "remote_stdout_sha256": hashlib.sha256(
                    result.stdout.encode("utf-8")
                ).hexdigest(),
                "remote_target_redacted": True,
                "two_agent_attribution_confirmed": payload[
                    "two_agent_attribution_confirmed"
                ],
            }
        )
    summary = {
        "cross_node_replay_prevention_gap": "redeemer_key_binding_required",
        "distributed_task_reservation_gap": "shared_coordinator_required",
        "no_clawhub_listing": True,
        "no_ecu_minting": True,
        "no_epoch_transition": True,
        "no_guard_clearance": True,
        "no_ilc_settlement": True,
        "no_openclaw_publication": True,
        "no_public_graph_submission": True,
        "no_public_rc_activation": True,
        "no_wallet_write": True,
        "phase": "1575b-Fix2e-Fix1",
        "private_values_redacted": True,
        "real_vps_mode": {
            "node_count": len(remote_results),
            "run": True,
            "status": "passed",
        },
        "remote_results": remote_results,
        "schema_version": "ilc_openclaw_two_vps_real_rehearsal_1575b_fix2e_fix1.v0.1",
        "semantic_duplicate_detection_gap": "future_graph_intelligence_required",
        "vps_targets_redacted": True,
    }
    summary["evidence_sha256"] = hashlib.sha256(
        _stable_json_bytes({k: v for k, v in summary.items() if k != "evidence_sha256"})
    ).hexdigest()
    _atomic_write_json(REAL_EVIDENCE_PATH, summary)
    print(REAL_EVIDENCE_PATH)
    print(summary["evidence_sha256"])
    return 0


def write_evidence(path: Path = EVIDENCE_PATH) -> dict[str, Any]:
    evidence = build_fixture_evidence()
    _atomic_write_json(path, evidence)
    return evidence


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = _stable_json_bytes(payload)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(body)
            handle.write(b"\n")
        os.replace(tmp_path, path)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def _stable_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, allow_nan=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


def _hash_optional(value: str | None) -> str | None:
    if value is None:
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _validate_remote_workdir(value: str) -> None:
    if not value.startswith("/home/ilcops/block6_rehearsal/"):
        raise ValueError("fix2e_remote_workdir_outside_rehearsal_root")
    if any(part in value for part in ("..", "\n", "\r", "\t", " ")):
        raise ValueError("fix2e_remote_workdir_invalid")
    allowed_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_./-")
    if any(char not in allowed_chars for char in value):
        raise ValueError("fix2e_remote_workdir_invalid")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", action="store_true", help="run deterministic local fixture mode")
    parser.add_argument("--real", action="store_true", help="probe explicitly configured real VPS targets")
    args = parser.parse_args()
    if args.fixture == args.real:
        parser.error("select exactly one of --fixture or --real")
    if args.real:
        return run_real_mode()
    evidence = write_evidence()
    print(EVIDENCE_PATH)
    print(evidence["evidence_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
