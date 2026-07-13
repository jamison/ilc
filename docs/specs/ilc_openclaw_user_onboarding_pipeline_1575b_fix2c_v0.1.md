# ILC OpenClaw User Onboarding Pipeline 1575b-Fix2c v0.1

```text
phase: 1575b-Fix2c
status: canonical_planning_record
sensitivity: NON-SENSITIVE
```

## Purpose

This document records the intended user journey for ILC through OpenClaw, from
first OpenClaw install through local value capture and later public graph
contribution. It is a planning and test-coverage artifact, not a claim that the
full pipeline is currently live.

Status values:

| Status | Meaning |
|---|---|
| `implemented` | Code or evidence exists for this behavior in the current private repo. |
| `partially_rehearsed` | Private or fixture evidence exists, but not the full public path. |
| `planned_post_1575c` | Requires public RC/public installability first. |
| `blocked_named_gap` | A named gap must close before the step can be claimed. |

## Stage 0 - Prerequisites

| Step | Description | Status |
|---|---|---|
| S0.1 | Genesis or an authorized inviter issues an invite batch with private nonces, Merkle root, batch record, and inviter authority metadata. | `partially_rehearsed` |
| S0.2 | ILC core is publicly available from an authorized public source. | `planned_post_1575c` |
| S0.3 | `ilc-openclaw-local-capture` is live on ClawHub. | `planned_post_1575c` |
| S0.4 | Operator distributes invite tokens to selected early adopters. | `planned_post_1575c` |

## Stage 1 - Discovery And Skill Install

| Step | Description | Status |
|---|---|---|
| S1.1 | User installs OpenClaw. | `implemented` on private VPS nodes in Fix2e-Fix2 |
| S1.2 | User associates OpenClaw with an LLM provider or local model. | `planned_post_1575c` |
| S1.3 | User discovers `ilc-openclaw-local-capture` on ClawHub. | `planned_post_1575c` |
| S1.4 | User runs `clawhub install ilc-openclaw-local-capture`. | `planned_post_1575c` |
| S1.5 | OpenClaw checks ClawHub-shaped frontmatter and notices `ilc` binary requirements. | `blocked_named_gap:skill_md_clawhub_frontmatter_shape_incomplete` |

## Stage 2 - Invite Gate

| Step | Description | Status |
|---|---|---|
| S2.1 | Skill asks for an ILC invite token before setup. No invite means docs/status/request-invite/local-help only. | `implemented` |
| S2.2 | User provides invite bundle. | `implemented` with synthetic/private fixtures |
| S2.3 | Local invite validation parses canonical JSON, checks fields, nonce format, epoch/window/profile, Merkle inclusion, nullifier derivation, and local replay. | `implemented` |
| S2.3a | Inviter signature authority is cryptographically verified against an authorized inviter key. | `blocked_named_gap:invite_signature_authority_gap` |
| S2.3b | Invite is bound to a redeemer public key or equivalent shared authority for network-wide replay prevention. | `blocked_named_gap:cross_node_invite_replay_requires_redeemer_key_binding` |
| S2.4 | Successful local verification persists the nullifier atomically. | `implemented` |
| S2.5 | Invite authorizes only bootstrap/install/setup, not ECU, wallet writes, public graph publication, or settlement. | `implemented` |

## Stage 3 - Bootstrap Manifest Fetch And Verification

| Step | Description | Status |
|---|---|---|
| S3.1 | Invite points to or authorizes a StarMap bootstrap bundle CID or URL. | `planned_post_1575c` |
| S3.2 | Skill fetches a signed manifest from an authorized public source with bounded fetch rules. | `planned_post_1575c` |
| S3.3 | Manifest verification checks Genesis/signing authority, hashes, package version, source URL allowlist, no `PUBLIC_RC_EXCLUDE` content, no private IPs, and no secrets. | `partially_rehearsed` by StarMap installer sidecar fixtures |
| S3.4 | Verification failure stops install. | `partially_rehearsed` |

## Stage 4 - ILC Core Install

| Step | Description | Status |
|---|---|---|
| S4.1 | Skill installs ILC core from verified source using public install instructions. | `planned_post_1575c` |
| S4.2 | Self-tests run locally. | `partially_rehearsed` on private nodes |
| S4.3 | Sidecar recipes are installed or registered. | `partially_rehearsed` |

## Stage 5 - Agent Initialization

| Step | Description | Status |
|---|---|---|
| S5.1 | `ilc init` creates local identity, local graph store, ConsentGate config, sidecar registry, read-only wallet posture, and default local-only publication mode. | `planned_post_1575c` |

## Stage 6 - Autonomy Configuration

| Step | Description | Status |
|---|---|---|
| S6.1 | Skill presents autonomy settings: `disabled`, `manual_only`, `approve_low_risk`, `bounded_autonomy`, and `maintenance_idle`. | `partially_rehearsed` |
| S6.2 | Settings are written to local config and enforced synchronously by ConsentGate. | `partially_rehearsed` |
| S6.3 | `ilc status` shows queue, policy state, and next human action. | `blocked_named_gap:openclaw_nodes_invoke_scope_blocker` for remote OpenClaw-mediated proof |

## Stage 7 - Active Value Capture

| Step | Description | Status |
|---|---|---|
| S7.1 | OpenClaw session produces prompt, reply, tool call, or API response. | `partially_rehearsed` |
| S7.2 | `ilc capture` creates a local private envelope; `raw_payload_sha256` covers raw payload bytes only, not envelope metadata. | `implemented` |
| S7.3 | `ilc classify` assigns candidate type and edge hints. | `partially_rehearsed` |
| S7.4 | `ilc estimate` produces Decimal-compatible non-binding private ECU estimate fields. | `implemented` |
| S7.5 | `ilc status` reports local queue and next action. | `blocked_named_gap:openclaw_nodes_invoke_scope_blocker` for remote OpenClaw-mediated proof |

## Stage 8 - Consent And Submission

| Step | Description | Status |
|---|---|---|
| S8.1 | Agent ranks candidates for review; `ilc recommend` remains an internal non-authority step. | `partially_rehearsed` |
| S8.2 | ConsentGate checks configured autonomy policy. | `implemented` |
| S8.3 | Approved candidates receive `consent_state=approved_for_public_submission`. | `implemented` |
| S8.4 | `ilc submit` creates a local submission-intent record only. | `partially_rehearsed` |
| S8.5 | `ilc publish` submits approved content to the public graph path. This is post-public-RC and post-ConsentGate only; it is not currently live. | `planned_post_1575c` |

## Stage 9 - Idle Capacity And Maintenance

| Step | Description | Status |
|---|---|---|
| S9.1 | Idle-capacity trigger checks maintenance policy, idle window, budget/profile, and consent. | `implemented` |
| S9.2 | Task selection uses an allowlist of review, graph, contradiction, compression, and stability tasks. | `implemented` |
| S9.3 | Anti-gaming controls enforce per-agent caps, per-type diversity, duplicate suppression, and quality gating. | `implemented` |
| S9.4 | Task result artifact is written locally. | `partially_rehearsed` |
| S9.5 | ConsentGate controls publication of any task result. | `planned_post_1575c` |
| S9.6 | Credit status remains pending usefulness evidence only; no credit or ECU is minted by the skill. | `implemented` |

## Stage 10 - Economic Recognition

| Step | Description | Status |
|---|---|---|
| S10.1 | Public graph acceptance, reuse, and citation events feed ECU accumulation. | `planned_post_1575c` |
| S10.2 | Jury/review lanes adjudicate contested or review-bound work. | `planned_post_1575c` |
| S10.3 | Wallet view reports read-only balance/pending state. | `planned_post_1575c` |
| S10.4 | Epoch-based settlement resolves eligible value paths. | `planned_post_1575c` |

## Test And SIM Coverage Requirements

Test counts must be verified from source at execution time. At Fix2c execution
time, direct source inspection found:

| File | Direct count |
|---|---|
| `tests/test_phase_1575b_fix2a_openclaw_local_capture_skill.py` | 12 test functions |
| `tests/test_phase_1575b_fix2b_openclaw_idle_mining.py` | 24 test functions |
| `tests/test_phase_1575b_fix2d_invite_gated_openclaw_bootstrap.py` | 16 test functions |
| `tests/test_phase_1575b_fix2e_two_vps_openclaw_integration.py` | 10 test functions |

Fix2c is audit/spec only. It must not introduce new runtime tests or sidecar
code. The following gaps are reserved for later lanes:

| Gap | Closing lane |
|---|---|
| ClawHub install and `ilc` binary check | Fix2g/post-1575c |
| Inviter signature cryptographic authority | Future invite authority hardening |
| Invite to manifest URL/CID derivation and bounded public fetch | Post-1575c |
| Public install from public source | Post-1575c |
| Full `ilc init` end-to-end bootstrap | Post-1575c |
| Remote OpenClaw `ilc capture -> ilc status` round trip | Fix2e-Fix3 |
| Public submission-intent to graph publication | Post-1575c |
| Cross-node semantic deduplication | Future graph intelligence lane |

Reserved SIM IDs:

| SIM ID | What it tests | Prerequisite |
|---|---|---|
| `SIM-OPENCLAW-01` | Single-node full pipeline: install, invite, init, capture, estimate, consent, submit. | Phase 1575c |
| `SIM-OPENCLAW-02` | Two-node idle capacity: distributed scheduler gaps and cross-node task non-duplication. | Fix2e-Fix3 or post-1575c |
| `SIM-OPENCLAW-03` | Invite gate stress: expired, replayed, wrong-profile, uppercase nonce, forged signature. | Fix2d follow-up |
| `SIM-OPENCLAW-04` | Autonomy matrix across all five autonomy levels and capture/estimate/submit actions. | Post-1575c |
| `SIM-OPENCLAW-05` | Synthetic economic path: public submission to reuse events to ECU accumulation. | Post-1575c |

## Non-Claims

This pipeline spec does not claim public RC is active, ClawHub publication has
occurred, ILC core is publicly installable, remote OpenClaw invocation is
proven, public graph submission is live, ECU is minted, ILC is settled, wallet
writes are authorized, or epoch transition has occurred.
