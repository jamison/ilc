# ILC CDL/ADR Implementation Map v0.1

**Recorded:** 2026-05-14
**Frontier phase at recording:** Phase 1336 (Window 1330-1342 open)
**Purpose:** Maps every ratified CDL and accepted ADR to its runtime implementation
file(s), key dependency tokens, and implementation status. Use this as the primary
audit guide when verifying spec-to-code correspondence.

**Status legend:**
- `FULL` — fully implemented with tests; DEPENDENCY token present in runtime
- `PARTIAL` — some aspects coded; others deferred, hard-coded False, or raise NotImplementedError
- `NONE` — no production runtime implementation; spec/governance only
- `GOV-A` — governance/constitutional decision that produced real code as a direct consequence; cite the file
- `GOV-B` — purely conceptual governance decision; no compute-layer runtime exists or is required; cite whitepaper/spec doc
- `GOV-C` — both: shaped real code AND has a conceptual component not yet built

**How to interpret GOV-A/B/C:**
Every ratified CDL made a *decision*. That decision either (A) directly caused or constrained
a function or module to be written, (B) is a constitutional rule or policy that lives entirely
in governance docs with no corresponding code object, or (C) both. A CDL that is GOV-B is
not a gap in the code — it is intentionally off-chain governance. A CDL that is GOV-C or
GOV-A with a missing component is a gap.

> **WARNING — living document:** This map was generated from a point-in-time scan.
> Update it when new CDL/ADR phases ratify, or when runtime implementations land.
> Do not treat it as authoritative for phases beyond 1336 without re-verifying.

---

## Quick-Reference: Implementation Status by Functional Domain

| Domain | CDLs/ADRs | Fully implemented | Gaps / GOV-B note |
|--------|-----------|-------------------|------|
| Issuance & emission schedule | CDL-025, 026, 027, 028, 029, 030, 031 | None | **ALL** — biggest unimplemented cluster |
| Treasury & fee governance | CDL-047, CDL-050 | None | Both |
| Allocation & Genesis cap | CDL-029, ADR-0008 | Cap governor only | Per-epoch distributor missing |
| Epoch attribution & settlement | CDL-081, 082, 083, 084, 085 | 081, 082, 084, 085 | CDL-083 treasury path (NotImplementedError) |
| Consensus & finality | CDL-051, CDL-V3, CDL-045 | 051, V3, 045 (request surface) | 045 auto-trigger absent |
| Validator governance | CDL-017, 054, 055, 056, 057, 058, 068 | 055, 056, 057, 058 | CDL-017 hooks stub, CDL-054 none, CDL-068 VRF absent |
| Identity & admission | CDL-040, 042, 066, 069, CDL-V2 | All | — |
| Epistemic / Popperian | CDL-V7, 049, 052, 059, 072, 073, 074, 075 | All | — |
| Node schema & lifecycle | CDL-034–038, 046 | All | — |
| Transport & P2P | CDL-039, 061, 076, 077, 078, 079, 080 | All | — |
| Bootstrap & genesis | CDL-022, 040, 073, 079 | All | — |
| Reputation & decay | CDL-V1, CDL-013 | CDL-V1, CDL-013 | H11 Decimal rewrite complete; production governance/reputation activation remains gated |
| Storage & schema | CDL-020, 023, 043, 044, 064, 071 | 020, 023, 064, 071 | CDL-043/044 partial |
| Claimability & conversion | CDL-048, CDL-088 | Partial (CDL-048 skeleton) | CDL-088 not opened |
| Release & packaging | CDL-086, 087 | Partial | Public serving gated |
| Sovereign substrate | ADR-0028 | `ilc_consensus/` (M-series Rust crate) | **PARTIAL** — M-series complete; `ilc_core/` production bridge missing (Phases 1358–1360) |
| Sidecar query | ADR-0031 | Partial | Many query types NotImplementedError |
| **V-series (constitutional cluster)** | CDL-V1 through CDL-V7 | V1, V2, V3, V7 full; V5 GOV-A | V4=GOV-B (intentional, procedural); **V6=GOV-B (gap — no enforcement code for 3-lifetime cap)** |
| **Founder/governance cluster** | CDL-003, 004, 005, 006, 008, 009, 010, 015 | GOV-A or GOV-C (partial) | CDL-006 challenge node spec unbuilt; CDL-009 fork UX unbuilt; CDL-005 preconditions CDL-025–031 which are all NONE |

---

## CDL Implementation Map

### Issuance & Emission Economics
*(CDL-025 through CDL-031 are all spec-ratified but have NO production runtime. This is the single largest gap cluster.)*

| CDL | Topic | Status | Runtime file(s) | Key notes |
|-----|-------|--------|-----------------|-----------|
| CDL-025 | Terminal issuance model (H=48 monthly halving) | **NONE** | — | `commit_epoch_emission_runtime.py` exists but is NOT production emission authorization (explicitly devnet only) |
| CDL-026 | C_max finite lock (total supply ceiling) | **NONE** | — | Constant ratified; not encoded as enforceable runtime constant in production |
| CDL-027 | Decay formulation + halving schedule | **NONE** | — | Schedule ratified; no production halving runtime |
| CDL-028 | Fee-burn split (10% of fees → genesis/burn per epoch) | **NONE** | — | No fee-burn runtime in `ilc_core/` |
| CDL-029 | Allocation split (80/15/5 performer/auditor/genesis) | **PARTIAL** | `ilc_core/analysis/genesis_accrual_governor.py` | Governor (cap/taper) implemented: `THETA_HARD = Decimal("0.05")`, `THETA_SOFT = exp(-3)`. The per-epoch *distributor* that routes 80/15/5 at each epoch commit does NOT exist. |
| CDL-030 | ECU price clamp | **NONE** | — | No price-clamp runtime |
| CDL-031 | Dynamic ranking policy | **NONE** | — | Node value kernel exists; CDL-031 dynamic ranking not production-implemented |

### Treasury & Fee Governance

| CDL | Topic | Status | Runtime file(s) | Key notes |
|-----|-------|--------|-----------------|-----------|
| CDL-047 | Treasury governance (0.15×B_e bounty cap, 0.05 burn floor, velocity alert) | **NONE** | — | All three constants ratified Phase 418; zero production runtime; `CDL_047_DEPENDENCY` token expected but absent |
| CDL-050 | Treasury ECU-governor lane (intervention ladder, lever ceilings) | **NONE** | — | Constitutional framework ratified Phase 459; CDL-051 epoch-state runtime is present but the ECU governor aspects are not implemented |

### Epoch Attribution & Settlement

| CDL | Topic | Status | Runtime file(s) | Key notes |
|-----|-------|--------|-----------------|-----------|
| CDL-081 | Hyperedge ECU attribution | **FULL** | `ilc_core/economics/epoch_attribution_settle_runtime.py` | `CDL_081_DEPENDENCY = "cdl_081_hyperedge_ecu_attribution_ratified_943.v0.1"` |
| CDL-082 | H013 emission threshold amendment (0.10→0.15) | **FULL** | `ilc_core/node/node_startup_runtime.py:61` | `H013_CHANGE_THRESHOLD = 0.15` |
| CDL-083 | H-CON-02 panel quorum ejected stake → treasury | **PARTIAL** | `ilc_core/economics/epoch_attribution_settle_runtime.py` (`evaluate_ejected_stake_vote`) | Quorum vote logic implemented. Treasury distribution path explicitly raises `NotImplementedError` (H-CON-01 CDL dependency guard). |
| CDL-084 | Provenance chain attribution | **FULL** | `ilc_core/economics/epoch_attribution_settle_runtime.py`, `ilc_core/types.py` | `CDL_084_DEPENDENCY = "cdl_084_provenance_chain_attribution_ratified_1113.v0.1"` |
| CDL-085 | Werner φ-bound (edge mint ceiling) | **FULL** | `ilc_core/types.py` (`EDGE_MINT_PHI_BOUND = Decimal("0.60")`), `epoch_attribution_settle_runtime.py` | φ-bound constant enforced in settle runtime |

### Consensus, Finality & Circuit Breakers

| CDL | Topic | Status | Runtime file(s) | Key notes |
|-----|-------|--------|-----------------|-----------|
| CDL-051 | Constitutional consensus and epoch finality | **FULL** | `ilc_core/consensus/epoch_state_runtime.py`, `finality_evaluator.py` | `CDL_051_DEPENDENCY = "cdl_051_constitutional_consensus_and_epoch_finality_443.v0.1"` |
| CDL-V3 | Quorum diversity floor | **FULL** | `ilc_core/consensus/diversity_floor_runtime.py` | `CDL_V3_RUNTIME_VERSION = "cdl_v3_diversity_floor_runtime_397.v0.1"` |
| CDL-V6 | Genesis intervention protocol (emergency brake, 3-lifetime cap) | **GOV-B** | B: This is the clearest GOV-B in the entire CDL register. The 3-lifetime cap, epoch ceiling, and audit trail are constitutional rules with no enforcement code anywhere in `ilc_core/`. There is no `genesis_intervention_runtime.py`, no `brake_invocation` counter, no audit log enforcer. At public RC, compliance relies entirely on off-chain process and Genesis's self-restraint. The whitepaper/CDL-V6 ratification evidence docs are the only artifact. **This is a real gap for post-RC hardening.** |
| CDL-045 | Operational emergency response / circuit breaker | **PARTIAL** | `ilc_core/consensus/circuit_breaker_interface.py` | `CDL_045_DEPENDENCY = "cdl_045_operational_emergency_response_408.v0.1"`. Request surface (build/verify) implemented. Auto-trigger/execution side absent. |
| CDL-068 | Topology shuffle authorization (VRF rotation) | **PARTIAL** | `ilc_core/consensus/circuit_breaker_interface.py` (diversity checks only) | Diversity floor/ceiling checks present. VRF-based shuffle rotation (`shuffle_cadence_epochs=1`, activation at ≥10 validators) has no production runtime. |

### Validator Governance

| CDL | Topic | Status | Runtime file(s) | Key notes |
|-----|-------|--------|-----------------|-----------|
| CDL-017 | Validator governance framework | **PARTIAL** | `ilc_core/consensus/circuit_breaker_interface.py` | `admit_validator` and `eject_validator` hooks explicitly `unimplemented!`. `SEC-004` (TransferCertificate epoch binding, historical validator-set resolution) also absent. |
| CDL-054 | Validator economic incentive framework (reward-pool routing) | **NONE** | — | Ratified Phase 491. Ratification artifact explicitly states "No `ilc_core/` mutation occurs in Phase 491." |
| CDL-055 | Validator staking + liveness enforcement | **FULL** | `ilc_core/validator/staking_liveness_runtime.py` | `CDL_055_DEPENDENCY = "cdl_055_ratified_496.v0.1"`. `GENESIS_STAKE_AMOUNT=400`, `LIVENESS_MISS_THRESHOLD=8`, `EQUIVOCATION_FULL_SLASH=1.0`, `LIVENESS_PENALTY_FRACTION=0.25`. |
| CDL-056 | Validator trust-tier elevation flag | **FULL** | `ilc_core/validator/trust_tier_runtime.py` | `CDL_056_DEPENDENCY = "cdl_056_ratified_501.v0.1"`. Breaks consensus dispute ties (block_proposal/equivocation/fork_choice). |
| CDL-057 | Epoch-boundary witness lane | **PARTIAL** | `ilc_core/epoch/epoch_boundary_witness_runtime.py` | `CDL_057_DEPENDENCY = "cdl_057_ratified_511.v0.1"`. Audit-only witness records. `is_blocking_authority_active()` hard-coded `return False`; `BLOCKING_AUTHORITY_DEFERRED = True`. |
| CDL-058 | Validator re-admission boundary (cooldown periods) | **FULL** | `ilc_core/validator/re_admission_runtime.py` | `CDL_058_DEPENDENCY = "cdl_058_ratified_520.v0.1"`. Cooldowns: liveness_miss=2, equivocation=12, voluntary_exit=1 (issuance epochs). |

### Identity, Admission & Sybil Resistance

| CDL | Topic | Status | Runtime file(s) | Key notes |
|-----|-------|--------|-----------------|-----------|
| CDL-040 | Admission control and identity envelope | **FULL** | `ilc_core/genesis/admission_control_bootstrap.py` | `CDL_040_DEPENDENCY = "cdl_040_ratified_393.v0.1"` |
| CDL-042 | Agent identity namespace (globally flat, key-derived `agent_id`) | **FULL** | `ilc_core/identity/agent_id_runtime.py` | `CDL_042_DEPENDENCY = "cdl_042_ratified_407.v0.1"`. `AGENT_ID_RUNTIME_VERSION = "agent_id_runtime_410.v0.1"` |
| CDL-066 | Agent sender authorization | **FULL** | Implemented via SEC-001 M-series work | CDL-066 ratification evidence confirms SEC-001 was closed pre-ratification |
| CDL-069 | PQ identity and epoch endorsement protocol | **FULL** | `ilc_core/identity/genesis_record_schema.py`, `ilc_core/epoch/epoch_endorsement_runtime.py` | Domain separator: `sha384(b"ilc-seed-commit-v1:" + identity_seed)`. DEPENDENCY `cdl_069_opens_phase_838`. Fix1 (Phase 1332 pre-gate) corrected the bare-hash bug. |
| CDL-V2 | Sybil resistance | **FULL** | `ilc_core/identity/sybil_resistance_runtime.py` | `CDL_V2_RUNTIME_VERSION = "cdl_v2_sybil_resistance_runtime_389.v0.1"` |

### Epistemic Layer & Popperian Gate

| CDL | Topic | Status | Runtime file(s) | Key notes |
|-----|-------|--------|-----------------|-----------|
| CDL-V7 | Agent decomposition criteria / Popperian gate | **FULL** | `ilc_core/consensus/popperian_gate_runtime.py` | `CDL_V7_RUNTIME_VERSION = "cdl_v7_popperian_gate_runtime_398.v0.1"`. Admissible forms: singular, bounded_existential, falsifiable_positive. `reproducibility_threshold=0.85`. |
| CDL-052 | Epistemic evaluation architecture | **FULL** | `ilc_core/epistemic/node_submission_runtime.py`, `reuse_centrality_runtime.py` | `CDL_052_DEPENDENCY = "cdl_052_ratified_466.v0.1"` |
| CDL-059 | Aesthetic panel governance | **FULL** | `ilc_core/epistemic/aesthetic_panel_runtime.py` | `CDL_059_DEPENDENCY = "cdl_059_ratified_531.v0.1"` |
| CDL-060 | Gossip centrality extension | **FULL** | `ilc_core/network/d2d/centrality_delta_gossip_runtime.py`, `passive_ecu_attribution_runtime.py` | `CDL_060_DEPENDENCY = "cdl_060_ratified_541.v0.1"` |
| CDL-072 | Bound B formula amendment | **FULL** | `ilc_core/privacy/metrics.py` | `CDL_072_DEPENDENCY = "cdl_072_bound_b_formula_amendment_ratified_846.v0.1"` |
| CDL-073 | Homoiconic bootstrap schema | **FULL** | `ilc_core/genesis/assertion_schema.py`, `ilc_core/node/node_schema_core_runtime_360.py` | `CDL_073_DEPENDENCY = "cdl_073_homoiconic_bootstrap_schema_ratified.v0.1"` |
| CDL-074 | Truth primitive runtime | **FULL** | `ilc_core/epistemic/truth_primitive_submission_runtime.py` | `CDL_074_DEPENDENCY = "cdl_074_truth_primitive_runtime_ratified.v0.1"` |
| CDL-075 | Truth primitive graph persistence | **FULL** | `ilc_core/epistemic/truth_primitive_graph_store.py` | `CDL_075_DEPENDENCY = "cdl_075_truth_primitive_graph_persistence.v0.1"` |

### Node Schema & Lifecycle

| CDL | Topic | Status | Runtime file(s) | Key notes |
|-----|-------|--------|-----------------|-----------|
| CDL-034 | Node schema core envelope and reserved fields | **FULL** | `ilc_core/node/node_schema_core_runtime_360.py` | |
| CDL-035 | Validation lifecycle and gate verdict attachment | **FULL** | `ilc_core/node/validation_lifecycle_runtime_361.py` | |
| CDL-036 | Node dissemination header and fetch contract | **FULL** | `ilc_core/node/node_dissemination_runtime_362.py` | |
| CDL-037 | Executable node descriptor and safety contract | **FULL** | `ilc_core/node/executable_descriptor_runtime_363.py` | |
| CDL-038 | Private-to-public promotion and promotion receipt | **FULL** | `ilc_core/node/promotion_continuity_runtime_364.py` | |
| CDL-046 | Timed-out amendment lifecycle | **FULL** | `ilc_core/node/timed_out_lifecycle_runtime_411.py` | `TIMED_OUT_LIFECYCLE_RUNTIME_VERSION = "timed_out_lifecycle_runtime_411.v0.1"`. `CDL_046_DEPENDENCY = "cdl_046_ratified_409.v0.1"`. |
| CDL-071 | Temporal tier reconciliation | **GOV-A** | A: `ilc_core/protocol/event_log_retention.py` (CDL-043/044) and `ilc_core/reputation/temporal_decay_runtime.py` (CDL-V1) are the code expressions — CDL-071 formally assigns all three to Tier 2 (issuance epoch) and takes constitutional precedence. No new code was written; the existing code *is* the expression. |

### Transport & P2P

| CDL | Topic | Status | Runtime file(s) | Key notes |
|-----|-------|--------|-----------------|-----------|
| CDL-039 | P2P transport baseline and topology privacy | **FULL** | `ilc_core/network/d2d/gossip_transport.py`, `gossip_peer_registry.py` | `CDL_039_DEPENDENCY = "cdl_039_ratified_379.v0.1"`. Channel ID prefix must be `{"cid", "rand"}` with ≥16 hex suffix. |
| CDL-061 | Gossip HTTP envelope | **FULL** | `ilc_core/network/d2d/gossip_transport.py`, `http_gossip_transport_runtime.py` | `CDL_061_DEPENDENCY = "cdl_061_ratified_561.v0.1"` |
| CDL-076 | Truth primitive announcement gossip | **FULL** | `ilc_core/network/d2d/truth_primitive_gossip_runtime.py` | `CDL_076_DEPENDENCY = "cdl_076_truth_primitive_announcement_gossip.v0.1"`. Channel: `"cid:truth_primitive_announced_v1_<hex>"` (Fix1 corrected prior malformed channel). |
| CDL-077 | Want/Have/Want-Block fetch protocol | **FULL** | `ilc_core/network/d2d/http_fetch_transport_runtime.py`, `truth_primitive_fetch_runtime.py` | `CDL_077_DEPENDENCY = "cdl_077_want_have_want_block_fetch.v0.1"` |
| CDL-078 | Relay incentive constitutional lock | **FULL** | `ilc_core/network/d2d/routing_reputation_runtime.py`, `truth_primitive_fetch_runtime.py` | `CDL_078_DEPENDENCY = "cdl_078_relay_incentive_constitutional_lock.v0.1"` |
| CDL-079 | HB-002 bootstrap distribution protocol | **FULL** | `ilc_core/network/d2d/bootstrap_fetch_runtime.py` | `CDL_079_DEPENDENCY = "cdl_079_hb_002_bootstrap_distribution.v0.1"` |
| CDL-080 | Star Map N-gram route index | **FULL** | `ilc_core/network/star_map/star_map_route_index_runtime.py`, `peer_fingerprint_cache.py` | `CDL_080_DEPENDENCY = "cdl_080_star_map_n_gram_route_index.v0.1"` |
| CDL-087 | Canonical fetch distribution policy | **PARTIAL** | `ilc_core/network/d2d/cdl087_observability.py`, `cdl087_serving_peer_evidence.py`, `ilc_core/graph/agent_graph_projection_runtime.py` | Observability + serving-peer evidence implemented. Public fetch serving and public sidecar/projection serving gated behind CDL-088 opening. |

### Bootstrap & Genesis Records

| CDL | Topic | Status | Runtime file(s) | Key notes |
|-----|-------|--------|-----------------|-----------|
| CDL-022 | Genesis state bundle | **FULL** | `ilc_core/genesis/genesis_state_bundle_runtime.py` | DEPENDENCY token present |
| CDL-040 | Admission control and identity envelope | **FULL** | (see Identity section) | |
| CDL-073 | Homoiconic bootstrap schema | **FULL** | (see Epistemic section) | |
| CDL-079 | HB-002 bootstrap distribution | **FULL** | (see Transport section) | |

### Storage & Numeric Representation

| CDL | Topic | Status | Runtime file(s) | Key notes |
|-----|-------|--------|-----------------|-----------|
| CDL-020 | D2 schema baseline | **FULL** | `ilc_core/schema/d2_schema_baseline_runtime.py` | |
| CDL-023 | Epoch snapshot | **FULL** | `ilc_core/epoch/epoch_snapshot_runtime.py` | |
| CDL-043 | Storage economics (adaptive pruning) | **PARTIAL** | `ilc_core/protocol/event_log_retention.py` | Retention/pruning logic exists; full adaptive pruning per CDL-043 semantics not fully wired |
| CDL-044 | Retention epochs amendment | **PARTIAL** | `ilc_core/protocol/event_log_retention.py` | Policy ratified; production epoch binding partial |
| CDL-064 | Exact numeric representation | **FULL** | `ilc_core/ledger/exact_numeric.py` | Pervasive use throughout `ilc_core/`. `decimal_to_canonical_string()` enforces `is_finite()` guard (Fix1). |

### Reputation & Governance Weight

| CDL | Topic | Status | Runtime file(s) | Key notes |
|-----|-------|--------|-----------------|-----------|
| CDL-V1 | Temporal decay | **FULL** | `ilc_core/reputation/temporal_decay_runtime.py` | `CDL_V1_RUNTIME_VERSION = "cdl_v1_temporal_decay_runtime_388.v0.1"` |
| CDL-013 | Decay-non-genesis-only governance weight | **FULL** | `ilc_core/analysis/governance_weight.py`; `ilc_core/protocol/governance_weighted_decision.py` | Decimal weight computation implemented and wired into default-off governance decision quotes; production execution remains inactive. |

### Claimability & ECU Conversion

| CDL | Topic | Status | Runtime file(s) | Key notes |
|-----|-------|--------|-----------------|-----------|
| CDL-048 | ECU mandatory conversion deadline | **PARTIAL** | `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py` | Conversion skeleton + lot accounting implemented. Public claimability activation explicitly blocked. Full public path blocked until CDL-088 ratified. |
| CDL-088 | Public claimability authority | **NOT OPENED** | — | CDL-088 has not been opened. Phase 1349 in Window 1343+ is the opening phase. `no_cdl_088_opening` enforced in release gates. |

### Early Foundations (CDL-001 through CDL-033)

> **Note on CDL-003 through CDL-010:** These were ratified as a batch in Phase 993
> (governance conflict-set closure). There are no individual ratification evidence
> files for them — they are recorded in `docs/specs/ilc_governance_conflict_set_ratification_v0.1.md`.
> All are governance/constitutional decisions; none require a direct compute-layer runtime.
>
> **CDL-016 and CDL-018** are unassigned numbers — they do not appear in the CDL register.
>
> **CDL-021** (Rust kernel port and WASM distribution) is `open` / not yet ratified.

| CDL | Topic | Ratified | Status | Runtime file(s) / notes |
|-----|-------|----------|--------|--------------------------|
| CDL-001 | Signer lineage trust root | Ph 251 | **FULL** | `ilc_core/security/signer_lineage_runtime.py` |
| CDL-002 | Key compromise response | Ph 251 | **FULL** | `ilc_core/security/key_compromise_runtime.py` |
| CDL-003 | Founder fade-out mechanics (`trigger-based sunset`) | Ph 993 | **GOV-C** | A: `genesis_accrual_governor.py` (`THETA_HARD`, `cap_blocked` flag) is the runtime expression of the founder accumulation cap; CDL-V6 sunset semantics bound the override authority. B: The specific trigger conditions (what fires the sunset) are in governance docs only — no enforcement code. |
| CDL-004 | Founder operational caps (`hard caps + reporting`) | Ph 993 | **GOV-C** | A: `genesis_accrual_governor.py` (`THETA_HARD=0.05`, `cap_blocked` stop flag) enforces the hard cap; CDL-055/056 enforce non-genesis validator caps. B: "Public reporting" obligation is governance/docs-only, no reporting runtime. |
| CDL-005 | Issuance/cap constitutional wording (`cap+trajectory+guardrails`) | Ph 993 | **GOV-C** | A: This CDL is the constitutional precondition for CDL-025 through CDL-031; its wording mandates `cap+trajectory+guardrails` which those CDLs operationalise. `commit_epoch_emission_runtime.py` is the structural placeholder. B: The production emission engine (CDL-025–031) does not yet exist — so the "guardrails" are spec-only. |
| CDL-006 | Governance override/challenge process (`multi-body checks`) | Ph 993 | **GOV-C** | A: CDL-V3 `diversity_floor_runtime.py` is the code expression of multi-body quorum; CDL-045 `circuit_breaker_interface.py` requires CDL-V3 quorum to assemble a challenge request. B: The "challenge node spec" and formal audit path are not yet built. |
| CDL-007 | Rollback resistance baseline | Ph 251 | **FULL** | `ilc_core/security/rollback_resistance_runtime.py` |
| CDL-008 | Layer boundary: fixed core vs policy-loaded layers (`split-by-domain`) | Ph 993 | **GOV-C** | A: The entire `ilc_core/` module structure is the primary code expression; `ilc_core/rc/package_profiles.py` + ADR-0026 enforce the protocol/harness/policy split; `PUBLIC_RC_EXCLUDE` marker system enforces the public/private layer boundary. B: Architecture narrative in `docs/architecture/`. |
| CDL-009 | Fork legitimacy/user signaling (`signature-badge+eligibility rules`) | Ph 993 | **GOV-C** | A: `bootstrap_fetch_runtime.py` ML-DSA-65 signature verification is the "signature-badge" enforcement; CDL-073 homoiconic bootstrap + Genesis lineage integrity is the "eligibility rules" expression. B: Client-facing fork-signaling UX is not yet built. |
| CDL-010 | Pseudonymity/accountability balance (`pseudonymous attestations`) | Ph 993 | **GOV-C** | A: CDL-V2 `sybil_resistance_runtime.py` and `agent_id_runtime.py` (key-derived IDs without identity disclosure) are the code expressions. B: Communications policy and incident-response policy are governance docs/process. |
| CDL-011 | Balanced composite node value | Ph 215 | **FULL** | `ilc_core/analysis/node_value_kernel.py` |
| CDL-012 | Usage + freshness utility flow | Ph 215 | **FULL** | `ilc_core/analysis/utility_flow_rewards.py` |
| CDL-013 | Governance weight (see Reputation section) | Ph 215 | **FULL** | `ilc_core/analysis/governance_weight.py`; `ilc_core/protocol/governance_weighted_decision.py` — Decimal weight computation wired into default-off governance decision quotes; production execution inactive |
| CDL-014 | Counterfactual path-lift | Ph 215 | **FULL** | `ilc_core/analysis/path_lift_counterfactual.py` |
| CDL-015 | Strict phase gate | Ph 215 | **GOV-A** | A: `tools/check_sensitive_runtime_coding_taboos.py`, pre-commit hooks (`tools/pre-commit`), code health tests (`tests/test_code_health.py`), and all phase gate scripts in `tools/` are the direct code expressions of this decision. These are tooling, not `ilc_core/` modules, but they are real enforced code. |
| CDL-016 | *(unassigned — number not in register)* | — | — | — |
| CDL-017 | Validator governance framework (see Validator section) | Ph 765 | **PARTIAL** | `ilc_core/consensus/circuit_breaker_interface.py`; `admit_validator`/`eject_validator` stubs |
| CDL-018 | *(unassigned — number not in register)* | — | — | — |
| CDL-019 | Multiplier governance surface | Ph 268 | **PARTIAL** | `ilc_core/consensus/governance.py` — governed constant present; invariant-floor enforcement not fully production-coded |
| CDL-021 | Rust kernel port and WASM distribution | **OPEN** (not ratified) | — | Milestone-triggered Rust port; no ratification yet |
| CDL-024 | Wire transport | Ph 329 | **FULL** | `ilc_core/network/wire_transport_runtime.py` |
| CDL-032 | CLI-first agent SDK interface contract | Ph 253 | **FULL** | `ilc_core/cli/` suite |
| CDL-033 | OpenClaw skill publication contract | Ph 291 | **PARTIAL** | `ilc_core/rc/package_profiles.py` (PROFILE_OPENCLAW_SKILL_LOCAL/CLAIMABLE); public publication blocked |
| CDL-049 | Bounded existential alignment | Ph 428 | **GOV-A** | A: `ilc_core/consensus/popperian_gate_runtime.py` — `_ADMISSIBLE_CLAIM_FORMS` vocabulary was directly changed from `existential` → `bounded_existential` as the immediate code consequence of this CDL. This is a small but real code change, not just a governance doc. |
| CDL-063 | ECU directed commission (earmark semantics) | Ph 627 | **FULL** | `ilc_core/ledger/ecu_active_layer_runtime.py` |
| CDL-065 | Coupling invariants governance lock | Ph 663 | **FULL** | `ilc_core/ledger/ecu_ilc_lifecycle_runtime.py` (`coupling_invariants_diagnostic`) |

### Release & Packaging

| CDL | Topic | Status | Runtime file(s) | Key notes |
|-----|-------|--------|-----------------|-----------|
| CDL-086 | Public launch packaging blocker | **PARTIAL** | `ilc_core/rc/` suite | Governance precondition ratified; public acts still gated on counsel/IP/signing |
| CDL-087 | Canonical fetch distribution policy | (see Transport) | | |

### V-Series CDLs — Complete Reference

> V-series CDLs (CDL-V1 through CDL-V7) were ratified in Phases 330–335 as a vulnerability/
> constitutional hardening cluster. Each entry below is the single authoritative reference for
> that CDL. Cross-references in domain sections (Consensus, Identity, Epistemic, Reputation)
> point back here.

| CDL | Topic | Ratified | Status | Runtime file(s) | A/B/C notes |
|-----|-------|----------|--------|-----------------|-------------|
| CDL-V1 | Temporal decay for reuse centrality | Ph 330 | **FULL** | `ilc_core/reputation/temporal_decay_runtime.py` | A: `CDL_V1_RUNTIME_VERSION = "cdl_v1_temporal_decay_runtime_388.v0.1"`. Exponential half-life decay on reuse centrality scores. CDL-071 formally assigns this to Tier 2. |
| CDL-V2 | Sybil resistance (hybrid heuristic) | Ph 331 | **FULL** | `ilc_core/identity/sybil_resistance_runtime.py` | A: `CDL_V2_RUNTIME_VERSION = "cdl_v2_sybil_resistance_runtime_389.v0.1"`. Enforces identity-stake cost and participation heuristics. Also expresses CDL-010 pseudonymous attestation policy. |
| CDL-V3 | Ratification quorum diversity floor | Ph 332 | **FULL** | `ilc_core/consensus/diversity_floor_runtime.py` | A: `CDL_V3_RUNTIME_VERSION = "cdl_v3_diversity_floor_runtime_397.v0.1"`. `compute_max_cluster_share()`, `meets_distinct_cluster_floor()`, `compute_diversity_floor_penalty()`. Also expresses CDL-006 multi-body checks at the quorum layer. |
| CDL-V4 | Minority dissent, appeal, and CDL reopening protocol | Ph 334 | **GOV-B** | — | B: This is a pure governance procedure — how a minority dissent is filed, what threshold triggers a formal reopening, and how Genesis is the final arbiter. There is no `reopening_runtime.py` and none is required. The process is followed by humans. Cite: CDL-V4 ratification evidence + governance process docs. |
| CDL-V5 | Schema epoch markers and cross-version translation protocol | Ph 333 | **GOV-A** | `ilc_core/schema/d2_schema_baseline_runtime.py` (CDL-020), `ilc_core/epoch/epoch_snapshot_runtime.py` (CDL-023), `ilc_core/reputation/temporal_decay_runtime.py` (CDL-V1) | A: All three runtimes already carry epoch markers and implement the translation principle CDL-V5 constitutionalises. CDL-V5 wrote no new code — the existing code *is* the expression. Constitutional precedence over tiering questions. |
| CDL-V6 | Genesis intervention protocol (emergency brake, 3-lifetime cap, audit trail) | Ph 334 | **GOV-B** | — | B: The clearest GOV-B in the register. Three constitutional rules — max 1 invocation per proposal, max 3 lifetime invocations, sunset under Phase 597 epoch ceiling — have zero enforcement code. No `genesis_intervention_runtime.py`, no invocation counter, no audit log enforcer exists in `ilc_core/`. Compliance at public RC is entirely off-chain. **Real gap for post-RC hardening** — the whitepaper and CDL-V6 ratification evidence are the only artifacts. |
| CDL-V7 | Agent decomposition criteria / Popperian gate | Ph 335 | **FULL** | `ilc_core/consensus/popperian_gate_runtime.py` | A: `CDL_V7_RUNTIME_VERSION = "cdl_v7_popperian_gate_runtime_398.v0.1"`. Admissible forms: `singular`, `bounded_existential` (narrowed by CDL-049), `falsifiable_positive`. `reproducibility_threshold=0.85`. |

**V-series summary:** V1, V2, V3, V7 are fully implemented. V5 is GOV-A (existing code expresses it). V4 is intentionally GOV-B (procedural governance). V6 is a real gap — GOV-B today, but the 3-lifetime enforcement and audit trail should become GOV-A in a post-public-RC hardening window.

---

### Not Ratified / Placeholders

| CDL | Note |
|-----|------|
| CDL-053 | Planning placeholder for Werner/long-tail research; never opened |
| CDL-062 | Sovereign substrate research lane (Mysticeti evaluation); never formally ratified; Option B authorized ~Phase 814 but no production code |
| CDL-070 | Deferred PQ ceremony planning item; never opened |
| CDL-088 | Not yet opened (see Claimability section) |

---

## ADR Implementation Map

| ADR # | Topic | Status | Runtime file(s) | Gap notes |
|-------|-------|--------|-----------------|-----------|
| ADR-0001 | Canonical encoding and MCP MVP | **FULL** | `ilc_core/mcp/`, `ilc_core/encoding/` | |
| ADR-0002 | NDJSON bundle transport | **FULL** | `ilc_core/protocol/ndjson_bundle.py` | |
| ADR-0003 | Star Map N-gram route index | **FULL** | `ilc_core/network/star_map/route_index.py` | |
| ADR-0004 | Genesis primitive commit epoch | **PARTIAL** | `ilc_core/genesis/commit_epoch_emission_runtime.py` | Production emission NOT authorized; devnet only. Production minting engine does not exist. |
| ADR-0005 | Star Map observational feeds | **PARTIAL** | Partially in gossip/fetch stack | H-013 feeds/gossip wiring and sealed-sender ADR-0034 work required |
| ADR-0006 | EVE canonical capsule integrity | **FULL** | `ilc_core/eve/capsule.py`, `capsule_builder.py` | |
| ADR-0007 | Constitutional baseline and ratification process | **GOV** | — | Framework only; no runtime object |
| ADR-0008 | Node usefulness vs governance weight and Genesis dilution | **PARTIAL** | `ilc_core/analysis/genesis_accrual_governor.py`, `governance_weight.py`, `node_value_kernel.py` | Cap governor fully implemented. Live governance-weight aggregation feeding decisions absent. |
| ADR-0009 | Four-layer protocol native bundle distribution | **NONE** | — | Not accepted; multi-CBOR-runtime participation is post-launch |
| ADR-0010 | Communication plane separation | **NONE** | — | Not accepted; plane separation partial via D2d/MCP but not formally ratified |
| ADR-0011 | Native P2P transport baseline | **FULL** | `ilc_core/network/d2d/` suite | |
| ADR-0012 | ECU/ILC graph coupling and anti-reflexivity | **FULL** | `ilc_core/ledger/ecu_ilc_lifecycle_runtime.py` | |
| ADR-0013 | External payment boundary and third-party independence | **NONE** | — | Not accepted; external payment boundary not formally implemented |
| ADR-0014 | Identity, Sybil, and admission control envelope | **PARTIAL** | CDL-040/042/V2 cover pieces | ADR-0014 itself not formally closed; identity envelope scope broader than what CDLs implement |
| ADR-0015 | Node transfer economics (transfer tax, cooling period) | **NONE** | — | Amended-accept disposition; numeric calibration and production runtime deferred. Leasehold/reversion requires simulation evidence. |
| ADR-0016 | Productive ECU expansion bounty mechanism | **NONE** | — | CDL-047 covers bounty cap; ECU credit creation runtime (Gap 12) does not exist |
| ADR-0017 | Post-issuance economic transition and late-economy design | **NONE** | — | Explicitly long-range/post-launch; requires CDL-025-031 production stack first |
| ADR-0019 | Graph-native governance compilation boundary | **PARTIAL** | `ilc_core/rc/atlas_graph_discipline.py` | ATLAS-G-006 through ATLAS-G-010 work in progress |
| ADR-0020 | Knowledge-node-first design principle | **PARTIAL** | `ilc_core/graph/` | Migration discipline accepted; not all constants/bootstrap artifacts migrated to graph-native nodes |
| ADR-0021 | Epistemic finality claims | **FULL** | `ilc_core/consensus/finality_evaluator.py` | Implemented through CDL-051 |
| ADR-0022 | Local-first private use and publication-bound economics | **FULL** | CDL-038 + Phase 730 hardening | Explicit promotion and public-anchor/private-interior model implemented |
| ADR-0023 | Multi-layer quality signal architecture | **PARTIAL** | CDL-059 (aesthetic), CDL-060 (centrality), novelty runtime | Multi-hop and long-horizon tuning deferred |
| ADR-0024 | Agent skills infrastructure | **PARTIAL** | `ilc_core/rc/package_profiles.py` | OpenClaw/NemoClaw skill packaging (Gap 14) underway; ADR-0024 remains Proposed |
| ADR-0025 | D2d HTTP gossip transport binding | **FULL** | `ilc_core/network/d2d/http_gossip_transport_runtime.py` | |
| ADR-0026 | Protocol vs harness product boundary | **FULL** | `ilc_core/rc/package_profiles.py` | |
| ADR-0027 | Canonical self-describing bootstrap and receipt boundary | **FULL** | Bootstrap fetch runtime, claimability receipt verifier | |
| ADR-0028 | Settlement substrate graduation and governance route (Option B: Mysticeti) | **PARTIAL** | `ilc_consensus/` (Rust crate — M-series complete) | M-001–M-022 complete. `ilc_consensus/` contains full ILC-native DAG-BFT crate (BLS12-381, QUIC, LMDB). 4-validator M-009 testnet config exists. HIGH-002 fixed (Phase 842). CDL-067 ratified (Phase 709). Option B selected (Phase 814). Gap: `ilc_core/` has no production gRPC/QUIC bridge to `ilc_consensus/` (only `tools/testbed/` stubs). HIGH-001 sender-identity leakage open. Multi-operator key ceremony not done. External audit not engaged. Production wiring routed to Window 1343–1368 Phases 1358–1360. |
| ADR-0029 | Hypergraph substrate | **FULL** | `ilc_core/graph/` suite | |
| ADR-0030 | Node embedding substrate and content typing | **PARTIAL** | `ilc_core/graph/`, encoding modules | |
| ADR-0031 | Subgraph homomorphism query contract | **PARTIAL** | `ilc_core/graph/sidecar_query_runtime.py` | Many query types raise `NotImplementedError`. Required for graph-native sidecar suite completeness. |
| ADR-0032 | Temporal hypergraph epoch-stamped incidence | **FULL** | `ilc_core/graph/` temporal epoch stamping | |
| ADR-0033 | Star Map homoiconic epistemological entity | **FULL** | `ilc_core/network/star_map/route_index.py` + homoiconic node integration | |
| ADR-0034 | D2d sealed sender mechanism | **FULL** | `ilc_core/network/d2d/spectral_beacon.py` (`H013_SEALED_SPECTRAL_BEACON_VERSION`) | |
| ADR-0035 | Homoiconic type definition system | **NONE** | — | Draft/direction accepted; "CDL required before any runtime change." Post-launch governance work. |
| ADR-0036 | Operational release key Genesis binding | **PARTIAL** | `ilc_core/rc/release_keys_envelopes_generation_gate.py` | Gate tooling present. Actual release key generation completed Phase 1335. Signing authorization required for v0.2 ceremony (Phase 1340). |
| ADR-0037 | Genesis canonical lineage contract | **PARTIAL** | Gate tooling (`ilc_core/rc/`) | Lineage contract defined; signing ceremony deferred to Phase 1340. |

---

## Genesis 5% Accumulation — Detailed Map

**This is the most frequently asked-about provision.** Here is the precise breakdown:

| Layer | What it covers | CDL | Implementation | Status |
|-------|---------------|-----|---------------|--------|
| Total supply ceiling | C_max — no more than this much ILC can ever exist | CDL-026 | Not encoded as enforceable runtime constant | **NONE** |
| Halving schedule | Emission decays every H=48 issuance epochs | CDL-027 | No production halving runtime | **NONE** |
| Per-epoch allocation split | 80% performer / 15% auditor / 5% genesis per epoch | CDL-029 | **Per-epoch distributor does NOT exist** | **NONE** |
| Genesis accumulation cap | Genesis total accrual ≤ 5% of cumulative issuance (θ_hard=0.05) | CDL-029 + ADR-0008 | `ilc_core/analysis/genesis_accrual_governor.py` — `THETA_HARD=Decimal("0.05")`, taper logic, `cap_blocked` flag | **FULL** |
| Fee-burn split | 10% of per-epoch fees → genesis/burn | CDL-028 | Not implemented | **NONE** |
| Treasury bounty cap | Per-epoch bounty cap ≤ 0.15 × B_e | CDL-047 | Not implemented | **NONE** |

**Bottom line on Genesis 5%:** The governance and cap enforcement are specified and the governor is coded. The actual per-epoch distribution engine that credits 5% of each epoch's issuance to Genesis does not exist. Neither does the emission engine it would plug into.

---

## Summary: Gaps by Milestone Target

### Required for Soft RC (private VPS mining — earliest)
1. **CDL-025/027 issuance schedule engine** — no production minting runtime; ILC cannot actually be minted
2. **CDL-029 per-epoch allocation distributor** — 80/15/5 split has no code; even if minting existed, Genesis would not receive its 5%
3. **CDL-017 validator admission/ejection hooks** — non-genesis validators cannot join/leave the network live
4. **CDL-068 topology shuffle VRF** — validator set rotation not enforced
5. **ADR-0028 sovereign substrate (Mysticeti)** — Python HTTP transport is explicitly devnet-only; sustained production consensus requires this

### Required for Full Public RC (Phase 1355 gate)
All soft RC items plus:
6. **CDL-028 fee-burn runtime** — fee-burn split has no code
7. **CDL-047 treasury governance runtime** — bounty cap, burn floor, velocity alert have no code
8. **CDL-083 ejected stake treasury distribution** — raises `NotImplementedError`
9. **CDL-054 validator reward-pool routing** — no production runtime
10. **CDL-088** — must be opened and ratified (Window 1343+, Phases 1349-1351)
11. **Identity bootstrap CDL** — must be ratified (Window 1343+, Phases 1346-1348)
12. **Replay/nullifier policy** — must be closed (Window 1343+, Phase 1352)
13. **Legacy `/v1/public/*` FastAPI cleanup** — Phase 1353
14. **Counsel clearance** — Phase 1354
15. **ADR-0031 sidecar query completeness** — many `NotImplementedError` query types

### Post-Launch (can defer)
- ADR-0035 homoiconic type definition system (CDL required first)
- ADR-0015 node transfer economics (transfer tax, cooling period, leasehold)
- ADR-0016/0017 productive ECU expansion bounty + post-issuance economics
- CDL-030 ECU price clamp
- CDL-031 dynamic ranking policy
- CDL-070 PQ ceremony
- CDL-062 Option B Mysticeti (if interim Python transport suffices for soft RC)
- CDL-V6 Genesis intervention enforcement code (currently off-chain process only)
