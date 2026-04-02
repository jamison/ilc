#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / 'out/rc0_1_release_gate'


class ReleaseGateError(RuntimeError):
    pass


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=str(REPO_ROOT), capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise ReleaseGateError(
            f"command_failed:{' '.join(command)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def run_release_gate(*, evidence_root: Path, output_root: Path) -> dict[str, object]:
    evidence_root = evidence_root.resolve()
    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    evidence_manifest_path = evidence_root / 'manifest.json'
    evidence_manifest = json.loads(evidence_manifest_path.read_text(encoding='utf-8'))
    economic_manifest_path = Path(str(evidence_manifest['economic_manifest_path'])) if evidence_manifest.get('economic_manifest_path') else None
    bundle_output = output_root / 'bundle'
    bundle_result = _run([
        'python3',
        'tools/package_rc0_1_bundle.py',
        '--output-root',
        str(bundle_output),
        '--evidence-root',
        str(evidence_root),
    ])
    bundle_payload = json.loads(bundle_result.stdout.strip())
    bundle_manifest_path = Path(bundle_payload['manifest']['manifest_path']) if 'manifest_path' in bundle_payload['manifest'] else bundle_output / 'manifest.json'
    if not bundle_manifest_path.exists():
        bundle_manifest_path = bundle_output / 'manifest.json'
    proof_output = output_root / 'bundle-install-proof'
    proof_result = _run([
        'python3',
        'tools/prove_rc0_1_bundle_install.py',
        '--bundle-root',
        str(bundle_output),
        '--output-root',
        str(proof_output),
        '--include-home',
    ])
    proof_payload = json.loads(proof_result.stdout.strip())
    proof_manifest_path = Path(proof_payload['manifest']['manifest_path']) if 'manifest_path' in proof_payload['manifest'] else proof_output / 'manifest.json'
    if not proof_manifest_path.exists():
        proof_manifest_path = proof_output / 'manifest.json'

    economic_proof_manifest_path: Path | None = None
    economic_proof_stdout = ''
    if economic_manifest_path is not None:
        economic_proof_output = output_root / 'economic-proof'
        economic_proof_result = _run([
            'python3',
            'tools/prove_rc0_1_economic_state.py',
            '--manifest',
            str(economic_manifest_path),
            '--output-root',
            str(economic_proof_output),
        ])
        economic_proof_payload = json.loads(economic_proof_result.stdout.strip())
        economic_proof_manifest_path = Path(
            str(economic_proof_payload['manifest'].get('proof_manifest_path', economic_proof_output / 'manifest.json'))
        )
        if not economic_proof_manifest_path.exists():
            economic_proof_manifest_path = economic_proof_output / 'manifest.json'
        economic_proof_stdout = economic_proof_result.stdout.strip()

    verdict_command = [
        'python3',
        'tools/check_rc0_1_release_gate.py',
        '--bundle-manifest',
        str(bundle_manifest_path),
        '--evidence-manifest',
        str(evidence_manifest_path),
        '--proof-manifest',
        str(proof_manifest_path),
    ]
    if economic_manifest_path is not None:
        verdict_command.extend(['--economic-manifest', str(economic_manifest_path)])
    if economic_proof_manifest_path is not None:
        verdict_command.extend(['--economic-proof-manifest', str(economic_proof_manifest_path)])
    verdict_result = _run(verdict_command)
    payload = {
        'version': 'rc0_1_release_gate_v0.1',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'bundle_manifest_path': str(bundle_manifest_path),
        'bundle_install_proof_manifest_path': str(proof_manifest_path),
        'evidence_manifest_path': str(evidence_manifest_path),
        'economic_manifest_path': str(economic_manifest_path) if economic_manifest_path is not None else None,
        'economic_proof_manifest_path': str(economic_proof_manifest_path) if economic_proof_manifest_path is not None else None,
        'bundle_stdout': bundle_result.stdout.strip(),
        'bundle_install_proof_stdout': proof_result.stdout.strip(),
        'economic_proof_stdout': economic_proof_stdout,
        'release_verdict_stdout': verdict_result.stdout.strip(),
    }
    manifest_path = output_root / 'manifest.json'
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return payload


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Build the current RC0.1 bundle candidate and emit the final release-gate verdict.')
    parser.add_argument('--evidence-root', required=True)
    parser.add_argument('--output-root')
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    output_root = Path(args.output_root) if args.output_root else DEFAULT_OUTPUT_ROOT / datetime.now().strftime('%Y%m%d_%H%M%S')
    try:
        payload = run_release_gate(evidence_root=Path(args.evidence_root), output_root=output_root)
    except ReleaseGateError as exc:
        print(json.dumps({'marker': 'rc0_1_release_gate_failed', 'detail': str(exc)}, sort_keys=True, separators=(',', ':')))
        return 1
    print(json.dumps({'marker': 'rc0_1_release_gate_ok', 'manifest': payload}, sort_keys=True, separators=(',', ':')))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
