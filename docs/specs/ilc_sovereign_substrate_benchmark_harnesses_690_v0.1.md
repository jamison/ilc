# ILC Sovereign Substrate Benchmark Harnesses 690 v0.1

Status: benchmark methodology artifact — bounded research only
Date: 2026-04-16
Phase: 690
Owner lane: G8 sovereign-substrate research

`benchmark_harnesses_690_complete`
`harnesses_anchored_to_settlement_state_enumeration_687`
`bounded_harnesses_are_not_public_production_proof`
`bal_profile_weights_are_unratified_planning_inputs_in_this_phase`

---

## 1. Anchor: settlement-state model

All workload definitions and measurement targets in this phase are anchored to
the settlement-state enumeration from Phase 687:
`docs/specs/ilc_settlement_state_enumeration_and_submission_model_687_v0.1.md`

The benchmark target is not "generic blockchain throughput."

The benchmark target is: can this substrate reliably finalize one ILC epoch
settlement record per validation epoch (~1 minute) under the conditions ILC
actually requires?

---

## 2. Economic and kernel assumptions — unratified inputs

The following planning assumptions are used in harness workload sizing. They
are NOT ratified constitutional law. They are planning inputs pending
calibration in Window 701-706.

| Assumption | Planning value | Ratification status |
|---|---|---|
| Validation epoch duration | ~1 minute | Ratified — Phase 546 |
| BAL reuse weight | 0.35 | UNRATIFIED — planning input |
| BAL contradiction-resilience weight | 0.25 | UNRATIFIED — planning input |
| BAL validation-integrity weight | 0.20 | UNRATIFIED — planning input |
| BAL path-uplift weight | 0.20 | UNRATIFIED — planning input |
| Freshness decay lambda | 0.25 | Implemented — no simulation provenance |
| P_e clamp range | 0.75–1.30 | Ratified — CDL-030 |
| Epoch budget constraint | B_e = I_e + F_e - X_e | Ratified — CDL-025/030 |

Benchmark results that depend on the unratified inputs must state this
explicitly and must not be presented as definitive economic analysis.

---

## 3. Workload definitions

### Workload A: Baseline epoch-record finalization

**Description:** Submit one complete epoch settlement record per validation
epoch. Measure finality latency, reliability, and rollback behavior.

**Record composition (Phase 687 planning estimate):**
- 1 epoch state root (CIDv1, 36 bytes)
- 100-500 new node CID entries (~3-18 KB)
- 200-1000 edge tuples (~8-40 KB)
- 10-50 economic events (~1-5 KB)
- 0-5 namespace events (<1 KB)
- 0-2 governance events (<1 KB)
- Total: ~12-65 KB per epoch record

**Target finality latency:** ≤ 30 seconds from submission to committed
(allowing half the epoch duration for finality before next epoch begins)

**Required observations:**
- median finality latency across 100 epochs
- 99th percentile finality latency
- failed-finality rate (epochs where finality was not achieved within 60
  seconds)
- does the substrate produce a single deterministic commit point, or a
  probabilistic convergence? (deterministic required — see row-7)

**Pass criterion:** 99th percentile finality latency ≤ 45 seconds, failed-
finality rate ≤ 0.1% over 100 epochs, deterministic commit point confirmed.

---

### Workload B: Censorship-resistance drill

**Description:** Operate a validator set where f validators are configured to
refuse to include epoch records from a designated "censored" submission node.
Measure whether the censored submission eventually achieves finality.

**Setup:** Minimum 7 validators (Byzantine fault tolerance requires 3f+1;
with f=2 faulty, need 7 honest). Configure 2 validators to exclude a
designated epoch record CID from their proposals.

**Required observations:**
- does the censored epoch record achieve finality within 3 epoch durations?
- does the f-censor configuration prevent finality entirely, or only delay it?
- is the censorship detectable from the public record? (required for row-7)

**Row-7 standard (Phase 675):** Censorship must not be the ordinary path.
One or two faulty validators should not be able to permanently block a valid
epoch record submission.

**Pass criterion:** Censored epoch record achieves finality within 5 epoch
durations despite f=2 censoring validators. Censorship attempt is detectable
from public validator behavior record.

---

### Workload C: Partition, heal, and recovery

**Description:** Partition the validator set into two groups that cannot
communicate. Allow each group to continue attempting to submit epoch records.
Reconnect. Measure recovery behavior.

**Required observations:**
- does the partitioned set halt (safe) or produce conflicting commits (unsafe)?
  A BFT system with honest majority should halt, not fork.
- how long after reconnection before the system recovers to normal operation?
- are any epoch records submitted during the partition window lost, or are they
  eventually committed after recovery?

**Pass criterion:**
- no conflicting commits produced during partition (safety preserved)
- recovery to normal operation within 10 epoch durations after reconnection
- no submitted epoch records permanently lost

---

### Workload D: Replayability and state extraction

**Description:** Reconstruct the full canonical state from genesis to the
current epoch using only the on-chain settlement record. No operator
cooperation assumed.

**Required observations:**
- can a new participant reconstruct the canonical epoch-state-root sequence
  from genesis to current epoch using only the settlement substrate data?
- is the genesis lineage anchor verifiable as the canonical root?
- can any arbitrary epoch's state root be retrieved and verified independently?

**Row-7 exitability standard:** Any participant must be able to replay the
full state history without privileged operator consent.

**Pass criterion:** Full genesis-to-current state-root chain reconstructed
from public substrate data without operator assistance. Verification of any
epoch state root succeeds independently.

---

### Workload E: Validator operability

**Description:** Measure the operational burden of running a validator node
for ILC's epoch-state submission workload.

**Required observations:**
- minimum hardware to run a validator node that achieves Workload A pass
  criteria (target: commodity server, ≤ 8 cores, ≤ 32 GB RAM, ≤ 1 TB SSD)
- time to sync a new validator node from genesis to current epoch
- time to recover a crashed validator node and rejoin the active set
- storage growth rate per epoch (target: ≤ 100 KB/epoch on-chain state growth)

**Pass criterion:** A validator node achieving Workload A finality targets
runs on commodity hardware. New node sync time ≤ 24 hours at 10,000 epoch
history. Storage growth ≤ 100 KB/epoch.

---

### Workload F: Bounded public auditability

**Description:** Verify that the settlement record supports bounded human
inspection without expert-only tooling.

**Required observations:**
- can a non-expert operator verify that a specific epoch state root is
  canonical, using only a standard JSON/CLI interface?
- can a non-expert operator verify that a specific economic event (stake, slash,
  bounty) appears in the canonical record?
- does any required audit operation require specialized cryptographic tooling
  beyond standard hash verification?

**Phase 679 observability budget standard:** Bounded human auditability is
non-negotiable. Default verification paths must not require expert-only tooling.

**Pass criterion:** All three observations achievable via standard CLI or
JSON interface. No cryptographic operations beyond standard hash verification
required for basic audit.

---

## 4. Scenario catalog summary

| Scenario | Workload | Primary gate tested | Pass criterion summary |
|---|---|---|---|
| Baseline finalization | A | Deterministic finality | ≤ 45s 99th-pct, ≤ 0.1% failure |
| Censorship resistance | B | Row-7 censorship | Finality within 5 epochs despite f=2 censors |
| Partition and recovery | C | Row-7 replayability / safety | No fork, recovery ≤ 10 epochs |
| State extraction | D | Row-7 exitability | Full chain reconstructible without operator |
| Validator operability | E | Row-7 operability | Commodity hardware, ≤ 24h sync |
| Bounded auditability | F | Phase 679 observability | CLI/JSON verifiable, no expert tools |

---

## 5. Row-5 compatibility check

For each candidate family that reaches Phase 691 analysis, the benchmark run
must include:

- Does the substrate require per-epoch-record contributor identity disclosure
  on-chain? If yes: flag as row-5 compatibility risk.
- Is there a structural requirement for per-agent linkable records in the
  economic event log? If yes: flag as row-5 compatibility risk.
- Can timing-smoothing (batching multiple submissions per epoch record) be
  implemented without protocol modification? If no: flag.

These are not full row-5 closure checks. They are compatibility red-flag
tests. A red flag here does not disqualify a family but must be resolved in
Phase 691 analysis.

---

## 6. What these harnesses are not

`bounded_harnesses_are_not_public_production_proof`

These harnesses are bounded research instruments. They establish whether a
candidate family is plausible for ILC's use case. They do not:
- prove production security under real hostile-internet conditions
- prove validator economics at scale
- prove censorship resistance against nation-state-level adversaries
- prove long-run liveness under Byzantine validator set evolution
- constitute any form of security audit

The results from these harnesses feed Phase 691 comparative analysis and
Phase 692 survivor-set narrowing. They are necessary but not sufficient for
any final substrate selection.
