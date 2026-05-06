# ILC Antigravity Context Capsule v5.49

**Date:** 2026-05-06
**Supersedes:** `docs/specs/ilc_antigravity_context_capsule_v5.48.md`
**Produced:** Phase 1231, Window 1225-1232
**Frontier:** Window 1225-1232 in progress; Phase 1231 complete; Phase 1232 closure gate pending

`capsule_v5_49_supersedes_v5_48`
`coherence_report_1231_verdict=pass`
`window_1225_1232_sequence_lock_committed`
`commit_epoch_causal_frontier_mapping_spec_committed_phase_1226`
`cdl_087_canonical_fetch_distribution_policy_opened_phase_1227`
`cdl_087_prelock_committed_phase_1228`
`agent_graph_projection_runtime_1229.v0.1`
`fetch_incentive_hypergraph_slice_projection_required_phase_1229`
`v0_2_signing_ceremony_deferred_pending_signing_authorization`
`fetch_distribution_architecture_reframed_phase_1222`
`transport_abuse_circuit_breaker_not_final_scaling_policy`

---

## 1. Current State

Window 1225-1232 is complete through Phase 1231. Phase 1232 remains pending and is
SENSITIVE.

Current coherence report:

- `docs/specs/ilc_coherence_report_1231_v0.1.md`

Current active window lock and guidance:

- `docs/specs/ilc_phase_1225_1232_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_1225_1232_candidate_phase_grouping_v0.1.md`

---

## 2. Governance Frontier

Truth-primitive permanence remains Genesis-attested:

```text
truth_primitive_permanence_genesis_attested_phase_1219
```

`commit.epoch` remains consensus-layer only and non-agent-issuable. Phase 1226 consumed the
mapping-spec carry-forward:

```text
commit_epoch_causal_frontier_mapping_spec_committed_phase_1226
commit_epoch_mapping_governed_by_cdl_051_no_new_cdl_required
```

Production emission runtime remains open:

```text
commit_epoch_projection_runtime_required_before_production_emission
```

CDL-086 remains ratified as the public-launch packaging blocker:

```text
cdl_086_ratified_phase_1220
```

CDL-086 ratification does not authorize public launch, public repository publication, public
release artifact distribution, public RC announcement, external contributor onboarding,
external operator bootstrap, v0.2 signing, release-key generation, or release envelope
production.

Open counsel/public-release obligations:

```text
counsel_license_instrument_selection_required_before_public_rc
counsel_cla_text_approved_required_before_external_contributors
counsel_trademark_policy_published_required_before_public_launch
allowlist_export_procedure_defined_required_before_public_repo_publication
genesis_canonical_lineage_contract_required_before_public_rc
```

---

## 3. CDL-087 Fetch Distribution Frontier

CDL-087 status:

```text
OPEN / PRELOCKED / NOT RATIFIED
```

Tokens:

```text
cdl_087_canonical_fetch_distribution_policy_opened_phase_1227
cdl_087_prelock_committed_phase_1228
cdl_087_not_ratified_phase_1228
```

CDL-087 ratification requires SIM-FETCH-01 and all six Phase 1228 ratification conditions.
The static/persistent fetch limiter remains the abuse circuit breaker floor:

```text
transport_abuse_circuit_breaker_not_final_scaling_policy
```

The preferred fetch-distribution direction remains:

```text
fetch_distribution_architecture_reframed_phase_1222
```

The reciprocal scoring formula in Phase 1222 §2 remains a non-selected research candidate,
not the preferred direction.

---

## 4. Runtime Frontier

Attribution runtime:

```python
EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION = "epoch_attribution_settle_runtime_1210.v0.7"
EDGE_MINT_PHI_BOUND = Decimal("0.60")
PROVENANCE_DECAY_ALPHA = Decimal("0.45")
CDL_085_DEPENDENCY = "cdl_085_werner_phi_bound_ratified_1185.v0.1"
```

HTTP fetch transport:

```python
HTTP_FETCH_TRANSPORT_RUNTIME_VERSION = "http_fetch_transport_runtime_1212.v0.2"
PERSISTENT_RATE_LIMITER_VERSION = "persistent_fetch_rate_limiter_runtime_1202.v0.1"
```

Agent graph projection runtime:

```python
AGENT_GRAPH_PROJECTION_RUNTIME_VERSION = "agent_graph_projection_runtime_1229.v0.1"
```

Runtime file:

```text
ilc_core/graph/agent_graph_projection_runtime.py
```

Phase 1229 converted `ilc_core.graph` into a package while preserving:

```python
from ilc_core.graph import EpistemicGraph
```

The runtime is read-only and deterministic, performs no filesystem/network I/O, rejects
float payload values, serializes finite `Decimal` values as strings, emits canonical JSON,
provides deterministic NDJSON export, and exposes the named `fetch_incentive_hypergraph_slice`.

---

## 5. Genesis Atlas Frontier

Signed Genesis v0.1 remains canonical and unchanged:

- Nodes: 32
- Edges: 55
- Root envelope hash:
  `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`

Committed immutable diagnostic:

- `out/genesis_compile_coverage_diagnostic_v0.1.json`
- Expected and current SHA-256:
  `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56`

Unsigned v0.2 candidate:

- Nodes: 41
- Edges: 73
- v0.2 remains an unsigned 41-node / 73-edge candidate
- Status: unsigned candidate
- Signing status: deferred pending signing authorization
- Token: `v0_2_signing_ceremony_deferred_pending_signing_authorization`

---

## 6. RC Gate Status

| Gate | Status |
|------|--------|
| CDL-085 ratified and active | **SATISFIED** |
| v0.2 signing ceremony executed | **OPEN** - authorization absent |
| Tier-3 runtime linkage | **SATISFIED** |
| Public-launch packaging blocker evaluated/progressed | **RATIFIED** - public-launch acts still separately blocked |
| Persistent rate limiter | **SATISFIED / CIRCUIT-BREAKER ONLY** - fetch distribution architecture reframed |
| Truth-primitive permanence | **ATTESTED** |
| Canon bundle signing/report/audit fixture debt | **SATISFIED** |
| Agent graph projection interface | **IMPLEMENTED** - `agent_graph_projection_runtime_1229.v0.1` |

---

## 7. Active Carry-Forward Obligations

- Phase 1232 closure gate - requires `GO Phase 1232`
- v0.2 signing ceremony - deferred pending explicit signing authorization
- CDL-087 ratification - deferred pending SIM-FETCH-01 and six Phase 1228 conditions
- `commit_epoch_projection_runtime_required_before_production_emission`
- `counsel_license_instrument_selection_required_before_public_rc`
- `counsel_cla_text_approved_required_before_external_contributors`
- `counsel_trademark_policy_published_required_before_public_launch`
- `allowlist_export_procedure_defined_required_before_public_repo_publication`
- `genesis_canonical_lineage_contract_required_before_public_rc`
- `l3_sidecar_infrastructure_spec_required_window_1225_plus`

---

## 8. MemPalace Disposition

No callable MemPalace tool is exposed to Codex in this session. Because no callable MemPalace tool is exposed,
MemPalace remains advisory-only for Codex execution in Window 1225-1232 unless refreshed and surfaced through
a callable tool. The live frontier is established by repo canon: `PLANNING_INDEX.md`,
`STATUS.md`, the sequence lock, current specs, and phase walkthroughs.

---

## 9. Verification

Window 1225-1232 is verified through Phase 1231:

- Phase 1225 sequence-lock tests passed
- Phase 1226 commit.epoch mapping tests passed
- Phase 1227 CDL-087 opening tests passed
- Phase 1228 CDL-087 prelock tests passed
- Phase 1229 graph projection runtime tests passed
- Phase 1230 signing-skip tests passed
- Phase 1231 coherence/capsule tests passed
- Sensitive-runtime guardrail passed
- Committed immutable diagnostic SHA remains:
  `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56`

Phase 1232 closure gate remains pending.

`capsule_v5_49_supersedes_v5_48`
