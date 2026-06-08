from __future__ import annotations

import re
import pytest

from ilc_core.encoding.cidv1 import parse_nodeid_strict
from ilc_core.types import Node


HEX64_RE = re.compile(r"^[a-f0-9]{64}$")


def _sample_node() -> Node:
    return Node(
        id="",
        type="claim",
        content={"text": "dual-id-test"},
        agent_id="agent:test",
        signature="sig",
    )


def test_compute_id_defaults_to_canonical_after_flip() -> None:
    node = _sample_node()
    canonical = node.compute_canonical_id()
    default_id = node.compute_id()
    assert default_id == canonical
    assert default_id.startswith("b")


def test_compute_canonical_id_returns_cidv1() -> None:
    node = _sample_node()
    canonical = node.compute_canonical_id()
    parsed = parse_nodeid_strict(canonical)
    assert canonical.startswith("b")
    assert parsed["version"] == 1


def test_dual_id_determinism() -> None:
    node_a = _sample_node()
    node_b = _sample_node()
    assert node_a.compute_legacy_id() == node_b.compute_legacy_id()
    assert node_a.compute_canonical_id() == node_b.compute_canonical_id()
    assert HEX64_RE.match(node_a.compute_legacy_id())


def test_compute_id_rejects_non_dag_cbor_payload() -> None:
    node = Node(
        id="",
        type="task",
        content={"compute_cost_joules": 0.05},
        agent_id="agent:test",
        signature="sig",
    )
    with pytest.raises(ValueError, match="Unsupported type float"):
        _ = node.compute_id()
