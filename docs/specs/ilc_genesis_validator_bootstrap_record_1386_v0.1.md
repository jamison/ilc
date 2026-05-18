# ILC Genesis Validator Bootstrap Record 1386 v0.1

**Phase:** 1386
**Date:** 2026-05-18
**Status:** complete
**Posture:** Genesis-controlled single-custodian pre-RC/testnet exception

## Tokens

```text
genesis_validator_bootstrap_record_committed_phase_1386
genesis_controlled_single_custodian_bootstrap_exception_phase_1386
single_operator_compromise_resistance_not_confirmed_phase_1386
production_split_custody_ceremony_required_before_mainnet_launch
```

## 1. Summary

Phase 1386 records the current genesis validator bootstrap posture honestly:
Genesis accepts a single-custodian pre-RC/testnet exception for this window.

This is not a completed multi-operator split-custody ceremony. It does not
confirm single-operator-compromise resistance. It does not authorize production
mainnet launch, production value-path activation, public RC graph permanence,
or production genesis-signed artifacts.

The production split-custody ceremony remains required before any production
mainnet launch with live value or production genesis-signed authority.

## 2. Human Authorization

The human Genesis authority gave explicit `GO Phase 1386` and then accepted the
Genesis-controlled exception path for Phase 1386 after review of the custody
tradeoff. The accepted result is:

| Field | Result |
|-------|--------|
| Current custody posture | Genesis-controlled single custodian |
| Environment scope | Pre-RC/testnet only |
| Split custody claim | Not claimed |
| Single-operator-compromise resistance | Not confirmed |
| Public RC gate status | Not a current Window 1369-1390 public-RC gate |
| Production carry-forward | Split-custody ceremony required before mainnet launch |

## 3. Claim Verification Table

| Claim | File/symbol checked | Result |
|-------|---------------------|--------|
| M-022 open item #7 says the multi-operator key ceremony was not executed | `docs/research/ilc_mysticeti_gemini_lane_handoff_M022_v0.1.md` lines 245-246 | confirmed |
| Existing BLS validator keygen tooling exists | `ilc_consensus/src/keygen_main.rs` | confirmed |
| Existing PQ identity keygen tooling can write public-only records but is not this validator ceremony | `ilc_consensus/src/pq_keygen_main.rs` | confirmed |
| Shamir tooling exists for recovery-oriented secret splitting, not a completed validator split-custody ceremony | `ilc_consensus/src/shamir_split_main.rs`; `ilc_consensus/src/shamir_recover_main.rs` | confirmed |
| Phase 1387 gates on Phase 1386a/1386b/1386c connectivity/hardening tokens, not Phase 1386 genesis custody tokens | `docs/antigravity_tasks/antigravity_prompt__phase_1387_g8_pre_activation_hardening_gate.md` | confirmed |
| CDL-090 governs identity-bootstrap secret-output discipline but does not execute agent seed generation in Phase 1386 | `docs/specs/ilc_cdl_090_ratification_evidence_1373_v0.1.md` | confirmed |

## 4. Validator Key Handling Rule

Private validator keys must not be committed to repository documents, STATUS
entries, walkthroughs, prompts, chat transcripts, terminal scrollback, logs, or
public artifacts.

For pre-RC validator machines, the safe default is:

1. Generate each validator key locally on the target machine or approved secure
   custody environment.
2. Keep the secret validator key off-repo and in that custody environment.
3. Record only public validator key material and non-secret custody receipts when
   a later phase explicitly authorizes such a record.
4. Do not copy a Genesis-held private validator key to additional machines as a
   substitute for local key generation.

Phase 1386 does not itself generate, distribute, copy, escrow, or publish any
validator private key material.

## 5. Agent Identity Scope

Non-human operator identity bootstrap and seed/mnemonic custody remain governed
by the CDL-090 identity-bootstrap contract and its secure-output target classes.
Phase 1386 does not generate identity seeds, write a secret store, create agent
birth attestations, or authorize OpenClaw/OpenClaw-harness public identity
activation.

If future agent identities are initialized for testnet work, the public/non-secret
records must follow CDL-090's no-secret-output discipline and distinguish testnet
or devnet identities from public authority.

## 6. Downstream Routing

Phase 1386 does not add a new hard gate to Phase 1387, Phase 1388, or Phase 1389.
This custody exception is not a current Window 1369-1390 public-RC gate. Those
prompts were checked for Phase 1386 genesis-custody tokens and do not currently
require them.

The production split-custody carry-forward is not inserted as a new hard gate for
Phase 1387, Phase 1388, or Phase 1389.

The carry-forward obligation is production-scoped:

```text
production_split_custody_ceremony_required_before_mainnet_launch
```

That obligation must be picked up by a future production mainnet launch planning
phase before any live-value mainnet launch claim or production genesis-signed
artifact claim.

## 7. Non-Authorizations

Phase 1386 does not authorize:

- CDL mutation;
- runtime changes to `ilc_core/` or `ilc_consensus/`;
- graph writes;
- public RC graph permanence;
- public repository push or package publication;
- production genesis-signed artifacts;
- production validator deployment;
- live ECU/ILC value-path activation;
- public claimability activation;
- sender-privacy claims;
- single-operator-compromise resistance claims;
- multi-operator split-custody claims;
- identity seed, mnemonic, or recovery-share generation.

## 8. Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_genesis_validator_bootstrap_record_1386_v0.1.md -> genesis-validator/bootstrap-exception
```
