# Window 707-712 Guidance — Governance Minimization and Validator-Agent Identity

**Date:** 2026-04-17  
**For:** Codex (RC main track)  
**Status:** Pre-sequence-lock guidance — Codex must produce the Window 707-712 sequence lock as Phase 707

---

## 1. Where we are

Window 701-706 closed today (`cbe35b7a`). Capsule v4.5 is the live frontier doc.

**Open CDLs (all three target Window 707-712):**
- CDL-066 (Phase 694) — agent sender authorization; implementation closed `acfcfd2d`; constitutional ratification open
- CDL-017 (Phase 695) — bootstrap transition criteria and Genesis sunset triggers
- CDL-067 (Phase 696) — settlement-substrate governance vehicle

**Option B row status:**
- Rows 1-4: `runtime_closed`
- Row 5: `spec_closed_runtime_pending`
- Row 6: `closed`
- Row 7: `spec_closed_runtime_pending`
- Rows 8-9: `closed`

**Frozen boundaries (do not reopen):**
- Phase 576/581 read-only wallet boundary
- Phase 609 ECU/ILC/runtime separation
- Phase 612 two-form MVP gate requirement
- ADR-0028 Option D active posture
- CDL-062 remains unauthorized

---

## 2. Window 707-712 scope

This window has two coupled sub-lanes running in parallel:

### Sub-lane A: Governance minimization and CDL-066/067 ratification routing

**Primary constitutional targets:**
- CDL-066 ratification (Track A — validator agent sender authorization)
- CDL-067 ratification (settlement substrate governance vehicle)
- Governance minimization taxonomy: what governance is and is not in graph-native ILC

**CDL-066 / CDL-067 note:** These are the shorter ratification arcs. CDL-017
ratification does NOT happen in 707-712 — it happens at the Mysticeti
convergence window (§5.6 of the carry-forward program), which requires both
Codex constitutional text AND Gemini M-series implementation evidence. Window
707-712 produces the CDL-017 prelock evidence and design resolution only.

### Sub-lane B: Validator-Agent Identity and CDL-017 prelock

This is the deeper, longer sub-lane. The six constitutional questions below
**must be answered in conversation with the local reviewer (Sonnet) before
any Codex phase in this sub-lane begins.** They are not resolvable from code alone.

---

## 3. The six constitutional questions for CDL-017 prelock

These must all be answered and recorded before CDL-017 prelock work starts:

1. **ValidatorKey**: same BLS key as `AgentID`, or derived sub-key with provable linkage?
2. **Minimum ECU stake threshold**: what does SIM-VALIDATOR-01 need to show, and what's the floor?
3. **Reputation-weighted selection**: proportional to `ecu_score`, or threshold-based eligibility pool?
4. **Validation pools**: CDL-017 scope, or separate subsequent CDL?
5. **Topology assignment seed**: epoch-hash (public/predictable) or VRF (private/unpredictable)?
6. **CDL-V3 diversity floor**: does it extend to validator set composition? If yes, what is the diversity metric?

The authoritative design framing: validators ARE agents. `ValidatorID` eventually
maps to `AgentID`. Validator stake is ECU. Reputation extends the CDL-V chain.
Topology shuffles via jury-like machinery. These are the agreed premises —
the six questions above refine the implementation detail.

---

## 4. Required outputs for Window 707-712

| Output | Type | Notes |
|---|---|---|
| Window 707-712 sequence lock | Phase 707 | First phase; locks ordering and pass criteria |
| Q1-Q6 answers recorded | Conversation artifact | `docs/research/ilc_validator_agent_design_evidence_v0.1.md` |
| SIM-VALIDATOR-01 commissioned | Research phase | Stake floor renders equivocation economically irrational |
| SIM-TOPOLOGY-01 commissioned | Research phase | k-regular subgraph bounds; may complete in later window |
| CDL-039 amendment scope note | Research/spec | Topology shuffling authorization path |
| CDL-066 ratification evidence | Ratification phase | Constitutional Track A |
| CDL-067 ratification evidence | Ratification phase | Settlement substrate governance vehicle |
| Coherence report + capsule v4.6 | Window close phase | |
| Closure gate | Window close phase | |

**CDL-017 ratification does NOT happen in 707-712.** The prelock evidence and
design resolution do. Ratification is at the Mysticeti convergence window.

---

## 5. Docs to read at session start

Required reading before Phase 707 begins:

1. `docs/PLANNING_INDEX.md` — live doc index (verify current window entry)
2. `docs/specs/ilc_antigravity_context_capsule_v4.5.md` — canonical frontier
3. `docs/phases/STATUS.md` (tail) — confirm Phase 706 is the last entry
4. `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md` §4.7 and §5.1–5.2 — the six Qs and window 707-712 scope
5. `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md` (M-series table) — Track B current state (M-011 complete, M-012 next)
6. `docs/specs/ilc_window_707_712_candidate_phase_grouping_v0.1.md` — recommended phase map, blockers, and open questions
7. `docs/antigravity_tasks/codex_brief__phases_707_712_g8_window_707_712_execution_guidance.md` — prompt-pack review brief

---

## 6. Hard constraints for this window

- Do NOT open CDL-062
- Do NOT select Option B (still requires explicit human authorization + runtime confirmation)
- Do NOT widen wallet authority or public claimability
- Do NOT ratify CDL-017 — prelock and design evidence only
- Do NOT begin CDL-017 prelock phases before Q1-Q6 are answered in conversation
- Do NOT mutate `ilc_core/` in the sequence lock or governance minimization doc phases
- SEC-004 (`epoch_validator_binding`) remains dormant until CDL-017 activation — do not activate early

---

## 7. Track B coordination note

While Track A (Codex) runs Window 707-712, Track B (Gemini) is running M-012
(full BFT ECUTransfer round-trip) and M-013 (Workload A real liveness run).

These tracks are independent until the Mysticeti convergence window, at which
point CDL-017 prelock evidence from Track A and M-series implementation evidence
from Track B must converge. That convergence window is not 707-712.

The capsule v4.5 Track B line ("M-011 planned") is stale — M-011 is
`binary_complete` as of 2026-04-17. The next capsule (v4.6, at window close)
should reflect Track B at M-012 or M-013 depending on Gemini's progress.
