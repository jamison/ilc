# SPDX-License-Identifier: AGPL-3.0-only
"""Correctness-only release artifact fetch and verification."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urljoin, urlparse

import requests

from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.release.current_policy import CurrentPolicyEvaluationInput
from ilc_core.release.upgrade_check import (
    UpgradeCheckError,
    require_arbitrary_source_release_authorized,
    validate_release_assertion,
)


ARTIFACT_DOWNLOAD_CHUNK_BYTES = 65_536
ARTIFACT_DOWNLOAD_TIMEOUT_SECONDS = 30.0
ARTIFACT_DOWNLOAD_EXTRA_BYTES = 1_048_576
MAX_ARTIFACT_DOWNLOAD_BYTES = 1_073_741_824
ARTIFACT_DISK_SAFETY_BYTES = 16_777_216
MAX_ARTIFACT_SOURCE_URLS = 8
MAX_ARTIFACT_REDIRECTS = 3
MAX_ARTIFACT_FILENAME_CHARS = 255
_HEX_32_BYTES_RE = re.compile(r"^[0-9a-f]{64}$")
_REDIRECT_STATUS_CODES = frozenset({301, 302, 303, 307, 308})
_ALLOWED_CROSS_HOST_REDIRECTS = frozenset(
    {
        ("github.com", "release-assets.githubusercontent.com"),
        ("pypi.org", "files.pythonhosted.org"),
    }
)


class ArtifactFetchError(ValueError):
    """Stable-token error for release artifact fetch failures."""

    def __init__(self, token: str, message: str | None = None) -> None:
        super().__init__(message or token)
        self.token = token
        self.message = message or token


def _require_mapping(value: Any, token: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ArtifactFetchError(token)
    return value


def _require_string(value: Any, token: str, *, max_chars: int = 2048) -> str:
    if not isinstance(value, str) or not value:
        raise ArtifactFetchError(token)
    if len(value) > max_chars:
        raise ArtifactFetchError(token)
    return value


def _require_sha256(value: Any, token: str) -> str:
    text = _require_string(value, token, max_chars=64)
    if _HEX_32_BYTES_RE.fullmatch(text) is None:
        raise ArtifactFetchError(token)
    return text


def _require_size(value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ArtifactFetchError("artifact_fetch_size_missing")
    if value > MAX_ARTIFACT_DOWNLOAD_BYTES:
        raise ArtifactFetchError("artifact_fetch_size_exceeds_absolute_max")
    return value


def _validate_filename(value: Any) -> str:
    filename = _require_string(
        value,
        "artifact_fetch_filename_missing",
        max_chars=MAX_ARTIFACT_FILENAME_CHARS,
    )
    if (
        filename in {".", ".."}
        or Path(filename).is_absolute()
        or Path(filename).name != filename
        or "/" in filename
        or "\\" in filename
        or any(ord(character) < 32 or ord(character) == 127 for character in filename)
    ):
        raise ArtifactFetchError("artifact_fetch_filename_invalid")
    return filename


def _artifact_body_for_cid(artifact_node: Mapping[str, Any]) -> dict[str, Any]:
    return {str(key): value for key, value in artifact_node.items() if key != "cid"}


def _verify_artifact_node_cid(artifact_node: Mapping[str, Any]) -> str:
    expected_cid = _require_string(artifact_node.get("cid"), "artifact_fetch_artifact_cid_missing")
    try:
        observed_cid = node_id_from_obj(_artifact_body_for_cid(artifact_node))
    except (TypeError, ValueError) as exc:
        raise ArtifactFetchError("artifact_fetch_cid_algorithm_unresolved") from exc
    if observed_cid != expected_cid:
        raise ArtifactFetchError("artifact_fetch_artifact_cid_mismatch")
    return expected_cid


def _validated_wheel_artifact(
    release_assertion: Mapping[str, Any],
    assertion_info: Mapping[str, Any],
) -> Mapping[str, Any]:
    release_node = _require_mapping(
        release_assertion.get("software_release_node"),
        "artifact_fetch_release_node_missing",
    )
    package_name = _require_string(
        assertion_info.get("package_name") or release_node.get("package_name"),
        "artifact_fetch_package_name_missing",
        max_chars=160,
    )
    package_version = _require_string(
        assertion_info.get("available_version") or release_node.get("version"),
        "artifact_fetch_package_version_missing",
        max_chars=80,
    )
    artifact_nodes = release_assertion.get("artifact_nodes")
    if not isinstance(artifact_nodes, list) or not artifact_nodes:
        raise ArtifactFetchError("artifact_fetch_artifact_nodes_missing")
    wheel_nodes = [
        _require_mapping(node, "artifact_fetch_artifact_node_invalid")
        for node in artifact_nodes
        if isinstance(node, Mapping) and node.get("artifact_type") == "wheel"
    ]
    if not wheel_nodes:
        raise ArtifactFetchError("artifact_fetch_wheel_artifact_missing")
    matching_wheel_nodes = [
        node
        for node in wheel_nodes
        if node.get("package_name") == package_name and node.get("package_version") == package_version
    ]
    if not matching_wheel_nodes:
        raise ArtifactFetchError("artifact_fetch_wheel_artifact_mismatch")
    if len(matching_wheel_nodes) != 1:
        raise ArtifactFetchError("artifact_fetch_multiple_wheel_artifacts")
    artifact_node = matching_wheel_nodes[0]
    _verify_artifact_node_cid(artifact_node)
    expected_cid = _require_string(artifact_node.get("cid"), "artifact_fetch_artifact_cid_missing")
    expected_sha256 = _require_sha256(artifact_node.get("sha256"), "artifact_fetch_sha256_missing")
    edges = release_assertion.get("release_attestation_edges")
    if not isinstance(edges, list):
        raise ArtifactFetchError("artifact_fetch_release_attestation_missing")
    matching_edges = [
        edge
        for edge in edges
        if isinstance(edge, Mapping)
        and edge.get("target") == expected_cid
        and edge.get("artifact_sha256") == expected_sha256
    ]
    if not matching_edges:
        raise ArtifactFetchError("artifact_fetch_artifact_not_attested")
    _require_size(artifact_node.get("size_bytes"))
    return artifact_node


def _validated_binary_tarball_artifact(
    release_assertion: Mapping[str, Any],
) -> Mapping[str, Any]:
    artifact_nodes = release_assertion.get("artifact_nodes")
    if not isinstance(artifact_nodes, list) or not artifact_nodes:
        raise ArtifactFetchError("artifact_fetch_artifact_nodes_missing")
    tarball_nodes = [
        _require_mapping(node, "artifact_fetch_artifact_node_invalid")
        for node in artifact_nodes
        if isinstance(node, Mapping) and node.get("artifact_type") == "binary_tarball"
    ]
    if not tarball_nodes:
        raise ArtifactFetchError("artifact_fetch_binary_tarball_missing")
    if len(tarball_nodes) != 1:
        raise ArtifactFetchError("artifact_fetch_multiple_binary_tarballs")
    artifact_node = tarball_nodes[0]
    _verify_artifact_node_cid(artifact_node)
    expected_cid = _require_string(
        artifact_node.get("cid"),
        "artifact_fetch_artifact_cid_missing",
    )
    expected_sha256 = _require_sha256(
        artifact_node.get("sha256"),
        "artifact_fetch_sha256_missing",
    )
    edges = release_assertion.get("release_attestation_edges")
    if not isinstance(edges, list):
        raise ArtifactFetchError("artifact_fetch_release_attestation_missing")
    matching_edges = [
        edge
        for edge in edges
        if isinstance(edge, Mapping)
        and edge.get("target") == expected_cid
        and edge.get("artifact_sha256") == expected_sha256
    ]
    if not matching_edges:
        raise ArtifactFetchError("artifact_fetch_artifact_not_attested")
    _require_size(artifact_node.get("size_bytes"))
    return artifact_node


def _candidate_urls(artifact_node: Mapping[str, Any]) -> list[str]:
    urls: list[str] = []
    source_urls = artifact_node.get("source_urls")
    if isinstance(source_urls, list):
        for source_url in source_urls:
            if isinstance(source_url, str) and source_url not in urls:
                urls.append(source_url)
    pypi_url = artifact_node.get("pypi_url")
    if isinstance(pypi_url, str) and pypi_url not in urls:
        urls.append(pypi_url)
    if not urls:
        raise ArtifactFetchError("artifact_fetch_source_unavailable")
    if len(urls) > MAX_ARTIFACT_SOURCE_URLS:
        raise ArtifactFetchError("artifact_fetch_too_many_sources")
    return [_validate_download_url(url) for url in urls]


def _validate_download_url(url: str) -> str:
    text = _require_string(url, "artifact_fetch_source_url_invalid")
    parsed = urlparse(text)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ArtifactFetchError("artifact_fetch_source_url_invalid")
    if parsed.username is not None or parsed.password is not None:
        raise ArtifactFetchError("artifact_fetch_source_url_invalid")
    if parsed.fragment:
        raise ArtifactFetchError("artifact_fetch_source_url_invalid")
    return text


def _require_download_space(expected_size: int) -> None:
    try:
        free = shutil.disk_usage(tempfile.gettempdir()).free
    except OSError as exc:
        raise ArtifactFetchError("artifact_fetch_free_space_unavailable") from exc
    required = expected_size + ARTIFACT_DOWNLOAD_EXTRA_BYTES + ARTIFACT_DISK_SAFETY_BYTES
    if free < required:
        raise ArtifactFetchError("artifact_fetch_insufficient_free_space")


def _validated_redirect_url(current_url: str, location: Any) -> str:
    if not isinstance(location, str) or not location:
        raise ArtifactFetchError("artifact_fetch_redirect_location_invalid")
    target_url = _validate_download_url(urljoin(current_url, location))
    current = urlparse(current_url)
    target = urlparse(target_url)
    current_host = (current.hostname or "").lower()
    target_host = (target.hostname or "").lower()
    if current_host != target_host and (
        current_host,
        target_host,
    ) not in _ALLOWED_CROSS_HOST_REDIRECTS:
        raise ArtifactFetchError("artifact_fetch_redirect_target_forbidden")
    return target_url


def _open_download_response(url: str):
    current_url = _validate_download_url(url)
    for redirect_count in range(MAX_ARTIFACT_REDIRECTS + 1):
        try:
            response = requests.get(
                current_url,
                stream=True,
                timeout=ARTIFACT_DOWNLOAD_TIMEOUT_SECONDS,
                verify=True,
                allow_redirects=False,
            )
        except requests.RequestException as exc:
            raise ArtifactFetchError("artifact_fetch_source_failed") from exc
        if response.status_code not in _REDIRECT_STATUS_CODES:
            return response
        if redirect_count == MAX_ARTIFACT_REDIRECTS:
            response.close()
            raise ArtifactFetchError("artifact_fetch_redirect_limit_exceeded")
        try:
            next_url = _validated_redirect_url(
                current_url,
                response.headers.get("Location"),
            )
        finally:
            response.close()
        current_url = next_url
    raise ArtifactFetchError("artifact_fetch_redirect_limit_exceeded")


def _validate_content_length(response: Any, *, cap: int) -> None:
    declared = response.headers.get("Content-Length")
    if declared is None:
        return
    try:
        declared_size = int(declared)
    except ValueError as exc:
        raise ArtifactFetchError("artifact_fetch_content_length_invalid") from exc
    if declared_size < 0 or declared_size > cap:
        raise ArtifactFetchError("artifact_fetch_size_exceeded")


def _write_response_body(response: Any, destination: Path, *, cap: int) -> None:
    total = 0
    try:
        with destination.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=ARTIFACT_DOWNLOAD_CHUNK_BYTES):
                if not chunk:
                    continue
                total += len(chunk)
                if total > cap:
                    raise ArtifactFetchError("artifact_fetch_size_exceeded")
                handle.write(chunk)
    except requests.RequestException as exc:
        raise ArtifactFetchError("artifact_fetch_source_failed") from exc


def _download_to_temp(url: str, destination: Path, *, expected_size: int) -> None:
    cap = expected_size + ARTIFACT_DOWNLOAD_EXTRA_BYTES
    response = _open_download_response(url)
    try:
        if response.status_code != 200:
            raise ArtifactFetchError("artifact_fetch_source_failed")
        _validate_content_length(response, cap=cap)
        _write_response_body(response, destination, cap=cap)
    finally:
        response.close()


def _download_artifact_bytes(url: str, destination: Path, *, expected_size: int) -> None:
    """Private transport primitive below the authorization boundary."""

    _download_to_temp(url, destination, expected_size=expected_size)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(ARTIFACT_DOWNLOAD_CHUNK_BYTES)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _authorize_release(
    release_assertion: Mapping[str, Any],
    policy_evaluation_input: CurrentPolicyEvaluationInput | None,
) -> Mapping[str, Any]:
    if policy_evaluation_input is None:
        raise ArtifactFetchError("artifact_fetch_eligibility_unresolved")
    try:
        assertion_info = validate_release_assertion(
            release_assertion,
            current_policy_evaluation_input=policy_evaluation_input,
        )
        require_arbitrary_source_release_authorized(assertion_info)
    except UpgradeCheckError as exc:
        raise ArtifactFetchError(
            "artifact_fetch_eligibility_gate_failed",
            f"artifact_fetch_eligibility_gate_failed:{exc.token}",
        ) from exc
    return assertion_info


def _fetch_validated_artifact(artifact_node: Mapping[str, Any]) -> Path:
    expected_sha256 = _require_sha256(artifact_node.get("sha256"), "artifact_fetch_sha256_missing")
    expected_size = _require_size(artifact_node.get("size_bytes"))
    filename = _validate_filename(artifact_node.get("filename"))
    urls = _candidate_urls(artifact_node)
    _require_download_space(expected_size)
    temp_dir = Path(tempfile.mkdtemp(prefix="ilc-artifact-fetch-"))
    try:
        last_error: ArtifactFetchError | None = None
        for url in urls:
            partial_path = temp_dir / f"{filename}.part"
            verified_path = temp_dir / filename
            try:
                _download_artifact_bytes(url, partial_path, expected_size=expected_size)
                if partial_path.stat().st_size != expected_size:
                    raise ArtifactFetchError("artifact_fetch_size_mismatch")
                if _sha256_file(partial_path) != expected_sha256:
                    raise ArtifactFetchError("artifact_fetch_sha256_mismatch")
                os.replace(partial_path, verified_path)
                return verified_path
            except ArtifactFetchError as exc:
                last_error = exc
                try:
                    partial_path.unlink()
                except FileNotFoundError:
                    pass
                continue
        if last_error is not None:
            raise ArtifactFetchError("artifact_fetch_all_sources_failed") from last_error
        raise ArtifactFetchError("artifact_fetch_all_sources_failed")
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def fetch_and_verify(
    release_assertion: Mapping[str, Any],
    *,
    policy_evaluation_input: CurrentPolicyEvaluationInput | None = None,
) -> Path:
    """Fetch the release wheel and return a verified temp path.

    The returned path lives in a temporary directory. Callers that install the
    wheel are responsible for removing the parent directory after use.
    """

    assertion_info = _authorize_release(release_assertion, policy_evaluation_input)
    artifact_node = _validated_wheel_artifact(release_assertion, assertion_info)
    return _fetch_validated_artifact(artifact_node)


def fetch_and_verify_binary_tarball(
    release_assertion: Mapping[str, Any],
    *,
    policy_evaluation_input: CurrentPolicyEvaluationInput | None = None,
) -> Path:
    """Fetch the sole authorized ``binary_tarball`` artifact.

    Authorization is evaluated before artifact selection, URL inspection,
    allocation, or network I/O. The caller owns cleanup of the returned path's
    temporary parent directory.
    """

    _authorize_release(release_assertion, policy_evaluation_input)
    artifact_node = _validated_binary_tarball_artifact(release_assertion)
    return _fetch_validated_artifact(artifact_node)


__all__ = [
    "ArtifactFetchError",
    "MAX_ARTIFACT_DOWNLOAD_BYTES",
    "fetch_and_verify",
    "fetch_and_verify_binary_tarball",
]
