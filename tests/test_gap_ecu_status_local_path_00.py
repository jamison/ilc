from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ilc_core.cli import ecu_status_cli
from ilc_core.cli.ecu_status_cli import EcuStatusCliError, handle_ecu_status
from ilc_core.consensus.attribution_batch_bridge import (
    initialize_rust_balance_store,
    read_rust_balance_store_ecu,
)
from ilc_core.ledger.ecu_active_layer_runtime import EcuActiveLayerRuntime
from ilc_core.ledger.ecu_ilc_lifecycle_runtime import EcuIlcLifecycleRuntime
from ilc_core import server as server_module
from ilc_core.server import create_app
from ilc_core.storage.lmdb_public_runtime import LmdbWalletStore


ROOT = Path(__file__).resolve().parents[1]
RUST_BINARY = ROOT / "ilc_consensus" / "target" / "release" / "attribution_batch_ingest"
AGENT_ID = "c43f69fcc4dfd021f5e468824c9560c03c45c601f8d004be4d244356ce6043849b9cf2af38bc51a40c1c4bc3e71b04d9"


def _args(**overrides: object) -> argparse.Namespace:
    values: dict[str, object] = {
        "agent_id": AGENT_ID,
        "endpoint": "",
        "timeout": 10.0,
        "wallet_store": "",
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def _clear_status_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "ILC_ECU_STATUS_ENDPOINT",
        "ILC_WALLET_STORE_PATH",
        "ILC_CONSENSUS_LMDB_PATH",
        "ILC_ATTRIBUTION_BATCH_INGEST_BINARY",
    ):
        monkeypatch.delenv(name, raising=False)


def _seed_wallet_store(path: Path) -> None:
    store = LmdbWalletStore(path)
    try:
        runtime = EcuIlcLifecycleRuntime(
            wallet_store=store,
            ecu_runtime=EcuActiveLayerRuntime(),
        )
        runtime.commit_settled_epoch(
            agent_id=AGENT_ID,
            epoch_id="epoch-gap-ecu-status-local-path-00",
            reward_delta_ilc="1.25",
        )
    finally:
        store.close()


def _require_rust_binary() -> Path:
    assert RUST_BINARY.exists(), f"missing Rust binary: {RUST_BINARY}"
    assert os.access(RUST_BINARY, os.X_OK), f"non-executable Rust binary: {RUST_BINARY}"
    return RUST_BINARY


def test_no_endpoint_no_wallet_returns_diagnostic_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_status_env(monkeypatch)

    result = handle_ecu_status(_args())

    assert result["pending_attribution_quote"] == "0"
    assert result["committed_ecu_balance"] == "0"
    assert result["balance_ecu_source"] == "local_zero_state_no_source_configured"
    assert result["status"] == "no_endpoint_or_wallet_store_configured"


def test_no_source_zero_does_not_emit_stale_bridge_marker(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_status_env(monkeypatch)

    result = handle_ecu_status(_args())

    assert "python_in_memory_ecu_python_rust_balance_bridge_missing_phase_1597" not in json.dumps(
        result,
        sort_keys=True,
    )


def test_invalid_agent_id_rejected_before_local_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_status_env(monkeypatch)

    with pytest.raises(EcuStatusCliError, match="ecu_status_agent_id_invalid"):
        handle_ecu_status(_args(agent_id="not-an-agent"))


def test_wallet_store_argument_returns_diagnostic_wallet_source(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_status_env(monkeypatch)
    wallet_store = tmp_path / "wallet.lmdb"
    _seed_wallet_store(wallet_store)

    result = handle_ecu_status(_args(wallet_store=str(wallet_store)))

    assert result["committed_ecu_balance"] == "0"
    assert result["settled_ilc_balance"] == "1.25"
    assert result["balance_ecu_source"] == "local_wallet_store_read_model"
    assert result["status"] == "local_wallet_store_read_model"


def test_wallet_store_diagnostic_reads_explicit_ecu_field_only(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_status_env(monkeypatch)
    wallet_store = tmp_path / "wallet-with-ecu.lmdb"
    store = LmdbWalletStore(wallet_store)
    try:
        store.put_wallet(
            AGENT_ID,
            {
                "agent_id": AGENT_ID,
                "balance_ecu": "2.5",
                "balance_ilc": "7",
                "claimability_state": "deferred",
            },
        )
    finally:
        store.close()

    result = handle_ecu_status(_args(wallet_store=str(wallet_store)))

    assert result["committed_ecu_balance"] == "2.5"
    assert result["settled_ilc_balance"] == "7"
    assert result["balance_ecu_source"] == "local_wallet_store_read_model"


def test_wallet_store_env_returns_diagnostic_wallet_source(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_status_env(monkeypatch)
    wallet_store = tmp_path / "wallet-env.lmdb"
    _seed_wallet_store(wallet_store)
    monkeypatch.setenv("ILC_WALLET_STORE_PATH", str(wallet_store))

    result = handle_ecu_status(_args())

    assert result["balance_ecu_source"] == "local_wallet_store_read_model"


def test_configured_missing_wallet_store_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_status_env(monkeypatch)

    with pytest.raises(EcuStatusCliError, match="ecu_status_wallet_store_missing"):
        handle_ecu_status(_args(wallet_store=str(tmp_path / "missing-wallet.lmdb")))


def test_endpoint_mode_unchanged_and_preserves_source(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_status_env(monkeypatch)

    def fake_load(_url: str, *, timeout: float) -> dict[str, object]:
        assert timeout == 10.0
        return {
            "agent_id": AGENT_ID,
            "pending_attribution_quote": "0",
            "committed_ecu_balance": "0",
            "balance_ecu_source": "remote_test_source",
            "status": "endpoint_response",
            "quote_epoch": 1,
        }

    monkeypatch.setattr(ecu_status_cli, "_load_status_payload", fake_load)

    result = handle_ecu_status(_args(endpoint="https://validator.example/api/v1/ecu/status"))

    assert result["endpoint"] == "https://validator.example/api/v1/ecu/status"
    assert result["balance_ecu_source"] == "remote_test_source"


def test_http_endpoint_still_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_status_env(monkeypatch)

    with pytest.raises(EcuStatusCliError, match="ecu_status_endpoint_https_required"):
        handle_ecu_status(_args(endpoint="http://validator.example/api/v1/ecu/status"))


def test_initialize_rust_balance_store_creates_readable_empty_store(tmp_path: Path) -> None:
    binary = _require_rust_binary()
    consensus_lmdb = tmp_path / "consensus.lmdb"

    report = initialize_rust_balance_store(consensus_lmdb, rust_binary=binary)

    assert report == {"marker": "attribution_balance_store_init_ok", "initialized": True}
    assert (consensus_lmdb / "data.mdb").exists()
    assert read_rust_balance_store_ecu(consensus_lmdb, AGENT_ID, rust_binary=binary) == 0


def test_existing_uninitialized_rust_lmdb_directory_fails_closed(tmp_path: Path) -> None:
    binary = _require_rust_binary()
    consensus_lmdb = tmp_path / "empty-consensus.lmdb"
    consensus_lmdb.mkdir()

    with pytest.raises(ValueError, match="lifecycle_balance_readback_lmdb_uninitialized"):
        read_rust_balance_store_ecu(consensus_lmdb, AGENT_ID, rust_binary=binary)


def test_rust_configured_status_initializes_and_reads_zero(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    binary = _require_rust_binary()
    _clear_status_env(monkeypatch)
    consensus_lmdb = tmp_path / "clean-consensus.lmdb"
    monkeypatch.setenv("ILC_CONSENSUS_LMDB_PATH", str(consensus_lmdb))
    monkeypatch.setenv("ILC_ATTRIBUTION_BATCH_INGEST_BINARY", str(binary))

    result = handle_ecu_status(_args())

    assert result["committed_ecu_balance"] == "0"
    assert result["balance_ecu_source"] == "rust_balance_store_committed_aggregate"
    assert result["balance_ecu_pending"] == "0"
    assert (consensus_lmdb / "data.mdb").exists()


def test_rust_configured_status_never_emits_stale_bridge_marker(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    binary = _require_rust_binary()
    _clear_status_env(monkeypatch)
    monkeypatch.setenv("ILC_CONSENSUS_LMDB_PATH", str(tmp_path / "consensus.lmdb"))
    monkeypatch.setenv("ILC_ATTRIBUTION_BATCH_INGEST_BINARY", str(binary))

    result = handle_ecu_status(_args())

    assert "python_in_memory_ecu_python_rust_balance_bridge_missing_phase_1597" not in json.dumps(
        result,
        sort_keys=True,
    )


def test_configured_rust_binary_missing_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_status_env(monkeypatch)
    monkeypatch.setenv("ILC_CONSENSUS_LMDB_PATH", str(tmp_path / "consensus.lmdb"))
    monkeypatch.setenv("ILC_ATTRIBUTION_BATCH_INGEST_BINARY", str(tmp_path / "missing-binary"))

    with pytest.raises(EcuStatusCliError, match="lifecycle_balance_store_init_binary_missing"):
        handle_ecu_status(_args())


def test_configured_rust_lmdb_file_path_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    binary = _require_rust_binary()
    _clear_status_env(monkeypatch)
    bad_path = tmp_path / "not-a-directory"
    bad_path.write_text("not lmdb\n", encoding="utf-8")
    monkeypatch.setenv("ILC_CONSENSUS_LMDB_PATH", str(bad_path))
    monkeypatch.setenv("ILC_ATTRIBUTION_BATCH_INGEST_BINARY", str(binary))

    with pytest.raises(EcuStatusCliError, match="lifecycle_balance_store_init_lmdb_path_invalid"):
        handle_ecu_status(_args())


def test_lifecycle_error_token_preserved_in_local_rust_status(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    binary = _require_rust_binary()
    _clear_status_env(monkeypatch)
    wallet_store = tmp_path / "bad-wallet.lmdb"
    store = LmdbWalletStore(wallet_store)
    try:
        store.put_wallet(
            AGENT_ID,
            {
                "agent_id": AGENT_ID,
                "balance_ilc": "0",
                "claimability_state": " padded ",
            },
        )
    finally:
        store.close()
    monkeypatch.setenv("ILC_CONSENSUS_LMDB_PATH", str(tmp_path / "consensus.lmdb"))
    monkeypatch.setenv("ILC_ATTRIBUTION_BATCH_INGEST_BINARY", str(binary))

    with pytest.raises(EcuStatusCliError, match="lifecycle_claimability_state_invalid"):
        handle_ecu_status(_args(wallet_store=str(wallet_store)))


def test_endpoint_precedence_over_local_rust(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    binary = _require_rust_binary()
    _clear_status_env(monkeypatch)
    monkeypatch.setenv("ILC_CONSENSUS_LMDB_PATH", str(tmp_path / "unused-consensus.lmdb"))
    monkeypatch.setenv("ILC_ATTRIBUTION_BATCH_INGEST_BINARY", str(binary))

    def fake_load(_url: str, *, timeout: float) -> dict[str, object]:
        return {
            "agent_id": AGENT_ID,
            "pending_attribution_quote": "0",
            "committed_ecu_balance": "0",
            "balance_ecu_source": "endpoint_wins",
            "status": "endpoint_response",
        }

    monkeypatch.setattr(ecu_status_cli, "_load_status_payload", fake_load)

    result = handle_ecu_status(_args(endpoint="https://validator.example/api/v1/ecu/status"))

    assert result["balance_ecu_source"] == "endpoint_wins"
    assert not (tmp_path / "unused-consensus.lmdb").exists()


def test_cli_help_exposes_wallet_store_flag() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ilc_core.cli", "ecu", "status", "--help"],
        capture_output=True,
        check=True,
        text=True,
    )

    assert "--wallet-store" in result.stdout


def test_server_wires_consensus_lmdb_and_reports_rust_source(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    binary = _require_rust_binary()
    _clear_status_env(monkeypatch)
    consensus_lmdb = tmp_path / "server-consensus.lmdb"
    monkeypatch.setenv("ILC_CONSENSUS_LMDB_PATH", str(consensus_lmdb))
    monkeypatch.setenv("ILC_ATTRIBUTION_BATCH_INGEST_BINARY", str(binary))

    app = create_app()
    with TestClient(app) as client:
        response = client.get("/api/v1/ecu/status", params={"agent_id": AGENT_ID})

    assert response.status_code == 200
    payload = response.json()
    assert payload["committed_ecu_balance"] == "0"
    assert payload["balance_ecu_source"] == "rust_balance_store_committed_aggregate"
    assert app.state.public_consensus_lmdb_path == str(consensus_lmdb)
    assert (consensus_lmdb / "data.mdb").exists()


def test_server_uses_configured_wallet_store_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_status_env(monkeypatch)
    wallet_store = tmp_path / "server-wallet.lmdb"
    monkeypatch.setenv("ILC_WALLET_STORE_PATH", str(wallet_store))

    app = create_app()
    with TestClient(app):
        pass

    assert app.state.public_wallet_store_path == wallet_store


def test_server_startup_failure_cleans_temp_runtime_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_status_env(monkeypatch)
    runtime_root = tmp_path / "runtime-root"
    monkeypatch.setenv("ILC_CONSENSUS_LMDB_PATH", str(tmp_path / "consensus.lmdb"))
    monkeypatch.setattr(tempfile, "mkdtemp", lambda prefix: str(runtime_root))

    def fail_init(*_args: object, **_kwargs: object) -> None:
        raise ValueError("lifecycle_balance_store_init_binary_missing")

    monkeypatch.setattr(server_module, "initialize_rust_balance_store", fail_init)

    with pytest.raises(ValueError, match="lifecycle_balance_store_init_binary_missing"):
        server_module._init_runtime_state(create_app())

    assert not runtime_root.exists()
