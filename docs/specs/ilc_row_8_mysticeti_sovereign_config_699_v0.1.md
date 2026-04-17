# ILC Row-8 Mysticeti Sovereign Configuration 699 v0.1

Status: confirmation artifact
Date: 2026-04-16
Phase: 699
Owner lane: G8 chosen-substrate legitimacy closure (Track A)
Document schema: `docs/specs/README.md#sequence-locks-phase-window-guidance-and-phase-artifacts`

`row_8_mysticeti_sovereign_confirmation_699_complete`
`row_8_reopened=no`
`mysticeti_sovereign_mode_external_constitutional_center=absent`

---

## 1. Locked row-8 criteria inherited from Phase 675

This phase does not reopen row 8.

It inherits the locked row-8 rule from:

- `docs/specs/ilc_rows_7_8_selection_criteria_lock_675_v0.1.md`
- `docs/specs/ilc_cdl_062_mysticeti_survivor_set_addendum_693_v0.1.md`

The inherited row-8 rule is:

- later substrate families may not make protocol legitimacy subordinate to an
  outside veto authority
- outside systems may carry or settle already-legitimate protocol state, but
  may not become the constitutional center that authors legitimacy
- the Phase-673 exclusion matrix remains binding for later substrate
  admissibility

The specific job of Phase 699 is narrower than the original row-8 lock:

- take the already-selected Mysticeti sovereign deployment mode
- map it against the locked criteria
- state whether the current concrete deployment assumptions still satisfy the
  independence bar

## 2. Mysticeti sovereign deployment assumptions

The sovereign deployment assumptions used in this confirmation are drawn from:

- `docs/specs/ilc_cdl_062_mysticeti_survivor_set_addendum_693_v0.1.md`
- `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`
- `docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md`

The relevant assumptions are:

1. The ILC deployment runs its own validator set.
   The current M-series lane explicitly states row 8 as:
   `ILC governs its own validator set; no Sui Foundation, no Mysten Labs`.

2. The near-term validator set is statically configured and Genesis-governed.
   `CDL-017` is not yet ratified, so validator admission remains a static
   Genesis configuration rather than an outside managed service.

3. Consensus networking is validator-to-validator QUIC over a static peer list.
   The implementation lane names `quinn` and a static peer list matching
   `static_v1`; it does not route consensus through an external shared
   sequencer, external bridge, or Sui-operated relay.

4. The sovereign ILC deployment does not rely on Sui mainnet or Sui governance.
   The 693 addendum already states:
   `the Sui network and Sui Foundation are not involved`.

5. The settlement substrate remains downstream only.
   Row 6 still governs. Mysticeti may carry epoch state and ECU certificates,
   but it does not author ILC legitimacy from outside the protocol.

These assumptions are enough to perform the row-8 confirmation check.

## 3. Criterion-by-criterion confirmation matrix

| Locked criterion | Mysticeti sovereign-mode evaluation | Verdict |
|---|---|---|
| Outside validator-set control must be absent | The current M-series plan uses a static Genesis validator set under ILC control. No outside organization is documented as controlling validator admission, validator ejection, or validator credential issuance in sovereign mode. | CONFIRMED |
| Outside veto authority over protocol legitimacy must be absent | Mysticeti in this lane is a sovereignly deployed protocol component, not a service controlled by Sui Foundation, Mysten Labs, or Sui governance. The row-6 upstream/downstream boundary remains active, so the substrate carries already-legitimate ILC state rather than authoring legitimacy from outside. | CONFIRMED |
| Reliance on Sui Foundation, Mysten Labs, or Sui mainnet governance must be absent | The 693 addendum states that `the Sui network and Sui Foundation are not involved`, and the M-series lane states `no Sui Foundation, no Mysten Labs` as a governing constraint. The current implementation lane uses extracted Rust components and local validator configuration, not Sui mainnet membership or Sui governance. | CONFIRMED |
| Reliance on external bridges or external sequencing for fast-path consensus must be absent | The owned-object ECU transfer path is described as validator-to-validator QUIC consensus using local validator keys and local balance state. No external bridge, rollup sequencer, shared sequencer, or outside ordering service appears in the fast-path plan. | CONFIRMED |
| The static bootstrap validator set must remain ILC-governed in sovereign mode | The current configuration is explicit: Genesis validator set documented as static and four validators, with `CDL-017` now open but still unratified and inactive for dynamic validator-set activation. That is a bounded internal governance posture, not outside constitutional dependence. | CONFIRMED |

## 4. Residual ambiguities and required resolution path

No current row-8 failure is identified for sovereign Mysticeti mode.

The remaining ambiguities are forward-governance questions, not present
independence gaps:

1. **Dynamic validator governance is not yet active.**
   `CDL-017` remains opening-only in this window. When dynamic validator
   admission and ejection activate later, the ratification packet must preserve
   the same ILC-native independence that the current static Genesis
   configuration already satisfies.

2. **Validator-agent identity is a future governance hardening lane.**
   The carry-forward plan now treats validators as agent-linked roles. That may
   deepen ILC-native accountability, but it is not required for the current
   row-8 confirmation because the present sovereign-mode configuration is
   already internally governed.

3. **Final production selection remains out of scope.**
   Confirming that sovereign Mysticeti mode satisfies row 8 does not select the
   final Option B production configuration. It only confirms that the current
   sovereign deployment assumptions do not violate the existing independence
   lock.

These items belong to later governance and convergence work. They do not turn
the current row-8 confirmation into a gap.

## 5. Final disposition

The concrete sovereign Mysticeti deployment assumptions satisfy the already
locked row-8 independence criteria.

The decisive reasons are:

- outside validator-set control is absent
- outside veto authority over legitimacy is absent
- Sui Foundation, Mysten Labs, and Sui mainnet governance are not part of the
  sovereign deployment mode
- no external bridge or shared sequencer is used for fast-path consensus
- the static bootstrap validator set remains ILC-governed

`row_8_post_699_disposition=CONFIRMED`

Row 8 therefore remains closed under the Mysticeti sovereign deployment mode
now being pursued in Track A and Track B.
