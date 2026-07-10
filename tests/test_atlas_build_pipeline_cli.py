from __future__ import annotations

import json
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.cli.main import _build_parser, _run_top_level_command


LMDB = Path("out/genesis_base_graph_v0.4_unified.lmdb")


def _key_hex_pair() -> tuple[str, str]:
    private_key = ed25519.Ed25519PrivateKey.generate()
    private_hex = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    ).hex()
    public_hex = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    ).hex()
    return private_hex, public_hex


def _run(argv: list[str]) -> dict:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return _run_top_level_command(str(args.command), args, Path(args.graph_state))


def test_build_slice_produces_manifest_file(tmp_path: Path) -> None:
    output = tmp_path / "manifest.json"
    payload = _run(
        [
            "atlas",
            "build-slice",
            "--lmdb",
            str(LMDB),
            "--slice-variant",
            "core",
            "--projection",
            "genesis_core_star_map",
            "--output",
            str(output),
        ]
    )

    assert payload["ok"] is True
    assert output.exists()
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["public_rc_exclude"] is True
    assert data["projection_filter"] == "genesis_core_star_map"
    assert data["cose_sign1_b64"] == ""


def test_build_slice_rejects_private_projection(tmp_path: Path) -> None:
    output = tmp_path / "manifest.json"

    try:
        _run(
            [
                "atlas",
                "build-slice",
                "--lmdb",
                str(LMDB),
                "--slice-variant",
                "core",
                "--projection",
                "excluded_private_material",
                "--output",
                str(output),
            ]
        )
    except ValueError as exc:
        assert "atlas_slice_manifest_private_projection_blocked" in str(exc)
    else:
        raise AssertionError("private projection was accepted")


def test_sign_manifest_adds_cose_sign1(tmp_path: Path) -> None:
    private_hex, _public_hex = _key_hex_pair()
    manifest = tmp_path / "manifest.json"
    signed = tmp_path / "signed.json"
    _run(
        [
            "atlas",
            "build-slice",
            "--lmdb",
            str(LMDB),
            "--slice-variant",
            "core",
            "--projection",
            "genesis_core_star_map",
            "--output",
            str(manifest),
        ]
    )

    payload = _run(
        [
            "atlas",
            "sign-manifest",
            "--manifest",
            str(manifest),
            "--private-key-hex",
            private_hex,
            "--output",
            str(signed),
        ]
    )

    assert payload["ok"] is True
    data = json.loads(signed.read_text(encoding="utf-8"))
    assert data["cose_sign1_b64"] != ""
    assert data["dev_signed"] is True


def test_verify_slice_passes_on_signed_manifest(tmp_path: Path) -> None:
    private_hex, public_hex = _key_hex_pair()
    signed = tmp_path / "signed.json"
    _build_and_sign(tmp_path, private_hex, signed)

    payload = _run(
        [
            "atlas",
            "verify-slice",
            "--manifest",
            str(signed),
            "--public-key-hex",
            public_hex,
        ]
    )

    assert payload["ok"] is True
    assert payload["data"]["verdict"] == "pass"


def test_verify_slice_fails_on_unsigned_manifest(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.json"
    _run(
        [
            "atlas",
            "build-slice",
            "--lmdb",
            str(LMDB),
            "--slice-variant",
            "core",
            "--projection",
            "genesis_core_star_map",
            "--output",
            str(manifest),
        ]
    )

    try:
        _run(["atlas", "verify-slice", "--manifest", str(manifest)])
    except ValueError as exc:
        assert "atlas_slice_manifest_signature_missing" in str(exc)
    else:
        raise AssertionError("unsigned manifest was accepted")


def test_verify_slice_fails_on_wrong_public_key(tmp_path: Path) -> None:
    private_hex, _public_hex = _key_hex_pair()
    _wrong_private_hex, wrong_public_hex = _key_hex_pair()
    signed = tmp_path / "signed.json"
    _build_and_sign(tmp_path, private_hex, signed)

    try:
        _run(
            [
                "atlas",
                "verify-slice",
                "--manifest",
                str(signed),
                "--public-key-hex",
                wrong_public_hex,
            ]
        )
    except ValueError as exc:
        assert "atlas_slice_manifest_signature_invalid" in str(exc)
    else:
        raise AssertionError("wrong public key was accepted")


def _build_and_sign(tmp_path: Path, private_hex: str, signed: Path) -> None:
    manifest = tmp_path / "manifest.json"
    _run(
        [
            "atlas",
            "build-slice",
            "--lmdb",
            str(LMDB),
            "--slice-variant",
            "core",
            "--projection",
            "genesis_core_star_map",
            "--output",
            str(manifest),
        ]
    )
    _run(
        [
            "atlas",
            "sign-manifest",
            "--manifest",
            str(manifest),
            "--private-key-hex",
            private_hex,
            "--output",
            str(signed),
        ]
    )
