# ILC Pre-Activation Hardening Gate Report 1387 v0.1

**Phase:** 1387
**Date:** 2026-05-18
**Status:** FAILED CLOSED
**Authority:** SENSITIVE gate report only

```text
pre_activation_hardening_gate_phase_1387_executed
pre_activation_hardening_gate_failed_phase_1387
gate_failed_reason=project_authority_security_disposition_missing
```

## 1. Verdict

Phase 1387 executed the pre-activation hardening gate and records a fail-closed
verdict.

Phase 1388 must not proceed because the first required gate condition is not
confirmed: the repository does not contain a committed project-authority
security disposition document for every known HIGH-severity finding in the
Phase 1384 scope.

The successful-outcome token is intentionally not written in this report.

## 2. Gate Condition Results

| # | Gate condition | Evidence checked | Result |
|---|----------------|------------------|--------|
| 1 | Project-authority security disposition for all known HIGH findings | `docs/specs/ilc_security_review_scope_1384_v0.1.md`; repo-wide search for project-authority security disposition artifacts | **FAIL** — Phase 1384 is scope-only and explicitly says it does not conduct the review or close HIGH findings; no committed disposition artifact was found. |
| 2 | HIGH-001 defense verified in non-loopback deployment | `docs/phases/phase_1359_high_001_two_layer_defense_walkthrough.md`; `docs/research/ilc_sim_leakage_01_run2_post_both_layers_results_779_v0.1.md`; `docs/phases/phase_1360_multi_operator_mysticeti_testnet_walkthrough.md` | PASS_WITH_SCOPE — log-layer AgentID redaction is verified, non-loopback private testnet evidence exists, and full sender-privacy remains explicitly unclaimed. |
| 3 | Production TLS gRPC path proven | `docs/specs/ilc_production_tls_grpc_proof_1386a_v0.1.md` | PASS — `production_tls_grpc_path_proven_phase_1386a` recorded. |
| 4 | Phase 1386b endpoint-registry ADR ratified | `docs/adr/ADR_0039_Validator_Endpoint_Registry.md`; Phase 1386b walkthrough and STATUS entries | PASS — `validator_endpoint_registry_adr_ratified_phase_1386b` recorded. |
| 5 | Phase 1386c persistent sessions proven or deferred with authority | `docs/specs/ilc_persistent_quic_connectivity_proof_1386c_v0.1.md`; `ilc_consensus/src/persistent_quic.rs` | PASS — `persistent_validator_quic_sessions_proven_phase_1386c` recorded. |
| 6 | Eight runtime hardening items addressed or deferred with authority | `docs/phases/phase_1369_fix1_numeric_hardening_walkthrough.md`; `docs/specs/ilc_production_tls_grpc_proof_1386a_v0.1.md`; `docs/specs/ilc_phase_1369_1390_sequence_lock_v0.1.md` | PASS — Phase 1369 Fix1 addresses the numeric/runtime hardening set and Phase 1386a closes the bounded `get_epoch_chain` item. |
| 7 | No hardcoded peer list in any production activation path | `docs/adr/ADR_0039_Validator_Endpoint_Registry.md`; `docs/specs/ilc_persistent_quic_connectivity_proof_1386c_v0.1.md`; `ilc_consensus/src/main.rs` | PASS — `no_hardcoded_peer_list_activation_path_confirmed_phase_1386c` recorded; `settlement_path=mysticeti_fast_path` now requires `endpoint_projection_path`. |

## 3. Claim Verification

| Claim | File or symbol checked | Result |
|-------|------------------------|--------|
| Phase 1387 prompt is valid and executable after explicit human GO | `docs/antigravity_tasks/antigravity_prompt__phase_1387_g8_pre_activation_hardening_gate.md`; `tools/validate_phase_prompt.py` | confirmed |
| Phase 1384 scope record exists | `docs/specs/ilc_security_review_scope_1384_v0.1.md` | confirmed |
| Phase 1384 scope record is not a disposition artifact | `docs/specs/ilc_security_review_scope_1384_v0.1.md` §§1, 4, 5, 7 | confirmed |
| Project-authority security disposition artifact exists | repo-wide searches for `project-authority security disposition`, `security disposition`, `HIGH-severity`, `high_severity_unaddressed`, and disposition file names | not found |
| HIGH-001 log-layer defense exists | `docs/phases/phase_1359_high_001_two_layer_defense_walkthrough.md` | confirmed |
| Non-loopback private testnet evidence exists | `docs/research/ilc_sim_leakage_01_run2_post_both_layers_results_779_v0.1.md`; `docs/phases/phase_1360_multi_operator_mysticeti_testnet_walkthrough.md` | confirmed |
| Full sender privacy is not claimed | Phase 1359 walkthrough; Phase 779 leakage results | confirmed |
| TLS gRPC production read path is proven | `docs/specs/ilc_production_tls_grpc_proof_1386a_v0.1.md` | confirmed |
| Endpoint registry ADR is ratified | `docs/adr/ADR_0039_Validator_Endpoint_Registry.md` | confirmed |
| Persistent QUIC sessions are proven | `docs/specs/ilc_persistent_quic_connectivity_proof_1386c_v0.1.md` | confirmed |
| Hardcoded production peer-list activation path is removed | Phase 1386c proof and Rust `settlement_path=mysticeti_fast_path` config guard | confirmed |

## 4. Discovery Record

| Section | Result |
|---------|--------|
| §0a known-token audit | Required prerequisite tokens were searched and direct-read. Phase 1384, 1386a, 1386b, 1386c, 1369 Fix1, and 1359 evidence tokens are present. |
| §0b concept-discovery search | Broad search covered project-authority disposition, AI-assisted security review, HIGH findings, HIGH-001, AgentID redaction, non-loopback/Tailscale evidence, TLS gRPC, persistent QUIC, hardcoded peers, and runtime hardening. |
| §0c contradiction and non-claim search | Found explicit non-claims: Phase 1384 is scope-only; Phase 1359 does not claim full sender privacy; Phase 779 still records structural sender-privacy failures; no Phase 1387 pass token exists. |
| §0d source expansion | Direct-read the Phase 1387 prompt, Phase 1384 scope record, Phase 1359 walkthrough, Phase 779 results, Phase 1360 walkthrough, Phase 1369 Fix1 walkthrough, Phase 1386a proof, ADR-0039, Phase 1386c proof, STATUS tail, PLANNING_INDEX, sequence lock, and candidate grouping. MemPalace tier-b returned no superseding current-worktree artifact. |

## 5. Required Fix Routing

The next remediation phase must produce a committed project-authority security
disposition artifact before Phase 1387 can be re-run or superseded by a passing
gate.

That artifact must cover the Phase 1384 surfaces:

- `ilc_consensus/` BFT safety, including certificate construction, epoch
  checkpoint handling, consensus networking, and settlement handoff code.
- `ilc_core/` economic surfaces that can affect ECU, ILC, stake, reward,
  claimability, governance weight, or settlement state.
- HIGH-001 defense, including log-layer defense, non-loopback evidence, and the
  remaining sender-privacy non-claim boundary.

The disposition must explicitly mark every known HIGH finding as closed,
accepted, or deferred with rationale and bounded carry-forward authority.

## 6. Non-Authorization

Phase 1387 does not authorize Phase 1388, Phase 1389, CDL mutation, runtime
mutation, production validator deployment, public P2P activation, public gRPC
serving, public claimability activation, public RC claim, source publication,
release signing, wallet/ECU/ILC value-path activation, sender-privacy claim,
production transfer mixing, counsel approval, or legal conclusion.

## 7. Graph Delta

`graph_delta=load_bearing_artifact_added:docs/specs/ilc_pre_activation_hardening_gate_report_1387_v0.1.md -> pre-activation/hardening-gate`
