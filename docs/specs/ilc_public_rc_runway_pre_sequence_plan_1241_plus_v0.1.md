# ILC Public RC Runway Pre-Sequence Plan 1241+ v0.1

**Status:** Planning-only pre-sequence artifact.
**Recorded:** 2026-05-07.
**Authority:** Current canon remains `PLANNING_INDEX.md`, `STATUS.md`, the active
Window 1233-1240 guidance and sequence lock, the CDL register, and the latest
context capsule. This document does not open Window 1241+, does not replace a
Window 1241+ sequence lock, and does not authorize public RC, public repository
publication, public launch, CDL mutation, signing, release-key generation, or
production network exposure.

`public_rc_runway_pre_sequence_plan_1241_plus_recorded_phase_1238`

---

## 1. Purpose

This document closes the current planning gap between:

1. the committed gap inventory in Launch Roadmap v1.0, and
2. the future Window 1241+ sequence lock, which cannot be validly issued until
   Phase 1240 closes Window 1233-1240.

It is a pre-sequence runway: it assigns candidate window bands, identifies the
public-RC blockers that must be classified more sharply, and records the
retrieval basis used so future agents do not depend on stale memory.

---

## 2. Retrieval Basis

This planning pass used repo-local retrieval, historical literature retrieval,
and MemPalace-style historical search. The historical material is evidence and
context, not authority over current canon.

Primary current-canon inputs:

- `docs/PLANNING_INDEX.md`
- `docs/phases/STATUS.md`
- `docs/specs/ilc_phase_1233_1240_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_1233_1240_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.0.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.49.md`
- `docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md`

Historical / literature retrieval anchors:

- `docs/specs/ilc_window_607_612_candidate_phase_grouping_v0.1.md` - ECU / ILC
  layer separation; MemPalace retrieval permitted as drafting support but not
  authority.
- `docs/specs/ilc_ecu_to_ilc_lifecycle_contract_spec_615_v0.1.md` - visible
  ECU-to-ILC lifecycle touchpoint and no-public-claimability boundary.
- `docs/specs/ilc_public_wallet_runtime_integration_653_v0.1.md` - wallet
  `claimability_state=deferred` boundary.
- `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md` - visible
  balances do not imply public claimability.
- `docs/whitepaper/ilc_whitepaper_working_draft_v6_0.md` and
  `docs/whitepaper/ilc_whitepaper_agent_edition_v0.2.md` - Protocol Bundle and
  OpenClaw deployment-artifact framing.
- `docs/research/constitution_dredge_raw_v0.1.jsonl` - historical conversation
  extracts on ECU as score, ECU-to-ILC budgeted conversion, and agent work
  replay/rescoring before mainnet economic carry-over.
- `docs/specs/ilc_window_913_920_closure_gate_919_v0.1.md` - example of explicit
  MemPalace retrieval requirement before a later sequence lock.

Retrieval rule:

```text
historical_retrieval_is_context_not_authority_current_canon_controls
```

---

## 3. Current Planning Corrections Needed

Launch Roadmap v1.0 remains the active roadmap, but parts of its early RC2
status surface are stale because it was produced at Phase 1192 and later edited
with new Gaps 9-14. Current canon records:

- CDL-086 is ratified in Phase 1220.
- Tier-3 runtime linkage was implemented in Phase 1201.
- Persistent fetch rate limiter backend was implemented in Phase 1202 and wired
  into HTTP fetch transport in Phase 1212.

Therefore a Roadmap v1.1 refresh is required after Phase 1240 closure. The v1.1
refresh should not merely append Gaps 9-14; it should reconcile the whole RC2 /
public-RC status table against current canon.

Token:

```text
launch_roadmap_v1_1_refresh_required_after_phase_1240
```

---

## 4. Public RC Blocker Classes

Future planning must separate blockers by the public action they block. The
current planning files already contain the raw tokens, but the next roadmap must
classify them in this form.

| Blocker class | Blocks | Examples |
|---------------|--------|----------|
| Public repository publication | Making the repository or selected public source tree public | US provisional patent filing, license instrument, public-doc exclusions, patent-pending folder exclusion |
| Public RC claim | Any claim that ILC is a public release candidate | package-size audit, release artifact manifest, lineage/allowlist export, regression closure, public claimability present for the selected RC profile |
| Public P2P exposure | Any hostile-network peer-to-peer node operation | TransportPrincipal, Rust P2P substrate ADR, Python HTTP downgrade, principal-bound rate limiting |
| Public sidecar/projection serving | Network-accessible graph projection or sidecar endpoint | CDL-087 ratification, TransportPrincipal auth, privacy aggregation, rate limit policy |
| Public economic claimability | Human withdrawal/claim/transfer path for ILC | ECU-to-ILC conversion runtime, public claimability substrate, receipts |
| OpenClaw/NemoClaw local skill preview | Local package/skill inside a harness, no public P2P claim, no public claimability claim | package boundary split, CLI/local sidecar API, harness adapter protocols, package-size audit |
| OpenClaw/NemoClaw claimable public RC | Final public-RC target profile: local harness package, no ILC-owned public P2P claim, public ECU-to-ILC claimability present | Gap 14 package modularity, Gap 13 ECU-to-ILC conversion and public claimability, release artifact manifest |

Token:

```text
public_rc_blocker_classification_required_in_roadmap_v1_1
```

---

## 5. Candidate Window Bands

These bands are approximate and non-authorizing. Exact phase numbers must be
assigned by the Window 1241+ sequence lock after Phase 1240 closes.

### Window 1241-1248 candidate - synthesis, reconciliation, and evidence

Primary scope:

- Publish Roadmap v1.1 as the new controlling public-RC roadmap with
  current-canon reconciliation and a clear supersession/tombstone note on v1.0.
- Execute the first Gap 14 implementation slice before Gap 10 public-P2P work:
  package profile contracts, import boundary linting, adapter protocol stubs,
  and dependency-isolated tests for the OpenClaw/NemoClaw skill path.
- Consume Phase 1238 Fix evidence and decide whether CDL-087 can advance.
- Publish Window 1241+ sequence lock.
- Run lineage receipt / allowlist export tooling plan or implementation.
- Execute TLA+ refinement notes pre-RC item.
- Classify public RC blockers by action class.

Candidate tokens:

```text
window_1241_plus_sequence_lock_required_after_phase_1240
roadmap_v1_1_must_reconcile_cdl_086_tier3_persistent_limiter_current_state
roadmap_v1_1_must_become_controlling_public_rc_roadmap
gap_14_package_modularity_first_slice_before_gap_10_transport_principal
openclaw_skill_claimable_profile_is_final_public_rc_target_no_public_p2p
cdl_087_ratification_candidate_requires_sim_fetch_01_fix_evidence
allowlist_export_procedure_window_1241_plus_candidate
tla_refinement_notes_pre_rc_window_1241_plus_candidate
```

### Window 1249-1256 candidate - public transport identity and substrate

Primary scope:

- TransportPrincipal CDL/spec.
- Principal-bound D2D admission and rate limiting.
- Issuance, rotation, revocation, replay prevention, and local-ban semantics.
- ADR deciding Quinn/rustls extension vs libp2p vs adapter boundary.
- Formal Python HTTP transport downgrade to devnet/test only.

Candidate tokens:

```text
transport_principal_window_1249_1256_candidate
rust_p2p_substrate_adr_window_1249_1256_candidate
python_http_transport_devnet_test_downgrade_window_1249_1256_candidate
```

### Window 1257-1264 candidate - fetch distribution, sidecar serving, and flow control

Primary scope:

- CDL-087 ratification if SIM-FETCH-01 evidence supports it.
- Sidecar projection endpoint only after CDL-087 and TransportPrincipal policy.
- SIM-FETCH-01 Werner Flow Governor overlay.
- Werner flow-governor CDL opening/prelock if simulation evidence supports it.
- No heat-signal direct ECU minting.

Candidate tokens:

```text
cdl_087_ratification_window_candidate_after_sim_fetch_01_evidence
sidecar_projection_endpoint_window_candidate_after_cdl_087_and_transport_principal
werner_flow_governor_overlay_window_candidate
```

### Window 1265-1272 candidate - package hardening and harness adapter integration

Primary scope:

- Continue the Gap 14 implementation after the first slice: package-boundary
  enforcement across the actual import graph, packaging CI gates, and real
  OpenClaw/NemoClaw adapter integration tests.
- Split package boundaries if not already complete: `ilc_consensus_core`,
  `ilc_consensus_node`, `ilc_logic`, `ilc_node_runtime`, `ilc_cli`,
  `ilc_harness_adapters`.
- Publish or finalize PyO3/FFI binding plan.
- Harden local sidecar/CLI profiles after the import-boundary lint exists.

Candidate tokens:

```text
openclaw_skill_first_vs_ilc_p2p_first_decision_required
package_boundary_import_lint_required_before_openclaw_skill_preview
generic_harness_adapter_contract_window_candidate
package_boundary_enforcement_ci_gate_window_candidate
```

### Window 1273-1280 candidate - ECU credit creation path

Primary scope:

- ECUCreditCreationIntent spec and wallet-side signing path.
- Productive credit authorization CDL.
- Exposure ceilings, escrow, clawback, and failed-commitment cancellation.
- Consensus-epoch-settled creation; wallet cannot mint ECU.

Candidate tokens:

```text
ecu_credit_creation_window_candidate
productive_credit_authorization_cdl_window_candidate
wallet_must_request_not_mint_ecu_runtime_gate
```

### Window 1281-1288 candidate - ECU-to-ILC conversion and claimability

Primary scope:

- Production conversion runtime.
- Fixed-point `P_e` governor.
- ECU lot accounting and mandatory conversion sweeper.
- ILC issuance budget accounting.
- Machine-verifiable receipts.
- Public claimability substrate decision.

Candidate tokens:

```text
ecu_to_ilc_conversion_window_candidate
pe_governor_window_candidate
public_claimability_substrate_decision_window_candidate
```

### Window 1289-1296 candidate - release/legal/IP/signing closure

Primary scope:

- US provisional patent application filed before public repository publication.
- License instrument, CLA/DCO, trademark policy.
- Genesis canonical lineage ADR route.
- v0.2 signing if explicitly authorized.
- Release artifact manifest and distribution checklist finalization.
- Public package-size audit.

Candidate tokens:

```text
public_repo_publication_prerequisites_window_candidate
license_cla_trademark_closure_window_candidate
us_provisional_patent_gate_window_candidate
v0_2_signing_authorization_tail_slot_candidate
```

### Final public RC closure window candidate

Primary scope:

- Public-RC readiness sweep.
- All blocker classes closed or explicitly scoped out of the RC claim.
- Release artifact build from selected packaging profile.
- Full regression, guardrail, canonical JSON, no-float economic boundary, and
  no-unbounded-network-surface sweep.
- Explicit public RC authorization token before any public claim.

Candidate token:

```text
public_rc_closure_window_candidate_requires_all_blocker_classes_disposed
```

---

## 6. Recommended Branch Decision

The preferred public-RC path should be decided explicitly:

1. **OpenClaw/NemoClaw skill-first RC** - local package/skill, CLI/local sidecar,
   public ECU-to-ILC claimability for the selected public-RC profile, no public
   ILC P2P claim. This can likely reach an external agentic harness preview
   earlier and reduces reliance on public transport readiness.
2. **ILC-owned public P2P RC** - full public network substrate first. This is the
   stronger infrastructure claim but requires TransportPrincipal, Rust P2P, and
   Python HTTP downgrade before exposure.

Recommended default unless overruled:

```text
public_rc_default_path=openclaw_skill_first_public_claimability_no_public_p2p_claim
```

This default does not remove the public P2P lane. It makes public P2P a parallel
hardening track while the first external-facing RC is a local/harness package
surface. The `openclaw_skill_local` profile is a local-preview profile only; the
final public-RC target is the claimable OpenClaw/NemoClaw skill profile, which
must include ECU-to-ILC conversion and public claimability runtime surfaces.

---

## 7. Gaps Closed By This Pre-Sequence Plan

Closed at planning level:

- The Roadmap v1.0 stale-status issue is recorded and routed to Roadmap v1.1.
- Public RC vs public launch vs public P2P vs public claimability are separated
  as blocker classes.
- OpenClaw/NemoClaw skill-first vs ILC-owned-P2P-first is identified as an
  explicit decision.
- The no-window float-migration item is routed into Roadmap v1.1 classification
  and should be assigned a Window 1241+ or later pre-RC slot.
- The new network/value-path planning file is anchored as a scope document, not
  an orphan task list.

Still not closed, intentionally:

- The Window 1241+ sequence lock itself.
- Any exact Phase 1241+ phase numbers.
- Any CDL mutation or ratification.
- Any implementation authorization.

---

## 8. Required Index / Roadmap Pointers

This document must be pointed to from:

- `docs/PLANNING_INDEX.md` §0.
- Launch Roadmap v1.0 as a post-Phase-1238 pre-sequence addendum.
- Phase 1239 coherence/capsule, if committed before Phase 1239 runs.
- Phase 1240 closure handoff.

Token:

```text
public_rc_runway_pre_sequence_plan_must_feed_window_1241_plus_sequence_lock
```
