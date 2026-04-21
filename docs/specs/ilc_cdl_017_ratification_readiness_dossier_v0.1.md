# ILC CDL-017 Ratification Readiness Dossier v0.1

Status: PRE-WORK — CDL-017 is not ratified and will not be ratified in this
window. This dossier assembles the ratification inputs so the later CDL-017
ratification window can execute immediately after the convergence window
closes. CDL-017 ratification requires both M-022 implementation confirmation
and convergence row evidence. M-022 approval alone is not sufficient to open
the CDL-017 ratification window.

**Phase:** 755  
**Window:** 753-756  
**Date:** 2026-04-21  
**Author:** Codex

`cdl_017_ratification_readiness_dossier_prework_only`
`cdl_017_current_status_open_unratified`
`codex_side_prelock_complete_inputs_assembled`
`m022_implementation_confirmation_required_for_cdl_017`
`convergence_window_outputs_required_before_cdl_017_ratification`
`m022_approval_alone_insufficient_for_cdl_017_window`
`sec_004_activation_scope_bound_to_post_ratification_m_track_work`
`cdl_017_ratification_window_sequenced_after_convergence`

## 1. What CDL-017 covers

Re-reading the constitutional decision log and the Phase `695` opening stub
fixes the live CDL-017 posture as follows:

- `CDL-017` was opened in Phase `695`,
- current decision-log status remains `open`,
- the lane covers validator-governance activation for:
  - bootstrap transition criteria,
  - Genesis-sunset triggers,
  - dynamic validator-set activation boundary,
- the lane is the constitutional home for validator admission and ejection,
- the lane does **not** by itself activate dynamic validator sets before
  ratification.

The opening stub also fixes the implementation relationship:

- M-007 created explicit `admit_validator` / `eject_validator` hook points,
- those hook points remain `unimplemented!` until CDL-017 ratifies,
- near-term testnet validator access remains Genesis configuration only until
  later ratification and activation.

The authoritative live posture is therefore narrow and unchanged:

- `CDL-017` is open,
- Codex-side prelock work is complete,
- implementation activation remains gated,
- first non-Genesis validator deployment remains unauthorized.

## 2. Codex-side prelock evidence summary

The Codex-side prelock block is complete and already committed. This dossier
does not re-derive that work; it assembles it for the later ratification
window.

The direct prelock sources are:

- `docs/research/ilc_validator_agent_q1_q6_prewindow_resolution_v0.1.md`
- `docs/research/ilc_validator_agent_design_evidence_v0.1.md`
- Phase `737` updates recorded in
  `docs/research/ilc_validator_agent_design_evidence_v0.1.md`
- `docs/specs/ilc_cdl_068_topology_shuffle_authorization_opening_v0.1.md`
- `docs/specs/ilc_cdl_068_topology_shuffle_authorization_ratification_evidence_743_v0.1.md`

Those committed artifacts establish the Codex-side inputs the later
ratification window will consume:

1. **ValidatorKey linkage**
   derived sub-key with provable linkage from `AgentID`, not same-key identity.

2. **Stake-floor evidence**
   `SIM-VALIDATOR-01` supplies the committed stake-floor interval
   `400000000-450000000` micro-ECU and the hard VRF-upgrade trigger
   `vrf_upgrade_threshold_validator_count = 10`.

3. **Admission semantics**
   threshold-gated validator eligibility pool, not proportional seat weighting.

4. **Validation-pool exclusion**
   validation pools, delegation, and slash propagation remain outside CDL-017
   core and require a later separate constitutional lane.

5. **Topology authorization path**
   topology shuffle is no longer an unnamed later question. CDL-068 now exists
   and is ratified, which gives CDL-017 an explicit constitutional neighbor for
   topology assignment, diversity constraints, and randomness-source boundary.

6. **Validator-composition diversity metric**
   `validator_cluster_id` remains the explicit diversity dimension and
   `SIM-TOPOLOGY-01` now supplies the full-pass thresholds:
   `distinct_cluster_floor_recommendation 4` and
   `max_cluster_share_ceiling_recommendation 33`.

The truthful Codex-side conclusion is:

- the constitutional text and supporting prelock evidence exist,
- the Codex lane no longer has unresolved prelock questions for CDL-017 core,
- ratification still requires implementation-side confirmation plus convergence
  outputs.

## 3. What M-022 must confirm

M-022 is the implementation-side confirmation surface. This dossier writes the
checklist against which the later ratification window will evaluate the M-022
handoff package.

The M-022 checklist is:

1. **Validator-governance scaffolding documented honestly**
   the handoff must confirm what the M-007 Rust governance hooks provide today
   and what remains disabled until ratification. The dossier assumes the
   documented `unimplemented!` gate remains authoritative until a later
   ratification opens activation.

2. **Key-ceremony protocol carried forward honestly**
   the handoff must explain how validator key generation, verification, and
   admission ceremony are intended to operate for non-Genesis validators.
   The M-series lane names this as an M-007 evidence topic. The ratification
   window may consume it from a standalone protocol artifact if present or from
   the M-022 handoff package if the handoff is the live carrier.

3. **SEC-004 activation scope stated explicitly**
   the handoff must name epoch / validator-set historical binding as
   post-ratification activation work:
   `TransferCertificate` must gain `epoch: EpochSeq`, and certificate
   verification must resolve the historically active `ValidatorSet` for that
   epoch from LMDB epoch records.

4. **First validator deployment prerequisites made explicit**
   the handoff must state what the Rust implementation still requires before a
   real non-Genesis validator can be deployed, rather than letting deployment
   preconditions hide inside ratification prose.

5. **Strong-exitability drill physically evidenced**
   the handoff must include actual export path, actual replay-log epoch
   numbers, and fresh-node startup log. The later ratification window does not
   treat this raw evidence as a direct ratification substitute; it routes
   through the convergence verdict on row `7`. But the raw evidence must exist
   in M-022 first.

M-022 is therefore necessary, but it is not sufficient. The later ratification
window still requires the convergence outputs that interpret the M-022 and
M-021 evidence against the row-closure contracts.

## 4. CDL-017 ratification window scope and sequencing

The later CDL-017 ratification window is separate and subsequent. The correct
execution order is:

`M-022 approval -> convergence window (CW-1 through CW-6) -> CDL-017 ratification window`

That later ratification window consumes four input classes:

1. constitutional text from the Phase `695` opening and the live CDL register,
2. Codex-side prelock evidence from Window `733-738`,
3. M-022 implementation confirmation of what the Rust validator-governance
   scaffolding provides and what activation still requires,
4. convergence outputs recording the honest runtime position on rows `5`, `7`,
   and `8`.

The later ratification window may then:

1. perform the constitutional ratification act for `CDL-017`,
2. record the exact activation boundary and what ratification authorizes,
3. preserve the separate explicit human gate for first authorized validator
   deployment.

This sequence prevents two invalid shortcuts:

- `M-022 approved, therefore ratify CDL-017 now`,
- convergence pre-drafts exist, therefore convergence outputs may be assumed.

Neither shortcut is legitimate.

## 5. SEC-004 disposition

SEC-004 remains dormant until CDL-017 activation begins. The live gap is:

- `TransferCertificate` carries no epoch reference,
- validator-set changes would make historical signature verification ambiguous,
- certificates from prior epochs could be checked against the current
  validator set incorrectly.

The fixed implementation scope is:

- `TransferCertificate` gains `epoch: EpochSeq`,
- certificate verification resolves the historically active `ValidatorSet` for
  that epoch from LMDB epoch records before verifying signatures.

The fixed acceptance condition is:

- `test_ejected_validator_sig_rejected_after_epoch_boundary` passes.

The routing is also fixed:

- this is M-track implementation work,
- it begins only after CDL-017 ratifies,
- M-022 must document it as activation scope rather than silently assuming it
  is already solved.

## 6. What this dossier is not

This dossier is not:

- a CDL-017 ratification artifact,
- an opening of the later ratification window,
- proof that M-022 has already been approved,
- proof that convergence outputs already exist,
- final constitutional ratification text,
- authorization for first non-Genesis validator deployment.

## 7. Source inputs

- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_cdl_017_opening_stub_695_v0.1.md`
- `docs/research/ilc_validator_agent_design_evidence_v0.1.md`
- `docs/research/ilc_validator_agent_q1_q6_prewindow_resolution_v0.1.md`
- `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`
- `docs/specs/ilc_master_completion_roadmap_v0.1.md`
- `docs/specs/ilc_mysticeti_convergence_window_commissioning_spec_746_v0.1.md`
- `docs/specs/ilc_mysticeti_convergence_window_guidance_v0.1.md`
- `docs/specs/ilc_cdl_068_topology_shuffle_authorization_ratification_evidence_743_v0.1.md`
