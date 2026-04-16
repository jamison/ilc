# ILC CDL-017 Validator Governance Framework Opening Stub 695 v0.1

Status: opening stub
Date: 2026-04-16
Decision vehicle: CDL-017
Phase: 695
Document schema: `docs/specs/README.md#sequence-locks-phase-window-guidance-and-phase-artifacts`

## 1. Lane identity

`cdl_017_opened_for_validator_governance_framework`
`cdl_017_activation_required_before_non_genesis_validator_deployment`
`sec_004_epoch_validator_binding_owned_by_cdl_017_activation`

CDL-017 opens in Phase 695 as the constitutional lane for validator-governance
activation under the sovereign Option-B path.

This opening covers:
- the protocol mechanism for validator admission and ejection,
- the bootstrap-transition and Genesis-sunset boundary for moving beyond a
  static Genesis validator set,
- the governance preconditions for any later non-Genesis validator deployment.

This opening does **not** activate dynamic validator sets.

## 2. Immediate opening rationale

Track B M-007 has already created explicit hook points for validator-set change
while keeping them disabled:

```rust
fn admit_validator(&mut self, candidate: ValidatorKey) -> Result<()> {
    unimplemented!("CDL-017 ratification required before this is active")
}

fn eject_validator(&mut self, id: ValidatorID) -> Result<()> {
    unimplemented!("CDL-017 ratification required before this is active")
}
```

That means the implementation surface now exists, but the constitutional
authority to activate it does not.

CDL-017 therefore needs to open now so the project has an explicit governance
home for:
- what validator-set change means,
- when Genesis-only control sunsets,
- what must be true before non-Genesis validator authority exists.

## 3. Scope boundary

### In scope

- the on-chain / protocol mechanism for validator admission and ejection
- bootstrap transition criteria for moving from Genesis-only governance to a
  governed validator-set regime
- Genesis-sunset trigger design as it applies to validator-set authority
- activation boundary for the existing `admit_validator` / `eject_validator`
  hooks in the Mysticeti lane

### Out of scope

- near-term testnet operator selection
- ad hoc permissioning of the M-009 validator roster
- immediate ratification of admission/ejection rules
- transport-layer redesign
- substrate selection

Near-term testnet validator access remains Genesis configuration only until
CDL-017 is later ratified and activated.

## 4. Inherited interactions and exclusions

### 4.1 M-007 hook interaction

The M-007 hook points are the immediate reason this lane must open, but the
hooks do not define the law by themselves.

Opening CDL-017 authorizes the governance lane. It does not authorize runtime
activation of those hooks.

### 4.2 SEC-004 interaction

SEC-004 becomes active once dynamic validator sets exist.

When CDL-017 later moves toward ratification / activation, the ratification
packet must explicitly resolve:
- epoch / validator-set historical binding for `TransferCertificate`,
- the required certificate fields or lineage hooks that identify which
  validator set governed a historical transfer,
- the M-019 handoff obligation already recorded in the M-series lane.

CDL-017 opening therefore carries `SEC-004` forward as an activation-bound
requirement, not as a solved problem.

### 4.3 CDL-055 / CDL-056 interaction

CDL-055 and CDL-056 already govern validator participation stake, liveness,
and trust-tier elevation surfaces.

CDL-017 must not silently supersede, erase, or mutate those ratified
boundaries. Any later CDL-017 ratification packet must either:
- carry them forward explicitly, or
- propose explicit amendment language where overlap exists.

## 5. Candidate opening rule set

The candidate rule set opened here is:
- validator admission / ejection is a governed protocol action, not an
  implicit runtime freedom
- non-Genesis validator deployment requires a ratified governance path
- Genesis-only configuration remains the operative authority for near-term
  testnet validator membership
- activation of dynamic validator sets must include SEC-004 historical-binding
  resolution
- any interaction with CDL-055 / CDL-056 must be explicit rather than implied

## 6. Evidence anchors

Required anchors:
- `docs/specs/ilc_phase_694_700_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_694_700_track_a_candidate_phase_grouping_v0.1.md`
- `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`
- `docs/specs/ilc_bootstrap_operations_runbook_draft_v0.1.md`
- `docs/specs/ilc_open_requirements_and_unknown_unknowns_analysis_354_v0.1.md`

## 7. Forward obligations

Before any lane authorizes first non-Genesis validator deployment:
- CDL-017 must be ratified
- the Genesis-sunset / bootstrap-transition criteria must be explicit
- SEC-004 activation requirements must be resolved
- CDL-055 / CDL-056 interaction must be stated explicitly

This opening is therefore a governance-preparation artifact, not a deployment
authorization artifact.
