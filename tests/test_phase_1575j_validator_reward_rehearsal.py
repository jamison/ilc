from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from tools.phase_1575j_validator_reward_rehearsal import (
    DESTINATION_REGISTRY_SCHEMA_VERSION,
    OUTPUT_TOKENS,
    PHASE,
    REHEARSAL_INPUT_ROWS,
    SCHEMA_VERSION,
    TURN_ON_READY_VERDICT,
    build_validator_destination_registry,
    build_validator_reward_rehearsal_evidence,
    evidence_sha256,
    stable_json,
    verify_validator_reward_rehearsal_evidence,
)


def test_phase_1575j_evidence_schema_and_dependency() -> None:
    evidence = build_validator_reward_rehearsal_evidence()

    assert evidence["schema_version"] == SCHEMA_VERSION
    assert evidence["phase"] == PHASE
    assert evidence["generated_at_source"] == "deterministic_static_phase_1575j"
    assert evidence["dependency_certificates"]["phase_1575i"]["payload_sha256"] == (
        "3ea9b2b54c44e2ca0e729c4eb1767982186ada98bbf30fb0389aa7b2304950f9"
    )


def test_phase_1575j_guard_state_and_non_claims_remain_default_off() -> None:
    evidence = build_validator_reward_rehearsal_evidence()

    assert evidence["guard_state"]["treasury_distribution_not_activated"] is True
    assert "not_activated" in evidence["guard_state"]["treasury_distribution_guard_token"]
    assert "not_activated" in evidence["guard_state"]["validator_reward_distribution_guard_token"]
    assert evidence["non_claims"]
    assert all(value is False for value in evidence["non_claims"].values())


def test_phase_1575j_destination_registry_is_private_and_digest_bound() -> None:
    registry = build_validator_destination_registry()

    assert registry["schema_version"] == DESTINATION_REGISTRY_SCHEMA_VERSION
    assert registry["destination_count"] == 4
    assert len(registry["registry_sha256"]) == 64
    for row in registry["destinations"]:
        assert row["destination_live_wallet_address"] is None
        assert row["destination_binding_scope"] == "private_retained_rehearsal_not_live_wallet"
        assert len(row["validator_agent_id"]) == 96
        assert len(row["destination_binding_sha256"]) == 64


def test_phase_1575j_rehearsal_epochs_use_actual_reward_fraction_and_conserve_destinations() -> None:
    evidence = build_validator_reward_rehearsal_evidence()
    epochs = evidence["rehearsal_epochs"]

    assert len(epochs) == len(REHEARSAL_INPUT_ROWS)
    for epoch in epochs:
        write_fee_burn = Decimal(epoch["inputs"]["write_fee_burn_pool_ilc"])
        expected_pool = write_fee_burn * Decimal("0.02")
        assert Decimal(epoch["validator_reward_pool_ilc"]) == expected_pool
        assert Decimal(epoch["reward_routing_quote"]["validator_reward_pool_ilc"]) == expected_pool
        assert Decimal(epoch["destination_allocation_total_ilc"]) == expected_pool
        assert sum(
            Decimal(allocation["amount_ilc_str"])
            for allocation in epoch["destination_allocations"]
        ) == expected_pool
        assert epoch["production_treasury_distribution_activated"] is False


def test_phase_1575j_settlement_roots_are_canonical_and_self_reference_free() -> None:
    evidence = build_validator_reward_rehearsal_evidence()

    roots = []
    for epoch in evidence["rehearsal_epochs"]:
        root = epoch["settlement_root"]
        root_payload = json.loads(root["canonical_record_json"])
        assert len(root["root_hex"]) == 64
        assert root_payload["event_payloads"]
        assert "settlement_root_hex" not in root["canonical_record_json"]
        assert root_payload["schema_version"] == "treasury_validator_reward_event_batch_root_1540p.v0.1"
        roots.append(root["root_hex"])
    assert len(set(roots)) == len(roots)


def test_phase_1575j_evidence_is_deterministic_and_canonical() -> None:
    first = build_validator_reward_rehearsal_evidence()
    second = build_validator_reward_rehearsal_evidence()

    assert first == second
    assert evidence_sha256(first) == evidence_sha256(second)
    assert stable_json(first) == json.dumps(
        first,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def test_phase_1575j_turn_on_ready_certificate_routes_to_1575k() -> None:
    evidence = build_validator_reward_rehearsal_evidence()
    certificate = evidence["turn_on_ready_certificate"]

    assert certificate["verdict"] == TURN_ON_READY_VERDICT
    assert certificate["requires_later_phase"] == "1575k"
    assert certificate["requires_live_destination_governance"] is True
    assert certificate["requires_replay_tests_before_guard_clearance"] is True
    assert tuple(evidence["output_tokens"]) == OUTPUT_TOKENS


def test_phase_1575j_verifier_rejects_guard_clearance_claim() -> None:
    evidence = build_validator_reward_rehearsal_evidence()
    evidence["guard_state"]["treasury_distribution_not_activated"] = False

    with pytest.raises(ValueError, match="treasury_guard_must_remain_true"):
        verify_validator_reward_rehearsal_evidence(evidence)


def test_phase_1575j_verifier_rejects_wallet_destination() -> None:
    evidence = build_validator_reward_rehearsal_evidence()
    evidence["rehearsal_epochs"][0]["destination_allocations"][0][
        "destination_live_wallet_address"
    ] = "wallet-1"
    evidence["evidence_payload_sha256"] = "0" * 64

    with pytest.raises(ValueError, match="live_wallet_address_must_not_be_set"):
        verify_validator_reward_rehearsal_evidence(evidence)


def test_phase_1575j_verifier_rejects_digest_mismatch() -> None:
    evidence = build_validator_reward_rehearsal_evidence()
    evidence["turn_on_ready_certificate"]["verdict"] = "changed"

    with pytest.raises(ValueError, match="evidence_payload_digest_mismatch"):
        verify_validator_reward_rehearsal_evidence(evidence)


def test_phase_1575j_verifier_rejects_positive_non_claim() -> None:
    evidence = build_validator_reward_rehearsal_evidence()
    evidence["non_claims"]["writes_wallet"] = True

    with pytest.raises(ValueError, match="non_claim_must_be_false:writes_wallet"):
        verify_validator_reward_rehearsal_evidence(evidence)
