#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.network.d2d.http_gossip_transport_runtime import (
    HttpGossipTransportRuntime,
    TransportRuntimeError,
)
from ilc_core.node.node_startup_runtime import build_node_startup_context


CONFIG_EXIT_CODE = 10
GENESIS_EXIT_CODE = 11
TRANSPORT_EXIT_CODE = 12
LIFECYCLE_EXIT_CODE = 13

NODE_SERVICE_STARTING = "node_service_starting"
NODE_SERVICE_READY = "node_service_ready"
NODE_SERVICE_STOPPING = "node_service_stopping"
NODE_SERVICE_RESTART_REQUESTED = "node_service_restart_requested"
NODE_SERVICE_FAILED = "node_service_failed"


def _emit(marker: str, **payload: object) -> None:
    entry = {"marker": marker, **payload}
    print(json.dumps(entry, sort_keys=True), flush=True)


def run_service(
    action: str,
    *,
    config_path: str | None,
    genesis_reference_path: str | None,
    stay_alive_seconds: float,
) -> int:
    if action == 'stop':
        _emit(NODE_SERVICE_STOPPING, action=action)
        return 0

    if action == 'restart':
        _emit(NODE_SERVICE_RESTART_REQUESTED, action=action)

    _emit(NODE_SERVICE_STARTING, action=action)
    runtime: HttpGossipTransportRuntime | None = None
    try:
        context = build_node_startup_context(config_path or '', genesis_reference_path or '')
    except ValueError as exc:
        token = str(exc)
        if token.startswith('peer_config_'):
            _emit(NODE_SERVICE_FAILED, token=token)
            return CONFIG_EXIT_CODE
        if token.startswith('genesis_import_'):
            _emit(NODE_SERVICE_FAILED, token=token)
            return GENESIS_EXIT_CODE
        _emit(NODE_SERVICE_FAILED, token=token)
        return LIFECYCLE_EXIT_CODE

    try:
        runtime = HttpGossipTransportRuntime(context.transport_config)
        runtime.start()
        _emit(
            NODE_SERVICE_READY,
            node_id=context.node_id,
            bind_port=runtime.state['bound_port'],
            transport_kind=runtime.state['transport_kind'],
        )
        if stay_alive_seconds > 0:
            time.sleep(stay_alive_seconds)
        return 0
    except (TransportRuntimeError, ValueError, OSError) as exc:
        _emit(NODE_SERVICE_FAILED, token=str(exc))
        return TRANSPORT_EXIT_CODE
    except Exception as exc:  # pragma: no cover - reserved for unexpected lifecycle faults
        _emit(NODE_SERVICE_FAILED, token=exc.__class__.__name__)
        return LIFECYCLE_EXIT_CODE
    finally:
        if runtime is not None and runtime.state.get('running'):
            runtime.stop()
        _emit(NODE_SERVICE_STOPPING, action=action)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Run the ILC node service v1 lifecycle wrapper.')
    parser.add_argument('action', choices=('start', 'stop', 'restart'))
    parser.add_argument('--config', dest='config_path')
    parser.add_argument('--genesis-ref', dest='genesis_reference_path')
    parser.add_argument('--stay-alive-seconds', type=float, default=0.1)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    return run_service(
        args.action,
        config_path=args.config_path,
        genesis_reference_path=args.genesis_reference_path,
        stay_alive_seconds=args.stay_alive_seconds,
    )


if __name__ == '__main__':
    raise SystemExit(main())
