# ILC Distribution Werner Credit Scope

**Phase:** `GAP-DISTRIBUTION-WERNER-CREDIT-00`
**Date:** 2026-10-24
**Disposition:** `governance_blocker`

## 1. Decision

Artifact serving and artifact-serving credit are separate capabilities. The
release lane may distribute and verify software without activating a Werner
economic effect. Current ratified authority does not authorize Werner credit
for serving release artifacts.

The controlling evidence is explicit:

- CDL-053 limits local productive credit to review-lane-passed
  maintenance-equivalent work and preserves
  `WERNER_LIVE_DISTRIBUTION_AUTHORIZED=false`.
- CDL-109 authorizes Werner only as a bounded pre-normalization reweighting
  input to CDL-108 backward attribution. Its scope is
  `cdl_108_backward_attribution_only_v1` and it preserves
  `WERNER_LIVE_DISTRIBUTION_AUTHORIZED=false`.
- CDL-096 treats Werner as an evidence and flow-control policy surface rather
  than an economic value path.
- CDL-121 expressly excludes any Werner distribution credit from release-object
  authority.

Accordingly, no receipt generator, credit calculator, wallet path, settlement
path, guard clearance, or runtime activation is implemented by this phase.

## 2. Observation-Window Distinction

Row 16a's 90-day observation window, with earliest review target 2027-01-07,
concerns live Model Router routing-receipt calibration under CDL-116. It does
not grant artifact-serving credit authority when the date arrives. Its evidence
may inform a future decision, but closing the window cannot silently flip a
Werner economic guard.

The distribution-credit blocker is therefore authority-bound, not merely
time-bound.

## 3. Future Authority Required

A future SENSITIVE phase, provisionally named
`GAP-DISTRIBUTION-WERNER-CREDIT-CDL-00`, would need to ratify the exact economic
scope before implementation or activation. It must decide at least:

1. Whether the result is local eligibility/reputation evidence, an input to an
   existing bounded attribution pool, or a separate non-settlement score.
2. Which serving acts qualify: exact artifact bytes, release assertion evidence,
   policy evidence, or some narrower subset.
3. Which independent party verifies successful service and exact-byte integrity.
4. Duplicate, retry, mirror, self-serving, collusion, and Sybil treatment.
5. Per-artifact, per-agent, per-observer, per-epoch, and per-cluster caps.
6. Superseded, withdrawn, stale, malformed, or equivocated artifact penalties.
7. Privacy limits and the boundary between public graph evidence and local
   transport telemetry.
8. Whether and how any local credit may later affect ECU, subject to existing
   settlement and no-double-pay constraints.

No future phase may repurpose `WERNER_LIVE_DISTRIBUTION_AUTHORIZED` to mean
software-byte transport. If artifact-serving credit is approved, its authority
and activation state must have a distinct, purpose-specific name.

## 4. Candidate Evidence Contract

This section scopes evidence for future governance; it is not an implementation
spec or activation authority.

A candidate serving receipt would need to bind:

- provider AgentID or authenticated TransportPrincipal;
- requesting observer identity or privacy-preserving authorized equivalent;
- network, channel, policy-view CID, and authoritative checkpoint;
- release assertion CID, software release CID, artifact CID, exact byte length,
  and exact digest;
- request nonce or stable event identifier;
- successful consumer-side integrity verification;
- observation epoch and governed freshness rule;
- outcome class, including withdrawn, stale, mismatched, or unavailable;
- signatures or attestations sufficient to prevent provider self-assertion from
  becoming credit by itself.

Attribution must collapse duplicate economic events and distinguish useful
counterexamples or defect reports from successful authorized service. Merely
advertising retention, returning bytes, or appearing in a source URL is not
proof of productive service.

## 5. Release-Candidate Boundary

Werner artifact-serving credit is non-blocking for RC-native distribution.
Rows 26, 29, and the fresh-invite smoke may proceed without it. The release
path remains correct because authorization, integrity, and current eligibility
do not depend on a reward mechanism.

## 6. Formal Blocker

```text
distribution_werner_credit_blocked_authority_absent
missing_authority=no_ratified_werner_distribution_cdl
required_phase=GAP-DISTRIBUTION-WERNER-CREDIT-CDL-00
earliest_unblock_date=not_date_bound_requires_future_ratified_authority
```

## 7. Non-Claims

This scope record does not authorize Werner credit, ECU issuance, wallet
mutation, settlement, a new receipt type, a new graph node kind, runtime code,
CDL mutation, package publication, VPS mutation, or public-RC activation.
