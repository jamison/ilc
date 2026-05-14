# ILC Public Claimability API Activation Or Carry-Forward Gate 1336 v0.1

**Date:** 2026-05-14
**Phase:** 1336
**Status:** no-claim carry-forward; no public claimability/API activation

```text
public_claimability_api_activation_or_carry_forward_gate_phase_1336.v0.1
public_claimability_requires_explicit_authority_phase_1336
claimability_replay_nullifier_policy_checked_phase_1336
wallet_value_actions_still_separate_gate_phase_1336
phase_1337_public_path_sidecar_activation_or_exclusion_gate_next
public_rc_remains_blocked_after_phase_1336
```

## 1. Verdict

Phase 1336 executed after the explicit gate authorization:

```text
GO Phase 1336
```

That authorization was sufficient to execute the activation-or-carry-forward
gate. It was not explicit authority to activate a public claimability API,
public verifier service, public claim endpoint, non-loopback listener, wallet
action, ECU minting path, ILC settlement path, public serving path, publication
path, release signing path, v0.2 signing path, CDL mutation, CDL-088 opening,
or identity bootstrap.

The gate result is:

```text
result=no_claim_carry_forward
public_claimability_api_activation_or_carry_forward_gate_verdict=no_claim_carry_forward
```

No runtime code was changed and no public endpoint was activated.

## 2. Claim Table

| Claim | File or symbol checked | Result |
|-------|------------------------|--------|
| Phase 1336 prompt validates and is executable. | `docs/antigravity_tasks/antigravity_prompt__phase_1336_g8_public_claimability_api_activation_or_carry_forward_gate.md`; `tools/validate_phase_prompt.py` | confirmed |
| Public claimability activation requires explicit authority. | `docs/specs/ilc_public_claimability_authority_decision_preflight_1283_v0.1.md`; Phase 1336 prompt | confirmed |
| The Phase 1305 verifier is local-only and not a public API. | `docs/specs/ilc_offline_claimability_receipt_verifier_sidecar_1305_v0.1.md`; `ilc_core/sidecars/claimability_receipt_verifier.py` | confirmed |
| Replay/nullifier and duplicate-claim policy remain gated. | `docs/specs/ilc_proof_binding_canonical_hash_negative_path_tests_1306_v0.1.md`; `docs/specs/ilc_offline_claimability_receipt_verifier_sidecar_1305_v0.1.md` | confirmed |
| CDL-088 is not opened or ratified. | `docs/specs/ilc_constitutional_decision_log_v0.1.md` | confirmed |
| Legacy `/v1/public/*` FastAPI routes remain a public-RC cleanup blocker. | `docs/specs/ilc_deep_no_activation_assertion_audit_1301_v0.1.md`; `ilc_core/server.py` | confirmed |
| Phase 1335 generated release key/envelope metadata but did not authorize public claimability. | `docs/specs/ilc_release_keys_envelopes_generation_gate_1335_v0.1.json` | confirmed |
| Window 1343+ routing exists for public claimability and identity-bootstrap blockers. | `docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.1.md` | confirmed |

MemPalace was queried as advisory retrieval. It returned no current planning or
evidence result that superseded direct repo reads.

## 3. Blocking Preconditions

| Blocker | Status | Carry-forward route |
|---------|--------|---------------------|
| Explicit public-claimability activation authority missing | open | Phase 1355 activation retry gate after predecessors close |
| Replay/nullifier policy not activated | open | Phase 1352 |
| Duplicate-claim registry not activated | open | Phase 1352 |
| CDL-088 not opened or ratified | open | Phases 1349-1351 |
| Genesis-rooted agent birth attestation unspecified | open | Phase 1345 |
| Identity-bootstrap ADR/CDL not ratified | open | Phases 1346-1348 |
| Legacy `/v1/public/*` FastAPI routes not cleaned | open | Phase 1353 |
| Counsel clearance for public verifier API surface missing | open | Phase 1354 |

The replay/nullifier and duplicate-claim policy check is recorded by:

```text
claimability_replay_nullifier_policy_checked_phase_1336
```

## 4. Endpoint/Public-Path Table

| Surface | Status | Route added | Non-loopback bind created |
|---------|--------|-------------|---------------------------|
| Public claimability API | not activated | false | false |
| Public verifier service | not activated | false | false |
| Public claim endpoint | not activated | false | false |

The local verifier substrate remains local-only:

```text
offline_claimability_receipt_verifier_sidecar_phase_1305.v0.1
claimability_verifier_local_only_no_api_phase_1305
receipt_verifier_public_serving_not_enabled_phase_1305
```

## 5. Wallet And Value-Path Boundary

Wallet and value actions remain separately gated:

```text
wallet_value_actions_still_separate_gate_phase_1336
```

Phase 1336 does not authorize wallet withdrawal, wallet transfer, wallet spend,
wallet signing, wallet ledger-write, ECU minting, ILC settlement, withdrawal
runtime, value-path activation, or any public payment path.

## 6. Phase 1335 Dependency

Phase 1336 directly consumed the Phase 1335 release key/envelope metadata:

| Item | Value |
|------|-------|
| Phase 1335 result | `keys_envelopes_generated` |
| Public key fingerprint | `sha256:4f2ca127b54872cff4010cfce3d0fbef617ca92cc97d8ef09be13bdfe3dea056` |
| Unsigned envelope hash | `sha256:4b26d11a5ee9008d41ad8449907b359f241f8d8a7863940694aef639222ed135` |
| Public RC blocked after Phase 1335 | true |

Phase 1335 did not authorize public claimability activation, public verifier
serving, release signing, public RC publication/claim, or CDL-088 opening.

## 7. Non-Claims

Phase 1336 does not authorize or perform:

- public claimability API activation
- public verifier service activation
- public claim endpoint activation
- public P2P/fetch/sidecar serving
- public confidential coordination serving
- wallet-facing withdrawal, transfer, or spend requests
- wallet signing or wallet ledger-write
- ECU minting or ILC settlement
- source publication, public repository publication, or public package publication
- release signing or release signature production
- public RC publication or public RC claim
- Genesis/Atlas mutation, regeneration, or signing
- v0.2 signing
- identity bootstrap, identity artifact creation, seed commitment creation, mnemonic generation, private-key generation, or secret-store write
- CDL mutation or CDL-088 opening
- counsel approval, patent filing, trademark-policy publication, or legal conclusion

Public RC remains blocked:

```text
public_rc_remains_blocked_after_phase_1336
```

## 8. Next Phase

The next planned phase is:

```text
phase_1337_public_path_sidecar_activation_or_exclusion_gate_next
```

Phase 1337 remains sensitive and requires explicit future `GO Phase 1337`.

## 9. Graph Delta

```text
graph_delta=support_only:docs/specs/ilc_public_claimability_api_activation_or_carry_forward_gate_1336_v0.1.json,docs/specs/ilc_public_claimability_api_activation_or_carry_forward_gate_1336_v0.1.md -> planning/frontier
```
