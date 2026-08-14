# SPDX-License-Identifier: AGPL-3.0-only
"""CLI/JSON conformance tests for GAP-HARNESS-SIDECAR-01."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
QUERY_SCHEMA_VERSION = "299.v0.1"
VERIFY_SCHEMA_VERSION = "301.v0.1"
BUNDLE_SCHEMA_VERSION = "303.v0.1"
PRIMARY_SCHEMA_VERSION = "254.v0.1"


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    return path


def _graph_state(tmp_path: Path) -> Path:
    return _write_json(
        tmp_path / "graph.json",
        {
            "schema_version": "sidecar_01_fixture.v0.1",
            "nodes": [
                {
                    "node_id": "node-1",
                    "claim_id": "claim-1",
                    "body": "sidecar conformance fixture",
                }
            ],
            "epochs": [
                {
                    "epoch": 0,
                    "state_root": "sha256:fixture",
                }
            ],
        },
    )


def _bundle_state(tmp_path: Path) -> Path:
    return _write_json(
        tmp_path / "bundles.json",
        {
            "schema_version": "sidecar_01_bundle_fixture.v0.1",
            "bundles": [
                {
                    "bundle_cid": "bundle-1",
                    "provider": "local",
                    "manifest": {"name": "sidecar-fixture"},
                    "graph_refs": {"node_ids": ["node-1"], "claim_ids": ["claim-1"]},
                }
            ],
        },
    )


def _run_cli(
    tmp_path: Path,
    *args: str,
    graph_state: Path | None = None,
    extra_env: dict[str, str] | None = None,
) -> dict[str, Any]:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    command = [sys.executable, "-m", "ilc_core.cli"]
    if graph_state is not None:
        command.extend(["--graph-state", str(graph_state)])
    command.extend(args)
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    payload = json.loads(result.stdout)
    assert isinstance(payload, dict)
    assert payload.get("ok") is True
    assert "error" not in payload
    return payload


def _assert_primary_envelope(payload: dict[str, Any], command: str) -> dict[str, Any]:
    assert payload["schema_version"] == PRIMARY_SCHEMA_VERSION
    assert payload["command"] == command
    assert isinstance(payload["ts_utc"], str)
    assert isinstance(payload["data"], dict)
    return payload["data"]


def _assert_meta_envelope(
    payload: dict[str, Any],
    *,
    command: str,
    schema_version: str,
) -> dict[str, Any]:
    assert isinstance(payload["data"], dict)
    meta = payload["meta"]
    assert meta["command"] == command
    assert meta["schema_version"] == schema_version
    assert isinstance(meta["generated_at"], str)
    return payload["data"]


def test_identity_show_and_export_json_shape(tmp_path: Path) -> None:
    graph_state = _graph_state(tmp_path)
    init_data = _assert_primary_envelope(
        _run_cli(tmp_path, "identity", "init", graph_state=graph_state),
        "identity",
    )
    assert init_data["action"] == "init"
    assert isinstance(init_data["state"], dict)

    show_data = _assert_primary_envelope(
        _run_cli(tmp_path, "identity", "show", graph_state=graph_state),
        "identity",
    )
    assert show_data["action"] == "show"
    assert show_data["state"]["lineage_id"] == "lineage-local"

    export_data = _assert_primary_envelope(
        _run_cli(tmp_path, "identity", "export", graph_state=graph_state),
        "identity",
    )
    assert export_data["action"] == "export"
    assert export_data["export"]["status"] == "active"


def test_query_node_json_shape(tmp_path: Path) -> None:
    data = _assert_meta_envelope(
        _run_cli(
            tmp_path,
            "query",
            "node",
            "--node-id",
            "node-1",
            graph_state=_graph_state(tmp_path),
        ),
        command="query node",
        schema_version=QUERY_SCHEMA_VERSION,
    )
    assert data["query"] == "node"
    assert data["node_id"] == "node-1"
    assert isinstance(data["node"], dict)


def test_verify_node_json_shape(tmp_path: Path) -> None:
    data = _assert_meta_envelope(
        _run_cli(
            tmp_path,
            "verify",
            "node",
            "--node-id",
            "node-1",
            graph_state=_graph_state(tmp_path),
        ),
        command="verify node",
        schema_version=VERIFY_SCHEMA_VERSION,
    )
    assert data["subject"]["node_id"] == "node-1"
    assert data["verdict"]["verified"] is True
    assert isinstance(data["checks"], list)


def test_bundle_inspect_json_shape(tmp_path: Path) -> None:
    data = _assert_meta_envelope(
        _run_cli(
            tmp_path,
            "bundle",
            "inspect",
            "--bundle-cid",
            "bundle-1",
            graph_state=_graph_state(tmp_path),
            extra_env={"ILC_BUNDLE_STATE_PATH": str(_bundle_state(tmp_path))},
        ),
        command="bundle inspect",
        schema_version=BUNDLE_SCHEMA_VERSION,
    )
    assert data["subject"]["bundle_cid"] == "bundle-1"
    assert data["result"]["status"] == "inspected"
    assert isinstance(data["checks"], list)


def test_epoch_prototype_json_shape(tmp_path: Path) -> None:
    data = _assert_primary_envelope(_run_cli(tmp_path, "epoch"), "epoch")
    assert data["epoch_id"] == "epoch-local"
    assert data["state"] == "open"
    assert data["finalization_hash"] == "sha256:prototype"


def test_balance_prototype_json_shape(tmp_path: Path) -> None:
    data = _assert_primary_envelope(_run_cli(tmp_path, "balance"), "balance")
    assert data["account_id"] == "prototype_compat"
    assert data["balance_ilc"] == "0"
    assert data["pending_balance_ilc"] == "0"
    assert data["report_mode"] == "prototype_compat"


def test_submit_value_action_surface_json_shape(tmp_path: Path) -> None:
    data = _assert_primary_envelope(
        _run_cli(
            tmp_path,
            "submit",
            "--primitive",
            "assert.truth",
            "--payload-json",
            json.dumps(
                {
                    "content": {"body": "sidecar conformance fixture"},
                    "primitive_type": "observation",
                    "epistemic_type": "objective",
                    "parent_node_ids": [],
                },
                sort_keys=True,
            ),
            "--agent-id",
            "agent-sidecar-01",
            "--epoch",
            "0",
            graph_state=_graph_state(tmp_path),
        ),
        "submit",
    )
    assert data["subcommand"] == "submit"
    assert data["primitive"] == "assert.truth"
    assert data["creates_node"] is True
    assert data["node_primitive_type"] == "observation"
    assert data["graph_persistence"].startswith("deferred")


def test_python_m_ilc_core_is_not_registered_entrypoint_deviation() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ilc_core", "version"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert "No module named ilc_core.__main__" in result.stderr
