# ILC Constitutional Decisions Proposal v0.2

Status: Draft for debate (post triage)
Owner: Governance/spec working track
Date: 2026-02-08
Supersedes: `docs/specs/ilc_constitutional_decisions_proposal_v0.1.md`

## 1) What Changed in v0.2

This version incorporates a clause-level logic-gate triage:

- Triage artifact: `docs/research/constitution_clause_triage_v0.1.md`
- MVP-criticality artifact: `docs/research/constitution_mvp_criticality_v0.1.md`
- Raw evidence artifacts remain:
  - `docs/research/constitution_dredge_raw_v0.1.jsonl`
  - `docs/research/constitution_dredge_matrix_v0.2.md`

Triage outcomes:
- `KEEP-NOW`: CDP-001, CDP-002, CDP-004, CDP-005, CDP-006, CDP-009
- `KEEP-DEFER`: CDP-003, CDP-007, CDP-010
- `DEFER-OUT`: CDP-008

MVP-criticality outcomes:
- `mvp_now`: CDP-001, CDP-002, CDP-006
- `mvp_guardrail`: CDP-003, CDP-004, CDP-005, CDP-007, CDP-008, CDP-009, CDP-010
- `post_mvp`: none in current top-10 set

## 2) KEEP-NOW Clauses (Constitution Candidate Core)

### CDP-001 Canonical Authority Is Signature-Rooted

Policy:
- Canonical protocol artifacts are those signed by canonical governance lineage keys.
- Forks are allowed at the software level but do not inherit canonical legitimacy by default.

Evidence:
- `Z_Past_Chats/2026_02_03_ILC Codex Antigravity Task Conversations.txt:6220`
- `Z_Past_Chats/2026_02_03_ILC Codex Antigravity Task Conversations.txt:6222`
- `Z_Past_Chats/2026_02_03_ILC Codex Antigravity Task Conversations.txt:6271`

Alignment:
- Partial implementation in key registry/channel stack.

### CDP-002 Reward Legitimacy Follows Canonical Lineage

Policy:
- Reward eligibility is anchored to canonical lineage, not mere code similarity.

Evidence:
- `Z_Past_Chats/2026_02_03_ILC Codex Antigravity Task Conversations.txt:6262`

Alignment:
- Partial.

### CDP-004 Governance Changes Must Be Procedural, Not Unilateral

Policy:
- Material protocol/governance changes require explicit procedural checks.
- No unilateral, silent immediate flips.

Evidence:
- `Z_Past_Chats/2026_02_03_ILC Codex Antigravity Task Conversations.txt:20013`

Alignment:
- Partial; governance structure text needs codification.

### CDP-005 Canonical Policy Supports Contestability

Policy:
- Canon remains contestable through bounded, auditable challenge pathways.

Evidence:
- `Z_Past_Chats/2026_01_06_ILC - ILC project status update.txt:2079`

Alignment:
- Partial.

### CDP-006 Local Canon Must Match Committed History

Policy:
- Local canon must match committed history and anti-rollback constraints.

Evidence:
- `Z_Past_Chats/2026_01_06_ILC - ILC project status update.txt:2096`

Alignment:
- Strong/partial via rollback/fallback protections in recent channel sync work.

### CDP-009 Branding and Canonicality Are Distinct from Copyability

Policy:
- Copyability is expected; canonical legitimacy and signaling remain explicit and separate.

Evidence:
- `Z_Past_Chats/2026_02_03_ILC Codex Antigravity Task Conversations.txt:6216`

Alignment:
- Conceptually strong; client/policy text still maturing.

## 3) KEEP-DEFER Clauses (Retain, But Not Yet Ratifiable)

### CDP-003 No Perpetual Founder Privilege

Retained principle:
- Genesis bootstraps, then operational centrality decays.

Why deferred:
- Precise sunset mechanics, exception process, and legal/accountability boundaries unresolved.

### CDP-007 Founder Economics Are Bounded and Explicit

Retained principle:
- Founder economics are bounded and transparent.

Why deferred:
- Exact constitutional cap/trajectory wording not yet fixed in current economics specs.

### CDP-010 Composability Above Fixed Base Layer

Retained principle:
- Keep a narrow fixed constitutional core, allow composable evolution above it.

Why deferred:
- Layer boundary wording (`fixed` vs `policy-loaded`) needs explicit ratified mapping by domain.

## 4) DEFER-OUT from Constitution (Policy Layer Candidate)

### CDP-008 Operational Participation Must Respect Caps and Separation

Decision:
- Keep as governance/ops policy requirement, not constitutional core text at this stage.

Reason:
- Important, but implementation/procedure-specific; better enforced by governance policy + audits.

## 5) Conflicts Requiring Resolution Before v1.0

1. Founder pseudonymity vs public accountability obligations.
2. Economic boundedness principle vs exact cap/schedule text.
3. Fixed constitutional base vs policy-loaded domains.

Tracked in:
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`

## 6) Immediate Next Ratification Work

1. Convert `KEEP-NOW` clauses into normative `MUST/SHALL` language and add conformance checks.
2. Resolve top 3 conflicts above and promote decision log entries to ratified.
3. Bind ratified clauses to explicit spec tests where feasible.
