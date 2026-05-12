# ILC OpenClaw/NemoClaw Claimable Profile Full Dry Run 1323 v0.1

Status: dry-run evidence only
Phase: 1323
Schema token: `openclaw_nemoclaw_claimable_profile_full_dry_run_phase_1323.v0.1`

## Summary

Phase 1323 dry-ran the checked-in ILC OpenClaw/NemoClaw claimable local bridge
profile against the graph-native sidecar suite on the three private
DigitalOcean/Tailscale droplets. The dry run passed for ILC profile and sidecar
integrity, but it does not prove native OpenClaw skill installability because
`openclaw` and `clawhub` are not installed on the droplets.

The exact ILC bridge profile is `openclaw_claimable_local_bridge`, using package
profile `openclaw_skill_claimable` from
`public_rc_package_profiles_1307.v0.1`. Public claimability remains metadata
only: runtime activation, public P2P, and public serving all remain false.

## Skill Format Discovery

Current OpenClaw discovery confirms an AgentSkills-compatible skill folder with
`SKILL.md` or `skill.md`, Markdown instructions, YAML frontmatter, at minimum
`name` and `description`, and optional `metadata.openclaw` requirements for
bins, env, config, installer metadata, and related gating. OpenClaw workspace
skills load from `/skills` ahead of managed `~/.openclaw/skills`, and
`openclaw skills install` is the public ClawHub install path.

Sources checked:

- `docs/specs/ilc_openclaw_architecture_deep_dive_v0.1.md`
- `docs/specs/ilc_cdl_033_openclaw_skill_publication_ratification_evidence_291_v0.1.md`
- `docs/specs/ilc_distribution_architecture_roadmap_v0.3.md`
- `docs/specs/ilc_cdl_032_cli_first_sdk_ratification_evidence_253_v0.1.md`
- `https://raw.githubusercontent.com/openclaw/openclaw/main/docs/tools/skills.md`
- `https://raw.githubusercontent.com/openclaw/clawhub/main/docs/skill-format.md`
- `https://github.com/openclaw/clawhub`

No Phase 1323 artifact claims that an ILC OpenClaw skill is published, listed,
accepted by ClawHub, publicly installable, or available from a public package
registry.

## Two Surfaces

| Surface | Phase 1323 status |
|---------|-------------------|
| CLI-first thin skill | Recorded as the right public-facing shape: `SKILL.md` should teach the agent to invoke `ilc` CLI/bootstrap commands. Not implemented, not published, not installable in Phase 1323. |
| Python import bridge | Checked in and dry-run on droplets through `execute_local_skill_preview`, `TransportHarness`, and `StorageHarness`; remains `local_import_only`. |

## Droplet Evidence

All three private droplets were synced to
`4ea3d0857764075b88775b25f1d31e1e252df855` before the dry run:

| Node | ILC profile checks | Native OpenClaw/ClawHub |
|------|--------------------|-------------------------|
| `ilc-node-2` | Pass; verifier/projection/wallet/value/bridge gates false for public activation. | Not installed. |
| `ilc-node-3` | Pass; verifier/projection/wallet/value/bridge gates false for public activation. | Not installed. |
| `ilc-node-6` | Pass; verifier/projection/wallet/value/bridge gates false for public activation. | Not installed. |

## Blockers Carried Forward

- `identity_seed_ux_public_bootstrap_blocker_phase_1323`: public bootstrap still
  needs one crypto path with interactive and agent-mode ceremony modes, explicit
  agent-mode secret output or secure store target, no stdout fallback, strict
  file permissions, and no seed/mnemonic/private-key exposure to LLM chat,
  transcript memory, logs, walkthroughs, or `STATUS.md`.
- `identity_seed_ux_agent_mode_not_custodial_by_default_phase_1323`: the LLM may
  guide setup but must not be custodial by default.
- `genesis_rooted_agent_birth_attestation_blocker_phase_1323`: no public
  Genesis-rooted bootstrap identity claim is allowed until an agent birth
  attestation or equivalent Genesis/Atlas lineage-origin proof is specified.
- The CDL-069 commitment-formula mismatch remains a fix-before-identity-bootstrap
  blocker: ratification evidence records
  `sha384("ilc-seed-commit-v1:" || identity_seed)`, while
  `ilc_core/identity/genesis_record_schema.py` still computes bare
  `sha384(identity_seed)`. Phase 1323 created no identity artifacts.
- Native OpenClaw/ClawHub install rehearsal remains blocked because neither
  binary is present on the droplets.

## Non-Authorization

Phase 1323 does not authorize public RC, source export, source publication,
package publication, OpenClaw skill publication, ClawHub listing, public
installability claims, public claimability/API activation, public verifier
service, public P2P, public sidecar/projection serving, wallet-provider signing,
wallet ledger writes, ECU minting, ILC settlement, release artifacts, release
keys, release envelopes, signatures, Genesis/Atlas mutation/signing, v0.2
signing, CDL mutation, CDL-088 opening, identity-seed generation, mnemonic
generation, secret-store writes, or Genesis-rooted public bootstrap identity
claims.

Required tokens:

```text
openclaw_nemoclaw_claimable_profile_full_dry_run_phase_1323.v0.1
claimable_profile_dry_run_public_claimability_still_gated_phase_1323
graph_native_sidecar_suite_profile_integrity_rehearsed_phase_1323
openclaw_nemoclaw_hosts_not_protocol_substrates_phase_1323
openclaw_skill_format_discovery_required_phase_1323
cli_first_skill_surface_recorded_phase_1323
python_import_bridge_surface_recorded_phase_1323
identity_seed_ux_public_bootstrap_blocker_phase_1323
identity_seed_ux_agent_mode_not_custodial_by_default_phase_1323
openclaw_skill_not_published_or_installable_phase_1323
genesis_rooted_agent_birth_attestation_blocker_phase_1323
phase_1324_ccss_private_gated_shard_contract_next
public_rc_remains_blocked_after_phase_1323
```

Graph delta:

```text
graph_delta=support_only:docs/specs/ilc_openclaw_nemoclaw_claimable_profile_full_dry_run_1323_v0.1.json,docs/specs/ilc_openclaw_nemoclaw_claimable_profile_full_dry_run_1323_v0.1.md,docs/phases/phase_1323_openclaw_nemoclaw_claimable_profile_full_dry_run_walkthrough.md,tests/test_phase_1323_openclaw_nemoclaw_claimable_profile_full_dry_run.py,docs/phases/STATUS.md,docs/PLANNING_INDEX.md,docs/specs/ilc_antigravity_context_capsule_v5.54.md -> planning/frontier
```
