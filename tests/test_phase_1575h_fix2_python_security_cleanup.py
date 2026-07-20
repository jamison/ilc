from __future__ import annotations

import inspect
from decimal import Decimal

import pytest

from ilc_core.agent import _agent_coerce_decimal
from ilc_core.consensus.engine import _engine_coerce_decimal
from ilc_core.consensus.governance import _to_decimal
from ilc_core.economics.epoch_attribution_settle_runtime import (
    AttributionEvent,
    evaluate_ejected_stake_vote,
    settle_attribution_batch,
)
from ilc_core.identity.agent_id_runtime import (
    AGENT_ID_V2_DISTINCT_DOMAIN_MIGRATION_DEFERRED_TOKEN,
    derive_agent_id_v2,
)
from ilc_core.identity.sybil_resistance_runtime import _score
from ilc_core.ledger.ecu_active_layer_runtime import EcuActiveLayerRuntime
from ilc_core.ledger.ecu_ilc_lifecycle_runtime import (
    EcuIlcLifecycleRuntime,
    EcuIlcLifecycleRuntimeError,
    _stable_digest,
)
from ilc_core.network.d2d import routing_reputation_runtime
from ilc_core.network.d2d.gossip_transport import (
    MAX_GOSSIP_BODY_BYTES,
    validate_gossip_body_size,
)
from ilc_core.storage.lmdb_public_runtime import LmdbWalletStore
from ilc_core.types import EdgeType, EpochAttributionBatch


def _coauth_batch() -> EpochAttributionBatch:
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(
        AttributionEvent(
            edge_type=EdgeType.CO_AUTHORSHIP,
            target_creator_id="unused",
            star_node_id="star:one",
            epoch=1,
        )
    )
    batch.seal()
    return batch


def test_epoch_attribution_batch_requires_seal_and_freezes_events() -> None:
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(
        AttributionEvent(
            edge_type=EdgeType.REUSE,
            target_creator_id="agent-a",
            star_node_id=None,
            epoch=1,
        )
    )

    with pytest.raises(ValueError, match="epoch_attribution_batch_must_be_sealed"):
        settle_attribution_batch(batch, stake_map={})
    with pytest.raises(ValueError, match="epoch_attribution_batch_must_be_sealed"):
        batch.settle(stake_map={})

    batch.seal()
    assert isinstance(batch.events, tuple)
    with pytest.raises(ValueError, match="epoch_attribution_batch_sealed_no_new_events"):
        batch.add_event(
            AttributionEvent(
                edge_type=EdgeType.REUSE,
                target_creator_id="agent-b",
                star_node_id=None,
                epoch=1,
            )
        )


def test_member_id_validation_rejects_empty_coauthor_and_distribution_members() -> None:
    with pytest.raises(ValueError, match="stake_map_member_id_must_be_non_empty_string"):
        settle_attribution_batch(
            _coauth_batch(),
            stake_map={"star:one": {"": Decimal("1")}},
        )

    with pytest.raises(ValueError, match="stake_map_member_id_must_be_non_empty_string"):
        evaluate_ejected_stake_vote(
            Decimal("1"),
            {"": Decimal("1")},
            approve_votes=1,
            participating_voters=1,
        )


def test_subquantum_ejected_stake_distribution_filters_zero_payouts() -> None:
    approved, payouts = evaluate_ejected_stake_vote(
        Decimal("0.0000000001"),
        {"agent-a": Decimal("1"), "agent-b": Decimal("1")},
        approve_votes=2,
        participating_voters=2,
    )

    assert approved is True
    assert payouts == []


def test_lifecycle_digest_rejects_raw_decimal_and_agent_id_empty(tmp_path) -> None:
    with pytest.raises(EcuIlcLifecycleRuntimeError) as exc_info:
        _stable_digest({"balance_after_ilc": Decimal("1")})
    assert exc_info.value.token == "lifecycle_stable_digest_decimal_unencoded"

    runtime = EcuIlcLifecycleRuntime(
        wallet_store=LmdbWalletStore(tmp_path / "wallet.lmdb"),
        ecu_runtime=EcuActiveLayerRuntime(),
    )
    with pytest.raises(EcuIlcLifecycleRuntimeError) as agent_exc:
        runtime.commit_settled_epoch(
            agent_id="",
            epoch_id="epoch-1",
            reward_delta_ilc="1",
        )
    assert agent_exc.value.token == "agent_id_required"


def test_float_rejection_is_explicit_across_python_economic_surfaces() -> None:
    with pytest.raises(ValueError, match="accrued_ecu_float_input_rejected"):
        EcuActiveLayerRuntime().set_accrued_ecu("agent-a", 1.0)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="agent_wallet_balance_invalid"):
        _agent_coerce_decimal(1.0, "agent_wallet_balance_invalid")
    with pytest.raises(ValueError, match="engine_reward_invalid"):
        _engine_coerce_decimal(1.0, "engine_reward_invalid")
    with pytest.raises(ValueError, match="governance_price_max_invalid"):
        _to_decimal(1.0, "governance_price_max_invalid")


def test_gossip_body_has_explicit_transport_cap() -> None:
    assert validate_gossip_body_size(b"x" * MAX_GOSSIP_BODY_BYTES) == MAX_GOSSIP_BODY_BYTES
    with pytest.raises(ValueError, match="gossip_body_too_large"):
        validate_gossip_body_size(b"x" * (MAX_GOSSIP_BODY_BYTES + 1))
    with pytest.raises(ValueError, match="gossip_body_must_be_bytes"):
        validate_gossip_body_size("not-bytes")  # type: ignore[arg-type]


def test_routing_reputation_has_no_wall_clock_settlement_input() -> None:
    source = inspect.getsource(routing_reputation_runtime)
    assert "import time" not in source
    assert "time.time(" not in source
    assert routing_reputation_runtime.ROUTING_REPUTATION_NO_SETTLEMENT_TOKEN == (
        "routing_reputation_wall_clock_not_settlement_input_phase_1575h_fix2"
    )


def test_sybil_scores_are_documented_advisory_not_consensus_weights() -> None:
    assert isinstance(_score(Decimal("0.5")), float)
    assert "not a consensus or settlement weight" in (_score.__doc__ or "")


def test_agent_id_distinct_v2_domain_is_deferred_not_silent_migration() -> None:
    seed = b"\x00" * 32
    assert derive_agent_id_v2(seed) == (
        "c9a63b2834721af699ccc4d93074f9b50c10439945431f7a"
        "d59d380407001a27863fcfe4cb034dcde3287cbf82928197"
    )
    assert AGENT_ID_V2_DISTINCT_DOMAIN_MIGRATION_DEFERRED_TOKEN == (
        "agent_id_v2_distinct_domain_migration_deferred_pending_identity_cdl"
    )
