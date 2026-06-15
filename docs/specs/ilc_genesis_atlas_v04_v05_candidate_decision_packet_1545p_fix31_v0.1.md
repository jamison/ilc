# ILC Genesis Atlas v0.4/v0.5 Candidate Decision Packet - Phase 1545p-Fix31

## Decision Boundary

This packet is the decision packet, not the signing decision. The current
Phase 1573 route remains compatible only with the Fix18 v0.4 core candidate
unless a human authorizes a broader scope.

## Variant Comparison

| Variant | Nodes | Edges | Genesis-core eligible | Hashed-only | Directed gaps | Phase 1573 verdict |
|---|---|---|---|---|---|---|
| v04_core_only_fix18_preserved | 57 | 80 | 57 | 0 | 0 | phase1573_current_guidance_compatible_with_fix18_only |
| v04_core_plus_full_repo_support | 10029 | 27668 | 57 | 9974 | 9974 | phase1573_requires_guidance_patch_for_v04_core_plus_support |
| v05_full_repo_optimized_candidate | 10029 | 27714 | 57 | 9928 | 9928 | phase1573_requires_new_scope_or_later_v05_for_full_repo_optimized |
| maximal_research_not_for_signing | 10029 | 27714 | 0 | 9928 | 9928 | not_a_signing_target_research_only |

## Pareto Frontier

| Variant | Coverage | Auth. Reach. | lambda2 | G | Nodes signed | Files included | Genesis-core eligible | Hashed-only | Directed gaps |
|---|---|---|---|---|---|---|---|---|---|
| v04_core_only_fix18_preserved | 1.0 | {'traceable_count': 56, 'total_count': 57, 'ratio': '56/57 plus one declared axiomatic Node 0 exception'} | not_recomputed_for_fix18_core | not_comparable_to_full_repo | 57 | 57 | 57 | 0 | 0 |
| v04_core_plus_full_repo_support | 1.0 | {'authority_reachability': 0.528846, 'authority_forward_trace_coverage': 0.005484, 'verification_backtrace_coverage': 0.005484} | {'clique': 0.000223125904, 'star': 0.0, 'star_status': 'cheeger_lb_fallback'} | baseline_full_repo_not_optimized | 0 | 10029 | 57 | 9974 | 9974 |
| v05_full_repo_optimized_candidate | 1.0 | {'authority_reachability': 0.528846, 'authority_forward_trace_coverage': 0.005484, 'verification_backtrace_coverage': 0.005484, 'fix30_added_typed_trace_candidate_edges': 46} | {'clique': 0.000223125904, 'star': 0.0, 'star_status': 'not_available_budget_fallback_for_fiedler_vector'} | 0.103428844 | 0 | 10029 | 57 | 9928 | 9928 |
| maximal_research_not_for_signing | 1.0 | research_frontier_not_a_signing_claim | {'clique': 0.000223125904, 'star': 0.0} | 0.103428844 | 0 | 10029 | 0 | 9928 | 9928 |

## Why Not Selected

| Variant | Reason | Evidence |
|---|---|---|
| v04_core_plus_full_repo_support | human_choice_required | Current Phase 1573 guidance is compatible with Fix18 only; v0.4 core plus support requires a guidance patch. |
| v05_full_repo_optimized_candidate | deferred_to_v0.5 | Fix30 optimized whole-repo output remains research-only and requires new scope or a later v0.5 route. |
| maximal_research_not_for_signing | out_of_scope_v0.4 | Research-only frontier; not a signing target. |

## Signing Scope Decision

```json
{
  "blocking_questions": [
    "Confirm whether Phase 1573 should sign only the Fix18 v0.4 core candidate.",
    "If v0.4 should reference the full-repo support graph, authorize a Block 6 guidance patch first.",
    "If the optimized whole-repo candidate should become a signing target, route it to v0.5 or a new explicit scope.",
    "Decide whether the broader full-repo route requires CDL-098 or an ADR amendment before signing."
  ],
  "scope_decision_requires_human_authorization": true,
  "v04_signing_input": "fix18_core_only",
  "v05_signing_input": "deferred"
}
```

## Signing Batch Rule

Only nodes with a declared typed trace and an accepted proof class can be
assigned to an Atlas semantic signing batch. Hashed repo material may appear in
a signed source-tree manifest, but is not a semantically rooted Atlas node and
is not Genesis-core signing-batch-ready.

## Human Choices Required

- Confirm Fix18 core-only v0.4 as the Phase 1573 signing input, or authorize a
  Block 6 guidance patch for a broader v0.4 support route.
- Decide whether the Fix30 full-repo optimized candidate is a later v0.5 route.
- Decide whether broader full-repo signing requires CDL-098 or an ADR amendment.

## Non-claims

- No Genesis v0.4 signing occurred.
- No Genesis v0.5 signing occurred.
- No node upload occurred.
- No canonical graph mutation occurred.
- No public graph publication occurred.
- No public repository push occurred.
- No public RC activation occurred.
- No runtime activation occurred.
- No economic activation occurred.
- No sidecar activation occurred.
- No ADR/CDL mutation occurred.
- No public-path authorization occurred.

## Non-claim Tokens

- `no_genesis_v04_signing`
- `no_genesis_v05_signing`
- `no_node_upload`
- `no_canonical_graph_mutation`
- `no_public_graph_publication`
- `no_public_repo_push`
- `no_public_rc_activation`
- `no_runtime_activation`
- `no_economic_activation`
- `no_sidecar_activation`
- `no_adr_cdl_mutation`
- `no_public_path_authorization`
