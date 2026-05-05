# ILC Launch Roadmap: Three Computers, Seven Agents

**Version:** v1.0
**Produced:** 2026-05-05
**Session context:** Window 1191-1199 is in progress through Phase 1192. Window
1183-1190 closed with CDL-085 ratified, `EDGE_MINT_PHI_BOUND = Decimal("0.60")`
active in runtime, and all three SIM-SPECTRAL-05 observer slices complete. Capsule v5.44
is current until Phase 1198 publishes v5.45.
**Supersedes:** `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.9.md`
**Purpose:** Refresh the public-RC and RC2 planning surface after CDL-085 ratification,
runtime activation, gossip-slice completion, and the Phase 1188 correction that routes the
public-launch packaging blocker to a fresh CDL number rather than CDL-001.

`launch_roadmap_v1_0_published_phase_1192`

---

## 1. What Has Changed Since v0.9

| Item | v0.9 state | Current v1.0 state |
|------|------------|--------------------|
| CDL-085 | Open / not ratified | **Ratified** in Phase 1185 (`cdl_085_ratified_phase_1185`) |
| EDGE_MINT_PHI_BOUND | Unset planning candidate | **Active runtime value:** `EDGE_MINT_PHI_BOUND = Decimal("0.60")` |
| Attribution runtime | `epoch_attribution_settle_runtime_1129_fix1.v0.5` | **`epoch_attribution_settle_runtime_1185.v0.6`** |
| Runtime dependency | CDL-084 only | `CDL_085_DEPENDENCY = "cdl_085_werner_phi_bound_ratified_1185.v0.1"` |
| SIM-SPECTRAL-05 runtime-binding slice | Deferred | **Passed** (`sim_spectral_05_runtime_binding_slice_pass`) |
| SIM-SPECTRAL-05 economic-flow slice | Deferred | **Passed** (`sim_spectral_05_economic_flow_slice_pass`) |
| SIM-SPECTRAL-05 gossip slice | Deferred | **Passed** (`sim_spectral_05_gossip_slice_pass`) |
| SIM-SPECTRAL-05 framework | Partial | **Complete:** `sim_spectral_05_three_slice_observer_framework_complete` |
| Public-launch packaging blocker | Label drift around CDL-001 | **CDL-086 is OPEN** (`cdl_086_public_launch_packaging_blocker_opened_phase_1194`); CDL-001 is a dependency |
| v0.2 signing | Prerequisites met, unsigned | Still unsigned; explicit signing authorization absent |
| Window state | Pre-1183 planning | Window 1191-1199 active through Phase 1192 |

---

## 2. Current State Summary

| Surface | Status |
|---------|--------|
| Option B selection | **SELECTED** (`adr_0028_posture=option_b`, Phase 814) |
| Row 5 privacy lane | **`runtime_closed`** (Phase 846, CDL-072) |
| Row 7 | **`runtime_closed`** |
| Row 8 | **`pass`** |
| Truth primitive stack | **OPERATIONAL** — submit → persist → gossip → fetch → spectral routing loop |
| RC0.1 substrate | **`satisfied_for_testbed`** |
| RC1 | **`satisfied`** — CDL-073 through CDL-084 ratified; HB-002 closed |
| CDL-084 | **RATIFIED** — `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`; `PROVENANCE_MAX_DEPTH = 3` |
| CDL-085 | **RATIFIED** — Werner φ-bound provenance equivalence limit |
| EDGE_MINT_PHI_BOUND | **ACTIVE** — `Decimal("0.60")` |
| Runtime | **`epoch_attribution_settle_runtime_1185.v0.6`** |
| SIM-SPECTRAL-05 observer slices | **COMPLETE** — runtime-binding, economic-flow, and gossip all passed |
| ADR-0037 Genesis Canonical Lineage Contract | **ACCEPTED** |
| ADR-0036 Operational Release Key | **ACCEPTED** |
| Genesis Atlas v0.1 signed | **IMMUTABLE** — 32 nodes, 55 edges, hash `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c` |
| Genesis Atlas v0.2 candidate | **41 nodes, 73 edges, unsigned** — signing prerequisites met; explicit human authorization required |
| Public-launch packaging blocker | **OPEN** — CDL-086 opened in Phase 1194; not ratified |
| Tier-3 runtime linkage | Governance met; runtime lane not yet implemented |
| Persistent rate limiter | Open RC2 gate |

---

## 3. RC Milestone Map

| Milestone | Gate criteria | Current status |
|-----------|---------------|----------------|
| RC0.1 | Three-node substrate; 7-agent scenario; reproducible substrate | **`satisfied_for_testbed`** |
| RC1 | CDL-073 bootstrap schema; truth primitive stack operational; CDL-078 relay incentives; HB-002 closed | **`satisfied`** |
| RC2 | CDL-085 ratified; v0.2 signed; Tier-3 linkage; public-launch packaging blocker evaluated/progressed; persistent rate limiter; truth-primitive permanence governance | **In progress** — gate 1 satisfied |
| RC3 / Launch | L4 privacy wired; CDL-070 PQ ceremony; compaction CDL; multi-hop attribution CDL; counsel track complete | Long-range |

### RC2 Gate Status

| # | Gate | Status |
|---|------|--------|
| 1 | CDL-085 ratified and active | **SATISFIED** |
| 2 | v0.2 signing ceremony executed | **OPEN** — authorization absent |
| 3 | Tier-3 runtime linkage | **OPEN** — Phase 1195 scope-first |
| 4 | Public-launch packaging blocker evaluated/progressed | **IN PROGRESS** — CDL-086 is open, not ratified |
| 5 | Persistent rate limiter | **OPEN** — Phase 1196 |
| 6 | Truth-primitive permanence community ratification | **OPEN** — governance carry-forward |

---

## 4. Gap Inventory

### Gap 1 — v0.2 Signing Ceremony

**Status:** Prerequisites met; explicit signing authorization absent.

ADR-0036 and ADR-0037 satisfy the governance prerequisites for signing the 41-node /
73-edge v0.2 candidate. The signing act still requires:

```text
v0_2_signing_ceremony_authorized_phase_1193
GO Phase 1193
```

If those tokens are not issued, Phase 1193 must use the skip path and preserve:

```text
v0_2_signing_ceremony_deferred_pending_signing_authorization
```

### Gap 2 — Public-Launch Packaging Blocker

**Status:** CDL-086 is open; ratification remains future work.

Phase 1188 corrected the roadmap label drift. CDL-001 is ratified signer-lineage canon and
is a dependency, not the public-launch packaging blocker target. The packaging blocker
opened under fresh number CDL-086 in Phase 1194.

`cdl_086_public_launch_packaging_blocker_opened_phase_1194`

Opening scope should cover:

- public release artifact definition;
- launch trigger conditions;
- release packaging and distribution governance;
- relationship to RC2, RC3, and public launch;
- dependency on CDL-001, ADR-0036, ADR-0037, and CDL-085;
- counsel track as a ratification condition.

### Gap 3 — Tier-3 Runtime Linkage

**Status:** Governance prerequisite met; runtime work open.

ADR-0020 is accepted. Phase 1195 should remain scope-first, with bounded implementation
only if inspection shows a small, unambiguous, testable first tranche.

### Gap 4 — Persistent Rate Limiter

**Status:** Open RC2 gate.

Phase 1196 should inspect the existing limiter surface and either implement a bounded,
testable persistence hardening change or publish a concrete implementation plan. It must
not introduce wall-clock protocol logic, predictable PRNG use, or unbounded input handling.

### Gap 5 — Truth-Primitive Permanence Community Ratification

**Status:** Governance carry-forward.

`truth_primitive_permanence_requires_community_ratification_before_genesis_sunset`

This remains a pre-public-RC governance requirement and is not assigned to Window
1191-1199.

### Gap 6 — Canon Bundle Signing Repair

**Status:** Tooling debt; firm-if-reached in Window 1191-1199.

The known failing fixtures remain:

- `test_canon_bundle_audit_artifact.py`
- `test_canon_bundle_pipeline_report.py`

Phase 1197 should run if the window reaches it. The repair remains non-sensitive and must
not mutate signed Genesis v0.1 or regenerate immutable diagnostics.

### Gap 7 — Counsel Track

**Status:** Parallel lane.

Contributor agreement, license strategy, and trademark/identity policy remain required for
public launch. Internal roadmap or CDL opening docs do not constitute legal conclusions.

### Gap 8 — Long-Range Economic and Scale Work

**Status:** Deferred.

- Multi-hop centrality attribution CDL — research evidence exists; CDL not opened.
- Cross-epoch compaction / snapshot export — required before network-scale operation.
- CDL-070 PQ migration ceremony — SIM-MONETARY-01 prerequisite.

---

## 5. Window 1191-1199 Execution Policy

The following policy answers the open decisions raised during Phase 1192:

| Question | Default for this window |
|----------|-------------------------|
| v0.2 signing authorization | Not issued as of Phase 1192; Phase 1193 skips unless the explicit token is provided before execution |
| Phase 1195 scope vs implementation | Scope-first; bounded implementation allowed only if small, unambiguous, and testable |
| Phase 1197 conditionality | Treat as firm-if-reached; defer only if prior phases expand unexpectedly |

Sensitive gates remain unchanged:

- Phase 1193 requires signing authorization and `GO Phase 1193`.
- Phase 1194 requires `GO Phase 1194` plus CDL mutation environment.
- Phase 1199 requires `GO Phase 1199`.

---

## 6. Layered Network Delivery Architecture

| Layer | Mechanism | CDL | Status |
|-------|-----------|-----|--------|
| L1 | Announcement gossip — soft push-signal | CDL-076 | **Ratified** |
| L2 | WANT-HAVE/WANT-BLOCK two-phase fetch; rate limiting | CDL-077 | **Ratified** |
| L3 | star.map N-gram route index; spectral routing | CDL-079, CDL-080 | **Ratified** |
| L4 | Onion routing + SURB reply envelopes | Future CDL | H-series designed; not wired |
| L5 | Relay incentives; centrality attribution; provenance attribution | CDL-078, CDL-081, CDL-084, CDL-085 | **Ratified where opened** |

---

## 7. Relationship to Current Canon

| Artifact | Path | Role |
|----------|------|------|
| Capsule v5.44 | `docs/specs/ilc_antigravity_context_capsule_v5.44.md` | Current frontier capsule until Phase 1198 |
| Window 1183-1190 handoff | `docs/specs/ilc_window_1183_1190_handoff_1190_v0.1.md` | Incoming handoff for Window 1191-1199 |
| Window 1191-1199 sequence lock | `docs/specs/ilc_phase_1191_1199_sequence_lock_v0.1.md` | Active sequence lock |
| CDL master log | `docs/specs/ilc_constitutional_decision_log_v0.1.md` | Authoritative CDL status |
| ADR-0037 | `docs/adr/ADR_0037_Genesis_Canonical_Lineage_Contract.md` | Accepted; lineage/equivalence/merge governance |
| ADR-0036 | `docs/adr/ADR_0036_Operational_Release_Key_Genesis_Binding.md` | Accepted; release key mechanism |
| SIM-SPECTRAL-05 disposition | `docs/sims/sim_spectral_05/disposition_1171_v0.1.md` | Gate pass evidence |
| SIM runtime-binding slice | `docs/sims/sim_spectral_05/runtime_binding_slice_disposition_1179_v0.1.md` | Observer slice pass |
| SIM economic-flow slice | `docs/sims/sim_spectral_05/economic_flow_slice_disposition_1180_v0.1.md` | Observer slice pass |
| SIM gossip slice | `docs/sims/sim_spectral_05/gossip_slice_disposition_1187_v0.1.md` | Observer slice pass |
| Phase 1188 scoping | `docs/specs/ilc_cdl_001_genesis_blocker_scoping_1188_v0.1.md` | Fresh-CDL packaging-blocker routing |

---

## 8. What This Roadmap Does NOT Claim

- v0.2 Atlas signing ceremony executed.
- Any release key generated or registered in Window 1191-1199 so far.
- CDL-086 ratified.
- Any public launch claim.
- Any public repository publication.
- Counsel track completion.
- Tier-3 runtime linkage implemented.
- Persistent rate limiter completed.
- Truth-primitive permanence ratified by community governance.
