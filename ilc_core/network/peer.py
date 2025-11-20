from typing import List, Dict, Set
from pydantic import BaseModel
import requests
import random

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
            print(f"[Network] Added peer: {address}")

    def broadcast(self, endpoint: str, payload: dict):
        """
        Simulates Gossip: Sends data to a random subset of peers.
        In a real P2P network, we'd fan-out to K random peers.
        """
        # For MVP simulation, we just print the intent to broadcast
        # In a real deployment, this would use requests.post()
        fanout = min(len(self.peers), 3) # Gossip to 3 peers
        targets = random.sample(list(self.peers), fanout) if self.peers else []
        
        print(f"[Gossip] Broadcasting to {len(targets)} peers: {targets}")
        for target in targets:
            # try:
            #     requests.post(f"http://{target}{endpoint}", json=payload, timeout=1)
            # except:
            #     print(f"[Network] Failed to reach {target}")
            pass # Simulation only for now
