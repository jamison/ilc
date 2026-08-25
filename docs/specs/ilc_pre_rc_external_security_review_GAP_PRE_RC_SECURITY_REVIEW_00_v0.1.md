# ILC Pre-RC External Security Review — GAP-PRE-RC-SECURITY-REVIEW-00 v0.1

**Date:** 2026-08-25
**External report path:** `/Users/jamison/.gemini/antigravity-ide/brain/844f5fc0-a07b-458c-9737-b584999d1933/security_audit_report.md`
**Reviewed source state:** local private repo after `b658fae89`
**Status:** COMPLETE

## Secret Boundary

Codex did not upload or transmit private keys, validator secret keys, identity
seeds, invite private nonces, mnemonic material, environment variables, private
LMDB state, VPS credentials, or `PUBLIC_RC_EXCLUDE` materials.

## HIGH Findings

| Finding | External severity | Direct-audit disposition | Fix evidence |
|---|---:|---|---|
| F1: `GetEpochChain` unbounded result allocation | HIGH | Already fixed in current tree before this follow-up. `MAX_EPOCH_CHAIN_BATCH = 128` caps returned records and existing tests cover the partial-result case. | `ilc_consensus/src/app_interface.rs`; existing `test_get_epoch_chain_caps_batch_size`. |
| F2: Bincode fixed-byte serde OOM hazard | HIGH | Already fixed in current tree before this follow-up. `deserialize_fixed_bytes` deserializes exact byte arrays through a visitor and rejects overlong inputs before constructing protocol wrappers. | `ilc_consensus/src/types.rs`; existing signature and AgentID deserialization tests. |
| F14: uncapped bincode fallback in network envelope decode | HIGH | Fixed in this follow-up. Legacy fallback now uses `bincode::DefaultOptions::new().allow_trailing_bytes().with_limit(MAX_GOSSIP_PAYLOAD_BYTES as u64)`. | `ilc_consensus/src/network.rs`; `network::tests::test_legacy_bincode_fallback_decodes_under_size_limit`. |

## MEDIUM Findings

| Finding | External severity | Disposition |
|---|---:|---|
| F3: CPython `Decimal.ln/exp` cross-version determinism risk | MEDIUM | Accepted as a verification carry-forward. Existing code uses `Decimal` and explicit precision; a future fleet-version determinism certificate should pin interpreter versions before live validator activation. |
| F4: float math in `genesis_accrual_governor.py` | MEDIUM | Not patched here. This is analysis/governor code, not an epoch-commit state-root writer in the current public-RC path. Keep on post-RC numeric migration backlog unless a launch runner imports it into settlement. |
| F5: finality/diversity float conversions | MEDIUM | Stale in current tree for the audited call path: `compute_max_cluster_share` accepts `Decimal`, and `evaluate_epoch_finality_with_diversity` passes `Decimal` weights directly. |
| F6: quorum ratio division | MEDIUM | Already fixed in current tree for the quorum decision: `participating_voters * 2 >= total_members` and exact integer vote-threshold multiplication are used. |
| F9: Rust fast-path epoch-set cold-start gap | MEDIUM | Deferred to validator runner/cold-start phase. It is not introduced by 0.4.2 packaging, but must be resolved before live validator set rotation/recovery activation. |
| F15: Popperian gate float comparison | MEDIUM | Fixed in this follow-up. Float inputs are rejected and threshold comparison uses `Decimal`. |
| F16: Rust validator secret key not zeroized after read | MEDIUM | Fixed in this follow-up. `sk_hex` and decoded `sk_bytes` are zeroized immediately after `SecretKey::from_bytes`. |
| F20: epoch recovery uses current validator set | MEDIUM | Deferred to live recovery/runner phase. It is not in the 0.4.2 install/onboarding package-critical path, but must be fixed before validator-set rotation recovery is public-live. |

## LOW Findings

| Finding | External severity | Disposition |
|---|---:|---|
| F8: outbound QUIC pool leak potential | LOW | Deferred to QUIC long-running validator service hardening. |
| F10: relay helper modulo-by-zero | LOW | Fixed in this follow-up; helper returns `0` for empty slices and has a regression test. |
| F11: P2P bridge routing hardcoded false | LOW | Accepted intentional default-off guard; bridge is not activated. |
| F12: Shamir recovery odd-hex panic | LOW | Fixed in this follow-up; odd and non-hex shares are rejected before slicing. |
| F13: Shamir split `.expect` operator-input panics | LOW | Fixed in this follow-up for interactive/error-prone paths. |
| F17: server body-size middleware lacks streaming cap | LOW | Deferred; route-level checks provide current defense-in-depth. |
| F18: Python LMDB environment cache lacks global eviction | LOW | Deferred; not package-build blocking. |
| F19: settlement residual can go negative | LOW | Existing code raises on negative residual in the currently audited proportional payout helper. |
| F21: runtime temp dir under `/tmp` | LOW | Accepted for current dev/runtime smoke; production data-dir selection belongs to VPS runner/provisioning. |
| F22: payout division without explicit precision | LOW | Fixed in this follow-up with `localcontext(prec=50)`. |
| F23: entropy cap unbounded | LOW | Fixed in this follow-up with `max_cap <= 10`. |
| F24: genesis authority key invalid hex raises bare error | LOW | Fixed in this follow-up with `GenesisAssertionError` token `genesis_authority_key_public_key_hex_invalid`. |

## Verification

```text
$ ./.venv/bin/python -m pytest tests/test_cdl_v7_popperian_gate_runtime_398.py tests/test_entropy_reward.py tests/test_phase_1557_hb001_genesis_authority_assertion.py tests/test_phase_1107_h_con_02_panel_quorum_settle.py -q
..............................................................           [100%]
62 passed in 8.34s

$ ~/.cargo/bin/cargo fmt --check

$ ~/.cargo/bin/cargo check
warning: constant `MAX_TESTNET_RELAY_HOPS` is never used
warning: function `next_relay_hop` is never used
Finished `dev` profile [unoptimized + debuginfo] target(s) in 9.44s

$ ~/.cargo/bin/cargo test --lib relay_routing_table::tests::deterministic_pick_index_handles_empty_candidates_without_panic -- --nocapture
running 1 test
test relay_routing_table::tests::deterministic_pick_index_handles_empty_candidates_without_panic ... ok
test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 149 filtered out

$ ~/.cargo/bin/cargo test --lib network::tests::test_legacy_bincode_fallback_decodes_under_size_limit -- --nocapture
running 1 test
test network::tests::test_legacy_bincode_fallback_decodes_under_size_limit ... ok
test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 149 filtered out

$ git diff --check
```

## Gate Disposition

Human disposition was supplied on 2026-08-26:

- F1 ACCEPTED: pre-existing `MAX_EPOCH_CHAIN_BATCH = 128` cap verified.
- F2 ACCEPTED: pre-existing `deserialize_fixed_bytes` visitor pattern verified.
- F14 ACCEPTED: follow-up `.with_limit(MAX_GOSSIP_PAYLOAD_BYTES as u64)` fix verified.

The phase is authorized to emit:

```text
pre_rc_external_security_review_complete_GAP_PRE_RC_SECURITY_REVIEW_00
```
