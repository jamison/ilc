# Phase 1322 Three-Machine Seven-Agent Private Deployment Rehearsal

```text
three_machine_seven_agent_private_deployment_rehearsal_phase_1322.v0.1
essential_graph_native_sidecar_suite_private_deployment_rehearsed_phase_1322
private_wiring_only_no_public_serving_phase_1322
digitalocean_openclaw_private_test_evidence_recorded_phase_1322
identity_artifact_creation_stop_guard_phase_1322
phase_1323_openclaw_nemoclaw_claimable_profile_dry_run_next
public_rc_remains_blocked_after_phase_1322
```

## 1. Result

Phase 1322 executed a live private rehearsal over three DigitalOcean droplets
connected through Tailscale:

| Node | Tailscale IP | Phase role |
|------|--------------|------------|
| ilc-node-2 | `100.112.32.42` | coordinator |
| ilc-node-3 | `100.91.33.46` | verifier/projection |
| ilc-node-6 | `100.72.17.38` | harness-adapter |

The declared evidence outcome is `executed_live_private_droplet`.

The rehearsal did not start public ILC listeners, public P2P, public sidecar
serving, public claim endpoints, source publication, release authority, signing,
wallet writes, ECU minting, or ILC settlement.

## 2. Topology

| Machine role | Agent role | Network mode | Public exposure | Secret handling | Evidence path |
|---------------|------------|--------------|-----------------|-----------------|---------------|
| coordinator | sidecar registry | tailscale_private_overlay | none_for_ilc_role | no secret read | remote role check on ilc-node-2 plus this report |
| coordinator | TransportPrincipal admission | tailscale_private_overlay | none_for_ilc_role | no secret read | remote role check on ilc-node-2 plus this report |
| verifier/projection | verifier | tailscale_private_overlay | none_for_ilc_role | no secret read | remote role check on ilc-node-3 plus this report |
| verifier/projection | projection | tailscale_private_overlay | none_for_ilc_role | no secret read | remote role check on ilc-node-3 plus this report |
| harness-adapter | wallet-facing preflight | tailscale_private_overlay | none_for_ilc_role | no secret read | remote role check on ilc-node-6 plus this report |
| harness-adapter | value-path preflight | tailscale_private_overlay | none_for_ilc_role | no secret read | remote role check on ilc-node-6 plus this report |
| harness-adapter | harness bridge | tailscale_private_overlay | none_for_ilc_role | no secret read | remote role check on ilc-node-6 plus this report |

The topology maps exactly three machine roles and seven agent roles.

## 3. Live Evidence

Private overlay reachability passed:

| Node | Private reachability |
|------|----------------------|
| ilc-node-2 | `ping_node3=ok`; `ping_node6=ok` |
| ilc-node-3 | `ping_node2=ok`; `ping_node6=ok` |
| ilc-node-6 | `ping_node2=ok`; `ping_node3=ok` |

Sidecar role checks passed:

| Node | Role evidence |
|------|---------------|
| ilc-node-2 | Registry manifest validated at `graph_native_sidecar_registry_manifest_phase_1307.v0.1`; TransportPrincipal admission manifest is local-only with public P2P and public sidecar serving disabled. |
| ilc-node-3 | Offline claimability verifier manifest is local-only with public API and public claimability disabled; local graph/memory projection manifest is local-only with public listener and public sidecar projection serving disabled; local centrality query returned bounded projection keys. |
| ilc-node-6 | Wallet-facing and value-path preflight packets validated as preflight-only with wallet write and ILC settlement disabled; local skill preview returned `local_import_only` and public P2P disabled. |

Firewall state was tightened during the phase. Each node started with public
`22/tcp` UFW allow rules. After confirming Tailscale SSH reachability, those
public SSH allow rules were removed. Each node now has only inbound UFW allow
rules on `tailscale0`.

System infrastructure listeners observed: `sshd`, `tailscaled`, and
`systemd-resolved`. No ILC sidecar, P2P, claimability, verifier, projection, or
wallet/value-path public listener was started.

## 4. Operational Findings

Remote trees under `/opt/ilc/current` are rsynced working trees without `.git`.
`tools/testbed/sync_repo.sh` therefore remains unsuitable for these nodes until
the remote clone/deploy-key issue is resolved or the testbed tooling grows an
explicit rsync mode.

The remote Ubuntu 22.04 venvs use Python 3.10. `ilc_core` import initially
failed because `ilc_core/ledger/backend.py` imported `NotRequired` from
`typing`. Phase 1322 added a Python 3.10 fallback to import `NotRequired` from
`typing_extensions` when needed and synced that single file to all three remote
working trees. Sidecar imports passed afterward.

Local `~/.ssh/config` aliases for `ilc-node-2` and `ilc-node-3` still pointed at
stale Tailscale IPs during the run. Commands used explicit supplied Tailscale
IPs, and `testbed/hosts.json` now uses explicit Tailscale IPs for all three
`ssh_host` fields.

## 5. Identity Artifact Stop Guard

Before execution, Phase 1322 checked that the rehearsal path does not create or
write any identity artifact, genesis record, seed commitment,
`identity_seed_commitment`, or dummy Agent Birth artifact.

Result: `pass_no_identity_artifact_created_or_written`.

If any such artifact is identified in a later run, the rehearsal must stop until
the CDL-069 commitment-formula mismatch is resolved by an explicit audit/fix
phase.

## 6. Non-Claims

Phase 1322 does not authorize or claim public RC, public launch, source export,
source publication, package publication, clean public tree materialization,
release artifact production, release-key generation, release envelope
production, signing, public claimability/API activation, public verifier
service, public claim endpoint activation, public P2P, public fetch serving,
public ILC listener, public sidecar/projection serving, peer discovery, public
confidential coordination serving, wallet writes, wallet withdrawal/transfer/
spend, ECU minting, ILC settlement, value-path activation, identity artifact
creation, Genesis Atlas mutation/signing, v0.2 signing, CDL mutation, or CDL-088
opening.

`public_rc_remains_blocked_after_phase_1322`.

## 7. Next

`phase_1323_openclaw_nemoclaw_claimable_profile_dry_run_next`.

Before Phase 1323 depends on remote updates, either fix remote Git deploy-key
auth or add an explicit rsync mode to the testbed tooling. Phase 1323 must also
continue to treat OpenClaw/NemoClaw as harnesses, not protocol substrates, and
must not claim skill publication/installability or identity-seed UX completion.

Graph delta:

```text
graph_delta=load_bearing_artifact_changed:ilc_core/ledger/backend.py -> testbed/runtime-python-3.10-compatibility
graph_delta=support_only:testbed/hosts.json,docs/specs/ilc_three_machine_seven_agent_private_deployment_rehearsal_1322_v0.1.json,docs/specs/ilc_three_machine_seven_agent_private_deployment_rehearsal_1322_v0.1.md,docs/phases/phase_1322_three_machine_seven_agent_private_deployment_rehearsal_walkthrough.md -> planning/frontier
```
