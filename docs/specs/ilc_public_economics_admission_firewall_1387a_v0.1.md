# ILC Public Economics Admission Firewall 1387a v0.1

**Phase:** 1387a
**Date:** 2026-05-19
**Status:** PASS
**Runtime guard:** `ilc_core/ledger/public_economics_admission_firewall.py`

```text
accepted_adr_cdl_coverage_phase_1387a_executed
accepted_adr_cdl_runtime_coverage_matrix_phase_1387a
public_economics_requires_public_node_admission_verified_phase_1387a
private_visibility_excluded_from_public_economics_phase_1387a
no_unrouted_accepted_cdl_adr_functionality_before_public_rc_phase_1387a
```

## 1. Purpose

This document records the production event-construction boundary for public
economic events. Public economics means:

- protocol ECU;
- public reputation;
- public settlement rights;
- public corroboration;
- public claimability.

Private, semi-private, shard-local, or operator-local advisory scores are not
public economics and cannot construct any of those events.

## 2. Guard Contract

The runtime guard exposes:

```text
PUBLIC_ECONOMIC_EVENT_TYPES = {
  public_ecu,
  public_reputation,
  public_settlement,
  public_corroboration,
  public_claimability
}
```

Before constructing any event, `build_public_economic_event()` requires:

1. `visibility == "public"`.
2. Machine-checkable `public_graph_admission_evidence` with:
   - `admission_id`;
   - non-negative integer `admitted_epoch`;
   - 64-character lowercase hex `admission_proof_sha256`;
   - `public_graph_root`.
3. `eligible_public_state` in:
   - `public_admitted`;
   - `public_evaluated`;
   - `public_promoted_zero_carry_forward`.
4. Zero private promotion carry-forward.
5. No private timestamp, private commitment, opaque commitment, or quantum hedge
   field used as public priority evidence.
6. Valid CDL-038 promotion-continuity record if the public node was promoted
   from private material.
7. No float values in the source node or event payload.

The guard returns a deterministic event with canonical JSON hashing using
`sort_keys=True`, compact separators, and `allow_nan=False`.

## 3. Fail-Closed Rejections

| Rejection | Token |
| --- | --- |
| non-public visibility | `private_visibility_excluded_from_public_economics_phase_1387a` |
| missing admission evidence | `public_graph_admission_evidence_missing_phase_1387a` |
| caller-supplied boolean instead of admission proof | `public_graph_admission_evidence_missing_phase_1387a` |
| private timestamp/hash/opaque commitment priority | `private_or_opaque_commitments_do_not_create_retroactive_public_priority` |
| non-zero private carry-forward | `private_promotion_does_not_rewrite_existing_public_reward_history` |
| missing promotion continuity record for promoted node | `public_promotion_continuity_record_required_phase_1387a` |
| invalid promotion continuity record | `public_promotion_continuity_record_invalid_phase_1387a` |
| float in source or payload | `public_economic_source_node_float_forbidden_phase_1387a` / `public_economic_event_payload_float_forbidden_phase_1387a` |

## 4. Protected Event Types

| Event type | Protected effect |
| --- | --- |
| `public_ecu` | protocol ECU construction or attribution |
| `public_reputation` | public reputation construction or update |
| `public_settlement` | public settlement right or settlement event |
| `public_corroboration` | public corroboration credit or reuse credit |
| `public_claimability` | public claimability proof or claim event |

## 5. Relationship to Existing Canon

ADR-0022 establishes that pressure may be continuous across private and public
space, but public legitimacy is discontinuous at explicit boundary crossings.
The node schema synthesis clarifies that historical "shadow economics" language
means operator-local advisory scoring only, not protocol ECU, public reputation,
or public settlement rights.

CDL-038 promotion continuity already blocks validation-state, corroboration, and
reputation carry-forward at promotion. Phase 1387a extends that boundary to
private timestamps, private commitments, opaque commitments, and the quantum
hedge pattern by refusing to use those fields as public priority evidence.

CDL-088 ratifies the `no_private_or_shadow_economics_claimability_v1` constant.
This runtime guard supplies the public-RC construction boundary required by that
constant.

## 6. Non-Authorization

This firewall does not activate public claimability, public ECU, public
reputation, public settlement, public corroboration, wallet actions, ECU minting,
ILC settlement, public routes, public P2P, source publication, release signing,
counsel approval, or legal conclusions. It only proves a fail-closed admission
boundary that later phases must use before constructing public economic events.

## 7. Graph Delta

`graph_delta=load_bearing_artifact_changed:ilc_core/ledger/public_economics_admission_firewall.py -> public_rc_activation_gate`
