# ILC Phase 1209-1217 Sequence Lock v0.1

**Date:** 2026-05-05
**Status:** committed
**Window:** 1209-1217
**Phase:** 1209

`window_1209_1217_sequence_lock_committed`

---

## 1. Authorization and Boundary

Window 1209-1217 sequence lock was authorized by explicit human token:

`GO Phase 1209`

This sequence lock authorizes Phase 1209 and permits the non-sensitive Phases 1210-1213
to proceed in order after Phase 1209 under the active window guidance and repository
guardrails. Phase 1216 is non-sensitive but remains ordered after the Phase 1214/1215
sensitive/conditional gates.

This lock does not authorize:

- CDL-086 ratification;
- v0.2 signing ceremony execution;
- release-key generation or registration;
- public repository publication;
- public launch claim;
- signed Genesis v0.1 mutation.

Phase 1214 remains SENSITIVE and requires explicit `GO Phase 1214` plus the required
CDL mutation environment if counsel disposition is satisfied. Phase 1215 remains
conditional and requires `v0_2_signing_ceremony_authorized_phase_1215` plus explicit
`GO Phase 1215`. Phase 1217 remains SENSITIVE and requires explicit `GO Phase 1217`.

---

## 2. Window Header

| Field | Value |
|-------|-------|
| Window | 1209-1217 |
| Baseline closure commit | `7d545106` (Window 1200-1208 closure) |
| Active guidance commit | `40f4cadc` |
| Planning-index guidance commit | `b69a1e0b` |
| Audit-fix guidance commit | `755d7243` |
| Rate-limit framing commit | `d9eb7cf1` |
| Incoming capsule | `docs/specs/ilc_antigravity_context_capsule_v5.46.md` |
| Incoming handoff | `docs/specs/ilc_window_1200_1208_handoff_1208_v0.1.md` |
| Prior closure token | `window_1200_1208_closed_phase_1208` |
| Current guidance | `docs/specs/ilc_window_1209_1217_candidate_phase_grouping_v0.1.md` |
| Phase prompts | `docs/phases/phase_1209_*` through `docs/phases/phase_1217_*` |
| CDL frontier | CDL-085 ratified; CDL-086 prelocked, not ratified |
| Runtime frontier | `epoch_attribution_settle_runtime_1185.v0.6`; φ-bound enforcement pending Phase 1210 |
| Genesis v0.1 root envelope hash | `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c` |
| Immutable diagnostic SHA | `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56` |

---

## 3. Incoming Carry-Forward Tokens

| Token | Window 1209-1217 routing |
|-------|--------------------------|
| `edge_mint_phi_bound_enforcement_not_yet_implemented` | Phase 1210 implementation |
| `persistent_rate_limiter_wiring_deferred_phase_1202` | Phase 1212 transport wiring |
| `truth_primitive_permanence_ratification_packet_required_window_1209` | Phase 1211 packet |
| `cdl_086_prelock_committed_phase_1204` | Phase 1213 prep and Phase 1214 conditional ratification |
| `v0_2_signing_ceremony_deferred_pending_signing_authorization` | Phase 1215 skip-default signing slot |

---

## 4. Locked Phase Order

| Phase | Topic | Sensitivity | Execution status |
|-------|-------|-------------|------------------|
| 1209 | Window sequence lock | SENSITIVE | authorized by `GO Phase 1209` |
| 1210 | φ-bound enforcement spec + implementation | NON-SENSITIVE | authorized to proceed after 1209 |
| 1211 | Truth-primitive permanence ratification packet | NON-SENSITIVE | authorized to proceed after 1210 |
| 1212 | Rate limiter transport wiring | NON-SENSITIVE | authorized to proceed after 1211 |
| 1213 | CDL-086 ratification prep | NON-SENSITIVE | authorized to proceed after 1212 |
| 1214 | CDL-086 ratification | SENSITIVE / conditional | not authorized by this lock |
| 1215 | v0.2 signing ceremony | SENSITIVE / conditional | not authorized by this lock |
| 1216 | Coherence report + capsule v5.47 | NON-SENSITIVE | ordered after 1214/1215 disposition |
| 1217 | Window closure gate | SENSITIVE | not authorized by this lock |

---

## 5. Human Decisions Recorded

- v0.2 signing is deferred to Window 1218+ unless separately authorized.
- CDL-086 ratification must skip with `cdl_086_ratification_deferred_pending_counsel_disposition`
  if counsel disposition is not ready before any `GO Phase 1214`.
- Truth-primitive permanence target ratification window is Window 1218-1224.
- Truth-primitive permanence hard unsafe-after boundary is Window 1225-1232 closure.

---

## 6. Rate-Limit Boundary

Phase 1212 is a transport abuse circuit breaker, not ILC's final scaling policy.
Static request caps protect early/public nodes from WANT-BLOCK resource-drain attacks,
but the long-term direction is reciprocal fetch admission.

Carry-forward:

`reciprocal_fetch_admission_model_required`

Phase 1212 and later synthesis/closure docs must record:

`transport_abuse_circuit_breaker_not_final_scaling_policy`

---

## 7. Guardrails

- No signed Genesis v0.1 mutation.
- No public launch claim.
- No v0.2 signing without explicit signing authorization.
- No CDL-086 ratification without explicit `GO Phase 1214`.
- No float in economic or attribution runtime state.
- No wall-clock source of truth for protocol decisions.
- No predictable PRNG in runtime/security-sensitive paths.
- No `assert` for production enforcement.
- Deterministic JSON for machine-verifiable artifacts.

---

## 8. Planning Index Cleanup

Phase 1209 cleans `docs/PLANNING_INDEX.md` so §0 and §1 point to Window 1209-1217
as the active window and mark Window 1200-1208 and older windows as closed references.

---

## 9. Explicit Non-Events

This sequence lock does not execute v0.2 signing, generate or register a release key,
ratify CDL-086, mutate `ilc_core/`, publish a public repo, make a public launch claim,
or mutate signed Genesis v0.1.

---

## 10. Phase 1209 Result

Phase 1209 commits this sequence lock and records the active Window 1209-1217 execution
boundary.

`window_1209_1217_sequence_lock_committed`
