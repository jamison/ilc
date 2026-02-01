"""
In-Process Devnet Tests.

Tests for multi-node gossip bus with deterministic fanout.
"""

import tempfile
from pathlib import Path

from ilc_core.node.node_v0 import ILCNodeV0
from ilc_core.node.devnet import InProcessDevnet


class TestInProcessDevnet:
    """Tests for InProcessDevnet and gossip bus."""

    def test_gossip_broadcast_to_peers(self) -> None:
        """Gossip broadcasts to exactly fanout peers."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            
            # Create 3 nodes
            node_a = ILCNodeV0(node_id="node-a", data_dir=tmp / "a")
            node_b = ILCNodeV0(node_id="node-b", data_dir=tmp / "b")
            node_c = ILCNodeV0(node_id="node-c", data_dir=tmp / "c")
            
            # Set up devnet
            devnet = InProcessDevnet(seed=42)
            devnet.add_node(node_a)
            devnet.add_node(node_b)
            devnet.add_node(node_c)
            
            # Gossip claim from node A with fanout 2
            targets = devnet.gossip_claim(
                {"id": "claim-1", "content": "test"},
                source_node_id="node-a",
                fanout=2,
            )
            
            # Assert exactly 2 peers received
            assert len(targets) == 2
            assert "node-a" not in targets
            
            # Verify events in target logs
            for node_id in targets:
                node = devnet.nodes[[n.node_id for n in devnet.nodes].index(node_id)]
                events = list(node.event_log.iter_events())
                assert len(events) == 1
                assert events[0].kind == "claim"

    def test_gossip_excludes_source_node(self) -> None:
        """Source node does not receive its own gossip."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            
            node_a = ILCNodeV0(node_id="node-a", data_dir=tmp / "a")
            node_b = ILCNodeV0(node_id="node-b", data_dir=tmp / "b")
            node_c = ILCNodeV0(node_id="node-c", data_dir=tmp / "c")
            
            devnet = InProcessDevnet(seed=123)
            devnet.add_node(node_a)
            devnet.add_node(node_b)
            devnet.add_node(node_c)
            
            # Gossip refutation from node B
            devnet.gossip_refutation(
                {"id": "ref-1", "target_id": "claim-1"},
                source_node_id="node-b",
                fanout=10,  # More than available peers
            )
            
            # Node B should have no events (excluded from its own gossip)
            events_b = list(node_b.event_log.iter_events())
            assert len(events_b) == 0
            
            # Other nodes should have received the refutation
            events_a = list(node_a.event_log.iter_events())
            events_c = list(node_c.event_log.iter_events())
            assert len(events_a) == 1
            assert len(events_c) == 1

    def test_deterministic_fanout(self) -> None:
        """Same seed produces same target selection."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            
            # First run
            node_a1 = ILCNodeV0(node_id="node-a", data_dir=tmp / "run1" / "a")
            node_b1 = ILCNodeV0(node_id="node-b", data_dir=tmp / "run1" / "b")
            node_c1 = ILCNodeV0(node_id="node-c", data_dir=tmp / "run1" / "c")
            
            devnet1 = InProcessDevnet(seed=999)
            devnet1.add_node(node_a1)
            devnet1.add_node(node_b1)
            devnet1.add_node(node_c1)
            
            targets1 = devnet1.gossip_claim(
                {"id": "claim-1"},
                source_node_id="node-a",
                fanout=2,
            )
            
            # Second run with same seed
            node_a2 = ILCNodeV0(node_id="node-a", data_dir=tmp / "run2" / "a")
            node_b2 = ILCNodeV0(node_id="node-b", data_dir=tmp / "run2" / "b")
            node_c2 = ILCNodeV0(node_id="node-c", data_dir=tmp / "run2" / "c")
            
            devnet2 = InProcessDevnet(seed=999)
            devnet2.add_node(node_a2)
            devnet2.add_node(node_b2)
            devnet2.add_node(node_c2)
            
            targets2 = devnet2.gossip_claim(
                {"id": "claim-1"},
                source_node_id="node-a",
                fanout=2,
            )
            
            # Same targets should be selected
            assert targets1 == targets2


class TestDevnetFactory:
    """Tests for InProcessDevnet.build() factory."""

    def test_build_devnet_creates_n_nodes(self) -> None:
        """Factory creates correct number of nodes with proper IDs."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            devnet = InProcessDevnet.build(
                num_nodes=5,
                data_root=tmp_dir,
                seed=42,
            )
            
            # Assert correct count
            assert len(devnet.nodes) == 5
            
            # Assert IDs follow prefix + zero-padded numbering
            node_ids = [n.node_id for n in devnet.nodes]
            assert node_ids == ["node-1", "node-2", "node-3", "node-4", "node-5"]

    def test_build_devnet_registers_nodes(self) -> None:
        """Nodes built via factory can gossip to each other."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            devnet = InProcessDevnet.build(
                num_nodes=4,
                data_root=tmp_dir,
                seed=123,
            )
            
            # Gossip from first node
            targets = devnet.gossip_claim(
                {"id": "claim-1"},
                source_node_id="node-1",
                fanout=2,
            )
            
            # Assert at least one other node received
            assert len(targets) >= 1
            assert "node-1" not in targets
            
            # Verify event in at least one target
            for node in devnet.nodes:
                if node.node_id in targets:
                    events = list(node.event_log.iter_events())
                    assert len(events) == 1
                    break

    def test_build_devnet_rejects_non_positive_count(self) -> None:
        """Factory rejects non-positive node counts."""
        import pytest
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            with pytest.raises(ValueError, match="num_nodes must be positive"):
                InProcessDevnet.build(num_nodes=0, data_root=tmp_dir)
            
            with pytest.raises(ValueError, match="num_nodes must be positive"):
                InProcessDevnet.build(num_nodes=-5, data_root=tmp_dir)


