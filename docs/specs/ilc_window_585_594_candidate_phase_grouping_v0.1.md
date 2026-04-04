# ILC Window 585-594 Candidate Phase Grouping v0.1

Status: candidate phase grouping - pre-sequence-lock
Date: 2026-04-03
Owner lane: RC0.1+ public-release constitutional closure

This document defines the candidate guidance window for the first public
release-candidate lane after the bounded RC0.1 testnet window.

Window 585-594 is not a generic continuation of Window 575-584. It is the first
explicit public-release constitutional and integration window. It must preserve
all RC0.1 testnet correctness boundaries while closing the missing public
legitimacy surfaces.

---

## 1. Window purpose

Window 585-594 exists to convert the bounded RC0.1 testnet into the first honest
public release-candidate evaluation lane.

This window must:
- preserve the RC0.1 runtime/economic correctness already established,
- close the public legitimacy boundaries around Genesis, identity, quorum,
  settlement, and minting,
- ensure the canonical public network is inseparable from its economic layer,
- and prevent any public-release claim from collapsing into founder discretion,
  silent Genesis privilege, or vague receipt semantics.

This window must not:
- silently treat testnet closure as equivalent to public-release closure,
- rely on analysis artifacts where ratified closure is required,
- or bury Genesis authority/sunset semantics inside implementation assumptions.

---

## 2. Mandatory dependency bundle

Every Phase 585-594 prompt, spec, walkthrough, and test-backfill artifact must
carry the following dependency bundle explicitly.

This guidance document is itself a mandatory reference for every Phase 585-594
artifact.

### 2.1 Binding canon bundle

These references are mandatory and should be treated as binding surfaces for the
window:
- `docs/specs/ilc_window_585_594_candidate_phase_grouping_v0.1.md`
- `docs/adr/ADR_0006_EVE_Canonical_Capsule_Integrity.md`
- `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md`
- `docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`
- `docs/research/ilc_cryptographic_economic_coupling_memo_v0.1.md`
- `docs/research/ilc_canonical_self_describing_bootstrap_and_receipt_boundary_note_v0.1.md`
- `docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md`
- `docs/research/ilc_rc_phase_575_execution_packets_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

The relevant decision-log cluster for this window includes at minimum:
- `CDL-001`
- `CDL-002`
- `CDL-003`
- `CDL-004`
- `CDL-007`
- `CDL-009`
- `CDL-013`
- `CDL-022`
- `CDL-023`
- `CDL-040`
- `CDL-042`
- `CDL-045`
- `CDL-V6`

### 2.2 Supporting context bundle

These references are not equal canon with the ratified CDL/accepted ADR layer,
but they are required context for this window and must be distinguished as such
when used:
- `docs/adr/ADR_0008_Node_Usefulness_vs_Governance_Weight_and_Genesis_Dilution.md`
- `docs/specs/ilc_freshness_gate_contract_v0.1.md`
- `docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.1.md`
- `docs/specs/ilc_constitutional_context_audit_v0.1.md`
- `docs/specs/ilc_epistemological_foundations_canonical_v0.1.md`
- `docs/specs/ilc_remaining_vulnerability_mechanisms_plan_v0.1.md`
- `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md`
- `whitepaper/02_design_principles.md`

### 2.3 Reference discipline rule

Any Phase 585-594 document that cites the supporting context bundle must say
which statements are:
- binding canon,
- supporting context,
- or unresolved carry-forward items.

No phase document in this window may treat the supporting context bundle as if
it were already fully ratified public-release law.

---

## 3. Public-release boundary decisions already locked

The following points are already fixed before this window opens:
- canonical public participation must become inseparable from the economic
  layer,
- Genesis-signed bootstrap artifacts are the recursive self-anchor for public
  legitimacy lineage,
- local/private use remains permitted outside public-release legitimacy,
- public-release coupling belongs at public authority boundaries rather than in
  every graph object,
- the protocol-vs-harness boundary from ADR-0026 remains in force,
- the wrong coupling shapes are already rejected:
  - transaction-hash-derived identity,
  - moving ledger root in every graph object,
  - poisoning reusable modules with token logic.

---

## 4. Pre-lock blockers for Window 585-594

This window must not sequence-lock or execute as public-release closure unless
all of the following are explicit.

### 4.1 Receipt representation cluster

A CDL or tight CDL cluster must lock the uniform representation discipline for
at minimum:
- public identity activation receipts,
- public quorum eligibility receipts/proofs,
- settlement-linked public legitimacy receipts,
- and the disposition of public namespace authority receipts.

### 4.2 Genesis authority and sunset dependency discipline

The window must preserve the dependency note in:
- `docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md`

That means:
- Genesis specialness is bootstrap-only and bounded,
- ordinary governance and `CDL-V6` extraordinary intervention remain distinct,
- recession mechanisms remain mandatory,
- public legitimacy must continue through Genesis-rooted canonical lineage.

### 4.3 Canonical-vs-fork public consequence

The window must make explicit that a different Genesis root or a stripped
public-legitimacy chain yields a different network, not an equivalent canonical
ILC public network.

### 4.4 Public operator honesty boundary

Any public-release candidate artifact produced in this window must explicitly
state what remains:
- non-mainnet-safe,
- curated or bounded,
- or still dependent on carry-forward constitutional closure.

---

## 5. Carry-forward canon queue (must return soon)

The following are explicit canon-return items for this window.

### TODO-P585-01 - Receipt representation CDL cluster

Open and close the public receipt-format cluster named in Section 4.1.

### TODO-P585-02 - Genesis governance dilution closure

Move the remaining Genesis-governance questions currently living partly in
`ADR-0008` into a ratifiable closure vehicle.

At minimum dispose of:
- transition-only suspensive Genesis brake semantics,
- hard bounds for any Genesis governance baseline or contribution bonus,
- the relationship between `CDL-013` and any future Genesis-specific governance
  guardrail.

### TODO-P585-03 - Freshness-gate provenance closure

Return the Genesis freshness exemption and decay-vs-reuse provenance gap into
canon. Resolve whether the Phase-217 / draft freshness posture is:
- ratified as-is,
- evidence-supplemented,
- or reopened through a dedicated vehicle.

### TODO-P585-04 - Genesis accrual governor provenance reconciliation

Return the Genesis accrual-governor provenance gap to canon so public-release
sunset semantics do not rely on unratified analysis alone.

### TODO-P585-05 - Namespace authority receipt disposition

Decide whether public namespace authority must carry its own first-class receipt
surface or whether it is fully derived from the public identity activation and
settlement receipt chain.

### TODO-P585-06 - Topological Exemption usage boundary

Keep the Topological Exemption as rationale unless and until a ratified artifact
promotes it further. Do not use whitepaper phrasing by itself as protocol law.

---

## 6. Candidate phase map

This is the candidate sketch only. The exact sequence may tighten at sequence
lock.

### Phase 585 - Window 585-594 sequence lock and dependency freeze

Purpose:
- freeze the public-release scope,
- freeze the mandatory dependency bundle,
- and refuse execution until the pre-lock blockers are explicit.

### Phase 586 - Receipt representation CDL cluster

Purpose:
- lock the public receipt/proof representation discipline required by ADR-0027
  and Packet 4.

### Phase 587 - Public identity activation and namespace authority boundary

Purpose:
- bind public identity activation to canonical admission/stake receipts,
- and dispose of public namespace authority receipt semantics.

### Phase 588 - Public quorum eligibility and Genesis-lineage authority boundary

Purpose:
- bind public 7+1 eligibility and later selection authority to the canonical
  public lineage and receipt chain.

### Phase 589 - Settlement-linked public legitimacy and payout traceability

Purpose:
- lock public legitimacy to settlement-linked receipts and payout traceability.

### Phase 590 - Genesis authority, sunset, and fork-legitimacy coherence lock

Purpose:
- make the Genesis authority/sunset posture and canonical-vs-fork consequence
  explicit in the public-release lane.

### Phase 591 - Public-runtime integration over the receipt boundary

Purpose:
- integrate the public receipt and legitimacy surfaces into the live runtime and
  proof lane without widening into unrelated product work.

### Phase 592 - Public release-claim and operator honesty package

Purpose:
- produce a public-release candidate package that states exactly what is and is
  not being claimed.

### Phase 593 - Coherence report and public-RC capsule update

Purpose:
- record the closure state of the public-release lane and its remaining carry-
  forward items.

### Phase 594 - Window closure gate and handoff

Purpose:
- close the window only if the public legitimacy boundary, Genesis authority
  boundary, and receipt-representation boundary are explicit and passed.

---

## 7. Protected boundaries and anti-pattern exclusions

This window must not:
- treat Genesis authority as informal founder discretion,
- treat supporting context artifacts as equal canon without explicit closure,
- reopen the protocol-vs-harness boundary,
- push QuotaMiner or onboarding UX into protocol closure work,
- embed a moving ledger root into every graph object,
- derive public identity from transaction hashes,
- treat RC0.1 testnet success as equivalent to public legitimacy closure.

---

## 8. Relationship to existing artifacts

- `docs/specs/ilc_window_575_584_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_phase_575_584_sequence_lock_v0.1.md`
- `docs/specs/ilc_post_586_strike_force_runtime_hardening_packet_v0.1.md`
- `docs/specs/ilc_post_582_harness_sdk_lane_v0.1.md`
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.2.md`
- `docs/research/ilc_rc_phase_575_execution_packets_v0.1.md`
- `docs/research/ilc_cryptographic_economic_coupling_memo_v0.1.md`
- `docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md`

---

## 9. Bottom line

Window 585-594 is the first public-release constitutional closure lane.

It should leave behind:
- an explicit Genesis authority and sunset boundary,
- a locked public receipt/proof representation discipline,
- public identity/quorum/settlement legitimacy bound to canonical lineage,
- and an honest public release-candidate package that does not overclaim.
