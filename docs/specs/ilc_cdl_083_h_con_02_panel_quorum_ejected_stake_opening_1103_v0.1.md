# CDL-083: H-CON-02 Panel Quorum Rules for Ejected Stake Treasury Distribution and REFUTATION Attribution

**Status:** OPEN
**Opened:** Phase 1103 (2026-04-28)
**Authority:** CDL-081 §4.5 (ejected stake → treasury, quorum required) / CDL-081 Q1
             (REFUTATION conditional, flow deferred) / CDL-046 (ejection mechanism) /
             CDL-V7 (Popperian gate upholds/rejects refutations) / epoch_state_runtime.py
             (canonical 2/3 quorum threshold)
**Blocks:** `CDL_HCON_02_DEPENDENCY` stub in
           `ilc_core/economics/epoch_attribution_settle_runtime.py` (active since Phase 946)

`cdl_083_open_phase_1103`

---

## 1. Problem Statement

CDL-081 established two deferred obligations that CDL-083 must resolve:

**1a — Ejected stake treasury distribution (CDL-081 §4.5):**
When a star node member is ejected via CDL-046 (timed-out lifecycle), their stake accumulates
in the star node treasury. CDL-081 §4.5 states explicitly: "ECU attribution from treasury
requires quorum governance (H-CON-02)." Without H-CON-02, the treasury is perpetually locked
— accumulated stake cannot be distributed.

**1b — REFUTATION edge attribution (CDL-081 Q1):**
CDL-081 Q1 declared REFUTATION attribution "conditional on CDL-V7 Popperian gate upholding
the refutation" but did not define the ECU flow for upheld refutations. Without H-CON-02,
upheld refutations produce no ECU — the incentive for legitimate refutation is broken.

Both gaps are enforced by the active stub in `epoch_attribution_settle_runtime.py`:
```python
CDL_HCON_02_DEPENDENCY = "h_con_02_cdl_required_before_ejected_stake_treasury_executes"

elif attr_event.edge_type == EdgeType.REFUTATION:
    raise NotImplementedError(CDL_HCON_02_DEPENDENCY)
```

CDL-083 resolves both obligations in a single constitutional action.

---

## 2. Human-Gate Decisions — All Resolved (Phase 1103, pre-authorized 2026-04-28)

### Q1 — Panel quorum participation floor (RESOLVED)

**≥0.50 of remaining star node members must cast a vote; hard minimum of 2 participating
voters regardless of group size.**

Rationale: The fractional floor (≥0.50) scales naturally with group size. The absolute
minimum of 2 prevents a single remaining member from unilaterally self-authorizing treasury
release. For groups of 3+, the fractional floor dominates. This is consistent with the
canonical 2/3 consensus threshold in `epoch_state_runtime.py` — participation floor is the
lower bar, agreement threshold is the higher bar.

`q1_quorum_floor_geq_050_hard_minimum_2_voters`

---

### Q2 — Vote threshold (RESOLVED)

**At least exact 2/3 of participating voters must agree to release ejected stake.**

Rationale: Canonical ILC consensus threshold. `epoch_state_runtime.py` encodes
`quorum_threshold: {"numerator": 2, "denominator": 3}` as the standard. The 7+1 knowledge-claim
panel uses 5/7 ≈ 71%, also ≥2/3. Supermajority protects against a bare majority of remaining
members gaming the treasury after a targeted ejection.

Implementation note: this threshold must be evaluated with integer arithmetic
(`approve_votes * 3 >= participating_voters * 2`), not by comparing against
`Decimal("0.67")`. The decimal approximation would incorrectly reject exact
2-of-3, 4-of-6, and 6-of-9 approvals.

`q2_vote_threshold_exact_two_thirds_supermajority`

---

### Q3 — Distribution formula (RESOLVED)

**Released ejected stake is distributed proportionally to the current stake of all remaining
members at the distribution epoch — not restricted to approving voters.**

Rationale: Consistent with CDL-081 §4.2 CO_AUTHORSHIP split formula (`stake_i(t) / Σ_j
stake_j(t)` — stake at epoch t, not vote-weighted). Restricting distribution to approving
voters creates a perverse incentive to vote yes regardless of merit (vote yes → get treasury
share). Distributing to all remaining members separates the governance decision (vote) from
the economic outcome (distribution formula), which is cleaner and harder to game. The
supermajority threshold (Q2) provides the necessary protection against bad-faith approvals.

`q3_distribution_proportional_all_remaining_members_stake_at_distribution_epoch`

---

### Q4 — REFUTATION ECU flow (RESOLVED)

**When CDL-V7 Popperian gate upholds a refutation, the refuting agent receives
`REUSE_ATTRIBUTION_RATE` (Decimal("0.20")) sourced from the epoch mint budget.**

**Caller-filter rule:** Upheld refutation events are identified by the caller before being
added to the `EpochAttributionBatch`. `settle()` receives only upheld REFUTATION events — no
`upheld: bool` field on `AttributionEvent`. A REFUTATION event in the batch is by construction
upheld. Non-upheld refutations are filtered before batch entry.

Rationale: `REUSE_ATTRIBUTION_RATE = Decimal("0.20")` is the canonical attribution rate for
epistemic engagement (CDL-081 Q6, SIM-REUSE-01). Upheld refutation is an epistemic
contribution of comparable magnitude to REUSE. No new constant needed. Source is epoch mint
(same as REUSE attribution) — not extracted from the refuted agent's stake, which is a
separate reputational channel governed by CDL-V7.

Implementation note: the settlement event must identify the refuting agent as
the payout recipient. The existing `target_creator_id` field is REUSE-oriented
terminology; the REFUTATION path must not accidentally pay the creator of the
refuted target. The runtime event shape must therefore add an explicit
`refuting_agent_id` field or an equivalent explicit recipient field before the
REFUTATION path is activated.

`q4_refutation_ecu_reuse_attribution_rate_epoch_mint_source_caller_filters_upheld`

---

### Q5 — Ejected stake recovery on readmission (RESOLVED)

**Ejected stake is irrevocable. An agent readmitted via CDL-058 re-admission boundary starts
with zero stake. No retroactive recovery of treasury share.**

Rationale: Allowing recovery creates a "stake-hostage" exploit — ejected agent accumulates
stake, deliberately goes inactive, gets ejected, waits out CDL-058 cooldown, re-admits, claims
treasury. The larger the treasury, the more attractive the exploit. CDL-046 ejection is for
liveness failure; readmission is a fresh start. No Canon basis authorizes retroactive recovery.

`q5_ejected_stake_irrevocable_readmission_starts_fresh`

---

## 3. Ratified Constitutional Text

### §5.1 Panel quorum participation floor

A treasury distribution vote on a star node's ejected stake is valid only if:
- At least `HCON02_QUORUM_FLOOR` (= 0.50) of the remaining active members cast a vote, AND
- At least `HCON02_QUORUM_MINIMUM_VOTERS` (= 2) members cast a vote.

If either condition is unmet, the vote is invalid and the treasury remains locked. A new vote
may be called in a subsequent epoch.

### §5.2 Vote threshold

A distribution decision is approved only if exact integer comparison shows at least 2/3 of the
participating voters voted to approve:

```
approve_votes * HCON02_VOTE_THRESHOLD_DENOMINATOR
    >= participating_voters * HCON02_VOTE_THRESHOLD_NUMERATOR
```

Abstentions do not count toward the threshold denominator.

### §5.3 Distribution formula

On approval, the released ejected stake is distributed among all remaining active star node
members proportionally to their current stake at the distribution epoch:

```
share_i = released_stake × (stake_i(t_dist) / Σ_j stake_j(t_dist))
```

where `t_dist` is the epoch at which the distribution is executed. All remaining members
receive a share regardless of their vote direction.

### §5.4 REFUTATION attribution

When a REFUTATION event appears in an `EpochAttributionBatch`, it is by construction upheld
by the CDL-V7 Popperian gate (caller-filter rule, Q4). The refuting agent receives:

```
attribution_ECU = REUSE_ATTRIBUTION_RATE  (= Decimal("0.20"))
```

sourced from the epoch mint budget, following the same settlement path as CDL-081 §4.1 REUSE
attribution. The refuted agent's stake and reputation are governed separately by CDL-V7 and
are not affected by this attribution.

### §5.5 Ejected stake irrevocability

Ejected stake transferred to the star node treasury is irrevocable. An agent who is
subsequently readmitted via CDL-058 re-admission boundary acquires no claim to treasury stake
accumulated from their prior ejection. Readmission starts with zero stake.

---

## 4. Implementation Targets

### 4.1 New constants (to be added at ratification — Phase 1105 Commit 1)

In `ilc_core/economics/epoch_attribution_settle_runtime.py`:

```python
HCON02_QUORUM_FLOOR = Decimal("0.50")          # Q1: ≥50% of remaining members must vote
HCON02_QUORUM_MINIMUM_VOTERS = 2               # Q1: hard minimum regardless of group size
HCON02_VOTE_THRESHOLD_NUMERATOR = 2             # Q2: exact 2/3 supermajority
HCON02_VOTE_THRESHOLD_DENOMINATOR = 3           # Q2: exact 2/3 supermajority
CDL_083_DEPENDENCY = "cdl_083_h_con_02_ratified_1105.v0.1"
```

### 4.2 REFUTATION path replacement

Replace in `settle_attribution_batch()`:
```python
elif attr_event.edge_type == EdgeType.REFUTATION:
    raise NotImplementedError(CDL_HCON_02_DEPENDENCY)
```

With:
```python
elif attr_event.edge_type == EdgeType.REFUTATION:
    # §5.4 Upheld REFUTATION attribution — caller-filter guarantees this is upheld.
    recipient_id = attr_event.refuting_agent_id  # explicit recipient; do not pay refuted creator
    if recipient_id in visited_set:
        continue
    visited_set.add(recipient_id)
    payouts.append((recipient_id, REUSE_ATTRIBUTION_RATE))
```

Note: The `CDL_HCON_02_DEPENDENCY` constant is retained as a historical marker token —
only the `raise NotImplementedError` call is removed.

Event-shape guard: Phase 1105/1106 must not overload `target_creator_id` as the
REFUTATION payout recipient. Add `refuting_agent_id` (or an equivalent explicit
recipient field) and test that the refuted target creator is not paid.

### 4.3 Runtime version token update

```python
EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION = "epoch_attribution_settle_runtime_1106.v0.2"
```

### 4.4 Optional: panel_quorum_runtime.py

If ejected stake distribution vote logic is extracted to a separate module:
`ilc_core/economics/panel_quorum_runtime.py`

This is implementation-discretion. The quorum constants and distribution formula must be
consistent with §5.1–5.3 regardless of module structure.

---

## 5. What This CDL Does NOT Constitute

- PROVENANCE chain attribution (CDL-084, Window 1110+)
- Changes to CDL-V7 Popperian gate adjudication logic (CDL-052 scope)
- Treasury governance framework (CDL-047 scope)
- Star node adoption rules (CDL-081 §4.6 scope)
- Werner φ-bound on edge minting (separate CDL)
- Changes to CDL-046 ejection trigger conditions

---

## 6. Forward Obligations This CDL Unlocks

| Item | Dependency |
|------|-----------|
| REFUTATION attribution live in `settle()` | This CDL |
| Ejected stake distribution governance | This CDL |
| CDL-084: PROVENANCE chain attribution | This CDL (PROVENANCE silently ignored pending CDL-084) |

---

## 7. Prelock Record (Phase 1104)

**Introducing commit:** `da10991f`
**Introducing commit message:** `feat(cdl): open CDL-083 H-CON-02 panel quorum ejected stake (Phase 1103)`

**Prelock assertion:** CDL-083 confirmed OPEN at introducing commit `da10991f`.

```bash
git show da10991f:docs/specs/ilc_cdl_083_h_con_02_panel_quorum_ejected_stake_opening_1103_v0.1.md \
  | grep "^\*\*Status:"
# Result: **Status:** OPEN ✓
```

**Evidence document:** `docs/specs/ilc_cdl_083_h_con_02_ratification_evidence_1104_v0.1.md`

`cdl_083_prelock_asserts_open_at_phase_1103_commit_da10991f`
`cdl_083_prelock_hardening_complete_phase_1104`

---

## 8. Ratification Gate (Pre-Ratification)

- [x] Prelock hardening complete — Phase 1104 — §7 above
- [x] Ratification evidence document (≥10 tests) — Phase 1104
- [ ] Phase 1105 Commit 1: runtime constants + REFUTATION path implemented
- [ ] Phase 1105 Commit 2: CDL-083 OPEN → RATIFIED; log row updated
- [ ] Human ratification authorization — Phase 1105

---

`cdl_083_open_phase_1103`
`h_con_02_ejected_stake_and_refutation_attribution_constitutional_basis_opening`
`q1_q2_q3_q4_q5_all_resolved_at_opening`
`cdl_hcon_02_dependency_stub_target_identified`
