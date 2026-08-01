from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from ilc_core.ledger.ecu_active_layer_runtime import EcuActiveLayerRuntime
from ilc_core.ledger.ecu_ilc_lifecycle_runtime import EcuIlcLifecycleRuntime
from ilc_core.protocol.public_wallet_runtime import WALLET_CLAIMABILITY_STATE_PROOF_AUTHORIZED
from ilc_core.sidecars.wallet_action_semantics_preflight import wallet_action_semantics_preflight_manifest
from ilc_core.storage.lmdb_public_runtime import LmdbWalletStore


AGENT_ID = "agent-1578g-wallet-cli"


def _seed_wallet_store(tmp_path: Path) -> Path:
    wallet_store_path = tmp_path / "wallet-store"
    wallet_store = LmdbWalletStore(wallet_store_path)
    try:
        runtime = EcuIlcLifecycleRuntime(
            wallet_store=wallet_store,
            ecu_runtime=EcuActiveLayerRuntime(),
        )
        runtime.commit_settled_epoch(
            agent_id=AGENT_ID,
            epoch_id="epoch-1578g",
            reward_delta_ilc="12.345",
        )
    finally:
        wallet_store.close()
    return wallet_store_path


def _run_wallet_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd())
    return subprocess.run(
        [sys.executable, "-m", "ilc_core.cli", "wallet", *args],
        check=False,
        capture_output=True,
        env=env,
        text=True,
    )


def _json_stdout(result: subprocess.CompletedProcess[str]) -> dict:
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_wallet_status_returns_exit_0(tmp_path: Path) -> None:
    wallet_store_path = _seed_wallet_store(tmp_path)

    result = _run_wallet_cli(
        "status",
        "--agent-id",
        AGENT_ID,
        "--wallet-store",
        str(wallet_store_path),
    )

    payload = _json_stdout(result)
    assert payload["subcommand"] == "status"
    assert payload["read_only"] is True
    assert payload["data"]["agent_id"] == AGENT_ID
    assert payload["data"]["balance_ilc"] == "12.345"


def test_wallet_history_includes_claimability_state(tmp_path: Path) -> None:
    wallet_store_path = _seed_wallet_store(tmp_path)

    payload = _json_stdout(
        _run_wallet_cli(
            "history",
            "--agent-id",
            AGENT_ID,
            "--wallet-store",
            str(wallet_store_path),
        )
    )

    assert payload["subcommand"] == "history"
    assert payload["data"]["claimability_state"] == WALLET_CLAIMABILITY_STATE_PROOF_AUTHORIZED
    assert payload["data"]["record_count"] == 1


def test_wallet_identity_returns_agent_id() -> None:
    payload = _json_stdout(_run_wallet_cli("identity", "--agent-id", AGENT_ID))

    assert payload["subcommand"] == "identity"
    assert payload["data"]["agent_id"] == AGENT_ID
    assert payload["data"]["account_anchor"] == "agent_id"
    assert payload["data"]["signer_binding_status"] == "deferred"


def test_status_does_not_create_lmdb_files_for_empty_existing_directory(tmp_path: Path) -> None:
    wallet_store_path = tmp_path / "empty-wallet-store"
    wallet_store_path.mkdir()

    result = _run_wallet_cli(
        "status",
        "--agent-id",
        AGENT_ID,
        "--wallet-store",
        str(wallet_store_path),
    )

    assert result.returncode == 1
    assert not (wallet_store_path / "data.mdb").exists()
    assert not (wallet_store_path / "lock.mdb").exists()


def test_no_submit_flag_exists() -> None:
    source = Path("ilc_core/cli/wallet_cli.py").read_text(encoding="utf-8")

    assert "--submit" not in source


def test_no_broadcast_capability() -> None:
    source = Path("ilc_core/cli/wallet_cli.py").read_text(encoding="utf-8")

    assert "broadcast" not in source
    assert "def send" not in source


def test_json_format_output(tmp_path: Path) -> None:
    wallet_store_path = _seed_wallet_store(tmp_path)

    payload = _json_stdout(
        _run_wallet_cli(
            "status",
            "--agent-id",
            AGENT_ID,
            "--wallet-store",
            str(wallet_store_path),
            "--format",
            "json",
        )
    )

    assert payload["ok"] is True
    assert payload["version"] == "wallet_cli_1578g.v0.1"


def test_text_format_output(tmp_path: Path) -> None:
    wallet_store_path = _seed_wallet_store(tmp_path)

    result = _run_wallet_cli(
        "status",
        "--agent-id",
        AGENT_ID,
        "--wallet-store",
        str(wallet_store_path),
        "--format",
        "text",
    )

    assert result.returncode == 0
    assert "wallet status" in result.stdout
    assert f"agent-id: {AGENT_ID}" in result.stdout
    assert "balance_ilc: 12.345" in result.stdout


def test_help_hierarchy() -> None:
    wallet_help = _run_wallet_cli("--help")
    status_help = _run_wallet_cli("status", "--help")
    top_help = subprocess.run(
        [sys.executable, "-m", "ilc_core.cli", "--help"],
        check=False,
        capture_output=True,
        env={**os.environ.copy(), "PYTHONPATH": str(Path.cwd())},
        text=True,
    )

    assert top_help.returncode == 0
    assert "wallet" in top_help.stdout
    assert wallet_help.returncode == 0
    assert "status" in wallet_help.stdout
    assert "history" in wallet_help.stdout
    assert "identity" in wallet_help.stdout
    assert status_help.returncode == 0
    assert "--agent-id" in status_help.stdout
    assert "--format" in status_help.stdout


def test_transfer_guards_unchanged_after_cli_call(tmp_path: Path) -> None:
    wallet_store_path = _seed_wallet_store(tmp_path)
    before = wallet_action_semantics_preflight_manifest()

    result = _run_wallet_cli(
        "status",
        "--agent-id",
        AGENT_ID,
        "--wallet-store",
        str(wallet_store_path),
    )

    after = wallet_action_semantics_preflight_manifest()
    assert result.returncode == 0
    assert before == after
    assert after["wallet_transfer_enabled"] is False
    assert after["wallet_withdrawal_enabled"] is False
    assert after["wallet_spend_enabled"] is False
