from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import ilc_core.consensus.production_bridge as production_bridge
from ilc_core.consensus.validator_endpoint_assertion import (
    VALIDATOR_ENDPOINT_ASSERTION_NODE_KIND,
    ValidatorEndpointAssertion,
    assertion_content_sha256,
    assertion_is_superseded,
    assertion_to_atlas_node,
    canonical_assertion_payload,
    load_from_atlas,
    validator_assertion_candidate_id,
)
from tools.testbed.generate_validator_endpoint_assertions import (
    build_revision_edges,
    write_atlas_nodes,
)


MANIFEST_PATH = Path("docs/specs/ilc_validator_endpoint_assertions_manifest_1577f_v0.1.json")
PRIOR_MANIFEST_PATH = Path(
    "docs/specs/ilc_validator_endpoint_assertions_manifest_1577b_fix1_v0.1.json"
)


def _load(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_new_manifest_loads() -> None:
    manifest = _load(MANIFEST_PATH)
    assertions = manifest["assertions"]
    assert isinstance(assertions, list)
    assert len(assertions) == 4
    loaded = [ValidatorEndpointAssertion.from_dict(item) for item in assertions]
    assert {item.grpc_endpoint for item in loaded} == {
        "ilc-node-1:7101",
        "ilc-node-2:7101",
        "ilc-node-3:7101",
        "ilc-node-6:7101",
    }


def test_cert_not_after_is_future() -> None:
    manifest = _load(MANIFEST_PATH)
    cutoff = datetime(2027, 8, 1, tzinfo=timezone.utc)
    for item in manifest["assertions"]:  # type: ignore[index]
        assertion = ValidatorEndpointAssertion.from_dict(item)
        assert assertion.tls_cert_not_after_utc is not None
        not_after = datetime.strptime(
            assertion.tls_cert_not_after_utc,
            "%Y-%m-%dT%H:%M:%SZ",
        ).replace(tzinfo=timezone.utc)
        assert not_after > cutoff


def test_revision_edges_are_content_hash_scoped() -> None:
    prior = _load(PRIOR_MANIFEST_PATH)
    manifest = _load(MANIFEST_PATH)
    prior_by_agent = {
        ValidatorEndpointAssertion.from_dict(item).validator_agent_id: ValidatorEndpointAssertion.from_dict(item)
        for item in prior["assertions"]  # type: ignore[index]
    }
    new_by_agent = {
        ValidatorEndpointAssertion.from_dict(item).validator_agent_id: ValidatorEndpointAssertion.from_dict(item)
        for item in manifest["assertions"]  # type: ignore[index]
    }
    edges = manifest["revision_edges"]
    assert isinstance(edges, list)
    assert len(edges) == 4
    for assertion in new_by_agent.values():
        assert assertion.revised_by is None
    for edge in edges:
        assert isinstance(edge, dict)
        agent_id = edge["validator_agent_id"]
        assert isinstance(agent_id, str)
        previous = prior_by_agent[agent_id]
        current = new_by_agent[agent_id]
        assert edge["edge_type"] == "revised_by"
        assert str(edge["edge_id"]).startswith("validator_endpoint_assertion_revision:")
        assert edge["source_candidate_id"] == validator_assertion_candidate_id(agent_id)
        assert edge["target_candidate_id"] == validator_assertion_candidate_id(agent_id)
        assert edge["source_assertion_sha256"] == assertion_content_sha256(previous)
        assert edge["target_assertion_sha256"] == assertion_content_sha256(current)
        assert edge["source_assertion_sha256"] != edge["target_assertion_sha256"]


def test_guard_clearance_followup_has_run() -> None:
    assert production_bridge.VALIDATOR_CERT_GRAPH_BINDING_NOT_ACTIVATED is False


def test_manifest_guard_status() -> None:
    manifest = _load(MANIFEST_PATH)
    assert manifest["current_guard_clearance_status"] == (
        "fresh_certs_committed_guard_clearance_pending"
    )
    assert manifest["token"] == "validator_endpoint_assertions_manifest_committed_phase_1577f"


def test_ca_and_leaf_generation_script_present() -> None:
    script = Path("tools/testbed/renew_m009_validator_tls.py")
    assert script.exists()
    text = script.read_text(encoding="utf-8")
    assert "DEFAULT_CA_DAYS = 730" in text
    assert "DEFAULT_LEAF_DAYS = 365" in text
    assert "_renew_client_cert" in text


def test_manifest_fingerprints_match_local_der_when_present() -> None:
    manifest = _load(MANIFEST_PATH)
    genesis = _load(Path(str(manifest["config_root"])) / "genesis.json")
    validators = {
        item["agent_id"]: item["validator_id"]
        for item in genesis["validators"]  # type: ignore[index]
    }
    for item in manifest["assertions"]:  # type: ignore[index]
        assertion = ValidatorEndpointAssertion.from_dict(item)
        validator_id = validators[assertion.validator_agent_id]
        der_path = Path(str(manifest["config_root"])) / "certs" / f"validator_{validator_id}_cert.der"
        if not der_path.exists():
            continue
        import hashlib

        assert hashlib.sha256(der_path.read_bytes()).hexdigest() == (
            assertion.tls_cert_sha256_fingerprint
        )


def test_manifest_bls_signatures_verify_with_rust_helper_when_available() -> None:
    cargo = Path.home() / ".cargo/bin/cargo"
    if not cargo.exists():
        return
    manifest = _load(MANIFEST_PATH)
    for item in manifest["assertions"]:  # type: ignore[index]
        assertion = ValidatorEndpointAssertion.from_dict(item)
        result = subprocess.run(
            (
                str(cargo),
                "run",
                "--quiet",
                "--manifest-path",
                "ilc_consensus/Cargo.toml",
                "--bin",
                "validator_endpoint_assertion_bls",
                "--",
                "verify",
                "--public-key-hex",
                assertion.bls_public_key_hex,
                "--signature-hex",
                assertion.bls_signature_hex,
                "--network-id",
                str(manifest["network_id"]),
            ),
            input=canonical_assertion_payload(assertion),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=90,
        )
        assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")


def test_client_cert_was_renewed_when_local_material_present() -> None:
    cert_path = Path("config/mysticeti_testnet_M009/certs/client_cert.pem")
    if not cert_path.exists():
        return
    result = subprocess.run(
        ("openssl", "x509", "-in", str(cert_path), "-noout", "-enddate"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0
    not_after_text = result.stdout.strip().split("=", 1)[1]
    parsed = datetime.strptime(not_after_text, "%b %d %H:%M:%S %Y %Z").replace(
        tzinfo=timezone.utc
    )
    assert parsed > datetime(2027, 8, 1, tzinfo=timezone.utc)


def test_atlas_revision_edges_are_persisted_and_current_head_selected(tmp_path) -> None:
    prior = _load(PRIOR_MANIFEST_PATH)
    manifest = _load(MANIFEST_PATH)
    old = ValidatorEndpointAssertion.from_dict(prior["assertions"][0])  # type: ignore[index]
    new = next(
        ValidatorEndpointAssertion.from_dict(item)
        for item in manifest["assertions"]  # type: ignore[index]
        if ValidatorEndpointAssertion.from_dict(item).validator_agent_id == old.validator_agent_id
    )
    edges = build_revision_edges([new], revised_manifest_path=PRIOR_MANIFEST_PATH)
    write_atlas_nodes(
        tmp_path / "atlas",
        [old, new],
        source_phase="1577f-Fix1",
        revision_edges=edges,
    )

    from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore

    store = GenesisAtlasCandidateStore(tmp_path / "atlas", allow_synthetic_edge_keys=True)
    try:
        assert len(store.iter_edges()) == 1
        assert assertion_is_superseded(store, old) is True
        selected = load_from_atlas(store, old.validator_agent_id)
        assert assertion_content_sha256(selected) == assertion_content_sha256(new)
        node = assertion_to_atlas_node(selected, source_phase="1577f-Fix1")
        assert node["node_kind"] == VALIDATOR_ENDPOINT_ASSERTION_NODE_KIND
        assert node["source_phase"] == "1577f-Fix1"
    finally:
        store.close()
