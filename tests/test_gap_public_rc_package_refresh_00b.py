from __future__ import annotations

import json
from pathlib import Path

from ilc_core.release.install_sh_manifest_sync import verify_install_sh_manifest_sync
from ilc_core.release.installable_release_manifest import (
    validate_installable_release_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_030 = (
    ROOT
    / "docs/specs/ilc_installable_release_manifest_ilc_core_030_GAP_PUBLIC_RC_PACKAGE_REFRESH_00_v0.1.json"
)
MANIFEST_031 = (
    ROOT
    / "docs/specs/ilc_installable_release_manifest_ilc_core_031_GAP_CDL017_PACKAGE_00a_v0.1.json"
)
MANIFEST_040 = (
    ROOT
    / "docs/specs/ilc_installable_release_manifest_ilc_core_040_GAP_AGENT_ONBOARDING_PACKAGE_00a_v0.1.json"
)
MANIFEST_041 = (
    ROOT
    / "docs/specs/ilc_installable_release_manifest_ilc_core_041_GAP_ONBOARDING_PACKAGE_FIX1_00a_v0.1.json"
)
MANIFEST_042 = (
    ROOT
    / "docs/specs/ilc_installable_release_manifest_ilc_core_042_GAP_ONBOARDING_PACKAGE_042_00a_v0.1.json"
)
MANIFEST_043 = (
    ROOT
    / "docs/specs/ilc_installable_release_manifest_ilc_core_043_GAP_ONBOARDING_PACKAGE_043_00a_v0.1.json"
)
MANIFEST_044 = (
    ROOT
    / "docs/specs/ilc_installable_release_manifest_ilc_core_044_GAP_ONBOARDING_PACKAGE_044_00a_v0.1.json"
)
MANIFEST_020 = (
    ROOT
    / "docs/specs/ilc_installable_release_manifest_ilc_core_020_GAP_PUBLIC_INSTALL_01_v0.1.json"
)
BUILD_RECEIPT = (
    ROOT / "docs/specs/ilc_package_build_receipt_GAP_PUBLIC_RC_PACKAGE_REFRESH_00a_v0.1.json"
)
UPLOAD_RECEIPT = (
    ROOT / "docs/specs/ilc_pypi_upload_receipt_GAP_PUBLIC_RC_PACKAGE_REFRESH_00b_v0.1.json"
)
SUPERSESSION_NOTE = (
    ROOT
    / "docs/specs/ilc_installable_release_manifest_ilc_core_020_superseded_by_030_GAP_PUBLIC_RC_PACKAGE_REFRESH_00b_v0.1.md"
)
INSTALL_SH = ROOT / "tools/install.sh"


def _load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def test_manifest_030_validates_and_targets_ilc_core_030() -> None:
    manifest = _load_json(MANIFEST_030)

    validate_installable_release_manifest(manifest)

    assert manifest["release_id"] == "ilc-core-0.3.0"
    assert manifest["channel"] == "rc"
    assert {artifact["artifact_type"] for artifact in manifest["artifacts"]} == {
        "python_sdist",
        "python_wheel",
    }


def test_manifest_030_uses_canonical_pypi_urls_and_unsigned_status() -> None:
    manifest = _load_json(MANIFEST_030)

    for artifact in manifest["artifacts"]:
        assert artifact["download_url"].startswith("https://files.pythonhosted.org/")
        assert "ilc_core-0.3.0" in artifact["download_url"]
        assert artifact["signing_status"] == "unsigned"


def test_build_receipt_and_upload_receipt_hashes_match_manifest() -> None:
    manifest = _load_json(MANIFEST_030)
    build_receipt = _load_json(BUILD_RECEIPT)
    upload_receipt = _load_json(UPLOAD_RECEIPT)
    wheel = next(
        artifact
        for artifact in manifest["artifacts"]
        if artifact["artifact_type"] == "python_wheel"
    )
    sdist = next(
        artifact
        for artifact in manifest["artifacts"]
        if artifact["artifact_type"] == "python_sdist"
    )

    assert build_receipt["pypi_upload_status"] == "uploaded"
    assert upload_receipt["pypi_upload_status"] == "uploaded"
    assert wheel["canonical_hash"] == f"sha256:{build_receipt['wheel_sha256']}"
    assert sdist["canonical_hash"] == f"sha256:{build_receipt['sdist_sha256']}"
    assert upload_receipt["wheel_sha256"] == build_receipt["wheel_sha256"]
    assert upload_receipt["sdist_sha256"] == build_receipt["sdist_sha256"]


def test_manifest_031_validates_and_targets_ilc_core_031() -> None:
    manifest = _load_json(MANIFEST_031)

    validate_installable_release_manifest(manifest)

    assert manifest["release_id"] == "ilc-core-0.3.1"
    assert manifest["channel"] == "rc"
    assert {artifact["artifact_type"] for artifact in manifest["artifacts"]} == {
        "python_sdist",
        "python_wheel",
    }


def test_manifest_031_remains_valid_after_040_supersession() -> None:
    validate_installable_release_manifest(_load_json(MANIFEST_031))


def test_manifest_041_validates_and_targets_ilc_core_041() -> None:
    manifest = _load_json(MANIFEST_041)

    validate_installable_release_manifest(manifest)

    assert manifest["release_id"] == "ilc-core-0.4.1"
    assert manifest["channel"] == "rc"
    assert {artifact["artifact_type"] for artifact in manifest["artifacts"]} == {
        "python_sdist",
        "python_wheel",
    }


def test_manifest_042_validates_and_targets_ilc_core_042() -> None:
    manifest = _load_json(MANIFEST_042)

    validate_installable_release_manifest(manifest)

    assert manifest["release_id"] == "ilc-core-0.4.2"
    assert manifest["channel"] == "rc"
    assert {artifact["artifact_type"] for artifact in manifest["artifacts"]} == {
        "python_sdist",
        "python_wheel",
    }


def test_manifest_043_validates_and_targets_ilc_core_043() -> None:
    manifest = _load_json(MANIFEST_043)

    validate_installable_release_manifest(manifest)

    assert manifest["release_id"] == "ilc-core-0.4.3"
    assert manifest["channel"] == "rc"
    assert {artifact["artifact_type"] for artifact in manifest["artifacts"]} == {
        "python_sdist",
        "python_wheel",
    }


def test_manifest_044_validates_and_targets_ilc_core_044() -> None:
    manifest = _load_json(MANIFEST_044)

    validate_installable_release_manifest(manifest)

    assert manifest["release_id"] == "ilc-core-0.4.4"
    assert manifest["channel"] == "rc"
    assert {artifact["artifact_type"] for artifact in manifest["artifacts"]} == {
        "python_sdist",
        "python_wheel",
    }


def test_manifest_040_remains_valid_after_041_supersession() -> None:
    validate_installable_release_manifest(_load_json(MANIFEST_040))


def test_manifest_041_remains_valid_after_042_supersession() -> None:
    validate_installable_release_manifest(_load_json(MANIFEST_041))


def test_install_sh_is_synced_to_current_044_manifest() -> None:
    verify_install_sh_manifest_sync(INSTALL_SH, MANIFEST_044)


def test_old_manifest_still_valid_and_unmodified_by_supersession() -> None:
    validate_installable_release_manifest(_load_json(MANIFEST_020))
    old_manifest_text = MANIFEST_020.read_text(encoding="utf-8")

    assert "superseded_by" not in old_manifest_text


def test_supersession_note_names_old_new_and_upload_receipt() -> None:
    text = SUPERSESSION_NOTE.read_text(encoding="utf-8")

    assert MANIFEST_020.name in text
    assert MANIFEST_030.name in text
    assert UPLOAD_RECEIPT.name in text
    assert "No release signature was produced in this phase." in text
