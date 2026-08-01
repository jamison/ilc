# SPDX-License-Identifier: AGPL-3.0-only
"""Validator gRPC endpoint assertions for graph-bound TLS identity.

Phase 1577b implements the CDL-105 assertion object, but does not activate
bridge enforcement. BLS verification is delegated to a Rust subprocess or an
explicit test verifier; this module intentionally does not implement native
Python BLS.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import subprocess
from dataclasses import dataclass, fields
from typing import Any, Callable, Mapping


VALIDATOR_ENDPOINT_ASSERTION_RUNTIME_VERSION = "validator_endpoint_assertion_phase_1577b.v0.1"
VALIDATOR_ENDPOINT_ASSERTION_NODE_KIND = "validator_grpc_endpoint_assertion"
VALIDATOR_ENDPOINT_ASSERTION_SCHEMA_VERSION = "validator_grpc_endpoint_assertion.v0.1"
VALIDATOR_ENDPOINT_ASSERTION_CANDIDATE_PREFIX = "validator_grpc_endpoint_assertion:"
VALIDATOR_ENDPOINT_ASSERTION_BLS_COMMAND_ENV = "ILC_VALIDATOR_ENDPOINT_ASSERTION_BLS_VERIFY_COMMAND"

_LOWER_HEX_RE = re.compile(r"^[0-9a-f]+$")
_AGENT_OR_BLS_KEY_RE = re.compile(r"^[0-9a-f]{96}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_ISO_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

BlsVerifier = Callable[[bytes, str, str, str], bool]


@dataclass(frozen=True)
class ValidatorEndpointAssertion:
    """CDL-105 validator endpoint assertion record."""

    asserted_at_epoch: int
    bls_public_key_hex: str
    bls_signature_hex: str
    genesis_witness: bool
    grpc_endpoint: str
    node_kind: str
    schema_version: str
    tls_cert_not_after_utc: str | None
    tls_cert_not_before_utc: str
    tls_cert_sha256_fingerprint: str
    validator_agent_id: str
    revised_by: str | None = None

    def __post_init__(self) -> None:
        _require_uint64(self.asserted_at_epoch, "validator_assertion_epoch_invalid_phase_1577b")
        _require_lower_hex_exact(
            self.validator_agent_id,
            96,
            "validator_assertion_agent_id_invalid_phase_1577b",
        )
        _require_lower_hex_exact(
            self.bls_public_key_hex,
            96,
            "validator_assertion_bls_public_key_invalid_phase_1577b",
        )
        _require_lower_even_hex(
            self.bls_signature_hex,
            "validator_assertion_bls_signature_invalid_phase_1577b",
        )
        if not isinstance(self.genesis_witness, bool):
            raise ValueError("validator_assertion_genesis_witness_invalid_phase_1577b")
        _require_endpoint(self.grpc_endpoint)
        if self.node_kind != VALIDATOR_ENDPOINT_ASSERTION_NODE_KIND:
            raise ValueError("validator_assertion_node_kind_invalid_phase_1577b")
        if self.schema_version != VALIDATOR_ENDPOINT_ASSERTION_SCHEMA_VERSION:
            raise ValueError("validator_assertion_schema_version_invalid_phase_1577b")
        _require_iso_utc(self.tls_cert_not_before_utc, "validator_assertion_cert_not_before_invalid_phase_1577b")
        if self.tls_cert_not_after_utc is not None:
            _require_iso_utc(self.tls_cert_not_after_utc, "validator_assertion_cert_not_after_invalid_phase_1577b")
        _require_lower_hex_exact(
            self.tls_cert_sha256_fingerprint,
            64,
            "validator_assertion_cert_fingerprint_invalid_phase_1577b",
        )
        if self.revised_by is not None and (not isinstance(self.revised_by, str) or not self.revised_by):
            raise ValueError("validator_assertion_revised_by_invalid_phase_1577b")

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "ValidatorEndpointAssertion":
        if not isinstance(payload, Mapping):
            raise ValueError("validator_assertion_payload_invalid_phase_1577b")
        values = {field.name: payload.get(field.name) for field in fields(cls)}
        return cls(**values)

    def to_dict(self, *, include_graph_metadata: bool = True) -> dict[str, Any]:
        payload = {
            "asserted_at_epoch": self.asserted_at_epoch,
            "bls_public_key_hex": self.bls_public_key_hex,
            "bls_signature_hex": self.bls_signature_hex,
            "genesis_witness": self.genesis_witness,
            "grpc_endpoint": self.grpc_endpoint,
            "node_kind": self.node_kind,
            "schema_version": self.schema_version,
            "tls_cert_not_after_utc": self.tls_cert_not_after_utc,
            "tls_cert_not_before_utc": self.tls_cert_not_before_utc,
            "tls_cert_sha256_fingerprint": self.tls_cert_sha256_fingerprint,
            "validator_agent_id": self.validator_agent_id,
        }
        if include_graph_metadata and self.revised_by is not None:
            payload["revised_by"] = self.revised_by
        return payload


def canonical_assertion_payload(assertion: ValidatorEndpointAssertion | Mapping[str, Any]) -> bytes:
    normalized = assertion if isinstance(assertion, ValidatorEndpointAssertion) else ValidatorEndpointAssertion.from_dict(assertion)
    payload = normalized.to_dict(include_graph_metadata=False)
    payload.pop("bls_signature_hex")
    payload.pop("genesis_witness")
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def verify_bls_signature(
    assertion: ValidatorEndpointAssertion | Mapping[str, Any],
    *,
    network_id: str,
    verifier: BlsVerifier | None = None,
) -> bool:
    normalized = assertion if isinstance(assertion, ValidatorEndpointAssertion) else ValidatorEndpointAssertion.from_dict(assertion)
    _require_network_id(network_id)
    payload = canonical_assertion_payload(normalized)
    if verifier is not None:
        try:
            return bool(
                verifier(
                    payload,
                    normalized.bls_signature_hex,
                    normalized.bls_public_key_hex,
                    network_id,
                )
            )
        except Exception:
            return False

    command = os.environ.get(VALIDATOR_ENDPOINT_ASSERTION_BLS_COMMAND_ENV)
    if not command:
        return False
    try:
        result = subprocess.run(
            shlex.split(command)
            + [
                "verify",
                "--public-key-hex",
                normalized.bls_public_key_hex,
                "--signature-hex",
                normalized.bls_signature_hex,
                "--network-id",
                network_id,
            ],
            input=payload,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0


def load_from_atlas(atlas_reader: Any, validator_agent_id: str) -> ValidatorEndpointAssertion:
    normalized_agent_id = _require_lower_hex_exact(
        validator_agent_id,
        96,
        "validator_assertion_agent_id_invalid_phase_1577b",
    )
    if atlas_reader is None:
        raise ValueError("validator_cert_assertion_not_found")

    getter = getattr(atlas_reader, "get_validator_endpoint_assertion", None)
    if callable(getter):
        payload = getter(normalized_agent_id)
        if payload is not None:
            return ValidatorEndpointAssertion.from_dict(payload)

    candidate_id = validator_assertion_candidate_id(normalized_agent_id)
    get_node = getattr(atlas_reader, "get_node", None)
    if callable(get_node):
        payload = get_node(candidate_id)
        if payload is not None:
            return ValidatorEndpointAssertion.from_dict(payload)

    if isinstance(atlas_reader, Mapping):
        payload = atlas_reader.get(candidate_id) or atlas_reader.get(normalized_agent_id)
        if payload is not None:
            return ValidatorEndpointAssertion.from_dict(payload)

    iter_nodes = getattr(atlas_reader, "iter_nodes", None)
    if callable(iter_nodes):
        matches = [
            node
            for node in iter_nodes()
            if isinstance(node, Mapping)
            and node.get("node_kind") == VALIDATOR_ENDPOINT_ASSERTION_NODE_KIND
            and node.get("validator_agent_id") == normalized_agent_id
        ]
        if matches:
            return ValidatorEndpointAssertion.from_dict(
                sorted(matches, key=lambda node: int(node.get("asserted_at_epoch", -1)))[-1]
            )

    raise ValueError("validator_cert_assertion_not_found")


def validator_assertion_candidate_id(validator_agent_id: str) -> str:
    normalized = _require_lower_hex_exact(
        validator_agent_id,
        96,
        "validator_assertion_agent_id_invalid_phase_1577b",
    )
    return f"{VALIDATOR_ENDPOINT_ASSERTION_CANDIDATE_PREFIX}{normalized}"


def assertion_to_atlas_node(assertion: ValidatorEndpointAssertion) -> dict[str, Any]:
    payload = assertion.to_dict()
    payload["candidate_id"] = validator_assertion_candidate_id(assertion.validator_agent_id)
    payload["content_sha256"] = hashlib.sha256(canonical_assertion_payload(assertion)).hexdigest()
    payload["tier"] = "support"
    payload["source_phase"] = "1577b"
    return payload


def _require_uint64(value: Any, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0 or value > 2**64 - 1:
        raise ValueError(token)
    return value


def _require_lower_hex_exact(value: Any, length: int, token: str) -> str:
    if not isinstance(value, str) or len(value) != length or not _LOWER_HEX_RE.fullmatch(value):
        raise ValueError(token)
    return value


def _require_lower_even_hex(value: Any, token: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) == 0
        or len(value) % 2 != 0
        or not _LOWER_HEX_RE.fullmatch(value)
    ):
        raise ValueError(token)
    return value


def _require_endpoint(value: Any) -> str:
    if not isinstance(value, str) or not value or any(char.isspace() for char in value):
        raise ValueError("validator_assertion_grpc_endpoint_invalid_phase_1577b")
    host, sep, port_text = value.rpartition(":")
    if not sep or not host or not port_text:
        raise ValueError("validator_assertion_grpc_endpoint_invalid_phase_1577b")
    try:
        port = int(port_text, 10)
    except ValueError as exc:
        raise ValueError("validator_assertion_grpc_endpoint_invalid_phase_1577b") from exc
    if port < 1 or port > 65535:
        raise ValueError("validator_assertion_grpc_endpoint_invalid_phase_1577b")
    if "://" in value or "/" in host:
        raise ValueError("validator_assertion_grpc_endpoint_invalid_phase_1577b")
    return value


def _require_iso_utc(value: Any, token: str) -> str:
    if not isinstance(value, str) or not _ISO_UTC_RE.fullmatch(value):
        raise ValueError(token)
    return value


def _require_network_id(value: Any) -> str:
    if not isinstance(value, str) or not value or any(char.isspace() for char in value):
        raise ValueError("validator_assertion_network_id_invalid_phase_1577b")
    return value


__all__ = [
    "BlsVerifier",
    "VALIDATOR_ENDPOINT_ASSERTION_BLS_COMMAND_ENV",
    "VALIDATOR_ENDPOINT_ASSERTION_CANDIDATE_PREFIX",
    "VALIDATOR_ENDPOINT_ASSERTION_NODE_KIND",
    "VALIDATOR_ENDPOINT_ASSERTION_RUNTIME_VERSION",
    "VALIDATOR_ENDPOINT_ASSERTION_SCHEMA_VERSION",
    "ValidatorEndpointAssertion",
    "assertion_to_atlas_node",
    "canonical_assertion_payload",
    "load_from_atlas",
    "validator_assertion_candidate_id",
    "verify_bls_signature",
]
