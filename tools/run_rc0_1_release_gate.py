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
    output_root.mkdir(parents=True, exist_ok=True)
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

    verdict_result = _run([
        'python3',
        'tools/check_rc0_1_release_gate.py',
        '--bundle-manifest',
        str(bundle_manifest_path),
        '--evidence-manifest',
        str(evidence_root / 'manifest.json'),
    ])
    payload = {
        'version': 'rc0_1_release_gate_v0.1',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'bundle_manifest_path': str(bundle_manifest_path),
        'evidence_manifest_path': str(evidence_root / 'manifest.json'),
        'bundle_stdout': bundle_result.stdout.strip(),
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
