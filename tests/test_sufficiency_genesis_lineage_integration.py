"""Row 35f signed-artifact audit and isolated lineage-overlay fixtures."""
from __future__ import annotations

import copy
import json
import os
import shutil
from dataclasses import fields
from pathlib import Path
from typing import Any

import pytest

from tools.sufficiency_lineage.verify_genesis_slices import (
    EXPECTED_NODE_0,
    ArtifactPaths,
    LineageVerificationError,
    VerifyResult,
    canonical_root_hash,
    default_paths,
    verify_artifacts,
    verify_node_zero,
)


ROOT = Path(__file__).resolve().parents[1]
GOOD_RESULT = VerifyResult(0, "signature_verified", "")


def good_runner(*_args: Path) -> VerifyResult:
    return GOOD_RESULT


def copy_artifacts(tmp_path: Path) -> ArtifactPaths:
    source = default_paths(ROOT)
    target_root = tmp_path / "repo"
    values: dict[str, Path] = {"repo_root": target_root}
    for field in fields(ArtifactPaths):
        if field.name == "repo_root":
            continue
        original = getattr(source, field.name)
        relative = original.relative_to(ROOT)
        target = target_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original, target)
        values[field.name] = target
    return ArtifactPaths(**values)


def rewrite_json(path: Path, mutator: Any) -> None:
    value = json.loads(path.read_text(encoding="utf-8"))
    mutator(value)
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")


def overlay_verdict(record: dict[str, Any]) -> str:
    if record.get("canonical_genesis_lineage") == "local_only_not_applicable":
        return "not_applicable"
    proof = record.get("lineage_proof")
    if type(proof) is not dict:
        if record.get("canonical_genesis_lineage") == "unresolved":
            return "unresolved"
        return "negative"
    if proof.get("root_envelope_hash") != (
        "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"
    ):
        return "negative"
    if proof.get("node_0_candidate_id") != EXPECTED_NODE_0:
        return "negative"
    if proof.get("root_signature_verified") is not True:
        return "negative"
    authority_path = proof.get("directed_authority_path")
    if type(authority_path) is not list or not authority_path:
        return "negative"
    if any(type(edge) is not dict or edge.get("authority") is not True for edge in authority_path):
        return "negative"
    if proof.get("weak_connectivity_only") is True:
        return "negative"
    return "affirmative"


def valid_overlay() -> dict[str, Any]:
    return {
        "canonical_genesis_lineage": "unresolved",
        "lineage_proof": {
            "root_envelope_hash": (
                "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"
            ),
            "root_signature_verified": True,
            "node_0_candidate_id": EXPECTED_NODE_0,
            "directed_authority_path": [
                {"source": EXPECTED_NODE_0, "target": "fixture:sufficiency", "authority": True}
            ],
            "weak_connectivity_only": False,
        },
    }


def test_live_signed_artifacts_verify_with_actual_mldsa_binary() -> None:
    paths = default_paths(ROOT)
    if not paths.pq_sign.is_file() or not os.access(paths.pq_sign, os.X_OK):
        pytest.skip("compiled pq_sign verifier is not available")
    audit = verify_artifacts(paths)
    assert audit["overall_result"] == "verified"
    assert audit["core_slice_0"]["node_count"] == 58
    assert audit["core_slice_0"]["node_0_candidate_id"] == EXPECTED_NODE_0


def test_overlay_positive_case() -> None:
    assert overlay_verdict(valid_overlay()) == "affirmative"


def test_overlay_without_proof_is_negative() -> None:
    assert overlay_verdict({"canonical_genesis_lineage": "unresolved"}) == "unresolved"


def test_overlay_broken_intermediate_link_is_negative() -> None:
    record = valid_overlay()
    record["lineage_proof"]["directed_authority_path"][0]["authority"] = False
    assert overlay_verdict(record) == "negative"


def test_overlay_weak_connectivity_is_negative() -> None:
    record = valid_overlay()
    record["lineage_proof"]["weak_connectivity_only"] = True
    assert overlay_verdict(record) == "negative"


def test_local_only_receipt_is_not_applicable() -> None:
    assert overlay_verdict({"canonical_genesis_lineage": "local_only_not_applicable"}) == (
        "not_applicable"
    )


def test_package_hash_mismatch_fails(tmp_path: Path) -> None:
    paths = copy_artifacts(tmp_path)
    paths.core_package.write_bytes(paths.core_package.read_bytes() + b" ")
    with pytest.raises(LineageVerificationError, match="core_slice_0_package_sha256"):
        verify_artifacts(paths, runner=good_runner)


def test_payload_hash_mismatch_fails(tmp_path: Path) -> None:
    paths = copy_artifacts(tmp_path)
    paths.core_payload.write_bytes(paths.core_payload.read_bytes() + b"x")
    with pytest.raises(LineageVerificationError, match="core_slice_0_payload_request"):
        verify_artifacts(paths, runner=good_runner)


def test_modified_slice_package_cannot_reuse_original_signed_payload(tmp_path: Path) -> None:
    paths = copy_artifacts(tmp_path)
    rewrite_json(
        paths.slice_package,
        lambda value: value.__setitem__("unsigned_mutation", True),
    )
    from tools.sufficiency_lineage.verify_genesis_slices import sha256_file

    rewrite_json(
        paths.slice_request,
        lambda value: value.__setitem__("package_sha256", sha256_file(paths.slice_package)),
    )
    with pytest.raises(LineageVerificationError, match="slice_1_signed_payload_package_mismatch"):
        verify_artifacts(paths, runner=good_runner)


def test_genesis_key_record_digest_is_pinned(tmp_path: Path) -> None:
    paths = copy_artifacts(tmp_path)
    paths.key_record.write_text(
        paths.key_record.read_text(encoding="utf-8") + "\nunsigned mutation\n",
        encoding="utf-8",
    )
    with pytest.raises(LineageVerificationError, match="genesis_key_record_sha256"):
        verify_artifacts(paths, runner=good_runner)


def test_signature_receipt_hash_mismatch_fails(tmp_path: Path) -> None:
    paths = copy_artifacts(tmp_path)
    rewrite_json(paths.core_verification, lambda value: value.__setitem__("signature_sha256", "0" * 64))
    with pytest.raises(LineageVerificationError, match="core_slice_0_signature_verification"):
        verify_artifacts(paths, runner=good_runner)


def test_unknown_verification_receipt_field_fails(tmp_path: Path) -> None:
    paths = copy_artifacts(tmp_path)
    rewrite_json(paths.core_verification, lambda value: value.__setitem__("unexpected", True))
    with pytest.raises(LineageVerificationError, match="core_slice_0_verification_schema"):
        verify_artifacts(paths, runner=good_runner)


def test_wrong_signer_record_fails(tmp_path: Path) -> None:
    paths = copy_artifacts(tmp_path)
    rewrite_json(paths.core_request, lambda value: value.__setitem__("signer_public_key_record", "wrong"))
    with pytest.raises(LineageVerificationError, match="core_slice_0_signer_public_key_record"):
        verify_artifacts(paths, runner=good_runner)


def test_slice_anchor_mismatch_fails(tmp_path: Path) -> None:
    paths = copy_artifacts(tmp_path)
    rewrite_json(
        paths.slice_package,
        lambda value: value.__setitem__("core_slice_0_authority_package_sha256", "0" * 64),
    )
    # Retarget the signing-request hash so this case reaches the authenticated anchor check.
    from tools.sufficiency_lineage.verify_genesis_slices import sha256_file

    rewrite_json(
        paths.slice_request,
        lambda value: value.__setitem__("package_sha256", sha256_file(paths.slice_package)),
    )
    request = json.loads(paths.slice_request.read_text(encoding="utf-8"))
    payload = request["domain_separator"].encode("utf-8") + paths.slice_package.read_bytes()
    paths.slice_payload.write_bytes(payload)
    payload_hash = sha256_file(paths.slice_payload)
    rewrite_json(
        paths.slice_request,
        lambda value: value.__setitem__("signature_payload_sha256", payload_hash),
    )
    rewrite_json(
        paths.slice_verification,
        lambda value: value.__setitem__("signature_payload_sha256", payload_hash),
    )
    with pytest.raises(LineageVerificationError, match="slice_1_core_slice_0_anchor"):
        verify_artifacts(paths, runner=good_runner)


def test_missing_node_zero_fails(tmp_path: Path) -> None:
    paths = copy_artifacts(tmp_path)
    package = json.loads(paths.core_package.read_text())
    node_index = next(
        index
        for index, node in enumerate(package["nodes"])
        if node.get("candidate_id") == EXPECTED_NODE_0
    )
    replacement = copy.deepcopy(package["nodes"][(node_index + 1) % len(package["nodes"])])
    package["nodes"][node_index] = replacement
    with pytest.raises(LineageVerificationError, match="core_slice_0_node_0_count"):
        verify_node_zero(package)


def test_duplicate_node_zero_fails(tmp_path: Path) -> None:
    paths = copy_artifacts(tmp_path)
    package = json.loads(paths.core_package.read_text())
    node = next(item for item in package["nodes"] if item.get("candidate_id") == EXPECTED_NODE_0)
    replacement_index = next(
        index
        for index, item in enumerate(package["nodes"])
        if item.get("candidate_id") != EXPECTED_NODE_0
    )
    package["nodes"][replacement_index] = copy.deepcopy(node)
    with pytest.raises(LineageVerificationError, match="core_slice_0_node_0_count"):
        verify_node_zero(package)


def test_declared_core_node_count_must_match_actual_length(tmp_path: Path) -> None:
    paths = copy_artifacts(tmp_path)
    package = json.loads(paths.core_package.read_text())
    package["nodes"].pop()
    with pytest.raises(LineageVerificationError, match="core_slice_0_nodes_length"):
        verify_node_zero(package)


def test_failed_pq_sign_result_fails(tmp_path: Path) -> None:
    paths = copy_artifacts(tmp_path)

    def failed_runner(*_args: Path) -> VerifyResult:
        return VerifyResult(1, "", "invalid signature")

    with pytest.raises(LineageVerificationError, match="core_slice_0_pq_sign_returncode"):
        verify_artifacts(paths, runner=failed_runner)


def test_invalid_root_internal_hash_fails(tmp_path: Path) -> None:
    paths = copy_artifacts(tmp_path)
    rewrite_json(paths.root_envelope, lambda value: value.__setitem__("envelope_hash", "0" * 64))
    with pytest.raises(LineageVerificationError, match="root_envelope_recorded_hash"):
        verify_artifacts(paths, runner=good_runner)


def test_root_hash_recomputation_is_independent_of_recorded_value() -> None:
    envelope = json.loads((ROOT / "out/genesis_signing_root_envelope_v0.1.json").read_text())
    modified = copy.deepcopy(envelope)
    modified["envelope_hash"] = "0" * 64
    assert canonical_root_hash(modified) == envelope["envelope_hash"]
