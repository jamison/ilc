# ILC Pre-Activation Hardening Gate Report 1387 Re-Run v0.2

**Phase:** 1387 re-run
**Date:** 2026-05-19
**Status:** PASS
**Authority:** SENSITIVE gate re-run after Phase 1387-Fix remediation
**Supersedes:** `docs/specs/ilc_pre_activation_hardening_gate_report_1387_v0.1.md`

```text
pre_activation_hardening_gate_phase_1387_executed
pre_activation_hardening_gate_pass_phase_1387
phase_1387_gate_rerun_passed_after_security_disposition_fix
```

## 1. Verdict

Phase 1387 was re-run after the Phase 1387-Fix remediation chain committed the
missing project-authority security disposition artifact.

The gate now records a pass verdict. The old failed token remains historical
evidence in the original v0.1 report and STATUS entry, but it is superseded by
this re-run report.

Phase 1387a is the next required phase before Phase 1388/1389 can proceed.
Phase 1388 and Phase 1389 remain blocked until Phase 1387a records its own pass.

## 2. Gate Condition Results

| # | Gate condition | Evidence checked | Result |
|---|----------------|------------------|--------|
| 1 | Project-authority security disposition for all known HIGH findings | `docs/specs/ilc_security_disposition_phase_1387_fix_v0.1.md` | PASS — `project_authority_security_disposition_complete_phase_1387_fix` and `all_known_high_findings_dispositioned_phase_1387_fix` recorded. |
| 2 | HIGH-001 defense verified in non-loopback deployment | `docs/phases/phase_1359_high_001_two_layer_defense_walkthrough.md`; `docs/research/ilc_sim_leakage_01_run2_post_both_layers_results_779_v0.1.md`; `docs/phases/phase_1360_multi_operator_mysticeti_testnet_walkthrough.md`; Phase 1387-Fix disposition | PASS_WITH_SCOPE — log-layer defense and non-loopback evidence are present; full structural sender privacy remains explicitly unclaimed. |
| 3 | Production TLS gRPC path proven | `docs/specs/ilc_production_tls_grpc_proof_1386a_v0.1.md` | PASS — `production_tls_grpc_path_proven_phase_1386a` recorded. |
| 4 | Phase 1386b endpoint-registry ADR ratified | `docs/adr/ADR_0039_Validator_Endpoint_Registry.md`; Phase 1386b walkthrough and STATUS entries | PASS — `validator_endpoint_registry_adr_ratified_phase_1386b` recorded. |
| 5 | Phase 1386c persistent sessions proven or deferred with authority | `docs/specs/ilc_persistent_quic_connectivity_proof_1386c_v0.1.md`; `ilc_consensus/src/persistent_quic.rs` | PASS — `persistent_validator_quic_sessions_proven_phase_1386c` recorded. |
| 6 | Eight runtime hardening items addressed or deferred with authority | `docs/phases/phase_1369_fix1_numeric_hardening_walkthrough.md`; `docs/specs/ilc_production_tls_grpc_proof_1386a_v0.1.md`; `docs/specs/ilc_phase_1369_1390_sequence_lock_v0.1.md` | PASS — Phase 1369 Fix1 addresses the numeric/runtime hardening set and Phase 1386a closes the bounded `get_epoch_chain` item. |
| 7 | No hardcoded peer list in any production activation path | `docs/adr/ADR_0039_Validator_Endpoint_Registry.md`; `docs/specs/ilc_persistent_quic_connectivity_proof_1386c_v0.1.md`; `ilc_consensus/src/main.rs` | PASS — `no_hardcoded_peer_list_activation_path_confirmed_phase_1386c` recorded; `settlement_path=mysticeti_fast_path` requires `endpoint_projection_path`. |

## 3. Security Disposition Summary

The Phase 1387-Fix disposition covers the Phase 1384 security scope:

- `ilc_consensus/` BFT safety, certificate construction, epoch checkpoint handling,
  consensus networking, and settlement handoff code.
- `ilc_core/` economic surfaces affecting ECU, ILC, stake, reward, claimability,
  governance weight, or settlement state.
- HIGH-001 defense, including log-layer closure, non-loopback evidence, and the
  remaining sender-privacy non-claim boundary.

The disposition records:

```text
project_authority_security_disposition_complete_phase_1387_fix
high_001_disposition_closed_log_layer_structural_non_claim_accepted
high_002_disposition_closed_bls_threshold_fix_verified
all_known_high_findings_dispositioned_phase_1387_fix
```

MEDIUM-007 and MEDIUM-008 remain accepted carry-forward items:

- MEDIUM-007: owned-object fast-path anti-equivocation is execution-safe through
  LMDB version locks but not yet cert-level tombstone-persistent; LMDB conflict
  tombstones are required before adversarial testnet or dynamic admission.
- MEDIUM-008: endpoint edge validation is structural only; cryptographic
  verification is required before endpoint projection data is accepted from any
  external source.

These carry-forwards do not block this Phase 1387 hardening-gate pass under the
static genesis network, local projection, and no-public-activation constraints.

## 4. Claim Verification

| Claim | File or symbol checked | Result |
|-------|------------------------|--------|
| Phase 1387 prompt remains valid | `docs/antigravity_tasks/antigravity_prompt__phase_1387_g8_pre_activation_hardening_gate.md`; `tools/validate_phase_prompt.py` | confirmed |
| Original Phase 1387 failed only on missing project-authority disposition | `docs/specs/ilc_pre_activation_hardening_gate_report_1387_v0.1.md` | confirmed |
| Phase 1387-Fix disposition artifact exists | `docs/specs/ilc_security_disposition_phase_1387_fix_v0.1.md` | confirmed |
| All known HIGH findings are dispositioned | `all_known_high_findings_dispositioned_phase_1387_fix` | confirmed |
| HIGH-001 log-layer closure and structural non-claim are recorded | `high_001_disposition_closed_log_layer_structural_non_claim_accepted` | confirmed |
| HIGH-002 BLS threshold fix is closed | `high_002_disposition_closed_bls_threshold_fix_verified` | confirmed |
| TLS gRPC production read path is proven | `production_tls_grpc_path_proven_phase_1386a` | confirmed |
| Endpoint registry ADR is ratified | `validator_endpoint_registry_adr_ratified_phase_1386b` | confirmed |
| Persistent QUIC sessions are proven | `persistent_validator_quic_sessions_proven_phase_1386c` | confirmed |
| Hardcoded production peer-list activation path is removed | `no_hardcoded_peer_list_activation_path_confirmed_phase_1386c` | confirmed |

## 5. Discovery Record

| Section | Result |
|---------|--------|
| §0a known-token audit | Required prerequisite tokens were searched and direct-read. The Phase 1387-Fix disposition now exists and carries the required completion tokens. |
| §0b concept-discovery search | Broad search covered project-authority disposition, AI-assisted security review, HIGH findings, HIGH-001, AgentID redaction, non-loopback evidence, TLS gRPC, persistent QUIC, hardcoded peers, and runtime hardening. |
| §0c contradiction and non-claim search | The old v0.1 report and older planning rows still record the historical fail-closed verdict; this v0.2 report supersedes that verdict. Full sender privacy remains unclaimed. Phase 1387a/1388/1389 have not executed. |
| §0d source expansion | Direct-read the Phase 1387 prompt, original v0.1 failed report, Phase 1387-Fix disposition, Phase 1359 walkthrough, Phase 1386a proof, ADR-0039, Phase 1386c proof, Phase 1369 Fix1 walkthrough, STATUS tail, PLANNING_INDEX, sequence lock, and candidate grouping. |

## 6. Non-Authorization

This re-run authorizes only the Phase 1387 gate pass. It does not execute Phase
1387a, Phase 1388, or Phase 1389; it does not authorize CDL mutation, runtime
mutation, production validator deployment, public P2P activation, public gRPC
serving, public claimability activation, public RC claim, source publication,
release signing, wallet/ECU/ILC value-path activation, sender-privacy claim,
production transfer mixing, counsel approval, or legal conclusion.

## 7. Graph Delta

`graph_delta=load_bearing_artifact_added:docs/specs/ilc_pre_activation_hardening_gate_report_1387_rerun_v0.2.md -> pre-activation/hardening-gate`
