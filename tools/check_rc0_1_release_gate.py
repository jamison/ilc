#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

REQUIRED_GUIDANCE = {
    'ilc_rc0_1_readiness_checklist_v0.1.md',
    'ilc_near_rc_node_definition_v0.1.md',
    'ilc_core_vs_agentic_harness_boundary_v0.1.md',
    'ilc_three_machine_operator_playbook_v0.1.md',
    'ilc_remote_control_surface_v0.1.md',
}
REQUIRED_INSTALLERS = {
    'rc_bundle_runtime.py',
    'rc_install_bundle_node.py',
    'rc_update_bundle_node.py',
    'check_rc0_1_release_gate.py',
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _parse_checklist_statuses(path: Path) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.startswith('|'):
            continue
        columns = [col.strip() for col in line.strip().strip('|').split('|')]
        if len(columns) != 4 or columns[0] in {'Area', '---'}:
            continue
        statuses[columns[0]] = columns[3]
    return statuses


def check_release_gate(
    *,
    bundle_manifest_path: Path,
    evidence_manifest_path: Path,
    checklist_path: Path,
    economic_manifest_path: Path | None = None,
    economic_proof_manifest_path: Path | None = None,
) -> tuple[str, list[str]]:
    bundle = json.loads(bundle_manifest_path.read_text(encoding='utf-8'))
    evidence = json.loads(evidence_manifest_path.read_text(encoding='utf-8'))
    checklist_statuses = _parse_checklist_statuses(checklist_path)
    failures: list[str] = []

    archive_path = Path(bundle['archive_path'])
    if not archive_path.is_file():
        failures.append(f'archive_missing:{archive_path}')
    elif bundle.get('archive_sha256') != _sha256(archive_path):
        failures.append('archive_sha_mismatch')

    if bundle.get('repo_head') != evidence.get('repo_head'):
        failures.append('bundle_evidence_repo_head_mismatch')

    guidance_names = {Path(path).name for path in bundle.get('guidance_files', [])}
    missing_guidance = sorted(REQUIRED_GUIDANCE - guidance_names)
    if missing_guidance:
        failures.append(f"missing_guidance:{','.join(missing_guidance)}")

    installer_names = {Path(path).name for path in bundle.get('installer_files', [])}
    missing_installers = sorted(REQUIRED_INSTALLERS - installer_names)
    if missing_installers:
        failures.append(f"missing_installers:{','.join(missing_installers)}")

    for key, value in sorted(evidence.get('closure_rows', {}).items()):
        if value != 'satisfied_for_testbed':
            failures.append(f'closure_row_not_satisfied:{key}:{value}')

    if evidence.get('scenario_summary', {}).get('panel_verdict_token') != 'panel_quorum_passed':
        failures.append('scenario_panel_verdict_not_passed')
    scenario_replay = evidence.get('scenario_replay_summary', {})
    if scenario_replay.get('panel_result_matches') is not True:
        failures.append('scenario_replay_panel_not_matched')
    if scenario_replay.get('ecu_claims_match') is not True:
        failures.append('scenario_replay_claims_not_matched')

    if economic_manifest_path is not None:
        if not economic_manifest_path.is_file():
            failures.append(f'economic_manifest_missing:{economic_manifest_path}')
        else:
            economic_manifest = json.loads(economic_manifest_path.read_text(encoding='utf-8'))
            economic_summary = economic_manifest.get('summary', {})
            if economic_summary.get('distribution_check_ok') is not True:
                failures.append('economic_manifest_distribution_check_not_passed')
            runtime_store = economic_manifest.get('runtime_store', {})
            if runtime_store.get('store_kind') != 'lmdb_public_runtime_v0.1':
                failures.append('economic_manifest_runtime_store_kind_invalid')

    if economic_proof_manifest_path is not None:
        if not economic_proof_manifest_path.is_file():
            failures.append(f'economic_proof_manifest_missing:{economic_proof_manifest_path}')
        else:
            proof_manifest = json.loads(economic_proof_manifest_path.read_text(encoding='utf-8'))
            comparison = proof_manifest.get('comparison', {})
            if not isinstance(comparison, dict) or not comparison or not all(comparison.values()):
                failures.append('economic_proof_comparison_failed')
            invariant_summary = proof_manifest.get('invariant_summary', {})
            if invariant_summary.get('runtime_store', {}).get('store_kind') != 'lmdb_public_runtime_v0.1':
                failures.append('economic_proof_runtime_store_kind_invalid')

    unsatisfied_rows = sorted(
        area for area, status in checklist_statuses.items() if status != 'satisfied_for_testbed'
    )
    if unsatisfied_rows:
        failures.append(f"checklist_rows_not_satisfied:{','.join(unsatisfied_rows)}")

    if failures:
        return 'fail', failures
    return 'pass', []


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Check the final RC0.1 bundle and evidence manifests for a deterministic release verdict.')
    parser.add_argument('--bundle-manifest', required=True)
    parser.add_argument('--evidence-manifest', required=True)
    parser.add_argument('--checklist', default='docs/specs/ilc_rc0_1_readiness_checklist_v0.1.md')
    parser.add_argument('--proof-manifest')
    parser.add_argument('--economic-manifest')
    parser.add_argument('--economic-proof-manifest')
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    verdict, failures = check_release_gate(
        bundle_manifest_path=Path(args.bundle_manifest),
        evidence_manifest_path=Path(args.evidence_manifest),
        checklist_path=Path(args.checklist),
        economic_manifest_path=Path(args.economic_manifest) if args.economic_manifest else None,
        economic_proof_manifest_path=Path(args.economic_proof_manifest) if args.economic_proof_manifest else None,
    )
    if args.proof_manifest:
        proof_payload = json.loads(Path(args.proof_manifest).read_text(encoding='utf-8'))
        proof_failures = [
            item.get('host', 'unknown')
            for item in proof_payload.get('results', [])
            if item.get('status') != 'ok'
        ]
        if proof_failures:
            failures.append(f"bundle_install_proof_failed:{','.join(sorted(proof_failures))}")
    if failures:
        for failure in failures:
            print(failure)
        print('rc0_1_release_verdict=fail')
        return 1
    print('rc0_1_release_verdict=pass')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
