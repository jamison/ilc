from __future__ import annotations

import json
from pathlib import Path

import pytest

from ilc_core.rc.package_boundary_inventory import (
    DEFAULT_IMPORT_BOUNDARY_SPECS,
    IMPORT_BOUNDARY_INVENTORY_VERSION,
    ImportBoundarySpec,
    build_default_import_boundary_inventory,
    build_import_boundary_inventory,
    export_import_boundary_inventory_json,
)
from ilc_core.rc.package_profiles import (
    NON_EXCISABLE_COMPONENTS,
    PACKAGE_PROFILES,
    PROFILE_OPENCLAW_SKILL_CLAIMABLE,
    PROFILE_OPENCLAW_SKILL_LOCAL,
    profile_manifest,
    validate_all_package_profiles,
)


def test_phase_1243_package_profiles_validate_and_keep_non_excisable_components() -> None:
    validate_all_package_profiles()
    manifest = profile_manifest(PROFILE_OPENCLAW_SKILL_CLAIMABLE)
    assert set(NON_EXCISABLE_COMPONENTS) <= set(manifest["components"])
    assert "rust_consensus_core_binding" in manifest["components"]
    assert manifest["public_rc_eligible"] is True
    assert manifest["public_claimability"] is True
    assert manifest["public_p2p"] is False


def test_phase_1243_local_preview_profile_is_not_final_public_rc() -> None:
    manifest = profile_manifest(PROFILE_OPENCLAW_SKILL_LOCAL)
    assert manifest["local_preview_eligible"] is True
    assert manifest["public_rc_eligible"] is False
    assert manifest["public_claimability"] is False
    assert "public_claimability" not in manifest["package_surfaces"]


def test_phase_1243_profile_surface_contracts_exist_for_all_profiles() -> None:
    for profile_id in PACKAGE_PROFILES:
        manifest = profile_manifest(profile_id)
        assert manifest["package_surfaces"]
        assert "ilc_logic" in manifest["package_surfaces"]


def test_phase_1243_import_inventory_detects_forbidden_import(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    root = tmp_path / "candidate"
    root.mkdir()
    (root / "logic.py").write_text("import lmdb\nfrom urllib.parse import urlparse\n", encoding="utf-8")
    spec = ImportBoundarySpec(
        surface_id="tmp_logic",
        root_paths=("candidate",),
        forbidden_import_roots=("lmdb", "urllib"),
    )
    inventory = build_import_boundary_inventory(spec)
    assert inventory["status"] == "violations_present"
    assert [v["import_root"] for v in inventory["violations"]] == ["lmdb", "urllib"]


def test_phase_1243_import_inventory_passes_clean_surface(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    root = tmp_path / "candidate"
    root.mkdir()
    (root / "logic.py").write_text("from decimal import Decimal\n", encoding="utf-8")
    spec = ImportBoundarySpec(
        surface_id="tmp_logic",
        root_paths=("candidate",),
        forbidden_import_roots=("lmdb", "urllib"),
    )
    inventory = build_import_boundary_inventory(spec)
    assert inventory["status"] == "pass"
    assert inventory["violations"] == []


def test_phase_1243_default_inventory_has_expected_surfaces() -> None:
    inventory = build_default_import_boundary_inventory()
    assert inventory["version"] == IMPORT_BOUNDARY_INVENTORY_VERSION
    assert sorted(inventory["surfaces"]) == sorted(DEFAULT_IMPORT_BOUNDARY_SPECS)
    assert "ilc_logic" in inventory["surfaces"]
    assert "ilc_cli" in inventory["surfaces"]
    assert "ilc_node_runtime" in inventory["surfaces"]
    assert "ilc_harness_adapters" in inventory["surfaces"]


def test_phase_1243_default_inventory_records_current_logic_boundary_status() -> None:
    inventory = build_default_import_boundary_inventory()
    logic = inventory["surfaces"]["ilc_logic"]
    assert logic["status"] == "violations_present"
    assert {
        violation["module"]
        for violation in logic["violations"]
    } == {
        "ilc_core.node.node_schema_core_runtime_360",
        "ilc_core.storage.lmdb_public_runtime",
    }
    assert logic["file_count"] > 0


def test_phase_1243_inventory_json_is_canonical() -> None:
    payload_once = export_import_boundary_inventory_json()
    payload_twice = export_import_boundary_inventory_json()
    assert payload_once == payload_twice
    assert payload_once == json.dumps(
        json.loads(payload_once),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def test_phase_1243_rejects_absolute_or_parent_roots() -> None:
    bad = ImportBoundarySpec(
        surface_id="bad",
        root_paths=("/tmp/nope",),
        forbidden_import_roots=(),
    )
    with pytest.raises(ValueError, match="root_must_be_repo_relative"):
        build_import_boundary_inventory(bad)
