from dataclasses import FrozenInstanceError, replace

import pytest

from ilc_core.bundle.layer1_genesis_bundle import (
    ADR_0009_LAYER1_NOT_PUBLIC_DISTRIBUTION,
    generate_layer1_genesis_bundle,
    verify_layer1_genesis_bundle,
)


def _fixture_bundle():
    return generate_layer1_genesis_bundle(
        bundle_id="layer1-genesis-private",
        layer0_sha256="a" * 64,
        seed_claims=[
            {"claim_id": "seed-001", "truth_primitive": "assert.truth"},
            {"claim_id": "seed-002", "truth_primitive": "validate.claim"},
        ],
        initial_agent_roster=[
            {"agent_id": "agent-a", "identity_anchor": "anchor-a"},
            {"agent_id": "agent-b", "identity_anchor": "anchor-b"},
        ],
        initial_shard_topology={
            "shards": [{"shard_id": "genesis", "role": "bootstrap"}],
            "version": "v0.1-private",
        },
        genesis_signing_key_refs=[
            {"key_ref": "genesis-key-a", "purpose": "private_fixture"},
        ],
    )


def test_generate_produces_nonempty_fields() -> None:
    bundle = _fixture_bundle()

    assert bundle.bundle_id == "layer1-genesis-private"
    assert bundle.layer0_protocol_bundle_sha256 == "a" * 64
    assert bundle.canonical_json
    assert bundle.sha256
    assert ADR_0009_LAYER1_NOT_PUBLIC_DISTRIBUTION is True


def test_verify_accepts_valid_bundle() -> None:
    assert verify_layer1_genesis_bundle(_fixture_bundle()) is True


def test_verify_rejects_wrong_sha256() -> None:
    bundle = replace(_fixture_bundle(), sha256="b" * 64)

    assert verify_layer1_genesis_bundle(bundle) is False


def test_verify_rejects_missing_layer0_sha256() -> None:
    bundle = replace(_fixture_bundle(), layer0_protocol_bundle_sha256="")

    with pytest.raises(ValueError, match="layer1_genesis_bundle_missing_layer0_sha256"):
        verify_layer1_genesis_bundle(bundle)


def test_verify_rejects_missing_bundle_id() -> None:
    bundle = replace(_fixture_bundle(), bundle_id="")

    with pytest.raises(ValueError, match="layer1_genesis_bundle_missing_bundle_id"):
        verify_layer1_genesis_bundle(bundle)


def test_immutability_frozen_dataclass() -> None:
    bundle = _fixture_bundle()

    with pytest.raises(FrozenInstanceError):
        bundle.bundle_id = "mutated"  # type: ignore[misc]


def test_canonical_json_sort_keys() -> None:
    bundle_a = generate_layer1_genesis_bundle(
        bundle_id="layer1-genesis-private",
        layer0_sha256="a" * 64,
        seed_claims=[
            {"truth_primitive": "assert.truth", "claim_id": "seed-001"},
        ],
        initial_agent_roster=[
            {"identity_anchor": "anchor-a", "agent_id": "agent-a"},
        ],
        initial_shard_topology={"version": "v0.1-private", "shards": []},
        genesis_signing_key_refs=[
            {"purpose": "private_fixture", "key_ref": "genesis-key-a"},
        ],
    )
    bundle_b = generate_layer1_genesis_bundle(
        bundle_id="layer1-genesis-private",
        layer0_sha256="a" * 64,
        seed_claims=[
            {"claim_id": "seed-001", "truth_primitive": "assert.truth"},
        ],
        initial_agent_roster=[
            {"agent_id": "agent-a", "identity_anchor": "anchor-a"},
        ],
        initial_shard_topology={"shards": [], "version": "v0.1-private"},
        genesis_signing_key_refs=[
            {"key_ref": "genesis-key-a", "purpose": "private_fixture"},
        ],
    )

    assert bundle_a.canonical_json == bundle_b.canonical_json
    assert bundle_a.sha256 == bundle_b.sha256


def test_public_rc_exclude_flag() -> None:
    bundle = _fixture_bundle()

    assert bundle.public_rc_exclude is True
