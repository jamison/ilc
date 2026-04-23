# ILC Master Completion Roadmap v0.2

**Date:** 2026-04-23
**Owner lane:** Codex main lane
**Window of publication:** Post-Window 806-810 (inter-window update)
**Supersedes:** `docs/specs/ilc_master_completion_roadmap_v0.1.md`

`master_completion_roadmap_v0_2_published`
`supersedes_v0_1_frontier_claims`

This document is the single human-readable forward-planning roadmap from the
live post-810 frontier through RC candidate and beyond. It supersedes v0.1,
whose frontier claims about rows 7/8, the Option B gate, CDL-017, and the
M-series are now materially stale.

Two authority rules survive unchanged from v0.1 and remain binding:

1. Track B current/next wording comes from the live `STATUS.md` tail rather
   than from capsules, roadmaps, or session memory.
2. Window entries remain artifact-gated. A phase-status line or session note
   does not satisfy a sequence-lock entry gate.

---

## 1. Live frontier (post-Window 806-810)

At the post-810 frontier, the authoritative posture is:

- Capsule `v5.11` is current.
- Window `806-810` is the last closed window.
- The M-series (M-001 through M-022) is **COMPLETE** as of 2026-04-21.
- The Mysticeti convergence window (CW-1 through CW-6) is **CLOSED** (Phase 762).
- The CDL-017 ratification window (763-766) is **CLOSED** (Phase 766).
- `CDL-017` is **RATIFIED** — validator governance framework in force.
- Row `5` remains `spec_closed_runtime_pending` (honest non-closure at CW-2).
- Row `7` is `runtime_closed` (CW-3 + CW-4 both pass).
- Row `8` is `mysticeti_sovereign_row_8_combined_status=pass` (CW-5 + Phase 809
  post-805 re-synthesis).
- `ilc_dag_audit` Tier-1 binary is delivered (Phase 805).
- `verification_tooling_delivery_before_public_deployment=discharged_by_phase_805`.
- Option B gate: `option_b_gate_synthesis_verdict=go_pending_human_authorization`.
- Option B gate conditions: `option_b_gate_conditions=none`.
- Option B selection: **NOT CLAIMED**. Human authorization still required.
- `CDL-062` remains open as a research lane; current evaluation verdict is pass.

The project is further along than v0.1 suggested. The remaining work falls
into five categories described below.

---

## 2. Category A: Option B selection and Mysticeti activation

This is the highest-leverage decision gate. All implementation-side conditions
are discharged. The remaining gate is human authorization.

### 2.1 What "Option B" means at this frontier

Option B means: ILC operates a sovereign BFT consensus substrate (Mysticeti)
rather than the current Option D deferred-substrate bridge. Under ADR-0028,
the graduation checklist must be satisfied and the human must explicitly
authorize the selection. The checklist is at:
`docs/specs/ilc_option_b_graduation_checklist_state_682_v0.1.json`

The rows in that checklist are materially further along than the 682 version
reflects (rows 7 and 8 are now `runtime_closed` / `pass`; row 5 remains
`partial`). ADR-0028 §2 states the checklist must be "satisfied" before
selection. Before Option B can be recorded, ADR-0028 must first be amended to
define what "satisfied" means for a row with an honest fail verdict and a
bounded parallel-obligation plan. That amendment is Phase 812 of Window 811-822.
Row 5 closure remains a required pre-public-RC obligation regardless of the
amendment — the amendment clarifies sequencing, not the obligation itself.

### 2.2 Human conversation required before a window can open

Before Option B can be recorded, two things must happen:

1. **ADR-0028 graduation clause amendment** — A Codex phase must add an
   explicit clause defining what "checklist satisfied" means when a row has an
   honest fail verdict with a documented parallel-obligation plan. This is
   governance work, not a policy override.

2. **Human authorization** — The human must explicitly authorize Option B
   selection. This judgment cannot be delegated to a Codex phase.

Both are handled in Window 811-822 (Phases 812 and 814 respectively).
Human authorization was given on 2026-04-23; the ADR amendment precedes
the selection record so the authorization is constitutionally grounded.

### 2.3 Proposed Window: Option B Selection and Activation Sequence Lock

**Size:** Phases 812-815 within Window 811-822. **Prerequisite:** human
authorization given (2026-04-23); ADR-0028 amendment in Phase 812 precedes
the selection record in Phase 814.

| Phase | Purpose | Research / Decision |
|---|---|---|
| **811** | Sequence lock — lock window constraints | — |
| **812** | ADR-0028 graduation clause amendment — add explicit definition of "partially satisfied" row semantics; add tests | No open decision; amendment text is determined |
| **813** | Checklist v0.2 — reclassify row 5 to `parallel_obligation_acknowledged`; update rows 7/8 to post-convergence verdicts | No open decision |
| **814** | Option B selection record — grounded in amended ADR; update checklist to v0.3 with `option_b_selected: true` | Requires Phase 812-813 committed first |
| **815** | Mysticeti activation scope — name SEC-004 live wiring requirements; name first deployment prerequisites | Open: what does live wiring concretely require? (read epoch_settlement.rs + node.rs) |

**What this window does NOT do:**
- Perform any live settlement-path rotation (that is a later implementation window)
- Authorize first non-Genesis validator deployment (that remains a separate human gate)
- Mutate any CDL row

**What comes after this window:**
- A bounded Mysticeti implementation activation window — scoping SEC-004 live
  wiring, the first validator deployment sequence, and true multi-machine proof.
  This window opens only after human authorization for first deployment.

---

## 3. Category B: Row 5 privacy closure

Row 5 is the only remaining MVP gate condition that is not closed. The honest
verdict from CW-2 is `row_5_runtime_closure_verdict=fail`. Closing row 5
requires two things per the CW-2 carry-forward record:

1. **Log hygiene** — AgentID redaction or equivalent removal of direct sender
   identity from the validator operational log surface.
2. **Transfer privacy** — a real privacy layer for contribution flow (mixing,
   k-anonymity, sealed-sender, or equivalent) sufficient to drive the linkage
   numbers below the closure bands from Phase 740 (`0.45 / 0.60`).

### 3.1 Open decisions before scoping can begin

The following questions require human judgment before a scoping window opens:

- **Which privacy mechanism family to pursue?**
  The three candidates are:
  - *H-013 sealed-sender* — ADR-0034 accepted, but implementation is not
    complete. H-015 gossip activation is blocked on H-013. If sealed-sender
    is chosen as the row-5 transfer privacy mechanism, the H-013
    implementation window and row-5 window would be linked.
  - *k-anonymity style protection* — lower implementation complexity;
    works within current gossip transport without H-013; unclear whether it
    can clear the 0.45/0.60 linkage bands — requires a scoping simulation.
  - *Mixing layer* — high implementation complexity; gold standard; would
    require a new protocol component.

- **Is the Phase 740 closure bar still the right bar?**
  The bar was set before the Mysticeti substrate was fully evaluated. The human
  should confirm that the `0.45 / 0.60` linkage thresholds remain appropriate
  or name a revised target.

### 3.2 Research needed before implementation

Before any implementation window opens, the following scoping research is needed:

- Run a pre-implementation simulation (SIM-LEAKAGE-02 or equivalent) against
  each candidate mechanism family to forecast achievable linkage reduction.
- Assess whether log hygiene alone changes the structural linkage picture
  meaningfully, or whether it is purely operational (the CW-2 record treats them
  as separable layers).
- Assess whether H-013 sealed-sender can be scoped to serve row-5 without
  full D2d gossip activation (partial implementation path).

### 3.3 Proposed Windows for Row 5

**Window B-Scope: Mechanism selection and simulation** (~4-5 phases)

| Phase | Purpose | Open Decision |
|---|---|---|
| **B-1** | Sequence lock | — |
| **B-2** | Privacy mechanism family analysis — read existing SIM results, assess H-013 partial path vs k-anonymity; produce a recommendation | Human: confirm or override mechanism recommendation |
| **B-3** | SIM-LEAKAGE-02 pre-implementation simulation against the selected mechanism family | Requires: mechanism family chosen in B-2 |
| **B-4** | Mechanism selection lock — record the chosen mechanism with explicit linkage-reduction projection; scope the implementation obligation | Human gate: accept or reject the simulation projection as sufficient |
| **B-5** | Coherence and closure | — |

**Window B-Impl: Row 5 implementation** (after mechanism selected; ~4-6 phases
depending on mechanism choice)

| Phase | Purpose |
|---|---|
| **B-I-1** | Sequence lock |
| **B-I-2** | Log hygiene implementation — AgentID redaction in validator operational logs |
| **B-I-3 to B-I-N** | Privacy layer implementation (scope depends on mechanism choice) |
| **B-I-N+1** | SIM-LEAKAGE-03 execution against implemented mechanism |
| **B-I-N+2** | Row 5 runtime-closure evaluation — pass or honest fail |
| **B-I-N+3** | Coherence and closure |

If row 5 closes in this window, the Option B graduation checklist becomes
complete and the full post-launch story improves materially.
If it fails again, the result must be recorded honestly. Row 5 non-closure
does not block Option B selection or Mysticeti implementation activation.

---

## 4. Category C: TLA+ pre-RC items

These are bounded, well-defined technical tasks with no open governance
decisions. They do not block Option B selection or row 5 work. They are
pre-RC hardening that strengthens the audit story.

From the TLA+ gap analysis (`docs/research/ilc_tla_plus_gap_analysis_v0.1.md`):

| Item | Effort | Value | Status |
|---|---|---|---|
| TLA-PRE-1: Widen Spec A MaxRound 5→12, re-run TLC | Low | Medium | Pending |
| TLA-PRE-2: Spec C — partition/heal recovery spec (M-015 scenario) | Medium | High | Pending; M-019 deferred TODO on SafetyNoDualCert is the primary input |
| TLA-PRE-3: Informal refinement notes for Spec A and Spec B | Low | Medium | Pending |

**Note on M-019 deferred TODO:** The SafetyNoDualCert invariant was deferred in
M-019 because a TLA+ spec for it did not exist. Spec C partially addresses
this. The M-019 deferred TODOs doc (`memory/m019_deferred_todos.md`) names this
as an open item for M-020+ disposition — it has not been formally resolved.

### 4.1 Proposed Window: TLA+ Pre-RC Hardening (~4 phases)

| Phase | Purpose |
|---|---|
| **C-1** | Sequence lock |
| **C-2** | TLA-PRE-1: Widen MaxRound to 12, re-run TLC, record result |
| **C-3** | TLA-PRE-2: Spec C partition/heal spec — write the spec, run TLC, record result; also disposition the SafetyNoDualCert deferred item from M-019 |
| **C-4** | TLA-PRE-3: Refinement notes for Spec A and Spec B; coherence report; closure gate |

**No human conversation required** for this window. The TLA-PRE items are
engineering carry-forward.

---

## 5. Category D: Deferred infrastructure (non-blocking, named)

These items are real obligations that must not be silently forgotten but do not
block any of the above windows.

### 5.1 DAG Audit Tier 2 (verify-dag-archive)

The Tier-2 archive mode design is in Appendix A of the Phase 803 CLI design
spec. It requires new LMDB tables (`dag_vertices`, `commit_wave_membership`),
an archive-node mode for the validator harness, and the `verify-dag-archive`
subcommand.

**Trigger:** `tier2_trigger=pre_external_security_audit_engagement`

This does not open before an external security audit is engaged. It is not
a current window candidate.

### 5.2 Legal positioning memo

A counsel-facing memo summarizing the passive ECU attribution/decay/treasury/
validator-parameter economic facts package remains unwritten.

**Trigger:** Required before broader public RC claims. Not a gate for Option B
selection or Mysticeti activation.

### 5.3 SEC-007a — protoc vendoring (build hygiene)

The `build.rs` proto compilation depends on a system `protoc` binary. The
long-term fix requires upgrading `tonic` + `tonic-build` from 0.11 → 0.13+
to use `protox`. This is maintenance, not a functional gap.

**Trigger:** Pre-RC cleanup window. Can be bundled into any future
maintenance window.

### 5.4 H-013 sealed-sender implementation + H-015 gossip activation

ADR-0034 is accepted. H-013 implementation is not complete. H-015 gossip
activation is blocked on H-013. If H-013 is chosen as the row-5 privacy
mechanism (see Category B), these tracks merge. If row-5 uses a different
mechanism, H-013/H-015 remain a later post-RC research lane.

**Open decision:** see Category B §3.1.

### 5.5 External security audit engagement

The external security audit is a named post-RC obligation. It triggers:
- Tier-2 dag_audit work,
- TLAPS unbounded liveness proof (TLA-POST-2),
- post-audit hardening carry-forward.

No pre-engagement action is currently open.

---

## 6. Post-RC research lanes

These do not block RC or any of the above windows. They are named so they
are not silently dropped.

### 6.1 CDL-062 sovereign-substrate research lane

`CDL-062` remains open. The current evaluation verdict is `pass` (Phase 808
post-805 re-synthesis). It does not activate merely because Option B is
selected. A separate human gate governs CDL-062 admissibility.

The admissibility path: rows 5, 7, and 8 must be honestly closed or locked
such that the lane is not opening into a privacy, censorship, or constitutional
vacuum. Rows 7 and 8 are now past that bar. Row 5 is not yet closed.

### 6.2 TLA+ post-launch items

| Item | Trigger |
|---|---|
| TLA-POST-1: Spec D (EpochSettlementTx shared-object path) | Post-launch audit hardening |
| TLA-POST-2: TLAPS unbounded liveness proof | Post-launch audit hardening |
| TLA-POST-3: Economic protocol specs (treasury, ECU governor, node-transfer) | Post-launch |

### 6.3 L3 app-development lane

Remains post-convergence. Not a current window candidate.

### 6.4 Morphogenetic hypergraph (H-series Tier 3)

Hypergraph Tier 3 activation remains blocked on its own prerequisites from
capsule v5.10. ADR-0031 accepted; ADR-0029/0030 proposed; H-013/H-015 carry-
forward as above. The lane is outside the critical path.

---

## 7. Human conversation gates — live inventory

The following judgments still require explicit human review and must not be
misrepresented as code-decided:

| Gate | Current status | Blocks |
|---|---|---|
| ADR-0028 graduation clause amendment | **In Window 811-822 (Phase 812)** — must precede selection record | Option B selection record (Phase 814) |
| Option B selection authorization | **AUTHORIZED 2026-04-23** — grounded in Phase 812 amendment | Phase 814 selection record |
| First non-Genesis validator deployment authorization | Not yet (follows Option B selection and Mysticeti activation sequence lock) | First validator deployment |
| Row 5 privacy mechanism choice | **OPEN** — H-013 vs k-anonymity vs mixing | Window B-Scope |
| Whether Phase 740 closure bar remains the correct bar | **OPEN** — not revisited since CW-2 | Window B-Scope |
| CDL-062 admissibility | Deferred — row 5 non-closure is still a consideration | CDL-062 activation window |
| External security audit engagement timing | Deferred — post-RC | Tier-2 dag_audit; TLA-POST items |

---

## 8. Proposed window sequence (indicative)

The following sequence is indicative. Human gates marked with `[HG]` must be
cleared in conversation before the window can open. Windows with no `[HG]`
can open at any time on Codex authorization.

| Order | Window | Size | HG required? | Prerequisite |
|---|---|---|---|---|
| 1 | **Window 811-822** — ADR amendment, Option B selection, TLA+, SEC-007a/b | 12 phases | Yes — Option B authorization (given 2026-04-23) | ADR amendment (Phase 812) precedes selection record (Phase 814) |
| 2 | **Row 5 Mechanism Scoping** (Category B-Scope) | ~5 phases | Yes — mechanism choice, closure bar confirmation | Can run after or in parallel with Window 811-822 |
| 3 | **Mysticeti Implementation Activation** (follows Window 811-822) | ~4-6 phases | Yes — first deployment authorization | Window 811-822 Phase 815 scope completed |
| 4 | **Row 5 Implementation** (Category B-Impl) | ~6-8 phases | No | Window B-Scope mechanism locked |
| 5 | **Legal positioning memo** | ~2-3 phases | No | Row status stable enough for public-claims framing |

Windows 1 and 3 can run independently or concurrently. Window 2 requires
the human Option B decision first. Window 4 requires Window 2 plus a
second human gate (first deployment). Window 5 requires Window 3.

---

## 9. What this roadmap does not claim

- Option B selection (human authorization not yet provided)
- Row 5 closure (mechanism not yet chosen; implementation not done)
- First non-Genesis validator deployment
- Settlement-path rotation activation
- Any CDL mutation
- Production readiness (external security audit not yet engaged)
