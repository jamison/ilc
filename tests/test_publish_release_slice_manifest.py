from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from ilc_core.bundle.atlas_slice_manifest import (
    manifest_from_json_dict,
    verify_atlas_slice_manifest,
    write_atlas_slice_manifest,
)
from tools import publish_release_slice_manifest as tooling


CID_LIKE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{2,255}$")
RELEASE_SOURCE_COMMIT = "849aec59b5acdd67f4961b9291d9e2d5e2d4fb9c"


def _fixture_assertion_path(tmp_path: Path) -> Path:
    payload = {
        "artifact_nodes": [
            {
                "artifact_id": "ilc-artifact:ilc-core-python-sdist-0432@phase-1628",
                "artifact_type": "sdist",
                "cid": "bafyreiducxg5icoh3laopqwgn57377bparmagl2xiwvuyzjl4emwhwrkma",
                "filename": "ilc_core-0.4.32.tar.gz",
                "node_kind": "ArtifactNode",
                "package_name": "ilc-core",
                "package_version": "0.4.32",
                "schema_version": "artifact_node.v0.1",
                "sha256": "172cd72d62393fae7785cf0bb321153d8ffdae368e8163f2183769d0dc7bfa4d",
                "size_bytes": 1267446,
            },
            {
                "artifact_id": "ilc-artifact:ilc-core-python-wheel-0432@phase-1628",
                "artifact_type": "wheel",
                "cid": "bafyreifqv34wxxqwknqyqpk7nrddvwssshheszaplcyl5kkscbjwoprodu",
                "filename": "ilc_core-0.4.32-py3-none-any.whl",
                "node_kind": "ArtifactNode",
                "package_name": "ilc-core",
                "package_version": "0.4.32",
                "schema_version": "artifact_node.v0.1",
                "sha256": "f5486b0b20cfef77aeba18d9dbe371d385cb58ec04b83fb7765f652695171c90",
                "size_bytes": 1549382,
            },
        ],
        "assertion_cid": "bafyreig47oqtnwxvd6feryuaw72qximlvzqb2e4oxz4c25dscmsogrurga",
        "build_recipe_nodes": [
            {
                "build_command": "python -m build",
                "build_date": "2026-10-06T01:27:36Z",
                "build_env_hash": "05518ed97579092ba3e7f1f516cd91bcf46347d389efeb28cf3e971191d7cf39",
                "build_toolchain": "python-build",
                "builder_agent_id": "phase:GAP-PACKAGE-V0432-00a",
                "cid": "bafyreihleym4lsdoijatneswrfm2lk5ojcqhapqyt5hgppn4g7iajtumzu",
                "node_kind": "BuildRecipeNode",
                "reproducibility_hash": "63ba7b34b998d7cf812dc6d088009ce620e4b0ca24188d6b8dc333e15c46b464",
                "schema_version": "build_recipe_node.v0.1",
                "source_commit": RELEASE_SOURCE_COMMIT,
            }
        ],
        "schema_version": "software_release_assertion.v0.1",
        "software_release_node": {
            "artifact_cids": [
                "bafyreiducxg5icoh3laopqwgn57377bparmagl2xiwvuyzjl4emwhwrkma",
                "bafyreifqv34wxxqwknqyqpk7nrddvwssshheszaplcyl5kkscbjwoprodu",
            ],
            "build_recipe_cid": "bafyreihleym4lsdoijatneswrfm2lk5ojcqhapqyt5hgppn4g7iajtumzu",
            "changelog_hash": "05518ed97579092ba3e7f1f516cd91bcf46347d389efeb28cf3e971191d7cf39",
            "cid": "bafyreidyzsgcy4zkuzl7spujcw5aio4nulrxibqrdkr4bbadlklidolz6e",
            "node_kind": "SoftwareReleaseNode",
            "package_name": "ilc-core",
            "release_channel": "public_rc",
            "release_date": "2026-10-06T01:27:36Z",
            "release_key_pubkey": "5bf71c1e0ac93f2d7414b0dc315161fc4a57462c198ba1618e2890ec89a5b15a",
            "schema_version": "software_release_node.v0.1",
            "source_commit": RELEASE_SOURCE_COMMIT,
            "version": "0.4.32",
        },
    }
    path = tmp_path / "release_assertion_core.json"
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    return path


def test_valid_manifest_construction_from_ceremony_assertion(tmp_path: Path) -> None:
    payload = tooling.build_release_slice_manifest(
        release_assertion_path=_fixture_assertion_path(tmp_path),
        version="0.4.32",
        source_commit=RELEASE_SOURCE_COMMIT,
    )

    assert CID_LIKE_RE.fullmatch(payload["cidv1"])
    assert re.fullmatch(r"[0-9a-f]{64}", payload["sha256"])
    assert payload["slice_id"]
    entries = payload["content_entries"]
    assert {entry["node_kind"] for entry in entries} >= {
        "ArtifactNode",
        "BuildRecipeNode",
        "SoftwareReleaseNode",
        "software_release_assertion",
    }


def test_manifest_round_trip_stable(tmp_path: Path) -> None:
    payload = tooling.build_release_slice_manifest(
        release_assertion_path=_fixture_assertion_path(tmp_path),
        version="0.4.32",
        source_commit=RELEASE_SOURCE_COMMIT,
    )
    manifest = manifest_from_json_dict(payload)
    output = tmp_path / "manifest.json"

    write_atlas_slice_manifest(output, manifest)
    round_trip = manifest_from_json_dict(json.loads(output.read_text(encoding="utf-8")))

    assert round_trip.cidv1 == manifest.cidv1
    assert round_trip.sha256 == manifest.sha256
    assert verify_atlas_slice_manifest(round_trip, require_signature=False)


def test_cidv1_determinism(tmp_path: Path) -> None:
    assertion_path = _fixture_assertion_path(tmp_path)
    first = tooling.build_release_slice_manifest(
        release_assertion_path=assertion_path,
        version="0.4.32",
        source_commit=RELEASE_SOURCE_COMMIT,
    )
    second = tooling.build_release_slice_manifest(
        release_assertion_path=assertion_path,
        version="0.4.32",
        source_commit=RELEASE_SOURCE_COMMIT,
    )

    assert first["cidv1"] == second["cidv1"]
    assert first["sha256"] == second["sha256"]


def test_no_float_in_content_entries_rejected(tmp_path: Path) -> None:
    source = json.loads(_fixture_assertion_path(tmp_path).read_text(encoding="utf-8"))
    source["artifact_nodes"][0]["size_bytes"] = 1.25
    path = tmp_path / "release_assertion_core.json"
    path.write_text(json.dumps(source, sort_keys=True), encoding="utf-8")

    with pytest.raises(ValueError, match="atlas_slice_manifest_float_not_allowed"):
        tooling.build_release_slice_manifest(
            release_assertion_path=path,
            version="0.4.32",
            source_commit=RELEASE_SOURCE_COMMIT,
        )


def test_cli_dry_run_does_not_write_and_actual_run_writes(tmp_path: Path) -> None:
    assertion_path = _fixture_assertion_path(tmp_path)
    output = tmp_path / "manifest.json"
    command = [
        sys.executable,
        "tools/publish_release_slice_manifest.py",
        "--version",
        "0.4.32",
        "--source-commit",
        RELEASE_SOURCE_COMMIT,
        "--release-assertion",
        str(assertion_path),
        "--output",
        str(output),
        "--dry-run",
    ]
    dry = subprocess.run(command, check=True, capture_output=True, text=True)
    dry_payload = json.loads(dry.stdout)

    assert not output.exists()
    assert CID_LIKE_RE.fullmatch(dry_payload["cidv1"])

    actual = subprocess.run(command[:-1], check=True, capture_output=True, text=True)
    actual_payload = json.loads(actual.stdout)

    assert output.exists()
    assert json.loads(output.read_text(encoding="utf-8")) == actual_payload
    assert actual_payload == dry_payload


def test_tool_source_has_no_network_or_signing_calls() -> None:
    source = Path("tools/publish_release_slice_manifest.py").read_text(encoding="utf-8")
    forbidden = [
        "urllib",
        "requests",
        "httpx",
        "socket",
        "quic",
        "grpc",
        "subprocess",
        "sign_atlas_slice_manifest",
        "Ed25519",
        "private_key",
        "cose_sign1_sign",
    ]
    assert all(token not in source for token in forbidden)
