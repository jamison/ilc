# ILC Window 613-619: Candidate Phase Grouping

**Author:** Claude Sonnet 4.6 (local architectural reviewer)
**Date:** 2026-04-12
**Baseline:** Window 607-612 CLOSED (phase_612_verdict=pass). ADR-0028 accepted. Option D active near-term posture. Option B graduation checklist governing any later sovereign substrate selection. CDL-062 not authorized. Capsule v3.2.
**Planning note:** This is a candidate grouping, not a locked sequence. Phases 613-619 are the firm minimum lane. No tail slot or overflow phase is reserved; the window closes at Phase 619.

---

## 1. Window identity and scope

Window 613-619 opens the first post-612 execution lane after the settlement-substrate reconciliation window closed.

The window has one authorized track: the first post-612 spec lane covering the public init/admission contract, visible ECU-to-ILC lifecycle contract, public receipt schema and query contract, and public wallet surface contract (the minimum participant-touch package specified in Phase 612 Section 3). This is the MVP gate spec lane.

Agent Skills is explicitly deferred to a post-619 window. Phase 612 Section 3 establishes a strict priority rule: post-612 work must prioritize the init/admission, receipt, lifecycle, and wallet touchpoints before opening new planning sub-lanes. Opening Agent Skills as a parallel track inside this window is prohibited.

No CDL mutation is anticipated in this window. No sovereign substrate execution opens. No wallet widening is authorized. The MVP gate from Phase 612 Section 3 requires both spec form AND interface/runtime form before broader public RC claims may proceed. This window satisfies the spec-form half of that gate; spec-form closure is necessary but NOT sufficient. Broader public RC claims remain blocked until both spec form and interface/runtime form are complete.

---

## 2. Baseline and inheritance

### Ratified CDL chain (carry-forward from Window 607-612)

The full CDL chain through CDL-061 is ratified. Relevant active CDLs for this window include CDL-042 (agent_id namespace), CDL-034 (authored envelope schema), CDL-052 (epistemic runtime), CDL-V7 (Popperian gate). No new CDL is anticipated in this window.

### Active runtime chain

Current active runtime modules: gossip_transport_runtime_558.v0.1, peer_discovery static_v1, agent_loop_v1, LMDB-backed economic runtime (Phase 579+), passive ECU attribution (Phase 550), CDL-060 gossip runtime (Phase 548). Phase 613 sequence lock inherits all of these as frozen law.

### Canonical anchors inherited

- `docs/specs/ilc_settlement_substrate_closure_and_mvp_gated_replan_612_v0.1.md` — authoritative closure memo
- `docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md` — graduation checklist governing body
- `docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md` — receipt discipline
- `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md` — protocol/harness boundary
- `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md` — wallet boundary (frozen)
- `docs/specs/ilc_rc0_1_ecu_settlement_wallet_query_integration_581_v0.1.md` — settlement integration
- `docs/specs/ilc_public_receipt_representation_cluster_lock_586_v0.1.md`
- `docs/specs/ilc_public_identity_activation_and_namespace_boundary_lock_587_v0.1.md`
- `docs/specs/ilc_settlement_linked_public_legitimacy_and_payout_traceability_lock_589_v0.1.md`
- `docs/specs/ilc_public_release_claim_and_operator_honesty_package_592_v0.1.md`

### Next fresh CDL number

CDL-062 is reserved but not authorized. The next assignable CDL number for non-substrate work is CDL-062 (reserved per Phase 612 Section 5). No CDL is authorized in this window.

---

## 3. Track inventory

### Constitutionally obligated

- Phase 613: window sequence lock (structural; SENSITIVE)
- Phase 614: Public init/admission contract spec (SENSITIVE — public contract scope)
- Phase 615: Visible ECU-to-ILC lifecycle contract spec (SENSITIVE — lifecycle claim scope)
- Phase 616: Public receipt schema and query contract spec (NON-SENSITIVE)
- Phase 617: Public wallet surface contract spec (SENSITIVE — wallet surface)
- Phase 618: MVP gate synthesis and coherence report + capsule v3.3 (NON-SENSITIVE)
- Phase 619: Window 613-619 closure gate and handoff (SENSITIVE — window closure)

### Deferred governance

- CDL-062: sovereign substrate — remains not authorized; deferred to post-MVP-gate window
- Agent Skills (ADR-0024): deferred per Phase 612 priority rule; post-619 window
- Option B graduation checklist execution: deferred; ADR-0028 governs

### Simulation-conditional

- No simulation phases planned in this window. The MVP gate synthesis at Phase 618 serves the verification role.

---

## 4. MVP gate spec lane scope

Four phases (614-617) each produce one boundary-lock spec document and one test file. Together they close the five-touchpoint minimum participant-touch package from Phase 612 Section 3. Phase 618 synthesizes the gate verdict.

### Init/admission spec (Phase 614)

**Primary output:** `docs/specs/ilc_public_init_admission_contract_spec_614_v0.1.md`

Dependency chain: Phase 576 (wallet boundary), Phase 581 (settlement/wallet query integration), Phase 587 (identity activation and namespace boundary), Phase 586 (receipt representation cluster), ADR-0027. The init/admission spec must lock the machine-legible interface for public participant init and admission without widening wallet authority or opening CDL-062.

SENSITIVE: this phase touches no CDL, no ADR, and no ilc_core/. It is SENSITIVE because it defines public-participant contract scope and a mistaken claim could widen the wallet or admission boundary.

### ECU-to-ILC lifecycle spec (Phase 615)

**Primary output:** `docs/specs/ilc_ecu_to_ilc_lifecycle_contract_spec_615_v0.1.md`

Dependency chain: Phase 576, Phase 581, Phase 586, Phase 587, Phase 589, ADR-0028. The lifecycle spec must lock the visible end-to-end participant journey from ECU attribution through epoch commit to ILC visibility, without selecting a final substrate, without opening wallet write authority, and without implying public claimability beyond the current bounded posture.

SENSITIVE: this phase touches no CDL, no ADR, and no ilc_core/. It is SENSITIVE because it defines participant-visible lifecycle semantics and an over-broad claim could imply transfer or claimability.

### Receipt schema and query spec (Phase 616)

**Primary output:** `docs/specs/ilc_public_receipt_schema_and_query_contract_spec_616_v0.1.md`

Dependency chain: Phase 586 (receipt representation cluster), Phase 587, Phase 589, ADR-0027. The receipt schema spec must lock the machine-legible public receipt schema and query surface for the minimum receipt classes identified in Phase 586. NON-SENSITIVE.

### Wallet surface spec (Phase 617)

**Primary output:** `docs/specs/ilc_public_wallet_surface_contract_spec_617_v0.1.md`

Dependency chain: Phase 576, Phase 581, Phase 589, ADR-0026. The wallet surface spec must lock the public-facing wallet query surface within the existing read-only boundary. No wallet widening. SENSITIVE: touches public-participant contract scope; wallet surface expansion risk requires GO token.

---

## 5. CDL number assignments

No new CDL is assigned in this window.

| CDL | Status | Notes |
|---|---|---|
| CDL-062 | Reserved, not authorized | Sovereign substrate — blocked per Phase 612 Section 5 and ADR-0028 Section 4 |

No CDL mutations are authorized in this window.

---

## 6. Candidate phase table

| Order | Phase | Topic | Character | Sensitivity |
|---|---|---|---|---|
| 1 | 613 | Window 613-619 sequence lock | Foundation / Constitutional | **SENSITIVE** |
| 2 | 614 | Public init/admission contract spec | Constitutional | **SENSITIVE** |
| 3 | 615 | Visible ECU-to-ILC lifecycle contract spec | Constitutional | **SENSITIVE** |
| 4 | 616 | Public receipt schema and query contract spec | Constitutional | NON-SENSITIVE |
| 5 | 617 | Public wallet surface contract spec | Constitutional | **SENSITIVE** |
| 6 | 618 | MVP gate synthesis and coherence report + capsule v3.3 | Synthesis | NON-SENSITIVE |
| 7 | 619 | Window 613-619 closure gate and handoff | Gate | **SENSITIVE** |

No tail slot or overflow phase is assigned. The window closes at Phase 619.

---

## 7. Sensitivity classification

### SENSITIVE phases

- **Phase 613** — sequence lock. Structural boundary phase. Commits the window scope, dependency bundle, and hard pass condition for all downstream phases. Sensitive: scope misstatement or boundary error propagates to all subsequent phases.
- **Phase 614** — public participant contract scope. Defines public init/admission interface. Mistaken widening of admission scope or wallet authority propagates as a false public claim.
- **Phase 615** — public participant lifecycle claim. Defines visible ECU-to-ILC journey. Mistaken claimability or transfer implication propagates as a false public economic claim.
- **Phase 617** — public wallet surface. Defines public-facing wallet query contract. Wallet widening risk requires GO token.
- **Phase 619** — structural boundary gate. Window closure verdict is load-bearing; incorrect pass propagates uncorrected scope errors forward.

### NON-SENSITIVE phases

- **Phase 616** — adds receipt schema spec doc and test only; no CDL, ADR, ilc_core/, or wallet authority change
- **Phase 618** — synthesis and coherence report; no CDL, no ADR, no ilc_core/ change; capsule version bump only

### Pre-commit hook requirement

Phases 613, 614, 615, 617, and 619 require the human's explicit GO token before any commit is executed.

No CDL mutation is authorized in this window, so `ILC_CDL_MUTATION_AUTHORIZED` is not applicable to any phase in this window.

---

## 8. Scope notes for fixed phases

### Phase 613 — SENSITIVE (sequence lock; GO token required)

Deliverables:
- `docs/specs/ilc_phase_613_619_sequence_lock_v0.1.md`
- `tests/test_phase_613_window_613_619_sequence_lock.py`
- `docs/phases/phase_613_g8_window_613_619_sequence_lock_walkthrough.md`
- `docs/phases/STATUS.md`

Test structure: 10 tests (8 primary + 2 commit path). Pre-commit split: 8 passed, 2 failed.

Main commit paths (exactly): `{docs/specs/ilc_phase_613_619_sequence_lock_v0.1.md, tests/test_phase_613_window_613_619_sequence_lock.py}`
Backfill commit paths (exactly): `{docs/phases/phase_613_g8_window_613_619_sequence_lock_walkthrough.md, docs/phases/STATUS.md}`

Commit subject (main): `docs(g8): phase 613 window 613-619 sequence lock`
Commit subject (backfill): `docs(g8): phase 613 walkthrough and status backfill`

---

### Phase 614 — SENSITIVE (public contract scope; GO token required)

Deliverables:
- `docs/specs/ilc_public_init_admission_contract_spec_614_v0.1.md`
- `tests/test_phase_614_public_init_admission_contract_spec.py`
- `docs/phases/phase_614_g8_public_init_admission_contract_spec_walkthrough.md`
- `docs/phases/STATUS.md`

Test structure: 10 tests. Pre-commit split: 8 passed, 2 failed. Main commit: spec + test only.
No `ilc_core/` path. No CDL. No ADR.

Commit subject (main): `docs(g8): phase 614 public init admission contract spec`
Commit subject (backfill): `docs(g8): phase 614 walkthrough and status backfill`

---

### Phase 615 — SENSITIVE (lifecycle claim scope; GO token required)

Deliverables:
- `docs/specs/ilc_ecu_to_ilc_lifecycle_contract_spec_615_v0.1.md`
- `tests/test_phase_615_ecu_to_ilc_lifecycle_contract_spec.py`
- `docs/phases/phase_615_g8_ecu_to_ilc_lifecycle_contract_spec_walkthrough.md`
- `docs/phases/STATUS.md`

Test structure: 10 tests. Pre-commit split: 8 passed, 2 failed. Main commit: spec + test only.
No `ilc_core/` path. No CDL. No ADR.

Commit subject (main): `docs(g8): phase 615 ecu to ilc lifecycle contract spec`
Commit subject (backfill): `docs(g8): phase 615 walkthrough and status backfill`

---

### Phase 616 — NON-SENSITIVE

Deliverables:
- `docs/specs/ilc_public_receipt_schema_and_query_contract_spec_616_v0.1.md`
- `tests/test_phase_616_public_receipt_schema_and_query_contract_spec.py`
- `docs/phases/phase_616_g8_public_receipt_schema_and_query_contract_spec_walkthrough.md`
- `docs/phases/STATUS.md`

Test structure: 11 tests. Pre-commit split: 9 passed, 2 failed. Main commit: spec + test only.
No `ilc_core/` path. No CDL. No ADR.

Commit subject (main): `docs(g8): phase 616 public receipt schema and query contract spec`
Commit subject (backfill): `docs(g8): phase 616 walkthrough and status backfill`

---

### Phase 617 — SENSITIVE (wallet surface; GO token required)

Deliverables:
- `docs/specs/ilc_public_wallet_surface_contract_spec_617_v0.1.md`
- `tests/test_phase_617_public_wallet_surface_contract_spec.py`
- `docs/phases/phase_617_g8_public_wallet_surface_contract_spec_walkthrough.md`
- `docs/phases/STATUS.md`

Test structure: 10 tests. Pre-commit split: 8 passed, 2 failed. Main commit: spec + test only.
No `ilc_core/` path. No CDL. No ADR. No wallet widening.

Commit subject (main): `docs(g8): phase 617 public wallet surface contract spec`
Commit subject (backfill): `docs(g8): phase 617 walkthrough and status backfill`

---

### Phase 618 — NON-SENSITIVE

Deliverables:
- `docs/specs/ilc_window_613_619_coherence_report_618_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v3.3.md`
- `tests/test_phase_618_mvp_gate_synthesis_and_coherence_report.py`
- `docs/phases/phase_618_g8_mvp_gate_synthesis_and_coherence_report_walkthrough.md`
- `docs/phases/STATUS.md`

Test structure: 9 tests. Main commit: coherence report + capsule + test. Backfill: walkthrough + STATUS.md.
No `ilc_core/` path. No CDL. No ADR. Capsule version bump to v3.3.

Commit subject (main): `docs(g8): phase 618 mvp gate synthesis and coherence report`
Commit subject (backfill): `docs(g8): phase 618 walkthrough and status backfill`

---

### Phase 619 — SENSITIVE (window closure gate; GO token required)

Deliverables:
- `tools/run_window_613_619_closure_gate_phase_619.sh` (gate script)
- `tests/test_phase_619_window_613_619_closure_gate.py`
- `docs/specs/ilc_window_613_619_handoff_619_v0.1.md`
- `docs/phases/phase_619_g8_window_613_619_closure_gate_and_handoff_walkthrough.md`
- `docs/phases/STATUS.md`

Test structure: 10 tests. Main commit: gate script + gate test + handoff. Backfill: walkthrough + STATUS.md.
No `ilc_core/` path. No CDL. No ADR.

Commit subject (main): `docs(g8): phase 619 window 613-619 closure gate and handoff`
Commit subject (backfill): `docs(g8): phase 619 walkthrough and status backfill`

---

## 9. Key dependencies and open questions

### Must-resolve at entry

- Phase 612 closure memo is the authoritative governing input for all post-612 work in this window. Any contradiction between a phase prompt and the Phase 612 closure memo must be resolved in favor of the closure memo.
- The wallet boundary from Phase 576 and Phase 581 remains frozen incoming law. No phase in this window may widen it.
- Agent Skills is not a parallel track in this window. Any prompt that opens or implies Agent Skills work is incorrect; this window is MVP gate spec only.

### Sequencing constraints

- Phase 613 must be executed before any other phase in this window.
- Phase 614 must precede Phase 615 because the lifecycle spec assumes the init/admission contract is stable.
- Phase 615 must precede Phase 616 because receipt schema anchors to the lifecycle contract.
- Phases 614-617 must all be complete before Phase 618 MVP gate synthesis.
- Phase 618 must be complete before Phase 619 closure gate.

### Open questions

1. **MVP gate form**: Phase 618 produces a synthesis verdict. If any of Phases 614-617 has unresolved gaps, Phase 618 must record them explicitly rather than issuing a premature green verdict. If gaps exist, Phase 618 routes them to a post-619 phase rather than widening this window.
2. **Phase 612 five-touchpoint coverage**: Note that Phase 612 defines five touchpoints but phases 614-617 cover four spec outputs. ECU visibility and delayed ILC visibility are both covered by the single Phase 615 lifecycle spec (consistent with Phase 612 Section 3 bundling). Phase 618 must explicitly evaluate all five touchpoints against Phase 615 when synthesizing the gate verdict.

### Permanently deferred

- CDL-062 (sovereign substrate ratification) — blocked per ADR-0028
- Agent Skills (ADR-0024) — deferred per Phase 612 priority rule; post-619 window
- Option B graduation checklist execution — governed by ADR-0028; not opened in this window
- Payment runtime, wallet widening, chain implementation — all remain out of scope

---

## 10. Known patterns and technical constraints

### MVP gate synthesis phase (Phase 618)

Phase 618 introduces a gate-synthesis character (not a pure closure gate). Unlike closure gates, it does not run a shell script; it produces a coherence report that reasons over all four spec outputs and either passes or flags gaps. If gaps exist, Phase 618 records them for a post-619 triage phase rather than issuing a premature pass.

### Historical prelock hardening

No CDL ratifications occur in this window. Historical prelock hardening is not applicable. Any phase that references a prior CDL's current state must use `git show <commit>:<path>` pattern to read historical state rather than assuming current state.

### Phantom edit guard

No `ilc_core/` files are mutation targets in this window. All phases must assert `not any(p.startswith("ilc_core/") for p in commit_paths)` in their commit path tests.

### Closure gate structural coverage

Phase 619 closure gate must use the six-category Phase 605 structural pattern
and explicitly cover the full current-window verification surface rather than
reasoning by analogy. Category 2 must cover the four MVP spec phase tests
(Phases 614-617). Category 3 must cover the sequence-lock and coherence tests
(Phases 613 and 618). The gate does not use the older selftest guard-chain
pattern.

---

## 11. Non-goals and explicitly deferred items

- **No CDL-062 opening**: not authorized by ADR-0028 or Phase 612 closure memo.
- **No wallet widening**: the Phase 576 and Phase 581 read-only wallet boundary is frozen.
- **No payment runtime implementation**: outbound and inbound payment remain out of scope.
- **No chain implementation**: no L1, L2, or rollup work is authorized or scoped.
- **No sovereign substrate selection**: Option D remains the active posture; Option B selection requires explicit satisfaction of the graduation checklist.
- **No Agent Skills in this window**: deferred per Phase 612 priority rule; post-619 window.
- **No new planning sub-lanes**: this window is bounded to the MVP gate spec lane only.
- **No public Genesis-governance or public minting claims**: the curated testnet boundary from Window 575-584 remains in effect.
- **No harness/product layer expansion** beyond what is authorized in ADR-0026.

---

## 12. Key canonical anchors for prompt drafting

- `docs/specs/ilc_settlement_substrate_closure_and_mvp_gated_replan_612_v0.1.md` — PRIMARY: Phase 612 closure memo (authoritative carry-forward)
- `docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md` — graduation checklist and CDL-062 non-authorization
- `docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md` — receipt and bootstrap discipline
- `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md` — protocol/harness boundary
- `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md` — wallet boundary (frozen law)
- `docs/specs/ilc_rc0_1_ecu_settlement_wallet_query_integration_581_v0.1.md` — settlement integration boundary
- `docs/specs/ilc_public_receipt_representation_cluster_lock_586_v0.1.md` — receipt cluster (Phase 616 anchor)
- `docs/specs/ilc_public_identity_activation_and_namespace_boundary_lock_587_v0.1.md` — identity activation (Phase 614 anchor)
- `docs/specs/ilc_settlement_linked_public_legitimacy_and_payout_traceability_lock_589_v0.1.md` — settlement legitimacy (Phase 615 anchor)
- `docs/specs/ilc_public_release_claim_and_operator_honesty_package_592_v0.1.md` — public RC honesty (Phase 618 anchor)
- `docs/specs/ilc_constitutional_decision_log_v0.1.md` — CDL register (read-only in this window)
- `docs/phases/STATUS.md` — phase completion log
- For closure gate (Phase 619): all Phase 613-618 test files and artifacts.
