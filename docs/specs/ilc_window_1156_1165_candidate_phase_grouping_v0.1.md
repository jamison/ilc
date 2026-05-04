# ILC Window 1156-1165: Candidate Phase Grouping

**Author:** Claude Sonnet 4.6 (local architectural reviewer)
**Date:** 2026-05-04
**Status:** CLOSED
**Baseline:** Window 1148-1156 CLOSED (Phase 1155 verdict: PASS, commit `610cf137`).
CDL-084 is the ratified attribution frontier. CDL-085 remains unopened and SIM-gated.
Capsule v5.40 current. Phase 1156 was deferred/not authorized in prior window; numbering
resumes at 1156.
**Closure:** Phase 1165 closure gate passed. `window_1156_1165_closed_phase_1165`.
**Planning note:** This is a candidate grouping, not a locked sequence. Phases 1156–1162
are the hard minimum lane. Phases 1163 and 1164 are conditional tail slots. Phase 1165
is the closure gate. The window may run lean (close at Phase 1164 with 1163 deferred) if
Phase 1163 conditions are not met.

---

## 1. Window Identity and Scope

Window 1156-1165 runs three lanes in dependency order:

1. **ADR acceptance lane** — accept ADR-0020 (priority), then batch-review ADR-0012,
   ADR-0022, ADR-0023, and ADR-0008 using the Phase 1156 stale-reconciliation
   dispositions; update the v0.2
   candidate star map as each ADR clears; draft the ADR-0036 release-key ADR.
   ADR acceptance is judgment-heavy governance review, not blind automation — each ADR
   is accepted only if truly ready; otherwise deferred cleanly.
2. **SIM-SPECTRAL-04 execution lane** — build the claim-composition projection tool
   (new loader, not reuse of star-map path), run the simulation, produce the Phase 1146
   disposition follow-on.
3. **CDL-085 conditional lane** — if SIM-SPECTRAL-04 passes the gate criterion defined in
   `docs/sims/sim_spectral_04/program.md`, a conditional tail slot (Phase 1163) opens
   CDL-085. Requires both a positive SIM-SPECTRAL-04 result AND explicit human GO token.
   No canonical CDL-085 pre-opening spec currently exists; Phase 1163 (if it fires) must
   create one from Phase 1162 pass evidence + prior planning references.

Phase numbering note: Phase 1156 was a reserved but unused tail slot in the prior window.
The prior window closed at Phase 1155. This window resumes numbering at 1156. No phase
numbering gap is introduced; later window references to "Window 1157+" in carry-forward
tokens should now be read as "Window 1156+."

The v0.2 signing ceremony is **not** in this window. It requires ADR-0036 acceptance,
which is drafted here but accepted in Window 1166+. The unsigned v0.2 candidate may grow
during this window as newly-accepted ADRs are added; it remains unsigned until the signing
ceremony.

---

## 2. Baseline and Inheritance

### Ratified CDL chain

- `CDL_084_DEPENDENCY = "cdl_084_provenance_chain_attribution_ratified_1113.v0.1"`
- `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`
- CDL-085: SIM-gated, unopened. Gate criterion defined in
  `docs/sims/sim_spectral_04/program.md` §5.

### Active runtime chain

- `epoch_attribution_settle_runtime_1129_fix1.v0.5` — unchanged
- No runtime semantic mutations authorized in this window

### Genesis Atlas canonical anchors

- Signed v0.1 star map: `out/genesis_core_star_map_v0.1.json` (32 nodes, 55 edges) — **untouched**
- Signed root envelope hash: `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`
- **Immutable:** `out/genesis_compile_coverage_diagnostic_v0.1.json` — must not be overwritten
- Unsigned v0.2 candidate: `out/genesis_core_star_map_v0.2_candidate.json` (36 nodes, 63 edges)
  — may grow this window as accepted ADRs are added; remains unsigned

### SIM-SPECTRAL anchors

- Corrected baseline: `out/sim_spectral_02_run02_fix2_summary.json`
- S3/S1 threshold: `0.6416011282246747`
- G2/S1 threshold: `0.8640456434014127`
- SIM-SPECTRAL-04 program spec: `docs/sims/sim_spectral_04/program.md`
- Composability audit: `out/genesis_32_node_composability_audit_v0.1.json`

### Capsule and handoff

- Capsule: `docs/specs/ilc_antigravity_context_capsule_v5.40.md`
- Handoff: `docs/specs/ilc_window_1148_1156_handoff_1155_v0.1.md`
- ADR stale reconciliation: `docs/specs/ilc_adr_stale_reconciliation_strike_force_1156_v0.1.md`

### Next fresh CDL number

CDL-085 is reserved and SIM-gated. Next fresh CDL number after CDL-085 is CDL-086
(unassigned). Do not assign CDL-086 this window.

---

## 3. Track Inventory

### 3.1 Constitutionally obligated (carry-forward from prior windows)

| Token | Routing in this window |
|-------|----------------------|
| `adr_0020_acceptance_review_priority_before_tier3_embedding_linkage` | Phase 1157 — acceptance review + v0.2 promotion |
| `adr_0012_tier2_blocked_status_proposed` | Phase 1158 — batch review; promote if accepted |
| `adr_0022_tier2_blocked_status_proposed` | Phase 1158 — batch review; promote if accepted |
| `adr_0023_tier2_blocked_status_proposed` | Phase 1158 — batch review; promote if accepted |
| `adr_0008_tier2_blocked_status_proposed_not_accepted` | Phase 1158 — include as boundary-acceptance candidate after ADR-0008 reconciliation |
| `sim_spectral_04_claim_composition_projection_required_before_cdl_085_reconsideration` | Phases 1160–1162 |
| `matched_size_controls_required_for_future_spectral_sims` | Phase 1161 (mandatory in run) |
| `genesis_canonical_lineage_contract_required_before_public_rc` | Phase 1159 drafts ADR-0036 (release-key subset only); full Canonical Lineage Contract requires separate ADR — Window 1166+ |
| `truth_primitive_permanence_requires_community_ratification_before_genesis_sunset` | Carry-forward only; no execution this window |
| `contributor_agreement_required_before_public_repo` | Carry-forward; counsel track |
| `public_rc_envelope_hash_transition_policy_required` | Carry-forward; covered by Phase 1153 spec |

### 3.2 Deferred governance

| Item | Status |
|------|--------|
| CDL-085 opening | **Conditional tail slot (Phase 1163)** — requires positive SIM-SPECTRAL-04 result + human GO |
| v0.2 candidate signing ceremony | Deferred to Window 1166+ — requires ADR-0036 acceptance first |
| ADR-0036 acceptance | Draft in Phase 1159; acceptance in Window 1166+ |
| Genesis Canonical Lineage Contract ADR (broader scope) | ADR-0036 covers release-key subset only; full Canonical Lineage Contract requires separate ADR or explicit incorporation decision — Window 1166+ |
| Tier-3 runtime linkage (`schema:*`/`runtime:*`) | Deferred — requires ADR-0020 acceptance (Phase 1157) + Window 1166+ |
| Canon bundle signing repair | Carry-forward tooling debt; not in scope |
| License/trademark/contributor agreement | Counsel track; not in scope |

### 3.3 Simulation-conditional

| Item | Routing |
|------|---------|
| SIM-SPECTRAL-04 Run 01 | Phase 1161 — authorized by this window |
| SIM-SPECTRAL-04 disposition | Phase 1162 |
| CDL-085 opening | Phase 1163 — conditional on Phase 1162 gate pass + human GO |

---

## 4. ADR Acceptance Lane

### 4.1 ADR acceptance scope and rules

The rule established in Phase 1148 applies consistently: only Accepted ADRs may be
promoted to canonical star-map nodes. Accepting an ADR changes its `**Status:**` field
from `Proposed` to `Accepted` and constitutes a governance-status decision.

ADR acceptance phases are NON-SENSITIVE (no CDL mutation) but must be proposed and
reviewed before execution per the standard workflow.

Acceptance criteria for each ADR:
1. The ADR describes a decision that has been substantively implemented or is durable
   governance that will not be reversed.
2. The ADR has no open blocking objections in the governance record.
3. The ADR's content correctly describes the protocol's current or intended state.

If an ADR fails criteria during Phase 1158 review, it remains Proposed and is deferred
with an updated blocked token.

### 4.2 ADR-0020 — Knowledge-Node-First Design Principle (Phase 1157)

**Title:** Knowledge-Node-First Design Principle
**Current status:** Proposed
**Priority:** Highest — prerequisite for Tier-3 embedding linkage

Phase 1157 reviews ADR-0020 against the three acceptance criteria. If accepted:
- Update `docs/adr/ADR_0020_Knowledge_Node_First_Design_Principle.md` status to Accepted
- Add `adr:0020_knowledge_node_first_design_principle` as a new node in the v0.2 candidate
  curated seed and regenerate the v0.2 candidate (37 nodes)
- Emit acceptance token: `adr_0020_accepted_phase_1157`
- Emit updated carry-forward: the Tier-3 embedding linkage prerequisite is now met at
  the governance level; Tier-3 implementation remains a separate lane

If ADR-0020 fails acceptance criteria, Phase 1157 records the specific gap with a new
deferred token and does not update the star map.

### 4.3 ADR batch acceptance — ADR-0012, ADR-0022, ADR-0023, ADR-0008 (Phase 1158)

Phase 1158 reviews all four remaining Proposed ADRs with corrected titles:

| ADR | Correct title | Governance surface |
|-----|--------------|-------------------|
| ADR-0012 | ECU-ILC-Graph Coupling and Anti-Reflexivity Contract | ECU/ILC graph coupling; anti-reflexivity contract |
| ADR-0022 | Local-First Private Use and Publication-Bound Economics | Local-first use; publication-bound economic model |
| ADR-0023 | Multi-Layer Quality Signal Architecture | Quality signal layer architecture |
| ADR-0008 | Node Usefulness vs Governance Weight and Genesis Dilution | Epistemic weight / utility flow / governance weight separation |

For each ADR that passes the three acceptance criteria:
- Update the ADR status field to Accepted
- Add the node to the v0.2 candidate curated seed
- Emit an individual acceptance token: `adr_NNNN_accepted_phase_1158`

For each ADR that does not pass:
- Record the specific gap
- Emit a deferred token: `adr_NNNN_acceptance_deferred_phase_1158_gap: <brief reason>`

Phase 1156 stale-reconciliation posture:

| ADR | Phase 1158 posture |
|-----|--------------------|
| ADR-0012 | likely acceptance-ready if scoped to directional ECU/ILC/graph coupling and anti-reflexivity |
| ADR-0022 | likely acceptance-ready if scoped to local/private boundary, explicit promotion, and publication-bound economics |
| ADR-0023 | narrow acceptance candidate only; avoid overclaiming full finality for all quality-signal economics |
| ADR-0008 | boundary-acceptance-ready after commit `b6e9e7a8`; coefficients/runtime retuning remain out of scope |

The four reviews remain independent. A failure or deferral for one ADR must not block
the others.

Phase 1158 regenerates the v0.2 candidate after each accepted ADR batch. Final v0.2
candidate node count depends on acceptance outcomes: between 37 (only ADR-0020 accepted)
and 41 (all five accepted).

### 4.4 ADR-0036 release-key ADR draft (Phase 1159)

Phase 1159 drafts ADR-0036 as a planning document. This is a new ADR, not an acceptance
review.

**Scope of ADR-0036 (release-key subset only):**

ADR-0036 covers the operational release-key mechanism specifically. It does NOT cover
the full Genesis Canonical Lineage Contract. The broader Canonical Lineage Contract
(network_id derivation, Node 0 Merkle inclusion, rolling ECU legitimacy windows,
gossip-domain continuity) still requires its own formal ADR or explicit incorporation
decision — that is a separate and larger governance surface. Do not conflate them.

ADR-0036 scope:

1. Defines the operational release key as the mechanism for signing canonical ILC
   releases without requiring routine Plate 2 (Genesis key) use.
2. Specifies how an operational release key is registered as Genesis-bound: the key must
   be signed or referenced by the Genesis root envelope (or a signed successor envelope).
3. Defines the signing authority delegation: operational release key signs release
   artifacts, packages, and versioned star maps (v0.2+); Genesis key signs root envelopes
   only.
4. Specifies key rotation policy: new operational keys must also be Genesis-bound; a
   key-transition envelope must reference the prior key's signed commitment.
5. Addresses the `public_rc_envelope_hash_transition_policy_required` obligation
   as it pertains to release key binding — the transition policy for the internal v0.1
   root envelope hash to a public RC envelope must use the operational release key.

ADR-0036 must have `**Status:** Proposed` at the end of Phase 1159. It is not accepted
in this window. The acceptance review is Window 1166+.

The broader Genesis Canonical Lineage Contract (from Phase 1153 planning spec) must
be tracked as a separate forward obligation requiring its own ADR or explicit
incorporation decision — not subsumed by ADR-0036. Record this explicitly in Phase 1159.

---

## 5. SIM-SPECTRAL-04 Execution Lane

### 5.1 Projection tool build (Phase 1160)

Implements `tools/build_genesis_claim_composition_projection.py` per the spec in
`docs/sims/sim_spectral_04/program.md` §3.

**Inputs:**
- `out/genesis_core_star_map_v0.1.json` (signed; do not mutate)
- `out/genesis_32_node_composability_audit_v0.1.json`
- `docs/specs/ilc_genesis_claim_composition_projection_plan_1146_v0.1.md`

**Output:**
- `out/genesis_claim_composition_projection_v0.1.json`

**Determinism requirements** (from program spec §3):
- `sort_keys=True`, `allow_nan=False`, stable separators
- Fail closed if audit node is missing from signed v0.1 star map
- Every projected vertex carries `authority_source_ref` to a signed Genesis node
- Every projected edge carries a typed reason

**Deliverables:**
- `tools/build_genesis_claim_composition_projection.py`
- `out/genesis_claim_composition_projection_v0.1.json`
- `tests/test_phase_1160_claim_composition_projection_build.py` (minimum 5 tests)
- Walkthrough + STATUS entry

**Gate token:** `claim_composition_projection_built_phase_1160`

### 5.2 SIM-SPECTRAL-04 Run 01 (Phase 1161)

Runs the simulation per `docs/sims/sim_spectral_04/program.md` §4.

**Run plan (mandatory):**
1. S1 against `out/genesis_claim_composition_projection_v0.1.json`
2. Matched-size S3 and G2 controls as primary controls (closes
   `matched_size_controls_required_for_future_spectral_sims`)
3. Raw 100-node S3 and G2 as secondary historical-continuity controls

**Seeds:** same three seeds as SIM-SPECTRAL-03 (42, 1337, 2026) for comparability.

**Output:**
- `out/sim_spectral_04_run01_summary.json`
- `docs/sims/sim_spectral_04/run01_raw_notes_1161.md`

**Comparison:** Report alongside SIM-SPECTRAL-03 raw-authority result so the projection
improvement (or lack thereof) is visible.

**Gate token:** `sim_spectral_04_run01_committed_phase_1161`

### 5.3 SIM-SPECTRAL-04 disposition (Phase 1162)

Applies the gate criterion from `docs/sims/sim_spectral_04/program.md` §5:

```
Pass condition:
- S1 projection slope positive across all seeds
- Matched-size S3/S1 < 0.6416011282246747 (all seeds)
- Matched-size G2/S1 < 0.8640456434014127 (all seeds)
- No accepted result depends solely on raw 100-node controls
```

The disposition document must explicitly state one of:

```
sim_spectral_04_gate_pass — CDL-085 reconsideration supported
```
or
```
sim_spectral_04_gate_fail — CDL-085 reconsideration not supported
```

If `sim_spectral_04_gate_pass`:
- Phase 1163 (CDL-085 opening) becomes active
- Human GO token required before Phase 1163 executes

If `sim_spectral_04_gate_fail`:
- Phase 1163 does not execute
- Disposition must state the specific failure mode and carry-forward
- CDL-085 remains SIM-gated; Phase 1162 must record a new deferred obligation with
  diagnosis (e.g., projection architecture gap, threshold gap, etc.)

**Output:**
- `docs/sims/sim_spectral_04/disposition_1162_v0.1.md`
- `tests/test_phase_1162_sim_spectral_04_disposition.py` (minimum 5 tests)
- Walkthrough + STATUS entry

---

## 6. CDL-085 Conditional Lane

### 6.1 CDL-085 opening (Phase 1163, conditional)

**Conditional on:** `sim_spectral_04_gate_pass` AND explicit human GO token.

Phase 1163 opens CDL-085 (Werner φ-bound / spectral efficiency constitutional limit).

No canonical CDL-085 pre-opening spec exists in the repo. Phase 1163 must therefore:

1. Confirm CDL-085 number is still unused (check CDL index and all CDL files)
2. Create `docs/specs/ilc_cdl_085_werner_phi_bound_opening_1163_v0.1.md` — the
   pre-opening spec, synthesized from:
   - Phase 1162 pass evidence (SIM-SPECTRAL-04 results)
   - `docs/sims/sim_spectral_04/disposition_1162_v0.1.md`
   - `docs/sims/sim_spectral_04/program.md` §5 (gate criterion)
   - Phase 1146 disposition named finding
   - Any prior mention of `EDGE_MINT_PHI_BOUND` in the codebase
3. Open CDL-085 in the CDL file using the standard opening format
4. The pre-opening spec is a Phase 1163 deliverable, not a prerequisite — it is created
   during the phase, not before it

**Pre-commit hook required:**
```
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1163
```

If Phase 1162 produces `sim_spectral_04_gate_fail`, Phase 1163 does not execute.
The window closes at Phase 1164 (coherence/capsule).

---

## 7. CDL Number Assignments

| CDL | Status | Notes |
|-----|--------|-------|
| CDL-085 | **Conditional opening in Phase 1163** | Only if `sim_spectral_04_gate_pass` + human GO |
| CDL-086 | Unassigned | Do not use this window |

---

## 8. Candidate Phase Table

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 1156 | Window sequence lock | Foundation / Constitutional | NON-SENSITIVE |
| 2 | 1157 | ADR-0020 acceptance review + v0.2 candidate update | Governance review | NON-SENSITIVE |
| 3 | 1158 | ADR batch acceptance — ADR-0012, ADR-0022, ADR-0023, ADR-0008 | Governance review | NON-SENSITIVE |
| 4 | 1159 | ADR-0036 release-key ADR draft | Synthesis | NON-SENSITIVE |
| 5 | 1160 | SIM-SPECTRAL-04 projection tool build + artifact | Simulation | NON-SENSITIVE |
| 6 | 1161 | SIM-SPECTRAL-04 Run 01 | Simulation | NON-SENSITIVE |
| 7 | 1162 | SIM-SPECTRAL-04 disposition + CDL-085 gate verdict | Synthesis | NON-SENSITIVE |
| — | 1163 | CDL-085 opening (conditional on Phase 1162 gate pass) | Constitutional | **conditional** |
| 8 | 1164 | Coherence report + capsule v5.41 | Synthesis | NON-SENSITIVE |
| 9 | 1165 | Closure gate | Gate | **SENSITIVE** |

### Conditional note on Phase 1163

Phase 1163 is a CDL opening slot. Two scenarios:

**Scenario PASS:** Phase 1162 produces `sim_spectral_04_gate_pass`. Human issues GO token.
Phase 1163 opens CDL-085 using `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1163`.
Phase 1164 (coherence) runs after Phase 1163.

**Scenario FAIL:** Phase 1162 produces `sim_spectral_04_gate_fail`. Phase 1163 does not
execute. Window closes at Phase 1164 (coherence runs after Phase 1162) then Phase 1165.
CDL-085 routing carries into Window 1166+ with a new diagnosis and deferred token.

Before executing Phase 1163 under PASS, confirm:
- CDL-085 pre-opening scope and title (check prior planning docs)
- CDL number not previously used
- Human has issued explicit GO token with `GO Phase 1163`

### Note on Phase 1157 ADR-0020 acceptance

Phase 1157 is the highest-priority phase of this window. ADR-0020 (Knowledge-Node-First
Design Principle) acceptance unblocks:
1. Tier-3 embedding linkage (governance prerequisite now met)
2. Addition of `adr:0020_knowledge_node_first_design_principle` to the v0.2 candidate

If ADR-0020 fails acceptance criteria, Phase 1157 records the gap and the v0.2 candidate
remains at 36 nodes. Phase 1158 still runs for the other four ADRs.

### Note on Phase 1158 batch acceptance

Phase 1158 reviews four ADRs. Per-ADR outcomes are independent — one failing does not
block others. Each ADR gets its own acceptance or deferred token. The v0.2 candidate
is regenerated once at the end of Phase 1158 with all accepted ADRs in the batch.

ADR-0008's previous default-defer posture is superseded by the ADR-0008 reconciliation
commit `b6e9e7a8` and the Phase 1156 stale-reconciliation memo. Phase 1158 should review
ADR-0008 as an acceptance candidate for its architectural boundary claim:
epistemic weight, utility flow, governance weight, Genesis dilution, and Genesis
economic/governance separation. Do not treat that as acceptance of final coefficients,
runtime retuning, or new Genesis emergency authority.

ADR-0023 is the highest-risk Phase 1158 candidate. It may be acceptance-ready only if
scoped to the evidence-backed portions of the quality-signal architecture. If review
cannot narrow the acceptance surface cleanly, defer with:
`adr_0023_acceptance_deferred_phase_1158_scope_overclaims_quality_signal_finality`.

### Note on Phase 1160 projection tool

The projection tool must be fully deterministic. Two runs with the same inputs must
produce byte-identical JSON output. This is a hard requirement because the output artifact
may eventually be hashed into a signed envelope. Test determinism explicitly:
- Run the tool twice; assert `sha256(output_run1) == sha256(output_run2)`

### Note on Phase 1162 gate verdict handling

The Phase 1162 disposition document is NON-SENSITIVE regardless of the gate verdict.
It is a scientific finding document. The CDL-085 opening (Phase 1163) is what is
SENSITIVE — and it only executes if Phase 1162 produces `sim_spectral_04_gate_pass`.

If Phase 1162 produces `sim_spectral_04_gate_fail`, the disposition must explain what
specifically failed and what would be needed for a future pass. The CDL-085 SIM-gate
obligation carries forward with a new diagnosis token rather than the generic
`sim_spectral_04_claim_composition_projection_required_before_cdl_085_reconsideration`.

---

## 9. Sensitivity Classification

### SENSITIVE phases

- **Phase 1163 (conditional — CDL-085 opening):** CDL mutation. Requires
  `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1163` and explicit human GO.
  Only executes if `sim_spectral_04_gate_pass`.
- **Phase 1165 (closure gate):** Structural window boundary. Requires human GO token.
  No CDL mutation if Phase 1163 did not execute.

### NON-SENSITIVE phases

- **Phase 1156:** Sequence lock. No CDL, no star-map mutation.
- **Phase 1157:** ADR acceptance review + v0.2 update. No CDL mutation; signed v0.1
  artifacts untouched; v0.2 candidate is an unsigned artifact.
- **Phase 1158:** ADR batch acceptance review. Same as Phase 1157.
- **Phase 1159:** ADR-0036 draft. New document, no CDL mutation.
- **Phase 1160:** Projection tool build. New tool + output artifact. No CDL mutation.
- **Phase 1161:** SIM-SPECTRAL-04 run. Simulation output. No CDL mutation.
- **Phase 1162:** Disposition. Document only. No CDL mutation.
- **Phase 1164:** Coherence + capsule. No CDL mutation.

### Conditional phases rule

Phase 1163: before executing, confirm Phase 1162 produced `sim_spectral_04_gate_pass`.
Confirm human GO token `GO Phase 1163`. If either condition is not met, Phase 1163 does
not execute — no GO token needed for non-execution.

### Pre-commit hook

Required only for Phase 1163 (if it executes):
```
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1163
```

No CDL mutation pre-commit hook needed for Phases 1156–1162, 1164–1165.

---

## 10. Scope Notes for Fixed Phases

### Phase 1156 — Window sequence lock

NON-SENSITIVE. No GO token required.

**Deliverables:**
- `docs/specs/ilc_phase_1156_1165_sequence_lock_v0.1.md` — sequence lock
- `docs/phases/phase_1156_window_sequence_lock_walkthrough.md`
- `docs/phases/STATUS.md` — Phase 1156 entry

**Required content:**
- Window token: `window_1156_1165_sequence_lock_committed`
- Phase numbering note: Phase 1156 was a reserved-but-deferred tail slot in Window
  1148-1156; `phase_1156_deferred_not_authorized` from prior window is inherited;
  this window resumes normal sequencing at Phase 1156.
- ADR stale-reconciliation intake: consume
  `docs/specs/ilc_adr_stale_reconciliation_strike_force_1156_v0.1.md` and preserve
  its per-ADR routing tokens. This guidance must preserve its per-ADR routing tokens in
  Phase 1157 and Phase 1158 prompts.
- CDL-085 pre-opening status: `cdl_085_no_canonical_opening_spec_exists_prior_to_phase_1163`
  (no dedicated pre-opening spec in repo; planning references only — Phase 1146
  disposition, SIM-SPECTRAL-04 program §5, older `EDGE_MINT_PHI_BOUND = None` mentions)
- Carry-forward tokens from prior window (list all 11 from Section 3.1)

**Commit subject:** `feat(g8): phase 1156 window 1156-1165 sequence lock`

---

### Phase 1157 — ADR-0020 acceptance + v0.2 candidate update

NON-SENSITIVE in the CDL mutation sense. No GO token required.
**Judgment-heavy governance review — not blind Strike Force automation.** Apply the
three acceptance criteria strictly. Accept only if the ADR document is truly ready.
If any criterion fails, defer cleanly with a specific gap token rather than forcing
acceptance.

**Deliverables:**
- Updated `docs/adr/ADR_0020_Knowledge_Node_First_Design_Principle.md` (if accepted:
  `**Status:** Accepted`)
- Updated `docs/sims/sim_spectral_02/genesis_core_star_map_curated_seed_v0.2.json`
  (if accepted: adds `adr:0020` node)
- Updated `out/genesis_core_star_map_v0.2_candidate.json` (if accepted: 37 nodes)
- `docs/sims/sim_spectral_04/adr_0020_acceptance_review_1157_v0.1.md` — review record
- `tests/test_phase_1157_adr_0020_acceptance.py` — minimum 3 tests
- `docs/phases/phase_1157_adr_0020_acceptance_walkthrough.md`
- `docs/phases/STATUS.md` — Phase 1157 entry

**Tests:**
| ID | Test | Gate |
|----|------|------|
| A1 | ADR-0020 file status field contains "Accepted" (if accepted) | Acceptance |
| A2 | v0.2 candidate node count is 37 (if accepted) or 36 (if deferred) | Node count |
| A3 | Signed v0.1 star map unchanged (32 nodes, root envelope hash unchanged) | Immutability |

**Commit subject:** `docs(atlas): phase 1157 adr-0020 acceptance review`

---

### Phase 1158 — ADR batch acceptance review

NON-SENSITIVE in the CDL mutation sense. No GO token required.
**Judgment-heavy governance review — not blind Strike Force automation.** Per-ADR
outcomes are independent; each ADR is accepted only if it meets all three criteria.
ADR-0008 is now a boundary-acceptance candidate after the reconciliation commit
`b6e9e7a8`; ADR-0023 remains the high-risk scoped-review candidate (see Section 4.3).
Record specific gap tokens for each deferral rather than generic "not ready" notes.

**Deliverables:**
- Updated ADR files for each accepted ADR
- Updated v0.2 candidate seed and generated candidate (node count grows by 0–4)
- `docs/sims/sim_spectral_04/adr_batch_acceptance_review_1158_v0.1.md` — per-ADR review
- `tests/test_phase_1158_adr_batch_acceptance.py` — minimum 4 tests (one per ADR)
- `docs/phases/phase_1158_adr_batch_acceptance_walkthrough.md`
- `docs/phases/STATUS.md` — Phase 1158 entry

**Tests:**
| ID | Test | Gate |
|----|------|------|
| B1 | Review record exists for each of the 4 ADRs with explicit accept/defer verdict | Coverage |
| B2 | v0.2 candidate node count is consistent with the acceptance outcomes recorded | Consistency |
| B3 | Signed v0.1 star map unchanged | Immutability |
| B4 | No ADR-0008 acceptance without explicit `adr_0008_acceptance_review_complete` token | Quality gate |
| B5 | ADR-0023 accepted only with explicit scoped-acceptance or otherwise deferred with overclaim token | Quality gate |

**Commit subject:** `docs(atlas): phase 1158 adr batch acceptance review 0012 0022 0023 0008`

---

### Phase 1159 — ADR-0036 release-key ADR draft

NON-SENSITIVE. No GO token required.

**Deliverables:**
- `docs/adr/ADR_0036_Operational_Release_Key_Genesis_Binding.md` — new ADR, Status: Proposed
- `docs/phases/phase_1159_adr_0036_release_key_draft_walkthrough.md`
- `docs/phases/STATUS.md` — Phase 1159 entry

**Must not:**
- Accept ADR-0036 in this phase
- Mutate any signed artifact
- Require CDL mutation pre-commit hook

**Gate token:** `adr_0036_release_key_draft_committed_phase_1159`

**Commit subject:** `docs(adr): phase 1159 adr-0036 operational release key draft`

---

### Phase 1160 — SIM-SPECTRAL-04 projection tool build

NON-SENSITIVE. No GO token required.

**New harness flag required:**
The existing `--s1-topology-file` loader (`load_s1_star_map_topology()`) expects the
Genesis star-map schema (`nodes[].candidate_id`, `edges[].source/target`, labeled
`genesis_core_star_map_v0.1` format). The projection JSON has a different structure.

Phase 1160 must add to `tools/sim_spectral_02.py`:
- New CLI flag: `--s1-topology claim-composition` (distinct from existing `genesis-star-map`)
- New CLI flag: `--s1-projection-file <path>` (analogous to `--s1-topology-file`)
- New loader function: `load_s1_claim_projection_topology(path)` — reads the projection
  JSON format, validates its schema, and returns the same `(Laplacian, diagnostics)` pair
  that the star-map loader returns. Must NOT call `load_s1_star_map_topology()` internally.
- The `source_format` diagnostic field should be `genesis_claim_composition_projection_v0.1`,
  not `genesis_core_star_map_v0.1`

The Laplacian shape returned can be constructed by the same adjacency/degree method; the
difference is schema validation and format labeling, not topology math.

**Deliverables:**
- `tools/build_genesis_claim_composition_projection.py`
- `out/genesis_claim_composition_projection_v0.1.json`
- Updated `tools/sim_spectral_02.py` — new `--s1-topology claim-composition` flag +
  `--s1-projection-file` flag + `load_s1_claim_projection_topology()` loader
- `tests/test_phase_1160_claim_composition_projection_build.py` — minimum 5 tests
- `docs/phases/phase_1160_claim_composition_projection_build_walkthrough.md`
- `docs/phases/STATUS.md` — Phase 1160 entry

**Required tests:**
| ID | Test | Gate |
|----|------|------|
| P1 | Projection file exists and is valid JSON | Existence |
| P2 | Every projected vertex has `authority_source_ref` pointing to a valid v0.1 node | Authority anchoring |
| P3 | Every projected edge has a typed reason in the allowed set | Edge typing |
| P4 | All 32 signed Genesis nodes appear in `authority_source_ref` values (full coverage) | Coverage |
| P5 | Tool is deterministic: two runs produce identical sha256 output | Determinism |

**Commit subject:** `sim(spectral-04): phase 1160 claim composition projection tool and artifact`

---

### Phase 1161 — SIM-SPECTRAL-04 Run 01

NON-SENSITIVE. No GO token required.

**Deliverables:**
- `out/sim_spectral_04_run01_summary.json`
- `docs/sims/sim_spectral_04/run01_raw_notes_1161.md`
- `tests/test_phase_1161_sim_spectral_04_run01.py` — minimum 5 tests
- `docs/phases/phase_1161_sim_spectral_04_run01_walkthrough.md`
- `docs/phases/STATUS.md` — Phase 1161 entry

**Run must include:**
- S1 using `--s1-topology claim-composition --s1-projection-file out/genesis_claim_composition_projection_v0.1.json`
  (the new Phase 1160 flag, not `--s1-topology-file`)
- Matched-size S3 and G2 controls (mandatory; closes
  `matched_size_controls_required_for_future_spectral_sims`)
- Raw 100-node S3 and G2 as secondary controls
- Seeds 42, 1337, 2026

**Commit subject:** `sim(spectral-04): phase 1161 run 01 claim composition projection`

---

### Phase 1162 — SIM-SPECTRAL-04 disposition

NON-SENSITIVE. No GO token required.

**Deliverables:**
- `docs/sims/sim_spectral_04/disposition_1162_v0.1.md`
- `tests/test_phase_1162_sim_spectral_04_disposition.py` — minimum 5 tests
- `docs/phases/phase_1162_sim_spectral_04_disposition_walkthrough.md`
- `docs/phases/STATUS.md` — Phase 1162 entry

**Disposition must contain:**
- Full comparison table vs. SIM-SPECTRAL-03 raw-authority result
- Explicit gate verdict token: `sim_spectral_04_gate_pass` or `sim_spectral_04_gate_fail`
- If PASS: "CDL-085 reconsideration supported pending human GO for Phase 1163"
- If FAIL: specific failure diagnosis + new carry-forward obligation token

**Commit subject:** `sim(spectral-04): phase 1162 disposition cdl-085 gate verdict`

---

### Phase 1164 — Coherence report + capsule v5.41

NON-SENSITIVE. No GO token required.

**Deliverables:**
- `docs/specs/ilc_integration_coherence_report_1164_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.41.md`
- `docs/phases/STATUS.md` — Phase 1164 entry

**Capsule v5.41 must record:**
- Final v0.2 candidate node count after all ADR acceptance outcomes
- SIM-SPECTRAL-04 gate verdict
- CDL-085 state (opened if Phase 1163 executed; still SIM-gated if Phase 1163 skipped)
- ADR-0036 status (Proposed)
- Signed v0.1 immutability (unchanged)

**Commit subject:** `docs(coherence): phase 1164 coherence report capsule v5.41`

---

### Phase 1165 — Closure gate

**SENSITIVE.** Requires explicit human GO token.

**Deliverables:**
- `docs/specs/ilc_window_1156_1165_handoff_1165_v0.1.md`
- `tests/test_phase_1165_window_1156_1165_closure_gate.py` — minimum 14 tests
- `docs/phases/phase_1165_window_1156_1165_closure_gate_walkthrough.md`
- `docs/phases/STATUS.md` — Phase 1165 entry

**Closure gate must verify:**
- Sequence lock committed (Phase 1156)
- ADR-0020 review outcome recorded (Phase 1157)
- ADR batch review outcome recorded for all 4 ADRs (Phase 1158)
- ADR-0036 draft committed (Phase 1159)
- Projection tool + artifact exist (Phase 1160)
- SIM-SPECTRAL-04 Run 01 summary exists (Phase 1161)
- Disposition committed with gate verdict token (Phase 1162)
- Phase 1163: either CDL-085 opened with pre-commit hook or explicitly deferred
- Signed v0.1 artifacts unchanged
- Runtime semantics unchanged
- Capsule v5.41 supersedes v5.40
- Handoff routing correct

**Closure token:** `window_1156_1165_closed_phase_1165`

**Commit subject:** `docs(phase): close window 1156-1165`

---

## 11. Key Dependencies and Open Questions

### Must-resolve at window entry

1. **CDL-085 pre-opening scope — RESOLVED:** No canonical CDL-085 pre-opening spec exists
   in the repo. Current sources are planning references only: Phase 1146 disposition,
   SIM-SPECTRAL-04 program §5, prior window guidance docs, and older mentions of
   `EDGE_MINT_PHI_BOUND = None`. Phase 1156 sequence lock must record this finding:
   `cdl_085_no_canonical_opening_spec_exists_prior_to_phase_1163`. If Phase 1163 fires,
   it must create `docs/specs/ilc_cdl_085_werner_phi_bound_opening_1163_v0.1.md` from
   Phase 1162 pass evidence plus consolidated prior planning, and confirm CDL-085 number
   is still unused before opening.

2. **v0.2 candidate regeneration consistency:** The curated seed and generated candidate
   are updated incrementally across Phases 1157 and 1158. Phase 1159 must read the
   post-1158 candidate as the v0.2 baseline. Confirm the seed JSON format is the same
   as v0.1's seed (same schema, just more nodes) before Phase 1157 executes.

3. **SIM-SPECTRAL-04 harness flag — RESOLVED:** Do not reuse `--s1-topology-file`
   unchanged. The existing loader expects `nodes[].candidate_id`, `edges[].source/target`,
   and labels the source as `genesis_core_star_map_v0.1`. The projection has a different
   schema. Phase 1160 must add `--s1-topology claim-composition` + `--s1-projection-file`
   + a new `load_s1_claim_projection_topology()` loader. The diagnostic `source_format`
   field must be `genesis_claim_composition_projection_v0.1`. See Phase 1160 scope note.

### Sequencing constraints

- Phase 1157 must complete before Phase 1158 (v0.2 candidate grows in order)
- Phase 1160 must complete before Phase 1161 (simulation needs the projection artifact)
- Phase 1161 must complete before Phase 1162 (disposition needs run results)
- Phase 1162 must complete before Phase 1163 can be evaluated (gate verdict required)
- Phase 1163 (if executing) must complete before Phase 1164 (capsule must reflect CDL state)

### Open questions

1. **CDL-085 scope documentation:** Where is the canonical pre-opening spec for CDL-085?
   Phase 1156 should locate this and reference it in the sequence lock so Phase 1163
   has a clear starting point.

2. **SIM-SPECTRAL-04 projection node count:** The claim-composition projection will have
   more nodes than the raw 32-node Genesis star map (projections expand composites and
   parameterized policies into subclaims). What is the expected projected node count?
   The Phase 1160 projection tool will determine this, but a rough estimate helps with
   matched-size control sizing.

3. **ADR-0008 acceptance readiness:** Given that ADR-0008 (Node Usefulness vs Governance
   Weight) is foundational to the claim-composition layer, is there enough settled
   governance on its three-surface separation (epistemic_weight / utility_flow /
   governance_weight) to accept it in Phase 1158? If not, it may need its own dedicated
   phase in Window 1166+.

### Permanently deferred from this window

- v0.2 signing ceremony (requires ADR-0036 acceptance; deferred to Window 1166+)
- ADR-0036 acceptance
- Tier-3 runtime linkage
- SIM-BEACON-01, SIM-HYPEREDGE-01, SIM-ECU-STABILITY-01
- Canon bundle signing repair
- License, trademark, contributor agreement drafting

---

## 12. Known Patterns and Technical Constraints

### v0.2 candidate grows incrementally

The unsigned v0.2 candidate starts this window at 36 nodes and may grow to 37–41 nodes
depending on ADR acceptance outcomes. The final count is recorded in the Phase 1158
walkthrough and in capsule v5.41. All growth is to the unsigned candidate only; the
signed v0.1 artifacts are untouched.

### Projection tool determinism (phase 1160)

The projection tool is a new artifact. Its determinism must be tested explicitly before
Phase 1161 runs the simulation against its output. A non-deterministic projection would
produce non-reproducible simulation results. See Phase 1160 test P5.

### CDL-085 opening pattern (phase 1163, if executing)

CDL-085 opening follows the standard CDL-opening pattern:
- `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1163`
- Runtime mutation (if any) in a separate commit from CDL doc mutation
- Prelock hardening phase is NOT required if Phase 1162 provides positive SIM-SPECTRAL-04
  evidence — the disposition serves as the prelock-hardening evidence record

### Selftest guard chain (Phase 1165)

Phase 1165 closure gate test must include `ILC_PHASE_1165_GATE_SELFTEST=1` guard.

### Signed v0.1 immutability

Any phase that touches the v0.2 candidate must include a test asserting:
- `out/genesis_core_star_map_v0.1.json` node count == 32
- Root envelope hash unchanged: `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`
- `out/genesis_compile_coverage_diagnostic_v0.1.json` not regenerated

### Merkle-Laplacian paper (research asset, not in scope)

`docs/research/ilc_merkle_laplacian_dual_commitment_paper_draft_v0.1.md` is a pre-SIM
research paper draft awaiting SIM-SPECTRAL-01 empirical validation. SIM-SPECTRAL-04
produces spectral data but against the claim-composition projection, not the raw
Laplacian topology the paper's Section 8.4 needs. This paper is not scoped in this
window. It becomes a candidate for a dedicated SIM + paper finalization lane once
SIM-SPECTRAL-01 (or an equivalent foundational spectral characterization) is run.

---

## 13. Non-Goals and Explicitly Deferred Items

- v0.2 star map signing ceremony
- ADR-0036 acceptance
- Tier-3 runtime linkage (`schema:*`/`runtime:*` node class)
- SIM-SPECTRAL-01 for Merkle-Laplacian paper
- Canon bundle signing failure repair
- License, trademark, or contributor agreement drafting
- Multi-agent testnet / RC substrate work
- Runtime semantic changes

---

## 14. Key Canonical Anchors for Prompt Drafting

- `docs/specs/ilc_window_1156_1165_candidate_phase_grouping_v0.1.md` — this document
- `docs/specs/ilc_window_1148_1156_handoff_1155_v0.1.md` — incoming handoff
- `docs/specs/ilc_antigravity_context_capsule_v5.40.md` — current capsule
- `docs/sims/sim_spectral_04/program.md` — SIM-SPECTRAL-04 program spec
- `out/genesis_32_node_composability_audit_v0.1.json` — Phase 1151 audit (projection tool input)
- `docs/specs/ilc_genesis_claim_composition_projection_plan_1146_v0.1.md` — projection rules
- `out/genesis_core_star_map_v0.1.json` — signed star map (projection tool input; do not mutate)
- `out/genesis_core_star_map_v0.2_candidate.json` — current unsigned candidate (36 nodes)
- `docs/sims/sim_spectral_02/genesis_core_star_map_curated_seed_v0.2.json` — v0.2 seed
- `docs/adr/ADR_0020_Knowledge_Node_First_Design_Principle.md` — Phase 1157 target
- `docs/adr/ADR_0012_ECU_ILC_Graph_Coupling_and_Anti_Reflexivity.md` — Phase 1158 target
- `docs/adr/ADR_0022_Local_First_Private_Use_and_Publication_Bound_Economics.md` — Phase 1158
- `docs/adr/ADR_0023_Multi_Layer_Quality_Signal_Architecture.md` — Phase 1158
- `docs/adr/ADR_0008_Node_Usefulness_vs_Governance_Weight_and_Genesis_Dilution.md` — Phase 1158
- `docs/specs/ilc_genesis_canonical_lineage_contract_planning_spec_v0.1.md` — ADR-0036 input

---

## 15. Rationale for Single-Window Scope

1. ADR acceptance (Phases 1157–1158) and SIM-SPECTRAL-04 execution (Phases 1160–1162)
   are independent lanes that can run in sequence within one window, with ADR acceptance
   providing governance groundwork while SIM-SPECTRAL-04 provides scientific groundwork
   for CDL-085.
2. ADR-0036 draft (Phase 1159) is lightweight and unblocking — it doesn't require
   acceptance here, only a well-formed draft for Window 1166+ acceptance review.
3. Keeping the CDL-085 conditional opening (Phase 1163) within this window allows
   CDL-085 to proceed in the same window as its scientific justification (Phase 1162),
   rather than forcing an additional round-trip window purely for the opening.
4. If Phase 1163 does not execute (gate fail or no GO token), the window closes cleanly
   at Phase 1165 without losing work — all other phases are valuable regardless of the
   CDL-085 outcome.
