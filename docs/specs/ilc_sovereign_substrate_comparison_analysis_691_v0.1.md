# ILC Sovereign Substrate Comparison Analysis 691 v0.1

Status: comparison analysis — adversarial review artifact
Date: 2026-04-16
Phase: 691
Owner lane: G8 sovereign-substrate research

`comparison_analysis_691_complete`
`evaluation_anchored_to_constitutional_gates_not_performance_first`
`bal_profile_weights_are_unratified_planning_inputs_in_this_phase`

---

## 1. Evaluation frame

This analysis compares the Phase 689 Tier 1 and Tier 2 families against ILC's
actual requirements. The evaluation hierarchy from the conversation frame
governs:

1. Constitutional admissibility (rows 6-8 filters — already applied in 688)
2. Finality semantics (deterministic commit, fork-resolution)
3. Censorship resistance and exitability (row-7 proof obligations)
4. Bounded public auditability (Phase 679 observability budget)
5. Participant operability (commodity hardware, small validator set)
6. Implementation tractability (audit surface, ILC engineering capacity)
7. Performance and operational cost (tiebreaker only)

Families evaluated: CometBFT (standalone), HotStuff/Jolteon, Narwhal-Bullshark.
Avalanche-native probabilistic finality is evaluated for exclusion confirmation.

---

## 2. CometBFT (standalone, no ICS dependency)

### 2.1 Finality semantics

CometBFT provides deterministic, single-round finality. A block receiving
2/3+ precommits is final. There is no fork under honest-majority conditions.

For ILC's epoch-boundary commit semantics: one epoch = one block = final.
The finality model is a natural fit. The 1-minute epoch cadence is well within
CometBFT's practical throughput at small validator sets.

**Assessment: STRONG — finality semantics match ILC's requirements precisely.**

### 2.2 Censorship resistance and exitability (row-7)

**Censorship resistance:**
A valid block requires 2/3+ prevotes and 2/3+ precommits. A censoring minority
(< 1/3 voting power) cannot prevent finality of a valid block. A censoring
majority (> 2/3) would constitute a Byzantine failure — beyond the honest-
majority assumption. Under the row-7 standard ("one operator or dashboard may
not be the ordinary path"), CometBFT satisfies censorship resistance as long
as the validator set is sufficiently distributed.

The key vulnerability: if a single entity controls > 1/3 of the validator set,
it can halt finality (safety margin breach). ILC's validator admission
governance (CDL-055/056) must prevent this concentration.

**Exitability:**
The full block history is available from any archive node. State reconstruction
from genesis requires only the public chain data. A participant can verify any
epoch state root independently by replaying the block history. CometBFT's
storage model (append-only block log) makes exitability straightforward.

**Row-7 verdict: CONDITIONAL PASS**
Censorship resistance is protocol-sound but validator-set-composition-dependent.
Exitability is strong. The row-7 proof obligation requires ILC's validator
governance to prevent >1/3 concentration — this is a governance obligation,
not a protocol deficiency.

### 2.3 Bounded public auditability

CometBFT exposes full block data via standard RPC (REST + gRPC). Block
headers, transaction records, and consensus state are queryable without
specialized cryptographic tooling. A standard JSON/CLI interface can verify
any epoch state root against the on-chain record.

The Cosmos SDK's ABCI interface separates consensus state from application
state — ILC's settlement record lives in the application layer, fully
accessible via standard queries.

**Assessment: PASS — strong auditability surface, no expert-only tooling
required for basic verification.**

### 2.4 Participant operability

CometBFT validator nodes are production-tested on commodity hardware.
The Cosmos SDK ecosystem has multi-year operational history at small-to-medium
validator sets. Sync time from genesis scales with block history but is
manageable for ILC's ~50 KB/epoch record size.

The operational burden of running a CometBFT-based ILC validator is comparable
to running a mid-tier Cosmos app-chain validator — a well-documented, well-
tooled workload.

**Assessment: STRONG — mature operational tooling, commodity hardware viable.**

### 2.5 Implementation tractability

CometBFT is MIT licensed and extractable from the Cosmos SDK. The consensus
engine is well-audited. The ABCI boundary cleanly separates ILC's application
logic from the consensus mechanism.

Risks:
- ILC must explicitly exclude the Cosmos SDK governance module and replace it
  with ILC's CDL process. This is architecturally clean but requires explicit
  effort.
- CometBFT's release cadence and security patches become a dependency ILC must
  track.
- The ILC application layer (ABCI app) is ILC's primary engineering surface —
  it must implement the settlement-state submission model from Phase 687.

**Assessment: STRONG — most tractable implementation path among the Tier 1
families. Largest existing audit surface.**

### 2.6 Row-5 compatibility

CometBFT does not require per-agent identity disclosure on-chain as a
structural requirement. The settlement record contains epoch state roots and
economic events — not raw contributor identity. The three near-term tractable
mechanism families from Phase 680 are all implementable on top of a CometBFT-
based ILC settlement layer without protocol modification.

**Assessment: PASS — no row-5 incompatibility identified.**

### 2.7 Where CometBFT is constitutionally strong but operationally demanding

**Strength:** Protocol-level censorship resistance, deterministic finality,
strong exitability, mature audit surface.

**Demand:** Validator governance must prevent >1/3 concentration. The CDL
process governs Cosmos SDK module exclusion. The ABCI application layer is
ILC's engineering responsibility.

**Overall verdict: TIER 1 SURVIVOR — recommended primary implementation
investigation target.**

---

## 3. HotStuff / Jolteon

### 3.1 Finality semantics

HotStuff provides deterministic pipelined finality with O(n) message
complexity via threshold signatures. Jolteon reduces to two-phase commit.
Finality is deterministic — a block that completes the commit phase is final.

For ILC's epoch-boundary semantics: same natural fit as CometBFT, with better
message complexity at larger validator set sizes.

**Assessment: STRONG — finality semantics equivalent to CometBFT.**

### 3.2 Censorship resistance and exitability (row-7)

**Censorship resistance:**
Similar to CometBFT — honest majority prevents censorship of valid blocks.
The pipelined leader rotation means a censoring leader is bypassed after
timeout. However, the threshold signature requirement means a censoring
minority that refuses to contribute signature shares can slow but not prevent
finality (the threshold can be met without the censoring validators if they
are in the minority).

**Exitability:**
Equivalent to CometBFT — full block history available from archive nodes.

**Row-7 verdict: CONDITIONAL PASS (same conditions as CometBFT)**

### 3.3 Bounded public auditability

Threshold signatures (BLS aggregation) are less familiar to non-expert
auditors than individual validator signatures. Verifying that a block received
2/3+ threshold signatures requires understanding of BLS aggregation — this
is slightly more complex than CometBFT's individual-signature model.

**Assessment: CONDITIONAL PASS — auditability is achievable but requires
more sophisticated tooling than CometBFT for complete verification.**

### 3.4 Implementation tractability

HotStuff-lineage implementations outside the Aptos/Diem ecosystem are fewer
and less audited than CometBFT. The threshold signature infrastructure (BLS12-
381 or similar) is an additional cryptographic dependency requiring careful
implementation and auditing.

The scaling advantage of O(n) message complexity is relevant at validator sets
>100. At ILC's initial validator set (likely 10-50 nodes), the practical
throughput advantage over CometBFT is small.

**Assessment: MODERATE — valid choice for later-stage scaling, but higher
implementation complexity and smaller audit surface than CometBFT at current
scale.**

### 3.5 Row-5 compatibility

Same as CometBFT — no structural incompatibility with Phase 680 near-term
mechanism families.

**Assessment: PASS.**

### 3.6 Verdict

**TIER 1 SURVIVOR — recommended secondary investigation target.**
Strong finality and censorship properties. Higher implementation complexity
than CometBFT. The scaling advantage is valuable for later-stage validator set
growth. Phase 692 should recommend CometBFT as primary and HotStuff/Jolteon
as the scaling-path alternative.

---

## 4. Narwhal-Bullshark

### 4.1 Finality semantics

Narwhal-Bullshark provides deterministic ordering of a DAG of certified
batches. Finality is deterministic once the Bullshark ordering protocol
commits a DAG vertex. However, the two-layer architecture (dissemination DAG +
ordering protocol) makes the finality model harder to reason about than
single-phase BFT.

**Assessment: MODERATE — deterministic finality achievable but more
architecturally complex.**

### 4.2 Censorship resistance (row-7) — adversarial review

**Flag raised in Phase 689.** The DAG dissemination model has a specific
censorship surface: a validator that withholds its certified batches from the
DAG can prevent the ordering protocol from committing blocks that include those
batches.

Under the row-7 practical-exclusion standard — "practical exclusion, not only
packet-level denial" — a validator that withholds certified batches is
exercising practical exclusion. If the censoring validator controls a
sufficient share of the DAG dissemination weight, this may be sufficient to
delay or prevent finality for specific records.

This is a more nuanced censorship surface than CometBFT's simpler
prevote/precommit model.

**Row-7 verdict: CONDITIONAL — requires more adversarial analysis than Tier 1
families. The DAG withholding attack surface must be formally bounded before
this family can claim row-7 compliance.**

### 4.3 Operability and implementation tractability

The DAG-based architecture is more complex to implement and operate than
single-phase BFT. Existing auditable implementations (Sui, early Aptos) are
tied to specific ecosystems. Extracting a standalone Narwhal-Bullshark
implementation for ILC is non-trivial.

**Assessment: LOWER TRACTABILITY than Tier 1 families at current scale.**

### 4.4 Verdict

**TIER 2 — CONDITIONAL SURVIVOR.** Interesting architecture with genuine
throughput advantages. The DAG censorship surface requires formal adversarial
bounding before row-7 compliance can be claimed. Recommended for Phase 692
carry-forward as a deeper-investigation target for the post-selection
implementation lane, not as the primary Phase 692 survivor for initial
implementation.

---

## 5. Avalanche-native (probabilistic) — exclusion confirmation

### 5.1 Row-7 analysis

Avalanche-native consensus uses probabilistic finality. Finality is statistical
— with overwhelming probability after sufficient rounds, but with no
deterministic commit point.

ILC's Phase 687 settlement-state model requires deterministic, replayable,
auditable finality. The question "is epoch N finally committed?" must have a
deterministic yes/no answer. Probabilistic finality cannot satisfy this
requirement.

**Row-7 replayability requirement:** The protocol must produce a single final,
replayable epoch state root per epoch. A probabilistically converged state
root is not the same as a deterministically committed one — an adversary with
sufficient resources can attempt to reverse probabilistic finality in a way
that is categorically impossible against deterministic BFT.

**Row-7 verdict: FAIL — probabilistic finality is incompatible with ILC's
replayability requirement.**

**Row-8 verdict: FAIL (separately) — Avalanche network governance.**

### 5.2 Exclusion confirmed

`avalanche_native_excluded_probabilistic_finality_fails_row_7`

Avalanche-native probabilistic consensus is excluded from the ILC sovereign
substrate candidate set on row-7 grounds.

This exclusion is independent of and in addition to the row-8 exclusion of
the Avalanche network confirmed in Phase 688.

---

## 6. Candidate summary

| Family | Finality | Row-7 | Row-8 | Row-5 | Auditability | Tractability | Verdict |
|---|---|---|---|---|---|---|---|
| CometBFT (standalone) | Deterministic | COND. PASS | PASS | PASS | STRONG | STRONG | **TIER 1 SURVIVOR** |
| HotStuff / Jolteon | Deterministic | COND. PASS | PASS | PASS | MOD. | MODERATE | **TIER 1 SURVIVOR** |
| Narwhal-Bullshark | Deterministic | CONDITIONAL | PASS | PASS | MODERATE | LOWER | **TIER 2 (deferred)** |
| Avalanche-native | **Probabilistic** | **FAIL** | **FAIL** | — | — | — | **EXCLUDED** |

---

## 7. Constitutionally strong but operationally demanding — explicit statement

Per Phase 692 handoff requirement: where a family is constitutionally strong
but difficult versus attractive-looking but constitutionally weak.

**Constitutionally strong, operationally demanding:**
- CometBFT: strong on all constitutional dimensions. Operationally demands
  explicit Cosmos SDK governance module exclusion, ongoing CometBFT release
  tracking, and ILC ABCI application layer development.
- HotStuff/Jolteon: strong on constitutional dimensions. Demands threshold
  signature infrastructure and smaller existing audit surface.

**Attractive-looking but constitutionally weak:**
- Avalanche-native: large production network, high throughput, mature tooling.
  Fails row-7 (probabilistic finality) and row-8 (external governance) — not
  a real candidate regardless of marketing.
- Shared sequencer networks: appear to offer sovereign-chain ergonomics while
  solving ordering complexity. Fail row-6, row-7, and row-8 — not a real
  candidate.
- Appchain frameworks with ICS: appear sovereign but delegate security to
  external validator sets. Fail row-8 under standard configuration.

---

## 8. Open questions for Phase 692 handoff

The Phase 692 survivor-set handoff must address:

1. **Validator set composition governance:** Both Tier 1 survivors require
   ILC's CDL process to prevent >1/3 concentration. The CDL-017 (Bootstrap
   transition criteria) carry-forward is directly relevant here — validator
   admission governance must be specified before any implementation lane.

2. **ABCI application layer scope (CometBFT path):** The ILC ABCI application
   is a non-trivial implementation deliverable. The next implementation lane
   must scope this explicitly.

3. **Threshold signature implementation (HotStuff path):** BLS12-381 or
   equivalent must be scoped as a cryptographic dependency if HotStuff/Jolteon
   is the implementation target.

4. **Narwhal-Bullshark DAG censorship formal analysis:** Before this family
   can be elevated to Tier 1 in any later lane, the DAG withholding attack
   surface must be formally bounded.

5. **BAL weight calibration dependency:** Any benchmark results in this window
   that used BAL profile weights for ECU kernel sizing must be re-evaluated
   after Window 701-706 calibration. The Phase 692 handoff must name this
   explicitly.
