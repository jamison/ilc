# SPDX-License-Identifier: AGPL-3.0-only
import time
import math
import hashlib
import sys
import logging

from ilc_core.identity.log_redaction_runtime import redact_agent_id_for_log

logger = logging.getLogger(__name__)


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
    """
    PoWBenchmark

    Purpose
    -------
    Provide a simple, reproducible "proof of potential" benchmark for agents.
    The output score is a scalar in [0, 1] that represents the relative
    compute capability of the agent's underlying hardware (and environment).

    Usage
    -----
        bench = PoWBenchmark(matrix_size=1024)
        result = bench.run(agent_id="agent-123")
        score = result["score"]  # 0.0 - 1.0

    This `score` is what should be passed into Governance.update_hardware_potential
    as part of the agent_potentials list for an epoch.
    """

    def __init__(self, matrix_size: int = 1024):
        # Size parameter for matrix-heavy work. Larger => heavier workload.
        self.n = int(matrix_size)

        # Reference specs (conceptual only; not hard enforcement).
        # Could be used later for more advanced FLOPS-per-watt scoring.
        self.specs = {
            "silicon": {"watts": 350, "tflops": 30.0},  # GPU baseline
            "carbon": {"watts": 100, "tflops": 1.0},    # CPU baseline
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(self, agent_id: str) -> dict:
        """
        Two-stage "proof of potential" benchmark.

        Stages
        ------
        1. Filter (Memory / Throughput check):
           - Run a matrix workload appropriate to the environment:
             GPU (torch.cuda) > NumPy > pure Python.

        2. Work (fixed kernel set):
           - Run both matrix-heavy and integer-search workloads so scores are
             comparable across agents.

        Scoring
        -------
        - Based on total time taken (filter + work).
        - Faster hardware => smaller total time => higher score.
        - Score is mapped into [0, 1] via a squashed logistic transform.
        - GPU ("silicon") gets a capped boost: score in [0.5, 1.0].
        - CPU-only ("carbon") gets score in [0.0, 0.5].

        Returns
        -------
        dict with keys:
            - "score"      : float in [0, 1]
            - "tier"       : "silicon" | "carbon" | "genesis"
            - "device"     : string describing the device type
            - "task"       : "MATRIX_HEAVY" | "INTEGER_SEARCH"
            - "total_time" : total benchmark wall-clock time (seconds)
        """
        logger.info(
            "[Benchmark] Initializing CapProof for %s",
            redact_agent_id_for_log(agent_id),
        )

        # --- ENVIRONMENT / TIER DETECTION ---------------------------------
        tier, device = self._detect_tier()

        # --- FILTER STAGE --------------------------------------------------
        start_filter = time.perf_counter()
        if tier == "silicon":
            # GPU or "fast path" filter
            self._run_gpu_or_numpy_matrix()
        else:
            # CPU-only filter
            self._run_numpy_or_python_matrix()
        filter_time = time.perf_counter() - start_filter

        # --- WORK STAGE ----------------------------------------------------
        start_work = time.perf_counter()
        if tier == "silicon":
            self._run_gpu_or_numpy_matrix(heavy=True)
        else:
            self._run_numpy_or_python_matrix(heavy=True)
        self._run_prime_search(agent_id)
        work_time = time.perf_counter() - start_work

        # --- SCORING -------------------------------------------------------
        # Efficiency proxy: smaller total_time => higher score.
        total_time = filter_time + work_time
        if total_time <= 0.0:
            total_time = 0.0001

        # Raw 'speed' metric.
        raw_score = 10.0 / total_time  # arbitrary scaling

        # Logistic squash into (0,1).
        # Center around raw_score ~= 2.0 for typical hardware.
        normalized_score = 1.0 / (1.0 + math.exp(-(raw_score - 2.0)))

        # Tier-based shaping:
        # - silicon: 0.5 - 1.0
        # - carbon: 0.0 - 0.5
        if tier == "silicon":
            normalized_score = 0.5 + (normalized_score * 0.5)
        else:
            normalized_score = normalized_score * 0.5

        # Clamp to [0,1].
        normalized_score = max(0.0, min(normalized_score, 1.0))

        logger.info(
            "[Benchmark] %s TIER. Time: %.4fs. Score: %.4f",
            tier.upper(),
            total_time,
            normalized_score,
        )

        return {
            "score": round(normalized_score, 4),
            "tier": tier,
            "device": device,
            "task": "FIXED_MATRIX_AND_INTEGER_SEARCH",
            "total_time": total_time,
        }

    # ------------------------------------------------------------------
    # Tier / environment helpers
    # ------------------------------------------------------------------
    def _detect_tier(self) -> tuple[str, str]:
        """
        Decide whether the environment is 'silicon' (GPU-capable) or
        'carbon' (CPU-only / fallback), and return a device description.
        """
        if HAS_TORCH and torch.cuda.is_available():
            dev = torch.cuda.get_device_name(0)
            return "silicon", f"cuda:{dev}"

        if HAS_NUMPY:
            return "carbon", "cpu:numpy"

        # Last-resort fallback: pure Python.
        return "carbon", "cpu:pure_python"

    # ------------------------------------------------------------------
    # Task / workload selection
    # ------------------------------------------------------------------
    def _assign_task(self, agent_id: str) -> str:
        """
        Simple lottery to decide which workload kernel is run.

        We use a hash of agent_id so each agent tends to see a stable mix
        of tasks across many epochs.
        """
        h = int(hashlib.sha256(agent_id.encode()).hexdigest(), 16)
        # ~33% chance of matrix-heavy work; otherwise prime search.
        if h % 3 == 0:
            return "MATRIX_HEAVY"
        return "INTEGER_SEARCH"

    # ------------------------------------------------------------------
    # Workload kernels
    # ------------------------------------------------------------------
    def _run_gpu_or_numpy_matrix(self, heavy: bool = False) -> None:
        """
        Run a matrix workload using GPU if available, else NumPy.

        heavy=True multiplies the effective workload size slightly.
        """
        size = self.n * (2 if heavy else 1)

        if HAS_TORCH and torch.cuda.is_available():
            s = size
            a = torch.randn(s, s, device="cuda", dtype=torch.float16)
            b = torch.randn(s, s, device="cuda", dtype=torch.float16)
            torch.matmul(a, b)
            torch.cuda.synchronize()
            return

        if HAS_NUMPY:
            s = size
            a = np.ones((s, s), dtype=float)
            b = np.ones((s, s), dtype=float)
            np.matmul(a, b)
            return

        # Fallback if neither torch nor numpy is available.
        self._run_pure_python_matrix()

    def _run_numpy_or_python_matrix(self, heavy: bool = False) -> None:
        """
        Run a matrix workload using NumPy if available, else pure Python.
        """
        size = self.n * (2 if heavy else 1)

        if HAS_NUMPY:
            s = size
            a = np.ones((s, s), dtype=float)
            b = np.ones((s, s), dtype=float)
            np.matmul(a, b)
            return

        self._run_pure_python_matrix()

    def _run_pure_python_matrix(self) -> None:
        """
        Very simple pure-Python matrix-like workload for worst-case environments.
        """
        s = 150
        A = [[((row * 131 + col * 17) % 997) / 997 for col in range(s)] for row in range(s)]
        _ = sum(sum(row) for row in A)

    def _run_prime_search(self, agent_id: str) -> None:
        """
        Integer workload: naive prime search near a deterministic large number.
        """
        offset = int.from_bytes(
            hashlib.sha256(agent_id.encode("utf-8")).digest()[:2],
            "big",
        ) % 1_000
        cand = 5_000_000 + offset + 1
        while True:
            is_prime = True
            limit = int(math.sqrt(cand)) + 1
            for i in range(2, limit):
                if cand % i == 0:
                    is_prime = False
                    break
            if is_prime:
                break
            cand += 1


# ----------------------------------------------------------------------
# Convenience helpers for simulations
# ----------------------------------------------------------------------
def run_benchmarks_for_agents(
    agent_ids: list[str],
    matrix_size: int = 1024,
) -> dict[str, float]:
    """
    Convenience function for simulations / orchestration:

        scores = run_benchmarks_for_agents(["a1", "a2", "a3"])
        median_potential = statistics.median(scores.values())

    Returns a dict mapping agent_id -> score (0.0 - 1.0).
    """
    bench = PoWBenchmark(matrix_size=matrix_size)
    scores: dict[str, float] = {}

    for aid in agent_ids:
        result = bench.run(aid)
        scores[aid] = result["score"]

    return scores
