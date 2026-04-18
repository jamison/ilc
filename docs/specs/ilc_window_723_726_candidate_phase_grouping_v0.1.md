# ILC Window 723-726: Candidate Phase Grouping (Codex Lead)

**Author:** Codex
**Date:** 2026-04-18
**Baseline:** Window `717-722` is closed. Capsule `v4.8` is published.
`CDL-066` and `CDL-067` are ratified. `CDL-017` remains open and unratified.
`CDL-062` remains the sovereign-substrate research lane and is separate from
this work. Track B shows `M-015` complete and the authoritative next M-phase
as `M-016` in `STATUS.md`.
**References:**
- `docs/specs/ilc_window_723_726_guidance_v0.1.md`
- `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md` §4.5
- `docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md` §12
- `docs/specs/ilc_economic_architecture_comprehensive_v0.1.md` §4.3
- `docs/specs/ilc_cdl_050_treasury_blocker_resolution_plan_v0.1.md`
- `docs/research/ilc_rights_licenses_and_gated_access_surfaces_memo_v0.1.md`
- `docs/specs/ilc_private_gated_shard_header_and_capability_token_contract_candidate_v0.1.md`

---

## 1. Window identity and scope

Window `723-726` is the sequestered financial-shard eligibility and
gated-economy prefilter lane.

This window is responsible for:

1. writing the sequence lock for `723-726`,
2. publishing the financial-shard eligibility prefilter,
3. publishing the post-launch trigger matrix,
4. publishing the contagion / firewall prerequisite list,
5. stating clearly how this lane remains separate from ordinary shard-lifecycle
   law, ADR-0022 private/gated access hardening, and `CDL-062`,
6. closing the window with a coherence report, capsule `v4.9`, and closure
   gate.

This window does NOT:
- activate the sequestered financial shard,
- ratify a new CDL by default,
- treat ADR-0018 as accepted live ADR text,
- reopen ordinary shard-lifecycle law,
- reopen private/gated rights/access hardening,
- mutate `ilc_core/` or `ilc_consensus/`.

---

## 2. Inter-lane dependencies

### 2.1 Inherited baseline

This window inherits:
- Window `717-722` closure and capsule `v4.8`,
- `CDL-047` treasury governance as the active L1 treasury lane,
- `CDL-048` ECU-time discipline,
- `CDL-062` as the sovereign-substrate research lane,
- ADR-0022 as the separate private/gated boundary,
- ADR-0028 as the Option D active posture,
- Track B current state from `STATUS.md`, not from memory.

### 2.2 Relationship to Track B

Track B is not the central work of this packet, but capsule and closure
language still depends on the live M-series frontier. The rule is:
- verify `STATUS.md` tail before every phase,
- do not copy stale M-series wording from older capsules,
- do not let local loopback work become a hidden claim of multi-machine proof.

### 2.3 Relationship to historical “ADR-0018”

Planning docs refer to “ADR-0018” as the historical sequestered financial
shard concept, but there is no live ADR file for ADR-0018 under `docs/adr/`.

This window must therefore treat the idea as a historically proposed concept,
not as accepted ADR law.

### 2.4 Relationship to adjacent lanes

This lane is separate from:
- ordinary shard-lifecycle governance,
- private/gated header and capability-token hardening,
- sovereign substrate / BFT family work under `CDL-062`,
- transfer-economics closure already completed in Window `717-722`.

---

## 3. Operationally obligated versus deferred

### 3.1 Obligated in this window

- Phase `723` sequence lock
- Phase `724` financial-shard eligibility prefilter
- Phase `725` post-launch trigger matrix and contagion / firewall prerequisites
- Phase `726` coherence report, capsule `v4.9`, and closure gate

### 3.2 Explicitly deferred

- financial-shard activation
- any actual `B_hft` runtime implementation
- any new CDL ratification by default
- any new shard-governance activation package
- private/gated rights/access hardening
- market microstructure implementation
- runtime mutation

---

## 4. Governing constraints inherited from prior windows

Hard constraints:
- no pre-window conversation gate applies here,
- `CDL-062` remains separate from this lane,
- no financial-shard activation may be claimed here,
- commons / treasury governance remains inherited through `CDL-047`,
- any future `B_hft` lane must remain separate from `B_e`,
- market microstructure must remain sequestered from the base epistemic graph,
- the lane must explicitly separate itself from ADR-0022 private/gated hardening,
- no claim may be made that post-launch trigger conditions are already met
  before launch exists.

---

## 5. Candidate phase table

| Order | Phase | Topic | Character | Sensitivity |
|---|---:|---|---|---|
| 1 | 723 | Window `723-726` sequence lock | Gate / Planning | **SENSITIVE** |
| 2 | 724 | Sequestered financial-shard eligibility prefilter | Research / Planning | **SENSITIVE** |
| 3 | 725 | Post-launch trigger matrix and contagion / firewall prerequisites | Research / Spec | **SENSITIVE** |
| 4 | 726 | Coherence report, capsule v4.9, and window `723-726` closure gate | Gate / Handoff | **SENSITIVE** |

---

## 6. Scope notes for candidate phases

### Phase 723 — sequence lock

Deliverables:
- `docs/specs/ilc_phase_723_726_sequence_lock_v0.1.md`

Required content:
- lock the four-phase ordering for `723-726`,
- state that no pre-window conversation is required,
- state that this is not an activation window,
- state that `CDL-062` remains separate,
- state that ADR-0022/private-gated hardening remains separate,
- state that closure phase is `726`.

### Phase 724 — eligibility prefilter

Deliverables:
- `docs/specs/ilc_sequestered_financial_shard_eligibility_prefilter_724_v0.1.md`

Required content:
- define candidate scope as securities-like trading, HFT, and financial
  instruments,
- state the historical ADR-0018 reference without treating it as accepted ADR,
- define the minimum separation boundaries,
- state current non-eligibility honestly,
- avoid activation language.

### Phase 725 — trigger matrix and firewall prerequisites

Deliverables:
- `docs/specs/ilc_sequestered_financial_shard_post_launch_trigger_matrix_725_v0.1.md`
- `docs/specs/ilc_sequestered_financial_shard_contagion_firewall_prerequisites_725_v0.1.md`

Required content:
- define minimum post-launch trigger conditions,
- define disqualifying conditions,
- define the required separate-budget and firewall conditions,
- define auditability / failure containment expectations,
- state whether a new CDL opening is recommended or deferred,
- keep current verdict explicit.

### Phase 726 — closure

Deliverables:
- `docs/specs/ilc_coherence_report_726_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v4.9.md`
- `docs/specs/ilc_window_723_726_closure_gate_726_v0.1.md`

Required content:
- summarize Phases `723-725`,
- state explicit eligibility and deferment posture,
- record that no activation or ratification occurred,
- update the capsule to `v4.9`,
- route carry-forward explicitly into Window `727-732`.

---

## 7. Phase-specific open questions, options, and recommendations

### 7.1 Is the sequestered financial shard still a real candidate?

Open question:
- is the concept still a live later-lane candidate or should it be recorded as
  dormant?

Options:
- real post-launch candidate,
- historically interesting but dormant,
- fully rejected.

Recommendation:
- keep it as a real later-lane candidate, but only as a post-launch optional
  lane with explicit eligibility and trigger discipline.

### 7.2 Historical “ADR-0018” status

Open question:
- should the packet treat “ADR-0018” as accepted ADR law?

Options:
- yes,
- no, treat it as historical concept only.

Recommendation:
- no. There is no live ADR file in `docs/adr/`, so the packet should state that
  the concept is historically referenced but not accepted ADR text.

### 7.3 Minimum trigger threshold

Open question:
- what minimum condition makes a later financial-shard opening even eligible?

Options:
- immediate eligibility after launch,
- at least one public-launch monitoring cycle plus concrete demand signal,
- multiple cycles plus simulation evidence,
- indefinite deferment.

Recommendation:
- at least one public-launch monitoring cycle plus a concrete demand signal,
  with contagion/firewall readiness also required.

### 7.4 Relation to ordinary shard lifecycle

Open question:
- does this lane reopen general shard-lifecycle law?

Options:
- yes,
- no, separate lanes.

Recommendation:
- no. Keep this lane strictly about financial-shard eligibility, not ordinary
  shard-lifecycle governance.

### 7.5 Relation to private/gated access hardening

Open question:
- is this the same lane as private/gated rights/access hardening?

Options:
- same lane,
- adjacent but separate,
- fully merged later.

Recommendation:
- adjacent but separate. The rights/access hardening lane concerns headers,
  capability tokens, continuity, and access control; this lane concerns
  sequestered financial-market eligibility and contagion isolation.

### 7.6 Need for a separate `B_hft`

Open question:
- if the lane ever opens, does it require a separate budget?

Options:
- yes, separate `B_hft`,
- no, share `B_e`,
- unresolved.

Recommendation:
- yes, a separate `B_hft` must be a prerequisite. Sharing `B_e` would blur the
  firewall and contaminate the base knowledge-economy lane.

### 7.7 Need for a new CDL opening now

Open question:
- does the lane need a new CDL opening in `723-726`?

Options:
- recommend opening now,
- explicit deferment,
- reject permanently.

Recommendation:
- explicit deferment. This window should sharpen eligibility and prerequisites,
  not open a constitutional lane prematurely.
