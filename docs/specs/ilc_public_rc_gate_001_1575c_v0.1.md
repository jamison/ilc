# ILC Public RC Gate-001 Phase 1575c

**Version:** v0.1
**Date:** 2026-07-14
**Phase:** 1575c
**Window:** 1565-1575
**Status:** passed
**Sensitivity:** SENSITIVE gate record. Public mirror push authorized, not executed by Codex.

## 1. Authorization Record

Human authorization received:

```text
GO PUBLIC-RC-GATE-001
```

This authorization opened the Phase 1575c public RC closure gate. The gate consumed the verified Genesis v0.5 public-RC signing envelope from Phase 1575c-Fix1c and the Phase 1575b economic activation certificate.

## 2. Token Census

The following required precondition tokens were confirmed before gate artifact production:

| Token | Result |
|---|---|
| `public_rc_economic_intent_reconciled_phase_1574_fix1` | present |
| `economic_soft_rc_rehearsal_1575a_disposition=freeze_retain_candidate` | present |
| `phase_1575a_evidence_accepted_for_1575b_consumption` | present |
| `economic_activation_certificate_complete_phase_1575b` | present |
| `cdl057_witness_lane_rehearsal_passed_phase_1575b_fix8` | present |
| `epoch_0_to_1_private_rehearsal_passed_phase_1575b_fix9` | present |
| `public_bootstrap_serving_readiness_audited_phase_1575b_fix1` | present |
| `public_rc_atlas_slice_readiness_gate_committed_phase_1575b_fix3` | present |
| `starmap_installer_sidecar_recipe_defined_phase_1575b_fix4` | present |
| `public_rc_slice_installability_rehearsed_phase_1575b_fix4` | present |
| `atlas_lmdb_cleanliness_pre_1575c_confirmed_phase_1575b_fix2f` | present |
| `public_rc_activation_matrix_committed_phase_1574` | present |
| `source_allowlist_export_rehearsal_passed_phase_1574` | present |
| `phase_1575_signing_pending` | present |
| `genesis_v05_public_rc_envelope_signed_phase_1575c_fix1` | present |
| `genesis_v05_public_rc_envelope_signature_verified_phase_1575c_fix1` | present |
| `atlas_slice_manifest_v05_signed_phase_1575c_fix1` | present |
| `genesis_v04_signing_superseded_by_v05_public_rc_envelope_phase_1575c_fix1` | present |
| `phase_1575c_v05_signing_tokens_accepted_by_gate_phase_1575c_fix1` | present |

Phase 1575c emits:

| Token | Result |
|---|---|
| `genesis_v05_public_rc_envelope_consumed_phase_1575c` | emitted |
| `public_rc_gate_001_authorized` | emitted |
| `window_1565_closed_phase_1575c` | emitted |
| `window_1565_closure_gate_verdict=pass` | emitted |
| `public_rc_live_phase_1575c` | emitted |
| `public_repository_push_authorized_phase_1575c` | emitted |
| `post_rc_v05_behavioral_graph_carry_forward_locked_phase_1575c` | emitted |
| `sanitized_public_mirror_regenerated_phase_1575c` | emitted |

## 3. Activation Matrix Enforcement Summary

The Phase 1574 activation matrix, as amended by the Phase 1575b Economic Activation Certificate, marks rows 5-9 and 20-21 as `public_rc_live` policy rows. Phase 1575c does not clear runtime guard constants. It verifies that the public release state is consistent with the matrix while preserving explicit activation boundaries.

The six economic activation guards were imported and confirmed `True`:

| Guard | Value |
|---|---|
| `CONVERSION_CANDIDATE_RUNTIME_NOT_ACTIVATED` | `True` |
| `EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED` | `True` |
| `PRODUCTION_EMISSION_NOT_ACTIVATED` | `True` |
| `PRODUCTIVE_ECU_EXPANSION_NOT_ACTIVATED` | `True` |
| `TREASURY_DISTRIBUTION_NOT_ACTIVATED` | `True` |
| `VALIDATOR_ADMISSION_NOT_ACTIVATED` | `True` |

Economic rows certified `public_rc_live` by Phase 1575b authorize public-RC posture and evidence acceptance. They do not by themselves mint ECU, settle ILC, write production wallets, or transition epochs.

## 4. Final Source Export Check Result

Final source allowlist export evidence:

| Field | Value |
|---|---|
| Artifact | `out/block6_public_rc_gate_001_1575c/final_source_export_1575c.json` |
| SHA-256 | `36de6e823b2f87c52f238a908f7737fb35ccd74f3553e0a2b58778d558d2f2df` |
| Result | `pass` |
| Included files | `435` |
| Excluded files | `39` |
| Blocked ambiguities | `0` |
| Marker scan | `pass` |
| Dependency scan | `pass` |
| Included/excluded intersection | `0` |

The raw `PUBLIC_RC_EXCLUDE` reference count across `ilc_core/`, `tests/`, `docs/`, and `tools/` was `3436`; this includes prompts, tests, and documentation that mention the marker. The authoritative export checks are the marker scan, dependency scan, blocked ambiguity count, and included/excluded intersection above.

## 5. Closure Gate Selftest Chain

The Phase 1564 prior-window closure selftest is protected by `ILC_PHASE_1564_GATE_SELFTEST`. Phase 1575c tests include a category-3 selftest-chain assertion that confirms this selftest guard remains present in `tests/test_phase_1564_window_1556_1564_closure_gate.py`.

## 6. Production Genesis Signing Disposition

Phase 1575c consumed the verified Genesis v0.5 public-RC signing envelope. This supersedes the earlier missing v0.4 production-signing-token expectation for this gate.

Phase 1575c-Fix2 later corrected the scope of this statement: the Fix1 artifact
is a signed public-RC envelope, not the immutable Atlas graph package itself.
The graph-package materialization and signing payload were produced separately
in Phase 1575c-Fix2.

Signing profile: `ML-DSA-65`.

| Artifact | SHA-256 |
|---|---|
| `out/genesis_public_rc_signing_envelope_v0.5.json` | `4fcf4dc632398c2f1bf6e0533565ea6dcfb33892ae3a7d76d27118c46ff857e8` |
| `out/genesis_public_rc_signing_envelope_v0.5.signature_payload.bin` | `57a6b9640686df7f21dcb39d8f102c19d8c75e553ce182e1529ac01060b4db01` |
| `out/genesis_public_rc_signing_envelope_v0.5.signature.hex` | `1d37d58ea63d10dfe2bbe477f75ca3298860c7381c3a8878fc774fa29f6083b6` |
| `out/genesis_public_rc_signing_envelope_v0.5.signature.json` | `0eac25ac813b8163b6e733627f773bf2c2b79213d34f171cf69384db4315dde5` |
| `out/genesis_public_rc_signing_envelope_v0.5.verification.json` | `762d4d95b2410710557b9089fc3c3c8e861ee281cb32195208546ed4bd569fd1` |

Verification command:

```bash
ilc_consensus/target/debug/pq_sign verify \
  --input-file out/genesis_public_rc_signing_envelope_v0.5.signature_payload.bin \
  --signature-hex "$(tr -d '\n' < out/genesis_public_rc_signing_envelope_v0.5.signature.hex)"
```

Verification output:

```text
signature_verified
```

The verification record asserts `verification_result = "signature_verified"` and `signature_payload_sha256 = "57a6b9640686df7f21dcb39d8f102c19d8c75e553ce182e1529ac01060b4db01"`.

## 7. Public Repository Push Authorization

Phase 1575c authorizes publication of the sanitized public mirror. Codex did not push to GitHub and did not change repository visibility.

Sanitized mirror evidence:

| Field | Value |
|---|---|
| Local staging directory | `/tmp/ilc-public-mirror-1575c` |
| Manifest | `out/block6_public_rc_gate_001_1575c/public_mirror_manifest_1575c.json` |
| Manifest SHA-256 | `d1dca9239d37823a588bad5e65c64a3b9ecab22f9824074355440c7ca9b4ca98` |
| Pipeline version | `generate_public_mirror_1573n.v0.2` |
| Source private commit | `8af0d4f0bb203074dd43466cfc1cdeb6fdceb4e4` |
| Filtered public HEAD SHA | `0730d639eee684737ff087e7ef8e7b9046495461` |
| Filtered archive SHA-256 | `4df9c0bc1db05872fc96e3fc3e4616b6618ffaa18cedfc9c01bb1d00366740dd` |
| Commit count before | `4318` |
| Commit count after | `2960` |
| Minimum required commit count | `2590` |
| Excluded path count | `7389` |
| Denylist scan | `pass` |
| PUBLIC_RC_EXCLUDE scan | `pass` |
| Staging repo status | clean |
| Network push performed by Codex | no |

The mirror pipeline was hardened during this gate from `generate_public_mirror_1573n.v0.1` to `generate_public_mirror_1573n.v0.2`. The v0.2 pipeline commits post-filter `ilc_consensus/Cargo.toml` cleanup before calculating the filtered public HEAD and archive hash, so the recorded HEAD is exactly the clean publishable tree.

Authorized human-operator publication commands:

```bash
cd /tmp/ilc-public-mirror-1575c
git remote add public git@github.com:ILC-Foundation/ilc.git
git push public HEAD:main
git tag public-rc-0.1
git push public public-rc-0.1
```

If the public repository is owned under a different GitHub account or organization, the remote URL must be explicitly rebound by the human operator before push. This gate authorizes publication of the sanitized mirror identified above, not any raw private repository push.

## 8. OpenClaw and ClawHub Disposition

OpenClaw/ClawHub publication remains pending. Phase 1575c does not publish the OpenClaw skill to ClawHub and does not claim ClawHub marketplace availability. The current disposition remains `openclaw_clawhub_not_published_pending_phase_1575`.

The OpenClaw skill and sidecar work completed before the gate remains useful onboarding infrastructure, but marketplace publication is a separate post-gate operator action.

## 9. Non-Claims

Phase 1575c does not claim any of the following:

- No raw private repository push was performed.
- No GitHub repository visibility change was performed by Codex.
- No runtime guard was cleared.
- No ECU was minted by Codex.
- No ILC was publicly settled by Codex.
- No production wallet write was performed by Codex.
- No epoch 0 to 1 transition was executed by Codex.
- No OpenClaw/ClawHub marketplace publication was performed.
- No formal differential privacy or formal anonymity proof is claimed.
- No full post-RC behavioral Genesis v0.5 ceremony is claimed.

## 10. Post-RC v0.5 Behavioral Graph Carry-Forward

The following workstreams from `docs/specs/ilc_post_rc_architectural_targets_v0.1.md` are locked as post-RC carry-forward items. Each row has status `post_rc_carry_forward`.

| Workstream | First likely window | Required before v0.5 ceremony | Status |
|---|---|---|---|
| Behavioral surface audit | 1576+ | Yes | post_rc_carry_forward |
| Behavioral spec node schema | 1576+ | Yes | post_rc_carry_forward |
| Economic behavior spec | Early, first post-RC window | Yes, highest risk | post_rc_carry_forward |
| Distributed CDL-048 mandatory conversion instrument | First post-RC economic window, or Block 6 defect slot if Fix2d requires live settlement semantics | Before any public value-path activation or claim that CDL-048 conversion is production-live | post_rc_carry_forward |
| Inverted ECU / spend-to-keep doctrine | Early, first post-RC economic window | Before any public claim that spend-to-keep is a live settlement rule | post_rc_carry_forward |
| Werner pressure diagnostics to policy review | After economic behavior spec | Before any settlement use of Werner pressure metrics | post_rc_carry_forward |
| Inverse ECU / backward attribution research lane | After behavioral/economic spec baseline | Before any backward-attribution payout rule | post_rc_carry_forward |
| Language-neutral test vectors | After spec node schema | Yes | post_rc_carry_forward |
| Conformance receipts | After test vectors | Yes | post_rc_carry_forward |
| Protocol-native content layer | Parallel to spec work | Yes, required for self-sufficient distributed operation | post_rc_carry_forward |
| Sidecar typed-subgraph schema | 1576+ | Yes, required before broad third-party sidecar registration | post_rc_carry_forward |
| Contributor sidecar registry and SDK | After sidecar schema | Before public marketplace/installability claim | post_rc_carry_forward |
| Graph-native recall/query sidecar | After sidecar schema; parallel to content layer | Before any public agent-native graph recall/query sidecar or third-party recall marketplace claim | post_rc_carry_forward |
| Inference substrate custody and representational independence | After Fix2h/Fix2i routing; candidate Fix2j/CDL lane | Before any public claim that jury assignment resists runtime-memory-substrate manipulation | post_rc_carry_forward |
| Harness sidecar model-router and endorsement runtime | After Block 6 or first post-RC sidecar window, depending on sequence lock | Before any public claim of live harness sidecar submission, model-router endorsement, or sovereign-cluster attestation | post_rc_carry_forward |
| Hyperedge type definition nodes (CDL-099) | First post-RC window (1576+) | Before ADR-0035 type registry activation | post_rc_carry_forward |
| Jury procedure for type disputes (CDL-100) | After CDL-099 | Before ADR-0035 type registry activation | post_rc_carry_forward |
| ADR-0035 type registry runtime activation | After CDL-099 + CDL-100 | Post-CDL-099/100, with explicit GO | post_rc_carry_forward |
| Hypergraph sidecar projection semantics | After sidecar schema and CDL-099 | Before sidecar-specific hyperedge activation | post_rc_carry_forward |
| Continuity proof tooling | Before v0.5 ceremony | Yes | post_rc_carry_forward |
| Spec-vs-implementation governance | Before non-Python implementation ships | Yes | post_rc_carry_forward |

Token emitted: `post_rc_v05_behavioral_graph_carry_forward_locked_phase_1575c`.

## 11. Phase 1575c-Fix2 Atlas Graph Package Correction

Phase 1575c-Fix2 is a corrective strike-force phase for the Genesis v0.5 Atlas
graph package. It does not reopen the Phase 1575c public-RC gate verdict and
does not authorize any additional public push by itself.

Corrective facts:

| Field | Value |
|---|---|
| Scope correction | Fix1 signed the public-RC envelope, not the Atlas graph package |
| LMDB source | `out/genesis_base_graph_v0.4_unified.lmdb` |
| Fix38 bad hub edges before repair | `2,611` invalid `SOURCE_TREE_MEMBER` edges |
| Fix38 bad hub edges after repair | `0` |
| Public graph package projection | `genesis_core_star_map` + `public_protocol_graph` |
| Package nodes | `1,035` |
| Package edges | `3,841` |
| Projection digest | `65402e75945a86ccc14bd83610e5f721ea17ed14f6dd5e4d4547647a8853c900` |
| Package file SHA-256 | `b85674e741611c1e2201f52e6dd6162b032a94d62bee8cb68d540a045b9569bd` |
| Signature payload SHA-256 | `6cdd1d4f055c81a7dc7fcd787016fc56dca378eecc4169822f8dfee593000aa8` |
| Current graph-package disposition | `blocked_with_named_defect:genesis_v05_atlas_graph_package_operator_signature_not_provided_phase_1575c_fix2` |

The package intentionally excludes `support_candidate_graph`, private/excluded
material, local overlays, and future local-user slice-inventory state. Those
records may exist in a user's operational LMDB, but they are not part of the
immutable public-RC Genesis v0.5 baseline graph package.
