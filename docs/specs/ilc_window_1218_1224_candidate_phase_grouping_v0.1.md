# ILC Window 1218-1224: Candidate Phase Grouping

**Author:** Claude Code (local planning synthesis)
**Date:** 2026-05-05
**Baseline:** Window 1209-1217 CLOSED at Phase 1217 (`window_1209_1217_closed_phase_1217`,
`window_1209_1217_closure_gate_verdict=pass`). Post-closure audit complete
(`post_closure_code_audit_1217_verdict=pass_after_fixes`). Capsule v5.47 is current.
**Planning note:** Candidate grouping only. Phase 1218 sequence lock publishes the locked
order. Sensitive phases require explicit human GO.

---

## 1. Window Objective

Window 1218-1224 has one hard-scheduled obligation and three conditional ones:

**Primary (firm):** Truth-primitive permanence ratification event. Per Phase 1211 packet,
target ratification window is 1218-1224; hard unsafe-after boundary is Window 1225-1232
closure. This window is the target — the ratification event must complete or be explicitly
blocked by a human decision with a new unsafe-after bound.

**Conditional:**
- CDL-086 ratification — if counsel disposition is provided before `GO Phase 1220`.
- v0.2 signing ceremony — if explicit authorization token is issued.
- Reciprocal fetch admission model spec — design artifact only; no implementation mandate
  this window. Produces the spec and CDL/ADR routing needed to eventually supersede the
  static rate limiter circuit breaker.

Non-goals:

- No public launch claim.
- No public repository publication.
- No CDL-086 ratification without counsel disposition.
- No Genesis v0.1 mutation.
- No v0.2 signing without explicit authorization token.
- No implementation of the reciprocal fetch admission model (design spec only this window).

---

## 2. Incoming State

Carry-forward tokens:

- `truth_primitive_permanence_ratification_packet_committed_phase_1211`
- `truth_primitive_permanence_ratification_event_required_window_1218_1224`
- `truth_primitive_permanence_unsafe_after_window_1225_1232_closure`
- `cdl_086_ratification_deferred_pending_counsel_disposition`
- `v0_2_signing_ceremony_deferred_pending_signing_authorization`
- `reciprocal_fetch_admission_model_required`
- `transport_abuse_circuit_breaker_not_final_scaling_policy`

RC2 gate status entering this window:

| # | Gate | Status |
|---|------|--------|
| 1 | CDL-085 ratified | SATISFIED |
| 2 | v0.2 signing | OPEN — deferred, target this window if authorized |
| 3 | Tier-3 runtime linkage | SATISFIED |
| 4 | Packaging blocker progressed | PREP-COMPLETE / PRELOCKED / DEFERRED (counsel open) |
| 5 | Persistent rate limiter | WIRED + AUDIT-HARDENED |
| 6 | Truth-primitive permanence | PACKET-COMMITTED — ratification event required THIS WINDOW |

---

## 3. Phase Table

| Phase | Topic | Sensitivity | Character |
|-------|-------|-------------|-----------|
| 1218 | Window sequence lock | SENSITIVE | Firm; requires `GO Phase 1218` |
| 1219 | Truth-primitive permanence ratification ceremony | SENSITIVE | Firm; requires `GO Phase 1219` + human signers |
| 1220 | CDL-086 counsel disposition + ratification | SENSITIVE / constitutional | Requires `GO Phase 1220` + counsel disposition; contingent |
| 1221 | v0.2 signing ceremony | SENSITIVE if executed | Requires `v0_2_signing_ceremony_authorized_phase_1221` + `GO Phase 1221`; skip-default |
| 1222 | Reciprocal fetch admission model spec | NON-SENSITIVE | Firm; mandatory design artifact |
| 1223 | Coherence report + capsule v5.48 | NON-SENSITIVE | Firm |
| 1224 | Window closure gate | SENSITIVE | Firm; requires `GO Phase 1224` |

---

## 4. Phase Specifications

### Phase 1219 — Truth-Primitive Permanence Ratification Ceremony

**SENSITIVE. Requires `GO Phase 1219`.** This is a multi-party governance event.
Codex prepares all ceremony materials. The actual ratification artifact requires human
signers per the Phase 1211 packet §4 ratifier class:

- At least 3 distinct Genesis founding/member signers.
- At least 1 external witness signer (not counted among the 3).
- Unanimous approval from all participating ratifiers.

**Two-stage execution:**

**Stage A — Ceremony preparation (Codex, after `GO Phase 1219`):**

Produce:

1. `docs/specs/ilc_truth_primitive_permanence_ceremony_materials_1219_v0.1.md` —
   ceremony package containing:
   - Link to Phase 1211 packet
   - Evidence bundle per packet §3 (all CDL/ADR/runtime/Genesis/SHA references resolved
     to actual current values)
   - Signer roster template (fields: signer name, signer class, date, approval/objection,
     signature or acknowledgement token)
   - Dissent field (required even if empty; must be explicitly recorded)
   - Threshold statement: Genesis authority attestation constitutes ratification;
     optional witness attestations may be included; dissent field required even if empty

2. A proposed ratification summary in the same file:
   - Primitive set covered (7 ADR-0004 New Seven; `star.map` excluded)
   - `commit.epoch` consensus-only exception carried forward
   - Non-bypass rule verbatim from packet §8
   - Pending signer signatures

**Stage B — Ratification commit (Human-authorized, after signatures collected):**

Human reviews ceremony materials and, when ready, issues `GO Phase 1219 ratification
commit`. Codex then:

1. Commits `docs/specs/ilc_truth_primitive_permanence_ratification_event_1219_v0.1.md`
   with the completed artifact — Genesis authority attestation (commit-anchored),
   optional witness attestations (may be empty list), dissent field (explicit even if
   empty), non-bypass rule verbatim.
2. Records token: `truth_primitive_permanence_genesis_attested_phase_1219`
3. Closes token: `truth_primitive_permanence_ratification_event_required_window_1218_1224`

**If ratification cannot complete this window** (signers unavailable, objection raised):
- Record: `truth_primitive_permanence_ratification_blocked_phase_1219`
- Record precise blocker (one sentence per unresolved item)
- Human must decide: extend window target or accept unsafe-after approach to Window 1225-1232

**No CDL mutation required** unless ceremony determines constitutional register change is
needed (packet §5 event mechanics). Default assumption: signed ceremony artifact suffices.

Minimum tests (in `tests/test_phase_1219_permanence_ratification.py`, minimum 4):

1. `test_ceremony_materials_file_exists`
2. `test_ceremony_materials_contains_evidence_references` — all 10 evidence bundle items
   from packet §3 resolved with actual values
3. `test_ratification_event_file_exists_or_blocked_token_recorded` — either ratification
   event doc committed OR blocked token present (not neither)
4. `test_ratification_token_or_blocked_token_mutually_exclusive` — exactly one of
   `truth_primitive_permanence_genesis_attested_phase_1219` or
   `truth_primitive_permanence_ratification_blocked_phase_1219` is present

Tokens:
- `truth_primitive_permanence_genesis_attested_phase_1219` (if complete)
- OR `truth_primitive_permanence_ratification_blocked_phase_1219` (if blocked)

Commit subjects:
- `docs(governance): phase 1219 permanence ceremony materials`
- `feat(governance): phase 1219 truth-primitive permanence ratified`

---

### Phase 1220 — CDL-086 Counsel Disposition + Ratification

**SENSITIVE / constitutional.** Requires `GO Phase 1220`.

CDL mutation environment required:
```
ILC_CDL_MUTATION_AUTHORIZED=1
ILC_CDL_MUTATION_PHASE=1220
```

**Contingent on:** Counsel disposition for all 5 counsel items from CDL-086 prelock §5
(license, contributor agreement, trademark, documentation license, commit-history treatment).
If disposition is not provided, record deferral token and skip:
`cdl_086_ratification_deferred_pending_counsel_disposition`

**If executed — same two-commit pattern as Phase 1214:**

Commit 1 — CDL register mutation only:
- CDL-086 status: PRELOCKED → RATIFIED
- Evidence doc: `docs/specs/ilc_cdl_086_ratification_evidence_1220_v0.1.md`
- Evidence doc records: all 9 prelock conditions from Phase 1204 §5 disposed; counsel
  disposition for each of 5 counsel items; references to Phase 1213 artifact tokens
- Token: `cdl_086_ratified_phase_1220`

Commit 2 — empty or skipped (CDL-086 has no runtime constant).

**CDL-086 block remains in force** until ratified. Ratification satisfies the governance
precondition but does not itself authorize any public-launch-adjacent act — separate
constitutional act(s) required for launch.

Token (if executed): `cdl_086_ratified_phase_1220`
Token (if deferred): `cdl_086_ratification_deferred_pending_counsel_disposition`

Commit subject: `feat(cdl): CDL-086 public-launch packaging blocker ratified (Phase 1220)`

---

### Phase 1221 — v0.2 Signing Ceremony (Conditional)

Default: **skip.** Authorization not expected this window unless explicitly issued.

Requires: `v0_2_signing_ceremony_authorized_phase_1221` + `GO Phase 1221`.
Follows ADR-0036 signing sequence. Pre-execution SHA check required.

Skip token: `v0_2_signing_ceremony_deferred_pending_signing_authorization`

---

### Phase 1222 — Reciprocal Fetch Admission Model Spec

**NON-SENSITIVE. Mandatory design spec phase — two documents, no runtime code.** This is
the design-spec phase for Window 1218-1224, producing substrates for two future
implementation tracks.

**Two-layer separation (explicit):** The graph projection interface (Deliverable B) is
Layer 1/2 prior art — the canonical read-only export substrate agents consume. The L3
sidecar infrastructure — the protocol by which external apps (including human visualization
tools) attach to ILC, their contracts, authorization model, and data-consumption guarantees
— is a *separate* future spec. Both layers are required before a visualization tool can be
properly built. Neither is implemented this phase. L3 sidecar infrastructure spec is
deferred to Window 1225+.

Deliverable: `docs/specs/ilc_reciprocal_fetch_admission_model_spec_1222_v0.1.md`

The spec must answer all of the following (no "TBD" for any item that has a current best
answer; explicit "open question" for items that genuinely require further evidence):

**1. Problem statement**
Why the static limiter is insufficient at ILC scale: fast digital agents, varying
legitimate pull demand, asymmetric inbound/outbound pressure, fixed caps as long-term
economic distortion.

**2. Model parameters (concrete proposed values)**
- Baseline free `WANT-BLOCK` capacity per requester per window (proposed default)
- Additional capacity per unit of CDL-078 routing reputation (proposed formula)
- Additional capacity from ECU/stake escrow (proposed rate and escrow mechanics)
- Optional puzzle requirement threshold (when does Hashcash-style proof of work kick in)
- Abuse debt accumulation rule (when does inbound pull pressure exceed useful outbound
  contribution enough to trigger penalty)
- Minimum capacity floor (legitimate nodes should not be starved)

**3. Interaction with existing CDLs/ADRs**
- CDL-077 (rate limiting): which provisions are superseded vs preserved
- CDL-078 (delivery / routing reputation): how reputation scores are consumed
- CDL-060 (gossip): whether gossip pull capacity is in scope
- CDL-054 (validator rewards): whether validator stake escrow qualifies

**4. Constitutional routing**
- Which CDL(s) would need to be opened and ratified to govern this model
- Whether existing CDLs can be amended or whether new CDL(s) are required
- Estimated window target for implementation (not this window — later)

**5. Static limiter supersession boundary**
- Conditions under which the static limiter may be deprecated
- Minimum: reciprocal admission model implemented, tested, and ratified in governing CDL

Minimum tests (in `tests/test_phase_1222_reciprocal_fetch_admission_spec.py`, minimum 3):

1. `test_spec_file_exists`
2. `test_spec_contains_token` — `reciprocal_fetch_admission_model_spec_committed_phase_1222`
3. `test_spec_contains_all_required_sections` — all 5 sections present; check individually
   or parametrize

Token: `reciprocal_fetch_admission_model_spec_committed_phase_1222`
(consumes: `reciprocal_fetch_admission_model_required`)

Commit subject: `docs(spec): phase 1222 reciprocal fetch admission model spec`

---

### Phase 1223 — Coherence Report + Capsule v5.48

Standard synthesis phase. Record actual verdicts for Phases 1218-1222. Capsule delta:

```
**Version**: v5.48
**Supersedes**: v5.47
**Produced**: Phase 1223, Window 1218-1224
**Token**: capsule_v5_48_supersedes_v5_47
```

Capsule must record:
- Truth-primitive permanence ratification status (attested or blocked, with token)
- CDL-086 status (ratified or deferred)
- v0.2 signing status
- `reciprocal_fetch_admission_model_spec_committed_phase_1222` status
- Signed Genesis v0.1 immutability confirmed
- Immutable diagnostic SHA confirmed: `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56`
- Phase 1224 closure pending

Token: `capsule_v5_48_supersedes_v5_47`

---

## 5. Open Human Decisions

Before Phase 1218 sequence lock or at first execution:

1. **Truth-primitive permanence attestation format** — Phase 1219 Stage B requires
   Genesis authority attestation. Before `GO Phase 1219 ratification commit`, confirm:
   - Preferred attestation form (committer identity on the ratification commit itself,
     explicit acknowledgement statement in the doc, or equivalent commit-anchored form)
   - Whether any additional witnesses will contribute optional attestations this window

2. **CDL-086 counsel disposition** — before `GO Phase 1220`:
   - Counsel-approved disposition for each of the 5 items, OR
   - Explicit human-authorized constitutional deferral per item
   Without one of these, Phase 1220 skips.

3. **v0.2 signing authorization** — issue `v0_2_signing_ceremony_authorized_phase_1221`
   if signing is to proceed this window. Otherwise carry-forward token is refreshed.

---

## 6. Sensitivity Classification

**SENSITIVE** (require explicit GO):
- Phase 1218 (sequence lock)
- Phase 1219 (permanence ratification ceremony — also requires human signers for Stage B)
- Phase 1220 (CDL-086 ratification, if counsel disposition satisfied)
- Phase 1221 (v0.2 signing, if authorized)
- Phase 1224 (closure gate)

**NON-SENSITIVE** (Codex may proceed after prompt approval):
- Phase 1222 (reciprocal fetch admission model spec)
- Phase 1223 (coherence + capsule)

**CDL mutation environment** required for Phase 1220 only:
`ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1220`

---

## 7. Carry-Forward Tokens

Consuming:
- `truth_primitive_permanence_ratification_packet_committed_phase_1211`
- `truth_primitive_permanence_ratification_event_required_window_1218_1224`
- `cdl_086_ratification_deferred_pending_counsel_disposition`
- `v0_2_signing_ceremony_deferred_pending_signing_authorization`
- `reciprocal_fetch_admission_model_required`
- `transport_abuse_circuit_breaker_not_final_scaling_policy`

Expected new tokens:
- `window_1218_1224_sequence_lock_committed`
- `truth_primitive_permanence_genesis_attested_phase_1219` OR `truth_primitive_permanence_ratification_blocked_phase_1219`
- `cdl_086_ratified_phase_1220` OR `cdl_086_ratification_deferred_pending_counsel_disposition`
- `v0_2_signing_ceremony_deferred_pending_signing_authorization` OR signed-v0.2 token
- `reciprocal_fetch_admission_model_spec_committed_phase_1222`
- `capsule_v5_48_supersedes_v5_47`
- `window_1218_1224_closed_phase_1224`

---

## 8. Guardrails

- Do not mutate signed Genesis v0.1.
- Verify immutable diagnostic SHA before Phase 1224:
  `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56`
- No `float` for any economic or attribution value — `Decimal` throughout.
- No `assert` for production constraints — `if not: raise ValueError("token")`.
- No wall-clock as protocol source of truth.
- Phase 1219 ratification artifact must be reproducible from repository artifacts alone —
  no oral/social convention as sole evidence of permanence.
- Phase 1220 requires two-phase check: CDL mutation commit must not include runtime
  changes. CDL-086 has no runtime constant so Commit 2 may be empty.
- No CDL-086 public-launch claim from ratification alone — separate constitutional act(s)
  required for any launch-adjacent act.
- Phase 1222 must not propose implementation — design spec only; no runtime code this phase.
- Do not drop `transport_abuse_circuit_breaker_not_final_scaling_policy` framing until
  the reciprocal admission model is ratified and implemented.
