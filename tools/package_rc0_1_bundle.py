#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / 'out/rc0_1_bundle'
DEFAULT_GUIDANCE_PATHS = [
    'docs/specs/ilc_rc0_1_readiness_checklist_v0.1.md',
    'docs/specs/ilc_near_rc_node_definition_v0.1.md',
    'docs/specs/ilc_core_vs_agentic_harness_boundary_v0.1.md',
    'docs/ops/ilc_three_machine_operator_playbook_v0.1.md',
    'docs/specs/ilc_remote_control_surface_v0.1.md',
]


class BundleError(RuntimeError):
    pass


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=str(REPO_ROOT), capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise BundleError(
            f"command_failed:{' '.join(command)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def _git_head() -> str:
    return _run(['git', 'rev-parse', 'HEAD']).stdout.strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def build_bundle(*, output_root: Path, evidence_root: Path | None) -> dict[str, object]:
    output_root.mkdir(parents=True, exist_ok=True)
    archive_path = output_root / 'ilc_rc0_1_bundle.tar.gz'
    _run(['git', 'archive', '--format=tar.gz', '--output', str(archive_path), 'HEAD'])

    copied_docs: list[str] = []
    docs_root = output_root / 'guidance'
    docs_root.mkdir(exist_ok=True)
    for rel_path in DEFAULT_GUIDANCE_PATHS:
        source = REPO_ROOT / rel_path
        target = docs_root / Path(rel_path).name
        shutil.copy2(source, target)
        copied_docs.append(str(target))

    copied_evidence: list[str] = []
    if evidence_root is not None and evidence_root.exists():
        evidence_out = output_root / 'evidence'
        evidence_out.mkdir(exist_ok=True)
        for name in ('manifest.json', 'summary.md'):
            source = evidence_root / name
            if source.exists():
                target = evidence_out / name
                shutil.copy2(source, target)
                copied_evidence.append(str(target))

    manifest = {
        'version': 'rc0_1_bundle_v0.1',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'repo_head': _git_head(),
        'archive_path': str(archive_path),
        'archive_sha256': _sha256(archive_path),
        'archive_size_bytes': archive_path.stat().st_size,
        'guidance_files': copied_docs,
        'evidence_files': copied_evidence,
    }
    manifest_path = output_root / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return manifest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Build the current RC0.1 tarball candidate and copy the core guidance/evidence files next to it.')
    parser.add_argument('--output-root')
    parser.add_argument('--evidence-root')
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    output_root = Path(args.output_root) if args.output_root else DEFAULT_OUTPUT_ROOT / datetime.now().strftime('%Y%m%d_%H%M%S')
    evidence_root = Path(args.evidence_root) if args.evidence_root else None
    try:
        manifest = build_bundle(output_root=output_root, evidence_root=evidence_root)
    except BundleError as exc:
        print(json.dumps({'marker': 'rc0_1_bundle_failed', 'detail': str(exc)}, sort_keys=True, separators=(',', ':')))
        return 1
    print(json.dumps({'marker': 'rc0_1_bundle_ok', 'manifest': manifest}, sort_keys=True, separators=(',', ':')))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
