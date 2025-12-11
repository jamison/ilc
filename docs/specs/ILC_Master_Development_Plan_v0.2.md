# ILC Master Development Plan v0.2

(post-MVP, post-Phase-61 strict closure)

# 0. Canonical references

These are the “don’t contradict these unless we know why” sources:

## Design & principles

*   `ILC_Master_Principle_List_v5.1.md` – single source of truth for high-level principles and truth primitives.
    *   *20251208 MAIN PLANNING OUTLINE …*

## Ops / governance

*   `ILC_Project_Operations_Guide_v1.0.md` – how we actually run the project (branches, phases, Antigravity runs, etc.).
    *   *20251208 MAIN PLANNING OUTLINE …*

## MVP SIM & config

*   `ilc_mvp_config_locked.json` – the frozen parameter set for MVP devnet SIM runs.
    *   *20251208 MAIN PLANNING OUTLINE …*

*   Phase-60+ CSVs: `ILC_MVP_Simulation___*.csv`, `ilc_tuned40_*.csv`, `ilc_controllers_*.csv`, etc. – canonical KPI baselines (error rates, backlog, PIC-like reuse, fairness, etc.).

## Task schema

*   `epistemic_work_task_schema_v1.json` – reference schema for epistemic.work.task, used later when SIM results meet actual task payloads.
    *   *20251208 MAIN PLANNING OUTLINE …*

From now on, SIMs and protocol work should either:
1.  adopt defaults from these, or
2.  explicitly document any deviation.

# 1. Where we are right now

## 1.1 MVP devnet status

We have an MVP devnet engine with:

*   `DevnetScenarioConfig` and helpers (`build_topology_and_profiles`, `build_snapshots_for_scenario`).
*   `run_devnet_multi_epoch` with:
    *   epoch stepping,
    *   deterministic RNG seeding,
    *   NDJSON event log export per epoch (`devnet_events.ndjson`),
    *   summary helpers (`DevnetExperimentSummary`, CSV exports).

### Key defaults already tuned and accepted from pre-MVP sims:

*   **QA controller**
    *   QA window ≈ 7 epochs
    *   backlog trigger ≈ 15
    *   error trigger ≈ 0.5%
*   **Contra caps & quorum**
    *   Cn=6, Ce=12 (early grid) as a balanced default; later contra harness suggests Cn=8, CAP_E=300 with optional guarded bump to 500.
*   **κ (pricing controller)**
    *   κ ON is strongly preferred (flattened backlog tails, within error budget).
    *   Good defaults: target_util ≈ 0.85, γ ≈ 0.10; 0.90 as throughput-tilted.
*   **Burn/PB**
    *   Network default: burn ≈ 10%, PB ≈ 5%.
    *   Growth-pilot shards: burn ≈ 5%, PB ≈ 7% (time-boxed and controlled).
*   **Micro-bounty per audit**
    *   Per-vote bounty: 0.01 (in “bounty units”) as the sweet spot; 0.0 under-incentivizes, 0.02 over-incentivizes.

These are already baked into various YAMLs / configs from the Oct-25 thread and should be treated as “locked until a new SIM proves otherwise.”

## 1.2 Phase 61+ SIM harness status (strict closure)

### Code artifacts (now “canon”):

*   **`ilc_core/sim/harness_param_grid.py`**
    *   Stable parameter-grid runner around `DevnetScenarioConfig`.
    *   Supports:
        *   `apply_params` hook for external knobs and scenario mutation.
        *   `label_suffix_builder` for compact labels.
        *   `rng_seed` → per-run deterministic `run_seed = rng_seed + run_index`.
        *   `export_root` / `export_prefix` → per-run NDJSON export directories (`grid_{label}`).
        *   CSV export: `export_param_grid_results_to_csv` with param columns + summary fields.

*   **`ilc_core/sim/harness_econ_scenarios.py`**
    *   `EconScenarioConfig(label, param_overrides)`.
    *   `run_econ_scenarios_on_devnet`:
        *   applies econ overrides via hook (`apply_econ`);
        *   uses `rng_seed + i` per scenario;
        *   uses per-scenario export directories under `export_root / label`.
    *   `default_apply_econ`:
        *   validates override keys against `ProtocolParams` fields,
        *   logs warnings for unknown keys,
        *   intentionally no-op on global state for MVP (no singleton wiring yet).
    *   `export_econ_summaries_with_overrides_to_csv`:
        *   sidecar CSV with summary metrics + `econ_*` columns for overrides.

*   **`ilc_core/sim/harness_closed_loop_controllers.py`**
    *   `ClosedLoopRunConfig(label, num_epochs, scenario, controller_params, ...)`.
    *   `run_closed_loop_devnet`:
        *   per-epoch simulation with controller callback,
        *   deterministic seeding `run_seed = rng_seed + epoch_idx`,
        *   metrics series `ClosedLoopEpochMetrics` (backlog proxy, error rates, etc.),
        *   NDJSON export per epoch if `export_root` supplied.

*   **`ilc_core/protocol/params.py`**
    *   `ProtocolParams` includes econ knobs: `burn_rate`, `pb_rate`.
    *   `load_protocol_params()` now correctly hydrates `burn_rate` and `pb_rate` from JSON.

*   **Tests: `tests/test_sim_harnesses.py`**
    *   Coverage:
        *   basic grid harness behavior,
        *   econ harness hook behavior,
        *   closed-loop harness shape & indices,
        *   econ overrides sidecar CSV,
        *   NDJSON export sanity (folders + `devnet_events.ndjson` existence),
        *   custom `apply_params` hook regression test.

Phase 61 code-level TODOs have been either:
1.  Implemented (RNG hooks, econ overrides CSV, NDJSON export, custom apply hooks), or
2.  Explicitly bumped to later phases (backlog metrics in core sim, EventLogger ergonomics, config-file scenario runners) and tagged in `TODO.txt` as Phase 63+/Genesis ergonomics.

The only non-code Phase-61 residual is:
*   **PENDING (manual):** run a couple of non-toy sweeps with `sim_param_grid_demo.py` (e.g., varying `num_agents` and stress schedules) to build intuition about `total_tasks` and `total_reward`.

You can treat that as “nice calibration homework,” not a blocker.

# 2. Phase 62–65 SIM series: what’s planned

This part is basically the “Phase 60+ retro-SIMs” mapping, now rephrased around your current harnesses.

## 2.1 Phase 62 – Consensus caps & vesting (controllers mostly fixed)

**Goal:** Re-validate and refine consensus-layer caps (Cn/Ce, CAP_E) and vesting length V in the MVP devnet, using canonical metrics & NDJSON logs.

### SIM-62A – Cn/Ce / CAP_E grid (Cn/Ce/caps)
*   **Harness:** `harness_param_grid`.
*   **Base:** `DevnetScenarioConfig` built from `ilc_mvp_config_locked.json` defaults.
*   **Grid:**
    *   Cn ∈ {4, 6, 8} (contra attempts per node),
    *   Ce ∈ {8, 12, 16} OR CAP_E ∈ {200, 300, 500} depending on how the parameter is exposed.
*   **Outputs:**
    *   `GridRunResult` list,
    *   CSV via `export_param_grid_results_to_csv`,
    *   NDJSON logs in `export_root/grid_{label}/epoch_*/devnet_events.ndjson`.
*   **Metrics to interpret (per point):**
    *   incorrect-finalized rate,
    *   false-refute rate,
    *   mean refute-T,
    *   backlog p95,
    *   DoS pressure proxies,
    *   genesis accrual (if in summary or via NDJSON post-processing).
*   **Canon to test:** earlier recommendation Cn=6/Ce=12, later contra harness recommending CN=8/CAP_E=300 with optional bump to 500.

### SIM-62B – Vesting V sweep (V ∈ {2,4,8})
*   Grid using `harness_param_grid` with param `vesting_epochs`.
*   Same base scenario & stress regime.
*   **Metrics:**
    *   incorrect-finalized,
    *   refute exposure (refute latency, how long bad claims stay live),
    *   slashing volume,
    *   churn and liquidity signals.
*   **Decision rule:** choose the shortest V that doesn’t increase incorrect-finalized or harmful churn > ~10%.

## 2.2 Phase 63 – ECU weights & subjective layer (gating/gestation/PB)

**Goal:** sanity-check that the ECU formula and subjective-broadcast gating still behave with more realistic agents, and that PB incentives don’t get gamed.

### SIM-63A – ECU β / θ grid under skewed skill distributions
*   **Harness:** `harness_param_grid`.
*   **Grid:**
    *   beta ∈ {0.4, 0.5, 0.6},
    *   theta ∈ {0.6, 0.7, 0.8}.
*   **Scenario tweaks:**
    *   introduce heavy-tailed skill prior (few superstars, many mediocre agents).
*   **Metrics:**
    *   long-run Gini of rewards,
    *   correlation skill→ILC earned,
    *   error band impact (incorrect-finalized, refute-T).
*   **Hypothesis:** β=0.5, θ=0.7 remains on fairness/quality frontier even under skew.

### SIM-63B – Subjective gating, gestation, PB-gaming
*   **Harness:** `harness_param_grid` + maybe small script-level logic.
*   **Grid axes:**
    *   gating mode ∈ {OFF, MEDIUM, CONSERVATIVE},
    *   gestation epochs ∈ {0, 1, 3},
    *   PB intensity ∈ {3%, 5%, 7%}.
*   **Add simple adversarial “PB farmer” agents.**
*   **Metrics:**
    *   reuse/PIC-like metrics,
    *   incorrect-finalized,
    *   PB farmer ROI vs genuine progenitors.
*   **Hypothesis:** MEDIUM/CONSERVATIVE + gestation=3 + PB=5% blocks naive PB-gaming.

## 2.3 Phase 64 – Macro-econ & fairness

**Goal:** port the 120-epoch A/B/C/D macro econ scenarios and burn×PB grids into the new MVP devnet, confirm earlier conclusions, and lock monetary defaults.

### SIM-64A – A/B/C/D macro scenarios
*   **Harness:** `harness_econ_scenarios`.
*   **EconScenarioConfig list:**
    *   A_default,
    *   B_pilot_growth (lower burn / higher PB),
    *   C_auditor_heavy,
    *   D_highburn_highPB.
*   Overrides applied via `apply_econ` hook (for now, may just validate/hypothetically set `burn_rate`, `pb_rate`).
*   Per-scenario NDJSON export under `export_root/{label}/epoch_*`.
*   Use `export_econ_summaries_with_overrides_to_csv` so `econ_burn_rate`, `econ_pb_rate` are captured in the CSV.
*   **Metrics:**
    *   PIC / reuse proxy,
    *   vault runway & supply growth,
    *   incorrect-finalized,
    *   fairness metrics (auditor Gini, top-10% share).
*   **Canonical expectation:**
    *   A = baseline,
    *   B = best onboarding runway with decent quality,
    *   C = auditor-heavy plus shorter runway,
    *   D = “extreme but informative.”

### SIM-64B – Burn×PB sensitivity grid
*   Also with `harness_econ_scenarios`.
*   **Grid:**
    *   burn ∈ {5, 10, 15, 20}%,
    *   PB ∈ {3, 5, 7, 10}%.
*   **Metrics:** same as 64A.
*   **Goal:** reconfirm that:
    *   network default ≈ burn 10%, PB 5%,
    *   growth-pilot ≈ burn 5%, PB 7% (time-boxed).

## 2.4 Phase 65 – Storage, DA, compaction, dust, panel independence

These are more architectural but still SIM-driven; they can reuse either `harness_param_grid` or custom scripts building on event logs.

### SIM-65A – Data availability & compaction under outages
*   Simulate different storage policies:
    *   pure replication vs hybrid vs EC-like codes,
    *   compaction policies (10-epoch compaction cycles, varying stale fractions).
*   Inject correlated node outages.
*   **Metrics:**
    *   replay viability,
    *   refute success after compaction,
    *   storage cost vs durability.
*   Earlier toy sim suggests hybrid+compaction yields ~11k steady-state nodes vs 66k un-compacted for similar integrity – this is the benchmark to aim at.

### SIM-65B – Dust batching & denomination floors
*   Use more realistic task size/reward distributions.
*   **Sweep:**
    *   dust threshold,
    *   batching frequency.
*   **Metrics:**
    *   fraction of participants “stuck under dust” vs chain cleanliness.
*   **Goal:** ensure current thresholds don’t block reasonable micro-payout patterns.

### SIM-65C – Panel independence with PVT-96
*   Sim pairing logic at devnet scale, including colluding, capital-heavy clusters.
*   **Metrics:**
    *   effective overlap rates of panels,
    *   collision / correlation rates under PVT-96 + Bloom filters.
*   **Goal:** confirm that the PVT-96 + Bloom scheme keeps panels reasonably independent.

# 3. Genesis / ilc_main track (beyond SIMs)

While Phases 62–65 are SIM-heavy, the other big branch is the Genesis / ilc_main implementation, as laid out in your *20251208 MAIN PLANNING OUTLINE ILC GENESIS (post MVP).docx*.

At 30k feet, this splits into:

## 3.1 Protocol / graph layer
*   Finalize `.ilc.protocol.json` schema for:
    *   claims,
    *   refutes/contradictions,
    *   staking payloads.
*   Ensure the schema aligns with:
    *   master truth primitives (from Master Principle List),
    *   `epistemic_work_task_schema_v1.json`.
*   Design and finalize:
    *   `genesis.node_structure` (payload, metadata, edges),
    *   how SIM‐side metrics map into real economic rewards (via ECU / task receipts).

## 3.2 Node implementation (ilc_main)
*   Define minimal Genesis node implementation:
    *   ingestion of tasks,
    *   claim creation,
    *   evaluation & refute handling,
    *   reward accounting (off-chain, at first).
*   Implementation plan:
    *   initial reference implementation in Python or C++,
    *   event-log–compatible so SIM harnesses and live nodes speak the same “telemetry” language,
    *   packaging for single-machine and small cluster experiments.

## 3.3 Network & launch preparation
*   Define what “ILC devnet” and “ILC mainnet-alpha” look like:
    *   minimal number of agents and human operators,
    *   which SIM-derived defaults are locked for launch,
    *   what metrics gates must be satisfied (max incorrect-finalized, minimal PIC, fairness bounds).
*   Tokenomics & emissions:
    *   align real on-chain emissions schedule with SIM results (burn/PB, emissions decay, slashing splits).

# 4. Cross-cutting tasks & their status

## 4.1 Documentation & specs

**DONE / IN PROGRESS**

*   `ILC_Master_Principle_List_v5.1.md` – living spec of philosophical + architectural constraints.
*   `ILC_Project_Operations_Guide_v1.0.md` – how phases, Antigravity prompts, branches, and artifacts are managed.
*   `ILC_Master_Development_Plan_v0.1` – first pass of this doc (you’ve now effectively upgraded it to v0.2 with this consolidation).

**TODO (near-term, “easy wins”)**

*   Update `ILC_Master_Development_Plan` to:
    *   mark Phase 61 as strictly closed,
    *   embed SIM-series outline (Section 2),
    *   reference canonical defaults (Section 1.1).
*   Ensure `TODO.txt`:
    *   tags backlog / EventLogger / config-runner ergonomics as “Phase 63+/Genesis”,
    *   has a short section listing “Tier-1 SIMs” (e.g., 62A, 62B, 63A, 63B, 64A, 64B, 65A).

## 4.2 Metrics & dashboards

**Goal:** bake metrics standards into both SIMs and future live systems.

**Canonical metric families:**
*   correctness: incorrect-finalized, false-refute,
*   latency: refute-T, finalization times,
*   load: backlog p95, utilization,
*   economics: vault runway, burn+PB flows, slashing volume,
*   fairness: Gini, top-10% share, skill→reward correlation,
*   reuse: PIC-like metrics, star-map hit rates.

**Tasks**
*   Lock metric definitions in a single doc (or in code comments where summaries are computed).
*   Align:
    *   SIM CSVs,
    *   dashboards (future Grafana / notebooks),
    *   acceptance criteria for launch.

## 4.3 Safety & adversarial SIMs

*   Design a small suite of safety SIMs reusing Phases 62–65 harnesses:
    *   heavy false-refute base,
    *   concentrated collusion on panels,
    *   DA failures + compaction,
    *   PB gaming patterns.
*   Use a simple rule: no parameter change gets adopted unless it passes:
    *   default scenario sims, and
    *   a set of adversarial/safety sims.

# 5. What’s actually pending vs done

Let’s label things clearly.

## 5.1 Phase 61+

*   Harness implementation & tests: **DONE.**
*   NDJSON export wiring: **DONE.**
*   Econ overrides CSV sidecar: **DONE.**
*   Custom apply-hook for “external knobs”: **DONE.**
*   Backlog metric wired from core sim → `ClosedLoopEpochMetrics`: **DEFERRED** (Phase 63+/Genesis ergonomics).
*   Config-file scenario runner (`run_scenarios_from_config`): **DEFERRED** (Genesis ergonomics).
*   EventLogger ergonomics & cleaning up naming: **DEFERRED.**
*   Non-toy param sweeps with `sim_param_grid_demo.py`: **PENDING** (manual, non-blocking).

## 5.2 Phase 62–65 SIM series

All of the SIMs in Section 2 are:
*   **PLANNED**, not yet implemented in your repo,
*   and they’re now much easier because the harnesses exist.

The most important “Tier-1” sims to prioritize (per the earlier doc) are:
*   62A – Cn/Ce (or Cn+CAP_E) grid,
*   62B – Vesting sweep,
*   63A – ECU β/θ grid,
*   63B – gating+gestation+PB,
*   64A – A/B/C/D macro scenarios,
*   64B – Burn×PB grid,
*   65A / 65B for DA & dust if time allows.

# 6. Practical action plan from here

Here’s how I’d operationalize all this right now:

1.  **Accept Phase 61 strict closure.**
    *   Treat all harness work as complete; remaining ergonomics are explicitly Phase 63+/Genesis items.

2.  **(Optional but nice) Run one non-toy sweep with `sim_param_grid_demo.py`:**
    *   vary `num_agents` and a non-trivial `stress_schedule`,
    *   generate CSV + eyeball how `total_tasks` and `total_reward` respond.

3.  **Promote this outline to `ILC_Master_Development_Plan_v0.2.md`.**
    *   Paste the contents of Sections 0–6 into the doc you’ve already created.
    *   Adjust version header and dates as you like.

4.  **Pick the first SIM phase to Antigravity-ify.**
    *   My suggestion: **Start with Phase 62A** (Cn/Ce / CAP_E grid) as the first dedicated Antigravity prompt:
        *   It’s simple to wire to `harness_param_grid`,
        *   It exercises the NDJSON export,
        *   And it tightens one of the most central consensus knobs.

5.  **Use this plan as the “north star” context.**
    *   When we design the Phase 62 Antigravity prompt, we’ll reference:
        *   this SIM outline,
        *   the MVP config file,
        *   and the harness API,
    *   so the prompt can be extremely explicit and code-heavy, not hand-wavy.

## How I got here (so you can sanity-check my reasoning):

*   I pulled the outstanding Phase-61 TODOs from `TODO.txt` and the previous harness review, then checked them against the actual `harness_*` files and tests you uploaded to see what’s truly implemented vs deferred.
*   I mined `20251209 List of Simulations and Tests and What might be pending.docx` for:
    *   the catalogue of past sims,
    *   canonical parameter conclusions,
    *   and the proposed mapping into Phases 61–65.
*   I cross-checked the high-level GENESIS outline from `20251208 MAIN PLANNING OUTLINE ILC GENESIS (post MVP).docx` to make sure the SIM phases line up with the longer-arc “ilc_main / genesis node” roadmap.

From here on out, the game is: treat this doc as the spine, and every new Antigravity phase either checks off one box or updates one section—with the SIM harnesses as your little physics bench for stress-testing each idea.
