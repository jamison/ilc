# ILC DAG Censorship Bounds TLC Evidence 698 v0.1

Status: formal evidence artifact
Date: 2026-04-16
Phase: 698
Owner lane: G8 chosen-substrate legitimacy closure (Track A)
Document schema: `docs/specs/README.md#sequence-locks-phase-window-guidance-and-phase-artifacts`

`row_7_tlc_evidence_698_complete`
`tlc_model_n4_f1_maxround5`
`checked_properties=TypeOK,Safety,CommittedSubsetDag,Liveness`

---

## 1. Verification target and model parameters

This phase produces the formal row-7 evidence artifact over Spec A:

- target spec: `docs/specs/tla/ilc_dag_censorship_bounds.tla`
- target cfg: `docs/specs/tla/ilc_dag_censorship_bounds.cfg`
- execution wrapper: `tools/run_tlc_m_series_gate.sh`
- resulting Spec-A log: `tools/tla/ilc_dag_censorship_bounds.tlc.out`

The concrete TLC model parameters used in the checked run are:

- `N=4`
- `F=1`
- `MaxRound=5`
- `ByzantineSet={4}`

These values come directly from the bound TLC configuration in
`docs/specs/tla/ilc_dag_censorship_bounds.cfg` and match the M-series gate
contract used to open the implementation lane.

The exact run path used for this phase was:

```bash
bash tools/run_tlc_m_series_gate.sh
```

That script executes both Spec A and Spec B, writes the per-spec logs into
`tools/tla/`, and reports the gate token outcome at the console.

## 2. Checked invariants and temporal properties

The row-7 evidence target is Spec A only:
`docs/specs/tla/ilc_dag_censorship_bounds.tla`.

The checked invariants from the cfg were:

- `TypeOK`
- `Safety`
- `CommittedSubsetDag`

The checked temporal property from the cfg was:

- `Liveness`

What each property means in row-7 terms:

- `TypeOK`: the bounded model stays within the intended state shape
  (`dag`, `committed`, and `rnd` remain well-typed).
- `Safety`: no conflicting committed vertices arise from the same
  proposer/round identity.
- `CommittedSubsetDag`: no committed vertex appears outside the DAG state.
- `Liveness`: any honest-broadcast vertex eventually commits despite bounded
  Byzantine withholding.

This is the property that matters most for row 7. The row-7 criteria lock from
Phase 675 requires concrete censorship-resistance evidence rather than a vendor
claim. This TLC run is the bounded formal proof packet for the Mysticeti DAG
commit rule.

## 3. TLC execution record

The execution used the self-resolving gate script:

```bash
bash tools/run_tlc_m_series_gate.sh
```

Console outcome:

```text
[PASS] ilc_dag_censorship_bounds: no violations
[PASS] ilc_ecu_fast_path_bcast: no violations
[PASS] GATE SATISFIED: tla_tlc_clean_m_series_implementation_gate
```

Spec-A run record from `tools/tla/ilc_dag_censorship_bounds.tlc.out`:

- TLC version: `2026.04.09.014118`
- workers: `4`
- heap/offheap: `6144MB / 64MB`
- start time: `2026-04-16 22:13:35`
- finish time: `2026-04-16 22:13:41`
- states generated: `4911`
- distinct states: `1111`
- search depth: `29`
- result: `Model checking completed. No error has been found.`

The log also records:

- `Checking 9 branches of temporal properties`
- `Finished checking temporal properties`
- `calculated (optimistic): val = 2.3E-13`

The location of the resulting TLC output log for the row-7 evidence artifact
is:

- `tools/tla/ilc_dag_censorship_bounds.tlc.out`

This phase therefore has a concrete, reproducible formal-evidence log on disk
for the exact bounded model required by the prompt.

## 4. TTrace artifact disposition

An older on-disk trace artifact exists for Spec B:

- `docs/specs/tla/ilc_ecu_fast_path_bcast_TTrace_1776345420.tla`
- companion binary: `docs/specs/tla/ilc_ecu_fast_path_bcast_TTrace_1776345420.bin`

The current Phase 698 gate run does not reproduce an active Spec-B failure.
Instead, `tools/tla/ilc_ecu_fast_path_bcast.tlc.out` now ends with:

- `Model checking completed. No error has been found.`
- `ilc_ecu_fast_path_bcast: no violations`

The older TTrace module itself says it was generated on:

- `Thu Apr 16 15:18:09 CEST 2026`

That is consistent with the already-documented pre-fix failure period named in
the planning packet, and inconsistent with the current post-fix gate run which
passes cleanly.

`spec_b_ttrace_1776345420_disposition=stale_pre_fix_artifact`

The honest reading is:

- the TTrace is historical debug residue from an earlier failed Spec-B run
- the current clean Spec-B log supersedes it
- Phase 698 does not treat the presence of that residual file as an active row-7
  or fast-path proof gap

## 5. Row-7 disposition

The row-7 criteria lock from Phase 675 is not reopened here. This phase only
tests whether the required Mysticeti-specific formal evidence now exists.

It does.

The reasons are:

- Spec A was rerun from the current on-disk TLA and cfg files
- the exact bounded model required by the M-series gate was used
- all three listed invariants passed
- the `Liveness` temporal property passed
- the resulting log is present on disk and reproducible through
  `tools/run_tlc_m_series_gate.sh`

`row_7_post_698_status=spec_closed_runtime_pending`

That disposition is stronger than the earlier criteria-only closure because the
formal model-check evidence now exists for the concrete Mysticeti DAG path.

It remains `runtime_pending` rather than a stronger final state because TLC on
a bounded model is formal evidence of protocol logic, not runtime proof of the
full deployed validator network under live operational conditions.
