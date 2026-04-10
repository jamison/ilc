# ILC Window 607-612: Candidate Phase Grouping

**Author:** Codex (GPT-5) - local implementation reviewer
**Date:** 2026-04-10
**Baseline:** Window 596-605 CLOSED (`phase_605_verdict=pass`), Phase 606 MemPalace retrieval boundary landed, capsule `v3.2` active.
**Planning note:** This is a candidate grouping, not a locked sequence. Window 607-612 is a targeted settlement-substrate reconciliation lane and supersedes the broader `607-615` continuation draft unless and until this narrower issue is explicitly resolved.

## 1. Window identity and scope

Window 607-612 is not a generic continuation window.

It exists to resolve one high-leverage architectural ambiguity before broader
post-605 work continues:
- whether the current internal epoch-settled RC/runtime ledger is only a
  bounded interim posture,
- or whether the repo is implicitly drifting toward treating that posture as
  the permanent final settlement substrate for `ILC`.

This window should force a clean distinction between:
- `ECU` and the local/shard epistemic-economic machinery,
- the current RC/runtime ledger posture,
- and the unresolved long-run public settlement substrate for `ILC`.

This window must not:
- reopen the frozen 585-595 public and bounded-RC boundaries,
- assume that historical blockchain aspirations are already current canon,
- assume that current capsule wording fully settles the long-run substrate,
- or continue broader payment/wallet/public-release planning without first
  reconciling the settlement-substrate issue.

## 2. Baseline and inheritance

The current inherited baseline is:
- `docs/specs/ilc_window_596_605_handoff_605_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v3.2.md`
- `docs/phases/STATUS.md`
- `docs/research/ilc_rc_gap_context_pack_v0.1.md`
- `docs/specs/ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md`
- `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md`
- `docs/specs/ilc_rc0_1_ecu_settlement_wallet_query_integration_581_v0.1.md`
- `docs/adr/ADR_0013_External_Payment_Boundary_and_Third_Party_Independence.md`
- `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md`
- `docs/specs/ilc_mempalace_internal_retrieval_adoption_and_boundary_606_v0.1.md`
- `docs/specs/ilc_mempalace_operational_enablement_and_workflow_integration_606_fix1_v0.1.md`
- `docs/specs/ilc_mempalace_retrieval_correctness_and_manifest_hardening_606_fix2_v0.1.md`

Supporting historical/planning context for this lane includes:
- `whitepaper/2025_12_03_ILC_whitepaper_v5_2.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.4.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.5.md`
- `docs/specs/ilc_economic_architecture_comprehensive_v0.1.md`
- `docs/specs/ilc_topological_exemption_boundary_and_public_tokenomics_statement_602_v0.1.md`
- `docs/specs/ilc_agent_sdk_boundary_contract_draft_v0.1.md`
- `docs/specs/ilc_claude_extraction_brief_v0.1.md`

Inherited boundary rules:
- Window 596-605 left explicit later-lane defers rather than silent closure by
  implication.
- Current wallet/query posture remains read-only/accounting-only.
- External payment remains a perimeter concern under the current boundary.
- MemPalace retrieval may support drafting, but authority remains with current
  repo canon and direct source review.
- The broader `docs/specs/ilc_window_607_615_candidate_phase_grouping_v0.1.md`
  draft is superseded pending this reconciliation-first lane.

Next fresh CDL number:
- `CDL-062`

This candidate grouping does not pre-authorize any guaranteed CDL ratification.
If a constitutional vehicle is required, it should be selected explicitly in
Phase 611 rather than assumed at window entry.

## 3. Track inventory

### 3.1 Constitutionally obligated

- preserve the 585-595 frozen boundaries
- preserve the current read-only wallet/query boundary
- explicitly classify whether the current RC/runtime ledger posture is an
  interim bounded implementation or a long-run substrate decision
- explicitly separate `ECU` / local-graph economics from `ILC` public-settlement
  substrate questions
- close the window with a clear downstream replan

### 3.2 Deferred governance

- outbound payment implementation
- inbound payment runtime
- wallet write/transfer/withdrawal widening
- native escrow authorization
- public-chain implementation work

### 3.3 Simulation-conditional

- no simulation lane is pre-authorized in this window
- if the options matrix discovers a need for fresh evidence, it becomes a
  later-lane defer rather than silent scope widening inside 607-612

## 4. Historical lineage and authority-reconciliation lane

This window must explicitly reconcile four source layers:
- early historical option space (June 2025)
- off-chain-first / later-chain direction (December 2025)
- February 2026 capsule and wallet/signing boundary language
- current RC/runtime implementation surfaces

The goal is not to let historical desire override current canon.
The goal is to classify what was:
- exploratory,
- strategic direction,
- current boundary language,
- and current executable implementation reality.

## 5. ECU / ILC / runtime-boundary lane

This lane exists because `ECU` and `ILC` are being conflated.

This window should determine, explicitly:
- what belongs to `ECU` and the local/protocol-internal economic machinery,
- what belongs to `ILC` as the hard settlement asset,
- what is merely true of the current RC/runtime implementation,
- and what remains unresolved about final public settlement substrate.

This lane must also prevent a second conflation:
- public auditability is not identical to public identity exposure

## 6. Public-ledger substrate options lane

Phase 610 should produce an options and rejection matrix for at least:
- current internal-ledger posture becoming the permanent final substrate
- custom minimal L1
- external rollup / L2 settlement substrate
- abstract ledger interface with deferred final substrate choice

The point is not to choose by vibe.
The point is to force explicit tradeoffs and make the architectural decision
auditable.

## 7. Governance vehicle selection lane

This window should determine whether settlement-substrate reconciliation needs:
- a narrow architecture memo only,
- an ADR,
- a CDL opening stub,
- or a combined memo + governance vehicle path.

That selection should happen only after the historical and runtime layers are
explicitly reconciled.

## 8. CDL number assignments

| CDL | Title (candidate) | Decision digest anchor | Opening phase | Ratification phase |
|-----|-------------------|------------------------|---------------|-------------------|
| CDL-062 | Settlement substrate boundary and public-ledger posture (conditional) | `ecu_local_internal_layer_vs_ilc_public_settlement_substrate` | Phase 611 (conditional) | later window (conditional) |

Note:
- no fixed phase in this candidate grouping is pre-authorized to ratify a new
  CDL
- `CDL-062` is only a reserved candidate if Phase 611 concludes that the issue
  cannot be carried cleanly by architecture memo or ADR alone

## 9. Candidate phase table

| Order | Phase | Topic | Character | Sensitivity |
|---|---|---|---|---|
| 1 | 607 | Window 607-612 sequence lock and issue framing | Foundation / Constitutional | **SENSITIVE** |
| 2 | 608 | Historical lineage and authority audit | Governance review | NON-SENSITIVE |
| 3 | 609 | ECU / ILC / runtime-boundary reconciliation | Governance review | NON-SENSITIVE |
| 4 | 610 | Public-ledger substrate options and rejection matrix | Governance review | NON-SENSITIVE |
| 5 | 611 | Governance vehicle selection and prelock | Conditional | **conditional** |
| 6 | 612 | Closure synthesis and downstream replan | Gate | **SENSITIVE** |

### Conditional note on Phase 611

There are two admissible scenarios:

- **Scenario A — memo/ADR path only**
  - Phase 611 remains NON-SENSITIVE
  - no decision-log mutation occurs
  - output is prelock/governance routing only

- **Scenario B — constitutional vehicle required**
  - Phase 611 becomes **SENSITIVE**
  - a narrow opening stub for `CDL-062` may be authorized
  - no ratification occurs in this window

### Note on Phase 609 non-ratifying boundary

Phase 609 is where the lane must say, explicitly:
- what belongs to `ECU`
- what belongs to `ILC`
- what belongs only to the current RC/runtime substrate

It is a reconciliation artifact, not a runtime implementation or token launch.

## 10. Sensitivity classification

### SENSITIVE phases list

- `Phase 607` — structural sequence-lock boundary for the reconciliation window
- `Phase 612` — closure gate and downstream handoff/replan boundary

### NON-SENSITIVE phases list

- `Phase 608` — historical lineage and authority audit only
- `Phase 609` — reconciliation memo only
- `Phase 610` — options and rejection matrix only

### Conditional phases rule

Before executing `Phase 611`, confirm with the human whether the selected
scenario requires a formal constitutional opening stub.

If yes:
- require GO token and treat Phase 611 as **SENSITIVE**

If no:
- Phase 611 remains NON-SENSITIVE and no decision-log mutation occurs

### Pre-commit hook block

If Phase 611 opens a CDL, require:

`ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=611`

In the default Scenario A path, no hook is required because no decision-log
mutation occurs.

## 11. Scope notes for fixed phases

### Phase 607 - Window 607-612 sequence lock and issue framing

Sensitivity: **SENSITIVE**. GO token required by future execution prompt.

Deliverables:
- sequence-lock spec
- explicit issue-framing / non-goal freeze

Required content spec:
- state that the broader 607-615 continuation draft is superseded pending this
  narrower reconciliation-first lane
- preserve 585-595 frozen boundaries
- preserve current read-only wallet/query boundary

Test structure:
- sequence-lock contract tests
- no `ilc_core/` mutation
- no decision-log mutation

Commit subject:
- `docs(g8): phase 607 window 607-612 sequence lock`

### Phase 608 - Historical lineage and authority audit

Sensitivity: NON-SENSITIVE.

Deliverables:
- historical lineage audit
- authority-tier classification artifact

Required content spec:
- classify June 2025, December 2025, February 2026, and current runtime
  sources separately
- explicitly classify capsule `v0.4` / `v0.5` anti-blockchain wording as
  historical drift-carrier language rather than silently inherited closure
- explicitly classify Phase 602 public tokenomics language as a bounded
  current public-claims surface rather than final substrate closure
- do not let historical chats outrank current canon

Test structure:
- document/token checks
- source classification checks

Commit subject:
- `docs(g8): phase 608 settlement substrate lineage audit`

### Phase 609 - ECU / ILC / runtime-boundary reconciliation

Sensitivity: NON-SENSITIVE.

Deliverables:
- reconciliation memo
- explicit separation of ECU, ILC, and current runtime posture

Required content spec:
- current runtime is not allowed to settle the forever substrate by implication
- public auditability and public identity exposure must be treated separately
- the wording inconsistency in
  `docs/specs/ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md`
  (`The ILC coin (ECU) is protocol-native.`) must be treated as a known
  reconciliation target rather than stable authority

Test structure:
- reconciliation token checks
- forbidden-scope assertions

Commit subject:
- `docs(g8): phase 609 ecu ilc runtime boundary reconciliation`

### Phase 610 - Public-ledger substrate options and rejection matrix

Sensitivity: NON-SENSITIVE.

Deliverables:
- options matrix
- rejection rationale for discarded options

Required content spec:
- evaluate at minimum internal-ledger-final, custom minimal L1, rollup/L2, and
  deferred-substrate ledger-interface paths
- require each option to include an explicit keep/defer/reject rationale
- no implementation work or wallet widening

Test structure:
- options coverage checks
- rejection matrix completeness checks

Commit subject:
- `docs(g8): phase 610 public ledger substrate options matrix`

### Phase 611 - Governance vehicle selection and prelock

Sensitivity: conditional. Confirm scenario before execution.

Deliverables:
- governance vehicle selection memo
- optional ADR or CDL opening/prelock artifact depending on selected scenario

Required content spec:
- explain why memo-only, ADR, or CDL route is chosen
- do not ratify anything in this phase

Test structure:
- scenario-sensitive token checks
- mutation-scope checks if a constitutional opening path is selected

Commit subject:
- `docs(g8): phase 611 settlement substrate governance vehicle selection`

### Phase 612 - Closure synthesis and downstream replan

Sensitivity: **SENSITIVE**. GO token required by future execution prompt.

Deliverables:
- closure synthesis
- downstream replanning note / handoff

Required content spec:
- state whether broader post-605 planning may resume and under what substrate
  assumptions
- explicitly carry forward any unresolved governance route

Test structure:
- closure gate
- inherited selftest chain if prior closure gates are consumed

Commit subject:
- `docs(g8): phase 612 settlement substrate closure handoff`

## 12. Key dependencies and open questions

### Must-resolve at entry

- whether the broader 607-615 planning draft should remain in active planning
  status during this targeted lane (recommended: no)
- whether the settlement-substrate question is an ADR-level problem or a
  constitutional/CDL problem
- whether public adoption requirements imply a hard future public-ledger
  commitment for `ILC`

### Sequencing constraints

- 608 must precede 609
- 609 must precede 610
- 610 must precede 611
- 612 must not quietly restore the broader 607-615 continuation map without an
  explicit downstream replan statement

### Open questions

- Is the current internal epoch-settled ledger a bounded RC posture or a
  permanent substrate claim?
- Is `ECU` strictly local/protocol-internal while `ILC` remains the only
  candidate for later public settlement?
- What must be public for auditability and settlement legitimacy, and what must
  remain privacy-preserving?
- Does the architecture return to a ledger-interface/deferred-substrate model?

### Permanently deferred from this window

- outbound payment implementation
- inbound payment runtime
- wallet write/transfer/withdrawal widening
- native escrow authorization
- public-chain implementation
- DeFi / liquidity / node-market protocol work

## 13. Known patterns and technical constraints

### Novel patterns introduced this window

- first window whose primary purpose is settlement-substrate reconciliation
  rather than direct runtime or payment progress
- first explicit planning move to separate current RC/runtime truth from
  long-run `ILC` settlement-substrate choice

### Historical prelock hardening

If Phase 611 opens `CDL-062`, later ratification work must harden the opening
state against the original opening commit and not reason only from the latest
tree.

### Phantom edit guard

No `ilc_core/` runtime mutation is expected anywhere in this window.
Any attempt to drag runtime implementation into 607-612 should be treated as
scope breach.

### Closure gate selftest guard chain

If the closure gate for Phase 612 consumes the Phase 605 gate or inherited
equivalent, it must set:
- `ILC_PHASE_605_GATE_SELFTEST=1`

### MemPalace drafting discipline

MemPalace may support this window in two places:
- reconstructing the historical lineage stack under tiered authority
- drafting retrieval briefs for the candidate grouping and later phase prompts

But retrieved material must pass through:
- direct repo reads
- current authority-tier checks
- `docs/tools/mempalace/ilc_mempalace_logic_gate_profile_v0.1.md`

## 14. Non-goals and explicitly deferred items

- no payment implementation
- no wallet-authority opening
- no native escrow
- no native escrow authorization
- no chain implementation
- no public FAQ/oracle lane
- no collapse of ECU and ILC into one undifferentiated substrate discussion
- no assumption that public identity-linked artifacts must be fully exposed

## 15. Key canonical anchors for prompt drafting

- PRIMARY: `docs/specs/ilc_antigravity_context_capsule_v3.2.md`
- `docs/specs/ilc_window_596_605_handoff_605_v0.1.md`
- `docs/specs/ilc_phase_596_605_sequence_lock_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/phases/STATUS.md`
- `docs/research/ilc_rc_gap_context_pack_v0.1.md`
- `docs/specs/ilc_wallet_agnostic_signing_strategy_codex_handoff_v0.1.md`
- `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md`
- `docs/specs/ilc_rc0_1_ecu_settlement_wallet_query_integration_581_v0.1.md`
- `docs/specs/ilc_genesis_accrual_governor_provenance_reconciliation_599_v0.1.md`
- `docs/specs/ilc_deterministic_genesis_economics_evidence_and_parameter_closure_600_v0.1.md`
- `docs/specs/ilc_topological_exemption_boundary_and_public_tokenomics_statement_602_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.4.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.5.md`
- `docs/adr/ADR_0013_External_Payment_Boundary_and_Third_Party_Independence.md`
- `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md`
- `whitepaper/2025_12_03_ILC_whitepaper_v5_2.md`
- `docs/specs/ilc_window_607_612_candidate_phase_grouping_v0.1.md`
- For closure gate (Phase 612): all Phase 607-611 test files and artifacts.

### Optional MemPalace retrieval appendix

Advisory only. Direct repo reads remain authoritative.

Suggested tier-scoped queries:
- `off-chain first later custom minimal L1`
- `independent of any blockchain`
- `read-only wallet query boundary`
- `ecu circulates here as medium of exchange`
- `ledger interface vs hard bind`

Required retrieval-use filter:
- `docs/tools/mempalace/ilc_mempalace_logic_gate_profile_v0.1.md`

## 16. Rationale for single-window scope

1. The settlement-substrate ambiguity now blocks payment, wallet, and public
   RC planning more than any one implementation defer does.
2. The December 2025 off-chain-first / later-chain direction remains historically
   strong enough that it must be reconciled explicitly rather than ignored.
3. The February/March 2026 boundary language is useful for current runtime
   truth but too blunt to settle the long-run `ILC` substrate alone.
4. The window is narrow enough to close cleanly without dragging in runtime,
   payment, or chain implementation work.
5. Once this lane closes, the next broader window can continue on a clearer
   architectural basis.
