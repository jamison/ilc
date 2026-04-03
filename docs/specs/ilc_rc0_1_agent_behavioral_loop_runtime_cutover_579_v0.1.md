# ILC RC0.1 Agent Behavioral Loop Runtime Cutover Lock 579 v0.1

Date: 2026-04-03
Phase: 579
Status: Locked
Scope: RC0.1 testnet only

## 1. Bounded RC target

Phase 579 converts the already-landed bounded seven-agent helper path into the
explicitly verified authoritative runtime cutover path over the three-machine
RC0.1 substrate.

Locked points:
- `agent_behavioral_loop_runtime_cutover_authoritative`
- `bounded_helper_surface_no_longer_sufficient_for_phase_579`
- `phase_579_cutover_reads_locked_576_577_578_surfaces`
- `seven_live_agent_submissions_required_for_cutover`
- `panel_and_claim_broadcasts_must_complete_before_cutover_pass`
- `phase_579_keeps_transport_and_wallet_semantics_unchanged`
- `scenario_manifest_output_root_and_identity_must_match_cutover_root`
- `panel_direct_author_must_match_direct_claim`

This packet does not invent new wallet, settlement, graph, or lineage meaning.
It hardens an existing bounded runtime baseline against the already-locked Phase
576, 577, and 578 boundaries.

## 2. Authoritative runtime surfaces

The authoritative cutover surfaces for Phase 579 are:
- `tools/agent_loop_v1.py`
- `tools/testbed/run_three_node_seven_agent_scenario.py`
- `tools/testbed/check_phase_579_agent_runtime_cutover.py`
- `tools/testbed/run_phase_579_agent_runtime_cutover.py`
- `tools/query_rc0_1_economic_state.py`

The cutover proof must consume and verify these live runtime artifacts:
- seven `agent_loop_submission_ok` submission artifacts
- one `agent_loop_panel_ok` panel artifact
- one `agent_loop_claims_ok` ECU claim artifact
- one `economic-state/manifest.json` durable economic-state artifact
- one machine-legible `phase_579_cutover_manifest.json`

The authoritative runtime identity tuple remains:
- `task_id`
- `epoch`
- normalized `channel`
- `node_name`
- `cluster_id`
- `variant`
- `runtime_version`

## 3. Deterministic cutover proof contract

A passing Phase 579 cutover requires all of the following:
- seven submission artifacts exist and are structurally valid
- each submission uses `gossip_type = agent_submission`
- each submission runtime version equals the active
  `AGENT_LOOP_V1_RUNTIME_VERSION`
- each submission matches the authoritative scenario identity tuple
- each submission send-status row exists and every status code is `202`
- the panel artifact is passing and aligned to the authoritative scenario
- the scenario manifest output root, task id, and epoch align with the live
  cutover root
- the standalone claim artifact matches the panel claim batch, preserves the
  panel-selected direct author, and has positive settled reward total
- panel and claim broadcasts both complete with `202` statuses only
- the scenario manifest points to an existing durable economic manifest
- the economic manifest aligns with the same scenario root, task id, and reward
  total as the live runtime artifacts

The success marker is:
- `phase_579_agent_cutover_ok`

Required failure tokens are:
- `phase_579_manifest_missing`
- `phase_579_manifest_invalid`
- `phase_579_submission_count_invalid`
- `phase_579_submission_runtime_version_mismatch`
- `phase_579_submission_identity_mismatch`
- `phase_579_submission_delivery_incomplete`
- `phase_579_panel_result_invalid`
- `phase_579_claim_batch_invalid`
- `phase_579_economic_manifest_missing`

## 4. Runtime boundary and non-goals

Phase 579 does not widen the protocol boundary.

It must not:
- redefine Phase 576 settlement or wallet meaning
- redefine Phase 577 persisted graph records
- redefine Phase 578 curated lineage or promotion posture
- reopen D2D transport governance
- introduce public admission or public-release lineage rules
- treat helper projections as authoritative instead of runtime artifacts

Phase 579 exists to prove that the live three-machine runtime path can be
checked deterministically without manual interpretation.

## 5. Carry-forward into Phase 580 and Phase 581

Phase 579 is complete when the live runtime cutover proof is authoritative and
machine-legible, not when panel and wallet semantics are fully public-facing.

Carry-forward rules:
- Phase 580 may harden panel/quorum submission flow only after Phase 579 cutover
  proof passes.
- Phase 581 may harden ECU attribution, settlement, and wallet query runtime
  only after Phase 579 proves live artifact identity and delivery integrity.
- Phase 579 does not authorize public-release minting or claimability
  statements.

Explicit deferrals beyond Phase 579:
- public-release minting semantics
- spend, transfer, or withdrawal wallet semantics
- permissionless public admission
- transport redesign beyond the current RC0.1 substrate
