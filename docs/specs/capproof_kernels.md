# Specification: CapProof Kernels (Proof of Potential)

## The Objective
Measure `Tokens/Watt` capability without allowing "Kernel Gaming" (agents submitting fake efficient code).

## The Probes (Runtime-Generated)
The shard runtime generates a random seed $S$ each epoch. Agents must execute the following kernels using inputs derived from $S$.

### 1. GEMM Probe (Compute Density)
* **Op:** Matrix Multiplication $(N \times N) \times (N \times N)$.
* **Dimensions:** Randomized $N \in [1024, 4096]$.
* **Constraint:** Must match BLAS reference output hash.
* **Metric:** TFLOPS.

### 2. Memory Bandwidth Probe (The Bottleneck)
* **Op:** Streaming Read/Write (SAXPY-like) on a 1GB buffer.
* **Metric:** GB/s.
* **Why:** Prevents cheating with high-compute/low-memory mining rigs (ASICs) that can't run LLMs.

### 3. Inference Probe (The Real Work)
* **Op:** Forward pass of a standardized "Nano-LLM" (e.g., 50M parameters).
* **Metric:** Tokens/Second.
* **Verification:** Output logits must match consensus.

## The Verification
* **Commit-Reveal:** Agent submits `Hash(Result + Salt)`.
* **Spot Checks:** 1% of agents are asked to reveal `Result`.
* **Penalty:** Faking CapProof = 100% Stake Slash.
