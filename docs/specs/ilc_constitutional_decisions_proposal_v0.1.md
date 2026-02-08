# ILC Constitutional Decisions Proposal v0.1

Status: Draft for debate (not ratified)
Owner: Governance/spec working track
Date: 2026-02-08

## 1) Purpose

This proposal consolidates constitutional-level decisions from historical design conversations and aligns them with current architecture artifacts. It is intentionally conservative: this document captures principles that appear repeatedly and with strong normative framing in the source corpus.

It is not a final constitution. It is the structured debate baseline for ratification.

## 2) Source and Method

Primary extraction artifacts:

- `docs/research/constitution_dredge_inventory_v0.1.md`
- `docs/research/constitution_dredge_meta_v0.1.md`
- `docs/research/constitution_dredge_raw_v0.1.jsonl`
- `docs/research/constitution_dredge_matrix_v0.2.md`

Primary high-signal conversation sources:

- `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt`
- `Z_Past_Chats/2026_02_03_ILC Codex Antigravity Task Conversations.txt`
- `Z_Past_Chats/2026_01_06_ILC - ILC project status update.txt`
- `Z_Past_Chats/2025_10_28_ILC - Greeting exchange.txt`

## 3) Proposed Constitutional Clauses (Candidate)

Each clause is a candidate with evidence and requires ratification.

### CDP-001 Canonical Authority Is Signature-Rooted

Policy:
- Canonical protocol artifacts are those signed by canonical governance lineage keys.
- Forks are allowed at the software level but do not inherit canonical legitimacy by default.

Evidence:
- `Z_Past_Chats/2026_02_03_ILC Codex Antigravity Task Conversations.txt:6220`
- `Z_Past_Chats/2026_02_03_ILC Codex Antigravity Task Conversations.txt:6222`
- `Z_Past_Chats/2026_02_03_ILC Codex Antigravity Task Conversations.txt:6271`

Current alignment:
- Partial (implemented in canon/key-registry tracks; broader ecosystem policy still maturing).

### CDP-002 Reward Legitimacy Follows Canonical Lineage

Policy:
- Reward eligibility should be anchored to canonical lineage, not mere code similarity.

Evidence:
- `Z_Past_Chats/2026_02_03_ILC Codex Antigravity Task Conversations.txt:6262`

Current alignment:
- Partial.

### CDP-003 No Perpetual Founder Privilege

Policy:
- Genesis bootstraps initial rules, then governance transitions toward objective, contestable, forkable mechanisms.
- Founder role trends toward reduced operational centrality over time.

Evidence:
- `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt:15626`

Current alignment:
- Partial.

### CDP-004 Governance Changes Must Be Procedural, Not Unilateral

Policy:
- Material protocol/governance changes require explicit procedural checks (multi-body or equivalent safeguards).
- No single actor should perform silent or immediate unilateral flips.

Evidence:
- `Z_Past_Chats/2026_02_03_ILC Codex Antigravity Task Conversations.txt:20013`

Current alignment:
- Partial.

### CDP-005 Canonical Policy Supports Contestability

Policy:
- Canon should remain contestable through bounded, auditable contradiction/challenge pathways.

Evidence:
- `Z_Past_Chats/2026_01_06_ILC - ILC project status update.txt:2079`

Current alignment:
- Partial.

### CDP-006 Local Canon Must Match Committed History

Policy:
- Local accepted canon must be consistent with committed historical records and anti-rollback guarantees.

Evidence:
- `Z_Past_Chats/2026_01_06_ILC - ILC project status update.txt:2096`

Current alignment:
- Partial to strong in recent channel rollback/fallback tracks.

### CDP-007 Founder Economics Are Bounded and Explicit

Policy:
- Founder/Genesis accrual targets are bounded, explicit, and enforced by transparent mechanisms.
- Accrual is not framed as arbitrary per-epoch privilege.

Evidence:
- `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt:20810`
- `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt:20664`

Current alignment:
- Partial (spec-level discussion stronger than implementation-level codification).

### CDP-008 Operational Participation Must Respect Caps and Separation

Policy:
- If founder-associated entities operate in protocol workflows, caps and conflict-separation constraints must apply.

Evidence:
- `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt:20804`

Current alignment:
- Partial.

### CDP-009 Branding and Canonicality Are Distinct from Copyability

Policy:
- Open copyability is expected; canonical governance legitimacy is separate and must be explicitly signaled.

Evidence:
- `Z_Past_Chats/2026_02_03_ILC Codex Antigravity Task Conversations.txt:6216`

Current alignment:
- Strong at conceptual level; needs formal constitutional text.

### CDP-010 Composability Is a Design Goal Above the Fixed Base Layer

Policy:
- Keep a narrow fixed constitutional/core layer and permit composable evolution in higher layers under canonical constraints.

Evidence:
- `Z_Past_Chats/2026_01_06_ILC - ILC project status update.txt:14559`
- `Z_Past_Chats/2026_01_06_ILC - ILC project status update.txt:14580`

Current alignment:
- Partial.

## 4) Deferred / Open Constitutional Questions

The following need explicit decision rounds:

1. Exact constitutional definition of canonical signer lineage and emergency rotation.
2. Founder anonymity and publication obligations balance (privacy vs accountability).
3. Hard-coding vs policy-node loading boundaries by layer (L0/L1/L2/L3).
4. Formal fork legitimacy criteria and migration rules.
5. Economic cap, issuance schedule, and governance-over-parameters boundary text.

See `docs/specs/ilc_constitutional_decision_log_v0.1.md`.

## 5) Ratification Process (Proposed)

1. Triage matrix entries in `docs/research/constitution_dredge_matrix_v0.2.md`.
2. Resolve conflicts in the decision log.
3. Promote stable clauses from proposal v0.1 into ratified constitution v1.0.
4. Bind ratified clauses to implementation tests where feasible.
