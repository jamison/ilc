# ILC CDL-092 CapProof Deliberation 1403 v0.1

Phase: 1403
Date: 2026-05-20
Status: deliberation complete; CDL-092 remains open and unratified

```text
cdl_092_deliberation_complete_phase_1403
cdl_092_not_ratified_phase_1403
cdl_092_candidate_prelock_constants_recorded_phase_1403
```

## 1. Purpose

This document resolves the four deliberation questions opened in Phase 1402 for
CDL-092. It records candidate prelock constants for Phase 1404.

Phase 1403 does not mutate the CDL register, prelock CDL-092, ratify CDL-092,
activate CapProof pricing, execute production probes, settle ECU, mint ILC, or
change the J-008 production jury activation gate verdict.

## 2. Claim Verification Table

| Claim | File or symbol checked | Result |
|-------|------------------------|--------|
| Phase 1402 opening document records Q1-Q4 | `docs/specs/ilc_cdl_092_capproof_opening_1402_v0.1.md` | confirmed |
| CDL-092 is open and not ratified | `docs/specs/ilc_constitutional_decision_log_v0.1.md` row `CDL-092` | confirmed |
| CapProof probe set includes GEMMProbe, InferProbe, GraphProbe, BandwidthProbe, DeterminismProbe | `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md`; J-005 contract | confirmed |
| CapProof is not direct ILC reward | `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md` section 6.1; J-005 contract | confirmed |
| ADR-0038 provides Genesis-rooted agent birth-attestation anchor | `docs/adr/ADR_0038_Agent_Birth_Attestation.md` | confirmed |
| Phase 231 Gate A requires canonical serialization/signing and no user-supplied kernels | `docs/specs/ilc_capability_proof_activation_readiness_contract_231_v0.1.md` | confirmed |

MemPalace was queried as an advisory recall net during the Phase 1402 and Phase
1403 discovery work. The useful canonical context remained the direct-read repo
files listed above; MemPalace did not add a more authoritative CapProof source
than the current worktree artifacts.

## 3. Q1 Resolution: Content-Address Input

Resolution: a CapProof content address is computed over a canonical envelope,
not over ad hoc probe output text. The envelope binds the agent, epoch scope,
probe suite, runtime-supplied inputs, probe outputs, Capability Vector payload,
and non-secret environment declaration.

Candidate constants:

| Constant | Candidate value |
|----------|-----------------|
| `CAPPROOF_CONTENT_ADDRESS_SCHEMA` | `capproof.content_address.v1` |
| `CAPPROOF_CONTENT_ADDRESS_SERIALIZATION` | `canonical_json_sort_keys_true_allow_nan_false_compact_separators_v1` |
| `CAPPROOF_CONTENT_ADDRESS_OUTPUT_FORMAT` | `cidv1_sha2_256_candidate` |
| `CAPPROOF_CONTENT_ADDRESS_TIME_FIELD` | `epoch_id_plus_measurement_sequence` |
| `CAPPROOF_WALL_CLOCK_IN_HASH_INPUT` | `false` |

Required canonical input fields for Phase 1404 prelock:

| Field | Requirement |
|-------|-------------|
| `schema_version` | Must equal `capproof.content_address.v1`. |
| `agent_id` | Must match the agent identity bound by the signing chain. |
| `agent_birth_attestation_ref` | Must reference the ADR-0038-compliant birth attestation or authorized successor chain. |
| `epoch_id` | Protocol epoch identifier; wall-clock timestamps are not protocol-time authority. |
| `measurement_sequence` | Deterministic per-epoch sequence number for multiple measurements or rechecks. |
| `probe_suite_ref` | Content-addressed reference to the runtime-supplied probe-suite definition. |
| `probe_binary_refs` | Ordered canonical list of runtime-supplied probe binary/input references. |
| `probe_input_bundle_hash` | Hash of the canonical runtime-supplied inputs. |
| `probe_output_bundle_hash` | Hash of canonical probe outputs. |
| `capability_vector_hash` | Hash of the signed Capability Vector payload. |
| `environment_profile_hash` | Hash of the non-secret environment declaration used for validation and replay context. |
| `pricing_band_ref` | Reference to the CDL-092 pricing-band constants. |

Any JSON serialization used for machine-verifiable content-address inputs must be
equivalent to:

```python
json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
```

Phase 1404 may replace `cidv1_sha2_256_candidate` only if it finds an existing
ratified project-wide CID hash profile that must govern CapProof payloads.

## 4. Q2 Resolution: Capability Vector Signing Chain

Resolution: the Capability Vector signer must chain to the ADR-0038
Genesis-rooted agent birth attestation. The signer may be the birth signing key
or an authorized rotated/delegated key, but the chain must be explicit and
non-secret.

Candidate constants:

| Constant | Candidate value |
|----------|-----------------|
| `CAPPROOF_CV_SIGNATURE_DOMAIN` | `ILC_CAPPROOF_CV_V1` |
| `CAPPROOF_CV_SIGNER_ROLE` | `capproof_cv_signer` |
| `CAPPROOF_IDENTITY_ANCHOR_REQUIRED` | `adr_0038_agent_birth_attestation_genesis_rooted` |
| `CAPPROOF_SECRET_MATERIAL_IN_PAYLOAD_ALLOWED` | `false` |

The signed Capability Vector envelope must include:

| Field | Requirement |
|-------|-------------|
| `agent_id` | Same agent as the content-address envelope. |
| `agent_birth_attestation_ref` | ADR-0038-compliant attestation reference. |
| `identity_chain_ref` | ADR-0037/ADR-0038 lineage reference or authorized recovery/rotation chain. |
| `signing_key_ref` | Non-secret reference to the public signing key or key identifier. |
| `signer_role` | Must equal `capproof_cv_signer`. |
| `signature_domain` | Must equal `ILC_CAPPROOF_CV_V1`. |
| `capability_vector_payload_hash` | Hash of the canonical Capability Vector payload. |
| `signature_ref` | Signature reference or detached signature over the domain-separated payload. |

The envelope must not include seed phrases, private keys, recovery secrets,
Shamir shares, raw secret entropy, or private graph content.

## 5. Q3 Resolution: Pricing-Band Rule

Resolution: the +/-15% CapProof band is multiplicative, not additive. It applies
as a Decimal-only multiplier to the relevant pre-CapProof ECU price for an
allowlisted CapProof-covered lane. The multiplier is clamped before downstream
global price clamps and settlement rules.

Candidate constants:

| Constant | Candidate value |
|----------|-----------------|
| `CAPPROOF_PRICE_MULTIPLIER_MIN` | `Decimal("0.85")` |
| `CAPPROOF_PRICE_MULTIPLIER_BASELINE` | `Decimal("1.00")` |
| `CAPPROOF_PRICE_MULTIPLIER_MAX` | `Decimal("1.15")` |
| `CAPPROOF_PRICE_BAND_MODE` | `multiplicative_decimal_multiplier` |
| `CAPPROOF_PRICE_BAND_CLAMP_ORDER` | `compute_score_then_clamp_multiplier_then_apply_existing_price_clamps` |
| `CAPPROOF_DIRECT_ILC_REWARD_ALLOWED` | `false` |

Candidate formula:

```text
capability_multiplier = clamp(raw_capability_multiplier, Decimal("0.85"), Decimal("1.15"))
caproof_adjusted_ecu_price = pre_capproof_ecu_price * capability_multiplier
final_ecu_price = existing_downstream_price_clamps(capproof_adjusted_ecu_price)
```

All values are Decimal or exact string constants. No float value is acceptable for
CapProof pricing, ECU pricing, reward, settlement, or staking state.

The CapProof multiplier must not mint ILC, allocate direct ILC rewards, bypass
review outcomes, bypass treasury governance, or override settlement law.

## 6. Q4 Resolution: Work-Type Applicability

Resolution: CapProof does not apply automatically to all ECU-earning work.
CapProof applies only to lanes explicitly allowlisted as CapProof-covered after
the corresponding runtime and review lane can validate the measurement surface.

Candidate constants:

| Constant | Candidate value |
|----------|-----------------|
| `CAPPROOF_APPLICABILITY_MODE` | `explicit_lane_allowlist` |
| `CAPPROOF_DEFAULT_FOR_UNLISTED_LANES` | `not_applicable` |
| `CAPPROOF_SUBJECTIVE_JURY_REVIEW_APPLICABILITY` | `excluded` |
| `CAPPROOF_VALIDATOR_BFT_WEIGHT_APPLICABILITY` | `excluded_pending_separate_consensus_authority` |
| `CAPPROOF_PUBLIC_CLAIMABILITY_APPLICABILITY` | `excluded` |

Initial candidate lane table:

| Lane type | Candidate applicability | Rationale |
|-----------|-------------------------|-----------|
| Epoch-start capability check-in | applicable after runtime activation | This is the native CapProof lane. |
| Scheduling and queue placement | applicable after runtime activation | J-005 already treats CapProof as routing/scheduling signal. |
| CapProof-covered maintenance tasks | applicable after review-lane wiring | Maintenance tasks can be capability-sensitive but must pass applicable review. |
| Objective high-throughput worker tasks | candidate-applicable after lane-specific validation | Requires proof that throughput/capability affects cost without rewarding speed directly. |
| Subjective jury review | excluded | Reviewer quality must not become hardware-speed weighted. |
| Reviewer payment | excluded | Governed by CDL-091; approval-volume bias controls must remain separate. |
| Public claimability | excluded | Governed by CDL-088 and claimability gates, not CapProof. |
| Validator BFT voting weight or safety quorum | excluded pending separate consensus authority | CapProof must not alter BFT safety thresholds or voting power in CDL-092. |
| ECU-to-ILC settlement/conversion | excluded | CapProof does not change settlement law or minting. |

## 7. Candidate Prelock Constants

Phase 1404 should prelock or deliberately route the following constants:

| Constant | Candidate value |
|----------|-----------------|
| `CAPPROOF_CONTENT_ADDRESS_SCHEMA` | `capproof.content_address.v1` |
| `CAPPROOF_CONTENT_ADDRESS_SERIALIZATION` | `canonical_json_sort_keys_true_allow_nan_false_compact_separators_v1` |
| `CAPPROOF_CONTENT_ADDRESS_OUTPUT_FORMAT` | `cidv1_sha2_256_candidate` |
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

```text
cdl_092_candidate_prelock_constants_recorded_phase_1403
```

## 8. Carry-Forward To Phase 1404

Phase 1404 must decide whether `cidv1_sha2_256_candidate` should remain the
CapProof content-address output format or be replaced by an existing project-wide
ratified CID/hash profile. All other Q1-Q4 decisions above are candidate prelock
constants ready for formal prelock review.

CDL-092 remains open and unratified after Phase 1403:

```text
cdl_092_not_ratified_phase_1403
```

Graph delta:
`graph_delta=load_bearing_artifact_added:docs/specs/ilc_cdl_092_capproof_deliberation_1403_v0.1.md -> constitutional/cdl`.
