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
    ):
        claim_value = claim_manifest.get(key)
        delta_value = delta_manifest.get(key)
        if claim_value and delta_value and str(claim_value) != str(delta_value):
            failures.append(f"claim_delta_path_mismatch:{key}")

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
