# ILC Phase 1118–1123 Sequence Lock

**Window:** 1118–1123
**Topic:** FLOAT-KILL-01 Runtime Hardening + SIM-PROVENANCE-01 Commissioning
**Locked:** Phase 1118 (2026-04-30)
**Author:** Claude Sonnet 4.6 (local architectural reviewer)
**Baseline:** Window 1110–1117 CLOSED (Phase 1117, commit `0437fcb1`). CDL-084 ratified
             (Phase 1113). PROVENANCE settlement active (Phase 1114). Capsule v5.35.
             Guidance doc: `docs/specs/ilc_window_1118_1123_candidate_phase_grouping_v0.1.md`.

`window_1118_1123_sequence_lock_committed_phase_1118`

---

## Phase Table (Locked)

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 1118 | Window sequence lock (this document) | Foundation | NON-SENSITIVE |
| 2 | 1119 | FLOAT-KILL-01: float→Decimal + PRNG hardening | Runtime | NON-SENSITIVE |
| 3 | 1120 | SIM-PROVENANCE-01 commissioning + first run **OR** FLOAT-KILL-02 | Simulation / Runtime | NON-SENSITIVE |
| 4 | 1121 | SIM-PROVENANCE-01 execution + evidence **OR** SIM-PROVENANCE-01 commissioning | Simulation | NON-SENSITIVE |
| 5 | 1122 | Coherence report + capsule v5.36 **OR** SIM-PROVENANCE-01 results | Synthesis / Simulation | NON-SENSITIVE |
| 6 | 1123 | Window 1118–1123 closure gate | Gate | **SENSITIVE** |

---

## Sequencing Constraints (Locked)

1. Phase 1118 (seq lock) must precede all other phases — **this document**.
2. Phase 1119 Commit 1 (PRNG kill: `spectral_routing_runtime.py`, `rl_agents.py`) must
   precede Commit 2 (active ECU path: `server.py`, `passive_ecu_attribution_runtime.py`,
   `rc/economic_cycle_runtime.py`, `epoch_ledger.py`). Commit 2 must precede Commit 3
   (interface cleanup).
3. FLOAT-KILL-01 Commits 1+2 must complete before SIM-PROVENANCE-01 commissioning begins.
   Commit 3 (or FLOAT-KILL-02 if triggered) need NOT be complete before SIM-PROVENANCE-01
   commissioning — the SIM imports only Decimal-clean paths (`epoch_attribution_settle_runtime.py`,
   `ilc_core/types.py`) and is not blocked by the remaining interface cleanup.
   Exception: if Phase 1119 Commit 1 or Commit 2 discovers direct float/PRNG contamination
   of the PROVENANCE simulation path (`epoch_attribution_settle_runtime.py`, `ilc_core/types.py`,
   or their SIM-PROVENANCE-01 imports), stop and escalate; SIM-PROVENANCE-01 may not
   commission until the contamination is resolved.
4. SIM-PROVENANCE-01 commissioning (writing `program.md` + `tools/sim_provenance_01.py`
   harness) must precede SIM-PROVENANCE-01 execution.
5. All phases 1118–1122 must precede Phase 1123 (closure gate cites all window work).

---

## FLOAT-KILL-01 Scope (Locked)

**Source prompt:** `docs/antigravity_tasks/antigravity_prompt__phase_1119_float_kill_01_ilc_core_float_prng_hardening.md`
(renamed from `phase_tbd_...` at Phase 1118; Phase header updated to 1119).

**Directive violations being remediated:**

| Directive | Violation | Primary target file(s) |
|-----------|-----------|------------------------|
| Directive 2 (PRNG ban) | `import random` in live routing runtime | `spectral_routing_runtime.py`, `rl_agents.py` |
| Directive 3 (float ban for ECU) | `net_stake=float(ecu_estimate_decimal)` | `rc/economic_cycle_runtime.py` |
| Directive 3 (float ban for ECU) | `ecu_spent: float`, `rewards_paid: float` accumulator | `epoch_ledger.py` |
| Directive 3 (float ban for ECU) | `compute_passive_ecu() -> float` | `passive_ecu_attribution_runtime.py` |
| Directive 3 (float ban for ECU) | `ecu_base_costs: Dict[str, float]` | `consensus/governance.py` |
| Directive 3 (float ban for ECU) | `node_stakes: Dict[str, float]` | `consensus/engine.py` |
| Directive 3 (float ban for ECU) | `net_stake: Optional[float]` in API models | `server.py` |
| Directive 3 (float ban for ECU) | stake/reward method signatures | `agent.py`, `onboarding.py`, `exceptions.py`, `genesis/work_task.py` |
| Directive 3 + exploit | `Decimal("NaN")`/`"Infinity"` not rejected at ingestion | `server.py` (confirmed exploit vector) |

**Three-commit structure (locked):**

- **Commit 1** — PRNG kill: `spectral_routing_runtime.py` + `rl_agents.py`
- **Commit 2** — Active ECU path: `server.py` (non-finite guard), `passive_ecu_attribution_runtime.py`,
  `rc/economic_cycle_runtime.py`, `epoch_ledger.py`
- **Commit 3** — Interface cleanup: `governance.py`, `engine.py`, `agent.py`, `onboarding.py`,
  `exceptions.py`, `genesis/work_task.py`

**FLOAT-KILL-02 trigger:** If `consensus/engine.py` Decimal arithmetic blast radius > ~10
usage sites at Commit 3, stop at annotation + coercion only. Phase 1120 becomes FLOAT-KILL-02.
Codex decides at Commit 3 execution time and records the decision in the Phase 1119 walkthrough.

**Files that must NOT be touched by FLOAT-KILL-01:**
- `ilc_core/economics/epoch_attribution_settle_runtime.py` — Decimal-clean (CDL-084, Phase 1114)
- `ilc_core/types.py` — Decimal-clean (CDL-084, Phase 1113)
- `ilc_core/sim/`, `ilc_core/analysis/` — simulation/analytics; float acceptable
- `ilc_core/identity/sybil_resistance_runtime.py` — probability scores; float acceptable
- `ilc_core/epistemic/aesthetic_panel_runtime.py` — vote scores; float acceptable
- `ilc_core/economics/entropy.py` — signal computation; float acceptable

---

## SIM-PROVENANCE-01 Scope (Locked)

**Primary obligation:** CDL-084 Q2 + Q8 tokens. `PROVENANCE_DECAY_ALPHA = Decimal("0.5")`
remains provisional until this SIM runs. Alpha must not be constitutionally locked before results.

**Why Phase 1120 and not deferred until after FLOAT-KILL-02:**
SIM-PROVENANCE-01 imports exclusively from Decimal-clean paths. It is not blocked by
any FLOAT-KILL-02 work on `consensus/engine.py`. Deferring further would leave alpha
provisional for two full windows. **SIM-PROVENANCE-01 at Phase 1120 (tight path) is locked.**
If FLOAT-KILL-02 triggers, SIM-PROVENANCE-01 shifts to Phase 1121 — not beyond.

**Harness artifact specification (from Phase 1116 §D, locked here):**

| Artifact | Path | Role |
|----------|------|------|
| `program.md` | `docs/sims/sim_provenance_01/program.md` or `docs/specs/sim_provenance_01_program.md` | Human-authored objective + hard metric |
| Mutable harness | `tools/sim_provenance_01.py` | Agent-mutable; exposes ALPHA, chain_depth, creator_overlap, n_epochs |
| Evaluator | Embedded in harness | Returns Gini, mint surface, alpha sensitivity, per-node descendant-count time series |

**Hard metric (locked):** Gini coefficient of PROVENANCE payout distribution per epoch < 0.6;
no single creator receives > 40% of total PROVENANCE ECU in any 100-epoch window.

**Required output (for SIM-SPECTRAL-02):** Per-node PROVENANCE descendant count as a
**time series across epochs** (not a single epoch snapshot). This is a hard output
requirement — the commissioning spec must enforce it.

**Execution deferral rule:** If overnight AutoResearch run cannot complete in one phase,
Phase 1120 (or 1121) delivers commissioning artifacts + harness. Execution results defer
to Window 1124+. The window closes on commissioning complete; alpha remains provisional.

---

## Sensitivity Classification

**SENSITIVE — requires human GO token:**
- Phase 1123 — closure gate; structural boundary

**NON-SENSITIVE — all other phases:**
- Phase 1118 — seq lock; no mutation
- Phase 1119 — runtime hardening; no CDL env var; pre-commit hook enforces automatically
- Phase 1120 — SIM commissioning or FLOAT-KILL-02; no CDL changes
- Phase 1121 — SIM execution or commissioning; no CDL changes
- Phase 1122 — Coherence or SIM results; no CDL changes

**No CDL mutations in this window.** Pre-commit hook active as safety net only.
`ILC_CDL_MUTATION_AUTHORIZED` must not appear in any commit in this window.

---

## Carry-Forward State (at Phase 1118)

**Obligated:**
- FLOAT-KILL-01 → Phase 1119
- SIM-PROVENANCE-01 → Phase 1120 (tight) or 1121 (FLOAT-KILL-02 path)

**Deferred (not advancing this window):**
- SIM-SPECTRAL-02 — awaits SIM-PROVENANCE-01 time-series data
- SIM-ECU-STABILITY-01 — candidate; authorization not granted
- SIM-HYPEREDGE-01 — gate clear; not scheduled
- Werner φ-bound CDL (CDL-085) — SIM-gated
- ADR-0035 implementation CDL — planning/authorization gated
- Star expansion — H-011 patent gate + explicit human authorization

`window_1118_1123_float_kill_01_precedes_sim_provenance_01`
`sim_provenance_01_alpha_remains_provisional_until_execution`
`float_kill_01_commits_1_2_unblock_sim_provenance_01_commissioning`
