# Phase 1323 Fix2 OpenClaw VPS Install Skill Discovery

```text
phase_1323_fix2_openclaw_vps_install_skill_discovery.v0.1
openclaw_cli_installed_on_private_vps_phase_1323_fix2
local_ilc_skill_draft_discovered_by_openclaw_phase_1323_fix2
openclaw_gateway_not_started_phase_1323_fix2
clawhub_publication_not_authorized_phase_1323_fix2
ilc_runtime_not_modified_phase_1323_fix2
public_rc_remains_blocked_after_phase_1323_fix2
phase_1324_ccss_private_gated_shard_contract_next_after_fix2
```

## Summary

Phase 1323 Fix2 installed OpenClaw on the private `ilc-node-6` VPS over
Tailscale and created a local-only draft ILC workspace skill. This closes the
Phase 1323 native-install discovery gap without claiming public skill
publication, ClawHub listing, public installability, identity bootstrap,
gateway serving, or ILC runtime activation.

OpenClaw is installed at:

```text
/home/ilcops/.npm-global/bin/openclaw
OpenClaw 2026.5.7 (eeef486)
```

The install used Node `v24.15.0`, npm `11.12.1`, npm prefix
`/home/ilcops/.npm-global`, and the official non-interactive installer command:

```bash
curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --no-onboard --no-prompt --verify
```

Onboarding was skipped. The gateway service is disabled/stopped, configured as
loopback-only if later started, and no listener was present on ports `18789` or
`19001` during verification.

## Draft Skill

The local-only draft skill was created on `ilc-node-6` at:

```text
/home/ilcops/.openclaw/workspace/skills/ilc-local/SKILL.md
```

Its SHA-256 is:

```text
406451b681be0674ca40271a924651c9c35ca2cd7c5e674d6ef03f4bcdd3c31b
```

OpenClaw reports the skill as:

| Field | Value |
|-------|-------|
| name | `ilc-local` |
| source | `openclaw-workspace` |
| eligible | `true` |
| model visible | `true` |
| user invocable | `true` |
| command visible | `true` |
| required env vars | none |
| install actions | none |
| missing requirements | none |

The first draft command attempted to call `build_sidecar_registry_manifest`
positionally. The live VPS probe caught that mismatch, the draft skill was
corrected to use the current keyword-free API and select the
`openclaw_claimable_local_bridge` profile from the returned manifest, and the
safe preview command then passed.

## Safe ILC Preview Result

The corrected local preview command reported:

```json
{
  "package_profile_id": "openclaw_skill_claimable",
  "preview_binding": "local_import_only",
  "preview_openclaw_dependency_required": false,
  "profile_id": "openclaw_claimable_local_bridge",
  "public_claimability_runtime_activated": false,
  "public_p2p_activated": false,
  "public_serving_enabled": false,
  "registry_public_rc_claimed": false
}
```

## Non-Claims

Fix2 does not authorize public RC, public launch, source export execution,
source publication, package publication, OpenClaw skill publication, ClawHub
listing, public installability claims, release artifacts, release keys, release
envelopes, signing, public claimability/API activation, public verifier service,
public P2P, public fetch serving, public sidecar/projection serving, OpenClaw
gateway public bind, gateway daemon install, Genesis/Atlas mutation or signing,
v0.2 signing, CDL mutation, CDL-088 opening, identity artifacts, genesis records,
seed commitments, `identity_seed_commitment`, mnemonic generation, private-key
generation, secret-store writes, dummy Agent Birth artifacts, wallet writes, ECU
minting, ILC settlement, or value-path activation.

## Graph Delta

```text
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1323_g8_openclaw_vps_install_skill_discovery_fix2.md,docs/specs/ilc_phase_1323_fix2_openclaw_vps_install_skill_discovery_v0.1.json,docs/specs/ilc_phase_1323_fix2_openclaw_vps_install_skill_discovery_v0.1.md,docs/phases/phase_1323_fix2_openclaw_vps_install_skill_discovery_walkthrough.md,docs/phases/STATUS.md,docs/PLANNING_INDEX.md,docs/specs/ilc_antigravity_context_capsule_v5.54.md,tests/test_phase_1323_fix2_openclaw_vps_install_skill_discovery.py -> planning/frontier
```
