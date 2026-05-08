# ILC Phase 1249-1256 Sequence Lock v0.1

**Date:** 2026-05-08
**Window:** 1249-1256
**Phase:** 1249
**Status:** LOCKED
**Human authorization:** `GO Phase 1249`
**Token:** `window_1249_1256_sequence_lock_committed`

---

## 1. Sequence Lock Verdict

Window 1249-1256 is opened after explicit human authorization:

```text
GO Phase 1249
```

Verdict:

```text
window_1249_1256_sequence_lock_verdict=pass
window_1249_1256_sequence_lock_committed
```

This lock fixes the Window 1249-1256 phase order, sensitive gates, public-RC
runway posture, required context-discovery discipline, and non-authorization
boundary. It does not mutate runtime code, the CDL register, signed Genesis v0.1,
Genesis Atlas artifacts, release keys, public repository state, or any public
release artifact.

---

## 2. Baseline Commits and Inputs

| Commit | Role |
|--------|------|
| `e684f325` | Window 1241-1248 closure handoff |
| `4b0341b0` | Phase 1247 graph reachability hardening |
| `ab8cee03` | Draft Window 1249-1256 guidance and prompt set |
| `b2e06d86` | Unknown-unknown discovery discipline added to prompts and planning |

Window 1241-1248 is CLOSED through Phase 1248 with:

```text
window_1241_1248_closed_phase_1248
window_1241_1248_closure_gate_verdict=pass
```

Current capsule entering this window:

```text
docs/specs/ilc_antigravity_context_capsule_v5.50.md
```

Current closure handoff:

```text
docs/specs/ilc_window_1241_1248_handoff_1248_v0.1.md
```

Current controlling public-RC roadmap:

```text
docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md
```

Candidate guidance consumed by this lock:

```text
docs/specs/ilc_window_1249_1256_candidate_phase_grouping_v0.1.md
```

---

## 3. Immutable Anchors

| Anchor | Value |
|--------|-------|
| Genesis v0.1 signed root envelope | `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c` |
| Immutable diagnostic SHA at committed `HEAD` | `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56` |
| Genesis v0.2 candidate | 41-node / 73-edge candidate; unsigned; signing deferred |
| Capsule | v5.50 |

Preflight preserves the earlier closure rule that pre-existing dirty generated
graph/diagnostic working-tree artifacts remain carried forward for ATLAS-G /
Genesis graph-lane reconciliation and are not staged by this sequence lock.

---

## 4. Entry Preflight and Discovery Audit

| Check | Result |
|-------|--------|
| Required-token audit | Before this lock was written, required Phase 1249 tokens were present only in the Phase 1249 prompt draft; this lock now records them as authoritative Window 1249-1256 sequence-lock tokens. |
| Concept-discovery search | Confirmed the active lanes: Gap 14 adapter extraction and package CI; Gap 13 claimability boundary; TransportPrincipal; ATLAS-G-004/005; TLA refinement notes; allowlist-export procedure; public-RC blocker classes. |
| Contradiction and non-claim search | Confirmed no public RC is open; CDL-087 remains unratified; v0.2 signing remains deferred; OpenClaw/NemoClaw local preview is local/private and not final public RC; public P2P, public sidecar serving, and public claimability remain blocked. |
| Source expansion | Direct-read planning/canon sources before execution. One prompt-draft hardening was applied: the Phase 1249 prompt now lists Phase 1249, Phase 1252, and Phase 1256 as SENSITIVE gates. |

Standing discovery tokens:

```text
historical_retrieval_is_context_not_authority_current_canon_controls
unknown_unknown_discovery_required_before_phase_execution
```

Every executable phase in this window must perform the same four-part discovery
pass before coding or drafting:

- §0a Known-token audit.
- §0b Concept-discovery search.
- §0c Contradiction and non-claim search.
- §0d Source expansion and newly discovered tokens.

MemPalace may be used only as advisory retrieval support. A MemPalace result is
not canon until the returned repo path is direct-read and reconciled against
current `docs/PLANNING_INDEX.md`, current capsule, current `docs/phases/STATUS.md`,
and the active window lock.

---

## 5. CDL, Signing, and Public-RC State at Window Entry

CDL-087 remains:

```text
OPEN / PRELOCKED / NOT RATIFIED
cdl_087_governance_review_complete_phase_1246
cdl_087_ratification_deferred_pending_production_candidate_fetch_evidence
cdl_087_sensitive_ratification_phase_required_if_later_authorized
```

The Phase 1246 disposition completed governance review only. It did not ratify
CDL-087. Remaining blockers include production-candidate Tier A/B/C
classification runtime, bootstrap snapshot builder/verifier, production-candidate
observability collection, and the final CDL-077 limiter regression.

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

Roadmap v1.1 remains the controlling public-RC roadmap:

```text
roadmap_v1_1_controlling_public_rc_roadmap_phase_1242
```

The default public-RC branch remains:

```text
public_rc_default_path=openclaw_skill_first_public_claimability_no_public_p2p_claim
openclaw_nemoclaw_skill_first_public_rc_path_no_public_ilc_p2p_claim
public_claimability_required_for_final_public_rc_profile
gap_14_package_modularity_executes_before_gap_10_public_p2p
```

Meaning:

- Gap 14 package modularity remains the immediate public-RC code-readiness lane.
- Gap 14 adapter extraction and package CI must run before any public-RC claim.
- OpenClaw/NemoClaw local preview is a local/private seam, not final public RC.
- Final public RC requires public ECU-to-ILC claimability.
- Public ILC-owned P2P remains blocked by TransportPrincipal and public-P2P
  substrate decisions.

Required Window 1249-1256 routing token:

```text
gap_14_adapter_extraction_runs_before_public_rc_claim_phase_1249
```

---

## 7. Locked Phase Order

| Order | Phase | Topic | Sensitivity | Gate |
|-------|-------|-------|-------------|------|
| 1 | 1249 | Window 1249-1256 sequence lock | **SENSITIVE** | `GO Phase 1249` consumed |
| 2 | 1250 | Gap 14 adapter extraction for `ilc_logic` migration debt | NON-SENSITIVE | After this lock |
| 3 | 1251 | Gap 14 package CI gate, profile export audit, package-size measurement | NON-SENSITIVE | After Phase 1250 |
| 4 | 1252 | Gap 13 claimability resolution boundary and chain/crypto dependency inventory | **SENSITIVE** | Requires `GO Phase 1252` |
| 5 | 1253 | TransportPrincipal identity spec and Python HTTP devnet downgrade plan | NON-SENSITIVE design/spec only | After Phase 1252 disposition |
| 6 | 1254 | ATLAS-G-004/005 high-authority classification and dependency bridge | NON-SENSITIVE | After Phase 1253 |
| 7 | 1255 | TLA+ refinement notes and allowlist-export procedure | NON-SENSITIVE | After Phase 1254 |
| 8 | 1256 | Window coherence, blocker classification, and closure gate | **SENSITIVE** | Requires `GO Phase 1256` |

Sensitive phases require separate explicit human authorization even if adjacent
non-sensitive phases are executed in sequence.

### Phase 1250 Fix1 Audit-Route Addendum

Phase 1250 Fix1 added a reproducible RC frontier gap audit:

```text
docs/specs/ilc_rc_frontier_gap_audit_1250_fix1_v0.1.md
docs/specs/ilc_rc_frontier_gap_audit_1250_fix1_v0.1.json
phase_1250_fix1_rc_frontier_gap_audit_complete
```

The audit does not reorder the locked phase sequence, but it is now a required
input to the remaining window phases:

| Audit route | Required disposition |
|-------------|----------------------|
| Phase 1251 | Consume `RCGAP-1250-FIX1-001` as confirmation that Gap 14 package CI/profile audit/package-size measurement remains next; do not pull Phase 1252/1253/1254 findings into the package-CI phase. |
| Phase 1252 | Classify all Phase 1250 Fix1 ledger/security digest truncation candidates as security-binding, storage/display-only, or already-covered; fix only cases safely in scope under the sensitive claimability/chain/crypto boundary. |
| Phase 1253 | Classify network digest/fingerprint truncations and the Rust M-5 `FIXME` under TransportPrincipal/public-P2P readiness; no public exposure or runtime identity activation is authorized by the classification. |
| Phase 1254 | Treat the 129 missing legacy `graph_delta=` closure/handoff docs as ATLAS-G hygiene. Produce a prioritized backfill/disposition plan rather than blindly editing every historical file. |
| Phase 1256 | Reconcile every Phase 1250 Fix1 finding route in the closure handoff so no audit finding is dropped. |

---

## 8. Sensitive Gate Rules

### Phase 1249 sequence lock

Phase 1249 opened this window and consumed:

```text
GO Phase 1249
```

### Phase 1252 claimability boundary

Phase 1252 is sensitive because it touches the boundary between internal
ECU-to-ILC conversion, public claimability, chain/crypto dependency inventory,
and eventual public economic access. It requires:

```text
GO Phase 1252
phase_1252_gap13_claimability_boundary_requires_explicit_go
```

Phase 1252 must not activate public claimability, wallet withdrawal, ILC
transfer, release keys, public launch, or public RC.

### Phase 1256 closure gate

Phase 1256 is sensitive and requires:

```text
GO Phase 1256
```

---

## 9. Active Carry-Forward Tokens

| Token | Window 1249-1256 routing |
|-------|--------------------------|
| `gap_14_adapter_extraction_and_package_ci_gate_should_continue_before_public_rc_claim` | Phases 1250-1251 |
| `gap_13_public_claimability_runtime_should_start_before_final_public_rc_claim` | Phase 1252 boundary and dependency inventory |
| `transport_principal_identity_required_before_public_p2p` | Phase 1253 design/spec only |
| `atlas_g_004_high_authority_gap_closure_required` | Phase 1254 |
| `atlas_g_005_import_dependency_graph_bridge_required` | Phase 1254 |
| `phase_1250_fix1_rc_frontier_gap_audit_complete` | Required input to Phases 1251-1254 and Phase 1256 closure |
| `phase_1252_digest_truncation_security_binding_classification_recorded` | Phase 1252 Fix1/addendum route from Phase 1250 Fix1 |
| `phase_1253_transport_digest_and_rust_m5_disposition_recorded` | Phase 1253 route from Phase 1250 Fix1 |
| `phase_1254_legacy_graph_delta_gap_disposition_recorded` | Phase 1254 ATLAS-G route from Phase 1250 Fix1 |
| `phase_1250_fix1_gap_audit_routes_reconciled_phase_1256` | Phase 1256 closure reconciliation requirement |
| `tla_refinement_notes_pre_rc_window_1241_plus_candidate` | Phase 1255 |
| `allowlist_export_procedure_window_1241_plus_candidate` | Phase 1255 |
| `unknown_unknown_discovery_required_before_phase_execution` | All phases |
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
- public claimability activation;
- wallet withdrawal, transfer, or spend semantics;
- ECU minting authorization;
- ILC settlement or withdrawal runtime;
- release-key generation;
- release envelope production;
- signed Genesis v0.1 mutation;
- Genesis Atlas mutation, regeneration, or signing;
- immutable diagnostic mutation;
- production `commit.epoch` emission authorization;
- v0.2 signing.

---

## 11. Graph Delta

This phase is a planning/sequence-lock phase. It adds no runtime graph edge, no
Genesis Star Map node, no Genesis Atlas node, and no package-profile reachability
manifest.

```text
graph_delta=support_only:docs/specs/ilc_phase_1249_1256_sequence_lock_v0.1.md -> planning/frontier
```

---

## 12. Next Phase

Next planned phase:

```text
Phase 1250 - Gap 14 adapter extraction for ilc_logic migration debt
```

Phase 1250 is NON-SENSITIVE and may proceed after this sequence lock under the
locked ordering. It may edit code only to reduce package-boundary/import debt
and must preserve the non-authorization boundary above.
