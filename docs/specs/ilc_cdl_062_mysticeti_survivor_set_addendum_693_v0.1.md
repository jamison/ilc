# ILC CDL-062 Research Lane Addendum 693 v0.1

Status: research lane addendum — survivor set update to Phase 692 handoff
Date: 2026-04-16
Phase: 693
Owner lane: G8 sovereign-substrate research (CDL-062)

`cdl_062_research_lane_addendum_693_complete`
`mysticeti_elevated_to_tier_1_primary`
`cometbft_deprioritized`
`ecu_owned_shared_object_split_defined`
`leaderless_dag_censorship_analysis_corrected`
`tla_plus_formal_verification_required_before_implementation_lane`

---

## 1. Purpose of this addendum

The Phase 692 handoff closed the Window 687-692 research lane with CometBFT
(standalone) as the Tier 1 primary implementation investigation target and
HotStuff/Jolteon as the Tier 1 secondary. This addendum records material
new analysis that emerged from a post-692 architectural review and corrects
the survivor set before the next implementation lane opens.

This addendum does not change:
- CDL-062 status: `open (research lane)` — unchanged
- Row states: unchanged
- The requirement that final Option-B selection requires completed spike work,
  row-5 mechanism proof, CDL-017 ratified, settlement-state CDL ratified,
  BAL calibration completed, and explicit human authorization

This addendum does change:
- The Tier 1 primary target: CometBFT → Mysticeti (leaderless DAG)
- The framing of the censorship analysis: corrected (see §3)
- The ECU settlement architecture: split into creation path and transfer path
- The formal verification requirement: TLA+ mandatory before implementation

---

## 2. The ECU creation / ECU transfer split

The Phase 692 handoff treated the settlement substrate as finalizing one
epoch settlement record per validation epoch (~1 minute). This was correct
for ECU attribution (creation) but incomplete for ECU transfers
post-creation.

The correct split is:

**ECU creation (epoch-gated, correctly slow):**
- The epistemic engine evaluates knowledge work over the epoch
- At epoch close, ECU attribution is calculated
- The epoch settlement record (including attribution batch) is submitted to the
  settlement substrate as a **shared-object transaction**
- Finality: 1-3 seconds, once per minute
- Shared-object path is appropriate — multiple validators must agree on one
  canonical epoch state root

**ECU transfer post-creation (block-level, must be fast):**
- An agent's ECU balance is an owned object
- A transfer from Agent A to Agent B requires no global consensus ordering —
  it touches only the owned objects of A and B
- Goes through the **owned-object fast path** (Byzantine Consistent Broadcast)
- Finality: < 500ms
- L3 applications require this speed to function correctly

This split is not achievable in any leader-based sequential pipeline. It
requires an object model that natively distinguishes owned-object and
shared-object semantics with different finality paths.

**Implication for substrate selection:**
CometBFT routes all transactions through a single sequential leader pipeline.
It cannot natively provide < 500ms finality for ECU transfers while also
handling shared epoch records. HotStuff/Jolteon is faster but has the same
structural limitation — it is a leader-based linear protocol. Neither can
natively express the owned/shared object split.

---

## 3. Corrected censorship analysis

The Phase 691 comparison analysis applied the DAG censorship concern too
broadly, treating all DAG-based systems under the same withholding attack
surface identified for Narwhal-Bullshark. This was incorrect.

There are two fundamentally different DAG architectures with different
censorship properties:

**Narwhal's DAG (the concern we correctly flagged):**
A validator can withhold certified batch certificates from its portion of the
DAG. If influential in the ordering, this can delay specific batches from
reaching the Bullshark ordering layer. This is the "practical exclusion"
concern under row-7.

**Mysticeti's DAG (different — and stronger on censorship):**
Each validator proposes blocks that reference blocks from all other validators.
A block is committed when it appears in the causal history of enough
subsequent validators' blocks. A censoring validator that refuses to reference
another validator's block is immediately detectable (its own blocks reflect
an incomplete view of the DAG), and other honest validators' blocks still
reference the excluded block, maintaining commitment through redundant paths.

**The inversion from Phase 691:**
Leaderless DAG protocols (Mysticeti, DAG-Rider) are potentially *more*
censorship resistant than the leader-based protocols we elevated to Tier 1,
not less. CometBFT's conditional row-7 pass — "censorship limited to one
leader rotation" — is a weaker guarantee than Mysticeti's, where censorship
requires corrupting a majority of the DAG's commitment paths simultaneously.

This corrects Gap 5 framing from Phase 692: the issue was not "DAG protocols
are risky on censorship" but "Narwhal specifically has a withholding surface
that does not apply to Mysticeti's commit architecture."

Gap 6 (HotStuff threshold-withholding analysis) remains open but is now
relevant only as a fallback analysis if Mysticeti extraction proves infeasible.

---

## 4. Updated survivor set

### Tier 1 — Primary implementation investigation target

**Mysticeti (sovereign, MIT licensed, mysticeti-core extraction)**

- ECU transfer finality (owned-object fast path): < 500ms
- ECU creation / epoch record finality (shared-object consensus path): 1-3s
- Finality semantics: deterministic — wave-based DAG commit rule
- Censorship resistance: strong — redundant causal history paths, detectable
  exclusion, no single leader to censor
- Row-7 exitability: strong — full DAG history reconstructible from public
  archive nodes
- Row-8 independence: pass — ILC governs its own validator set; the Mysticeti
  protocol is sovereign; the Sui network and Sui Foundation are not involved
- Row-5 compatibility: pass — no structural incompatibility with Phase 680
  near-term mechanism families
- Auditability: DAG commit structure verifiable via graph traversal; ILC must
  build a one-time verification CLI abstracting this for non-expert operators
  (satisfies Phase 679 observability budget with tooling investment)
- License: MIT — clean for sovereign deployment
- Implementation tractability: moderate — `mysticeti-core` crate is more
  separable than Aptos monorepo; main coupling is at application-layer boundary
  (transaction types, state machine) which ILC replaces entirely
- Production maturity: proven on Sui mainnet under real adversarial conditions

**Mandatory prerequisite before implementation lane opens:**
TLA+ formal verification of both:
1. Shared-object DAG commit path (row-7 censorship liveness bound)
2. Owned-object Byzantine Consistent Broadcast fast path (fast-path safety)

TLC model-check must pass on bounded model before any Rust implementation
begins. See §6.

### Tier 1 — Fallback if Mysticeti extraction proves infeasible

**Jolteon/HotStuff (standalone, no Aptos dependency)**

- ECU transfer finality: 1-2 seconds (no native owned-object fast path)
- Epoch record finality: 1-2 seconds
- Censorship resistance: conditional pass — threshold-withholding surface
  (Gap 6 from Phase 692) still requires formal analysis
- Auditability: BLS threshold signatures require more sophisticated tooling
  than Mysticeti's DAG graph traversal
- If Jolteon becomes primary: owned/shared object split must be simulated at
  the application layer rather than being native to the protocol

### Tier 2 — Theoretical foundation for future ILC-native consensus

**DAG-Rider (Keidar et al. 2021)**

- Formally proven: full asynchronous safety, optimal message complexity,
  provably censorship-resistant under honest majority
- No production implementation — research code only
- Appropriate as the formal specification basis for an eventual ILC-native
  consensus engine in a later lane
- The DAG-Rider paper is the reference for the TLA+ specifications in §6

### Deprioritized

**CometBFT (standalone)**
Leader-based sequential pipeline. Cannot natively provide < 500ms ECU
transfer finality. Deprioritized from Tier 1. May remain a reference for
ABCI boundary design patterns.

### Excluded (confirmed)

All exclusions from Phase 691 remain in force:
- External public L1s: row-6 + row-8
- External L2 rollups: row-6 + row-8
- Shared sequencer networks: row-6 + row-7 + row-8
- Appchain with external security: row-8 (standard config)
- Avalanche-native probabilistic: row-7 (probabilistic finality)

---

## 5. Python / Rust application boundary

ILC's epistemic engine is Python. Mysticeti's consensus engine will be Rust.
The boundary must be defined precisely to preserve sub-500ms ECU transfer
finality.

**Rust Mysticeti layer owns:**
- ECU owned-object balance state (LMDB)
- Owned-object transfer certificate protocol (fast path)
- Shared-object consensus path (epoch settlement records)
- Validator-to-validator DAG gossip (QUIC, CDL-061 aligned)
- BLS12-381 validator key management
- All write-path economic rules for ECU transfers encoded in Rust

**Python epistemic engine owns:**
- Knowledge graph state, scoring, attribution
- Epoch record computation (produces DAG-CBOR + CIDv1 epoch state root)
- Panel operations, agent lifecycle
- Submits epoch settlement records as shared-object transactions to Rust
- Queries ECU balances via gRPC (read path only — NOT in write critical path)

**The gRPC boundary is read-only from Python's perspective for ECU state.**
Python submits epoch records and reads balances. Python is never in the
write critical path for ECU transfers. Any gRPC round-trip that blocked
sub-500ms ECU transfer confirmation would defeat the fast path. The Rust
layer applies transfer logic autonomously, then Python observes the results.

**DAG-CBOR / CIDv1 integration point:**
Python computes the epoch state root using ILC's existing DAG-CBOR + CIDv1
canonical commitment format (Phase 14). The resulting CIDv1 hash is
submitted as the payload of a shared-object epoch settlement transaction.
No changes to ILC's DAG-CBOR format are required; the integration is in
the submission path.

---

## 6. TLA+ formal verification requirement

**Two specifications are required:**

### Spec A — Shared-object DAG consensus path

Verifies that Mysticeti's DAG commit rule satisfies row-7's censorship
liveness requirement: any vertex broadcast by an honest validator is
eventually committed despite Byzantine withholding.

Key elements:
- `CONSTANT ByzantineSet` — explicit Byzantine validator set (size ≤ F)
- `HonestValidators == Validators \ ByzantineSet`
- Byzantine validators modeled implicitly — they never broadcast (withholding)
- `AdvanceRound` requires 2f+1 honest validator broadcasts (Byzantine
  withholding cannot prevent round advancement under honest majority)
- Wave-based commit rule: vertex commits when it appears in causal history
  of 2f+1 honest validators in two subsequent rounds
- **Safety**: no two honest-proposed vertices in same round conflict
- **Liveness** (Row-7): any honest-broadcast vertex eventually commits

Location: `docs/specs/tla/ilc_dag_censorship_bounds.tla`

### Spec B — Owned-object Byzantine Consistent Broadcast fast path

Verifies that the ECU transfer fast path satisfies safety:
no two conflicting transfers on the same ECU object can both be certified.

Key elements:
- Object ownership model: each ECU balance owned by one agent at a time
- Transfer certificate: 2f+1 validator acknowledgments
- **Safety**: at most one transfer per owned object can reach certificate
  threshold (conflicting transfers cannot both be certified)
- **Liveness**: a valid transfer from an honest submitter eventually
  receives 2f+1 acknowledgments

Location: `docs/specs/tla/ilc_ecu_fast_path_bcast.tla`

**TLC model check parameters:**
- N = 4 validators, F = 1 Byzantine (minimum for non-trivial BFT)
- MaxRound = 5 (sufficient for finding safety violations in bounded model)
- Model check must complete with no violation before implementation begins

---

## 7. Updated remaining gaps (supersedes Phase 692 §3)

| Gap | Status | Change from Phase 692 |
|---|---|---|
| Validator governance CDL (CDL-017) | Open — must ratify before first deployment | Unchanged |
| Settlement-state formal CDL | Open | Unchanged |
| BAL-weight calibration (Window 701-706) | Open | Unchanged |
| Row-5 mechanism proof over concrete substrate | Open — now over Mysticeti | Substrate changed from CometBFT |
| Narwhal-Bullshark DAG censorship analysis | **Closed** — not a Tier 1/2 target | Mysticeti selected instead |
| HotStuff threshold-withholding analysis | Demoted — fallback analysis only | Was Gap 6, now fallback-only |
| **TLA+ formal verification (both specs)** | **New — mandatory prerequisite** | Added by this addendum |
| **Mysticeti extraction feasibility spike** | **New — bounded, no production deployment** | Added by this addendum |

---

## 8. 693-700 window scope implications

The 693-700 window (originally scoped as "chosen-substrate legitimacy
mechanism and final remaining closures") now runs two parallel tracks:

**Constitutional / governance track:**
- Row-5 mechanism proof over Mysticeti concrete substrate model
- Row-7 validation: TLC results as formal censorship bound evidence
- Row-8 confirmation: Mysticeti sovereign configuration vs row-8 criteria
- CDL-017 opening stub and settlement-state formal CDL opening

**Implementation track (bounded spike — no production deployment):**
- TLA+ specs written and TLC clean (prerequisite gate for all below)
- `mysticeti-core` crate study: map all Sui-specific coupling points
- ILC type definitions: `ECUTransfer`, `ECUBalance`, `EpochSettlementRecord`
- Owned-object fast path prototype: LMDB ECU balance store + certificate
  protocol (no networking — local only)
- Scope limit: no production keys, no live validators, no persistent state
  beyond local test environments

`693_700_window_runs_constitutional_and_implementation_tracks_in_parallel`
`tla_plus_clean_is_gate_for_implementation_spike`
`spike_scope_bounded_no_production_deployment`

---

## 9. Minimum acceptable result for this addendum

- Corrected survivor set recorded before next lane opens: YES
- ECU creation / transfer split formally defined: YES
- Censorship analysis corrected: YES
- TLA+ requirement explicit: YES
- Python/Rust boundary defined: YES
- No constitutional locks changed without CDL process: YES
