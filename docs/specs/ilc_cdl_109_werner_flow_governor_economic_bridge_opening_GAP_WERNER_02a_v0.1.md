# CDL-109 — Werner Flow-Governor Economic Bridge Authority

Status: RATIFIED
Ratified in: Phase GAP-WERNER-02a
Ratification date: 2026-08-03
Governing CDLs: CDL-053, CDL-096, CDL-108
Phase 1263 decision preserved: `direct_werner_ecu_creation_rejected_phase_1263`

## 1. Ratified Scope (v1)

CDL-109 authorizes Werner topology pressure as a bounded bridge reweighting input
to CDL-108 backward attribution. This is not direct ECU minting, not ILC
settlement, and not wallet-visible Werner credit.

Ratified v1 scope:

| Constant or rule | Ratified value |
|---|---|
| Application target | CDL-108 backward attribution traversal only |
| Application stage | Pre-normalization |
| Application formula | `werner_adjusted_raw_score = raw_path_score * (Decimal("1") + flow_budget)` |
| `runtime_policy_cap` | `Decimal("0.10")` |
| `flow_budget` | `min(Decimal("0.10"), candidate_priority)` |
| Candidate priority source | `compute_werner_smoothed_candidate_priority()` in `ilc_core/economics/werner_runtime.py` |
| Residual handling | Clipped or non-issued residual is not redistributed unless already governed by CDL-108 |

Werner reweighting modifies the CDL-108 `raw_path_score` before normalization.
CDL-108 normalization, per-node caps, per-agent caps, per-cluster caps, duplicate
collapse, and residual treatment continue to govern the resulting allocation.

## 2. Paths Explicitly Excluded from v1 Scope

CDL-109 does not authorize Werner application to:

- Passive ECU (CDL-060).
- Forward attribution.
- Wallet transfers.
- ILC settlement.
- Maintenance lottery distribution under the CDL-093 lane.
- Any path outside CDL-108 backward attribution traversal.

The CDL-053/CDL-093 maintenance-lottery lane remains separately gated and is not
activated by this decision.

## 3. Decimal-Only and Fail-Closed Constraints

All bridge arithmetic is Decimal-only. No float value may enter Werner bridge
economics, attribution reweighting, settlement inputs, or any hash/signature
payload that carries bridge evidence.

Boundary constraints:

- Non-finite Decimal inputs (`NaN`, `Infinity`) must be rejected with
  `ValueError("invalid_amount_non_finite")`.
- Missing, malformed, stale, or untrusted Werner evidence fails closed.
- Fail-closed absent evidence returns `flow_budget = Decimal("0")`,
  records `werner_context_present = False`, and emits
  `werner_context_absent_no_reweight`.
- The bridge must never guess, interpolate, or substitute a default pressure
  value.

For public RC, Werner context is optional. Absent context yields no reweighting
instead of wedging CDL-108 backward attribution.

## 4. CDL-108 Cap Confirmation

Werner reweighting operates before CDL-108 normalization. The following CDL-108
caps apply after Werner reweighting:

| Cap | Ratified value |
|---|---|
| Per-node cap | `BACKWARD_ATTRIBUTION_PER_NODE_CAP = Decimal("0.05")` |
| Per-agent cap | `BACKWARD_ATTRIBUTION_PER_AGENT_CAP = Decimal("0.10")` |
| Per-cluster cap | `BACKWARD_ATTRIBUTION_PER_CLUSTER_CAP = Decimal("0.25")` |

Werner cannot circumvent CDL-108 caps. Any clipping remains unissued under the
CDL-108 residual rule.

## 5. Supersession Table

The following blockers or authorization states are superseded only within the
bounded CDL-108 attribution-bridge scope:

| Token | Previous state | CDL-109 disposition |
|---|---|---|
| `WERNER_FLOW_GOVERNOR_SCOPE_AUTHORIZED` | `false` under CDL-053 | Authorized for CDL-108 backward attribution reweighting only |
| `WERNER_CREDIT_WIRING_NOT_ACTIVATED` | `True` in `werner_runtime.py` | Guard clearance authorized for bounded bridge, to be executed only in GAP-WERNER-02b |
| `cdl_096_runtime_activation_not_authorized_phase_1553p` | Not authorized | Superseded within CDL-108 backward attribution scope only |
| `runtime_policy_cap` | Deferred in CDL-096 | Ratified as `Decimal("0.10")` |

The following tokens are permanently preserved and are not changed by CDL-109:

| Token | State | Authority |
|---|---|---|
| `direct_werner_ecu_creation_rejected_phase_1263` | Permanently preserved | Phase 1263 |
| `WERNER_DIRECT_HEAT_TO_ECU_MINTING` | `not_authorized` | CDL-053 section 8 |
| `WERNER_DIRECT_ECU_CREATION_AUTHORIZED` | `false` | CDL-053 |
| `WERNER_WALLET_MUTATION_AUTHORIZED` | `false` | CDL-053 |
| `WERNER_ILC_SETTLEMENT_AUTHORIZED` | `false` | CDL-053 |
| `WERNER_LIVE_DISTRIBUTION_AUTHORIZED` | `false` | CDL-053 |

Tokens still not authorized after CDL-109:

| Scope | Status |
|---|---|
| Maintenance lottery live distribution (CDL-093 lane) | Not authorized |
| Passive ECU Werner weighting | Not authorized |
| Direct productive-credit conversion from local Werner credit | Not authorized |
| Wallet-visible Werner credit | Not authorized |
| ILC settlement from Werner | Not authorized |
| Generalized ECU money transfer | Not authorized |
| Werner applied to forward attribution | Not authorized |
| Werner applied outside CDL-108 backward attribution in v1 | Not authorized |

## 6. CDL-053 Blocker Satisfaction Clause

CDL-109 is the governance act satisfying
`WERNER_CDL_093_AMENDMENT_REQUIRED_BEFORE_USE = true` for the bounded CDL-108
attribution-bridge scope. It does not amend CDL-093 or activate the maintenance
lottery lane.

## 7. Ratified Constants

```python
RUNTIME_POLICY_CAP = Decimal("0.10")
WERNER_BRIDGE_SCOPE = "cdl_108_backward_attribution_only_v1"
WERNER_ATTRIBUTION_FORMULA = "raw_path_score * (Decimal('1') + flow_budget)"
WERNER_APPLICATION_STAGE = "pre_normalization"
WERNER_CONTEXT_ABSENT_TOKEN = "werner_context_absent_no_reweight"
WERNER_CDL_109_VERSION = "cdl_109_werner_flow_governor_economic_bridge_GAP_WERNER_02a.v0.1"
```

## 8. Non-Claims

This decision does not clear `WERNER_CREDIT_WIRING_NOT_ACTIVATED`, implement a
Werner attribution bridge module, wire Werner into traversal, activate public RC,
activate mainnet, mint ECU, mint or settle ILC, mutate wallets, activate
maintenance-lottery distribution, authorize passive ECU weighting, or push any
public mirror.
