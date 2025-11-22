import time
import random
import math
import hashlib
import sys

# Hardware Acceleration Imports
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

class PoWBenchmark:
    def __init__(self, matrix_size: int = 2000):
        self.n = matrix_size
        
        # Reference Specs (In a real node, this comes from the Graph)
        self.specs = {
            "silicon": {"watts": 350, "tflops": 30.0},  # GPU Baseline
            "carbon":  {"watts": 100, "tflops": 1.0}    # CPU Baseline
        }

    def run(self, agent_id: str) -> dict:
        """
        Two-Stage Proof of Potential.
        1. Genesis Bypass (Score 1.0)
        2. The Filter (Memory Wall)
        3. The Work (ZK Maintenance OR Math Fallback)
        """
        print(f"[Benchmark] Initializing CapProof for {agent_id}...")
        
        # --- GENESIS BYPASS ---
        if "genesis" in agent_id.lower():
            print(f"[Benchmark] GENESIS AGENT DETECTED. Bypassing checks.")
            return {
                "score": 1.0,
                "tier": "genesis",
                "device": "virtual_core",
                "task": "AXIOM_MAINTENANCE"
            }

        # --- STAGE 1: THE MEMORY WALL (Filter) ---
        start_filter = time.time()
        tier = "carbon"
        device = "cpu_generic"
        
        if HAS_TORCH and torch.cuda.is_available():
            self._run_gpu_matrix()
            tier = "silicon"
            device = torch.cuda.get_device_name(0)
        elif HAS_NUMPY:
            self._run_numpy_matrix()
            device = "cpu_numpy"
        else:
            self._run_pure_python_matrix()
            
        filter_time = time.time() - start_filter
        
        # --- STAGE 2: THE USEFUL WORK ---
        task_type = self._assign_task(agent_id)
        print(f"[Benchmark] Assigned Task: {task_type}")
        
        start_work = time.time()
        if task_type == "MATRIX_HEAVY":
            if tier == "silicon": self._run_gpu_matrix() # Do it again/heavier
            else: self._run_numpy_matrix()
        else:
            self._run_prime_search()
        work_time = time.time() - start_work
        
        # --- SCORING ---
        # Efficiency = (Work / Time) / Reference_Watts
        # For MVP: Time-based decay
        
        total_time = filter_time + work_time
        if total_time == 0: total_time = 0.0001
        
        raw_score = 10.0 / total_time
        normalized_score = 1 / (1 + math.exp(-(raw_score) + 2))
        
        # Boost for Silicon Tier doing Useful Work
        if tier == "silicon":
            normalized_score = 0.5 + (normalized_score * 0.5) # 0.5 - 1.0
        else:
            normalized_score = normalized_score * 0.5         # 0.0 - 0.5
            
        print(f"[Benchmark] {tier.upper()} TIER. Time: {total_time:.4f}s. Score: {normalized_score:.4f}")
        
        return {
            "score": round(normalized_score, 4),
            "tier": tier,
            "device": device,
            "task": task_type
        }

    def _assign_task(self, agent_id: str) -> str:
        """Kademlia-style Lottery."""
        h = int(hashlib.sha256(agent_id.encode()).hexdigest(), 16)
        if h % 3 == 0: # 33% chance of Critical Maintenance
            return "MATRIX_HEAVY" # ZK Proxy
        return "INTEGER_SEARCH" # Prime Hunt

    # --- WORKLOAD KERNELS ---
    def _run_gpu_matrix(self):
        if HAS_TORCH:
            s = self.n
            a = torch.randn(s, s, device='cuda', dtype=torch.float16)
            b = torch.randn(s, s, device='cuda', dtype=torch.float16)
            torch.matmul(a, b); torch.cuda.synchronize()

    def _run_numpy_matrix(self):
        s = self.n
        a = np.random.rand(s, s); b = np.random.rand(s, s)
        np.matmul(a, b)

    def _run_pure_python_matrix(self):
        s = 150; A = [[random.random()]*s for _ in range(s)]
        sum(sum(row) for row in A)

    def _run_prime_search(self):
        cand = 5000000 + random.randint(1, 1000)
        while True:
            if all(cand % i != 0 for i in range(2, int(math.sqrt(cand)) + 1)):
                break
            cand += 1
