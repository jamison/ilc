#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[1]
for candidate in (REPO_ROOT, SCRIPT_DIR):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

try:
    from tools.rc_bundle_runtime import RcBundleRuntimeError, update_bundle, write_result
except ModuleNotFoundError:
    from rc_bundle_runtime import RcBundleRuntimeError, update_bundle, write_result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Update an existing ILC node installation from an RC bundle.')
    parser.add_argument('--bundle', required=True)
    parser.add_argument('--repo-path', required=True)
    parser.add_argument('--venv-path', required=True)
    parser.add_argument('--config-source')
    parser.add_argument('--config-path')
    parser.add_argument('--service-unit-name', default='ilc-node-v1.service')
    parser.add_argument('--service-unit-dest')
    parser.add_argument('--emit-path')
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = update_bundle(
            bundle_path=Path(args.bundle),
            repo_path=Path(args.repo_path),
            venv_path=Path(args.venv_path),
            config_source=Path(args.config_source) if args.config_source else None,
            config_path=Path(args.config_path) if args.config_path else None,
            service_unit_name=args.service_unit_name,
            service_unit_dest=Path(args.service_unit_dest) if args.service_unit_dest else None,
        )
    except RcBundleRuntimeError as exc:
        print(json.dumps({'marker': 'rc_bundle_update_failed', 'detail': str(exc)}, sort_keys=True, separators=(',', ':')))
        return 1
    if args.emit_path:
        write_result(Path(args.emit_path), result)
    print(json.dumps({'marker': 'rc_bundle_update_ok', 'result': result.__dict__}, sort_keys=True, separators=(',', ':')))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
