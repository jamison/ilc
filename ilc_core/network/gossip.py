from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import copy

from .topology import DevnetTopology

class MessageType(str, Enum):
    TASK_ANNOUNCEMENT = "task_announcement"
    CLAIM_BROADCAST = "claim_broadcast"
    EPOCH_SUMMARY = "epoch_summary"
    GENERIC = "generic"

@dataclass
class Message:
    msg_id: str
    msg_type: MessageType
    origin_node: str
    payload: Dict[str, Any]
    ttl: int = 3  # hop limit

# Node ID -> List of Messages
Inboxes = Dict[str, List[Message]]

def initialize_inboxes(topology: DevnetTopology) -> Inboxes:
    """
    Creates empty inboxes for all nodes in the topology.
    """
    return {node_id: [] for node_id in topology.nodes.keys()}

def gossip_broadcast(
    topology: DevnetTopology,
    inboxes: Inboxes,
    origin_node: str,
    message: Message,
) -> None:
    """
    Enqueue a message into origin_node's inbox to seed the gossip process.
    If origin_node doesn't exist, does nothing (or could raise).
    """
    if origin_node in inboxes:
        # We place it in the origin inbox so it can be picked up by the next step
        # effectively treating "broadcast" as "I have this message, now share it"
        inboxes[origin_node].append(message)

def gossip_step(
    topology: DevnetTopology,
    inboxes: Inboxes,
) -> None:
    """
    Perform a single gossip round:
      - For each node's inbox:
          - For each message with ttl > 0:
              - deliver it to neighbors' inboxes with ttl-1
      - Messages with ttl <= 0 do not propagate further.

    This is in-place; inboxes accumulate messages.
    Duplicate deliveries are allowed for MVP.
    """
    # 1. Snapshot current messages to avoid infinite propagation in one step
    # We iterate over everything currently in inboxes.
    # New messages generated in this step will simply be appended to inboxes
    # and processed in the *next* step (or ignored if we process snapshot validly).
    
    # Actually, simpler model:
    # Gather all (node_id, message) pairs that need to be sent.
    # Then apply them.
    
    to_deliver: List[tuple[str, Message]] = []
    
    for node_id, messages in inboxes.items():
        neighbors = topology.adjacency.get(node_id, [])
        if not neighbors:
            continue
            
        for msg in messages:
            if msg.ttl > 0:
                # Prepare delivery to neighbors
                next_ttl = msg.ttl - 1
                for neighbor_id in neighbors:
                    # Create a copy with reduced TTL
                    # We use replace or copy
                    new_msg = dataclass_replace(msg, ttl=next_ttl)
                    to_deliver.append((neighbor_id, new_msg))
                    
    # 2. Deliver
    for target_node, msg in to_deliver:
        if target_node in inboxes:
            inboxes[target_node].append(msg)

def dataclass_replace(obj: Any, **changes: Any) -> Any:
    """
    Simple helper to replace fields in a dataclass, similar to dataclasses.replace
    but ensuring we don't have import issues if strictly adhering to standard lib.
    (Actually dataclasses.replace is standard lib, I'll use it).
    """
    from dataclasses import replace
    return replace(obj, **changes)
