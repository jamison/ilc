# ILC Antigravity Context Capsule v5.12

Supersedes: docs/specs/ilc_antigravity_context_capsule_v5.11.md
Date: 2026-04-23
Owner lane: G8 Window 811-822 Option B selection and pre-RC hardening

`capsule_v5_12_supersedes_v5_11`
`option_b_selected_by_human_authorization_2026_04_23`
`adr_0028_posture=option_b`
`tla_spec_a_maxround_widened_pre_rc`
`tla_spec_a_maxround12_default_gate_memory_bound`
`tla_safety_no_dual_cert_deferred_spec_d`
`tla_spec_c_partition_heal_pre_rc`
`tla_refinement_notes_pre_rc`
`sec_007a_protoc_vendored`
`sec_007b_rand_alert_dispositioned`
`row_5_pre_public_rc_obligation_still_active`
`no_cdl_mutation_in_window_811_822`

This capsule is self-contained.

## 1. Current Frontier State

Window 811-822 resolved the ADR-0028/checklist inconsistency, consumed the
human authorization of 2026-04-23, and formally recorded Option B selection.

Current frontier posture:

- `option_b_selected_by_human_authorization_2026_04_23`
- `adr_0028_posture=option_b`
- row 5 remains open as a named parallel obligation and a required
  pre-public-RC obligation,
- row 7 remains `runtime_closed`,
- row 8 remains `pass`,
- first non-Genesis validator deployment still requires a separate explicit
  human gate.

## 2. TLA+ and Build Hardening Posture

Pre-RC hardening now stands as follows:

- Spec A horizon widened to `MaxRound=12`,
- the default 6GB TLC gate is memory-bound at that horizon,
- a higher-heap retry progressed materially further without finding a
  counterexample,
- shared-object `SafetyNoDualCert` remains honestly deferred to a later Spec D,
- Spec C partition/heal now has a clean TLC evidence artifact,
- TLA-to-Rust refinement notes are published,
- `ilc_consensus` now vendors `protoc`,
- SEC-007b rand alert is dispositioned with no direct `rand` use in
  `ilc_consensus/src`.

## 3. Preserved Boundaries

This capsule does not claim:

- live settlement-path rotation,
- first non-Genesis validator deployment,
- row-5 runtime closure,
- HIGH-002 remediation,
- any CDL mutation,
- production readiness.

## 4. Carry-Forward

Carry-forward from this frontier:

- the next activation window can scope or implement live settlement-path
  rotation without reopening Option B selection,
- row 5 privacy remains a real pre-public-RC obligation,
- HIGH-002 remains a documented limitation,
- default TLC tooling may need a larger repeatable heap contract if
  `MaxRound=12` is to become a canonical clean gate rather than an
  environment-tuned run.
