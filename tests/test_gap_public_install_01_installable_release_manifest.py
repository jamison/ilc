from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from ilc_core.release.installable_release_manifest import (
    InstallableReleaseManifestError,
    canonical_installable_release_manifest_bytes,
    load_installable_release_manifest,
    validate_installable_release_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
INSTANCE_PATH = (
    ROOT
    / "docs/specs/ilc_installable_release_manifest_ilc_core_020_GAP_PUBLIC_INSTALL_01_v0.1.json"
)
SCHEMA_PATH = (
    ROOT / "docs/specs/ilc_installable_release_manifest_schema_GAP_PUBLIC_INSTALL_01_v0.1.md"
)
PHASE_1213_SCHEMA_PATH = ROOT / "docs/specs/ilc_release_artifact_manifest_schema_1213_v0.1.md"
PYPROJECT_PATH = ROOT / "pyproject.toml"

PHASE_1213_SCHEMA_SHA256 = (
    "7860f5746570d20e8272d7d8c6f0e3dd2a859a9b5aac23141af0a28c1ff0c9a7"
)
EXPECTED_WHEEL_SHA256 = (
    "sha256:80e53ea18aea0a7c474400a41e20f346c00ee3e36e8f0dd60f233cca2b0e2f1d"
)
EXPECTED_SDIST_SHA256 = (
    "sha256:95c73d42799d3a662b14c4b81da8781df861c222f1e04c458dd1b4ac318e2ab4"
)


def _manifest() -> dict:
    return load_installable_release_manifest(INSTANCE_PATH)


def _wheel_manifest() -> dict:
    manifest = _manifest()
    manifest["artifacts"] = [
        artifact
        for artifact in manifest["artifacts"]
        if artifact["artifact_type"] == "python_wheel"
    ]
    return manifest


def _cli_binary_manifest() -> dict:
    manifest = copy.deepcopy(_manifest())
    artifact = manifest["artifacts"][0]
    artifact["artifact_id"] = "ilc-artifact:ilc-cli-binary@phase-1575"
    artifact["artifact_type"] = "cli_binary"
    artifact.pop("min_python_version")
    manifest["artifacts"] = [artifact]
    return manifest


def _validate_raises(manifest: dict, token: str) -> None:
    with pytest.raises(InstallableReleaseManifestError, match=token):
        validate_installable_release_manifest(manifest)


def test_valid_wheel_manifest_passes_validation() -> None:
    validate_installable_release_manifest(_wheel_manifest())


def test_missing_1213_field_rejects() -> None:
    manifest = _wheel_manifest()
    manifest["artifacts"][0].pop("canonical_hash")
    _validate_raises(manifest, "missing_field:canonical_hash")


def test_missing_platform_field_rejects() -> None:
    manifest = _wheel_manifest()
    manifest["artifacts"][0].pop("platform")
    _validate_raises(manifest, "missing_field:platform")


def test_missing_arch_field_rejects() -> None:
    manifest = _wheel_manifest()
    manifest["artifacts"][0].pop("arch")
    _validate_raises(manifest, "missing_field:arch")


def test_invalid_channel_rejects() -> None:
    manifest = _wheel_manifest()
    manifest["artifacts"][0]["channel"] = "nightly"
    _validate_raises(manifest, "invalid_channel:nightly")


def test_artifact_channel_must_match_manifest_channel() -> None:
    manifest = _wheel_manifest()
    manifest["artifacts"][0]["channel"] = "stable"
    _validate_raises(manifest, "artifact_channel_mismatch")


def test_invalid_platform_rejects() -> None:
    manifest = _wheel_manifest()
    manifest["artifacts"][0]["platform"] = "linux-amd64"
    _validate_raises(manifest, "invalid_platform:linux-amd64")


def test_zero_size_bytes_rejects() -> None:
    manifest = _wheel_manifest()
    manifest["artifacts"][0]["size_bytes"] = 0
    _validate_raises(manifest, "non_positive_integer:size_bytes")


def test_bool_size_bytes_rejects() -> None:
    manifest = _wheel_manifest()
    manifest["artifacts"][0]["size_bytes"] = True
    _validate_raises(manifest, "invalid_integer:size_bytes")


def test_float_size_bytes_rejects() -> None:
    manifest = _wheel_manifest()
    manifest["artifacts"][0]["size_bytes"] = 1.5
    _validate_raises(manifest, "float_rejected")


def test_http_download_url_rejects() -> None:
    manifest = _wheel_manifest()
    manifest["artifacts"][0]["download_url"] = "http://files.pythonhosted.org/artifact.whl"
    _validate_raises(manifest, "download_url_not_https")


def test_placeholder_download_url_rejects() -> None:
    manifest = _wheel_manifest()
    manifest["artifacts"][0]["download_url"] = "https://example.invalid/artifact.whl"
    _validate_raises(manifest, "placeholder_download_url")


def test_min_python_version_required_for_wheel() -> None:
    manifest = _wheel_manifest()
    manifest["artifacts"][0].pop("min_python_version")
    _validate_raises(manifest, "missing_field:min_python_version")


def test_min_python_version_not_required_for_cli_binary() -> None:
    validate_installable_release_manifest(_cli_binary_manifest())


def test_min_python_version_rejected_for_cli_binary() -> None:
    manifest = _cli_binary_manifest()
    manifest["artifacts"][0]["min_python_version"] = "3.10"
    _validate_raises(manifest, "extra_field:min_python_version")


def test_invalid_canonical_hash_format_rejects() -> None:
    manifest = _wheel_manifest()
    manifest["artifacts"][0]["canonical_hash"] = "md5:abc"
    _validate_raises(manifest, "invalid_canonical_hash")


def test_uppercase_canonical_hash_rejects() -> None:
    manifest = _wheel_manifest()
    manifest["artifacts"][0]["canonical_hash"] = EXPECTED_WHEEL_SHA256.upper()
    _validate_raises(manifest, "invalid_canonical_hash")


def test_extra_artifact_field_rejects() -> None:
    manifest = _wheel_manifest()
    manifest["artifacts"][0]["extra"] = "not allowed"
    _validate_raises(manifest, "extra_field:extra")


def test_extra_top_level_field_rejects() -> None:
    manifest = _wheel_manifest()
    manifest["extra"] = "not allowed"
    _validate_raises(manifest, "extra_field:extra")


def test_duplicate_artifact_id_rejects() -> None:
    manifest = _manifest()
    manifest["artifacts"][1]["artifact_id"] = manifest["artifacts"][0]["artifact_id"]
    _validate_raises(manifest, "duplicate_artifact_id")


def test_load_instance_manifest_validates_successfully() -> None:
    manifest = _manifest()
    assert len(manifest["artifacts"]) == 2
    hashes = {artifact["artifact_type"]: artifact["canonical_hash"] for artifact in manifest["artifacts"]}
    assert hashes["python_wheel"] == EXPECTED_WHEEL_SHA256
    assert hashes["python_sdist"] == EXPECTED_SDIST_SHA256


def test_manifest_validator_has_no_expected_self_assignment() -> None:
    source = (
        ROOT / "ilc_core/release/installable_release_manifest.py"
    ).read_text(encoding="utf-8")
    assert "expected = expected" not in source


def test_instance_manifest_uses_actual_pypi_urls_and_sizes() -> None:
    manifest = _manifest()
    by_type = {artifact["artifact_type"]: artifact for artifact in manifest["artifacts"]}
    assert by_type["python_wheel"]["download_url"].startswith(
        "https://files.pythonhosted.org/"
    )
    assert by_type["python_wheel"]["size_bytes"] == 1000828
    assert by_type["python_sdist"]["download_url"].startswith(
        "https://files.pythonhosted.org/"
    )
    assert by_type["python_sdist"]["size_bytes"] == 783493


def test_nan_json_constant_rejected_on_load(tmp_path: Path) -> None:
    path = tmp_path / "nan.json"
    path.write_text('{"manifest_schema_version": NaN}', encoding="utf-8")
    with pytest.raises(InstallableReleaseManifestError, match="non_finite_json_constant:NaN"):
        load_installable_release_manifest(path)


def test_canonical_bytes_are_deterministic() -> None:
    manifest = _manifest()
    expected = json.dumps(
        manifest,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    assert canonical_installable_release_manifest_bytes(manifest) == expected


def test_phase_1213_schema_is_unmodified() -> None:
    digest = hashlib.sha256(PHASE_1213_SCHEMA_PATH.read_bytes()).hexdigest()
    assert digest == PHASE_1213_SCHEMA_SHA256


def test_schema_doc_extends_1213_without_mutating_it() -> None:
    text = SCHEMA_PATH.read_text(encoding="utf-8")
    assert "extends `docs/specs/ilc_release_artifact_manifest_schema_1213_v0.1.md`" in text
    assert "python_wheel" in text
    assert "python_sdist" in text
    assert "install_script" in text
    assert "Phase 1213 schema mutation | Not performed" in text


def test_pyproject_packages_release_module() -> None:
    pyproject = PYPROJECT_PATH.read_text(encoding="utf-8")
    assert '"ilc_core.release"' in pyproject
    assert '"ilc_core.network.relay"' in pyproject
