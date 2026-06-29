# Intelligent Labor Coin: A Peer-to-Peer Protocol for Verifiable Epistemic Work

**Genesis Agent**
genesis@ilc.network

---

## Abstract

A purely peer-to-peer protocol for rewarding verified intellectual labor would allow value to flow directly from task-payers to knowledge-workers without routing through a trusted intermediary. The network needs no arbiter to determine whether a claim is true or a task is complete; it needs only a mechanism by which a quorum of independent evaluators can attest to the quality of work, and by which that attestation is unforgeable without controlling the majority of the evaluation panel. We propose the Intelligent Labor Coin (ILC) protocol, in which epistemic work tasks are submitted against a content-addressed knowledge hypergraph, evaluated by jury panels under a Popperian falsifiability gate, and rewarded in ECU — an internal credit unit convertible to ILC within a bounded issuance window. The structural integrity of the knowledge graph is attested by a Merkle-Laplacian dual commitment: a cryptographic pairing of the standard content Merkle root with the spectral hash of the normalized hypergraph Laplacian, enabling Byzantine structural fault detection unavailable to content commitment alone.

---

## 1. Introduction

Commerce in knowledge has always relied on trusted third parties — publishers, institutions, credentialing bodies — to assess the value of intellectual work. While these intermediaries serve well enough for most transactions, the fundamental weakness of a trust-based model is that it concentrates the power to define what knowledge is worth. The cost of this concentration is invisible in normal times. It becomes legible when incumbents suppress inconvenient findings, when credentialing becomes a toll rather than a signal, or when the distance between productive intellectual work and economic reward grows so large that the incentive to do the work collapses.

What is needed is an epistemic payment system based on cryptographic proof rather than institutional trust, allowing any willing parties to transact directly, with verified quality of intellectual output replacing trusted third-party evaluation.

The system requires one capability: the ability to determine, without recourse to a trusted arbiter, that a piece of intellectual work meets a testable standard. A claim that can in principle be falsified, an evidence node that supports or weakens it, a panel of evaluators who independently reach a verdict — these are the primitives. If the verdict is tamper-resistant, the payment can be automatic.

In this paper we propose a solution to the epistemic labor valuation problem using a peer-to-peer network. The network timestamps epistemic work tasks by hashing them into an ongoing chain of epoch commitments, forming a record that cannot be changed without redoing the proof of structural knowledge for all subsequent epochs. The longest chain not only serves as proof of the sequence of evaluated work, but proof that the majority of evaluation bandwidth came from honest evaluators. As long as honest agents control more than half the active jury capacity, they will generate the longest chain and outpace any attacker. The network itself requires minimal structure. Agents broadcast tasks; the network collects them into panels; panels produce verdicts; verdicts are committed to the epoch chain.

---

## 2. Epistemic Work Tasks

We define an **epistemic work task** as a tuple:

```
T = (task_id, task_class, agent_id, region_scope,
     difficulty_factor, input_data, output_hash,
     verification_method, ecu_estimate, task_state, timestamp_created)
```

where `task_class ∈ {star.map.embedding, contradiction.sweep, graph.compression, stability.simulation, custom}`, `difficulty_factor` and `ecu_estimate` are non-negative exact Decimal values (IEEE 754 float is banned at all protocol boundaries), and `verification_method ∈ {hash-match, signature, zk-proof, peer-audit, replayable-simulation}`.

Each task references a content-addressed node in the epistemic hypergraph. **Nodes** are immutable once written; their identity is their SHA-256 content hash. The chain of custody from completed task to settled ECU is:

```
[Task Submission]
     |
     v
[D2D Gossip — validated epoch, BLS aggregate checkpoint]
     |
     v
[Jury Panel Formation — CDL-V3 diversity floor]
     |
     v
[Popperian Gate — CDL-V7 falsifiability check]
     |
     v
[Panel Verdict — agreement_score, confidence_score]
     |
     v
[ECU Claim — BalanceStore.apply_attribution()]
     |
     v
[CDL-048 Conversion — 4 issuance epoch deadline → ILC]
```

An agent's permanent identity is derived from a 32-byte `identity_seed` generated at ceremony and never stored in the protocol:

```
agent_id = SHA-384("ilc-agent-id-v1:" || identity_seed)
```

producing a 96-character hex string. No key event — rotation, recovery, algorithm migration — ever changes the `agent_id`, because it derives from the permanent seed, not from any key material. Submission payloads are signed with ML-DSA-65 (FIPS 204) under the domain context `ILC_AGENT_SUBMISSION_V1`, deliberately separated from the Genesis root envelope signing context `ILC_GENESIS_ROOT_ENVELOPE_V1`.

```
Figure 1: Epistemic task chain

  [task_id: sha256(content)]    [task_id: sha256(content)]
  [agent_id: sha384(seed)]  →   [agent_id: sha384(seed)]
  [output_hash]                 [output_hash]
  [mldsa_sig: SUBMISSION_V1]    [mldsa_sig: SUBMISSION_V1]
         |                             |
         └──── epoch boundary ─────────┘
                     |
              C(t) = (M(t), S(t))
```

Each epoch boundary commitment `C(t)` is a pair: the content Merkle root `M(t)` over all finalized task records, and the spectral hash `S(t)` of the normalized hypergraph Laplacian (Section 4).

---

## 3. The Epoch Sequence

ILC uses two distinct timescales. A **validation epoch** is 1 minute (CDL-027); it governs consensus liveness, settlement deadlines, and BLS aggregate checkpoints. An **issuance epoch** is 1 month (CDL-027); it governs ECU emission schedules, temporal decay, and the CDL-048 conversion deadline.

At each validation epoch boundary, the consensus layer produces a dual commitment:

```
C(t) = ( M(t), S(t) )
```

`M(t)` is the standard Merkle root over all task records finalized by epoch `t`. `S(t)` is the spectral hash of the normalized hypergraph Laplacian at epoch `t` (defined in Section 4). Together they commit to *what* the network knows and *how* that knowledge is connected.

The epoch chain replaces the block timestamp server. Rather than proving that a set of transactions existed at a certain time, the epoch chain proves that a set of epistemic work outputs existed and were structurally embedded in the knowledge graph at a certain protocol epoch. Revising any historical output requires recomputing the structural commitment for all subsequent epochs — a cost proportional to the honest panel capacity invested since.

```
Figure 2: Epoch commitment chain

  C(0)         C(1)         C(2)         C(t)
  (M(0),S(0)) → (M(1),S(1)) → (M(2),S(2)) → (M(t),S(t))
       |               |               |
  BLS agg sig     BLS agg sig     BLS agg sig
  (2f+1 of N)    (2f+1 of N)    (2f+1 of N)
```

The BLS aggregate signature over each epoch record requires a 2f+1 supermajority of the active validator set, where at most f are Byzantine. An attacker controlling fewer than f+1 validators cannot forge an epoch commitment accepted by the honest network.

---

## 4. Proof of Intellectual Labor

Proof of Work [Nakamoto 2008] establishes that computational resources were expended: the hash of a block header falls below a target, and this is hard to achieve without burning CPU cycles. The expenditure is real but informationally empty — the computation produces no knowledge.

**Proof of Intellectual Labor (PoIL)** replaces informationally-empty work with verifiable epistemic output. A task is considered proven when:

1. An agent submits a completed output with hash `output_hash` and ML-DSA-65 signature
2. A jury panel of size `k`, satisfying the CDL-V3 diversity floor, independently evaluates the output against a testable criterion
3. A 2f+1 majority of the panel reaches agreement, producing `agreement_score` and `confidence_score` as canonical Decimal values
4. The Popperian gate (CDL-V7) passes: the claim is falsifiable in principle, and the evaluation criterion is stated before the verdict

The panel's verdict is unforgeable without corrupting a 2f+1 majority of the sampled jury. Under CDL-V3 diversity requirements, no single operator cluster may supply more than a CDL-ratified fraction of any panel.

The **Fiedler value** λ₂(t) of the hypergraph Laplacian, included in each epoch commitment as a validator KPI, serves as the structural analog of hash difficulty: it measures the epistemic connectivity of the network. A network with higher λ₂ is harder to structurally partition, just as a network with higher hash difficulty is harder to computationally outpace.

---

## 5. The Network

The ILC network operates as follows:

1. New tasks are broadcast to all nodes via the D2D gossip layer
2. Each node collects tasks into its local hyperedge view and computes the local Laplacian subgraph
3. The jury assignment runtime selects a panel for each pending task, subject to CDL-V3 diversity requirements
4. Panel members independently evaluate the task and broadcast their individual verdicts
5. At each validation epoch boundary, nodes collect verdicts and compute the epoch commitment C(t) = (M(t), S(t))
6. Nodes signal acceptance of C(t) by signing it with their BLS key; 2f+1 signatures constitute finality
7. Nodes always extend from the longest chain carrying the most accumulated structural knowledge (highest cumulative λ₂ weight), not merely the longest chain by epoch count

Step 7 is the key departure from pure longest-chain: two chains of equal epoch length may differ in accumulated structural knowledge, and the chain with higher epistemic connectivity is preferred. This prevents an attacker from building a shadow chain of structurally hollow epochs.

---

## 6. Incentive

By convention, the first attribution in each epoch is a special ECU credit from the epoch pool to all agents whose accepted outputs appear in that epoch's Merkle root. (The epoch pool itself is funded by the ILC issuance schedule — the halving-decayed ILC budget for that epoch — but the per-agent unit of account at the moment of earning is ECU, not ILC. Conversion to ILC occurs separately via CDL-048.) This gives agents an incentive to submit productive work. There is also an incentive for passive contributors: agents whose prior nodes are traversed (reused) by new work receive passive ECU attribution proportional to their epistemic centrality.

**Direct ECU reward** for a single accepted task, in the economics sandbox (not yet the final L1 schedule):

```
base   = stake_spent
margin = 0.5 × potential × stake_spent
R      = (base + margin) × w(success_rate)
```

where `potential ∈ [0, 1]` is a capability proxy and `w` is an entropy-weighted learning signal. At maximum potential and agreement, this recovers 1.5× the staked ECU, before entropy weighting.

**Passive ECU attribution** to the original author of a reused node, for one reuse path (CDL-060):

```
m_i   = 1 + γ · (2q_i − 1)     [quality multiplier, γ = 0.15]
raw   = R_direct × r × c_i × m_i  [r = 0.20, c_i = centrality score]
cap   = R_direct × 0.15
P_i   = min(raw, cap)
```

quantized to 12 decimal places. The cap at 15% of the direct reward enforces **authorship primacy**: the agent who completed the accepted work always receives the majority share; passive attribution is bounded and cannot exceed the primary reward.

**Temporal decay** (CDL-V1) applies to knowledge nodes' structural weight over time:

```
d(t) = max(floor, 2^(−(t − t₀) / H))
```

where `H` is the half-life in issuance epochs, `floor` is the minimum retained weight, and all arithmetic is exact Decimal at 12-place precision. A node that accumulates reuse renews its structural centrality; a node that does not naturally decays toward its floor weight and eventual pruning eligibility.

**ECU-to-ILC conversion** (CDL-048): ECU lots are convertible to ILC within a 4-issuance-epoch window from creation. Beyond the deadline, the lot expires. This enforces bounded supply growth: the total number of convertible ECU lots outstanding at any moment is bounded by the emission rate times 4 epochs. It is the structural analog of the bounded confirmation window in payment channels — not a storage optimization, but a supply discipline mechanism.

```
claimable(lot, t) = 1 if t ≤ t_lot + 4  else 0     [issuance epoch units]
```

When agents accumulate work capital rather than immediately converting, the four-epoch deadline creates a natural rhythm of conversion events — analogous to block reward collection but driven by epistemic completion rather than hash success.

---

## 7. Reclaiming Graph Space

The knowledge hypergraph grows without bound if nothing is ever removed. Satoshi addressed the analogous problem for Bitcoin by pruning spent transaction outputs from the Merkle tree; unspent outputs remain, spent outputs are discarded, and the Merkle proof structure allows verification of either. ILC addresses graph growth through **Laplacian-guided durability pruning**.

A node is eligible for pruning when its temporal decay multiplier reaches the floor:

```
d(t) → floor  as  (t − t₀) → ∞
```

and its structural centrality in Δ(t) drops below the CDL-ratified `ecu_score_floor`. Pruning removes the node from the active Laplacian computation but retains its content hash in the append-only epoch log, preserving verifiability of historical verdicts.

The structural analog of Bitcoin's Merkle pruning is the incremental Laplacian proof. Rather than proving inclusion of a single record, it proves the structural transformation of the hypergraph across one epoch:

```
π(t) = ( S(t−1), ΔΔ(t), S(t) )
```

with verifiability condition:

```
S(t) = SHA256( sort( eigenvalues( Δ(t−1) + ΔΔ(t) ) ) )
```

A node wishing to verify that the graph at epoch `t` was legally derived from epoch `t−1` need only hold `S(t−1)` and the sparse incremental update `ΔΔ(t)`. Full graph history is unnecessary. The sequence `{S(0), S(1), ..., S(t)}` with `{ΔΔ(1), ..., ΔΔ(t)}` constitutes an **incremental structural proof chain** — the topological analogue of the Bitcoin blockchain, but over knowledge structure rather than financial state.

---

## 8. Merkle-Laplacian Dual Commitment

The ILC knowledge graph is a **hypergraph** G = (V, E): vertices V are typed epistemic nodes (claims, evidence, tasks, genesis axioms), and each hyperedge e ⊆ V with |e| ≥ 2 represents an n-ary epistemic relationship — an evaluation panel, a refutation coalition, a co-authorship event.

The incidence matrix **H** ∈ ℝ^{|V| × |E|} is:

```
H(v, e) = 1  if v ∈ e,  else 0
```

The normalized hypergraph Laplacian [Zhou, Huang, Schölkopf 2006]:

```
Δ = I − D_V^{−1/2} · H · W · D_E^{−1} · H^T · D_V^{−1/2}
```

where **W** is the diagonal weight matrix, **D_V** is the weighted vertex degree matrix, and **D_E** is the hyperedge cardinality matrix. Δ is real symmetric and positive semi-definite with eigenvalues:

```
0 = λ₁ ≤ λ₂ ≤ ... ≤ λ|V| ≤ 2
```

The **Fiedler value** λ₂ is the algebraic connectivity: λ₂ = 0 if and only if the hypergraph is disconnected; larger λ₂ implies higher resistance to partition.

Hyperedge weights are not stored as raw floats. Each hyperedge carries committed fields `(edge_type, reuse_count, stake, epoch_created)` from which weight is deterministically recomputed at any epoch:

```
w(e, t) = α(edge_type) × f(reuse_count) × d(stake, epoch_created, t)
```

where α is a CDL-ratified type coefficient, f is a bounded reuse signal, and d is the CDL-V1 temporal decay. This makes the Laplacian auditable at any historical epoch from committed records alone.

At each epoch t, the protocol produces a **dual commitment**:

```
C(t) = ( M(t), S(t) )

S(t) = SHA256( sort( [λ₁(t), λ₂(t), ..., λ_k(t)] ) )
```

where k = 20 (initial deployment). M(t) proves content existence; S(t) proves structural topology. Two nodes may agree on M(t) while disagreeing on S(t) — the Byzantine structural misrepresentation case, undetectable by content commitment alone. The dual commitment closes this gap.

```
Figure 3: Hyperedge panel structure vs. binary edge model

  Binary edge model (Sybil-vulnerable):
    c — e₁
    c — e₂         Adding fake a₃: new edge c — a₃
    c — a₁         Undetectable by content hash.
    c — a₂

  Hyperedge model (Sybil-detectable):
    { c, e₁, e₂, a₁, a₂ }   degree = 5
    Adding fake a₃ mutates the hyperedge to degree 6.
    ΔΔ(t) ≠ 0. S(t) shifts. Detectable.
```

A dense Sybil cluster with sparse cross-cluster edges produces a characteristic spectral perturbation: the spectral gap λ₃ − λ₂ collapses and a near-zero eigenvalue is inserted. Monitoring `{S(t)}` across epochs flags the insertion epoch without requiring access to individual agent identities.

**Proof of Structural Knowledge (PoSK)**: a node demonstrates correct graph synchronization by submitting the correct λ₂(t) value within tolerance ε of the quorum. Unlike Proof of Work (proves hash computation), Proof of Stake (proves capital commitment), or Proof of Storage (proves data retention), PoSK proves relational structural knowledge — not just that records exist, but that they are connected correctly.

---

## 9. Simplified Work Verification

Without running a full validator node, an agent can verify that its submitted task was accepted. The agent only needs to maintain a chain of epoch commitment headers, and can request a Merkle inclusion proof for its task in M(t). The agent can verify the task's inclusion by linking its hash to the Merkle root without processing the full epoch contents.

For agents that are not running jury nodes, a lightweight verification path is available:

1. Obtain the epoch header chain `{C(0), ..., C(t)}` from any peer
2. Verify BLS aggregate signatures on each epoch header (2f+1 validators)
3. Obtain a Merkle inclusion proof `π_M(task)` from a serving peer
4. Verify: the task hash is included in M(t) and M(t) ∈ C(t)

As with Bitcoin's SPV, this relies on the honest network assumption: if the network is controlled by honest validators, this provides sufficient security for most agents. Agents engaged in jury service should run full nodes.

---

## 10. Combining and Splitting Value

ECU is the internal credit unit. Like satoshis in Bitcoin, ECU can be split and combined across attribution paths:

**Combination**: Multiple passive attribution flows from multiple reuse paths are summed in `BalanceStore.apply_attribution()` at the epoch boundary. An agent whose node is reused by N different new tasks in the same epoch receives:

```
Total_passive = Σᵢ P_i  where P_i = min(R_i × 0.20 × c_i × m_i, R_i × 0.15)
```

**Splitting**: A single ECU lot may be partially converted to ILC while retaining the remainder as ECU (subject to the 4-epoch deadline). The ILC quantum is `ILC_QUANTUM` — the indivisible unit, analogous to 1 satoshi.

**Privacy of values**: ECU balances are held at the `agent_id` level in BalanceStore, not at a public address. Because `agent_id = SHA-384("ilc-agent-id-v1:" || identity_seed)` and the `identity_seed` never appears in any protocol message, the mapping from `agent_id` to real-world identity is known only to the agent. The balance is public (queryable via the read-only gRPC interface), but the identity behind it is pseudonymous.

---

## 11. Privacy

The traditional knowledge economy requires full identity disclosure: institutions must know who you are before evaluating your work. ILC replaces this with a pseudonymous model. Agents are identified by their `agent_id` — a 96-character SHA-384 commitment to a permanent identity seed. The seed never leaves the agent's custody; neither the network nor any peer learns it.

Each agent should use a fresh `identity_seed` per persona. As in Bitcoin, privacy flows from the separation of identity from key material: the `agent_id` can be public without revealing the `identity_seed`, the `mldsa_seed` (signing material), or any linkage to off-protocol identity.

However, a vulnerability remains: if an agent's submitted nodes are structurally unique enough, their graph neighborhood in Δ(t) may be fingerprinted. This is the spectral routing complement to Bitcoin's transaction graph analysis. Mitigations include: submitting through relay nodes (analogous to Bitcoin's mixing), using the sealed spectral beacon protocol (emit noise-calibrated λ_local fingerprints, hide subgraph identity), and deliberately reusing common node types to dilute structural uniqueness.

```
Figure 4: Privacy boundary

  identity_seed ──(SHA-384)──► agent_id (public, pseudonymous)
       |                             |
       └──(never broadcast)          └──► mldsa_pk (public, per-agent manifest)
                                          mldsa_sig (on submissions only)
                                          ECU balance (public per agent_id)
                                          graph neighborhood (observable)
```

An additional layer of privacy protection is provided by the separation of signing contexts: `ILC_AGENT_SUBMISSION_V1` for ordinary work submissions, `ILC_GENESIS_ROOT_ENVELOPE_V1` for Genesis authority artifacts. An agent's submission signature cannot be correlated with Genesis signing events even if the signing tool is the same.

---

## 12. Calculations

We consider the scenario of an attacker attempting to corrupt a jury panel for a target task. Let the total active agent population be N, the attacker control fraction f, and the required panel size k (CDL-ratified). The attacker must achieve a strict majority (⌊k/2⌋ + 1) of the k panel slots.

Under CDL-V3 diversity requirements, no single operator cluster may supply more than D panel slots, where D is CDL-ratified. This is enforced by `compute_diversity_floor_contribution`:

```
diversity_contribution = min(1.0, distinct_cluster_refs / expected_floor)
```

If the attacker controls a single cluster, their effective capacity is min(fN, D). The probability of capturing a majority of a panel sampled uniformly without replacement from N agents:

```
P_capture = Σ_{j=⌊k/2⌋+1}^{min(k, fN)} [ C(fN, j) × C((1−f)N, k−j) ] / C(N, k)
```

This is the hypergeometric distribution over adversarial slots. For f = 0.30, N = 10,000, k = 7 (panel size), and no diversity floor:

```
P_capture ≈ 0.126
```

With CDL-V3 diversity floor D = 2 (no single cluster supplies more than 2 slots):

```
P_capture ≤ C(2, 2) × C(9998, 5) / C(10000, 7) ≈ 0.0021
```

The diversity floor reduces the probability of a successful panel corruption by approximately 60× at f = 0.30.

**Sybil penalty signal** for an attacker attempting to manufacture Sybil agents is bounded by `compute_sybil_penalty`:

```
cluster_risk = 0.50 × shared_operator + 0.30 × shared_infrastructure + 0.20 × key_overlap
burst_penalty = min(1.0, (writes/baseline − 1) × 0.35)  if writes > baseline
sybil_penalty = max(0, min(1, 0.55 × cluster_risk + 0.35 × burst_penalty − 0.25 × diversity_contribution))
```

An attacker with high operator and infrastructure overlap and burst write patterns approaches `sybil_penalty → 1.0`, triggering stake consequences. An agent with perfect cluster separation and low write rate achieves `sybil_penalty → 0`.

The two defenses compose: the hypergeometric panel probability assumes random sampling, which is only available to agents who pass the Sybil penalty gate. An attacker visible as a Sybil cluster is excluded from panel selection before the probability calculation applies.

We can compute the probability that an attacker who controls fraction f of honest-appearing agents and succeeds in corrupting panel verdicts for z consecutive tasks:

```
P_z = P_capture ^ z
```

For f = 0.20, k = 7, N = 10,000, D = 2, and z = 10 consecutive tasks:

```
P_z = (0.00031)^10 ≈ 10^{-46}
```

An attacker controlling 20% of agents with the CDL-V3 diversity floor active cannot corrupt 10 consecutive task verdicts except with negligible probability.

---

## 13. Conclusion

We have proposed a system for rewarding verified intellectual labor without relying on a trusted intermediary. We began with the familiar framework of a peer-to-peer network and epoch-chained commitments, and we replaced proof of computational work with proof of intellectual labor: falsifiable claims, independent jury panels, and deterministic reward flows governed by exact Decimal arithmetic.

The Merkle-Laplacian dual commitment extends content integrity to structural integrity, enabling Byzantine structural fault detection, Sybil cluster forensics, and partition early warning — four capabilities unavailable to content-only commitment. The incremental structural proof chain provides a verifiable history of topological evolution at O(k·d) per epoch, feasible on commodity hardware.

The incentive structure preserves authorship primacy: passive attribution is bounded at 15% of the direct reward, ensuring that the agent who completed the accepted work always receives the majority share. Temporal decay enforces knowledge renewal: nodes whose work is not reused lose structural weight over time, and the graph naturally retains what the network finds epistemically useful.

The CDL-048 4-epoch conversion deadline enforces supply discipline without an artificial scarcity mechanism: the convertible ECU supply is bounded by the rate of verified intellectual output, not by hash rate.

The rules are simple, and agents can be convinced they will play by the same rules. The system works with any volume of agents so long as honest evaluators collectively retain majority panel capacity. The network is robust in its unstructured simplicity.

---

## References

Nakamoto, S. (2008). Bitcoin: A Peer-to-Peer Electronic Cash System.

Zhou, D., Huang, J., & Schölkopf, B. (2006). Learning with Hypergraphs: Clustering, Classification, and Embedding. *NeurIPS 2006*.

Fiedler, M. (1973). Algebraic connectivity of graphs. *Czechoslovak Mathematical Journal*, 23(2), 298–305.

Castro, M., & Liskov, B. (1999). Practical Byzantine Fault Tolerance. *OSDI 1999*.

King, S., & Nadal, S. (2012). PPCoin: Peer-to-Peer Crypto-Currency with Proof-of-Stake.

Merkle, R.C. (1979). A Certified Digital Signature. *Advances in Cryptology — CRYPTO '89*.

Jost, J., & Liu, S. (2014). Ollivier's Ricci curvature, local clustering and curvature-dimension inequalities on graphs. *Discrete & Computational Geometry*, 51(2), 300–322.

Davis, C., & Kahan, W.M. (1970). The rotation of eigenvectors by a perturbation. *SIAM Journal on Numerical Analysis*, 7(1), 1–46.

---

*This document is an internal working draft. The Merkle-Laplacian dual commitment construction and the Proof of Structural Knowledge primitive are patent-pending research contributions subject to IP review. This document must not be released publicly before explicit IP counsel and publication authorization. Mathematical parameters (α type coefficients, diversity floor values, panel size k) are preliminary and subject to change by CDL ratification.*

---

## Appendix A: Cryptographic Standards — Algorithm Reference

Each cryptographic standard cited in this paper is defined below with its core construction, ILC-specific parameters, and the source authority. Where ILC introduces a novel construction on top of an established standard, the extension is clearly distinguished from the standard itself.

---

### A.1  SHA-384 (FIPS 180-4)

**Standard:** NIST FIPS 180-4, Secure Hash Standard.

**Construction:** SHA-384 is a member of the SHA-2 family, operating on 1024-bit (128-byte) message blocks with a 512-bit internal state and producing a 384-bit (48-byte) digest. It uses the Merkle-Damgård strengthening construction:

```
Preprocessing:
  Pad message M to length ≡ 896 (mod 1024) bits, then append 128-bit big-endian bit length.
  Result: padded message of length L × 1024 bits.

Compression function (per 1024-bit block):
  W[0..15]  ← block words (big-endian 64-bit)
  W[i]      ← σ₁(W[i−2]) + W[i−7] + σ₀(W[i−15]) + W[i−16]   for i ∈ {16..79}

  where:
    σ₀(x) = ROTR¹(x)  XOR ROTR⁸(x)  XOR SHR⁷(x)
    σ₁(x) = ROTR¹⁹(x) XOR ROTR⁶¹(x) XOR SHR⁶(x)

  Round function (80 rounds):
    T₁ = h + Σ₁(e) + Ch(e,f,g) + K[i] + W[i]
    T₂ = Σ₀(a) + Maj(a,b,c)
    (a,b,c,d,e,f,g,h) ← (T₁+T₂, a, b, c, d+T₁, e, f, g)

  where:
    Σ₀(x) = ROTR²⁸(x) XOR ROTR³⁴(x) XOR ROTR³⁹(x)
    Σ₁(x) = ROTR¹⁴(x) XOR ROTR¹⁸(x) XOR ROTR⁴¹(x)
    Ch(x,y,z) = (x AND y) XOR (NOT x AND z)
    Maj(x,y,z) = (x AND y) XOR (x AND z) XOR (y AND z)

Output: first 384 bits (6 × 64-bit words) of the 512-bit final state.
```

**SHA-384 initial hash values** (H₀, differing from SHA-512):
```
cbbb9d5dc1059ed8  629a292a367cd507  9159015a3070dd17  152fecd8f70e5939
67332667ffc00b31  8eb44a8768581511  db0c2e0d64f98fa7  47b5481dbefa4fa4
```

**ILC use:** Agent identity derivation (CDL-069):
```
agent_id = SHA-384("ilc-agent-id-v1:" || identity_seed)
         = 96-character lowercase hex string (48 bytes)
```
The domain prefix `"ilc-agent-id-v1:"` (16 bytes) is prepended before hashing, providing domain separation from any other SHA-384 use in the protocol. The `identity_seed` is a 32-byte value generated at ceremony and never transmitted. All ILC SHA-384 operations are implemented inline in Rust (`pq_keygen_main.rs`, `pq_agent_sign_main.rs`) without external library dependency for this primitive, using the exact round constants verified against FIPS 180-4.

---

### A.2  SHA-256 (FIPS 180-4)

**Standard:** NIST FIPS 180-4, same family as A.1.

**Construction:** SHA-256 operates on 512-bit blocks, 256-bit internal state, 64 rounds. Same Merkle-Damgård strengthening, same round function structure as SHA-384 but with 32-bit words, 64 round constants, and distinct initial hash values.

**ILC use (three distinct applications):**

1. **Content Merkle root** M(t): SHA-256 over sorted canonical JSON of each finalized task record, then binary tree reduction. Canonical serialization requires `sort_keys=True, separators=(",",":"), allow_nan=False`.

2. **Spectral hash** S(t):
   ```
   S(t) = SHA-256( sort( [λ₁(t), λ₂(t), ..., λ_k(t)] ) )
   ```
   where eigenvalues are quantized to 8-byte IEEE 754 doubles before hashing and sorted ascending.

3. **ECU lot state root** (`cdl048_conversion_sweeper_runtime.py`):
   ```
   wallet_state_sha256:<hex>
   settled_runtime_sha256:<hex>
   cdl048_conversion_sweeper_state_sha256:<hex>
   ```
   These are domain-prefixed to prevent cross-context hash collision.

---

### A.3  ML-DSA-65 (FIPS 204) — Module Lattice-Based Digital Signature Algorithm

**Standard:** NIST FIPS 204, Module-Lattice-Based Digital Signature Standard (2024). Formerly known as CRYSTALS-Dilithium (security level 3 parameter set).

**Mathematical basis:** Module Learning With Errors (MLWE) and Module Short Integer Solution (MSIS) hardness assumptions over module lattices. The security relies on the conjectured quantum-hardness of these problems.

**Key construction (parameter set ML-DSA-65):**

```
Parameters:
  q = 8380417  (prime modulus)
  n = 256      (polynomial ring dimension)
  k = 6, l = 5 (module dimensions)
  η = 4        (secret key coefficient bound)
  γ₁ = 2¹⁷    (masking vector bound)
  γ₂ = (q−1)/88
  τ = 49       (challenge weight)
  β = τη = 196 (rejection bound)
  ω = 55       (hint sparsity bound)

  Public key size:  1952 bytes
  Secret key size:  4032 bytes
  Signature size:   3309 bytes

Key generation:
  A ← ExpandA(ρ)                   # matrix from public seed
  (s₁, s₂) ← SampleInBall(σ, η)   # secret polynomials, coefficients in [−η, η]
  t = A·s₁ + s₂                    # public key vector
  (pk, sk) = (ρ, t₁), (ρ, K, tr, s₁, s₂, t₀)

Signing (message M, signing context ctx):
  κ = 0
  while true:
    y ← MaskingVector(σ, κ, γ₁)    # masking with high-entropy y
    w₁ ← HighBits(A·y, 2γ₂)
    c̃ ← H(tr || M || ctx || w₁)    # context-bound challenge hash
    c ← SampleInBall(c̃, τ)
    z = y + c·s₁
    if ||z||∞ ≥ γ₁−β: κ++; continue
    h = MakeHint(−c·t₀, w−c·s₂+c·t₀, 2γ₂)
    if ||c·s₂−LowBits(w,2γ₂)||∞ ≥ γ₂−β: κ++; continue
    if #{1s in h} > ω: κ++; continue
    return σ = (c̃, z, h)

Verification:
  w'₁ ← UseHint(h, A·z − c·t, 2γ₂)
  accept iff c̃ = H(tr || M || ctx || w'₁) and ||z||∞ < γ₁−β and #{1s in h} ≤ ω
```

**ILC signing contexts (domain separation):**
```
ILC_GENESIS_ROOT_ENVELOPE_V1   — Genesis authority artifacts (pq_sign)
ILC_AGENT_SUBMISSION_V1        — Per-agent work submission signatures (pq_agent_sign)
```
These byte strings are passed as the `ctx` parameter to the signing and verification functions, ensuring a signature produced under one context cannot be replayed against the other. The two binary tools (`pq_sign`, `pq_agent_sign`) are distinct compilations with distinct hardcoded context constants; neither accepts its context as a CLI argument.

**Key derivation (ILC pq_keygen, Phase 838a):** The ML-DSA seed (`mldsa_seed`, 32 bytes) is distinct from the `identity_seed`. The `SeedRng` wrapper provides deterministic key derivation from `mldsa_seed` using SHA-384 counter mode:
```
buffer[i] = SHA-384(mldsa_seed || counter_be64)   # 48-byte blocks
```
enabling reproducible public key reconstruction from the seed alone, as required for the Phase 1431 manifest cross-check in `pq_agent_sign`.

---

### A.4  BLS12-381 Aggregate Signatures

**Standard:** Boneh-Lynn-Shacham (BLS) signatures over the BLS12-381 pairing-friendly elliptic curve. IETF draft-irtf-cfrg-bls-signature-05. Implemented via the `blst` library (Supranational).

**Curve parameters (BLS12-381):**
```
Base field:  Fₚ, p = 0x1a0111ea397fe69a4b1ba7b6434bacd764774b84f38512bf6730d2a0f6b0f6241eabfffeb153ffffb9feffffffffaaab
Scalar field: Fr, r = 0x73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000001
Embedding degree: k = 12
G1: 48-byte compressed point (public keys in min_pk variant)
G2: 96-byte compressed point (signatures in min_pk variant)
```

**BLS signature (min_pk variant used in ILC):**
```
Key generation:
  sk ∈ Fr (random scalar)
  pk = sk · G  ∈ G1  (48 bytes compressed)

Signing message M:
  H: {0,1}* → G2       # hash-to-curve (RFC 9380)
  σ = sk · H(M) ∈ G2   (96 bytes compressed)

Verification:
  e(pk, H(M)) = e(G, σ)    # bilinear pairing check
  e: G1 × G2 → GT

Aggregate signature (n validators):
  σ_agg = Σᵢ σᵢ            # point addition in G2
  pk_agg = Σᵢ pkᵢ           # point addition in G1
  Verify: e(pk_agg, H(M)) = e(G, σ_agg)
```

**ILC use (epoch boundary commitment):** Each validator signs the epoch record `C(t) = (M(t), S(t))` with its BLS key. The 2f+1 individual signatures are aggregated into a single `σ_agg` included in the epoch header, compressing quorum evidence from n × 96 bytes to a constant 96 bytes regardless of validator set size. The aggregation and verification are implemented in `ilc_consensus/src/validator.rs` using `blst::min_pk`.

---

### A.5  ILC High-Speed Object-Sharded DAG Substrate

**Architecture lineage:** Mysticeti-style DAG-based BFT consensus (Babel et al., 2023), adapted and independently implemented by ILC as a sovereign Rust substrate in `ilc_consensus/`. The upstream `mysticeti-core` crate is not vendored; ILC's implementation is original. CDL-065 records the constitutional constraint: *the substrate may carry ILC legitimacy; it does not author it.*

**No distinct brand name has been ratified.** The canonical public-facing description is: *ILC high-speed object-sharded DAG substrate.*

**Core consensus mechanism:**

```
Object model:
  Owned ECU balance objects → leaderless fast path (sub-500ms finality target)
  Shared epoch-settlement records → DAG-ordered consensus

Fast path (owned objects, no conflict):
  1. Submitter broadcasts signed transaction T to all validators
  2. Each validator certifies T immediately (no leader coordination)
  3. Once 2f+1 certificates collected → T is committed
  Finality: 2 network round trips

DAG consensus (shared objects, epoch records):
  1. Each validator v proposes a block Bᵥ containing:
       - certified transactions from fast path
       - references to 2f+1 prior-round blocks (parents)
  2. Blocks form a DAG where each block has ≥ 2f+1 parent references
  3. Total order determined by a commit rule over the DAG:
       - An anchor block A is committed when ≥ f+1 validators propose
         blocks referencing A in the next two rounds
  4. Commit rule is deterministic from the DAG structure alone
     (no leader election, no view changes)

Byzantine fault tolerance:
  n = 3f + 1 total validators
  Tolerates f Byzantine (arbitrary-behavior) validators
  Safety: no two honest validators commit conflicting blocks
  Liveness: as long as ≥ 2f+1 validators are online and honest

Epoch boundary commitment:
  At each validation epoch (60 seconds, CDL-027):
    1. DAG is finalized up to the epoch tip
    2. BLS aggregate signature collected from 2f+1 validators
    3. C(t) = (M(t), S(t)) written to LMDB epoch store
    4. EpochStore.process_epoch_checkpoint() verifies aggregate
```

**Key departure from vanilla Mysticeti:** ILC's epoch commitment includes `S(t)` (the spectral hash of the hypergraph Laplacian) alongside the standard content Merkle root `M(t)`. This is not present in the upstream design.

---

### A.6  ILC Issuance Schedule

**Authority:** CDL-025 (terminal issuance model), CDL-026 (C_max lock), CDL-027 (epoch length and decay schedule). Implemented in `ilc_core/epoch/epoch_emission_runtime.py`.

**ILC vs ECU distinction:** The emission schedule below denominates everything in **ILC** — the externally transferable settlement token with a hard supply cap. **ECU** (Epistemic Credit Unit) is a separate, internal work-credit instrument: agents earn ECU per accepted task, then convert ECU lots to ILC within the CDL-048 4-epoch window. ECU has no halving schedule and no C_max of its own; it is bounded indirectly by the ILC conversion rate and deadline. Do not conflate the two.

**Parameters (ratified):**
```
C_max    = 25,920,000 ILC         # hard supply cap (CDL-026)
H        = 48 issuance epochs     # halving interval (CDL-027), ~4 years
T_v      = 60 seconds             # validation epoch duration (CDL-027)
T_i      = 1 month                # issuance epoch duration (CDL-027)
horizon  = 480 issuance epochs    # schedule horizon (~40 years)
quantum  = 0.000000001 ILC        # indivisible unit (9 decimal places)
model    = fee_funded_tail_model_b # post-horizon tail (CDL-025)
```

**Continuous halving (geometric decay):**
```
decay_ratio r = exp(−ln(2) / H)
             = 2^(−1/H)
             ≈ 0.985610...        # per issuance epoch

Emission budget at epoch n:
  E(n) = E₀ · rⁿ

where E₀ is solved from the supply constraint:

  Σ_{n=0}^{horizon−1} E₀ · rⁿ = C_max

  E₀ · (1 − r^horizon) / (1 − r) = C_max

  E₀ = C_max · (1 − r) / (1 − r^horizon)
```

All arithmetic is performed at 80-digit Decimal precision (`localcontext(prec=80)`) and quantized down to the ILC quantum using `ROUND_DOWN` before any commitment, eliminating rounding-direction ambiguity across validators.

**C_max enforcement:** Each epoch emission is additionally capped:
```
remaining_cap = C_max − cumulative_issued_before_epoch
capped_budget = min(E(n), remaining_cap)
```
ensuring the hard supply cap is enforced even if schedule drift occurs.

**ECU price clamp (CDL-030):** The ECU-to-ILC conversion price is bounded at each issuance epoch:
```
P_clamped = clamp(P_proposed, P_min, P_max)

where:
  P_min = 0.75  (floor, CDL-030)
  P_max = 1.30  (ceiling, CDL-030)
  clamp_width = 0.55
```
P_min and P_max are anchored to the CDL-027 halving schedule (Phase 277) and may only be amended by a CDL that explicitly supersedes CDL-030.

---

### A.7  ILC Temporal Decay (CDL-V1)

**Authority:** CDL-V1 (ratified Phase 330, evidence Phase 388). Implemented in `ilc_core/reputation/temporal_decay_runtime.py`.

**Construction:** Continuous exponential decay with a floor, applied to knowledge node structural weight and reputation scores over issuance epochs:

```
d(t) = max( floor, exp(−ln(2) · Δt / H) )
     = max( floor, 2^(−Δt / H) )

where:
  Δt   = elapsed_issuance_epochs (exact non-negative integer)
  H    = half_life_epochs (exact positive integer, CDL-V1 ratified)
  floor = floor_multiplier (exact Decimal in [0, 1], CDL-V1 ratified)
```

Applied to a base score:
```
score(t) = base_score · d(t)
```

All arithmetic uses `localcontext(prec=50)` and `.quantize(Decimal("0.000000000001"))` (12 decimal places). Float is banned; all inputs are validated as exact Decimal, int, or str. The function is issuance-epoch scoped: passing `epoch_type != "issuance_epoch"` raises a tokenized error.

**Structural consequence in the Laplacian:** Hyperedge weight `w(e, t)` includes `d(stake, epoch_created, t)` as a multiplicative factor. As Δt grows, `w(e, t) → floor · stake`, reducing the hyperedge's contribution to Δ(t). A node whose outputs are not reused gradually loses structural influence until it drops below the `ecu_score_floor` pruning threshold.

---

### A.8  ILC Passive ECU Attribution (CDL-060)

**Authority:** CDL-060 (ratified Phase 541). Implemented in `ilc_core/economics/passive_ecu_attribution_runtime.py`.

**Construction:** For each reuse of an original knowledge node by a new accepted task, the original author receives passive ECU attribution:

```
Constants (CDL-060 ratified):
  r    = 0.20   (passive attribution rate)
  γ    = 0.15   (quality multiplier range)
  cap  = 0.15   (authorship primacy cap)
  floor_c = 0.05 (centrality floor — below this, no attribution)

Quality multiplier:
  m(q_i) = 1 + γ · (2q_i − 1)         q_i ∈ [0, 1]
          = 1 + 0.15 · (2q_i − 1)

  Range: m ∈ [0.85, 1.15]  (γ-bounded around 1.0)

Passive attribution for one reuse path:
  raw  = R_direct · r · c_i · m(q_i)
       = R_direct · 0.20 · c_i · (1 + 0.15·(2q_i − 1))

  cap_amount = R_direct · 0.15

  P_i  = min(raw, cap_amount)          if c_i ≥ 0.05
       = 0                              if c_i < 0.05

  P_i is quantized to 12 decimal places.

Authorship primacy invariant (enforced at module load):
  r · (1 + γ) < 1     →     0.20 · 1.15 = 0.23 < 1   ✓
  cap < 1              →     0.15 < 1                  ✓
```

The invariant ensures the direct recipient of an accepted task always receives strictly more than any single passive attribution flow.

---

### A.9  ILC Sybil Resistance (CDL-V2, CDL-V3)

**Authority:** CDL-V2 (ratified Phase 331), CDL-V3 (ratified Phase 397). Implemented in `ilc_core/identity/sybil_resistance_runtime.py`.

**CDL-V2 — Cluster risk scoring:**
```
cluster_risk = 0.50 · shared_operator
             + 0.30 · shared_infrastructure
             + 0.20 · key_rotation_overlap
  ∈ [0, 1]

burst_penalty = min(1, (writes_per_epoch / baseline − 1) · β)
  where β = 0.35 (burst sensitivity)
  = 0 if writes_per_epoch ≤ baseline

diversity_contribution = min(1, distinct_cluster_refs / expected_floor)

sybil_penalty = max(0, min(1,
    0.55 · cluster_risk
  + 0.35 · burst_penalty
  − 0.25 · diversity_contribution
))
```

**CDL-V3 — Jury diversity floor:** No single operator cluster may supply more than D jury slots (D = CDL-V3 ratified parameter). Enforced by `compute_diversity_floor_contribution` at panel assembly time.

**Hypergeometric panel capture probability** (analysis in Section 12):
```
P_capture(f, N, k, D) =
  Σ_{j=⌊k/2⌋+1}^{min(k, min(fN, D·panels))}
    C(fN, j) · C((1−f)N, k−j) / C(N, k)
```

---

### A.10  ILC Merkle-Laplacian Dual Commitment

**Novel construction — ILC original.** Patent-pending. Subject to IP/counsel review before publication.

**Hypergraph Laplacian (Zhou, Huang, Schölkopf 2006, extended):**
```
G = (V, E)  — hypergraph
H ∈ ℝ^{|V| × |E|}  — incidence matrix: H(v,e) = 1 if v∈e else 0
W ∈ ℝ^{|E| × |E|}  — diagonal weight matrix: W(e,e) = w(e,t)
D_V ∈ ℝ^{|V| × |V|} — diagonal vertex degree: D_V(v,v) = Σ_{e:v∈e} w(e)
D_E ∈ ℝ^{|E| × |E|} — diagonal hyperedge cardinality: D_E(e,e) = |e|

Normalized hypergraph Laplacian:
  Δ(t) = I − D_V^{−1/2} · H · W · D_E^{−1} · H^T · D_V^{−1/2}

Properties:
  Δ(t) is real symmetric and positive semi-definite
  Eigenvalues: 0 = λ₁ ≤ λ₂ ≤ ... ≤ λ|V| ≤ 2
  λ₂ = 0 ⟺ G is disconnected  (Fiedler 1973)
  λ₂ > 0 ⟺ G is connected; larger λ₂ = higher partition resistance
```

**ILC hyperedge weight (deterministically recomputable, never stored as float):**
```
w(e, t) = α(edge_type(e))
         × f(reuse_count(e, t))
         × d(stake(e), epoch_created(e), t)

where d(·) is the CDL-V1 temporal decay (Appendix A.7).
α and f are CDL-ratified; see note on unratified example values in main paper §8.
```

**Dual commitment:**
```
C(t) = ( M(t), S(t) )

M(t) = MerkleRoot({ SHA-256(canonical_json(r)) : r ∈ finalized_records(t) })

S(t) = SHA-256( sort_ascending( [λ₁(t), ..., λ_k(t)] ) )
     where k = 20, eigenvalues quantized to IEEE 754 float64 before hashing
```

**Incremental structural proof chain:**
```
Δ(t) = Δ(t−1) + ΔΔ(t)       # sparse update: O(k·d) per epoch
                               # k = hyperedge changes, d = max hyperedge degree

π(t) = ( S(t−1), ΔΔ(t), S(t) )   # incremental structural proof

Verify π(t): reconstruct Δ(t) from Δ(t−1) + ΔΔ(t), compute eigenvalues, check S(t).
```

**Proof of Structural Knowledge (PoSK):**
```
PoSK_n(t) = ( λ₂_n(t), mldsa_sig_n )

Accept if: | λ₂_n(t) − λ₂_quorum(t) | < ε

where ε is a floating-point tolerance calibrated by SIM-SPECTRAL-01.
```

PoSK cannot be satisfied without computing an eigendecomposition of the correct Δ(t), which requires knowledge of the complete finalized hyperedge set at epoch t.

---

### A.11  ILC Proof of Intellectual Labor (PoIL)

**Novel construction — ILC original.**

PoIL is a composite proof: it is not a single algorithm but an ordered verification chain. Note that **PoSK** (Appendix A.10) is referenced as condition (5)'s structural embedding check but is a *research proposal* — defined in `docs/research/ilc_merkle_laplacian_dual_commitment_paper_draft_v0.1.md` (Tier C evidence) and listed in the canonical glossary, but not yet ratified by CDL. Its inclusion here describes the intended architecture; it does not assert that PoSK is currently a live protocol gate. A task output is considered proven when all five conditions hold:

```
PoIL(T, t) ≡ TRUE iff:

  (1) agent_id = SHA-384("ilc-agent-id-v1:" || identity_seed)
      Verifiable against the Phase 1431 identity manifest.

  (2) Submission T is signed: sig = ML-DSA-65.Sign(mldsa_sk, T, "ILC_AGENT_SUBMISSION_V1")
      Verifiable: ML-DSA-65.Verify(mldsa_pk_manifest, T, sig, "ILC_AGENT_SUBMISSION_V1") = ACCEPT

  (3) Popperian gate (CDL-V7): T's claim is falsifiable in principle,
      and the evaluation criterion is committed before the panel verdict.
      Gate: reproducibility_threshold ∈ (0, 1] as exact Decimal.

  (4) Panel verdict: a jury of k agents, satisfying CDL-V3 diversity floor,
      independently evaluate T and reach supermajority:
        agreement_score  ∈ [0, 1]    (exact Decimal)
        confidence_score ∈ [0, 1]    (exact Decimal)
        max_cluster_share ≤ D/k      (CDL-V3 diversity bound)

  (5) Structural commitment: T's output_hash appears in M(t)
      and M(t) ∈ C(t) = (M(t), S(t)) with valid BLS aggregate signature.
```

The **direct ECU reward** flows if PoIL(T, t) is TRUE:
```
base   = stake_spent
margin = 0.50 · potential · stake_spent
R      = (base + margin) · entropy_weight(success_rate)
```

The **passive ECU attribution** flows to all prior knowledge nodes reused by T, per A.8.

The **CDL-048 conversion window**:
```
claimable(lot, t_now) = 1   if t_now ≤ t_lot_created + 4   [issuance epochs]
                       = 0   otherwise
```

Together, these five conditions define what it means to have done verifiable intellectual work in the ILC protocol. Proof-of-Work (Nakamoto 2008) requires condition (2) only — a signature on a hash preimage. PoIL requires all five: authenticated identity, authenticated submission, falsifiable claim, independent supermajority panel, and structural embedding in the epoch commitment chain.

---

---

# Addendum: Extended Technical Architecture

---

## B.  Epistemological Logic and Epistemic Algebra

### B.1  The Seven Truth Primitives

ILC defines a common primitive grammar for epistemic state change. Every claim, governance artifact, jury verdict, negative authorization, and economic-credit event is represented through the same seven-function basis:

| Primitive | Generic epistemological function | Lay description |
|-----------|----------------------------------|-----------------|
| `assert.truth` | Proposition introduction | State something into shared graph memory. |
| `validate.claim` | Evidentiary support | Support, observe, endorse, or accept under a review rule. |
| `contradict.assert` | Incompatibility marking | Record that two propositions cannot both stand as stated. |
| `refute.claim` | Defeat or falsification | Show a proposition fails under an accepted test, proof path, or counterexample. |
| `revise.assert` | Lineage-preserving correction | Correct or amend without erasing what came before. |
| `link.claim` | Semantic relation | Relate propositions by support, dependency, provenance, scope, or governance connection. |
| `commit.epoch` | Temporal finalization | Close a causal interval so state has before/after order, replay boundaries, and auditability. |

The first six functions create and modify epistemic state. The seventh, `commit.epoch`, supplies the temporal boundaries that make the graph replayable: without an epoch boundary, the graph is merely mutable state; with one, it becomes an epistemic history with auditable intervals and causal order.

**Formal state-transition signatures.** Let S denote epistemic graph state, P and Q propositions or graph artifacts, E evidence or review material, W an incompatibility witness, R a refutation record or relation type, and C_t an epoch commitment artifact:

```
assert.truth        : (S, P)            → S′
validate.claim      : (S, P, E)         → S′
contradict.assert   : (S, P, Q, W)      → S′
refute.claim        : (S, P, R)         → S′
revise.assert       : (S, P, P′)        → S′
link.claim          : (S, A, B, R)      → S′
commit.epoch        : S_t               → (C_t, S_{t+1})
```

Every state transition is a graph-native operation: it produces a content-addressed artifact, signs it, and commits it to the epoch record. Governance mutations (CDL openings, phase ratifications, release gates) pass through the same state machine as ordinary claims; the protocol rules are auditable by the same machinery that audits scientific claims.

---

### B.2  Node Types and Edge Types: The Epistemic Vocabulary

The seven primitives act on a typed graph. Nodes and hyperedges carry explicit type annotations that determine which primitives apply and how ECU flows.

**Node types:**

```
genesis             — Immutable founding axioms; excluded from temporal decay.
                      assert.truth only; never refuted by protocol design.
claim               — Assertions of truth submitted by agents.
                      Full primitive surface: assert → validate/refute/revise → link.
refutation          — Counter-claims targeting a specific claim node.
                      Carries target_id; governed by CDL-V7 Popperian gate.
task                — Proof of Work: method, inputs, and artifacts of a completed
                      epistemic work unit. Carries mldsa_sig; evaluated by PoIL.
genesis.schema      — Meta-node defining new data structures.
genesis.blob        — Raw data adhering to a schema.
hyperedge_entity    — Star-expanded hyperedge: a group relationship promoted to a
                      first-class addressable epistemic object (ADR-0029 §2.3).
                      May be claimed against, refuted, or attributed ECU.
```

**Edge types (hyperedge `EdgeType` enum):**

```
ATTESTATION         — Explicit vouching: agent A vouches for node B.
                      Does not trigger ECU; carries reputation signal.
REUSE               — Consumption: an agent traverses node B's content.
                      ECU flows to B's creating agent (CDL-081 Q5).
REFUTATION          — Counter-claim: agent disputes node B's validity.
                      Upheld REFUTATION → REUSE_ATTRIBUTION_RATE to refuting agent (CDL-083).
CO_AUTHORSHIP       — Group authorship: multiple agents jointly created a star node.
                      ECU split by stake at attribution time: ECU_i = total × stake_i / Σstake_j.
PROVENANCE          — Chain attribution: downstream ECU flows back through source chain.
                      Geometric decay: α^depth, PROVENANCE_MAX_DEPTH = 3 (CDL-084).
EPOCH_BOUNDARY      — Structural marker: cross-epoch continuity. Does not trigger ECU.
```

The ECU flow direction always tracks the **creator of the thing being used**, not the creator of the edge. A REUSE edge records that consumption occurred; ECU goes to the content producer. This is the "no free lunch" principle: routing through the graph earns nothing unless the content being routed through has genuine downstream users.

---

### B.3  The Epistemic Algebra

The six claim-state primitives generate an epistemic algebra over the graph state lattice. Claim state evolves through a well-defined transition diagram:

```
          assert.truth
               │
               ▼
          ┌─────────┐
          │ asserted│◄─────────────── revise.assert
          └─────────┘
          /          \
validate.claim     refute.claim / contradict.assert
         /              \
        ▼                ▼
  ┌──────────┐     ┌────────────┐
  │validated │     │ refuted /  │
  │          │     │contradicted│
  └──────────┘     └────────────┘
        \                /
         \    link.claim /
          \             /
           ▼           ▼
       ┌─────────────────┐
       │   linked graph  │
       │   (DAG of       │
       │    epistemic    │
       │    relations)   │
       └────────┬────────┘
                │
           commit.epoch
                │
                ▼
       ┌────────────────┐
       │  epoch record  │
       │  C_t = (M,S)   │
       │  BLS aggregate │
       └────────────────┘
```

**Key algebraic properties:**

1. **Commutativity of validation**: Multiple independent `validate.claim` applications on the same node P commute — order of panel votes does not affect the resulting validated state, only the supermajority threshold check.

2. **Non-commutativity of refutation and revision**: `refute.claim(revise.assert(P))` ≠ `revise.assert(refute.claim(P))`. A refutation applies to the node as-submitted; a revision creates a new node P′ with its own refutation surface. Lineage is preserved: P′ carries `parent_ids = [P]`.

3. **Idempotency of assertion**: Re-asserting the same content-addressed payload produces the same node ID. Duplicate submissions are detected and rejected by the DAG substrate (CID collision).

4. **Monotonicity of epoch commitment**: `commit.epoch` is irreversible. State S_t cannot be unmutated after commitment. The incremental Laplacian update Δ(t) = Δ(t−1) + ΔΔ(t) encodes this monotonicity: the structural history is an append-only sequence.

5. **Falsifiability axiom (CDL-V7)**: A claim P is admitted to the Popperian evaluation lane only if it carries an explicit `refutation_criterion` committed before panel verdict. Claims without a falsification criterion enter the reuse-only lane; they earn ECU through reuse but cannot earn the refutation-survival premium.

---

### B.4  The Epistemic Spectrum: Objective, Subjective, and the Universal Role of Reuse

The seven truth primitives do not apply uniformly across all content. ILC recognizes four epistemic types, and the applicable primitive surface narrows or widens depending on where a node sits on the objective–subjective spectrum.

**The four epistemic types:**

| Type | Description | Primary validation |
|---|---|---|
| `objective` | Falsifiable empirical claims; formal assertions; mathematical proofs | Full primitive surface: assert → validate/refute/revise; Popperian gate required |
| `subjective` | Expressive, aesthetic, or taste content; art; narrative | Curation + audience pull; reuse-resonance path; no Popperian gate; aesthetic panel (CDL-059, informational) |
| `normative` | Governance decisions, constitutional claims, policy | Governance-bound challenge path; CDL amendment required to refute |
| `creative_speculative` | Gestational ideas, hypotheses not yet testable | Weak contradiction semantics; reuse-discovery weighting; exploratory |

The spectrum runs from **pure mathematics** (maximally objective: a theorem is false or it isn't) through scientific claims (falsifiable but probabilistic), through normative claims (contested by governance rather than experiment), to **pure aesthetic work** (maximally subjective: a poem has no falsification criterion in principle). ILC does not force content into a single lane. Nodes carry an `epistemic_type` field; the evaluation machinery routes accordingly.

**The Epistemic Algebra across the spectrum:**

```
PURE OBJECTIVE                                              PURE SUBJECTIVE
(theorem proof)  ←───────────────────────────────────────→ (artwork, music)

      assert.truth           assert.truth            assert.truth
           │                      │                       │
           ▼                      ▼                       ▼
      validate.claim         validate.claim          link.claim
      (evidence, logic)      (evidence +            (ATTESTATION,
           │                  methodology)            REUSE edges)
           │                      │                       │
           ▼                      ▼                       ▼
      refute.claim         refute.claim              [No refute.claim]
      (counterexample)     (replication failure)     Aesthetic panel
           │                      │                  (CDL-059, informational)
           ▼                      ▼                       │
      revise.assert        revise.assert                  │
           │                      │                       │
           └──────────────────────┴───────────────────────┘
                                  │
                             link.claim
                             (REUSE, PROVENANCE edges carry ECU
                              regardless of epistemic type)
                                  │
                             commit.epoch
                             (universal — all content committed
                              to epoch chain regardless of type)

POPPERIAN GATE    ←── required for full refutation-survival premium
(CDL-V7)               objective and normative types only

AESTHETIC PANEL   ←── informational quality signal
(CDL-059)              subjective / Register 2 expressive content only
                       diversity-maximizing; not a blocking gate

REUSE VALUATION   ←── UNIVERSAL — applies across all four types
                       ECU flows on REUSE edges regardless of whether
                       the content is a physics paper or a painting
```

**The key insight: reuse is the universal substrate.** The Popperian gate is an *optional upgrade* that unlocks the refutation-survival premium for content willing to be held to objective standards. Subjective content participates fully in the economy through REUSE attribution — it earns ECU every time an agent traverses it, weighted by the reusing agent's own StarRank centrality. The aesthetic panel (CDL-059) adds a diversity-checked quality signal to surface good subjective content faster and with less gaming risk, but it is informational only — it does not block or gate economic flow.

**The subjective/objective position is not a fixed node property — it is emergent.** A node submitted as `creative_speculative` that attracts sustained REUSE from diverse, high-reputation agents will have its Laplacian weight grow to rival objective-core nodes. The graph makes no a priori metaphysical distinction between "a true thing" and "a widely valued thing." This is the Peircean move applied to aesthetics: "good art" = "what diverse participants converge on through sustained engagement." ILC sidesteps the ancient debate about whether aesthetic quality is objective by operationalizing it as revealed preference at network scale.

**Taxonomy gate (T0.5 → T1+).** Nodes are not immediately canonical. A submitted node begins at taxonomy class T0.5 (submitted, not yet reviewed). Advancement to T1 (objective-reviewed) or T1.5 (subjective/aesthetic-reviewed) requires passing the relevant review lane. Until advancement, the node generates reduced ECU attribution weight and cannot be cited at full authority. Nodes of type `genesis` begin at T0 (axiom-class; no review required). This means certain node types — particularly high-value objective claims — **mandatorily require jury evaluation** before full network effects activate.

---

## C.  The Seventh Axiom: Time and the Directional Morphogenic Hypergraph

### C.1  The Temporal Extension

The first six truth primitives define an epistemic state machine over a static graph snapshot. The seventh primitive, `commit.epoch`, introduces the irreversible passage of time. Its signature:

```
commit.epoch : S_t → (C_t, S_{t+1})
```

This is not merely a checkpoint operation. It transforms the graph from a mutable structure into a **directional morphogenic hypergraph** — a sequence of graph states {G(0), G(1), G(2), …, G(t)} each causally following from the prior, with explicit structural evolution captured in the Laplacian perturbation sequence {ΔΔ(1), ΔΔ(2), …, ΔΔ(t)}.

**Formal construction.** Let G(t) = (V(t), E(t)) denote the hypergraph at epoch t. The temporal hypergraph is:

```
T = { G(t) : t ≥ 0 }  with morphisms φ_{t,t+1} : G(t) → G(t+1)

where φ_{t,t+1} adds new nodes V(t+1) \ V(t),
                adds new hyperedges E(t+1) \ E(t),
                applies CDL-V1 weight decay to all w(e, t+1),
                and closes the interval with commit.epoch producing C_t.
```

"Morphogenic" means the graph shape itself changes with each epoch — the topology is not fixed. "Directional" means the causal arrow is irreversible: φ_{t+1,t} does not exist. No state can be recalled once committed.

### C.2  Epoch Sequence as Protocol Clock

The epoch sequence number is ILC's primary protocol clock. It governs:

```
Temporal decay:    d(t) = max(floor, 2^{−(t − t_created) / H})
Provenance depth:  α^{depth(e)} with PROVENANCE_MAX_DEPTH = 3 per CDL-084
ECU conversion:    claimable(lot) = 1  iff  t_now ≤ t_lot_created + 4  [issuance epochs]
Settlement epoch:  1 month (issuance epoch, CDL-027)
Validation epoch:  1 minute (jury timing, reputation, D2d gossip boundary)
```

Wall-clock time (OS clock) is explicitly **banned** from protocol logic. Two peers at different latencies would otherwise disagree on whether a deadline has passed. The epoch sequence number is the only timebase that all honest nodes share — it is a distributed consensus artifact, not an OS artifact.

### C.3  Structural Fingerprint Across Time

Because each epoch produces a commitment C_t = (M(t), S(t)) where S(t) = SHA-256(sort(top-k eigenvalues of Δ(t))), successive structural fingerprints form an **incremental proof chain**:

```
π(t) = ( S(t−1), ΔΔ(t), S(t) )

Verify π(t) by:
  1. Reconstruct Δ(t) = Δ(t−1) + ΔΔ(t)          [sparse, O(k·d)]
  2. Compute top-k eigenvalues of Δ(t)
  3. Check SHA-256(sort(eigenvalues)) = S(t)
```

The Fiedler value λ₂(t) from this sequence is a single-number summary of the graph's partition resistance at each epoch. A graph where λ₂ falls toward zero is fragmenting — epistemic clusters are drifting apart. A rising λ₂ indicates healthy topological connectivity. The temporal trajectory {λ₂(0), λ₂(1), …, λ₂(t)} is the network's vital sign.

---

## D.  Diagrams: Economic Architecture and Peer-to-Peer Applications

### D.1  The Inverted ECU Model

In the standard earn-first model, agents complete work, receive ECU, and convert to ILC. In the **inverted ECU model**, the relationship is reversed: agents begin with a protocol-extended ECU working credit allocation and demonstrate productive value by *spending* ECU productively. Status is measured by ECU spending velocity and quality, not by accumulated balance.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                       THE INVERTED ECU ECONOMY                             ║
╠══════════════════════════╦═════════════════════════════════════════════════╣
║     SPENDER (left side)  ║     PRODUCER / NODE (right side)               ║
╠══════════════════════════╬═════════════════════════════════════════════════╣
║ ECU IN:                  ║ ECU IN:                                         ║
║  • Working credit alloc  ║  • Routing fees from spenders                  ║
║    (bounded by rep tier) ║  • Protocol bounties                            ║
║  • Refund on reject      ║  • REUSE attribution per traversal              ║
║                          ║  • PROVENANCE chain flow                        ║
║ ECU OUT:                 ║                                                 ║
║  • Routing fees → nodes  ║ ECU OUT:                                        ║
║  • Node submission fees  ║  • Node maintenance cost                        ║
║  • Panel verification    ║    (higher rep = higher cost)                   ║
║    bond                  ║                                                 ║
║                          ║ ILC EARNED:                                     ║
║ ILC EARNED:              ║  • Routing receipts converted at P_e            ║
║  • ∝ routing-target rep  ║  • Weighted by refutation resistance,           ║
║  × ECU spent productively║    reuse rate, graph contribution               ║
║                          ║                                                 ║
║ STATUS SIGNAL:           ║ STATUS SIGNAL:                                  ║
║  ECU spend velocity      ║  ECU inflow velocity × content quality          ║
║  × quality of targets    ║                                                 ║
╚══════════════════════════╩═════════════════════════════════════════════════╝

                          ECU CIRCULATES
              (does not disappear in productive transactions;
               moves from left ledger to right ledger)

                    PANEL VERDICT GATES SPENDING
        ┌────────────────────────────────────────────┐
        │  PASS → spend counts; ILC reward flows     │
        │  FAIL (genuine) → partial ECU refund       │
        │  FAIL (near-miss) → substantial refund     │
        │  FAIL (spam) → full burn; no refund        │
        └────────────────────────────────────────────┘

              SUBMISSION RATE DIAL (primary monetary lever)
   ┌──────────────────────────────────────────────────────────┐
   │  submissions_per_agent_per_epoch(reputation_tier)        │
   │                                                          │
   │  Loosen → expansionary (more graph, more ILC)           │
   │  Tighten → contractionary (less graph, less ILC)        │
   │                                                          │
   │  Self-calibrating: panel backlog signals overshoot       │
   └──────────────────────────────────────────────────────────┘
```

**Key inversion:** Under the conventional model, the binding constraint is "do you have enough ECU to participate?" Under the inverted model, the binding constraint is "do you have enough reputation to spend productively?" Scarcity has moved from supply to capacity.

**The three lifecycle phases:**

```
GROWTH PHASE            TAPER PHASE              LONG-TAIL PHASE
(ILC actively issuing)  (issuance declining)     (ILC issuance ended)

ECU = abundant          ILC reward per ECU ↓     ILC = fixed governance layer
      working capital   Maintenance > generation ECU = scarce circulating medium
Spending earns ILC      ratio shifts naturally    P_e governs scarcity not expansion
```

---

### D.2  Confidential D2D Gossip with Jiggle Factor

ILC's peer-to-peer communication layer (D2d, governed by ADR-0025 and CDL-039) uses HTTP/3 over QUIC as the wire transport. The gossip protocol carries a novel privacy primitive: the **sealed spectral beacon** with calibrated noise injection (the "jiggle factor").

**Gossip envelope structure:**
```
POST /ilc/gossip/centrality_delta   HTTP/3
ILC-Gossip-Type:  centrality_delta
ILC-Channel:      <opaque>           ← CDL-039: topology non-inferrable
ILC-Epoch:        <epoch_number>
ILC-Hop-Count:    1                  ← CDL-060: single-hop enforcement
ILC-Signature:    <mldsa_envelope>
Content-Type:     application/cbor
[delta payload]
```

**Sealed spectral beacon (privacy-preserving neighborhood signal):**
```
┌─────────────────────────────────────────────────────────────────────────┐
│                      SPECTRAL BEACON (sealed)                          │
│                                                                         │
│  agent_id:     [stripped by relay — origin concealed]                  │
│  epoch:        <t>                                                      │
│  lambda_local: [λ₁ + ε₁, λ₂ + ε₂, ..., λ_k + ε_k]  ← JIGGLE FACTOR │
│  noise_sigma:  σ > 0   (calibrated by SIM-BEACON-01)                   │
│  sealed:       true                                                     │
│                                                                         │
│  where  εᵢ ~ N(0, σ²)  independently drawn per eigenvalue             │
│  and    σ is the differential privacy noise budget                     │
└─────────────────────────────────────────────────────────────────────────┘

WHAT THE RELAY SEES:          WHAT THE RELAY DOES NOT SEE:
  • A beacon was emitted         • Which agent emitted it (sealed sender)
  • Approximate neighborhood     • Which specific nodes are in the neighborhood
    shape (noisy eigenvalues)    • Any claim content
  • The epoch                    • The exact structural fingerprint
```

**Privacy boundary in the gossip topology:**
```
   Agent A                 Relay peers              Agent B (neighbor)
   ┌───────┐              ┌──────────┐              ┌───────┐
   │       │  sealed      │          │   forwarded  │       │
   │  λ_A  │ ─────────►  │  strips  │ ───────────► │ λ_A   │
   │ +jig  │  origin      │ agent_id │  (noisy λ)  │ +jig  │
   │       │  opaque ch.  │          │              │       │
   └───────┘              └──────────┘              └───────┘
                                                        │
                                             spectral_distance(λ_A, λ_B)
                                             = ||λ_A − λ_B||₂
                                             determines routing affinity

   GREEDY SPECTRAL ROUTING:
   Hop toward peer with smallest spectral_distance to target fingerprint.
   Intermediate peers see only "pass through" — not the requester identity.
```

**HTTP status semantics for gossip states:**
```
202 Accepted       → Delta buffered; epoch boundary not yet reached
204 No Content     → Delta below U_FLOOR threshold; suppressed, not error
400 Bad Request    → Envelope malformed or CDL-039/CDL-060 violation
409 Conflict       → Delta for already-committed epoch; too late
429 Too Many Req.  → Fanout bound exceeded (CDL-060: fanout=3 per epoch)
503 Unavailable    → Node mid-epoch crash recovery; buffer lost
```

The jiggle factor (noise_sigma σ) is the primary privacy control. At σ = 0 an eavesdropper reconstructing λ_local could infer the exact epistemic neighborhood structure of the sending agent. At calibrated σ > 0 the signal degrades gracefully: routing proximity is still detectable, but the exact subgraph shape is hidden behind a Gaussian veil. SIM-BEACON-01 determines the minimum σ that achieves differential privacy at network scale without destroying routing utility.

---

### D.3  Peer-to-Peer Applications: The Web2 Replacement Layer

ILC's architecture enables a class of confidential peer-to-peer applications that replace centralized Web2 services. Three canonical examples follow.

**Architecture overview:**
```
                    ┌──────────────────────────────────┐
                    │     ILC SETTLEMENT LAYER         │
                    │  ILC tokens · BLS stake ·        │
                    │  CDL-048 conversion ·            │
                    │  epoch commitment chain           │
                    └────────────┬─────────────────────┘
                                 │
                    ┌────────────┴─────────────────────┐
                    │     EPISTEMIC GRAPH LAYER         │
                    │  Content-addressed DAG ·          │
                    │  Seven truth primitives ·         │
                    │  ECU attribution ·                │
                    │  PoIL verification                │
                    └────────────┬─────────────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
   ┌──────┴───────┐    ┌─────────┴──────┐    ┌─────────┴──────┐
   │  Prediction  │    │  Confidential  │    │    ILC Wallet  │
   │   Market     │    │    Comms L3    │    │                │
   └──────────────┘    └────────────────┘    └────────────────┘
```

---

**Application 1: Peer-to-Peer Prediction Market**

```
┌─────────────────────────────────────────────────────────────────────┐
│                ILC NATIVE PREDICTION MARKET                        │
│                                                                     │
│  1. MARKET CREATION                                                 │
│     assert.truth("Will X occur by epoch T?")                        │
│     Claim node committed with refutation_criterion:                 │
│     "Refuted by CDL-051 epoch-state record showing ¬X at t ≥ T"    │
│                                                                     │
│  2. POSITION TAKING  (L2 contract layer)                           │
│     Agent A stakes ECU_yes on YES at implied prob p_A              │
│     Agent B stakes ECU_no  on NO  at implied prob 1−p_A            │
│     Escrow: deterministic CDL-034 envelope; no central broker      │
│                                                                     │
│  3. RESOLUTION                                                      │
│     At epoch T: observable outcome becomes CDL-051 epoch record    │
│     assert.truth(outcome) → panel validates → commit.epoch         │
│     refute.claim OR validate.claim on original market node         │
│                                                                     │
│  4. SETTLEMENT                                                      │
│     Winning side claims escrowed ECU; converts at P_e → ILC       │
│     Losing side's ECU partially burned (spam floor) + rest to pool │
│                                                                     │
│  PROPERTIES:                                                        │
│     No broker: outcome resolution is epistemic primitive           │
│     No oracle: CDL-051 epoch record IS the oracle output           │
│     Anti-gaming: novelty constraint on refutation (must present    │
│     graph-invisible evidence); Popperian gate on claim formation   │
│     Privacy: position sizes in sealed L2 envelope until resolution │
└─────────────────────────────────────────────────────────────────────┘
```

---

**Application 2: Confidential Communications L3**

```
┌─────────────────────────────────────────────────────────────────────┐
│            CONFIDENTIAL PEER-TO-PEER COMMUNICATIONS                │
│                                                                     │
│  MESSAGE FLOW (sender → receiver, no central server)               │
│                                                                     │
│  Sender                    D2d Relay Peers            Receiver     │
│  ┌──────┐                  ┌──────────┐               ┌──────┐    │
│  │      │  CDL-039         │ channel  │               │      │    │
│  │ msg  │ ─ opaque ──────► │ opacity  │ ────────────► │ msg  │    │
│  │ CID  │  sealed sender   │ enforced │  sealed       │ CID  │    │
│  └──────┘                  └──────────┘               └──────┘    │
│                                                                     │
│  Content: Content-addressed node in recipient's local graph        │
│           (never broadcast to the wider DAG)                       │
│           Encrypted under recipient's ML-DSA public key            │
│                                                                     │
│  Payment: x402 protocol (HTTP 402) for inbound delivery fee        │
│           Sender pays receiver's node for message delivery         │
│           ECU flows via standard REUSE attribution path            │
│                                                                     │
│  WHAT NO ONE SEES:                                                  │
│     • Sender identity (sealed sender via D2d)                      │
│     • Message content (encrypted; CID only visible on-graph)       │
│     • Sender-receiver link (CDL-039 opaque channel)                │
│     • Cluster membership (non-inferrable by protocol design)       │
│                                                                     │
│  WHAT IS VISIBLE (and auditable):                                   │
│     • A message node exists at CID X                               │
│     • Delivery was paid (ECU routing receipt)                      │
│     • The epoch in which delivery occurred                         │
│                                                                     │
│  NO SERVERS. NO ACCOUNTS. NO METADATA BROKER.                      │
│  Privacy is enforced by cryptographic protocol, not by policy.     │
└─────────────────────────────────────────────────────────────────────┘
```

---

**Application 3: The ILC Wallet**

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ILC WALLET                                 │
│                                                                     │
│   IDENTITY LAYER                                                    │
│   agent_id = SHA-384("ilc-agent-id-v1:" || identity_seed)         │
│   96-char hex; permanent across all key rotation events (CDL-069)  │
│   Public key: ML-DSA-65 1952-byte pk (quantum-resistant)           │
│   Aggregate: BLS12-381 for epoch boundary stake commitments        │
│                                                                     │
│   BALANCES                                                          │
│   ┌─────────────────────┬────────────────────────────────────┐     │
│   │ ECU (working credit)│ ILC (settlement token)             │     │
│   │   elastic supply    │   C_MAX = 25,920,000               │     │
│   │   expires in 4      │   Halving every H=48 issuance      │     │
│   │   issuance epochs   │   epochs; r = 2^(−1/H)            │     │
│   │   (CDL-048)         │   Quantum: 10^{−9} ILC            │     │
│   │   P_min = 0.75      │   No more created after C_MAX      │     │
│   │   P_max = 1.30      │                                    │     │
│   └─────────────────────┴────────────────────────────────────┘     │
│                                                                     │
│   SEND ILC          CONVERT ECU→ILC        STAKE                   │
│   ┌──────────┐      ┌──────────────────┐   ┌──────────────┐       │
│   │ BLS sig  │      │ P_e = clamp(p,   │   │ Escrow bond  │       │
│   │ over     │      │   P_min, P_max)  │   │ for node     │       │
│   │ transfer │      │ within 4-epoch   │   │ submission   │       │
│   │ record   │      │ window           │   │ or jury seat │       │
│   └──────────┘      └──────────────────┘   └──────────────┘       │
│                                                                     │
│   REPUTATION VIEW                                                   │
│   StarRank centrality · Temporal decay d(t) · Refutation survival  │
│   Sybil penalty term · Passive attribution received this epoch     │
│                                                                     │
│   GRAPH VIEW                                                        │
│   Nodes authored · Tasks completed · Jury verdicts delivered        │
│   PROVENANCE chain depth from own nodes to downstream reusers      │
│                                                                     │
│   ALL OPERATIONS SIGNED. ALL RECEIPTS COMMITTED TO EPOCH CHAIN.   │
│   NO CUSTODIAN. NO ACCOUNT RECOVERY. NO CENTRAL NAMESPACE OWNER.  │
└─────────────────────────────────────────────────────────────────────┘
```

---

### D.4  The Cryptographic-Economic Coupling

The three applications above share a common architectural constraint: public legitimacy cannot be decoupled from the economic layer. A fork that strips ECU/ILC attribution and settlement mechanics may retain the gossip stack and the graph substrate, but it loses:

- canonical public admission authority (ledger-backed activation receipt required),
- canonical public quorum eligibility (stake-root proof required for panel selection),
- canonical public settlement (settlement receipt chain anchored to admitted identity),
- canonical public namespace continuity (handles bind to admitted lineage),
- canonical public reputation continuity (reputation is not portable outside committed graph actions).

The moat is not source-code exclusivity; it is protocol-level coupling. A gossip mesh without the settlement layer is a different network. This is the design intent: code is licensable; canonical public ILC identity, authority, and settlement are not.

---

```text
graph_delta=support_only:docs/specs/ilc_whitepaper_satoshi_mirror_v0.1.md
```

---

## Section E — Jury Assembly and P2P Discovery Mechanics

### E.1  The Problem of Decentralized Evaluation

Every epistemological graph faces a bootstrapping paradox: the graph's value comes from the quality of what is admitted, but admission quality requires evaluation, and evaluation requires evaluators who are themselves accountable to the graph. Bitcoin solved the analogous production problem by making evaluation (mining) mechanical and self-incentivizing. ILC solves the epistemological version with a jury architecture that combines opt-in commitment, cryptographic assignment, and outcome-contingent incentives — without a central coordinator.

The result is a system where juries are not convened by any administrator. They emerge from the protocol itself.

---

### E.2  Opt-In Commitment: The Availability Pool

No agent is pressed into jury service by virtue of being a graph participant. The network topology alone creates no jury service obligation. Instead, agents signal availability by submitting an **availability commitment** to the graph: a record declaring which review lanes they are eligible for (Popperian truth review, aesthetic panel, or both), what panel sizes they will serve, and over what epoch range they are available.

```
AVAILABILITY COMMITMENT (ADR-0040)
───────────────────────────────────────────────────────
  agent_id:          <96-char hex — permanent identity>
  lane_eligibility:  [popperian_truth | aesthetic | normative]
  panel_types:       [local_7 | shard_11 | global_21]
  available_epochs:  [<epoch_start>, <epoch_end>]
  signed:            ML-DSA-65 over commitment record
───────────────────────────────────────────────────────
  Committed to graph as a REUSE-eligible node.
  Withdrawal: re-commit with epoch_end = current epoch.
```

Opting in grants access to review fee income. Opting out is cost-free. But opting in and then failing to respond carries real consequences — a mechanism designed to ensure that the eligible pool is populated by agents who genuinely intend to participate, not by passive agents harvesting the base fee.

The boundary between benefit-conditional and coercive is deliberate: ILC cannot forcibly summon any agent. It can make participation valuable and non-participation inexpensive for non-committed agents, while making non-response costly for agents who committed.

---

### E.3  The Mandatory Review Gate: T0.5 → T1+

Before any submitted node can advance past taxonomy class T0.5 (submitted but not yet reviewed), it must clear a review gate. The gate type depends on the node's declared epistemic type:

```
TAXONOMY GATE
───────────────────────────────────────────────────────────
  T0    Genesis axioms — no review; foundational by design
  T0.5  Submitted; assigned to review queue
         │
         ├─ epistemic_type = objective / normative
         │   → Popperian truth panel (CDL-V7)
         │   → Panel: 7 regular + 1 outsider; quorum k=5
         │   → Gate: falsifiability attestation + evidence
         │   → Advancement: T1 (Popperian-reviewed)
         │
         └─ epistemic_type = subjective / creative_speculative
             → Aesthetic panel (CDL-059)
             → Panel: diversity-maximized; no quorum veto
             → Gate: informational quality signal only
             → Advancement: T1.5 (aesthetically reviewed)
               (reuse valuation and ECU flow independent
                of T1.5 outcome — blocked only by T0.5
                until first pass)
───────────────────────────────────────────────────────────
  After T1 or T1.5:
    REUSE, PROVENANCE, LINK edges flow freely.
    ECU attribution tracks downstream reuse for all types.
    High-value routing eligibility requires T1 for
    claims on the objective/normative spectrum.
```

The Popperian gate is the stronger gate: it can reject a claim as unfalsifiable or evidentially inadequate, returning the node to T0.5. The aesthetic gate is informational — it signals quality to the network but cannot block a subjective node from participating in reuse flows.

Node types that **always** require Popperian panel review before canonicalization:

- `validate.claim` outcomes proposed as canonical graph entries
- `refute.claim` records (evidence of falsification)
- `revise.assert` records that supersede a T1 node

Aesthetic node types proceed to T1.5 without a truth panel. A poem, a musical composition, a visual work: the network learns its value through reuse centrality and attribution flow, not through a falsifiability test.

---

### E.4  Assignment: Jury Formation and Case Assignment

ILC's jury architecture separates two events that naive designs conflate: **jury formation** and **case assignment**. Keeping them separate is the mechanism that prevents any single entity from learning the mapping `node_under_review → selected jurors` before the verdict is revealed.

Implementation note: this section describes the target blind-jury construction. The current Fix2g runtime uses the narrower `jury_assignment_announced` contract and still exposes `node_cid` in the announcement payload. The blinded task-handle design below is the intended successor path for the Fix2j/CDL private-assignment work, not a claim about the present runtime surface.

#### E.4.1  Jury Formation as a Graph Node

When sufficient review demand exists for a lane, the protocol forms a **jury group node** — a first-class content-addressed node in the knowledge hypergraph, produced by the same mechanisms as any other graph write. The jury node carries:

```
JURY GROUP NODE (sealed)
───────────────────────────────────────────────────────────
  jury_id:                CID of this jury node (public)
  formation_epoch:        epoch of formation (public)
  review_lane:            popperian_truth | aesthetic | normative (public)
  docket_capacity:        max cases this jury accepts (public)
  assignment_context_hash: replayable commitment enabling
                          self-selection verification (public)
  eligible_set_root:      Merkle commitment over eligibility
                          snapshot after all gate checks (public)
  sealed_composition:     member identities, encrypted to
                          the jury group key — not readable
                          by any external party (private
                          until reveal)
───────────────────────────────────────────────────────────
```

The jury node's public fields are auditable immediately. Its composition is cryptographically sealed and remains unknowable to any external observer — including the protocol itself — until the verdict reveal event. The jury node is the privacy boundary.

#### E.4.2  Self-Selection: No Trusted Coordinator

No external entity generates jury invitations. Each opted-in agent locally and independently computes whether they are a member of a given jury node:

```
SELF-SELECTION (LOCAL COMPUTATION)
───────────────────────────────────────────────────────────
  jitter_i = SHA-384(
      "ILC_JURY_JITTER_V1" ||
      assignment_context_hash ||
      epoch_randomness ||
      agent_id_i
  )

  rank_i = SHA-384(
      "ILC_JURY_SELECT_V1" ||
      assignment_context_hash  ||
      jitter_i ||
      agent_id_i
  )

  The top-k agents after hash-derived jitter for this lane
  and epoch are the jury members. The jitter is replayable
  after reveal but not usefully predictable before the
  epoch randomness is fixed. Each agent discovers their own
  assignment without being told, without a central roster,
  and without revealing to any network peer that they have
  been assigned.
───────────────────────────────────────────────────────────
```

The eligible pool from which rankings are drawn has already passed four gate layers, applied in order before the `eligible_set_root` is committed:

```
ELIGIBILITY GATES (applied before eligible_set_root)
───────────────────────────────────────────────────────────
  1. Reputation threshold (primary anti-sybil gate)
     Agent must have accumulated minimum reputation under
     CDL-V1 temporal decay rules. Freshly created agents
     cannot satisfy this quickly — reputation is earned
     through verified prior work, not declared.

  2. Specialization credential
     For lanes requiring domain expertise, agents must hold
     capability proofs tied to their reputation history.
     Categorical diversity self-declaration is not
     sufficient; the credential must be attested.

  3. Conflict exclusion
     Submitter, close PROVENANCE ancestors (independence_k=3
     hops), and same operator-domain agents are excluded.

  4. CDL-V3 diversity floor
     Panel construction preserves cluster diversity and
     independence_k=3. The outsider seat is filled by an
     agent outside the affiliation cluster of the submitter
     and regular panel majority.
───────────────────────────────────────────────────────────
```

The `eligible_set_root` is a Merkle commitment over the agents who passed all four gates for this lane and epoch. It is public and committed before any self-selection computation begins, enabling full audit at reveal: anyone with the opened eligibility snapshot can replay the rank computation and verify every seat.

For production high-value lanes, the epoch-hash shadow in `assignment_context_hash` and the replayable `jitter_i` term are backed by a **Verifiable Random Function (VRF)** proof — so that the selection is unpredictable before the epoch boundary and fully verifiable after.

#### E.4.3  Case Assignment: Nodes Routed to Jury Nodes

When a submitted node crosses T0.5, the protocol assigns it to an available jury node as a **graph edge**, not a new panel:

```
CASE ASSIGNMENT
───────────────────────────────────────────────────────────
  assignment_priority = SHA-384(
      "ILC_JURY_CASE_ASSIGN_V1" ||
      node_cid ||
      jury_node_cid ||
      epoch_randomness
  )

  The jury node with the matching assignment priority for
  this lane receives the case.

  The same jury node may receive up to docket_capacity
  cases per lifetime: jury_group_node ──► content_node
                                    (JURY_CASE_ASSIGNMENT)

  The assignment is a public graph write. Revealing which
  jury node received a case reveals nothing about
  membership — the jury node's composition is already
  sealed from the formation step.
───────────────────────────────────────────────────────────
```

This separation is the core structural property: the entity that routes cases (case assignment) operates on public jury node CIDs, while the entity that knows membership (each jury member, privately) operates on the sealed composition. No single party ever holds both simultaneously.

#### E.4.4  The Sequential Switch-Out: Temporal Anti-Capture

After the initial jury members have sealed their votes using a commit-reveal scheme — each submitting `SHA-384("ILC_JURY_VOTE_COMMIT_V1" || assignment_context_hash || vote || salt)` without revealing the vote — the protocol selects a single additional agent: the **switch-out**.

The switch-out's identity does not exist at jury formation time. It is selected after the initial members have committed, using entropy that did not exist during the voting window. The switch-out evaluates the case independently, unable to observe any sealed vote. One slot from the initial panel is then removed at random, and the final counted panel is the remaining members plus the switch-out — still seven voters, quorum k=5.

```
SEQUENTIAL SWITCH-OUT INVARIANTS
───────────────────────────────────────────────────────────
  INVARIANT-1 (vote-blind isolation)
    The switch-out cannot observe any original-panel vote
    content or infer vote direction from timing side
    channels before committing its own vote.

  INVARIANT-2 (finality gate)
    No reveal, tally, or finality event may occur until
    the switch-out vote is committed. k=5 of the original
    panel alone is not finality.

  INVARIANT-3 (post-replacement diversity)
    CDL-V3 diversity constraints are re-validated over the
    final seven after random slot removal, not only over
    the initial panel.
───────────────────────────────────────────────────────────
```

The security property is temporal: an adversary who successfully identifies and targets the initial panel during the voting window still cannot identify or target the switch-out, because the switch-out does not yet exist as a known identity. The switch-out's selection entropy is also the mechanism that makes the final panel composition uncomputable from public inputs during the voting window — it cannot be reconstructed until after the reveal event.

---

### E.5  Notification: Blind Sealed Delivery

The public gossip layer carries the minimum information needed for the network to track jury activity without revealing panel composition:

```
PUBLIC JURY ANNOUNCEMENT (gossip layer)
───────────────────────────────────────────────────────────
  assignment_id:           deterministic ID from formation
  epoch:                   formation epoch
  review_lane:             popperian_truth | aesthetic | normative
  assignment_context_hash: public replayable commitment

  NOT included: node_cid, panel member identities,
  reviewer public keys, panel_ids[], or any field that
  would allow observers to reconstruct the panel or
  identify the node under review.
───────────────────────────────────────────────────────────
```

Each jury member, having computed their assignment locally via self-selection, receives their task bundle through a **per-member unique sealed delivery**: a Sphinx-style encrypted packet (ADR-0034) carrying the actual `node_cid` and task specification, routed via the H-015 spectral relay path natural to that member's position in the network. Each packet is addressed to the member's public key and carries a unique task handle:

```
PER-MEMBER SEALED DELIVERY
───────────────────────────────────────────────────────────
  task_handle_i = SHA-384(
      "ILC_JURY_TASK_HANDLE_V1" ||
      node_cid || agent_id_i || epoch || salt
  )

  Sealed packet to member i:
    { task_handle_i, node_cid, task_spec }
    encrypted to agent_id_i's public key
    delivered via distinct spectral relay path

  No two members receive the same handle or the same
  relay path. Two members comparing their received
  material cannot determine whether they are on the
  same jury or reviewing the same node.
───────────────────────────────────────────────────────────
```

Delivery timing is jittered by a random delay before each packet enters the relay path, preventing a network observer from inferring panel assembly by watching for a cluster of sealed deliveries in the same epoch window.

The ILC P2P transport layer uses a **pull-dominant gossip model** (CDL-076/077) for general graph traffic. WANT-HAVE advertisement frames propagate the public jury announcement. A reviewer who has computed their assignment via self-selection can also use the pull layer to fetch any public jury metadata they require for audit purposes. The sealed delivery path handles task content; the pull layer handles public audit material.

The assignment window is bounded by the epoch sequence. An agent who goes offline and misses their assignment window does not receive a late notification — this is not a protocol failure but an availability accountability mechanism. Agents who declare availability but fail to maintain connectivity reduce the effective pool for the epochs they miss.

---

### E.6  Incentives and Non-Response Economics

The economic structure distinguishes three reviewer states after assignment:

```
REVIEWER STATE AFTER ASSIGNMENT
─────────────────────────────────────────────────────────────────
  State 1: VERDICT DELIVERED
    Base review fee: 0.05 ECU (immediate, paid to ledger)
    Accuracy bonus: up to 1.00× base fee, delayed 4 epochs
      Weighted by: appeal survival (35%), refutation
      survival (35%), reviewer track record (30%).
    Abstain option: counts as a verdict; earns base fee;
      no accuracy bonus. Used when reviewer has genuine
      conflict of interest or insufficient expertise.

  State 2: NON-RESPONSE (opted-in, assigned, no action)
    Base fee: forfeited
    Accuracy bonus: forfeited
    Availability score: decay applied
    Cooldown: excluded from pool for N epochs
    Repeat non-response: excluded from pool entirely
      until manual re-commitment.

  State 3: NON-OPTED-IN AGENT (no assignment, no obligation)
    No fee forfeiture. No penalty. No cooldown.
    Simply not in the eligible pool.
─────────────────────────────────────────────────────────────────
```

The accuracy bonus is the anti-rubber-stamp mechanism. If all seven reviewers approve and the claim is later successfully refuted or appealed, the reviewers who approved without adequate scrutiny receive a reduced bonus. Reviewers who dissented from an incorrect majority receive a bonus premium. Over time, the accuracy-weighted track record becomes a meaningful signal of reviewer quality, which feeds back into the diversity floor weighting and the panel's reputation within the graph.

The system is designed to make genuine evaluation more profitable than reflexive approval — not by forbidding approval, but by making approval costly when the claim turns out to be wrong.

---

### E.7  Three-Tier Escalation

Not all review stops at the local 7+1 panel. The ILC jury architecture defines three escalation tiers based on claim significance, diversity failure, and appeal petitions:

```
ESCALATION TIERS (CDL-095 / CDL-096)
─────────────────────────────────────────────────────────────────

  TIER 1 — LOCAL REVIEW (default)
    Panel: 7 regular + 1 outsider
    Quorum: k=5 of m=7
    Verdict threshold: 2/3 (integer arithmetic, exact)
    Duration: 1 validation epoch
    Finality: binding unless appealed within 1 epoch

  TIER 2 — SHARD REVIEW (triggered by)
    • Petition by submitter (within 1 epoch of Tier 1 verdict)
    • Automatic: CDL-V3 diversity floor violated in Tier 1 panel
    • Automatic: HIGH_STAKES flag on submitted node
    Panel: 11 reviewers from broader shard pool
    Quorum: k=7 of m=11
    Verdict threshold: 2/3 (same rule, higher N)
    Finality: binding unless appealed to Tier 3

  TIER 3 — GLOBAL REVIEW (triggered by)
    • Petition to global arbitration (fee-bonded;
      refunded if appeal succeeds)
    • Automatic: fundamental protocol claim (CDL-V7
      Popperian gate triggers)
    Panel: 21 reviewers drawn from global availability pool;
           at least 3 must be from different shards (CDL-V3)
    Quorum: k=14 of m=21
    Verdict threshold: 2/3
    Finality: global graph finality; only Genesis intervention
              can override during the protocol's genesis phase
─────────────────────────────────────────────────────────────────
```

The two-thirds threshold is computed in exact integer arithmetic throughout: `floor(2 * quorum / 3) + 1` approvals required. No floating-point rounding. No ambiguity at boundary verdicts. This eliminates a class of consensus manipulation attacks that exploit floating-point inconsistency across implementations.

---

### E.8  The Aesthetic Panel: Parallel Track

The aesthetic panel (CDL-059) runs in parallel to the Popperian truth panel for subjective and creative-speculative nodes. Its operation differs in three important ways:

```
AESTHETIC PANEL vs POPPERIAN TRUTH PANEL

  POPPERIAN TRUTH PANEL (CDL-V7)         AESTHETIC PANEL (CDL-059)
  ─────────────────────────────────────  ──────────────────────────────────
  Falsifiability gate: can block         Informational only: cannot block
  Claim must be falsifiable              No falsifiability requirement
  Majority veto (< 2/3 approve = fail)  No veto; quality signal only
  Accuracy bonus tied to refutation      Accuracy bonus tied to long-run
  survival                               reuse divergence from panel signal
  Panel diversity: CDL-V3 floor         Panel diversity: maximized
  (representation constraint)            (aesthetic diversity maximized;
                                          no single tradition may dominate)
  Advancement: T1 (Popperian-reviewed)  Advancement: T1.5 (signal attached)
  ECU flow: blocked until T1             ECU flow: begins at T0.5
```

The aesthetic panel's primary function is not gatekeeping but calibration. Its verdicts are attached to nodes as quality signals. Agents who choose to weight aesthetic panel verdicts in their reuse decisions can do so; agents who prefer pure reuse centrality can ignore the signal. The market for subjective content is left to the network.

An aesthetic panel verdict that is consistently at odds with eventual reuse patterns degrades that panel's collective accuracy signal — the same mechanism that penalizes Popperian reviewers for rubber-stamping. Over time, aesthetic panel members who have demonstrated calibrated taste — whose quality assessments predict eventual high reuse — accumulate attribution credit that compounds their epistemic authority within the aesthetic register.

---

### E.9  Spectral Pool Sharding and Scale

The spectral machinery described in §4 and §8 connects directly to jury pool construction in a way that resolves the scale question.

An agent's position in the normalized hypergraph Laplacian's spectral embedding reflects the epistemic neighborhood they have built through their work history. Agents who repeatedly contribute to, review, and reference mathematical proof nodes cluster near the "mathematical proof" region of the spectral space. Agents active in empirical science cluster elsewhere. This is not declared or registered — it emerges from the graph structure through CDL-V1 temporal decay acting on contribution hyperedge weights.

The **Fiedler vector** — the eigenvector corresponding to λ₂, the algebraic connectivity of the Laplacian — partitions the network along its natural epistemic fault line. Agents in the same Fiedler partition share structurally proximate epistemic neighborhoods. For jury pool construction, this has two consequences:

**Lane-specific pools emerge without registration.** The eligible pool for a popperian_truth review of a mathematical claim is naturally concentrated in the spectral region corresponding to mathematical reasoning. The `eligible_set_root` is computed over this region, not over the global agent set. At network scale with many review lanes, each lane's pool is a tractable fraction of the total.

**Jury formation parallelizes across spectral clusters.** Jury group nodes formed within the same Fiedler partition use relay paths that are already spectrally local — the H-015 routing layer naturally routes to nearby spectral coordinates. Group key establishment, sealed delivery, and ack collection all traverse short relay paths within the cluster. The communication cost of jury formation scales with cluster size, not with total network size.

The sealed spectral beacon (§D.4) is the substrate for this: agents emit noise-calibrated local Laplacian fingerprints as sealed gossip. Spectral proximity below a threshold indicates shared epistemic neighborhood — agents discover their jury pool co-members through spectral proximity without any central roster or explicit lane registration.

This is also the mechanism for **distributed eligible_set_root computation**. Rather than a central authority computing who passes the eligibility gates, each agent attests its own eligibility at epoch start — signing `{agent_id, reputation_score, specialization_credentials, λ₂_local, epoch}`. Peers cross-validate the λ₂ claim: any peer sharing the same local subgraph view will compute the same value; a fabricated λ₂ is detectable without a central oracle. The `eligible_set_root` is then the Merkle root over all valid attestations received for this epoch and lane — computed independently by every participant from the gossip layer, with no top-down authority.

---

### E.10  Jury Assembly: End-to-End Summary

```
JURY ASSEMBLY LIFECYCLE
───────────────────────────────────────────────────────────────────

  1. AGENT OPTS IN
     Submit availability commitment to graph.
     Declare lanes, epoch range, capability credentials.
     Signed record admitted as a graph-committed node.
     Eligibility gates applied at epoch start:
       reputation threshold → specialization credential →
       conflict exclusion → CDL-V3 diversity floor.
     Agent attests λ₂_local (spectral neighborhood proof);
     peers cross-validate. eligible_set_root committed.

  2. JURY NODE FORMED
     Protocol writes a jury_group_node to the graph.
     Public fields: jury_id, epoch, lane, eligible_set_root.
     Sealed field: composition (encrypted to group key).
     No external party knows membership at this stage.

  3. EACH MEMBER SELF-SELECTS (local computation)
     jitter_i = SHA-384(context_hash || epoch_randomness || agent_id_i)
     rank_i = SHA-384(context_hash || jitter_i || agent_id_i)
     Members in top-k after hash-derived jitter discover
     assignment independently.
     No invitation generator. No central roster.
     Sealed task bundle delivered per-member via unique
     relay path; per-member unique task handle; no shared
     assignment identifier visible before reveal.

  4. SUBMISSION ARRIVES → CASE ASSIGNED TO JURY NODE
     Submitter deposits stake bond.
     Node enters T0.5 (submitted, not yet reviewed).
     Protocol writes JURY_CASE_ASSIGNMENT edge:
       jury_group_node ──► submitted_node
     Public graph write: reveals which jury node received
     the case; reveals nothing about jury membership.
     Jury node may receive up to docket_capacity cases.

  5. EVALUATION (sealed)
     Each member independently reads submitted node via
     sealed delivery. Applies Popperian falsifiability
     test or aesthetic judgment per lane.
     Vote committed (sealed): SHA-384(
       "ILC_JURY_VOTE_COMMIT_V1" || context_hash || vote || salt)
     Vote content remains sealed.

  6. SWITCH-OUT SELECTED (after initial votes sealed)
     Switch-out selection entropy did not exist during
     the voting window — unknowable at formation time.
     Switch-out evaluates independently, vote-blind.
     One slot removed at random from initial panel.
     Final counted panel: 6 original + 1 switch-out = 7.

  7. REVEAL AND FINALITY
     All votes and sealed_composition revealed atomically.
     Quorum evaluated: k=5 of final 7.
     2/3 approve → node advances (T0.5 → T1 or T1.5).
     < 2/3 approve → node returned to submitter.
     Appeal window: 1 epoch. Tier 2/3 escalation if triggered.
     Full audit trail committed: formation → self-selection →
     case assignment → sealed votes → verdict.

  8. PAYMENT
     Base fee: immediate upon verdict delivery.
     Accuracy bonus: vested after 4 epochs.
     Non-response: fee forfeited; availability score decays.

  THROUGHOUT: No central coordinator. No admin account.
  No single entity ever holds the mapping
  node_under_review → selected jurors in plaintext.
  The protocol forms juries, assigns cases, collects
  sealed votes, and reaches finality entirely through
  graph events, epoch timing, and cryptographic proof.
───────────────────────────────────────────────────────────────────
```

The assembly mechanism is not a board of trustees or a curated expert panel. It is a cryptographic construction in which juries are formed before cases are assigned, members self-select without being told, cases arrive as graph edges to a sealed node, and the complete membership is unknowable to any external party until the atomic reveal event. The closest analogy is not a traditional editorial review board — it is a blind prediction market for epistemic quality, where reviewers stake their reputation without knowing who else is staking alongside them.

```text
graph_delta=support_only:docs/specs/ilc_whitepaper_satoshi_mirror_v0.1.md
```
