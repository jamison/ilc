"""PUBLIC_RC_EXCLUDE: adr_0009_layer1_private_implementation
PUBLIC_RC_EXCLUDE_REASON: Private ADR-0009 Layer 1 generator/verifier. Does not mutate ADR status or publish protocol bundles.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Mapping

ADR_0009_LAYER1_NOT_PUBLIC_DISTRIBUTION = True


def _reject_float(value: object, token: str) -> None:
    if isinstance(value, float):
        raise ValueError(token)
    if isinstance(value, Mapping):
        for key, nested in value.items():
            _reject_float(key, token)
            _reject_float(nested, token)
        return
    if isinstance(value, (list, tuple)):
        for nested in value:
            _reject_float(nested, token)


def _canonical_json(payload: Mapping[str, object]) -> str:
    _reject_float(payload, "layer1_genesis_bundle_float_not_allowed")
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _normalize_list(rows: list[object] | tuple[object, ...]) -> list[object]:
    _reject_float(rows, "layer1_genesis_bundle_float_not_allowed")
    return [dict(row) if isinstance(row, Mapping) else row for row in rows]


@dataclass(frozen=True)
class Layer1GenesisBundle:
    bundle_id: str
    layer0_protocol_bundle_sha256: str
    seed_claims: list[object]
    initial_agent_roster: list[object]
    initial_shard_topology: dict[str, object]
    genesis_signing_key_refs: list[object]
    canonical_json: str
    sha256: str
    public_rc_exclude: bool = True


def generate_layer1_genesis_bundle(
    *,
    bundle_id: str,
    layer0_sha256: str,
    seed_claims: list[object] | tuple[object, ...],
    initial_agent_roster: list[object] | tuple[object, ...],
    initial_shard_topology: Mapping[str, object],
    genesis_signing_key_refs: list[object] | tuple[object, ...],
) -> Layer1GenesisBundle:
    if bundle_id == "":
        raise ValueError("layer1_genesis_bundle_missing_bundle_id")
    if layer0_sha256 == "":
        raise ValueError("layer1_genesis_bundle_missing_layer0_sha256")

    normalized_seed_claims = _normalize_list(seed_claims)
    normalized_roster = _normalize_list(initial_agent_roster)
    normalized_topology = dict(initial_shard_topology)
    normalized_signing_refs = _normalize_list(genesis_signing_key_refs)

    envelope = {
        "bundle_id": bundle_id,
        "genesis_signing_key_refs": normalized_signing_refs,
        "initial_agent_roster": normalized_roster,
        "initial_shard_topology": normalized_topology,
        "layer": 1,
        "layer0_protocol_bundle_sha256": layer0_sha256,
        "public_rc_exclude": True,
        "seed_claims": normalized_seed_claims,
    }
    canonical_json = _canonical_json(envelope)
    return Layer1GenesisBundle(
        bundle_id=bundle_id,
        layer0_protocol_bundle_sha256=layer0_sha256,
        seed_claims=normalized_seed_claims,
        initial_agent_roster=normalized_roster,
        initial_shard_topology=normalized_topology,
        genesis_signing_key_refs=normalized_signing_refs,
        canonical_json=canonical_json,
        sha256=hashlib.sha256(canonical_json.encode("utf-8")).hexdigest(),
    )


def verify_layer1_genesis_bundle(bundle: Layer1GenesisBundle) -> bool:
    rebuilt = generate_layer1_genesis_bundle(
        bundle_id=bundle.bundle_id,
        layer0_sha256=bundle.layer0_protocol_bundle_sha256,
        seed_claims=bundle.seed_claims,
        initial_agent_roster=bundle.initial_agent_roster,
        initial_shard_topology=bundle.initial_shard_topology,
        genesis_signing_key_refs=bundle.genesis_signing_key_refs,
    )
    return (
        rebuilt.canonical_json == bundle.canonical_json
        and rebuilt.sha256 == bundle.sha256
        and bundle.public_rc_exclude is True
    )


__all__ = [
    "ADR_0009_LAYER1_NOT_PUBLIC_DISTRIBUTION",
    "Layer1GenesisBundle",
    "generate_layer1_genesis_bundle",
    "verify_layer1_genesis_bundle",
]
