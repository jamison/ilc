from typing import List, Dict, Set
import logging
from pydantic import BaseModel
import requests
import random

logger = logging.getLogger(__name__)


class Peer(BaseModel):
    host: str
    port: int
    agent_id: str

class PeerManager:
    def __init__(self, local_port: int):
        self.local_port = local_port
        self.peers: Set[str] = set() # Set of "host:port" strings
        self.banned: Set[str] = set()

    def add_peer(self, host: str, port: int):
        address = f"{host}:{port}"
        if address not in self.banned and address != f"127.0.0.1:{self.local_port}":
            self.peers.add(address)
            logger.info("network_peer_added address=%s", address)

    def broadcast(self, endpoint: str, payload: dict):
        """
        Simulates Gossip: Sends data to a random subset of peers.
        In a real P2P network, we'd fan-out to K random peers.
        """
        # For MVP simulation, we just print the intent to broadcast
        # In a real deployment, this would use requests.post()
        fanout = min(len(self.peers), 3) # Gossip to 3 peers
        targets = random.sample(list(self.peers), fanout) if self.peers else []
        
        logger.info(
            "network_gossip_broadcast endpoint=%s fanout=%s targets=%s",
            endpoint,
            len(targets),
            targets,
        )
        for target in targets:
            # Real network send path can be enabled later:
            # requests.post(f"http://{target}{endpoint}", json=payload, timeout=1)
            pass # Simulation only for now
