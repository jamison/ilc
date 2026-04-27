# H-CON-01: Hyperedge ECU Attribution — Opening Draft

**Status:** DRAFT — awaiting human authorization to open as CDL
**Prepared:** Phase 928 (2026-04-28)
**Constitutional authority:** Requires new CDL (number TBD)
**Prerequisites:** ADR-0029 accepted; SIM-REUSE-01 positive result
**Blocks:** Star expansion implementation (H-012), panel quorum rules (H-CON-02)

---

## 1. Problem Statement

ILC currently has no constitutional rule governing how ECU flows when a
hyperedge is traversed or reused. Without this rule:
- Star-expanded hyperedge nodes (`Node(type="hyperedge_entity")`) cannot be
  created — they accumulate ECU but there is no ratified split function
- `REUSE` edges cannot trigger attribution — the target is undefined
- `CO_AUTHORSHIP` star nodes cannot distribute ECU — the proportionality rule
  is undefined
- `PROVENANCE` chain attribution has no legal basis

This CDL constitutionalizes the attribution rules so that H-012 (star expansion)
and H-CON-02 (panel quorum) can proceed.

---

## 2. Options Considered

### Option A — Flat equal split among all member agents

When a CO_AUTHORSHIP star node is reused, ECU is split equally among all
member agents regardless of stake.

**Recommendation: REJECT.**

Flat split ignores the stake signal — an agent who contributed 1 ECU gets the
same attribution as one who contributed 100 ECU. This destroys the incentive
to stake deeply in valuable group outputs. It also cannot accommodate buy-in
or exit after creation (all members are equal by definition).

`option_a_rejected_destroys_stake_signal`

---

### Option B — Proportional by stake at attribution time (RECOMMENDED)

ECU attribution to member agent `i` at attribution time `t`:

```
ECU_i = total_ECU_attributed × (stake_i(t) / Σ_j stake_j(t))
```

Where `stake_i(t)` is agent `i`'s current stake in the star node at epoch `t`.
Stake is dynamic: agents may buy in or exit after creation (subject to §4.4
constraints). Attribution always reflects the current stake distribution, not
the founding stake.

**Recommendation: ACCEPT.**

- Preserves stake-as-signal: high-stake agents earn proportionally more
- Allows secondary markets in star node stake (buy into successful group outputs)
- Consistent with CDL-V1 temporal decay framework (stake is already epoch-tracked)
- `ECU_i` is a pure function of committed on-chain state — auditable
- Empty denominator is impossible if minimum stake floor enforced (§4.4)

`option_b_selected_proportional_by_stake_at_attribution_time`

---

### Option C — Proportional by stake at creation time (frozen shares)

Same formula as B but `stake_i` is frozen at epoch_created, not updated.

**Recommendation: REJECT.**

Frozen shares mean early stakers cannot exit and late stakers cannot buy in.
This reduces liquidity and creates a coordination problem: agents must decide
final stake before the star node's value is known. Option B's dynamic stake
model is strictly superior.

`option_c_rejected_frozen_shares_reduce_liquidity`

---

### Option D — Attribution to star node only (deferred split)

All ECU attributed to the star node's treasury; individual agents claim via
a separate governance process.

**Recommendation: REJECT for primary attribution; KEEP as fallback.**

Individual claims against a shared treasury create governance overhead and
delay attribution. However, if agent ejection (CDL-046) leaves a star node
with no active members, ECU should accumulate in the star node treasury
pending quorum resolution. This is the §4.5 ejection fallback.

`option_d_rejected_as_primary_keep_as_ejection_fallback`

---

## 3. Open Questions for Human Decision

### Q1 — Which edge types trigger ECU attribution?

**Context:** Not all edge traversals should trigger attribution. Structural
edges (`EPOCH_BOUNDARY`) exist only for Laplacian continuity. Attribution on
structural edges would create gaming incentives.

**Options:**

| Edge type | Attribution trigger | Rationale |
|---|---|---|
| REUSE | Yes | Core revealed-preference signal; direct content consumption |
| CO_AUTHORSHIP (star-expanded) | Yes | Group output reuse; split per Option B |
| ATTESTATION | No (reputation only) | Vouching has no direct ECU; reputation → future earning |
| REFUTATION | Conditional | ECU flows only if refutation is upheld by CDL-V7 Popperian gate |
| PROVENANCE | Partial (TBD) | Chain attribution creates unbounded recursion without a depth cap |
| EPOCH_BOUNDARY | No | Structural only; gaming risk |

**My recommendation:** REUSE=yes, CO_AUTHORSHIP=yes, ATTESTATION=no,
REFUTATION=conditional (CDL-V7 gate), PROVENANCE=defer to H-CON-02,
EPOCH_BOUNDARY=no.

**Your decision needed:** Confirm PROVENANCE chain attribution scope. Full
chain (all ancestors share) vs. immediate parent only vs. capped depth (e.g.,
max 3 hops). Unbounded chain = infinite recursion risk; immediate parent only
= ignores deep provenance; capped depth = clean but arbitrary.

---

### Q2 — What is the minimum stake floor for star node membership?

**Context:** Option B's denominator requires Σ stake_j > 0 always.
A floor prevents zero-stake free-riders and ensures the denominator is
never empty after ejection.

**Options:**
- A: 1 ECU (minimal, accessible to all agents)
- B: Some fraction of the node's total stake at creation (e.g., 1% of total)
- C: The same minimum stake as required for validator participation (CDL-055)

**My recommendation:** Option A (1 ECU floor) for accessibility, with a
distinct protocol rule that if all members fall below floor, star node enters
"dormant" mode and ECU accumulates in the star node treasury (Option D
fallback from §2).

**Your decision needed:** Minimum stake floor value and dormancy trigger.

---

### Q3 — What is the maximum post-creation buy-in window?

**Context:** Unlimited buy-in lets agents observe a star node's success and
buy in just before a large attribution event — a form of front-running.

**Options:**
- A: No limit (open market — simplest, maximum liquidity)
- B: Buy-in only within N epochs of creation (lockout after N)
- C: Buy-in at any time but stake subject to CDL-V1 decay from buy-in epoch
  (late stake is worth less because it has had less time to decay)

**My recommendation:** Option C. Decay-from-buy-in naturally discounts late
stake without requiring a hard cutoff. An agent buying in one epoch before a
big attribution event gets almost no benefit because their stake has barely
aged. This uses existing CDL-V1 machinery without a new governance rule.

**Your decision needed:** Confirm Option C or select another.

---

### Q4 — What happens when a member agent is ejected (CDL-046 timed-out lifecycle)?

**Context:** CDL-046 defines timed-out lifecycle. If a member agent times out,
their stake in the star node is released. The denominator shrinks.

**Options:**
- A: Ejected stake redistributed proportionally among remaining members
- B: Ejected stake burns (removed from star node)
- C: Ejected stake accumulates in star node treasury (Option D fallback)

**My recommendation:** Option C. Burning destroys value (bad for remaining
members). Redistribution is a windfall that could be gamed (eject weak members
deliberately). Treasury accumulation is neutral and keeps the governance
decision separate from the ejection event.

**Your decision needed:** Ejected stake disposition.

---

### Q5 — Does REUSE attribution flow to the edge creator or the target node creator?

**Context:** A REUSE edge is created by the consuming agent (they declare that
they are reusing content). The target node was created by a different agent.
The planning doc's principle is: "attribution flows to the creator of the thing
being used, not to the creator of the edge."

**Options:**
- A: Target node creator receives ECU (content producer rewarded)
- B: Edge creator receives ECU (consumer rewarded for discovering and using content)
- C: Split between target creator and edge creator (e.g., 80/20)

**My recommendation:** Option A (target node creator). The edge creator is
already performing a reuse action that benefits them (they get the content).
Double-paying the consumer removes the incentive gradient: content creators
should be rewarded for quality that attracts reuse, not consumers for
consuming. Option C is a governance compromise that adds complexity without
a clear theoretical basis.

**Your decision needed:** Confirm Option A or select split ratio for Option C.

---

### Q6 — What is the per-traversal ECU amount for REUSE attribution?

**Context:** When a REUSE edge is traversed, how much ECU flows? Flat rate?
Fraction of content producer's stake? Fraction of consumer's action cost?

**Options:**
- A: Flat rate per traversal (e.g., 0.001 ECU) — simple, but not stake-aware
- B: Fraction of content node's current net_stake (e.g., 0.1% of net_stake)
- C: Fraction of validator block reward (linked to monetary policy)
- D: Defer to SIM-REUSE-01 — do not lock until simulation validates

**My recommendation:** Option D (defer to SIM-REUSE-01). The per-traversal
amount interacts directly with Laplacian dynamics and gaming resistance.
SIM-REUSE-01 must validate the `reuse_count` functional form first; the ECU
rate should be calibrated in that same simulation.

**Your decision needed:** Confirm deferral to SIM-REUSE-01 or provide
a floor/ceiling range to constrain the simulation.

---

## 4. Recommended CDL Text (for ratification, pending Q1–Q6 resolution)

### 4.1 REUSE edge attribution

When a `REUSE` edge is traversed in epoch `t`, the creating agent of the
target node receives:

```
attribution_ECU = <rate from SIM-REUSE-01>
```

Attribution is batched per epoch and settled at epoch finalization.

### 4.2 CO_AUTHORSHIP star node attribution (Option B)

When a `CO_AUTHORSHIP` star-expanded node is reused in epoch `t`:

```
ECU_i = total_ECU_attributed × (stake_i(t) / Σ_j stake_j(t))
```

Where `stake_j(t)` is member `j`'s stake at epoch `t`. Minimum floor: §Q2 decision.

### 4.3 Attribution chain for edge types (pending Q1 decision)

Per §Q1 recommendation: REUSE and CO_AUTHORSHIP trigger attribution.
ATTESTATION, EPOCH_BOUNDARY do not. REFUTATION is conditional on CDL-V7 gate.
PROVENANCE deferred to H-CON-02.

### 4.4 Buy-in and decay (Option C from Q3)

Post-creation stake in a star node is subject to CDL-V1 temporal decay from
the buy-in epoch. No hard lockout window.

### 4.5 Ejection fallback (Option C from Q4)

On CDL-046 member ejection, ejected stake accumulates in star node treasury.
ECU attribution from treasury requires quorum governance (H-CON-02).

---

## 5. Forward Obligations This CDL Unlocks

| Item | Dependency |
|------|-----------|
| H-012: Star expansion implementation | This CDL |
| H-CON-02: Panel hyperedge quorum rules | This CDL |
| REUSE edge traversal runtime | This CDL + SIM-REUSE-01 |
| Hyperedge ECU attribution runtime | This CDL |

---

## 6. Human Gates Before CDL Can Open

- [ ] Q1: Edge type attribution trigger list confirmed
- [ ] Q2: Minimum stake floor value confirmed
- [ ] Q3: Buy-in window policy confirmed
- [ ] Q4: Ejected stake disposition confirmed
- [ ] Q5: REUSE attribution target confirmed
- [ ] Q6: Per-traversal ECU rate confirmed (or SIM-REUSE-01 deferral confirmed)
- [ ] ADR-0029 accepted (or explicitly bundled into this CDL's scope)
- [ ] Human authorization to open this as a numbered CDL

`h_con_01_draft_ready_for_human_review`
`six_open_questions_require_human_decision`
`option_b_proportional_stake_recommended`
