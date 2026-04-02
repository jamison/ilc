#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]

PUBLICATION_PENDING_ITEMS = [
    "select_candidate_bundle_archive",
    "tag_repo_head_and_publish_release",
    "publish_release_notes_and_claim_package",
]

POST_RC_DEFERRED_SCOPE = [
    {
        "item": "mutual_tls_rollout",
        "status": "deferred_post_rc",
        "reason": "server_tls_plus_ilc_signature_is_the_current_rc_boundary",
    },
    {
        "item": "dynamic_peer_discovery",
        "status": "deferred_post_rc",
        "reason": "curated_bootstrap_inventory_is_the_current_rc_boundary",
    },
    {
        "item": "hostile_internet_admission",
        "status": "deferred_post_rc",
        "reason": "current_rc_scope_is_private_testbed_and_operator_controlled",
    },
    {
        "item": "inbound_http_machine_payment",
        "status": "deferred_post_rc",
        "reason": "launch_critical_path_keeps_inbound_payment_out_of_scope",
    },
    {
        "item": "harness_specific_packaging",
        "status": "deferred_post_rc",
        "reason": "rc_surface_must_remain_harness_agnostic",
    },
]


class ReadinessDeltaError(RuntimeError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def render_readiness_delta(*, candidate_manifest_path: Path) -> dict[str, Any]:
    candidate = _load_json(candidate_manifest_path)
    closure_manifest_path = Path(str(candidate["closure_manifest_path"]))
    release_manifest_path = Path(str(candidate["release_manifest_path"]))
    closure_manifest = _load_json(closure_manifest_path)
    release_manifest = _load_json(release_manifest_path)
    evidence_manifest_path = Path(str(closure_manifest["evidence_manifest_path"]))
    evidence_manifest = _load_json(evidence_manifest_path)
    bundle_manifest_path = Path(str(release_manifest["bundle_manifest_path"]))
    bundle_manifest = _load_json(bundle_manifest_path)
    proof_manifest_path = Path(str(release_manifest["bundle_install_proof_manifest_path"]))
    proof_manifest = _load_json(proof_manifest_path)
    economic_proof_manifest_path = None
    economic_proof_manifest = None
    economic_proof_pass = False
    economic_negative_path_pass = False
    economic_replay_pass = False
    economic_proof_path_value = release_manifest.get("economic_proof_manifest_path")
    if economic_proof_path_value:
        candidate_economic_proof_manifest = Path(str(economic_proof_path_value))
        if candidate_economic_proof_manifest.is_file():
            economic_proof_manifest_path = candidate_economic_proof_manifest
            economic_proof_manifest = _load_json(candidate_economic_proof_manifest)
            comparison = economic_proof_manifest.get("comparison", {})
            if isinstance(comparison, dict) and comparison and all(comparison.values()):
                runtime_store = (economic_proof_manifest.get("invariant_summary") or {}).get("runtime_store", {})
                economic_negative_path_pass = economic_proof_manifest.get("negative_path_verdict") == "pass"
                economic_replay_pass = (
                    economic_proof_manifest.get("replay_verdict") == "pass"
                    and economic_proof_manifest.get("replay_settlement_status") == "idempotent_replay"
                )
                economic_proof_pass = (
                    runtime_store.get("store_kind") == "lmdb_public_runtime_v0.1"
                    and economic_negative_path_pass
                    and economic_replay_pass
                )
    economic_manifest_path = None
    economic_manifest = None
    economic_summary: dict[str, Any] | None = None
    economic_claim_summary: dict[str, Any] | None = None
    economic_path_value = candidate.get("economic_manifest_path")
    if economic_path_value:
        candidate_economic_manifest = Path(str(economic_path_value))
        if candidate_economic_manifest.is_file():
            economic_manifest_path = candidate_economic_manifest
            economic_manifest = _load_json(candidate_economic_manifest)
            raw_summary = economic_manifest.get("summary")
            if isinstance(raw_summary, dict):
                economic_summary = raw_summary
    if economic_manifest is not None:
        settlement_manifest = economic_manifest.get("settlement_manifest", {})
        wallet_manifest = economic_manifest.get("wallet_manifest", {})
        invariant_summary = economic_proof_manifest.get("invariant_summary", {}) if isinstance(economic_proof_manifest, dict) else {}
        runtime_store = invariant_summary.get("runtime_store", {}) if isinstance(invariant_summary, dict) else {}
        economic_claim_summary = {
            "task_id": (economic_summary or {}).get("task_id"),
            "reward_total": (economic_summary or {}).get("reward_total"),
            "wallet_count": (economic_summary or {}).get("wallet_count"),
            "rewarded_wallet_count": invariant_summary.get("rewarded_wallet_count") if isinstance(invariant_summary, dict) else None,
            "epoch_record_count": invariant_summary.get("epoch_record_count") if isinstance(invariant_summary, dict) else None,
            "settlement_status": settlement_manifest.get("settlement_status") if isinstance(settlement_manifest, dict) else None,
            "latest_epoch_id": wallet_manifest.get("latest_epoch_id") if isinstance(wallet_manifest, dict) else None,
            "runtime_store_kind": runtime_store.get("store_kind") if isinstance(runtime_store, dict) else None,
            "negative_path_verdict": economic_proof_manifest.get("negative_path_verdict") if isinstance(economic_proof_manifest, dict) else None,
            "replay_verdict": economic_proof_manifest.get("replay_verdict") if isinstance(economic_proof_manifest, dict) else None,
            "replay_settlement_status": economic_proof_manifest.get("replay_settlement_status") if isinstance(economic_proof_manifest, dict) else None,
        }
    scenario_summary = evidence_manifest.get("scenario_summary", {})
    scenario_replay_summary = evidence_manifest.get("scenario_replay_summary", {})
    closure_rows = evidence_manifest.get("closure_rows", {})
    unsatisfied_rows = sorted(
        key for key, value in closure_rows.items() if value != "satisfied_for_testbed"
    )
    failed_bundle_hosts = sorted(
        item.get("host", "unknown")
        for item in proof_manifest.get("results", [])
        if item.get("status") != "ok"
    )

    closure_pass = "rc0_1_substrate_verdict=pass" in str(closure_manifest.get("verdict_stdout", ""))
    release_pass = "rc0_1_release_verdict=pass" in str(release_manifest.get("release_verdict_stdout", ""))
    scenario_pass = scenario_summary.get("panel_verdict_token") == "panel_quorum_passed"
    replay_pass = (
        scenario_replay_summary.get("panel_result_matches") is True
        and scenario_replay_summary.get("ecu_claims_match") is True
    )
    bundle_proof_pass = not failed_bundle_hosts

    candidate_ready = all(
        [
            closure_pass,
            release_pass,
            scenario_pass,
            replay_pass,
            bundle_proof_pass,
            economic_proof_pass,
            not unsatisfied_rows,
        ]
    )

    return {
        "version": "rc0_1_readiness_delta_v0.1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "candidate_manifest_path": str(candidate_manifest_path),
        "closure_manifest_path": str(closure_manifest_path),
        "release_manifest_path": str(release_manifest_path),
        "evidence_manifest_path": str(evidence_manifest_path),
        "economic_manifest_path": str(economic_manifest_path) if economic_manifest_path is not None else None,
        "bundle_manifest_path": str(bundle_manifest_path),
        "bundle_install_proof_manifest_path": str(proof_manifest_path),
        "economic_proof_manifest_path": str(economic_proof_manifest_path) if economic_proof_manifest_path is not None else None,
        "repo_head": evidence_manifest.get("repo_head"),
        "release_candidate_ready": candidate_ready,
        "closure_pass": closure_pass,
        "release_pass": release_pass,
        "scenario_pass": scenario_pass,
        "scenario_replay_pass": replay_pass,
        "bundle_install_proof_pass": bundle_proof_pass,
        "economic_proof_pass": economic_proof_pass,
        "economic_state_present": economic_manifest is not None,
        "economic_summary": economic_summary,
        "economic_claim_summary": economic_claim_summary,
        "economic_negative_path_pass": economic_negative_path_pass,
        "economic_replay_pass": economic_replay_pass,
        "unsatisfied_closure_rows": unsatisfied_rows,
        "failed_bundle_hosts": failed_bundle_hosts,
        "publication_pending_items": PUBLICATION_PENDING_ITEMS,
        "post_rc_deferred_scope": POST_RC_DEFERRED_SCOPE,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render the current RC0.1 candidate readiness delta over the latest release-candidate artifacts.")
    parser.add_argument("--candidate-manifest", required=True)
    parser.add_argument("--output-path")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        payload = render_readiness_delta(candidate_manifest_path=Path(args.candidate_manifest))
    except ReadinessDeltaError as exc:
        print(json.dumps({"marker": "rc0_1_readiness_delta_failed", "detail": str(exc)}, sort_keys=True, separators=(",", ":")))
        return 1
    if args.output_path:
        Path(args.output_path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"marker": "rc0_1_readiness_delta_ok", "manifest": payload}, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
