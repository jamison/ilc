from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from ilc_core.bundle.atlas_slice_manifest import build_atlas_slice_manifest
from ilc_core.sidecars.starmap_installer import (
    StarMapInstallerError,
    build_install_receipt,
    canonical_sha256,
    load_manifest_payload,
    materialize_starmap_manifest,
    merge_manifest_entries,
    verify_starmap_manifest,
)


FIXTURE_DIR = Path("tests/fixtures/starmap")
CORE_FIXTURE = FIXTURE_DIR / "core_public_rc_slice_fixture.json"
ECONOMIC_FIXTURE = FIXTURE_DIR / "economic_soft_rc_slice_fixture.json"


def _load(path: Path) -> dict[str, object]:
    return load_manifest_payload(path)


def _tampered_payload(path: Path) -> dict[str, object]:
    payload = _load(path)
    canonical = json.loads(str(payload["canonical_json"]))
    canonical["content_entries"][0]["record_sha256"] = "0" * 64
    payload["canonical_json"] = json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    payload["content_entries"][0]["record_sha256"] = "0" * 64  # type: ignore[index]
    return payload


def _manifest_payload_with_entries(entries: list[dict[str, object]]) -> dict[str, object]:
    return build_atlas_slice_manifest(
        slice_version="1575b-fix4.test",
        section_label="core",
        source_lmdb_root_sha256="a" * 64,
        projection_filter="genesis_core_star_map",
        root_pointers=(str(entries[0]["node_id"]),),
        content_entries=entries,
        installer_profile="installer_profile:starmap_installer_sidecar_mvp:test",
    ).to_json_dict()


def test_valid_core_public_rc_slice_fixture_verifies() -> None:
    result = verify_starmap_manifest(_load(CORE_FIXTURE))

    assert result["verification"] == "passed"
    assert result["content_entry_count"] == 5


def test_valid_economic_soft_rc_slice_fixture_verifies() -> None:
    result = verify_starmap_manifest(_load(ECONOMIC_FIXTURE))

    assert result["verification"] == "passed"
    assert result["projection_filter"] == "economic_soft_rc_slice"


def test_manifest_canonical_hash_deterministic_under_key_reordering() -> None:
    payload = _load(CORE_FIXTURE)
    reversed_payload = dict(reversed(list(payload.items())))

    assert canonical_sha256(payload) == canonical_sha256(reversed_payload)


def test_blob_hash_mismatch_rejected() -> None:
    with pytest.raises(StarMapInstallerError) as excinfo:
        verify_starmap_manifest(_tampered_payload(CORE_FIXTURE))

    assert "mismatch" in str(excinfo.value)


def test_public_rc_exclude_materialization_rejected_for_public_slice() -> None:
    payload = _manifest_payload_with_entries(
        [
            {
                "authority_source": "PUBLIC_RC_EXCLUDE",
                "export_category": "public",
                "graph_projection": "genesis_core_star_map",
                "node_id": "node:marker",
                "record_sha256": "1" * 64,
                "source_path": "docs/marker.md",
            }
        ]
    )

    with pytest.raises(StarMapInstallerError) as excinfo:
        materialize_starmap_manifest(payload, dry_run=True)

    assert str(excinfo.value) == "starmap_public_rc_exclude_content_rejected"


def test_path_traversal_rejected() -> None:
    payload = _manifest_payload_with_entries(
        [
            {
                "authority_source": "adr:fixture",
                "export_category": "public",
                "graph_projection": "genesis_core_star_map",
                "materialization_path": "../escape.md",
                "node_id": "node:escape",
                "record_sha256": "3" * 64,
                "source_path": "docs/escape.md",
            }
        ]
    )

    with pytest.raises(StarMapInstallerError) as excinfo:
        materialize_starmap_manifest(payload, dry_run=True)

    assert str(excinfo.value) == "starmap_path_traversal_rejected"


def test_same_node_same_hash_overlap_dedupes() -> None:
    merged = merge_manifest_entries([_load(CORE_FIXTURE), _load(CORE_FIXTURE)])

    assert merged["deduped_node_count"] == 5


def test_same_node_different_hash_conflicts() -> None:
    first = _load(CORE_FIXTURE)
    entry = dict(json.loads(str(first["canonical_json"]))["content_entries"][0])
    entry["record_sha256"] = "2" * 64
    second = _manifest_payload_with_entries([entry])

    with pytest.raises(StarMapInstallerError):
        merge_manifest_entries([first, second])


def test_receipt_generation_deterministic() -> None:
    first = build_install_receipt(_load(ECONOMIC_FIXTURE))
    second = build_install_receipt(_load(ECONOMIC_FIXTURE))

    assert first == second
    assert first["created_at_policy"] == "deterministic_test_fixture"
    assert first["receipt_sha256"]


def test_materialize_writes_under_target(tmp_path: Path) -> None:
    result = materialize_starmap_manifest(
        _load(CORE_FIXTURE),
        target=tmp_path,
        dry_run=False,
    )

    assert result["materialization"] == "written"
    assert len(list(tmp_path.rglob("*.node.json"))) == result["materialized_file_count"]


def test_cli_wrapper_verify_and_receipt() -> None:
    verify = subprocess.run(
        [".venv/bin/python", "tools/ilc_starmap_installer.py", "verify", str(CORE_FIXTURE)],
        check=True,
        capture_output=True,
        text=True,
    )
    receipt = subprocess.run(
        [".venv/bin/python", "tools/ilc_starmap_installer.py", "receipt", str(CORE_FIXTURE)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(verify.stdout)["verification"] == "passed"
    assert json.loads(receipt.stdout)["receipt_sha256"]


def test_no_publication_command_surface() -> None:
    source = Path("ilc_core/sidecars/starmap_installer.py").read_text(encoding="utf-8")
    wrapper = Path("tools/ilc_starmap_installer.py").read_text(encoding="utf-8")
    forbidden = [
        "git " + "push",
        "gh repo " + "create",
        "gh repo " + "edit",
        "ClawHub " + "publish",
        "public_rc_" + "published",
    ]

    for term in forbidden:
        assert term not in source
        assert term not in wrapper
