# ILC CCSS-005 Private OpenClaw/NemoClaw Droplet Dry Run

**Phase:** 1328
**Status:** Passed as private droplet evidence only
**Version token:** `ccss_005_private_openclaw_nemoclaw_droplet_dry_run_phase_1328.v0.1`

## Purpose

Phase 1328 records the CCSS-005 private OpenClaw/NemoClaw-compatible droplet dry run. It proves the confidential coordination local-preview profile can be rehearsed on real private DigitalOcean/Tailscale hosts with OpenClaw visible on the harness node and CCSS-001 through CCSS-004 record construction reproducible across all three machines.

This is not a public serving activation. It does not create public P2P, public sidecar serving, public confidential coordination serving, public confidential messaging, public claimability, public skill publication, ClawHub listing, source publication, release material, signing, identity artifacts, wallet writes, ECU minting, ILC settlement, or value-path activation.

## Live Topology

| Host | Role | Tailscale IP | Result |
|---|---|---:|---|
| `ilc-node-2` | Coordinator | `100.112.32.42` | Pass |
| `ilc-node-3` | Verifier/projection | `100.91.33.46` | Pass |
| `ilc-node-6` | Harness adapter / OpenClaw node | `100.72.17.38` | Pass |

All three remote Git worktrees were clean and fast-forwarded to committed source `acc92d645055c4ea288aad947df0f54604975fc6` using a private Git bundle over Tailscale. No GitHub push or source publication was performed as part of this phase.

Full mesh Tailscale reachability passed in all six directions.

## Private Wiring Evidence

Every node reported:

| Check | Result |
|---|---|
| Python runtime | `Python 3.10.12` |
| UFW posture | active, default deny incoming, allow incoming only on `tailscale0` |
| OpenClaw gateway ports `18789` / `19001` | no listeners observed |
| CCSS deterministic sample construction | pass |
| Registry public flags | all false |

The `ss -ltn` probe observed normal SSH, loopback DNS, and Tailscale daemon listeners. UFW remained the authority boundary for public ingress and allowed inbound traffic only on `tailscale0`.

## OpenClaw Harness Evidence

OpenClaw was installed only on `ilc-node-6`:

```text
OpenClaw 2026.5.7 (eeef486)
```

`openclaw skills info ilc-local` reported the local workspace skill as ready, model-visible, command-visible, and backed by:

```text
~/.openclaw/workspace/skills/ilc-local/SKILL.md
```

The skill remained a local workspace draft. It was not published to ClawHub, not listed publicly, and not claimed as publicly installable.

The Python import bridge was also exercised on `ilc-node-6` through `execute_local_skill_preview({"action": "profile_manifest", "epoch": 1328, "max_bytes": 100000})`. The response remained local-only with `transport_address = null` and `storage_key = null`, proving no non-loopback transport/storage path was activated.

NemoClaw was not installed or invoked in Phase 1328. This phase records OpenClaw-compatible private droplet evidence only and makes no NemoClaw, GPU, or local-inference claim.

## CCSS Reproducibility

Each node validated the confidential coordination local-preview profile and produced the same deterministic sample states:

| Sample | Value |
|---|---|
| CCSS-001 header envelope count | `1` |
| CCSS-002 access state | `active_local` |
| CCSS-002 local access allowed | `true` |
| CCSS-003 sealed delivery state | `sealed_delivered_local` |
| CCSS-004 gossip decision state | `announce_pending_local` |
| CCSS-004 private local action allowed | `true` |
| CCSS-004 fixture jitter epoch | `1331` |

The confidential local-preview profile required these sidecars:

```text
confidential_coordination_capability_membership_boundary
confidential_coordination_gossip_jitter_cover_policy
confidential_coordination_local_preview
confidential_coordination_private_gated_shard
confidential_coordination_sealed_sender_local_delivery
local_graph_memory_projection
openclaw_nemoclaw_local_bridge
sidecar_registry_manifest
```

## Reproducibility Inputs

The private dry run used:

```text
git bundle create /tmp/ilc_phase1328_acc92d64.bundle HEAD
scp /tmp/ilc_phase1328_acc92d64.bundle ilcops@<tailscale-ip>:/tmp/ilc_phase1328_acc92d64.bundle
git -C /opt/ilc/current fetch /tmp/ilc_phase1328_acc92d64.bundle HEAD:refs/remotes/phase1328/local
git -C /opt/ilc/current merge --ff-only refs/remotes/phase1328/local
/opt/ilc/venv/bin/python -m pip install -e /opt/ilc/current
/opt/ilc/venv/bin/python /tmp/phase1328_probe.py
ping -c 1 -W 2 <peer-tailscale-ip>
openclaw skills info ilc-local
execute_local_skill_preview({"action":"profile_manifest","epoch":1328,"max_bytes":100000})
```

The machine-readable evidence is recorded at `docs/specs/ilc_ccss_005_private_openclaw_nemoclaw_droplet_dry_run_1328_v0.1.json`.

## Required Tokens

```text
ccss_005_private_openclaw_nemoclaw_droplet_dry_run_phase_1328.v0.1
confidential_coordination_private_wiring_dry_run_recorded_phase_1328
reproducibility_pass_recorded_phase_1328
public_confidential_coordination_serving_not_enabled_phase_1328
phase_1329_window_1317_1329_closure_next
public_rc_remains_blocked_after_phase_1328
```

## Non-Authorization

Phase 1328 does not authorize public RC, public launch, source export execution, source publication, package publication, clean public tree materialization, OpenClaw skill publication, ClawHub listing, public installability claim, NemoClaw production claim, release artifact production, release-key generation, release envelope production, release signing material generation, signature, Genesis Atlas mutation/regeneration/signing, v0.2 signing, ATLAS-G-007, ATLAS-G-008, ATLAS-G-009, ATLAS-G-010, CDL mutation, CDL-088 opening, identity artifact creation, genesis record creation, seed commitment creation, `identity_seed_commitment` creation, dummy Agent Birth artifact creation, identity-seed generation, mnemonic generation, private-key generation, secret-store write, public claimability activation, public claimability API activation, public verifier service, public claim endpoint, public P2P, public fetch serving, public ILC listener, peer discovery, public sidecar/projection serving, public relay serving, public confidential messaging, public confidential coordination serving, anonymity, unlinkability, Signal-equivalent protection, wallet-facing withdrawal request, wallet-facing transfer request, wallet-facing spend request, wallet-provider signing, wallet-provider ledger-write, wallet write, withdrawal runtime, ECU minting, ILC settlement, or value-path activation.

## Next Phase

`phase_1329_window_1317_1329_closure_next`
