# ILC Row-5 Runtime Evidence Package 740 v0.1

Status: runtime-evidence package
Date: 2026-04-20
Phase: 740
Owner lane: G8 MVP-gate runtime-form lane
Document schema: `docs/specs/README.md#sequence-locks-phase-window-guidance-and-phase-artifacts`

`row_5_runtime_evidence_package_740_complete`
`row_5_runtime_closure_requires_dedicated_live_leakage_measurement`
`phase_679_observability_floor_bound_to_row_5_runtime_evidence`
`phase_681_attacker_variants_bound_to_row_5_runtime_measurement`
`phase_682_narrowing_honored_not_blanket_secrecy`

## 1. Purpose and inherited authority

This artifact formalizes what live evidence is required to move row `5` from
`spec_closed_runtime_pending` to `runtime_closed`.

It inherits the authoritative row-5 baseline from:

- `docs/specs/ilc_row_5_mechanism_proof_mysticeti_697_v0.1.md`
- `docs/specs/ilc_public_legitimacy_observability_budget_679_v0.1.md`
- `docs/specs/ilc_row_5_correlation_unlinkability_simulation_packet_681_v0.1.md`
- `docs/specs/ilc_row_5_prework_narrowing_decision_682_v0.1.md`
- `docs/specs/ilc_phase_739_744_sequence_lock_v0.1.md`

Phase `697` already proved the mechanism shape over Mysticeti at code-review
level. This phase does not reopen that proof. It formalizes the remaining live
runtime evidence bar.

## 2. Remaining gap after Phase 697

Phase `697` left one explicit remaining runtime gap:

- live operator-path leakage measurement on a multi-machine validator network.

That remaining gap must now be read together with the inherited Phase `681`
attacker model:

- operator-path attacker,
- hosted-query attacker,
- repeated-contributor attacker.

The governing row-5 narrowing remains:

- correlation minimization and unlinkability, not blanket secrecy.

The honest reading is:

- static code review already shows that transfer details are not promoted into
  the ordinary public legitimacy surface by default,
- that does not yet prove that traffic timing, message size, validator-host
  vantage, or hosted-query aggregation fail to reintroduce materially stronger
  contributor linkage at runtime,
- row `5` therefore remains `spec_closed_runtime_pending` until live evidence
  exists.

`row_5_phase_697_gap_live_leakage_validation_still_required`

## 3. Required live evidence for a runtime-closed row-5 verdict

The minimum evidence sufficient to move row `5` to `runtime_closed` is:

1. a dedicated `SIM-LEAKAGE-01` execution over a multi-machine validator
   testbed,
2. complete artifact capture for all three attacker variants from Phase `681`,
3. an explicit result table mapping those measurements to the Phase `679`
   observability floor,
4. evidence that ordinary public legitimacy remains receipt-queryable,
   lineage-legible, challengeable, and bounded-human-auditable during the run,
5. evidence that contributor linkage is materially harder under the measured
   runtime than under naive public receipts,
6. no contradictory runtime finding that turns validator-only or hosted-query
   vantage into a trivially public same-contributor feed.

For closure sufficiency, the runtime evidence package adopts the two bands
already carried forward from Phase `681`:

- ordinary-observer or hosted-query same-contributor linkage recall must remain
  at or below `0.45`,
- operator-path same-contributor linkage recall must remain at or below `0.60`.

These numbers are not invented here. The ordinary-observer band is the Phase
`681` minimum materially-harder threshold, and the operator-path band is the
named stretch target from the same packet. Phase `740` makes the operator-path
band load-bearing for closure sufficiency because operator-path leakage is the
specific residual named by Phase `697`.

If the run completes but either linkage band is exceeded, the honest result is:

- row `5` remains `spec_closed_runtime_pending`,
- the evidence is still useful,
- the closure bar was not met.

## 4. Required measurement surfaces and attacker mapping

The runtime package requires the following measurement surfaces.

### 4.1 Required surfaces

- inter-arrival timing and ordering across validator-host vantage points,
- message-size buckets visible at validator-host vantage points,
- epoch-boundary timing and settlement-commit timing relative to contributor
  activity,
- hosted-query request timing and repetition patterns against any exposed read
  or query surface,
- repeated-contributor public-receipt and lineage traces across epochs.

### 4.2 Required attacker-variant mapping

**Operator-path attacker**

- vantage: validator-host or validator-network operator who can observe runtime
  message timing and message-size buckets,
- required evidence: host-level traffic capture or equivalent timestamped event
  log sufficient to estimate same-contributor linkage from timing and size,
- required question: do timing and size surfaces materially collapse the
  contributor-linkage weakening claimed by the spec-level proof?

**Hosted-query attacker**

- vantage: a provider or hosted interface aggregating repeated balance or epoch
  queries over time,
- required evidence: query logs or equivalent trace outputs showing request
  timing, repeated identifiers, and aggregation potential,
- required question: does the hosted-query surface reconstruct contributor
  linkage that the public receipt surface alone would not?

**Repeated-contributor attacker**

- vantage: an ordinary observer correlating repeated public submissions and
  surrounding lineage over time,
- required evidence: receipt and lineage corpus for repeated scripted
  contributors over multiple epochs,
- required question: does the ordinary public legitimacy surface stay below the
  materially-harder threshold rather than reverting to near-certain linkage?

### 4.3 Explicit exclusions

The following are not required closure evidence in this lane:

- global passive-surveillance resistance,
- blanket secrecy for all private work,
- heroic user anonymity operations,
- proof that no operator can ever learn anything,
- hiding receipts, breaking lineage, or suppressing challenge paths.

Those exclusions are required by Phase `682` and may not be reintroduced here
through measurement sprawl.

## 5. Observability-floor mapping

Every future `SIM-LEAKAGE-01` run must publish its findings against the Phase
`679` observability floor.

The required mapping is:

- **machine-legible receipts**:
  the run must show that receipts remain discoverable and machine-queryable
  while leakage is being measured,
- **receipt lineage intact**:
  the run must show that the measured receipts still sit inside intelligible
  legitimacy lineage,
- **challengeability preserved**:
  the run must show that the public legitimacy traces remain contestable rather
  than buried behind privileged operator state,
- **bounded human auditability preserved**:
  the run must show that an ordinary participant can still read the resulting
  legitimacy traces without expert-only tooling.

Any measured privacy improvement that requires hiding receipts, breaking
lineage, or routing verification through one privileged dashboard is
inadmissible even if the linkage metrics look favorable.

The runtime evidence package must not trade away receipts or lineage in order
to claim a favorable leakage result.

`row_5_runtime_measurement_must_not_trade_away_receipts_or_lineage`

## 6. Current status and carry-forward

This phase does not execute `SIM-LEAKAGE-01`. It formalizes the live evidence
bar and commissions the dedicated run protocol in a separate companion spec.

`row_5_status_after_phase_740=spec_closed_runtime_pending`
`sim_leakage_01_execution_pending_after_phase_740`

The post-Phase-740 status is therefore:

- row `5` remains `spec_closed_runtime_pending`,
- the runtime evidence package now exists,
- `SIM-LEAKAGE-01` is commissioned as the dedicated leakage-measurement pass,
- actual execution of `SIM-LEAKAGE-01` remains the next load-bearing row-5
  runtime obligation.
