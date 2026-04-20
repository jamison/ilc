# ILC Window 749-752 Guidance v0.1

**Prepared by:** Claude (architectural review lane)
**Date:** 2026-04-20
**For:** Codex
**Capsule at open:** v5.3
**Frontier at open:** Window 745-748 CLOSED; Window 749-752 is the next
main-lane continuation

---

## 1. Window purpose

Window 749-752 has one job: consolidate the planning canon into a single
human-readable master completion roadmap, retire stale multi-window planning
docs whose narrative has been overtaken, and update the M-series implementation
lane document to reflect current state and adopted Q1-Q4 decisions.

This window does not open the convergence window. It does not execute M-track
work. It does not claim any row closure, CDL ratification, or Option B
graduation. It is a documentation and planning-surface consolidation window
only.

The outputs of this window give a human reader — or any future agent — a single
document they can follow from the current frontier through to RC candidate,
without needing to cross-reference five partially stale planning artifacts.

Primary source anchors:

- `docs/specs/ilc_antigravity_context_capsule_v5.3.md`
- `docs/specs/ilc_window_745_748_closure_gate_748_v0.1.md`
- `docs/specs/ilc_mysticeti_convergence_window_commissioning_spec_746_v0.1.md`
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.4.md`
- `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`
- `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md`
- `docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md`

---

## 2. Role context

**Gemini** continues M-track execution (M-021 next, then M-022). Gemini
produces first-pass artifacts. Claude performs adversarial audit and applies
fixes. The operator gates each phase.

**Codex** executes all main-lane planning and constitutional work. The
convergence window, CDL-017 ratification, and post-convergence windows are
Codex lanes.

**"Owner: Gemini"** language in the M-series doc should be updated to
**"Owner: Gemini (execution) / Claude (audit)"** to reflect the current
pattern. Do not reassign M-track execution to Codex — Gemini holds the
implementation continuity from M-001 forward.

---

## 3. In scope

### 3.1 Master completion roadmap (new document)

Create `docs/specs/ilc_master_completion_roadmap_v0.1.md`.

This is the primary output of this window. It must cover the complete remaining
sequence in order, from the current frontier through to RC candidate, in a
form a human can follow without cross-referencing other documents.

Required sections and content:

**Section 1 — Current frontier**
One paragraph: what is complete, what is commissioned-but-not-open, what is
still pending. Bind to STATUS.md Track B line and capsule v5.3. As of window
open: M-020 complete, M-021 next; convergence window commissioned but not open;
rows 5 and 7 spec_closed_runtime_pending; row 8 inherited; CDL-017 open;
Option B deferred.

**Section 2 — M-track remaining (Gemini execution / Claude audit)**

Two phases:

M-021 — SIM-LEAKAGE-01 + security fix verification (+ conditional audit remediation):
- Primary obligation: SIM-LEAKAGE-01 execution per Phase 740 commissioning
  spec. Three attacker variants required: operator-path, hosted-query,
  repeated-contributor. Pass criteria: ordinary-observer / hosted-query
  linkage recall ≤ 0.45; operator-path linkage recall ≤ 0.60. Observability-
  floor mapping required. Raw numbers and methodology required — not just the
  verdict.
- Secondary obligation: verify three committed security fixes (CRIT-001 at
  commit `16147c2b`, HIGH-002 comment at same commit, TEST-002 port correction
  at same commit) are correctly applied. Add explicit HIGH-001 note to audit
  brief §5: in-memory equivocation detection is not LMDB-persisted, but
  `balance_store` LMDB version locking is the durable double-spend barrier.
  This two-layer defence is the correct architecture; document it explicitly.
- Conditional obligation: external audit remediation. If an external security
  audit has been engaged and findings exist at M-021 execution time, all
  Critical and High findings must be addressed with explicit dispositions and
  the Phase 690 workloads re-run on any remediated code. If no external audit
  findings exist, this obligation remains pending and is noted as such in the
  M-021 results. The master roadmap must preserve this conditional path, not
  erase it.
- Note: testbed uses `--features testnet_fault_sim` build as before. CRIT-001
  does not change the measurement surface.
- Deliverable: `docs/research/ilc_sim_leakage_01_results_M021_v0.1.md`
- Gate: Claude adversarial audit of results artifact before operator approval.

M-022 — Exitability drill + handoff package:
- Primary obligation: strong exitability drill per Phase 741 §4 contract.
  Four steps in sequence: (1) export LMDB state from a running validator,
  (2) independently verify from exported data only — no calls to the original
  validator, (3) replay on a fresh node from the exported state, (4) migrate
  without calling any original-operator API. Physical evidence required: actual
  exported file path, actual replay log with epoch numbers, fresh-node startup
  log. A results document that asserts "drill passed" without physical evidence
  is not a passing artifact.
- Secondary obligation: handoff package per existing M-022 scope in the M-series
  doc. This includes CDL-017 implementation notes, SEC-004 disposition, Phase
  690 final results, TLA+ verification summary, audit brief and remediation
  summary, open items list, integration notes, first validator deployment
  prerequisites checklist.
- SEC-004 note: TransferCertificate epoch/validator-set historical binding is
  documented as a CDL-017 activation-scope implementation item, not silently
  assumed solved by static validator sets.
- Deliverable: `docs/research/ilc_mysticeti_gemini_lane_handoff_M022_v0.1.md`
- Gate: Claude final approval triggers convergence window open.

**Section 3 — Convergence window (Codex, six phases)**

This section summarizes the six-phase budget from the commissioning spec
(`ilc_mysticeti_convergence_window_commissioning_spec_746_v0.1.md`) and states
the entry conditions. Do not re-specify the commissioning spec — point to it
as the authority. State clearly: window does not open until all three artifact
classes exist and are re-verified by the convergence sequence lock.

Entry artifact classes:
1. Row-7 censorship bundle — `ilc_row_7_runtime_evidence_package_bundle_M020_v0.1.md` (EXISTS)
2. SIM-LEAKAGE-01 results — `ilc_sim_leakage_01_results_M021_v0.1.md` (M-021 obligation)
3. Exitability drill results — within `ilc_mysticeti_gemini_lane_handoff_M022_v0.1.md` (M-022 obligation)

Six-phase summary (from commissioning spec):
- CW-1: Convergence sequence lock + artifact re-verification
- CW-2: Row 5 runtime closure evaluation (SIM-LEAKAGE-01 results)
- CW-3: Row 7 censorship-resistance runtime closure evaluation (M-020 bundle)
- CW-4: Row 7 strong-exitability runtime closure evaluation (M-022 drill results)
- CW-5: Row 8 disposition + Option B graduation-gate synthesis under ADR-0028
- CW-6: Coherence report + successor capsule + closure gate

**Section 4 — CDL-017 ratification window (Codex, separate from convergence)**

This is a separate bounded Codex window that opens after the convergence window
closes, not inside it. Content:
- CDL-017 ratification using M-022 implementation notes plus convergence
  row evidence as the basis. The Codex-side prelock evidence is already
  complete (Window 733-738). What remains is the M-022 implementation handoff
  confirming what the Rust validator governance scaffolding provides and what
  ratification must activate.
- SEC-004 activation: after CDL-017 is ratified, `TransferCertificate` gains
  `epoch: EpochSeq`; `execute_certificate` resolves the historically active
  `ValidatorSet` per epoch. This is an implementation task owned by the M-track
  after ratification — not a Codex coding task.
- First authorized validator deployment: **explicit human gate**. Not
  automated. Not implied by CDL-017 ratification. Requires operator sign-off.
- True multi-machine provisioning: cert/key distribution, remote binary
  placement, multi-operator evidence capture. These are engineering tasks that
  follow the deployment authorization.

**Section 5 — Pre-RC obligations (parallel / non-blocking)**

Items that must exist before broader public RC claims but do not block the
convergence window or CDL-017 ratification:
- Legal positioning memo (passive ECU attribution rate 0.20, decay floor 0.05,
  attribution cap 0.15, CDL-054/055/056 Howey analysis inputs). Not yet written.
  Explicitly deferred non-gate carry-forward. Write before broader public RC
  claims.
- SEC-007a (protoc-bin-vendored / tonic 0.13+ upgrade): self-contained
  maintenance, non-blocking, can happen any time.

**Section 6 — Post-convergence research lanes (non-blocking to RC)**

Name these explicitly as later, not on critical path:
- CDL-062 (sovereign substrate research lane): opens only after rows 5, 7-9
  closed or locked, row 5 narrowed, CDL-062 admissibility human gate cleared.
  Post-RC or late-RC.
- L3 app development program: post-convergence, when sovereign substrate is
  stable. Spec exists at `docs/specs/ilc_l3_app_sidecar_and_homoiconic_object_model_note_v0.1.md`.
- Morphogenetic hypergraph research lane: post-mainnet. ADR-0029/0030 proposed;
  SIM-HYPEREDGE-01/SPECTRAL-01/EMBED-01/BEACON-01/ROUTING-01 registered but not
  commissioned. ADR-0031 is now accepted (Phase 746) — the pre-M-018 gate is
  closed. Remaining items are post-mainnet.

**Section 7 — Human conversation gates**

These decisions are not code-only calls. List them explicitly so they are not
forgotten or assumed-resolved:
- What counts as enough censorship resistance for row 7 (convergence CW-3)
- What "independence from external constitutional centers" means for row 8
  (convergence CW-5)
- How much privacy is enough for row 5 without making the system unverifiable
  (convergence CW-2)
- Whether CDL-062 is admissible yet (post-convergence planning gate)
- Final Option B selection (convergence CW-5 synthesizes the gate; selection
  is a human decision)
- First authorized validator deployment (CDL-017 window — explicit human gate)

### 3.2 M-series implementation lane document update

Update `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`
in place. No new file. Changes required:

1. **Remove the estimated timeline line** at approximately line 1112:
   `"Estimated elapsed time with LLM-augmented development: 4-6 months..."`.
   Remove the entire sentence. It is not realistic and not informative.

2. **Update M-021 scope** to reflect Q1 adoption while preserving the
   conditional external-audit remediation branch:
   - Primary: SIM-LEAKAGE-01 execution (Phase 740 commissioning spec governs).
     Raw numbers and methodology required, not just verdict.
   - Secondary: verify three committed security fixes (CRIT-001/HIGH-002/TEST-002
     at `16147c2b`); add HIGH-001 explicit note to audit brief §5.
   - Conditional: external audit remediation remains a parallel M-021 obligation
     if an external audit has been engaged and findings exist. Do not erase this
     branch from the M-series doc — update it to note that no external findings
     exist yet at M-021 open, so the obligation is pending-if-activated.
   - Update Claude audit checklist: add item for HIGH-001 two-layer defence
     documentation; add item requiring methodology + raw numbers in results doc;
     preserve the existing external-audit remediation checklist item as
     conditional (applicable only if external findings exist).
   - Update "Owner: Gemini" to "Owner: Gemini (execution) / Claude (audit)".

3. **Update M-022 scope** to reflect Q2 adoption:
   - Clarify: M-022 = exitability drill (primary) + handoff package (secondary).
     Exitability drill results are what unlock CDL-017 ratification in the
     convergence window. CDL-017 ratification is not a separate Gemini phase;
     it is a Codex convergence-window action consuming M-022 results as input.
   - The "M-022 handoff" language in older artifacts means "Gemini produces
     the runtime evidence that CDL-017 ratification requires." That evidence
     IS the exitability drill results plus the implementation notes in the
     handoff package.
   - Add to Claude final approval checklist: physical exitability drill evidence
     required (actual file paths, actual epoch numbers in replay log, fresh-node
     startup log). Assertion without evidence is not a passing artifact.
   - Update "Owner: Gemini" to "Owner: Gemini (execution) / Claude (audit)".

4. **Fix the orphaned checklist block** at approximately line 1011-1013.
   There is a `**Claude audit checklist:**` header followed immediately by
   `**Owner:** Gemini (draft) + Claude (final approval gate)` — this is
   the M-022 block missing its phase header. Add `### M-022 — Gemini Lane
   Handoff Package + Exitability Drill` before that block.

5. **Update §6 security deferred items tracking summary** at line 1279:
   - SEC-009: mark CLOSED (M-018 `19efe35d`) — already closed; confirm in table
   - Add SEC-010: CLOSED (M-020 / `16147c2b`) — EpochSettlementTx handler
     gated to testnet_fault_sim; production builds reject message type
   - HIGH-002: add row — documented in code comment at `16147c2b`; known
     liveness limitation (all-N vs 2F+1 quorum); production fix deferred
   - HIGH-001: add row — in-memory equivocation detection; durable barrier is
     LMDB version locking in balance_store; two-layer defence, no fix required

6. **Update summary timeline table** at line 1086:
   - M-009 through M-020: mark all as COMPLETE with commit refs where known
   - M-021: update scope note (SIM-LEAKAGE-01 primary + security fix verification)
   - M-022: update scope note (exitability drill primary + handoff package)

### 3.3 Stale document retirement

Three documents require action. Do not delete — archive by adding a stale
header and a pointer to the successor. No content may be silently lost;
anything still load-bearing must be confirmed as covered in the master roadmap
before archiving.

**`docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md`**

Add at top of file:

```
> **ARCHIVED 2026-04-20.** This document covered Windows 701-726. Its
> forward-looking content (convergence window definition, integration rules,
> L3 and hypergraph deferred programs) is now carried in
> `docs/specs/ilc_master_completion_roadmap_v0.1.md`. The window-by-window
> narrative (§1-5.5) is complete history. Do not consult for current planning.
```

Confirm before archiving that the following content from §5.6, §6, §7.1, and
§8 is explicitly covered in the master roadmap:
- Mysticeti convergence window definition and trigger (now covered by
  commissioning spec + master roadmap §3)
- Integration rules — artifact-gate authority, TODO.txt carry-forward block,
  no doctrinal citations as constitutional proof (covered in master roadmap
  constraints)
- L3 app development program (covered in master roadmap §6)
- Morphogenetic hypergraph research lane deferred items (covered in master
  roadmap §6)

**`docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md`**

Add at top of file:

```
> **ARCHIVED 2026-04-20.** This document covered the Option D → B transition
> program through Window 723-726. Its forward-looking content (CDL-062
> admissibility prerequisites, simulation iteration list, human conversation
> gates) is now carried in `docs/specs/ilc_master_completion_roadmap_v0.1.md`.
> Do not consult for current planning.
```

Confirm before archiving that the following content from lines 470-530 is
covered in the master roadmap:
- CDL-062 admissibility prerequisites (master roadmap §6)
- Human conversation gates list (master roadmap §7)
- "Fastest honest route" sequencing: close row 6, resolve CDL-062 admissibility
  vs Option B sequencing knot, close/lock rows 7-9, narrow row 5, then open
  sovereign substrate lane (covered in master roadmap §4 and §6)

**`docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.3.md`**

Add at top of file:

```
> **SUPERSEDED.** Replaced by v0.4 (`docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.4.md`).
> The morphogenetic hypergraph note at §4.3 (lines 189-199) is now covered in
> `docs/specs/ilc_master_completion_roadmap_v0.1.md` §6.
```

The v0.3 content at §4.3 about ADR-0031 being a breaking wire-format gate
before M-018 is now resolved (ADR-0031 accepted in Phase 746). Confirm this
is recorded in the master roadmap as closed before archiving v0.3.

### 3.4 Planning index and capsule advance

Update `docs/PLANNING_INDEX.md`:
- Point master roadmap as the primary human-readable completion guide
- Mark v0.3 roadmap as archived/superseded
- Mark the two archived docs as archived with pointers
- Capsule v5.3 remains current; no new capsule in this window unless needed
  for coherence

---

## 4. Hard constraints

- No opening of the Mysticeti convergence window
- No row 5, 7, or 8 closure claim
- No CDL-017 ratification
- No Option B graduation
- No ilc_core/ or ilc_consensus/ mutation
- No decision-log mutation except archival headers on retired documents
- Do not reassign M-021 or M-022 to Codex — Gemini owns M-track execution
- Do not represent planning-surface work as evidence that rows, CDLs, or
  Option B have crossed their actual gates
- The master roadmap is a factual sequencing document. It must not contain
  claims that any pending work is already done.
- When archiving stale docs, confirm each load-bearing forward section is
  covered in the master roadmap before adding the archived header. Do not
  assume coverage — verify.
- Track B current/next line must be re-read from STATUS.md tail at execution
  time. Do not copy from memory or older capsules.

---

## 5. Required outputs

| Output | File | Notes |
|---|---|---|
| Window 749-752 sequence lock | `docs/specs/ilc_phase_749_752_sequence_lock_v0.1.md` | Freeze non-goals, re-read live Track B from STATUS.md |
| Master completion roadmap | `docs/specs/ilc_master_completion_roadmap_v0.1.md` | Primary output — human-readable end-to-end plan |
| M-series lane update | `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md` | In-place update; 6 specific changes listed in §3.2 |
| Foundational carry-forward archived | `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md` | Archival header only; no content deleted |
| Option D→B guide archived | `docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md` | Archival header only; no content deleted |
| Roadmap v0.3 superseded | `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.3.md` | Superseded header only |
| Planning index advance | `docs/PLANNING_INDEX.md` | Pointer to master roadmap; archived docs noted |
| Coherence report | `docs/specs/ilc_coherence_report_752_v0.1.md` | Standard window-close synthesis |
| Closure gate | `docs/specs/ilc_window_749_752_closure_gate_752_v0.1.md` | Selftest chain extends ILC_PHASE_748_GATE_SELFTEST=1 → ILC_PHASE_752_GATE_SELFTEST=1 |

---

## 6. Suggested phase structure

| Phase | Purpose |
|---|---|
| 749 | Sequence lock — re-read live frontier, freeze non-goals, record Track B from STATUS.md |
| 750 | Master roadmap creation + M-series lane update |
| 751 | Stale doc archival + planning index advance |
| 752 | Coherence report + closure gate |

---

## 7. Key questions this window must answer honestly

1. Is every load-bearing forward section from the three archived documents
   explicitly covered in the master roadmap before the archival headers land?
2. Does the master roadmap §2 (M-track remaining) correctly reflect the Q1-Q4
   decisions adopted 2026-04-20 — specifically the SIM-LEAKAGE-01 methodology
   requirement and the M-022 physical-evidence gate?
3. Does the master roadmap §4 (CDL-017 ratification window) correctly
   distinguish between the convergence window (rows 5/7/8 closure + Option B
   gate) and the subsequent CDL-017 ratification window (constitutional
   ratification + first validator deployment gate)?
4. Is the human conversation gates list in §7 complete and honest — nothing
   presented as code-decidable that actually requires operator judgment?

---

## 8. Closure-gate selftest chain note

The closure gate for this window should extend from:

- `ILC_PHASE_748_GATE_SELFTEST=1`

to:

- `ILC_PHASE_752_GATE_SELFTEST=1`

Read the actual Phase 748 closure gate file before drafting the test rather
than reasoning from memory.

---

## 9. No special pre-window gate

This window contains no CDL ratification and no runtime mutation. No special
pre-window conversation gate is required before packet drafting begins.

Standard review still applies. The live authority order remains:
1. STATUS.md tail for Track B
2. Capsule v5.3 and Phase 748 closure gate for main-lane frontier
3. This guidance doc for Window 749-752 scope and drafting intent
