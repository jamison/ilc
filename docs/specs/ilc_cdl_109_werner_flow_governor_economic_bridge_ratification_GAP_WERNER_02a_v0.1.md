# CDL-109 Ratification Evidence — Werner Flow-Governor Economic Bridge Authority

Phase: GAP-WERNER-02a
Date: 2026-08-03
Verdict: RATIFIED
GO phrase: `GO Phase GAP-WERNER-02a WERNER-CDL-DELIBERATION`

## 1. Authority Chain

CDL-109 is ratified as a bounded successor authority over a narrow bridge
surface:

| Source | Preserved or consumed authority |
|---|---|
| Phase 1263 | Preserves `direct_werner_ecu_creation_rejected_phase_1263` and rejects direct heat-to-ECU minting |
| CDL-053 | Preserves local productive-credit boundaries and the non-settlement/non-wallet nature of Werner local credit |
| CDL-096 | Supplies Werner topology-pressure and `flow_budget = min(runtime_policy_cap, candidate_priority)` semantics while leaving `runtime_policy_cap` deferred until this phase |
| CDL-108 | Supplies the only v1 attribution path, normalization, caps, duplicate handling, residual treatment, and audit boundary |
| CDL-109 | Ratifies the bounded bridge reweighting authority for CDL-108 backward attribution only |

## 2. Ratified Constants

```python
RUNTIME_POLICY_CAP = Decimal("0.10")
WERNER_BRIDGE_SCOPE = "cdl_108_backward_attribution_only_v1"
WERNER_ATTRIBUTION_FORMULA = "raw_path_score * (Decimal('1') + flow_budget)"
WERNER_APPLICATION_STAGE = "pre_normalization"
WERNER_CONTEXT_ABSENT_TOKEN = "werner_context_absent_no_reweight"
WERNER_CDL_109_VERSION = "cdl_109_werner_flow_governor_economic_bridge_GAP_WERNER_02a.v0.1"
```

## 3. Ratified Formula

The ratified bridge formula is:

```python
flow_budget = min(Decimal("0.10"), candidate_priority)
werner_adjusted_raw_score = raw_path_score * (Decimal("1") + flow_budget)
```

This multiplication happens before CDL-108 normalization and caps. CDL-108 caps
continue to apply after reweighting:

| Cap | Ratified value |
|---|---|
| Per-node cap | `Decimal("0.05")` of `backward_pool(E)` |
| Per-agent cap | `Decimal("0.10")` of `backward_pool(E)` |
| Per-cluster cap | `Decimal("0.25")` of `backward_pool(E)` |

Clipped residual is unissued, not redistributed, unless governed by the existing
CDL-108 residual rule.

## 4. Supersession and Preservation

Superseded only within CDL-108 backward attribution reweighting:

| Token | Previous state | CDL-109 disposition |
|---|---|---|
| `WERNER_FLOW_GOVERNOR_SCOPE_AUTHORIZED` | `false` | Authorized for CDL-108 backward attribution reweighting only |
| `WERNER_CREDIT_WIRING_NOT_ACTIVATED` | `True` | Guard clearance authorized for GAP-WERNER-02b only |
| `cdl_096_runtime_activation_not_authorized_phase_1553p` | Not authorized | Superseded within bounded bridge scope only |
| `runtime_policy_cap` | Deferred | Ratified as `Decimal("0.10")` |

Permanently preserved:

| Token | Preserved state |
|---|---|
| `direct_werner_ecu_creation_rejected_phase_1263` | Direct Werner ECU creation remains rejected |
| `WERNER_DIRECT_HEAT_TO_ECU_MINTING` | `not_authorized` |
| `WERNER_DIRECT_ECU_CREATION_AUTHORIZED` | `false` |
| `WERNER_WALLET_MUTATION_AUTHORIZED` | `false` |
| `WERNER_ILC_SETTLEMENT_AUTHORIZED` | `false` |
| `WERNER_LIVE_DISTRIBUTION_AUTHORIZED` | `false` |

## 5. CDL-053 Blocker Satisfaction

CDL-109 satisfies `WERNER_CDL_093_AMENDMENT_REQUIRED_BEFORE_USE = true` only for
the bounded CDL-108 attribution-bridge scope. CDL-093 maintenance-lottery
distribution remains untouched and separately gated.

## 6. Non-Claim Inventory

CDL-109 does not authorize:

- Clearing `WERNER_CREDIT_WIRING_NOT_ACTIVATED` in this phase.
- Implementing `ilc_core/economics/werner_attribution_bridge.py` in this phase.
- Wiring Werner into backward attribution traversal in this phase.
- Direct Werner ECU minting.
- Direct heat-to-ECU creation.
- Wallet-visible Werner credit.
- ILC settlement from Werner.
- Passive ECU weighting.
- Forward-attribution weighting.
- Maintenance-lottery distribution.
- Generalized ECU money transfer.
- Any public mirror push or public RC activation.

## 7. Audit Confirmations

| Check | Result |
|---|---|
| `WERNER_CREDIT_WIRING_NOT_ACTIVATED` guard | Confirmed `True` before ratification and intentionally unchanged |
| `compute_flow_budget` signature | Confirmed present in `ilc_core/economics/werner_runtime.py` |
| Existing Werner import in attribution bridge | Confirmed absent from `ilc_core/consensus/attribution_batch_bridge.py` before ratification |
| CDL-109 in decision log before phase | Confirmed absent before mutation |
| Runtime mutation | None in this phase |
| Guard clearance | None in this phase |

## 8. Output Tokens

```text
werner_cdl_109_opened_GAP_WERNER_02a
werner_cdl_109_prelocked_GAP_WERNER_02a
werner_cdl_109_ratified_GAP_WERNER_02a
werner_cdl_deliberation_complete_GAP_WERNER_02a
```

## 9. Commit Hash Recording Boundary

The final Git commit hash is generated after this document is written. The
phase completion report records the commit hash containing this ratification
evidence; embedding the final commit hash inside the same committed blob would
change the hash-bearing commit content.
