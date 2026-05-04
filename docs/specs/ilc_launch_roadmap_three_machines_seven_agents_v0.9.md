# ILC Launch Roadmap: Three Computers, Seven Agents

**Version**: v0.9
**Produced**: 2026-05-04
**Session context**: Window 1166-1175 closed (`ee0f6b48`); SIM-SPECTRAL-05 gate pass;
CDL-085 open (not ratified); ADR-0036 + ADR-0037 accepted; capsule v5.42.
**Supersedes**: `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.8.md`
**Purpose**: First roadmap update to reflect SIM-SPECTRAL-05 completion, Genesis Canonical
Lineage Contract acceptance, CDL-085 opening, and the v0.2 signing ceremony becoming
unblocked. Sections 1, 4, 7, 8 are carried forward from v0.8 with minor updates.
Sections 2, 3, 5, 6 are substantially revised.

---

## 1. What Has Changed Since v0.8

| Item | v0.8 claim | Actual state (v0.9) |
|------|-----------|---------------------|
| CDL-078 | Design intent locked, CDL not opened | **Ratified** (Phase 904) |
| CDL-079 | H-series designed, not wired | **Ratified** (Phase 927) — star.map L3 groundwork |
| CDL-080 | Not in scope | **Ratified** (Phase 935) — spectral routing |
| CDL-081 | Not in scope | **Ratified** (Phase 943) — hyperedge ECU attribution |
| CDL-082 | Not in scope | **Ratified** (Phase ~1009) |
| CDL-083 | Not in scope | **Ratified** (Phase 1105) — H-CON-02 panel quorum |
| CDL-084 | Not in scope | **Ratified** (Phase 1113) — provenance chain attribution; `α=0.45` |
| CDL-085 | SIM-gated, unopened | **Open** (Phase 1172) — not ratified; φ-bound unset |
| HB-002 | Not yet opened | **Closed** (Phase 918) |
| SIM-SPECTRAL-04 | Not run | Gate fail (Phase 1162); S3/S1 calibration issue |
| SIM-SPECTRAL-05 | Not run | **Gate pass** (Phase 1171) — Track A + Track B |
| ADR-0036 | Proposed (Phase 1159) | **Accepted** (Phase 1173) |
| ADR-0037 | Not yet drafted | **Accepted** (Phase 1173) — Genesis Canonical Lineage Contract |
| v0.2 Atlas candidate | 36 nodes | **41 nodes**, 73 edges — still unsigned |
| v0.2 signing prerequisites | ADR-0036 + Lineage Contract pending | **Both satisfied** |
| RC1 | In progress | **`satisfied`** — CDL-073 through CDL-084 ratified; truth primitive stack operational |

---

## 2. Current State Summary (2026-05-04)

| Surface | Status |
|---------|--------|
| Option B selection | **SELECTED** (`adr_0028_posture=option_b`, Phase 814) |
| Row 5 (privacy lane) | **`runtime_closed`** (Phase 846, CDL-072) |
| Row 7 | **`runtime_closed`** |
| Row 8 | **`pass`** |
| H-013 (sealed spectral beacon) | **IMPLEMENTED** — no production gossip activation |
| H-015 (spectral routing) | **PRIMITIVE COMPLETE** |
| Truth primitive stack | **OPERATIONAL** — submit → persist → gossip → fetch → spectral routing loop |
| RC0.1 substrate | **`satisfied_for_testbed`** |
| RC1 | **`satisfied`** — all gates closed (CDL-073 through CDL-084 ratified; HB-002 closed) |
| CDL-084 | **RATIFIED** (Phase 1113) — `PROVENANCE_DECAY_ALPHA = Decimal("0.45")` |
| CDL-085 | **OPEN, not ratified** (Phase 1172) — Werner φ-bound provenance equivalence limit; `EDGE_MINT_PHI_BOUND` unset |
| SIM-SPECTRAL-05 | **PASSED** (`sim_spectral_05_gate_pass`, Phase 1171) |
| ADR-0037 Genesis Canonical Lineage Contract | **ACCEPTED** (`adr_0037_accepted_phase_1173`) |
| ADR-0036 Operational Release Key | **ACCEPTED** (`adr_0036_accepted_phase_1173`) |
| Genesis Atlas v0.1 signed | **IMMUTABLE** — 32 nodes, 55 edges, hash `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c` |
| Genesis Atlas v0.2 candidate | **41 nodes, 73 edges, unsigned** — signing prerequisites met; explicit human authorization required |
| Runtime | `epoch_attribution_settle_runtime_1129_fix1.v0.5` — **unchanged** |
| SIM-SPECTRAL-05 deferred slices | runtime-binding, economic-flow, gossip — deferred Window 1176+ |
| Public-launch packaging blocker | **SCOPED** — fresh CDL required before any public launch claim; ratified CDL-001 is signer-lineage dependency, not target |
| Tier-3 runtime linkage | Governance met (ADR-0020 accepted); runtime lane not yet implemented |

---

## 3. Gap Inventory (Current — as of Phase 1175)

### Gap 1 — CDL-085 prelock and ratification (Werner φ-bound)

**Status: OPEN — prelock required before ratification.**

CDL-085 scope: Werner φ-bound provenance equivalence limit — governs when edge-mint /
provenance-attribution claims are canonical productive work vs Sybil-amplified or
non-canonical derivation branches.

What remains:
- Prelock: establish `EDGE_MINT_PHI_BOUND` value (φ-bound target) via deliberate
  review of SIM-SPECTRAL-05 branchial convergence results (Track B separation = 0.60)
- Runtime spec: where and how `EDGE_MINT_PHI_BOUND` is enforced in `ilc_core/`
- Ratification: CDL-085 amendment through standard prelock → ratification evidence → ratify path
- CDL-V7 / PEC integration: CDL-085 should reference the Popperian Equivalence Criterion
  (ADR-0037 §4) as the provenance equivalence test gate

**Urgency:** HIGH. CDL-085 ratification is the next constitutional frontier item. RC2
gate requires CDL-085 ratified.

### Gap 2 — v0.2 signing ceremony

**Status: prerequisites met; explicit human authorization required.**

ADR-0036 (release key) and ADR-0037 (version equivalence, fork boundary) are both
accepted. The v0.2 candidate has 41 nodes and 73 edges.

What remains:
- Explicit human authorization token for v0.2 signing ceremony
- Signing sequence per ADR-0036 delegation chain
- Release key registration artifact (ADR-0036 §4)
- Release envelope binding (ADR-0036 §5)
- PLANNING_INDEX and capsule update after signing

**Note:** v0.2 signing is NOT blocked on CDL-085 ratification. They are independent tracks.
The version equivalence criterion (ADR-0037 §3.3) governs the signing, not CDL-085.

**Urgency:** HIGH. First signed multi-ADR star map is a milestone for public RC narrative.

### Gap 3 — Tier-3 runtime linkage

**Status: governance prerequisite met; implementation separate lane.**

ADR-0020 (Knowledge-Node-First Design Principle) is accepted (`adr_0020_accepted_phase_1157`).
The governance prerequisite for Tier-3 embedding linkage is satisfied.

What remains:
- `schema:*` / `runtime:*` node class implementation in `ilc_core/`
- Integration with the signed star map reference chain
- Tests and runtime version token

**Urgency:** MEDIUM. Not blocking RC2, but required for Tier-3 completeness and the
launch milestone.

### Gap 4 — SIM-SPECTRAL-05 deferred observer slices

**Status: three slices deferred with explicit carry-forward tokens.**

- `sim_spectral_05_runtime_binding_slice_deferred_window_1176`
- `sim_spectral_05_economic_flow_slice_deferred_window_1176`
- `sim_spectral_05_gossip_slice_deferred_window_1176`

Each slice requires a new SIM program spec declaring the convergence question, then
a Track A / Track B style execution.

**Urgency:** MEDIUM. Needed for completeness of the multi-slice observer framework and
full Genesis encrustation verification.

### Gap 5 — Public-launch packaging blocker

**Status: scoped in Phase 1188. Required before any public launch claim.**

Roadmap correction: earlier wording reused `CDL-001` for the packaging/genesis-blocker
label.
That was label drift. CDL-001 is already ratified signer-lineage canon and remains a
dependency. The packaging/release governance blocker should open under a fresh CDL number,
likely CDL-086 if still next fresh at opening time.

**Urgency:** HIGH for any public RC or launch claim. Not blocking internal testbed work.

### Gap 6 — Truth-primitive permanence community ratification

**Status: governance carry-forward. No CDL mutation.**

`truth_primitive_permanence_requires_community_ratification_before_genesis_sunset`

Community ratification event or CDL required before any Genesis sunset policy takes effect.

**Urgency:** MEDIUM. Pre-public-RC requirement.

### Gap 7 — Canon bundle signing repair

**Status: tooling debt. Two test fixtures failing.**

`test_canon_bundle_audit_artifact.py` and `test_canon_bundle_pipeline_report.py` root
cause not yet resolved.

**Urgency:** LOW. Tooling debt; not blocking any constitutional or runtime work.

### Gap 8 — Multi-hop centrality attribution CDL

**Status: SIM-MULTI-HOP-01 evidence available (Phase 552). CDL not opened.**

SIM-MULTI-HOP-01 studied compounding ECU streams across citation chains (A→B→C).
Evidence is research-only; no CDL opened.

**Urgency:** LOW. Needed for L5 economics completeness; deferred until after CDL-085.

### Gap 9 — Cross-epoch compaction / snapshot export

**Status: deferred.**

LMDB stores accumulate indefinitely. A compaction CDL is needed before the network grows
beyond testbed scale.

**Urgency:** LOW. Needed before RC2 / public network scale.

### Gap 10 — CDL-070 (PQ migration ceremony)

**Status: deferred — SIM-MONETARY-01 prerequisite.**

ML-DSA-65 is the identity root (CDL-069). CDL-070 covers the migration ceremony for
existing BLS keys. SIM-MONETARY-01 must run first.

**Urgency:** LOW. Deep audit agenda; not blocking any RC milestone.

### Gap 11 — Counsel track

**Status: parallel lane.**

- Contributor agreement (required before public repo)
- License strategy (counsel review before public repo)
- Trademark / identity policy (human + counsel before public launch)

**Urgency:** HIGH for public launch narrative. Not blocking testbed work.

---

## 4. Layered Network Delivery Architecture (canonical, v0.8 / v0.9 unchanged)

| Layer | Mechanism | CDL | Status |
|-------|-----------|-----|--------|
| L1 | Announcement gossip — soft push-signal | CDL-076 | **Ratified** |
| L2 | WANT-HAVE/WANT-BLOCK two-phase fetch; rate limiting | CDL-077 | **Ratified** |
| L3 | star.map N-gram route index; spectral routing | CDL-079, CDL-080 | **Ratified** |
| L4 | Onion routing + SURB reply envelopes (privacy) | Future CDL | H-series designed; not wired |
| L5 | Relay incentives; centrality attribution; provenance attribution | CDL-078, CDL-081, CDL-084 | **Ratified** |

---

## 5. Proposed Next Sequence (Window 1176+)

### Window 1176 — v0.2 Signing Ceremony + CDL-085 Prelock

**Primary goals:** Execute the v0.2 signing ceremony (if explicit signing authorization
issued) and establish the CDL-085 prelock (φ-bound value + runtime scope).

These are two independent tracks that can run in the same window:
- **Signing track (Phase 1176-ish):** ADR-0036 §4 registration → signing ceremony → release
  envelope → PLANNING_INDEX/capsule update. Requires explicit human signing authorization.
- **CDL-085 prelock track (Phase 1177-ish):** Deliberate review of SIM-SPECTRAL-05 Track B
  branchial convergence results; establish φ-bound candidate value; write prelock spec;
  commit CDL-085 prelock. No CDL mutation at prelock; just the prelock spec document.

If signing authorization is not issued, the window focuses on CDL-085 prelock + coherence.

**Hard pass conditions (preview):**
- v0.2 signing ceremony (if authorized): signed release envelope exists; ADR-0036 §4
  registration complete; capsule records `genesis_atlas_v0_2_signed`
- CDL-085 prelock: `EDGE_MINT_PHI_BOUND` candidate value documented; prelock spec committed;
  token `cdl_085_prelock_committed_phase_NNNN`

### Window 1177 — CDL-085 Ratification + Observer Slice Progress

**Primary goal:** Ratify CDL-085 (Werner φ-bound provenance equivalence limit) using the
prelock spec from Window 1176 as the ratification evidence base.

Secondary goal: Begin one or two deferred SIM-SPECTRAL-05 observer slices (runtime-binding
and/or economic-flow) as simulation work in parallel with CDL-085 ratification.

**Hard pass conditions (preview):**
- CDL-085 ratified: `EDGE_MINT_PHI_BOUND` locked; runtime enforcement specified;
  constitutional token `cdl_085_ratified_phase_NNNN`
- At least one deferred observer slice addressed with program spec + SIM execution

### Window 1178+ — Tier-3 Runtime + RC2 Preparation

**Primary goal:** Implement Tier-3 runtime linkage (`schema:*` / `runtime:*` node class);
begin fresh-CDL public-launch packaging-blocker evaluation; address any remaining observer
slices.

**Hard pass conditions (preview):**
- Tier-3 runtime: `schema_node_runtime_NNNN.v0.1` deployed and tested
- Public-launch packaging-blocker evaluation: scope, urgency, and sequencing relative to
  public RC documented

---

## 6. RC Milestone Map

| Milestone | Gate criteria | Current status |
|-----------|---------------|----------------|
| RC0.1 | Three-node substrate; 7-agent scenario; reproducible substrate | **`satisfied_for_testbed`** |
| RC1 | + CDL-073 bootstrap schema; truth primitive stack operational; CDL-078 relay incentives; HB-002 closed | **`satisfied`** — CDL-073 through CDL-084 all ratified; HB-002 closed |
| RC2 | + CDL-085 ratified; v0.2 signed; Tier-3 linkage; public-launch packaging blocker evaluated; persistent rate limiter | **In progress** — CDL-085 open/not ratified; v0.2 unsigned; Tier-3 not implemented |
| RC3/Launch | + L4 privacy wired; CDL-070 PQ ceremony; compaction CDL; multi-hop attribution CDL; counsel track complete | Long-range |

**RC2 remaining gates (internal definition):**
1. CDL-085 ratified (`EDGE_MINT_PHI_BOUND` locked)
2. v0.2 signing ceremony executed (explicit human authorization)
3. Tier-3 runtime linkage (`schema:*` / `runtime:*` node class)
4. Public-launch packaging blocker evaluated and progressed under a fresh CDL number
5. Persistent rate limiter (deferred from prior windows)
6. Truth-primitive permanence community ratification

**RC3/Launch remaining gates (preview):**
1. L4 privacy (onion routing / SURB) wired — CDL future
2. CDL-070 PQ migration ceremony (SIM-MONETARY-01 first)
3. Cross-epoch compaction CDL
4. Multi-hop centrality attribution CDL
5. Canon bundle signing repair
6. Full SIM-SPECTRAL-05 observer slice coverage (runtime-binding, economic-flow, gossip)
7. Counsel track complete (contributor agreement, license, trademark)

---

## 7. Relationship to Current Canon

| Artifact | Path | Role |
|---------|------|------|
| Capsule v5.42 | `docs/specs/ilc_antigravity_context_capsule_v5.42.md` | Current frontier capsule |
| CDL master log | `docs/specs/ilc_constitutional_decision_log_v0.1.md` | Authoritative CDL status |
| Window 1166-1175 handoff | `docs/specs/ilc_window_1166_1175_handoff_1175_v0.1.md` | Current closure handoff |
| ADR-0037 | `docs/adr/ADR_0037_Genesis_Canonical_Lineage_Contract.md` | Accepted; lineage/equivalence/merge governance |
| ADR-0036 | `docs/adr/ADR_0036_Operational_Release_Key_Genesis_Binding.md` | Accepted; release key mechanism |
| SIM-SPECTRAL-05 disposition | `docs/sims/sim_spectral_05/disposition_1171_v0.1.md` | Gate pass evidence; branchial convergence baseline |
| CDL-085 opening spec | `docs/specs/ilc_cdl_085_werner_phi_bound_opening_1172_v0.1.md` | CDL-085 opening posture |
| Pre-RC obligations synthesis | `docs/specs/ilc_pre_public_rc_obligations_synthesis_1154_v0.1.md` | Pre-RC obligations register (see postscript for updated status) |
| RC0.1 checklist | `docs/specs/ilc_rc0_1_readiness_checklist_v0.1.md` | All rows `satisfied_for_testbed` |
| star.map spec | `docs/specs/star.map.ngram.route_index.v1.md` | L3 design source |

---

## 8. What This Roadmap Does NOT Claim

- Row 5 privacy lane deployed in production (testbed only)
- CDL-076/077 gossip/fetch deployed in production (testbed only)
- CDL-085 ratified or any active runtime φ-bound value introduced
- v0.2 Atlas signing ceremony executed (prerequisites met; human authorization still required)
- Any public launch claim (fresh-CDL packaging blocker not yet progressed)
- L4 routing operational (H-series designed; not wired)
- CDL-070 PQ ceremony scheduled (SIM-MONETARY-01 not run)
- Tier-3 runtime linkage implemented (governance met; runtime lane not started)
- All SIM-SPECTRAL-05 observer slices tested (gossip remains deferred)

## Postscript 2026-05-04 — Window 1176-1182 Closure

Window 1176-1182 is closed via Phase 1182.

`window_1176_1182_closed_phase_1182`
`window_1176_1182_closure_gate_verdict=pass`

CDL-085 state:

- CDL-085 is open and prelocked, not ratified.
- Candidate value: `EDGE_MINT_PHI_BOUND = Decimal("0.60")`.
- Runtime-binding observer slice passed.
- Economic-flow observer slice passed.
- No active runtime value was introduced.

Atlas/signing state:

- Signed v0.1 remains unchanged.
- v0.2 candidate remains unsigned at 41 nodes / 73 edges.
- v0.2 signing ceremony was deferred pending explicit signing authorization.

Updated RC2 gates:

- CDL-085 ratification is now unblocked for deliberation by prelock + runtime/economic
  observer evidence, but still not executed.
- v0.2 signing remains blocked only by explicit signing authorization.
- Tier-3 runtime linkage, fresh-CDL packaging-blocker evaluation, persistent rate limiter,
  and truth-primitive permanence community ratification remain open.
- Gossip observer slice remains deferred to Window 1183+.
