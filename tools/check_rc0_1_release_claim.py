#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def check_release_claim(*, claim_manifest_path: Path, delta_manifest_path: Path) -> tuple[str, list[str]]:
    claim_manifest = _load_json(claim_manifest_path)
    delta_manifest = _load_json(delta_manifest_path)
    failures: list[str] = []

    for key in (
        "candidate_manifest_path",
        "closure_manifest_path",
        "release_manifest_path",
        "evidence_manifest_path",
        "bundle_manifest_path",
        "bundle_install_proof_manifest_path",
        "economic_proof_manifest_path",
        "release_notes_input_path",
    ):
        value = claim_manifest.get(key)
        if not value:
            failures.append(f"claim_field_missing:{key}")
            continue
        if not Path(str(value)).is_file():
            failures.append(f"claim_path_missing:{key}:{value}")

    for key in (
        "candidate_manifest_path",
        "closure_manifest_path",
        "release_manifest_path",
        "evidence_manifest_path",
        "bundle_manifest_path",
        "bundle_install_proof_manifest_path",
        "economic_proof_manifest_path",
    ):
        claim_value = claim_manifest.get(key)
        delta_value = delta_manifest.get(key)
        if claim_value and delta_value and str(claim_value) != str(delta_value):
            failures.append(f"claim_delta_path_mismatch:{key}")

    economic_claim_value = claim_manifest.get("economic_manifest_path")
    economic_delta_value = delta_manifest.get("economic_manifest_path")
    if economic_claim_value and economic_delta_value and str(economic_claim_value) != str(economic_delta_value):
        failures.append("claim_delta_path_mismatch:economic_manifest_path")
    if economic_claim_value and not Path(str(economic_claim_value)).is_file():
        failures.append(f"claim_path_missing:economic_manifest_path:{economic_claim_value}")
    economic_claim_summary = claim_manifest.get("economic_claim_summary")
    if not isinstance(economic_claim_summary, dict):
        failures.append("claim_field_missing:economic_claim_summary")
    else:
        for key in (
            "task_id",
            "reward_total",
            "wallet_count",
            "rewarded_wallet_count",
            "settlement_status",
            "runtime_store_kind",
            "negative_path_verdict",
            "replay_verdict",
            "replay_settlement_status",
        ):
            if economic_claim_summary.get(key) in (None, ""):
                failures.append(f"claim_economic_summary_missing:{key}")
        if economic_claim_summary.get("runtime_store_kind") != "lmdb_public_runtime_v0.1":
            failures.append("claim_economic_runtime_store_kind_invalid")
        if economic_claim_summary.get("settlement_status") not in {"applied", "idempotent_replay"}:
            failures.append("claim_economic_settlement_status_invalid")
        if economic_claim_summary.get("negative_path_verdict") != "pass":
            failures.append("claim_economic_negative_path_invalid")
        if economic_claim_summary.get("replay_verdict") != "pass":
            failures.append("claim_economic_replay_verdict_invalid")
        if economic_claim_summary.get("replay_settlement_status") != "idempotent_replay":
            failures.append("claim_economic_replay_settlement_status_invalid")
    delta_economic_claim_summary = delta_manifest.get("economic_claim_summary")
    if isinstance(economic_claim_summary, dict) and isinstance(delta_economic_claim_summary, dict):
        if economic_claim_summary != delta_economic_claim_summary:
            failures.append("claim_delta_path_mismatch:economic_claim_summary")

    if delta_manifest.get("release_candidate_ready") is not True:
        failures.append("release_candidate_not_ready")
    if delta_manifest.get("closure_pass") is not True:
        failures.append("closure_verdict_not_pass")
    if delta_manifest.get("release_pass") is not True:
        failures.append("release_verdict_not_pass")
    if delta_manifest.get("scenario_pass") is not True:
        failures.append("scenario_verdict_not_pass")
    if delta_manifest.get("scenario_replay_pass") is not True:
        failures.append("scenario_replay_not_pass")
    if delta_manifest.get("bundle_install_proof_pass") is not True:
        failures.append("bundle_install_proof_not_pass")
    if delta_manifest.get("economic_proof_pass") is not True:
        failures.append("economic_proof_not_pass")
    if delta_manifest.get("economic_negative_path_pass") is not True:
        failures.append("economic_negative_path_not_pass")
    if delta_manifest.get("economic_replay_pass") is not True:
        failures.append("economic_replay_not_pass")
    if delta_manifest.get("unsatisfied_closure_rows"):
        failures.append("unsatisfied_closure_rows_present")
    if not delta_manifest.get("publication_pending_items"):
        failures.append("publication_pending_items_missing")

    if failures:
        return "fail", failures
    return "pass", []


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check the final RC0.1 release-claim package over a successful release-candidate run.")
    parser.add_argument("--claim-manifest", required=True)
    parser.add_argument("--delta-manifest", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    verdict, failures = check_release_claim(
        claim_manifest_path=Path(args.claim_manifest),
        delta_manifest_path=Path(args.delta_manifest),
    )
    if failures:
        for failure in failures:
            print(failure)
        print("rc0_1_release_claim_verdict=fail")
        return 1
    print("rc0_1_release_claim_verdict=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
