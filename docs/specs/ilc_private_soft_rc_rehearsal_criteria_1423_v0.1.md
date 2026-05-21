# ILC Private Soft-RC Rehearsal Entry Criteria - Phase 1423

**Status:** Criteria defined, rehearsal not activated
**Phase:** 1423
**Date:** 2026-05-21

```text
private_soft_rc_rehearsal_entry_criteria_defined_phase_1423
three_machine_seven_agent_topology_spec_defined_phase_1423
rehearsal_not_activated_phase_1423
no_live_llm_calls_in_rehearsal_spec_phase_1423
```

## Purpose

This document defines the entry criteria and private topology plan for the
first private soft-RC rehearsal: 3 machines x 7 agents. It is a rehearsal
specification only. It does not provision machines, start a live network, run
agents, write production graph state, or distribute ECU.

## Claim Verification

| Claim | File/symbol checked | Result |
|-------|---------------------|--------|
| ADR-0038 accepted token confirmed | `docs/adr/ADR_0038_Agent_Birth_Attestation.md` | confirmed: `agent_birth_attestation_adr_0038_committed_phase_1370` |
| ADR-0041 accepted token confirmed | `docs/adr/ADR_0041_Agent_INIT_and_Ingestion_Protocol.md` | confirmed: `adr_0041_agent_init_and_ingestion_protocol_accepted` |
| `agent_mode` ceremony referenced in ADR-0038 | `docs/adr/ADR_0038_Agent_Birth_Attestation.md` | confirmed |
| Three-machine/seven-agent roadmap exists | `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md` | confirmed |

## 1. Entry Criteria

The private soft-RC rehearsal may not start until all of these are true:

| Criterion | Required source |
|-----------|-----------------|
| J-008 gate PASS recorded | Phase 1427 J-008 rerun artifact records `verdict="PASS"` |
| Soft-RC eligible true | Phase 1426 soft-RC rerun records `soft_rc_eligible=true` |
| All 10 J-008 conditions MET | Phase 1427 report, after Phase 1425 static-source verification/patch |
| Launch readiness manifest schema defined | Phase 1422 schema artifact |
| Public RC activation certificate design complete | Phase 1424 design artifact |
| Rehearsal operator plan accepted | Human operator confirms machine access and wipe/reset authority before any run |

These criteria define rehearsal entry only. They do not authorize public RC,
mainnet, production jury activation, public serving, or value-path execution.

## 2. Topology

The rehearsal topology is three machines and seven agents:

| Machine | Role | Agents |
|---------|------|--------|
| M1 | Genesis machine | Genesis agent, Reviewer-1, Reviewer-2 |
| M2 | Validator-A machine | Validator-A1, Validator-A2 |
| M3 | Validator-B machine | Validator-B1, Validator-B2 |

Network path requirements:

- M1, M2, and M3 form a private operator-controlled network only.
- D2D gossip is exercised between all machine pairs: M1<->M2, M1<->M3, and
  M2<->M3.
- No public listener, public P2P claim, public fetch endpoint, public sidecar
  endpoint, or public claimability HTTP serving is enabled.
- Logs must identify machine role and scripted-agent role without printing
  secrets, identity seeds, private keys, mnemonic material, or recovery shares.

```text
three_machine_seven_agent_topology_spec_defined_phase_1423
```

## 3. Agent Identity Initialization

Each rehearsal agent must initialize through ADR-0038 and ADR-0041 semantics:

- ADR-0038 birth attestation semantics are required.
- ADR-0041 permissionless INIT semantics are required.
- CDL-042 flat namespace law and CDL-069 identity-seed derivation apply.
- `agent_id` is key-derived and must not encode parentage, machine role, or
  inviter lineage.
- Ceremony mode is `agent_mode` for scripted rehearsal agents.
- No secret seed, mnemonic, private key, recovery seed, Shamir share, or
  plaintext recovery material may be written to stdout, logs, docs,
  walkthroughs, chat transcripts, terminal scrollback, or public artifacts.
- Rehearsal identities must be marked `private_soft_rc_rehearsal_only` unless a
  later explicit authority promotes them.

## 4. Test Dataset Selection

The rehearsal dataset must be deterministic and rights-safe:

- Synthetic corpus: at least 10 knowledge nodes.
- Taxonomy coverage: at least 3 taxonomy classes.
- Lean Mathlib subset design: at most 5 theorems, selected for
  machine-verifiable proof status and compact dependency closure.
- No copyrighted verbatim content.
- External artifacts may appear only as hash, metadata, extracted claims, and
  source-span records consistent with Phase 1420.
- Dataset manifest must be canonical JSON with deterministic ordering before
  any hash or signature claim.

## 5. Wipe And Reset Rights

The rehearsal is ephemeral:

- Genesis machine M1 holds wipe authority for the rehearsal state.
- Any rehearsal participant may request reset.
- Reset request requires a recorded reason token and operator acknowledgement.
- Reset wipes rehearsal-only graph state, local receipts, temporary identity
  artifacts, script-output caches, and noncanonical logs.
- Production graph state does not persist from rehearsal.
- No rehearsal artifact becomes public-RC canon unless a later phase explicitly
  promotes it.

## 6. Scripted-Agent Behavioral Specification

All rehearsal agents are deterministic scripted agents:

- No live LLM calls.
- No external model API calls.
- No stochastic agent behavior.
- Each action is a predefined script step with an expected input, expected
  output, and expected audit token.
- The script covers INIT, birth attestation construction, T0.5 submission,
  review-lane quote, reviewer vote simulation, VRF proof verification fixture,
  anti-capture evidence check, and default-off economics quote checks.
- No economic settlement.
- No production ECU distribution.
- No wallet mutation.
- Harness pass requires all scripted steps to complete and all non-activation
  assertions to remain true.

```text
no_live_llm_calls_in_rehearsal_spec_phase_1423
```

## Non-Activation

```text
rehearsal_not_activated_phase_1423
```

Phase 1423 does not provision VPS machines, deploy live agents, start public
listeners, activate public P2P, activate public sidecar serving, activate
public claimability serving, write production graph state, distribute ECU,
execute ILC settlement, mutate wallets, mutate ledger state, mutate treasury
state, mutate registry state, mutate the CDL register, or
patch `jury_activation_gate.py`.

## Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_private_soft_rc_rehearsal_criteria_1423_v0.1.md -> private_soft_rc/rehearsal_criteria
```
