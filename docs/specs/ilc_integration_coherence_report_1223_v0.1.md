# ILC Integration Coherence Report 1223 v0.1

**Phase:** 1223
**Window:** 1218-1224
**Date:** 2026-05-06
**Verdict:** PASS

`coherence_report_1223_verdict=pass`

---

## 1. Phase Outcomes

| Phase | Topic | Verdict | Token |
|-------|-------|---------|-------|
| 1218 | Window sequence lock | PASS | `window_1218_1224_sequence_lock_committed` |
| 1219 | Truth-primitive permanence ceremony | ATTESTED | `truth_primitive_permanence_genesis_attested_phase_1219`; `commit_epoch_causal_frontier_mapping_spec_required` |
| 1220 | CDL-086 ratification | RATIFIED | `cdl_086_ratified_phase_1220` |
| 1221 | v0.2 signing | DEFERRED | `v0_2_signing_ceremony_deferred_pending_signing_authorization` |
| 1222 | Fetch distribution / graph projection specs | DONE | `reciprocal_fetch_admission_model_spec_committed_phase_1222`; `fetch_distribution_architecture_reframed_phase_1222`; `agent_graph_projection_interface_spec_committed_phase_1222` |

---

## 2. Governance Coherence

Truth-primitive permanence is Genesis-attested for the ADR-0004 New Seven:

```text
truth_primitive_permanence_genesis_attested_phase_1219
```

The Phase 1219 event explicitly excludes `star.map`, preserves the `commit.epoch`
consensus-only boundary, and carries:

```text
commit_epoch_causal_frontier_mapping_spec_required
```

CDL-086 is ratified:

```text
cdl_086_ratified_phase_1220
```

The ratification basis is provisional, not counsel-approved:

```text
counsel_license_instrument_selection_required_before_public_rc
counsel_cla_text_approved_required_before_external_contributors
counsel_trademark_policy_published_required_before_public_launch
allowlist_export_procedure_defined_required_before_public_repo_publication
genesis_canonical_lineage_contract_required_before_public_rc
```

Ratification satisfies the governance precondition only. It does not authorize public launch,
public repository publication, public release artifact distribution, public RC announcement,
external contributor onboarding, external operator bootstrap, v0.2 signing, release-key
generation, or release envelope production.

---

## 3. Fetch Distribution Coherence

Phase 1222 initially documented a reciprocal fetch admission model research candidate:

```text
reciprocal_fetch_admission_model_spec_committed_phase_1222
```

Post-commit review reframed that candidate:

```text
fetch_distribution_architecture_reframed_phase_1222
```

Current canonical direction:

- reciprocal scoring is a deferred research candidate, not the preferred implementation;
- ILC fetch traffic is rooted and topological, not symmetric peer pressure;
- reads of canonical content should be cheap, cacheable, and verifiable;
- writes, mutations, publication, validator participation, and economic recognition remain
  the appropriate gated surfaces;
- high-centrality artifacts require caching, mirroring, snapshots, and non-local compilation
  from verified lineage proofs;
- the static/persistent limiter remains an abuse circuit breaker only:
  `transport_abuse_circuit_breaker_not_final_scaling_policy`.

Future carry-forwards:

```text
l3_sidecar_infrastructure_spec_required_window_1225_plus
agent_graph_projection_interface_implementation_required_window_1225_plus
```

---

## 4. Genesis And Signing Coherence

Signed Genesis v0.1 remains canonical and unchanged:

```text
ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c
```

Committed immutable diagnostic SHA is confirmed from the committed artifact:

```text
5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56
```

Working-tree note: the local working-tree copy of
`out/genesis_compile_coverage_diagnostic_v0.1.json` currently differs from the committed
immutable artifact and hashes to:

```text
3eb15f5c4c15d6b24191f1403912bfa88df17e47c4a6328a6bdff3905a63bd4d
```

This was pre-existing dirty generated state and was not touched by Phase 1223. Phase 1224
closure should restore or otherwise resolve the dirty generated copy before declaring a
clean closure.

v0.2 signing remains deferred:

```text
v0_2_signing_ceremony_deferred_pending_signing_authorization
```

No release key was generated, no release envelope was produced, and v0.2 remains an unsigned
41-node / 73-edge candidate.

---

## 5. Phase 1224 Closure Readiness

Phase 1224 remains SENSITIVE and requires explicit GO. Closure should verify:

- Phase 1218-1223 tokens above;
- CDL-086 ratified but no public-launch act authorized;
- v0.2 signing deferred or explicitly signed by a later authorization;
- committed immutable diagnostic SHA remains `5a67a919...`;
- dirty generated immutable diagnostic working copy is restored or explicitly resolved;
- no runtime mutation occurred in Phases 1221-1223;
- public-release/public-launch non-claims remain intact.

`coherence_report_1223_verdict=pass`

