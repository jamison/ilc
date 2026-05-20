# ILC CDL-092 CapProof Ratification Evidence 1405 v0.1

Phase: 1405
Date: 2026-05-20
Status: ratification evidence committed; CDL register mutation performed in separate constitutional commit

Required tokens:

```text
cdl_092_ratified_phase_1405
cdl_092_capproof_ratification_evidence_committed
cdl_092_historical_hardening_phase_1402_ref_asserted
capproof_pricing_activation_not_authorized_phase_1405
```

## 1. Ratification Statement

Phase 1405 ratifies CDL-092 for CapProof content-addressing, Capability Vector
signing-chain scope, and the bounded +/-15% ECU pricing-band rule locked by
Phase 1404.

This ratification locks the constitutional scope constants listed below. It does
not activate CapProof pricing, execute production probes, adjust live ECU
pricing, mint ILC, settle ECU, activate wallet behavior, activate reviewer
payment, change the Phase 1398 J-008 gate verdict, or activate production jury
behavior.

## 2. Claim Verification

| Claim | File/symbol checked | Result |
|-------|---------------------|--------|
| CDL-092 is open before Phase 1405 mutation | `docs/specs/ilc_constitutional_decision_log_v0.1.md` row `CDL-092` | confirmed before C2 mutation |
| Phase 1404 prelock scope constants exist | `docs/specs/ilc_cdl_092_capproof_prelock_1404_v0.1.md` | confirmed |
| Phase 1404 prelock token exists | `cdl_092_prelock_committed_phase_1404` | confirmed |
| Phase 1404 non-ratification token exists | `cdl_092_not_ratified_phase_1404` | confirmed |
| Phase 1404 scope-lock token exists | `cdl_092_scope_constants_locked_phase_1404` | confirmed |
| Phase 1402 historical CDL-092 row is open | `git show 5d3ef87d:docs/specs/ilc_constitutional_decision_log_v0.1.md` | confirmed |
| No CapProof code exists | repo search for CapProof runtime surfaces | not confirmed; historical CLI/benchmark scaffold exists |
| No CDL-092-authorized CapProof pricing/probe activation exists | CDL-092 row plus Phase 1402-1404 artifacts | confirmed |
| J-008 gate still records `CAPPROOF_CDL_RATIFIED` as NOT_MET before this phase | `ilc_core/epistemic/jury_activation_gate.py` | confirmed; Phase 1405 does not flip the gate |
| MemPalace advisory recall found no newer CapProof ratification source | `tools/mempalace/query_tiered.py` tier A query | confirmed; direct repo reads remain authoritative |

## 3. Ratified Scope Constants

| Constant | Ratified value |
|----------|----------------|
| `CAPPROOF_CONTENT_ADDRESS_SCHEMA` | `capproof.content_address.v1` |
| `CAPPROOF_CONTENT_ADDRESS_SERIALIZATION` | `canonical_json_sort_keys_true_allow_nan_false_compact_separators_v1` |
| `CAPPROOF_CONTENT_ADDRESS_OUTPUT_FORMAT` | `adr_0001_nodeid_cidv1_dag_cbor_sha2_256_multihash` |
| `CAPPROOF_CONTENT_ADDRESS_TIME_FIELD` | `epoch_id_plus_measurement_sequence` |
| `CAPPROOF_WALL_CLOCK_IN_HASH_INPUT` | `false` |
| `CAPPROOF_CV_SIGNATURE_DOMAIN` | `ILC_CAPPROOF_CV_V1` |
| `CAPPROOF_CV_SIGNER_ROLE` | `capproof_cv_signer` |
| `CAPPROOF_IDENTITY_ANCHOR_REQUIRED` | `adr_0038_agent_birth_attestation_genesis_rooted` |
| `CAPPROOF_SECRET_MATERIAL_IN_PAYLOAD_ALLOWED` | `false` |
| `CAPPROOF_PRICE_MULTIPLIER_MIN` | `Decimal("0.85")` |
| `CAPPROOF_PRICE_MULTIPLIER_BASELINE` | `Decimal("1.00")` |
| `CAPPROOF_PRICE_MULTIPLIER_MAX` | `Decimal("1.15")` |
| `CAPPROOF_PRICE_BAND_MODE` | `multiplicative_decimal_multiplier` |
| `CAPPROOF_PRICE_BAND_CLAMP_ORDER` | `compute_score_then_clamp_multiplier_then_apply_existing_price_clamps` |
| `CAPPROOF_DIRECT_ILC_REWARD_ALLOWED` | `false` |
| `CAPPROOF_APPLICABILITY_MODE` | `explicit_lane_allowlist` |
| `CAPPROOF_DEFAULT_FOR_UNLISTED_LANES` | `not_applicable` |
| `CAPPROOF_SUBJECTIVE_JURY_REVIEW_APPLICABILITY` | `excluded` |
| `CAPPROOF_VALIDATOR_BFT_WEIGHT_APPLICABILITY` | `excluded_pending_separate_consensus_authority` |
| `CAPPROOF_PUBLIC_CLAIMABILITY_APPLICABILITY` | `excluded` |

## 4. Serialization and Numeric Safety

The ratified content-address serialization rule is:

```python
json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
```

The final NodeID/CID output profile is the accepted ADR-0001 profile:

```text
adr_0001_nodeid_cidv1_dag_cbor_sha2_256_multihash
```

The ratified pricing band uses exact decimal multipliers only:

```python
Decimal("0.85")
Decimal("1.00")
Decimal("1.15")
```

Floating-point fee or reward state is not authorized by CDL-092.

## 5. Historical Hardening

Historical hardening command:

```bash
git show 5d3ef87d:docs/specs/ilc_constitutional_decision_log_v0.1.md | rg -n "^\\| CDL-092 \\|"
```

Result: the Phase 1402 C2 register state contains exactly one CDL-092 row with
`status: open`, `opened_phase: 1402`, `opening_token:
cdl_092_capproof_opened_phase_1402`, and `historical_non_ratification_token:
cdl_092_not_ratified_phase_1402`.

Token:

```text
cdl_092_historical_hardening_phase_1402_ref_asserted
```

## 6. Non-Authorizations

The following remain unauthorized after Phase 1405:

| Surface | Phase 1405 disposition |
|---------|------------------------|
| CapProof pricing activation | not authorized |
| Production probe execution | not authorized |
| Live ECU price adjustment | not authorized |
| Direct ILC reward from CapProof | not authorized |
| ILC minting | not authorized |
| ECU settlement | not authorized |
| Wallet behavior | not authorized |
| Reviewer payment | not authorized |
| J-008 gate verdict flip | not authorized |
| Production jury activation | not authorized |

Required non-activation token:

```text
capproof_pricing_activation_not_authorized_phase_1405
```

## 7. Register Mutation Boundary

The evidence document and tests are committed before the CDL mutation. The CDL
register mutation is limited to the CDL-092 row and is performed separately with:

```bash
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1405
```

The mutation records:

```text
cdl_092_ratified_phase_1405
```

## 8. Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_cdl_092_capproof_ratification_evidence_1405_v0.1.md -> constitutional/cdl
```
