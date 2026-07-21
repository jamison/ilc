from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.phase_1575i_treasury_readiness import (
    OUTPUT_TOKENS,
    READINESS_VERDICT,
    SCHEMA_VERSION,
    build_treasury_readiness_certificate,
    certificate_sha256,
    stable_json,
    verify_treasury_readiness_certificate,
)


def test_phase_1575i_certificate_schema_and_verdict() -> None:
    certificate = build_treasury_readiness_certificate()

    assert certificate["schema_version"] == SCHEMA_VERSION
    assert certificate["phase"] == "1575i"
    assert certificate["readiness_verdict"] == READINESS_VERDICT
    assert certificate["generated_at_source"] == "deterministic_static_phase_1575i"


def test_phase_1575i_authorities_are_ratified_and_named() -> None:
    certificate = build_treasury_readiness_certificate()
    authorities = certificate["authorities"]

    assert authorities["treasury_governance"]["cdl"] == "CDL-047"
    assert authorities["treasury_governance"]["status"] == "ratified"
    assert "cdl_047" in authorities["treasury_governance"]["dependency_token"]
    assert authorities["validator_reward_routing"]["cdl"] == "CDL-054"
    assert authorities["validator_reward_routing"]["status"] == "ratified"
    assert "cdl_054" in authorities["validator_reward_routing"]["dependency_token"]


def test_phase_1575i_genesis_fixed_tranche_is_not_treasury_route() -> None:
    certificate = build_treasury_readiness_certificate()
    non_overlap = certificate["genesis_non_overlap"]

    assert non_overlap["genesis_5pct_is_bootstrap_fixed_tranche"] is True
    assert non_overlap["treasury_is_long_term_network_maintenance_lane"] is True
    assert non_overlap["treasury_routes_to_genesis_agent1_by_default"] is False
    assert non_overlap["requires_separate_cdl_to_route_treasury_to_genesis_identity"] is True
    assert certificate["destination_requirements"]["must_not_default_to_genesis_agent1"] is True


def test_phase_1575i_guard_state_is_default_off() -> None:
    certificate = build_treasury_readiness_certificate()
    guards = certificate["guard_state"]

    assert guards["treasury_distribution_not_activated"] is True
    assert guards["genesis_wallet_write_authorized"] is False
    assert guards["genesis_settlement_write_authorized"] is False
    assert guards["genesis_minting_authorized"] is False
    assert "not_activated" in guards["treasury_distribution_guard_token"]


def test_phase_1575i_non_claims_are_all_false() -> None:
    certificate = build_treasury_readiness_certificate()

    assert certificate["non_claims"]
    assert all(value is False for value in certificate["non_claims"].values())
    assert certificate["non_claims"]["writes_wallet"] is False
    assert certificate["non_claims"]["executes_transfer"] is False
    assert certificate["non_claims"]["executes_settlement"] is False
    assert certificate["non_claims"]["clears_treasury_guard"] is False


def test_phase_1575i_source_pools_keep_genesis_excluded() -> None:
    certificate = build_treasury_readiness_certificate()
    pools = {row["name"]: row for row in certificate["source_pools"]}

    assert "fee_revenue" in pools
    assert "transfer_tax_revenue" in pools
    assert "governed_bounty_budget" in pools
    assert pools["genesis_fixed_5pct_tranche"]["status"] == (
        "excluded_from_treasury_default_routes"
    )


def test_phase_1575i_destination_has_no_live_wallet_address() -> None:
    certificate = build_treasury_readiness_certificate()
    destinations = certificate["destination_requirements"]

    assert destinations["treasury_live_wallet_address"] is None
    assert destinations["treasury_destination_class"] == (
        "governance_controlled_account_pending_1575k"
    )


def test_phase_1575i_output_tokens_present() -> None:
    certificate = build_treasury_readiness_certificate()

    assert tuple(certificate["output_tokens"]) == OUTPUT_TOKENS
    assert "treasury_guard_not_cleared_phase_1575i" in certificate["output_tokens"]


def test_phase_1575i_certificate_rejects_guard_clearance_claim() -> None:
    certificate = build_treasury_readiness_certificate()
    certificate["guard_state"]["treasury_distribution_not_activated"] = False

    with pytest.raises(ValueError, match="treasury_guard_must_remain_not_activated"):
        verify_treasury_readiness_certificate(certificate)


def test_phase_1575i_certificate_rejects_wallet_address() -> None:
    certificate = build_treasury_readiness_certificate()
    certificate["destination_requirements"]["treasury_live_wallet_address"] = "wallet-1"

    with pytest.raises(ValueError, match="treasury_live_wallet_address_must_not_be_set"):
        verify_treasury_readiness_certificate(certificate)


def test_phase_1575i_certificate_rejects_positive_non_claim() -> None:
    certificate = build_treasury_readiness_certificate()
    certificate["non_claims"]["executes_transfer"] = True

    with pytest.raises(ValueError, match="non_claim_must_be_false:executes_transfer"):
        verify_treasury_readiness_certificate(certificate)


def test_phase_1575i_stable_json_is_canonical_and_finite(tmp_path: Path) -> None:
    certificate = build_treasury_readiness_certificate()
    rendered = stable_json(certificate)

    assert rendered == json.dumps(
        certificate,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )
    path = tmp_path / "cert.json"
    path.write_text(rendered + "\n", encoding="utf-8")
    assert path.read_text(encoding="utf-8").endswith("\n")


def test_phase_1575i_certificate_sha256_is_deterministic() -> None:
    first = build_treasury_readiness_certificate()
    second = build_treasury_readiness_certificate()

    assert certificate_sha256(first) == certificate_sha256(second)
    assert len(certificate_sha256(first)) == 64

