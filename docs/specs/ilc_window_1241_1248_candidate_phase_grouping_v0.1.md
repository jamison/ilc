# ILC Window 1241-1248 Candidate Phase Grouping v0.1

**Status:** Candidate guidance / prompt-draft registry.
**Recorded:** 2026-05-08.
**Authority:** This document does not open Window 1241-1248, does not replace a
sequence lock, does not authorize public RC, public repository publication,
public P2P exposure, CDL mutation, v0.2 signing, release-key generation, or
production network exposure. Exact phase authorization requires a future Window
1241-1248 sequence lock and explicit human GO for sensitive gates.

```text
window_1241_1248_candidate_phase_grouping_recorded_after_phase_1240
window_1241_1248_not_open_until_sequence_lock
```

---

## 1. Purpose

Window 1233-1240 closed with SIM-FETCH-01 evidence complete through Fix10,
Capsule v5.50 published, and CDL-087 still OPEN / PRELOCKED / NOT RATIFIED.
The next public-RC runway must turn the committed planning evidence into
execution discipline without creating another disconnected planning branch.

This candidate grouping converts the 1241+ pre-sequence plan into draftable
phase prompts for the first post-1240 window. It keeps the default public-RC
posture explicit:

```text
openclaw_nemoclaw_skill_first_public_rc_path_no_public_ilc_p2p_claim
public_claimability_required_for_final_public_rc_profile
gap_14_package_modularity_executes_before_gap_10_public_p2p
```

The window is primarily an RC-code runway, not a documentation-only runway.
Roadmap v1.1 and CDL-087 review are necessary governance work, but the code
center of gravity is Gap 14 package modularity: import boundaries, package
profiles tied to real modules, adapter protocols, dependency-isolated smoke
tests, and CI/lint gates.

---

## 2. Inputs To Read Before Any Phase

Read in this order:

1. `docs/PLANNING_INDEX.md`
2. `docs/specs/ilc_antigravity_context_capsule_v5.50.md`
3. `docs/phases/STATUS.md` tail
4. `docs/specs/ilc_window_1233_1240_handoff_1240_v0.1.md`
5. `docs/specs/ilc_public_rc_runway_pre_sequence_plan_1241_plus_v0.1.md`
6. `docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md`
7. `docs/specs/ilc_atlas_g_1241_plus_candidate_phase_grouping_v0.1.md`
8. `docs/specs/ilc_constitutional_decision_log_v0.1.md`

If memory or session summaries disagree with `STATUS.md` and
`PLANNING_INDEX.md`, current repo canon controls.

---

## 3. Candidate Phase Order

| Phase | Candidate scope | Sensitivity | Prompt draft |
|-------|-----------------|-------------|--------------|
| 1241 | Window 1241-1248 sequence lock | **SENSITIVE** - requires `GO Phase 1241` | `docs/antigravity_tasks/antigravity_prompt__phase_1241_g8_window_1241_1248_sequence_lock.md` |
| 1242 | Roadmap v1.1 controlling public-RC reconciliation | NON-SENSITIVE | `docs/antigravity_tasks/antigravity_prompt__phase_1242_g8_roadmap_v1_1_controlling_public_rc_reconciliation.md` |
| 1243 | Gap 14 package profile contracts and import-boundary inventory | NON-SENSITIVE | `docs/antigravity_tasks/antigravity_prompt__phase_1243_g8_gap14_package_profile_contracts_and_import_boundary_inventory.md` |
| 1244 | `ilc_logic` import-boundary lint and harness protocol stubs | NON-SENSITIVE | `docs/antigravity_tasks/antigravity_prompt__phase_1244_g8_ilc_logic_import_boundary_lint_and_protocol_stubs.md` |
| 1245 | OpenClaw/NemoClaw local skill preview dependency isolation | NON-SENSITIVE | `docs/antigravity_tasks/antigravity_prompt__phase_1245_g8_openclaw_nemoclaw_skill_preview_dependency_isolation.md` |
| 1246 | CDL-087 governance evidence review and ratification disposition packet | NON-SENSITIVE review only | `docs/antigravity_tasks/antigravity_prompt__phase_1246_g8_cdl_087_governance_review_and_ratification_disposition.md` |
| 1247 | ATLAS-G-001..003 graph discipline first slice | NON-SENSITIVE | `docs/antigravity_tasks/antigravity_prompt__phase_1247_g8_atlas_g_001_003_graph_discipline_slice.md` |
| 1248 | Window coherence, blocker classification, handoff, and closure gate | **SENSITIVE** - requires `GO Phase 1248` | `docs/antigravity_tasks/antigravity_prompt__phase_1248_g8_window_1241_1248_coherence_and_closure_gate.md` |

---

## 4. Scope Rationale

### 4.1 Why Gap 14 comes before Gap 10

The selected default public-RC path is OpenClaw/NemoClaw skill-first with no
public ILC P2P claim. Therefore package modularity is on the immediate shipping
path, while TransportPrincipal is on the parallel future public-P2P path.

This window should not wait for TransportPrincipal before proving that ILC can
be consumed as a clean local package/skill with:

- no `http.server`, public network transport, or LMDB ownership leaking into
  `ilc_logic`;
- explicit `TransportHarness` and `StorageHarness` Protocol contracts;
- local CLI/sidecar adapter seams that harnesses can call without importing
  the devnet HTTP stack;
- non-excisable component validation tied to real package profiles.

### 4.2 Why CDL-087 review is not ratification by default

Phase 1238j produced a strong candidate envelope and negative-control evidence,
but it did not ratify CDL-087. Phase 1246 should assemble a governance
disposition packet and answer whether ratification is ready. A CDL mutation or
ratification evidence commit requires a later explicit sensitive phase.

### 4.3 Why ATLAS-G starts in this window

Public RC must not ship a package surface where Genesis, ILC, ECU, or the repo
hypergraph can be treated as optional appendages. ATLAS-G-001..003 establish
the phase-close graph delta schema, deterministic compiler hardening, and
package-profile reachability manifests needed before later public-RC
reachability gates.

---

## 5. Window Exit Criteria

Window 1241-1248 should not close as pass unless all of the following are true:

- Roadmap v1.1 is either committed as the controlling public-RC roadmap or the
  handoff records exactly why it remains blocked.
- A Window 1241-1248 sequence lock exists and records exact sensitive gates.
- Gap 14 has moved from declaration toward executable enforcement: package
  profile contracts, import-boundary inventory, and at least one real lint or
  smoke gate are committed.
- OpenClaw/NemoClaw local skill preview is represented as a real package/test
  boundary, not just prose.
- CDL-087 evidence has a governance disposition packet, even if ratification
  remains deferred.
- ATLAS-G-001..003 have either landed or are explicitly blocked with next-step
  pointers.
- Public-RC blocker classes are reconciled into Roadmap v1.1 or the closure
  handoff.

---

## 6. Non-Claims

This guidance does not:

- open Window 1241-1248;
- assign official phase authority without a sequence lock;
- ratify CDL-087;
- open CDL-088;
- authorize public P2P exposure;
- authorize public sidecar/projection serving;
- authorize ECU minting or ILC settlement;
- authorize public claimability;
- authorize public repository publication;
- authorize public RC or public launch;
- authorize release-key generation;
- authorize v0.2 signing;
- mutate signed Genesis v0.1 or immutable diagnostic anchors.

