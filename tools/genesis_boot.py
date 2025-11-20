import json
import hashlib
import time
import os

def boot_genesis():
    print("--- ILC GENESIS BOOT SEQUENCE ---")
    
    # Use relative path safe for project root
    config_path = os.path.join("config", "genesis.json")
    
    if not os.path.exists(config_path):
        print(f"ERROR: Genesis file not found at {config_path}")
        return

    # 1. Load Genesis Config
    with open(config_path, "r") as f:
        data = json.load(f)
    
    # 2. Canonicalize (sort keys for consistent hashing)
    payload = json.dumps(data, sort_keys=True).encode("utf-8")
    
    # 3. Mint Genesis Hash (The 'Root of Trust')
    genesis_hash = hashlib.sha256(payload).hexdigest()
    
    # 4. Simulate Genesis Signature (Mock Key for MVP)
    signature = hashlib.sha256(genesis_hash.encode("utf-8") + b"GENESIS_KEY").hexdigest()
    
    print(f"STATUS:  SUCCESS")
    print(f"TIME:    {time.ctime()}")
    print(f"BLOCK:   {config_path}")
    print(f"HASH:    {genesis_hash}")
    print(f"SIGNER:  agent:genesis:00")
    print(f"SIG:     {signature[:16]}...")
    print("---------------------------------")

if __name__ == "__main__":
    boot_genesis()
