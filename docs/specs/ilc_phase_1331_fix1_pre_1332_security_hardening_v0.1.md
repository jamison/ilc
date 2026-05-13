# Phase 1331 Fix1 - Pre-1332 Security Hardening

**Date:** 2026-05-14
**Status:** Complete
**Scope:** Scoped hardening before Phase 1332. This is not Phase 1332 execution.

```text
phase_1331_fix1_pre_1332_security_hardening.v0.1
ccss_001_pre_serialization_budget_backported_phase_1331_fix1
truth_primitive_gossip_redirect_guard_added_phase_1331_fix1
bootstrap_signature_env_bypass_removed_phase_1331_fix1
identity_seed_commitment_domain_separator_applied_phase_1331_fix1
exact_numeric_non_finite_canonical_string_rejected_phase_1331_fix1
ledger_balance_read_decimal_boundary_phase_1331_fix1
agent_id_assert_removed_phase_1331_fix1
phase_1332_final_deterministic_code_security_audit_still_next_after_fix1
public_rc_remains_blocked_after_phase_1331_fix1
```

## 1. Finding Disposition

| Audit item | Disposition |
|------------|-------------|
| CCSS-001 missing pre-serialization byte budget | Fixed by back-porting the CCSS-002/003/004 byte-budget accumulator into `confidential_coordination_shard.py`. |
| CCSS-001 missing oversized-integer guard | Fixed by adding `_MAX_CANONICAL_JSON_INT_ABS` and fail-closed integer validation before decimal stringification. |
| CCSS-001 bool branch | Reclassified as not reproduced: JSON booleans are expected fields in CCSS records and CCSS-002/003/004 also preserve boolean leaves while guarding integers with `not isinstance(item, bool)`. |
| Truth primitive gossip SSRF redirect risk | Fixed by adding `_NoRedirectHandler` and using an explicit opener for outbound gossip POSTs. |
| Truth primitive gossip channel failed CDL-039 shape | Fixed by replacing the `cdl076:*` channel string with a valid opaque `cid:<hex>` channel. |
| Bootstrap signature verification env bypass | Fixed by removing `ILC_BOOTSTRAP_SKIP_SIG_VERIFY` from the production verifier path and failing closed if `oqs` import attempts raise `SystemExit`. |
| CDL-069 `identity_seed_commitment` mismatch | Fixed in runtime by applying the later ratification-evidence formula: `sha384("ilc-seed-commit-v1:" || identity_seed)`. |
| CDL-069 spec-history drift | Fixed by updating the active capsule, roadmap, and CDL-069 opening doc with the Phase 1331 Fix1 supersession state. |
| Exact numeric canonical Decimal rendering accepted non-finite values | Fixed by adding an `is_finite()` guard in `decimal_to_canonical_string`. |
| `derive_agent_id_v2` used `assert` for a runtime invariant | Fixed by replacing the assertion with `AgentIdentityError`. |
| Ledger balance read boundary returned float | Fixed by returning `Decimal` from `LedgerBackend.get_balance()` and `InMemoryLedgerBackend.get_balance()`. |

## 2. Deferred Items

The following audit findings remain out of this Fix1 scope because they need a
larger economic/protocol design pass rather than mechanical hardening:

- entropy/reward float-chain conversion and `clearing_price()` return semantics;
- proportional payout quantization and settlement verification alignment;
- exact-numeric float input acceptance at runtime boundaries;
- reputation runtime Decimal/version-token/in-place-mutation rewrite;
- broader network hardening for rate-limiter bucket eviction, chunked request
  bounds, NDJSON `read_bundle` memory profile, peer endpoint private-address
  denial, and CBOR pre-load size caps.

These remain inputs for Phase 1332.

## 3. Non-Authorization Boundary

This fix does not authorize Phase 1332 execution, public RC, public launch,
source allowlist export execution, source publication, public repository
publication, public package publication, clean public tree production, release
artifact production, release-key generation, release envelope production,
release signing material generation, signature production, release signing,
Genesis Atlas mutation/regeneration/signing, v0.2 signing, ATLAS-G-007,
ATLAS-G-008, ATLAS-G-009, ATLAS-G-010, CDL mutation, CDL-088 opening, identity
artifact creation, genesis record creation, seed commitment creation,
`identity_seed_commitment` artifact creation, dummy Agent Birth artifact
creation, identity-seed generation, mnemonic generation, private-key
generation, secret-store write, public claimability activation, public verifier
service, public claim endpoint, public P2P, public fetch serving, public ILC
listener, peer discovery, non-loopback bind, public sidecar/projection serving,
public confidential messaging, public confidential coordination serving,
wallet-facing withdrawal request, wallet-facing transfer request, wallet-facing
spend request, wallet-provider signing, wallet-provider ledger-write, wallet
write, withdrawal runtime, ECU minting, ILC settlement, value-path activation,
counsel approval, patent filing, CLA approval, trademark-policy publication, or
legal conclusion.

## 4. Verification

```bash
.venv/bin/python -m pytest \
  tests/test_phase_1331_fix1_pre_1332_security_hardening.py \
  tests/test_phase_1324_ccss_001_private_gated_shard_sidecar_contract.py \
  tests/test_phase_894_898_truth_primitive_gossip.py \
  tests/test_phase_913_920_cdl_079_hb_002_bootstrap.py \
  tests/test_phase_838e_genesis_record_schema.py \
  tests/test_exact_numeric.py \
  tests/test_ledger_backend.py \
  tests/test_sensitive_runtime_coding_taboos.py \
  tests/test_phase_1331_context_capsule_v5_55_release_candidate_freeze.py \
  tests/test_window_1330_1342_prompt_drafts.py

.venv/bin/python -m pytest \
  tests/test_settlement_stability.py \
  tests/test_ledger_persistence.py \
  tests/test_lmdb_public_runtime_store.py \
  tests/test_devnet_multi_epoch.py \
  tests/test_phase_1330_window_1330_1342_sequence_lock.py \
  tests/test_phase_1329_window_1317_1329_closure_gate.py

python3 -m py_compile \
  ilc_core/sidecars/confidential_coordination_shard.py \
  ilc_core/network/d2d/truth_primitive_gossip_runtime.py \
  ilc_core/network/d2d/bootstrap_fetch_runtime.py \
  ilc_core/ledger/exact_numeric.py \
  ilc_core/identity/agent_id_runtime.py \
  ilc_core/identity/genesis_record_schema.py \
  ilc_core/ledger/backend.py

python3 tools/check_sensitive_runtime_coding_taboos.py

git diff --check -- ilc_core tests docs/PLANNING_INDEX.md docs/phases/STATUS.md \
  docs/phases/phase_1331_fix1_pre_1332_security_hardening_walkthrough.md \
  docs/specs/ilc_phase_1331_fix1_pre_1332_security_hardening_v0.1.md \
  docs/specs/ilc_antigravity_context_capsule_v5.55.md \
  docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md \
  docs/specs/ilc_phase_1330_1342_sequence_lock_v0.1.md \
  docs/specs/ilc_window_1330_1342_candidate_phase_grouping_v0.1.md \
  docs/specs/ilc_cdl_069_pq_identity_and_epoch_endorsement_protocol_opening_838_v0.1.md
```
