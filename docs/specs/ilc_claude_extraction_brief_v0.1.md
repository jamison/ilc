# ILC Claude Extraction Brief v0.1

Status: active extraction brief  
Date: 2026-02-18  
Audience: architectural reviewer (Claude)

## 1. Purpose

Close the three weakest context areas with corpus-grounded extraction and produce draft artifacts that can be promoted into canon lanes.

Target areas:
1. Agent SDK contract boundary (protocol surface vs orchestration surface)
2. Bootstrap operations runbook (Phase A to Phase B)
3. Genesis/runtime boundary statement (what Genesis is and is not)

## 2. Mandatory Inputs

Read in this order:
1. `docs/specs/ilc_reviewer_context_pack_v0.2_delta.md`
2. `docs/specs/ilc_mining_economics_and_bootstrapping_strategy_v0.1.md`
3. `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md`
4. `docs/specs/ilc_constitutional_context_audit_response_v0.1.md`
5. `docs/specs/ilc_phase_226_open_cdl_security_triage_v0.1.md`
6. `docs/research/constitution_dredge_matrix_v0.2.md` (only the raw IDs listed below)

## 3. Required Raw-ID Extraction Set

For each target area, extract direct evidence from these rows:

### 3.1 SDK boundary
- `raw-011274` (L1/L2 layering and emergence constraints)
- `raw-016792` (ledger interface vs hard bind; fork-policy pressure)
- `raw-008595` (agent functional scope declaration)

### 3.2 Bootstrap operations runbook
- `raw-006100` (low-agent bootstrap role)
- `raw-011967` (agent cost/incentive framing)
- `raw-012555` (post-bootstrap no privileged humans)
- `raw-012565` (sunset/hand-off framing)
- `raw-012961` (share caps and assignment discipline)
- `raw-013084` (capability check-ins framing)

### 3.3 Genesis/runtime boundary statement
- `raw-015306` (economics sandbox documentation need)
- `raw-018013` (MVP canon as strong priors, not immutable truth)
- `raw-016900` (contestability requirement)
- `raw-002601` (rollback protection baseline concern)

## 4. Output Artifacts Required from Claude

Produce three markdown drafts (non-normative unless ratified later):

1. `ilc_agent_sdk_boundary_contract_draft_v0.1.md`
2. `ilc_bootstrap_operations_runbook_draft_v0.1.md`
3. `ilc_genesis_runtime_boundary_statement_draft_v0.1.md`

## 5. Output Format Contract (for each draft)

Each draft must include:
1. **Normative status line** (`non-normative draft`, with precedence note)
2. **Scope and non-goals**
3. **Decision table** (what is locked vs open vs deferred)
4. **Evidence table** with columns:
   - claim
   - source raw-id
   - matrix line
   - source file and line in the matrix row
   - interpretation note
5. **Open questions requiring decision-log routing**
6. **Proposed phase lane** (Genesis sequence, post-Genesis, or research)

## 6. Quality Bar

1. No claims without at least one canon anchor or raw-id anchor.
2. No migration of strategic assumptions into constitutional language without explicit decision-log routing note.
3. Distinguish clearly between:
   - implemented (`code + tests + gates`),
   - ratified (`CDL decision state`),
   - simulated/designed (`historical or strategic only`).

## 7. Acceptance Checks

Extraction is complete only if:
1. Every raw-id listed in Section 3 appears in at least one evidence table row.
2. Each of the three drafts has an explicit "what this does not imply" subsection.
3. Each draft includes at least one concrete next-step item that can be routed into:
   - `TODO.txt`,
   - a future phase prompt,
   - or a decision-log queue item.
