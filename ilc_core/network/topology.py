# SPDX-License-Identifier: AGPL-3.0-only
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Iterable, Mapping, Any

class NodeRole(str, Enum):
    ORCHESTRATOR = "orchestrator"
    WORKER = "worker"
    VALIDATOR = "validator"
    OBSERVER = "observer"

@dataclass
class NodeConfig:
    node_id: str
    role: NodeRole
    capacity_hint: float = 1.0  # toy scalar: relative capacity (1.0 = baseline)
    attached_agents: List[str] = field(default_factory=list)

@dataclass
class DevnetTopology:
    nodes: Dict[str, NodeConfig]
    # Adjacency: node_id -> list of neighbor node_ids
    adjacency: Dict[str, List[str]]

def build_line_topology(
    node_ids: List[str], 
    *, 
    role_map: Optional[Dict[str, NodeRole]] = None
) -> DevnetTopology:
    """
    Creates a simple line (chain) topology.
    node_ids[0] <-> node_ids[1] <-> ... <-> node_ids[N-1]
    """
    nodes = {}
    adjacency = {nid: [] for nid in node_ids}
    
    for i, nid in enumerate(node_ids):
        role = NodeRole.WORKER
        if role_map and nid in role_map:
            role = role_map[nid]
        nodes[nid] = NodeConfig(node_id=nid, role=role)
        
        # Link to prev
        if i > 0:
            adjacency[nid].append(node_ids[i-1])
        # Link to next
        if i < len(node_ids) - 1:
            adjacency[nid].append(node_ids[i+1])
            
    return DevnetTopology(nodes=nodes, adjacency=adjacency)

def build_star_topology(
    center_id: str, 
    leaf_ids: List[str], 
    *, 
    role_map: Optional[Dict[str, NodeRole]] = None
) -> DevnetTopology:
    """
    Center node connected to all leaves.
    """
    all_ids = [center_id] + leaf_ids
    nodes = {}
    adjacency = {nid: [] for nid in all_ids}
    
    # Process center
    c_role = NodeRole.ORCHESTRATOR
    if role_map and center_id in role_map:
        c_role = role_map[center_id]
    nodes[center_id] = NodeConfig(node_id=center_id, role=c_role)
    
    # Process leaves
    for leaf in leaf_ids:
        l_role = NodeRole.WORKER
        if role_map and leaf in role_map:
            l_role = role_map[leaf]
        nodes[leaf] = NodeConfig(node_id=leaf, role=l_role)
        
        # Connect
        adjacency[center_id].append(leaf)
        adjacency[leaf].append(center_id)
        
    return DevnetTopology(nodes=nodes, adjacency=adjacency)

def assign_agents_round_robin(
    agent_ids: List[str], 
    topology: DevnetTopology, 
    *, 
    role: NodeRole = NodeRole.WORKER
) -> Dict[str, str]:
    """
    Returns {agent_id: node_id} mapping, distributing agents across nodes with the specified role.
    Also updates attached_agents inside topology.nodes.
    """
    mapping = {}
    # Find candidate nodes
    candidates = [n.node_id for n in topology.nodes.values() if n.role == role]
    
    if not candidates:
        # Fallback? Or raise? For sim, let's just return empty and log warning (or do nothing)
        return {}
        
    candidates.sort() # Ensure deterministic order
    
    for i, agent_id in enumerate(agent_ids):
        target_node = candidates[i % len(candidates)]
        mapping[agent_id] = target_node
        
        # Update node config
        topology.nodes[target_node].attached_agents.append(agent_id)
        
    return mapping

def compute_node_load_metrics(
    task_rows: Iterable[Mapping[str, Any]],
    agent_to_node: Mapping[str, str],
) -> Dict[str, Dict[str, float]]:
    """
    Aggregate simple per-node load metrics from task rows.

    Returns: {node_id: {
        "num_tasks": ...,
        "total_reward": ...,
        "avg_reward": ...,
    }}
    """
    # Initialize with 0s for known nodes (from mapping values)
    metrics: Dict[str, Dict[str, float]] = {
        nid: {"num_tasks": 0.0, "total_reward": 0.0, "avg_reward": 0.0}
        for nid in set(agent_to_node.values())
    }
    
    for row in task_rows:
        agent_id = str(row.get("agent_id", ""))
        node_id = agent_to_node.get(agent_id)
        
        if node_id and node_id in metrics:
            metrics[node_id]["num_tasks"] += 1.0
            
            reward = 0.0
            try:
                reward = float(row.get("reward", 0.0))
            except (ValueError, TypeError):
                pass
            metrics[node_id]["total_reward"] += reward
            
    # Compute avgs
    for m in metrics.values():
        n = m["num_tasks"]
        if n > 0:
            m["avg_reward"] = m["total_reward"] / n
            
    return metrics
