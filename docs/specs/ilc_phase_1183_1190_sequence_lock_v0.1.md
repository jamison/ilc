# ILC Phase 1183-1190 Sequence Lock v0.1

**Date:** 2026-05-04
**Status:** committed
**Window:** 1183-1190
**Phase:** 1183

`window_1183_1190_sequence_lock_committed`

---

## 1. Authorization and Boundary

Window 1183-1190 sequence lock was authorized by explicit human token:

`GO Phase 1183`

This sequence lock authorizes the Phase 1183 structural window-boundary commit only.
It records the active window order and allows later non-sensitive phases to proceed in
order after Phase 1183, subject to their phase prompts and dependencies.

This lock does not authorize:

- CDL-085 ratification
- `ilc_core/` runtime mutation
- v0.2 signing ceremony execution
- release-key generation
- a new CDL opening
- signed Genesis v0.1 mutation

Phase 1185 remains SENSITIVE and requires explicit `GO Phase 1185`.
Phase 1186 remains conditional and requires explicit signing authorization token
`v0_2_signing_ceremony_authorized_phase_1186` plus explicit `GO Phase 1186`.
Phase 1190 remains SENSITIVE and requires explicit `GO Phase 1190`.

---

## 2. Window Header

| Field | Value |
|-------|-------|
| Window | 1183-1190 |
| Baseline capsule | `docs/specs/ilc_antigravity_context_capsule_v5.43.md` |
| Incoming handoff | `docs/specs/ilc_window_1176_1182_handoff_1182_v0.1.md` |
| Prior closure commit | `b3f2abeb` (`window_1176_1182_closed_phase_1182`) |
| Current guidance | `docs/specs/ilc_window_1183_1190_candidate_phase_grouping_v0.1.md` |
| Phase prompts | `docs/phases/phase_1183_*` through `docs/phases/phase_1190_*` |
| CDL frontier | CDL-084 ratified; CDL-085 open + prelocked; CDL-086 next fresh number |
| Runtime frontier | `epoch_attribution_settle_runtime_1129_fix1.v0.5` |
| Genesis v0.1 root envelope hash | `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c` |
| Unsigned Atlas candidate | v0.2 candidate, 41 nodes / 73 edges, unsigned |

---

## 3. Constitutional Frontier

`CDL-084` remains the ratified attribution frontier:

- `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`
- `PROVENANCE_MAX_DEPTH = 3`
- Active runtime dependency: `CDL_084_DEPENDENCY`

`CDL-085` is open and prelocked, but not ratified:

- Opening phase: 1172
- Opening token: `cdl_085_sim_gate_lifted_phase_1172_sim_spectral_05_gate_pass`
- Prelock phase: 1177
- Prelock token: `cdl_085_prelock_committed_phase_1177`
- Candidate value: `EDGE_MINT_PHI_BOUND = Decimal("0.60")`
- Runtime status: candidate not yet active in `ilc_core/`

The two activation-gate observer slices needed for ratification are cleared:

- Runtime-binding: `sim_spectral_05_runtime_binding_slice_pass`
- Economic-flow: `sim_spectral_05_economic_flow_slice_pass`

CDL-085 ratification is routed to Phase 1185 and remains sensitive.

---

## 4. Runtime Baseline

Runtime semantics remain unchanged at Phase 1183:

- Runtime version: `epoch_attribution_settle_runtime_1129_fix1.v0.5`
- `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`
- `PROVENANCE_MAX_DEPTH = 3`
- `EDGE_MINT_PHI_BOUND` remains a placeholder candidate boundary, not an active runtime
  attribution value
- No settlement, QATPS, slashing, wallet, gossip, or economic-flow rule is changed by
  this lock

Phase 1185 Commit 2 is expected to replace the placeholder with
`EDGE_MINT_PHI_BOUND: Decimal = Decimal("0.60")` and register
`CDL_085_DEPENDENCY = "cdl_085_werner_phi_bound_ratified_1185.v0.1"`, but only after
explicit `GO Phase 1185`.

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
`GO Phase 1186`.

---

## 6. Carry-Forward Intake

| Carry-forward | Window 1183-1190 routing |
|---------------|--------------------------|
| `cdl_085_prelock_committed_phase_1177` | Phase 1184 hardening + Phase 1185 ratification |
| `sim_spectral_05_gossip_slice_deferred_window_1176` | Phase 1187 conditional tail after ratification |
| `v0_2_signing_ceremony_deferred_pending_signing_authorization` | Phase 1186 conditional signing slot |
| `cdl_001_genesis_blocker_scope_required_for_public_rc` | Phase 1188 planning-only scoping |
| Tier-3 runtime linkage | Carry-forward only |
| Truth-primitive permanence community ratification | Carry-forward only |
| Contributor agreement / license / trademark | Counsel track carry-forward |
| Canon bundle signing repair | Tooling debt carry-forward |

---

## 7. Locked Phase Order

| Phase | Topic | Sensitivity | Execution status |
|-------|-------|-------------|------------------|
| 1183 | Window sequence lock | SENSITIVE | authorized by `GO Phase 1183` |
| 1184 | CDL-085 prelock hardening | NON-SENSITIVE | may proceed after 1183 |
| 1185 | CDL-085 ratification | SENSITIVE / constitutional | not authorized by this lock |
| 1186 | v0.2 signing ceremony | SENSITIVE / conditional | not authorized |
| 1187 | SIM-SPECTRAL-05 gossip observer slice | NON-SENSITIVE / conditional | may proceed only after 1185 if reached |
| 1188 | CDL-001 scoping | NON-SENSITIVE / planning-only | may proceed if reached |
| 1189 | Coherence report + capsule v5.44 | NON-SENSITIVE | may proceed after routed tail slots |
| 1190 | Closure gate | SENSITIVE | not authorized |

---

## 8. Explicit Non-Events at Phase 1183

This sequence lock does not ratify CDL-085, activate `EDGE_MINT_PHI_BOUND`, mutate
`ilc_core/`, execute v0.2 signing, generate a release key, mutate signed Genesis v0.1,
or open CDL-001. Later phases must preserve their own sensitivity gates.

---

## 9. Planning Index Update

`docs/PLANNING_INDEX.md` is advanced by Phase 1183 to show Window 1183-1190 in progress
through Phase 1183, with this sequence lock and the Window 1183-1190 guidance in the
session-start quick-reference set.

---

## 10. Phase 1183 Result

Phase 1183 commits this sequence lock and records the active Window 1183-1190 execution
boundary.

`window_1183_1190_sequence_lock_committed`
