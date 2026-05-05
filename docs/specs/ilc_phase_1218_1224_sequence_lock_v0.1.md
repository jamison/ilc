# ILC Phase 1218-1224 Sequence Lock v0.1

**Date:** 2026-05-05
**Status:** committed
**Window:** 1218-1224
**Phase:** 1218

`window_1218_1224_sequence_lock_committed`

---

## 1. Authorization and Boundary

Window 1218-1224 sequence lock was authorized by explicit human token:

`GO Phase 1218`

This sequence lock authorizes Phase 1218 only. It locks the order and assumptions for
Window 1218-1224. Later phases must execute in order under their own sensitivity rules.

This lock does not authorize:

- truth-primitive permanence ratification;
- CDL-086 ratification;
- v0.2 signing ceremony execution;
- release-key generation or registration;
- public repository publication;
- public RC or public launch claim;
- signed Genesis v0.1 mutation;
- Genesis Atlas v0.2 signing.

Phase 1219 remains SENSITIVE and requires explicit `GO Phase 1219`. Its ratification
mechanism is Genesis authority attestation, not a multi-party signer roster. Phase 1220
remains SENSITIVE and requires explicit `GO Phase 1220` plus counsel disposition before
any CDL mutation. Phase 1221 remains conditional and requires
`v0_2_signing_ceremony_authorized_phase_1221` plus explicit `GO Phase 1221`.
Phase 1224 remains SENSITIVE and requires explicit `GO Phase 1224`.

---

## 2. Window Header

| Field | Value |
|-------|-------|
| Window | 1218-1224 |
| Baseline closure commit | `09bef7e7` (Window 1209-1217 closure) |
| Post-closure audit hardening commit | `55901768` |
| Active guidance commit | `9802536a` |
| Planning-index guidance commit | `1851f099` |
| Agent graph projection scope commit | `c85193f2` |
| Genesis attestation correction commit | `4b495342` |
| Incoming capsule | `docs/specs/ilc_antigravity_context_capsule_v5.47.md` |
| Incoming handoff | `docs/specs/ilc_window_1209_1217_handoff_1217_v0.1.md` |
| Prior closure token | `window_1209_1217_closed_phase_1217` |
| Current guidance | `docs/specs/ilc_window_1218_1224_candidate_phase_grouping_v0.1.md` |
| Phase prompts | `docs/phases/phase_1218_*` through `docs/phases/phase_1224_*` |
| CDL frontier | CDL-085 ratified; CDL-086 prelocked, not ratified |
| Runtime frontier | φ-bound enforcement live; persistent limiter wired and audit-hardened |
| Genesis v0.1 root envelope hash | `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c` |
| Immutable diagnostic SHA | `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56` |

---

## 3. Incoming Carry-Forward Tokens

| Token | Window 1218-1224 routing |
|-------|--------------------------|
| `truth_primitive_permanence_ratification_packet_committed_phase_1211` | Phase 1219 ceremony materials and Genesis attestation path |
| `truth_primitive_permanence_ratification_event_required_window_1218_1224` | Phase 1219 target event or explicit blocker |
| `truth_primitive_permanence_unsafe_after_window_1225_1232_closure` | Phase 1219 and Phase 1224 deadline checks |
| `cdl_086_ratification_deferred_pending_counsel_disposition` | Phase 1220 conditional ratification or deferral |
| `v0_2_signing_ceremony_deferred_pending_signing_authorization` | Phase 1221 skip-default signing slot |
| `reciprocal_fetch_admission_model_required` | Phase 1222 design spec |
| `transport_abuse_circuit_breaker_not_final_scaling_policy` | Phase 1222 scaling-policy boundary |

---

## 4. Locked Phase Order

| Phase | Topic | Sensitivity | Execution status |
|-------|-------|-------------|------------------|
| 1218 | Window sequence lock | SENSITIVE | authorized by `GO Phase 1218` |
| 1219 | Truth-primitive permanence ratification ceremony | SENSITIVE | not authorized by this lock |
| 1220 | CDL-086 counsel disposition + ratification | SENSITIVE / constitutional | not authorized by this lock |
| 1221 | v0.2 signing ceremony | SENSITIVE if executed | not authorized by this lock |
| 1222 | Reciprocal fetch admission model spec | NON-SENSITIVE | ordered after 1219-1221 dispositions |
| 1223 | Coherence report + capsule v5.48 | NON-SENSITIVE | ordered after 1222 |
| 1224 | Window closure gate | SENSITIVE | not authorized by this lock |

---

## 5. Human Decisions Recorded

- Truth-primitive permanence ratification is by Genesis authority attestation. Optional
  witness attestations may be recorded, but no multi-party signer roster is required for
  Genesis bootstrap governance.
- CDL-086 ratification must skip with `cdl_086_ratification_deferred_pending_counsel_disposition`
  if counsel disposition is not ready before any `GO Phase 1220`.
- v0.2 signing remains skip-default unless the explicit authorization token is issued.
- Truth-primitive permanence target ratification window is Window 1218-1224.
- Truth-primitive permanence hard unsafe-after boundary is Window 1225-1232 closure.

---

## 6. Rate-Limit Boundary

The persistent fetch limiter is an early abuse circuit breaker, not ILC's final scaling
policy.

Carry-forward:

`reciprocal_fetch_admission_model_required`

Window 1218-1224 routes this to Phase 1222 as a design-only spec for reciprocal, organic
admission. The static limiter cannot be treated as the final network-wide communication
policy.

`transport_abuse_circuit_breaker_not_final_scaling_policy`

---

## 7. Guardrails

- No signed Genesis v0.1 mutation.
- No public launch claim.
- No public repository publication.
- No public release artifact distribution.
- No v0.2 signing without explicit signing authorization.
- No CDL-086 ratification without explicit `GO Phase 1220` and counsel disposition.
- No truth-primitive permanence ratification without explicit `GO Phase 1219`.
- No float in economic or attribution runtime state.
- No wall-clock source of truth for protocol decisions.
- No predictable PRNG in runtime/security-sensitive paths.
- No `assert` for production enforcement.
- Deterministic JSON for machine-verifiable artifacts.

---

## 8. Planning Index Cleanup

Phase 1218 updates `docs/PLANNING_INDEX.md` so §0 and §1 point to Window 1218-1224
as the active window and mark Window 1209-1217 as a closed reference.

---

## 9. Explicit Non-Events

This sequence lock does not execute truth-primitive permanence ratification, ratify
CDL-086, execute v0.2 signing, generate or register a release key, produce a release
envelope, mutate `ilc_core/`, publish a public repo, distribute public release artifacts,
make a public RC or public launch claim, or mutate signed Genesis v0.1.

---

## 10. Phase 1218 Result

Phase 1218 commits this sequence lock and records the active Window 1218-1224 execution
boundary.

`window_1218_1224_sequence_lock_committed`
