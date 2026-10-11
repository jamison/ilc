# SPDX-License-Identifier: AGPL-3.0-only
"""Read-only upgrade check against signed homoiconic release assertions."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import math
import re
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

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
from ilc_core.release.upgrade_state import read_upgrade_state, write_upgrade_state


_CID_LIKE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{2,255}$")
_HEX_32_BYTES_RE = re.compile(r"^[0-9a-f]{64}$")
_HEX_64_BYTES_RE = re.compile(r"^[0-9a-f]{128}$")
_GIT_COMMIT_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_UTC_Z_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z$")
_VERSION_RE = re.compile(r"^[0-9]+(?:\.[0-9]+){1,3}$")
_ARTIFACT_ID_RE = re.compile(r"^ilc-artifact:[a-z0-9][a-z0-9-]*@phase-[1-9][0-9]*$")
_ALLOWED_CHANNELS = frozenset({"public_rc", "testnet", "mainnet", "dev", "stable", "rc"})
_MAX_BOOTSTRAP_HINT_FILE_BYTES = 1_000_000
_MAX_BOOTSTRAP_HINT_SCAN_ITEMS = UPGRADE_CHECK_PEER_HINT_MAX_PEERS * 2

FetchJson = Callable[[str, float], Mapping[str, Any]]
PeerFetchJson = Callable[[str, float, Mapping[str, str]], Mapping[str, Any]]
InstalledVersion = Callable[[], str | None]
NowFn = Callable[[], datetime]


class PeerRegistryLike(Protocol):
    """Minimal read-only peer registry surface used by upgrade discovery."""

    def get_peers(self) -> Sequence[str]:
        """Return currently promoted peer endpoints."""


class UpgradeCheckError(ValueError):
    """Typed upgrade-check error carrying a stable token."""

    def __init__(self, token: str, message: str | None = None) -> None:
        super().__init__(message or token)
        self.token = token
        self.message = message or token


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
        return None


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"upgrade_assertion_non_finite_json:{value}")


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


def _require_string(value: Any, field: str, *, max_chars: int = 512) -> str:
    if not isinstance(value, str) or not value:
        raise UpgradeCheckError(f"upgrade_assertion_invalid_string:{field}")
    if len(value) > max_chars:
        raise UpgradeCheckError(f"upgrade_assertion_string_too_long:{field}")
    return value


def _require_literal(value: Any, field: str, expected: str) -> str:
    text = _require_string(value, field)
    if text != expected:
        raise UpgradeCheckError(f"upgrade_assertion_literal_mismatch:{field}")
    return text


def _require_hex(value: Any, field: str, pattern: re.Pattern[str]) -> str:
    text = _require_string(value, field)
    if pattern.fullmatch(text) is None:
        raise UpgradeCheckError(f"upgrade_assertion_invalid_hex:{field}")
    return text


def _require_cid_like(value: Any, field: str) -> str:
    text = _require_string(value, field)
    if _CID_LIKE_RE.fullmatch(text) is None:
        raise UpgradeCheckError(f"upgrade_assertion_invalid_cid:{field}")
    return text


def _require_timestamp(value: Any, field: str) -> str:
    text = _require_string(value, field)
    if _UTC_Z_RE.fullmatch(text) is None:
        raise UpgradeCheckError(f"upgrade_assertion_invalid_timestamp:{field}")
    return text


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
    import os

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
    if "software_release_node" in payload:
        node = payload.get("software_release_node")
    else:
        node = payload
    if not isinstance(node, Mapping):
        raise UpgradeCheckError("upgrade_assertion_release_node_missing")
    return node


def _extract_attestation_edges(payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    edges = payload.get("release_attestation_edges")
    if edges is None and "release_attestation_edge" in payload:
        edges = [payload.get("release_attestation_edge")]
    if not isinstance(edges, list) or not edges:
        raise UpgradeCheckError("upgrade_assertion_release_attestation_missing")
    result: list[Mapping[str, Any]] = []
    for edge in edges:
        if not isinstance(edge, Mapping):
            raise UpgradeCheckError("upgrade_assertion_release_attestation_invalid")
        result.append(edge)
    return result


def _validate_release_node(node: Mapping[str, Any], expected_pubkey: str) -> dict[str, Any]:
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
    artifact_cids = node.get("artifact_cids")
    if not isinstance(artifact_cids, list) or not artifact_cids:
        raise UpgradeCheckError("upgrade_assertion_artifact_cids_invalid")
    artifact_cids = [_require_cid_like(value, "artifact_cids") for value in artifact_cids]
    build_recipe_cid = _require_cid_like(node.get("build_recipe_cid"), "build_recipe_cid")
    release_key_pubkey = _require_string(node.get("release_key_pubkey"), "release_key_pubkey")
    if release_key_pubkey != expected_pubkey:
        raise UpgradeCheckError("upgrade_assertion_release_key_mismatch")
    release_signature_ref = _require_string(
        node.get("release_signature_ref"),
        "release_signature_ref",
    )
    changelog_hash = _require_hex(node.get("changelog_hash"), "changelog_hash", _HEX_32_BYTES_RE)
    cid = node.get("cid")
    if cid is not None:
        cid = _require_cid_like(cid, "cid")
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


def _verify_release_attestation_edge(
    edge: Mapping[str, Any],
    *,
    node_info: Mapping[str, Any],
    expected_pubkey: str,
) -> dict[str, str]:
    _require_literal(edge.get("edge_type"), "edge_type", "RELEASE_ATTESTS_ARTIFACT")
    _require_literal(
        edge.get("schema_version"),
        "schema_version",
        "release_attestation_edge.v0.1",
    )
    source = _require_cid_like(edge.get("source"), "source")
    node_cid = node_info.get("cid")
    if isinstance(node_cid, str) and source != node_cid:
        raise UpgradeCheckError("upgrade_assertion_attestation_source_mismatch")
    target = _require_cid_like(edge.get("target"), "target")
    if target not in node_info["artifact_cids"]:
        raise UpgradeCheckError("upgrade_assertion_attestation_target_mismatch")
    artifact_id = _require_string(edge.get("artifact_id"), "artifact_id", max_chars=160)
    if _ARTIFACT_ID_RE.fullmatch(artifact_id) is None:
        raise UpgradeCheckError("upgrade_assertion_artifact_id_invalid")
    artifact_sha256 = _require_hex(edge.get("artifact_sha256"), "artifact_sha256", _HEX_32_BYTES_RE)
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
    release_key_registration_ref = str(
        edge.get("release_key_registration_ref") or DEFAULT_RELEASE_KEY_REGISTRATION_REF
    )
    genesis_lineage_ref = str(edge.get("genesis_lineage_ref") or DEFAULT_GENESIS_LINEAGE_REF)
    prior_release_envelope_ref = str(
        edge.get("prior_release_envelope_ref") or DEFAULT_PRIOR_RELEASE_ENVELOPE_REF
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
    _require_literal(edge.get("signing_algorithm"), "signing_algorithm", "Ed25519")
    signer_public_key_hex = _require_string(edge.get("signer_public_key_hex"), "signer_public_key_hex")
    if signer_public_key_hex != expected_pubkey:
        raise UpgradeCheckError("upgrade_assertion_release_signer_mismatch")
    signature_hex = _require_hex(edge.get("signature_hex"), "signature_hex", _HEX_64_BYTES_RE)
    _require_timestamp(edge.get("attestation_date"), "attestation_date")
    try:
        public_key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(expected_pubkey))
        public_key.verify(bytes.fromhex(signature_hex), bytes.fromhex(signed_preimage_sha256))
    except (InvalidSignature, ValueError) as exc:
        raise UpgradeCheckError("upgrade_assertion_release_signature_verify_failed") from exc
    return {
        "artifact_sha256": artifact_sha256,
        "artifact_id": artifact_id,
        "signed_preimage_domain": signed_preimage_domain,
        "signed_preimage_sha256": signed_preimage_sha256,
        "signer_public_key_hex": signer_public_key_hex,
        "target": target,
    }


def validate_release_assertion(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Validate release assertion shape and mandatory Ed25519 release authority."""

    if not isinstance(payload, Mapping):
        raise UpgradeCheckError("upgrade_assertion_not_object")
    _assert_no_floats(payload)
    expected_pubkey = release_signer_public_key_hex()
    node = _extract_release_node(payload)
    edges = _extract_attestation_edges(payload)
    node_info = _validate_release_node(node, expected_pubkey)
    verified_edges = [
        _verify_release_attestation_edge(edge, node_info=node_info, expected_pubkey=expected_pubkey)
        for edge in edges
    ]
    assertion_cid = payload.get("assertion_cid") or node_info.get("cid")
    if assertion_cid is not None:
        assertion_cid = _require_cid_like(assertion_cid, "assertion_cid")
    graph_envelope = payload.get("native_submit_envelope")
    graph_verified = False
    graph_status = "not_present_read_only_phase"
    if graph_envelope is not None:
        graph_status = "present_not_validated_in_phase"
    return {
        "assertion_cid": assertion_cid or "",
        "available_version": node_info["version"],
        "channel": node_info["release_channel"],
        "graph_provenance_status": graph_status,
        "graph_provenance_verified": graph_verified,
        "package_name": node_info["package_name"],
        "release_authority": "ed25519_phase_1335",
        "release_key_pubkey": expected_pubkey,
        "release_signature_verified": True,
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


def _load_peer_hint_endpoints(path: Path) -> list[str]:
    if not path.exists():
        return []
    try:
        if path.stat().st_size > _MAX_BOOTSTRAP_HINT_FILE_BYTES:
            return []
    except OSError:
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return []
    if not isinstance(payload, Mapping):
        return []
    schema = payload.get("schema_version")
    endpoints: list[str] = []
    if schema == "bootstrap_peer_hints.v0.1":
        raw_hints = payload.get("known_peer_hints")
        if isinstance(raw_hints, list):
            for raw_hint in raw_hints[:_MAX_BOOTSTRAP_HINT_SCAN_ITEMS]:
                endpoint = _extract_hint_endpoint(raw_hint)
                if endpoint:
                    endpoints.append(endpoint)
                if len(endpoints) >= _MAX_BOOTSTRAP_HINT_SCAN_ITEMS:
                    break
    elif schema == "bootstrap_fetch_peers.v0.1":
        raw_endpoints = payload.get("peer_endpoints")
        if isinstance(raw_endpoints, list):
            for endpoint in raw_endpoints[:_MAX_BOOTSTRAP_HINT_SCAN_ITEMS]:
                if isinstance(endpoint, str):
                    endpoints.append(endpoint)
                if len(endpoints) >= _MAX_BOOTSTRAP_HINT_SCAN_ITEMS:
                    break
    return endpoints


def _peer_release_assertion_endpoint(peer_endpoint: str) -> str:
    base = _validate_peer_discovery_endpoint(peer_endpoint)
    return f"{base.rstrip('/')}/.well-known/ilc/software-release/latest.json"


def _try_local_graph_cache(
    state_path: Path | None,
    *,
    now: datetime,
    validate_fn: Callable[[Mapping[str, Any]], Mapping[str, Any]] = validate_release_assertion,
) -> Mapping[str, Any] | None:
    try:
        state = read_upgrade_state(path=state_path)
        if not _is_upgrade_state_fresh(state, now):
            return None
        payload = _cached_release_assertion_payload(state)
        if payload is None:
            return None
        validate_fn(payload)
        return dict(payload)
    except Exception:  # noqa: BLE001 - discovery candidates fail closed to fallback.
        return None


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
    for peer_endpoint in peer_endpoints:
        try:
            assertion_endpoint = _peer_release_assertion_endpoint(peer_endpoint)
            payload = peer_fetcher(assertion_endpoint, timeout, headers)
            validate_fn(payload)
            return dict(payload)
        except Exception:  # noqa: BLE001 - try the next candidate, then fallback.
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
        try:
            payload = peer_fetcher(assertion_endpoint, timeout, headers)
            validate_fn(payload)
            return dict(payload)
        except Exception:  # noqa: BLE001 - try the next candidate, then fallback.
            pass
    return None


def _build_upgrade_result(
    payload: Mapping[str, Any],
    *,
    discovery_source: str,
    endpoint: str,
    installed_version_resolver: InstalledVersion | None,
    now: datetime,
) -> dict[str, Any]:
    assertion_sha256 = _canonical_assertion_sha256(payload)
    assertion_info = validate_release_assertion(payload)
    installed_resolver = installed_version_resolver or installed_ilc_core_version
    installed_version = installed_resolver() or "unknown"
    available_version = str(assertion_info["available_version"])
    upgrade_available = (
        installed_version == "unknown"
        or _version_key(available_version) > _version_key(installed_version)
    )
    return {
        "assertion_cid": assertion_info["assertion_cid"],
        "assertion_sha256": assertion_sha256,
        "available_version": available_version,
        "channel": assertion_info["channel"],
        "checked_at_utc": _now_rfc3339(now),
        "discovery_source": discovery_source,
        "endpoint": endpoint,
        "graph_provenance_status": assertion_info["graph_provenance_status"],
        "graph_provenance_verified": assertion_info["graph_provenance_verified"],
        "installed_version": installed_version,
        "package_name": assertion_info["package_name"],
        "release_authority": assertion_info["release_authority"],
        "release_key_pubkey": assertion_info["release_key_pubkey"],
        "release_signature_verified": assertion_info["release_signature_verified"],
        "upgrade_available": upgrade_available,
        "verified_attestation_count": assertion_info["verified_attestation_count"],
    }


def check_for_upgrade(
    *,
    endpoint: str | None = None,
    state_path: Path | None = None,
    fetcher: FetchJson | None = None,
    peer_fetcher: PeerFetchJson | None = None,
    bootstrap_peer_hints_paths: Sequence[Path] | None = None,
    peer_registry: PeerRegistryLike | None = None,
    installed_version_resolver: InstalledVersion | None = None,
    now_fn: NowFn | None = None,
    timeout_seconds: float = UPGRADE_CHECK_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Fetch, verify, compare, and cache the current upgrade-check result."""

    explicit_endpoint = endpoint or _endpoint_from_env()
    fetch = fetcher or fetch_upgrade_assertion_json
    peer_fetch = peer_fetcher or _fetch_peer_upgrade_assertion_json
    timeout = _validate_timeout(timeout_seconds)
    now = (now_fn or _now_utc)()
    if explicit_endpoint:
        selected_endpoint = _validate_endpoint(explicit_endpoint)
        payload = dict(fetch(selected_endpoint, timeout))
        result = _build_upgrade_result(
            payload,
            discovery_source="explicit_endpoint",
            endpoint=selected_endpoint,
            installed_version_resolver=installed_version_resolver,
            now=now,
        )
        write_upgrade_state(result, path=state_path)
        return result

    cached_payload = _try_local_graph_cache(state_path, now=now)
    if cached_payload is not None:
        result = _build_upgrade_result(
            cached_payload,
            discovery_source="local_graph_cache",
            endpoint="local_graph_cache",
            installed_version_resolver=installed_version_resolver,
            now=now,
        )
        write_upgrade_state(result, path=state_path)
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
            installed_version_resolver=installed_version_resolver,
            now=now,
        )
        write_upgrade_state(result, path=state_path)
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
            installed_version_resolver=installed_version_resolver,
            now=now,
        )
        write_upgrade_state(result, path=state_path)
        return result

    selected_endpoint = DEFAULT_UPGRADE_CHECK_ENDPOINT
    payload = dict(fetch(selected_endpoint, timeout))
    result = _build_upgrade_result(
        payload,
        discovery_source="https_fallback",
        endpoint=selected_endpoint,
        installed_version_resolver=installed_version_resolver,
        now=now,
    )
    write_upgrade_state(result, path=state_path)
    return result


__all__ = [
    "UpgradeCheckError",
    "check_for_upgrade",
    "fetch_upgrade_assertion_json",
    "installed_ilc_core_version",
    "validate_release_assertion",
]
