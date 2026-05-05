# ILC Window 1191-1199: Candidate Phase Grouping

**Author:** Codex (local planning synthesis)
**Date:** 2026-05-04
**Baseline:** Window 1183-1190 CLOSED at Phase 1190 with closure verdict PASS.
Capsule v5.44 is current. CDL-085 is ratified and active in runtime with
`EDGE_MINT_PHI_BOUND = Decimal("0.60")`; all three SIM-SPECTRAL-05 observer slices
passed; v0.2 signing remains deferred pending explicit signing authorization; public-launch
packaging blocker scoping completed with fresh-CDL routing.
**Planning note:** This is a candidate grouping, not a locked sequence. Phase 1191 must
publish the sequence lock before execution. Sensitive phases require explicit human GO.

---

## 1. Window Objective

Window 1191-1199 should move from CDL-085 completion into RC2 consolidation.

Primary goals:

- Refresh the launch roadmap to v1.0 so it reflects the actual post-1190 frontier.
- Preserve the v0.2 signing ceremony as an explicit conditional human authorization gate.
- Open the public-launch packaging blocker under a fresh CDL number, likely CDL-086 if it
  remains next fresh at opening time.
- Scope or begin the Tier-3 runtime linkage lane.
- Scope or implement the persistent rate limiter gate.
- Triage or repair canon bundle signing tooling debt.
- Publish coherence report + capsule v5.45, then close the window.

Non-goals:

- No public launch claim.
- No public repository publication.
- No counsel/legal conclusion.
- No Genesis v0.1 mutation.
- No v0.2 signing without the explicit signing authorization token.
- No CDL-086 ratification in this window unless a later human explicitly re-scopes it.

---

## 2. Incoming State

Constitutional/runtime frontier:

- `CDL-085` is ratified.
- `EDGE_MINT_PHI_BOUND = Decimal("0.60")` is active in `ilc_core/types.py`.
- `CDL_085_DEPENDENCY = "cdl_085_werner_phi_bound_ratified_1185.v0.1"`.
- Runtime version: `epoch_attribution_settle_runtime_1185.v0.6`.
- `CDL-086` appears to be the next fresh CDL number after CDL-085.

SIM frontier:

- Runtime-binding observer slice: `sim_spectral_05_runtime_binding_slice_pass`.
- Economic-flow observer slice: `sim_spectral_05_economic_flow_slice_pass`.
- Gossip observer slice: `sim_spectral_05_gossip_slice_pass`.
- Completion token: `sim_spectral_05_three_slice_observer_framework_complete`.

Genesis frontier:

- Signed v0.1 remains immutable: 32 nodes, 55 edges.
- Root envelope hash:
  `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`.
- Strict diagnostic SHA at Phase 1190 closure:
  `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56`.
- v0.2 candidate remains unsigned: 41 nodes, 73 edges.

Public-launch blocker frontier:

- Phase 1188 scoped the blocker.
- `CDL-001` is ratified signer-lineage canon and should be treated as a dependency.
- The public-launch packaging blocker should use a fresh CDL number, likely CDL-086.
- Counsel track can be a ratification condition; it should not block opening the CDL unless
  the human decides otherwise.

---

## 3. Phase Table

| Phase | Topic | Sensitivity | Status |
|-------|-------|-------------|--------|
| 1191 | Window sequence lock | SENSITIVE | Firm; requires `GO Phase 1191` |
| 1192 | Launch roadmap v1.0 / RC2 status refresh | NON-SENSITIVE | Firm |
| 1193 | v0.2 signing ceremony conditional slot | SENSITIVE if executed | Requires `v0_2_signing_ceremony_authorized_phase_1193` and `GO Phase 1193`; otherwise skip |
| 1194 | CDL-086 public-launch packaging blocker opening | SENSITIVE constitutional | Requires `GO Phase 1194` and CDL mutation env |
| 1195 | Tier-3 runtime linkage scoping / first tranche | NON-SENSITIVE | Firm |
| 1196 | Persistent rate limiter scoping / bounded implementation | NON-SENSITIVE | Firm |
| 1197 | Canon bundle signing repair | NON-SENSITIVE | Conditional tail; run if capacity remains |
| 1198 | Coherence report + capsule v5.45 | NON-SENSITIVE | Firm |
| 1199 | Window closure gate | SENSITIVE | Firm; requires `GO Phase 1199` |

---

## 4. Recommended Sequencing Rationale

Phase 1192 should precede the other work because roadmap v0.9 is stale: it says CDL-085 is
open, runtime-binding/economic-flow/gossip slices are incomplete, and RC2 gate 1 is not
satisfied. A v1.0 refresh prevents later phases from inheriting stale planning text.

Phase 1193 remains conditional because v0.2 signing is materially different from normal
documentation work. The prerequisites are met, but the signing authorization token is still
absent.

Phase 1194 opens the packaging blocker after the roadmap refresh so the opening uses current
RC2 language and the corrected CDL-001 dependency relationship. Opening CDL-086 does not
ratify it and does not make a public launch claim.

Phases 1195-1197 address RC2 execution debt. Tier-3 linkage and persistent rate limiting are
RC2 gates. Canon bundle signing repair is lower urgency but useful to clear while the window
is already consolidating release/packaging surfaces.

---

## 5. Open Human Decisions

Before or during Phase 1191:

- Decide whether to issue `v0_2_signing_ceremony_authorized_phase_1193`.
- Decide whether CDL-086 opening is authorized this window. Recommendation: yes, as opening
  only; counsel/legal completion should be a ratification condition.
- Decide whether Phase 1195 should be scoping-only or may implement a bounded first tranche
  if the code path is obvious after inspection. Recommendation: scope first, implement only
  if small and testable.
- Decide whether Phase 1197 should run this window if Phase 1195 or 1196 expands. Recommendation:
  include if capacity remains; otherwise defer without blocking closure.

### Phase 1192 default decisions

Unless superseded by later explicit human instruction:

- v0.2 signing authorization has not been issued. Phase 1193 should use the documented
  skip path unless `v0_2_signing_ceremony_authorized_phase_1193` and `GO Phase 1193` are
  both issued before execution.
- Phase 1195 remains scope-first. A bounded first tranche is acceptable only if code
  inspection finds a small, unambiguous, testable runtime change with no protocol ambiguity.
- Phase 1197 should be treated as firm-if-reached, not merely optional capacity filler. The
  canon bundle repair may still defer if Phase 1195 or 1196 expands unexpectedly.

---

## 6. Carry-Forward Tokens

Window 1191-1199 should consume or preserve:

- `v0_2_signing_ceremony_deferred_pending_signing_authorization`
- `cdl_001_genesis_blocker_scoping_committed_phase_1188`
- `sim_spectral_05_three_slice_observer_framework_complete`
- `cdl_085_ratified_phase_1185`
- `capsule_v5_44_supersedes_v5_43`

Expected new tokens:

- `window_1191_1199_sequence_lock_committed`
- `launch_roadmap_v1_0_published_phase_1192`
- `v0_2_signing_ceremony_deferred_pending_signing_authorization` or a signed-v0.2 token
- `cdl_086_public_launch_packaging_blocker_opened_phase_1194`
- `tier3_runtime_linkage_scope_committed_phase_1195`
- `persistent_rate_limiter_scope_committed_phase_1196`
- `canon_bundle_signing_repair_triaged_phase_1197`
- `capsule_v5_45_supersedes_v5_44`
- `window_1191_1199_closed_phase_1199`

---

## 7. Guardrails

- Do not mutate signed Genesis v0.1.
- Do not regenerate or commit the immutable compile coverage diagnostic unless a phase
  explicitly authorizes a new diagnostic version. Closure must verify the Phase 1190 SHA.
- Do not use floats for economic, attribution, or staking runtime state.
- Do not open or ratify a CDL without the required human GO and CDL mutation environment.
- Do not claim public-launch readiness from CDL-086 opening alone.
- Do not treat counsel/legal drafting as completed by internal planning docs.
