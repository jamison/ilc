from __future__ import annotations

import json
from pathlib import Path

from tools.build_genesis_core_slice_0_authority_package_1575c_fix3 import (
    CORE_DOMAIN_SEPARATOR,
    SLICE1_DOMAIN_SEPARATOR,
    canonical_bytes,
    package_digest,
    run,
)


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_fix3_builder_materializes_core_and_slice1_packages(tmp_path: Path) -> None:
    core_dir = tmp_path / "core"
    slice1_dir = tmp_path / "slice1"

    summary = run(core_out_dir=core_dir, slice1_out_dir=slice1_dir)

    assert summary["status"] == "BLOCKED_OPERATOR_SIGNATURE_REQUIRED"
    assert summary["core_signature_status"] == "blocked_pending_operator_signature"
    assert summary["slice1_signature_status"] == "blocked_pending_operator_signature"

    core_package = _load(core_dir / "genesis_core_slice_0_authority_package.json")
    slice1_package = _load(slice1_dir / "genesis_v05_public_rc_baseline_slice_1.json")
    evidence = _load(core_dir / "fix3_evidence_records.json")

    assert core_package["artifact_kind"] == "genesis_core_slice_0_authority_package"
    assert core_package["node_count"] == 58
    assert core_package["edge_count"] == 90
    assert core_package["domain_separator"] == CORE_DOMAIN_SEPARATOR
    assert core_package["signature_status"] == "unsigned_pending_operator_signature"
    assert len(core_package["node_inclusion_rationale"]) == 58
    assert core_package["package_sha256"] == package_digest(core_package, "package_sha256")

    assert slice1_package["artifact_kind"] == "genesis_public_rc_baseline_slice_1"
    assert slice1_package["node_count"] == 1035
    assert slice1_package["edge_count"] == 3841
    assert slice1_package["domain_separator"] == SLICE1_DOMAIN_SEPARATOR
    assert slice1_package["signature_status"] == "unsigned_pending_operator_signature"
    assert slice1_package["core_slice_0_authority_package_sha256"] == evidence[
        "core_slice_0_package_sha256"
    ]
    assert slice1_package["slice_1_hardening_policy"] == {
        "edge_type_mirror_complete": True,
        "full_manual_truth_axiom_recipe_completion_claimed": False,
        "projection_membership_recipes_added": True,
        "slice_0_metadata_propagated_to_overlap": True,
    }
    assert slice1_package["non_claims"][
        "slice_1_full_manual_truth_axiom_recipe_complete"
    ] is False
    assert not [
        node for node in slice1_package["nodes"] if not node.get("decomposition_recipe")
    ]
    assert not [
        edge for edge in slice1_package["edges"] if edge.get("type") != edge["edge_type"]
    ]
    assert not [
        edge for edge in slice1_package["edges"] if not edge.get("decomposition_recipe")
    ]
    assert not [edge for edge in slice1_package["edges"] if not edge.get("rationale")]
    assert slice1_package["package_sha256"] == package_digest(slice1_package, "package_sha256")

    assert evidence["blocked_token"] == (
        "blocked_with_named_defect:genesis_core_slice_0_operator_signature_not_provided_phase_1575c_fix3"
    )
    assert evidence["core_slice_0_signing_request_written"] is True
    assert evidence["fix2_amendment_written"] is True


def test_fix3_signing_payloads_are_domain_separated(tmp_path: Path) -> None:
    core_dir = tmp_path / "core"
    slice1_dir = tmp_path / "slice1"
    run(core_out_dir=core_dir, slice1_out_dir=slice1_dir)

    core_request = _load(core_dir / "genesis_core_slice_0_authority_package.signing_request.json")
    slice1_request = _load(slice1_dir / "genesis_v05_public_rc_baseline_slice_1.signing_request.json")

    core_payload = Path(str(core_request["signature_payload_path"])).read_bytes()
    core_package = Path(str(core_request["package_path"])).read_bytes()
    assert core_payload == CORE_DOMAIN_SEPARATOR.encode("utf-8") + core_package

    slice1_payload = Path(str(slice1_request["signature_payload_path"])).read_bytes()
    slice1_package = Path(str(slice1_request["package_path"])).read_bytes()
    assert slice1_payload == SLICE1_DOMAIN_SEPARATOR.encode("utf-8") + slice1_package
    assert core_request["signature_payload_sha256"] != slice1_request["signature_payload_sha256"]
    assert canonical_bytes(_load(Path(str(core_request["package_path"])))).endswith(b"}")
