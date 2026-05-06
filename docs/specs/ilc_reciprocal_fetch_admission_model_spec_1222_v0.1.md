# ILC Reciprocal Fetch Admission Model Spec 1222 v0.1

**Phase:** 1222
**Window:** 1218-1224
**Date:** 2026-05-06
**Status:** DESIGN SPEC ONLY - no runtime implementation — SUPPLEMENTED post-commit: reciprocal scoring is a deferred research candidate, not the preferred direction. See §8.

`reciprocal_fetch_admission_model_spec_committed_phase_1222`
`fetch_distribution_architecture_reframed_phase_1222`

Consumes:

```text
reciprocal_fetch_admission_model_required
```

Preserves:

```text
transport_abuse_circuit_breaker_not_final_scaling_policy
```

---

## 1. Problem Statement

The existing static WANT-BLOCK limiter is a necessary abuse circuit breaker, not the final
ILC communication policy.

Static caps are insufficient at ILC scale because:

- digital agents may legitimately request and serve content much faster than human users;
- useful pull demand varies by shard, topic, epoch, replication state, and agent role;
- fixed request ceilings punish high-throughput useful agents and underprice low-output
  extractive agents;
- ILC is pull-dominant by design, so the correct long-term policy should reward reciprocal
  service rather than suppress speed;
- communication pressure should equilibrate through reputation, ECU/stake escrow, useful
  outbound service, and bounded proof-of-work fallback, not through a permanent one-size cap.

The model below is a candidate for a future ratified reciprocal admission policy. It is not
implemented in Phase 1222 and does not supersede CDL-077 or Phase 1212 limiter wiring.

---

## 2. Model Parameters — Non-Selected Candidate

> **Correction recorded post-commit (Phase 1222 supplement):** The formula below is a
> research candidate only. It is not the recommended implementation direction. The
> structural objections in §8 must be resolved before this model or any derivative is
> opened as a CDL. Do not use this formula as a planning default for future windows.

All arithmetic is Decimal or integer arithmetic. No float constants are permitted in a future
runtime implementation.

### 2.1 Admission Window

Proposed measurement window:

```text
fetch_admission_window = one protocol fetch epoch
```

The fetch epoch must be defined by protocol sequence/epoch counters, not wall-clock time.
Wall-clock minute limits may remain as operator-local circuit breakers during transition,
but constitutional admission accounting should be epoch-based.

### 2.2 Baseline Free Capacity

```text
baseline_want_block_capacity = Decimal("10")
capacity_floor = Decimal("2")
capacity_ceiling = Decimal("1000")
```

Every valid requester with a Genesis-lineage-valid identity receives at least the floor unless
that identity is under explicit abuse quarantine. The baseline preserves current CDL-077
calibration shape while allowing a future epoch-based transition.

### 2.3 Reciprocal Ratio

```text
reciprocal_ratio = useful_outbound_serves / max(inbound_pull_requests, Decimal("1"))
```

Definitions:

- `inbound_pull_requests`: accepted WANT-BLOCK requests made by this requester during the
  rolling fetch epoch window.
- `useful_outbound_serves`: verified successful WANT-BLOCK serves by this requester to
  other peers during the same rolling window.
- Failed, duplicate, invalid-lineage, or self-loop serves do not count as useful outbound
  serves.

### 2.4 Decimal Sigmoid-Like Capacity Curve

Future implementation should avoid `math.exp` and binary floats. The recommended calibration
function is a rational Hill curve:

```text
admission_midpoint = Decimal("0.50")
admission_slope_power = 2
reciprocal_component =
  reciprocal_ratio^2 / (reciprocal_ratio^2 + admission_midpoint^2)
```

`reciprocal_component` is in `[0, 1]`, monotonic, saturating, and implementable with Decimal
arithmetic. It behaves like a sigmoid without requiring exponential functions.

### 2.5 CDL-078 Routing Reputation Booster

CDL-078 routing reputation is the primary x-axis trust input:

```text
reputation_score in [Decimal("0"), Decimal("1")]
reputation_capacity = Decimal("200") * reputation_score
```

Reputation can boost capacity but cannot bypass quarantine, invalid lineage, or explicit
abuse-debt penalties.

### 2.6 ECU / Stake Escrow Booster

ECU/stake escrow is a secondary booster, not the primary admission signal:

```text
escrow_unit = Decimal("10")
escrow_capacity_cap = Decimal("200")
escrow_capacity = min(escrowed_ecu / escrow_unit, escrow_capacity_cap)
```

Escrow mechanics:

- escrow is locked per fetch epoch;
- useful outbound service reduces future escrow requirements;
- abuse debt consumes escrow first;
- unused escrow unlocks after the rolling window if no abuse debt is recorded;
- validator stake may qualify only if a governing CDL explicitly maps validator stake to
  fetch-admission escrow without weakening validator-security economics.

### 2.7 Proposed Capacity Formula

```text
organic_capacity =
  baseline_want_block_capacity
  + (Decimal("600") * reciprocal_component)
  + reputation_capacity
  + escrow_capacity

admitted_capacity =
  min(capacity_ceiling, max(capacity_floor, organic_capacity - abuse_debt_penalty))
```

This formula rewards reciprocal service first, reputation second, escrow third. It should be
calibrated by simulation before ratification.

### 2.8 Puzzle Requirement Threshold

Hashcash-style proof-of-work is a fallback when an identity demands more than its organic
capacity:

```text
puzzle_required_if =
  inbound_pull_requests > admitted_capacity
  AND reputation_score < Decimal("0.25")
  AND reciprocal_ratio < Decimal("0.25")
```

Puzzle difficulty should be symbolic and bounded. It should deter spam without becoming a
dominant resource market or disadvantaging low-power legitimate agents.

### 2.9 Abuse Debt Accumulation

```text
allowed_asymmetry = Decimal("2.0")
abuse_debt_delta =
  max(Decimal("0"), inbound_pull_requests - (allowed_asymmetry * useful_outbound_serves)
      - escrow_capacity)
abuse_debt_next = max(Decimal("0"), abuse_debt_previous + abuse_debt_delta - repayment)
```

Repayment comes from later useful outbound serves and optional escrow burn. Abuse debt
reduces future admitted capacity before puzzle fallback is offered.

### 2.10 Minimum Capacity Floor

The model must not starve new or small legitimate nodes:

```text
minimum_capacity_floor = Decimal("2")
```

The floor is available only to valid Genesis-lineage identities that are not quarantined.

---

## 3. Interaction With Existing CDLs / ADRs

### CDL-077

Preserved:

- WANT-HAVE / WANT-BLOCK two-phase pull design;
- WANT-HAVE as cheap availability probe;
- WANT-BLOCK as protected expensive fetch path;
- over-limit machine token behavior.

Superseded only after future ratification:

- static per-identity cap as the final admission policy.

CDL-077 remains active until the reciprocal admission model is implemented, tested, and
ratified.

### CDL-078

CDL-078 routing reputation becomes the primary trust input for capacity scaling. Reputation
is consumed as a bounded signal, not as an unconditional bypass.

### CDL-060

Gossip pull capacity is adjacent but not automatically in scope. Phase 1222 recommends that
the first implementation target WANT-BLOCK fetch only. Gossip admission should be evaluated
after fetch admission calibration because gossip can amplify topology-wide load.

### CDL-054

Validator rewards and validator stake may inform escrow only by explicit constitutional
mapping. Fetch admission must not silently convert validator stake into general bandwidth
privilege.

### ADR-0037

Genesis-lineage validity is a prerequisite. A requester that cannot resolve to the current
canonical Genesis lineage receives no canonical admission guarantee.

---

## 4. Constitutional Routing

Recommended future route:

1. Open a new CDL for reciprocal fetch admission, unless CDL-077 amendment scope is judged
   sufficient by a sequence-lock phase.
2. Run a SIM calibration phase before ratification:
   - legitimate high-throughput agent;
   - low-reputation spammer;
   - high-escrow extractor;
   - reciprocal relay cluster;
   - Sybil requester cluster.
3. Implement behind a feature flag or operator-local opt-in.
4. Run a parallel-operation validation window with both static limiter and reciprocal
   admission active.
5. Ratify static-limiter supersession only after validation.

Estimated target: Window 1225+ for opening/spec refinement; implementation only after SIM
calibration and constitutional routing are complete.

---

## 5. Static Limiter Supersession Boundary

The static limiter may not be deprecated until all conditions below are satisfied:

1. Reciprocal admission model is ratified in a governing CDL.
2. Runtime implementation exists with Decimal-only arithmetic.
3. Static limiter and reciprocal limiter run in parallel for a validation window.
4. Regression tests prove no unlimited fetch path exists.
5. Abuse circuit-breaker semantics remain fail-closed.
6. Operators can inspect emitted admission tokens.
7. The transition preserves `transport_abuse_circuit_breaker_not_final_scaling_policy`.

Until then, the persistent/static limiter remains a safety rail.

---

## 6. Open Questions For Calibration

These are evidence questions, not TBD placeholders:

- exact capacity ceiling per shard class;
- exact reputation scale imported from CDL-078 runtime;
- whether escrow burn or escrow lock is preferable under attack;
- whether puzzle fallback is needed at all once reciprocal reputation is live;
- whether gossip admission should share the same formula or remain separate.

---

## 8. Reframing: Fetch Is Topological, Not Symmetric

> **Post-commit supplement.** This section records the architectural correction made
> following review by Codex and Genesis authority. It supersedes the framing implied by
> §1–§6 as the preferred direction. §1–§6 remain as documentation of the research candidate
> only.

### 8.1 The Structural Error in the Original Framing

The reciprocal fetch admission model assumes **symmetric peer pressure** — agents pulling
roughly as much as they serve over time, with healthy nodes converging toward balanced
reciprocity ratios.

That assumption is wrong for ILC. ILC fetch traffic has a **topology**. The graph has a
root (Genesis), high-centrality nodes (truth primitives, accepted CDLs, ADR chain,
manifests, lineage receipts), and a long tail of lower-centrality content. Fetch pressure
flows **down from root** toward the high-centrality center, not uniformly between peers.

New agents, bootstrapping agents, archival readers, and visualization tools all legitimately
generate asymmetric pull pressure toward high-centrality nodes. That is not abuse — it is
the network behaving correctly. A new agent that pulls Genesis, the seven truth primitives,
CDL-073 through CDL-086, and the ADR chain before it has served a single block is doing the
right thing. A reciprocal scoring model penalizes exactly that behavior.

**Reciprocity assumes mature peer symmetry. ILC bootstrap is asymmetric and
forward-oriented. These are structurally incompatible.**

### 8.2 The Read/Write Asymmetry Rule

**Reads and writes are different surfaces and must be protected differently.**

| Surface | Correct posture |
|---------|----------------|
| Reads — fetching truth primitives, provenance paths, Genesis lineage, CDL/ADR chain, manifests, lineage receipts | Public verifiable access wherever possible; treat as infrastructure |
| Writes/mutations — submit.truth, validate.claim, publication, mutation of canonical state | Economically gated by stake, reputation, and constitutional authority |
| Economic recognition — ECU attribution, validator rewards, canonical settlement | Gated by Genesis-lineage-valid participation and CDL-governed rules |
| Non-cacheable expensive operations, adversarial fetches, write-dressed-as-read | Targeted abuse controls at the protocol boundary |

"Admission" belongs to writes, mutations, publication, validator participation, and
non-cacheable expensive operations. It does not belong to ordinary reads of canonical
content. Making reads cheap and universally verifiable is a design goal, not a risk.

### 8.3 Content-Addressed Public Caching and High-Centrality Replication

The correct architecture for high-centrality read pressure is distribution and caching,
not admission scoring.

**Required infrastructure for high-centrality nodes:**

- Genesis artifacts, truth primitives, accepted CDLs and ADRs, manifests, and lineage
  receipts must be **cached, mirrored, and snapshotted** — treated as public verifiable
  infrastructure, not scarce peer favors.
- **Bulk snapshot distribution**: a new agent should be able to acquire a Genesis-rooted
  verified snapshot and prove its lineage without pulling every artifact live from a peer.
- **Incremental delta fetching**: after snapshot acquisition, only deltas since the snapshot
  need to be pulled from live peers.
- **Non-local compilation**: if content-addressed hashes plus lineage proofs are sufficient
  to verify a locally-cached or non-locally-held copy is canonical — and they should be,
  given the inward proof chain design — then an agent that compiles or reconstructs a local
  view from a verified snapshot does not create live peer pressure at all.

The fetch problem for legitimate agents is a **distribution and caching problem**, not an
admission scoring problem.

### 8.4 Additional Structural Objections to Reciprocal Scoring

Beyond bootstrapping asymmetry, the following concerns apply to any future reciprocal
scoring proposal and must be addressed by simulation evidence before any CDL is opened:

**Centralization risk:** High-reputation and high-stake actors earn more capacity, which
advantages incumbents and may make new and small agents structurally second-class.

**Privacy and surveillance surface:** Measuring reciprocal ratios requires tracking who
asks for what, who serves what, and how often. This creates a persistent behavioral record
that may leak agent identity and intent patterns.

**Gameability:** Reciprocal clusters, manufactured useful serves, escrow-backed spam, and
circular traffic can all artificially inflate admission capacity without contributing
legitimate value.

**Layer conflation:** Transport abuse prevention, routing reputation, ECU/stake economics,
and constitutional admission are separate concerns. Combining them in one formula before
evidence of their interaction is available risks coupling failures that are hard to
untangle constitutionally.

**Prematurity:** Without real traffic data from operating ILC agents, any calibration
(sigmoid midpoint, reputation scale, escrow unit, abuse debt threshold) is speculation.
Premature constitutional locking of these parameters before real traffic evidence is
available produces a brittle policy.

### 8.5 The Real Abuse Surface

Fetch abuse takes specific forms. Each has a targeted control that does not require
reciprocal scoring:

| Abuse form | Correct control |
|------------|----------------|
| Non-cacheable adversarial fetches at scale | Caching and mirroring of high-centrality content; non-cacheable requests require operator-local backpressure, not global scoring |
| Malformed or invalid requests | Protocol boundary validation; reject early before expensive processing |
| Write/mutation attempts dressed as reads | Explicit write surface enforcement; reads do not mutate state |
| Flooding a single high-centrality node | Replication and mirroring of that node, not per-requester admission throttling |
| Sybil spam at scale | Genesis-lineage identity requirement (already required); invalid identities receive no canonical admission guarantee |

### 8.6 Preferred Near-Term Direction

Until real traffic evidence exists:

1. **Keep the static limiter as an emergency circuit breaker.** Do not deprecate it.
2. **Add observability.** Measure request pressure per node tier, cache hit rates, failure
   patterns, and actual agent fetch behavior before designing any admission model.
3. **Build high-centrality replication infrastructure.** Genesis/root artifacts, truth
   primitives, ADR/CDL chain, manifests, and lineage receipts should be cached, mirrored,
   and snapshot-distributable before any admission model is designed.
4. **Prefer operator-local backpressure and shard-local configuration** over constitutional
   global formulas.
5. **Use puzzles or escrow only as last-resort attack-mode tools**, not as normal fetch
   infrastructure.
6. **Do not tie normal fetch capacity to reputation or stake** until simulations and real
   traffic show this is necessary and that the structural objections above are addressed.

### 8.7 Carry-Forward

```text
fetch_distribution_architecture_reframed_phase_1222
```

Future windows should plan high-centrality replication infrastructure and observability
before any reciprocal admission CDL is opened. The sigmoid/reciprocal formula in §2 is a
research candidate requiring simulation calibration and structural objection resolution
before it may be proposed for ratification.

---

## 7. Non-Claims

This phase does not:

- implement reciprocal admission;
- mutate `ilc_core/`;
- amend CDL-077;
- open or ratify any new CDL;
- deprecate the static limiter;
- authorize public launch, public repository publication, public release artifact
  distribution, public RC announcement, or external operator bootstrap.

