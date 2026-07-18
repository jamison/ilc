# ILC OpenClaw ClawHub Publication Readiness 1575b-Fix2c v0.1

```text
phase: 1575b-Fix2c
outcome: A_audit_only_default_off_retained
sensitivity: NON-SENSITIVE
status: publication_not_ready
```

## Purpose

This document records the Phase 1575b-Fix2c Outcome A audit of the
`ilc-openclaw-local-capture` skill publication surface. It is a readiness and
disposition record only. It does not publish an OpenClaw skill, create a
ClawHub listing, claim public installability, submit graph nodes, mint ECU,
settle ILC, write wallets, clear runtime guards, activate public RC, or change
repository visibility.

## Source Checks

The audit read the following source authorities:

| Source | Finding |
|---|---|
| `docs/specs/ilc_constitutional_decision_log_v0.1.md` | CDL-033 is ratified and governs the OpenClaw skill specification and ClawHub publication contract. |
| `docs/specs/ilc_agent_skills_surface_spec_621_v0.1.md` | Agent skills are `skills/<skill-name>/SKILL.md` surfaces; OpenClaw graph interaction beyond baseline CDL-033 remains an extension surface. |
| `ilc_core/rc/package_profiles.py` | `PROFILE_OPENCLAW_SKILL_LOCAL = "openclaw_skill_local"` and `PROFILE_OPENCLAW_SKILL_CLAIMABLE = "openclaw_skill_claimable"` exist. |
| `docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md` | OpenClaw/NemoClaw are harness hosts, not protocol substrates. |
| `docs/architecture/ilc_core_vs_agentic_harness_boundary_v0.1.md` | The harness may build private artifacts but may not mutate production graph, wallet, treasury, registry, CDL, ADR, or activation state. |
| `docs/specs/ilc_openclaw_real_harness_strikeforce_1575b_fix2e_fix2_v0.1.md` | Fix2e-Fix2 proves real OpenClaw installation, skill visibility, Gateway/node-host pairing, and connection; it does not prove `openclaw nodes invoke`. |
| `skills/ilc-openclaw-local-capture/SKILL.md` | YAML frontmatter is present and OpenClaw-visible, but not ClawHub-shaped. |

MemPalace retrievals for CDL-033/OpenClaw publication and prior private
OpenClaw dry-run evidence returned the same boundary: earlier phases kept
OpenClaw skill publication, ClawHub listing, and public installability blocked.

## Current Skill Package State

The current skill package path is:

```text
skills/ilc-openclaw-local-capture/SKILL.md
```

At Phase 1575b-Fix2c, the frontmatter began with:

```yaml
---
name: ilc-openclaw-local-capture
description: Use when an OpenClaw-hosted local agent needs to verify an ILC invite, install or operate local ILC capture helpers, turn selected prompt/reply/tool/API outputs into private ILC-shaped candidate records, estimate non-binding private ECU usefulness, prepare ConsentGate-reviewed submission intents, or offer explicit idle-capacity graph-maintenance work without minting, settlement, wallet writes, or public graph publication.
metadata:
  short-description: ILC invite-gated local capture and private ECU estimate skill
---
```

The post-1575n publication-preflight correction replaces that frontmatter with the
ClawHub-shaped form:

```yaml
---
name: ilc-openclaw-local-capture
description: Local capture, consent-gated estimation, and invite-gated bootstrap for ILC graph contribution via OpenClaw.
metadata:
  openclaw:
    requires:
      bins: [ilc]
---
```

The old description was 425 characters and the old frontmatter did not contain
`metadata.openclaw.requires.bins`. The current corrected state is:

```text
openclaw_visible_frontmatter_present=true
clawhub_shape_complete=true_after_post_1575n_publication_preflight
skill_md_clawhub_frontmatter_shape_incomplete=false_after_post_1575n_publication_preflight
```

The old blocker `skill_md_missing_clawhub_frontmatter` is stale and must not be
used for current state. Fix2e-Fix2 added enough frontmatter for OpenClaw
visibility on private VPS nodes. The post-1575n publication-preflight
correction reshaped the frontmatter; Phase 1575f should verify this shape rather
than add or replace a second YAML block.

## Publication Readiness Verdict

```text
publication_ready=false
public_installability_ready=false
outcome=A_audit_only_default_off_retained
```

| Blocker | Type | Closing lane |
|---|---|---|
| `outcome_b_deferred_post_1575c_by_design` | Sequencing blocker | Phase 1575c must make public RC/public repository installability real before publication. |
| `ilc_core_not_publicly_installable` | Distribution blocker | Phase 1575c public mirror/public repository publication must close this. |

The local `clawhub` command is not installed in the current workstation
environment, so this audit does not claim `clawhub_tooling_available`.

## Operational Gaps That Do Not Block ClawHub Readiness Audit

The following are real gaps, but they are not blockers to the Fix2c Outcome A
readiness audit itself:

| Gap | Meaning | Closing lane |
|---|---|---|
| `openclaw_nodes_invoke_scope_blocker` | Fix2e-Fix2 proved paired OpenClaw harnesses, but did not prove remote invocation through `openclaw nodes invoke`. | Phase 1575b-Fix2e-Fix3. |
| `invite_signature_authority_gap` | Invite bootstrap currently records signature authority as a named gap rather than verifying an inviter signature against a known authority key. | Future invite authority hardening lane. |
| `cross_node_invite_replay_requires_redeemer_key_binding` | Local nullifier persistence is per-node only; network-wide replay prevention requires issuer-side redeemer-key binding or equivalent shared authority. | Future invite issuance/redeemer-binding lane. |

`openclaw_nodes_invoke_scope_blocker` is not a ClawHub listing blocker, because
a ClawHub listing requires package metadata and publication authority, not
remote invocation. It is, however, a blocker to claiming a fully operational
OpenClaw-mediated ILC skill round trip.

## Forward Design - TOON Outbound Serialization

TOON (Token-Oriented Object Notation) remains deferred.

1. TOON belongs in the skill package as a thin outbound adapter layer, never in
   `ilc_core/`.
2. TOON applies only to outbound serialization for LLM-facing structured
   payloads. It must not feed content-addressed hashes, DAG edges, canonical
   graph artifacts, or protocol signatures.
3. The hash separation invariant is non-negotiable:
   `raw_payload_sha256 == sha256(canonical_json_bytes(raw_payload))` regardless
   of any TOON encoding elsewhere.
4. The TypeScript TOON reference has known nested optional-field schema
   inference concerns and must not be ported directly.
5. The implementation dependency, when triggered, is `toon-python v1.0`.
6. The trigger is live LLM round-trips in the skill package, not Fix2c.
7. Named gap: `toon_outbound_adapter_deferred_pending_live_roundtrips`.

This token is a named design gap in this spec and walkthrough, not a
`STATUS.md` completion token.

## Non-Claims

Phase 1575b-Fix2c Outcome A does not:

- publish OpenClaw or ClawHub;
- create a ClawHub listing;
- claim public installability;
- publish or push a public mirror;
- change repository visibility;
- submit public graph nodes;
- mint ECU;
- settle ILC;
- write wallets, treasury, or production graph state;
- clear runtime guards;
- activate public RC;
- execute `openclaw nodes invoke`;
- prove a remote `ilc capture -> ilc status` round trip.
