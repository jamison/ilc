# ILC Window 607-615: Candidate Phase Grouping

**Author:** Codex (GPT-5) - local implementation reviewer
**Date:** 2026-04-10
**Baseline:** Window 596-605 CLOSED (`phase_605_verdict=pass`), Phase 606 MemPalace retrieval-only boundary landed, capsule `v3.2` active.
**Planning note:** This is a candidate grouping, not a locked sequence. Phases 607-615 are the proposed single-window lane. No inbound payment runtime or wallet-authority widening is pre-authorized in this packet.

## 1. Window identity and scope

Window 607-615 is the first post-606 strategic planning window. It should not
be treated as a generic continuation of Window 596-605, and it should not
quietly revive the earlier over-broad payment map.

This window exists to do four bounded things:
- close the surviving `Phase 305 canonical output package` defer,
- land the lower-risk outbound HTTP machine-payment support lane at the
  perimeter only,
- force an explicit inbound payment boundary-selection step without pretending
  inbound runtime is already ready,
- and take the first post-RC operator hardening bite around mTLS posture and
  LMDB parameterization/observability.

This window must not:
- reopen the frozen 585-595 public and bounded-RC boundaries,
- treat wallet-agnostic signing as equivalent to wallet spend/transfer
  authority,
- collapse external perimeter payment adapters into native escrow or ledger
  writes,
- or import market-liquidity, node-market, or blockchain-migration work into
  the core protocol lane.

## 2. Baseline and inheritance

The current inherited baseline is:
- `docs/specs/ilc_window_596_605_handoff_605_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v3.2.md`
- `docs/phases/STATUS.md`
- `docs/research/ilc_rc_gap_context_pack_v0.1.md`
- `docs/specs/ilc_mempalace_internal_retrieval_adoption_and_boundary_606_v0.1.md`
- `docs/specs/ilc_mempalace_operational_enablement_and_workflow_integration_606_fix1_v0.1.md`
- `docs/specs/ilc_mempalace_retrieval_correctness_and_manifest_hardening_606_fix2_v0.1.md`

Inherited boundary rules:
- Window 596-605 closed the Genesis carry-forward closure band and left explicit
  later-lane defers rather than silent closure by implication.
- Inbound HTTP machine-payment ingress remains a separate later lane unless
  explicitly reopened by later work.
- Current wallet/query posture remains read-only/accounting-only.
- External payment remains a perimeter concern under the current boundary.
- MemPalace retrieval is available as advisory drafting support only.

Next fresh CDL number:
- `CDL-062`

This candidate grouping does not pre-authorize any guaranteed CDL ratification.
At most, it conditionally opens an inbound-boundary vehicle if Phase 612
concludes that a new formal decision-log lane is required.

## 3. Track inventory

### 3.1 Constitutionally obligated

- preserve the explicit later-lane defer for inbound payment ingress until a
  boundary-selection step says otherwise
- preserve the read-only wallet/query boundary
- carry forward the surviving `Phase 305 canonical output package` closure item
  into an explicit phase rather than letting it drift
- close the window with an explicit synthesis/handoff packet

### 3.2 Deferred governance

- inbound payment runtime semantics
- any wallet write/transfer/withdrawal widening
- any native escrow authorization
- any public-blockchain or external-token migration posture

### 3.3 Simulation-conditional

- no new simulation lane is pre-authorized in this window
- if Phase 614 uncovers observability or parameter pressure requiring dedicated
  runtime evidence, that becomes a later-lane defer rather than an implicit
  scope widening inside this window

## 4. Surviving Genesis carry-forward closure lane

The strongest surviving later-lane item after Window 596-605 is the
`Phase 305 canonical output package` closure. This is not a re-run of historical
Phase 305. It is the packet that closes the missing canonical output-package
surface now carried forward through the 603/604/605 stack.

Target files should stay in the Genesis carry-forward cluster and its direct
walkthrough/evidence neighborhood. This lane must not reopen Genesis economics
runtime alignment, Genesis-only ECU controller implementation, or capability-
proof runtime work.

## 5. Outbound HTTP machine-payment skill lane

The outbound lane remains the lower-risk payment-related track because it can
stay at the perimeter.

This lane should:
- define an explicit boundary/contract packet before implementation,
- keep all payment execution external/perimeter-facing,
- produce operator guidance and negative-path drills after implementation.

This lane should not:
- authorize inbound payment,
- widen core wallet authority,
- or imply stablecoin conversion is part of the core protocol.

## 6. Inbound payment boundary-selection lane

The inbound lane remains real, but it is not execution-ready.

This window should force one explicit decision:
- whether the future inbound model is an external perimeter adapter only, or
- whether a later lane would require deeper authority changes.

Phase 612 is therefore a boundary-selection memo and prelock phase only. It may
conditionally open a later decision vehicle, but it must not implement inbound
runtime, ratify a runtime path by implication, or smuggle native escrow into
the current ledger surface.

## 7. Operator hardening lane

The operator hardening lane contains two independent post-RC tasks:
- mTLS posture and certificate-ceremony planning
- LMDB parameterization and observability tightening

These are allowed because they harden deployment posture without changing the
current constitutional wallet/payment boundary.

## 8. CDL number assignments

| CDL | Title (candidate) | Decision digest anchor | Opening phase | Ratification phase |
|-----|-------------------|------------------------|---------------|-------------------|
| CDL-062 | Inbound machine-payment ingress boundary-selection vehicle (conditional) | `external_perimeter_adapter_only_vs_later_authority_opening` | Phase 612 (conditional) | later window (conditional) |

Note:
- No CDL ratification is pre-authorized in Window 607-615.
- `CDL-062` should only be opened if Phase 612 concludes that the inbound
  boundary question cannot be carried cleanly by memo/ADR/prelock alone.

## 9. Candidate phase table

| Order | Phase | Topic | Character | Sensitivity |
|---|---|---|---|---|
| 1 | 607 | Window 607-615 sequence lock and dependency freeze | Foundation / Constitutional | **SENSITIVE** |
| 2 | 608 | Phase 305 canonical output package closure | Constitutional | NON-SENSITIVE |
| 3 | 609 | Outbound payment skill boundary and operator contract | Constitutional / Runtime-prep | NON-SENSITIVE |
| 4 | 610 | Outbound payment skill implementation | Runtime | NON-SENSITIVE |
| 5 | 611 | Outbound payment drills and operator guidance | Synthesis | NON-SENSITIVE |
| 6 | 612 | Inbound payment boundary-selection memo and prelock | Governance review | NON-SENSITIVE |
| 7 | 613 | mTLS posture ADR and cert-ceremony planning | Constitutional / Runtime-prep | NON-SENSITIVE |
| 8 | 614 | LMDB parameterization and observability tightening | Runtime | NON-SENSITIVE |
| 9 | 615 | Window closure synthesis and handoff | Gate | **SENSITIVE** |

### Note on Phase 612 non-ratifying boundary

Phase 612 is the explicit anti-drift phase in this window. It exists to stop
the repo from sliding between:
- external perimeter payment-adapter logic,
- native ILC/ECU economics theory,
- and unsupported wallet-authority assumptions.

If Phase 612 concludes that a new formal decision vehicle is needed, it may open
the path for later work. It does not authorize inbound runtime inside this
window.

### Note on Phase 614 runtime mutation pattern

Phase 614 is the only phase in this candidate map that is likely to touch live
runtime or operator configuration surfaces directly. If sequence lock confirms
`ilc_core/` mutation targets here, the phase prompt must carry:
- exact target file list,
- phantom-edit guard commands,
- clean-state guard for unrelated runtime drift,
- and a custom mutation-scope check for LMDB map-size/config/metrics surfaces.

## 10. Sensitivity classification

### SENSITIVE phases list

- `Phase 607` — structural sequence-lock boundary for the whole window
- `Phase 615` — closure gate and handoff boundary

### NON-SENSITIVE phases list

- `Phase 608` — canonical output-package closure only; no CDL mutation required
- `Phase 609` — boundary/contract packet for outbound perimeter support
- `Phase 610` — bounded outbound support implementation only
- `Phase 611` — drills and operator guidance only
- `Phase 612` — non-ratifying boundary-selection/prelock only
- `Phase 613` — posture/ceremony planning only
- `Phase 614` — hardening/runtime work only; no CDL mutation in this candidate map

### Conditional phases rule

There are no conditional tail slots in this candidate grouping. The only
conditional governance move is whether `CDL-062` is opened at Phase 612; if it
is not needed, Phase 612 remains memo/prelock only.

### Pre-commit hook block

If any later sequence-lock version adds CDL mutation, require:

`ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=<phase>`

In this current candidate grouping, no fixed phase is pre-authorized to mutate
the decision log.

## 11. Scope notes for fixed phases

### Phase 607 - Window 607-615 sequence lock and dependency freeze

Sensitivity: **SENSITIVE**. GO token required by future execution prompt.

Deliverables:
- sequence-lock spec
- dependency freeze list
- explicit non-goals / preserved-boundary list

Required content spec:
- preserve 585-595 freeze
- preserve 605 later-lane defer record
- state that inbound runtime is excluded

Test structure:
- selftest and dependency-bundle validation
- no decision-log mutation

Commit subject:
- `docs(g8): phase 607 window 607-615 sequence lock`

### Phase 608 - Phase 305 canonical output package closure

Sensitivity: NON-SENSITIVE.

Deliverables:
- closure spec for the surviving output-package defer
- supporting walkthrough/test backfill

Required content spec:
- distinguish historical Phase 305 from the later-lane closure packet
- identify exactly which output-package artifact set is now authoritative

Test structure:
- closure-artifact existence and linkage checks
- no wallet/payment boundary changes

Commit subject:
- `docs(g8): phase 608 phase 305 canonical output package closure`

### Phase 609 - Outbound payment skill boundary and operator contract

Sensitivity: NON-SENSITIVE.

Deliverables:
- perimeter-only boundary/contract spec
- operator contract / non-goal surface

Required content spec:
- external/perimeter posture only
- no inbound scope
- no wallet write/transfer widening

Test structure:
- boundary-token checks
- forbidden-scope assertions

Commit subject:
- `docs(g8): phase 609 outbound payment skill boundary`

### Phase 610 - Outbound payment skill implementation

Sensitivity: NON-SENSITIVE.

Deliverables:
- outbound payment tooling/runtime surface
- targeted tests

Required content spec:
- implementation must remain outside core constitutional wallet widening
- explicit source-path mutation list

Test structure:
- implementation tests
- negative assertions on inbound and wallet-authority drift

Commit subject:
- `feat(g8): phase 610 outbound payment skill implementation`

### Phase 611 - Outbound payment drills and operator guidance

Sensitivity: NON-SENSITIVE.

Deliverables:
- negative-path drill packet
- retrieval-backed operator guidance

Required content spec:
- operator failure cases
- perimeter degradation behavior

Test structure:
- drill/test packet
- guidance artifact validation

Commit subject:
- `docs(g8): phase 611 outbound payment drills and guidance`

### Phase 612 - Inbound payment boundary-selection memo and prelock

Sensitivity: NON-SENSITIVE.

Deliverables:
- boundary-selection memo
- optional prelock stub if a later governance vehicle is required

Required content spec:
- compare external perimeter adapter posture against any deeper later-lane
  authority-opening path
- explicitly forbid inbound runtime landing in this phase

Test structure:
- memo token checks
- forbidden-scope checks for runtime, escrow, and wallet widening

Commit subject:
- `docs(g8): phase 612 inbound payment boundary selection`

### Phase 613 - mTLS posture ADR and cert-ceremony planning

Sensitivity: NON-SENSITIVE.

Deliverables:
- mTLS posture ADR/planning packet
- certificate-ceremony outline

Required content spec:
- keep this independent from payment scope
- no implicit hostile-internet admission widening

Test structure:
- ADR structure checks
- preserved-boundary assertions

Commit subject:
- `docs(g8): phase 613 mtls posture planning`

### Phase 614 - LMDB parameterization and observability tightening

Sensitivity: NON-SENSITIVE.

Deliverables:
- operator-configurable LMDB parameter packet
- observability tightening artifact

Required content spec:
- name exact runtime/config mutation targets
- preserve economic and wallet boundaries

Test structure:
- config/runtime tests
- phantom-edit and clean-state guards if `ilc_core/` is touched

Commit subject:
- `feat(g8): phase 614 lmdb parameterization and observability`

### Phase 615 - Window closure synthesis and handoff

Sensitivity: **SENSITIVE**. GO token required by future execution prompt.

Deliverables:
- coherence delta
- handoff spec
- closure gate artifacts

Required content spec:
- explicit carry-forward of any unresolved inbound/payment/hardening items
- no silent scope inflation

Test structure:
- closure gate
- inherited selftest chain including `ILC_PHASE_605_GATE_SELFTEST=1` when the
  605 closure test or equivalent is consumed

Commit subject:
- `docs(g8): phase 615 window 607-615 closure handoff`

## 12. Key dependencies and open questions

### Must-resolve at entry

- confirm the exact file set for the `Phase 305 canonical output package`
  closure
- confirm whether outbound payment support is still wanted as a perimeter-only
  lane in this window
- confirm whether mTLS and LMDB hardening remain in the same window or split

### Sequencing constraints

- 609 must precede 610
- 610 must precede 611
- 612 must not be allowed to back-authorize inbound runtime in 613-615
- 615 must consume the preserved Phase 605 closure-gate inheritance correctly

### Open questions

- Does Phase 612 need a conditional `CDL-062` opening stub, or is memo/ADR
  discipline enough?
- Which exact runtime/config files are in scope for Phase 614?
- Is there any surviving operator need for outbound payment support after Phase
  608 closes the strongest inherited defer?

### Permanently deferred from this window

- inbound payment runtime
- wallet write/transfer/withdrawal widening
- native escrow authorization
- blockchain migration or external-token wrapping
- node-market and market-liquidity protocol work

## 13. Known patterns and technical constraints

### Novel patterns this window

- first post-606 candidate grouping that explicitly uses MemPalace retrieval as
  drafting support while preserving direct-read-first authority discipline
- first post-605 window that deliberately splits outbound payment support from
  inbound payment boundary selection

### Historical prelock hardening

If Phase 612 opens any later-boundary vehicle, later ratification work must
harden the historical prelock against the original opening commit ref rather
than reasoning from the latest tree alone.

### Phantom edit guard

If Phase 614 mutates `ilc_core/`, the phase prompt must name the exact target
files and include phantom-edit detection and fix commands before any runtime
patch is accepted.

### Pre-commit hook ilc_core clean-state guard

If runtime mutation phases are present at sequence lock, require a clean-state
check on the exact mutation targets before commit.

### Closure gate selftest guard chain

Any closure gate in Phase 615 that consumes the 605 closure gate or inherited
equivalent must set:
- `ILC_PHASE_605_GATE_SELFTEST=1`

Future execution prompts should read inherited gate tests directly rather than
reasoning by analogy.

### MemPalace drafting discipline

MemPalace retrieval may support prompt and guidance drafting in this window, but
only under:
- tiered retrieval,
- direct repo reads,
- and the logic-gate profile in
  `docs/tools/mempalace/ilc_mempalace_logic_gate_profile_v0.1.md`

## 14. Non-goals and explicitly deferred items

- no inbound payment implementation
- no inbound payment ratification in this window
- no wallet-authority opening
- no native ledger escrow
- no public FAQ/oracle lane
- no DeFi/liquidity/node-market protocol expansion
- no reinterpretation of wallet-agnostic signing as blockchain migration

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
- `docs/adr/ADR_0013_External_Payment_Boundary_and_Third_Party_Independence.md`
- `docs/adr/ADR_0025_D2d_HTTP_Gossip_Transport_Binding.md`
- `docs/specs/ilc_window_607_615_candidate_phase_grouping_v0.1.md`
- For closure gate (Phase 615): all Phase 607-614 test files and artifacts.

### Optional MemPalace retrieval appendix

Advisory only. Direct repo reads remain authoritative.

Suggested tier-scoped queries:
- `Phase 305 canonical output package later-lane defer`
- `inbound HTTP machine-payment ingress remains a separate later lane`
- `wallet-agnostic signing independent of any blockchain`
- `read-only wallet query boundary`

Required retrieval-use filter:
- `docs/tools/mempalace/ilc_mempalace_logic_gate_profile_v0.1.md`

Use this appendix only as drafting support. Retrieved material must pass through
the gate profile and then be checked against the canonical anchors above.

## 16. Rationale for single-window scope

1. The window closes the strongest surviving post-605 defer (`Phase 305
   canonical output package`) without dragging in unrelated public-boundary work.
2. The outbound payment support lane is narrow enough to be useful without
   reopening the wallet boundary.
3. The inbound payment issue is forced into an explicit boundary-selection lane
   instead of drifting in historical theory.
4. mTLS and LMDB hardening are useful post-RC tasks that do not require a new
   public-authority theory.
5. The window remains small enough to close cleanly while preserving the
   inherited 585-606 boundary chain.
