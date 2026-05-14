# Phase 1332 - Final Deterministic Code/Security Audit

**Date:** 2026-05-14
**Status:** Complete - audit pass with blockers
**Authority:** Executed after explicit `GO Phase 1332`

```text
final_deterministic_code_security_audit_phase_1332.v0.1
runtime_guardrail_scope_revalidated_phase_1332
canonical_json_security_sweep_recorded_phase_1332
release_blocker_audit_no_activation_phase_1332
phase_1333_source_allowlist_export_execution_gate_next
public_rc_remains_blocked_after_phase_1332
```

## 1. Verdict

Phase 1332 completed the final deterministic code/security audit and confirmed
that Phase 1331 Fix1/Fix2/Fix3 closed the scoped high-risk findings they claimed
to close.

Phase 1333 is the next numeric gate, but it must not execute until Fix4 closes
the remaining pre-1333 blockers below:

```text
phase_1333_status=blocked_pending_fix4_before_phase_1333
fix4_private_address_denial_cbor_size_cap_required_before_phase_1333
code_health_refactor_candidates_recorded_window_1330_1342
reputation_py_rewrite_deferred_window_1343_plus
```

No source export, clean public tree, release artifact, release key, release
envelope, signing material, signature, public serving, public RC claim, identity
artifact, wallet/ECU/ILC activation, Genesis/Atlas mutation, or CDL mutation was
authorized or performed by this audit.

## 2. Claim Verification

| Claim | File/symbol checked | Result |
|-------|---------------------|--------|
| Phase 1332 prompt is executable under the active schema. | `docs/antigravity_tasks/antigravity_prompt__phase_1332_g8_final_deterministic_code_security_audit.md`; `tools/validate_phase_prompt.py` | Confirmed. Validator passed. |
| Phase 1331 is closed and Phase 1332 was the next planned sensitive phase. | `docs/phases/STATUS.md`; `docs/PLANNING_INDEX.md` | Confirmed. Phase 1331/Fix1/Fix2/Fix3 entries exist and Phase 1332 was still next. |
| Public RC/source export/release/signing remains blocked. | `docs/specs/ilc_antigravity_context_capsule_v5.55.md`; `docs/specs/ilc_phase_1330_1342_sequence_lock_v0.1.md`; Phase 1332 prompt | Confirmed. No source grants publication, release, signing, public serving, or public RC authority. |
| Phase 1333 is a source allowlist export execution gate, not publication authority. | `docs/antigravity_tasks/antigravity_prompt__phase_1333_g8_source_allowlist_export_execution_gate.md` | Confirmed. Phase 1333 itself also requires explicit future `GO Phase 1333`. |
| Fix1/Fix2/Fix3 closed their claimed runtime/security items. | Direct reads in `ilc_core/` and focused tests/checkers | Confirmed for the scoped items listed in Section 3. |
| Remaining private-address endpoint denial and CBOR size-cap findings are still open. | `ilc_core/network/d2d/gossip_peer_registry.py:52`; `ilc_core/crypto/cbor_canonical.py:35` | Confirmed open. |
| Remaining code-health findings still fail after the sim-harness exclusion. | `tests/test_code_health.py` with `CODE_HEALTH_TOP_N=20` | Confirmed open: two tests fail, two pass. |

## 3. Closed Finding Verification

| Prior item | Direct source evidence | Phase 1332 disposition |
|------------|------------------------|------------------------|
| C1 CCSS-001 missing pre-serialization byte budget and integer guard | `ilc_core/sidecars/confidential_coordination_shard.py:47`, `:1165`, `:1203`, `:1231` | Closed by Fix1. |
| C2 CCSS-001 bool primitives pass tree validation | `ilc_core/sidecars/confidential_coordination_shard.py:1226`; required boolean invariants in CCSS records | Reclassified as not a bug. JSON booleans are valid CCSS record values; numeric validators reject bool where an integer is expected. |
| C3/H1/M1 economics entropy/reward/exact numeric float chain | `ilc_core/economics/entropy.py:21`, `:42`, `:55`; `ilc_core/economics/reward.py:65`; `ilc_core/ledger/exact_numeric.py:7`, `:18`, `:30` | Closed by Fix2. Float input is rejected at the boundary and non-finite Decimal is rejected. |
| C4 epoch clearing price float cast | `ilc_core/economics/epoch_ledger.py:47`, `:50`, `:63` | Closed by Fix2. Return type is Decimal. |
| C5 truth primitive gossip redirect SSRF | `ilc_core/network/d2d/truth_primitive_gossip_runtime.py:58`, `:142` | Closed by Fix1. Redirect-denying opener installed. |
| C6 bootstrap signature env-var bypass | `ilc_core/network/d2d/bootstrap_fetch_runtime.py` | Closed by Fix1. `ILC_BOOTSTRAP_SKIP_SIG_VERIFY` no longer appears in the runtime path. |
| C7 CDL-069 identity seed commitment mismatch | `ilc_core/identity/genesis_record_schema.py:70` | Closed by Fix1. Runtime now uses the domain-separated CDL-069 commitment formula. |
| H2/H3/M21 proportional payout rounding gaps | `ilc_core/economics/epoch_attribution_settle_runtime.py:48`, `:53`, `:67`, `:316` | Closed by Fix2. Uses quantum `ROUND_DOWN` with deterministic residual assignment. |
| H4 settlement verification arithmetic mismatch | `ilc_core/ledger/settlement_verification.py:22`, `:35`, `:151` | Closed by Fix2. Verification is quantum-aligned. |
| H5 ledger balance float boundary | `ilc_core/ledger/backend.py:85`, `:306` | Closed by Fix1. Balance reads return Decimal. |
| H6 fetch rate limiter bucket growth | `ilc_core/network/d2d/truth_primitive_fetch_runtime.py:53`, `:149`, `:157`, `:181` | Closed by Fix3. Bucket set is bounded and pruned. |
| H7 chunked HTTP gossip body without content length | `ilc_core/network/d2d/http_gossip_transport_runtime.py:41`, `:268` | Closed by Fix3. `Transfer-Encoding` is rejected before body drain. |
| H8 unsafe `read_bundle()` materialization | `ilc_core/protocol/ndjson_bundle.py:37`, `:537`, `:574` | Closed by Fix3. Materialized record count is bounded; `iter_bundle()` remains streaming. |
| H9 unbounded `ILC-Gossip-Type` | `ilc_core/network/d2d/gossip_transport.py:24`, `:81` | Closed by Fix3. Gossip type values are byte-bounded. |
| H10 production assert in agent id derivation | `ilc_core/identity/agent_id_runtime.py:55` | Closed by Fix1. No production `assert` remains in `derive_agent_id_v2`. |
| M2 non-finite Decimal canonical string | `ilc_core/ledger/exact_numeric.py:35`, `:36` | Closed by Fix1. Non-finite Decimal rendering fails closed. |
| M15 non-atomic canon export write | `ilc_core/ledger/canon_export.py:107`, `:116` | Closed by Fix2. Uses same-directory temporary file plus `os.replace`. |
| One-line code-health precondition | `tests/test_code_health.py:33` | Closed before Phase 1332. `ilc_core/sim/` is excluded from code-health scope as simulation-only. |

## 4. Remaining Blockers Before Phase 1333

| ID | Finding | Evidence | Required disposition |
|----|---------|----------|----------------------|
| F1332-1 | Private-address SSRF denial is not enforced at peer endpoint validation. | `ilc_core/network/d2d/gossip_peer_registry.py:52` validates HTTPS syntax but does not reject loopback, private, link-local, or otherwise internal IP literals. | Fix4 before Phase 1333. Add endpoint IP classification/denial or a documented static-allowlist exception model, then add tests. |
| F1332-2 | CBOR decode has no pre-load size cap before `cbor2.loads`. | `ilc_core/crypto/cbor_canonical.py:35` calls `cbor2.loads(data)` at `:47` without first bounding `len(data)`. | Fix4 before Phase 1333. Add a byte cap before decode and tests for oversized input. |
| F1332-3 | Release-gate package profile validation remains too large for auditability. | `ilc_core/sidecars/registry_manifest.py:632` is `_validate_package_profile_integrity()`, reported by code health as 415 lines. | Fix4 before Phase 1333. Split into per-lane validators. |
| F1332-4 | TransportPrincipal admission builder has an unsafe argument surface. | `ilc_core/sidecars/transport_principal_admission.py:249`, reported by code health as 28 args. | Fix4 before Phase 1333. Introduce a params dataclass or equivalent validated input object. |
| F1332-5 | Source export / Atlas release-gate functions remain over code-health thresholds. | `ilc_core/rc/atlas_graph_discipline.py:1111`; `ilc_core/rc/source_allowlist_export_rehearsal.py:136` | Fix before Phase 1333/1339 as routed. Source export gate code should not stay in the failing code-health set. |
| F1332-6 | `test_code_health.py` still fails on non-sim runtime hotspots. | `CODE_HEALTH_TOP_N=20 .venv/bin/python -m pytest tests/test_code_health.py -q` | Blocker map only; not fully fixed in Phase 1332. Fix4/code-health subphase required. |

## 5. Carry-Forward With Rationale

| ID | Finding | Evidence | Disposition |
|----|---------|----------|-------------|
| H11 | `reputation.py` uses floats, mutates caller trust-vector state, and has no version token. | `ilc_core/consensus/reputation.py:7`, `:24`, `:37` | Deferred to Window 1343+ because the Decimal/version-token/mutation-boundary rewrite needs governance/CDL design. It is not an ECU settlement boundary today. |
| H12 | Hash-before-ref helper centralization is inconsistent across CCSS modules. | CCSS-003 has `_verify_ref()` at `confidential_coordination_sealed_sender.py:981`; CCSS-004 has inline `_reference_for()` at `confidential_coordination_gossip_policy.py:836`. | Carry-forward. Style/maintainability issue, not a Phase 1333 blocker. |
| H14 | CCSS-004 `_require_non_negative_int()` carries a shared `_MAX_SEQUENCE` upper bound into unrelated count fields. | `ilc_core/sidecars/confidential_coordination_gossip_policy.py:938` | Carry-forward with note. No immediate over-authorization or security bypass found. |
| M13 | CCSS-004 `_require_text()` parameter order differs from CCSS-001/002/003. | `ilc_core/sidecars/confidential_coordination_gossip_policy.py:875` | Carry-forward to a standalone CCSS-004 cleanup with search-and-replace and focused tests. |
| LOW-1 to LOW-5 | CCSS error-string consistency, path-relative test read, AST assert-ban coverage gaps, and test monkeypatch cleanup. | Candidate grouping §11 | Fix in place alongside the next CCSS module touch. |
| CLI/parser and lower-priority code-health items | `tests/test_code_health.py` output | Carry-forward per code-health lane unless they are release/source-export/Atlas gate functions. |

## 6. Runtime Guardrail Scope Review

`runtime_guardrail_scope_revalidated_phase_1332`

The sensitive runtime guardrail remains useful and passed in this phase. Its
current scope checks the highest-cost regressions: predictable PRNG, wall-clock
use on sensitive paths, production `assert`, selected outbound network timeout
requirements, TLS verification disablement, outbound fetch/archive bounds,
atomic writes for selected canonical/state files, strict canonical JSON, and
selected untrusted payload bounds.

Two gaps are now explicitly routed to Fix4 rather than hidden inside the
checker:

- Private-address endpoint denial is not yet a checker rule.
- CBOR pre-load size caps are not yet a checker rule.

Fix4 should close the implementation gaps first and then decide whether to
extend `tools/check_sensitive_runtime_coding_taboos.py` so these regressions
become machine-enforced.

## 7. Canonical JSON Security Sweep

`canonical_json_security_sweep_recorded_phase_1332`

Focused source reads and the sensitive-runtime static checker confirmed the
post-Fix1/Fix2/Fix3 canonical JSON posture for the audited machine surfaces:

- JSON hashing/canonicalization surfaces remain under `sort_keys=True` and
  `allow_nan=False` checks where the checker has explicit coverage.
- CCSS-001 now has the same pre-serialization byte-budget and oversized-integer
  hardening pattern used by later CCSS modules.
- Decimal canonical rendering rejects non-finite values before string emission.
- Known remaining payload-bound gap is CBOR, not JSON.

## 8. Non-Authorization Boundary

`release_blocker_audit_no_activation_phase_1332`

This audit did not execute Phase 1333, source allowlist export, clean public
tree materialization, public repository publication, public package publication,
release artifact production, release-key generation, release envelope
production, release signing material generation, signature production, release
signing, public RC claim, public launch claim, OpenClaw/ClawHub listing or
installability claim, Genesis Atlas mutation/regeneration/signing, v0.2 signing,
ATLAS-G-007, ATLAS-G-008, ATLAS-G-009, ATLAS-G-010, CDL mutation, CDL-088
opening, identity artifact creation, genesis record creation, seed commitment
artifact creation, dummy Agent Birth artifact creation, identity-seed generation,
mnemonic generation, private-key generation, secret-store write, public
claimability activation, public verifier service, public claim endpoint, public
P2P, public fetch serving, public ILC listener, peer discovery, non-loopback
bind, public sidecar/projection serving, public confidential messaging, public
confidential coordination serving, wallet-facing withdrawal request,
wallet-facing transfer request, wallet-facing spend request, wallet-provider
signing, wallet-provider ledger-write, wallet write, withdrawal runtime, ECU
minting, ILC settlement activation, value-path activation, counsel approval,
patent filing, CLA approval, trademark-policy publication, or legal conclusion.

## 9. Verification

```bash
python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_1332_g8_final_deterministic_code_security_audit.md
.venv/bin/python -m pytest tests/test_sensitive_runtime_coding_taboos.py
python3 tools/check_sensitive_runtime_coding_taboos.py
.venv/bin/python -m pytest tests/test_phase_1332_final_deterministic_code_security_audit.py tests/test_window_1330_1342_prompt_drafts.py
CODE_HEALTH_TOP_N=20 .venv/bin/python -m pytest tests/test_code_health.py -q
```

Expected and observed: `test_code_health.py` still fails with two failing tests
and two passing tests. That failure is the recorded code-health blocker, not a
Phase 1332 execution failure.

## 10. Graph Delta

```text
graph_delta=support_only:docs/specs/ilc_final_deterministic_code_security_audit_1332_v0.1.md -> planning/frontier
graph_delta=support_only:docs/phases/phase_1332_final_deterministic_code_security_audit_walkthrough.md -> planning/frontier
graph_delta=support_tests_added:tests/test_phase_1332_final_deterministic_code_security_audit.py -> validation
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_window_1330_1342_candidate_phase_grouping_v0.1.md -> planning/frontier
```
