# ILC Validator Enhancement Roadmap

Author: Architecture governance dialogue (Phase 479 session)
Date: 2026-03-28
Status: planning artifact only. Not a CDL. Does not pre-authorize execution or amend any
active sequence lock.

Purpose: formalize the validator enhancement proposals identified during the Phase 479 genesis
validator governance dialogue. Records the current function inventory, identified gaps, proposed
CDL lanes, and window assignment candidates so these improvements enter the canonical planning
record and are not lost between windows.

---

## 1. Context and motivation

The genesis validator bootstrap specification (Phase 479) defines the signing key format,
enrollment record structure, and epoch-zero state for ILC's seven genesis validators. That
work revealed a material gap: the validator node is performing essential but narrow
infrastructure work while several high-value functions — economic enforcement, staking,
incentive distribution, and governance surface exposure — remain unimplemented and
constitutionally unspecified.

This roadmap formalizes those gaps and proposes the CDL lanes and simulation studies required
to close them before broad network launch.

---

## 2. Current validator function inventory

The following functions are constitutionally locked and implemented as of Phase 479.

| Function | Runtime file | CDL authority |
|---|---|---|
| Epoch finality attestation signing | `ilc_core/consensus/finality_evaluator.py` | CDL-051 |
| CDL-V3 diversity floor enforcement | `ilc_core/consensus/finality_evaluator.py` + `diversity_floor_runtime.py` | CDL-051 + CDL-V3 |
| Deterministic fork resolution | `ilc_core/consensus/finality_evaluator.py` (`resolve_fork`, lexicographic minimum) | CDL-051 |
| CDL-045 circuit breaker quorum (implicit) | CDL-045 designates the CDL-V3 diversity quorum as the circuit breaker trigger authority | CDL-045 |

The validator does NOT currently perform any of the following:

- receive any economic reward for attestation work,
- hold a stake subject to slash or release on liveness failure,
- participate in ECU→ILC epoch-boundary conversion enforcement,
- gate admission control (CDL-040) events,
- witness shard merge/split decisions (CDL-041),
- exercise the CDL-045 circuit breaker authority through any explicit interface,
- receive a trust-tier elevation for validator participation.

---

## 3. Identified gaps and enhancement proposals

### 3.1 Economic incentive gap (PRIORITY: HIGH)

**Gap:** no positive reward mechanism exists for running a validator. The only current
economic coupling is the negative one — CDL-046's `RECOVERY_POLICY = "stake_full_release"`
governs timed-out knowledge *claims*, not validator participation. A validator that signs
every epoch faithfully earns nothing beyond implicit governance authority.

**Consequence:** for a seven-node genesis cohort this is acceptable. For a broader network,
the absence of a positive reward creates a long-term participation collapse risk — rational
agents will not run validator infrastructure if it has no return.

**Proposed lane:** Validator Economic Incentive Framework CDL. Core design direction:

- a fraction of per-epoch write-fee-burn (currently routed to CDL-047 treasury) is instead
  routed to a validator reward pool,
- the pool is split proportionally to attestations signed per epoch per validator,
- reward rate is governed by the CDL-047 treasury framework (no new treasury primitive needed),
- requires SIM-010 to size the allocation fraction before constitutional lock.

The CDL-047 treasury framework already provides the governed allocation surface. This CDL
extends it with a validator-directed disbursement lane, not a new economic primitive.

### 3.2 Validator staking and liveness enforcement gap (PRIORITY: HIGH)

**Gap:** there is no validator-specific staking mechanism. CDL-046 handles claim orphan
timeouts (`ORPHAN_TIMEOUT_EPOCHS = 4`, `stake_full_release`), but this governs node
*content claims*, not the validator's own participation stake. A validator that goes offline
imposes a collective harm (quorum degrades toward `provisional`) but faces no individual
consequence.

**Proposed lane:** Validator Staking and Liveness Enforcement CDL. Core design direction:

- each genesis validator holds a staking entry at enrollment time (amount governance-defined,
  sized by SIM-010),
- validators that miss more than a governance-defined threshold of consecutive epochs have
  their stake partially slashed (not fully released — full release is an admission-exit
  mechanism, not a liveness penalty),
- equivocation (signing two conflicting `block_hash` values for the same epoch) triggers
  a full stake slash,
- liveness recovery: a slashed validator can re-stake via a CDL-V4-governed re-admission
  process,
- this CDL is a constitutional amendment to CDL-046, extending it from content-claim orphans
  to validator-node liveness enforcement.

Note: this CDL must be sequenced AFTER the Validator Economic Incentive Framework CDL, since
the stake amount must be sized relative to the reward rate.

### 3.3 Circuit breaker surface gap (PRIORITY: MEDIUM)

**Gap:** CDL-045 designates the CDL-V3 diversity quorum as the circuit breaker trigger
authority. The validators ARE that quorum. But no interface exists for validators to
explicitly exercise this authority. The circuit breaker currently has no activation surface
— it is governed law without a practical mechanism.

**Resolution path:** this does not require a new CDL. It requires a Phase implementation:
a `circuit_breaker_interface.py` under `ilc_core/consensus/` that surfaces the CDL-045
authority to the validator quorum. The Phase 479+ genesis validator tooling (under `tools/`)
is the natural place to first expose this. Estimated: one Phase, Window 485+.

### 3.4 Epoch boundary economic enforcement gap (PRIORITY: MEDIUM)

**Gap:** the ECU→ILC conversion (CDL-030, P_e clamp [0.75, 1.30]) happens at epoch
boundaries driven by the same epoch clock as validator finality attestations. These two
events are currently completely disconnected: the validator signs the epoch, but the
conversion logic does not require or use validator sign-off.

**Proposed design direction:** validators could serve as *epoch-boundary witnesses* for
ECU→ILC conversion batches — the conversion event would record the `canonical_block_hash`
from the epoch's finality attestation, cryptographically anchoring conversions to the
validator quorum's consensus. This is a provenance improvement, not a gating one (validators
cannot block conversions, only attest to the epoch state in which they occurred).

This may or may not require a CDL amendment to CDL-030 or CDL-051. Scoping is deferred
to SIM-010 analysis and a dedicated architectural review phase.

### 3.5 Trust-tier elevation gap (PRIORITY: MEDIUM)

**Gap:** running a validator node provides no benefit to the agent's epistemic standing in
the 7+1 evaluation panel (ADM-001 v0.2). The L-tier quorum ladder (L0=3, L1=5, L2=7, L3=9)
is tied to epistemic quality alone. A genesis validator who contributes infrastructure work
earns no additional weight in governance proceedings.

**Proposed lane:** Validator Trust-Tier Elevation CDL (or ADM-001 amendment). Core direction:

- active validators receive a non-inheritable trust-tier elevation flag that is visible in
  7+1 panel composition,
- the elevation does not increase L-tier quorum requirements (those remain quality-anchored),
  but validators receive a tiebreaker advantage or a dedicated panel seat in disputes
  touching consensus-layer decisions,
- the elevation is contingent on active validator status (liveness threshold met); validators
  who miss the liveness threshold lose the elevation flag.

This requires an ADM-001 v0.3 amendment and possibly a new CDL, depending on whether the
trust-tier elevation constitutes a constitutional change. Governance boundary analysis
required before opening.

### 3.6 Optional validator co-location protocol gap (PRIORITY: LOW)

**Gap:** Phase 479 mandates the keypair offset pattern across independent machines for
genesis. This is correct and must not change for genesis. However, for non-genesis network
participants who wish to run a full node (consensus + epistemic layers on the same machine),
no constitutional guidance exists.

**Proposed lane:** Optional Validator Co-location Protocol CDL. Core direction:

- defines a `full_node` registration type for non-genesis participants,
- co-location is opt-in and non-default,
- co-located nodes are excluded from the genesis validator quorum (cannot hold a genesis
  validator_id),
- CDL-V3 diversity floor applies: no single machine-type or hosting provider can exceed
  the max_cluster_share_ceiling for co-located nodes in any governance quorum,
- private key isolation requirements between the consensus signing context and the LLM/agent
  context are specified (hardware key store or process boundary),
- this CDL does NOT modify the Phase 479 genesis validator enrollment constraints.

Timing: post-genesis launch, Window 495+. This is the lowest priority enhancement.

---

## 4. Proposed CDL lanes summary

| Proposed lane | Priority | CDL type | Dependencies | Timing candidate |
|---|---|---|---|---|
| Validator Economic Incentive Framework | HIGH | New CDL | SIM-010 | Window 485–494 |
| Validator Staking and Liveness Enforcement | HIGH | CDL-046 amendment | Validator Economic CDL (for stake sizing) | Window 485–494 |
| Validator Trust-Tier Elevation | MEDIUM | ADM-001 amendment + possible new CDL | Staking CDL (for liveness threshold) | Window 495–504 |
| Optional Validator Co-location Protocol | LOW | New CDL | Post-genesis launch | Window 495+ |

The circuit breaker surface (§3.3) resolves as a Phase implementation in Window 485, not
a CDL.

The epoch boundary economic enforcement (§3.4) requires a scoping phase before a CDL
category can be assigned.

---

## 5. Proposed simulation study: SIM-010

**Name:** Validator Incentive Economics

**Purpose:** size the validator reward pool fraction and staking amount before either is
constitutionally locked. This prevents arbitrary or non-evidence-based parameter choices.

**Scenarios:**

1. Reward fraction scan: 0.5%–5% of per-epoch write-fee-burn routed to validator pool.
   Measure: reward rate per validator per epoch at various network sizes (N_agents = 10k,
   50k, 200k). Goal: confirm reward is meaningful at minimum viable network scale.

2. Staking sizing: stake amount = K × expected_epoch_reward, K ∈ {10, 25, 50, 100}.
   Measure: time-to-payback after a slash event. Goal: confirm the stake is a credible
   deterrent without being a prohibitive barrier to participation.

3. Liveness threshold sensitivity: miss-streak thresholds ∈ {4, 8, 16} epochs before
   partial slash. Measure: effect on quorum availability when one validator machine fails.
   Goal: threshold must be long enough to survive hardware failure without triggering slash,
   short enough to deter deliberate non-participation.

4. Participation equilibrium: model the network at 7, 25, and 100 active validators.
   Measure: whether the reward pool naturally induces validator participation at each scale,
   or whether additional incentives (trust-tier elevation, governance authority) are required.

**Output required before Validator Economic Incentive Framework CDL opens:**

- `recommended_validator_reward_fraction` (write-fee-burn routing percentage),
- `recommended_genesis_stake_amount` (in ECU-equivalent),
- `recommended_liveness_miss_threshold` (consecutive epochs before partial slash),
- at least one scenario showing reward remains meaningful at N_agents = 10,000 (minimum
  viable network per SIM-001 evidence).

---

## 6. Window assignment candidates

| Window candidate | Primary work |
|---|---|
| Window 475–484 | Genesis validator bootstrap spec (Phase 479), validator enrollment runtime, and admission bundle enforcement (Phases 479–481). Completed window; validator enhancements remained OUT OF SCOPE. |
| Window 485–494 | SIM-010 execution + circuit breaker surface implementation + Validator Economic Incentive Framework CDL opening + Staking and Liveness CDL opening |
| Window 495–504 | Validator Trust-Tier Elevation CDL + epoch boundary economic enforcement scoping |
| Window 505+ | Optional co-location CDL (post-genesis launch) |

Planning rule: no validator enhancement CDL should open before a future Window 485–494
sequence lock exists, and no CDL should open before its SIM-010 pass criteria are
satisfied.

---

## 7. Dependencies and constraints

1. **Phase 479 must complete unmodified.** This roadmap does not alter the Phase 479 prompt
   or scope. The genesis bootstrap specification is complete as designed.

2. **CDL-053 is reserved for Werner credit architecture** (bounded authorization / issuance
   discipline). Validator enhancement CDLs are architecturally distinct and must not be
   folded into CDL-053. They open in the CDL-05X range following CDL-053.

3. **SIM-010 gates the economic CDLs.** Neither the Validator Economic Incentive Framework
   nor the Staking and Liveness CDL may be ratified without SIM-010 evidence passing the
   output criteria in §5.

4. **CDL-V3 diversity floor applies to all validator quorum expansions.** Any expansion
   beyond the genesis cohort must satisfy the cluster diversity floor and max_cluster_share
   ceiling before the new validators are admitted to the signing quorum.

5. **Phase 479 genesis constraints are permanent for genesis validators.** The keypair
   offset pattern (no single machine holds all keys for any cluster) and the no-co-location
   requirement apply to the seven genesis validator_ids permanently. Non-genesis validators
   are subject to the Optional Co-location CDL once it is ratified.

---

## 8. Explicit out-of-scope items

The following are NOT addressed by this roadmap and must remain in their existing planning
lanes:

- Werner credit architecture / CDL-053 (separate lane, see
  `docs/specs/ilc_window_469_plus_cdl_053_and_long_tail_research_placeholder_v0.1.md`),
- long-tail post-issuance economics / LT-0 through LT-4 research track (separate),
- biometric or proof-of-personhood credential for validators (CDL-V2 Phase 331 confirmed
  rejection; not revisited here),
- threshold signature schemes (out of scope per Phase 479; deferred to future lane),
- validator network join and recovery flow (out of scope per Phase 479; separate planning
  required),
- CDL-045 constitutional text changes (circuit breaker authority already established;
  only surface implementation is needed, not a CDL).

---

## 9. Carry-forward obligation

Future window planning artifacts (grouping documents, sequence locks, and capsule updates)
must explicitly disposition this roadmap as one of:

- deferred,
- partially activated,
- opened (with specific CDL opening phase assigned).

The minimum dispositions required at each next window grouping are:

- Window 485–494 grouping: disposition SIM-010 and Validator Economic Incentive Framework CDL,
- Window 495–504 grouping: disposition Staking/Liveness CDL and Trust-Tier Elevation CDL,
- The next capsule refresh after v2.2: reference this roadmap explicitly as a standing
  forward obligation under the validator infrastructure heading.
