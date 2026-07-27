# ILC DAG Substrate — Public RC Gap Plan v0.1

**Date:** 2026-07-27
**Status:** DRAFT — for Codex review and human GO
**Owner:** Genesis Agent
**Sensitivity:** NON-SENSITIVE (planning document); individual phases below carry their own sensitivity
**Phase series:** GAP-SUBSTRATE-01 through GAP-INTEGRATION-11, assigned Phases 1584–1593

---

## §1 — Purpose and Scope

This document is the authoritative gap plan for activating the ILC distributed DAG consensus
substrate (`ilc_consensus/`) at public RC. It was produced after a deep investigation of the live
codebase on 2026-07-27, following confirmation by the Genesis Agent that all 11 identified gaps
are blocking for public RC.

The distributed DAG substrate (`ilc_consensus/`, Rust, Mysticeti-style BLS, QUIC networking) is
the canonical ILC settlement rail at production launch. Every pre-RC soak ran against a local
Python LMDB store only. The substrate has never been exercised as a settlement destination
end-to-end. This plan closes that gap before public RC.

**Canonical reference:** `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md` §ILC;
CDL-065 ("The Mysticeti substrate may carry ILC legitimacy, not author it").

**Pre-RC hardening rule (Codex review correction, 2026-07-27):** Because the project
is now close to public RC, substrate blockers must not be closed by "document and
defer" dispositions when the public RC claim depends on the blocked behavior. Each
discovered blocker must either be resolved in a Fix phase with executable pass
criteria, or explicitly removed from public RC scope with a human-approved non-claim.

---

## §2 — Codebase State at Gap Discovery (2026-07-27)

| Symbol | File | Value | Meaning |
|--------|------|-------|---------|
| `PRODUCTION_BRIDGE_ACTIVE` | `ilc_core/consensus/production_bridge.py:32` | `False` | Python→Rust bridge is a stub |
| `submit_ecu_transfer_via_quic()` | `ilc_core/consensus/production_bridge.py:607-614` | `raise ValueError(LIVE_ECU_TRANSFER_NOT_ACTIVATED_TOKEN)` when bridge inactive; `raise ValueError("production_bridge_activation_not_implemented_phase_1358")` even when active | Write path not implemented at either end |
| `require_production_validator_admission_activation()` | `ilc_core/validator/admission_ejection_runtime.py:396-402` | `raise ValueError("production_validator_admission_activation_not_implemented_phase_1353")` | Admission not implemented |
| `PASSIVE_ECU_WIRING_NOT_ACTIVATED` | `ilc_core/economics/epoch_attribution_settle_runtime.py:56` | `False` | Operationally set for 49-epoch private soak; no SENSITIVE authorization phase ran |
| `public_claimability_activated` | `ilc_core/sidecars/wallet_action_semantics_preflight.py:60,146` | `False` (enforced by `_require_all_false()`) | Must flip to `True` at public RC |
| `ilc_settlement_authorized` | `ilc_core/sidecars/wallet_action_semantics_preflight.py:68,174` | `False` (enforced by `_require_all_false()`) | Must flip to `True` at public RC |
| `is_testnet` | `config/mysticeti_testnet_M009/genesis.json` | `true` | All timing enforcement bypassed; needed: `false` for mainnet |
| `SettlementPath` | `ilc_consensus/src/config.rs:97` | `None` in all current configs | `MysticetiFastPath` not activated in any config |
| `process_epoch_checkpoint()` | `ilc_consensus/src/epoch_settlement.rs:233` | Implemented (BLS verify + LMDB write) | Rust-side settlement exists; no exposed write endpoint from Python |
| Rust gRPC proposal ingress | `ilc_consensus/src/app_interface.rs` | Read-only (`IlcAppReadService`) | No proposal ingress for epoch settlement submission |
| TLA+ Spec D | `docs/specs/ilc_tla_plus_spec_d_phase_1385a_v0.1.tla` (Phase 1385a) | 67M states proved SafetyNoDualCert | Does NOT model `not_before_unix_ms` timing or validator admission/ejection |

**Key architecture fact (not previously documented in one place):** The Rust
`validator_harness` binary runs an internal BFT consensus protocol via
`FastPathProtocol` and `NodeRunner`. Python→Rust settlement is NOT a direct call
to `process_epoch_checkpoint()` — it requires Python to submit epoch data to the
validator network via a QUIC or gRPC proposal ingress, which the validators then
process through BFT agreement before calling `process_epoch_checkpoint()`. Neither
the Python proposal call nor the Rust proposal ingress currently exist.

---

## §3 — Gap Inventory

| Gap ID | What is missing | Blocking for RC? | Phase |
|--------|----------------|-----------------|-------|
| GAP-SUBSTRATE-07 | Passive ECU guard disposition (`PASSIVE_ECU_WIRING_NOT_ACTIVATED = False` set without SENSITIVE authorization) | Yes — pre-mirror hard stop | **1584** |
| GAP-SUBSTRATE-BRIDGE-SPEC | Wire protocol spec: Python submits a canonical epoch settlement proposal; Rust validators own BFT ordering/signing/checkpoint commitment | Yes — gates implementation | **1585** |
| GAP-SUBSTRATE-BRIDGE-RUST | Implement authenticated Rust proposal ingress; route into consensus-owned checkpoint processing, not a direct externally supplied checkpoint bypass | Yes — core activation | **1586** |
| GAP-SUBSTRATE-BRIDGE-PY | Implement Python client in `production_bridge.py`; flip `PRODUCTION_BRIDGE_ACTIVE = True` | Yes — core activation | **1587** |
| GAP-SUBSTRATE-CONFIG | Mainnet genesis config (`is_testnet=false`); provision timing enforcement | Yes — mainnet gate | **1588** |
| GAP-SUBSTRATE-ADMISSION | Validator admission activation: clear `PRODUCTION_VALIDATOR_ADMISSION_NOT_ACTIVATED` guard, implement production path | Yes — validators must join | **1589** |
| GAP-SUBSTRATE-TLA | TLA+ timing/admission model update plus TLC evidence, or explicit human-approved removal of those semantics from public RC scope | Yes — formal substrate gap | **1590** |
| GAP-INTEGRATION-SOAK | E2E soak: Python proposal → Rust authenticated ingress → BFT/quorum checkpoint → `process_epoch_checkpoint()` → LMDB → Python gRPC read | Yes — final gate | **1591** |
| GAP-SEMANTICS-WALLET-RC | Wallet action semantics preflight RC posture: flip `public_claimability_activated` and `ilc_settlement_authorized` to True only after distributed-substrate integration passes | Yes — users must claim consensus-backed balances | **1592** |

Note: GAP-CONSENSUS-09 (ConsensusBridgeConfig into soak harness) is addressed within
Phase 1591 (GAP-INTEGRATION-SOAK). GAP-SUBSTRATE-01 (E2E integration test) is the same
as GAP-INTEGRATION-SOAK. GAP-SUBSTRATE-02 is split into BRIDGE-SPEC (1585) +
BRIDGE-RUST (1586) + BRIDGE-PY (1587). GAP-SUBSTRATE-03 and GAP-SUBSTRATE-08
(TLA+ gaps) are combined into Phase 1590.

---

## §4 — Critical Path

```
Phase 1584 (Passive ECU guard) ──────────────────────────────────────────────────────┐
Phase 1585 (Bridge spec) ──→ Phase 1586 (Bridge Rust) ──→ Phase 1587 (Bridge Py) ──→┐│
Phase 1588 (Mainnet config) ──→ Phase 1589 (Validator admission) ─────────────────→ ││
Phase 1590 (TLA+ timing/admission model + TLC evidence) ─────────────────────────────┤│
                                                                                      ↓│
                                                              Phase 1591 (Integration soak)
                                                                                      │
                                                              Phase 1578h (Wallet gate)┤
                                                                                      ↓
                                                              Phase 1592 (Wallet RC preflight)
```

**Parallel tracks (no dependency on each other):**
- 1584, 1588, and 1590 can run in parallel with each other
- 1584 can run concurrently with 1585
- 1592 (wallet RC preflight) must run AFTER Phase 1578h wallet gate completes AND after
  Phase 1591 confirms consensus-backed readback

**Sequential constraints:**
- 1585 → 1586 → 1587 (bridge spec gates implementation; Rust gates Python)
- 1588 → 1589 (mainnet config needed before admission live testing)
- 1590 → 1591 unless timing/admission semantics are explicitly removed from public RC scope
- 1586 + 1587 + 1588 + 1589 + 1590 → 1591 (all substrate components and formal gap
  disposition needed before integration soak)
- 1578h + 1591 → 1592 (wallet gate and consensus-backed substrate readback must pass first)

---

## §5 — Phase Detail

---

### Phase 1584 / GAP-CDL060-PASSIVE-ECU-GUARD

**Sensitivity:** SENSITIVE — guard disposition requires explicit human GO
**GO phrase:** `GO GAP-CDL060-PASSIVE-ECU-GUARD AUTHORIZED PATH-B AUTHORIZE-CURRENT-STATE`
**Prerequisite:** None
**Prompt status:** COMPLETE on Path B, 2026-07-27

**Background:**
`PASSIVE_ECU_WIRING_NOT_ACTIVATED = False` at
`ilc_core/economics/epoch_attribution_settle_runtime.py:56`. This was set
operationally during the 49-epoch canonical private soak (commit `93773ef8a`). No
SENSITIVE authorization phase ran. The forward plan (Part 12b G-F row) states
"deferred to a future SENSITIVE guard-clearance phase." Phase 1581 recorded the
ambiguity but did not resolve it.

**Execution result:**
Phase 1584 executed Path B. The current source value
`PASSIVE_ECU_WIRING_NOT_ACTIVATED = False` remains unchanged and is explicitly
authorized for public RC under CDL-052/CDL-060/CDL-078 authority. The prior
Phase 1581 ambiguity is resolved by token
`passive_ecu_guard_disposition_committed_phase_1584`.

**Historical scope:**
Two resolution paths were available before execution:

**Path A (Re-guard to True):** Set `PASSIVE_ECU_WIRING_NOT_ACTIVATED = True`. This
matches the forward plan's deferred intent. Passive ECU is NOT active at public RC.
Activation requires a future SENSITIVE `GAP-CDL060-GUARD-CLEARANCE` phase with explicit
CDL-060 authority analysis.

**Path B (Authorize current state):** Run a SENSITIVE authorization phase that explicitly
reviews CDL-060, CDL-052, CDL-078, and the passive ECU attribution chain, determines
that `PASSIVE_ECU_WIRING_NOT_ACTIVATED = False` is correct for public RC, and emits a
disposition token. Flag must remain False (meaning passive ECU IS active) with explicit
governance authority.

**Deliverables:**
- Walkthrough doc: `docs/phases/phase_1584_gap_cdl060_passive_ecu_guard_walkthrough.md`
- Test correction: `tests/test_phase_1577_passive_ecu_wiring.py`
- Output token: `passive_ecu_guard_disposition_committed_phase_1584`

**Non-claims:** No CDL is opened by this phase. Path A: passive ECU deferred to post-RC.
Path B: passive ECU authorized for RC with explicit governance citation.

---

### Phase 1585 / GAP-SUBSTRATE-BRIDGE-SPEC

**Sensitivity:** NON-SENSITIVE — spec-only, no code changes
**Prerequisite:** None
**Prompt status:** Drafted and validator-compliant

**Background:**
The Python→Rust bridge (`production_bridge.py`) has a stub that raises
`ValueError("production_bridge_activation_not_implemented_phase_1358")`. The Rust
`validator_harness` binary exposes only a gRPC read service. No write endpoint exists.
Before Codex can implement either side, the wire protocol must be specified.

**Scope:**
Produce `docs/specs/ilc_production_bridge_proposal_ingress_spec_1585_v0.1.md` defining:

1. **Epoch proposal wire format:** How Python serializes a canonical epoch settlement
   proposal for submission to the Rust network. Define whether this uses:
   - gRPC proposal ingress (`SubmitEpochProposal`) added to `app_interface.rs`, or
   - QUIC datagram via `PersistentQuicSessionManager`

   Recommendation: authenticated gRPC proposal ingress — consistent with the existing
   read-service pattern and avoids raw QUIC framing complexity. Do not define an external
   `SubmitEpochCheckpoint` API unless the request is already a post-consensus, quorum-signed
   artifact produced by Rust validators.

2. **BLS signing chain:** `process_epoch_checkpoint()` expects a `SignedEpochCheckpoint`
   with BLS multi-signatures from validators. The signing chain must be specified:
   - Who produces the `EpochSettlementRecord` (Python, from LMDB lifecycle writes)
   - Who verifies the proposal preimage and evidence references
   - Who BLS-signs (Rust validators, after receiving the proposal through the ingress path)
   - Whether Python submits an unsigned proposal that Rust validators collectively sign via
     BFT, or whether the phase is intentionally downgraded to a Genesis-controlled single
     operator devnet with explicit non-BFT public-RC non-claims

3. **Error contract:** What Rust returns on: BLS verify failure, timing violation
   (`not_before_unix_ms` too far future, `MIN_EPOCH_DURATION_MS` not elapsed),
   epoch sequence conflict, or duplicate submission.

4. **`ConsensusBridgeConfig` extension:** What new fields are needed in the Python
   `ConsensusBridgeConfig` dataclass to support the proposal path (gRPC ingress endpoint,
   timeout, retry policy).

5. **`SettlementPath=MysticetiFastPath` prerequisite check:** The Rust binary must be
   running with `settlement_path=mysticeti_fast_path` for the proposal ingress to be
   active. Spec must define how Python detects and enforces this.

**Deliverables:**
- `docs/specs/ilc_production_bridge_proposal_ingress_spec_1585_v0.1.md`
- Output token: `production_bridge_proposal_ingress_spec_committed_phase_1585`

**Human decision required (before Phase 1586 begins):**
The BLS signing chain option in item 2 above is the key architectural decision. The
default recommended public-RC path is N=4, f=1, because this matches the previous
Mysticeti/TLA model family and demonstrates distributed BFT rather than single-operator
settlement. `check_settlement_path_gate()` currently rejects f=0 with an error:
"settlement_path=mysticeti_fast_path with f=0 is not permitted; HIGH-002 hardening
required." Human must decide:
- Use N≥4, f≥1 for public RC (recommended)
- OR explicitly downgrade RC0.1 to a Genesis-controlled non-BFT devnet and record that
  non-claim before any public release language says distributed consensus is live

This decision gates the BLS signing architecture in Phase 1586.

---

### Phase 1586 / GAP-SUBSTRATE-BRIDGE-RUST

**Sensitivity:** SENSITIVE — Rust runtime mutation
**GO phrase:** `GO GAP-SUBSTRATE-BRIDGE-RUST AUTHORIZED`
**Prerequisite:** Phase 1585 complete; human BLS signing architecture decision made
**Prompt status:** Drafted and validator-compliant

**Background:**
The Rust `validator_harness` binary has no proposal ingress for epoch settlement
submission. `process_epoch_checkpoint()` exists at `epoch_settlement.rs:233` but is
only called internally (in tests and node internals). Python has no path to trigger it.

**Scope:**
Implement authenticated proposal ingress in Rust:

1. Extend `ilc_app.proto` with a `SubmitEpochProposal` RPC that accepts the canonical
   proposal payload defined by Phase 1585
2. Add `SubmitEpochProposalRequest` and `SubmitEpochProposalResponse` message types
3. Implement the handler in `app_interface.rs`:
   - Authenticate the caller and enforce TLS/mTLS or an equivalent configured allowlist
   - Validate domain, network ID, epoch number, idempotency key, max body size, and replay state
   - Route the validated proposal into the Rust consensus-owned path
   - Call `EpochSettlementProtocol::process_epoch_checkpoint()` only after BFT/quorum signing
     has produced a valid `SignedEpochCheckpoint`
   - Return success/error token
4. Wire the proposal-ingress service into the gRPC server in `main.rs` (alongside existing read service)
5. Gate behind `settlement_path == MysticetiFastPath` check
6. Resolve HIGH-002 guard disposition per Phase 1585 human decision
7. Add Rust unit tests for the new gRPC proposal-ingress handler
8. Rebuild and verify `validator_harness` binary

**Deliverables:**
- Modified `ilc_consensus/src/app_interface.rs` (new write handler)
- Modified `ilc_consensus/proto/ilc_app.proto` (new RPC + message types)
- Modified `ilc_consensus/src/main.rs` (wire proposal-ingress service into server)
- Rust test coverage (at minimum: submit valid checkpoint passes; submit duplicate fails;
  submit checkpoint with invalid BLS fails)
- `docs/phases/phase_1586_gap_substrate_bridge_rust_walkthrough.md`
- Output token: `rust_grpc_submit_epoch_proposal_implemented_phase_1586`

**ILC_CDL_MUTATION_AUTHORIZED:** Not required (no CDL mutation). Rust + proto changes require:
`ILC_CDL_MUTATION_AUTHORIZED=not_required ILC_CDL_MUTATION_PHASE=1586`

---

### Phase 1587 / GAP-SUBSTRATE-BRIDGE-PY

**Sensitivity:** SENSITIVE — Python runtime mutation (`ilc_core/`)
**GO phrase:** `GO GAP-SUBSTRATE-BRIDGE-PY AUTHORIZED`
**Prerequisite:** Phase 1586 complete (Rust proposal ingress exists)
**Prompt status:** Drafted and validator-compliant

**Background:**
`submit_ecu_transfer_via_quic()` at `production_bridge.py:607-614` raises
`ValueError("production_bridge_activation_not_implemented_phase_1358")` even when
`PRODUCTION_BRIDGE_ACTIVE = True`. Python has no serialization of `EpochSettlementRecord`
and no gRPC proposal client.

**Scope:**

1. Replace `submit_ecu_transfer_via_quic()` stub with actual implementation:
   - Serialize the Python epoch settlement proposal into the wire format defined by Phase 1585
   - Call the Rust gRPC `SubmitEpochProposal` endpoint via the existing `ConsensusBridgeConfig.target`
   - Handle all error responses from Phase 1586's error contract
   - Enforce socket timeout (`grpc_timeout_seconds`)

2. Extend `ConsensusBridgeConfig` with write-path fields per Phase 1585 spec

3. Flip `PRODUCTION_BRIDGE_ACTIVE = True` with an explicit phase token constant:
   `PRODUCTION_BRIDGE_ACTIVATED_PHASE_1587_TOKEN`

4. Add Python unit tests:
   - `test_submit_ecu_transfer_calls_grpc_write_endpoint`
   - `test_submit_ecu_transfer_rejects_bad_config`
   - `test_submit_ecu_transfer_handles_rust_error_responses`
   - `test_production_bridge_active_flag_is_true`

5. Update `__all__` with new token constant

**Deliverables:**
- Modified `ilc_core/consensus/production_bridge.py`
- Modified `tests/test_production_bridge.py` (new tests)
- `docs/phases/phase_1587_gap_substrate_bridge_py_walkthrough.md`
- Output token: `production_bridge_write_path_activated_phase_1587`

**ILC_CDL_MUTATION_AUTHORIZED:** Not required (no CDL mutation, only `ilc_core/` change).

---

### Phase 1588 / GAP-SUBSTRATE-CONFIG

**Sensitivity:** SENSITIVE — creates mainnet configuration
**GO phrase:** `GO GAP-SUBSTRATE-CONFIG MAINNET-GENESIS AUTHORIZED`
**Prerequisite:** None
**Prompt status:** Drafted and validator-compliant

**Background:**
All current configs use `is_testnet: true` (`config/mysticeti_testnet_M009/genesis.json`).
With `is_testnet=true`, `epoch_settlement.rs` bypasses all timing enforcement:
- Forward skew guard (`CLOCK_SKEW_TOLERANCE_MS = 300_000` — 5 min) is skipped
- Minimum epoch duration guard (`MIN_EPOCH_DURATION_MS = 2_592_000_000` — 30 days) is skipped

Public RC requires a mainnet genesis config with `is_testnet: false` to enforce these
guards. This also gates Phase 1589 (validator admission), which must be tested against
a mainnet-mode config.

**Scope:**

1. Create `config/mysticeti_mainnet_rc01/genesis.json` with:
   - `"is_testnet": false`
   - `"network_id": "ilc-rc01"` (or human-specified RC network ID)
   - Real BLS12-381 G1 public keys for the validator set (per human decision on f-value
     from Phase 1585: single-validator f=0 with HIGH-002 disposition, or multi-validator)
   - `"settlement_path": "mysticeti_fast_path"`
   - All other required genesis fields

2. Create `config/mysticeti_mainnet_rc01/node_config.toml` with:
   - `grpc_listen_addr` for the gRPC server
   - `endpoint_projection_path` pointing to validator peer configuration
   - All required TLS certificate paths

3. Document the timing implications in a spec annex:
   - 30-day minimum epoch duration means settlement is NOT fast at RC0.1 (testnet cadence only)
   - Operators must understand the timing gate before going live
   - Either: RC0.1 uses a shorter epoch via explicit CDL parameter (if CDL-027 allows), or
     timing enforcement is accepted as-is

4. Record the HIGH-002 disposition: if using f=0 single-validator, emit an explicit
   guard disposition token `high_002_f_zero_rc_posture_dispositioned_phase_1588` with
   a rationale that RC0.1 is Genesis-controlled, not independently operated.

**Deliverables:**
- `config/mysticeti_mainnet_rc01/genesis.json`
- `config/mysticeti_mainnet_rc01/node_config.toml`
- `docs/phases/phase_1588_gap_substrate_config_walkthrough.md`
- Output token: `mainnet_rc01_genesis_config_committed_phase_1588`

---

### Phase 1589 / GAP-SUBSTRATE-ADMISSION

**Sensitivity:** SENSITIVE — removes a production guard
**GO phrase:** `GO GAP-SUBSTRATE-ADMISSION VALIDATOR-ADMISSION AUTHORIZED`
**Prerequisite:** Phase 1588 (mainnet config) complete
**Prompt status:** Drafted and validator-compliant

**Background:**
`admit_validator()` at `ilc_core/validator/admission_ejection_runtime.py:269` returns
`PRODUCTION_VALIDATOR_ADMISSION_NOT_ACTIVATED_TOKEN` when called without the activation
token, and `require_production_validator_admission_activation()` at line 396 raises
`ValueError("production_validator_admission_activation_not_implemented_phase_1353")`
even with the correct token. Neither Python nor Rust side has a live admission path.

The Rust side (`ilc_consensus/`) has `admit_validator()` in the Rust code with a 1,000
ECU minimum stake requirement (per prior phase notes), but this has never been tested
end-to-end against the Python admission runtime.

**Scope:**

1. Review the full Python `admit_validator()` call path and the Rust counterpart; map
   how they are meant to interlock (this is a pre-drafting claim-enumeration step)

2. Implement the production path in Python `admit_validator()`:
   - Remove the NOT_ACTIVATED guard
   - Emit `PRODUCTION_VALIDATOR_ADMISSION_ACTIVATION_TOKEN` in the return
   - Wire to the Rust admission path via `ConsensusBridgeConfig` (or direct gRPC call)
   - Enforce 1,000 ECU minimum stake check via `EcuActiveLayerRuntime`

3. Add integration test with Phase 1588 mainnet config:
   - `test_admit_validator_mainnet_mode_requires_minimum_stake`
   - `test_admit_validator_mainnet_mode_propagates_to_rust_consensus`
   - `test_admit_validator_mainnet_mode_rejected_below_minimum_stake`

4. Document the validator admission invariants in the walkthrough

**Deliverables:**
- Modified `ilc_core/validator/admission_ejection_runtime.py`
- New/modified tests in `tests/test_validator_admission.py`
- `docs/phases/phase_1589_gap_substrate_admission_walkthrough.md`
- Output token: `production_validator_admission_activated_phase_1589`

---

### Phase 1590 / GAP-SUBSTRATE-TLA

**Sensitivity:** NON-SENSITIVE — spec and formal-methods only, no code changes
**Prerequisite:** None (can run in parallel with 1584–1589); must complete before Phase 1591
**Prompt status:** COMPLETE via Phase 1590-Fix1 on 2026-07-27

**Execution result (2026-07-27):**
TLC found a real `SafetyNoDualCert` counterexample after dynamic admission to five
validators. With the live Rust threshold `quorum_threshold(5)=3`, signer sets
`{1,2,5}` and `{3,4,5}` can certify conflicting epoch-1 roots while intersecting
only at Byzantine validator `5`. Completion token
`tla_plus_timing_admission_checked_phase_1590` was not emitted. Phase 1591 remains
blocked until a SENSITIVE quorum-intersection hardening phase reruns TLC cleanly.
Recommended fix: change production quorum threshold to `n - f`, or otherwise
constrain admission to intersection-safe validator-set sizes.

**Fix1 result (2026-07-27):**
Phase 1590-Fix1 changed the Rust production threshold to
`N - floor((N - 1) / 3)`, updated the TLA model to the same rule, and reran TLC
cleanly. TLC result: 1,031,138 generated states, 255,483 distinct states, depth
10, queue 0, no violations. Token `tla_plus_timing_admission_checked_phase_1590`
is now live.

**Background:**
TLA+ Spec D (Phase 1385a, 2026-05-18) proved `SafetyNoDualCert` over 67M states. It
does not model:
1. `not_before_unix_ms` — the timing field added to `EpochSettlementRecord` in the
   1575h-Fix5 commit (`63cab34cc`, 2026-07-23). This field triggers a 5-min forward
   skew guard and 30-day minimum epoch duration guard, both gated on `is_testnet=false`.
2. Validator admission and ejection — `admit_validator()` and `eject_validator()` are
   not modeled in any TLA+ spec.

**Scope:**
Produce formal-methods evidence, not only a documentation note:

1. Documents the exact gap between Spec D and the current Rust implementation
2. Records the specific invariants that need future TLA+ coverage:
   - `not_before_unix_ms` forward-skew liveness property (no valid checkpoint is
     permanently rejected by timing guard)
   - `MIN_EPOCH_DURATION_MS` safety property (no epoch advances faster than 30 days
     on mainnet)
   - Validator admission monotonicity (once admitted, not double-admitted)
   - Validator ejection finality (ejected validator cannot re-enter in the same epoch)
3. Adds or updates a bounded TLA+ model for the active RC substrate mode, with at least:
   - `NoSkipEpoch`
   - `NoFastMainnetEpoch` when `is_testnet=false`
   - `NoFutureCheckpointAccepted`
   - validator-admission/ejection membership safety for the selected RC scope
   - `SafetyNoDualCert` preserved under the new timing/membership fields
4. Runs TLC with checked-in config(s), records state counts and PASS/FAIL output, and
   commits the evidence
5. If the selected RC mode intentionally excludes dynamic admission/ejection or mainnet
   timing, records that as a human-approved public-RC non-claim instead of silently
   deferring the proof
6. Emits token `tla_plus_timing_admission_checked_phase_1590`

**Deliverables:**
- `docs/specs/ilc_tla_plus_substrate_timing_admission_evidence_1590_v0.1.md`
- `docs/phases/phase_1590_gap_substrate_tla_walkthrough.md`
- Output token: `tla_plus_timing_admission_checked_phase_1590`

---

### Phase 1591 / GAP-INTEGRATION-SOAK

**Sensitivity:** SENSITIVE — live Rust binary, BLS verification, mainnet config
**GO phrase:** `GO GAP-INTEGRATION-SOAK SUBSTRATE-E2E AUTHORIZED`
**Prerequisite:** Phases 1586 + 1587 + 1588 + 1589 + 1590 ALL complete, plus the
confirmed public-RC live lanes: invite economics (1576m-1576r), spectral commitment
(1580 + 1582, implementing validator-signed `C(t) = (M(t), S(t))`), dynamic discovery
and validator identity (1577 + 1577a + 1577b + 1579 + 1583), and wallet gate 1578h PASS.
**Prompt status:** Drafted and validator-compliant

**Background:**
All prior soaks (Phases 1575h, 1575p, 1575r, 1575s, 1575t) ran Python-only against
local LMDB stores. No soak has ever: (a) produced a Python epoch checkpoint,
(b) submitted it to a running `validator_harness` binary, (c) had Rust verify the BLS
signatures and call `process_epoch_checkpoint()`, and (d) read the settled balance back
via the gRPC read service. This is the final integration gate before public RC.

**Scope:**

This phase is the most complex deliverable in the plan. It requires:

0. **Public-RC live-scope prerequisite check:** Verify that invite economics, spectral
   commitment, dynamic discovery / peer advertisement / validator identity, and wallet
   gate 1578h are complete. These are confirmed public-RC live claims as of 2026-07-27,
   so the integration soak must test the final public-RC substrate shape, not an
   intermediate bridge-only system.

1. **Test harness setup:** Script that starts the `validator_harness` binary or equivalent
   test harness with `#[cfg(test)]`-shortened timing constants, while separately verifying
   that the production binary enforces the Phase 1588 immutable timing constants. No
   genesis-config timing bypass is authorized.

2. **Proposal production:** Python script that:
   - Runs a mini economic soak (1-3 epochs via `EcuIlcLifecycleRuntime`)
   - Serializes the resulting epoch settlement proposal via the bridge wire format
   - Submits via the Phase 1587 production bridge client

3. **Rust processing verification:** Confirm via Rust logs or gRPC read response that:
   - The proposal entered the consensus-owned path, not a direct external checkpoint bypass
   - `process_epoch_checkpoint()` was called
   - BLS verification passed
   - LMDB settlement record was written

4. **Readback verification:** Call `get_epoch_record()` and `get_balance()` via the
   Python `ILCConsensusGrpcReadAdapter` and confirm the settled balance matches the
   Python-side calculation

5. **Wire `ConsensusBridgeConfig`** into the soak harness (replacing the bare stub
   calls that exist in current test infrastructure)

6. **Timing note:** The mainnet config's 30-day epoch minimum makes live integration
   testing impractical. After Phase 1588 removes `is_testnet` entirely, there is no
   timing bypass in any genesis config. The soak test binary must use a test genesis
   config coupled with `#[cfg(test)]`-shortened timing constants (e.g.,
   `MIN_EPOCH_DURATION_MS_TEST = 10_000` — 10 seconds) compiled into the test binary.
   This confirms the integration path without requiring a 30-day wait, and without any
   production bypass. The walkthrough must note that the test binary uses shortened
   constants and that the production binary enforces 30-day timing unconditionally.

7. **Tests:**
   - `test_e2e_python_to_rust_epoch_checkpoint_submission`
   - `test_e2e_rust_bls_verification_passes_for_valid_checkpoint`
   - `test_e2e_gRPC_readback_matches_python_settled_balance`
   - `test_e2e_rust_rejects_duplicate_epoch_submission`

**Deliverables:**
- `tools/phase1591_integration_soak.py` (harness script)
- `tests/test_phase_1591_integration_soak.py` (integration tests)
- `docs/phases/phase_1591_gap_integration_soak_walkthrough.md`
- Output token: `e2e_python_rust_substrate_integration_soak_committed_phase_1591`
- Output token: `production_bridge_end_to_end_verified_phase_1591`

---

### Phase 1592 / GAP-SEMANTICS-WALLET-RC

**Sensitivity:** SENSITIVE — changes authorization flag posture
**GO phrase:** `GO GAP-SEMANTICS-WALLET-RC CLAIMABILITY-AUTHORIZED`
**Prerequisite:** Phase 1578h wallet gate PASS verdict + Phase 1591 substrate integration soak PASS
**Prompt status:** Drafted and validator-compliant; execute after 1578h and 1591 complete

**Background:**
`wallet_action_semantics_preflight.py` currently enforces ALL flags in
`_FALSE_AUTHORIZATION_FLAGS` (lines 54-71) as False, including:
- `public_claimability_activated` (line 60)
- `ilc_settlement_authorized` (line 68)

Phase 1578h (the public RC wallet gate) explicitly confirms these are False and emits
`wallet_transfer_spend_withdrawal_blocked_through_public_rc_phase_1578h`. But at
public RC, `public_claimability_activated` and `ilc_settlement_authorized` MUST flip
to True only after the balances being claimed are verified through the distributed
substrate readback path. This phase makes that change after Phase 1591, not before it.

The other flags in `_FALSE_AUTHORIZATION_FLAGS` (transfer, withdrawal, spend) remain
False through public RC default and require a separate `TRANSFER-ENABLED RC AUTHORIZED`
gate (per the wallet gate prompt spec).

**Scope:**

1. Read `wallet_action_semantics_preflight.py` in full and map every flag, its current
   enforcement location, and its required state at RC

2. Restructure `_FALSE_AUTHORIZATION_FLAGS` or add a complementary
   `_RC_AUTHORIZED_FLAGS` block that allows `public_claimability_activated=True` and
   `ilc_settlement_authorized=True` while keeping transfer/withdrawal/spend blocked

3. Update `run_wallet_action_semantics_preflight()` to:
   - Accept `public_claimability_activated=True` as valid
   - Accept `ilc_settlement_authorized=True` as valid
   - Continue to enforce `wallet_transfer_enabled=False`, `wallet_withdrawal_enabled=False`,
     `wallet_spend_enabled=False`

4. Add tests:
   - `test_preflight_accepts_claimability_authorized_at_rc`
   - `test_preflight_accepts_ilc_settlement_authorized_at_rc`
   - `test_preflight_still_rejects_transfer_enabled_at_rc`
   - `test_preflight_still_rejects_withdrawal_enabled_at_rc`

5. Update the genesis agent wallet records to set `public_claimability_activated=True`
   and `ilc_settlement_authorized=True` (requires re-running the wallet action
   preflight with the updated flags, per the wallet sidecar invocation path)

**Deliverables:**
- Modified `ilc_core/sidecars/wallet_action_semantics_preflight.py`
- New tests
- `docs/phases/phase_1592_gap_semantics_wallet_rc_walkthrough.md`
- Output token: `public_claimability_authorized_phase_1592`
- Output token: `ilc_settlement_authorized_phase_1592`

---

## §6 — Sensitivity and GO Phrase Table

| Phase | Gap | Sensitivity | GO Phrase |
|-------|-----|-------------|-----------|
| 1584 | Passive ECU guard | SENSITIVE | `GO GAP-CDL060-PASSIVE-ECU-GUARD AUTHORIZED` |
| 1585 | Bridge proposal-ingress spec | NON-SENSITIVE | — |
| 1586 | Bridge Rust proposal ingress | SENSITIVE | `GO GAP-SUBSTRATE-BRIDGE-RUST AUTHORIZED` |
| 1587 | Bridge Python | SENSITIVE | `GO GAP-SUBSTRATE-BRIDGE-PY AUTHORIZED` |
| 1588 | Mainnet config | SENSITIVE | `GO GAP-SUBSTRATE-CONFIG MAINNET-GENESIS AUTHORIZED` |
| 1589 | Validator admission | SENSITIVE | `GO GAP-SUBSTRATE-ADMISSION VALIDATOR-ADMISSION AUTHORIZED` |
| 1590 | TLA+ timing/admission check | NON-SENSITIVE | — |
| 1591 | Integration soak | SENSITIVE | `GO GAP-INTEGRATION-SOAK SUBSTRATE-E2E AUTHORIZED` |
| 1592 | Wallet RC preflight after substrate readback | SENSITIVE | `GO GAP-SEMANTICS-WALLET-RC CLAIMABILITY-AUTHORIZED` |

---

## §7 — Human Decisions — CONFIRMED 2026-07-27

All three decisions confirmed by Genesis Agent on 2026-07-27.

---

**Decision 1 (before Phase 1585/1586): Validator set size at RC0.1**

**CONFIRMED: N≥4, f=1 (true distributed BFT).**

Provision at least 4 validators for BFT quorum at RC0.1. `check_settlement_path_gate()`
already rejects f=0 with `settlement_path=mysticeti_fast_path`. HIGH-002 is resolved by
the quorum requirement, not by a single-validator bypass disposition. Phase 1585 must record
Decision 1 as N≥4 f=1 in its spec §7 so downstream phases can cite it.

---

**Decision 2 (before Phase 1584): Passive ECU path at RC**

**CONFIRMED: Path B — Authorize current state (PASSIVE_ECU_WIRING_NOT_ACTIVATED = False).**

Phase 1584 is SENSITIVE and requires GO phrase:
`GO GAP-CDL060-PASSIVE-ECU-GUARD AUTHORIZED PATH-B AUTHORIZE-CURRENT-STATE`

Passive ECU IS active for public RC. Phase 1584 must review CDL-060, CDL-052, CDL-078,
and the passive ECU attribution chain, confirm the current False value is correct under
those authorities, and emit a governance-cited disposition token.

---

**Decision 3 (before Phase 1588): RC0.1 epoch timing**

**CONFIRMED: Immutable compile-time constants; `is_testnet` field removed entirely.**

Security rationale: Genesis Agent must not have unilateral power over epoch timing.
Only the community via constitutional governance (CDL-027 amendment process) can change
epoch duration. Giving a genesis config field control over timing enforcement would make
whoever controls the genesis file a target and would allow minting-rate manipulation.

**What Phase 1588 does:**
- Remove `is_testnet: bool` from `EpochSettlementProtocol` struct in `epoch_settlement.rs`
- Remove both `if !self.is_testnet { ... }` conditionals — timing guards are unconditional
- Remove `is_testnet` from `GenesisConfig` struct and genesis parsing in `config.rs`
- `MIN_EPOCH_DURATION_MS = 2_592_000_000` (30 days, CDL-027) and
  `CLOCK_SKEW_TOLERANCE_MS = 300_000` (5 min) remain as compile-time Rust constants
- Rust tests that need short epochs use `#[cfg(test)]`-gated shortened constants —
  transparent in source code, zero production impact
- Post-public-RC speedier testing uses private local simulation, not production bypass
- Future timing changes require a CDL-027 amendment through full community governance

**Explicitly rejected approaches:**
- Option C (genesis-parameterized timing): rejected because genesis creator would have
  unilateral power over timing and minting rate
- Option B (CDL-027 amendment for shorter RC epochs): rejected; 30-day timing is accepted
- Option A (accept 30-day timing, keep `is_testnet` flag): rejected; `is_testnet` bypass
  must be removed for security hardening regardless of timing choice

---

## §8 — Prompt Drafting Status (as of 2026-07-27)

All phase prompts for Window 1584–1593 were drafted and committed at
`3dd282d1d` (window guidance doc + all 10 phase prompts + closure gate).
Phase 1588 was subsequently amended at the commit following this gap plan
update to reflect Decision 3 (immutable timing, `is_testnet` removed).

| Phase | Prompt status | Blocking decision |
|-------|--------------|-------------------|
| 1584 | COMPLETE Path B authorization; `PASSIVE_ECU_WIRING_NOT_ACTIVATED=False` authorized for public RC | RESOLVED |
| 1585 | COMPLETE; NON-SENSITIVE; spec committed with token `production_bridge_proposal_ingress_spec_committed_phase_1585` | RESOLVED |
| 1586 | Drafted; GO required after 1585 | — |
| 1587 | Drafted; GO required after 1586 | — |
| 1588 | Drafted + amended for Decision 3 immutable timing; GO required | RESOLVED |
| 1589 | Drafted; GO required after 1588 | — |
| 1590 | COMPLETE via Fix1 quorum-intersection hardening; TLC PASS depth 10 | RESOLVED |
| 1591 | Drafted; GO required after 1586+1587+1588+1589+1590 + invite/spectral/discovery/wallet-gate prerequisites | — |
| 1592 | Drafted; GO required after 1578h and 1591 | — |
| 1593 | Drafted (closure gate); GO required after all phases | — |

**Phase 1591 timing note update:** Phase 1591 originally referenced running the
integration soak with "testnet M009 config" to bypass timing. Since Phase 1588 removes
`is_testnet` entirely, Phase 1591 must instead use a test binary or harness with
`#[cfg(test)]`-shortened timing constants and separately verify that the production binary
enforces the 30-day timing constants unconditionally. The Phase 1591 prompt has been
updated to reflect this execution model.

---

## §9 — Non-Claims

This planning document does NOT:
- Authorize any of the SENSITIVE phases above
- Change any guard state, flag, or CDL
- Constitute a public RC launch authorization
- Constitute a transfer-enabled RC authorization
- Push any public mirror update
- Change the `GENESIS_WALLET_WRITE_AUTHORIZED` flag
- Modify any production path code

All code mutations require the GO phrases listed in §6 and must follow the standard
Phase Window Workflow: prompt → human review → GO → Codex execution → walkthrough → commit.

---

## §10 — LMDB Node Registration

| Path | node_kind | graph_delta |
|------|-----------|-------------|
| `docs/specs/ilc_dag_substrate_public_rc_gap_plan_v0.1.md` | `spec_doc` | `support_only` |

> Use the table above as the **baseline plan** — Codex must expand and correct it based
> on actual files created during execution: every new file in `docs/specs/`,
> `docs/antigravity_tasks/`, `ilc_core/`, `tools/`, or `tests/` requires a ledger
> record with the correct `node_kind` and typed trace edges per the taxonomy in
> `docs/specs/ilc_atlas_graph_node_classification_and_edge_type_taxonomy_v0.1.md`.
> Write ledger atomically with `tempfile.mkstemp` + `os.replace`. Run coverage audit
> after writing to confirm all staged new files are registered.
