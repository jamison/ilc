# ILC CDL-052 Epistemic Evaluation Architecture Opening Stub 464 v0.1

Status: open
Date: 2026-03-27
Owner lane: G8 Constitution Cluster A

## 1. Opening declaration

CDL-052 is opened in Phase 464 following clean Gate 1, Gate 2, and Gate 3 clearances.

## 2. Scope of CDL-052

CDL-052 governs the three-mode epistemic evaluation architecture for knowledge graph nodes.
The lane covers Mode 1 reuse-valuation routing, Mode 2 Popperian elevation via `refutation_criterion`, and Mode 3 anomaly-triggered auditor review.
CDL-052 does not govern CDL-V7 agent decomposition admissibility, CDL-V3 quorum diversity, CDL-V2 Sybil resistance, or CDL-V1 temporal decay.

## 3. Dependency clauses

CDL-052 depends on:
- ADR-0021 for the finality-claim boundary,
- Phase 462 schema specification for `refutation_criterion`,
- Phase 463 staking contract specification for Mode 2 and refutation obligations,
- CDL-034 and CDL-035 as inherited schema and validation dependencies.

## 4. Gate clearance references

Gate references:
- Gate 1 cleared by `docs/specs/ilc_adr_0021_epistemic_finality_claims_461_v0.1.md`
- Gate 2 cleared by `docs/specs/ilc_refutation_criterion_schema_specification_462_v0.1.md`
- Gate 3 cleared by `docs/specs/ilc_minimal_staking_contract_specification_463_v0.1.md`

## 5. Prelock target

Prelock hardening occurs in Phase 465.
Ratification occurs in Phase 466 if and only if the prelock phase remains clean.
