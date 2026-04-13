# ILC Window 613-619: Strike-Force Redo Instructions

Author: Local architectural reviewer (Claude Sonnet 4.6)
Date: 2026-04-13
Status: SUPERSEDED IN PART — see Section 0.1 below.

The hard-reset git strategy (Section 2 Step 8) is no longer applicable. Window 613-618 is
now published history on origin/main as of 2026-04-13. The full rollback path is off the
table. The per-phase content improvements (Sections 3-4) remain valid and are adopted into
Phase 619 via the strengthened carry-forward approach described in Section 0.1.

---

## 0.1. Supersession note (2026-04-13)

Codex review found that the git assumptions in this document are stale. Window 613-618 is
already published on origin/main. The hard-reset strategy (Section 2 Step 8) would
require destructive rewrite of published history, which is not the clean path.

**Adopted path:** Finish Phase 619 with the Option-B readiness improvements from
Sections 3-4 absorbed directly into the Phase 619 handoff. Specifically:
- Phase 619 handoff gets a 7th section with the full 9-row Phase 611 checklist-delta table
- Phase 619 handoff requires `blockers_reduced` and `blockers_unchanged` sections
- All four Option-B gate carry-forward tokens must appear in the Phase 619 handoff
- One explicit line: "Window 613-619 advanced Option-B admissibility without changing the
  active Option-D posture"

This gets most of the value without history surgery. The non-destructive comparison branch
path (Section 2, Steps 1-4 only, without Step 8 reset) remains available if the human
decides to create a comparison artifact, but is not the recommended path now.

**Corrections from Codex review also applied to the Option B memo:**
- Werner framing is planning-level, not canonical ("Phase 609 is controlling canon")
- Privacy blocker is narrowed but not closed (Phase 611 row 5 remains `not_started`)
- Gate 3 (BFT) is not required before Window 623+ (only before sovereign L1 selection)
- Gate 1 (CDL-053) is a planning judgment, not a canonical critical-path gate

---

## 0. Evaluation and rationale

The current executed window (613-618 complete, 619 pending) correctly closes all five MVP
touchpoints in spec form. Its weakness is that it does the minimum work and leaves on the
table the explicit Option-B readiness tracking that would make the window far more useful
as a carry-forward artifact.

The cost of the redo is low: everything is docs-only, local-only, and not yet pushed to
origin. The gain is high: the rebuilt window will explicitly track advancement against the
Phase 611 graduation checklist (Section 5), bind each phase to its checklist row, and
produce a dedicated Option-B readiness compression document in Phase 618.

**What the redo does NOT do:**
- does not select Option B
- does not open CDL-062
- does not widen wallet authority
- does not implement chain or payment runtime
- does not add Agent Skills
- does not renumber phases or add new phases

The rebuilt window will make the same passes as the current window, plus it will produce
a materially stronger carry-forward artifact for future substrate selection work.

---

## 1. Current git state (as of 2026-04-13)

```
bb20ae50  docs: register Option B remaining gates and architecture memo   ← current tip
b2f46590  docs(g8): phase 618 walkthrough and status backfill
eba5caf0  docs(g8): phase 618 mvp gate synthesis and coherence report
768859aa  docs(g8): phase 617 walkthrough and status backfill
a01827c7  docs(g8): phase 617 public wallet surface contract spec
d69849fc  docs(g8): fix queued prompt token references for phases 616 and 618
7523ea61  docs(g8): phase 616 walkthrough and status backfill
34cf0d30  docs(g8): phase 616 public receipt schema and query contract spec
9b3486c6  docs(g8): phase 615 walkthrough and status backfill
160b69d5  docs(g8): phase 615 ecu to ilc lifecycle contract spec
81c93b8a  docs(g8): phase 614 walkthrough and status backfill
cc2d092b  docs(g8): phase 614 public init admission contract spec
7ecf244e  docs(g8): phase 613 walkthrough and status backfill
87918afb  docs(g8): phase 613 window 613-619 sequence lock
dd6e63f4  docs(g8): tighten window 613-619 queued prompt contracts   ← pre-execution boundary
```

Phase 619 has NOT been executed. Phase 618 is the last executed phase.

---

## 2. Git strategy (execute in this exact order)

### Step 1 — Create backup tag
```bash
git tag window-613-618-executed-v1 bb20ae50
```
This preserves the current executed window. Do not delete this tag.

### Step 2 — Create redo branch from pre-execution boundary
```bash
git checkout -b strike-force/window-613-619-v2 dd6e63f4
```

### Step 3 — Cherry-pick the Option B gates memo onto the redo branch
```bash
git cherry-pick bb20ae50
```
This brings `docs/research/ilc_option_b_architecture_memo_and_remaining_gates_v0.1.md`
and the `TODO.txt` gates block onto the redo branch. It will not conflict.

### Step 4 — Rewrite all 8 prompt/package files as specified in Section 3
Do all rewriting work here before executing any phase.

### Step 5 — Validate the full prompt package
```bash
python3 tools/validate_phase_prompt.py <each prompt file>
```
All 7 window prompts (613-619) must pass VALID before execution begins.

### Step 6 — Re-execute phases 613 through 619 in order
Each SENSITIVE phase (613, 614, 615, 617, 619) requires explicit human GO before committing.

### Step 7 — Compare old vs new
After Phase 619 completes on the redo branch, compare:
- Does the rebuilt window produce a stronger checklist-delta artifact?
- Does Phase 618 include the Option-B readiness compression doc?
- Do all tests pass?
- Are all scope constraints honored?

### Step 8 — Replace local main only after redo is confirmed better
```bash
git checkout main
git reset --hard strike-force/window-613-619-v2
```
Keep the `window-613-618-executed-v1` tag. Do not push to origin until human review.

---

## 3. Phase-by-phase prompt changes

### Phase 613 — Window sequence lock

**Additions to the window objective section:**

State explicitly: "This window is also Option-B readiness compression. It advances Phase 611
graduation checklist rows 1-4 from `partial`/`not_started` to `spec_closed_runtime_pending`
in spec form. It does not select Option B, open CDL-062, or change the active Option-D
posture."

**New hard pass criterion:**
Phases 614-617 must each contain a dedicated checklist-advancement section (see per-phase
requirements below). Phase 618 must produce a readiness compression document.

**New governance tokens required in the sequence lock doc:**
- `window_613_619_also_compresses_option_b_graduation_checklist_without_selection`
- `checklist_rows_1_through_4_advance_to_spec_closed_runtime_pending_in_spec_form`
- `checklist_rows_5_through_9_remain_unchanged_after_window_613_619`

**Test count:** Keep at 10 tests. Absorb the new framing into Test 3 (window objective
contains `option_b` readiness language) or Test 5 (hard pass conditions).

---

### Phase 614 — Public init/admission contract spec

**SENSITIVE — GO token required.**

**New section to add after Section 7:**

```
## 8. Public/private activation boundary
```

Section 8 must state:
- Local/private identity creation: explicitly permitted. Private nodes may exist and perform
  computation without canonical public admission.
- Canonical public activation: requires receipt-linked public admission lineage. Local key
  existence is NOT equivalent to canonical public activation.
- Local/private existence is not canonical public legitimacy. A node that has generated
  keys but has not obtained a public admission receipt is not a canonically admitted
  participant.
- Future sovereign anchoring: the admission receipt schema must preserve a stable anchor
  slot for future sovereign settlement binding. This slot is documented but not activated.
  The Phase 614 spec does not require chain-side admission now; it only requires the slot
  to exist and be stable.

**New required governance tokens:**
- `public_private_activation_boundary_locked`
- `local_key_existence_is_not_canonical_public_activation`
- `admission_receipt_preserves_future_sovereign_anchor_slot`
- `init_admission_row_1_advanced_to_spec_closed_runtime_pending`

**New checklist-advancement statement (required in Section 8 or Section 1):**

> Phase 611 graduation checklist row 1: "public init/admission flow tied to canonical
> receipts" — status before this phase: `partial`. Status after this phase: `spec_closed_
> runtime_pending`. Runtime implementation follows in Window 623+.

**Test contract:** Add 1 test to check Section 8 exists and contains the four new tokens.
Total tests: 10 → 11.

---

### Phase 615 — ECU-to-ILC lifecycle contract spec

**SENSITIVE — GO token required.**

**New section to add after the last existing section:**

```
## 8. Measurement vs settlement boundary
```

Section 8 must state:
- ECU is the protocol-internal measurement and accounting layer (Werner's productive credit).
  It is not compensation, not a currency, and not monetary law. It measures epistemic
  transformation efficiency: `W_e = ΔH / E_cost`.
- Visible ILC is settled internal balance only (Werner's monetary base). It records completed
  network membership; it does not promise future returns.
- Passive attribution constants (`rate=0.20`, `decay_floor=0.05`, `attribution_cap=0.15`)
  are bounded testnet proxies. They are not public monetary law and are subject to revision
  before any broader public RC claim.
- Canonical public settlement rights arise only after a public-legible boundary crossing.
  Private/local work is permitted but does not earn protocol ILC from private work alone.
  The public-work-only model resolves the privacy concern by participation scope, not by
  cryptographic privacy guarantees over private contributions.

**New required governance tokens:**
- `ecu_is_protocol_measurement_not_compensation_or_monetary_law`
- `canonical_settlement_rights_require_public_legible_boundary_crossing`
- `passive_attribution_constants_are_testnet_proxy_not_public_monetary_law`
- `lifecycle_row_3_and_4_advanced_to_spec_closed_runtime_pending`

**Checklist-advancement statement (required):**

> Phase 611 graduation checklist rows 3 and 4: "user and agent visible ECU to ILC lifecycle
> contract" and "delayed ILC visibility touchpoint" — both are covered by this phase per
> Phase 612 Section 3 bundling. Status before this phase: `partial`. Status after this phase:
> `spec_closed_runtime_pending`. Runtime implementation follows in Window 623+.

**Test contract:** Add 1 test to check Section 8 exists and contains the four new tokens.
Total tests: 10 → 11.

---

### Phase 616 — Public receipt schema and query contract spec

**NON-SENSITIVE.**

**New section to add after the last existing section:**

```
## 8. Future sovereign compatibility and extension discipline
```

Section 8 must state:
- The receipt schema must document (not activate) the following extension points for future
  sovereign compatibility:
  - `future_settlement_anchor_ref`: a stable slot for a future sovereign settlement
    anchor reference (e.g., chain txid, L1 proof anchor). Not populated in current spec
    form. Must not cause schema breakage when populated in a future window.
  - `future_publication_promotion_ref`: a stable slot for future publication/promotion
    reference (e.g., governance publication record). Not populated in current spec form.
  - `future_privacy_correlation_control_ref`: a stable slot for future privacy/correlation
    control metadata. Not populated in current spec form.
- These are documented extension slots. None are activated. Any future activation requires
  a dedicated phase and explicit human GO.
- The schema must not claim any of these slots as current functionality.

**New required governance tokens:**
- `receipt_schema_documents_future_sovereign_anchor_extension_point`
- `receipt_schema_extension_slots_documented_not_activated`
- `receipt_row_2_advanced_to_spec_closed_runtime_pending`

**Checklist-advancement statement (required):**

> Phase 611 graduation checklist row 2: "machine-legible public receipt issuance and
> query/runtime contract" — status before this phase: `not_started`. Status after this
> phase: `spec_closed_runtime_pending`. Runtime implementation follows in Window 623+.

**Test contract:** Add 1 test to check Section 8 exists and contains the three new tokens.
Total tests: 11 → 12.

---

### Phase 617 — Public wallet surface contract spec

**SENSITIVE — GO token required.**

**Required new machine-state fields in the wallet surface contract:**

Add to the wallet query response schema (Section 3 or wallet query definition section) the
following two machine-state fields or documented stable equivalents:

```
claimability_state: deferred
settlement_backend_class: bounded_internal
```

These fields must be defined in the spec as required response fields for any `wallet_status`
or `wallet_history` query. Their current values must be:
- `claimability_state=deferred`: reflects current bounded posture; no ILC claimability
  is open. This field must be a first-class machine-readable field, not a comment.
- `settlement_backend_class=bounded_internal`: reflects current internal ledger settlement.
  This field disambiguates the wallet surface from any future sovereign settlement backend
  without requiring a schema change at transition time.

These fields reduce later ambiguity and make the wallet surface more explicit about what
it is showing (bounded internal accounting) vs what it is not (sovereign chain balance).

**New required governance tokens:**
- `wallet_surface_claimability_state_field_required`
- `wallet_surface_settlement_backend_class_field_required`
- `wallet_claimability_state_is_deferred_in_current_bounded_posture`
- `wallet_settlement_backend_class_is_bounded_internal`
- `wallet_row_4_advanced_to_spec_closed_runtime_pending`

**Checklist-advancement statement (required):**

> Phase 611 graduation checklist row 4: "public wallet surface contract sufficient for a
> first participant-touch economic loop" — status before this phase: `partial`. Status
> after this phase: `spec_closed_runtime_pending`. Runtime implementation follows in
> Window 623+. Wallet boundary (Phase 576/Phase 581) remains unchanged.

**Test contract:** Add 1 test to check the two machine fields are defined and carry the
new tokens. Total tests: 10 → 11.

---

### Phase 618 — MVP gate synthesis and coherence report

**NON-SENSITIVE.**

**New deliverable: Option-B readiness compression document**

Add to deliverables:
```
docs/specs/ilc_option_b_readiness_compression_618_v0.1.md
```

This document is separate from the coherence report. The coherence report structure
(6 required section headings) is unchanged.

**Required sections in readiness compression doc:**

```
## 1. Option-B graduation checklist: window 613-619 delta
## 2. Blockers reduced by window 613-619
## 3. Blockers unchanged by window 613-619
## 4. Public/private legitimacy clarification
## 5. Residual blockers and next artifact needed
## 6. Carry-forward requirements
```

**Section 1** must include a before/after table for all 9 Phase 611 graduation checklist
rows (from Phase 611 Section 5):

| Row | Before window 613-619 | After window 613-619 | Phase |
|-----|----------------------|---------------------|-------|
| public init/admission flow | partial | spec_closed_runtime_pending | 614 |
| machine-legible public receipt | not_started | spec_closed_runtime_pending | 616 |
| ECU to ILC lifecycle contract | partial | spec_closed_runtime_pending | 615 |
| public wallet surface contract | partial | spec_closed_runtime_pending | 617 |
| privacy-preserving legitimacy | not_started | not_started | deferred |
| coupling invariants | partial | partial | deferred |
| censorship-resistance | partial | partial | deferred |
| independence from external centers | partial | partial | deferred |
| transport/discovery maturity | partial | partial | deferred |

**Section 2** must state:
- Rows 1-4 (the five MVP touchpoints) advanced to `spec_closed_runtime_pending`
- What specifically each phase contributed that produced this advancement

**Section 3** must state:
- Rows 5-9 are unchanged after this window
- Each row's reason for no change (not in MVP gate scope, or deferred per Phase 612)
- This is not a failure: Phase 612 explicitly deferred rows 5-9 to later lanes

**Section 4** must state the public/private legitimacy clarification:
- The public-work-only model resolves the privacy concern (row 5) by participation scope
- Local/private work is permitted; canonical public legitimacy requires public-legible
  boundary crossing
- The remaining privacy concern (row 5) is therefore smaller than it appears: it is
  about correlation minimization / unlinkability for public submissions, not about hiding
  non-public work on-chain
- This is a material narrowing of the privacy blocker even though the row status is
  unchanged

**Section 5** must identify the next artifact needed for each residual blocker:

| Residual blocker | Next artifact | Gate |
|-----------------|---------------|------|
| privacy-preserving legitimacy | correlation/unlinkability mechanism spec | post-619 public-legitimacy window |
| coupling invariants | coupling invariants governance lock | post-619 governance window |
| censorship-resistance | censorship-threshold study and mechanism spec | post-619 |
| independence from external centers | substrate selection criteria formalization | Option B graduation checklist |
| transport/discovery maturity | transport/discovery operationalization packet | Window 623+ runtime |
| CDL-053 Werner CDL | LT evidence track (LT-0 through LT-2) first | later |
| legal positioning memo | passive ECU + validator rewards memo | pre-RC |
| BFT variant selection | L1 implementation spec | before Window 623+ |
| Window 623+ runtime form | MVP gate runtime form | Window 623+ |

**Section 6** must carry all four Option B gate tokens:
- `cdl_053_werner_credit_architecture_deferred_pending_lt_evidence`
- `legal_positioning_memo_passive_ecu_and_validator_rewards_pre_rc_prerequisite`
- `bft_variant_selection_deferred_engineering_decision`
- `mvp_gate_runtime_form_window_623_plus_blocked_pending_spec_form_pass`

And also:
- `option_b_readiness_compression_618_locked`
- `option_b_checklist_rows_1_through_4_advanced_to_spec_closed_runtime_pending`
- `option_b_checklist_rows_5_through_9_unchanged_after_window_613_619`
- `option_b_selection_remains_unauthorized_after_window_613_619`
- `window_613_619_advanced_option_b_readiness_without_changing_option_d_posture`

**Updated Phase 618 scope (add to In scope):**
```
- new file docs/specs/ilc_option_b_readiness_compression_618_v0.1.md
```

**Updated Phase 618 test contract (9 → 11 tests):**

Tests 1-7: unchanged from current spec.
Test 8 (commit path-set): update to "main commit touches exactly
`{coherence_report_path, capsule_path, readiness_compression_path, test_path}`"
Test 9: unchanged (backfill commit touches exactly `{walkthrough_path, status_path}`).
New Test 10: readiness compression doc exists and contains all 6 required section headings.
New Test 11: readiness compression doc contains all 10 required governance tokens from
Section 6 (including all four Option B gate tokens) and does NOT contain language claiming
Option B is selected or rows 5-9 are closed.

**Commit:** Main commit must now touch 4 files:
`docs/specs/ilc_window_613_619_coherence_report_618_v0.1.md`,
`docs/specs/ilc_antigravity_context_capsule_v3.3.md`,
`docs/specs/ilc_option_b_readiness_compression_618_v0.1.md`,
`tests/test_phase_618_mvp_gate_synthesis_and_coherence_report.py`

---

### Phase 619 — Window closure gate and handoff

**SENSITIVE — GO token required.**

**Expanded handoff document: add 7th section**

The handoff document must contain these section headings (updated from 6 to 7):

```
## 1. Window identity and closure basis
## 2. Inputs and closure inheritance
## 3. Closure verdict summary
## 4. Carry-forward items and residual blockers
## 5. Next-window entry criteria and routing
## 6. MemPalace refresh disposition
## 7. Option-B graduation checklist: window 613-619 delta
```

**Section 7 must contain:**
- The full before/after table for all 9 Phase 611 checklist rows (same as in Phase 618
  readiness compression doc, Section 1)
- Explicit statement: "Window 613-619 advanced rows 1-4 of the Option-B graduation
  checklist to `spec_closed_runtime_pending` without selecting Option B or changing the
  active Option-D posture. The admission of the D → B transition remains governed by the
  full graduation checklist (Phase 611 Section 5) and ADR-0028."
- The four Option B gate carry-forward tokens (from memo)
- `handoff_records_option_b_graduation_checklist_delta`
- `option_b_selection_remains_unauthorized_after_613_619`

**Updated required tokens in handoff (add to existing list):**
- `handoff_records_option_b_graduation_checklist_delta`
- `option_b_selection_remains_unauthorized_after_613_619`
- `cdl_053_werner_credit_architecture_deferred_pending_lt_evidence`
- `legal_positioning_memo_passive_ecu_and_validator_rewards_pre_rc_prerequisite`
- `bft_variant_selection_deferred_engineering_decision`
- `mvp_gate_runtime_form_window_623_plus_blocked_pending_spec_form_pass`

**Gate script (Category 2 — mvp_spec_band_tests):** Add the readiness compression doc
test from Phase 618 to the synthesis category, or verify it is covered by the existing
Phase 618 test invocation (it should be, since Phase 618 test file is already in
Category 3).

No change to the 6-category structure of the gate script.

**Updated Phase 619 test contract:**

Test 3 (handoff contains 6 section headings): update to 7 section headings.
Test 4 (handoff contains all required tokens): add the 6 new tokens above.
Test 5 (Section 3 closure verdict): unchanged.
Test 6 (Section 5 next-window entry): add check for `handoff_records_option_b_graduation_checklist_delta`.
New Test 10.5 or update Test 10: verify Section 7 contains the full checklist-delta table
with all 9 rows and the `option_b_selection_remains_unauthorized` token.
Total tests: 10 → 11.

---

## 4. New governance tokens introduced by the redo

This is the complete set of new tokens the redo introduces across all phases. These must
appear in the Phase 613 sequence lock as required downstream outputs, and in the Phase 618
readiness compression doc and Phase 619 handoff as explicit requirements.

**Phase 613 (sequence lock):**
- `window_613_619_also_compresses_option_b_graduation_checklist_without_selection`
- `checklist_rows_1_through_4_advance_to_spec_closed_runtime_pending_in_spec_form`
- `checklist_rows_5_through_9_remain_unchanged_after_window_613_619`

**Phase 614 (init/admission):**
- `public_private_activation_boundary_locked`
- `local_key_existence_is_not_canonical_public_activation`
- `admission_receipt_preserves_future_sovereign_anchor_slot`
- `init_admission_row_1_advanced_to_spec_closed_runtime_pending`

**Phase 615 (lifecycle):**
- `ecu_is_protocol_measurement_not_compensation_or_monetary_law`
- `canonical_settlement_rights_require_public_legible_boundary_crossing`
- `passive_attribution_constants_are_testnet_proxy_not_public_monetary_law`
- `lifecycle_row_3_and_4_advanced_to_spec_closed_runtime_pending`

**Phase 616 (receipt):**
- `receipt_schema_documents_future_sovereign_anchor_extension_point`
- `receipt_schema_extension_slots_documented_not_activated`
- `receipt_row_2_advanced_to_spec_closed_runtime_pending`

**Phase 617 (wallet):**
- `wallet_surface_claimability_state_field_required`
- `wallet_surface_settlement_backend_class_field_required`
- `wallet_claimability_state_is_deferred_in_current_bounded_posture`
- `wallet_settlement_backend_class_is_bounded_internal`
- `wallet_row_4_advanced_to_spec_closed_runtime_pending`

**Phase 618 (synthesis + readiness compression):**
- `option_b_readiness_compression_618_locked`
- `option_b_checklist_rows_1_through_4_advanced_to_spec_closed_runtime_pending`
- `option_b_checklist_rows_5_through_9_unchanged_after_window_613_619`
- `option_b_selection_remains_unauthorized_after_window_613_619`
- `window_613_619_advanced_option_b_readiness_without_changing_option_d_posture`
- `cdl_053_werner_credit_architecture_deferred_pending_lt_evidence` (carry-forward)
- `legal_positioning_memo_passive_ecu_and_validator_rewards_pre_rc_prerequisite` (carry-forward)
- `bft_variant_selection_deferred_engineering_decision` (carry-forward)
- `mvp_gate_runtime_form_window_623_plus_blocked_pending_spec_form_pass` (carry-forward)

**Phase 619 (closure gate + handoff):**
- `handoff_records_option_b_graduation_checklist_delta`
- `option_b_selection_remains_unauthorized_after_613_619`
- (all four Option B gate carry-forward tokens again)

---

## 5. What does NOT change in the redo

These items must remain unchanged in all rewritten prompts:

- Phase numbers: 613 through 619 (no renumbering)
- Five MVP touchpoints: same five (init, receipt, lifecycle, wallet, ECU visibility)
- The two-form requirement: spec form (613-619) necessary but NOT sufficient; runtime
  form (623+) still required; broader public RC claims remain blocked
- Wallet boundary: Phase 576/Phase 581 boundary unchanged
- No CDL-062 opening
- No Agent Skills in this window
- No chain implementation
- No wallet write/transfer/withdrawal widening
- No Option B selection
- Phase 605 six-category gate script structure for Phase 619
- SENSITIVE designation for phases 613, 614, 615, 617, 619

---

## 6. Validation checklist before starting any execution

Before re-executing Phase 613 (the first SENSITIVE phase of the rebuilt window), verify:

- [ ] All 7 window prompts pass `python3 tools/validate_phase_prompt.py`
- [ ] Phase 613 sequence lock doc lists all new Option-B compression tokens as required
      downstream outputs
- [ ] Phase 614-617 each have the new Section 8 (or equivalent) in their scope and
      deliverables
- [ ] Phase 618 lists `ilc_option_b_readiness_compression_618_v0.1.md` as a deliverable
      with 6 required section headings and 11 tests (not 9)
- [ ] Phase 619 handoff requires 7 sections (not 6) and lists `handoff_records_option_b_graduation_checklist_delta` as a required token
- [ ] The cherry-pick of `bb20ae50` is clean on the strike-force branch

---

## 7. Success criteria for the redo

The rebuilt window is better than the current executed window if:

1. Phase 618 produces `ilc_option_b_readiness_compression_618_v0.1.md` with a
   complete before/after table for all 9 Phase 611 checklist rows
2. Phases 614-617 each contain an explicit checklist-row advancement statement and
   the corresponding governance token
3. Phase 619 handoff contains Section 7 with the full checklist delta
4. All tests pass (11 for 614, 11 for 615, 12 for 616, 11 for 617, 11 for 618, 11 for 619)
5. No scope widening has occurred (CDL-062, wallet widening, chain impl, Agent Skills
   are all absent from every output artifact)
6. All four Option B gate carry-forward tokens appear in Phase 618 and Phase 619

If criteria 1-6 are met and all tests pass, replace local main.

---

## 8. Inputs to read before rewriting each prompt

Read these before rewriting any prompt (do not reason from prior memory):
- `docs/specs/ilc_settlement_substrate_governance_vehicle_selection_611_v0.1.md` Section 5
  (graduation checklist) and Section 6 (blocker matrix)
- `docs/specs/ilc_settlement_substrate_closure_and_mvp_gated_replan_612_v0.1.md`
- `docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md`
- `docs/specs/ilc_phase_613_619_sequence_lock_v0.1.md` (current executed version)
- `docs/research/ilc_option_b_architecture_memo_and_remaining_gates_v0.1.md`
- The current executed versions of each prompt at `dd6e63f4^..` commits

---

## 9. Phase 619 only: what to do if this doc arrives after Phase 619 is done

If this document arrives after Phase 619 has already been executed on the current branch
(i.e., the redo is not possible because the window is fully closed), the fallback is:

1. Produce `docs/specs/ilc_option_b_readiness_compression_618_v0.1.md` as a standalone
   post-window document in a new non-windowed phase
2. Register all 10 new governance tokens from Section 4 in a post-619 synthesis memo
3. Require the next window's sequence lock to explicitly carry forward the checklist-delta
   table and all four Option B gate tokens

This fallback is weaker than the full redo but preserves the carry-forward without
requiring a rollback.

---

## 10. Human authorization required

Phase 613 re-execution is SENSITIVE. Codex must not commit Phase 613 outputs without an
explicit human GO token, even on the strike-force branch. The same SENSITIVE designation
applies to 614, 615, 617, and 619.

Human review of this instructions document is required before Codex begins the git
branching in Step 2. The human should confirm:

- The redo is authorized
- The scope additions (Section 8 in each of 614-617, new readiness compression doc in 618,
  Section 7 in 619 handoff) are acceptable
- The success criteria in Section 7 are acceptable
