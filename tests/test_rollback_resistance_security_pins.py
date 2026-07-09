from __future__ import annotations

from pathlib import Path

import pytest

from ilc_core.security.rollback_resistance_runtime import (
    CLAWBACK_REQUIRED,
    FINALIZATION_STATE_ROLLED_BACK,
    RollbackResistanceRuntime,
)
from ilc_core.security.signer_lineage_runtime import SignerLineageRegistry


REPO_ROOT = Path(__file__).resolve().parents[1]


def _registry() -> SignerLineageRegistry:
    registry = SignerLineageRegistry()
    registry.register(
        lineage_id="lineage-alpha",
        canonical_root_key="root-001",
        authority_recovery_key="recovery-001",
        operational_signer_key="ops-001",
        authorizer_signer_id="root-001",
        reason_code="genesis_register",
        event_ts="2026-02-20T00:00:00Z",
    )
    return registry


def _payload(**overrides: str) -> dict[str, str]:
    payload = {
        "supersession_id": "sup-001",
        "target_window_id": "epoch-window-42",
        "finalization_state": FINALIZATION_STATE_ROLLED_BACK,
        "clawback_policy": CLAWBACK_REQUIRED,
        "canonical_root_key": "root-001",
        "authorizing_lineage_id": "lineage-alpha",
        "authorizing_signer_id": "ops-001",
        "reason_code": "rollback_reorg_detected",
        "event_ts": "2026-02-20T00:30:00Z",
    }
    payload.update(overrides)
    return payload


def test_rollback_runtime_not_imported_by_public_server_surface() -> None:
    server_source = (REPO_ROOT / "ilc_core/server.py").read_text(encoding="utf-8")
    d2d_sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (REPO_ROOT / "ilc_core/network/d2d").glob("*.py")
    )

    assert "rollback_resistance_runtime" not in server_source
    assert "RollbackResistanceRuntime" not in server_source
    assert "rollback_resistance_runtime" not in d2d_sources
    assert "RollbackResistanceRuntime" not in d2d_sources


def test_same_process_replay_rejected_but_fresh_runtime_forgets_prior_event() -> None:
    registry = _registry()
    runtime_one = RollbackResistanceRuntime(registry)
    event_one = runtime_one.build_event_from_mapping(_payload())

    runtime_one.apply_supersession_event(event_one)
    with pytest.raises(ValueError, match="replayed_supersession_identifier"):
        runtime_one.apply_supersession_event(event_one)

    runtime_two = RollbackResistanceRuntime(registry)
    event_two = runtime_two.build_event_from_mapping(_payload())
    runtime_two.apply_supersession_event(event_two)

    assert len(runtime_two.events) == 1
    assert runtime_two.events[0].supersession_id == "sup-001"


def test_rollback_runtime_records_durable_replay_store_activation_prerequisite() -> None:
    source = (REPO_ROOT / "ilc_core/security/rollback_resistance_runtime.py").read_text(
        encoding="utf-8"
    )

    assert "phase_1573am_activation_prerequisite_durable_replay_store" in source
    assert "process-local dictionaries" in source


def test_phase_1573am_status_records_rollback_review_token() -> None:
    status = (REPO_ROOT / "docs/phases/STATUS.md").read_text(encoding="utf-8")

    assert "rollback_resistance_replay_protection_reviewed_phase_1573am" in status
