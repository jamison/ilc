# ILC Reviewer Context Pack v0.2 Delta

Status: active reviewer delta pack  
Date: 2026-02-18  
Scope: missing/underrepresented context areas for architectural review continuity

## 1. Purpose

Provide a compact delta to `docs/specs/ilc_reviewer_context_pack_v0.1.md` so reviewers (including Claude) can load the highest-leverage context gaps with direct canon and historical-corpus anchors.

This document does not replace the v0.1 pack; it augments it.

## 2. Delta Gap Map (with references)

| Gap area | Canonical anchors | Historical-corpus anchors | Current status | Recommended lane |
|---|---|---|---|---|
| Issuance policy closure (`C_max`, decay mode, tail model, fee/burn split) | `docs/specs/ilc_mining_economics_and_bootstrapping_strategy_v0.1.md` (Section 3.2-3.4), `TODO.txt` (Genesis packaging TODO block) | `docs/research/constitution_dredge_matrix_v0.2.md` rows: `raw-012042` (hard cap), `raw-012979` (tail-emission variant) | discussed, not ratified | Genesis packaging documentation + decision-log lane |
| Agent SDK contract boundary vs orchestration boundary | `docs/specs/ilc_mining_economics_and_bootstrapping_strategy_v0.1.md` (Section 5.2) | weak direct corpus mapping in current matrix; closest policy framing: `raw-011274` (L1/L2 layering) | strategic framing only; no canonical SDK spec yet | post-Genesis product/spec lane |
| Coalition anti-gaming controls beyond single-agent concentration | `docs/specs/ilc_anti_gaming_simulation_findings_v0.1.md` (Sections 5-6), `ilc_core/analysis/reuse_diversity_invariants.py` (current implemented proxy) | `docs/research/constitution_dredge_matrix_v0.2.md` rows: `raw-012316` (cartel/cabal test), `raw-009690` (stake/rate anti-Sybil shaping) | partially represented (proxy only) | post-Genesis anti-gaming hardening lane |
| Bootstrap operations spec and Phase A->B transition criteria | `docs/specs/ilc_mining_economics_and_bootstrapping_strategy_v0.1.md` (Sections 4.4, 5.4) | `docs/research/constitution_dredge_matrix_v0.2.md` rows: `raw-006100` (low-agent bootstrap role), `raw-011967` (agent cost/incentive framing) | strategic notes exist; no formal ops spec | go-to-market/operations spec lane |
| Explicit Genesis/runtime boundary statement for external reviewers | `docs/specs/ilc_constitutional_context_audit_response_v0.1.md` (Sections 5.2, 7), `docs/specs/ilc_reviewer_context_pack_v0.1.md` (Section 4 snapshot) | N/A (primarily canon/process boundary) | partially present across multiple docs, not single-source | release-note and onboarding lane |
| CapProof baseline-transition policy (epoch-0 Genesis anchor -> non-privileged reference) | `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md` (Sections 3.1, 6.3) | `docs/research/constitution_dredge_matrix_v0.2.md` rows: `raw-013084` (capability check-ins), `raw-019157` (capability vector concept) | strategic design captured; not ratified/implemented | decision-log + post-Genesis capability-proof lane |
| Open security CDL execution path (`CDL-001/002/007`) | `docs/specs/ilc_constitutional_decision_log_v0.1.md`, `docs/specs/ilc_phase_226_open_cdl_security_triage_v0.1.md` | `docs/research/constitution_dredge_matrix_v0.2.md` rows: `raw-009224`, `raw-019035`, `raw-012745`, `raw-012748`, `raw-006766`, `raw-012565`, `raw-013401`, `raw-002601` | triaged as blockers in Phase 226 | Phase 227 remediation lane |
| Whitepaper-level epistemic framing and convergence caveat | `docs/specs/ilc_mining_economics_and_bootstrapping_strategy_v0.1.md` (Section 6.4) | `docs/research/constitution_dredge_matrix_v0.2.md` rows: `raw-016900` (contestability), `raw-018013` (canon as strong prior, not immutable truth) | represented in supplements, not yet a formal whitepaper artifact in-repo | whitepaper/research synthesis lane |

## 3. Reviewer Notes on Evidence Strength

1. Rows with strong canon + raw-id support: issuance closure, coalition anti-gaming, CapProof transition, open security CDL path.
2. Rows with weaker direct historical extraction support in current matrix: SDK boundary (currently anchored primarily in strategic supplement and architecture inference).
3. For dropped/out-of-scope matrix rows that still carry historical signal (`raw-012979`, `raw-019157`), treat as rationale evidence, not constitutional authority.

## 4. Claude Ingestion Order (deterministic)

1. `docs/specs/ilc_reviewer_context_pack_v0.1.md`
2. `docs/specs/ilc_constitutional_decision_log_v0.1.md`
3. `docs/specs/ilc_phase_226_open_cdl_security_triage_v0.1.md`
4. `docs/specs/ilc_constitutional_context_audit_response_v0.1.md`
5. `docs/specs/ilc_anti_gaming_simulation_findings_v0.1.md`
6. `docs/specs/ilc_mining_economics_and_bootstrapping_strategy_v0.1.md`
7. `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md`
8. `docs/research/constitution_dredge_matrix_v0.2.md` (only for raw-id backtrace checks listed in Section 2)
9. `docs/specs/ilc_claude_extraction_brief_v0.1.md` (tasked extraction contract for weak-context areas)
10. `docs/specs/ilc_agent_sdk_boundary_contract_draft_v0.1.md` (non-normative draft output)
11. `docs/specs/ilc_bootstrap_operations_runbook_draft_v0.1.md` (non-normative draft output)
12. `docs/specs/ilc_genesis_runtime_boundary_statement_draft_v0.1.md` (non-normative draft output)

## 5. Non-Normative Reminder

The two strategic supplements are intentionally non-normative:
- `docs/specs/ilc_mining_economics_and_bootstrapping_strategy_v0.1.md`
- `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md`

They provide direction and provenance linkage but do not override ratified decision-log state.

## 6. Extraction Outputs Registered

The following artifacts were produced via the extraction brief workflow and are now tracked for review/promotion:
- `docs/specs/ilc_agent_sdk_boundary_contract_draft_v0.1.md`
- `docs/specs/ilc_bootstrap_operations_runbook_draft_v0.1.md`
- `docs/specs/ilc_genesis_runtime_boundary_statement_draft_v0.1.md`
