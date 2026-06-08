# tools/demo_walkthrough.py
import os
import subprocess
import sys
import time

import requests

REQUEST_TIMEOUT = (2.0, 10.0)

def run_demo():
    print("--- 🚀 STARTING ILC GENESIS DEMO ---")
    
    # 1. Launch the Daemon (Background Process)
    # We assume run_node.py is in the root
    # Get the root directory
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    run_node_path = os.path.join(root_dir, "run_node.py")
    
    print(f"Launching node from: {run_node_path}")
    
    process = subprocess.Popen(
        [sys.executable, run_node_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=root_dir,  # Ensure CWD is root so imports work
        start_new_session=True,  # new process group so we can kill all children
    )
    
    print("Waiting for node to boot...")
    time.sleep(5) # Give it time to spin up FastAPI
    
    try:
        base_url = "http://127.0.0.1:8000"
        
        # 2. Check Status (The Handshake)
        print("\n1. Checking Node Status...")
        resp = requests.get(f"{base_url}/", timeout=REQUEST_TIMEOUT)
        print(f"   Response: {resp.json()}")
        
        if resp.status_code != 200:
            raise Exception("Node failed to respond")

        # 3. Local demo boundary. Public/static peer wiring is intentionally
        # excluded here; mining below should not depend on external peers.
        print("\n2. Bootstrap peer step skipped for local-only demo.")

        # 4. Mine a Claim (The Labor)
        print("\n3. Mining Genesis Claim 'Hello World'...")
        payload = {
            "content": "Hello ILC World",
            "parent_id": "axiom:math:01", # Linking to Genesis Axiom
            "stake": "2.0",
        }
        mine_resp = requests.post(f"{base_url}/mine", json=payload, timeout=REQUEST_TIMEOUT)
        mining_data = mine_resp.json()
        print(f"   Mining Result: {mining_data}")
        if mine_resp.status_code != 200:
            raise Exception(f"Mining failed: {mining_data}")
        
        node_id = mining_data.get("node_id")
        if not isinstance(node_id, str) or not node_id:
            raise Exception(f"Mining response missing node_id: {mining_data}")
        
        # 5. Verify the Graph (The Truth)
        print(f"\n4. Verifying Node {node_id[:8]} in Graph...")
        read_resp = requests.get(f"{base_url}/node/{node_id}", timeout=REQUEST_TIMEOUT)
        print(f"   Graph Verification: {read_resp.json()}")
        
        print("\n--- DEMO COMPLETE: SYSTEM IS LIVE ---")

    except Exception as e:
        print(f"\n!!! DEMO FAILED: {e}")
        # Print logs if failed
        # Note: stdout/stderr might be buffered, so we might not see everything immediately
        # but we'll try to read what's available if the process has outputted anything.
        # Since Popen communicates via pipes, reading here might block if we aren't careful,
        # but for a failed/crashed process or short output it might be okay.
        # Safest is just to terminate and print what we can.
    finally:
        print("\nShutting down daemon...")
        try:
            os.killpg(os.getpgid(process.pid), 15)  # SIGTERM entire process group
        except (ProcessLookupError, PermissionError):
            process.terminate()
        try:
            outs, errs = process.communicate(timeout=5)
            if outs: print(f"Daemon Stdout:\n{outs}")
            if errs: print(f"Daemon Stderr:\n{errs}")
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(process.pid), 9)  # SIGKILL entire process group
            except (ProcessLookupError, PermissionError):
                process.kill()
            print("Daemon killed (timeout).")

if __name__ == "__main__":
    run_demo()
