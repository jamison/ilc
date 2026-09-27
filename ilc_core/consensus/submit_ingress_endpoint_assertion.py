# SPDX-License-Identifier: AGPL-3.0-only
"""Public submit ingress endpoint assertions for CDL-117.

Pre-signer-binding advisory trust:
Before signer binding activates, serving_agent_id is self-declared by the
submitter. BLS signature verification here proves transport key control and
payload integrity only; it does NOT prove cryptographic ownership of the
declared serving_agent_id. Phase 1578d explicitly deferred signer binding to a
future SignerBinding activation CDL or SignatureSchemeRegistry CDL.
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


PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NOT_ACTIVATED = True
# CDL-117 IS ratified (commit 4d4e54e43). This guard is a downstream activation
# gate for consumers that need to check CDL ratification status before using the
# ingress surface. It is NOT a factual claim that CDL-117 is unratified.
PUBLIC_RC_NATIVE_SUBMIT_INGRESS_CDL_NOT_RATIFIED = True

PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_RUNTIME_VERSION = (
    "public_submit_ingress_endpoint_assertion_IMPL_00.v0.1"
)
PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NODE_KIND = (
    "public_submit_ingress_endpoint_assertion"
)
PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_SCHEMA_VERSION = (
    "public_submit_ingress_endpoint_assertion.v0.1"
)
PUBLIC_SUBMIT_INGRESS_ENDPOINT_REVOCATION_NODE_KIND = (
    "public_submit_ingress_endpoint_revocation"
)
PUBLIC_SUBMIT_INGRESS_ENDPOINT_REVOCATION_SCHEMA_VERSION = (
    "public_submit_ingress_endpoint_revocation.v0.1"
)
PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_CANDIDATE_PREFIX = (
    "public_submit_ingress_endpoint_assertion:"
)
PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_BLS_COMMAND_ENV = (
    "ILC_PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_BLS_VERIFY_COMMAND"
)
PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_BLS_DST_PREFIX = (
    "ILC_PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_V1"
)
PUBLIC_SUBMIT_INGRESS_ENDPOINT_REVOCATION_BLS_DST_PREFIX = (
    "ILC_PUBLIC_SUBMIT_INGRESS_ENDPOINT_REVOCATION_V1"
)
MAX_SUBMIT_INGRESS_ASSERTION_ATLAS_SCAN_NODES = 10_000

_LOWER_HEX_RE = re.compile(r"^[0-9a-f]+$")
_AGENT_OR_BLS_KEY_RE = re.compile(r"^[0-9a-f]{96}$")
_BLS_SIGNATURE_RE = re.compile(r"^[0-9a-f]{192}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_ATLAS_METADATA_FIELDS = frozenset(
    {"candidate_id", "content_sha256", "source_phase", "tier"}
)
_SUPERSESSION_FORWARD_EDGE_TYPES = frozenset({"revised_by", "superseded_by"})
_SUPERSESSION_REVERSE_EDGE_TYPES = frozenset({"revision", "replaces", "supersedes"})

BlsVerifier = Callable[[bytes, str, str, str], bool]


@dataclass(frozen=True)
class PublicSubmitIngressEndpointAssertion:
    """CDL-117 public submit ingress endpoint assertion record."""

    node_kind: str
    schema_version: str
    network_id: str
    service_kind: str
    serving_agent_id: str
    transport_key_kind: str
    transport_public_key_hex: str
    transport_key_scope: str
    endpoint_uri_hint: str
    tls_cert_sha256_fingerprint: str
    valid_from_epoch: int
    valid_until_epoch: int
    revocation_policy: Mapping[str, Any]
    asserted_at_epoch: int
    signing_dst: str
    bls_public_key_hex: str
    bls_signature_hex: str
    revised_by: str | None = None

    def __post_init__(self) -> None:
        if self.node_kind != PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NODE_KIND:
            raise ValueError("submit_ingress_assertion_node_kind_invalid_IMPL_00")
        if self.schema_version != PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_SCHEMA_VERSION:
            raise ValueError("submit_ingress_assertion_schema_version_invalid_IMPL_00")
        _require_non_empty_no_space(
            self.network_id,
            "submit_ingress_assertion_network_id_invalid_IMPL_00",
        )
        if self.service_kind != "public_submit_ingress":
            raise ValueError("submit_ingress_assertion_service_kind_invalid_IMPL_00")
        _require_lower_hex_exact(
            self.serving_agent_id,
            96,
            "submit_ingress_assertion_serving_agent_id_invalid_IMPL_00",
        )
        if self.transport_key_kind != "purpose_scoped_public_submit_ingress":
            raise ValueError("submit_ingress_assertion_transport_key_kind_invalid_IMPL_00")
        _require_lower_hex_exact(
            self.transport_public_key_hex,
            96,
            "submit_ingress_assertion_transport_public_key_invalid_IMPL_00",
        )
        if self.transport_key_scope != "public_submit_ingress":
            raise ValueError("submit_ingress_assertion_transport_key_scope_invalid_IMPL_00")
        _require_non_empty_no_space(
            self.endpoint_uri_hint,
            "submit_ingress_assertion_endpoint_uri_hint_invalid_IMPL_00",
        )
        _require_lower_hex_exact(
            self.tls_cert_sha256_fingerprint,
            64,
            "submit_ingress_assertion_tls_fingerprint_invalid_IMPL_00",
        )
        _require_uint64(
            self.valid_from_epoch,
            "submit_ingress_assertion_valid_from_epoch_invalid_IMPL_00",
        )
        _require_uint64(
            self.valid_until_epoch,
            "submit_ingress_assertion_valid_until_epoch_invalid_IMPL_00",
        )
        if self.valid_until_epoch != 0 and self.valid_until_epoch < self.valid_from_epoch:
            raise ValueError("submit_ingress_assertion_valid_until_before_from_IMPL_00")
        _require_revocation_policy(self.revocation_policy)
        _require_uint64(
            self.asserted_at_epoch,
            "submit_ingress_assertion_asserted_at_epoch_invalid_IMPL_00",
        )
        expected_dst = f"{PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_BLS_DST_PREFIX}:{self.network_id}"
        if self.signing_dst != expected_dst:
            raise ValueError("submit_ingress_assertion_signing_dst_invalid_IMPL_00")
        _require_lower_hex_exact(
            self.bls_public_key_hex,
            96,
            "submit_ingress_assertion_bls_public_key_invalid_IMPL_00",
        )
        _require_lower_hex_exact(
            self.bls_signature_hex,
            192,
            "submit_ingress_assertion_bls_signature_invalid_IMPL_00",
        )
        if self.revised_by is not None and (
            not isinstance(self.revised_by, str) or not self.revised_by
        ):
            raise ValueError("submit_ingress_assertion_revised_by_invalid_IMPL_00")

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "PublicSubmitIngressEndpointAssertion":
        if not isinstance(payload, Mapping):
            raise ValueError("submit_ingress_assertion_payload_invalid_IMPL_00")
        allowed = {field.name for field in fields(cls)} | _ATLAS_METADATA_FIELDS
        if set(payload).difference(allowed):
            raise ValueError("submit_ingress_assertion_unknown_field_IMPL_00")
        values = {field.name: payload.get(field.name) for field in fields(cls)}
        return cls(**values)

    def to_dict(self, *, include_graph_metadata: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "node_kind": self.node_kind,
            "schema_version": self.schema_version,
            "network_id": self.network_id,
            "service_kind": self.service_kind,
            "serving_agent_id": self.serving_agent_id,
            "transport_key_kind": self.transport_key_kind,
            "transport_public_key_hex": self.transport_public_key_hex,
            "transport_key_scope": self.transport_key_scope,
            "endpoint_uri_hint": self.endpoint_uri_hint,
            "tls_cert_sha256_fingerprint": self.tls_cert_sha256_fingerprint,
            "valid_from_epoch": self.valid_from_epoch,
            "valid_until_epoch": self.valid_until_epoch,
            "revocation_policy": dict(self.revocation_policy),
            "asserted_at_epoch": self.asserted_at_epoch,
            "signing_dst": self.signing_dst,
            "bls_public_key_hex": self.bls_public_key_hex,
            "bls_signature_hex": self.bls_signature_hex,
        }
        if include_graph_metadata and self.revised_by is not None:
            payload["revised_by"] = self.revised_by
        return payload


@dataclass(frozen=True)
class PublicSubmitIngressEndpointRevocation:
    """Minimal schema for public_submit_ingress_endpoint_revocation records.

    INV-D blocking obligation from CDL-117: this record kind must have defined
    required fields before PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NOT_ACTIVATED
    can be cleared. Richer revocation policy is deferred to a future CDL after
    operational experience.
    """

    node_kind: str
    schema_version: str
    network_id: str
    revoked_assertion_sha256: str
    serving_agent_id: str
    revoked_at_epoch: int
    revocation_reason: str
    supersession_required: bool
    bls_public_key_hex: str
    bls_signature_hex: str
    revised_by: str | None = None

    def __post_init__(self) -> None:
        if self.node_kind != PUBLIC_SUBMIT_INGRESS_ENDPOINT_REVOCATION_NODE_KIND:
            raise ValueError("submit_ingress_revocation_node_kind_invalid_IMPL_00")
        if self.schema_version != PUBLIC_SUBMIT_INGRESS_ENDPOINT_REVOCATION_SCHEMA_VERSION:
            raise ValueError("submit_ingress_revocation_schema_version_invalid_IMPL_00")
        _require_non_empty_no_space(
            self.network_id,
            "submit_ingress_revocation_network_id_invalid_IMPL_00",
        )
        _require_lower_hex_exact(
            self.revoked_assertion_sha256,
            64,
            "submit_ingress_revocation_assertion_sha256_invalid_IMPL_00",
        )
        _require_lower_hex_exact(
            self.serving_agent_id,
            96,
            "submit_ingress_revocation_serving_agent_id_invalid_IMPL_00",
        )
        _require_uint64(
            self.revoked_at_epoch,
            "submit_ingress_revocation_revoked_at_epoch_invalid_IMPL_00",
        )
        _require_non_empty_str(
            self.revocation_reason,
            "submit_ingress_revocation_reason_invalid_IMPL_00",
        )
        if self.supersession_required is not True:
            raise ValueError("submit_ingress_revocation_supersession_required_invalid_IMPL_00")
        _require_lower_hex_exact(
            self.bls_public_key_hex,
            96,
            "submit_ingress_revocation_bls_public_key_invalid_IMPL_00",
        )
        _require_lower_hex_exact(
            self.bls_signature_hex,
            192,
            "submit_ingress_revocation_bls_signature_invalid_IMPL_00",
        )
        if self.revised_by is not None and (
            not isinstance(self.revised_by, str) or not self.revised_by
        ):
            raise ValueError("submit_ingress_revocation_revised_by_invalid_IMPL_00")

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "PublicSubmitIngressEndpointRevocation":
        if not isinstance(payload, Mapping):
            raise ValueError("submit_ingress_revocation_payload_invalid_IMPL_00")
        allowed = {field.name for field in fields(cls)} | _ATLAS_METADATA_FIELDS
        if set(payload).difference(allowed):
            raise ValueError("submit_ingress_revocation_unknown_field_IMPL_00")
        values = {field.name: payload.get(field.name) for field in fields(cls)}
        return cls(**values)

    def to_dict(self, *, include_graph_metadata: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "node_kind": self.node_kind,
            "schema_version": self.schema_version,
            "network_id": self.network_id,
            "revoked_assertion_sha256": self.revoked_assertion_sha256,
            "serving_agent_id": self.serving_agent_id,
            "revoked_at_epoch": self.revoked_at_epoch,
            "revocation_reason": self.revocation_reason,
            "supersession_required": self.supersession_required,
            "bls_public_key_hex": self.bls_public_key_hex,
            "bls_signature_hex": self.bls_signature_hex,
        }
        if include_graph_metadata and self.revised_by is not None:
            payload["revised_by"] = self.revised_by
        return payload


def parse_endpoint_assertion(
    record: Mapping[str, Any],
) -> PublicSubmitIngressEndpointAssertion:
    """Parse CDL-117 endpoint assertion records.

    Pre-signer-binding advisory trust: before signer binding activates,
    serving_agent_id is self-declared. BLS signature proves transport key
    control and payload integrity only; it does NOT prove cryptographic
    ownership of serving_agent_id. Phase 1578d deferred signer binding to a
    future SignerBinding activation CDL or SignatureSchemeRegistry CDL.
    """

    return PublicSubmitIngressEndpointAssertion.from_dict(record)


def parse_endpoint_revocation(
    record: Mapping[str, Any],
) -> PublicSubmitIngressEndpointRevocation:
    """Parse the minimal CDL-117 endpoint revocation schema."""

    return PublicSubmitIngressEndpointRevocation.from_dict(record)


def canonical_endpoint_assertion_payload(
    assertion: PublicSubmitIngressEndpointAssertion | Mapping[str, Any],
) -> bytes:
    normalized = (
        assertion
        if isinstance(assertion, PublicSubmitIngressEndpointAssertion)
        else PublicSubmitIngressEndpointAssertion.from_dict(assertion)
    )
    payload = normalized.to_dict(include_graph_metadata=False)
    payload.pop("bls_signature_hex")
    return _canonical_json_bytes(payload)


def canonical_revocation_payload(
    revocation: PublicSubmitIngressEndpointRevocation | Mapping[str, Any],
) -> bytes:
    normalized = (
        revocation
        if isinstance(revocation, PublicSubmitIngressEndpointRevocation)
        else PublicSubmitIngressEndpointRevocation.from_dict(revocation)
    )
    payload = normalized.to_dict(include_graph_metadata=False)
    payload.pop("bls_signature_hex")
    return _canonical_json_bytes(payload)


# REVOCATION_BLS_VERIFY_NOT_ACTIVATED: BLS signature verification over revocation records
# is deferred to the guard-clearance phase. parse_endpoint_revocation validates schema only.


def verify_endpoint_assertion_bls_signature(
    assertion: PublicSubmitIngressEndpointAssertion | Mapping[str, Any],
    *,
    verifier: BlsVerifier | None = None,
) -> bool:
    normalized = (
        assertion
        if isinstance(assertion, PublicSubmitIngressEndpointAssertion)
        else PublicSubmitIngressEndpointAssertion.from_dict(assertion)
    )
    payload = canonical_endpoint_assertion_payload(normalized)
    network_id = _require_non_empty_no_space(
        normalized.network_id,
        "submit_ingress_assertion_network_id_invalid_IMPL_00",
    )
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

    command = os.environ.get(PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_BLS_COMMAND_ENV)
    if not command:
        raise ValueError("submit_ingress_assertion_bls_command_missing_IMPL_00")
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
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError("submit_ingress_assertion_bls_command_failed_IMPL_00") from exc
    return result.returncode == 0


def load_from_atlas(
    atlas_reader: Any,
    *,
    serving_agent_id: str,
    network_id: str,
) -> PublicSubmitIngressEndpointAssertion:
    if PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NOT_ACTIVATED:
        raise ValueError("public_submit_ingress_endpoint_assertion_not_activated_IMPL_00")

    normalized_agent_id = _require_lower_hex_exact(
        serving_agent_id,
        96,
        "submit_ingress_assertion_serving_agent_id_invalid_IMPL_00",
    )
    normalized_network_id = _require_non_empty_no_space(
        network_id,
        "submit_ingress_assertion_network_id_invalid_IMPL_00",
    )
    if atlas_reader is None:
        raise ValueError("submit_ingress_assertion_not_found_IMPL_00")

    candidate_id = submit_ingress_assertion_candidate_id(
        normalized_agent_id,
        normalized_network_id,
    )
    getter = getattr(atlas_reader, "get_public_submit_ingress_endpoint_assertion", None)
    if callable(getter):
        payload = getter(normalized_agent_id, normalized_network_id)
        if payload is not None:
            return PublicSubmitIngressEndpointAssertion.from_dict(payload)

    get_node = getattr(atlas_reader, "get_node", None)
    if callable(get_node):
        payload = get_node(candidate_id)
        if payload is not None:
            return PublicSubmitIngressEndpointAssertion.from_dict(payload)

    if isinstance(atlas_reader, Mapping):
        payload = (
            atlas_reader.get(candidate_id)
            or atlas_reader.get((normalized_agent_id, normalized_network_id))
            or atlas_reader.get(normalized_agent_id)
        )
        if payload is not None:
            assertion = PublicSubmitIngressEndpointAssertion.from_dict(payload)
            _require_assertion_pair(assertion, normalized_agent_id, normalized_network_id)
            return assertion

    iter_nodes = getattr(atlas_reader, "iter_nodes", None)
    if callable(iter_nodes):
        matches: list[PublicSubmitIngressEndpointAssertion] = []
        for index, node in enumerate(iter_nodes(), start=1):
            if index > MAX_SUBMIT_INGRESS_ASSERTION_ATLAS_SCAN_NODES:
                raise ValueError("submit_ingress_assertion_scan_limit_exceeded_IMPL_00")
            if (
                isinstance(node, Mapping)
                and node.get("node_kind") == PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NODE_KIND
                and node.get("serving_agent_id") == normalized_agent_id
                and node.get("network_id") == normalized_network_id
            ):
                matches.append(PublicSubmitIngressEndpointAssertion.from_dict(node))
        if matches:
            return _select_current_assertion(matches, atlas_reader=atlas_reader)

    raise ValueError("submit_ingress_assertion_not_found_IMPL_00")


def assertion_content_sha256(assertion: PublicSubmitIngressEndpointAssertion) -> str:
    return hashlib.sha256(canonical_endpoint_assertion_payload(assertion)).hexdigest()


def submit_ingress_assertion_candidate_id(serving_agent_id: str, network_id: str) -> str:
    normalized_agent_id = _require_lower_hex_exact(
        serving_agent_id,
        96,
        "submit_ingress_assertion_serving_agent_id_invalid_IMPL_00",
    )
    normalized_network_id = _require_non_empty_no_space(
        network_id,
        "submit_ingress_assertion_network_id_invalid_IMPL_00",
    )
    return (
        f"{PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_CANDIDATE_PREFIX}"
        f"{normalized_network_id}:{normalized_agent_id}"
    )


def assertion_is_superseded(
    atlas_reader: Any,
    assertion: PublicSubmitIngressEndpointAssertion,
) -> bool:
    if assertion.revised_by is not None:
        return True
    if atlas_reader is None:
        return False

    candidate_id = submit_ingress_assertion_candidate_id(
        assertion.serving_agent_id,
        assertion.network_id,
    )
    content_sha256 = assertion_content_sha256(assertion)
    iter_edges = getattr(atlas_reader, "iter_edges", None)
    if not callable(iter_edges):
        return False

    for index, edge in enumerate(iter_edges(), start=1):
        if index > MAX_SUBMIT_INGRESS_ASSERTION_ATLAS_SCAN_NODES:
            raise ValueError("submit_ingress_assertion_edge_scan_limit_exceeded_IMPL_00")
        if isinstance(edge, Mapping) and _edge_supersedes_assertion(
            edge,
            candidate_id,
            content_sha256,
        ):
            return True
    return False


def _select_current_assertion(
    candidates: list[PublicSubmitIngressEndpointAssertion],
    *,
    atlas_reader: Any = None,
) -> PublicSubmitIngressEndpointAssertion:
    if not candidates:
        raise ValueError("submit_ingress_assertion_not_found_IMPL_00")
    current = [
        assertion
        for assertion in candidates
        if not assertion_is_superseded(atlas_reader, assertion)
    ]
    if not current:
        raise ValueError("submit_ingress_assertion_all_candidates_superseded_IMPL_00")
    pair = {(assertion.serving_agent_id, assertion.network_id) for assertion in current}
    if len(pair) != 1:
        raise ValueError("submit_ingress_assertion_pair_mismatch_IMPL_00")
    if len(current) != 1:
        raise ValueError("submit_ingress_assertion_multiple_current_IMPL_00")
    return current[0]


def _canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _require_assertion_pair(
    assertion: PublicSubmitIngressEndpointAssertion,
    serving_agent_id: str,
    network_id: str,
) -> None:
    if assertion.serving_agent_id != serving_agent_id or assertion.network_id != network_id:
        raise ValueError("submit_ingress_assertion_pair_mismatch_IMPL_00")


def _require_revocation_policy(value: Any) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("submit_ingress_assertion_revocation_policy_invalid_IMPL_00")
    if value.get("revocation_record_kind") != PUBLIC_SUBMIT_INGRESS_ENDPOINT_REVOCATION_NODE_KIND:
        raise ValueError("submit_ingress_assertion_revocation_record_kind_invalid_IMPL_00")
    if value.get("supersession_required") is not True:
        raise ValueError("submit_ingress_assertion_supersession_required_invalid_IMPL_00")
    return value


def _require_uint64(value: Any, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0 or value > 2**64 - 1:
        raise ValueError(token)
    return value


def _require_lower_hex_exact(value: Any, length: int, token: str) -> str:
    if not isinstance(value, str) or len(value) != length or not _LOWER_HEX_RE.fullmatch(value):
        raise ValueError(token)
    return value


def _require_non_empty_str(value: Any, token: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(token)
    return value


def _require_non_empty_no_space(value: Any, token: str) -> str:
    if not isinstance(value, str) or not value or any(char.isspace() for char in value):
        raise ValueError(token)
    return value


def _edge_supersedes_assertion(
    edge: Mapping[str, Any],
    candidate_id: str,
    content_sha256: str,
) -> bool:
    edge_type = str(edge.get("edge_type") or "").lower()
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
    source_assertion_sha256 = edge.get("source_assertion_sha256")
    target_assertion_sha256 = edge.get("target_assertion_sha256")

    if edge_type in _SUPERSESSION_FORWARD_EDGE_TYPES and source == candidate_id:
        if source_assertion_sha256 is not None and source_assertion_sha256 != content_sha256:
            return False
        if target_assertion_sha256 is not None and target_assertion_sha256 == content_sha256:
            return False
        return True
    if edge_type in _SUPERSESSION_REVERSE_EDGE_TYPES and target == candidate_id:
        if target_assertion_sha256 is not None and target_assertion_sha256 != content_sha256:
            return False
        if source_assertion_sha256 is not None and source_assertion_sha256 == content_sha256:
            return False
        return True
    return False


__all__ = [
    "BlsVerifier",
    "MAX_SUBMIT_INGRESS_ASSERTION_ATLAS_SCAN_NODES",
    "PUBLIC_RC_NATIVE_SUBMIT_INGRESS_CDL_NOT_RATIFIED",
    "PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_BLS_COMMAND_ENV",
    "PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_BLS_DST_PREFIX",
    "PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_CANDIDATE_PREFIX",
    "PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NODE_KIND",
    "PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NOT_ACTIVATED",
    "PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_RUNTIME_VERSION",
    "PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_SCHEMA_VERSION",
    "PUBLIC_SUBMIT_INGRESS_ENDPOINT_REVOCATION_BLS_DST_PREFIX",
    "PUBLIC_SUBMIT_INGRESS_ENDPOINT_REVOCATION_NODE_KIND",
    "PUBLIC_SUBMIT_INGRESS_ENDPOINT_REVOCATION_SCHEMA_VERSION",
    "PublicSubmitIngressEndpointAssertion",
    "PublicSubmitIngressEndpointRevocation",
    "assertion_content_sha256",
    "assertion_is_superseded",
    "canonical_endpoint_assertion_payload",
    "canonical_revocation_payload",
    "load_from_atlas",
    "parse_endpoint_assertion",
    "parse_endpoint_revocation",
    "submit_ingress_assertion_candidate_id",
    "verify_endpoint_assertion_bls_signature",
]
