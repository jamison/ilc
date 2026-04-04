# ILC Phase 585 Genesis Authority and Sunset Dependency Note v0.1

Status: dependency note for Window 585-594 planning
Date: 2026-04-03
Owner lane: RC0.1+ public-release constitutional closure

## 1. Purpose

This note distills the Genesis authority and sunset context needed for the
Phase 585+ public-release lane.

It separates:
- binding canonical surfaces that Phase 585+ must obey,
- supporting but not fully ratified context that may inform design,
- carry-forward items that must return to canon before or during the public
  release-candidate lane.

This note does not ratify new protocol law. It is a dependency note for Window
585-594 planning and later phase prompts.

## 2. Binding canonical synthesis

### 2.1 Genesis is a bounded bootstrapping necessity, not informal founder discretion

The binding canon already establishes that Genesis is a special bootstrap role,
but not an unlimited one.

Binding anchors:
- `docs/specs/ilc_constitutional_decision_log_v0.1.md` (`CDL-001`, `CDL-002`,
  `CDL-003`, `CDL-004`, `CDL-007`, `CDL-013`, `CDL-V6`, `CDL-022`,
  `CDL-023`, `CDL-040`, `CDL-042`, `CDL-045`)
- `docs/specs/ilc_cdl_v6_genesis_intervention_protocol_ratification_evidence_334_v0.1.md`
- `docs/adr/ADR_0006_EVE_Canonical_Capsule_Integrity.md`
- `docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`

Synthesis:
- Genesis is allowed as a special role because a network cannot govern its own
  initialization before it exists.
- That authority is constitutionalized and bounded.
- Genesis authority in the public-release lane must never be described as
  informal founder discretion.

### 2.2 Ordinary governance and extraordinary Genesis intervention are distinct

`CDL-V6` is ratified as narrow extraordinary authority only.

Binding constraints:
- Genesis intervention is limited to capture, constitutional violation, or
  time-critical emergency.
- Genesis intervention may not bypass ordinary `CDL-V4` reopening.
- Every invocation requires an audit record.
- Every invocation requires post hoc `CDL-V4` review once ordinary governance is
  available.
- `CDL-V6` is not a general parallel path for ordinary governance.

This boundary is mandatory for Window 585-594.

### 2.3 Genesis authority is paired with recession mechanisms

The binding public-release posture is not perpetual founder privilege.

Binding recession mechanisms already exist in canon:
- `CDL-003`: trigger-based founder fade-out mechanics
- `CDL-004`: hard founder operational caps plus public reporting
- `CDL-013`: non-Genesis decay plus globally normalized voting share
- `CDL-V6`: sunset and challenge criteria for extraordinary intervention
- `CDL-045`: emergency circuit-breaker path with `CDL-V6` sunset and `CDL-V4`
  post hoc review

Phase 585+ must preserve this pattern:
- Genesis may be special enough to bootstrap the canonical network,
- but not special enough to become indefinite hidden sovereign authority.

### 2.4 Genesis is the canonical self-anchor for public legitimacy lineage

`ADR-0027` now makes the key public-release architectural move explicit.

Binding claim:
- Genesis-signed bootstrap artifacts are the recursive self-anchors that bind
  early network identity, early economic activation, and consensus bootstrap
  into one canonical artifact lineage.
- Later governance must extend the same lineage rather than replacing it with an
  unrelated foundation.

This means the public-release lane should treat a different Genesis root as a
non-canonical network, not as the same public ILC network with optional
configuration changes.

### 2.5 Fork consequence is architectural, not rhetorical

For public release, removing the Genesis-rooted legitimacy lineage or the
ledger-backed public authority chain must produce a different network.

That consequence should flow through:
- public identity activation,
- public namespace authority,
- public quorum eligibility,
- settlement-linked public legitimacy,
- public reputation continuity.

## 3. Supporting context that is not equal canon

The following sources are useful context for Phase 585+, but they are not all
binding law at the same level as ratified CDLs or accepted ADRs.

### 3.1 Supporting but not fully ratified sources

- `docs/adr/ADR_0008_Node_Usefulness_vs_Governance_Weight_and_Genesis_Dilution.md`
  - status: `Proposed`
  - useful for Genesis dilution framing and emergency-path posture
  - not sufficient by itself as binding public-release law

- `docs/specs/ilc_freshness_gate_contract_v0.1.md`
  - status: `Draft`
  - useful for Genesis freshness exemption and scoring posture
  - not yet sufficient as public-release governance closure by itself

- `docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.1.md`
  - status: analysis
  - useful for taper-governor interpretation and economic sunset trajectory
  - not protocol law by itself

### 3.2 Supporting rationale and planning context

- `whitepaper/02_design_principles.md`
  - useful for the Topological Exemption rationale
  - not a substitute for ratified protocol law

- `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md`
  - useful for the separate post-Genesis capability-proof roadmap
  - not current public-release law and not a substitute for Genesis
    governance/accrual closure in Window 585-594

- `docs/specs/ilc_epistemological_foundations_canonical_v0.1.md`
  - useful for Genesis-as-oracle reasoning and bootstrap necessity framing
  - should be treated as explanatory context, not direct authority for public
    release semantics

- `docs/specs/ilc_remaining_vulnerability_mechanisms_plan_v0.1.md`
  - useful for forward planning and vulnerability mapping
  - not direct authority for public legitimacy

- `docs/specs/ilc_constitutional_context_audit_v0.1.md`
  - useful as an audit and provenance warning surface
  - not a replacement for ratified closure artifacts

## 4. Public-release dependency consequences

Window 585-594 must preserve the following dependency statements:
- Genesis specialness is justified only by bootstrap necessity and canonical
  lineage continuity.
- Public legitimacy must not collapse back into founder discretion.
- Genesis recession mechanisms are mandatory, not optional.
- Canonical public identity and settlement legitimacy must remain traceable to
  the same Genesis-rooted artifact lineage described in `ADR-0027`.

## 5. Carry-forward canon queue for non-equal-canon gaps

The following items should be treated as explicit return points in canon.

Priority discipline:
- `TODO-P585-02`, `TODO-P585-03`, and `TODO-P585-04` are the highest-priority
  Genesis-return items because they govern Genesis governance dilution,
  Genesis freshness privilege, and Genesis ILC generation/accrual fade-away
  semantics.
- The capability-proof roadmap is a separate future lane. It should be tracked
  explicitly, but it must not be allowed to displace the higher-priority
  Genesis governance/accrual closures in this window.

### TODO-P585-01 - Receipt representation CDL cluster

Before Phase 585 execution locks, open and close the CDL or tight CDL cluster
for:
- public identity activation receipts,
- public quorum eligibility receipts/proofs,
- settlement-linked public legitimacy receipts,
- and the disposition of public namespace authority receipts.

### TODO-P585-02 - Genesis governance dilution closure

Return the remaining Genesis-governance questions that sit partly in
`ADR-0008` into a ratifiable vehicle.

At minimum, the public-release lane should explicitly dispose of:
- transition-only suspensive Genesis brake semantics,
- hard bounds for any Genesis governance baseline or contribution bonus,
- the exact relationship between `CDL-013` global normalization and any future
  Genesis-specific governance guardrail.

### TODO-P585-03 - Freshness-gate provenance and Genesis exemption closure

Return the Genesis freshness exemption and decay-vs-reuse provenance gap to
canon.

At minimum, resolve whether the current `genesis_exempt = true` posture is:
- ratified as-is,
- ratified with evidence supplement,
- or reopened through a dedicated decision-log vehicle.

This should also close the known `CFR-002` decay-vs-reuse-persistence context
gap documented in `docs/specs/ilc_constitutional_context_audit_v0.1.md`.

### TODO-P585-04 - Genesis accrual governor provenance reconciliation

Return the accumulation-governor provenance gap to canon.

At minimum, reconcile:
- `CDL-003` fade-out mechanics,
- `CDL-004` founder caps,
- `CDL-026` / `CDL-027` / `CDL-029` / `CDL-030`,
- and the Phase-218/298 taper-governor interpretation,

so the public-release lane does not rely on unexamined analysis artifacts when
stating Genesis sunset semantics.

### TODO-P585-05 - Topological Exemption usage boundary

Keep the Topological Exemption as a rationale and explanatory anchor unless and
until a ratified artifact explicitly elevates it into more direct protocol law.

Do not use the whitepaper phrase by itself as a substitute for the ratified
CDL/ADR stack.

### Related future lane - TODO-P585-07 Post-Genesis capability-proof disposition

`docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md` must remain supporting
context only until a later ratified vehicle explicitly dispositions the lane.

At minimum, the later vehicle should dispose of:
- the explicit rule that CapProof does not directly mint additional `ILC`,
- the bounded Genesis role as an epoch-0 or bootstrap-only capability baseline,
- the transition from Genesis baseline to a non-privileged reference,
- and the post-Genesis sequencing `CapProof -> AWP/IIH -> optional QATPS/CIT`.

This is a real future lane, but it is not a blocker for Phases `585-590`
unless it is misread as already-ratified public-release law.

## 6. Required references for later phase documents

Any Phase 585-594 prompt/spec/walkthrough that touches Genesis authority,
bootstrapping, governance recession, or public legitimacy should cite at least:
- this dependency note,
- `docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`,
- `docs/research/ilc_cryptographic_economic_coupling_memo_v0.1.md`,
- `docs/research/ilc_canonical_self_describing_bootstrap_and_receipt_boundary_note_v0.1.md`,
- the relevant `CDL` rows and evidence artifacts from
  `docs/specs/ilc_constitutional_decision_log_v0.1.md`.

Where non-equal-canon sources are used, the document must explicitly distinguish
between:
- binding canon,
- supporting context,
- and unresolved carry-forward items.

## 7. Related references

- `docs/adr/ADR_0006_EVE_Canonical_Capsule_Integrity.md`
- `docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`
- `docs/research/ilc_cryptographic_economic_coupling_memo_v0.1.md`
- `docs/research/ilc_canonical_self_describing_bootstrap_and_receipt_boundary_note_v0.1.md`
- `docs/research/ilc_rc_phase_575_execution_packets_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
