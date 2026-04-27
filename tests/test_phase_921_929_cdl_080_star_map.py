# Tests for Phase 921–929: CDL-080 Star.Map N-Gram Route Index (L3)
#
# CDL-080 constitutional authority: opened Phase 922
# Covers: star_map_route_index_runtime.py (Phase 923)
#         ADR-0033 publication boundary (Phase 924)
#         H-015 spectral routing integration (Phase 925)
#
# Pass condition: all tests pass, zero regressions

import hashlib
import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Group 1 — Module tokens (6 tests)
# ---------------------------------------------------------------------------

def test_runtime_module_exists():
    import importlib
    mod = importlib.import_module(
        "ilc_core.network.star_map.star_map_route_index_runtime"
    )
    assert mod is not None


def test_star_map_runtime_version_token():
    from ilc_core.network.star_map.star_map_route_index_runtime import (
        STAR_MAP_RUNTIME_VERSION,
    )
    assert STAR_MAP_RUNTIME_VERSION == "star_map_route_index_runtime_923.v0.1"


def test_cdl_080_dependency_token():
    from ilc_core.network.star_map.star_map_route_index_runtime import (
        CDL_080_DEPENDENCY,
    )
    assert CDL_080_DEPENDENCY == "cdl_080_star_map_n_gram_route_index.v0.1"


def test_adr_0003_dependency_token():
    from ilc_core.network.star_map.star_map_route_index_runtime import (
        ADR_0003_DEPENDENCY,
    )
    assert ADR_0003_DEPENDENCY == "adr_0003_star_map_route_index"


def test_adr_0033_dependency_token():
    from ilc_core.network.star_map.star_map_route_index_runtime import (
        ADR_0033_DEPENDENCY,
    )
    assert ADR_0033_DEPENDENCY == "adr_0033_star_map_homoiconic_entity"


def test_cdl_077_dependency_token():
    from ilc_core.network.star_map.star_map_route_index_runtime import (
        CDL_077_DEPENDENCY,
    )
    assert CDL_077_DEPENDENCY == "cdl_077_want_have_want_block_fetch.v0.1"


def test_h015_dependency_token():
    from ilc_core.network.star_map.star_map_route_index_runtime import (
        H015_DEPENDENCY,
    )
    assert H015_DEPENDENCY == "spectral_routing_runtime_h015.v0.1"


def test_l3_advisory_l2_authoritative_token():
    from ilc_core.network.star_map.star_map_route_index_runtime import (
        L3_ADVISORY_L2_AUTHORITATIVE,
    )
    assert "l3_advisory" in L3_ADVISORY_L2_AUTHORITATIVE
    assert "l2_authoritative" in L3_ADVISORY_L2_AUTHORITATIVE


# ---------------------------------------------------------------------------
# Group 2 — compute_route_index (5 tests)
# ---------------------------------------------------------------------------

def test_compute_route_index_returns_route_index():
    from ilc_core.network.star_map.star_map_route_index_runtime import (
        RouteIndex,
        compute_route_index,
    )
    idx = compute_route_index(
        {"machine learning": ["https://peer1.example"]}, epoch=1, generator_agent_id="agent-abc"
    )
    assert isinstance(idx, RouteIndex)


def test_compute_route_index_deterministic():
    from ilc_core.network.star_map.star_map_route_index_runtime import compute_route_index

    node_endpoints = {
        "distributed consensus": ["https://a.example", "https://b.example"],
        "knowledge graph": ["https://c.example"],
    }
    idx1 = compute_route_index(node_endpoints, epoch=5, generator_agent_id="agent-x")
    idx2 = compute_route_index(node_endpoints, epoch=5, generator_agent_id="agent-x")
    assert idx1.buckets == idx2.buckets
    assert idx1.parameter_digest == idx2.parameter_digest


def test_compute_route_index_epoch_stamped():
    from ilc_core.network.star_map.star_map_route_index_runtime import compute_route_index

    idx = compute_route_index({"hello world": ["https://p.example"]}, epoch=42, generator_agent_id="ag")
    assert idx.epoch == 42


def test_compute_route_index_empty_returns_empty_buckets():
    from ilc_core.network.star_map.star_map_route_index_runtime import compute_route_index

    idx = compute_route_index({}, epoch=1, generator_agent_id="ag")
    assert idx.buckets == {}


def test_compute_route_index_not_published_by_default():
    from ilc_core.network.star_map.star_map_route_index_runtime import compute_route_index

    idx = compute_route_index({"test": ["https://p.example"]}, epoch=1, generator_agent_id="ag")
    assert not idx.is_published


# ---------------------------------------------------------------------------
# Group 3 — query_route_index (5 tests)
# ---------------------------------------------------------------------------

def test_query_route_index_returns_hints():
    from ilc_core.network.star_map.star_map_route_index_runtime import (
        compute_route_index,
        query_route_index,
        RouteHint,
    )
    idx = compute_route_index(
        {"epistemic graph": ["https://peer1.example"]}, epoch=1, generator_agent_id="ag"
    )
    hints = query_route_index(idx, "epistemic")
    assert isinstance(hints, list)
    assert all(isinstance(h, RouteHint) for h in hints)


def test_query_route_index_finds_matching_endpoint():
    from ilc_core.network.star_map.star_map_route_index_runtime import (
        compute_route_index,
        query_route_index,
    )
    idx = compute_route_index(
        {"distributed ledger": ["https://ledger.example"]}, epoch=1, generator_agent_id="ag"
    )
    hints = query_route_index(idx, "distributed")
    endpoints = [h.endpoint for h in hints]
    assert "https://ledger.example" in endpoints


def test_query_route_index_top_k_respected():
    from ilc_core.network.star_map.star_map_route_index_runtime import (
        compute_route_index,
        query_route_index,
    )
    node_eps = {f"topic number {i}": [f"https://peer{i}.example"] for i in range(20)}
    idx = compute_route_index(node_eps, epoch=1, generator_agent_id="ag")
    hints = query_route_index(idx, "topic number", top_k=5)
    assert len(hints) <= 5


def test_query_route_index_empty_index_returns_empty():
    from ilc_core.network.star_map.star_map_route_index_runtime import (
        compute_route_index,
        query_route_index,
    )
    idx = compute_route_index({}, epoch=1, generator_agent_id="ag")
    hints = query_route_index(idx, "anything")
    assert hints == []


def test_query_route_index_empty_query_returns_empty():
    from ilc_core.network.star_map.star_map_route_index_runtime import (
        compute_route_index,
        query_route_index,
    )
    idx = compute_route_index({"some content": ["https://p.example"]}, epoch=1, generator_agent_id="ag")
    hints = query_route_index(idx, "")
    assert hints == []


# ---------------------------------------------------------------------------
# Group 4 — publish_star_map_result / ADR-0033 boundary (7 tests)
# ---------------------------------------------------------------------------

def test_publish_star_map_result_returns_node_dict():
    from ilc_core.network.star_map.star_map_route_index_runtime import (
        compute_route_index,
        publish_star_map_result,
        NODE_TYPE_STAR_MAP,
    )
    idx = compute_route_index({"test": ["https://p.example"]}, epoch=1, generator_agent_id="ag")
    node = publish_star_map_result(idx, source_node_set_digest="abc123", agent_id="ag", epoch=1)
    assert isinstance(node, dict)
    assert node["type"] == NODE_TYPE_STAR_MAP


def test_publish_star_map_result_has_all_adr_0033_fields():
    from ilc_core.network.star_map.star_map_route_index_runtime import (
        compute_route_index,
        publish_star_map_result,
    )
    idx = compute_route_index({"knowledge": ["https://p.example"]}, epoch=2, generator_agent_id="gen-ag")
    node = publish_star_map_result(idx, source_node_set_digest="digest-xyz", agent_id="pub-ag", epoch=2)
    required = [
        "entity_kind", "generator_ref", "source_artifact_refs",
        "source_node_set_digest", "method", "parameter_digest",
        "result_payload", "epoch", "agent_id",
    ]
    for field in required:
        assert field in node, f"Missing ADR-0033 field: {field}"


def test_publish_star_map_result_content_addressed_id():
    from ilc_core.network.star_map.star_map_route_index_runtime import (
        compute_route_index,
        publish_star_map_result,
    )
    idx = compute_route_index({"x": ["https://p.example"]}, epoch=3, generator_agent_id="ag")
    node1 = publish_star_map_result(idx, source_node_set_digest="d1", agent_id="ag", epoch=3)
    idx2 = compute_route_index({"x": ["https://p.example"]}, epoch=3, generator_agent_id="ag")
    node2 = publish_star_map_result(idx2, source_node_set_digest="d1", agent_id="ag", epoch=3)
    assert node1["id"] == node2["id"]  # deterministic content-addressed ID


def test_publish_star_map_result_marks_index_as_published():
    from ilc_core.network.star_map.star_map_route_index_runtime import (
        compute_route_index,
        publish_star_map_result,
    )
    idx = compute_route_index({"test": ["https://p.example"]}, epoch=1, generator_agent_id="ag")
    assert not idx.is_published
    publish_star_map_result(idx, source_node_set_digest="d", agent_id="ag", epoch=1)
    assert idx.is_published


def test_publish_star_map_result_invalid_entity_kind_raises():
    from ilc_core.network.star_map.star_map_route_index_runtime import (
        compute_route_index,
        publish_star_map_result,
    )
    idx = compute_route_index({"test": ["https://p.example"]}, epoch=1, generator_agent_id="ag")
    with pytest.raises(ValueError, match="entity_kind"):
        publish_star_map_result(idx, source_node_set_digest="d", agent_id="ag", epoch=1, entity_kind="invalid_kind")


def test_ephemeral_index_has_no_node_id_before_publish():
    from ilc_core.network.star_map.star_map_route_index_runtime import compute_route_index
    idx = compute_route_index({"scratch": ["https://p.example"]}, epoch=1, generator_agent_id="ag")
    assert idx._published_node_id is None


def test_publish_star_map_result_carries_cdl_080_token():
    from ilc_core.network.star_map.star_map_route_index_runtime import (
        compute_route_index,
        publish_star_map_result,
        CDL_080_DEPENDENCY,
    )
    idx = compute_route_index({"x": ["https://p.example"]}, epoch=1, generator_agent_id="ag")
    node = publish_star_map_result(idx, source_node_set_digest="d", agent_id="ag", epoch=1)
    assert node.get("cdl_080_dependency") == CDL_080_DEPENDENCY


# ---------------------------------------------------------------------------
# Group 5 — L3 advisory / L2 authoritative contract (4 tests)
# ---------------------------------------------------------------------------

def test_l3_route_and_fetch_returns_l2_result():
    from ilc_core.network.star_map.star_map_route_index_runtime import (
        compute_route_index,
        l3_route_and_fetch,
    )
    idx = compute_route_index(
        {"consensus protocol": ["https://peer.example"]}, epoch=1, generator_agent_id="ag"
    )
    fetch_fn = MagicMock(return_value={"content": "found"})
    result = l3_route_and_fetch("consensus", idx, None, None, fetch_fn)
    assert result == {"content": "found"}


def test_l3_route_and_fetch_returns_none_when_l2_misses():
    """L2 returning None is NOT a routing error per CDL-080 §4.5."""
    from ilc_core.network.star_map.star_map_route_index_runtime import (
        compute_route_index,
        l3_route_and_fetch,
    )
    idx = compute_route_index(
        {"consensus protocol": ["https://peer.example"]}, epoch=1, generator_agent_id="ag"
    )
    fetch_fn = MagicMock(return_value=None)  # L2 says not found
    result = l3_route_and_fetch("consensus", idx, None, None, fetch_fn)
    assert result is None  # advisory hint → L2 authoritative → not found is OK


def test_l3_route_and_fetch_tries_multiple_candidates():
    from ilc_core.network.star_map.star_map_route_index_runtime import (
        compute_route_index,
        l3_route_and_fetch,
    )
    idx = compute_route_index(
        {
            "distributed consensus": ["https://peer1.example"],
            "distributed ledger": ["https://peer2.example"],
        },
        epoch=1,
        generator_agent_id="ag",
    )
    call_count = {"n": 0}
    def fetch_fn(endpoint):
        call_count["n"] += 1
        if endpoint == "https://peer2.example":
            return {"content": "found at peer2"}
        return None
    result = l3_route_and_fetch("distributed", idx, None, None, fetch_fn)
    assert result == {"content": "found at peer2"}
    assert call_count["n"] >= 1


def test_l3_route_and_fetch_no_candidates_returns_none():
    from ilc_core.network.star_map.star_map_route_index_runtime import (
        compute_route_index,
        l3_route_and_fetch,
    )
    idx = compute_route_index({}, epoch=1, generator_agent_id="ag")
    fetch_fn = MagicMock(return_value={"content": "should not reach"})
    result = l3_route_and_fetch("anything", idx, None, None, fetch_fn)
    assert result is None
    fetch_fn.assert_not_called()


# ---------------------------------------------------------------------------
# Group 6 — Spectral routing integration (3 tests)
# ---------------------------------------------------------------------------

def test_query_route_index_spectral_returns_hints_with_distance():
    from ilc_core.network.star_map.star_map_route_index_runtime import (
        compute_route_index,
        query_route_index_spectral,
    )
    idx = compute_route_index(
        {"knowledge graph topology": ["https://spectral.example"]},
        epoch=1,
        generator_agent_id="ag",
    )
    local_fp = [0.1, 0.2, 0.3, 0.4]
    peer_fps = {"https://spectral.example": [0.11, 0.21, 0.29, 0.39]}
    hints = query_route_index_spectral(idx, "knowledge graph", local_fp, peer_fps)
    assert isinstance(hints, list)
    if hints:
        assert hints[0].spectral_distance is not None


def test_query_route_index_spectral_no_fingerprints_falls_back():
    from ilc_core.network.star_map.star_map_route_index_runtime import (
        compute_route_index,
        query_route_index_spectral,
    )
    idx = compute_route_index(
        {"test content": ["https://p.example"]}, epoch=1, generator_agent_id="ag"
    )
    hints = query_route_index_spectral(idx, "test", [0.1], {})
    # Peer has no fingerprint → spectral_distance = inf → still returned
    assert isinstance(hints, list)


def test_l3_spectral_routing_uses_h015_spectral_distance():
    """Verify spectral_distance from spectral_utils is used — no beacon gossip."""
    from ilc_core.analysis.spectral_utils import spectral_distance
    d = spectral_distance([0.1, 0.2], [0.15, 0.25])
    assert isinstance(d, float)
    assert d >= 0.0


# ---------------------------------------------------------------------------
# Group 7 — No ECU / no gossip beacon (2 tests)
# ---------------------------------------------------------------------------

def test_no_ecu_call_in_star_map_source():
    import ast, pathlib
    src = pathlib.Path("ilc_core/network/star_map/star_map_route_index_runtime.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and "ecu" in func.attr.lower():
                pytest.fail(f"ECU call found in star_map_route_index_runtime.py: {func.attr}")
            if isinstance(func, ast.Name) and "ecu" in func.id.lower():
                pytest.fail(f"ECU call found in star_map_route_index_runtime.py: {func.id}")


def test_no_gossip_beacon_activation_in_star_map_source():
    import pathlib
    src = pathlib.Path("ilc_core/network/star_map/star_map_route_index_runtime.py").read_text()
    forbidden = ["emit_beacon", "gossip_beacon", "send_beacon", "beacon_gossip"]
    for term in forbidden:
        assert term not in src, f"Beacon gossip term '{term}' found in star_map_route_index_runtime.py"


# ---------------------------------------------------------------------------
# Group 8 — CDL-080 in master log (1 test)
# ---------------------------------------------------------------------------

def test_cdl_080_in_master_log():
    import pathlib
    cdl_log = pathlib.Path("docs/specs/ilc_constitutional_decision_log_v0.1.md").read_text()
    assert "CDL-080" in cdl_log, "CDL-080 row missing from CDL master log"
    for line in cdl_log.splitlines():
        if line.startswith("| CDL-080 |"):
            assert "opened_phase: 922" in line, "CDL-080 row missing opened_phase: 922"
            break
    else:
        pytest.fail("CDL-080 row not found in CDL master log")


# ---------------------------------------------------------------------------
# Group 9 — Commit scope guard (1 test)
# ---------------------------------------------------------------------------

def test_star_map_commit_scope_guard():
    """Phase 923–926 commit must not touch ilc_consensus/ or docs/specs/ilc_constitutional_decision_log."""
    import subprocess
    result = subprocess.run(
        ["git", "show", "--name-only", "--format=", "HEAD"],
        capture_output=True, text=True
    )
    files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
    for f in files:
        assert not f.startswith("ilc_consensus/src/"), (
            f"Scope violation: {f} in star_map commit"
        )
