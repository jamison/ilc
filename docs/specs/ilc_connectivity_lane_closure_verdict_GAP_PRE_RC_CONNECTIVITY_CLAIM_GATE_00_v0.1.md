# ILC Pre-RC Connectivity Lane Closure Verdict

Version: v0.1
Phase: GAP-PRE-RC-CONNECTIVITY-CLAIM-GATE-00
Date: 2026-09-03
Status: PASS
Executor: Codex
Authority: human GO phrase received: `GO Phase GAP-PRE-RC-CONNECTIVITY-CLAIM-GATE-00 CONNECTIVITY-LANE-CLOSED`

## Verdict

PASS. The Part 3l pre-RC connectivity lane is closed.

All 29 required Part 3l, package, bridge, deployment, and smoke input tokens are present in `docs/phases/STATUS.md`. The output token was absent from `STATUS.md` before execution. Runtime guard state is correct for the pre-RC boundary:

```text
PROBE_GUARD: False
RELAY_GUARD: False
CA_GUARD: True
```

This means connectivity probing and relay client operation are active, while CDL-112 connectivity advertisement propagation remains guarded because CDL-112 is opened but not ratified.

## Relay Health

Public relay health checks passed for all three live relay hosts:

```text
## 164.90.201.11
{"active_slot_count":1,"data_plane":{"active_slot_count":1,"active_udp_ports":[52000],"enabled":true,"last_error_counts":{},"total_counters":{"claim_only_datagrams":0,"client_to_target_forwarded":0,"datagrams_received":0,"nonce_claims_accepted":0,"nonce_mismatch_drops":0,"nonce_prefixed_payloads":0,"sendto_failures":0,"sendto_successes":0,"target_to_client_forwarded":0,"unknown_sender_drops":0}},"data_port_range_end":52999,"data_port_range_start":52000,"ilc_core_version":"0.4.12","relay_agent_id":"b04db7ea3767813769789bf48f9bbb128c12495137854f84f961ce72b0d1d7280ef15ac7bdd2a81c81a39ab1c6e6d8dc","schema_version":"relay_server_GAP_RELAY_SERVER_IMPL_00.v0.1","server_guard_active":false}
## 64.227.70.134
{"active_slot_count":1,"data_plane":{"active_slot_count":1,"active_udp_ports":[52000],"enabled":true,"last_error_counts":{},"total_counters":{"claim_only_datagrams":0,"client_to_target_forwarded":0,"datagrams_received":0,"nonce_claims_accepted":0,"nonce_mismatch_drops":0,"nonce_prefixed_payloads":0,"sendto_failures":0,"sendto_successes":0,"target_to_client_forwarded":0,"unknown_sender_drops":0}},"data_port_range_end":52999,"data_port_range_start":52000,"ilc_core_version":"0.4.12","relay_agent_id":"829316f5202c81e16a9f70e1687aa1588a7a3c385b873191453b9af6304017f98aae26f13cd5f4d2a32a13ea34516cdc","schema_version":"relay_server_GAP_RELAY_SERVER_IMPL_00.v0.1","server_guard_active":false}
## 167.99.45.238
{"active_slot_count":0,"data_plane":{"active_slot_count":0,"active_udp_ports":[],"enabled":true,"last_error_counts":{},"total_counters":{"claim_only_datagrams":0,"client_to_target_forwarded":0,"datagrams_received":0,"nonce_claims_accepted":0,"nonce_mismatch_drops":0,"nonce_prefixed_payloads":0,"sendto_failures":0,"sendto_successes":0,"target_to_client_forwarded":0,"unknown_sender_drops":0}},"data_port_range_end":52999,"data_port_range_start":52000,"ilc_core_version":"0.4.12","relay_agent_id":"8227692815f26f96fd17964c29cc38e72450bed4953f63d0ebb756f653d5300cd0f2a6a8f9039ba3347fca11435016f8","schema_version":"relay_server_GAP_RELAY_SERVER_IMPL_00.v0.1","server_guard_active":false}
```

## Connectivity Smoke Evidence

The recorded `GAP-INSTALL-CONNECTIVITY-SMOKE-00` evidence confirms the fresh install path is not `local_only`:

```json
{
  "bare_network_doctor_disposition": "followup_ux_gap_not_install_path_failure",
  "bare_network_doctor_result": "local_only_relay_server_url_missing",
  "bootstrap_peer_hints_count": 1,
  "clean_home": "/tmp/ilc-connectivity-smoke-0412-final/home",
  "connectivity_receipt_mode": "relay_reachable",
  "install_receipt_connectivity_mode": "relay_reachable",
  "install_success": true,
  "known_peer_hints_verified": 1,
  "onboarding_connectivity_mode": "relay_reachable",
  "onboarding_software_version": "0.4.12",
  "post_install_network_doctor_with_material": "relay_reachable",
  "relay_endpoint": "164.90.201.11:52000",
  "remote_host": "ilc-node-6",
  "validator_participation_enabled": true,
  "version": "0.4.12"
}
```

The bare `ilc network-doctor` UX carry-forward remains non-blocking for this gate because the one-shot install path and explicit relay diagnostic both passed with `relay_reachable`.

## Taxonomy And CDL Boundary

Direct read of `docs/specs/ilc_connectivity_path_taxonomy_GAP_CONNECTIVITY_RECONCILE_00_v0.1.md` confirms the canonical 9-mode table:

```text
local_only
outbound_only
nat_traversed_direct
relay_reachable
direct_public
validator_observer_relay
validator_observer_direct
validator_direct
validator_relay
```

The prompt's raw grep command returned `13` because mode strings appear in both the canonical table and transition prose. The direct-read table check confirms there are exactly nine canonical modes.

`docs/specs/ilc_constitutional_decision_log_v0.1.md` contains the CDL-112 opened row with `guard_status: CONNECTIVITY_ADVERTISEMENT_NOT_ACTIVATED=True_pending_impl`. This gate does not ratify CDL-112 and does not clear that guard.

## Closure Effect

This gate emits:

```text
pre_rc_connectivity_claim_gate_passed_GAP_PRE_RC_CONNECTIVITY_CLAIM_GATE_00
```

This unblocks the next signed bootstrap-capsule and downstream public-RC version/signing lanes. It does not itself authorize public-RC publication or launch.

## Non-Claims

- This gate does not ratify CDL-112.
- This gate does not clear `CONNECTIVITY_ADVERTISEMENT_NOT_ACTIVATED`.
- This gate does not activate CDL-078 serving rewards.
- This gate does not push to the public mirror.
- This gate does not publish a PyPI package.
- This gate does not sign a Genesis relay bootstrap capsule.
- This gate does not constitute public-RC launch authority.
- This gate does not execute epoch transition, settlement, production minting, or public network launch.
