from __future__ import annotations

from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.bundle.atlas_slice_manifest import (
    build_atlas_slice_manifest,
    manifest_from_json_dict,
    sign_atlas_slice_manifest,
    verify_atlas_slice_manifest,
)
from ilc_core.encoding.cidv1 import node_id_from_bytes


def _entries() -> list[dict[str, object]]:
    return [
        {
            "graph_projection": "genesis_core_star_map",
            "node_id": "node:b",
            "node_kind": "spec_document_node",
            "record_sha256": "b" * 64,
            "source_path": "docs/b.md",
        },
        {
            "graph_projection": "genesis_core_star_map",
            "node_id": "node:a",
            "node_kind": "runtime_source_file_node",
            "record_sha256": "a" * 64,
            "source_path": "ilc_core/a.py",
        },
    ]


def _manifest():
    return build_atlas_slice_manifest(
        slice_version="0.1",
        section_label="core",
        source_lmdb_root_sha256="c" * 64,
        projection_filter="genesis_core_star_map",
        root_pointers=("node:a",),
        content_entries=_entries(),
    )


def test_manifest_cidv1_deterministic() -> None:
    first = _manifest()
    second = _manifest()

    assert first.cidv1 == second.cidv1
    assert first.canonical_json == second.canonical_json


def test_manifest_sha256_and_cidv1_match_dag_cbor() -> None:
    manifest = _manifest()

    assert manifest.sha256
    assert node_id_from_bytes(manifest.dag_cbor) == manifest.cidv1


def test_manifest_float_rejected() -> None:
    entries = _entries()
    entries[0]["bad_float"] = 1.25

    try:
        build_atlas_slice_manifest(
            slice_version="0.1",
            section_label="core",
            source_lmdb_root_sha256="c" * 64,
            projection_filter="genesis_core_star_map",
            root_pointers=("node:a",),
            content_entries=entries,
        )
    except ValueError as exc:
        assert str(exc) == "atlas_slice_manifest_float_not_allowed"
    else:
        raise AssertionError("float was accepted")


def test_manifest_public_rc_exclude_is_true_and_unsigned_by_default() -> None:
    manifest = _manifest()

    assert manifest.public_rc_exclude is True
    assert manifest.cose_sign1 == b""
    assert manifest.dev_signed is False


def test_verify_rejects_unsigned_manifest_by_default() -> None:
    try:
        verify_atlas_slice_manifest(_manifest())
    except ValueError as exc:
        assert str(exc) == "atlas_slice_manifest_signature_missing"
    else:
        raise AssertionError("unsigned manifest was accepted")


def test_sign_and_verify_round_trip() -> None:
    private_key = ed25519.Ed25519PrivateKey.generate()
    signed = sign_atlas_slice_manifest(_manifest(), private_key=private_key)

    assert signed.cose_sign1 != b""
    assert signed.dev_signed is True
    assert verify_atlas_slice_manifest(
        signed,
        public_key=private_key.public_key(),
    )


def test_verify_rejects_wrong_public_key() -> None:
    signer = ed25519.Ed25519PrivateKey.generate()
    wrong_key = ed25519.Ed25519PrivateKey.generate().public_key()
    signed = sign_atlas_slice_manifest(_manifest(), private_key=signer)

    try:
        verify_atlas_slice_manifest(signed, public_key=wrong_key)
    except ValueError as exc:
        assert str(exc) == "atlas_slice_manifest_signature_invalid"
    else:
        raise AssertionError("wrong key was accepted")


def test_manifest_json_round_trip_and_tamper_rejected() -> None:
    signer = ed25519.Ed25519PrivateKey.generate()
    signed = sign_atlas_slice_manifest(_manifest(), private_key=signer)
    payload = signed.to_json_dict()
    round_tripped = manifest_from_json_dict(payload)

    assert round_tripped.cidv1 == signed.cidv1

    payload["content_entries"][0]["record_sha256"] = "d" * 64  # type: ignore[index]
    try:
        manifest_from_json_dict(payload)
    except ValueError as exc:
        assert str(exc) in {
            "atlas_slice_manifest_canonical_json_mismatch",
            "atlas_slice_manifest_dag_cbor_mismatch",
            "atlas_slice_manifest_cid_mismatch",
            "atlas_slice_manifest_sha_mismatch",
        }
    else:
        raise AssertionError("tampered manifest was accepted")
