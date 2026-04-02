#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from tools.rc_bundle_runtime import RcBundleRuntimeError, install_bundle, write_result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Install an ILC RC bundle into the standard node path layout.')
    parser.add_argument('--bundle', required=True)
    parser.add_argument('--repo-path', required=True)
    parser.add_argument('--venv-path', required=True)
    parser.add_argument('--config-source')
    parser.add_argument('--config-path')
    parser.add_argument('--service-unit-name', default='ilc-node-v1.service')
    parser.add_argument('--service-unit-dest')
    parser.add_argument('--replace-existing', action='store_true')
    parser.add_argument('--recreate-venv', action='store_true')
    parser.add_argument('--emit-path')
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = install_bundle(
            bundle_path=Path(args.bundle),
            repo_path=Path(args.repo_path),
            venv_path=Path(args.venv_path),
            config_source=Path(args.config_source) if args.config_source else None,
            config_path=Path(args.config_path) if args.config_path else None,
            service_unit_name=args.service_unit_name,
            service_unit_dest=Path(args.service_unit_dest) if args.service_unit_dest else None,
            replace_existing=args.replace_existing,
            recreate_venv=args.recreate_venv,
        )
    except RcBundleRuntimeError as exc:
        print(json.dumps({'marker': 'rc_bundle_install_failed', 'detail': str(exc)}, sort_keys=True, separators=(',', ':')))
        return 1
    if args.emit_path:
        write_result(Path(args.emit_path), result)
    print(json.dumps({'marker': 'rc_bundle_install_ok', 'result': result.__dict__}, sort_keys=True, separators=(',', ':')))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
