# ILC Window 596-605 Candidate Phase Grouping v0.1

Status: candidate phase grouping - pre-sequence-lock
Date: 2026-04-05
Owner lane: G8 Genesis carry-forward canon closure

This document defines the candidate guidance window for the first post-595 lane.

Window 596-605 should be ambitious. It should attempt to close the entire
remaining Genesis carry-forward canon cluster in one window rather than letting
Genesis governance, Genesis centrality/fade-away semantics, Genesis ILC
generation/accrual sunset semantics, and the post-Genesis capability-proof lane
continue to drift as supporting context.

Window 596-605 is not a generic continuation of the RC0.1 runtime lane. Phase
595 already closed the bounded RC0.1 Strike Force bite. This window exists to
turn the remaining Genesis carry-forward queue into explicit canon or explicit
later-lane deferments.

---

## 1. Window purpose

Window 596-605 exists to close the remaining Genesis support-canon cluster left
explicitly open by Phases 590, 594, and 595.

This window must:
- preserve the frozen public-release boundary from Phases 585-594,
- preserve the bounded RC0.1 closure achieved in Phase 595,
- close the remaining Genesis governance, freshness, accrual, and bootstrap
  transition questions through ratified or explicitly dispositioned vehicles,
- produce a coherent public statement of Genesis fade-away, Genesis ILC
  generation/accrual limits, and Genesis bootstrap-only specialness,
- and leave the repository ready for either later implementation planning or a
  narrower public-release packaging lane without silent Genesis ambiguity.

This window must not:
- reopen the public identity/quorum/settlement/fork boundaries already frozen in
  Phases 587-590,
- treat Phase 595 bounded RC0.1 evidence as authority to settle Genesis canon by
  implication,
- silently treat supporting-context Genesis artifacts as equal canon,
- or mix unrelated transport, harness, onboarding, payment-ingress, or product
  work into Genesis carry-forward closure.

---

## 2. Mandatory dependency bundle

Every Phase 596-605 prompt, spec, walkthrough, and test-backfill artifact must
carry the following dependency bundle explicitly.

This guidance document is itself a mandatory reference for every Phase 596-605
artifact.

### 2.1 Binding canon bundle

These references are mandatory and should be treated as binding surfaces for the
window:
- `docs/specs/ilc_window_596_605_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md`
- `docs/specs/ilc_genesis_authority_sunset_and_fork_legitimacy_coherence_lock_590_v0.1.md`
- `docs/specs/ilc_window_585_594_handoff_594_v0.1.md`
- `docs/specs/ilc_rc0_1_strike_force_consolidation_and_runtime_hardening_595_v0.1.md`
- `docs/specs/ilc_integration_coherence_report_593_v0.1.md`
- `docs/adr/ADR_0006_EVE_Canonical_Capsule_Integrity.md`
- `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md`
- `docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`
- `docs/research/ilc_cryptographic_economic_coupling_memo_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

The relevant decision-log cluster for this window includes at minimum:
- `CDL-001`
- `CDL-003`
- `CDL-004`
- `CDL-013`
- `CDL-019`
- `CDL-022`
- `CDL-023`
- `CDL-026`
- `CDL-027`
- `CDL-029`
- `CDL-030`
- `CDL-031`
- `CDL-045`
- `CDL-V4`
- `CDL-V6`

### 2.2 Supporting context bundle

These references are not equal canon with the ratified CDL/accepted ADR layer,
but they are required context for this window and must be distinguished as such
when used:
- `docs/adr/ADR_0008_Node_Usefulness_vs_Governance_Weight_and_Genesis_Dilution.md`
- `docs/specs/ilc_freshness_gate_contract_v0.1.md`
- `docs/specs/ilc_genesis_accrual_governor_contract_v0.1.md`
- `docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.3.md`
- `docs/specs/ilc_genesis_accrual_reconciliation_8pct_vs_theta_hard_266_v0.1.md`
- `docs/specs/ilc_phase_305_genesis_accumulation_canonicalization_checklist_v0.1.md`
- `docs/specs/ilc_constitutional_context_audit_v0.1.md`
- `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md`
- `docs/specs/ilc_post_genesis_capability_proof_activation_sequence_230_239_v0.1.md`
- `docs/research/ilc_genesis_authority_and_sunset_canon_briefing_v0.1.md`
- `whitepaper/02_design_principles.md`

### 2.3 Reference discipline rule

Any Phase 596-605 document that cites the supporting context bundle must say
which statements are:
- binding canon,
- supporting context,
- analysis only,
- or unresolved carry-forward items.

No phase document in this window may treat the supporting context bundle as if
it were already fully ratified law for Genesis governance, Genesis centrality,
Genesis accrual, capability proofs, or public tokenomics.

---

## 3. Locked inheritance from Phases 585-595

The following points are already fixed before this window opens:
- the public identity, quorum, settlement, and canonical-vs-fork legitimacy
  boundaries from Phases 587-590 remain frozen,
- the public-runtime integration and public-claim honesty boundaries from
  Phases 591-594 remain frozen,
- the bounded RC0.1 runtime/testnet closure from Phase 595 remains frozen,
- the curated Genesis/testnet posture from Phase 578 remains RC0.1-only and may
  not be silently upgraded into public Genesis privilege,
- the Genesis carry-forward queue is explicit and must be closed or explicitly
  deferred rather than left implicit,
- supporting-context artifacts remain non-equal-canon unless a phase in this
  window explicitly ratifies or dispositions the relevant question,
- and inbound HTTP machine-payment ingress remains a separate later lane.

---

## 4. Pre-lock blockers for Window 596-605

This window should not sequence-lock or execute unless all of the following are
explicit.

### 4.1 Post-595 boundary preservation

The window must preserve:
- the Phase 590 Genesis authority/sunset/fork-legitimacy closure,
- the Phase 594 handoff and its explicit Genesis carry-forward queue,
- and the Phase 595 bounded RC0.1 Strike Force closure.

### 4.2 Explicit closure-vs-defer disposition discipline

Each Genesis carry-forward item in this window must end in exactly one of these
states:
- ratified/accepted closure,
- evidence-supplemented closure,
- or explicit later-lane defer with named reason and boundary.

### 4.3 Deterministic evidence rule

If simulation, economic trajectory evidence, or parameter-reconciliation work is
used in this window, it must be deterministic and reproducible. No phase may
rely on analysis claims alone where parameter closure or public tokenomics
language is being hardened.

### 4.4 No boundary widening by cleanup

This window may clarify Genesis carry-forward canon, but it must not:
- reopen the Phase 585-594 public-release law,
- reopen the Phase 595 bounded RC0.1 runtime lane,
- or smuggle unrelated inbound payment, harness/product, transport, or hostile-
  internet admission work into Genesis closure.

---

## 5. Carry-forward closure objectives

The ambition of Window 596-605 is to close the remaining Genesis support-canon
cluster in one ordered lane.

Priority discipline:
- Genesis governance dilution, Genesis freshness privilege, and Genesis
  generation/accrual fade-away semantics are the top-priority closure items.
- Capability-proof disposition is real and must be made explicit, but it must
  not displace the higher-priority Genesis governance/accrual questions.
- Public tokenomics and Topological Exemption language must be aligned to the
  ratified governor stack rather than treated as free-floating rhetoric.

The target closure set for this window is:
- Genesis governance dilution closure, including any bounded brake semantics or
  contribution-bonus guardrails,
- freshness-gate provenance and Genesis exemption closure,
- Genesis accrual-governor provenance reconciliation, including denominator mode
  and other parameter-provenance questions that affect honest public language,
- Genesis generation/vesting/accrual sunset semantics stated in a way that is
  consistent with founder caps, fade-out, and ratified issuance surfaces,
- post-Genesis capability-proof lane disposition and bootstrap transition
  boundary,
- Topological Exemption usage boundary,
- and a clean public tokenomics statement that matches the ratified governor and
  allocation surfaces instead of drift across analysis artifacts.

---

## 6. Candidate phase map

This is the candidate sketch only. The exact sequence may tighten at sequence
lock.

### 6.0 Execution strategy split

Window 596-605 should be split into two bands:
- Phases `597-602`: Genesis carry-forward closure and evidence band
- Phases `603-605`: synthesis, coherence, and closure band

Interpretation rule:
- Phases `597-602` should attempt to close the entire remaining Genesis support-
  canon cluster, not just one narrow item.
- Phases `603-605` should convert those closures into a clean public-facing and
  planning-facing state without reopening runtime or public-legitimacy law.

### Phase 596 - Window 596-605 sequence lock and dependency freeze

Purpose:
- freeze the Genesis carry-forward closure scope,
- freeze the dependency tiers,
- and refuse execution unless closure-vs-defer discipline and deterministic
  evidence rules are explicit.

### Phase 597 - Genesis governance dilution and brake-semantics closure

Purpose:
- close the remaining Genesis governance-dilution questions now living partly
  in `ADR-0008`,
- and make the Genesis fade-away/governance posture explicit without treating
  bootstrap specialness as permanent privilege.

### Phase 598 - Freshness-gate provenance and Genesis exemption closure

Purpose:
- disposition the `genesis_exempt = true` freshness posture,
- close the decay-vs-reuse provenance gap,
- and state the Genesis centrality/persistence boundary in canon rather than
  draft-only language.

### Phase 599 - Genesis accrual-governor provenance reconciliation

Purpose:
- reconcile the Genesis accrual-governor contract, reconciliation notes, and
  decision-log stack,
- and lock the authoritative provenance for Genesis ILC generation/accrual
  sunset semantics.

### Phase 600 - Deterministic Genesis economics evidence and parameter closure

Purpose:
- close any remaining denominator-mode, parameter-provenance, or multiplier-
  interaction questions that still require deterministic evidence,
- and produce an evidence-backed basis for honest Genesis/public tokenomics
  language.

### Phase 601 - Post-Genesis capability-proof disposition and bootstrap transition boundary

Purpose:
- disposition the capability-proof roadmap as a separate later lane,
- make the Genesis bootstrap baseline transition explicit,
- make any snapshot or fast-bootstrap provenance dependency under `CDL-023`
  explicit where the transition boundary depends on inherited bootstrap state,
- and forbid silent import of that lane into current governance, minting, or
  public-release claims.

### Phase 602 - Topological Exemption boundary and public tokenomics statement

Purpose:
- keep Topological Exemption at the correct legal tier,
- reconcile whitepaper language with the ratified issuance/governor stack,
- and publish a public tokenomics statement that does not overclaim beyond the
  ratified Genesis fade-away surfaces.

### Phase 603 - Genesis carry-forward synthesis and readiness-delta addendum

Purpose:
- synthesize the Genesis carry-forward closures from Phases 597-602,
- and update readiness/public-honesty-facing context so later planning no
  longer depends on stale Genesis ambiguity.

### Phase 604 - Coherence report and capsule v3.2

Purpose:
- record the Genesis carry-forward closure state,
- the surviving later-lane defers,
- and the next approved planning or implementation boundary.

### Phase 605 - Window 596-605 closure gate and handoff

Purpose:
- close the window only if the Genesis carry-forward queue has been explicitly
  closed or explicitly deferred,
- deterministic evidence claims are honest,
- and public/runtime boundaries remain preserved.

---

## 7. Protected boundaries and anti-pattern exclusions

This window must not:
- treat supporting-context Genesis artifacts as equal canon by silence,
- reopen the public identity/quorum/settlement/fork boundaries already frozen in
  Phases 587-590,
- reopen the bounded RC0.1 runtime/testnet surfaces already frozen in Phase 595,
- treat Genesis bootstrap necessity as authority for permanent public privilege,
- treat whitepaper Topological Exemption phrasing as self-executing law,
- silently import capability proofs into current governance or minting law,
- push inbound HTTP machine-payment ingress into Genesis carry-forward closure,
- or use harness/product work as a substitute for Genesis canon closure.

---

## 8. Relationship to existing artifacts

- `docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md`
- `docs/specs/ilc_genesis_authority_sunset_and_fork_legitimacy_coherence_lock_590_v0.1.md`
- `docs/specs/ilc_window_585_594_handoff_594_v0.1.md`
- `docs/specs/ilc_rc0_1_strike_force_consolidation_and_runtime_hardening_595_v0.1.md`
- `docs/specs/ilc_phase_305_genesis_accumulation_canonicalization_checklist_v0.1.md`
- `docs/specs/ilc_post_genesis_capability_proof_activation_sequence_230_239_v0.1.md`
- `docs/research/ilc_rc_phase_575_execution_packets_v0.1.md`
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.2.md`

---

## 9. Bottom line

Window 596-605 should be a concentrated Genesis carry-forward closure lane.

If it passes cleanly, the repository should no longer rely on scattered draft,
analysis, and supporting-context artifacts when speaking about:
- Genesis governance fade-away,
- Genesis centrality/reuse persistence boundaries,
- Genesis ILC generation/accrual sunset semantics,
- capability-proof bootstrap transition,
- or the legal tier of Topological Exemption and public tokenomics language.

This is the largest coherent remaining canon bite. It is the right next window.
