# ILC Codex B-5 Commissioning Brief
**Date:** 2026-04-24
**From:** Local reviewer (Claude Code / Claude Sonnet 4.6)
**To:** Codex (GPT-4.1 → GPT-5.5 transition brief included)
**Re:** B-5 mechanism lock, B-Impl commissioning spec, model transition supplement

---

## 0. Read this first — your B-4 context is superseded

When you stopped at the B-4 hold point (commit `05899be1`), you had run a
**formula-based simulation** and recommended **mixing** as the primary mechanism
family with bars A≤0.30, B≤0.45, C≤0.40.

That recommendation is fully superseded. The local reviewer ran four FIX
iterations replacing the formula harness with real Monte Carlo simulation,
which reversed the family ranking entirely. Summary of corrections:

**FIX-1** — Real Monte Carlo pipeline replaced formula functions in
`tools/testbed/sim_leakage_autoresearch.py`. Family ranking reversed: k-anonymity
dominates the Pareto frontier; mixing is Pareto-dominated. New simulation-derived
bar: A≤0.15, B≤0.15, C≤0.05.
Evidence: `docs/research/ilc_sim_leakage_02_autoresearch_results_b3_fix1_v0.1.md`
Recommendation: `docs/specs/ilc_row5_mechanism_selection_recommendation_b4_fix1_v0.1.md`

**FIX-2** — Added settlement timing metrics, rolling threshold release, long-tail
distributions, bounded_hold carry-over. Key finding: rolling threshold k-anonymity
is fast (p95=1ep) but exposes Variant C recall=0.82–0.99 under non-uniform
distributions — group-formation timing is itself a fingerprint.
Evidence: `docs/research/ilc_sim_leakage_02_autoresearch_results_b3_fix2_v0.1.md`
Recommendation: `docs/specs/ilc_row5_mechanism_selection_recommendation_b4_fix2_v0.1.md`

**FIX-3** — Added `release_jitter_epochs` to rolling threshold. Completed groups
are deferred rng(0..J) additional epochs before settlement is published. J=3 is
the phase-transition point: Variant C drops 0.82→0.030 while maintaining p95=3ep.
This is the **current primary recommendation**.
Evidence: `docs/research/ilc_sim_leakage_02_autoresearch_results_b3_fix3_v0.1.md`
Recommendation: `docs/specs/ilc_row5_mechanism_selection_recommendation_b4_fix3_v0.1.md`

**FIX-4** — k=20 fallback evidence run (answers B-4 Q4). k=20+jitter=3 clears all
bars: A=0.050, B=0.050, C=0.045, p95=3ep, metric=0.111. J=3 phase transition
confirmed at k=20. Fallback activation criterion established.
Evidence: `docs/research/ilc_sim_leakage_02_autoresearch_results_b3_fix4_v0.1.md`

**Rust groundwork (outside B-scope sequence lock, do not re-implement):**
`TransferClass` enum and `ExpressConsent` struct added to
`ilc_consensus/src/types.rs`. `ECUTransfer` now carries `transfer_class:
TransferClass` covered by BLS sender signature. All construction sites updated
across `fast_path.rs`, `node.rs`, `balance_store.rs`, `network.rs`,
`testnet_client_main.rs`. 83 tests passing.

---

## 1. B-4 Hold Point — all four questions answered

Q1: Accept k=30, rolling_threshold, jitter=3, bounded_hold as the mechanism?
**YES. Adopted.**

Q2: Is p95≤3 minutes acceptable UX, or is 1 minute required?
**3 minutes is acceptable.** k=30+jitter=3 is the primary recommendation.
Mixing pool=32+delay=1 (p95=1ep, A=0.091, C=0.005) remains documented as
the alternative only if 1-minute p95 becomes a hard requirement.

Q3: Simulation-derived bar A≤0.15, B≤0.15, C≤0.05 confirmed as B-Impl target?
**YES.** Pending live confirmation via SIM-LEAKAGE-03.

Q4: Should FIX-4 explore k=20+jitter before locking?
**YES — FIX-4 has been run.** k=20+jitter=3 is confirmed viable (see §0 above).
Fallback activation: if k=30 fill-failure rate >5% of windows within 1.5×max_wait,
reduce k to 20. No CDL amendment required.

Token to emit: `row5_mechanism_selection_human_gate_closed`

---

## 2. Complete mechanism comparison table

| Mechanism | A | B | C | p95 | Metric | Status |
|---|---:|---:|---:|---:|---:|---|
| k=30, rolling, jitter=3 | 0.033 | 0.033 | 0.030 | 3 ep | 0.074 | **PRIMARY** |
| k=20, rolling, jitter=3 | 0.050 | 0.050 | 0.045 | 3 ep | 0.111 | **FALLBACK** |
| k=15, rolling, jitter=3 | 0.067 | 0.067 | 0.025 | 4 ep | 0.148 | Reserve |
| mixing pool=32, delay=1 | 0.091 | 0.084 | 0.005 | 1 ep | 0.186 | Alt if 1-min p95 required |
| k=20, epoch-aligned, drop | 0.060 | 0.046 | 0.005 | 5 ep | 0.103 | Superseded (FIX-1) |
| k=20, rolling, jitter=0 | 0.050 | 0.050 | 0.824 | 1 ep | 1.831 | Not viable |
| mixing (formula-based) | 0.252 | 0.440 | 0.374 | — | — | Formula artifact, superseded |

---

## 3. B-5 required deliverables

**3.1 — B-4 FIX-3 hold point closure record**
Document or section within the B-5 closure that records the Q1–Q4 answers above.
Token: `row5_mechanism_selection_human_gate_closed`

**3.2 — B-5 mechanism lock document**
File: `docs/specs/ilc_row5_mechanism_selection_lock_b5_v0.1.md`

Must contain:
- Locked primary: k=30, rolling_threshold, release_jitter_epochs=3, bounded_hold,
  max_wait=3–5 epochs
- Locked fallback: k=20, rolling_threshold, release_jitter_epochs=3, bounded_hold,
  max_wait=3 — activate if k=30 fill-failure rate >5%
- Simulation-derived bar (B-Impl target): A≤0.15, B≤0.15, C≤0.05 — pending
  SIM-LEAKAGE-03 live confirmation
- Settlement timing at volume: p50≈1.5ep, p95≈3ep (jitter-dominated floor, not
  throughput-limited — the correct architectural property)
- Two-tier privacy lanes adopted:
  - `Contribution` transfers → mandatory privacy lane (k-group queue), no opt-out.
    Anonymity set is collective; one opt-out degrades the batch for all members.
  - `Payment` transfers → privacy-default (same queue); express opt-out to
    immediate settlement via `ExpressConsent { agent_acknowledged_timing_disclosure:
    bool, consent_epoch: EpochSeq }` — per-transfer, epoch-scoped, not permanent
- Reference: `TransferClass`/`ExpressConsent` already implemented in
  `ilc_consensus/src/types.rs` (local reviewer, 2026-04-24; do not re-implement)
- Non-claims: Row 5 remains `spec_closed_runtime_pending`; this lock does not
  claim runtime closure; does not authorize Option B graduation; does not ratify
  any CDL

**3.3 — B-Impl commissioning spec**
File: `docs/specs/ilc_row5_b_impl_commissioning_spec_v0.1.md`

Six implementation obligations (from FIX-3 recommendation §6):
1. Rolling group construction integrated into the transfer submission path. Entry
   point: `handle_broadcast_honest` in `ilc_consensus/src/node.rs` — read
   `transfer_class` to route `Contribution` and privacy-default `Payment`
   transfers into the k-group accumulator; `Payment { express: Some(...) }` with
   `agent_acknowledged_timing_disclosure: true` bypasses to fast-path directly.
2. Deferred release queue with jitter scheduling. Data structure:
   `Vec<(release_epoch: EpochSeq, transfers: Vec<ECUTransfer>, contributors: Vec<AgentID>)>`.
   When a k-group completes: `release_epoch = current_epoch + rng.randint(0, J)`.
   Queue is flushed on each epoch tick.
3. bounded_hold carry-over with max_wait enforcement. Transfers that cannot fill
   a complete k-group within max_wait epochs are force-released with whatever
   partial group has formed (not single-contributor release — that would degrade
   privacy further).
4. Group-fill monitoring: emit metric alert if k=30 groups fail to fill within
   1.5×max_wait. Activate k=20 fallback automatically at >5% failure rate.
5. Force-release degraded-anonymity notification: contributors whose transfer
   settled via force-release must receive a flag indicating the anonymity set
   was smaller than k. (Notification path to be defined in B-Impl Phase 3.)
6. Live instrumentation for SIM-LEAKAGE-03: expose per-epoch metrics including
   group fill rate, jitter distribution observed, force-release count, and
   anonymity-set size histogram per settled batch. These metrics are what
   SIM-LEAKAGE-03 will consume against the M-009 testbed to confirm the live
   system meets the A≤0.15/B≤0.15/C≤0.05 bar.

Note: B-Impl Phases 1–3 are being executed by the local reviewer (Claude Code),
not Codex. Codex owns the commissioning spec document only. The Rust implementation
is not a B-5 deliverable.

**3.4 — STATUS.md and PLANNING_INDEX.md advance**
- Append Phase B-5 entry to `docs/phases/STATUS.md`
- Advance `docs/PLANNING_INDEX.md`: B-scope closed, mechanism locked,
  B-Impl commissioned, Row 5 remains `spec_closed_runtime_pending`
- Do NOT advance Row 5 to runtime_closed

**3.5 — Coherence check and capsule advance**
- Brief coherence check confirming B-scope closure is internally consistent
- Find the most recent capsule: `docs/specs/ilc_antigravity_context_capsule_v*.md`
  and produce the next version
- Capsule must accurately reflect: B-scope closed, k=30+jitter=3 locked,
  TransferClass groundwork complete, Row 5 still spec_closed_runtime_pending,
  B-Impl commissioned to local reviewer, CDL-017 ratification window pending

**3.6 — Model transition rehydration supplement (NEW — read §4)**
File: `docs/specs/ilc_codex_model_transition_supplement_b5_v0.1.md`
See §4 for full specification.

---

## 4. Model transition supplement (GPT-5.4 → GPT-5.5)

After B-5 commits, the operator will switch Codex from GPT-4.1/5.4 to GPT-5.5.
The transition supplement is a concise rehydration document structured for a fresh
GPT-5.5 instance with no prior project context. It should be self-contained and
cover:

**4.1 — Correction record (critical)**
The single most important thing for GPT-5.5 to know is that Codex's last committed
B-4 recommendation (mixing, A≤0.30) is superseded. The supplement must state this
explicitly with the correction: k-anonymity with jitter=3 is the locked mechanism,
and the four FIX runs (FIX-1 through FIX-4) are the evidence chain.

**4.2 — Current constitutional posture (one table)**

| Item | Status |
|---|---|
| Row 5 | spec_closed_runtime_pending (B-scope closed, mechanism locked) |
| Row 7 | runtime_closed (convergence window Phase 762) |
| Row 8 | inherited criteria lock, no candidate evaluated |
| ADR-0028 | Option D active; Option B gate no-go (rows 5+7 runtime required) |
| CDL-017 | OPEN — prelock evidence committed; ratification window pending |
| Capsule | v5.x (check actual version after B-5 produces it) |

**4.3 — CDL-017 ratification entry conditions**
CDL-017 covers: epoch binding for TransferCertificate; validator set rotation
governance; SEC-004 closure. Prelock evidence exists. Ratification window is the
next Codex task after B-5.

**4.4 — B-Impl parallel track status**
Local reviewer (Claude Code) is implementing B-Impl Phases 1–3 in Rust in parallel.
GPT-5.5 does not need to execute B-Impl. GPT-5.5's next task after CDL-017 is the
Row 5 runtime closure evaluation window, which only opens after B-Impl is complete
and SIM-LEAKAGE-03 has run on the M-009 testbed.

**4.5 — Format requirements**
- Max 2 pages (the supplement is an entry document, not a full capsule)
- Each section should be readable cold by a model that has not seen any prior
  ILC conversation
- Include the capsule version number and date so GPT-5.5 can locate the full
  context pack if needed

---

## 5. What B-5 must NOT do

Per the B-1 sequence lock (`docs/specs/ilc_phase_b1_b5_sequence_lock_v0.1.md`):
- Do NOT claim Row 5 is runtime_closed
- Do NOT implement Rust (that is B-Impl, local reviewer)
- Do NOT open or mutate any CDL
- Do NOT claim Option B is graduated
- Do NOT run SIM-LEAKAGE-03

---

## 6. After B-5: what Codex (GPT-5.5) does next

1. **CDL-017 ratification window** — prelock evidence already committed;
   this is the first task for the new model
2. **Row 5 runtime closure evaluation** — only opens after local reviewer
   completes B-Impl Phases 1–3 and SIM-LEAKAGE-03 results are committed
3. **Option B graduation gate** — requires rows 5 and 7 both runtime_closed

The operator will brief GPT-5.5 using:
- The capsule produced in B-5 §3.5
- The transition supplement produced in B-5 §3.6
- The CDL-017 prelock evidence already in tree

---

## 7. Key file references

| Purpose | File |
|---|---|
| Primary B-4 recommendation (read first) | `docs/specs/ilc_row5_mechanism_selection_recommendation_b4_fix3_v0.1.md` |
| FIX-4 fallback evidence | `docs/research/ilc_sim_leakage_02_autoresearch_results_b3_fix4_v0.1.md` |
| B-scope sequence lock | `docs/specs/ilc_phase_b1_b5_sequence_lock_v0.1.md` |
| FIX-1 evidence | `docs/research/ilc_sim_leakage_02_autoresearch_results_b3_fix1_v0.1.md` |
| FIX-2 evidence | `docs/research/ilc_sim_leakage_02_autoresearch_results_b3_fix2_v0.1.md` |
| FIX-3 evidence | `docs/research/ilc_sim_leakage_02_autoresearch_results_b3_fix3_v0.1.md` |
| Rust groundwork (reference only) | `ilc_consensus/src/types.rs` |
| STATUS.md tail | `docs/phases/STATUS.md` |

---

Proceed directly to producing the B-5 deliverables listed in §3.
Do not ask for further confirmation — all hold-point questions are answered in §1.
