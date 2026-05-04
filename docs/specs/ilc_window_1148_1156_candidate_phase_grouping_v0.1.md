# ILC Window 1148-1156: Candidate Phase Grouping

**Status:** CLOSED — Phase 1155 closure gate passed. Phase 1156 deferred/not authorized. `window_1148_1156_closed_phase_1155` `phase_1156_deferred_not_authorized`
**Author:** Claude Sonnet 4.6 (local architectural reviewer)
**Date:** 2026-05-04
**Baseline:** Window 1139-1147 CLOSED (Phase 1147 verdict: PASS, commit `5c985349`).
CDL-084 is the ratified attribution frontier. CDL-085 remains unopened and SIM-gated.
Capsule v5.39 current.
**Planning note:** This is a candidate grouping, not a locked sequence. Phases 1148–1154
are the hard minimum lane. Phases 1155–1156 are a conditional tail slot (Atlas Tier-2
signing ceremony). The window may close early at Phase 1155 (closure gate) if the
signing tail slot is not authorized.

---

## 1. Window Identity and Scope

Window 1148-1156 advances the Genesis Atlas from Tier-1 (signed 32-node star map) to
Tier-2 (high-authority ADR promotion + checkpoint #2), closes the composability audit
obligation from Phase 1146, drafts the SIM-SPECTRAL-04 program spec, and produces the
Genesis Canonical Lineage Contract as a planning spec.

Three primary lanes run in dependency order:

1. **Atlas Tier-2 lane** — add 8 confirmed high-authority ADRs as star-map nodes; run
   GENESIS-COMPILE checkpoint #2; produce a v0.2 candidate star map (unsigned until a
   signing ceremony is authorized).
2. **SIM-SPECTRAL-04 spec lane** — close the composability audit obligation, then draft
   the SIM-SPECTRAL-04 program spec for claim-composition projection.
3. **Pre-public-RC obligations lane** — produce the Genesis Canonical Lineage Contract
   pre-ADR spec; synthesize the remaining counsel-track obligations into a structured
   carry-forward record.

A fourth conditional lane — Atlas Tier-2 signing ceremony (v0.2 star map) — appears as a
tail slot. It requires either an established operational release key or explicit human
authorization of a Genesis exceptional signing. If neither is in place at checkpoint #2,
the tail slot is deferred and the window closes at Phase 1155.

CDL-085 remains SIM-gated for this entire window. No CDL opening or ratification is
authorized here.

---

## 2. Baseline and Inheritance

### Ratified CDL chain

CDL-084 (`cdl:084_provenance_chain_attribution`) is the frontier. Key constant:

- `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`
- `CDL_084_DEPENDENCY = "cdl_084_provenance_chain_attribution_ratified_1113.v0.1"`

CDL-085 (Werner φ-bound): DEFER — SIM-gated pending SIM-SPECTRAL-04
claim-composition projection. Must not open without explicit human override of
Phase 1146 DEFER verdict.

### Active runtime chain

- `epoch_attribution_settle_runtime_1129_fix1.v0.5` — unchanged
- No runtime semantic mutations are authorized in this window

### Genesis Atlas canonical anchors

- Signed star map: `out/genesis_core_star_map_v0.1.json` (32 nodes, 55 edges, all signed)
- Root envelope: `out/genesis_signing_root_envelope_v0.1.json`
- Root envelope hash: `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`
- **Immutable artifact:** `out/genesis_compile_coverage_diagnostic_v0.1.json` — covered
  by Phase 1142s toolchain manifest; must not be overwritten; future diagnostics use new
  versioned paths
- GENESIS-COMPILE checkpoint #1 token: `genesis_compile_checkpoint_1_pass`

### SIM-SPECTRAL anchors

- Corrected baseline: `out/sim_spectral_02_run02_fix2_summary.json`
- S3/S1 threshold: `0.6416011282246747`
- G2/S1 threshold: `0.8640456434014127`
- Named finding: `raw_authority_graph_is_not_the_right_spectral_work_graph`

### Capsule and handoff

- Capsule: `docs/specs/ilc_antigravity_context_capsule_v5.39.md`
- Handoff: `docs/specs/ilc_window_1139_1147_handoff_1147_v0.1.md`

### Next fresh CDL number

CDL-085 is reserved and SIM-gated. Next fresh CDL number is **CDL-086** (unassigned).
Do not assign CDL-086 in this window unless explicitly authorized.

---

## 3. Track Inventory

### 3.1 Constitutionally obligated

From Phase 1146 and Phase 1147 carry-forwards:

| Token | Status | Sequencing |
|-------|--------|-----------|
| `genesis_32_node_composability_audit_required` | Obligated | Phase 1151 |
| `matched_size_controls_required_for_future_spectral_sims` | Obligated | Folded into SIM-SPECTRAL-04 program spec (Phase 1152) |
| `sim_spectral_04_claim_composition_projection_required_before_cdl_085_reconsideration` | Obligated — spec only this window | Program spec Phase 1152; execution deferred to Window 1157+ |
| `genesis_canonical_lineage_contract_required_before_public_rc` | Obligated — pre-ADR spec this window | Phase 1153 |
| `truth_primitive_permanence_requires_community_ratification_before_genesis_sunset` | Obligated — synthesis this window | Phase 1154 |
| `public_rc_envelope_hash_transition_policy_required` | Obligated — synthesis this window | Phase 1154 |
| `contributor_agreement_required_before_public_repo` | Obligated — synthesis this window | Phase 1154 |

### 3.2 Deferred governance

| Item | Status | Reason |
|------|--------|--------|
| CDL-085 opening | **Hard deferred** — SIM-gated | Cannot open without positive SIM-SPECTRAL-04 result and explicit human override |
| Atlas Tier-2 signing ceremony (v0.2) | **Conditional tail slot** | Requires operational release key ADR or Genesis exceptional signing authorization; Scenario A (release key) is effectively deferred to Window 1157+ |
| Tier-3 runtime linkage (`schema:*`/`runtime:*` node class) | Deferred to Window 1166+ | Blocked until Tier-2 ADR promotions are complete |
| ADR-0036 (candidate: Canonical Lineage Contract) | **Not opening this window** | Phase 1153 produces a pre-ADR planning spec; formal ADR opening in Window 1157+ |
| ADR-0020 Tier-2 promotion | **Blocked** — status Proposed, not Accepted | Priority for acceptance in Window 1157+; prerequisite for Tier-3 embedding linkage; carry-forward token: `adr_0020_acceptance_review_priority_before_tier3_embedding_linkage` |
| ADR-0012, ADR-0022, ADR-0023 Tier-2 promotion | **Blocked** — status Proposed, not Accepted | Acceptance review batch Window 1157+ after ADR-0020; each gets blocked-status token in Phase 1148 |
| ADR-0008 Tier-2 promotion | **Blocked** — status Proposed, not Accepted | Same rule applied consistently; token in Phase 1148 |
| ADR-0034 Tier-2 promotion | **Deferred** — low-level transport ADR | Governs D2d sealed-sender; revisit in Window 1166+ with Tier-3 runtime linkage |

### 3.3 Simulation-conditional

| Item | Status |
|------|--------|
| SIM-SPECTRAL-04 claim-composition run | Not authorized this window — program spec only |
| SIM-HYPEREDGE-01 | Not authorized this window |
| SIM-ECU-STABILITY-01 | Not authorized this window |

---

## 4. Atlas Tier-2 Lane

### 4.1 ADR status normalization audit and content review (Phase 1148)

**Hard gate before Phase 1149:**

```
adr_status_normalization_required_before_tier2_promotion
```

Phase 1148 must perform a status normalization audit across all 10 planning-bridge ADR
candidates before Phase 1149 executes. Confirmed statuses from ADR headers:

| ADR | Confirmed title | Confirmed status |
|-----|----------------|-----------------|
| ADR-0019 | Graph-Native Governance Compilation Boundary | **Accepted** |
| ADR-0026 | Protocol vs Harness/Product Boundary | **Accepted** |
| ADR-0028 | Settlement Substrate Graduation and Governance Route | **Accepted** |
| ADR-0031 | Subgraph Homomorphism Query Contract | **Accepted** |
| ADR-0012 | ECU-ILC-Graph Coupling and Anti-Reflexivity Contract | Proposed |
| ADR-0020 | Knowledge-Node-First Design Principle | Proposed |
| ADR-0022 | Local-First Private Use and Publication-Bound Economics | Proposed |
| ADR-0023 | Multi-Layer Quality Signal Architecture | Proposed |
| ADR-0008 | Node Usefulness vs Governance Weight and Genesis Dilution | Proposed |
| ADR-0034 | D2d Sealed-Sender Mechanism | Accepted (but deferred — see below) |

**The rule applied consistently:** Only Accepted ADRs may be promoted as canonical star-map
nodes in the v0.2 candidate. Proposed ADRs may appear as `canonicality_tier: "candidate"`
nodes if the guidance doc explicitly authorizes it — but not in this window.

**Phase 1148 disposition verdicts:**

*ADR-0034 (D2d Sealed-Sender Mechanism, Accepted):*
Governs sealed spectral beacon emission and D2d privacy. This is a low-level transport
privacy mechanism, not a high-level governance ADR in the constitutional authority class.
**Disposition: Defer Tier-2 promotion to Window 1166+ with Tier-3 runtime linkage work.**
Token: `adr_0034_tier2_deferred_to_window_1166_plus`

*ADR-0012, ADR-0020, ADR-0022, ADR-0023 (all Proposed):*
High-value candidates for Tier-2 once accepted. Cannot promote Proposed ADRs as canonical
star-map nodes. **Disposition: Blocked — status Proposed, not Accepted.**
Carry-forward obligation: each of these ADRs must reach Accepted status before Tier-2
promotion. Phase 1148 should record per-ADR tokens:
- `adr_0012_tier2_blocked_status_proposed`
- `adr_0020_tier2_blocked_status_proposed`
- `adr_0022_tier2_blocked_status_proposed`
- `adr_0023_tier2_blocked_status_proposed`

*ADR-0008 (Node Usefulness vs Governance Weight, Proposed):*
Same rule. **Disposition: Blocked — status Proposed.**
Token: `adr_0008_tier2_blocked_status_proposed_not_accepted`

**Confirmed Tier-2 ADR promotion list for Phase 1149 (Accepted only):**

| ADR | Confirmed title | Star-map governance surface |
|-----|----------------|-----------------------------|
| ADR-0019 | Graph-Native Governance Compilation Boundary | Directly motivates GENESIS-COMPILE-01; explains the star map's own diagnostic tool |
| ADR-0026 | Protocol vs Harness/Product Boundary | Protocol boundary governance surface |
| ADR-0028 | Settlement Substrate Graduation and Governance Route | Settlement substrate governance; amended 2026-04-23 with graduation clause |
| ADR-0031 | Subgraph Homomorphism Query Contract | Subgraph query contract; M-series milestone anchor |

This is 4 nodes, not 8. The v0.2 candidate will have 36 nodes (32 original + 4 new).

Each promoted ADR node must include:
- `node_type: "adr"` (or the current schema equivalent for ADR nodes)
- `genesis_attested: true`
- `genesis_attested_by: "genesis_agent:01"`
- `signing_key_ref: "artifact:genesis_agent1_pubkey_record_838a"`
- `signature_status: "pending_signing"` — until a signing ceremony is authorized
- `star_map_version: "v0.2_candidate"`
- At least one `GOVERNS` or `CONSTRAINS` edge to the CDL or runtime surface the ADR
  governs (use the canonical CDL node already in the star map where available)

### 4.2 Star map versioning posture

The Phase 1142s signing model established that the Genesis key (Plate 2) signs the v0.1
root envelope only. Later versions require an operational release key (release-key ADR
TBD) or an explicit Genesis exceptional signing.

This window produces:
- `docs/sims/sim_spectral_02/genesis_core_star_map_curated_seed_v0.2.json` (updated seed
  with 4 new accepted ADR nodes)
- `out/genesis_core_star_map_v0.2_candidate.json` (generated candidate — NOT a signed
  artifact)

**The v0.2 candidate is NOT signed.** GENESIS-COMPILE checkpoint #2 (Phase 1150) runs
against the v0.2 candidate. The signing ceremony (tail slot Phase 1156) is conditional
on release-key authorization.

**`out/genesis_core_star_map_v0.1.json` and all v0.1 signed artifacts remain
untouched.** Do not modify them.

### 4.3 GENESIS-COMPILE checkpoint #2 target (Phase 1150)

Run the diagnostic against the v0.2 candidate. Expected improvement:

| Metric | Checkpoint #1 | Checkpoint #2 target |
|--------|--------------|---------------------|
| `authority_traceable_core_nodes` | 31/32 (97%) | ≥ 34/36 (maintains ≥ 94%) |
| Accepted high-authority ADRs still unlinked | ≥ 4 (the 4 now being promoted) | 0 |
| Proposed high-priority ADRs blocked from promotion | — | 5 (recorded with tokens) |
| `basis_reachable_core_nodes` | 17/32 | Expect modest improvement; not the primary metric |

The diagnostic must use a new versioned output path:
`out/genesis_compile_coverage_diagnostic_v0.2_candidate.json`
Do not overwrite `v0.1.json`.

---

## 5. SIM-SPECTRAL-04 Spec Lane

### 5.1 Genesis 32-node composability audit (Phase 1151)

Closes obligation `genesis_32_node_composability_audit_required`.

Classify each of the original 32 signed Genesis nodes into one of:
- `primitive` — axiomatic operation or non-decomposed foundation
- `historical_artifact` — signed record, ceremony, identity, or governance event
- `parameterized_policy` — governance parameter or tunable policy surface
- `claim_composite` — ADR/CDL/spec surface composed from primitives and subclaims
- `runtime_binding_pending` — schema/runtime surface needing code-module linkage

Use the hypothesis table in
`docs/specs/ilc_genesis_claim_composition_projection_plan_1146_v0.1.md` §5 as a
starting point. Phase 1151 must review and confirm or revise each entry.

Deliverable: `out/genesis_32_node_composability_audit_v0.1.json` — machine-readable
classification record with `node_id`, `projection_class`, and `rationale` per node.
Also produce `docs/sims/sim_spectral_04/composability_audit_1151_v0.1.md` as a
human-readable summary.

Gate: all 32 nodes classified; no node left unclassified; token
`genesis_32_node_composability_audit_committed_phase_1151`.

### 5.2 SIM-SPECTRAL-04 program spec (Phase 1152)

Closes obligation `sim_spectral_04_claim_composition_projection_required_before_cdl_085_reconsideration`
— spec only; execution is deferred to Window 1157+.

The program spec must address:

1. **Input:** `out/genesis_claim_composition_projection_v0.1.json` — a derived
   claim-composition graph built from the classification audit (Phase 1151). This file
   does not yet exist; the spec must describe its construction.
2. **Projection build step:** A deterministic tool
   (`tools/build_genesis_claim_composition_projection.py`) that reads the composability
   audit and the v0.1 star map and emits the projected claim-level graph.
3. **Simulation run plan:** Minimum run: S1 against claim-composition projection;
   matched-size S3 and G2 controls mandatory (closes
   `matched_size_controls_required_for_future_spectral_sims`); raw 100-node S3/G2
   comparisons as secondary historical continuity only.
4. **CDL-085 gate criterion:** What positive result from SIM-SPECTRAL-04 would constitute
   sufficient evidence to reconsider CDL-085? Define the pass threshold in the spec.
5. **Scope exclusion:** The projection must not mutate `out/genesis_core_star_map_v0.1.json`
   or any signed artifact.

Deliverable: `docs/sims/sim_spectral_04/program.md`. No simulation runs, no new data
artifacts in Phase 1152 — spec only.

Gate: document exists and contains sections for projection build, run plan, CDL-085 gate
criterion, and matched-size controls mandate. Token:
`sim_spectral_04_program_committed_phase_1152`.

---

## 6. Pre-Public-RC Obligations Lane

### 6.1 Genesis Canonical Lineage Contract pre-ADR spec (Phase 1153)

Closes obligation `genesis_canonical_lineage_contract_required_before_public_rc`.

Produce `docs/specs/ilc_genesis_canonical_lineage_contract_planning_spec_v0.1.md`
as a planning document (not a ratified ADR). This is input for a future ADR-0036
opening in Window 1157+.

The spec must cover:

1. `network_id = H(genesis_root_envelope_hash)` — the binding that makes a fork's network
   identity distinguishable without any single hard-coded node check.
2. Node 0 Merkle inclusion proof — every release carries a proof that Node 0 is in the
   signed Genesis manifest.
3. Operational release key Genesis binding — how release keys inherit from Genesis without
   requiring routine Plate 2 use.
4. Rolling ECU legitimacy windows — canonical ECU/ILC recognition requires continuous
   Genesis-lineage-valid settlement; any lineage break severs ECU recognition.
5. Gossip-domain continuity — `genesis_domain = H(genesis_root_envelope_v0.1)`;
   canonical peers relay only same-domain events.
6. Envelope transition policy — explicit, deliberate process for transitioning from the
   current internal v0.1 signed root envelope hash
   (`ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`) to a public RC
   envelope; addresses obligation `public_rc_envelope_hash_transition_policy_required`.

Reference: `docs/research/ilc_genesis_lineage_fork_resistance_and_license_strategy_v0.1.md`

This is a non-canonical planning document. It does not mutate any CDL, runtime, or
signed artifact.

### 6.2 Pre-public-RC obligations synthesis (Phase 1154)

Produce `docs/specs/ilc_pre_public_rc_obligations_synthesis_1154_v0.1.md` — a structured
register of all remaining pre-public-RC obligations with their current disposition.

Must include:

| Obligation | Token | This window disposition | Remaining gap |
|-----------|-------|------------------------|---------------|
| Canonical Lineage Contract | `genesis_canonical_lineage_contract_required_before_public_rc` | Planning spec drafted Phase 1153; formal ADR opening deferred Window 1157+ | ADR-0036 opening, ratification |
| Truth-primitive permanence | `truth_primitive_permanence_requires_community_ratification_before_genesis_sunset` | Synthesis note only; no CDL mutation | CDL or community ratification event required |
| Envelope transition policy | `public_rc_envelope_hash_transition_policy_required` | Addressed in Phase 1153 spec | Formal ADR/CDL ratification required |
| Contributor agreement | `contributor_agreement_required_before_public_repo` | Synthesis note only | Counsel drafting required |
| License strategy | (parallel counsel track) | Synthesis note only | Counsel review required before public repo |
| Trademark / identity policy | (parallel counsel track) | Synthesis note only | Human + counsel; required before public launch |
| Canon bundle signing failures | (tooling debt) | Pre-existing; carry-forward | Tooling fix required before public RC |
| ADR-0008 acceptance | (prerequisite for Tier-2 star-map promotion) | Review disposition Phase 1148 | ADR-0008 must be accepted before promotion |
| Atlas Tier-2 signing ceremony | (conditional tail slot) | Deferred unless authorized in this window | Release-key ADR or Genesis exceptional signing |

The synthesis doc must not recommend specific license terms or legal conclusions — that
is counsel's role. It records the gap and the routing, not the substance.

---

## 7. CDL Number Assignments

No new CDL is being opened or ratified in this window.

| CDL | Status | Notes |
|-----|--------|-------|
| CDL-085 | SIM-gated; DEFER | Cannot open without positive SIM-SPECTRAL-04 result + explicit human override |
| CDL-086 | **Unassigned** | Next fresh CDL; do not use this window |

---

## 8. Candidate Phase Table

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 1148 | Window sequence lock + ADR-0034/ADR-0008 content review verdict | Foundation / Constitutional | NON-SENSITIVE |
| 2 | 1149 | Atlas Tier-2 curated seed patch — 4 accepted ADRs, v0.2 candidate (36 nodes) | Constitutional | NON-SENSITIVE |
| 3 | 1150 | GENESIS-COMPILE checkpoint #2 | Simulation / Gate | NON-SENSITIVE |
| 4 | 1151 | Genesis 32-node composability audit | Simulation | NON-SENSITIVE |
| 5 | 1152 | SIM-SPECTRAL-04 program spec | Synthesis | NON-SENSITIVE |
| 6 | 1153 | Genesis Canonical Lineage Contract pre-ADR spec | Synthesis | NON-SENSITIVE |
| 7 | 1154 | Pre-public-RC obligations synthesis | Synthesis | NON-SENSITIVE |
| 8 | 1155 | Coherence report + capsule v5.40 + closure gate | Gate | **SENSITIVE** |
| — | 1156 | Atlas Tier-2 signing ceremony (v0.2 star map) | Constitutional | **conditional** |

### Conditional note on Phase 1156

Phase 1156 is a signing ceremony tail slot. It executes only if, by the Phase 1155
closure gate, the human has explicitly authorized one of:

**Scenario A — Operational release key established:**
An ADR for the operational release key exists (ADR-0036 or equivalent) and has been
accepted. Phase 1156 uses the release key to sign the v0.2 star map and transition
envelopes. This is the preferred path.

**Scenario B — Genesis exceptional signing authorized:**
Human explicitly authorizes a Genesis exceptional signing for v0.2 as a deliberate
exception (append-only; must reference prior envelope hash + change_summary; not
routine). Phase 1156 performs a Plate 2 ceremony with the same structure as Phase 1142s.

**Scenario C — No authorization:**
Neither Scenario A nor B is in place at Phase 1155 closure gate. Phase 1156 does not
execute. The v0.2 candidate remains unsigned. Window closes at Phase 1155.

The Phase 1155 closure gate must ask: "Is Phase 1156 signing authorized under Scenario A
or B?" If neither, the closure gate verdict for Phase 1156 is "deferred — not authorized
this window." Window 1148-1155 still closes cleanly without it.

### Note on Phase 1148 sequence lock

Phase 1148 is NON-SENSITIVE. It:
- Commits the window sequence lock
- Performs the ADR status normalization audit across all 10 planning-bridge candidates
- Records disposition tokens for all 10 ADRs (accepted/deferred/blocked)
- Records the `adr_status_normalization_required_before_tier2_promotion` gate as satisfied
- Does NOT open any CDL
- Does NOT mutate the star map

No pre-commit hook required. Commit message: `feat(g8): phase 1148 window 1148-1156 sequence lock`

### Note on Phase 1149 star map patch

Phase 1149 adds 4 accepted ADR nodes to the curated seed and regenerates the candidate
star map (36 nodes total: 32 original + 4 new). It is NON-SENSITIVE because:
- No CDL mutation occurs
- The signed v0.1 artifacts are untouched
- The output is a `_candidate` artifact, not a signed canonical one
- All 5 Proposed ADRs remain outside the star map with blocked-status tokens from Phase 1148

**Prerequisite gate from Phase 1148:** The sequence lock must record
`adr_status_normalization_required_before_tier2_promotion` as satisfied before Phase 1149
executes. Phase 1149 should assert this token is present in the Phase 1148 sequence lock.

The Laplacian builder in `tools/sim_spectral_02.py` must not be called with the v0.2
candidate during the Phase 1149 phase unless a dedicated test is added to confirm
`--s1-topology-file` works with the updated node count.

### Note on Phase 1150 GENESIS-COMPILE checkpoint #2

Phase 1150 runs the existing GENESIS-COMPILE-01 diagnostic tool against the v0.2
candidate. The signed diagnostic `v0.1.json` is NOT regenerated. Outputs:
- `out/genesis_compile_coverage_diagnostic_v0.2_candidate.json`
- `docs/sims/sim_spectral_02/genesis_compile_checkpoint_2_1150_v0.1.md`

The tool invocation must explicitly specify the v0.2 candidate path. If the tool
currently hardcodes the v0.1 path, it must be updated to accept `--star-map-path` and
`--output-path` flags before Phase 1150 executes. Confirm this in Phase 1148.

---

## 9. Sensitivity Classification

### SENSITIVE phases

- **Phase 1155 (closure gate):** Structural window boundary. Requires human GO token.
  No CDL mutation; no pre-commit hook needed. Requires human GO because it is a window
  closure gate.
- **Phase 1156 (conditional — signing ceremony):** Requires human GO token for Scenario A
  or B authorization. If Scenario A: no Plate 2 use; operational release key signs. If
  Scenario B: Plate 2 use; same structure as Phase 1142s; requires explicit human GO after
  Phase 1155 checkpoint.

### NON-SENSITIVE phases

- **Phase 1148:** Sequence lock + content review. No CDL mutation, no star-map mutation.
- **Phase 1149:** Star-map candidate patch. No CDL mutation; signed artifacts untouched.
- **Phase 1150:** GENESIS-COMPILE run. Doc-only output + diagnostic JSON (new versioned
  path, not overwriting v0.1).
- **Phase 1151:** Composability audit. Classification exercise; no mutations to signed
  artifacts.
- **Phase 1152:** SIM-SPECTRAL-04 program spec. Planning document only.
- **Phase 1153:** Lineage Contract planning spec. Non-canonical planning document.
- **Phase 1154:** Pre-public-RC obligations synthesis. Planning document only.

### Conditional phases rule

Phase 1156: before executing, confirm with human whether Scenario A or B is authorized.
If yes, require GO token. If neither is authorized, Phase 1156 does not execute —
no GO token needed for non-execution.

### Pre-commit hook

No CDL mutation is authorized in this window's firm phases. No `ILC_CDL_MUTATION_AUTHORIZED`
invocations needed for Phases 1148–1155.

If Phase 1156 Scenario B (Genesis exceptional signing) executes, there is no CDL
mutation, but the signed artifact output requires the same pre-signing checklist as
Phase 1142s.

---

## 10. Scope Notes for Fixed Phases

### Phase 1148 — Sequence lock + ADR content review

NON-SENSITIVE. No GO token required.

**Deliverables:**
- `docs/specs/ilc_phase_1148_1156_sequence_lock_v0.1.md` — sequence lock
- `docs/phases/phase_1148_window_sequence_lock_adr_review_walkthrough.md` — walkthrough
- `docs/phases/STATUS.md` — Phase 1148 entry

**Required content (sequence lock):**
- Window token: `window_1148_1156_sequence_lock_committed`
- Gate token: `adr_status_normalization_required_before_tier2_promotion` — satisfied
- ADR-0034 disposition: `adr_0034_tier2_deferred_to_window_1166_plus`
- ADR-0012 disposition: `adr_0012_tier2_blocked_status_proposed`
- ADR-0020 disposition: `adr_0020_tier2_blocked_status_proposed` + carry-forward: `adr_0020_acceptance_review_priority_before_tier3_embedding_linkage`
- ADR-0022 disposition: `adr_0022_tier2_blocked_status_proposed`
- ADR-0023 disposition: `adr_0023_tier2_blocked_status_proposed`
- ADR-0008 disposition: `adr_0008_tier2_blocked_status_proposed_not_accepted`
- Confirmed Tier-2 promotion list: ADR-0019, ADR-0026, ADR-0028, ADR-0031 (all Accepted)

**Commit subject:** `feat(g8): phase 1148 window 1148-1156 sequence lock`

---

### Phase 1149 — Atlas Tier-2 curated seed patch

NON-SENSITIVE. No GO token required.

**Deliverables:**
- `docs/sims/sim_spectral_02/genesis_core_star_map_curated_seed_v0.2.json` — updated seed
- `out/genesis_core_star_map_v0.2_candidate.json` — generated candidate star map (NOT a
  signed artifact; filename must include `_candidate` to be unambiguous)
- `tests/test_phase_1149_atlas_tier2_patch.py` — minimum 5 tests
- `docs/phases/phase_1149_atlas_tier2_curated_seed_patch_walkthrough.md` — walkthrough
- `docs/phases/STATUS.md` — Phase 1149 entry

**Test structure:** Minimum 5 tests:

| ID | Test | Gate |
|----|------|------|
| T1 | v0.2 seed file exists and parses as valid JSON | Existence |
| T2 | v0.2 candidate star map exists and has 36 nodes (32 original + 4 accepted ADRs) | Node count |
| T3 | All 4 accepted ADR nodes (0019, 0026, 0028, 0031) present by ID in v0.2 candidate | ADR coverage |
| T4 | All 4 new ADR nodes have `genesis_attested: true` and `signature_status: pending_signing` | Attestation fields |
| T5 | Original v0.1 signed star map is unchanged (node count still 32, root envelope hash unchanged) | Immutability |
| T6 | Phase 1148 sequence lock contains `adr_status_normalization_required_before_tier2_promotion` token | Gate prerequisite |

**v0.1 immutability guard:** Any test file must assert:
- `len(v0_1_nodes) == 32`
- v0.1 root envelope hash == `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`

**Commit subject:** `feat(atlas): phase 1149 tier-2 curated seed patch 4 accepted adr nodes v0.2 candidate`

---

### Phase 1150 — GENESIS-COMPILE checkpoint #2

NON-SENSITIVE. No GO token required.

**Pre-condition check in Phase 1148:** Confirm `tools/genesis_compile.py` (or equivalent)
accepts `--star-map-path` and `--output-path` flags. If not, Phase 1149 must add them
before Phase 1150 can run cleanly.

**Deliverables:**
- `out/genesis_compile_coverage_diagnostic_v0.2_candidate.json` — diagnostic against v0.2 candidate
- `docs/sims/sim_spectral_02/genesis_compile_checkpoint_2_1150_v0.1.md` — checkpoint report
- `tests/test_phase_1150_genesis_compile_checkpoint_2.py` — minimum 3 tests
- `docs/phases/phase_1150_genesis_compile_checkpoint_2_walkthrough.md` — walkthrough
- `docs/phases/STATUS.md` — Phase 1150 entry

**Test structure:** Minimum 3 tests:

| ID | Test | Gate |
|----|------|------|
| C1 | Diagnostic exists and parses as valid JSON with required keys | Existence |
| C2 | `authority_traceable_core_nodes` ≥ 38/40 (≥ 0.95 fraction) | Coverage gate |
| C3 | Signed v0.1 diagnostic is unchanged from Phase 1142s hash | Immutability |

**Checkpoint token:** `genesis_compile_checkpoint_2_pass` (if C2 passes) or
`genesis_compile_checkpoint_2_partial` (if C2 result is below gate). Either token must
appear in the checkpoint report.

**Commit subject:** `atlas(diagnostic): phase 1150 genesis compile checkpoint 2 v0.2 candidate`

---

### Phase 1151 — Genesis 32-node composability audit

NON-SENSITIVE. No GO token required.

**Deliverables:**
- `out/genesis_32_node_composability_audit_v0.1.json` — machine-readable classification
- `docs/sims/sim_spectral_04/composability_audit_1151_v0.1.md` — human-readable summary
- `tests/test_phase_1151_composability_audit.py` — minimum 5 tests
- `docs/phases/phase_1151_genesis_composability_audit_walkthrough.md` — walkthrough
- `docs/phases/STATUS.md` — Phase 1151 entry

**Test structure:** Minimum 5 tests:

| ID | Test | Gate |
|----|------|------|
| A1 | Audit file exists and parses as valid JSON | Existence |
| A2 | Audit covers all 32 original Genesis node IDs | Completeness |
| A3 | Every entry has `projection_class` in the 5 allowed values | Schema validity |
| A4 | Every entry has non-empty `rationale` | Quality |
| A5 | Audit token `genesis_32_node_composability_audit_committed_phase_1151` present in summary doc | Gate token |

**Commit subject:** `sim(spectral-04): phase 1151 genesis 32-node composability audit`

---

### Phase 1152 — SIM-SPECTRAL-04 program spec

NON-SENSITIVE. No GO token required.

**Deliverables:**
- `docs/sims/sim_spectral_04/program.md` — program spec
- `docs/phases/phase_1152_sim_spectral_04_program_spec_walkthrough.md` — walkthrough
- `docs/phases/STATUS.md` — Phase 1152 entry

**Required sections in program spec:**
1. Projection build step (inputs, tool path, output artifact path, determinism requirements)
2. Run plan (S1 against projection; mandatory matched-size controls; historical
   comparisons as secondary)
3. CDL-085 gate criterion (what positive result constitutes sufficient evidence)
4. Scope exclusions (no mutation to v0.1 signed artifacts)
5. Dependency: composability audit (`genesis_32_node_composability_audit_committed_phase_1151`)

**Gate token:** `sim_spectral_04_program_committed_phase_1152`

**Commit subject:** `sim(spectral-04): phase 1152 program spec claim-composition projection`

---

### Phase 1153 — Genesis Canonical Lineage Contract pre-ADR spec

NON-SENSITIVE. No GO token required.

**Deliverables:**
- `docs/specs/ilc_genesis_canonical_lineage_contract_planning_spec_v0.1.md` — planning spec
- `docs/phases/phase_1153_canonical_lineage_contract_spec_walkthrough.md` — walkthrough
- `docs/phases/STATUS.md` — Phase 1153 entry

**Required sections:** network_id derivation, Node 0 Merkle inclusion, release key Genesis
binding, rolling ECU legitimacy windows, gossip-domain continuity, envelope transition
policy (see Section 6.1 of this guidance doc for full spec).

**Must not:** make legal or license recommendations; open an ADR or CDL; mutate any
signed artifact.

**Gate token:** `genesis_canonical_lineage_contract_planning_spec_committed_phase_1153`

**Commit subject:** `docs(genesis): phase 1153 canonical lineage contract pre-adr planning spec`

---

### Phase 1154 — Pre-public-RC obligations synthesis

NON-SENSITIVE. No GO token required.

**Deliverables:**
- `docs/specs/ilc_pre_public_rc_obligations_synthesis_1154_v0.1.md` — obligations register
- `docs/phases/phase_1154_pre_public_rc_obligations_synthesis_walkthrough.md` — walkthrough
- `docs/phases/STATUS.md` — Phase 1154 entry

**Required content:** Structured table per Section 6.2 of this guidance doc. Must not
make legal conclusions. Records gaps and routing only.

**Gate token:** `pre_public_rc_obligations_synthesis_committed_phase_1154`

**Commit subject:** `docs(rc): phase 1154 pre-public-rc obligations synthesis`

---

### Phase 1155 — Coherence report + capsule v5.40 + closure gate

**SENSITIVE.** Requires explicit human GO token before execution.

**Deliverables:**
- `docs/specs/ilc_integration_coherence_report_1155_v0.1.md` — coherence report
- `docs/specs/ilc_antigravity_context_capsule_v5.40.md` — capsule
- `docs/specs/ilc_window_1148_1156_handoff_1155_v0.1.md` — handoff doc
- `tests/test_phase_1155_window_1148_1156_closure_gate.py` — closure gate tests (≥ 14)
- `docs/phases/phase_1155_window_1148_1156_closure_gate_walkthrough.md` — walkthrough
- `docs/phases/STATUS.md` — Phase 1155 entry

**Closure gate must verify:**
- Window sequence lock committed
- ADR status normalization audit complete; all 10 ADR disposition tokens recorded (Phase 1148)
- v0.2 candidate star map exists with 36 nodes (32 + 4 accepted ADRs) (Phase 1149)
- v0.1 signed artifacts unchanged (Phase 1149 immutability gate)
- GENESIS-COMPILE checkpoint #2 result documented (Phase 1150)
- Composability audit complete and covers all 32 original nodes (Phase 1151)
- SIM-SPECTRAL-04 program spec committed (Phase 1152)
- Canonical Lineage Contract planning spec committed (Phase 1153)
- Pre-public-RC obligations synthesis committed (Phase 1154)
- CDL-085 still SIM-gated (no CDL mutation occurred)
- Runtime semantics unchanged
- Phase 1156 authorization question: closed or deferred (must be recorded)
- Capsule v5.40 supersedes v5.39
- Handoff routing correct

**Pre-commit hook:** NOT required (no CDL mutation).

**Closure token:** `window_1148_1156_closed_phase_1155` (if Phase 1156 not executing) or
`window_1148_1156_closure_gate_phase_1155_pass_pending_1156` (if signing authorized).

**Commit subject:** `docs(phase): close window 1148-1156`

---

## 11. Key Dependencies and Open Questions

### Must-resolve at window entry

1. **GENESIS-COMPILE tool flags:** Does the current `GENESIS-COMPILE-01` tool accept
   `--star-map-path` and `--output-path`? If not, Phase 1149 must add flag support.
   Phase 1148 should check this and record the answer.
2. **v0.2 candidate node ID scheme:** The 4 new ADR nodes need canonical IDs. Pattern
   from v0.1: `adr:NNNN_title_fragment`. Confirm the exact title fragments for ADR-0019,
   ADR-0026, ADR-0028, ADR-0031 before Phase 1149.
3. **Curated seed schema:** The v0.1 curated seed
   (`docs/sims/sim_spectral_02/genesis_core_star_map_curated_seed_v0.1.json`) must be
   read before drafting v0.2 to confirm the exact format for adding new nodes.

### Sequencing constraints

- Phase 1149 must complete before Phase 1150 (tool needs the v0.2 candidate to run against)
- Phase 1151 must complete before Phase 1152 (program spec references audit classification)
- Phase 1155 cannot execute without human GO token regardless of prior phase status

### Open questions

1. **Proposed ADR acceptance path — RESOLVED:** ADR-0020 (Knowledge-Node-First) is
   priority for Window 1157+ acceptance review before Tier-3 embedding linkage work begins.
   ADR-0012, ADR-0022, ADR-0023, ADR-0008 follow in a batch after ADR-0020. None of
   these acceptance reviews are in scope for this window. Phase 1148 records
   `adr_0020_acceptance_review_priority_before_tier3_embedding_linkage` as a
   carry-forward token. The clean distinction is maintained: Window 1148-1156 reflects
   accepted canon; Window 1157+ promotes desired canon after governance acceptance.
2. **Release key ADR timing:** Scenario A for Phase 1156 (operational release key) is
   effectively deferred to Window 1157+. Confirm this is the agreed posture in Phase 1148.
3. **GENESIS-COMPILE-01 scope expansion:** Should checkpoint #2 also report Tier-3 linkage
   gaps more precisely (runtime module count, schema node count)? If yes, the tool should
   be updated in Phase 1148 or 1149, not during Phase 1150.
4. **Canon bundle signing failures:** The pre-existing canon bundle test failures
   (`test_canon_bundle_audit_artifact.py`, `test_canon_bundle_pipeline_report.py`) are
   carry-forward tooling debt. This window is not the repair window. Confirm they remain
   pre-existing in Phase 1148 walkthrough.

### Permanently deferred from this window

- CDL-085 opening
- Tier-3 runtime linkage (`schema:*`/`runtime:*` node class)
- SIM-SPECTRAL-04 simulation runs (spec only this window)
- ADR-0036 formal opening (planning spec only)
- SIM-HYPEREDGE-01, SIM-ECU-STABILITY-01
- Any runtime semantic mutation
- Public RC, testnet, or external release work

---

## 12. Known Patterns and Technical Constraints

### Star map versioning pattern

The v0.2 candidate must be clearly distinguished from the signed v0.1. Naming convention:
- Signed artifact: `out/genesis_core_star_map_v0.1.json`
- Unsigned candidate: `out/genesis_core_star_map_v0.2_candidate.json`
- Curated seed: `docs/sims/sim_spectral_02/genesis_core_star_map_curated_seed_v0.2.json`

The `_candidate` suffix in the `out/` artifact name is MANDATORY until a signing ceremony
makes it canonical.

### Diagnostic immutability pattern (Phase 1142s / commit `0eff6e52`)

Any tool that previously wrote to `out/genesis_compile_coverage_diagnostic_v0.1.json`
must be updated to write to a new path when invoked for checkpoint #2. Confirm this in
Phase 1148. The signed v0.1 diagnostic must never be overwritten.

### Phantom edit guard for v0.1 star map

After Phase 1149, any test that reads `out/genesis_core_star_map_v0.1.json` must
assert it has exactly 32 nodes and the root envelope hash is unchanged. Use:
```bash
python -c "import json; d=json.load(open('out/genesis_core_star_map_v0.1.json')); assert len(d['nodes'])==32"
```
Add this to the Phase 1149 phantom edit guard or the Phase 1149 test file.

### Selftest guard chain

Any new Phase 1155 closure gate test file must include the selftest guard pattern
(`ILC_PHASE_1155_GATE_SELFTEST=1`) to avoid re-triggering prior gate logic. Each new
closure gate test file must initialize this guard at the file level.

### JSON canonicalization

Any new tool that writes JSON artifacts must use `json.dumps(..., sort_keys=True,
separators=(",", ":"))` for canonicalization per ILC coding standards.

### `_safe_ratio` pattern (commit `102ed6f2`)

Any future simulation harness that computes per-seed ratios must use `_safe_ratio()` or
equivalent guard against zero-denominator slope values.

---

## 13. Non-Goals and Explicitly Deferred Items

- **CDL-085 opening or ratification** — hard deferred; SIM-gated
- **Runtime semantic changes** — no `ilc_core/` mutations this window
- **SIM-SPECTRAL-04 execution** — program spec only; execution Window 1157+
- **ADR-0036 opening** — planning spec only; formal ADR opening Window 1157+
- **v0.2 star map signing** — conditional tail slot only; not a firm phase
- **ADR-0008 acceptance process** — out of scope; noted as dependency
- **Canon bundle signing fix** — out of scope; pre-existing tooling debt
- **Multi-agent testnet / RC substrate** — deferred to G8/G9 milestones
- **License, trademark, contributor agreement drafting** — counsel-track obligations;
  synthesis note only; no substantive work this window

---

## 14. Key Canonical Anchors for Prompt Drafting

Codex should reference these in every phase prompt for this window:

- `docs/specs/ilc_window_1148_1156_candidate_phase_grouping_v0.1.md` — this document
- `docs/specs/ilc_window_1139_1147_handoff_1147_v0.1.md` — incoming handoff
- `docs/specs/ilc_antigravity_context_capsule_v5.39.md` — current capsule
- `docs/specs/ilc_genesis_claim_composition_projection_plan_1146_v0.1.md` — projection plan and 5-class taxonomy
- `docs/sims/sim_spectral_02/genesis_core_star_map_curated_seed_v0.1.json` — v0.1 curated seed (read before drafting v0.2)
- `out/genesis_core_star_map_v0.1.json` — signed star map (32 nodes; do not mutate)
- `out/genesis_compile_coverage_diagnostic_v0.1.json` — signed diagnostic (do not mutate; immutable)
- `docs/sims/sim_spectral_03/disposition_1146_v0.1.md` — CDL-085 DEFER disposition with 7 carry-forwards
- `docs/research/ilc_genesis_lineage_fork_resistance_and_license_strategy_v0.1.md` — lineage/license strategy memo
- `docs/specs/ilc_window_1130_1138_to_rc_planning_bridge_v0.1.md` — planning bridge (Gap Buckets 2 and 3)
- ADR files for all 8 Tier-2 candidates (read before Phase 1149)

---

## 15. Rationale for Single-Window Scope

This window is scoped to Atlas Tier-2 promotion, composability audit, SIM-SPECTRAL-04
spec, and pre-public-RC obligations planning because:

1. Atlas Tier-2 (Phase 1149) is a prerequisite for GENESIS-COMPILE checkpoint #2 and
   for any Tier-3 runtime linkage work. It is the most actionable next step.
2. The composability audit (Phase 1151) is a blocking obligation for SIM-SPECTRAL-04.
   It can run immediately after the Tier-2 patch using the original 32 signed nodes.
3. SIM-SPECTRAL-04 (Phase 1152) spec-only is the right scope for one window; execution
   is too large to combine with Tier-2 promotion.
4. The Canonical Lineage Contract (Phase 1153) and obligations synthesis (Phase 1154)
   are lightweight planning docs that close 4 of the 7 Phase 1146 carry-forward
   obligations at the planning level, giving the counsel track a structured entry point.
5. Keeping the signing ceremony conditional (Phase 1156) prevents forcing a signing
   decision before the operational release key architecture is ready.

If Phase 1156 does not execute, the window closes at Phase 1155 with the v0.2 candidate
unsigned. Window 1157+ will open the release key ADR and schedule the v0.2 signing.
