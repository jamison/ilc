# ILC Werner Flow Governor CDL Decision 1263 v0.1

**Date:** 2026-05-08
**Phase:** 1263
**Status:** Sensitive CDL decision packet; no opening or prelock
**Human authorization:** `GO Phase 1263`
**Window lock:** `docs/specs/ilc_phase_1257_1264_sequence_lock_v0.1.md`

```text
werner_flow_governor_cdl_opening_prelock_decision_phase_1263.v0.1
werner_flow_governor_cdl_not_opened_without_evidence_phase_1263
direct_werner_ecu_creation_rejected_phase_1263
phase_1263_sensitive_cdl_gate_complete
```

## 1. Decision Verdict

Phase 1263 does not open or prelock a Werner flow-governor CDL.

```text
werner_flow_governor_cdl_decision_phase_1263=no_open_no_prelock
```

The current evidence supports Werner as a SIM-FETCH topology-pressure evidence
lane, but it is not yet sufficient for constitutional opening or prelock of a
runtime flow-governor policy.

The controlling reason is narrow:

- Phase 1262 promoted Werner only as a future SIM-FETCH evidence profile after a
  follow-up, not as an already-default evidence profile.
- The forward plan still requires spectral trust threshold discipline before
  heat/topology signals can become policy inputs.
- The forward plan still requires beta/noise decomposition or equivalent
  productive-flow evidence before heat can distinguish verified demand from
  reputation theater.
- Any admission, routing, or public-path use still depends on authenticated
  transport identity rather than IP, JSON/body requester IDs, AgentID exposure,
  or harness identity.
- Any ECU credit path remains separate and requires a productive-credit
  authorization CDL, consensus-epoch settlement, fixed-point or Decimal numeric
  contracts, exposure ceilings, escrow/clawback, and wallet-signing boundary
  work.

This phase therefore records a no-open decision, not a rejection of the Werner
lane. The lane carries forward with explicit closing conditions.

In short: this is not a rejection of the Werner lane.

Dependency verdict consumed from Phase 1262:

```text
werner_overlay_verdict_phase_1262=promote_to_default_sim_fetch_topology_pressure_profile_after_followup
```

## 2. Evidence Basis

| Source | Phase 1263 read |
|--------|-----------------|
| `docs/specs/ilc_werner_flow_governor_overlay_validation_1262_v0.1.md` | Werner is validated as a simulation/evidence topology-pressure profile only. The Phase 1262 verdict is `promote_to_default_sim_fetch_topology_pressure_profile_after_followup`. |
| `docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md` | Werner is a bidirectional topology-aware flow governor, not a rate limiter and not a per-request ECU toll. Runtime policy needs a future CDL, spectral trust threshold discipline, and beta/noise decomposition. |
| `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md` | Gap 11 remains open as a SIM evidence surface with no CDL/runtime policy. Gap 12 separately blocks productive-credit authorization. |
| `docs/specs/ilc_cdl_085_werner_phi_bound_opening_1172_v0.1.md` | Historical Werner CDL opening required positive SIM evidence and explicit scoped questions before prelock. |
| `docs/specs/ilc_cdl_085_prelock_spec_1177_v0.1.md` | Historical Werner prelock narrowed the bound object, expression, runtime relation, and economic-flow dependency before ratification. |
| `docs/specs/ilc_cdl_085_ratification_evidence_1185_v0.1.md` | Historical Werner ratification separated constitutional rule, runtime activation, and economic-flow activation. |
| `docs/specs/ilc_constitutional_decision_log_v0.1.md` | CDL-085 is already ratified for provenance-equivalent derivation paths; CDL-087 remains open; no fresh Werner flow-governor CDL row exists. |

## 3. Why Evidence Is Insufficient Today

The current Werner evidence is useful, but it stops at the simulation/evidence
layer. A CDL opening or prelock would need at least a concrete policy question
and a bounded artifact set. The evidence does not yet provide all of the
following:

- A committed `topology_pressure_model=werner_v1` default SIM-FETCH profile with
  `"none"` or null retained as a comparison profile.
- A profile-level artifact proving deterministic Decimal or fixed-point pressure
  arithmetic, canonical JSON exports, bounded inputs, and hard false
  authorization flags for ECU minting, ILC settlement, and public claimability.
- A beta/noise decomposition or equivalent productive-flow evidence showing how
  heat separates verified useful demand from spam, stale routing, reputation
  theater, or Sybil-like amplification.
- A spectral trust threshold packet for the flow-governor policy input:
  established-node floor, connected-enough topology check, nonzero reliable
  lambda2, largest-component safeguards, and failure behavior.
- A transport-identity binding plan for any admission or public-path effect,
  including lifecycle, revocation, replay resistance, privacy, and no fallback to
  JSON/body requester ID.
- A non-economic runtime policy skeleton that is limited to routing reputation,
  route weight, admission budget, cache priority, and mirror priority.
- A separate productive-credit authorization route before any ECU credit,
  bounty, escrow, wallet-intent, claimability, ILC settlement, or withdrawal
  semantics are considered.

Because those artifacts are missing, the safe decision is:

```text
werner_flow_governor_cdl_not_opened_without_evidence_phase_1263
```

## 4. Closing Conditions for a Future Werner CDL Opening

A later sensitive phase may reconsider a Werner flow-governor CDL opening only
after the following conditions are direct-read and satisfied or deliberately
scoped into the opening:

1. SIM-FETCH default evidence profile exists and is named explicitly, preferably
   `topology_pressure_model=werner_v1`, with deterministic comparison against a
   `"none"` profile.
2. The profile emits canonical JSON and rejects unsafe numeric input while using
   Decimal or fixed-point arithmetic for pressure fields.
3. The policy question is limited to flow control: routing reputation, routing
   weight, admission budget, cache priority, and mirror priority.
4. The opening states that heat does not directly mint ECU, settle ILC, activate
   public claimability, or authorize wallet withdrawal, transfer, or spend.
5. Spectral trust thresholds are specified before any runtime policy input.
6. Productive-flow evidence separates useful pressure from spam/noise/reputation
   theater before any policy consequence.
7. TransportPrincipal or an equivalent authenticated public-path identity plan
   is available before any non-loopback admission or public serving effect.
8. Any productive-credit or value path is routed to a separate CDL and remains
   consensus-epoch settled, not wallet-mutated or heat-mutated.

These closing conditions are deliberately stricter than a simulation pass. They
are the boundary between "useful evidence" and "constitutional policy."

## 5. Direct Werner ECU Creation Rejection

Phase 1263 explicitly rejects direct Werner ECU creation:

```text
direct_werner_ecu_creation_rejected_phase_1263
```

Heat may identify pressure and inform flow-control evidence. It does not create
ECU. ECU credit or minting authority can only arise from a separate authorized
productive-work or settlement path, with consensus-epoch settlement and the
existing economic guardrails.

The allowed policy surface for a future Werner flow-governor CDL is therefore:

- reputation evidence;
- routing weight;
- admission budget;
- cache priority;
- mirror priority;
- future evidence for a separate productive-credit authorization lane.

Allowed flow-control keywords: routing reputation, routing weight, admission
budget, cache priority, and mirror priority.

The forbidden surface remains:

- direct ECU minting from heat;
- ILC settlement from heat;
- public claimability activation;
- wallet withdrawal, transfer, or spend semantics;
- per-hop ECU micropayments for fetch or relay;
- public RC or public launch claim;
- public P2P or public sidecar/projection exposure;
- release-key generation, release envelope production, or v0.2 signing.

## 6. CDL Register Disposition

The CDL register is not mutated by Phase 1263.

No new CDL row is added, no CDL status changes, CDL-087 remains open, and
CDL-088 remains unopened.

Expected verification:

```bash
git diff -- docs/specs/ilc_constitutional_decision_log_v0.1.md
```

Expected output: empty diff.

## 7. Carry-Forward Tokens

```text
werner_flow_governor_cdl_decision_phase_1263=no_open_no_prelock
werner_flow_governor_cdl_not_opened_without_evidence_phase_1263
direct_werner_ecu_creation_rejected_phase_1263
phase_1263_sensitive_cdl_gate_complete
werner_default_topology_pressure_profile_required_before_runtime_cdl
beta_decomposition_required_before_policy_use
flow_governor_spectral_trust_threshold_required_before_policy_use
flow_governor_cdl_required_before_runtime_policy_deployment
transport_principal_identity_required_before_public_p2p
werner_productive_credit_authorization_cdl_required
ecu_credit_creation_must_be_consensus_epoch_settled_not_wallet_mutation
heat_signal_must_not_directly_mint_ecu
```

## 8. Graph Delta

```text
graph_delta=load_bearing_spec_added:docs/specs/ilc_werner_flow_governor_cdl_decision_1263_v0.1.md -> planning/werner
graph_delta=support_tests_added:tests/test_phase_1263_werner_flow_governor_cdl_decision.py -> validation
graph_delta=support_only:docs/phases/phase_1263_werner_flow_governor_cdl_decision_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
```

## 9. Next Phase

Phase 1264 is the locked window closure gate and remains sensitive:

```text
phase_1264_requires_explicit_go_for_window_closure
```
