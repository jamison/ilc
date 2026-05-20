# ILC CDL-092 CapProof Prelock 1404 v0.1

Phase: 1404
Date: 2026-05-20
Status: prelocked; CDL-092 remains open and unratified

```text
cdl_092_prelock_committed_phase_1404
cdl_092_not_ratified_phase_1404
cdl_092_scope_constants_locked_phase_1404
```

## 1. Purpose

This document prelocks the CDL-092 CapProof scope constants for Phase 1405
ratification review. It consumes the Phase 1402 opening and Phase 1403
deliberation artifacts, resolves the content-address output-format
carry-forward, and preserves all non-activation boundaries.

CDL-092 remains open and unratified after Phase 1404.

## 2. Claim Verification Table

| Claim | File or symbol checked | Result |
|-------|------------------------|--------|
| CDL-092 is open at Phase 1402 mutation commit | `git show 5d3ef87d:docs/specs/ilc_constitutional_decision_log_v0.1.md` | confirmed |
| Phase 1403 deliberation doc is present with all four Q resolutions | `docs/specs/ilc_cdl_092_capproof_deliberation_1403_v0.1.md` | confirmed |
| Phase 1403 records the output-format carry-forward | `docs/specs/ilc_cdl_092_capproof_deliberation_1403_v0.1.md` section 8 | confirmed |
| Project-wide canonical NodeID format exists | `docs/adr/ADR_0001_Canonical_Encoding_and_MCP_MVP.md`; `ilc_core/encoding/cidv1.py` | confirmed |
| ADR-0001 is accepted | `docs/adr/README.md`; ADR-0001 status header | confirmed |
| Broad claim "no CapProof runtime exists yet" | repo search | not confirmed; historical CLI/benchmark scaffold exists |
| Narrow claim "no CDL-092 CapProof pricing/probe activation exists" | CDL-092 row, J-005, Phase 1402/1403 artifacts | confirmed |

## 3. Carry-Forward Resolution

Phase 1403 left one item open: whether `cidv1_sha2_256_candidate` should remain
the CapProof content-address output format or be replaced by an existing
project-wide ratified CID/hash profile.

Resolution: replace the placeholder with the existing accepted ADR-0001 NodeID
profile:

```text
CAPPROOF_CONTENT_ADDRESS_OUTPUT_FORMAT = adr_0001_nodeid_cidv1_dag_cbor_sha2_256_multihash
```

Evidence:

- ADR-0001 is accepted and defines NodeID as `CIDv1(multicodec="dag-cbor",
  multihash=H(dag_cbor_bytes))`.
- ADR-0001 sets MVP default hash function to `sha2-256`.
- `ilc_core/encoding/cidv1.py` implements CIDv1 + DAG-CBOR + SHA2-256
  multihash and exposes `node_id_from_obj(obj)`.
- CDL-075 later ratifies graph persistence using the same `node_id_from_obj`
  CIDv1 derivation rule.

The Phase 1403 `cidv1_sha2_256_candidate` placeholder is therefore superseded
for CDL-092 prelock by the accepted ADR-0001 profile. A later content-addressing
ADR may still introduce a future CapProof-specific profile, but it would need to
amend or supersede this prelock explicitly.

## 4. Locked Scope Constants

```text
cdl_092_scope_constants_locked_phase_1404
```

| Constant | Locked value | Source / note |
|----------|--------------|---------------|
| `CAPPROOF_CONTENT_ADDRESS_SCHEMA` | `capproof.content_address.v1` | Confirmed from Phase 1403. |
| `CAPPROOF_CONTENT_ADDRESS_SERIALIZATION` | `canonical_json_sort_keys_true_allow_nan_false_compact_separators_v1` | Confirmed for JSON projection / machine-verifiable envelope export; final NodeID output follows ADR-0001 DAG-CBOR CIDv1 profile. |
| `CAPPROOF_CONTENT_ADDRESS_OUTPUT_FORMAT` | `adr_0001_nodeid_cidv1_dag_cbor_sha2_256_multihash` | Amended from `cidv1_sha2_256_candidate` after ADR-0001 discovery. |
| `CAPPROOF_CONTENT_ADDRESS_TIME_FIELD` | `epoch_id_plus_measurement_sequence` | Confirmed from Phase 1403. |
| `CAPPROOF_WALL_CLOCK_IN_HASH_INPUT` | `false` | Protocol time only; wall clock is not a validity source. |
| `CAPPROOF_CV_SIGNATURE_DOMAIN` | `ILC_CAPPROOF_CV_V1` | Confirmed from Phase 1403. |
| `CAPPROOF_CV_SIGNER_ROLE` | `capproof_cv_signer` | Confirmed from Phase 1403. |
| `CAPPROOF_IDENTITY_ANCHOR_REQUIRED` | `adr_0038_agent_birth_attestation_genesis_rooted` | Confirmed from Phase 1403 and ADR-0038. |
| `CAPPROOF_SECRET_MATERIAL_IN_PAYLOAD_ALLOWED` | `false` | Confirmed from Phase 1403 and ADR-0038 secure-output rule. |
| `CAPPROOF_PRICE_MULTIPLIER_MIN` | `Decimal("0.85")` | Confirmed from Phase 1403. |
| `CAPPROOF_PRICE_MULTIPLIER_BASELINE` | `Decimal("1.00")` | Confirmed from Phase 1403. |
| `CAPPROOF_PRICE_MULTIPLIER_MAX` | `Decimal("1.15")` | Confirmed from Phase 1403. |
| `CAPPROOF_PRICE_BAND_MODE` | `multiplicative_decimal_multiplier` | Confirmed from Phase 1403. |
| `CAPPROOF_PRICE_BAND_CLAMP_ORDER` | `compute_score_then_clamp_multiplier_then_apply_existing_price_clamps` | Confirmed from Phase 1403. |
| `CAPPROOF_DIRECT_ILC_REWARD_ALLOWED` | `false` | Confirmed from J-005 and Phase 1403. |
| `CAPPROOF_APPLICABILITY_MODE` | `explicit_lane_allowlist` | Confirmed from Phase 1403. |
| `CAPPROOF_DEFAULT_FOR_UNLISTED_LANES` | `not_applicable` | Confirmed from Phase 1403. |
| `CAPPROOF_SUBJECTIVE_JURY_REVIEW_APPLICABILITY` | `excluded` | Locked in Phase 1404 to avoid hardware-weighted subjective judgment. |
| `CAPPROOF_VALIDATOR_BFT_WEIGHT_APPLICABILITY` | `excluded_pending_separate_consensus_authority` | Locked in Phase 1404; CDL-092 must not alter BFT voting weight or safety quorum. |
| `CAPPROOF_PUBLIC_CLAIMABILITY_APPLICABILITY` | `excluded` | Confirmed from Phase 1403; CDL-088 governs public claimability. |

## 5. Canonical Input Envelope

The logical CapProof content-address envelope must include these fields before
ADR-0001 NodeID derivation:

| Field | Requirement |
|-------|-------------|
| `schema_version` | Must equal `capproof.content_address.v1`. |
| `agent_id` | Must match the identity bound by the CV signing chain. |
| `agent_birth_attestation_ref` | Must reference ADR-0038-compliant birth attestation or authorized successor chain. |
| `epoch_id` | Protocol epoch identifier. |
| `measurement_sequence` | Deterministic per-epoch sequence or recheck number. |
| `probe_suite_ref` | Content-addressed runtime-supplied probe-suite reference. |
| `probe_binary_refs` | Canonical ordered list of runtime-supplied probe binary/input references. |
| `probe_input_bundle_hash` | Hash of canonical runtime-supplied inputs. |
| `probe_output_bundle_hash` | Hash of canonical probe outputs. |
| `capability_vector_hash` | Hash of the signed Capability Vector payload. |
| `environment_profile_hash` | Hash of the non-secret environment declaration. |
| `pricing_band_ref` | Reference to the CDL-092 pricing-band constants. |

Any JSON projection used for machine-verifiable exports, test fixtures, or
intermediate audit material must use deterministic key ordering equivalent to:

```python
json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
```

The canonical NodeID output must use the ADR-0001 path:

```text
encode_dag_cbor(strict_string_key_payload) -> sha2-256 multihash -> CIDv1
```

## 6. Pricing Band

The CapProof pricing band is multiplicative and Decimal-only:

```text
capability_multiplier = clamp(raw_capability_multiplier, Decimal("0.85"), Decimal("1.15"))
caproof_adjusted_ecu_price = pre_capproof_ecu_price * capability_multiplier
final_ecu_price = existing_downstream_price_clamps(capproof_adjusted_ecu_price)
```

No float is permitted for the CapProof price multiplier or any ECU, reward,
settlement, or staking value.

## 7. Applicability

CapProof applies only by explicit lane allowlist. It is not an all-ECU-work
modifier.

| Lane type | Locked applicability |
|-----------|----------------------|
| Epoch-start capability check-in | applicable after runtime activation |
| Scheduling and queue placement | applicable after runtime activation |
| CapProof-covered maintenance tasks | applicable after review-lane wiring |
| Objective high-throughput worker tasks | candidate-applicable after lane-specific validation |
| Subjective jury review | excluded |
| Reviewer payment | excluded |
| Public claimability | excluded |
| Validator BFT voting weight or safety quorum | excluded pending separate consensus authority |
| ECU-to-ILC settlement/conversion | excluded |

## 8. Non-Authorizations

Phase 1404 does not authorize:

- CDL-092 ratification;
- CDL register mutation;
- CapProof runtime implementation;
- CapProof pricing activation;
- production probe execution;
- direct ILC reward or minting from CapProof;
- ECU settlement or ledger writes from CapProof;
- wallet signing, wallet transfer, or wallet withdrawal behavior;
- validator reward distribution;
- reviewer payment activation;
- production jury activation;
- J-008 gate verdict changes;
- public RC publication.

CDL-092 remains open and unratified after Phase 1404:

```text
cdl_092_not_ratified_phase_1404
```

Graph delta:
`graph_delta=load_bearing_artifact_added:docs/specs/ilc_cdl_092_capproof_prelock_1404_v0.1.md -> constitutional/cdl`.
