# ILC Constitutional Decisions Proposal v0.3

Status: Draft for ratification pass
Owner: Governance/spec working track
Date: 2026-02-08
Supersedes: `docs/specs/ilc_constitutional_decisions_proposal_v0.2.md`

## 1) Scope of v0.3

This revision converts the `KEEP-NOW` constitutional clauses into enforceable normative language (`MUST`/`SHALL`) and attaches explicit conformance hooks.

Reference triage:
- `docs/research/constitution_clause_triage_v0.1.md`
- `docs/research/constitution_mvp_criticality_v0.1.md`
- `docs/research/constitution_mvp_guardrails_matrix_v0.1.md`

## 2) Normative Constitutional Clauses (Candidate Core)

### CONST-001 Canonical Authority

1. Canonical protocol artifacts MUST be accepted only when signed by canonical governance lineage keys.
2. Artifacts not signed by canonical lineage keys SHALL be treated as non-canonical.
3. Implementations MUST expose canonical vs non-canonical status in machine-readable output.

Evidence:
- `Z_Past_Chats/2026_02_03_ILC Codex Antigravity Task Conversations.txt:6220`
- `Z_Past_Chats/2026_02_03_ILC Codex Antigravity Task Conversations.txt:6222`

### CONST-002 Reward Legitimacy

1. Reward eligibility MUST be derived from canonical lineage membership.
2. Code-level compatibility alone SHALL NOT grant canonical reward eligibility.

Evidence:
- `Z_Past_Chats/2026_02_03_ILC Codex Antigravity Task Conversations.txt:6262`

### CONST-003 Procedural Governance Changes

1. Material governance/protocol changes MUST pass explicit procedural checks.
2. Unilateral silent immediate activation SHALL NOT be valid.
3. Changes MUST provide auditable activation metadata.

Evidence:
- `Z_Past_Chats/2026_02_03_ILC Codex Antigravity Task Conversations.txt:20013`

### CONST-004 Contestability of Canon

1. Canonical policy MUST preserve bounded challenge/contest pathways.
2. Challenge outcomes SHALL be auditable and attributable to explicit governance process states.

Evidence:
- `Z_Past_Chats/2026_01_06_ILC - ILC project status update.txt:2079`

### CONST-005 Historical Consistency and Rollback Resistance

1. Local accepted canon MUST be consistent with committed historical state.
2. Rollback acceptance MUST be explicit, bounded, and machine-auditable.
3. Implementations SHALL reject unapproved rollback/fallback paths in production mode.

Evidence:
- `Z_Past_Chats/2026_01_06_ILC - ILC project status update.txt:2096`

### CONST-006 Copyability vs Legitimacy Signaling

1. Protocol copyability is expected and SHALL NOT be treated as canonical legitimacy.
2. Clients and reports MUST clearly signal canonical vs non-canonical status.

Evidence:
- `Z_Past_Chats/2026_02_03_ILC Codex Antigravity Task Conversations.txt:6216`

## 3) Conformance Hooks

| hook_id | clause | current anchor | conformance expectation |
|---|---|---|---|
| CH-001 | CONST-001 | `ilc_core/ledger/canon_bundle_key_registry_channel.py` | Validation rejects non-canonical signer lineage per policy mode. |
| CH-002 | CONST-001/006 | `ilc_core/ledger/canon_bundle_key_registry_sync.py` | Sync result includes canonical/non-canonical decision fields. |
| CH-003 | CONST-002 | `ilc_core/ledger/canon_bundle_key_registry_sync.py` | Reward/acceptance gate depends on canonical lineage status. |
| CH-004 | CONST-003 | `docs/specs/canon_bundle_key_registry_channel_v0.4.md` | Spec requires procedural metadata for material channel/policy transitions. |
| CH-005 | CONST-004 | `docs/specs/commit_epoch_economics_v0.1.md` | Challenge/rollback flow remains explicit and auditable at settlement boundary. |
| CH-006 | CONST-005 | `tests/test_canon_bundle_key_registry_channel_rollback.py` | Production rollback override requires explicit force/guardrails. |
| CH-007 | CONST-005 | `tests/test_canon_bundle_key_registry_sync_version_policy.py` | Version fallback paths are bounded and policy-controlled. |
| CH-008 | CONST-006 | `docs/specs/canon_bundle_key_registry_channel_v0.4.md` | Canonicality signaling language is explicit in channel/distribution policy text. |

## 4) Deferred Constitutional Clauses (Retained for Later Ratification)

- `CDP-003` No perpetual founder privilege (`mvp_guardrail` now, full ratification deferred)
- `CDP-007` Founder economics bounded/explicit (`mvp_guardrail` now, exact wording deferred)
- `CDP-010` Composability above fixed base (`mvp_guardrail` now, layer boundaries deferred)

## 5) Ratification Exit Criteria for v1.0

1. Each `CONST-*` clause has at least one passing conformance artifact.
2. Deferred clauses are either ratified or explicitly moved to policy-layer governance docs.
3. Decision log entries tied to `CONST-*` have chosen options and rationale.
