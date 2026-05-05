# ILC Antigravity Context Capsule v5.46

**Date:** 2026-05-05
**Supersedes:** `docs/specs/ilc_antigravity_context_capsule_v5.45.md`
**Produced:** Phase 1207, Window 1200-1208
**Frontier:** Window 1200-1208 in progress; Phase 1207 complete; Phase 1208 closure gate pending

`capsule_v5_46_supersedes_v5_45`
`window_1200_1208_sequence_lock_committed`
`tier3_runtime_linkage_runtime_1201.v0.1`
`persistent_fetch_rate_limiter_runtime_1202.v0.1`
`cdl_086_deliberation_committed_phase_1203`
`edge_mint_phi_bound_enforcement_not_yet_implemented`
`cdl_086_prelock_committed_phase_1204`
`v0_2_signing_ceremony_deferred_pending_signing_authorization`
`truth_primitive_permanence_governance_routed_phase_1206`
`coherence_report_1207_verdict=pass`

---

## 1. Current State

Window 1200-1208 is complete through Phase 1207. Phase 1208 remains pending and is
SENSITIVE.

Current coherence report:

- `docs/specs/ilc_integration_coherence_report_1207_v0.1.md`

Current active window lock and guidance:

- `docs/specs/ilc_phase_1200_1208_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_1200_1208_candidate_phase_grouping_v0.1.md`

Current roadmap:

- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.0.md`

---

## 2. Runtime Frontier

Implemented this window:

```python
TIER3_RUNTIME_LINKAGE_VERSION = "tier3_runtime_linkage_runtime_1201.v0.1"
PERSISTENT_RATE_LIMITER_VERSION = "persistent_fetch_rate_limiter_runtime_1202.v0.1"
```

Existing attribution runtime:

```python
EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION = "epoch_attribution_settle_runtime_1185.v0.6"
PROVENANCE_DECAY_ALPHA = Decimal("0.45")
EDGE_MINT_PHI_BOUND = Decimal("0.60")
CDL_085_DEPENDENCY = "cdl_085_werner_phi_bound_ratified_1185.v0.1"
```

Gemini pre-1204 audit hardening:

- H-CON-02 malformed quorum guard hardened.
- Zero-remaining-member ejected-stake votes are explicitly invalid.
- `EDGE_MINT_PHI_BOUND` settlement enforcement remains a Window 1209+ implementation
  obligation: `edge_mint_phi_bound_enforcement_not_yet_implemented`.

---

## 3. Constitutional Frontier

`CDL-085` remains ratified and runtime-active:

- `cdl_085_ratified_phase_1185`
- `EDGE_MINT_PHI_BOUND = Decimal("0.60")`

`CDL-086` is open and prelocked, not ratified:

- Opening token: `cdl_086_public_launch_packaging_blocker_opened_phase_1194`
- Deliberation token: `cdl_086_deliberation_committed_phase_1203`
- Prelock token: `cdl_086_prelock_committed_phase_1204`

CDL-086 prelock does not authorize public launch, public repository publication, public
release artifact distribution, legal/counsel conclusions, release-key generation, v0.2
signing, or ratification.

Truth-primitive permanence is routed:

- `truth_primitive_permanence_governance_routed_phase_1206`
- `truth_primitive_permanence_ratification_packet_required_window_1209`

---

## 4. Genesis Atlas Frontier

Signed Genesis v0.1 remains canonical and unchanged:

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
- Status: unsigned candidate
- Signing outcome this window: deferred pending signing authorization
- Token: `v0_2_signing_ceremony_deferred_pending_signing_authorization`

---

## 5. RC2 Gate Status

| Gate | Status |
|------|--------|
| CDL-085 ratified and active | **SATISFIED** |
| v0.2 signing ceremony executed | **OPEN** — authorization absent |
| Tier-3 runtime linkage | **SATISFIED** — runtime linkage implemented |
| Public-launch packaging blocker evaluated/progressed | **IN PROGRESS** — CDL-086 prelocked, not ratified |
| Persistent rate limiter | **SATISFIED** — persistent backend implemented; transport wiring deferred |
| Truth-primitive permanence community ratification | **ROUTED** — ratification packet required |
| Canon bundle signing/report/audit fixture debt | **SATISFIED** |

---

## 6. Active Carry-Forward Obligations

- Phase 1208 closure gate — requires `GO Phase 1208`
- v0.2 signing ceremony — deferred pending explicit signing authorization
- CDL-086 ratification — future sensitive constitutional phase
- CDL-086 counsel/package conditions — unresolved ratification conditions
- persistent rate limiter transport wiring — `persistent_rate_limiter_wiring_deferred_phase_1202`
- `EDGE_MINT_PHI_BOUND` settlement enforcement — `edge_mint_phi_bound_enforcement_not_yet_implemented`
- truth-primitive permanence ratification packet — `truth_primitive_permanence_ratification_packet_required_window_1209`
- contributor agreement, license, trademark — counsel track

---

## 7. Verification

Window 1200-1208 is verified through Phase 1207:

- Phase 1200 sequence-lock tests passed
- Phase 1201 Tier-3 runtime linkage tests passed
- Phase 1202 persistent-rate-limiter tests passed
- Phase 1203 CDL-086 deliberation tests passed
- Phase 1204 CDL-086 prelock tests passed
- Phase 1205 signing deferral tests passed
- Phase 1206 truth-primitive permanence routing tests passed
- Immutable diagnostic SHA remains:
  `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56`

Phase 1208 closure gate remains pending.

`capsule_v5_46_supersedes_v5_45`
