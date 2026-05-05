# ILC Phase 1191-1199 Sequence Lock v0.1

**Date:** 2026-05-05
**Status:** committed
**Window:** 1191-1199
**Phase:** 1191

`window_1191_1199_sequence_lock_committed`

---

## 1. Authorization and Boundary

Window 1191-1199 sequence lock was authorized by explicit human token:

`GO Phase 1191`

This sequence lock authorizes the Phase 1191 structural window-boundary commit only. It
records the active window order and allows later non-sensitive phases to proceed in order
after Phase 1191, subject to their phase prompts and dependencies.

This lock does not authorize:

- v0.2 signing ceremony execution
- release-key generation or registration
- CDL-086 opening
- CDL-086 ratification
- public repository publication
- public launch claim
- signed Genesis v0.1 mutation
- runtime mutation

Phase 1193 remains conditional and requires explicit signing authorization token
`v0_2_signing_ceremony_authorized_phase_1193` plus explicit `GO Phase 1193`.
Phase 1194 remains SENSITIVE and requires explicit `GO Phase 1194` plus CDL mutation
environment:

```text
ILC_CDL_MUTATION_AUTHORIZED=1
ILC_CDL_MUTATION_PHASE=1194
```

Phase 1199 remains SENSITIVE and requires explicit `GO Phase 1199`.

---

## 2. Window Header

| Field | Value |
|-------|-------|
| Window | 1191-1199 |
| Baseline capsule | `docs/specs/ilc_antigravity_context_capsule_v5.44.md` |
| Incoming handoff | `docs/specs/ilc_window_1183_1190_handoff_1190_v0.1.md` |
| Prior closure token | `window_1183_1190_closed_phase_1190` |
| Current guidance | `docs/specs/ilc_window_1191_1199_candidate_phase_grouping_v0.1.md` |
| Phase prompts | `docs/phases/phase_1191_*` through `docs/phases/phase_1199_*` |
| CDL frontier | CDL-085 ratified; CDL-086 likely next fresh number |
| Runtime frontier | `epoch_attribution_settle_runtime_1185.v0.6` |
| Genesis v0.1 root envelope hash | `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c` |
| Unsigned Atlas candidate | v0.2 candidate, 41 nodes / 73 edges, unsigned |

---

## 3. Constitutional Frontier

`CDL-085` is ratified and active in runtime:

- Ratification token: `cdl_085_ratified_phase_1185`
- `EDGE_MINT_PHI_BOUND = Decimal("0.60")`
- Runtime dependency: `CDL_085_DEPENDENCY = "cdl_085_werner_phi_bound_ratified_1185.v0.1"`

The SIM-SPECTRAL-05 observer framework is complete:

- Runtime-binding: `sim_spectral_05_runtime_binding_slice_pass`
- Economic-flow: `sim_spectral_05_economic_flow_slice_pass`
- Gossip: `sim_spectral_05_gossip_slice_pass`
- Completion: `sim_spectral_05_three_slice_observer_framework_complete`

The public-launch packaging blocker remains unopened. Phase 1188 scoped the blocker and
corrected the CDL-001 label drift. CDL-001 is ratified signer-lineage canon and should be
treated as a dependency. A fresh CDL number, likely CDL-086 if still next fresh at opening
time, should be used for the packaging blocker.

---

## 4. Runtime Baseline

Runtime semantics are unchanged at Phase 1191:

- Runtime version: `epoch_attribution_settle_runtime_1185.v0.6`
- `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`
- `PROVENANCE_MAX_DEPTH = 3`
- `EDGE_MINT_PHI_BOUND = Decimal("0.60")`
- No settlement, QATPS, slashing, wallet, gossip, transport, or economic-flow rule is
  changed by this lock

Any future runtime work in this window must preserve repository coding standards:

- no float for economic or attribution runtime state;
- no wall-clock source of truth for protocol decisions;
- deterministic JSON for machine-verifiable artifacts.

---

## 5. Genesis Atlas Baseline

Signed Genesis v0.1 remains immutable:

- Star map: `out/genesis_core_star_map_v0.1.json`
- Nodes: 32
- Edges: 55
- Root envelope hash:
  `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`

Strictly immutable diagnostic:

- `out/genesis_compile_coverage_diagnostic_v0.1.json`
- Expected SHA-256:
  `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56`

Unsigned v0.2 candidate:

- Artifact: `out/genesis_core_star_map_v0.2_candidate.json`
- Nodes: 41
- Edges: 73
- Status: unsigned

ADR-0036 and ADR-0037 acceptance satisfy governance prerequisites for a future v0.2
signing ceremony. The signing act still requires explicit signing authorization and
`GO Phase 1193`.

---

## 6. Carry-Forward Intake

| Carry-forward | Window 1191-1199 routing |
|---------------|--------------------------|
| `v0_2_signing_ceremony_deferred_pending_signing_authorization` | Phase 1193 conditional signing slot |
| `cdl_001_genesis_blocker_scoping_committed_phase_1188` | Phase 1194 fresh-CDL packaging blocker opening |
| `sim_spectral_05_three_slice_observer_framework_complete` | Consumed by roadmap v1.0 / RC2 status refresh |
| Tier-3 runtime linkage | Phase 1195 |
| Persistent rate limiter | Phase 1196 |
| Canon bundle signing repair | Phase 1197 conditional tail |
| Truth-primitive permanence community ratification | Carry-forward only |
| Contributor agreement / license / trademark | Counsel track carry-forward |

---

## 7. Locked Phase Order

| Phase | Topic | Sensitivity | Execution status |
|-------|-------|-------------|------------------|
| 1191 | Window sequence lock | SENSITIVE | authorized by `GO Phase 1191` |
| 1192 | Launch roadmap v1.0 / RC2 status refresh | NON-SENSITIVE | may proceed after 1191 |
| 1193 | v0.2 signing ceremony | SENSITIVE / conditional | not authorized by this lock |
| 1194 | CDL-086 public-launch packaging blocker opening | SENSITIVE / constitutional | not authorized by this lock |
| 1195 | Tier-3 runtime linkage scoping / first tranche | NON-SENSITIVE | may proceed after routed gates |
| 1196 | Persistent rate limiter scoping / bounded implementation | NON-SENSITIVE | may proceed after 1195 |
| 1197 | Canon bundle signing repair | NON-SENSITIVE / conditional | may proceed if capacity remains |
| 1198 | Coherence report + capsule v5.45 | NON-SENSITIVE | may proceed after routed work |
| 1199 | Closure gate | SENSITIVE | not authorized by this lock |

---

## 8. Explicit Non-Events at Phase 1191

This sequence lock does not execute v0.2 signing, generate or register a release key, open
or ratify CDL-086, mutate `ilc_core/`, publish a public repo, make a public launch claim,
or mutate signed Genesis v0.1. Later phases must preserve their own sensitivity gates.

---

## 9. Planning Index Update

`docs/PLANNING_INDEX.md` is advanced by Phase 1191 to show Window 1191-1199 in progress
through Phase 1191, with this sequence lock and the Window 1191-1199 guidance in the
session-start quick-reference set.

---

## 10. Phase 1191 Result

Phase 1191 commits this sequence lock and records the active Window 1191-1199 execution
boundary.

`window_1191_1199_sequence_lock_committed`
