from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Any, Set

from ilc_core.graph import EpistemicGraph
from ilc_core.types import ClaimRecord, LinkRecord
from ilc_core.analysis.problem_space_kpis import ProblemSpace, infer_problem_space

@dataclass
class AgentLightConeRow:
    agent_id: str
    # Component scores
    reach_score: float
    horizon_score: float
    domain_span: int

    # Composite score
    light_cone_score: float

def compute_agent_light_cone_kpis(
    graph: EpistemicGraph,
    task_rows: Iterable[Mapping[str, Any]],
) -> Dict[str, AgentLightConeRow]:
    """
    Compute epistemic light cone KPIs per agent.

    Reach: Count of unique neighbor claims reachable from agent's claims.
    Horizon: Average verification window or deadline - creation.
    Domain Span: Count of unique problem spaces.
    """
    
    # 1. Reach Score
    # Map agent -> set of authored claim IDs
    agent_claims: Dict[str, Set[str]] = {}
    for node in graph.nodes.values():
        # Only consider claim-like nodes
        if node.type not in ("claim", "refutation", "refute"):
            continue
            
        if node.agent_id not in agent_claims:
            agent_claims[node.agent_id] = set()
        agent_claims[node.agent_id].add(node.id)
        
    # Build adjacency (undirected for reachability context)
    # Actually, let's stick to the prompt: "reachable by any incident LinkRecord"
    # So if I wrote C1, and C1->C2, C2 is in my reach. If C3->C1, C3 is in my reach.
    adj: Dict[str, Set[str]] = {}
    for link in graph.links.values():
        if link.source_id not in adj: adj[link.source_id] = set()
        if link.target_id not in adj: adj[link.target_id] = set()
        adj[link.source_id].add(link.target_id)
        adj[link.target_id].add(link.source_id)
        
    reach_scores: Dict[str, float] = {}
    all_agents = set(agent_claims.keys())
    
    for agent_id in all_agents:
        my_claims = agent_claims[agent_id]
        neighbors = set()
        for cid in my_claims:
            if cid in adj:
                neighbors.update(adj[cid])
        # Exclude my own claims from neighbors count? 
        # The prompt says "count unique neighbor claims". Usually implies distinct from self.
        # But if I link to my own claim, does it count? Let's exclude claims I authored to be safe/cleaner.
        neighbors -= my_claims
        reach_scores[agent_id] = float(len(neighbors))

    # 2. Horizon & Domain Span
    # We need to aggregate from task rows
    agent_horizons: Dict[str, float] = {}
    agent_task_counts: Dict[str, int] = {}
    agent_domains: Dict[str, Set[str]] = {}
    
    # Also track agents seen in tasks
    task_agents = set()

    for row in task_rows:
        agent_id = str(row.get("agent_id", "unknown"))
        task_agents.add(agent_id)
        
        # Horizon
        h = 1.0
        if "verification_window" in row:
            h = float(row["verification_window"])
        elif "deadline_epoch" in row and "created_epoch" in row:
            h = float(row["deadline_epoch"]) - float(row["created_epoch"])
        else:
            h = float(row.get("horizon", 1.0))
            
        agent_horizons[agent_id] = agent_horizons.get(agent_id, 0.0) + h
        agent_task_counts[agent_id] = agent_task_counts.get(agent_id, 0) + 1
        
        # Domain
        # We need to infer problem space. infer_problem_space expects a TaskRecord-like object or dict.
        # It handles dicts gracefully? Let's check imports.
        # infer_problem_space takes (task: Any). Inside it does getattr or get item.
        # So passing the row dict is fine.
        # Wait, infer_problem_space returns a ProblemSpace enum (or string if not enum).
        # It returns a string in the current codebase (Literal/str).
        p_space = infer_problem_space(row)
        if agent_id not in agent_domains:
            agent_domains[agent_id] = set()
        agent_domains[agent_id].add(p_space)

    # Final assembly
    # Union of all agents seen
    all_agents.update(task_agents)
    
    results: Dict[str, AgentLightConeRow] = {}
    
    for agent_id in all_agents:
        # Reach
        r = reach_scores.get(agent_id, 0.0)
        
        # Horizon
        total_h = agent_horizons.get(agent_id, 0.0)
        count = agent_task_counts.get(agent_id, 0)
        h_score = total_h / count if count > 0 else 0.0
        
        # Domain
        d_span = len(agent_domains.get(agent_id, set()))
        
        # Composite
        # (1 + reach) * (1 + horizon) * (1 + domain)
        lc_score = (1.0 + r) * (1.0 + h_score) * (1.0 + float(d_span))
        
        results[agent_id] = AgentLightConeRow(
            agent_id=agent_id,
            reach_score=r,
            horizon_score=h_score,
            domain_span=d_span,
            light_cone_score=lc_score
        )
        
    return results

# Post-MVP TODOs:
# - Cluster-level light cone (namespaces/shards).
# - Using light-cone deltas over time as a candidate emergent-organism signal.
# - Possible normalization by total ECUs per agent.
