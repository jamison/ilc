from __future__ import annotations

import json
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.bundle.layer0_protocol_bundle import ADR_0009_LAYER0_NOT_PUBLIC_DISTRIBUTION
from ilc_core.bundle.layer1_genesis_bundle import ADR_0009_LAYER1_NOT_PUBLIC_DISTRIBUTION
from ilc_core.bundle.layer2_epoch_snapshot import ADR_0009_LAYER2_NOT_PUBLIC_DISTRIBUTION
from ilc_core.bundle.layer3_wire_binding import ADR_0009_LAYER3_NOT_PUBLIC_DISTRIBUTION
from ilc_core.rc.source_allowlist_export_rehearsal import (
    ADR_0009_BUNDLE_CHAIN_VERIFIED_FIELD,
    ADR_0009_PUBLIC_EXPORT_NOT_EXECUTED_TOKEN,
    ADR_0009_SOURCE_EXPORT_REHEARSAL_PROFILE_INTEGRATION_TOKEN,
    build_adr_0009_source_export_rehearsal_profile,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "tests/fixtures/adr_0009"
SCHEMA = ROOT / "docs/specs/ilc_launch_readiness_manifest_schema_1422_v0.1.md"


def _load_fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _public_keys_by_layer(bundle: dict[str, object]) -> dict[int, ed25519.Ed25519PublicKey]:
    public_key_hex = bundle.get("public_key_hex")
    if not isinstance(public_key_hex, str):
        raise ValueError("test_fixture_public_key_missing")
    public_key = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex))
    return {layer: public_key for layer in range(4)}


def test_phase_1519_rehearsal_profile_verifies_valid_bundle_without_public_tree(
    tmp_path: Path,
) -> None:
    (tmp_path / "README.md").write_text("ILC source rehearsal candidate\n", encoding="utf-8")
    bundle = _load_fixture("bundle_four_layer_chain_valid.json")

    manifest = build_adr_0009_source_export_rehearsal_profile(
        repo_root=tmp_path,
        include_roots=("README.md",),
        excluded_roots=(),
        force_include_paths=(),
        adr_0009_bundle=bundle,
        adr_0009_public_keys_by_layer=_public_keys_by_layer(bundle),
    )

    assert manifest["result"] == "pass"
    assert manifest[ADR_0009_BUNDLE_CHAIN_VERIFIED_FIELD] is True
    assert manifest["adr_0009_bundle_verification"]["result"] == "pass"
    assert len(manifest["adr_0009_bundle_verification"]["layer_cidv1_chain"]) == 4
    assert ADR_0009_SOURCE_EXPORT_REHEARSAL_PROFILE_INTEGRATION_TOKEN in manifest[
        "phase_1519_tokens"
    ]
    assert ADR_0009_PUBLIC_EXPORT_NOT_EXECUTED_TOKEN in manifest["phase_1519_tokens"]
    assert ADR_0009_PUBLIC_EXPORT_NOT_EXECUTED_TOKEN in manifest["non_claims"]
    assert "no_adr_0009_guard_clearance" in manifest["non_claims"]
    assert "no_adr_0009_public_distribution_authorization" in manifest["non_claims"]
    assert "no_clean_public_tree_materialization" in manifest["non_claims"]
    assert not (tmp_path / "out").exists()


def test_phase_1520_guard_clearance_does_not_clear_publication_gate(tmp_path: Path) -> None:
    assert ADR_0009_LAYER0_NOT_PUBLIC_DISTRIBUTION is False
    assert ADR_0009_LAYER1_NOT_PUBLIC_DISTRIBUTION is False
    assert ADR_0009_LAYER2_NOT_PUBLIC_DISTRIBUTION is False
    assert ADR_0009_LAYER3_NOT_PUBLIC_DISTRIBUTION is False

    (tmp_path / "README.md").write_text("ILC source rehearsal candidate\n", encoding="utf-8")
    bundle = _load_fixture("bundle_four_layer_chain_valid.json")
    manifest = build_adr_0009_source_export_rehearsal_profile(
        repo_root=tmp_path,
        include_roots=("README.md",),
        excluded_roots=(),
        force_include_paths=(),
        adr_0009_bundle=bundle,
        adr_0009_public_keys_by_layer=_public_keys_by_layer(bundle),
    )

    assert manifest[ADR_0009_BUNDLE_CHAIN_VERIFIED_FIELD] is True
    assert "no_adr_0009_guard_clearance" in manifest["non_claims"]
    assert "no_public_source_export" in manifest["non_claims"]
    assert "no_source_publication" in manifest["non_claims"]
    assert "no_package_publication" in manifest["non_claims"]
    assert ADR_0009_PUBLIC_EXPORT_NOT_EXECUTED_TOKEN in manifest["non_claims"]
    assert not (tmp_path / "out").exists()


def test_phase_1519_rehearsal_profile_rejects_tampered_bundle_before_result() -> None:
    bundle = _load_fixture("bundle_tampered_layer1.json")

    with pytest.raises(
        ValueError,
        match="phase_1519_adr_0009_bundle_verification_failed",
    ):
        build_adr_0009_source_export_rehearsal_profile(
            repo_root=Path("/phase-1519-missing-root"),
            include_roots=("README.md",),
            excluded_roots=(),
            force_include_paths=(),
            adr_0009_bundle=bundle,
            adr_0009_public_keys_by_layer=_public_keys_by_layer(bundle),
        )


def test_phase_1519_launch_schema_records_default_false_and_non_authorization() -> None:
    schema = SCHEMA.read_text(encoding="utf-8")

    assert "`adr_0009_bundle_chain_verified` | boolean | yes" in schema
    assert '"adr_0009_bundle_chain_verified": false' in schema
    assert "does not authorize public distribution" in schema
    assert "authorize ADR-0009 public distribution" in schema
