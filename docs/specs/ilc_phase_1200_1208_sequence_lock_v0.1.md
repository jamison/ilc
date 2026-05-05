# ILC Phase 1200-1208 Sequence Lock v0.1

**Date:** 2026-05-05
**Status:** committed
**Window:** 1200-1208
**Phase:** 1200

`window_1200_1208_sequence_lock_committed`

---

## 1. Authorization and Boundary

Window 1200-1208 sequence lock was authorized by explicit human token:

`GO Phase 1200-1203`

This sequence lock authorizes the Phase 1200 structural window-boundary commit and permits
the non-sensitive Phases 1201-1203 to proceed in order after Phase 1200, subject to their
phase prompts and repository guardrails.

This lock does not authorize:

- v0.2 signing ceremony execution;
- release-key generation or registration;
- CDL-086 prelock execution;
- CDL-086 ratification;
- public repository publication;
- public launch claim;
- signed Genesis v0.1 mutation.

Phase 1204 remains SENSITIVE and requires explicit `GO Phase 1204` if Phase 1203 resolves
Q1-Q5 without blockers. Phase 1205 remains conditional and requires
`v0_2_signing_ceremony_authorized_phase_1205` plus explicit `GO Phase 1205`. Phase 1208
remains SENSITIVE and requires explicit `GO Phase 1208`.

---

## 2. Window Header

| Field | Value |
|-------|-------|
| Window | 1200-1208 |
| Baseline capsule | `docs/specs/ilc_antigravity_context_capsule_v5.45.md` |
| Incoming handoff | `docs/specs/ilc_window_1191_1199_handoff_1199_v0.1.md` |
| Prior closure token | `window_1191_1199_closed_phase_1199` |
| Current guidance | `docs/specs/ilc_window_1200_1208_candidate_phase_grouping_v0.1.md` |
| Phase prompts | `docs/phases/phase_1200_*` through `docs/phases/phase_1208_*` |
| CDL frontier | CDL-085 ratified; CDL-086 open, not ratified |
| Runtime frontier | `epoch_attribution_settle_runtime_1185.v0.6` |
| Genesis v0.1 root envelope hash | `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c` |
| Unsigned Atlas candidate | v0.2 candidate, 41 nodes / 73 edges, unsigned |

---

## 3. Constitutional Frontier

`CDL-085` is ratified and active in runtime:

- Ratification token: `cdl_085_ratified_phase_1185`
- `EDGE_MINT_PHI_BOUND = Decimal("0.60")`
- Runtime dependency: `CDL_085_DEPENDENCY = "cdl_085_werner_phi_bound_ratified_1185.v0.1"`

`CDL-086` is open and not ratified:

- Opening token: `cdl_086_public_launch_packaging_blocker_opened_phase_1194`
- Scope: public-launch packaging blocker
- Status: open
- Ratification: not authorized by this lock

The SIM-SPECTRAL-05 observer framework is complete:

- Runtime-binding: `sim_spectral_05_runtime_binding_slice_pass`
- Economic-flow: `sim_spectral_05_economic_flow_slice_pass`
- Gossip: `sim_spectral_05_gossip_slice_pass`
- Completion: `sim_spectral_05_three_slice_observer_framework_complete`

---

## 4. Runtime Baseline

Runtime semantics at Phase 1200:

- Runtime version: `epoch_attribution_settle_runtime_1185.v0.6`
- `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`
- `PROVENANCE_MAX_DEPTH = 3`
- `EDGE_MINT_PHI_BOUND = Decimal("0.60")`

Phases 1201 and 1202 are implementation phases. They must obey:

- no float for economic, attribution, or staking runtime state;
- no wall-clock source of truth for protocol decisions;
- no predictable PRNG in runtime/security-sensitive paths;
- no `assert` for production enforcement;
- deterministic JSON with `sort_keys=True`, `allow_nan=False`, and compact separators for
  machine-verifiable artifacts.

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

---

## 6. RC2 Gate Status

| # | Gate | Status |
|---|------|--------|
| 1 | CDL-085 ratified | **SATISFIED** |
| 2 | v0.2 signing | OPEN — authorization absent |
| 3 | Tier-3 runtime linkage | SCOPED — Phase 1201 implementation |
| 4 | Packaging blocker progressed | IN PROGRESS — CDL-086 open, Phase 1203/1204 target |
| 5 | Persistent rate limiter | SCOPED — Phase 1202 implementation |
| 6 | Truth-primitive permanence governance | OPEN — Phase 1206 routing |

---

## 7. Carry-Forward Intake

| Carry-forward | Window 1200-1208 routing |
|---------------|--------------------------|
| `v0_2_signing_ceremony_deferred_pending_signing_authorization` | Phase 1205 conditional signing slot; default skip |
| `cdl_086_public_launch_packaging_blocker_opened_phase_1194` | Phase 1203 deliberation and Phase 1204 conditional prelock |
| `tier3_runtime_linkage_scope_committed_phase_1195` | Phase 1201 implementation |
| `persistent_rate_limiter_scope_committed_phase_1196` | Phase 1202 implementation |
| `truth_primitive_permanence_requires_community_ratification_before_genesis_sunset` | Phase 1206 governance routing |

---

## 8. Locked Phase Order

| Phase | Topic | Sensitivity | Execution status |
|-------|-------|-------------|------------------|
| 1200 | Window sequence lock | SENSITIVE | authorized by `GO Phase 1200-1203` |
| 1201 | Tier-3 runtime linkage implementation | NON-SENSITIVE | authorized to proceed after 1200 |
| 1202 | Persistent rate limiter implementation | NON-SENSITIVE | authorized to proceed after 1201 |
| 1203 | CDL-086 deliberation Q1-Q5 | NON-SENSITIVE | authorized to proceed after 1202 |
| 1204 | CDL-086 prelock | SENSITIVE / conditional | not authorized by this lock |
| 1205 | v0.2 signing ceremony | SENSITIVE / conditional | not authorized by this lock |
| 1206 | Truth-primitive permanence governance | NON-SENSITIVE unless CDL opening required | not part of this GO token |
| 1207 | Coherence report + capsule v5.46 | NON-SENSITIVE | not part of this GO token |
| 1208 | Closure gate | SENSITIVE | not authorized by this lock |

---

## 9. Explicit Non-Events at Phase 1200

This sequence lock does not execute v0.2 signing, generate or register a release key,
prelock or ratify CDL-086, mutate `ilc_core/`, publish a public repo, make a public launch
claim, or mutate signed Genesis v0.1.

---

## 10. Planning Index Update

`docs/PLANNING_INDEX.md` is advanced by Phase 1200 to show Window 1200-1208 in progress
through Phase 1200, with this sequence lock and the Window 1200-1208 guidance in the
session-start quick-reference set.

---

## 11. Phase 1200 Result

Phase 1200 commits this sequence lock and records the active Window 1200-1208 execution
boundary.

`window_1200_1208_sequence_lock_committed`
