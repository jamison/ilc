"""Phase 1142s Genesis signing ceremony artifact tests."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_KWARGS = {
    "sort_keys": True,
    "separators": (",", ":"),
    "allow_nan": False,
}


def _load_json(path: str) -> Any:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _canonical_hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, **CANONICAL_KWARGS).encode("utf-8")).hexdigest()


def _manifest_hash(manifest: dict[str, Any], field: str = "manifest_hash") -> str:
    payload = dict(manifest)
    payload[field] = None
    return _canonical_hash(payload)


def test_s1_node_attestation_manifest_shape() -> None:
    manifest = _load_json("out/genesis_node_attestation_manifest_v0.1.json")
    assert manifest["manifest_type"] == "genesis_node_attestation_manifest"
    assert manifest["issuer"] == "genesis_agent:01"
    assert manifest["public_key_ref"] == "artifact:genesis_agent1_pubkey_record_838a"
    assert len(manifest["nodes"]) == 32
    assert manifest["manifest_hash"] == _manifest_hash(manifest)


def test_s2_root_signature_exists_and_is_non_empty() -> None:
    signature = (REPO_ROOT / "out/genesis_signing_root_envelope_v0.1.sig").read_text(
        encoding="utf-8"
    ).strip()
    assert signature
    assert len(signature) == 6618
    int(signature, 16)


def test_s3_all_genesis_attested_nodes_are_signed_in_star_map() -> None:
    star_map = _load_json("out/genesis_core_star_map_v0.1.json")
    nodes = [node for node in star_map["nodes"] if node.get("genesis_attested")]
    assert len(nodes) == 32
    for node in nodes:
        assert node["signature_status"] == "signed"
        assert node["signature_envelope_ref"] == "out/genesis_signing_root_envelope_v0.1.json"
        assert node["signature_file_ref"] == "out/genesis_signing_root_envelope_v0.1.sig"
        assert node["star_map_version"] == "v0.1"


def test_s4_node_manifest_contains_32_stable_node_hashes() -> None:
    manifest = _load_json("out/genesis_node_attestation_manifest_v0.1.json")
    star_map = _load_json("out/genesis_core_star_map_v0.1.json")
    excluded = set(manifest["node_hash_excluded_fields"])
    nodes_by_id = {node["candidate_id"]: node for node in star_map["nodes"]}
    assert len(manifest["nodes"]) == 32
    for entry in manifest["nodes"]:
        node = nodes_by_id[entry["candidate_id"]]
        payload = {key: value for key, value in node.items() if key not in excluded}
        assert entry["canonical_hash"] == _canonical_hash(payload)


def test_s5_root_envelope_identity_and_hash() -> None:
    envelope = _load_json("out/genesis_signing_root_envelope_v0.1.json")
    assert envelope["issuer"] == "genesis_agent:01"
    assert envelope["public_key_ref"] == "artifact:genesis_agent1_pubkey_record_838a"
    assert envelope["signing_context"] == "ILC_GENESIS_ROOT_ENVELOPE_V1"
    assert envelope["envelope_hash"] == _manifest_hash(envelope, "envelope_hash")


def test_s6_root_envelope_backlinks_to_all_manifest_hashes() -> None:
    envelope = _load_json("out/genesis_signing_root_envelope_v0.1.json")
    by_type = {entry["manifest_type"]: entry for entry in envelope["manifests"]}
    expected = {
        "genesis_node_attestation_manifest": "out/genesis_node_attestation_manifest_v0.1.json",
        "genesis_bootstrap_toolchain_manifest": "out/genesis_bootstrap_toolchain_manifest_v0.1.json",
        "genesis_reference_implementation_manifest": "out/genesis_reference_implementation_manifest_v0.1.json",
    }
    assert set(by_type) == set(expected)
    for manifest_type, path in expected.items():
        manifest = _load_json(path)
        assert by_type[manifest_type]["path"] == path
        assert by_type[manifest_type]["manifest_hash"] == manifest["manifest_hash"]


def test_s7_toolchain_manifest_files_are_git_tracked() -> None:
    manifest = _load_json("out/genesis_bootstrap_toolchain_manifest_v0.1.json")
    for entry in manifest["files"]:
        subprocess.run(
            ["git", "ls-files", "--error-unmatch", entry["path"]],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        assert (REPO_ROOT / entry["path"]).is_file()
        assert hashlib.sha256((REPO_ROOT / entry["path"]).read_bytes()).hexdigest() == entry["sha256"]


def test_s8_reference_implementation_manifest_scope() -> None:
    manifest = _load_json("out/genesis_reference_implementation_manifest_v0.1.json")
    paths = {entry["path"] for entry in manifest["files"]}
    assert "pyproject.toml" in paths
    assert any(path.startswith("ilc_core/") and path.endswith(".py") for path in paths)
    assert any(path.startswith("ilc_consensus/src/") and path.endswith(".rs") for path in paths)
    assert not any(path.startswith("tests/") for path in paths)
    assert not any("/target/" in path or path.startswith("target/") for path in paths)
    assert manifest["manifest_hash"] == _manifest_hash(manifest)


def test_s9_public_key_verifies_root_envelope_signature() -> None:
    signature = (REPO_ROOT / "out/genesis_signing_root_envelope_v0.1.sig").read_text(
        encoding="utf-8"
    ).strip()
    result = subprocess.run(
        [
            str(REPO_ROOT / "ilc_consensus/target/debug/pq_sign"),
            "verify",
            "--input-file",
            "out/genesis_signing_root_envelope_v0.1.json",
            "--signature-hex",
            signature,
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "signature_verified" in result.stdout
