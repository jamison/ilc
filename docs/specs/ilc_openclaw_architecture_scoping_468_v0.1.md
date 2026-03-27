# ILC OpenClaw Architecture Scoping 468 v0.1

Status: scoped
Date: 2026-03-27
Owner lane: G8 Constitution Cluster A

## 1. CDL-052 graph operations surface

OpenClaw architecture scoping is complete as of Phase 468.

The CDL-052 graph-operations surface for OpenClaw is scoped to four first-class operations:
- graph node submission carrying authored-envelope metadata and optional `refutation_criterion`,
- refutation submission against an existing node or claim,
- novelty-check status query,
- reuse-centrality query.

These are interface-surface scopes only. No OpenClaw runtime implementation occurs in Phase 468.

## 2. CDL-033 extension requirements

CDL-033 will need extension work beyond its baseline skill/publication contract to surface:
- authored-envelope submission verbs,
- refutation verbs,
- novelty-status read APIs,
- reuse-centrality read APIs,
- bounded auditor-review handoff hooks for Mode 3 initiation.

This scoping does not ratify those extensions. It identifies them as required future work.

## 3. SDK-level contracts required

The SDK-level contracts required beyond current baseline scoping are:
- typed request and response envelopes for node submission,
- typed request and response envelopes for refutation submission,
- status-query contracts for novelty and corroboration state,
- query contracts for reuse-centrality snapshots,
- error-code contracts for malformed `refutation_criterion` and mode-boundary violations.

These contracts are not implemented in Phase 468. They are architecture-scope outputs only.

## 4. Deferred implementation items

OpenClaw CDL-052 implementation is deferred beyond Window 460-468.

Deferred items include:
- executable SDK surface changes,
- runtime novelty-check plumbing,
- runtime staking and reward wiring,
- Mode 3 auditor-review execution hooks,
- production query services for reuse centrality.
