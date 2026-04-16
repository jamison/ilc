# ILC Sovereign BFT and Finality-Family Research Packet 689 v0.1

Status: research artifact — not a CDL, not a substrate selection
Date: 2026-04-16
Phase: 689
Owner lane: G8 sovereign-substrate research

`sovereign_bft_research_packet_689_complete`
`research_is_within_sovereign_design_space_only`
`bal_profile_weights_are_unratified_planning_inputs_in_this_phase`

---

## 1. Scope and framing

Phase 688 established that the primary live candidate is the custom minimal
sovereign L1 family. This phase researches what that means in practice.

The question is not "which existing chain should ILC use."

The question is "which BFT protocol design should ILC's own settlement
infrastructure be built on, and what does that mean for the implementation?"

This is a design-space research artifact, not a benchmark. Benchmarks come
in Phase 690. This phase establishes the conceptual and engineering frame
that makes Phase 690 benchmark definitions meaningful.

---

## 2. BFT protocol families in scope

### 2.1 PBFT-lineage (Practical Byzantine Fault Tolerance)

**Origin and character:**
Castro and Liskov 1999. The classical deterministic BFT protocol. Three-phase
commit (pre-prepare, prepare, commit). Requires 2f+1 of 3f+1 nodes honest for
safety. O(n²) message complexity.

**Finality semantics:**
Deterministic. A block committed in the commit phase is final — no forks, no
probabilistic convergence. This is the most rigorous finality guarantee
available.

**Fork resolution:**
Not needed. PBFT does not fork under honest-majority conditions. If the leader
is faulty, view-change protocol elects a new leader. The view-change has O(n²)
cost.

**Validator-set assumptions:**
Works well at small-to-medium validator sets (practical upper bound ~100 nodes
before message complexity becomes a throughput bottleneck). Requires known,
stable validator identity — admission and ejection require explicit governance.

**ILC relevance:**
The deterministic finality model is ideal for ILC's epoch-boundary commit
semantics. One epoch = one committed block = final. No probabilistic
accumulation needed.

**Key risks:**
- O(n²) message complexity limits practical scale
- Leader rotation under view-change is expensive
- Admission/ejection governance overhead is real

**Admissibility (row-7 / row-8):**
PASS — all validators are ILC-governed. No external constitutional center.
Censorship resistance depends on honest-majority validator set and leader
rotation mechanism. Exitability is strong: full state is available from any
honest node.

---

### 2.2 Tendermint / CometBFT

**Origin and character:**
Buchman 2016, refined into CometBFT (the consensus engine extracted from
Cosmos SDK). Two-round BFT (propose + prevote + precommit). O(n²) message
complexity in the common case, but with optimizations for the happy path.
Requires 2/3+ voting power for commit. Used in production by Cosmos
app-chains without ICS.

**Finality semantics:**
Deterministic. A block receiving 2/3+ precommits is final. No forks under
honest-majority. The view-change (timeout-based round advancement) is simpler
than PBFT's but conceptually similar.

**Fork resolution:**
Not needed in normal operation. Equivocation (validator signing conflicting
messages) is detectable and slashable. This aligns with ILC's slashing
framework (CDL-055/056).

**Validator-set assumptions:**
Practical range: 10-200 validators before throughput degrades. Validator set
is defined per consensus instance — changes require governance. The Cosmos SDK
provides a mature validator management framework usable independently of ICS.

**ILC relevance:**
CometBFT is the most mature production-tested sovereign BFT engine available
without external security dependencies. It can be extracted from the Cosmos
SDK and run with an ILC-native application layer. The ABCI (Application
BlockChain Interface) abstraction separates consensus from application logic
cleanly — ILC's settlement-state submission model maps naturally to the ABCI
application layer.

**Key risks:**
- Taking a dependency on CometBFT means ILC inherits its release and security
  track, though not its governance
- The Cosmos SDK's governance module must be explicitly excluded or replaced
  with ILC's CDL process
- ABCI v2 (vote extensions, in Cosmos SDK v0.50+) adds complexity that ILC
  may not need

**Admissibility (row-7 / row-8):**
PASS if ILC operates its own validator set with no ICS dependency. CometBFT
is MIT licensed. The software is a tool; the governance model (Cosmos Hub,
ICS) is what Phase 688 excluded — and CometBFT without ICS has no Cosmos Hub
dependency.

**Row-7 detail:**
Tendermint BFT provides strong censorship resistance at the consensus layer —
a faulty proposer can be skipped after timeout, and 1/3+ honest validators
prevents finality of a censored block. Exitability is strong: the full block
history is available from any archive node. These properties satisfy row-7's
proof obligations at the design level; Phase 691 must verify them in practice.

---

### 2.3 HotStuff / Jolteon / Fast-HotStuff

**Origin and character:**
Yin et al. 2018 (HotStuff). Linear message complexity O(n) in the happy path
via a leader-based pipeline. Three-phase commit with threshold signatures.
Jolteon (2021, Diem/Aptos lineage) reduces to two rounds. Fast-HotStuff (2023)
optimizes latency further.

**Finality semantics:**
Deterministic. Linear commit pipeline. A block committed in phase 3 is final.

**Fork resolution:**
Not needed under honest majority. Equivocation is detectable via threshold
signature properties.

**Validator-set assumptions:**
The linear message complexity makes HotStuff-lineage protocols better at larger
validator sets than PBFT or Tendermint. Practical range extends to 500+
validators with threshold signatures. Admission/ejection still requires
governance.

**ILC relevance:**
The linear message complexity is a significant operational advantage if ILC's
validator set grows. HotStuff-lineage protocols are the current state of the
art for scalable deterministic BFT. The threshold signature requirement adds
cryptographic complexity but reduces per-round communication volume.

**Key risks:**
- Threshold signature infrastructure (BLS or similar) is an additional
  cryptographic dependency requiring careful implementation
- The Diem/Aptos lineage carries some association with Meta — the protocol is
  open, but the tooling ecosystem skews toward Aptos/Diem
- Auditable implementations outside the Aptos/Diem ecosystem are fewer than
  for Tendermint

**Admissibility (row-7 / row-8):**
PASS — the protocol is independent of any external constitutional center.
Row-7 properties are comparable to Tendermint. The threshold signature
approach may have slightly different censorship properties under adversarial
conditions — Phase 691 must evaluate this.

---

### 2.4 Narwhal-Bullshark (DAG-based mempool + BFT ordering)

**Origin and character:**
Spiegelman et al. 2022. Separates data dissemination (Narwhal DAG mempool)
from consensus ordering (Bullshark BFT). High-throughput design where
validators build a DAG of certified batches and the consensus layer orders
the DAG rather than individual transactions.

**Finality semantics:**
Deterministic finality via the ordering protocol. However, the separation of
dissemination from ordering means the finality model is more complex than
single-phase BFT.

**Fork resolution:**
The DAG structure makes equivocation detectable at the dissemination layer.
The ordering layer (Bullshark) provides BFT finality on the DAG ordering.

**Validator-set assumptions:**
Designed for high-throughput at medium validator sets. The DAG structure
distributes dissemination load, reducing the bottleneck at the leader.

**ILC relevance:**
The throughput advantage is primarily relevant at high transaction volume. For
ILC's settlement model — one epoch record per minute, relatively small per
record — the throughput advantage of Narwhal-Bullshark may not be the deciding
factor. The DAG-based dissemination model has interesting parallels with ILC's
own gossip architecture (CDL-060).

**Key risks:**
- Higher architectural complexity than Tendermint or HotStuff
- The auditable implementation surface is smaller (primarily Sui and early
  Aptos work)
- The finality model is harder to reason about for non-experts — Phase 691
  must test auditability explicitly
- The separation of dissemination and ordering may interact poorly with ILC's
  epoch-boundary commit semantics, which require atomic epoch-state finality

**Admissibility (row-7 / row-8):**
PASS at the protocol design level. Row-7 censorship resistance depends on the
DAG dissemination layer's anti-censorship properties — a censoring validator
can withhold its certified batches, which requires careful analysis against
the row-7 lock's "practical exclusion, not only packet-level denial" standard.

**Note:** This family is flagged for closer adversarial review in Phase 691
specifically on the censorship-resistance dimension.

---

### 2.5 Snowball / Avalanche-native (probabilistic BFT)

**Origin and character:**
Avalanche 2020. Probabilistic finality via repeated sub-sampled voting.
Nodes repeatedly sample a random subset of validators and converge
probabilistically to a common decision. No fixed leader.

**Finality semantics:**
PROBABILISTIC. Finality is statistical — with overwhelming probability after
sufficient rounds, but not deterministic. There is no single commit point
equivalent to PBFT's commit phase.

**Row-7 result: LIKELY FAIL**
Probabilistic finality creates a window in which a sufficiently resourced
adversary can attempt to delay or reverse finality. ILC's epoch-boundary
commit semantics require deterministic, replayable, auditable finality. A
substrate where "finality" is statistical cannot satisfy the replayability
requirement: the question "is epoch N finally committed?" has no deterministic
answer.

**Admissibility (row-7):** LIKELY FAIL for this reason specifically.

**Disposition: FLAGGED FOR EXCLUSION IN PHASE 691**
Avalanche-native probabilistic finality is likely inadmissible on row-7
grounds. Phase 691 should formally confirm this. The Avalanche
network-architecture (subnets, primary network) is separately excluded on
row-8 grounds as analyzed in Phase 688.

---

## 3. Constitutional versus engineering versus benchmark question separation

### 3.1 Constitutional questions (answered by canon, not by Phase 689)

- Must finality be deterministic? **YES** — row-7 replayability requirement.
- May the validator set include an external governance body? **NO** — row-8.
- May the backend author legitimacy? **NO** — CDL-065/row-6.
- Must strong exitability be provable? **YES** — row-7 proof obligations.

These questions are not design choices. They are already answered by closed
constitutional gates.

### 3.2 Engineering questions (answered by Phase 689 research)

- Which BFT protocol family has the best fit for ILC's 1-minute epoch cadence
  and ~50 KB/epoch settlement record size?
- What is the minimum honest-majority validator set size for practical
  operation?
- What is the implementation complexity of each family relative to ILC's
  current engineering capacity?
- Which family has the most auditable existing implementation?
- Which family is most compatible with ILC's gossip infrastructure
  (CDL-060/061 HTTP/3 gossip envelope)?

### 3.3 Benchmark questions (answered by Phase 690/691)

- Can this family finalize one epoch record per minute reliably?
- What is the failure behavior when f validators are offline?
- What is the recovery latency after a partition heals?
- Can a participant replay the full state history from genesis without
  operator assistance?
- Does the family expose any censorship surface that violates the row-7
  practical-exclusion standard?

---

## 4. Engineering comparison summary (planning level)

| Property | PBFT-lineage | CometBFT | HotStuff/Jolteon | Narwhal-Bullshark | Avalanche |
|---|---|---|---|---|---|
| Finality model | Deterministic | Deterministic | Deterministic | Deterministic | **Probabilistic** |
| Message complexity | O(n²) | O(n²) optimized | O(n) linear | O(n) DAG | O(n log n) |
| Leader dependency | Yes | Yes | Yes (pipelined) | No (DAG) | No |
| Validator set scale | ~50 practical | ~100 practical | ~500 practical | ~100-200 practical | ~1000+ |
| Production maturity | Academic, some prod | High (Cosmos) | Medium (Aptos) | Medium (Sui) | High (Avalanche) |
| Audit surface | Moderate | Large (CometBFT) | Smaller | Smaller | Large (Avalanche) |
| ILC epoch cadence fit | Good | Good | Good | Complex | N/A (excluded) |
| Row-7 admissibility | PASS | PASS | PASS | CONDITIONAL | **LIKELY FAIL** |
| Row-8 admissibility | PASS | PASS | PASS | PASS | **FAIL** |

---

## 5. Preliminary ordering for Phase 691 focus

Based on the engineering research above, the ordering of families for serious
Phase 691 analysis is:

**Tier 1 — Primary evaluation targets:**
- CometBFT (standalone, no ICS): highest production maturity, most auditable
  implementation, deterministic finality, good epoch cadence fit
- HotStuff / Jolteon: best message-complexity scaling, strong finality
  semantics, worth serious evaluation as the scalable alternative to CometBFT

**Tier 2 — Secondary evaluation (conditional):**
- Narwhal-Bullshark: architecturally interesting, but DAG complexity and
  censorship-resistance questions require closer adversarial review
- PBFT-lineage minimal custom: relevant as a design reference; practical only
  at small validator sets (<50); may be the right choice if ILC's initial
  validator set is intentionally small

**Tier 3 — Flagged for exclusion confirmation:**
- Avalanche-native: probabilistic finality likely fails row-7; confirm in
  Phase 691

---

## 6. Implementation-shape considerations

The "custom minimal sovereign L1" family does not prescribe a single
implementation. The implementation shape question is:

**Option A: Protocol-native clean-room BFT implementation**
- Maximum constitutional clarity: ILC writes its own consensus engine
- Maximum implementation risk: BFT is hard to implement correctly
- Maximum audit independence: no inherited external codebase dependencies

**Option B: CometBFT extracted and wrapped with ILC-native application layer**
- Lowest implementation risk for the consensus engine
- Inherits CometBFT's audit history and security track record
- Requires explicit exclusion of Cosmos SDK governance module and careful
  ABCI boundary definition
- The consensus engine is MIT licensed; the application layer is entirely ILC

**Option C: HotStuff reference implementation adapted**
- Medium implementation risk
- Smaller existing audit surface than CometBFT
- Better long-term scaling if validator set grows beyond ~100

**Option D: Narwhal-Bullshark adapted**
- Highest implementation complexity
- Best theoretical throughput but likely unnecessary at ILC's initial epoch
  volume

**Planning recommendation (unratified):**
Option B (CometBFT extracted) for the first implementation lane, evaluated in
Phase 691 against Option A (clean-room) and Option C (HotStuff) on audit
surface, row-7 censorship properties, and epoch-cadence fit.

This is a planning recommendation only. Phase 691 comparison analysis governs
the actual survivor set.

---

## 7. What this phase does not decide

This phase does not decide:
- which family is selected as the substrate
- what the validator set size is
- whether CometBFT or any other framework is adopted
- any runtime implementation details
- any final mechanism for row-5 privacy compliance
