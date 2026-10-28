# SPDX-License-Identifier: AGPL-3.0-only
"""Read-only upgrade check against signed homoiconic release assertions."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import math
import os
import re
import time
import urllib.request
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from ilc_core.encoding.cidv1 import node_id_from_obj, parse_nodeid_strict
from ilc_core.epistemic.node_submission_runtime import EpistemicSubmissionError
from ilc_core.epistemic.truth_primitive_submission_runtime import (
    verify_native_submit_sig_envelope,
)
from ilc_core.release.current_policy import (
    CurrentPolicyEvaluationInput,
    resolve_current_policy,
)
from ilc_core.release.constants import (
    DEFAULT_UPGRADE_CHECK_ENDPOINT,
    ILC_UPGRADE_CHECK_ENDPOINT_ENV,
    MAX_UPGRADE_ASSERTION_BYTES,
    UPGRADE_CHECK_D2D_HOP_COUNT_HEADER,
    UPGRADE_CHECK_D2D_HOP_COUNT_VALUE,
    UPGRADE_CHECK_HTTP_CHUNK_BYTES,
    UPGRADE_CHECK_LOCAL_CACHE_MAX_AGE_SECONDS,
    UPGRADE_CHECK_PEER_HINT_MAX_PEERS,
    UPGRADE_CHECK_TIMEOUT_SECONDS,
)
from ilc_core.release.installable_release_signature import (
    DEFAULT_GENESIS_LINEAGE_REF,
    DEFAULT_PRIOR_RELEASE_ENVELOPE_REF,
    DEFAULT_RELEASE_KEY_REGISTRATION_REF,
    SIGNED_PREIMAGE_DOMAIN,
    compute_signed_preimage_sha256,
)
from ilc_core.release.release_authority import release_signer_public_key_hex
from ilc_core.release.release_assertion_schema import (
    ARTIFACT_NODE_FIELDS as _ARTIFACT_NODE_FIELDS,
    ASSERTION_OPTIONAL_FIELDS as _ASSERTION_OPTIONAL_FIELDS,
    ASSERTION_REQUIRED_FIELDS as _ASSERTION_REQUIRED_FIELDS,
    ATTESTATION_OPTIONAL_FIELDS as _ATTESTATION_OPTIONAL_FIELDS,
    ATTESTATION_REQUIRED_FIELDS as _ATTESTATION_REQUIRED_FIELDS,
    BUILD_RECIPE_NODE_FIELDS as _BUILD_RECIPE_NODE_FIELDS,
    CURRENT_ELIGIBILITY_STATUSES as _CURRENT_ELIGIBILITY_STATUSES,
    MAX_RELEASE_ARTIFACTS as _MAX_RELEASE_ARTIFACTS,
    MAX_RELEASE_ATTESTATIONS as _MAX_RELEASE_ATTESTATIONS,
    MAX_RELEASE_BUILD_RECIPES as _MAX_RELEASE_BUILD_RECIPES,
    SOFTWARE_RELEASE_NODE_FIELDS as _SOFTWARE_RELEASE_NODE_FIELDS,
)
from ilc_core.release.upgrade_state import (
    CURRENT_POLICY_HIGH_WATER_MARKS_KEY,
    advance_current_policy_high_water_mark,
    read_upgrade_state,
    write_upgrade_state,
)
from ilc_core.release.upgrade_validation_primitives import (
    UpgradeCheckError,
    reject_json_constant as _reject_json_constant,
    require_bounded_list as _require_bounded_list,
    require_exact_fields as _require_exact_fields,
    require_hex as _require_hex,
    require_literal as _require_literal,
    require_string as _require_string,
    require_strict_node_cid as _require_strict_node_cid,
    require_cid_like,
    require_timestamp,
)


_CID_LIKE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{2,255}$")
_HEX_32_BYTES_RE = re.compile(r"^[0-9a-f]{64}$")
_HEX_64_BYTES_RE = re.compile(r"^[0-9a-f]{128}$")
_GIT_COMMIT_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_UTC_Z_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z$")
_VERSION_RE = re.compile(r"^[0-9]+(?:\.[0-9]+){1,3}$")
_ARTIFACT_ID_RE = re.compile(r"^ilc-artifact:[a-z0-9][a-z0-9-]*@phase-[1-9][0-9]*$")
_ALLOWED_CHANNELS = frozenset({"public_rc", "testnet", "mainnet", "dev", "stable", "rc"})
_DEFAULT_SIGNATURE_SCHEME = "ed25519_phase_1335"
_ACTIVE_SIGNATURE_SCHEMES = frozenset({_DEFAULT_SIGNATURE_SCHEME})
_INACTIVE_SIGNATURE_SCHEMES = frozenset({"threshold_bls_v1"})
_DISPATCHED_SIGNATURE_SCHEMES = frozenset({_DEFAULT_SIGNATURE_SCHEME})
_MAX_BOOTSTRAP_HINT_FILE_BYTES = 1_000_000
_MAX_BOOTSTRAP_HINT_SCAN_ITEMS = UPGRADE_CHECK_PEER_HINT_MAX_PEERS * 2
FetchJson = Callable[[str, float], Mapping[str, Any]]
PeerFetchJson = Callable[[str, float, Mapping[str, str]], Mapping[str, Any]]
InstalledVersion = Callable[[], str | None]
NowFn = Callable[[], datetime]
DelegationPolicyResolver = Callable[[Mapping[str, Any]], Mapping[str, Any]]


@dataclass(frozen=True)
class UpgradeEvaluationRuntime:
    """Injectable local evaluation dependencies for deterministic tests."""

    installed_version_resolver: InstalledVersion | None = None
    now_fn: NowFn | None = None


class PeerRegistryLike(Protocol):
    """Minimal read-only peer registry surface used by upgrade discovery."""

    def get_peers(self) -> Sequence[str]:
        """Return currently promoted peer endpoints."""



class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        req: Request,
        fp: object,
        code: int,
        msg: str,
        headers: object,
        newurl: str,
    ) -> None:
        raise UpgradeCheckError("upgrade_check_endpoint_redirect_forbidden")


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _now_rfc3339(now: datetime) -> str:
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return now.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_rfc3339_utc(value: Any) -> datetime:
    text = _require_string(value, "checked_at_utc", max_chars=64)
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise UpgradeCheckError("upgrade_state_checked_at_invalid") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _require_cid_like(value: Any, field: str) -> str:
    return require_cid_like(value, field, _CID_LIKE_RE)


def _require_timestamp(value: Any, field: str) -> str:
    return require_timestamp(value, field, _UTC_Z_RE)


def _assert_no_floats(value: Any, field: str = "$", depth: int = 0) -> None:
    if depth > 16:
        raise UpgradeCheckError("upgrade_assertion_nesting_too_deep")
    if isinstance(value, float):
        raise UpgradeCheckError(f"upgrade_assertion_float_rejected:{field}")
    if isinstance(value, dict):
        for key, child in value.items():
            _assert_no_floats(child, f"{field}.{key}", depth + 1)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _assert_no_floats(child, f"{field}[{index}]", depth + 1)


def _version_key(version: str) -> tuple[int, ...]:
    text = _require_string(version, "version", max_chars=64)
    if _VERSION_RE.fullmatch(text) is None:
        raise UpgradeCheckError("upgrade_assertion_version_invalid")
    parts = tuple(int(part) for part in text.split("."))
    return parts + (0,) * (4 - len(parts))


def installed_ilc_core_version() -> str | None:
    try:
        return importlib.metadata.version("ilc-core")
    except importlib.metadata.PackageNotFoundError:
        return None


def _endpoint_from_env() -> str:
    return os.environ.get(ILC_UPGRADE_CHECK_ENDPOINT_ENV, "").strip()


def _validate_endpoint(endpoint: str) -> str:
    text = _require_string(endpoint, "endpoint", max_chars=2048)
    parsed = urlparse(text)
    if parsed.scheme != "https" or not parsed.netloc:
        raise UpgradeCheckError("upgrade_check_endpoint_insecure")
    if parsed.username is not None or parsed.password is not None:
        raise UpgradeCheckError("upgrade_check_endpoint_userinfo_forbidden")
    return text


def _validate_peer_discovery_endpoint(endpoint: str) -> str:
    """Accept http:// or https:// peer endpoints for signed release discovery."""

    text = _require_string(endpoint, "endpoint", max_chars=2048)
    parsed = urlparse(text)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise UpgradeCheckError("upgrade_check_peer_endpoint_invalid_scheme")
    if parsed.username is not None or parsed.password is not None:
        raise UpgradeCheckError("upgrade_check_peer_endpoint_userinfo_forbidden")
    if parsed.query or parsed.fragment:
        raise UpgradeCheckError("upgrade_check_peer_endpoint_invalid_base")
    return text


def _validate_timeout(timeout_seconds: float) -> float:
    try:
        timeout = float(timeout_seconds)
    except (TypeError, ValueError) as exc:
        raise UpgradeCheckError("upgrade_check_timeout_invalid") from exc
    if not math.isfinite(timeout) or timeout <= 0:
        raise UpgradeCheckError("upgrade_check_timeout_invalid")
    return timeout


def _read_json_response(
    *,
    endpoint: str,
    timeout: float,
    headers: Mapping[str, str],
) -> Mapping[str, Any]:
    opener = urllib.request.build_opener(_NoRedirectHandler)
    request = Request(endpoint, headers=dict(headers))
    try:
        with opener.open(request, timeout=timeout) as response:
            status = getattr(response, "status", None)
            if status != 200:
                raise UpgradeCheckError("upgrade_check_endpoint_unreachable")
            declared = response.headers.get("Content-Length")
            if declared is not None:
                try:
                    declared_size = int(declared)
                except ValueError as exc:
                    raise UpgradeCheckError("upgrade_assertion_content_length_invalid") from exc
                if declared_size < 0:
                    raise UpgradeCheckError("upgrade_assertion_content_length_invalid")
                if declared_size > MAX_UPGRADE_ASSERTION_BYTES:
                    raise UpgradeCheckError("upgrade_assertion_too_large")
            chunks: list[bytes] = []
            total = 0
            while True:
                chunk = response.read(UPGRADE_CHECK_HTTP_CHUNK_BYTES)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_UPGRADE_ASSERTION_BYTES:
                    raise UpgradeCheckError("upgrade_assertion_too_large")
                chunks.append(chunk)
    except HTTPError as exc:
        if 300 <= exc.code < 400:
            raise UpgradeCheckError("upgrade_check_endpoint_redirect_forbidden") from exc
        raise UpgradeCheckError("upgrade_check_endpoint_unreachable") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise UpgradeCheckError("upgrade_check_endpoint_unreachable") from exc
    try:
        payload = json.loads(
            b"".join(chunks).decode("utf-8"),
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise UpgradeCheckError("upgrade_assertion_invalid_json") from exc
    if not isinstance(payload, Mapping):
        raise UpgradeCheckError("upgrade_assertion_not_object")
    return payload


def fetch_upgrade_assertion_json(endpoint: str, timeout_seconds: float) -> Mapping[str, Any]:
    endpoint = _validate_endpoint(endpoint)
    timeout = _validate_timeout(timeout_seconds)
    return _read_json_response(
        endpoint=endpoint,
        timeout=timeout,
        headers={"Accept": "application/json"},
    )


def _fetch_peer_upgrade_assertion_json(
    endpoint: str,
    timeout_seconds: float,
    headers: Mapping[str, str],
) -> Mapping[str, Any]:
    endpoint = _validate_peer_discovery_endpoint(endpoint)
    timeout = _validate_timeout(timeout_seconds)
    peer_headers = {"Accept": "application/json", **dict(headers)}
    if peer_headers.get(UPGRADE_CHECK_D2D_HOP_COUNT_HEADER) != UPGRADE_CHECK_D2D_HOP_COUNT_VALUE:
        raise UpgradeCheckError("upgrade_check_peer_hop_count_invalid")
    return _read_json_response(endpoint=endpoint, timeout=timeout, headers=peer_headers)


def _canonical_assertion_sha256(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        dict(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _is_upgrade_state_fresh(state: Mapping[str, Any], now: datetime) -> bool:
    checked_at = _parse_rfc3339_utc(state.get("checked_at_utc"))
    now = now.astimezone(timezone.utc) if now.tzinfo is not None else now.replace(tzinfo=timezone.utc)
    max_future_skew = timedelta(minutes=5)
    if checked_at > now + max_future_skew:
        return False
    age = now - checked_at
    return 0 <= age.total_seconds() <= UPGRADE_CHECK_LOCAL_CACHE_MAX_AGE_SECONDS


def _cached_release_assertion_payload(state: Mapping[str, Any]) -> Mapping[str, Any] | None:
    payload = state.get("release_assertion_payload")
    if payload is None:
        payload = state.get("release_assertion")
    if isinstance(payload, Mapping):
        return payload
    return None


def _extract_release_node(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    node = payload.get("software_release_node")
    if not isinstance(node, Mapping):
        raise UpgradeCheckError("upgrade_assertion_release_node_missing")
    return node


def _extract_attestation_edges(payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    edges = payload.get("release_attestation_edges")
    edges = _require_bounded_list(
        edges,
        field="release_attestation_edges",
        maximum=_MAX_RELEASE_ATTESTATIONS,
    )
    result: list[Mapping[str, Any]] = []
    for edge in edges:
        if not isinstance(edge, Mapping):
            raise UpgradeCheckError("upgrade_assertion_release_attestation_invalid")
        result.append(edge)
    return result


def _validate_release_node(node: Mapping[str, Any], expected_pubkey: str) -> dict[str, Any]:
    _require_exact_fields(
        node,
        required=_SOFTWARE_RELEASE_NODE_FIELDS,
        object_name="software_release_node",
    )
    _require_literal(node.get("node_kind"), "node_kind", "SoftwareReleaseNode")
    _require_literal(
        node.get("schema_version"),
        "schema_version",
        "software_release_node.v0.1",
    )
    package_name = _require_string(node.get("package_name"), "package_name")
    if package_name != "ilc-core":
        raise UpgradeCheckError("upgrade_assertion_package_name_mismatch")
    version = _require_string(node.get("version"), "version")
    _version_key(version)
    release_channel = _require_string(node.get("release_channel"), "release_channel")
    if release_channel not in _ALLOWED_CHANNELS:
        raise UpgradeCheckError("upgrade_assertion_release_channel_invalid")
    _require_timestamp(node.get("release_date"), "release_date")
    source_commit = _require_hex(node.get("source_commit"), "source_commit", _GIT_COMMIT_RE)
    artifact_cids = _require_bounded_list(
        node.get("artifact_cids"),
        field="artifact_cids",
        maximum=_MAX_RELEASE_ARTIFACTS,
    )
    artifact_cids = [_require_cid_like(value, "artifact_cids") for value in artifact_cids]
    if len(set(artifact_cids)) != len(artifact_cids):
        raise UpgradeCheckError("upgrade_assertion_duplicate_artifact_cid")
    build_recipe_cid = _require_cid_like(node.get("build_recipe_cid"), "build_recipe_cid")
    release_key_pubkey = _require_string(node.get("release_key_pubkey"), "release_key_pubkey")
    if release_key_pubkey != expected_pubkey:
        raise UpgradeCheckError("upgrade_assertion_release_key_mismatch")
    release_signature_ref = _require_string(
        node.get("release_signature_ref"),
        "release_signature_ref",
    )
    changelog_hash = _require_hex(node.get("changelog_hash"), "changelog_hash", _HEX_32_BYTES_RE)
    cid = _require_strict_node_cid(node, object_name="software_release_node")
    return {
        "artifact_cids": artifact_cids,
        "build_recipe_cid": build_recipe_cid,
        "changelog_hash": changelog_hash,
        "cid": cid,
        "package_name": package_name,
        "release_channel": release_channel,
        "release_key_pubkey": release_key_pubkey,
        "release_signature_ref": release_signature_ref,
        "source_commit": source_commit,
        "version": version,
    }


def _validate_artifact_nodes(
    payload: Mapping[str, Any],
    *,
    node_info: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    raw_nodes = _require_bounded_list(
        payload.get("artifact_nodes"),
        field="artifact_nodes",
        maximum=_MAX_RELEASE_ARTIFACTS,
    )
    by_cid: dict[str, dict[str, Any]] = {}
    artifact_ids: set[str] = set()
    for index, raw_node in enumerate(raw_nodes):
        if not isinstance(raw_node, Mapping):
            raise UpgradeCheckError("upgrade_assertion_artifact_node_invalid")
        _require_exact_fields(
            raw_node,
            required=_ARTIFACT_NODE_FIELDS,
            object_name=f"artifact_nodes[{index}]",
        )
        _require_literal(raw_node.get("node_kind"), "node_kind", "ArtifactNode")
        _require_literal(raw_node.get("schema_version"), "schema_version", "artifact_node.v0.1")
        artifact_id = _require_string(raw_node.get("artifact_id"), "artifact_id", max_chars=160)
        if _ARTIFACT_ID_RE.fullmatch(artifact_id) is None:
            raise UpgradeCheckError("upgrade_assertion_artifact_id_invalid")
        if artifact_id in artifact_ids:
            raise UpgradeCheckError("upgrade_assertion_duplicate_artifact_id")
        artifact_ids.add(artifact_id)
        artifact_type = _require_string(raw_node.get("artifact_type"), "artifact_type", max_chars=32)
        if artifact_type not in {"wheel", "sdist", "binary_tarball"}:
            raise UpgradeCheckError("upgrade_assertion_artifact_type_invalid")
        filename = _require_string(raw_node.get("filename"), "filename", max_chars=255)
        package_name = _require_string(raw_node.get("package_name"), "package_name", max_chars=160)
        package_version = _require_string(raw_node.get("package_version"), "package_version", max_chars=80)
        if package_name != node_info["package_name"] or package_version != node_info["version"]:
            raise UpgradeCheckError("upgrade_assertion_artifact_package_mismatch")
        sha256 = _require_hex(raw_node.get("sha256"), "sha256", _HEX_32_BYTES_RE)
        size_bytes = raw_node.get("size_bytes")
        if not isinstance(size_bytes, int) or isinstance(size_bytes, bool) or size_bytes <= 0:
            raise UpgradeCheckError("upgrade_assertion_artifact_size_invalid")
        pypi_url = _require_string(raw_node.get("pypi_url"), "pypi_url", max_chars=2048)
        cid = _require_strict_node_cid(raw_node, object_name=f"artifact_nodes[{index}]")
        if cid in by_cid:
            raise UpgradeCheckError("upgrade_assertion_duplicate_artifact_cid")
        by_cid[cid] = {
            "artifact_id": artifact_id,
            "artifact_type": artifact_type,
            "cid": cid,
            "filename": filename,
            "package_name": package_name,
            "package_version": package_version,
            "pypi_url": pypi_url,
            "sha256": sha256,
            "size_bytes": size_bytes,
        }
    if set(by_cid) != set(node_info["artifact_cids"]):
        raise UpgradeCheckError("upgrade_assertion_artifact_coverage_mismatch")
    return by_cid


def _validate_build_recipe_nodes(
    payload: Mapping[str, Any],
    *,
    node_info: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    raw_nodes = _require_bounded_list(
        payload.get("build_recipe_nodes"),
        field="build_recipe_nodes",
        maximum=_MAX_RELEASE_BUILD_RECIPES,
    )
    by_cid: dict[str, dict[str, Any]] = {}
    for index, raw_node in enumerate(raw_nodes):
        if not isinstance(raw_node, Mapping):
            raise UpgradeCheckError("upgrade_assertion_build_recipe_invalid")
        _require_exact_fields(
            raw_node,
            required=_BUILD_RECIPE_NODE_FIELDS,
            object_name=f"build_recipe_nodes[{index}]",
        )
        _require_literal(raw_node.get("node_kind"), "node_kind", "BuildRecipeNode")
        _require_literal(
            raw_node.get("schema_version"),
            "schema_version",
            "build_recipe_node.v0.1",
        )
        source_commit = _require_hex(raw_node.get("source_commit"), "source_commit", _GIT_COMMIT_RE)
        if source_commit != node_info["source_commit"]:
            raise UpgradeCheckError("upgrade_assertion_build_recipe_source_commit_mismatch")
        _require_timestamp(raw_node.get("build_date"), "build_date")
        _require_hex(raw_node.get("build_env_hash"), "build_env_hash", _HEX_32_BYTES_RE)
        _require_hex(
            raw_node.get("reproducibility_hash"),
            "reproducibility_hash",
            _HEX_32_BYTES_RE,
        )
        _require_string(raw_node.get("build_command"), "build_command", max_chars=2048)
        _require_string(raw_node.get("build_toolchain"), "build_toolchain", max_chars=160)
        _require_string(raw_node.get("builder_agent_id"), "builder_agent_id", max_chars=255)
        cid = _require_strict_node_cid(raw_node, object_name=f"build_recipe_nodes[{index}]")
        if cid in by_cid:
            raise UpgradeCheckError("upgrade_assertion_duplicate_build_recipe_cid")
        by_cid[cid] = dict(raw_node)
    if set(by_cid) != {node_info["build_recipe_cid"]}:
        raise UpgradeCheckError("upgrade_assertion_build_recipe_coverage_mismatch")
    return by_cid


def _resolve_release_signature_scheme(edge: Mapping[str, Any]) -> str:
    raw_scheme = edge.get("signature_scheme", _DEFAULT_SIGNATURE_SCHEME)
    signature_scheme = _require_string(raw_scheme, "signature_scheme", max_chars=80)
    if signature_scheme in _ACTIVE_SIGNATURE_SCHEMES:
        return signature_scheme
    if signature_scheme in _INACTIVE_SIGNATURE_SCHEMES:
        raise UpgradeCheckError("release_assertion_signature_scheme_not_active")
    raise UpgradeCheckError("release_assertion_unknown_signature_scheme")


def _verify_release_attestation_signature(
    *,
    signature_scheme: str,
    signing_algorithm: str,
    expected_pubkey: str,
    signature_hex: str,
    signed_preimage_sha256: str,
) -> None:
    if signature_scheme not in _DISPATCHED_SIGNATURE_SCHEMES:
        raise UpgradeCheckError("release_assertion_signature_scheme_not_dispatched")
    if signature_scheme == _DEFAULT_SIGNATURE_SCHEME:
        if signing_algorithm != "Ed25519":
            raise UpgradeCheckError("upgrade_assertion_literal_mismatch:signing_algorithm")
        try:
            public_key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(expected_pubkey))
            public_key.verify(bytes.fromhex(signature_hex), bytes.fromhex(signed_preimage_sha256))
        except (InvalidSignature, ValueError) as exc:
            raise UpgradeCheckError("upgrade_assertion_release_signature_verify_failed") from exc
        return
    raise UpgradeCheckError("release_assertion_signature_scheme_not_dispatched")


def _verify_release_attestation_edge(
    edge: Mapping[str, Any],
    *,
    node_info: Mapping[str, Any],
    artifact_nodes: Mapping[str, Mapping[str, Any]],
    expected_pubkey: str,
) -> dict[str, str]:
    _require_exact_fields(
        edge,
        required=_ATTESTATION_REQUIRED_FIELDS,
        optional=_ATTESTATION_OPTIONAL_FIELDS,
        object_name="release_attestation_edge",
    )
    _require_literal(edge.get("edge_type"), "edge_type", "RELEASE_ATTESTS_ARTIFACT")
    _require_literal(
        edge.get("schema_version"),
        "schema_version",
        "release_attestation_edge.v0.1",
    )
    signature_scheme = _resolve_release_signature_scheme(edge)
    source = _require_cid_like(edge.get("source"), "source")
    node_cid = node_info.get("cid")
    if isinstance(node_cid, str) and source != node_cid:
        raise UpgradeCheckError("upgrade_assertion_attestation_source_mismatch")
    target = _require_cid_like(edge.get("target"), "target")
    artifact_node = artifact_nodes.get(target)
    if artifact_node is None:
        raise UpgradeCheckError("upgrade_assertion_attestation_target_mismatch")
    artifact_id = _require_string(edge.get("artifact_id"), "artifact_id", max_chars=160)
    if _ARTIFACT_ID_RE.fullmatch(artifact_id) is None:
        raise UpgradeCheckError("upgrade_assertion_artifact_id_invalid")
    artifact_sha256 = _require_hex(edge.get("artifact_sha256"), "artifact_sha256", _HEX_32_BYTES_RE)
    if artifact_id != artifact_node["artifact_id"]:
        raise UpgradeCheckError("upgrade_assertion_attestation_artifact_id_mismatch")
    if artifact_sha256 != artifact_node["sha256"]:
        raise UpgradeCheckError("upgrade_assertion_attestation_artifact_hash_mismatch")
    signed_preimage_domain = _require_literal(
        edge.get("signed_preimage_domain"),
        "signed_preimage_domain",
        SIGNED_PREIMAGE_DOMAIN,
    )
    signed_preimage_sha256 = _require_hex(
        edge.get("signed_preimage_sha256"),
        "signed_preimage_sha256",
        _HEX_32_BYTES_RE,
    )
    release_key_registration_ref = _require_string(
        edge.get("release_key_registration_ref"),
        "release_key_registration_ref",
        max_chars=255,
    )
    genesis_lineage_ref = _require_string(
        edge.get("genesis_lineage_ref"),
        "genesis_lineage_ref",
        max_chars=255,
    )
    prior_release_envelope_ref = _require_string(
        edge.get("prior_release_envelope_ref"),
        "prior_release_envelope_ref",
        max_chars=255,
    )
    expected_preimage_sha256 = compute_signed_preimage_sha256(
        release_id=f"{node_info['package_name']}-{node_info['version']}",
        artifact_id=artifact_id,
        artifact_sha256=artifact_sha256,
        release_key_registration_ref=release_key_registration_ref,
        genesis_lineage_ref=genesis_lineage_ref,
        prior_release_envelope_ref=prior_release_envelope_ref,
    )
    if signed_preimage_sha256 != expected_preimage_sha256:
        raise UpgradeCheckError("upgrade_assertion_release_preimage_mismatch")
    signing_algorithm = _require_string(edge.get("signing_algorithm"), "signing_algorithm", max_chars=80)
    signer_public_key_hex = _require_string(edge.get("signer_public_key_hex"), "signer_public_key_hex")
    if signer_public_key_hex != expected_pubkey:
        raise UpgradeCheckError("upgrade_assertion_release_signer_mismatch")
    signature_hex = _require_hex(edge.get("signature_hex"), "signature_hex", _HEX_64_BYTES_RE)
    _require_timestamp(edge.get("attestation_date"), "attestation_date")
    _verify_release_attestation_signature(
        signature_scheme=signature_scheme,
        signing_algorithm=signing_algorithm,
        expected_pubkey=expected_pubkey,
        signature_hex=signature_hex,
        signed_preimage_sha256=signed_preimage_sha256,
    )
    return {
        "artifact_sha256": artifact_sha256,
        "artifact_id": artifact_id,
        "signed_preimage_domain": signed_preimage_domain,
        "signed_preimage_sha256": signed_preimage_sha256,
        "signature_scheme": signature_scheme,
        "signer_public_key_hex": signer_public_key_hex,
        "target": target,
    }


def _require_all_artifacts_attested(
    *,
    artifact_cids: Sequence[str],
    verified_edges: Sequence[Mapping[str, str]],
) -> None:
    attested_targets = {edge["target"] for edge in verified_edges}
    declared_artifacts = set(artifact_cids)
    if len(verified_edges) != len(attested_targets):
        raise UpgradeCheckError("upgrade_assertion_duplicate_attestation_coverage")
    if attested_targets != declared_artifacts:
        raise UpgradeCheckError("upgrade_assertion_unattested_artifacts_present")


def _canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        dict(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _assertion_core(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        str(key): deepcopy(value)
        for key, value in payload.items()
        if key != "native_submit_envelope"
    }


def _verify_assertion_cid(payload: Mapping[str, Any]) -> str:
    assertion_cid = _require_string(payload.get("assertion_cid"), "assertion_cid", max_chars=255)
    try:
        parse_nodeid_strict(assertion_cid)
        body = {
            str(key): value
            for key, value in payload.items()
            if key not in {"assertion_cid", "native_submit_envelope"}
        }
        observed = node_id_from_obj(body)
    except (TypeError, ValueError) as exc:
        raise UpgradeCheckError("upgrade_assertion_cid_invalid:aggregate") from exc
    if observed != assertion_cid:
        raise UpgradeCheckError("upgrade_assertion_cid_mismatch:aggregate")
    return assertion_cid


def _native_submit_network_id(envelope: Mapping[str, Any]) -> str:
    sig = envelope.get("sig")
    if not isinstance(sig, Mapping):
        raise UpgradeCheckError("release_graph_provenance_sig_missing")
    _require_exact_fields(
        sig,
        required=frozenset(
            {
                "dst",
                "key_ref",
                "payload_sha256",
                "schema_version",
                "signature_hex",
                "verifier_profile",
            }
        ),
        object_name="native_submit_envelope.sig",
    )
    dst = _require_string(sig.get("dst"), "native_submit_envelope.sig.dst", max_chars=255)
    prefix = "ILC_NATIVE_TRUTH_SUBMIT_V1:"
    if not dst.startswith(prefix) or len(dst) == len(prefix):
        raise UpgradeCheckError("release_graph_provenance_network_invalid")
    return dst[len(prefix) :]


def _verify_native_release_envelope(
    envelope: Any,
    *,
    assertion_core: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(envelope, Mapping):
        raise UpgradeCheckError("release_graph_provenance_envelope_invalid")
    _require_exact_fields(
        envelope,
        required=frozenset({"agent_id", "epoch", "payload", "primitive", "sig", "v"}),
        object_name="native_submit_envelope",
    )
    payload = envelope.get("payload")
    if not isinstance(payload, Mapping):
        raise UpgradeCheckError("release_graph_provenance_payload_invalid")
    content = payload.get("content")
    if not isinstance(content, Mapping):
        raise UpgradeCheckError("release_graph_provenance_content_invalid")
    nested_core = content.get("software_release_assertion")
    if not isinstance(nested_core, Mapping):
        raise UpgradeCheckError("release_graph_provenance_assertion_missing")
    if _canonical_json_bytes(nested_core) != _canonical_json_bytes(assertion_core):
        raise UpgradeCheckError("release_graph_provenance_assertion_core_mismatch")
    network_id = _native_submit_network_id(envelope)
    try:
        verify_native_submit_sig_envelope(dict(envelope))
    except EpistemicSubmissionError as exc:
        raise UpgradeCheckError("release_graph_provenance_bls_verify_failed") from exc
    sig = envelope["sig"]
    epoch = envelope.get("epoch")
    if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 0:
        raise UpgradeCheckError("release_graph_provenance_epoch_invalid")
    return {
        "agent_id": _require_string(envelope.get("agent_id"), "native_submit_envelope.agent_id"),
        "epoch": epoch,
        "key_ref": _require_string(sig.get("key_ref"), "native_submit_envelope.sig.key_ref"),
        "network_id": network_id,
    }


def _resolve_delegation_at_submission(
    envelope_info: Mapping[str, Any],
    *,
    resolver: DelegationPolicyResolver | None,
) -> tuple[bool, str, dict[str, Any]]:
    context = {
        "agent_id": envelope_info["agent_id"],
        "epoch": envelope_info["epoch"],
        "key_ref": envelope_info["key_ref"],
        "network_id": envelope_info["network_id"],
    }
    if resolver is None:
        return (
            False,
            "graph_submitter_policy_not_evaluated_permissionless_ingress",
            context,
        )
    raw = resolver(context)
    if not isinstance(raw, Mapping):
        raise UpgradeCheckError("release_graph_delegation_resolver_invalid")
    valid = raw.get("valid_at_submission") is True
    status = _require_string(raw.get("status"), "delegation.status", max_chars=160)
    for field in ("key_ref", "network_id", "epoch"):
        if raw.get(field) != context[field]:
            raise UpgradeCheckError("release_graph_delegation_evidence_mismatch")
    if valid:
        if status != "verified_valid_at_submission":
            raise UpgradeCheckError("release_graph_delegation_status_invalid")
        _require_string(raw.get("policy_ref"), "delegation.policy_ref", max_chars=255)
        if raw.get("mldsa_evidence_verified") is not True:
            raise UpgradeCheckError("release_graph_delegation_mldsa_unverified")
        if raw.get("revocation_resolver_available") is not True:
            raise UpgradeCheckError("release_graph_delegation_revocation_unavailable")
        if raw.get("revoked_at_submission") is not False:
            raise UpgradeCheckError("release_graph_delegation_revoked_at_submission")
    elif status == "verified_valid_at_submission":
        raise UpgradeCheckError("release_graph_delegation_status_invalid")
    return valid, status, dict(raw)


def _unresolved_eligibility_receipt(
    *,
    assertion_cid: str,
    artifact_cids: Sequence[str],
) -> dict[str, Any]:
    return {
        "policy_ref": "unavailable:current_release_policy",
        "policy_version": "unavailable",
        "network_id": "unresolved",
        "release_assertion_cid": assertion_cid,
        "artifact_cids": list(artifact_cids),
        "authoritative_epoch_or_snapshot": "unavailable",
        "eligibility_evidence_refs": [],
        "freshness_rule": "unavailable",
        "evaluated_at": "not_evaluated",
        "withdrawal_resolver_available": False,
    }


def _resolve_current_eligibility(
    *,
    assertion_cid: str,
    software_release_cid: str,
    artifact_cids: Sequence[str],
    release_channel: str,
    expected_network_id: str | None,
    evaluation_input: CurrentPolicyEvaluationInput | None,
) -> tuple[str, dict[str, Any]]:
    context = {
        "assertion_cid": assertion_cid,
        "artifact_cids": list(artifact_cids),
    }
    if evaluation_input is None:
        return "unresolved", _unresolved_eligibility_receipt(**context)
    if evaluation_input.release_assertion_cid != assertion_cid:
        raise UpgradeCheckError("release_current_policy_assertion_mismatch")
    if evaluation_input.software_release_cid != software_release_cid:
        raise UpgradeCheckError("release_current_policy_software_release_mismatch")
    if evaluation_input.artifact_cids != tuple(artifact_cids):
        raise UpgradeCheckError("release_current_policy_artifacts_mismatch")
    if evaluation_input.channel != release_channel:
        raise UpgradeCheckError("release_current_policy_channel_mismatch")
    if expected_network_id is not None and evaluation_input.network_id != expected_network_id:
        raise UpgradeCheckError("release_current_policy_network_mismatch")
    resolved = resolve_current_policy(evaluation_input)
    status = resolved.status
    if status not in _CURRENT_ELIGIBILITY_STATUSES:
        raise UpgradeCheckError("release_current_policy_status_invalid")
    receipt = resolved.evidence_receipt
    if not isinstance(receipt, Mapping):
        raise UpgradeCheckError("release_current_policy_evidence_missing")
    required = {
        "policy_ref",
        "policy_version",
        "network_id",
        "release_assertion_cid",
        "artifact_cids",
        "authoritative_epoch_or_snapshot",
        "eligibility_evidence_refs",
        "freshness_rule",
        "evaluated_at",
        "withdrawal_resolver_available",
    }
    if not required <= set(receipt):
        raise UpgradeCheckError("release_current_policy_evidence_incomplete")
    if receipt.get("release_assertion_cid") != assertion_cid:
        raise UpgradeCheckError("release_current_policy_assertion_mismatch")
    if receipt.get("artifact_cids") != list(artifact_cids):
        raise UpgradeCheckError("release_current_policy_artifacts_mismatch")
    if status in {"verified_current_policy", "rejected_by_current_policy"}:
        if expected_network_id is None:
            raise UpgradeCheckError("release_current_policy_network_unresolved")
        for field in (
            "policy_ref",
            "policy_version",
            "network_id",
            "authoritative_epoch_or_snapshot",
            "freshness_rule",
        ):
            _require_string(receipt.get(field), f"current_policy.{field}", max_chars=255)
        if receipt.get("network_id") != expected_network_id:
            raise UpgradeCheckError("release_current_policy_network_mismatch")
        refs = receipt.get("eligibility_evidence_refs")
        if not isinstance(refs, list) or not refs or not all(isinstance(ref, str) and ref for ref in refs):
            raise UpgradeCheckError("release_current_policy_evidence_refs_invalid")
        evaluated_at = receipt.get("evaluated_at")
        if not isinstance(evaluated_at, str) or not evaluated_at.startswith("validation_epoch:"):
            raise UpgradeCheckError("release_current_policy_evaluated_checkpoint_invalid")
        if receipt.get("withdrawal_resolver_available") is not True:
            raise UpgradeCheckError("release_current_policy_withdrawal_unavailable")
    return status, dict(receipt)


def require_arbitrary_source_release_authorized(validation: Mapping[str, Any]) -> None:
    """Fail closed unless full graph binding and current eligibility are proven."""

    if validation.get("full_release_graph_binding_verified") is not True:
        raise UpgradeCheckError("arbitrary_source_full_release_graph_binding_required")
    if validation.get("current_release_eligibility_status") != "verified_current_policy":
        raise UpgradeCheckError("arbitrary_source_current_release_eligibility_required")


def validate_release_assertion(
    payload: Mapping[str, Any],
    *,
    delegation_policy_resolver: DelegationPolicyResolver | None = None,
    current_policy_evaluation_input: CurrentPolicyEvaluationInput | None = None,
) -> dict[str, Any]:
    """Validate a strict CDL-121 assertion and report layered trust outcomes."""

    if not isinstance(payload, Mapping):
        raise UpgradeCheckError("upgrade_assertion_not_object")
    _assert_no_floats(payload)
    _require_exact_fields(
        payload,
        required=_ASSERTION_REQUIRED_FIELDS,
        optional=_ASSERTION_OPTIONAL_FIELDS,
        object_name="software_release_assertion",
    )
    _require_literal(
        payload.get("schema_version"),
        "schema_version",
        "software_release_assertion.v0.1",
    )
    expected_pubkey = release_signer_public_key_hex()
    node = _extract_release_node(payload)
    node_info = _validate_release_node(node, expected_pubkey)
    artifact_nodes = _validate_artifact_nodes(payload, node_info=node_info)
    _validate_build_recipe_nodes(payload, node_info=node_info)
    edges = _extract_attestation_edges(payload)
    verified_edges = [
        _verify_release_attestation_edge(
            edge,
            node_info=node_info,
            artifact_nodes=artifact_nodes,
            expected_pubkey=expected_pubkey,
        )
        for edge in edges
    ]
    _require_all_artifacts_attested(
        artifact_cids=node_info["artifact_cids"],
        verified_edges=verified_edges,
    )
    signature_schemes = {edge["signature_scheme"] for edge in verified_edges}
    if len(signature_schemes) != 1:
        raise UpgradeCheckError("release_assertion_signature_scheme_mismatch")
    signature_scheme = next(iter(signature_schemes))
    assertion_cid = _verify_assertion_cid(payload)
    core = _assertion_core(payload)

    graph_verified = False
    delegation_valid = False
    graph_status = "not_present_core_only"
    graph_network_id: str | None = None
    delegation_status = "not_present_core_only"
    delegation_evidence: dict[str, Any] = {}
    graph_envelope = payload.get("native_submit_envelope")
    if graph_envelope is not None:
        envelope_info = _verify_native_release_envelope(graph_envelope, assertion_core=core)
        graph_network_id = envelope_info["network_id"]
        graph_verified = True
        graph_status = "verified_native_submit_sig_v0.1"
        delegation_valid, delegation_status, delegation_evidence = _resolve_delegation_at_submission(
            envelope_info,
            resolver=delegation_policy_resolver,
        )

    eligibility_status, eligibility_receipt = _resolve_current_eligibility(
        assertion_cid=assertion_cid,
        software_release_cid=node_info["cid"],
        artifact_cids=node_info["artifact_cids"],
        release_channel=node_info["release_channel"],
        expected_network_id=graph_network_id,
        evaluation_input=current_policy_evaluation_input,
    )
    # Schema, Ed25519 authority, artifact coverage, CIDs, and graph links were
    # verified above. A matching CDL-118 envelope completes graph binding;
    # optional submitter-policy evidence is reported separately and is not a
    # content-submission authority gate.
    full_binding = graph_verified
    return {
        "assertion_cid": assertion_cid,
        "available_version": node_info["version"],
        "channel": node_info["release_channel"],
        "artifact_cids": list(node_info["artifact_cids"]),
        "artifact_release_authority_verified": True,
        "graph_submission_provenance_verified": graph_verified,
        "graph_provenance_delegation_valid_at_submission": delegation_valid,
        "graph_provenance_delegation_status": delegation_status,
        "graph_provenance_delegation_evidence": delegation_evidence,
        "full_release_graph_binding_verified": full_binding,
        "current_release_eligibility_status": eligibility_status,
        "current_release_eligibility_evidence": eligibility_receipt,
        "graph_provenance_status": graph_status,
        "graph_provenance_verified": graph_verified,
        "package_name": node_info["package_name"],
        "release_authority": "ed25519_phase_1335",
        "release_key_pubkey": expected_pubkey,
        "release_signature_verified": True,
        "signature_scheme": signature_scheme,
        "verified_attestation_count": len(verified_edges),
    }


def _default_bootstrap_peer_hints_paths() -> tuple[Path, Path]:
    from ilc_core.identity.first_run_provisioning import identity_root

    root = identity_root(Path.home())
    return (root / "bootstrap_peer_hints.json", root / "bootstrap_fetch_peers.json")


def _endpoint_from_transport_endpoint(value: Mapping[str, Any]) -> str | None:
    scheme = value.get("scheme")
    host = value.get("host")
    port = value.get("port")
    if not isinstance(scheme, str) or scheme.lower() != "https":
        return None
    if not isinstance(host, str) or not host.strip():
        return None
    if not isinstance(port, int) or isinstance(port, bool) or not (1 <= port <= 65535):
        return None
    formatted_host = f"[{host.strip().lower()}]" if ":" in host else host.strip().lower()
    return f"https://{formatted_host}:{port}"


def _extract_hint_endpoint(raw_hint: Any) -> str | None:
    if not isinstance(raw_hint, Mapping):
        return None
    endpoint = raw_hint.get("endpoint") or raw_hint.get("endpoint_url")
    if isinstance(endpoint, str):
        return endpoint
    body = raw_hint.get("body")
    candidates: list[Any] = [raw_hint.get("transport_endpoint")]
    if isinstance(body, Mapping):
        candidates.append(body.get("transport_endpoint"))
    for candidate in candidates:
        if isinstance(candidate, Mapping):
            endpoint = _endpoint_from_transport_endpoint(candidate)
            if endpoint:
                return endpoint
    return None


def _endpoints_from_known_hints(raw_hints: Any) -> list[str]:
    if not isinstance(raw_hints, list):
        return []
    endpoints: list[str] = []
    for raw_hint in raw_hints[:_MAX_BOOTSTRAP_HINT_SCAN_ITEMS]:
        endpoint = _extract_hint_endpoint(raw_hint)
        if endpoint:
            endpoints.append(endpoint)
    return endpoints[:_MAX_BOOTSTRAP_HINT_SCAN_ITEMS]


def _endpoints_from_fetch_peers(raw_endpoints: Any) -> list[str]:
    if not isinstance(raw_endpoints, list):
        return []
    endpoints = [
        endpoint
        for endpoint in raw_endpoints[:_MAX_BOOTSTRAP_HINT_SCAN_ITEMS]
        if isinstance(endpoint, str)
    ]
    return endpoints[:_MAX_BOOTSTRAP_HINT_SCAN_ITEMS]


def _load_peer_hint_endpoints(path: Path) -> list[str]:
    if not path.exists():
        return []
    try:
        with path.open("rb") as handle:
            if os.fstat(handle.fileno()).st_size > _MAX_BOOTSTRAP_HINT_FILE_BYTES:
                return []
            raw = handle.read(_MAX_BOOTSTRAP_HINT_FILE_BYTES + 1)
    except OSError:
        return []
    if len(raw) > _MAX_BOOTSTRAP_HINT_FILE_BYTES:
        return []
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return []
    if not isinstance(payload, Mapping):
        return []
    schema = payload.get("schema_version")
    if schema == "bootstrap_peer_hints.v0.1":
        return _endpoints_from_known_hints(payload.get("known_peer_hints"))
    if schema == "bootstrap_fetch_peers.v0.1":
        return _endpoints_from_fetch_peers(payload.get("peer_endpoints"))
    return []


def _peer_release_assertion_endpoint(peer_endpoint: str) -> str:
    base = _validate_peer_discovery_endpoint(peer_endpoint)
    return f"{base.rstrip('/')}/.well-known/ilc/software-release/latest.json"


def _try_local_graph_cache(
    state_path: Path | None,
    *,
    now: datetime,
) -> Mapping[str, Any] | None:
    try:
        state = read_upgrade_state(path=state_path)
    except ValueError as exc:
        if str(exc) == "upgrade_state_missing":
            return None
        raise UpgradeCheckError("upgrade_state_corrupt") from exc
    except OSError:
        return None
    if not _is_upgrade_state_fresh(state, now):
        return None
    payload = _cached_release_assertion_payload(state)
    if payload is None:
        return None
    return dict(payload)


def _is_transient_discovery_error(exc: UpgradeCheckError) -> bool:
    return exc.token in {
        "upgrade_check_endpoint_redirect_forbidden",
        "upgrade_check_endpoint_unreachable",
        "upgrade_check_peer_endpoint_invalid_base",
        "upgrade_check_peer_endpoint_invalid_scheme",
        "upgrade_check_peer_endpoint_userinfo_forbidden",
        "upgrade_check_timeout_invalid",
        "upgrade_assertion_release_attestation_missing",
        "upgrade_assertion_literal_mismatch:node_kind",
    }


def is_transient_upgrade_error(exc: UpgradeCheckError) -> bool:
    """Return whether a watcher may retry this token without policy widening."""

    return _is_transient_discovery_error(exc)


def _try_bootstrap_peer_hints(
    hints_paths: Sequence[Path] | None,
    *,
    peer_fetcher: PeerFetchJson,
    timeout_seconds: float,
    validate_fn: Callable[[Mapping[str, Any]], Mapping[str, Any]] = validate_release_assertion,
) -> Mapping[str, Any] | None:
    paths = tuple(hints_paths) if hints_paths is not None else _default_bootstrap_peer_hints_paths()
    seen: set[str] = set()
    peer_endpoints: list[str] = []
    for path in paths:
        for endpoint in _load_peer_hint_endpoints(Path(path).expanduser()):
            if endpoint in seen:
                continue
            seen.add(endpoint)
            peer_endpoints.append(endpoint)
            if len(peer_endpoints) >= UPGRADE_CHECK_PEER_HINT_MAX_PEERS:
                break
        if len(peer_endpoints) >= UPGRADE_CHECK_PEER_HINT_MAX_PEERS:
            break
    headers = {UPGRADE_CHECK_D2D_HOP_COUNT_HEADER: UPGRADE_CHECK_D2D_HOP_COUNT_VALUE}
    timeout = _validate_timeout(timeout_seconds)
    deadline = time.monotonic() + timeout
    for peer_endpoint in peer_endpoints:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        try:
            assertion_endpoint = _peer_release_assertion_endpoint(peer_endpoint)
            payload = peer_fetcher(assertion_endpoint, min(timeout, remaining), headers)
            validate_fn(payload)
            return dict(payload)
        except UpgradeCheckError:
            # Peer candidates are untrusted and isolated. A malformed or
            # cryptographically invalid peer must not poison later candidates.
            continue
        except (OSError, TimeoutError, ValueError):
            continue
    return None


def _try_single_hop_d2d_peers(
    peer_registry: PeerRegistryLike | None,
    *,
    peer_fetcher: PeerFetchJson,
    timeout_seconds: float,
    validate_fn: Callable[[Mapping[str, Any]], Mapping[str, Any]] = validate_release_assertion,
) -> Mapping[str, Any] | None:
    if peer_registry is None:
        return None
    try:
        raw_peers = peer_registry.get_peers()
    except Exception:  # noqa: BLE001 - discovery candidates fail closed to fallback.
        return None
    if isinstance(raw_peers, (str, bytes)) or not isinstance(raw_peers, Sequence):
        return None
    headers = {UPGRADE_CHECK_D2D_HOP_COUNT_HEADER: UPGRADE_CHECK_D2D_HOP_COUNT_VALUE}
    timeout = _validate_timeout(timeout_seconds)
    deadline = time.monotonic() + timeout
    seen: set[str] = set()
    considered = 0
    for raw_endpoint in raw_peers:
        if considered >= UPGRADE_CHECK_PEER_HINT_MAX_PEERS:
            break
        if not isinstance(raw_endpoint, str) or raw_endpoint in seen:
            continue
        seen.add(raw_endpoint)
        considered += 1
        try:
            assertion_endpoint = _peer_release_assertion_endpoint(raw_endpoint)
        except UpgradeCheckError:
            continue
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        try:
            payload = peer_fetcher(assertion_endpoint, min(timeout, remaining), headers)
            validate_fn(payload)
            return dict(payload)
        except UpgradeCheckError:
            # Explicit operator endpoints fail closed elsewhere; discovery
            # peers are bounded candidates and are skipped independently.
            pass
        except (OSError, TimeoutError, ValueError):
            pass
    return None


def _build_upgrade_result(
    payload: Mapping[str, Any],
    *,
    discovery_source: str,
    endpoint: str,
    installed_version_resolver: InstalledVersion | None,
    now: datetime,
    current_policy_evaluation_input: CurrentPolicyEvaluationInput | None = None,
    include_release_assertion_payload: bool = False,
) -> dict[str, Any]:
    assertion_sha256 = _canonical_assertion_sha256(payload)
    assertion_info = validate_release_assertion(
        payload,
        current_policy_evaluation_input=current_policy_evaluation_input,
    )
    eligibility_status = assertion_info["current_release_eligibility_status"]
    eligibility_receipt = dict(assertion_info["current_release_eligibility_evidence"])
    if current_policy_evaluation_input is None:
        eligibility_status = "bounded_compatibility_source"
        eligibility_receipt = {
            **eligibility_receipt,
            "policy_ref": "compatibility:bounded_release_discovery",
            "policy_version": "bounded_release_discovery.v0.1",
            "network_id": "transport_source_only",
            "authoritative_epoch_or_snapshot": "not_authoritative",
            "eligibility_evidence_refs": [f"discovery_source:{discovery_source}"],
            "freshness_rule": "transport freshness is not ILC eligibility authority",
            "evaluated_at": _now_rfc3339(now),
            "withdrawal_resolver_available": False,
        }
    installed_resolver = installed_version_resolver or installed_ilc_core_version
    installed_version = installed_resolver() or "unknown"
    available_version = str(assertion_info["available_version"])
    available_version_key = _version_key(available_version)
    if installed_version == "unknown":
        candidate_version_relation = "unknown"
    else:
        try:
            installed_version_key = _version_key(installed_version)
        except UpgradeCheckError:
            candidate_version_relation = "unknown"
        else:
            if available_version_key > installed_version_key:
                candidate_version_relation = "newer"
            elif available_version_key < installed_version_key:
                candidate_version_relation = "older"
            else:
                candidate_version_relation = "same"
    candidate_upgrade_available = candidate_version_relation == "newer"
    authorized_upgrade_available = (
        candidate_upgrade_available
        and assertion_info["full_release_graph_binding_verified"] is True
        and eligibility_status == "verified_current_policy"
    )
    result = {
        "assertion_cid": assertion_info["assertion_cid"],
        "assertion_sha256": assertion_sha256,
        "available_version": available_version,
        "channel": assertion_info["channel"],
        "checked_at_utc": _now_rfc3339(now),
        "discovery_source": discovery_source,
        "endpoint": endpoint,
        "artifact_cids": assertion_info["artifact_cids"],
        "artifact_release_authority_verified": assertion_info[
            "artifact_release_authority_verified"
        ],
        "current_release_eligibility_evidence": eligibility_receipt,
        "current_release_eligibility_status": eligibility_status,
        "full_release_graph_binding_verified": assertion_info[
            "full_release_graph_binding_verified"
        ],
        "graph_provenance_delegation_evidence": assertion_info[
            "graph_provenance_delegation_evidence"
        ],
        "graph_provenance_delegation_status": assertion_info[
            "graph_provenance_delegation_status"
        ],
        "graph_provenance_delegation_valid_at_submission": assertion_info[
            "graph_provenance_delegation_valid_at_submission"
        ],
        "graph_provenance_status": assertion_info["graph_provenance_status"],
        "graph_provenance_verified": assertion_info["graph_provenance_verified"],
        "graph_submission_provenance_verified": assertion_info[
            "graph_submission_provenance_verified"
        ],
        "installed_version": installed_version,
        "package_name": assertion_info["package_name"],
        "release_authority": assertion_info["release_authority"],
        "release_key_pubkey": assertion_info["release_key_pubkey"],
        "release_signature_verified": assertion_info["release_signature_verified"],
        "signature_scheme": assertion_info["signature_scheme"],
        "candidate_version_relation": candidate_version_relation,
        "candidate_upgrade_available": candidate_upgrade_available,
        "authorized_upgrade_available": authorized_upgrade_available,
        "verified_attestation_count": assertion_info["verified_attestation_count"],
    }
    if include_release_assertion_payload:
        result["release_assertion_payload"] = dict(payload)
    return result


def _write_upgrade_result_preserving_policy_state(
    result: Mapping[str, Any],
    *,
    state_path: Path | None,
) -> None:
    try:
        prior_state = read_upgrade_state(path=state_path)
    except ValueError as exc:
        if str(exc) != "upgrade_state_missing":
            raise
        prior_state = {}
    payload = dict(result)
    prior_marks = prior_state.get(CURRENT_POLICY_HIGH_WATER_MARKS_KEY)
    if prior_marks is not None:
        if not isinstance(prior_marks, Mapping):
            raise ValueError("current_policy_high_water_marks_corrupt")
        payload[CURRENT_POLICY_HIGH_WATER_MARKS_KEY] = dict(prior_marks)

    if result.get("current_release_eligibility_status") in {
        "verified_current_policy",
        "rejected_by_current_policy",
    }:
        receipt = result.get("current_release_eligibility_evidence")
        if not isinstance(receipt, Mapping):
            raise UpgradeCheckError("release_current_policy_evidence_missing")
        sequence = receipt.get("policy_sequence")
        if type(sequence) is not int or sequence < 1:
            raise UpgradeCheckError("release_current_policy_sequence_missing")
        try:
            payload = advance_current_policy_high_water_mark(
                payload,
                policy_id=_require_string(
                    receipt.get("policy_id"),
                    "current_policy.policy_id",
                    max_chars=255,
                ),
                network_id=_require_string(
                    receipt.get("network_id"),
                    "current_policy.network_id",
                    max_chars=255,
                ),
                channel=_require_string(
                    receipt.get("channel"),
                    "current_policy.channel",
                    max_chars=80,
                ),
                accepted_sequence=sequence,
            )
        except ValueError as exc:
            raise UpgradeCheckError(str(exc)) from exc
    write_upgrade_state(payload, path=state_path)


def check_for_upgrade(
    *,
    endpoint: str | None = None,
    state_path: Path | None = None,
    fetcher: FetchJson | None = None,
    peer_fetcher: PeerFetchJson | None = None,
    bootstrap_peer_hints_paths: Sequence[Path] | None = None,
    peer_registry: PeerRegistryLike | None = None,
    evaluation_runtime: UpgradeEvaluationRuntime | None = None,
    timeout_seconds: float = UPGRADE_CHECK_TIMEOUT_SECONDS,
    current_policy_evaluation_input: CurrentPolicyEvaluationInput | None = None,
    include_release_assertion_payload: bool = False,
) -> dict[str, Any]:
    """Fetch, verify, compare, and cache the current upgrade-check result."""

    explicit_endpoint = endpoint or _endpoint_from_env()
    fetch = fetcher or fetch_upgrade_assertion_json
    peer_fetch = peer_fetcher or _fetch_peer_upgrade_assertion_json
    timeout = _validate_timeout(timeout_seconds)
    runtime = evaluation_runtime or UpgradeEvaluationRuntime()
    now = (runtime.now_fn or _now_utc)()
    if explicit_endpoint:
        selected_endpoint = _validate_endpoint(explicit_endpoint)
        payload = dict(fetch(selected_endpoint, timeout))
        result = _build_upgrade_result(
            payload,
            discovery_source="explicit_endpoint",
            endpoint=selected_endpoint,
            installed_version_resolver=runtime.installed_version_resolver,
            now=now,
            current_policy_evaluation_input=current_policy_evaluation_input,
            include_release_assertion_payload=include_release_assertion_payload,
        )
        _write_upgrade_result_preserving_policy_state(result, state_path=state_path)
        return result

    cached_payload = _try_local_graph_cache(state_path, now=now)
    if cached_payload is not None:
        result = _build_upgrade_result(
            cached_payload,
            discovery_source="local_graph_cache",
            endpoint="local_graph_cache",
            installed_version_resolver=runtime.installed_version_resolver,
            now=now,
            current_policy_evaluation_input=current_policy_evaluation_input,
            include_release_assertion_payload=include_release_assertion_payload,
        )
        _write_upgrade_result_preserving_policy_state(result, state_path=state_path)
        return result

    peer_payload = _try_bootstrap_peer_hints(
        bootstrap_peer_hints_paths,
        peer_fetcher=peer_fetch,
        timeout_seconds=timeout,
    )
    if peer_payload is not None:
        result = _build_upgrade_result(
            peer_payload,
            discovery_source="bootstrap_peer_hint",
            endpoint="bootstrap_peer_hint",
            installed_version_resolver=runtime.installed_version_resolver,
            now=now,
            current_policy_evaluation_input=current_policy_evaluation_input,
            include_release_assertion_payload=include_release_assertion_payload,
        )
        _write_upgrade_result_preserving_policy_state(result, state_path=state_path)
        return result

    single_hop_payload = _try_single_hop_d2d_peers(
        peer_registry,
        peer_fetcher=peer_fetch,
        timeout_seconds=timeout,
    )
    if single_hop_payload is not None:
        result = _build_upgrade_result(
            single_hop_payload,
            discovery_source="single_hop_d2d",
            endpoint="single_hop_d2d",
            installed_version_resolver=runtime.installed_version_resolver,
            now=now,
            current_policy_evaluation_input=current_policy_evaluation_input,
            include_release_assertion_payload=include_release_assertion_payload,
        )
        _write_upgrade_result_preserving_policy_state(result, state_path=state_path)
        return result

    selected_endpoint = DEFAULT_UPGRADE_CHECK_ENDPOINT
    payload = dict(fetch(selected_endpoint, timeout))
    result = _build_upgrade_result(
        payload,
        discovery_source="https_fallback",
        endpoint=selected_endpoint,
        installed_version_resolver=runtime.installed_version_resolver,
        now=now,
        current_policy_evaluation_input=current_policy_evaluation_input,
        include_release_assertion_payload=include_release_assertion_payload,
    )
    _write_upgrade_result_preserving_policy_state(result, state_path=state_path)
    return result


__all__ = [
    "UpgradeCheckError",
    "UpgradeEvaluationRuntime",
    "check_for_upgrade",
    "fetch_upgrade_assertion_json",
    "installed_ilc_core_version",
    "is_transient_upgrade_error",
    "require_arbitrary_source_release_authorized",
    "validate_release_assertion",
]
