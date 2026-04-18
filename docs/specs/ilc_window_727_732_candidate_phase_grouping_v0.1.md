# ILC Window 727-732: Candidate Phase Grouping (Codex Lead)

**Author:** Codex  
**Date:** 2026-04-18  
**Baseline:** Window `723-726` is closed. Capsule `v4.9` is published.
Financial-shard activation remains deferred. `CDL-017` remains open and
unratified. `CDL-062` remains the separate sovereign-substrate research lane.
Track B shows `M-016` complete and the authoritative next M-phase as `M-017`
in `STATUS.md`.  
**References:**
- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_window_727_732_codex_guidance_and_audit_brief_v0.1.md`
- `docs/specs/ilc_window_723_726_closure_gate_726_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v4.9.md`
- `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md`
- `docs/research/ilc_rights_licenses_and_gated_access_surfaces_memo_v0.1.md`
- `docs/specs/ilc_private_gated_shard_header_and_capability_token_contract_candidate_v0.1.md`
- `docs/adr/ADR_0022_Local_First_Private_Use_and_Publication_Bound_Economics.md`
- `docs/specs/ilc_cdl_038_private_to_public_promotion_and_promotion_receipt_ratification_evidence_353_v0.1.md`
- `docs/specs/ilc_cdl_041_shard_lifecycle_ratification_evidence_394_v0.1.md`
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.3.md`
- `docs/phases/STATUS.md`

---

## 1. Window identity and scope

Window `727-732` is the adjacent gated-economy hardening lane.

This window is responsible for:

1. writing the sequence lock for `727-732`,
2. selecting and locking the non-financial carry-forward lane for this window,
3. publishing a rights / licensing / gated-access disposition,
4. publishing a private/gated shard header and capability-token hardening note,
5. publishing the coherence report,
6. closing the window with capsule `v5.0` and a closure gate.

This window does NOT:
- activate the sequestered financial shard,
- reopen the financial-shard trigger question solved in `723-726`,
- ratify `CDL-017`,
- merge ADR-0022 hardening into `CDL-062`,
- mutate `ilc_core/` or `ilc_consensus/`.

---

## 2. Inherited boundaries and dependencies

### 2.1 Inherited baseline

This window inherits:
- Window `723-726` closure and capsule `v4.9`,
- the explicit deferment posture for financial-shard activation,
- `CDL-017` as open but not ratifiable in this window,
- `CDL-062` as the separate sovereign-substrate research lane,
- ADR-0022 as the private/public and gated-use boundary anchor,
- the live Track B line from `STATUS.md`, not from memory.

### 2.2 What `723-726` already settled

Window `723-726` already established that:
- financial-shard prerequisites remain unmet,
- no activation is honest today,
- no new financial CDL opening is recommended today,
- ADR-0022/private-gated hardening is adjacent but separate,
- later main-lane work may continue on adjacent gated-economy hardening.

### 2.3 Why this is the right next lane

The next honest non-financial continuation is not more trigger-matrix work.
That lane is already bounded and deferred.

The remaining adjacent work is:
- clarifying how rights and licensing sit relative to epistemic adjudication,
- clarifying what minimal public/private contract surfaces should exist for
  gated shards,
- hardening planning boundaries so future implementations do not drift.

### 2.4 Relationship to Track B

Track B is not the central work here, but all phase artifacts must still cite
the live M-series frontier from `STATUS.md`.

Rule:
- verify `STATUS.md` tail before every phase,
- do not repeat stale M-series claims from older capsules,
- do not convert `M-016` local offline extraction into a stronger replayability
  claim than the evidence supports.

---

## 3. Operationally obligated versus deferred

### 3.1 Obligated in this window

- Phase `727` sequence lock
- Phase `728` adjacent carry-forward selection and boundary lock
- Phase `729` rights / licensing / gated-access disposition
- Phase `730` private/gated header and capability-token hardening note
- Phase `731` coherence report
- Phase `732` capsule `v5.0` and window closure gate

### 3.2 Explicitly deferred

- financial-shard activation
- any new financial-shard CDL opening
- `CDL-017` ratification
- `CDL-062` convergence or ratification
- runtime implementation of gated access or capability tokens
- refactoring rights disputes into a new production contract surface
- runtime mutation

---

## 4. Governing constraints

Hard constraints:
- no pre-window conversation gate applies here,
- no CDL ratification is planned in this window,
- `CDL-017` text review is permitted but ratification is not,
- `CDL-062` remains separate from this hardening lane,
- ADR-0022 remains the architectural anchor for private/public and gated-use
  boundaries,
- the window must not imply that rights/licensing is the same as epistemic
  refutation,
- the window must not imply that subscription or market microstructure belongs
  fully at L1,
- no `ilc_core/` or `ilc_consensus/` mutation is allowed.

---

## 5. Candidate phase table

| Order | Phase | Topic | Character | Sensitivity |
|---|---:|---|---|---|
| 1 | 727 | Window `727-732` sequence lock | Gate / Planning | **SENSITIVE** |
| 2 | 728 | Adjacent gated-economy carry-forward selection and boundary lock | Research / Planning | **SENSITIVE** |
| 3 | 729 | Rights, licenses, and gated-access surfaces disposition | Research / Spec | **SENSITIVE** |
| 4 | 730 | Private/gated shard header and capability-token contract hardening | Research / Spec | **SENSITIVE** |
| 5 | 731 | Coherence report for Window `727-732` | Gate / Handoff | **SENSITIVE** |
| 6 | 732 | Capsule `v5.0` and Window `727-732` closure gate | Gate / Handoff | **SENSITIVE** |

---

## 6. Scope notes for candidate phases

### Phase 727 — sequence lock

Deliverables:
- `docs/specs/ilc_phase_727_732_sequence_lock_v0.1.md`

Required content:
- lock the six-phase ordering for `727-732`,
- cite the live Track B line from `STATUS.md`,
- state that the financial-shard deferment posture is unchanged,
- state that `CDL-062` remains separate,
- state that ADR-0022/private-gated hardening remains separate from financial
  activation work,
- state that closure phase is `732`.

### Phase 728 — carry-forward selection and boundary lock

Deliverables:
- `docs/specs/ilc_adjacent_gated_economy_carry_forward_selection_728_v0.1.md`

Required content:
- identify the honest non-financial continuation from the `723-726` carry-forward,
- select adjacent gated-economy hardening as the active lane for `729-730`,
- record why financial-shard opening remains deferred,
- record why `CDL-062` remains separate,
- record that no new CDL opening is recommended in this phase.

### Phase 729 — rights / licensing / gated-access disposition

Deliverables:
- `docs/specs/ilc_rights_licenses_and_gated_access_surfaces_disposition_729_v0.1.md`

Required content:
- state that rights/licensing is not collapsed into `refutation_criterion`,
- define the L1 / gated-shard / L2-L3 split,
- define what belongs at the public anchor versus what remains gated/private,
- define dispute/adjudication posture without over-ratifying a new contract.

### Phase 730 — private/gated contract hardening

Deliverables:
- `docs/specs/ilc_private_gated_shard_header_and_capability_token_contract_hardening_730_v0.1.md`

Required content:
- harden the minimum public header surface,
- bound the capability-token or contract-reference model,
- preserve continuity with `CDL-038` private-to-public promotion,
- preserve continuity with `CDL-041` shard lifecycle,
- state what remains deferred to later implementation or constitutional work.

### Phase 731 — coherence report

Deliverables:
- `docs/specs/ilc_coherence_report_731_v0.1.md`

Required content:
- summarize Phases `727-730`,
- confirm that no CDL ratification occurred,
- confirm that no financial-shard activation occurred,
- confirm that `CDL-062` and ADR-0022 remain separate from this lane,
- record which A-series audit items from the pre-window brief were addressed
  in-window versus explicitly carried forward,
- state what carries into the closure gate.

### Phase 732 — closure

Deliverables:
- `docs/specs/ilc_antigravity_context_capsule_v5.0.md`
- `docs/specs/ilc_window_727_732_closure_gate_732_v0.1.md`

Required content:
- summarize what the window actually closed,
- state explicit deferment boundaries,
- publish capsule `v5.0`,
- route carry-forward explicitly into the next main-lane window,
- update `PLANNING_INDEX.md` to the true post-`732` frontier,
- review and update the launch roadmap if the window changed any live completed
  versus remaining gap description.

---

## 7. Open questions, options, and recommendations

### 7.1 What is the honest non-financial continuation?

Open question:
- which carry-forward item can proceed now without financial-shard activation?

Options:
- reopen financial-shard trigger work,
- advance `CDL-062`,
- do adjacent gated-economy hardening,
- defer the whole window.

Recommendation:
- adjacent gated-economy hardening. It is explicitly carried forward by capsule
  `v4.9` and does not require faking post-launch prerequisites.

### 7.2 How should rights/licensing be treated?

Open question:
- is rights/licensing mostly epistemic refutation, or a separate metadata /
  contract surface?

Options:
- collapse into refutation,
- separate metadata / provenance / dispute surface,
- full L1 rights engine now.

Recommendation:
- separate metadata / provenance / dispute surface. Do not pretend it is a
  refutation rule, and do not overbuild a full L1 rights engine here.

### 7.3 How much of gated access belongs at L1?

Open question:
- what minimum surface belongs at L1 versus L2/L3?

Options:
- push almost everything into L1,
- minimal header / fee-hook / access-reference surface at L1,
- fully off-protocol.

Recommendation:
- minimal header / fee-hook / access-reference surface at L1, with recurring
  billing, delivery, enterprise permissions, and market logic kept at L2/L3.

### 7.4 What is the right relationship to `CDL-017`?

Open question:
- should this window attempt validator-governance ratification?

Options:
- yes,
- text review only,
- no mention at all.

Recommendation:
- text review only if needed for boundary clarity, but no ratification.

### 7.5 What is the right relationship to `CDL-062`?

Open question:
- should this window merge into the sovereign-substrate lane?

Options:
- merge into `CDL-062`,
- cite and keep separate,
- block `CDL-062` until later.

Recommendation:
- cite and keep separate. This lane is adjacent hardening, not sovereign-
  substrate convergence.

### 7.6 Is a new CDL opening needed now?

Open question:
- do these outputs require a new CDL opening in-window?

Options:
- yes, open now,
- no, publish planning/spec hardening only,
- defer everything.

Recommendation:
- no new CDL opening in `727-732`. Publish bounded hardening artifacts first.

---

## 8. Recommended packet verdict

Window `727-732` should be drafted and executed as a docs-only, no-ratification,
no-runtime-mutation hardening window.

Its honest meaning is:
- keep the financial-shard lane deferred,
- harden adjacent gated-economy boundaries,
- reduce implementation drift risk around rights, licensing, and gated access,
- close with capsule `v5.0` and explicit carry-forward.
