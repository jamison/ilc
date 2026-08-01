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
from datetime import datetime, timezone
from typing import Any, Callable, Mapping


VALIDATOR_ENDPOINT_ASSERTION_RUNTIME_VERSION = "validator_endpoint_assertion_phase_1577b.v0.1"
VALIDATOR_ENDPOINT_ASSERTION_NODE_KIND = "validator_grpc_endpoint_assertion"
VALIDATOR_ENDPOINT_ASSERTION_SCHEMA_VERSION = "validator_grpc_endpoint_assertion.v0.1"
VALIDATOR_ENDPOINT_ASSERTION_CANDIDATE_PREFIX = "validator_grpc_endpoint_assertion:"
VALIDATOR_ENDPOINT_ASSERTION_BLS_COMMAND_ENV = "ILC_VALIDATOR_ENDPOINT_ASSERTION_BLS_VERIFY_COMMAND"
VALIDATOR_ENDPOINT_ASSERTION_BLS_DST_PREFIX = "ILC_VALIDATOR_ENDPOINT_ASSERTION_V1"
MAX_ASSERTION_ATLAS_SCAN_NODES = 10_000

_LOWER_HEX_RE = re.compile(r"^[0-9a-f]+$")
_AGENT_OR_BLS_KEY_RE = re.compile(r"^[0-9a-f]{96}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_ISO_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_ATLAS_METADATA_FIELDS = frozenset(
    {"candidate_id", "content_sha256", "source_phase", "tier"}
)
_SUPERCESSION_FORWARD_EDGE_TYPES = frozenset({"revised_by", "superseded_by"})
_SUPERCESSION_REVERSE_EDGE_TYPES = frozenset({"revision", "replaces", "supersedes"})

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
        _require_lower_hex_exact(
            self.bls_signature_hex,
            192,
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
        allowed = {field.name for field in fields(cls)} | _ATLAS_METADATA_FIELDS
        if set(payload).difference(allowed):
            raise ValueError("validator_assertion_unknown_field_phase_1577b_fix1")
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
        matches: list[ValidatorEndpointAssertion] = []
        for index, node in enumerate(iter_nodes(), start=1):
            if index > MAX_ASSERTION_ATLAS_SCAN_NODES:
                raise ValueError(
                    "validator_cert_assertion_scan_limit_exceeded_phase_1577b_fix1"
                )
            if (
                isinstance(node, Mapping)
                and node.get("node_kind") == VALIDATOR_ENDPOINT_ASSERTION_NODE_KIND
                and node.get("validator_agent_id") == normalized_agent_id
            ):
                matches.append(ValidatorEndpointAssertion.from_dict(node))
        if matches:
            return sorted(matches, key=lambda assertion: assertion.asserted_at_epoch)[-1]

    raise ValueError("validator_cert_assertion_not_found")


def assertion_is_superseded(atlas_reader: Any, assertion: ValidatorEndpointAssertion) -> bool:
    """Return true when an inline marker or Atlas revision edge supersedes an assertion."""

    if assertion.revised_by is not None:
        return True

    candidate_id = validator_assertion_candidate_id(assertion.validator_agent_id)
    iter_edges = getattr(atlas_reader, "iter_edges", None)
    if not callable(iter_edges):
        return False

    for index, edge in enumerate(iter_edges(), start=1):
        if index > MAX_ASSERTION_ATLAS_SCAN_NODES:
            raise ValueError(
                "validator_cert_assertion_edge_scan_limit_exceeded_phase_1577b_fix1"
            )
        if isinstance(edge, Mapping) and _edge_supersedes_assertion(edge, candidate_id):
            return True
    return False


def assertion_valid_at(
    assertion: ValidatorEndpointAssertion,
    *,
    now_utc: datetime | None = None,
) -> bool:
    """Validate the assertion certificate validity window at a UTC instant."""

    if now_utc is None:
        raise ValueError("validator_assertion_now_utc_required_phase_1577b_fix1")
    now = now_utc
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("validator_assertion_now_utc_invalid_phase_1577b_fix1")
    normalized_now = now.astimezone(timezone.utc)
    not_before = _parse_iso_utc(
        assertion.tls_cert_not_before_utc,
        "validator_cert_assertion_not_yet_valid",
    )
    if normalized_now < not_before:
        raise ValueError("validator_cert_assertion_not_yet_valid")
    if assertion.tls_cert_not_after_utc is not None:
        not_after = _parse_iso_utc(
            assertion.tls_cert_not_after_utc,
            "validator_cert_assertion_expired",
        )
        if normalized_now > not_after:
            raise ValueError("validator_cert_assertion_expired")
    return True


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


def _parse_iso_utc(value: str, token: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )
    except ValueError as exc:
        raise ValueError(token) from exc


def _edge_supersedes_assertion(edge: Mapping[str, Any], candidate_id: str) -> bool:
    edge_type = str(edge.get("edge_type") or edge.get("type") or "").lower()
    source = (
        edge.get("source_candidate_id")
        or edge.get("source")
        or edge.get("from")
        or edge.get("old_candidate_id")
    )
    target = (
        edge.get("target_candidate_id")
        or edge.get("target")
        or edge.get("to")
        or edge.get("new_candidate_id")
    )
    if edge_type in _SUPERCESSION_FORWARD_EDGE_TYPES and source == candidate_id:
        return True
    if edge_type in _SUPERCESSION_REVERSE_EDGE_TYPES and target == candidate_id:
        return True
    if edge_type == "revision" and (source == candidate_id or target == candidate_id):
        return True
    return False


def _require_network_id(value: Any) -> str:
    if not isinstance(value, str) or not value or any(char.isspace() for char in value):
        raise ValueError("validator_assertion_network_id_invalid_phase_1577b")
    return value


__all__ = [
    "BlsVerifier",
    "VALIDATOR_ENDPOINT_ASSERTION_BLS_COMMAND_ENV",
    "VALIDATOR_ENDPOINT_ASSERTION_BLS_DST_PREFIX",
    "VALIDATOR_ENDPOINT_ASSERTION_CANDIDATE_PREFIX",
    "VALIDATOR_ENDPOINT_ASSERTION_NODE_KIND",
    "VALIDATOR_ENDPOINT_ASSERTION_RUNTIME_VERSION",
    "VALIDATOR_ENDPOINT_ASSERTION_SCHEMA_VERSION",
    "ValidatorEndpointAssertion",
    "assertion_is_superseded",
    "assertion_to_atlas_node",
    "assertion_valid_at",
    "canonical_assertion_payload",
    "load_from_atlas",
    "validator_assertion_candidate_id",
    "verify_bls_signature",
]
