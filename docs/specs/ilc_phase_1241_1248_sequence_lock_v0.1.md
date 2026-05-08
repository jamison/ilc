# ILC Phase 1241-1248 Sequence Lock v0.1

**Date:** 2026-05-08
**Window:** 1241-1248
**Phase:** 1241
**Status:** LOCKED
**Human authorization:** `GO Phase 1241`
**Token:** `window_1241_1248_sequence_lock_committed`

---

## 1. Sequence Lock Verdict

Window 1241-1248 is opened after explicit human authorization token:

```text
GO Phase 1241
```

Verdict:

```text
window_1241_1248_sequence_lock_verdict=pass
window_1241_1248_sequence_lock_committed
```

This phase locks the Window 1241-1248 order, sensitive gates, public-RC runway
posture, and entry-state anchors. It does not mutate the CDL register, runtime
code, signed Genesis v0.1, the Genesis Atlas, release keys, or any public
release artifact.

---

## 2. Baseline Commits

| Commit | Role |
|--------|------|
| `ef466e65` | Window 1233-1240 closure gate PASS |
| `bb48911f` | Post-closure 1233-1240 audit hardening |
| `68b73117` | Draft Window 1241-1248 guidance and prompt set |

Window 1233-1240 is CLOSED through Phase 1240 with:

```text
window_1233_1240_closed_phase_1240
window_1233_1240_closure_gate_verdict=pass
```

Current capsule entering this window:

```text
docs/specs/ilc_antigravity_context_capsule_v5.50.md
```

Current closure handoff:

```text
docs/specs/ilc_window_1233_1240_handoff_1240_v0.1.md
```

Candidate guidance consumed by this lock:

```text
docs/specs/ilc_window_1241_1248_candidate_phase_grouping_v0.1.md
```

---

## 3. Immutable Anchors

| Anchor | Value |
|--------|-------|
| Genesis v0.1 signed root envelope | `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c` |
| Immutable diagnostic SHA at committed `HEAD` | `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56` |
| Genesis v0.2 candidate | 41-node / 73-edge candidate; unsigned; signing deferred |
| Capsule | v5.50 |

Preflight preserved the Phase 1240 rule that pre-existing dirty generated
graph/diagnostic working-tree artifacts are carried forward for ATLAS-G /
Genesis graph-lane reconciliation and are not staged into this sequence-lock
commit.

---

## 4. Entry Preflight

Phase 1241 preflight confirmed:

```text
tools/check_sensitive_runtime_coding_taboos.py: PASS
git diff --exit-code -- ilc_core/: clean
docs/specs/ilc_constitutional_decision_log_v0.1.md: clean
docs/PLANNING_INDEX.md: Capsule v5.50 current; Window 1241+ not open before GO Phase 1241
docs/phases/STATUS.md: Phase 1240 latest closed phase
```

---

## 5. CDL and Signing State at Window Entry

CDL-087:

```text
OPEN / PRELOCKED / NOT RATIFIED
cdl_087_canonical_fetch_distribution_policy_opened_phase_1227
cdl_087_prelock_committed_phase_1228
cdl_087_not_ratified_phase_1227
cdl_087_candidate_envelope_identified_not_ratified_phase_1238j
```

Phase 1238j produced SIM-FETCH-01 robustness evidence for future governance
review. It did not ratify CDL-087.

Next fresh CDL number:

```text
CDL-088
```

CDL-088 must not be opened without explicit future authorization.

v0.2 signing remains deferred:

```text
v0_2_signing_ceremony_deferred_pending_signing_authorization
```

No signing ceremony executed, no release key was generated or registered, and no
release envelope was produced.

---

## 6. Public-RC Branch Posture

The default public-RC path for this window is:

```text
openclaw_nemoclaw_skill_first_public_rc_path_no_public_ilc_p2p_claim
public_claimability_required_for_final_public_rc_profile
gap_14_package_modularity_executes_before_gap_10_public_p2p
```

This means:

- Gap 14 package modularity is on the immediate execution path.
- Gap 10 TransportPrincipal remains required before public ILC-owned P2P, but
  it is not a prerequisite for local OpenClaw/NemoClaw skill-preview work.
- Local skill preview is not the final public RC claim.
- Final public RC requires public claimability for the selected profile.

---

## 7. Locked Phase Order

| Order | Phase | Topic | Sensitivity | Gate |
|-------|-------|-------|-------------|------|
| 1 | 1241 | Window sequence lock | **SENSITIVE** | `GO Phase 1241` consumed |
| 2 | 1242 | Roadmap v1.1 controlling public-RC reconciliation | NON-SENSITIVE | May proceed after this lock |
| 3 | 1243 | Gap 14 package profile contracts and import-boundary inventory | NON-SENSITIVE | After Phase 1242 disposition |
| 4 | 1244 | `ilc_logic` import-boundary lint and harness protocol stubs | NON-SENSITIVE | After Phase 1243 |
| 5 | 1245 | OpenClaw/NemoClaw local skill preview dependency isolation | NON-SENSITIVE | After Phase 1244 |
| 6 | 1246 | CDL-087 governance review packet, no ratification | NON-SENSITIVE | Review-only unless later sensitive phase opens |
| 7 | 1247 | ATLAS-G-001..003 graph discipline first slice | NON-SENSITIVE | Coordinates with Gap 14 |
| 8 | 1248 | Coherence, blocker classification, handoff, closure | **SENSITIVE** | Requires `GO Phase 1248` |

Sensitive phases require separate explicit human authorization even if adjacent
non-sensitive phases are executed in sequence.

---

## 8. Sensitive Gate Rules

### Phase 1241 sequence lock

Phase 1241 opened this window and consumed:

```text
GO Phase 1241
```

### CDL-087 ratification

Phase 1246 is review-only. CDL-087 ratification requires a separate future
SENSITIVE phase and must not be implied by the Phase 1246 disposition packet.

### Phase 1248 closure gate

Phase 1248 is SENSITIVE and requires:

```text
GO Phase 1248
```

---

## 9. Active Carry-Forward Tokens

| Token | Window 1241-1248 routing |
|-------|--------------------------|
| `launch_roadmap_v1_1_refresh_required_after_phase_1240` | Phase 1242 |
| `roadmap_v1_1_must_become_controlling_public_rc_roadmap` | Phase 1242 |
| `public_rc_blocker_classification_required_in_roadmap_v1_1` | Phase 1242 and closure |
| `gap_14_package_modularity_first_slice_before_gap_10_transport_principal` | Phases 1243-1245 |
| `ilc_package_modularity_split_required_before_openclaw_skill_launch` | Phases 1243-1245 |
| `ilc_logic_pure_protocol_interfaces_required` | Phase 1244 |
| `harness_adapter_transport_storage_protocols_required` | Phase 1244 |
| `digitalocean_openclaw_droplet_first_external_harness_target` | Phase 1245 as private harness target only |
| `cdl_087_ratification_deferred_pending_sim_fetch_01` | Phase 1246 governance review only |
| `atlas_g_001_graph_delta_schema_required` | Phase 1247 |
| `atlas_g_002_repo_hypergraph_compiler_hardening_required` | Phase 1247 |
| `atlas_g_003_package_profile_reachability_manifest_required` | Phase 1247 |
| `tla_refinement_notes_pre_rc_window_1241_plus_candidate` | Phase 1248 carry-forward unless completed earlier |
| `allowlist_export_procedure_window_1241_plus_candidate` | Phase 1248 carry-forward unless completed earlier |
| `v0_2_signing_ceremony_deferred_pending_signing_authorization` | Carries forward; no signing this window |

---

## 10. Non-Authorization Boundary

This sequence lock does not authorize:

- CDL-087 ratification;
- CDL-088 opening;
- CDL mutation;
- public launch;
- public RC claim;
- public repository publication;
- public release artifact distribution;
- public P2P exposure;
- public sidecar/projection serving;
- public claimability;
- ECU minting authorization;
- ILC settlement authorization;
- release-key generation;
- release envelope production;
- signed Genesis v0.1 mutation;
- Genesis Atlas mutation;
- immutable diagnostic mutation;
- production `commit.epoch` emission authorization;
- v0.2 signing.

---

## 11. Next Phase

Next planned phase:

```text
Phase 1242 — Roadmap v1.1 controlling public-RC reconciliation
```

Phase 1242 is NON-SENSITIVE and may proceed after this sequence lock under the
locked ordering. It must not mutate runtime code or the CDL register.

