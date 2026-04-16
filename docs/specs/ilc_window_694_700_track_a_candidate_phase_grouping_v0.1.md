# ILC Window 694-700: Track A Candidate Phase Grouping (Codex Lead)

**Author:** Claude (architectural reviewer)
**Date:** 2026-04-16
**Baseline:** Window 687-692 CLOSED. Phase 693 addendum COMPLETE (`cf9cb777`).
Mysticeti selected as Tier 1 primary for Option B. CDL-062 open (sovereign
substrate research CDL, Window 687+). Active window: 693-700. Two parallel
tracks: Track A (Codex, this doc) + Track B (Gemini M-series).
**Reference:** `docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md` §7

---

## 1. Window identity and scope

Window 694-700 is the constitutional closure and governance-preparation
half of the 693-700 window. Track A (Codex) is responsible for:

1. **CDL-063 opening** — agent sender authorization envelope; hard gate for
   Track B M-009 testnet approval (see §3 inter-lane dependency note).
2. **CDL-017 opening** — validator governance framework; must open before any
   lane authorizing first non-Genesis validator deployment.
3. **Settlement-state CDL** — Phase 687 settlement-state enumeration →
   ratified constitutional law.
4. **Row-5 mechanism proof** over Mysticeti concrete substrate model.
5. **Row-7 TLC model check** — `ilc_dag_censorship_bounds.tla` must pass
   before row-7 can close.
6. **Row-8 Mysticeti sovereign configuration** confirmation vs row-8 criteria.
7. **Coherence + capsule v4.4**.
8. **Window 693-700 closure gate**.

Track A does NOT:
- select the final Option-B production configuration,
- ratify CDL-017 (opening only; ratification is a later window),
- ratify CDL-063 (opening only; ratification gates on M-series progress),
- make any public-launch or token-issuance claim.

---

## 2. Inter-lane dependencies (critical — read before sequencing)

Track B (Gemini M-series) has one hard constitutional dependency on Track A
within this window:

**CDL-063 must be opened by Track A before M-009 testnet is approved.**

SEC-001 audit finding (2026-04-16, `486b6896`): `ECUTransfer` carries no
sender signature. Any party can forge a transfer against any AgentID's
balance; honest validators cannot detect the forgery. This is a critical
pre-testnet security gap that requires a CDL vehicle to authorize the fix.

- CDL-062 is already open (sovereign substrate research CDL, Window 687+).
- CDL-063 is the next available number.
- Tracking token: `sec_001_agent_sender_auth_cdl_063_required_before_m009`
- Full SEC-001 entry: `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md` §6
- TODO.txt block: `[TODO – M-Series Security Deferred Items (HARD GATES before M-009 testnet)]`
- Hard gate token: `m009_blocked_until_sec_001_sec_002_sec_003_resolved`

**Sequencing implication:** CDL-063 opening should occur at Phase 694 or
695 — early in the window — so Track B is not blocked if M-series moves
quickly through M-008 and approaches M-009 approval.

CDL-017 (Track A) does NOT gate any Track B phase before M-019.
All other Track A/Track B hard blockers: none within window 693-700.

---

## 3. Operationally obligated versus deferred

### 3.1 Obligated in this window (Track A)

- CDL-063 opening stub (agent sender authorization envelope, SEC-001 vehicle)
- CDL-017 opening stub (validator governance framework)
- Settlement-state CDL opening (enumeration → law)
- Row-5 mechanism proof over Mysticeti concrete model
- Row-7 TLC model check evidence (`ilc_dag_censorship_bounds.tla`)
- Row-8 Mysticeti sovereign configuration confirmation
- Coherence report + capsule v4.4
- Window 693-700 closure gate

### 3.2 Explicitly deferred

- CDL-063 ratification (M-series implementation progress required first)
- CDL-017 ratification (validator set dynamics; activation planning is 701+)
- Settlement-state CDL ratification (may extend past this window)
- Final Option-B substrate winner selection
- Production validator deployment
- Public launch or token-issuance claims
- Row-5 final closure (mechanism proof is a prerequisite, not the closure)

---

## 4. Governing constraints inherited from prior windows

Constitutional anchors that govern this window:
- Row-6: upstream/downstream protocol legitimacy boundary — not relaxable
- Row-7: censorship resistance and exitability — TLC must pass
- Row-8: independence from external constitutional centers
- Row-5: privacy-preserving public legitimacy — narrowed, not closed
- CDL-039, CDL-044: transport invariants — carry-forward, not reopened
- CDL-017: `unimplemented!` hooks in M-series Rust code gate on this CDL
  but CDL-017 ratification itself is not a this-window requirement
- ADR-0011 amendment (2026-04-16): SEC-002 network discriminator requirement
  for QUIC transport — Track-B-internal, but Track A aware

---

## 5. Candidate phase table

| Order | Phase | Topic | Character | Sensitivity |
|---|---:|---|---|---|
| 1 | 694 | Sequence lock + CDL-063 opening stub (SEC-001 vehicle) | Gate / Planning | **SENSITIVE** |
| 2 | 695 | CDL-017 opening stub (validator governance framework) | Gate / Constitutional | **SENSITIVE** |
| 3 | 696 | Settlement-state CDL opening (enumeration → law) | Constitutional | **SENSITIVE** |
| 4 | 697 | Row-5 mechanism proof over Mysticeti substrate model | Research / Proof | **SENSITIVE** |
| 5 | 698 | Row-7 TLC model check evidence (`ilc_dag_censorship_bounds.tla`) | Research / Formal | planning |
| 6 | 699 | Row-8 Mysticeti sovereign configuration confirmation | Analysis / Criteria | planning |
| 7 | 700 | Coherence report + capsule v4.4 + window 693-700 closure gate | Gate / Handoff | **SENSITIVE** |

Note: phases 694-700 map only the Track A constitutional lane.
Track B (Gemini M-series) and Track C (RC) run in parallel and are not
scheduled here. Track B scope is documented in
`docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`.

---

## 6. Scope notes for candidate phases

### Phase 694 — sequence lock + CDL-063 opening stub

Deliverables:
- `docs/specs/ilc_phase_694_700_sequence_lock_v0.1.md`
- `docs/specs/ilc_cdl_063_opening_stub_694_v0.1.md`

Required content for CDL-063 stub:
- Cite SEC-001 audit finding (`486b6896`, 2026-04-16) as the opening rationale
- Scope: agent sender authorization envelope for ECU fast-path transfers
- Note interaction with CDL-042 (globally flat namespace, key-derived agent_id)
  — sender verification must be consistent with CDL-042 key derivation model
- Bounded scope: CDL-063 opens the authorization lane only; it does not
  prescribe the specific signature scheme or wire format (those are Track B
  M-series implementation decisions under CDL-063 ratification scope)
- Non-goal: CDL-063 does not reopen CDL-039 transport invariants
- State gate token: `sec_001_agent_sender_auth_cdl_063_required_before_m009`
- State that M-009 testnet approval is blocked until CDL-063 opens and
  Track B wires sender verification into ECUTransfer

Required content for sequence lock:
- Inherit the 692 handoff and Phase 693 addendum as the baseline
- Name the inter-lane dependency (CDL-063 → M-009 gate)
- Lock the Track A deliverable list for 694-700
- State Track B and Track C continue in parallel under their own sequence locks

### Phase 695 — CDL-017 opening stub (validator governance framework)

Deliverables:
- `docs/specs/ilc_cdl_017_opening_stub_695_v0.1.md`

Required content:
- Cite M-007 `unimplemented!` hooks as the opening context:
  `admit_validator` and `eject_validator` are `CDL-017`-gated stubs
- Define the scope boundary: CDL-017 governs the on-chain/protocol mechanism
  for validator admission and ejection; it does not govern who may run a
  validator in the near-term testnet context (that remains Genesis config only)
- State that CDL-017 ratification is explicitly deferred; this phase opens
  the CDL vehicle and commits to ratification as a 701+ window action
- SEC-004 dependency note: epoch/validator historical binding (M-series SEC-004)
  activates once CDL-017 enables dynamic validator sets; SEC-004 resolution
  must be named in the CDL-017 ratification planning docs
- CDL-055/056 interaction: existing validator participation stake and trust-tier
  elevation CDLs already ratified — CDL-017 must not silently supersede their
  clauses without explicit carry-forward or amendment provisions

### Phase 696 — settlement-state CDL opening

Deliverables:
- `docs/specs/ilc_settlement_state_cdl_opening_696_v0.1.md`

Required content:
- Elevate Phase 687 settlement-state enumeration
  (`docs/specs/ilc_settlement_state_enumeration_and_submission_model_687_v0.1.md`)
  from planning artifact to constitutional CDL vehicle
- Define the settlement-state CDL scope: what counts as durable ILC protocol
  state for Option B substrate finalization purposes
- Explicitly inherit the upstream/downstream legitimacy boundary from row 6
  — the settlement substrate may not author protocol legitimacy, only carry it
- State ratification path: may extend past this window depending on Mysticeti
  implementation progress in Track B

### Phase 697 — row-5 mechanism proof over Mysticeti substrate model

Deliverables:
- `docs/specs/ilc_row_5_mechanism_proof_mysticeti_697_v0.1.md`

Required content:
- Re-derive the row-5 privacy-preserving public legitimacy claim against the
  Mysticeti concrete architecture (owned-object fast path + shared-object
  epoch settlement)
- Show that the row-5 partial narrowing from Phase 682 still holds under
  Mysticeti's block structure, validator set, and gossip assumptions
- Identify any new row-5 gaps introduced by Mysticeti's specific design
- Closing condition: row-5 moves from `partial` to `spec_closed_runtime_pending`
  only when the proof satisfies all inherited narrowing criteria, OR a new
  narrowing decision is made in this phase

### Phase 698 — row-7 TLC model check evidence

Deliverables:
- `docs/specs/ilc_dag_censorship_bounds_tlc_evidence_698_v0.1.md`
- TLC model check log or summary (may reference external artifact if large)

Required content:
- `ilc_dag_censorship_bounds.tla` TLC run is required before row-7 can close
- Document TLC parameters, validator count, fault tolerance assumptions,
  censorship scenario catalog
- If TLC passes: row-7 moves to `spec_closed_runtime_pending`
- If TLC reveals gaps: document them as hard carry-forwards; row-7 stays open

### Phase 699 — row-8 Mysticeti sovereign configuration confirmation

Deliverables:
- `docs/specs/ilc_row_8_mysticeti_sovereign_config_699_v0.1.md`

Required content:
- Map Mysticeti sovereign configuration against row-8 selection criteria lock
  (`docs/specs/ilc_rows_7_8_selection_criteria_lock_675_v0.1.md`)
- Confirm that Mysticeti in sovereign ILC deployment mode satisfies
  independence from external constitutional centers
- If any row-8 criterion is not yet satisfied: name the gap and the
  required resolution path
- Note that this is a confirmation check, not a re-opening of row-8

### Phase 700 — coherence report + capsule v4.4 + closure gate

Deliverables:
- `docs/specs/ilc_coherence_report_700_v0.1.md`
- Updated capsule (v4.4)
- Closure gate artifact: `docs/specs/ilc_window_693_700_closure_gate_700_v0.1.md`

Required content (closure gate):
- CDL-063 opened and gate token confirmed (`sec_001_agent_sender_auth_cdl_063_required_before_m009`)
- CDL-017 opened
- Settlement-state CDL opened
- Row-5 disposition (proof published; new status stated explicitly)
- Row-7 disposition (TLC evidence published; new status stated explicitly)
- Row-8 disposition (Mysticeti config confirmed; new status stated explicitly)
- Track B status as of Phase 700 (non-blocking summary; Track B is parallel)
- Capsule v4.4 published
- Explicit statement of what carries forward into Window 701+

---

## 7. Main conversation questions for this window

The phase work is downstream of these human decisions:

1. Should CDL-063 open at Phase 694 as Track A work, or should opening
   be delegated to Track B with Track A only registering the gate requirement?
2. How tightly should CDL-017 scope bind to the M-series `unimplemented!`
   hooks vs. the broader validator governance constitutional design?
3. Should the settlement-state CDL ratification be attempted in 694-700
   or is a 701+ ratification more honest given Track B timeline uncertainty?
4. Is the row-5 mechanism proof deliverable in one phase, or does it require
   a separate research-and-prove cycle that extends past Phase 697?
5. Is the `ilc_dag_censorship_bounds.tla` spec already sufficiently drafted
   for TLC check, or does Phase 698 need to absorb drafting work too?
6. What exactly should Phase 700 authorize about Track B M-series progress,
   and what remains deferred?

---

## 8. Sequence-lock input status

This artifact is a required input to the Phase 694 sequence lock. The Phase
694 sequence lock must cite it and may not silently drop any of the obligated
deliverables or inter-lane dependency requirements defined above.

The inter-lane CDL-063 dependency (§2) is load-bearing and must appear
explicitly in the Phase 694 sequence lock even if the rest of this grouping
is modified during the session.

---

## 9. What this candidate grouping does not claim

This artifact does not claim:
- CDL-063 is already open
- CDL-017 is already open
- row-5 can be skipped now that Mysticeti is selected
- row-7 TLC evidence already exists
- Track B M-009 is already approved
- any public-launch or token-issuance right
- Option B final winner selection has occurred
