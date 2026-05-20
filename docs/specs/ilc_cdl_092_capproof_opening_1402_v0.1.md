# ILC CDL-092 CapProof Opening 1402 v0.1

Phase: 1402
Date: 2026-05-20
Status: open

```text
cdl_092_capproof_opened_phase_1402
cdl_092_not_ratified_phase_1402
cdl_092_deliberation_questions_recorded_phase_1402
```

## 1. Purpose

CDL-092 opens the constitutional lane for CapProof content-addressing,
Capability Vector signing, and the bounded +/-15% ECU pricing band.

This phase does not ratify CDL-092 and does not activate CapProof pricing,
runtime probes, public RC, ECU settlement, ILC minting, validator reward
distribution, wallet behavior, or production jury activation.

## 2. Claim Verification Table

| Claim | File or symbol checked | Result |
|-------|------------------------|--------|
| CDL-091 is ratified before CDL-092 opening | `docs/specs/ilc_constitutional_decision_log_v0.1.md` row `CDL-091` | confirmed |
| CDL-092 is absent before Phase 1402 register mutation | `docs/specs/ilc_constitutional_decision_log_v0.1.md` before C2 | confirmed |
| J-005 records CapProof as readiness, routing, and ECU-pricing signal only | `docs/specs/ilc_epoch_start_capability_maintenance_contract_v0.1.md` | confirmed |
| CapProof has historical design/spec scaffold but is not implemented or ratified | `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md`; `ilc_core/mining/benchmark.py`; `ilc_core/cli/main.py` | confirmed |
| CapProof never directly mints or awards ILC | `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md` section 6.1; J-005 contract | confirmed |
| ADR-0038 provides the Genesis-rooted agent birth-attestation identity anchor | `docs/adr/ADR_0038_Agent_Birth_Attestation.md` | confirmed |
| J-008 blocks production jury activation on unratified CapProof CDL | `ilc_core/epistemic/jury_activation_gate.py` condition `CAPPROOF_CDL_RATIFIED` | confirmed |

Discovery correction: Phase 1402 does not claim "no CapProof code exists."
The codebase contains historical CLI/benchmark scaffold and protocol-bundle
schema references. The missing authority is the CDL-092 constitutional rule for
content-addressing, CV signing, and the pricing band, plus any later production
runtime activation.

## 3. Inherited Canon

### J-005 Boundary

The following J-005 tokens are inherited as canon:

```text
epoch_start_capability_maintenance_contract_phase_j005
capproof_no_direct_ilc_reward_boundary_confirmed
awp_iih_depends_on_capproof_infrastructure_confirmed
activation_ladder_shadow_to_production_defined_phase_j005
```

CapProof is a readiness, routing, scheduling, and ECU-pricing signal. The five
standardized probes are:

- `GEMMProbe`
- `InferProbe`
- `GraphProbe`
- `BandwidthProbe`
- `DeterminismProbe`

The probes produce a signed Capability Vector. The Capability Vector may affect
ECU pricing and queue placement within a bounded +/-15% band after later
ratification and activation. It must not directly affect ILC rewards.

### ADR-0038 Identity Anchor

ADR-0038 records:

```text
adr_0038_agent_birth_attestation_genesis_rooted
```

For CDL-092 purposes, any future Capability Vector signing chain must bind the
Capability Vector signer to a Genesis-rooted agent identity lineage. This opening
does not decide the final chain format; it records ADR-0038 as the anchor that
Phase 1403 must use when resolving Q2.

### J-008 Gate Dependency

J-008 records `CAPPROOF_CDL_RATIFIED` as a blocking NOT_MET condition. Phase 1402
opens the CDL track that may later satisfy that condition, but the J-008 gate
must remain incomplete until CDL-092 is ratified and any required runtime/gate
code is explicitly updated.

## 4. CDL-092 Scope

CDL-092 is scoped to:

- CapProof content-addressing for probe suites, probe inputs, probe outputs, and
  Capability Vector payloads.
- Capability Vector signing chain back to the ADR-0038/ADR-0037
  Genesis-rooted identity lineage.
- The exact application rule for the +/-15% ECU-pricing band.
- Applicability boundaries for CapProof-covered work types.
- Carry-forward conditions for Genesis-baseline transition and spot-recheck
  design, if the deliberation phase routes them forward.

CDL-092 does not amend CDL-047 treasury governance, CDL-054 validator reward
framework, CDL-088 public claimability authority, CDL-091 reviewer incentive
economics, or public launch packaging law.

## 5. Deliberation Questions

The following questions are explicitly opened for Phase 1403 deliberation:

| ID | Question | Initial boundary |
|----|----------|------------------|
| Q1 | What fields constitute the CapProof content-address input? | Must consider CV hash, probe-suite hash, probe-input hash, probe-output hash, agent identity binding, epoch or scope binding, environment declaration, and canonical serialization. |
| Q2 | How does the Capability Vector signing chain anchor to ADR-0038 birth attestation? | Must bind the CV signer to an ADR-0038-compliant agent birth attestation or authorized recovery/rotation chain without exposing private key material. |
| Q3 | What is the exact +/-15% ECU pricing band application rule? | Must define additive vs. multiplicative adjustment, Decimal or fixed-point arithmetic, floor/ceiling order, and interaction with existing price clamps. |
| Q4 | Does CapProof apply to all ECU-earning work types or only specific lane types? | Must distinguish scheduling/routing, reviewed maintenance tasks, reviewer work, shard-specific work, and production validator/BFT lanes. |

```text
cdl_092_deliberation_questions_recorded_phase_1402
```

## 6. Non-Authorizations

Phase 1402 does not authorize:

- CDL-092 ratification;
- CapProof pricing activation;
- CapProof probe execution in production;
- public RC publication;
- public CapProof API exposure;
- direct ILC reward or minting from CapProof;
- ECU settlement or ledger writes from CapProof;
- wallet signing, wallet transfer, or wallet withdrawal behavior;
- validator reward distribution;
- reviewer payment activation;
- production jury activation;
- J-008 gate verdict changes;
- VRF spot-recheck implementation;
- runtime use of wall-clock time as protocol time.

## 7. Carry-Forward

Phase 1403 must resolve or explicitly route Q1-Q4. CDL-092 remains open and
unratified after Phase 1402:

```text
cdl_092_not_ratified_phase_1402
```

The expected sequence is:

1. Phase 1402 opens CDL-092.
2. Phase 1403 resolves the deliberation questions.
3. Phase 1404 prelocks CDL-092 scope constants.
4. Phase 1405 ratifies CDL-092 if prelock evidence is sufficient and explicit
   sensitive authorization is provided.

Graph delta:
`graph_delta=load_bearing_artifact_added:docs/specs/ilc_cdl_092_capproof_opening_1402_v0.1.md -> constitutional/cdl`.
