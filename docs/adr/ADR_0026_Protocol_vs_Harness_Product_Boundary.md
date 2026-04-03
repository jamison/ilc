# ADR-0026: Protocol vs Harness/Product Boundary

**Status:** Accepted
**Date:** 2026-04-03
**Authors:** Jamison (ILC), Codex
**Classification:** Architectural boundary and planning directive

---

## Context

ILC is moving from a bounded RC0.1 curated testnet toward a later public RC
lane. That transition creates pressure to add strong operator and harness
features:

- budget-aware "mining" modes,
- simple onboarding,
- wallet creation/import UX,
- status/accounting surfaces,
- local orchestrator logic,
- richer dashboards or other product wrappers.

These are useful features. They are also a common source of architectural drift.
If they are placed inside protocol runtime semantics, wallet authority, or
settlement logic, they can:

- blur protocol truth with product UX,
- break harness agnosticism,
- conflict with Phase 576 wallet boundaries,
- weaken local/private architectural guarantees in ADR-0022,
- and make later public legitimacy harder to reason about.

The project therefore needs a hard boundary between:
- protocol/core/runtime semantics,
- and harness/operator/product features layered on top.

## Decision

### 1. Protocol truth remains separate from harness/product features

ILC protocol truth, settlement semantics, graph legitimacy, and wallet
authority remain inside the protocol/runtime layer.

Operator conveniences, budgeting helpers, dashboards, and onboarding flows must
sit on top of the protocol through explicit machine-legible surfaces.

### 2. The immediate post-582 harness lane is limited to foundation work

The first post-582 harness/SDK lane should pull in only the foundations that
directly reduce failure risk and improve harness interoperability:

- workflow state persistence,
- system event logging,
- tool and permission metadata,
- harness verification.

These are accepted as the immediate harness-layer priorities because they:
- reduce crash ambiguity,
- improve replay and permission safety,
- remain harness-agnostic,
- and strengthen existing RC runtime surfaces without changing protocol meaning.

### 3. Budget-aware mining belongs in the harness/operator layer, not protocol logic

`QuotaMiner`-style behavior is permitted only as a harness/operator feature.

It must not be implemented as:
- protocol economics,
- settlement semantics,
- wallet authority,
- or any consensus-bearing runtime primitive.

It may be implemented later as a bounded operator feature that:
- estimates provider or local-model budget,
- selects bounded work,
- schedules conservatively,
- stops before exceeding configured caps,
- and reports projected versus actual cost over protocol-generated receipts.

### 4. Onboarding must remain simple and subordinate to protocol surfaces

An OpenClaw-like onboarding flow is acceptable in later public-RC product work
if it remains thin over the same CLI/state surfaces used by agents and
operators.

The preferred shape is:
- `ilc init`
- `ilc status`
- `ilc mine`

This is a harness/product layer. It must not redefine protocol truth.

### 5. Wallet UX remains narrow unless separately authorized

Public-RC onboarding may include wallet create/import/export flows so users do
not need to leave ILC to begin using the system.

However, wallet scope remains narrow unless separately authorized:
- create/import/export,
- backup guidance,
- accounting visibility.

It must not silently widen into:
- spend,
- transfer,
- withdrawal,
- or generalized signing authority

without explicit constitutional and architectural authorization.

### 6. Auto-configuration may bind only to signed canonical artifacts

Genesis-driven or bootstrap-driven auto-configuration is allowed only when it
derives from signed canonical Genesis/bootstrap artifacts, manifests, or
receipts.

The harness must not treat arbitrary graph state as trustworthy configuration
authority.

### 7. Vanity metrics remain product-only and non-authoritative

Leaderboards, counters, or other operator-facing "hooks" may exist only as thin
product surfaces.

They must not affect:
- consensus,
- reward legitimacy,
- graph truth,
- or canonical public reputation.

At most, early public-RC product surfaces should use restrained metrics such as:
- verified work completed,
- ECU / settled ILC accounting.

### 8. The following items are explicitly excluded from ILC core

The following are not accepted as ILC core directions:
- Ink or terminal-OS style UI as a protocol/core dependency,
- Anthropic-style fixed agent archetypes,
- transcript compaction as a protocol concern,
- tool-pool assembly as a first-class protocol priority,
- budget-aware mining inside protocol economics/runtime,
- vanity metrics affecting consensus or rewards.

## Consequences

### Immediate

- Post-582 harness planning should focus on:
  - workflow state persistence,
  - system event log,
  - tool/permission metadata,
  - harness verification.
- Product hooks such as QuotaMiner and onboarding remain explicitly later-layer
  work.
- The protocol/core boundary remains clear for current RC runtime work.

### Near-term

- A post-582 harness planning spec may sequence:
  1. workflow state persistence,
  2. system event log,
  3. tool/permission metadata,
  4. harness verification,
  5. wallet/bootstrap init UX,
  6. provider/local-model connection UX,
  7. QuotaMiner harness,
  8. minimal status/accounting view,
  9. optional tiny dashboard,
  10. restrained leaderboard metrics.

### Non-goals

- This ADR does not authorize a new UI framework choice.
- This ADR does not create new protocol economics.
- This ADR does not widen wallet semantics beyond Phase 576.
- This ADR does not redefine public legitimacy or the Phase 585+ public
  cryptographic-economic coupling packet.

## Related references

- `docs/adr/ADR_0022_Local_First_Private_Use_and_Publication_Bound_Economics.md`
- `docs/research/ilc_cryptographic_economic_coupling_memo_v0.1.md`
- `docs/research/ilc_agentic_harness_lessons_learned_classification_v0.1.md`
- `docs/research/ilc_rc_phase_575_execution_packets_v0.1.md`
