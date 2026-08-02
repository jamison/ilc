from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import ilc_core.consensus.production_bridge as production_bridge
from ilc_core.consensus.validator_endpoint_assertion import (
    ValidatorEndpointAssertion,
    assertion_content_sha256,
    validator_assertion_candidate_id,
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
        assert edge["source_candidate_id"] == validator_assertion_candidate_id(agent_id)
        assert edge["target_candidate_id"] == validator_assertion_candidate_id(agent_id)
        assert edge["source_assertion_sha256"] == assertion_content_sha256(previous)
        assert edge["target_assertion_sha256"] == assertion_content_sha256(current)
        assert edge["source_assertion_sha256"] != edge["target_assertion_sha256"]


def test_guard_still_active() -> None:
    assert production_bridge.VALIDATOR_CERT_GRAPH_BINDING_NOT_ACTIVATED is True


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
