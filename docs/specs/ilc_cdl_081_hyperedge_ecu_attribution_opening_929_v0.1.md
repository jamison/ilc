# CDL-081: Hyperedge ECU Attribution

**Status:** OPEN
**Opened:** Phase 929 (2026-04-28)
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

### Q6 — Per-traversal ECU rate (RESOLVED)

**Deferred to SIM-REUSE-01.** No floor or ceiling pre-committed.

`REUSE_ATTRIBUTION_RATE = None` is the named provisional constant in
`ilc_core/types.py`. SIM-REUSE-01 must model:
- All three bootstrap phases simultaneously
- Clearance vs settlement timing interaction
- Werner φ-bound interaction (edge minting ≤ φ × node minting per epoch;
  `EDGE_MINT_PHI_BOUND = None` pending Werner CDL)
- Reputation-implicit signal (reuse_count routing preference) vs direct ECU
  transfer per traversal — whether both are needed or reuse_count alone suffices

`q6_deferred_to_sim_reuse_01_reuse_attribution_rate_none_pending`

---

## 3. Ratified Constitutional Text

### §4.1 REUSE edge attribution

When a `REUSE` edge is traversed in epoch `t`, the creating agent of the target
node receives:

```
attribution_ECU = REUSE_ATTRIBUTION_RATE  (rate from SIM-REUSE-01; currently None)
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

- Per-traversal ECU rate (SIM-REUSE-01 pending)
- PROVENANCE chain attribution rules (H-CON-02)
- Panel hyperedge quorum rules (H-CON-02)
- Werner φ-bound on edge minting (separate CDL, `EDGE_MINT_PHI_BOUND = None`)
- Ensemble/ContentPackage governance (future CDL; "content_package" hyperedge
  type is reserved in proto and types.py as a forward reservation)
- Operator serving fee structure (Wire Protocol layer; not Protocol Bundle)
- Sigmoid traversal fee parameters (SIM-REUSE-01 pending)

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

- [ ] SIM-REUSE-01 calibration complete — per-traversal ECU rate determined
- [ ] `REUSE_ATTRIBUTION_RATE` constant updated from None to calibrated value
- [ ] Ratification evidence document (≥20 tests across attribution rules)
- [ ] H-012 attribution runtime implemented and tested
- [ ] H-CON-02 opened (or explicitly deferred with forward obligation recorded)
- [ ] Human ratification authorization

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
