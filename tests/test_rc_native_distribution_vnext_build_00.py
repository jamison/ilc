from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ilc_core.encoding.cidv1 import node_id_from_obj


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = (
    ROOT
    / "docs/specs/ilc_rc_native_distribution_vnext_build_evidence_"
    "GAP_RC_NATIVE_DISTRIBUTION_VNEXT_BUILD_00_v0.1.json"
)
SOURCE_COMMIT = "63b4d8db9313250d9ccd20bef91501732f32177f"
GENESIS_AGENT_1_ID = (
    "c43f69fcc4dfd021f5e468824c9560c03c45c601f8d004be4d244356ce604384"
    "9b9cf2af38bc51a40c1c4bc3e71b04d9"
)
PREDECESSOR_POLICY_CID = "bafyreiblyg3bvbb26c37cixhxurlkadsxcqgelk7u5rakamdui4fjwbk7y"
ARTIFACT_TYPES = {"wheel", "sdist", "binary_tarball"}
CONSENSUS_HELPERS = {
    "attribution_batch_ingest",
    "bls_verify_digest",
    "ilc_p2p_bridge",
    "invite_pop_bls",
    "keygen",
    "validator_endpoint_assertion_bls",
    "validator_harness",
}


def _payload() -> dict[str, Any]:
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def _without(value: dict[str, Any], key: str) -> dict[str, Any]:
    return {field: item for field, item in value.items() if field != key}


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _mapping_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        return set(value) | {
            key for item in value.values() for key in _mapping_keys(item)
        }
    if isinstance(value, list):
        return {key for item in value for key in _mapping_keys(item)}
    return set()


def test_vnext_build_identity_and_authorization_boundary() -> None:
    payload = _payload()

    assert payload["schema_version"] == "ilc.rc_native_distribution_vnext_build_evidence.v0.1"
    assert payload["phase"] == "GAP-RC-NATIVE-DISTRIBUTION-VNEXT-BUILD-00"
    assert payload["version"] == "0.4.34"
    assert payload["source"]["commit"] == SOURCE_COMMIT
    assert payload["source"]["tree_clean_before_build"] is True
    assert payload["authorization"] == {
        "amendment_sha256": "25956f78996c5995bc7181a4175a393427142d82cdc470b2f5f0807a996888dd",
        "baseline_manifest_sha256": "58ec4371586db19eb9cd044ed74f004dbde05f0fec5353fd112aa957fc0ffdd0",
    }
    assert "unsigned_candidate_not_authoritative" in payload["non_claims"]
    assert "no_upload_or_provider_publication" in payload["non_claims"]
    assert "no_graph_write" in payload["non_claims"]


def test_artifact_inventory_has_exact_types_and_recomputable_cids() -> None:
    payload = _payload()
    artifacts = payload["artifact_inventory"]

    assert len(artifacts) == 3
    assert {node["artifact_type"] for node in artifacts} == ARTIFACT_TYPES
    assert sum(node["artifact_type"] == "binary_tarball" for node in artifacts) == 1
    assert len({node["cid"] for node in artifacts}) == 3
    assert len({node["sha256"] for node in artifacts}) == 3
    for node in artifacts:
        assert node["node_kind"] == "ArtifactNode"
        assert node["schema_version"] == "artifact_node.v0.1"
        assert node["package_name"] == "ilc-core"
        assert node["package_version"] == "0.4.34"
        assert node["size_bytes"] > 0
        assert len(node["sha256"]) == 64
        assert node["pypi_url"].startswith(
            "https://github.com/jamison/ilc/releases/download/v0.4.34/"
        )
        assert node_id_from_obj(_without(node, "cid")) == node["cid"]


def test_candidate_graph_cids_and_cross_references_recompute() -> None:
    payload = _payload()
    inventory = payload["artifact_inventory"]
    recipe = payload["build_recipe_node"]
    assertion = payload["candidate_release_assertion"]
    release = assertion["software_release_node"]

    assert node_id_from_obj(_without(recipe, "cid")) == recipe["cid"]
    assert recipe["source_commit"] == SOURCE_COMMIT
    assert recipe["builder_agent_id"] == GENESIS_AGENT_1_ID
    assert payload["builder_execution_context"]["role"] == "builder_operator"
    assert recipe["build_env_hash"] == _canonical_sha256(payload["build_environment"])
    assert recipe["reproducibility_hash"] == _canonical_sha256(payload["reproducibility"])
    assert node_id_from_obj(_without(release, "cid")) == release["cid"]
    assert release["build_recipe_cid"] == recipe["cid"]
    assert release["artifact_cids"] == sorted(node["cid"] for node in inventory)
    assert release["changelog_hash"] == hashlib.sha256(
        payload["release_changelog"].encode("utf-8")
    ).hexdigest()
    assert assertion["artifact_nodes"] == inventory
    assert assertion["build_recipe_nodes"] == [recipe]
    assert assertion["release_attestation_edges"] == []
    assert node_id_from_obj(_without(assertion, "assertion_cid")) == assertion["assertion_cid"]


def test_reproducibility_classifications_are_exact_and_non_overclaimed() -> None:
    reproducibility = _payload()["reproducibility"]
    wheel = reproducibility["python_artifacts"]["wheel"]
    sdist = reproducibility["python_artifacts"]["sdist"]
    rust = reproducibility["rust_artifacts"]

    assert wheel["classification"] == "byte_reproducible"
    assert wheel["byte_identical"] is True
    assert wheel["run1_sha256"] == wheel["run2_sha256"]
    assert sdist["classification"] == "content_equal_archive_not_reproducible"
    assert sdist["byte_identical"] is False
    assert sdist["run1_sha256"] != sdist["run2_sha256"]
    assert sdist["member_names_equal"] is True
    assert sdist["member_payloads_equal"] is True
    assert sdist["retained_run"] == "run1"
    assert rust["classification"] == "byte_reproducible"
    assert rust["tarball_byte_identical"] is True
    assert rust["source_and_target_paths_remapped"] is True
    assert set(rust["helper_sha256"]) == CONSENSUS_HELPERS
    assert set(rust["helper_size_bytes"]) == CONSENSUS_HELPERS
    assert len(set(rust["helper_sha256"].values())) == len(CONSENSUS_HELPERS)
    initial = rust["initial_attempt"]
    assert initial["affected_helper"] == "validator_harness"
    assert initial["classification"] == "non_reproducible_absolute_target_path"
    assert initial["run1_sha256"] != initial["run2_sha256"]


def test_policy_template_is_bound_but_remains_unsigned() -> None:
    payload = _payload()
    policy = payload["policy_update_candidate"]
    fixed = policy["fixed_policy_body_fields"]
    release = payload["candidate_release_assertion"]["software_release_node"]
    artifacts = payload["artifact_inventory"]

    assert policy["status"] == "unsigned_template"
    assert fixed["policy_sequence"] == 2
    assert fixed["previous_policy_claim_cid"] == PREDECESSOR_POLICY_CID
    assert fixed["selected_software_release_cid"] == release["cid"]
    assert fixed["selected_artifact_cids"] == sorted(node["cid"] for node in artifacts)
    assert "selected_release_assertion_cid" in policy["pending_fields"]
    assert "policy_authorization.signature_hex" in policy["pending_fields"]
    keys = _mapping_keys(payload)
    assert "signature_hex" not in keys
    assert "native_submit_sig" not in keys


def test_publication_inventory_is_transport_only_and_complete() -> None:
    payload = _payload()
    expected = {node["cid"] for node in payload["artifact_inventory"]}
    publication = payload["publication_inventory"]

    assert {item["artifact_cid"] for item in publication} == expected
    assert all(item["publication_status"] == "not_published" for item in publication)
    assert all(item["retrieval_hint_authoritative"] is False for item in publication)
    binary = next(item for item in publication if item["artifact_type"] == "binary_tarball")
    assert binary["intended_providers"] == ["github_release", "ilc_peer"]
    assert "transport-neutral" in payload["retrieval_hint_boundary"]
    assert "not release authority" in payload["retrieval_hint_boundary"]


def test_unsigned_identity_boundary_is_explicit() -> None:
    payload = _payload()
    identity = payload["identity_boundary"]
    assertion = payload["candidate_release_assertion"]

    assert identity["candidate_assertion_identity"] == assertion["assertion_cid"]
    assert identity["candidate_assertion_status"] == "unsigned_non_authoritative_build_candidate"
    assert identity["software_release_identity"] == assertion["software_release_node"]["cid"]
    assert "recomputed" in identity["final_assertion_identity_rule"]
    assert payload["PUBLIC_RC_EXCLUDE"] == "unsigned_vnext_build_candidate"
