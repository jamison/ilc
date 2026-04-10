# ILC MemPalace Agent Usage and Prompt Guidelines v0.1

Status: internal guidance
Date: 2026-04-10
Classification: operating guidance for internal retrieval usage

## 1. Operating rules

- MemPalace retrieval is optional internal tooling.
- Local MemPalace runtime currently requires Python 3.9-3.12 in a dedicated
  local environment.
- MemPalace retrieval never overrides ratified or accepted repo artifacts.
- Retrieved material must be cited by source path before it is summarized.
- Agents must verify against the authoritative tier before relying on a
  retrieved result.
- Agents must verify retrieved claims against the authoritative tier before
  turning them into strong conclusions.
- If a retrieved result conflicts with current handoff, capsule, status, or
  accepted ADR material, the authoritative repo source wins.

## 2. Query protocol

1. Start with a scoped query against the most authoritative relevant tier.
2. Read the retrieved file directly rather than trusting a one-line match.
3. Classify the source as canonical, planning, evidence, or historical before
   answering.
4. If the result is historical or draft, label it as such in the response.
5. If the answer would affect protocol scope, wallet/payment authority, or
   release posture, verify against current handoff/boundary docs before using
   the result.
6. Use the staged tiered corpus build as the supported ILC workflow when
   authority separation matters.
7. When a tier contains both broad planning packs and narrow target specs, use
   source-path filters to keep retrieval focused before reading the files
   directly.

## 3. Prompt snippet

Use this bounded snippet in future prompts when MemPalace retrieval is allowed:

> MemPalace may be used as a local retrieval aid only. Treat repo canon,
> approved planning packs, accepted ADRs, current handoffs, and current status
> entries as authoritative. Cite retrieved source paths and verify against the
> highest relevant authority tier before making a strong claim. Historical or
> draft retrieval results must be labeled as non-canonical provenance support.
> Prompts must not treat retrieval results as canon without source checking.
> Operators may render a retrieval brief with
> `tools/mempalace/render_retrieval_brief.py`, but final drafting decisions
> still require direct repo reads.

## 4. Maintenance triggers

Refresh or re-mine the internal MemPalace corpus after:
- a new closure gate or handoff lands,
- a new context capsule supersedes the prior capsule,
- a new approved planning pack or adoption packet lands,
- the staged tiered corpus manifest changes,
- a migration/recovery event changes where session history or context artifacts
  live,
- or a major window closes and the authoritative frontier moves.

## 5. Forbidden uses

Do not use MemPalace retrieval alone to:
- declare canon,
- widen wallet authority,
- justify native escrow,
- justify payment-ingress implementation,
- revive market-liquidity or node-market protocol work,
- override the approved context pack,
- or answer a public FAQ/oracle query from historical or draft corpora without
  explicit labeling.
