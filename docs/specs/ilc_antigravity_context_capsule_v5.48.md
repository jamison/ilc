# ILC Antigravity Context Capsule v5.48

**Date:** 2026-05-06
**Supersedes:** `docs/specs/ilc_antigravity_context_capsule_v5.47.md`
**Produced:** Phase 1223, Window 1218-1224
**Frontier:** Window 1218-1224 in progress; Phase 1223 complete; Phase 1224 closure gate pending

`capsule_v5_48_supersedes_v5_47`
`coherence_report_1223_verdict=pass`
`truth_primitive_permanence_genesis_attested_phase_1219`
`commit_epoch_causal_frontier_mapping_spec_required`
`cdl_086_ratified_phase_1220`
`v0_2_signing_ceremony_deferred_pending_signing_authorization`
`reciprocal_fetch_admission_model_spec_committed_phase_1222`
`fetch_distribution_architecture_reframed_phase_1222`
`agent_graph_projection_interface_spec_committed_phase_1222`
`transport_abuse_circuit_breaker_not_final_scaling_policy`

---

## 1. Current State

Window 1218-1224 is complete through Phase 1223. Phase 1224 remains pending and is
SENSITIVE.

Current coherence report:

- `docs/specs/ilc_integration_coherence_report_1223_v0.1.md`

Current active window lock and guidance:

- `docs/specs/ilc_phase_1218_1224_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_1218_1224_candidate_phase_grouping_v0.1.md`

---

## 2. Governance Frontier

Truth-primitive permanence:

- Genesis-attested in Phase 1219.
- Token: `truth_primitive_permanence_genesis_attested_phase_1219`
- `star.map` remains excluded.
- `commit.epoch` remains consensus-layer only and non-agent-issuable.
- Production `commit.epoch` emission mapping remains open:
  `commit_epoch_causal_frontier_mapping_spec_required`.

CDL-086:

- Opened Phase 1194.
- Prelocked Phase 1204.
- Ratified Phase 1220.
- Token: `cdl_086_ratified_phase_1220`.

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

## 3. Runtime Frontier

Attribution runtime remains:

```python
EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION = "epoch_attribution_settle_runtime_1210.v0.7"
EDGE_MINT_PHI_BOUND = Decimal("0.60")
PROVENANCE_DECAY_ALPHA = Decimal("0.45")
CDL_085_DEPENDENCY = "cdl_085_werner_phi_bound_ratified_1185.v0.1"
```

HTTP fetch transport remains:

```python
HTTP_FETCH_TRANSPORT_RUNTIME_VERSION = "http_fetch_transport_runtime_1212.v0.2"
PERSISTENT_RATE_LIMITER_VERSION = "persistent_fetch_rate_limiter_runtime_1202.v0.1"
```

No runtime mutation occurred in Phases 1218-1223.

---

## 4. Fetch Distribution Frontier

Phase 1222 published:

- `docs/specs/ilc_reciprocal_fetch_admission_model_spec_1222_v0.1.md`
- `docs/specs/ilc_agent_graph_projection_interface_spec_1222_v0.1.md`

The reciprocal scoring formula is a non-selected research candidate. The corrected direction
is:

- fetch traffic is topological and rooted, not symmetric;
- reads of canonical content should be public, cacheable, and verifiable where possible;
- write/mutation/economic-recognition surfaces remain gated;
- high-centrality Genesis, truth primitive, ADR/CDL, manifest, and lineage artifacts should
  be mirrored, snapshotted, and locally compilable from verified lineage proofs;
- static/persistent rate limiting remains an abuse circuit breaker, not the final network
  scaling policy.

Tokens:

```text
reciprocal_fetch_admission_model_spec_committed_phase_1222
fetch_distribution_architecture_reframed_phase_1222
agent_graph_projection_interface_spec_committed_phase_1222
transport_abuse_circuit_breaker_not_final_scaling_policy
```

Carry-forwards:

```text
l3_sidecar_infrastructure_spec_required_window_1225_plus
agent_graph_projection_interface_implementation_required_window_1225_plus
```

---

## 5. Genesis Atlas Frontier

Signed Genesis v0.1 remains canonical and unchanged:

- Nodes: 32
- Edges: 55
- Root envelope hash:
  `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`

Committed immutable diagnostic:

- `out/genesis_compile_coverage_diagnostic_v0.1.json`
- Expected and committed SHA-256:
  `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56`

Working-tree note:

- local working-tree copy currently differs and hashes to:
  `3eb15f5c4c15d6b24191f1403912bfa88df17e47c4a6328a6bdff3905a63bd4d`
- Phase 1224 closure should restore or otherwise resolve the dirty generated copy before
  declaring a clean closure.

Unsigned v0.2 candidate:

- Nodes: 41
- Edges: 73
- Status: unsigned candidate
- Signing status: deferred pending signing authorization
- Token: `v0_2_signing_ceremony_deferred_pending_signing_authorization`

---

## 6. RC2 Gate Status

| Gate | Status |
|------|--------|
| CDL-085 ratified and active | **SATISFIED** |
| v0.2 signing ceremony executed | **OPEN** - authorization absent |
| Tier-3 runtime linkage | **SATISFIED** |
| Public-launch packaging blocker evaluated/progressed | **RATIFIED** - public-launch acts still separately blocked |
| Persistent rate limiter | **SATISFIED / CIRCUIT-BREAKER ONLY** - fetch distribution architecture reframed |
| Truth-primitive permanence community ratification | **ATTESTED** |
| Canon bundle signing/report/audit fixture debt | **SATISFIED** |

---

## 7. Active Carry-Forward Obligations

- Phase 1224 closure gate - requires `GO Phase 1224`
- v0.2 signing ceremony - deferred pending explicit signing authorization
- `commit_epoch_causal_frontier_mapping_spec_required`
- `counsel_license_instrument_selection_required_before_public_rc`
- `counsel_cla_text_approved_required_before_external_contributors`
- `counsel_trademark_policy_published_required_before_public_launch`
- `allowlist_export_procedure_defined_required_before_public_repo_publication`
- `genesis_canonical_lineage_contract_required_before_public_rc`
- `l3_sidecar_infrastructure_spec_required_window_1225_plus`
- `agent_graph_projection_interface_implementation_required_window_1225_plus`

---

## 8. Verification

Window 1218-1224 is verified through Phase 1223:

- Phase 1218 sequence-lock tests passed
- Phase 1219 permanence ratification tests passed
- Phase 1220 CDL-086 ratification tests passed
- Phase 1221 signing-skip tests passed
- Phase 1222 fetch/projection spec tests passed
- Phase 1223 coherence/capsule tests passed
- Committed immutable diagnostic SHA remains:
  `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56`

Phase 1224 closure gate remains pending.

`capsule_v5_48_supersedes_v5_47`

