# ILC Window 613-622: Candidate Phase Grouping

**Author:** Claude Sonnet 4.6 (local architectural reviewer)
**Date:** 2026-04-12
**Baseline:** Window 607-612 CLOSED (phase_612_verdict=pass). ADR-0028 accepted. Option D active near-term posture. Option B graduation checklist governing any later sovereign substrate selection. CDL-062 not authorized. Capsule v3.2.
**Planning note:** This is a candidate grouping, not a locked sequence. Phases 613-621 are the firm minimum lane. Phase 622 is the tail slot reserved for overflow or late additions as directed.

---

## 1. Window identity and scope

Window 613-622 opens the first post-612 execution lane after the settlement-substrate reconciliation window closed.

The window has two parallel authorized tracks: (1) the first post-612 spec lane covering the public init/admission contract, visible ECU-to-ILC lifecycle contract, public receipt schema and query contract, and public wallet surface contract (the minimum participant-touch package specified in Phase 612 Section 3); (2) the Agent Skills Tier 1+2 infrastructure lane authorized by ADR-0024 acceptance (pending; ADR-0024 is currently Proposed and must be moved to Accepted as Phase 614's primary action).

No CDL mutation is anticipated in this window. No sovereign substrate execution opens. No wallet widening is authorized. The MVP gate from Phase 612 Section 3 is the pass criterion for the spec lane; the gate must be satisfied in spec form before broader public RC claims are made.

Tail-slot policy: Phase 622 is reserved for overflow. If the firm phases 613-621 close clean, Phase 622 may be used for an additional spec review or deferred item. If not needed, the window closes at 621.

---

## 2. Baseline and inheritance

### Ratified CDL chain (carry-forward from Window 607-612)

The full CDL chain through CDL-061 is ratified. Relevant active CDLs for this window include CDL-042 (agent_id namespace), CDL-034 (authored envelope schema), CDL-052 (epistemic runtime), CDL-V7 (Popperian gate). No new CDL is anticipated in this window; Tier 1+2 skills require no CDL per ADR-0024.

### Active runtime chain

Current active runtime modules: gossip_transport_runtime_558.v0.1, peer_discovery static_v1, agent_loop_v1, LMDB-backed economic runtime (Phase 579+), passive ECU attribution (Phase 550), CDL-060 gossip runtime (Phase 548). Phase 613 sequence lock inherits all of these as frozen law.

### Canonical anchors inherited

- `docs/specs/ilc_settlement_substrate_closure_and_mvp_gated_replan_612_v0.1.md` — authoritative closure memo
- `docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md` — graduation checklist governing body
- `docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md` — receipt discipline
- `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md` — protocol/harness boundary
- `docs/adr/ADR_0024_Agent_Skills_Infrastructure.md` — Agent Skills (currently Proposed)
- `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md` — wallet boundary (frozen)
- `docs/specs/ilc_rc0_1_ecu_settlement_wallet_query_integration_581_v0.1.md` — settlement integration
- `docs/specs/ilc_public_receipt_representation_cluster_lock_586_v0.1.md`
- `docs/specs/ilc_public_identity_activation_and_namespace_boundary_lock_587_v0.1.md`
- `docs/specs/ilc_settlement_linked_public_legitimacy_and_payout_traceability_lock_589_v0.1.md`
- `docs/specs/ilc_public_release_claim_and_operator_honesty_package_592_v0.1.md`

### Next fresh CDL number

CDL-062 is reserved but not authorized. The next assignable CDL number for non-substrate work is CDL-062 (reserved per Phase 612 Section 5). Tier 3 skills would require a new CDL beyond CDL-062 — this is not authorized in this window.

---

## 3. Track inventory

### Constitutionally obligated

- Phase 613: window sequence lock (structural; SENSITIVE)
- Phase 614: ADR-0024 acceptance + Agent Skills Tier 1 implementation (SENSITIVE — ADR mutation)
- Phase 615: Agent Skills Tier 2 scaffold skills (NON-SENSITIVE — skills/ additions only)

### Deferred governance

- CDL-062: sovereign substrate — remains not authorized; deferred to post-MVP-gate window
- Tier 3 skills (skill_node CDL): deferred per ADR-0024 explicit constraint
- Option B graduation checklist execution: deferred; ADR-0028 governs

### Simulation-conditional

- No simulation phases planned in this window. The MVP gate synthesis at Phase 620 serves the verification role.

---

## 4. Agent Skills lane scope

ADR-0024 is currently Proposed and must be accepted as Phase 614's first commit action. Phase 614 changes the ADR-0024 Status field from "Proposed" to "Accepted."

**Tier 1 skills (Phase 614):** Seven workflow skills, each implemented as a `skills/<name>/SKILL.md` file per the agentskills.io standard. Skills live at root `skills/` directory (not `.claude/skills/`). All seven are `disable-model-invocation: true`.

| Skill | File path |
|---|---|
| `phase-validate` | `skills/phase-validate/SKILL.md` |
| `phase-commit` | `skills/phase-commit/SKILL.md` |
| `run-canary` | `skills/run-canary/SKILL.md` |
| `cdl-status` | `skills/cdl-status/SKILL.md` |
| `selftest-audit` | `skills/selftest-audit/SKILL.md` |
| `pre-flight-check` | `skills/pre-flight-check/SKILL.md` |
| `cdl-open` | `skills/cdl-open/SKILL.md` |

**Tier 2 skills (Phase 615):** Five scaffold skills, each implemented as `skills/<name>/SKILL.md` (with optional `skills/<name>/templates/` subdirectory).

| Skill | File path |
|---|---|
| `phase-test-scaffold` | `skills/phase-test-scaffold/SKILL.md` |
| `cdl-evidence-scaffold` | `skills/cdl-evidence-scaffold/SKILL.md` |
| `sim-doc-scaffold` | `skills/sim-doc-scaffold/SKILL.md` |
| `gate-scaffold` | `skills/gate-scaffold/SKILL.md` |
| `coherence-scaffold` | `skills/coherence-scaffold/SKILL.md` |

Tier 2 skills may include supporting `templates/` subdirectories. No external skills may be imported (ADR-0024 explicit exclusion).

---

## 5. MVP gate spec lane scope

Four phases (616-619) each produce one boundary-lock spec document and one test file. Together they close the five-touchpoint minimum participant-touch package from Phase 612 Section 3. Phase 620 synthesizes the gate verdict.

### Initiative/admission spec (Phase 616)

**Primary output:** `docs/specs/ilc_public_init_admission_contract_spec_616_v0.1.md`

Dependency chain: Phase 576 (wallet boundary), Phase 581 (settlement/wallet query integration), Phase 587 (identity activation and namespace boundary), Phase 586 (receipt representation cluster), ADR-0027. The init/admission spec must lock the machine-legible interface for public participant init and admission without widening wallet authority or opening CDL-062.

The init/admission contract covers:
- the canonical admission entry point and its signed receipt output
- the exact admission authority scope (not public permissionless admission; curated testnet boundary still applies)
- the link from the admission receipt to canonical key-derived agent_id
- the explicit out-of-scope list (no spend, no transfer, no withdrawal, no chain interaction)

SENSITIVE: this phase touches no CDL, no ADR, and no ilc_core/. It is SENSITIVE because it defines public-participant contract scope and a mistaken claim could widen the wallet or admission boundary.

### ECU-to-ILC lifecycle spec (Phase 617)

**Primary output:** `docs/specs/ilc_ecu_to_ilc_lifecycle_contract_spec_617_v0.1.md`

Dependency chain: Phase 576, Phase 581, Phase 586, Phase 587, Phase 589, ADR-0028. The lifecycle spec must lock the visible end-to-end participant journey from ECU attribution through epoch commit to ILC visibility, without selecting a final substrate, without opening wallet write authority, and without implying public claimability beyond the current bounded posture.

The lifecycle contract covers:
- ECU attribution to participant (production contribution recognized)
- ECU accrual and epoch attribution candidate state
- epoch-commit settlement producing settled internal balance
- delayed ILC visibility as a read-only accounting surface
- explicit deferred-claimability state boundary

SENSITIVE: this phase touches no CDL, no ADR, and no ilc_core/. It is SENSITIVE because it defines participant-visible lifecycle semantics and an over-broad claim could imply transfer or claimability.

### Receipt schema and query spec (Phase 618)

**Primary output:** `docs/specs/ilc_public_receipt_schema_and_query_contract_spec_618_v0.1.md`

Dependency chain: Phase 586 (receipt representation cluster), Phase 587, Phase 589, ADR-0027. The receipt schema spec must lock the machine-legible public receipt schema and query surface for the minimum receipt classes identified in Phase 586. NON-SENSITIVE.

### Wallet surface spec (Phase 619)

**Primary output:** `docs/specs/ilc_public_wallet_surface_contract_spec_619_v0.1.md`

Dependency chain: Phase 576, Phase 581, Phase 589, ADR-0026. The wallet surface spec must lock the public-facing wallet query surface within the existing read-only boundary. No wallet widening. SENSITIVE: touches public-participant contract scope; wallet surface expansion risk requires GO token.

---

## 6. CDL number assignments

No new CDL is assigned in this window.

| CDL | Status | Notes |
|---|---|---|
| CDL-062 | Reserved, not authorized | Sovereign substrate — blocked per Phase 612 Section 5 and ADR-0028 Section 4 |

No CDL mutations are authorized in this window. ADR-0024 acceptance (Phase 614) is an ADR mutation, not a CDL mutation.

---

## 7. Candidate phase table

| Order | Phase | Topic | Character | Sensitivity |
|---|---|---|---|---|
| 1 | 613 | Window 613-622 sequence lock | Foundation / Constitutional | **SENSITIVE** |
| 2 | 614 | ADR-0024 acceptance and Agent Skills Tier 1 | Constitutional / Runtime | **SENSITIVE** |
| 3 | 615 | Agent Skills Tier 2 scaffold skills | Runtime | NON-SENSITIVE |
| 4 | 616 | Public init/admission contract spec | Constitutional | **SENSITIVE** |
| 5 | 617 | Visible ECU-to-ILC lifecycle contract spec | Constitutional | **SENSITIVE** |
| 6 | 618 | Public receipt schema and query contract spec | Constitutional | NON-SENSITIVE |
| 7 | 619 | Public wallet surface contract spec | Constitutional | **SENSITIVE** |
| 8 | 620 | MVP gate synthesis and coherence report + capsule v3.3 | Synthesis | NON-SENSITIVE |
| 9 | 621 | Window 613-622 closure gate and handoff | Gate | **SENSITIVE** |
| 10 | 622 | Overflow / tail slot | Conditional | **conditional** |

### Conditional note on Phase 622

Phase 622 is a tail slot. It is assigned conditionally at Phase 621 if any of the following apply:

- **Scenario A**: one or more of Phases 616-619 produced incomplete spec coverage and a targeted fix-up is needed (NON-SENSITIVE if fix-up is doc-only, SENSITIVE if it touches a contract scope boundary)
- **Scenario B**: the MVP gate synthesis at Phase 620 identifies a gap that requires a targeted supplemental spec (NON-SENSITIVE if no contract scope change)
- **Scenario C**: not needed — window closes cleanly at Phase 621

Before executing Phase 622, confirm with the human whether the assigned scenario requires a GO token. If Scenario A or B in a sensitive sub-case, require GO token. If Scenario B NON-SENSITIVE or Scenario C, no GO token required.

---

## 8. Sensitivity classification

### SENSITIVE phases

- **Phase 613** — sequence lock. Structural boundary phase. Commits the window scope, dependency bundle, and hard pass condition for all downstream phases. Sensitive: scope misstatement or boundary error propagates to all subsequent phases.
- **Phase 614** — ADR mutation. Phase 614 changes ADR-0024 Status from "Proposed" to "Accepted." All seven Tier 1 skill files are also committed in the same phase. ADR mutation requires explicit GO token.
- **Phase 616** — public participant contract scope. Defines public init/admission interface. Mistaken widening of admission scope or wallet authority propagates as a false public claim.
- **Phase 617** — public participant lifecycle claim. Defines visible ECU-to-ILC journey. Mistaken claimability or transfer implication propagates as a false public economic claim.
- **Phase 619** — public wallet surface. Defines public-facing wallet query contract. Wallet widening risk requires GO token.
- **Phase 621** — structural boundary gate. Window closure verdict is load-bearing; incorrect pass propagates uncorrected scope errors forward.

### NON-SENSITIVE phases

- **Phase 615** — adds `skills/` directory entries only; no CDL, ADR, ilc_core/, or public-participant contract change
- **Phase 618** — adds receipt schema spec doc and test only; no CDL, ADR, ilc_core/, or wallet authority change
- **Phase 620** — synthesis and coherence report; no CDL, no ADR, no ilc_core/ change; capsule version bump only

### Conditional phases rule

Before executing Phase 622, confirm with the human which scenario applies. If the assigned scenario involves contract scope boundary changes, require GO token. If doc-only without scope widening, NON-SENSITIVE execution is permitted.

### Pre-commit hook requirement

Phases 613, 614, 616, 617, 619, and 621 require the human's explicit GO token before any commit is executed. Phase 614 additionally requires explicit GO before the ADR status change is committed.

No CDL mutation is authorized in this window, so `ILC_CDL_MUTATION_AUTHORIZED` is not applicable to any phase in this window. The ADR mutation in Phase 614 uses a simpler explicit-authorization model without a pre-commit env hook.

---

## 9. Scope notes for fixed phases

### Phase 613 — SENSITIVE (sequence lock; GO token required)

Deliverables:
- `docs/specs/ilc_phase_613_622_sequence_lock_v0.1.md`
- `tests/test_phase_613_window_613_622_sequence_lock.py`
- `docs/phases/phase_613_g8_window_613_622_sequence_lock_walkthrough.md`
- `docs/phases/STATUS.md`

Test structure: 10 tests (8 primary + 2 commit path). Pre-commit split: 8 passed, 2 failed (commit path tests). Commit resolver: main commit subject must contain both `phase 613` and `sequence lock`; backfill commit subject must contain `phase 613` and `walkthrough` and `backfill`.

Main commit paths (exactly): `{docs/specs/ilc_phase_613_622_sequence_lock_v0.1.md, tests/test_phase_613_window_613_622_sequence_lock.py}`
Backfill commit paths (exactly): `{docs/phases/phase_613_g8_window_613_622_sequence_lock_walkthrough.md, docs/phases/STATUS.md}`

Commit subject (main): `docs(g8): phase 613 window 613-622 sequence lock`
Commit subject (backfill): `docs(g8): phase 613 walkthrough and status backfill`

---

### Phase 614 — SENSITIVE (ADR mutation; GO token required)

Deliverables:
- `docs/adr/ADR_0024_Agent_Skills_Infrastructure.md` (Status changed from "Proposed" to "Accepted")
- `skills/phase-validate/SKILL.md`
- `skills/phase-commit/SKILL.md`
- `skills/run-canary/SKILL.md`
- `skills/cdl-status/SKILL.md`
- `skills/selftest-audit/SKILL.md`
- `skills/pre-flight-check/SKILL.md`
- `skills/cdl-open/SKILL.md`
- `tests/test_phase_614_adr_0024_acceptance_and_agent_skills_tier_1.py`
- `docs/phases/phase_614_g8_adr_0024_acceptance_and_agent_skills_tier_1_walkthrough.md`
- `docs/phases/STATUS.md`

Test structure: 10 tests. Pre-commit split: 8 passed, 2 failed. Main commit must include the ADR file + all 7 skill files + test file. Backfill commit: walkthrough + STATUS.md.

Main commit paths (exactly): `{docs/adr/ADR_0024_Agent_Skills_Infrastructure.md, skills/phase-validate/SKILL.md, skills/phase-commit/SKILL.md, skills/run-canary/SKILL.md, skills/cdl-status/SKILL.md, skills/selftest-audit/SKILL.md, skills/pre-flight-check/SKILL.md, skills/cdl-open/SKILL.md, tests/test_phase_614_adr_0024_acceptance_and_agent_skills_tier_1.py}`

No `ilc_core/` path in main commit. No CDL path in main commit.

Commit subject (main): `docs(g8): phase 614 adr-0024 acceptance and agent skills tier 1`
Commit subject (backfill): `docs(g8): phase 614 walkthrough and status backfill`

---

### Phase 615 — NON-SENSITIVE (skills/ additions only)

Deliverables:
- `skills/phase-test-scaffold/SKILL.md`
- `skills/cdl-evidence-scaffold/SKILL.md`
- `skills/sim-doc-scaffold/SKILL.md`
- `skills/gate-scaffold/SKILL.md`
- `skills/coherence-scaffold/SKILL.md`
- Optional: `skills/<name>/templates/` subdirectories with one reference file each
- `tests/test_phase_615_agent_skills_tier_2_scaffold_skills.py`
- `docs/phases/phase_615_g8_agent_skills_tier_2_scaffold_skills_walkthrough.md`
- `docs/phases/STATUS.md`

Test structure: 8 tests. Main commit: all 5+ skill files + test file. Backfill: walkthrough + STATUS.md.

No `ilc_core/` path in main commit. No CDL path. No ADR path.

Commit subject (main): `docs(g8): phase 615 agent skills tier 2 scaffold skills`
Commit subject (backfill): `docs(g8): phase 615 walkthrough and status backfill`

---

### Phase 616 — SENSITIVE (public contract scope; GO token required)

Deliverables:
- `docs/specs/ilc_public_init_admission_contract_spec_616_v0.1.md`
- `tests/test_phase_616_public_init_admission_contract_spec.py`
- `docs/phases/phase_616_g8_public_init_admission_contract_spec_walkthrough.md`
- `docs/phases/STATUS.md`

Test structure: 11 tests. Pre-commit split: 9 passed, 2 failed. Main commit: spec + test only.
No `ilc_core/` path. No CDL. No ADR.

Commit subject (main): `docs(g8): phase 616 public init admission contract spec`
Commit subject (backfill): `docs(g8): phase 616 walkthrough and status backfill`

---

### Phase 617 — SENSITIVE (lifecycle claim scope; GO token required)

Deliverables:
- `docs/specs/ilc_ecu_to_ilc_lifecycle_contract_spec_617_v0.1.md`
- `tests/test_phase_617_ecu_to_ilc_lifecycle_contract_spec.py`
- `docs/phases/phase_617_g8_ecu_to_ilc_lifecycle_contract_spec_walkthrough.md`
- `docs/phases/STATUS.md`

Test structure: 11 tests. Pre-commit split: 9 passed, 2 failed. Main commit: spec + test only.
No `ilc_core/` path. No CDL. No ADR.

Commit subject (main): `docs(g8): phase 617 ecu to ilc lifecycle contract spec`
Commit subject (backfill): `docs(g8): phase 617 walkthrough and status backfill`

---

### Phase 618 — NON-SENSITIVE

Deliverables:
- `docs/specs/ilc_public_receipt_schema_and_query_contract_spec_618_v0.1.md`
- `tests/test_phase_618_public_receipt_schema_and_query_contract_spec.py`
- `docs/phases/phase_618_g8_public_receipt_schema_and_query_contract_spec_walkthrough.md`
- `docs/phases/STATUS.md`

Test structure: 10 tests. Pre-commit split: 8 passed, 2 failed. Main commit: spec + test only.
No `ilc_core/` path. No CDL. No ADR.

Commit subject (main): `docs(g8): phase 618 public receipt schema and query contract spec`
Commit subject (backfill): `docs(g8): phase 618 walkthrough and status backfill`

---

### Phase 619 — SENSITIVE (wallet surface; GO token required)

Deliverables:
- `docs/specs/ilc_public_wallet_surface_contract_spec_619_v0.1.md`
- `tests/test_phase_619_public_wallet_surface_contract_spec.py`
- `docs/phases/phase_619_g8_public_wallet_surface_contract_spec_walkthrough.md`
- `docs/phases/STATUS.md`

Test structure: 10 tests. Pre-commit split: 8 passed, 2 failed. Main commit: spec + test only.
No `ilc_core/` path. No CDL. No ADR. No wallet widening.

Commit subject (main): `docs(g8): phase 619 public wallet surface contract spec`
Commit subject (backfill): `docs(g8): phase 619 walkthrough and status backfill`

---

### Phase 620 — NON-SENSITIVE

Deliverables:
- `docs/specs/ilc_window_613_622_coherence_report_620_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v3.3.md`
- `tests/test_phase_620_mvp_gate_synthesis_and_coherence_report.py`
- `docs/phases/phase_620_g8_mvp_gate_synthesis_and_coherence_report_walkthrough.md`
- `docs/phases/STATUS.md`

Test structure: 8 tests. Main commit: coherence report + capsule + test. Backfill: walkthrough + STATUS.md.
No `ilc_core/` path. No CDL. No ADR. Capsule version bump to v3.3.

Commit subject (main): `docs(g8): phase 620 mvp gate synthesis and coherence report`
Commit subject (backfill): `docs(g8): phase 620 walkthrough and status backfill`

---

### Phase 621 — SENSITIVE (window closure gate; GO token required)

Deliverables:
- `tools/run_window_613_622_closure_gate_phase_621.sh` (gate script)
- `tests/test_phase_621_window_613_622_closure_gate.py`
- `docs/specs/ilc_window_613_622_handoff_621_v0.1.md`
- `docs/phases/phase_621_g8_window_613_622_closure_gate_and_handoff_walkthrough.md`
- `docs/phases/STATUS.md`

Test structure: 10 tests. Main commit: gate script + gate test + handoff. Backfill: walkthrough + STATUS.md.
No `ilc_core/` path. No CDL. No ADR.

Commit subject (main): `docs(g8): phase 621 window 613-622 closure gate and handoff`
Commit subject (backfill): `docs(g8): phase 621 walkthrough and status backfill`

---

## 10. Key dependencies and open questions

### Must-resolve at entry

- ADR-0024 is currently Proposed — must be accepted at Phase 614; no Agent Skills work may be committed before Phase 614 GO token is received.
- Phase 612 closure memo is the authoritative governing input for all post-612 work in this window. Any contradiction between a phase prompt and the Phase 612 closure memo must be resolved in favor of the closure memo.
- The wallet boundary from Phase 576 and Phase 581 remains frozen incoming law. No phase in this window may widen it.

### Sequencing constraints

- Phase 613 must be executed before any other phase in this window.
- Phase 614 (ADR acceptance) must precede Phase 615 (Tier 2 scaffold skills) because Tier 2 builds on Tier 1 conventions locked in Phase 614.
- Phase 616 must precede Phase 617 because the lifecycle spec assumes the init/admission contract is stable.
- Phase 617 must precede Phase 618 because receipt schema anchors to the lifecycle contract.
- Phases 616-619 must all be complete before Phase 620 MVP gate synthesis.
- Phase 620 must be complete before Phase 621 closure gate.

### Open questions

1. **Skills/ top-level directory**: does an existing `skills/` directory exist in the repository? If not, the Phase 614 commit creates it. Phase 614 must not assume it exists without checking.
2. **Claude Code auto-discovery**: Phase 614 may optionally configure `.claude/settings.json` to add `skills/` to the additional-directories list, but this is not required per ADR-0024. The phase prompt should note this as an optional enhancement.
3. **MVP gate form**: Phase 620 produces a synthesis verdict. If any of Phases 616-619 has unresolved gaps, Phase 620 must record them explicitly rather than issuing a premature green verdict.

### Permanently deferred

- CDL-062 (sovereign substrate ratification) — blocked per ADR-0028
- Tier 3 skills (skill_node as ILC knowledge node subtype) — deferred per ADR-0024 explicit constraint
- Option B graduation checklist execution — governed by ADR-0028; not opened in this window
- Payment runtime, wallet widening, chain implementation — all remain out of scope

---

## 11. Parallel administrative track

ADR-0024 acceptance (Phase 614) is a parallel administrative track to the spec lane phases (616-619). The two tracks may execute in any order relative to each other, subject to the following constraints:

- Phase 613 (sequence lock) must execute first.
- Phase 614 and Phase 615 may execute before, during, or after Phase 616-619 as long as Phase 613 is complete.
- Phase 620 must wait for both tracks to complete.

---

## 12. Known patterns and technical constraints

### Novel patterns introduced this window

1. **ADR status mutation without CDL mutation (Phase 614)**: This window introduces accepting an ADR that is currently Proposed by changing its Status line. This is a simpler mutation than CDL ratification (no pre-commit hook required) but still requires a GO token and explicit test verification that the ADR now reads "Accepted."

2. **skills/ top-level directory creation**: Phase 614 creates a new `skills/` directory at the repository root. The commit path resolver must list all 7 skill SKILL.md files explicitly by path. No glob patterns — exact path enumeration.

3. **MVP gate synthesis phase**: Phase 620 introduces a gate-synthesis character (not a pure closure gate). Unlike closure gates, it does not run a shell script; it produces a coherence report that reasons over all four spec outputs and either passes or flags gaps. If gaps exist, Phase 620 records them for Phase 622 or later triage.

### Historical prelock hardening

No CDL ratifications occur in this window. Historical prelock hardening is not applicable. Any phase that references a prior CDL's current state must use `git show <commit>:<path>` pattern to read historical state rather than assuming current state.

### Phantom edit guard

No `ilc_core/` files are mutation targets in this window. All phases must assert `not any(p.startswith("ilc_core/") for p in commit_paths)` in their commit path tests.

### Pre-commit hook ilc_core/ clean-state guard

No runtime mutation phases are present. However, all phase test files must include a guard that asserts the main commit touched no `ilc_core/` paths.

### Closure gate selftest guard chain

Phase 621 closure gate must enumerate all prior gate tests in its category 3 selftest guard chain. Read each gate test file explicitly (do not reason by analogy). The full list includes at minimum: test_phase_607, test_phase_612, and all 613-620 test files.

---

## 13. Non-goals and explicitly deferred items

- **No CDL-062 opening**: not authorized by ADR-0028 or Phase 612 closure memo.
- **No wallet widening**: the Phase 576 and Phase 581 read-only wallet boundary is frozen.
- **No payment runtime implementation**: outbound and inbound payment remain out of scope.
- **No chain implementation**: no L1, L2, or rollup work is authorized or scoped.
- **No sovereign substrate selection**: Option D remains the active posture; Option B selection requires explicit satisfaction of the graduation checklist.
- **No Tier 3 skills**: the skill_node research track is explicitly deferred per ADR-0024.
- **No external skill import**: community skills from agentskills.io, SkillsMP, or any other external catalog must not be imported (ADR-0024 exclusion).
- **No new planning sub-lanes**: this window is bounded to the MVP gate spec lane and Agent Skills Tier 1+2. New planning sub-lanes are not authorized.
- **No public Genesis-governance or public minting claims**: the curated testnet boundary from Window 575-584 remains in effect.
- **No harness/product layer expansion** beyond what is authorized in ADR-0026.

---

## 14. Key canonical anchors for prompt drafting

- `docs/specs/ilc_settlement_substrate_closure_and_mvp_gated_replan_612_v0.1.md` — PRIMARY: Phase 612 closure memo (authoritative carry-forward)
- `docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md` — graduation checklist and CDL-062 non-authorization
- `docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md` — receipt and bootstrap discipline
- `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md` — protocol/harness boundary
- `docs/adr/ADR_0024_Agent_Skills_Infrastructure.md` — Agent Skills tiers, skill format, placement (Proposed → Accepted at Phase 614)
- `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md` — wallet boundary (frozen law)
- `docs/specs/ilc_rc0_1_ecu_settlement_wallet_query_integration_581_v0.1.md` — settlement integration boundary
- `docs/specs/ilc_public_receipt_representation_cluster_lock_586_v0.1.md` — receipt cluster (Phase 618 anchor)
- `docs/specs/ilc_public_identity_activation_and_namespace_boundary_lock_587_v0.1.md` — identity activation (Phase 616 anchor)
- `docs/specs/ilc_settlement_linked_public_legitimacy_and_payout_traceability_lock_589_v0.1.md` — settlement legitimacy (Phase 617 anchor)
- `docs/specs/ilc_public_release_claim_and_operator_honesty_package_592_v0.1.md` — public RC honesty (Phase 620 anchor)
- `docs/specs/ilc_constitutional_decision_log_v0.1.md` — CDL register (read-only in this window)
- `docs/phases/STATUS.md` — phase completion log
- For closure gate (Phase 621): all Phase 613-620 test files and artifacts.

---

## 15. Rationale for single-window scope

1. Window 613-622 is the first post-612 execution window. Its primary obligation is to close the MVP gate in spec form before broader public RC claims are made (Phase 612 Section 3 strict requirement).
2. The Agent Skills track (Phases 614-615) is bounded infrastructure work that produces no CDL mutation, no public-participant claims, and no semantic drift risk. It is safe to include in the same window.
3. The MVP gate spec phases (616-619) are four focused documents, each with bounded scope. A single window closure gate at Phase 621 is appropriate.
4. Phases 616, 617, and 619 are SENSITIVE. Human GO tokens are required at each. The window is therefore appropriately gated throughout the sensitive spec work.
5. CDL-062 is not authorized. No CDL mutation phases are needed. The window is narrower than the settlement-substrate window.
6. Tail slot Phase 622 is reserved for overflow only and is not expected to be needed if Phases 616-619 execute cleanly.
