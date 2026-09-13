from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ilc_core.protocol.public_wallet_runtime import (
    WALLET_CLAIMABILITY_STATE_DEFERRED,
    WALLET_CLAIMABILITY_STATE_PROOF_AUTHORIZED,
)
from ilc_core.server import create_app


TOOL_PATH = Path("tools/phase1575t_e2e_production_soak.py")


def _seed_wallet(client: TestClient, *, agent_id: str = "a" * 96) -> str:
    client.app.state.ecu_active_layer_runtime.set_accrued_ecu(agent_id, "1")
    client.app.state.public_lifecycle_runtime.commit_settled_epoch(
        agent_id=agent_id,
        epoch_id="epoch-claimability-fix1",
        reward_delta_ilc="1",
    )
    return agent_id


def test_wallet_status_defaults_to_deferred_from_lifecycle_row() -> None:
    with TestClient(create_app()) as client:
        agent_id = _seed_wallet(client)

        status = client.app.state.public_wallet_runtime.wallet_status(agent_id=agent_id)

    assert status["data"]["claimability_state"] == WALLET_CLAIMABILITY_STATE_DEFERRED


def test_wallet_runtime_reports_explicit_authorized_state_only_when_persisted() -> None:
    with TestClient(create_app()) as client:
        agent_id = _seed_wallet(client)
        store = client.app.state.public_lifecycle_runtime.wallet_store
        wallet_row = store.get_wallet(agent_id)
        wallet_history = store.get_wallet_history(agent_id)
        assert wallet_row is not None
        assert wallet_history is not None
        wallet_row["claimability_state"] = WALLET_CLAIMABILITY_STATE_PROOF_AUTHORIZED
        store.put_wallet_and_history(agent_id, wallet_row, wallet_history)

        status = client.app.state.public_wallet_runtime.wallet_status(agent_id=agent_id)

    assert status["data"]["claimability_state"] == WALLET_CLAIMABILITY_STATE_PROOF_AUTHORIZED


def test_wallet_runtime_rejects_noncanonical_persisted_claimability_state() -> None:
    with TestClient(create_app()) as client:
        agent_id = _seed_wallet(client)
        store = client.app.state.public_lifecycle_runtime.wallet_store
        wallet_row = store.get_wallet(agent_id)
        wallet_history = store.get_wallet_history(agent_id)
        assert wallet_row is not None
        assert wallet_history is not None
        wallet_row["claimability_state"] = " proof_claimability_authorized "
        store.put_wallet_and_history(agent_id, wallet_row, wallet_history)

        with pytest.raises(Exception) as exc_info:
            client.app.state.public_wallet_runtime.wallet_status(agent_id=agent_id)

    assert getattr(exc_info.value, "token", None) == "lifecycle_claimability_state_invalid"


def test_phase1575t_genesis_gate_expects_deferred_claimability() -> None:
    source = TOOL_PATH.read_text(encoding="utf-8")

    assert "WALLET_CLAIMABILITY_STATE_DEFERRED" in source
    assert "expected_claimability_state\": WALLET_CLAIMABILITY_STATE_DEFERRED" in source
    assert "WALLET_CLAIMABILITY_STATE_PROOF_AUTHORIZED" not in source
