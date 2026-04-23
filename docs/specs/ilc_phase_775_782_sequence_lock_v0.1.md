# ILC Phase 775-782 Sequence Lock v0.1

**Phase:** 775  
**Window:** 775-782  
**Date:** 2026-04-22  
**Author:** Local architectural reviewer (Sonnet)

`window_775_782_sequence_lock_active`
`row_5_privacy_remediation_window`
`layer_1_agentid_log_hygiene_and_layer_2_batching_multi_relay`
`sim_leakage_01_rerun_required_before_closure`
`row_5_honest_nonclosure_permitted_if_bands_not_met`
`no_cdl_mutation_in_window_775_782`
`window_767_774_closed_capsule_v5_6_current_at_sequence_lock_time`

## 1. Baseline and authority order

Window 767-774 is closed. Capsule `v5.6` is the current frontier. SEC-004
acceptance test is passing. M-007 hooks are activated under CDL-017 authority.
Six post-window bugs were found and fixed (BUG-001 through BUG-006, 2026-04-22)
and are already committed on head at `dda9c06a`; Phase 775 verifies this
baseline before any row-5 remediation work begins.

Row 5 is `spec_closed_runtime_pending`. The authoritative honest-fail record is
`docs/research/ilc_sim_leakage_01_results_M021_v0.1.md` (verdict: fail at
recall=1.0 across all three variants; no privacy layer applied in M-021; result
expected and documented).

Authority order for this window:

1. live `STATUS.md` tail and `docs/PLANNING_INDEX.md`
2. capsule `v5.6`
3. `docs/research/ilc_post_766_continuation_program_guide_2026_04_22_v0.1.md`
   (Window 2 section — all pre-window design questions resolved 2026-04-22)
4. `docs/research/ilc_sim_leakage_01_results_M021_v0.1.md` (authoritative fail record)
5. `docs/specs/ilc_sim_leakage_01_commissioning_spec_740_v0.1.md`
6. `docs/specs/ilc_row_5_mechanism_family_matrix_680_v0.1.md`
7. `docs/specs/ilc_row_5_prework_narrowing_decision_682_v0.1.md`
8. `docs/specs/ilc_privacy_public_legitimacy_threat_model_678_v0.1.md`
9. `docs/specs/ilc_public_legitimacy_observability_budget_679_v0.1.md`
10. live constitutional decision log
11. `config/mysticeti_testnet_M009/README.md` (authoritative multi-machine host layout)

## 2. Pre-window state corrections and decisions (decided 2026-04-22)

The following design decisions and scope corrections are locked before execution
begins. Codex must not re-open these as design questions.

**Row 5 scope — decided:**
Row 5 does not require hiding the content of public submissions. The public
epistemic graph is public by design. Row 5's actual protection target is
**AgentID behavioral pseudonymity**: preventing an attacker from building a
behavioral fingerprint from submission timing, frequency, inter-submission
interval, and activity correlation that de-pseudonymizes a CDL-042 derived
AgentID. The receipt is public; the submitter-to-receipt behavioral linkage is
the protected thing.

Private shard coordination is out of scope for Row 5.

**Attacker model — decided (corrected for p2p architecture):**
The SIM-LEAKAGE-01 variant labels map to the production p2p architecture as:
- Variant A (operator-path): **node-local log attacker** — a node operator
  reads validator log files. AgentID is currently logged in plaintext in every
  `acking_transfer` line. This is the Layer-1 surface.
- Variant B (hosted-query structural): **gRPC balance surface attacker** —
  any party querying `GetBalance` before and after submission windows can
  reconstruct transfer graphs from balance delta observation. Layer-2 partially
  addresses this by breaking the timing correlation.
- Variant C (repeated-contributor): **epoch-lineage correlator** — an attacker
  correlating `GetEpochChain` state roots across epoch boundaries with
  `GetBalance` queries to cluster contributors across epochs. Layer-2 submission
  indirection partially disrupts this; full ZK nullifiers are the long-term answer.

There is no central API. Privacy must be at every submission boundary.

**Layer-2 mechanism family — decided:**
From Phase 680's near-term tractable survivor set:
- **Near-term target**: batching + multi-relay submission indirection.
  Timing-window batching disrupts Variant A/C temporal correlation. Multi-relay
  routing (non-custodial; distinct from CDL-060 single-hop gossip) means no
  single relay sees both submitter identity and full behavioral pattern.
- **Relay eligibility filter**: relay candidates filtered by reputation
  percentile (R_min) AND centrality percentile (C_min) against epoch-anchored
  agent subgraph. Applied locally by submitting agent. SIM-calibrated in this
  window.
- **Wire format constraint**: near-term implementation must be ZK-compatible.
  Submission envelope design must not preclude a later ZK nullifier overlay.
- **Long-term named target**: ZK nullifier-style submission unlinkability (Phase
  680 "later-stage tractable" — deferred; not in this window's scope).

**H-013 non-dependency — confirmed:**
H-013 (D2d sealed-sender ADR) does not gate Row 5 Layer-2. The submission relay
channel is a separate subsystem from CDL-060 centrality delta gossip.
Windows 775-782 (Row 5) and 791-800 (hypergraph) are parallel.

**Committed baseline to verify before window opens:**
BUG-001 through BUG-006 (found 2026-04-22, fixed same day) are already
committed at `dda9c06a`. Phase 775 verifies that the live head still contains
those fixes before any further mutation occurs. See §8.

## 3. Window meaning

Window 775-782 is the Row 5 privacy remediation window.

`layer_1_agentid_log_hygiene_required`
`layer_2_batching_multi_relay_indirection_required`
`relay_eligibility_filter_r_min_c_min_required`
`sim_leakage_01_rerun_required_two_iterations_minimum`
`row_5_closure_permitted_only_if_all_three_bands_satisfied`
`honest_nonclosure_required_if_any_band_still_fails`
`zk_compatibility_note_required_on_wire_format_decisions`
`observability_floor_must_remain_intact_after_remediation`

This window exists to:

1. implement Layer-1 AgentID log hygiene (redact AgentID from log lines in
   non-debug builds across all node-facing surfaces)
2. implement Layer-2 batching + real multi-machine relay submission
   indirection across the M-009 topology (local + two VPSs)
3. retarget the SIM harness so Run 2 measures the relay-aware path rather than
   the legacy direct-broadcast path
4. rerun SIM-LEAKAGE-01 at minimum twice: post-Layer-1 only, then post-both-layers
5. record the closure or honest non-closure verdict against all three bands
6. confirm ZK compatibility of all wire format decisions made in this window
7. update capsule and close the window honestly

This window does not close row 8. It does not advance Option B. It does not
interact with H-013 or CDL-060. It does not claim perfect anonymity.

## 4. Implementation scope

### 4.1 Layer-1 — AgentID log hygiene

**Target surface:** all `tracing::info!` / `eprintln!` / log macro call sites
in `ilc_consensus/src/` that emit `AgentID` bytes in plaintext.

**Specific known site:** `node.rs` — the `acking_transfer` log line that prints
`agent: AgentID([...])` in the object_ref. Confirmed as the primary Variant A
leakage surface by SIM-LEAKAGE-01.

**Approach:** in non-debug builds (i.e., without `--cfg debug_agent_ids` or
equivalent feature gate), replace AgentID bytes in log lines with an opaque
short token (e.g., first 4 bytes as hex, prefixed `[redacted:`). In debug
builds the full AgentID remains visible for development.

**Observability floor constraint:** the Phase 679 observability floor requires
that receipts remain discoverable, lineage legible, challengeability preserved,
and bounded human auditability intact. AgentID redaction in log files does not
affect gRPC query surfaces — `GetBalance` and `GetEpochRecord` remain unaffected.
Log hygiene targets only the node-local disk/log surface.

**Required outcome:** SIM-LEAKAGE-01 Variant A rerun with log hygiene applied
should show recall substantially reduced from 1.0. Threshold is ≤ 0.60.

### 4.2 Layer-2 — Batching + multi-relay submission indirection

**Submission batching:**
The submission path actually exercised by SIM-LEAKAGE-01 must support a
`--batch-window-ms` parameter (or equivalent) that places a submission into a
fixed-length timing window before the first relay hop. This disrupts the
precise per-submission timestamp available in Variant A log correlation and
degrades Variant C epoch-boundary clustering.

Minimum batch window for SIM calibration: 200ms–2000ms range. Default:
500ms (calibrate during window; update default if SIM shows different optimum).

**Multi-relay submission routing:**
The SIM-LEAKAGE submission path must support routing through multiple relay
candidates rather than directly to the primary validator. At minimum: two relay
hops before reaching the final validator destination. This must be exercised on
the real M-009 multi-machine topology: one local host plus the two VPS hosts
declared in `config/mysticeti_testnet_M009/README.md`.

For this window, "relay candidate" = another validator peer that receives a
relay-envelope and forwards it unchanged toward the next hop. This is
non-custodial: the relay forwards but does not mutate the transfer or final
certificate semantics. Validator/network scope expansion is explicitly
authorized for this forwarding path.

**ZK compatibility:** the submission envelope must not include a timestamp field
that uniquely identifies the submitter. Any metadata fields added to support
batching must be either absent from the production wire format or explicitly
noted as `testnet_only`.

### 4.3 Relay selection baseline

The current runtime does not expose a live reputation/centrality surface that
can support `R_min` / `C_min` percentile filtering honestly in this window.
Accordingly, the executable baseline for Window 775-782 is an explicit
testnet-only relay allowlist drawn from the M-009 validator set and exercised
across the local + two-VPS topology.

For this window:
- relay path selection must be deterministic and explicit
- the allowlist must be documented in the Phase 778 mechanism artifact
- the path used in each SIM run must be recorded explicitly

Carry-forward:
- reputation/centrality relay eligibility remains a later-surface enhancement
- this window must not claim `R_min` / `C_min` were calibrated in runtime

### 4.4 SIM-LEAKAGE-01 rerun protocol

Two mandatory runs:

**Run 1: post-Layer-1 only.** Apply log hygiene; do not apply Layer-2. Rerun
the full SIM-LEAKAGE-01 harness against all three variants. Record recall for
each variant. This isolates the Layer-1 contribution.

**Harness interpretation requirement for Run 1:** once AgentID bytes are
redacted from node-local logs, Variant A can no longer use the plaintext
`AgentID([..])` extraction path from M-021. The harness must be updated to
interpret the redacted log form honestly and report the post-redaction
observable rather than failing on a stale plaintext regex.

**Run 2: post-both-layers.** Apply both Layer-1 and Layer-2. Rerun all three
variants through the relay-aware submission path, not the legacy direct
broadcast path. Record recall. This is the primary closure evidence.

**Harness retarget requirement:** the SIM-LEAKAGE-01 harness currently drives
direct `broadcast` submissions. Before Run 2, it must be updated so the
measured path is the real relay-aware path introduced in this window. If the
harness is not retargeted, Run 2 is invalid and the window may not claim row-5
closure evidence.

For each run, the commissioning spec thresholds apply:
- Variant A (operator-path): recall ≤ 0.60
- Variant B (hosted-query): structural recall ≤ 0.45
- Variant C (repeated-contributor): structural recall ≤ 0.45

Closure rule: all three bands must be satisfied in Run 2 for row-5 to close.
If any band still fails after Run 2, record an honest non-closure verdict with
the exact residual recall values.

**Variant B note:** Variant B measures structural recall against the gRPC
balance surface. Layer-2 submission indirection does not directly address the
gRPC `GetBalance` polling surface (which reveals balance changes regardless of
submission path). Layer-1 does not address it either. Variant B structural
recall may remain elevated. This is a known limitation and must be documented
honestly — it does not block the attempt, but it may result in honest
non-closure for Variant B.

### 4.5 What must not be implied

- No sentence in this window may claim perfect anonymity.
- No sentence may claim that ZK nullifiers are implemented.
- No sentence may claim that the gRPC balance query surface is anonymized.
- No sentence may imply row 5 is closed unless all three bands are satisfied in
  Run 2. If any band fails, the verdict is honest non-closure.
- No sentence may imply that the observability floor is violated. Log hygiene
  applies only to node-local logs; gRPC receipt and lineage surfaces remain open.

## 5. Phase table and sequencing

| Order | Phase | Topic | Character |
|---|---:|---|---|
| 1 | 775 | sequence lock (this document) + committed-head BUG-001..006 verification | gate |
| 2 | 776 | Layer-1 AgentID log hygiene implementation | M-track Rust |
| 3 | 777 | SIM-LEAKAGE-01 Run 1 (post-Layer-1 only) | SIM |
| 4 | 778 | Layer-2 batching + multi-relay submission indirection | M-track Rust |
| 5 | 779 | SIM-LEAKAGE-01 Run 2 (post-both-layers) + relay eligibility calibration | SIM |
| 6 | 780 | Row-5 evaluation artifact: closure or honest non-closure verdict | evaluation |
| 7 | 781 | Coherence report + capsule v5.7 | coherence |
| 8 | 782 | Closure gate + handoff | gate |

Sequencing rules:

- Phase 775 requires verification that head still contains the BUG-001..006
  fixes before any implementation work begins (see §8)
- Phase 777 must follow Phase 776 (Layer-1 must be built before Run 1)
- Phase 779 must follow Phase 778 (Layer-2 must be built before Run 2)
- Phase 780 reads both SIM run results; it may not execute before Run 2 completes
- Phase 780 must record honestly; if bands are not met it must not claim closure
- Phase 781 capsule is `v5.7` regardless of whether row 5 closes
- Phase 782 closure gate must assert the verdict token from Phase 780

## 6. Pass conditions for closure gate (Phase 782)

The closure gate must assert:

- Layer-1 log hygiene is implemented; `AgentID` does not appear in plaintext
  in non-debug build log lines
- Layer-2 batching and multi-relay implementation exists in `ilc_consensus/`
- SIM-LEAKAGE-01 Run 1 artifact exists with recall values for all three variants
- SIM-LEAKAGE-01 Run 2 artifact exists with recall values for all three variants
- Phase 780 row-5 evaluation artifact exists and contains one of:
  - `row_5_closure_verdict=pass` (all three bands met) — only if actually satisfied
  - `row_5_honest_nonclosure_verdict=bands_not_met` with the exact residual values
- ZK compatibility note recorded: wire format decisions do not preclude ZK overlay
- Observability floor intact: gRPC receipt/lineage surfaces unaffected by remediation
- No CDL mutation occurred anywhere in Window 775-782
- Capsule v5.7 exists and supersedes v5.6
- Handoff names the residual Row 5 gap (if any) and the long-term ZK nullifier path

## 7. Non-goals

This window does not include:

- ZK nullifier implementation
- H-013 sealed-sender ADR or CDL-060 gossip changes
- Row 8 substrate evaluation
- CDL-062 admissibility determination
- Option B graduation
- Any `ilc_core/` Python runtime mutation
- Any constitutional decision-log mutation
- Private shard architecture or ZK proximity proof
- Full anonymity against a global passive adversary

## 8. Pre-window commit requirement

Before Phase 776 executes, the following bug fixes must be committed:

**Committed baseline files to verify:**
- `ilc_consensus/src/validator.rs`
  - BUG-001: `rebuild_with` warning for f=0 on N>1
  - BUG-002: `check_concentration_limit` multiplication fix (exact 1/3 rejection)
  - BUG-006: `check_concentration_limit` saturation guard + new edge-case tests
- `ilc_consensus/src/fast_path.rs`
  - BUG-003: `rotate_validator_set` staleness window eliminated
  - BUG-004: `test_quorum_floor_enforced_after_ejection` added
- `ilc_consensus/src/testnet_client_main.rs`
  - BUG-005: `--epoch` default-to-1 with warning replaces hard mandatory flag
- `tests/test_phase_768_sec_004_acceptance.py`
  - Updated to match BUG-005 behavior

**Required committed head subject:**
`fix(g8): remediate post-window 767-774 audit findings`

**Required verification before proceeding past Phase 775:**
- `~/.cargo/bin/cargo test --features testnet_fault_sim` — all pass (76 tests)
- `.venv/bin/python -m pytest tests/test_phase_768_sec_004_acceptance.py -q` — pass

## 9. Source inputs

- `docs/PLANNING_INDEX.md`
- `docs/phases/STATUS.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.6.md`
- `docs/specs/ilc_window_767_774_closure_gate_774_v0.1.md`
- `docs/research/ilc_post_766_continuation_program_guide_2026_04_22_v0.1.md`
- `docs/research/ilc_sim_leakage_01_results_M021_v0.1.md`
- `docs/specs/ilc_sim_leakage_01_commissioning_spec_740_v0.1.md`
- `docs/specs/ilc_row_5_mechanism_family_matrix_680_v0.1.md`
- `docs/specs/ilc_row_5_prework_narrowing_decision_682_v0.1.md`
- `docs/specs/ilc_privacy_public_legitimacy_threat_model_678_v0.1.md`
- `docs/specs/ilc_public_legitimacy_observability_budget_679_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `ilc_consensus/src/node.rs` (locate acking_transfer log line)
- `ilc_consensus/src/testnet_client_main.rs` (submission paths)
- `config/mysticeti_testnet_M009/README.md` (local + two-VPS topology)

This sequence lock remains active until Phase `782` closes Window `775-782`.
