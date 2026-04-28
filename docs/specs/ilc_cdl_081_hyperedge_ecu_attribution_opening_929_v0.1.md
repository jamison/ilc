# CDL-081: Hyperedge ECU Attribution

**Status:** RATIFIED
**Opened:** Phase 929 (2026-04-28)
**Ratified:** Phase 943 (2026-04-28)
**Authority:** ADR-0029 (hypergraph substrate, accepted); ADR-0015 (leasehold/reversion, canon)
**Supersedes:** `docs/specs/ilc_hcon_01_hyperedge_ecu_attribution_opening_draft_v0.1.md` (H-CON-01 draft)
**Blocks:** H-012 (star expansion implementation), H-CON-02 (panel hyperedge quorum rules),
           REUSE edge traversal runtime, Hyperedge ECU attribution runtime

---

## 1. Problem Statement

ILC has no constitutional rule governing how ECU flows when a hyperedge is traversed
or reused. Without this CDL:

- CO_AUTHORSHIP star-expanded nodes cannot be created — they accumulate ECU but
  there is no ratified split function
- REUSE edges cannot trigger attribution — the target is undefined
- Star node member lifecycle (buy-in, exit, ejection) has no constitutional basis
- Zero-member (abandoned) star nodes have no defined disposition

This CDL constitutionalizes the attribution rules so that H-012 (star expansion)
and H-CON-02 (panel quorum) can proceed.

---

## 2. Human-Gate Decisions — All Resolved (Phase 929)

### Q1 — Edge type attribution triggers (RESOLVED)

| Edge type | Attribution trigger | Rationale |
|---|---|---|
| REUSE | **Yes** | Core revealed-preference signal; direct content consumption |
| CO_AUTHORSHIP (star-expanded) | **Yes** | Group output reuse; split per §4.2 |
| ATTESTATION | **No** | Vouching has no direct ECU; reputation flows instead |
| REFUTATION | **Conditional** | ECU flows only if refutation upheld by CDL-V7 Popperian gate |
| PROVENANCE | **Deferred to H-CON-02** | Chain attribution depth cap and α-decay governance belong in H-CON-02; PROVENANCE_MAX_DEPTH=3 and PROVENANCE_DECAY_ALPHA=0.5 are named provisional constants pending that CDL |
| EPOCH_BOUNDARY | **No** | Structural continuity marker only; attribution creates gaming incentives |

`q1_reuse_yes_co_authorship_yes_attestation_no_refutation_conditional_provenance_hcon02_epoch_boundary_no`

---

### Q2 — Minimum stake floor (RESOLVED)

No hard stake floor. A star node may have zero members (unowned/commons state).

When the last member leaves or is ejected, the node transitions to commons via the
ADR-0015 leasehold/reversion framework, routed through CDL-047 treasury governance.
The node continues to exist and be served; serving agents continue earning serving
fees (CDL-078). Creator attribution is suspended while unowned.

Any agent may adopt an unowned node by staking into it. Adoption is opt-in and
explicit (not automatic). On adoption, attribution resumes immediately flowing to
the adopting agent. There is no minimum stake amount for adoption — any positive
stake establishes membership.

The zero-member → commons transition is the same mechanism as ADR-0015 time-expiry
leasehold reversion. Both cases route to CDL-047 treasury governance. This prevents
graph-land feudalism: no node extracts unbounded rent by being early, and no content
is lost when a group dissolves.

`q2_no_stake_floor_zero_members_commons_transition_adr_0015_leasehold_cdl_047_routing`

---

### Q3 — Buy-in window (RESOLVED)

**Option C selected:** Post-creation stake in a star node is subject to CDL-V1
temporal decay from the buy-in epoch. No hard lockout window.

Late stake is naturally discounted: an agent staking one epoch before a large
attribution event receives near-zero benefit because their stake has barely aged.
Uses existing CDL-V1 machinery without a new governance rule.

`q3_option_c_decay_from_buy_in_epoch_no_hard_lockout`

---

### Q4 — Ejected stake disposition (RESOLVED)

**Option C selected:** On CDL-046 member ejection (timed-out lifecycle), the
ejected member's stake accumulates in the star node treasury. ECU attribution
from treasury requires quorum governance (H-CON-02).

Burning destroys value (rejected). Redistribution among remaining members can be
gamed by deliberate ejection of weak members (rejected). Treasury accumulation is
neutral and separates the ejection event from the attribution decision.

`q4_option_c_ejected_stake_treasury_accumulation_hcon02_quorum_required`

---

### Q5 — REUSE attribution target (RESOLVED)

**Option A selected:** ECU flows entirely to the creator of the target node.
The edge creator (consuming agent) is not rewarded. There is no free lunch:
content producers are rewarded for quality that attracts reuse; consumers
are not double-paid for consuming.

Serving agents earn their serving fee (Wire Protocol layer, CDL-078 framework)
independently. Creator attribution and serving fee are additive and completely
independent — creator is agnostic to who serves and at what price.

`q5_option_a_target_node_creator_receives_ecu_no_consumer_reward`

---

### Q6 — Per-traversal ECU rate (RESOLVED — SIM-REUSE-01)

**`REUSE_ATTRIBUTION_RATE = 0.20`** — resolved by SIM-REUSE-01 (Phase 940-941).

SIM-REUSE-01 evidence document:
`docs/specs/ilc_sim_reuse_01_attribution_rate_results_synthesis_941_v0.1.md`

Key findings establishing this decision:
- **Floor at 0.10**: rate=0.05 fails creation-rate target (8.43% vs >=25%) and
  produces severe inequality (Gini=0.874). Rate=0.10 is the minimum that passes all
  three calibration targets simultaneously.
- **0.20 preferred over 0.10**: 82.3% creation rate + Gini=0.197 vs 59.1% at 0.10.
  The marginal attribution cost of the 0.10 to 0.20 step is small.
- **0.20 preferred over 0.25+**: Gini at 0.25+ (<=0.11) risks erasing the epistemic
  quality gradient. CDL-081 §4.1 should be conservative at ratification.
- **Gaming non-attractive by construction**: gaming_roi_ratio < 0.02 at all tested
  rates. Rate parameter choice does not determine gaming resistance.

`REUSE_ATTRIBUTION_RATE = 0.20` applies to CO_AUTHORSHIP and REUSE edge types (Q1).
ATTESTATION excluded (Q1). REFUTATION conditional (CDL-V7). PROVENANCE deferred (H-CON-02).

Constitutional note: `ilc_core/types.py` must be updated from `None` to
`Decimal("0.20")` only after CDL-081 ratification (ILC_CDL_MUTATION_AUTHORIZED=1 required).

`q6_resolved_reuse_attribution_rate_0_20_sim_reuse_01_evidence`
`sim_reuse_01_complete_phase_941`
`gaming_structurally_non_attractive_validated`
`reuse_attribution_floor_confirmed_at_0_10`

---

## 3. Ratified Constitutional Text

### §4.1 REUSE edge attribution

When a `REUSE` edge is traversed in epoch `t`, the creating agent of the target
node receives:

```
attribution_ECU = REUSE_ATTRIBUTION_RATE  (= 0.20 per SIM-REUSE-01; locked post-ratification)
```

Attribution is batched per epoch via `EpochAttributionBatch` (CDL-078 temporal
batching pattern) and settled at epoch finalization. Each event in the batch is
processed with a fresh `visited_set`; no cross-event state contamination.

Clearance (signed traversal commitment at WANT-BLOCK delivery time, Wire Protocol
layer, sub-30ms over QUIC/CDL-061) is distinct from settlement (epoch-final ECU
transfer, Epoch State layer). Clearance records carry `epoch_tag` at signing time;
late-arriving records become epoch+1 obligations. Settlement never retroactively
reopens a closed epoch.

### §4.2 CO_AUTHORSHIP star node attribution

When a `CO_AUTHORSHIP` star-expanded node is reused in epoch `t`:

```
ECU_i = total_ECU_attributed × (stake_i(t) / Σ_j stake_j(t))
```

Where `stake_j(t)` is member `j`'s stake at epoch `t` (dynamic, not frozen at
creation). Minimum: at least one member in the denominator set. If zero members:
§4.6 commons transition applies.

### §4.3 Edge type attribution scope

Per Q1: REUSE and CO_AUTHORSHIP trigger attribution. ATTESTATION and EPOCH_BOUNDARY
do not. REFUTATION is conditional on CDL-V7 Popperian gate upholding the refutation.
PROVENANCE attribution is deferred to H-CON-02. `PROVENANCE_MAX_DEPTH = 3` and
`PROVENANCE_DECAY_ALPHA = 0.5` are provisional constants; CDL required to change them.

### §4.4 Buy-in and decay

Post-creation stake in a star node is subject to CDL-V1 temporal decay from the
buy-in epoch. No hard lockout window. An agent staking N epochs after creation
receives stake that has decayed from the buy-in epoch forward — late stake is
naturally discounted without a new governance rule.

### §4.5 Ejection fallback

On CDL-046 member ejection, ejected stake accumulates in star node treasury.
ECU attribution from treasury requires quorum governance (H-CON-02). This CDL
does not resolve treasury distribution — that is H-CON-02 scope.

### §4.6 Zero-member commons transition

When the last member leaves or is ejected, the star node transitions to commons:

1. Node continues to exist and be routable via CDL-080 star.map index
2. Serving agents continue earning serving fees (CDL-078) — unaffected
3. Creator attribution is suspended (denominator is empty; formula does not execute)
4. ECU that would have been attributed accumulates in the CDL-047 treasury
5. Any agent may adopt the node by staking a positive amount into it
6. On adoption, the adopting agent becomes sole member; attribution resumes immediately
7. Adoption is explicit and opt-in — not automatic transfer to any serving agent

The zero-member → commons transition is constitutionally equivalent to ADR-0015
time-expiry leasehold reversion. Both route through CDL-047 treasury governance.

`cdl_047_governs_commons_attribution_accumulation`
`adr_0015_leasehold_reversion_commons_transition_equivalent`
`adoption_is_opt_in_any_agent_any_positive_stake`

---

## 4. What This CDL Does NOT Constitute

- Per-traversal ECU rate — RESOLVED: 0.20 (SIM-REUSE-01 Phase 941); types.py update pending ratification
- PROVENANCE chain attribution rules (H-CON-02)
- Panel hyperedge quorum rules (H-CON-02)
- Werner φ-bound on edge minting (separate CDL, `EDGE_MINT_PHI_BOUND = None`)
- Ensemble/ContentPackage governance (future CDL; "content_package" hyperedge
  type is reserved in proto and types.py as a forward reservation)
- Operator serving fee structure (Wire Protocol layer; not Protocol Bundle)
- Sigmoid traversal fee parameters (deferred; SIM-REUSE-01 calibrated flat rate only)

---

## 5. Forward Obligations This CDL Unlocks

| Item | Dependency |
|------|-----------|
| H-012: Star expansion implementation | This CDL |
| H-CON-02: Panel hyperedge quorum rules | This CDL |
| REUSE edge traversal runtime | This CDL + SIM-REUSE-01 |
| Hyperedge ECU attribution runtime | This CDL |
| Werner edge-minting CDL | This CDL (φ-bound interacts with §4.1 rate) |
| SIM-REUSE-01 commissioning | This CDL (defines what SIM must calibrate) |

---

## 6. Ratification Gate (Pre-Ratification)

Before CDL-081 can be ratified, the following must be complete:

- [x] SIM-REUSE-01 calibration complete — `REUSE_ATTRIBUTION_RATE = 0.20` (Phase 941)
- [x] `REUSE_ATTRIBUTION_RATE` constant updated to `Decimal("0.20")` in `ilc_core/types.py` (Phase 943)
- [x] Ratification evidence document — 30 tests, all pass (Phase 942)
- [x] H-012 attribution runtime — DEFERRED; forward obligation recorded in §5
- [x] H-CON-02 — DEFERRED; forward obligation recorded in §5
- [x] Human ratification authorization — granted Phase 943

---

## 7. Code Already in Place

| Item | Location | Commit |
|------|----------|--------|
| EdgeType enum | `ilc_core/types.py` | f69a87da |
| WeightParams dataclass | `ilc_core/types.py` | f69a87da |
| HyperEdge with edge_type + edge_payload | `ilc_core/types.py` | f69a87da |
| compute_weight() provisional | `ilc_core/analysis/spectral_utils.py` | f69a87da |
| EpochAttributionBatch stub | `ilc_core/types.py` | d40c458a |
| REUSE_ATTRIBUTION_RATE = None | `ilc_core/types.py` | d40c458a |
| EDGE_MINT_PHI_BOUND = None | `ilc_core/types.py` | d40c458a |
| PROVENANCE_MAX_DEPTH = 3 | `ilc_core/types.py` | d40c458a |
| PROVENANCE_DECAY_ALPHA = 0.5 | `ilc_core/types.py` | d40c458a |
| STAR_NODE_MIN_STAKE_ECU = Decimal("1") | `ilc_core/types.py` | d40c458a |
| ClearanceRecord proto reservation | `ilc_consensus/proto/ilc_app.proto` | d40c458a |
| "content_package" hyperedge_type reserved | `ilc_core/types.py` + proto | d40c458a |

`cdl_081_open_phase_929`
`hyperedge_ecu_attribution_constitutional_basis_established`
`h_012_h_con_02_sim_reuse_01_now_unblocked`
`commons_transition_via_adr_0015_cdl_047_no_separate_treasury_mechanism_needed`
