# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOKEN_RE = re.compile(r"^[0-9a-f]{64}$")


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


def test_model_router_help_lists_three_subcommands() -> None:
    result = _run_cli("sidecar", "model-router", "--help")

    assert result.returncode == 0
    assert "route" in result.stdout
    assert "promote-receipt" in result.stdout
    assert "list-receipts" in result.stdout


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
        "--dry-run",
    )
    assert route.returncode == 0, route.stderr
    route_payload = json.loads(route.stdout)
    receipt_token = route_payload["receipt_token"]
    assert TOKEN_RE.fullmatch(receipt_token)
    assert route_payload["status"] == "success"
    assert route_payload["consent_status"] == "local_only"

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
        "--out-dir",
        str(promotion_dir),
    )
    assert promoted.returncode == 0, promoted.stderr
    promoted_payload = json.loads(promoted.stdout)
    assert promoted_payload["promotion_status"] == "local_only_stub"
    assert promoted_payload["non_claim"] == "graph_promotion_requires_cdl_116_phase_1615"
    assert (promotion_dir / f"{receipt_token}.json").exists()


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


def test_smoke_script_writes_atomic_evidence(tmp_path: Path) -> None:
    out_dir = tmp_path / "smoke"
    env = os.environ.copy()
    env["ILC_MODEL_ROUTER_SMOKE_OUT_DIR"] = str(out_dir)
    env["ILC_MODEL_ROUTER_STORE_PATH"] = str(out_dir / "router_receipts.lmdb")
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
    assert evidence["promote_status"] == "local_only_stub"
