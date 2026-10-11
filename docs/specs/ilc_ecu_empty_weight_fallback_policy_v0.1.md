# ILC ECU Empty-Weight Fallback Policy v0.1

**Phase:** `GAP-ECU-MONTHLY-CLOSE-EMPTY-POOL-FALLBACK-POLICY-00`  
**Status:** RATIFIED by Genesis GO on 2026-10-03  
**Output token:** `fallback_policy_ratified_GAP_ECU_MONTHLY_CLOSE_EMPTY_POOL_FALLBACK_POLICY_00`

## 1. Purpose

This policy ratifies the canonical empty-weight branch of the normal monthly-close distribution algorithm. It does not create a discretionary side canon, a carry-forward pool, or a wallet-balance-driven settlement path.

At monthly close, each distribution pool is resolved in this order:

1. If close-bearing ECU attribution weights exist for the pool, distribute the pool by those weights.
2. If the pool's close-bearing attribution weight map is empty, distribute that epoch-local pool to the deterministic fallback set fixed before the issuance interval opened.
3. If the fallback set is empty, the close hard-stops with `fallback_set_empty_observe_00_hard_stop`.

No ILC may evaporate, be operator-redirected, or carry forward solely because a performer or auditor weight map is empty.

## 2. Weight Boundary

Wallet ECU balances and close-bearing ECU attribution weights are distinct. A wallet balance row does not by itself make an agent a distribution-weight recipient. The normal path consumes attribution weights. The fallback path exists only for the rare case where that attribution-weight map is empty at close.

The fallback set is not discovered by gRPC enumeration and is not expanded by operator judgment. It is derived from committed pre-open configuration and identity constants.

## 3. Epoch 1 Eligible Set

The Epoch 1 fallback set is:

| Role | AgentID | Source |
|---|---|---|
| Genesis Agent 01 | `c43f69fcc4dfd021f5e468824c9560c03c45c601f8d004be4d244356ce6043849b9cf2af38bc51a40c1c4bc3e71b04d9` | `ilc_core/epoch/genesis_settlement_destination.py:31` |
| VPS Validator 1 | `97fc59d642f4df19bc017ede43e0e15202d933c89913201da5945b672d624fbf963262e795d23309362e5b419fd5ba09` | `config/public_rc_validators/genesis.json` |
| VPS Validator 2 | `8c3b517ece61ca111a1e44939b40c2fb85e96d0295b935ce50b2f95204cd938d23c244178a7367b21fc1622f5a95e62f` | `config/public_rc_validators/genesis.json` |
| VPS Validator 3 | `8b4370fe4ffa16bbb9fc8430d638d9d19a12d8efad02964c85a867f65d942f98230a0b78baaa59b340ba88c6c480ac19` | `config/public_rc_validators/genesis.json` |
| VPS Validator 4 | `b306d66948b4dca95aade079b42931dd553432131d7138cc2b6e8ba804807fc881689bfc7fc0d9568e198bdbbea8d1e9` | `config/public_rc_validators/genesis.json` |

The `validator_1_config.json` through `validator_4_config.json` files were read as committed validator harness configuration sources, but the validator AgentIDs are bound in `config/public_rc_validators/genesis.json`.

## 4. Weighting Rule

For Epoch 1, the fallback weighting rule is equal weight across the five eligible agents:

`weight = 0.2` for each eligible AgentID.

Future liveness-weighted fallback rules require separate ratification and committed pre-open evidence. They are not authorized by this policy.

Residual quantum assignment uses largest remainder; ties among equal remainders are broken lexicographically by AgentID, matching `_allocate_pool_to_agents()` in `ilc_core/epoch/epoch_distribution_writer.py`.

Epochs after Epoch 1 require either non-empty close-bearing attribution weights or a new pre-open fallback eligible-set ratification artifact for that epoch. This Epoch 1 policy must not be silently reused for later issuance intervals.

## 5. Auditor Pool

The auditor pool uses the same fallback set and weights when its own close-bearing attribution weight map is empty. The performer and auditor pools remain separately reported, but the same eligible set may receive both branches. Implementation may combine the two empty-weight pool allocations for arithmetic efficiency only if evidence still reports the performer and auditor pool sources separately.

## 6. Epoch 1 Conservation Example

From `out/gap_observe_live_accrual_census_00/distribution_dry_run.json`:

| Quantity | ILC |
|---|---:|
| Total epoch allocation | `371609.891246338` |
| Performer pool | `297287.91299707` |
| Auditor pool | `55741.48368695` |
| Genesis overhead pool | `18580.494562318` |
| Combined empty-weight fallback value | `353029.39668402` |
| Per eligible fallback share | `70605.879336804` |

Epoch 1 equal fallback distribution:

| Agent | Empty-weight fallback share | Genesis overhead | Total settlement delta |
|---|---:|---:|---:|
| `8b4370fe4ffa16bbb9fc8430d638d9d19a12d8efad02964c85a867f65d942f98230a0b78baaa59b340ba88c6c480ac19` | `70605.879336804` | `0` | `70605.879336804` |
| `8c3b517ece61ca111a1e44939b40c2fb85e96d0295b935ce50b2f95204cd938d23c244178a7367b21fc1622f5a95e62f` | `70605.879336804` | `0` | `70605.879336804` |
| `97fc59d642f4df19bc017ede43e0e15202d933c89913201da5945b672d624fbf963262e795d23309362e5b419fd5ba09` | `70605.879336804` | `0` | `70605.879336804` |
| `b306d66948b4dca95aade079b42931dd553432131d7138cc2b6e8ba804807fc881689bfc7fc0d9568e198bdbbea8d1e9` | `70605.879336804` | `0` | `70605.879336804` |
| `c43f69fcc4dfd021f5e468824c9560c03c45c601f8d004be4d244356ce6043849b9cf2af38bc51a40c1c4bc3e71b04d9` | `70605.879336804` | `18580.494562318` | `89186.373899122` |

Conservation:

`89186.373899122 + (4 * 70605.879336804) = 371609.891246338`

For this example, the performer and auditor pool quanta are exactly divisible by five; `explicit_rounding_sinks_ilc = 0` and `carry_forward_record_count = 0`.

## 7. Implementation Gate

`GAP-ECU-MONTHLY-CLOSE-EMPTY-POOL-FALLBACK-IMPL-00` must implement this policy exactly:

- `load_fallback_eligible_set()` must read the canonical machine-readable artifact `docs/specs/ilc_ecu_empty_weight_fallback_eligible_set_v0.1.json`.
- `_allocate_pool_to_agents()` must use the fallback set only when the close-bearing pool weight map is empty or all-positive-filtered weights are empty.
- `_build_carry_forward_out_records()` must not create performer/auditor carry-forward records solely because the attribution weight map is empty.
- `verify_epoch_conservation_before_commit()` must still pass before any settlement write.

## 8. Non-Claims

This phase does not execute OBSERVE-00, close an epoch, write LMDB, mint ECU, mint ILC, distribute settlement balances, run `commit_epoch_distribution()`, modify runtime code, discover agents via gRPC, update the public mirror, or authorize production/mainnet activation.
