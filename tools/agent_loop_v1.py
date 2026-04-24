#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
import time
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.consensus.diversity_floor_runtime import compute_max_cluster_share
from ilc_core.crypto.cbor_canonical import cbor_dumps_canonical
from ilc_core.consensus.popperian_gate_runtime import (
    PopperianGateValidationError,
    evaluate_decomposition_admissibility,
)
from ilc_core.economics.epoch_ledger import SimpleEpochLedger
from ilc_core.economics.outcome import OutcomeLogger, TaskOutcome
from ilc_core.economics.passive_ecu_attribution_runtime import compute_passive_ecu
from ilc_core.economics.reward import simple_claim_reward
from ilc_core.genesis.work_task import EpistemicWorkTask, ep_task_to_json
from ilc_core.identity.agent_id_runtime import derive_agent_id
from ilc_core.network.d2d.http_gossip_transport_runtime import (
    HttpGossipTransportRuntime,
    TransportRuntimeConfig,
    TransportRuntimeError,
)
from ilc_core.node.node_startup_runtime import load_static_peer_config

AGENT_LOOP_V1_RUNTIME_VERSION = "agent_loop_v1_runtime_575.v0.1"
DEFAULT_CHANNEL = "ilc.agent-loop.v1"
DEFAULT_REPRODUCIBILITY_THRESHOLD = 0.85
PANEL_SIZE = 8
QUORUM_THRESHOLD = 5
DISTINCT_CLUSTER_FLOOR = 3


@dataclass(frozen=True)
class AgentProfile:
    slot: int
    seed_hex: str
    cluster_id: str
    node_name: str
    variant: str
    agent_id: str


@dataclass(frozen=True)
class AgentSubmission:
    task_id: str
    epoch: int
    channel: str
    profile: AgentProfile
    output_hash: str
    output_payload: dict[str, Any]
    ep_task: dict[str, Any]
    gossip_type: str
    send_statuses: list[dict[str, Any]]


@dataclass(frozen=True)
class PanelVote:
    reviewer_agent_id: str
    cluster_id: str
    node_name: str
    variant: str
    output_hash: str
    matches_majority: bool
    passed_gate: bool
    passed: bool


@dataclass(frozen=True)
class PanelResult:
    task_id: str
    epoch: int
    yes_votes: int
    no_votes: int
    quorum_threshold: int
    quorum_reached: bool
    distinct_clusters: int
    distinct_cluster_floor: int
    diversity_floor_met: bool
    max_cluster_share: float
    agreement_score: float
    reproducibility_threshold: float
    majority_output_hash: str | None
    direct_author_agent_id: str | None
    verdict_token: str
    passed: bool
    confidence_score: float
    votes: list[PanelVote]


@dataclass(frozen=True)
class EcuClaim:
    claim_id: str
    task_id: str
    epoch: int
    agent_id: str
    claim_kind: str
    amount: float
    basis: dict[str, Any]


class AgentLoopRuntimeError(ValueError):
    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


def _stable_json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256_hex(payload: Any) -> str:
    return hashlib.sha256(_stable_json_bytes(payload)).hexdigest()


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")), flush=True)


def _require_dict(name: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AgentLoopRuntimeError(f"{name}_must_be_object", f"{name} must be an object")
    return value


def _require_string(name: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AgentLoopRuntimeError(f"{name}_must_be_non_empty_string", f"{name} must be a non-empty string")
    return value.strip()


def _require_int(name: str, value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise AgentLoopRuntimeError(f"{name}_must_be_integer", f"{name} must be an integer")
    return value


def _require_float(name: str, value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise AgentLoopRuntimeError(f"{name}_must_be_numeric", f"{name} must be numeric")
    return float(value)


def _require_list_of_strings(name: str, value: Any) -> list[str]:
    if not isinstance(value, list) or not value:
        raise AgentLoopRuntimeError(f"{name}_must_be_non_empty_list", f"{name} must be a non-empty list")
    result: list[str] = []
    for item in value:
        result.append(_require_string(name, item))
    return result


def _normalize_channel(value: str) -> str:
    raw = _require_string("channel", value)
    if raw.startswith("cid:") or raw.startswith("rand:"):
        return raw
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]
    return f"cid:{digest}"


def _load_task_spec(
    *,
    task_spec_path: str | None,
    task_json: str | None,
    task_json_base64: str | None,
) -> dict[str, Any]:
    provided = [task_spec_path is not None, task_json is not None, task_json_base64 is not None]
    if sum(1 for item in provided if item) != 1:
        raise AgentLoopRuntimeError(
            "task_spec_source_invalid",
            "exactly one of task_spec_path, task_json, or task_json_base64 must be provided",
        )
    if task_spec_path is not None:
        raw = json.loads(Path(task_spec_path).read_text(encoding="utf-8"))
    elif task_json is not None:
        raw = json.loads(task_json)
    else:
        # task_json_base64 is the only remaining option (enforced by the mutex check above)
        raw = json.loads(base64.b64decode(task_json_base64).decode("utf-8"))  # type: ignore[arg-type]
    task = _require_dict("task_spec", raw)
    task.setdefault("channel", DEFAULT_CHANNEL)
    task.setdefault("claim_form", "falsifiable_positive")
    task.setdefault("has_falsifiable_test", True)
    task.setdefault("is_inadmissible_counterexample", False)
    task.setdefault("reproducibility_threshold", DEFAULT_REPRODUCIBILITY_THRESHOLD)
    task.setdefault("difficulty_factor", 1.0)
    task.setdefault("ecu_estimate", 1.0)
    task.setdefault("verification_method", "replayable-simulation")
    task.setdefault("timestamp_created", 1_700_000_000)
    task.setdefault("epoch", 0)
    task.setdefault("canonical_output", "deterministic-majority-output-v1")
    task.setdefault("divergent_output_prefix", "deterministic-divergent-output-v1")
    _require_string("task_id", task.get("task_id"))
    _require_string("task_class", task.get("task_class"))
    _require_list_of_strings("region_scope", task.get("region_scope"))
    _require_string("verification_method", task.get("verification_method"))
    task["channel"] = _normalize_channel(str(task.get("channel")))
    _require_string("claim_form", task.get("claim_form"))
    _require_float("difficulty_factor", task.get("difficulty_factor"))
    _require_float("ecu_estimate", task.get("ecu_estimate"))
    _require_int("timestamp_created", task.get("timestamp_created"))
    _require_int("epoch", task.get("epoch"))
    if not isinstance(task.get("has_falsifiable_test"), bool):
        raise AgentLoopRuntimeError(
            "has_falsifiable_test_must_be_bool",
            "has_falsifiable_test must be a bool",
        )
    if not isinstance(task.get("is_inadmissible_counterexample"), bool):
        raise AgentLoopRuntimeError(
            "is_inadmissible_counterexample_must_be_bool",
            "is_inadmissible_counterexample must be a bool",
        )
    return task


def _profile(slot: int, seed_hex: str, cluster_id: str, node_name: str, variant: str) -> AgentProfile:
    try:
        seed_bytes = bytes.fromhex(seed_hex)
    except ValueError as exc:
        raise AgentLoopRuntimeError("agent_seed_hex_invalid", "seed_hex must be valid hex") from exc
    if not seed_bytes:
        raise AgentLoopRuntimeError("agent_seed_hex_invalid", "seed_hex must decode to bytes")
    return AgentProfile(
        slot=slot,
        seed_hex=seed_hex,
        cluster_id=_require_string("cluster_id", cluster_id),
        node_name=_require_string("node_name", node_name),
        variant=_require_string("variant", variant),
        agent_id=derive_agent_id(seed_bytes),
    )


def _output_payload(task: dict[str, Any], profile: AgentProfile) -> dict[str, Any]:
    solution = _require_string("canonical_output", task.get("canonical_output"))
    if profile.variant == "divergent":
        prefix = _require_string("divergent_output_prefix", task.get("divergent_output_prefix"))
        solution = f"{prefix}:{profile.slot}"
    payload = {
        "task_id": task["task_id"],
        "task_class": task["task_class"],
        "solution": solution,
        "claim_form": task["claim_form"],
        "verification_method": task["verification_method"],
        "difficulty_factor": task["difficulty_factor"],
    }
    return payload


def _build_ep_task(task: dict[str, Any], profile: AgentProfile, output_hash: str) -> dict[str, Any]:
    ep_task = EpistemicWorkTask(
        task_id=f"{task['task_id']}::{profile.agent_id[:16]}",
        task_class=task["task_class"],
        agent_id=profile.agent_id,
        region_scope=task["region_scope"],
        difficulty_factor=task["difficulty_factor"],
        input_data={
            "source_task_id": task["task_id"],
            "claim_form": task["claim_form"],
            "has_falsifiable_test": task["has_falsifiable_test"],
            "is_inadmissible_counterexample": task["is_inadmissible_counterexample"],
            "cluster_id": profile.cluster_id,
            "node_name": profile.node_name,
            "variant": profile.variant,
        },
        output_hash=output_hash,
        verification_method=task["verification_method"],
        ecu_estimate=task["ecu_estimate"],
        task_state="completed",
        timestamp_created=task["timestamp_created"],
    )
    return ep_task_to_json(ep_task)


def _transport_bundle(config_path: str | Path) -> tuple[TransportRuntimeConfig, list[str]]:
    config = load_static_peer_config(config_path)
    transport = config["transport"]
    return (
        TransportRuntimeConfig(
            transport_kind=str(transport["kind"]),
            bind_host=str(transport["bind_host"]),
            bind_port=int(transport["bind_port"]),
            tls_cert_path=str(transport["tls_cert_path"]),
            tls_key_path=str(transport["tls_key_path"]),
        ),
        list(config["peers"]),
    )


def _signature(payload: dict[str, Any]) -> str:
    return f"agent-loop-v1:{_sha256_hex(payload)[:24]}"


def _broadcast_submission(
    *,
    config_path: str | Path,
    artifact: dict[str, Any],
    gossip_type: str,
    channel: str,
    epoch: int,
) -> list[dict[str, Any]]:
    transport_config, peers = _transport_bundle(config_path)
    runtime = HttpGossipTransportRuntime(transport_config)
    # CDL-061 production traffic stays on canonical CBOR; JSON remains only a
    # lower-layer fallback path in the transport runtime.
    payload = cbor_dumps_canonical(artifact)
    payload_sha256 = hashlib.sha256(payload).hexdigest()
    payload_bytes = len(payload)
    signature = _signature(artifact)
    statuses: list[dict[str, Any]] = []
    for endpoint in peers:
        started_at = time.perf_counter()
        try:
            status = runtime.send_gossip(
                endpoint,
                gossip_type,
                channel,
                epoch,
                signature,
                payload,
            )
        except TransportRuntimeError as exc:
            raise AgentLoopRuntimeError(
                "agent_loop_transport_request_failed",
                f"broadcast failed for {endpoint}: {exc.token}",
            ) from exc
        duration_ms = round((time.perf_counter() - started_at) * 1000.0, 6)
        if status != 202:
            raise AgentLoopRuntimeError(
                "agent_loop_unexpected_status_code",
                f"unexpected status {status} from {endpoint}",
            )
        statuses.append(
            {
                "endpoint": endpoint,
                "status_code": status,
                "duration_ms": duration_ms,
                "payload_bytes": payload_bytes,
                "payload_sha256": payload_sha256,
            }
        )
    return statuses


def run_agent_once(
    *,
    slot: int,
    seed_hex: str,
    cluster_id: str,
    node_name: str,
    node_config_path: str | Path,
    variant: str,
    task: dict[str, Any],
    broadcast: bool,
) -> dict[str, Any]:
    profile = _profile(slot, seed_hex, cluster_id, node_name, variant)
    output_payload = _output_payload(task, profile)
    output_hash = _sha256_hex(output_payload)
    ep_task = _build_ep_task(task, profile, output_hash)
    artifact = {
        "agent_loop_runtime_version": AGENT_LOOP_V1_RUNTIME_VERSION,
        "artifact_kind": "agent_submission",
        "task_id": task["task_id"],
        "epoch": task["epoch"],
        "channel": task["channel"],
        "profile": asdict(profile),
        "output_hash": output_hash,
        "output_payload": output_payload,
        "ep_task": ep_task,
    }
    send_statuses: list[dict[str, Any]] = []
    if broadcast:
        send_statuses = _broadcast_submission(
            config_path=node_config_path,
            artifact=artifact,
            gossip_type="agent_submission",
            channel=task["channel"],
            epoch=int(task["epoch"]),
        )
    submission = AgentSubmission(
        task_id=task["task_id"],
        epoch=int(task["epoch"]),
        channel=task["channel"],
        profile=profile,
        output_hash=output_hash,
        output_payload=output_payload,
        ep_task=ep_task,
        gossip_type="agent_submission",
        send_statuses=send_statuses,
    )
    return {
        "marker": "agent_loop_submission_ok",
        "runtime_version": AGENT_LOOP_V1_RUNTIME_VERSION,
        "submission": asdict(submission),
    }


def _load_submission_payloads(submission_dir: str | Path) -> list[dict[str, Any]]:
    root = Path(submission_dir)
    if not root.is_dir():
        raise AgentLoopRuntimeError("submission_dir_missing", f"submission_dir missing: {root}")
    payloads: list[dict[str, Any]] = []
    for path in sorted(root.glob("submission_*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        submission = _require_dict("submission_wrapper", payload).get("submission")
        payloads.append(_require_dict("submission", submission))
    if not payloads:
        raise AgentLoopRuntimeError("submission_dir_empty", f"no submission_*.json files in {root}")
    return payloads


def _build_outsider_submission(task: dict[str, Any], seed_hex: str, cluster_id: str, node_name: str) -> dict[str, Any]:
    profile = _profile(8, seed_hex, cluster_id, node_name, "outsider")
    output_payload = _output_payload(task, profile)
    output_hash = _sha256_hex(output_payload)
    return asdict(
        AgentSubmission(
            task_id=task["task_id"],
            epoch=int(task["epoch"]),
            channel=task["channel"],
            profile=profile,
            output_hash=output_hash,
            output_payload=output_payload,
            ep_task=_build_ep_task(task, profile, output_hash),
            gossip_type="agent_submission",
            send_statuses=[],
        )
    )


def _direct_author_tiebreak_digest(task: dict[str, Any], majority_hash: str, agent_id: str) -> str:
    material = f"{task['task_id']}|{task['epoch']}|{majority_hash}|{agent_id}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def evaluate_panel(
    *,
    task: dict[str, Any],
    submissions: list[dict[str, Any]],
    outsider_submission: dict[str, Any],
) -> dict[str, Any]:
    all_submissions = submissions + [outsider_submission]
    if len(all_submissions) != PANEL_SIZE:
        raise AgentLoopRuntimeError(
            "panel_size_mismatch",
            f"expected {PANEL_SIZE} total submissions including outsider, got {len(all_submissions)}",
        )
    output_counts = Counter(item["output_hash"] for item in all_submissions)
    if not output_counts:
        raise AgentLoopRuntimeError("panel_output_hash_missing", "no output hashes available")
    major = output_counts.most_common(2)
    if len(major) > 1 and major[0][1] == major[1][1]:
        majority_hash = None
        agreement_score = 0.0
        gate_ok = False
        verdict_token = "panel_majority_hash_tie"
    else:
        majority_hash = major[0][0]
        agreement_score = round(major[0][1] / PANEL_SIZE, 12)
        try:
            gate_ok = evaluate_decomposition_admissibility(
                claim_form=task["claim_form"],
                has_falsifiable_test=bool(task["has_falsifiable_test"]),
                is_inadmissible_counterexample=bool(task["is_inadmissible_counterexample"]),
                agreement_score=agreement_score,
                reproducibility_threshold=float(task["reproducibility_threshold"]),
            )
        except PopperianGateValidationError as exc:
            raise AgentLoopRuntimeError(exc.token, str(exc)) from exc
        verdict_token = "panel_reproducibility_failed"

    votes: list[PanelVote] = []
    for item in all_submissions:
        profile = _require_dict("profile", item.get("profile"))
        matches_majority = majority_hash is not None and item["output_hash"] == majority_hash
        passed = bool(gate_ok and matches_majority)
        votes.append(
            PanelVote(
                reviewer_agent_id=_require_string("agent_id", profile.get("agent_id")),
                cluster_id=_require_string("cluster_id", profile.get("cluster_id")),
                node_name=_require_string("node_name", profile.get("node_name")),
                variant=_require_string("variant", profile.get("variant")),
                output_hash=_require_string("output_hash", item.get("output_hash")),
                matches_majority=matches_majority,
                passed_gate=bool(gate_ok),
                passed=passed,
            )
        )

    yes_votes = sum(1 for vote in votes if vote.passed)
    no_votes = PANEL_SIZE - yes_votes
    distinct_clusters = len({vote.cluster_id for vote in votes})
    diversity_floor_met = distinct_clusters >= DISTINCT_CLUSTER_FLOOR
    max_cluster_slots = max(Counter(vote.cluster_id for vote in votes).values())
    max_cluster_share = compute_max_cluster_share(
        largest_cluster_slots=max_cluster_slots,
        total_panel_slots=PANEL_SIZE,
    )
    quorum_reached = yes_votes >= QUORUM_THRESHOLD
    direct_author_agent_id: str | None = None
    if majority_hash is not None:
        candidates = sorted(
            (
                _direct_author_tiebreak_digest(task, majority_hash, vote.reviewer_agent_id),
                vote.reviewer_agent_id,
            )
            for vote in votes
            if vote.matches_majority and vote.variant != "outsider"
        )
        if candidates:
            direct_author_agent_id = candidates[0][1]

    passed = bool(gate_ok and diversity_floor_met and quorum_reached and majority_hash is not None)
    if majority_hash is None:
        verdict_token = "panel_majority_hash_tie"
    elif not gate_ok:
        verdict_token = "panel_reproducibility_failed"
    elif not diversity_floor_met:
        verdict_token = "panel_diversity_floor_failed"
    elif not quorum_reached:
        verdict_token = "panel_quorum_failed"
    else:
        verdict_token = "panel_quorum_passed"

    panel_result = PanelResult(
        task_id=task["task_id"],
        epoch=int(task["epoch"]),
        yes_votes=yes_votes,
        no_votes=no_votes,
        quorum_threshold=QUORUM_THRESHOLD,
        quorum_reached=quorum_reached,
        distinct_clusters=distinct_clusters,
        distinct_cluster_floor=DISTINCT_CLUSTER_FLOOR,
        diversity_floor_met=diversity_floor_met,
        max_cluster_share=max_cluster_share,
        agreement_score=agreement_score,
        reproducibility_threshold=float(task["reproducibility_threshold"]),
        majority_output_hash=majority_hash,
        direct_author_agent_id=direct_author_agent_id,
        verdict_token=verdict_token,
        passed=passed,
        confidence_score=round(yes_votes / PANEL_SIZE, 12),
        votes=votes,
    )
    return {
        "marker": "agent_loop_panel_ok" if passed else "agent_loop_panel_failed",
        "runtime_version": AGENT_LOOP_V1_RUNTIME_VERSION,
        "panel_result": asdict(panel_result),
    }


def build_ecu_claim_batch(task: dict[str, Any], panel_payload: dict[str, Any]) -> dict[str, Any]:
    panel = _require_dict("panel_result", panel_payload.get("panel_result"))
    if not bool(panel.get("passed")):
        return {
            "marker": "agent_loop_claims_skipped",
            "runtime_version": AGENT_LOOP_V1_RUNTIME_VERSION,
            "claims": [],
            "ledger": {"tasks": 0, "ecu_spent": 0.0, "rewards_paid": 0.0, "clearing_price": 0.0},
            "outcome_summary": {"count": 0, "total_stake": 0.0, "total_reward": 0.0},
        }

    direct_author_agent_id = panel.get("direct_author_agent_id")
    if not isinstance(direct_author_agent_id, str) or not direct_author_agent_id:
        raise AgentLoopRuntimeError("direct_author_missing", "direct author missing from passing panel result")

    confidence_score = _require_float("confidence_score", panel.get("confidence_score"))
    agreement_score = _require_float("agreement_score", panel.get("agreement_score"))
    ecu_estimate = _require_float("ecu_estimate", task.get("ecu_estimate"))
    base_reward = round(
        simple_claim_reward(
            stake_spent=ecu_estimate,
            potential=confidence_score,
            success_rate=agreement_score,
        ),
        12,
    )
    passive_amount = compute_passive_ecu(
        base_reward,
        centrality_score=agreement_score,
        q_i=confidence_score,
    )

    claims: list[EcuClaim] = [
        EcuClaim(
            claim_id=f"ecu-claim::{task['task_id']}::{direct_author_agent_id[:16]}::direct",
            task_id=task["task_id"],
            epoch=int(task["epoch"]),
            agent_id=direct_author_agent_id,
            claim_kind="direct",
            amount=base_reward,
            basis={
                "base_reward": base_reward,
                "confidence_score": confidence_score,
                "agreement_score": agreement_score,
            },
        )
    ]

    votes = panel.get("votes")
    if not isinstance(votes, list):
        raise AgentLoopRuntimeError("panel_votes_missing", "panel votes missing")
    passive_recipients = sorted(
        vote["reviewer_agent_id"]
        for vote in votes
        if isinstance(vote, dict)
        and vote.get("passed") is True
        and vote.get("variant") != "outsider"
        and vote.get("reviewer_agent_id") != direct_author_agent_id
    )
    for agent_id in passive_recipients:
        claims.append(
            EcuClaim(
                claim_id=f"ecu-claim::{task['task_id']}::{agent_id[:16]}::passive",
                task_id=task["task_id"],
                epoch=int(task["epoch"]),
                agent_id=agent_id,
                claim_kind="passive",
                amount=passive_amount,
                basis={
                    "base_reward": base_reward,
                    "centrality_score": agreement_score,
                    "quality_score": confidence_score,
                },
            )
        )

    ledger = SimpleEpochLedger()
    total_reward = round(sum(claim.amount for claim in claims), 12)
    ledger.record_task(int(task["epoch"]), ecu_estimate, total_reward)

    outcomes = OutcomeLogger()
    outcomes.log(
        TaskOutcome(
            task_type="claim.submit",
            domain=str(task["task_class"]),
            stake_spent=ecu_estimate,
            reward_paid=total_reward,
            success=True,
        )
    )

    return {
        "marker": "agent_loop_claims_ok",
        "runtime_version": AGENT_LOOP_V1_RUNTIME_VERSION,
        "claims": [asdict(claim) for claim in claims],
        "ledger": {
            "tasks": ledger.get_epoch_stats(int(task["epoch"])).tasks,
            "ecu_spent": ledger.get_epoch_stats(int(task["epoch"])).ecu_spent,
            "rewards_paid": ledger.get_epoch_stats(int(task["epoch"])).rewards_paid,
            "clearing_price": ledger.clearing_price(int(task["epoch"])),
        },
        "outcome_summary": outcomes.summary(),
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _run_agent_command(args: argparse.Namespace) -> int:
    task = _load_task_spec(
        task_spec_path=args.task_spec,
        task_json=args.task_json,
        task_json_base64=args.task_json_base64,
    )
    payload = run_agent_once(
        slot=args.slot,
        seed_hex=args.seed_hex,
        cluster_id=args.cluster_id,
        node_name=args.node_name,
        node_config_path=args.node_config,
        variant=args.variant,
        task=task,
        broadcast=not args.no_broadcast,
    )
    if args.emit_dir:
        _write_json(Path(args.emit_dir) / f"submission_{args.slot}.json", payload)
    _emit(payload)
    return 0


def _run_panel_command(args: argparse.Namespace) -> int:
    task = _load_task_spec(
        task_spec_path=args.task_spec,
        task_json=args.task_json,
        task_json_base64=args.task_json_base64,
    )
    submissions = _load_submission_payloads(args.submission_dir)
    outsider_submission = _build_outsider_submission(
        task,
        args.outsider_seed_hex,
        args.outsider_cluster_id,
        args.outsider_node_name,
    )
    panel_payload = evaluate_panel(task=task, submissions=submissions, outsider_submission=outsider_submission)
    claim_payload = build_ecu_claim_batch(task, panel_payload)
    combined = {
        "marker": panel_payload["marker"],
        "runtime_version": AGENT_LOOP_V1_RUNTIME_VERSION,
        "panel_result": panel_payload["panel_result"],
        "ecu_claim_batch": {
            key: value for key, value in claim_payload.items() if key not in {"marker", "runtime_version"}
        },
        "outsider_submission": outsider_submission,
    }
    if args.emit_dir:
        emit_dir = Path(args.emit_dir)
        _write_json(emit_dir / "panel_result.json", combined)
        _write_json(emit_dir / "ecu_claims.json", claim_payload)
        _write_json(emit_dir / "outsider_submission.json", outsider_submission)
    _emit(combined)
    return 0


def _normalized_claim_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in payload.items()
        if key not in {"marker", "runtime_version"}
    }


def replay_panel(
    *,
    task: dict[str, Any],
    submissions: list[dict[str, Any]],
    outsider_seed_hex: str,
    outsider_cluster_id: str,
    outsider_node_name: str,
    panel_result_payload: dict[str, Any],
    ecu_claim_payload: dict[str, Any],
) -> dict[str, Any]:
    outsider_submission = _build_outsider_submission(
        task,
        outsider_seed_hex,
        outsider_cluster_id,
        outsider_node_name,
    )
    recomputed_panel = evaluate_panel(
        task=task,
        submissions=submissions,
        outsider_submission=outsider_submission,
    )
    recomputed_claims = build_ecu_claim_batch(task, recomputed_panel)

    expected_panel = _require_dict(
        "panel_result",
        panel_result_payload.get("panel_result", panel_result_payload),
    )
    panel_matches = expected_panel == recomputed_panel.get("panel_result")
    claims_matches = _normalized_claim_payload(ecu_claim_payload) == _normalized_claim_payload(recomputed_claims)
    if not panel_matches:
        raise AgentLoopRuntimeError(
            "agent_loop_panel_replay_mismatch",
            "recomputed panel result does not match saved panel artifact",
        )
    if not claims_matches:
        raise AgentLoopRuntimeError(
            "agent_loop_claim_replay_mismatch",
            "recomputed ECU claim batch does not match saved claim artifact",
        )
    return {
        "marker": "agent_loop_replay_ok",
        "runtime_version": AGENT_LOOP_V1_RUNTIME_VERSION,
        "panel_result_matches": panel_matches,
        "ecu_claims_match": claims_matches,
        "panel_verdict_token": recomputed_panel["panel_result"]["verdict_token"],
        "ecu_claim_count": len(recomputed_claims["claims"]),
        "reward_total": recomputed_claims["ledger"]["rewards_paid"],
    }


def _run_replay_command(args: argparse.Namespace) -> int:
    task = _load_task_spec(
        task_spec_path=args.task_spec,
        task_json=args.task_json,
        task_json_base64=args.task_json_base64,
    )
    submissions = _load_submission_payloads(args.submission_dir)
    panel_payload = _require_dict(
        "panel_payload",
        json.loads(Path(args.panel_result_file).read_text(encoding="utf-8")),
    )
    claims_payload = _require_dict(
        "ecu_claim_payload",
        json.loads(Path(args.ecu_claims_file).read_text(encoding="utf-8")),
    )
    result = replay_panel(
        task=task,
        submissions=submissions,
        outsider_seed_hex=args.outsider_seed_hex,
        outsider_cluster_id=args.outsider_cluster_id,
        outsider_node_name=args.outsider_node_name,
        panel_result_payload=panel_payload,
        ecu_claim_payload=claims_payload,
    )
    if args.emit_dir:
        _write_json(Path(args.emit_dir) / "panel_replay.json", result)
    _emit(result)
    return 0


def _run_broadcast_command(args: argparse.Namespace) -> int:
    artifact_path = Path(args.artifact_file)
    payload = _require_dict(
        "artifact_payload",
        json.loads(artifact_path.read_text(encoding="utf-8")),
    )
    task = _load_task_spec(
        task_spec_path=args.task_spec,
        task_json=args.task_json,
        task_json_base64=args.task_json_base64,
    )
    send_statuses = _broadcast_submission(
        config_path=args.node_config,
        artifact=payload,
        gossip_type=args.gossip_type,
        channel=task["channel"],
        epoch=int(task["epoch"]),
    )
    result = {
        "marker": "agent_loop_broadcast_ok",
        "runtime_version": AGENT_LOOP_V1_RUNTIME_VERSION,
        "artifact_file": str(artifact_path),
        "gossip_type": args.gossip_type,
        "send_statuses": send_statuses,
    }
    if args.emit_dir:
        _write_json(Path(args.emit_dir) / f"broadcast_{args.gossip_type}.json", result)
    _emit(result)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deterministic agent loop v1 helpers")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_task_source(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--task-spec")
        subparser.add_argument("--task-json")
        subparser.add_argument("--task-json-base64")

    run_agent = subparsers.add_parser("run-agent", help="Run one deterministic agent submission")
    run_agent.add_argument("--slot", type=int, required=True)
    run_agent.add_argument("--seed-hex", required=True)
    run_agent.add_argument("--cluster-id", required=True)
    run_agent.add_argument("--node-name", required=True)
    run_agent.add_argument("--node-config", required=True)
    run_agent.add_argument("--variant", default="canonical", choices=("canonical", "divergent", "outsider"))
    run_agent.add_argument("--emit-dir")
    run_agent.add_argument("--no-broadcast", action="store_true")
    add_task_source(run_agent)

    panel = subparsers.add_parser("evaluate-panel", help="Evaluate 7+1 panel results and build ECU claims")
    panel.add_argument("--submission-dir", required=True)
    panel.add_argument("--outsider-seed-hex", required=True)
    panel.add_argument("--outsider-cluster-id", required=True)
    panel.add_argument("--outsider-node-name", default="ilc-node-1")
    panel.add_argument("--emit-dir")
    add_task_source(panel)

    replay = subparsers.add_parser("replay-panel", help="Replay saved panel artifacts and verify deterministic agreement")
    replay.add_argument("--submission-dir", required=True)
    replay.add_argument("--panel-result-file", required=True)
    replay.add_argument("--ecu-claims-file", required=True)
    replay.add_argument("--outsider-seed-hex", required=True)
    replay.add_argument("--outsider-cluster-id", required=True)
    replay.add_argument("--outsider-node-name", default="ilc-node-1")
    replay.add_argument("--emit-dir")
    add_task_source(replay)

    broadcast = subparsers.add_parser("broadcast-artifact", help="Broadcast a JSON artifact over the live gossip path")
    broadcast.add_argument("--node-config", required=True)
    broadcast.add_argument("--artifact-file", required=True)
    broadcast.add_argument("--gossip-type", required=True)
    broadcast.add_argument("--emit-dir")
    add_task_source(broadcast)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "run-agent":
            return _run_agent_command(args)
        if args.command == "evaluate-panel":
            return _run_panel_command(args)
        if args.command == "replay-panel":
            return _run_replay_command(args)
        if args.command == "broadcast-artifact":
            return _run_broadcast_command(args)
        raise AgentLoopRuntimeError("agent_loop_command_unknown", f"unknown command: {args.command}")
    except AgentLoopRuntimeError as exc:
        _emit({
            "marker": "agent_loop_error",
            "runtime_version": AGENT_LOOP_V1_RUNTIME_VERSION,
            "token": exc.token,
            "detail": str(exc),
        })
        return 1
    except (json.JSONDecodeError, OSError) as exc:
        _emit({
            "marker": "agent_loop_error",
            "runtime_version": AGENT_LOOP_V1_RUNTIME_VERSION,
            "token": exc.__class__.__name__,
            "detail": str(exc),
        })
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
