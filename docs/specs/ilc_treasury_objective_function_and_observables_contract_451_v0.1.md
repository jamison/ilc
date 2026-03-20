# ILC Treasury Objective-Function and Observables Contract 451 v0.1

Status: Phase-451 objective-function and observables contract
Date: 2026-03-20
Owner lane: G8 Constitution Cluster A

## 1. Treasury optimization target

Phase 451 freezes the Treasury objective-function for Window 450-459 before any simulation work begins.

The Treasury optimization target is not a single defended output. Treasury is optimizing for bounded productive continuity under ECU-side intervention discipline.

For this window, the optimization target is:
- keep the system within the constitutional clamp surface often enough to avoid persistent destabilization,
- preserve organic ECU production rather than replacing it with Treasury-driven output,
- minimize productive backlog accumulation and queue-stall behavior,
- minimize release shocks after time-lock expiry,
- minimize intervention duration and intervention cost.

This contract therefore treats `P_e` as an observed output inside a larger control surface rather than the sole optimization target.

## 2. Candidate observables

The following five observables are frozen for Window 450-459 simulation and blocker-clearance work:
- `P_e clamp-respect rate`
- `organic ECU production rate`
- `productive backlog / queue-clearance behavior`
- `release-shock amplitude after time-lock expiry`
- `intervention duration and intervention cost`

No blocker closes on prose alone.

## 3. Observable definitions

`P_e clamp-respect rate`
- Definition: the share of measured epochs in which `P_e` remains within the ratified `CDL-030` clamp band (`0.75-1.30`) unless a later constitutional amendment explicitly changes that band.
- Why it matters: it measures whether Treasury interventions preserve the bounded external price surface without making that surface the only thing that counts.

`organic ECU production rate`
- Definition: ECU generated per epoch excluding direct Treasury-enhanced output categories that the later simulation brief classifies as intervention-contaminated.
- Why it matters: blocker 1 cannot close unless recovery is evaluated on a production measure that Treasury cannot satisfy by directly extending intervention pressure.

`productive backlog / queue-clearance behavior`
- Definition: the measured depth, persistence, and clearance rate of productive work awaiting validation, release, or conversion under the candidate intervention regime.
- Why it matters: an intervention that protects a clamp while choking productive throughput is not constitutionally successful.

`release-shock amplitude after time-lock expiry`
- Definition: the magnitude of post-lock volatility or destabilization when a previously restricted cohort exits the time-lock and becomes eligible for conversion or release.
- Why it matters: blocker 2 cannot close unless the window measures whether an intervention merely delays a later destabilization pulse.

`intervention duration and intervention cost`
- Definition: the total time Treasury stays active plus the bounded cost profile of the chosen lever set during that intervention episode.
- Why it matters: Treasury must be able to justify both how long it intervenes and what the intervention costs the network.

No parameter locks without pre-registered discriminating metrics.

## 4. Evidence-source ladder

The evidence-source ladder for Window 450-459 observables is frozen as follows:

Tier 1 - commissioned simulation artifacts
- canonical scenario manifests,
- seeded run manifests,
- raw scenario outputs,
- reproducible summary tables derived from those outputs.

Tier 2 - contract-bound derived metrics
- metric calculations explicitly defined by the SIM-T commission brief,
- comparative synthesis tables produced from Tier 1 artifacts,
- blocker-clearance tables that point back to frozen metric definitions.

Tier 3 - constitutional interpretation artifacts
- blocker-clearance memoranda,
- Treasury risk-tolerance judgment drafts,
- recovery-criterion comparison memoranda.

Tier 4 - narrative-only discussion
- meeting prose,
- freeform commentary,
- non-reproducible argument without metric traceability.

Window 450-459 may use Tier 3 material to explain results, but the observables are only evidenced by Tier 1 and Tier 2 material. Tier 4 is non-authoritative for blocker closure.

Observable-to-evidence binding:
- `P_e clamp-respect rate` is evidenced by Tier 1 and Tier 2 artifacts only, using the ratified `CDL-030` clamp band (`0.75-1.30`) as the constitutional measurement surface.
- `organic ECU production rate` is evidenced by Tier 1 and Tier 2 artifacts only, with intervention-contaminated categories defined explicitly in the commissioned simulation brief.
- `productive backlog / queue-clearance behavior` is evidenced by Tier 1 and Tier 2 artifacts only, using reproducible queue-depth and clearance summaries rather than narrative descriptions.
- `release-shock amplitude after time-lock expiry` is evidenced by Tier 1 and Tier 2 artifacts only, using reproducible post-expiry volatility or destabilization measurements.
- `intervention duration and intervention cost` is evidenced by Tier 1 and Tier 2 artifacts only, using explicit duration and cost tables derived from the commissioned runs.

## 5. Anti-goals

The following anti-goals are frozen for this phase:
- do not collapse Treasury success into a single defended `P_e` number,
- do not count Treasury narrative preference as evidence,
- do not lock Treasury parameters before the simulation brief freezes discriminating metrics,
- do not use Phase 451 to decide the L1/L2 prerequisite question,
- do not let Jubilee, node-rent lifecycle, or unrelated macro theory enter the objective contract,
- do not treat Phase 451 as authorization to open CDL-050.

No blocker closes on prose alone.

No parameter locks without pre-registered discriminating metrics.

## 6. Non-authorization statement

No CDL-050 opening or ratification occurs in Phase 451.

Phase 451 freezes the Treasury objective-function and observables contract only. It does not authorize Treasury implementation, simulation execution, or parameter lock-in.
