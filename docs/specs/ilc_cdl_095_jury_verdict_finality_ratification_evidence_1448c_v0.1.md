# CDL-095 Ratification Evidence — Phase 1448c

**CDL number:** CDL-095  
**Title:** Jury Verdict Finality and Escalation Architecture  
**Ratified phase:** 1448c  
**Ratified date:** 2026-05-25  
**Ratification token:** `cdl_095_ratified_phase_1448c`

---

## 1. Opening and deliberation record

CDL-095 was opened during the Phase 1448a pre-publication review session. The jury system (J-series, Phase 1427 PASS) was production-ready but lacked constitutionally defined verdict finality semantics. This was identified as a governance gap that must be closed before external participants are exposed to the protocol via public RC push (Phase 1448b).

The opening document underwent four rounds of review:
- Round 1 (Sonnet): Fixed sequencing error, P=3 rejection, CDL-013 blocked dependency, PUBLIC_RC_EXCLUDE marker, Phase 1449 conflict
- Round 2 (Codex second-reviewer): Fixed overbroad "juries produce verdicts" framing, abstain mislabeled as non-response
- Round 3 (Codex third-reviewer): Fixed Q3 human-decision wording, CDL-027 citation × 2 (→ ADR-0025), global-tier contradiction with CDL-096 deferral, verdict schema completeness
- Round 4 (Codex fourth-reviewer): Fixed implementation map path, resolved abstain compensation default, marked interim fallback NOT ratified, corrected Q6 framing

Human confirmation of Q1–Q6: received 2026-05-25.

---

## 2. Scope constants locked (prelock token: `cdl_095_scope_constants_locked_phase_1448c`)

```python
# CDL-095: Jury Verdict Finality and Escalation Architecture
CDL_095_JURY_VERDICT_FINALITY_VERSION = "cdl_095_jury_verdict_finality_v0.1"

# Q1 — Local verdict threshold (integer arithmetic, CDL-083 consistent)
JURY_VERDICT_APPROVE_NUMERATOR = 2
JURY_VERDICT_APPROVE_DENOMINATOR = 3
JURY_VERDICT_PARTICIPATION_FLOOR = 5          # of 7 regular reviewers
JURY_ABSTAIN_EARNS_BASE_FEE = True
JURY_ABSTAIN_EARNS_ACCURACY_BONUS = False

# Q3 — Escalation constants
JURY_PETITION_WINDOW_VALIDATION_EPOCHS = 1440  # ≈24 hours at 1-min validation epoch (ADR-0025)
JURY_PETITION_BOND_MULTIPLIER = 3             # bond = 3× CDL-091 base review fee
JURY_AUTO_ESCALATION_HIGH_STAKES_TAG = "HIGH_STAKES"

# Q4 — Shard-tier panel
JURY_SHARD_PANEL_SIZE = 11
JURY_SHARD_PARTICIPATION_FLOOR = 7            # of 11
JURY_SHARD_COMPENSATION_MULTIPLIER = 2        # × CDL-091 base review fee
JURY_SHARD_ACTIVATION_STATUS = "ratified_not_activated"
JURY_SHARD_INTERIM_FALLBACK_SELECTION_STATUS = "deferred_to_shard_activation_gate"

# Q5 — Global tier
JURY_GLOBAL_TIER_ACTIVATION_STATUS = "deferred_to_cdl_096"

# Q2 — Relationship to epoch finality
JURY_VERDICT_BLOCKS_EPOCH_FINALITY = False    # two-track design
JURY_VERDICT_REQUIRED_FOR_T_FINAL = True      # T1+ cannot advance without finalized_local+
```

---

## 3. Ratification decisions

| Q | Confirmed decision |
|---|-------------------|
| Q1 | Exact 2/3 integer arithmetic; regular-reviewer-only; non-response excluded from denominator; abstain counted in denominator, not approve_votes; abstain earns base fee, no accuracy-weighted bonus |
| Q2 | Two-track separation accepted; jury finality ≠ consensus finality; absence of jury verdict record does not block epoch finalization |
| Q3 | Three-path escalation accepted (petition Path A, auto HIGH_STAKES Path B, diversity fail Path C); P=1440 validation epochs; B=3× CDL-091 base fee |
| Q4 | 11-member shard panel; k≥7 participation floor; exact 2/3 threshold; 2× CDL-091 base fee; deferred activation; interim fallback panel-selection NOT ratified — deferred to shard activation gate phase |
| Q5 | Full deferral to CDL-096; no constants, panel size, bond amounts, or design sketch in CDL-095 |
| Q6 | CDL-095 ratification is a prerequisite for Phase 1448b; Phase 1448b may not execute without this ratification token |

---

## 4. Non-authorization floor

This ratification does NOT:
- Activate shard-tier review
- Activate global-tier review
- Change the Phase 1427 J-008 production jury activation verdict
- Amend CDL-051 (validator epoch finality unchanged)
- Amend CDL-083 (H-CON-02 panel quorum unchanged)
- Activate claim state advancement machinery (`T1+` → `T_final`)
- Implement `jury_finality_evaluator.py` or the verdict record schema
- Push any code to a public repository
- Ratify an interim fallback panel-selection method for shard-tier activation

---

## 5. What this ratification enables (unblocked runtime phases)

1. `jury_finality_evaluator.py` — implement `evaluate_jury_verdict_finality()` mirroring `finality_evaluator.py`'s threshold machinery but consuming jury verdict records
2. `jury_verdict_record` schema — define the typed epoch-state entry
3. `jury_petition` node type — petition filing and bond handling
4. Shard-tier panel selection — extend `jury_assignment_runtime.py` for shard-scope pool (deferred activation; fallback selection method separately gated)

---

## 6. Prerequisites satisfied

| Prerequisite | Verified |
|---|---|
| CDL-051 epoch finality ratified (Phase 443) | Yes — `finality_evaluator.py:FINALITY_EVALUATOR_VERSION = "finality_evaluator_445.v0.1"` |
| CDL-083 H-CON-02 panel quorum (Phase 1105) | Yes — `HCON02_VOTE_THRESHOLD_NUMERATOR = 2`, `HCON02_VOTE_THRESHOLD_DENOMINATOR = 3` |
| CDL-V3 cluster diversity floor (Phase 397/470) | Yes — `diversity_floor_runtime.py` active |
| CDL-091 jury incentive economics (Phase 1400) | Yes — `cdl_091_ratified_phase_1400` |
| J-008 production jury activation gate (Phase 1427) | Yes — PASS |

---

## 7. Gate compliance checklist

- [x] PUBLIC_RC_EXCLUDE marker removed from ratified document
- [x] Status updated from OPEN to RATIFIED
- [x] Opening, prelock, and ratification tokens recorded in document header
- [x] CDL register row added
- [x] Phase 1448b prerequisite recorded in checklist blocking items
- [x] Scope constants block updated with `JURY_ABSTAIN_EARNS_BASE_FEE`, `JURY_ABSTAIN_EARNS_ACCURACY_BONUS`, `JURY_SHARD_INTERIM_FALLBACK_SELECTION_STATUS`
- [x] Ratification evidence document committed with `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1448c`
