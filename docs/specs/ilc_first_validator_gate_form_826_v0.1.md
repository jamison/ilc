# ILC First Non-Genesis Validator Deployment — Phase 826 §6 Gate Form

**Phase:** 826 §6
**Date:** 2026-04-26
**Operator:** Genesis Agent
**Reviewer:** Claude Sonnet 4.6 (local reviewer lane)

`first_validator_gate_826_pulled_2026_04_26`
`phase_826_s6_gate_form_v0_1_published`

---

## Gate statement

The first non-Genesis validator deployment gate (Phase 826 §6) is hereby pulled.
The operator authorizes the activation of Validator 4 (ilc-node-6) as the first
non-Genesis validator on the M-009 testnet, subject to the post-rotation smoke
proof requirement below.

---

## 1. Date and operator identity

**Date:** 2026-04-26
**Operator:** Genesis Agent (human principal, ILC project)
**Reviewer:** Claude Sonnet 4.6 (local architectural reviewer lane)

---

## 2. Validator IDs and machine identities

| Validator ID | Host | Tailscale IP | Role |
|-------------|------|-------------|------|
| 1 (Genesis) | ilc-node-1 | 100.111.172.103 | Honest |
| 2 (Genesis) | ilc-node-2 | 100.109.27.59 | Honest |
| 3 (Genesis) | ilc-node-3 | 100.108.3.57 | Honest |
| **4 (first non-Genesis)** | **ilc-node-6** | **100.73.21.68** | **Honest** |

Validator 4 was previously assigned to ilc-node-2 for testbed adversarial
simulation (HIGH-002 Phase B). This gate pull assigns it to ilc-node-6 as its
permanent deployment host.

---

## 3. Network ID and chain ID

**Network ID:** `ilc-mysticeti-testnet-m009`
**Chain ID:** Same (network_id is the BLS DST domain separator)
**is_testnet:** true
**real_ecu:** false

---

## 4. Genesis hash and validator-set snapshot

**Genesis file:** `config/mysticeti_testnet_M009/genesis.json`
**Version:** `mysticeti_testnet_m009_v0.3`
**Generated:** 2026-04-26 (key rotation at gate pull)

**Canonical SHA-256 (json.dumps sort_keys=True, separators=(',',':'))):**
```
0518b4738f1df26458ef000c1c715c0038cc253a4f29df57d66f8dea437d83bf
```

**Validator set snapshot:**

| Validator | Host | BLS12-381 G1 public key (first 32 chars) |
|-----------|------|------------------------------------------|
| V1 | ilc-node-1 | `8fc76b0b897092833d575794290242b4...` |
| V2 | ilc-node-2 | `922486d898592c3725e45f4e20d10946...` |
| V3 | ilc-node-3 | `86b28a5eb409ed07c091450524a7e03b...` |
| V4 | ilc-node-6 | `a07b32c8d62605d2c533002c22e5a9a4...` |

N=4, f=1, quorum_threshold=3.

All four BLS keypairs generated fresh on 2026-04-26 using `keygen --out <path>`
(getrandom IKM → blst key_gen). Public keys deployed to genesis.json v0.3.
Secret keys deployed to each node's `~/m009_phase779/certs/` directory.

---

## 5. Deployment command

On ilc-node-6:
```bash
ssh ilcops@100.73.21.68
cd ~/m009_phase779
./validator_harness --config validator_4_config.json >> validator_4.log 2>&1 &
echo $! > v4.pid
```

On ilc-node-1 (Genesis, local):
```bash
cd /Users/jamison/Documents/ILC_Main/01_Current
./ilc_consensus/target/release/validator_harness \
  --config config/mysticeti_testnet_M009/validator_1_config.json >> v1.log 2>&1 &
```

On ilc-node-2 and ilc-node-3: same pattern, `validator_<N>_config.json`.

---

## 6. Failure recovery runbook reference

`docs/ops/ilc_validator_deployment_failure_recovery_runbook_v0.1.md`

Summary of levels:
- Level 1 (process restart): safe, always available, LMDB preserved
- Level 2 (config restore, pre-epoch-commit): safe, LMDB preserved
- Level 3 (LMDB wipe): DESTRUCTIVE — testnet only (`real_ecu: false`); committed state is lost
- Level 4 (CDL-007 clawback): governance path, runtime not yet implemented

`gate_826_rollback_runbook_satisfied`

---

## 7. Row 5 acknowledgement

Row 5 (ADR-0028 Phase 812 parallel-obligation row) remains
`spec_closed_runtime_pending`. The B-Impl implementation window (6 Rust
obligations, `node.rs` entry point, k=30/k=20 rolling group, jitter,
bounded_hold) has not yet been executed. SIM-LEAKAGE-03 live run against
M-009 has not yet been executed.

Row 5 runtime closure is not a prerequisite for first-validator deployment at
controlled testnet scale (Phase 826 §3 rationale). The obligation remains
intact and carry-forward is confirmed.

`row5_runtime_obligation_carry_forward_acknowledged_at_gate_826`

---

## 8. HIGH-002 acknowledgement

**HIGH-002 is CLOSED** as of 2026-04-26. The original Phase 826 §6 checklist
read "acknowledgement that HIGH-002 remains production-hardening debt" — this
acknowledgement is superseded.

HIGH-002 Phase A (`3abd63e4`): `quorum_threshold(N) = 2*floor((N-1)/3)+1` in
`validator.rs`; `signers: Vec<ValidatorID>` in `EpochCheckpoint` +
`StoredCheckpoint`; `process_epoch_checkpoint` verifies subset ≥ threshold.
86/86 tests pass.

HIGH-002 Phase B (`53c4000d`): Live M-009 loopback run. V4 partitioned.
V1/V2/V3 committed epoch 1 with 3-of-4 quorum. SafetyNoDualCert unaffected.

`high_002_closed_gate_826_liveness_caveat_superseded`

---

## 9. Post-rotation smoke proof requirement

The Phase 826 §5 post-rotation smoke proof is required before this deployment
is accepted as successful. The smoke proof must pass all Phase 825 §5 criteria:

1. Validator peering across all four nodes
2. Live ECU transfer finalization (testnet, `real_ecu: false`)
3. Exact-once balance update
4. Extractable epoch state
5. Audit replayability
6. Rollback readiness (confirmed by runbook reference)

**Status at gate pull:** Phase 572 smoke proof passed all criteria with the
prior key set. A post-rotation proof on the new key set is required and will
be executed immediately following this gate form.

`post_rotation_smoke_proof_required_after_gate_826`

---

## 10. Explicit gate-pull statement

The first non-Genesis validator deployment gate (Phase 826 §6 of the Phase 826
Entry Conditions spec, published 2026-04-24) is hereby pulled by human operator
authorization.

Validator 4 (ilc-node-6, Tailscale 100.73.21.68) is authorized to join the
M-009 testnet as a first non-Genesis validator, operating under CDL-017
validator governance law.

`first_validator_gate_826_pulled_operator_authorized_2026_04_26`
`cdl_017_validator_governance_law_active_first_non_genesis_validator`
`validator_4_ilc_node_6_authorized_join_m009_testnet`

---

## Prerequisites satisfied

| Prerequisite | Status | Reference |
|-------------|--------|-----------|
| SEC-004 historical validator-set binding | ✅ closed | Phase 768 |
| M-007 local ValidatorSet mutation helpers | ✅ available | CDL-017 authority |
| M-019 adversarial hardening | ✅ complete | Window 839-843 |
| M-021 genesis BLS fix | ✅ complete | Phase M-021 |
| SEC-007a vendored protoc build path | ✅ green | Phase 826 §2 verification |
| Phase 825 settlement-path rotation design consumed | ✅ | Phase 572 implementation |
| Validator keys generated and deployed | ✅ | 2026-04-26 (this session) |
| TLS material generated and deployed | ✅ | 2026-04-26 (this session) |
| Genesis state recorded (v0.3) | ✅ | 2026-04-26 (this session) |
| Network ID confirmed | ✅ | `ilc-mysticeti-testnet-m009` |
| Failure recovery runbook | ✅ | v0.1 published 2026-04-26 |
| Phase 572 smoke proof passed | ✅ | 2026-04-22 |
| HIGH-002 closed | ✅ | Phase B `53c4000d` 2026-04-26 |
| Post-rotation smoke proof | ⬜ PENDING | Immediately following gate pull |

---

*Gate form drafted by reviewer. To be signed by operator.*

**Operator signature:** Genesis Agent — 2026-04-26

`gate_826_s6_form_operator_signed_2026_04_26`
