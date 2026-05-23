# SPDX-License-Identifier: AGPL-3.0-or-later
"""
In-Process Devnet.

Multi-node gossip bus for local development and testing.
No HTTP/network dependencies - all communication is in-process.
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ilc_core.node.node_v0 import ILCNodeV0


class InProcessGossipBus:
    """
    In-process gossip routing with deterministic fanout.
    
    Routes events between registered nodes without network I/O.
    Uses a seeded RNG for reproducible fanout selection.
    """
    
    def __init__(self, seed: Optional[int] = None) -> None:
        """
        Initialize gossip bus.
        
        Args:
            seed: Optional RNG seed for deterministic fanout.
        """
        self._nodes: Dict[str, ILCNodeV0] = {}
        self._rng = random.Random(seed)
    
    def register(self, node: ILCNodeV0) -> None:
        """
        Register a node with the bus.
        
        Args:
            node: ILCNodeV0 instance to register.
        """
        self._nodes[node.node_id] = node
    
    def broadcast(
        self,
        kind: str,
        payload: Dict[str, Any],
        *,
        source_node_id: str,
        fanout: int = 3,
    ) -> List[str]:
        """
        Broadcast an event to a subset of peers.
        
        Args:
            kind: Event kind (e.g., "claim", "refutation").
            payload: Event payload data.
            source_node_id: ID of the originating node.
            fanout: Maximum number of peers to notify.
            
        Returns:
            List of target node IDs that received the event.
        """
        # Get eligible targets (all nodes except source)
        eligible = [
            node_id for node_id in self._nodes
            if node_id != source_node_id
        ]
        
        # Select up to fanout targets
        num_targets = min(fanout, len(eligible))
        targets = self._rng.sample(eligible, num_targets) if eligible else []
        
        # Deliver to each target
        for node_id in targets:
            node = self._nodes[node_id]
            node._record_event(kind, payload)
        
        return targets


class InProcessDevnet:
    """
    In-process development network.
    
    Manages multiple ILCNodeV0 instances and coordinates
    gossip between them via InProcessGossipBus.
    """
    
    def __init__(self, seed: Optional[int] = None) -> None:
        """
        Initialize devnet.
        
        Args:
            seed: Optional RNG seed for deterministic gossip routing.
        """
        self._nodes: List[ILCNodeV0] = []
        self._bus = InProcessGossipBus(seed=seed)
    
    def add_node(self, node: ILCNodeV0) -> None:
        """
        Add a node to the devnet.
        
        Args:
            node: ILCNodeV0 instance to add.
        """
        self._nodes.append(node)
        self._bus.register(node)
    
    def gossip_claim(
        self,
        payload: Dict[str, Any],
        *,
        source_node_id: str,
        fanout: int = 3,
    ) -> List[str]:
        """
        Gossip a claim to peers.
        
        Args:
            payload: Claim data.
            source_node_id: ID of the originating node.
            fanout: Maximum number of peers to notify.
            
        Returns:
            List of target node IDs that received the claim.
        """
        return self._bus.broadcast(
            kind="claim",
            payload=payload,
            source_node_id=source_node_id,
            fanout=fanout,
        )
    
    def gossip_refutation(
        self,
        payload: Dict[str, Any],
        *,
        source_node_id: str,
        fanout: int = 3,
    ) -> List[str]:
        """
        Gossip a refutation to peers.
        
        Args:
            payload: Refutation data.
            source_node_id: ID of the originating node.
            fanout: Maximum number of peers to notify.
            
        Returns:
            List of target node IDs that received the refutation.
        """
        return self._bus.broadcast(
            kind="refutation",
            payload=payload,
            source_node_id=source_node_id,
            fanout=fanout,
        )
    
    @property
    def nodes(self) -> List[ILCNodeV0]:
        """Access the list of registered nodes."""
        return self._nodes
    
    @property
    def bus(self) -> InProcessGossipBus:
        """Access the underlying gossip bus."""
        return self._bus
    
    @classmethod
    def build(
        cls,
        num_nodes: int,
        *,
        data_root: Union[Path, str],
        seed: Optional[int] = None,
        node_id_prefix: str = "node",
    ) -> "InProcessDevnet":
        """
        Factory method to create a devnet with N nodes.
        
        Args:
            num_nodes: Number of nodes to create.
            data_root: Root directory for node data (each node gets a subdir).
            seed: Optional RNG seed for deterministic gossip routing.
            node_id_prefix: Prefix for node IDs (default: "node").
            
        Returns:
            InProcessDevnet instance with all nodes registered.
            
        Raises:
            ValueError: If num_nodes <= 0.
        """
        if num_nodes <= 0:
            raise ValueError(f"num_nodes must be positive, got {num_nodes}")
        
        data_root = Path(data_root)
        devnet = cls(seed=seed)
        
        # Determine zero-pad width based on num_nodes
        pad_width = len(str(num_nodes))
        
        for i in range(1, num_nodes + 1):
            node_id = f"{node_id_prefix}-{str(i).zfill(pad_width)}"
            node_data_dir = data_root / node_id
            node = ILCNodeV0(node_id=node_id, data_dir=node_data_dir)
            devnet.add_node(node)
        
        return devnet

