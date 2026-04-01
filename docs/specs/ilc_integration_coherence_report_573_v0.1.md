# ILC Integration Coherence Report 573 v0.1

Status: synthesis report
Date: 2026-04-01
Owner lane: G8 implementation cluster

## 1. Window 565-574 implementation summary

Window 565-574 is coherent through Phase 573.

Phase 565 sequence-locked the three-machine transport and packaging lane.
Phase 566 bounded the runtime to a minimal HTTP transport wrapper.
Phase 567 locked JSON static peer config, test-grade genesis import, and
minimum persistence. Phases 568-571 implemented the real HTTP transport
wrapper, startup wiring, and `venv + systemd` lifecycle surface. Phase 572
published the deterministic smoke harness and recorded the operator-guided
external proof path.

`three_machine_transport_wrapper_lane_complete`

The transport wrapper lane is complete in code and bounded to the explicit
`kind=http` proof lane while preserving ADR-0025 `kind=quic` as the production
binding.

## 2. JSON config, startup, and genesis coherence

`json_static_peer_config_and_startup_lane_complete`

The startup lane is complete with JSON operator config, normalized duplicate
peer rejection at the loader boundary, relative path resolution for TLS
material, and test-grade genesis import reference loading through
`build_node_startup_context(...)`.

## 3. Packaging and lifecycle coherence

`venv_systemd_testbed_packaging_lane_complete`

The packaging lane is complete for the testbed target. `run_ilc_node_service_v1`
provides deterministic lifecycle markers and exit codes, while
`deploy/systemd/ilc-node-v1.service` establishes the reproducible `venv +
systemd` operator path required by the window.

## 4. Smoke gate evidence

`three_machine_smoke_gate_complete`

The deterministic local three-node smoke proof is complete and the recorded
operator-guided proof contract is present under the required
`phase_572_real_three_machine_operator_proof_recorded` token. This keeps the
window grounded in real runtime and lifecycle evidence rather than scaffold
counts.

## 5. Deferred lanes after Phase 573

`http_machine_payment_skill_deferred_to_575_584`

The outbound HTTP machine-payment skill lane remains deferred to Window 575-584.

`http_machine_payment_ingress_deferred_to_595_plus`

The inbound HTTP machine-payment ingress lane remains deferred to Window 595+ so
that launch-critical transport work stays separate from treasury-governed
inbound payment design.

`multi_hop_still_deferred_after_573`

Multi-hop remains deferred under `sim_multi_hop_01_insufficient`.

`full_node_orchestration_redesign_still_pending`

The full node-orchestration redesign remains pending after this window. The
current wrapper/startup/service split is an intentional seam, not the final
public-release runtime shape.

## 6. Priority order after Window 565-574 closes

The next priority order remains:
1. Window 575-584 agent behavioral loop implementation and 7+1 panel wiring
2. outbound HTTP machine-payment skill lane
3. Window 585-594 deterministic RC0 public release-candidate integration pass
4. post-RC0 hardening tranche for mTLS, automatic fallback, and stronger
   packaging/orchestration
