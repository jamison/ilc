# ILC Antigravity Context Capsule v5.17

Supersedes: docs/specs/ilc_antigravity_context_capsule_v5.16.md
Date: 2026-04-26
Owner lane: CDL-069 PQ identity and epoch endorsement ratification (Phase 838)

`capsule_v5_17_supersedes_v5_16`
`cdl_069_ratified_recorded_in_capsule_v5_17`
`phase_838_complete`
`phase_838_test_count_213_all_pass`
`row5_spec_closed_runtime_pending_preserved`
`first_validator_deployment_human_gate_not_yet_pulled`
`row5_sim_leakage_03_live_run_deferred_pending_rust_integration_gate`

This capsule is self-contained.

## 1. Current Frontier State

**Phase 838 (CDL-069 ratification lane) — COMPLETE.**

CDL-069 is ratified as of commit `9ea0ca23` (2026-04-26). Three new runtime
files govern post-quantum identity and epoch endorsement:

| File | Version token |
|------|---------------|
| `ilc_core/identity/genesis_record_schema.py` | `genesis_record_schema_838e.v0.1` |
| `ilc_core/identity/endorsement_packet_schema.py` | `endorsement_packet_schema_838f.v0.1` |
| `ilc_core/identity/epoch_endorsement_runtime.py` | `epoch_endorsement_runtime_838c.v0.1` |

Two audit rounds completed (commits `c5dc9633`, `c8fd06a0`) — 17 findings
fixed across both rounds. 213 tests, all pass.

**Prior state (v5.16) preserved:** Track 1 pre-deployment lane (Phases 830–837)
remains at the same posture. First-validator human gate not yet pulled.

## 2. CDL-069 Ratified Scope

ML-DSA-65 (FIPS 204) is the mandatory canonical identity root key for all
agents from Genesis forward. BLS12-381 is retained exclusively for consensus
aggregation and ephemeral hot signing (per-validation-epoch endorsement keys).

Ratified protocol constants:
- `agent_id = sha384("ilc-agent-id-v1:" || identity_seed)` — 96-char hex, permanent
- `blinding_factor = sha384("ilc-recovery-blind-v1:" || identity_seed)` — deterministic
- Tier 3 (permanent): SHA-384 for all genesis record commitments and agent_id
- Tier 2 (issuance epoch): SHA-256 for endorsement packets, epoch-close attestations
- Tier 1 (validation epoch): SHA-256 for ephemeral BLS keys, gossip

Migration window: pre-ratification agents with BLS12-381 identity root keys
accepted under the legacy `derive_agent_id` path during migration only. New
agents from ratification forward must use ML-DSA-65.

## 3. CDL Status (relevant)

| CDL | Status | Phase |
|-----|--------|-------|
| CDL-001 | Open (genesis_blocker, bounded for packaging) | — |
| CDL-017 | **Ratified** | 765 |
| CDL-042 | Ratified | 407 |
| CDL-068 | Ratified | 743 |
| CDL-069 | **Ratified** | 838j |
| CDL-070 | Not yet opened (forward PQ migration ceremony) | — |
| CDL-071 | Not yet opened (temporal tier reconciliation) | — |

## 4. Identity and Endorsement Surface

Three runtime layers now govern the CDL-069 identity and endorsement protocol:

1. **Genesis ceremony layer** (`genesis_record_schema.py`): derives blinding
   factor, computes genesis record commitments, validates recovery transactions
   with freeze clamping.
2. **Endorsement packet schema layer** (`endorsement_packet_schema.py`): strict
   field validation, liveness assertion derivation, COSE_Sign1 payload
   construction.
3. **Validator runtime layer** (`epoch_endorsement_runtime.py`): sequence-number
   ordering, valid_epochs window enforcement, supersedes_epoch_id distributed
   atomicity, freeze/revocation, `EndorsementCache` eviction.

Open item D1 (recovery spec wire format mismatch between Rust `pq_keygen` and
Python `encode_recovery_spec`) is non-blocking; CDL-070 resolution path.

## 5. First-Validator Deployment Readiness

Unchanged from v5.16. All code-verifiable Phase 826 entry conditions satisfied.
Human gate not pulled. CDL-069 ratification is an additive strengthening — it
does not change the gate-pull conditions.

What remains:
1. Operator provisions validator keys, TLS material, genesis state, network ID,
   rollback plan (Phase 826 §6).
2. Live three-machine smoke proof passes all Phase 825 §5 criteria.
3. Human authorization record completed per Phase 826 §6.

## 6. Row 5 and SIM-LEAKAGE-03

Row 5 remains `spec_closed_runtime_pending`. CDL-069 ratification establishes
a structural assertion (Phase 838h item 7) that SIM-LEAKAGE-03 bounds A/B/C
remain satisfiable under the endorsement protocol — but the live run is still
required before `runtime_closed` can be recorded.

The live run requires: (1) Rust privacy lane integration gate (human decision);
(2) live `LeakageMetricsCollector` run against M-009 testbed; (3)
`check_bounds()` returning `{"A": True, "B": True, "C": True}`.

`row5_sim_leakage_03_live_run_deferred_pending_rust_integration_gate`

## 7. Preserved Boundaries

- Option B selected, not graduated,
- CDL-017 ratified; first non-Genesis validator deployment human-gated,
- Row 5 `spec_closed_runtime_pending`,
- privacy lane not wired into live settlement,
- SIM-LEAKAGE-03 live run not yet executed,
- CDL-070 and CDL-071 not yet opened.

## 8. Immediate Carry-Forward

**Code-side (convergence window):**
1. Open Codex convergence window — all three entry conditions satisfied
   (SIM-LEAKAGE-01 committed, M-019 bundle committed, M-022 exitability drill
   committed).
2. Row 5 runtime-closure evaluation against SIM-LEAKAGE-01 results.
3. Row 7 censorship-resistance closure against M-019 + Phase 698 TLC.
4. Row 7 strong-exitability closure against M-022 evidence.
5. Row 8 disposition + Option B graduation-gate synthesis (ADR-0028).
6. CDL-017 convergence-window work (SEC-004 hard pre-ratification requirement
   must be addressed).
7. Convergence window coherence report + closure gate.

**Operator-gated:**
1. First-validator human gate (Phase 826 §6 checklist).
2. Rust privacy lane integration gate → SIM-LEAKAGE-03 live run on M-009.
