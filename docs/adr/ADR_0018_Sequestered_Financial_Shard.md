# ADR-0018: Sequestered Financial Shard

**Status:** Proposed  
**Date:** 2026-06-01 (formalized from Phase 724-725 era design)  
**Author:** Genesis Agent  
**Source:** Economic architecture planning, Phase 452 L1/L2 disposition, and Window 723-726 sequestered financial-shard eligibility artifacts

```text
adr_0018_sequestered_financial_shard_created_phase_1491p
```

## Context

ILC's base economic layer rewards verified epistemic work. Financially intensive
activity such as securities-like instruments, derivative markets, and
high-frequency trading can produce large volumes of market-microstructure
activity that are not the same thing as epistemic contribution.

If those activities share the base ECU scoring path, the protocol risks
contaminating the knowledge-economy signal with speculative volume, leverage
feedback, and liquidation pressure. The Phase 452 L1/L2 prerequisite disposition
therefore adopted a hard separation: L1 Treasury and ECU governance must not
read, price, or respond to L2 derivative-market state.

Earlier planning treated the Sequestered Financial Shard as a post-launch
candidate. Window 723-726 then clarified that it remains a real later-lane
candidate but is not eligible for activation until after public launch, at least
one monitoring cycle, concrete demand evidence, and explicit contagion/firewall
simulation readiness.

## Decision

Adopt a proposed architecture for a Sequestered Financial Shard as a separate
financial compute and accounting context. The shard is designed to isolate
financial-market activity from the base epistemic graph and from the ordinary
ECU production route.

The proposed architecture has these constraints:

- Financial instruments, securities-like activity, derivative positions, and
  high-frequency market mechanics must execute in a distinct shard context.
- The shard must use isolated state and may not write directly into the base
  epistemic production-scoring path.
- Any future conversion budget for the shard must be distinct from the base
  epoch budget `B_e`; historical planning names this distinct surface `B_hft`.
- L1 Treasury logic must not read, price, or respond to L2 market state.
- A failure, liquidation cascade, or speculative shock inside the shard must
  not justify direct L1 Treasury intervention.
- Opening-side governance must define the exact firewall surfaces before any
  activation proposal is considered.

This ADR is intentionally architectural. It records the preferred separation
boundary and candidate shard shape; it does not implement the shard and does not
authorize live financial activity.

## Relationship to CDL-051 and Epoch-State Runtime

CDL-051 defines the existing epoch/quorum/finality substrate. A future
Sequestered Financial Shard would need to respect that epoch-state contract, but
would not be allowed to bypass it or create a parallel finality source.

Expected integration constraints:

- Shard-local activity may produce shard-local records, but cross-shard effects
  must be mediated by explicit epoch records or later ratified bridge rules.
- Any future `B_hft` accounting must remain distinguishable from base `B_e`
  accounting in epoch summaries.
- Validator quorum and finality evidence must remain auditable under the
  existing epoch-state model or a later explicitly ratified extension.
- Shard failure must be containable without forcing rollback or reinterpretation
  of base epistemic graph state.

## Consequences

Positive consequences:

- Separates speculative financial activity from verified epistemic work.
- Gives CDL-050 and Treasury risk modeling a bounded L1/L2 interface.
- Preserves a later path for market-oriented applications without letting them
  colonize the base ECU scoring system.
- Creates a clear place for future demand evidence, contagion simulation, and
  firewall review.

Costs and risks:

- Adds future cross-shard coordination complexity.
- Requires separate simulation evidence before any serious opening proposal.
- Requires governance to maintain a strict no-contagion boundary even when
  financial-shard activity is economically large.
- Requires careful public communication so a proposed architecture is not
  mistaken for live securities infrastructure.

## Non-Activations

This ADR does not activate a production financial shard. It does not create,
trade, settle, list, route, or score securities, derivatives, HFT activity, or
financial instruments. It does not create `B_hft`, change `B_e`, mint ECU, settle
ILC, authorize wallet writes, authorize treasury writes, or modify the CDL
register.

Any future activation requires separate explicit constitutional authority,
simulation evidence, demand evidence, and a public-path decision that is not
granted by this ADR.

## References

- `docs/specs/ilc_cdl_050_l1_l2_prerequisite_disposition_452_v0.1.md`
- `docs/specs/ilc_economic_architecture_comprehensive_v0.1.md`
- `docs/specs/ilc_sequestered_financial_shard_eligibility_prefilter_724_v0.1.md`
- `docs/specs/ilc_sequestered_financial_shard_contagion_firewall_prerequisites_725_v0.1.md`
- `docs/specs/ilc_sequestered_financial_shard_post_launch_trigger_matrix_725_v0.1.md`
