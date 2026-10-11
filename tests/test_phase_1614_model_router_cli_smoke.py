# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from argparse import Namespace
from pathlib import Path

from ilc_model_router import cli as model_router_cli
from ilc_model_router.adapter import ProviderAdapter, ProviderResponse, RouterRequest

REPO_ROOT = Path(__file__).resolve().parents[1]
TOKEN_RE = re.compile(r"^[0-9a-f]{64}$")


class _FailureAdapter(ProviderAdapter):
    def route(
        self,
        request: RouterRequest,
        *,
        timeout: float | None = None,
    ) -> ProviderResponse:
        return ProviderResponse(
            status="failure",
            content="",
            error_token="provider_timeout",
            token_counts_input=0,
            token_counts_output=0,
        )


def _run_cli(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(
        [sys.executable, "-m", "ilc_core.cli.main", *args],
        cwd=REPO_ROOT,
        env=merged_env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_model_router_help_lists_four_subcommands() -> None:
    result = _run_cli("sidecar", "model-router", "--help")

    assert result.returncode == 0
    assert "route" in result.stdout
    assert "promote-receipt" in result.stdout
    assert "list-receipts" in result.stdout
    assert "set-consent" in result.stdout
    assert "werner-context" in result.stdout


def test_sidecar_list_includes_model_router() -> None:
    result = _run_cli("sidecar", "list")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    sidecar_ids = {
        row["sidecar_id"]
        for row in payload["data"]["sidecars"]
        if "sidecar_id" in row
    }
    assert "model-router" in sidecar_ids


def test_route_list_promote_roundtrip_uses_real_lmdb_store(tmp_path: Path) -> None:
    store_path = tmp_path / "router_receipts.lmdb"
    graph_store_path = tmp_path / "truth_graph.lmdb"
    consent_path = tmp_path / "consent.json"
    promotion_dir = tmp_path / "promotions"

    route = _run_cli(
        "sidecar",
        "model-router",
        "route",
        "--model",
        "claude-haiku-4-5",
        "--provider",
        "anthropic",
        "--message",
        '{"role":"user","content":"ping"}',
        "--store-path",
        str(store_path),
        "--graph-store-path",
        str(graph_store_path),
        "--no-promote",
        "--dry-run",
        env={"ILC_MODEL_ROUTER_CONSENT_PATH": str(consent_path)},
    )
    assert route.returncode == 0, route.stderr
    route_payload = json.loads(route.stdout)
    receipt_token = route_payload["receipt_token"]
    assert TOKEN_RE.fullmatch(receipt_token)
    assert route_payload["status"] == "success"
    assert route_payload["error_token"] == ""
    assert route_payload["capability_class"] == "inference"
    assert route_payload["consent_status"] == "local_only"
    assert route_payload["promotion_status"] == "suppressed_no_promote"

    listed = _run_cli(
        "sidecar",
        "model-router",
        "list-receipts",
        "--store-path",
        str(store_path),
    )
    assert listed.returncode == 0, listed.stderr
    listed_payload = json.loads(listed.stdout)
    assert [row["receipt_token"] for row in listed_payload["receipts"]] == [receipt_token]

    promoted = _run_cli(
        "sidecar",
        "model-router",
        "promote-receipt",
        receipt_token,
        "--store-path",
        str(store_path),
        "--graph-store-path",
        str(graph_store_path),
        "--out-dir",
        str(promotion_dir),
        env={"ILC_MODEL_ROUTER_CONSENT_PATH": str(consent_path)},
    )
    assert promoted.returncode == 0, promoted.stderr
    promoted_payload = json.loads(promoted.stdout)
    assert promoted_payload["promotion_status"] == "promoted"
    assert promoted_payload["consent_status"] == "promoted"
    assert promoted_payload["node_id"].startswith("b")
    assert (promotion_dir / f"{receipt_token}.json").exists()

    context = _run_cli(
        "sidecar",
        "model-router",
        "werner-context",
        "--agent-id",
        "c" * 96,
        "--epoch",
        "0",
        "--store-path",
        str(store_path),
    )
    assert context.returncode == 0, context.stderr
    context_payload = json.loads(context.stdout)
    assert context_payload["receipt_count"] == 1
    assert context_payload["werner_context_present"] is True
    assert context_payload["flow_budget"] != "0E-12"
    assert "no_genesis_atlas_lmdb_write" in context_payload["non_claims"]


def test_route_without_dry_run_requires_api_key(tmp_path: Path) -> None:
    result = _run_cli(
        "sidecar",
        "model-router",
        "route",
        "--model",
        "claude-haiku-4-5",
        "--provider",
        "anthropic",
        "--message",
        '{"role":"user","content":"ping"}',
        "--store-path",
        str(tmp_path / "router_receipts.lmdb"),
        env={
            "ANTHROPIC_API_KEY": "",
            "ILC_MODEL_ROUTER_API_KEY": "",
            "OPENROUTER_API_KEY": "",
        },
    )

    assert result.returncode == 1
    payload = json.loads(result.stderr)
    assert payload["message"] == "model_router_api_key_required"


def test_route_output_includes_failure_error_token(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        model_router_cli,
        "_adapter_from_args",
        lambda _args: _FailureAdapter(),
    )
    result = model_router_cli.run_model_router_command(
        Namespace(
            agent_id="c" * 96,
            capability_class="embedding",
            dry_run=False,
            epoch=7,
            message='{"role":"user","content":"ping"}',
            model_id="claude-haiku-4-5",
            model_router_command="route",
            provider="anthropic",
            store_path=str(tmp_path / "router_receipts.lmdb"),
            graph_store_path=str(tmp_path / "truth_graph.lmdb"),
            no_promote=True,
            timeout=30.0,
        )
    )

    assert result["status"] == "failure"
    assert result["error_token"] == "provider_timeout"
    assert result["capability_class"] == "embedding"


def test_smoke_script_writes_atomic_evidence(tmp_path: Path) -> None:
    out_dir = tmp_path / "smoke"
    env = os.environ.copy()
    env["ILC_MODEL_ROUTER_SMOKE_OUT_DIR"] = str(out_dir)
    env["ILC_MODEL_ROUTER_STORE_PATH"] = str(out_dir / "router_receipts.lmdb")
    env["ILC_MODEL_ROUTER_GRAPH_STORE_PATH"] = str(out_dir / "truth_graph.lmdb")
    env["ILC_MODEL_ROUTER_CONSENT_PATH"] = str(out_dir / "consent.json")
    env["ILC_MODEL_ROUTER_PROMOTION_DIR"] = str(out_dir / "promotions")
    result = subprocess.run(
        ["bash", "tools/model_router/model_router_cli_smoke.sh"],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "model_router_cli_smoke_pass_phase_1614" in result.stdout
    evidence = json.loads((out_dir / "smoke_evidence.json").read_text())
    assert evidence["output_token"] == "model_router_cli_smoke_pass_phase_1614"
    assert TOKEN_RE.fullmatch(evidence["receipt_token"])
    assert evidence["promote_status"] == "promoted"
