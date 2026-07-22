# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.crypto.cose_sign1 import cose_sign1_sign, cose_sign1_verify
from ilc_core.encoding.cidv1 import node_id_from_bytes
from ilc_core.encoding.dag_cbor import encode_dag_cbor
from ilc_core.private_json_guardrails import (
    canonical_json,
    freeze_json_value,
    normalize_json_value,
    reject_float,
    thaw_json_value,
)

ADR_0009_LAYER1_NOT_PUBLIC_DISTRIBUTION = False  # guard cleared Phase 1520p - ADR-0009 accepted


def _reject_float(value: object, token: str) -> None:
    reject_float(value, token)


def _canonical_json(payload: Mapping[str, object]) -> str:
    return canonical_json(payload, float_token="layer1_genesis_bundle_float_not_allowed")


def _normalize_list(rows: list[object] | tuple[object, ...]) -> list[object]:
    _reject_float(rows, "layer1_genesis_bundle_float_not_allowed")
    normalized = normalize_json_value(rows)
    if not isinstance(normalized, list):
        raise ValueError("layer1_genesis_bundle_invalid_list")
    return normalized


@dataclass(frozen=True)
class Layer1GenesisBundle:
    bundle_id: str
    layer0_protocol_bundle_sha256: str
    layer0_protocol_bundle_cidv1: str
    seed_claims: tuple[object, ...]
    initial_agent_roster: tuple[object, ...]
    initial_shard_topology: Mapping[object, object]
    genesis_signing_key_refs: tuple[object, ...]
    canonical_json: str
    dag_cbor: bytes
    cidv1: str
    sha256: str
    cose_sign1: bytes = b""
    public_rc_exclude: bool = True


def _build_layer1_envelope(
    *,
    bundle_id: str,
    layer0_sha256: str,
    layer0_cidv1: str,
    seed_claims: list[object] | tuple[object, ...],
    initial_agent_roster: list[object] | tuple[object, ...],
    initial_shard_topology: Mapping[str, object],
    genesis_signing_key_refs: list[object] | tuple[object, ...],
) -> tuple[
    dict[str, object],
    tuple[object, ...],
    tuple[object, ...],
    Mapping[object, object],
    tuple[object, ...],
]:
    normalized_seed_claims = _normalize_list(seed_claims)
    normalized_roster = _normalize_list(initial_agent_roster)
    _reject_float(initial_shard_topology, "layer1_genesis_bundle_float_not_allowed")
    normalized_topology = normalize_json_value(initial_shard_topology)
    if not isinstance(normalized_topology, dict):
        raise ValueError("layer1_genesis_bundle_invalid_topology")
    normalized_signing_refs = _normalize_list(genesis_signing_key_refs)

    envelope = {
        "bundle_id": bundle_id,
        "genesis_signing_key_refs": normalized_signing_refs,
        "initial_agent_roster": normalized_roster,
        "initial_shard_topology": normalized_topology,
        "layer": 1,
        "layer0_protocol_bundle_cidv1": layer0_cidv1,
        "layer0_protocol_bundle_sha256": layer0_sha256,
        "public_rc_exclude": True,
        "seed_claims": normalized_seed_claims,
    }
    return (
        envelope,
        freeze_json_value(normalized_seed_claims),  # type: ignore[return-value]
        freeze_json_value(normalized_roster),  # type: ignore[return-value]
        freeze_json_value(normalized_topology),  # type: ignore[return-value]
        freeze_json_value(normalized_signing_refs),  # type: ignore[return-value]
    )


def generate_layer1_genesis_bundle(
    *,
    bundle_id: str,
    layer0_sha256: str,
    seed_claims: list[object] | tuple[object, ...],
    initial_agent_roster: list[object] | tuple[object, ...],
    initial_shard_topology: Mapping[str, object],
    genesis_signing_key_refs: list[object] | tuple[object, ...],
    layer0_cidv1: str = "",
    signing_private_key: ed25519.Ed25519PrivateKey | None = None,
    cose_kid: bytes | None = None,
) -> Layer1GenesisBundle:
    if bundle_id == "":
        raise ValueError("layer1_genesis_bundle_missing_bundle_id")
    if layer0_sha256 == "":
        raise ValueError("layer1_genesis_bundle_missing_layer0_sha256")

    (
        envelope,
        frozen_seed_claims,
        frozen_roster,
        frozen_topology,
        frozen_signing_refs,
    ) = _build_layer1_envelope(
        bundle_id=bundle_id,
        layer0_sha256=layer0_sha256,
        layer0_cidv1=layer0_cidv1,
        seed_claims=seed_claims,
        initial_agent_roster=initial_agent_roster,
        initial_shard_topology=initial_shard_topology,
        genesis_signing_key_refs=genesis_signing_key_refs,
    )
    canonical_json = _canonical_json(envelope)
    dag_cbor = encode_dag_cbor(envelope)
    cidv1 = node_id_from_bytes(dag_cbor)
    cose_sign1 = (
        cose_sign1_sign(dag_cbor, signing_private_key, kid=cose_kid)
        if signing_private_key is not None
        else b""
    )
    return Layer1GenesisBundle(
        bundle_id=bundle_id,
        layer0_protocol_bundle_sha256=layer0_sha256,
        layer0_protocol_bundle_cidv1=layer0_cidv1,
        seed_claims=frozen_seed_claims,
        initial_agent_roster=frozen_roster,
        initial_shard_topology=frozen_topology,
        genesis_signing_key_refs=frozen_signing_refs,
        canonical_json=canonical_json,
        dag_cbor=dag_cbor,
        cidv1=cidv1,
        sha256=hashlib.sha256(dag_cbor).hexdigest(),
        cose_sign1=cose_sign1,
    )


def verify_layer1_genesis_bundle(
    bundle: Layer1GenesisBundle,
    *,
    public_key: ed25519.Ed25519PublicKey | None = None,
) -> bool:
    rebuilt = generate_layer1_genesis_bundle(
        bundle_id=bundle.bundle_id,
        layer0_sha256=bundle.layer0_protocol_bundle_sha256,
        layer0_cidv1=bundle.layer0_protocol_bundle_cidv1,
        seed_claims=thaw_json_value(bundle.seed_claims),  # type: ignore[arg-type]
        initial_agent_roster=thaw_json_value(bundle.initial_agent_roster),  # type: ignore[arg-type]
        initial_shard_topology=thaw_json_value(bundle.initial_shard_topology),  # type: ignore[arg-type]
        genesis_signing_key_refs=thaw_json_value(bundle.genesis_signing_key_refs),  # type: ignore[arg-type]
    )
    return (
        rebuilt.canonical_json == bundle.canonical_json
        and rebuilt.dag_cbor == bundle.dag_cbor
        and rebuilt.cidv1 == bundle.cidv1
        and rebuilt.sha256 == bundle.sha256
        and bundle.public_rc_exclude is True
        and _verify_optional_cose(bundle, public_key)
    )


def _verify_optional_cose(
    bundle: Layer1GenesisBundle,
    public_key: ed25519.Ed25519PublicKey | None,
) -> bool:
    if bundle.cose_sign1 == b"":
        return True
    if public_key is None:
        return False
    try:
        verified = cose_sign1_verify(bundle.cose_sign1, public_key)
    except (InvalidSignature, ValueError):
        return False
    return verified["nodeid"] == bundle.cidv1 and verified["payload"] == bundle.dag_cbor


__all__ = [
    "ADR_0009_LAYER1_NOT_PUBLIC_DISTRIBUTION",
    "Layer1GenesisBundle",
    "generate_layer1_genesis_bundle",
    "verify_layer1_genesis_bundle",
]
