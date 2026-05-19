# ILC Window 1369-1390: Candidate Phase Grouping

**Author:** Claude Code (local planning synthesis)
**Date:** 2026-05-16
**Baseline:** Window 1343-1368 CLOSED with carry-forward at Phase 1368 (`390e0be4`),
`window_1343_1368_closed_phase_1368.v0.1`. Capsule v5.57 current (Phase 1365).
CDL-089 ratified Phase 1364. CDL-088 pre-reserved (unopened). Next fresh CDL: CDL-090.
**Planning note:** This is a candidate grouping, not a locked sequence. Phase 1369 sequence
lock publishes the locked order. SENSITIVE phases require explicit human GO. NON-SENSITIVE
phases may proceed after guidance doc approval.

---

## 1. Window Identity and Scope

Window 1369-1390 is the **public claimability governance, CDL-006/009 completeness,
external audit, and full public RC activation window**. Its primary obligations are:

1. **Identity bootstrap CDL (CDL-090)** — no ADR or CDL currently governs the
   non-custodial identity-seed path, ceremony modes, secure output target, or
   Genesis-rooted birth attestation linkage. This CDL is a prerequisite for any
   public identity-creation or claim-seed flow.
2. **Agent birth attestation ADR (ADR-0038)** — Genesis-rooted identity-origin proof;
   `agent_id` bound to signed Genesis/Atlas lineage anchor; non-custodial default; no
  private graph content as entropy. Prerequisite for CDL-090 deliberation.
3. **CDL-088 opening, deliberation, and ratification** — CDL-088 is pre-reserved for
   public claimability authority. It governs bounded public claimability, reciprocal
   scoring (if included), and ECU-escrow admission (if included). Must NOT be opened
   without explicit `GO Phase 1374`.
4. **Replay/nullifier + duplicate-claim registry policy** — no nullifier construction
   policy or epoch-bounded expiry rule currently exists for the claim endpoint surface.
   Required before any live claim endpoint activation.
5. **Legacy FastAPI route cleanup** — legacy `/v1/public/*` routes flagged Phase 1301
   remain in the codebase. Must be removed or replaced before public RC.
6. **ADR-0031 sidecar query runtime completeness** — `sidecar_query_runtime.py` raises
   `NotImplementedError` for all query types not yet implemented. Required for sidecar
   completeness before public RC.
7. **CDL-048 ECU-to-ILC dry-run wiring and activation** — sweeper runtime wire-up
   in gate-closed state (Phase 1380), then live activation after Phase 1387 hardening
   gate (Phase 1388).
8. **CDL-006 challenge node spec and runtime** — CDL-006 policy ratified Phase 993,
   multi-body check selected. Phase 1381 completed the spec and stub; Phase 1382
   completed the runtime helper and tests without public activation.
9. **CDL-009 fork legitimacy UX** — CDL-009 policy ratified Phase 993,
   signature-badge+eligibility-rules selected, but UX surface was never built.
   Governance completeness prerequisite.
10. **Security review scope record** — M-022 open item #6. Records AI-assisted
    structured review plus open source community contribution path; commercial audit firm
    engagement is not required. Covers `ilc_consensus/` BFT safety, `ilc_core/`
    economic surfaces, and HIGH-001 defense review. Project-authority security disposition
    is required at Phase 1387 for every known HIGH finding.
11. **TLA+ SafetyNoDualCert disposition** — M-022 open item #1. Phase 1385
    records `tla_plus_safetynodualcert_disposed_phase_1385` and
    `safetynodualcert_deferred_with_authority_phase_1385`; Phase 1385a closes the
    deferral with Spec D and `safetynodualcert_spec_d_proven_epoch_checkpoint`.
12. **Genesis validator bootstrap record** — M-022 open item #7. Phase 1386 records
    a Genesis-controlled single-custodian pre-RC/testnet exception. Production
    split custody remains required before mainnet launch, not before public RC in
    Window 1369-1390.
13. **Production TLS gRPC proof (Phase 1386a)** — COMPLETE. Phase 1360 proved gRPC
    via insecure channel; Phase 1386a proves the TLS `build_secure_grpc_read_stub()`
    path against a TLS-configured validator endpoint, verifies epoch-0 sentinel
    reconciliation, and closes hardening item 7.
14. **Validator endpoint registry ADR (Phase 1386b)** — COMPLETE by ADR-0039.
    **Persistent QUIC connectivity proof (Phase 1386c)** remains next; durable
    per-topology-epoch sessions are not yet proven.
15. **Phase 1369 Fix1 — numeric hardening pass** — 8 runtime hardening items from the
    Window 1343-1368 joint audit are carried forward. Items 1-6 and 8 (Decimal magnitude
    escape, genesis counter TOCTOU, governance weight bounds, audit log non-atomic,
    LMDB batch-cap starvation, LMDB dry_run write lock, `_decimal_to_string` dead branch)
    should be addressed in a Phase 1369 Fix1 NON-SENSITIVE numeric hardening pass drafted
    and authorized after the sequence lock. Item 7 (`get_epoch_chain` post-materialization
    bound) pairs with Phase 1386a.
16. **Accepted ADR/CDL coverage and public-economics admission firewall (Phase 1387a)** —
    ADR-0022 and the node-schema canon allow private and semi-private work, but they do
    not allow private graph work to create protocol ECU, public reputation, public settlement
    rights, public claimability, or public corroboration. Historical "shadow economics"
    language is clarified as operator-local advisory scoring only, not ECU generation.
    Current economics settlement helpers are generic and rely on caller-supplied admissible
    events. Before any public RC activation, Phase 1387a must produce a repo-derived accepted
    ADR/CDL coverage matrix and implement or verify a fail-closed event-construction boundary
    proving public economics events can only be constructed from public knowledge nodes with
    public graph admission evidence.

**Character of this window:** governance-heavy with two CDL tracks (CDL-090 and CDL-088),
external process tracks (audit, key ceremony), runtime tracks (CDL-006, CDL-009, CDL-048,
sidecar, FastAPI), and a hard Phase 1389 public RC gate that fails closed if any
predecessor remains open or if Phase 1387a records any unresolved accepted ADR/CDL
implementation gap that blocks public RC.

**Tail-slot policy:** Phase 1389 is the explicit full public RC milestone gate.
`result=public_claimability_activated` may appear for the first time in Phase 1389.
It fails closed if ANY predecessor phase is open. Phase 1390 is the window closure.
No tail-slot conditional phases follow Phase 1390.

---

## 2. Baseline and Inheritance

### Ratified CDL chain (current through Window 1343-1368)

| CDL | Scope | Status |
|-----|-------|--------|
| CDL-051 | Constitutional consensus and epoch finality | ratified |
| CDL-073 | Homoiconic bootstrap schema | ratified |
| CDL-074 | Truth primitive runtime | ratified |
| CDL-075 | Truth primitive graph persistence | ratified |
| CDL-076 | L1 announcement gossip | ratified |
| CDL-077 | L2 WANT-HAVE/WANT-BLOCK fetch; rate limiting | ratified |
| CDL-078 | L3 relay incentives / routing reputation | ratified |
| CDL-079 | L3 star.map N-gram route index | ratified |
| CDL-080 | L3 spectral routing | ratified |
| CDL-081 | Hyperedge ECU attribution | ratified |
| CDL-083 | H-CON-02 panel quorum ejected stake | ratified |
| CDL-084 | Provenance decay α=0.45 / max depth=3 | ratified |
| CDL-085 | Werner φ-bound `EDGE_MINT_PHI_BOUND = Decimal("0.60")` | ratified |
| CDL-086 | Public-launch packaging blocker | ratified |
| CDL-087 | Canonical fetch distribution policy | ratified Phase 1278 Fix1 |
| CDL-088 | Public claimability authority | RESERVED — do not open without explicit `GO Phase 1374` |
| CDL-089 | Blocking-authority activation vehicle (CDL-057 epoch-boundary witness) | ratified Phase 1364 |

**Next fresh CDL number: CDL-090** (for identity bootstrap CDL, Phase 1371)

### Active runtime chain (inherited through Phase 1368)

| Module | Version token |
|--------|---------------|
| Epoch attribution settle | `epoch_attribution_settle_runtime_1210.v0.7` |
| HTTP fetch transport | `http_fetch_transport_runtime_1212.v0.2` |
| Persistent fetch rate limiter | `persistent_fetch_rate_limiter_runtime_1202.v0.1` |
| Agent graph projection | `agent_graph_projection_runtime_1229.v0.1` |
| Public receipt | `public_receipt_runtime_651.v0.1` |
| CDL-V6 genesis intervention | `cdl_v6_genesis_intervention_runtime_phase_1355.v0.1` |
| CDL-013 governance weight integration | `cdl_013_governance_weight_live_integration_phase_1356.v0.1` |
| Reputation H11 float-kill | `reputation_runtime_h11_float_kill_phase_1357.v0.1` |
| Production bridge (gRPC read adapter) | `ilc_core_consensus_grpc_read_adapter_phase_1358.v0.1` |
| HIGH-001 log redaction | `high_001_log_redaction_runtime_phase_1359.v0.1` |
| CDL-043/044 adaptive pruning | `cdl_043_adaptive_pruning_threshold_runtime_phase_1361.v0.1` |
| Epoch boundary witness (blocking authority active) | `blocking_authority_ratified_phase_1364.v0.1` |

### Immutable anchors (unchanged)

| Artifact | Value |
|----------|-------|
| Genesis v0.1 signed root envelope hash | `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c` |
| Immutable diagnostic SHA | `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56` |
| Genesis v0.2 candidate | 41-node / 73-edge; unsigned; signing deferred |

### Inherited carry-forward from Window 1343-1368

| Token | Source | Window 1369 obligation |
|-------|--------|----------------------|
| `production_minting_activation_deferred_phase_1368` | Phase 1368 | Record disposition in Phase 1369 sequence lock; no activation this window unless Phase 1389 passes and authorizes |
| `soft_rc_eligible=false_with_blockers` | Phase 1366 | Inherited status; not re-gated in Phase 1369; re-gate is Phase 1389 |
| `legacy_public_labeled_fastapi_routes_carry_forward_phase_1301` | Phase 1301 | Phase 1378 removes or replaces all flagged routes |
| `grpc_end_to_end_python_to_rust_proven_phase_1360` scope qualifier | Phase 1360 Fix2a | Production TLS path now closed by Phase 1386a; Phase 1360 remains plaintext/insecure-channel evidence only |
| `phase_1360_fix2a_proof_scope_narrowed_injected_checkpoint_only` | Phase 1360 Fix2a | Durable peer-to-peer sessions route to Phase 1386c |
| 8 runtime hardening items (joint audit) | Window 1343-1368 audit | Phase 1369 Fix1 (items 1-6, 8); Phase 1386a (item 7) — see §4 |
| `public_only_economics_rule_verified_in_canon_not_enforced_at_event_construction_boundary` | ADR-0022 / node schema audit | Phase 1387a produces accepted ADR/CDL coverage matrix and public-economics admission firewall |

---

## 3. Track Inventory

### 3.1 Constitutionally obligated (firm this window)

- `agent_birth_attestation_adr_required_before_identity_bootstrap_cdl` — Phase 1370 delivers ADR-0038
- `identity_bootstrap_cdl_required_before_any_public_identity_artifact` — CDL-090 opening (Phase 1371), prelock (Phase 1372), ratification (Phase 1373)
- `cdl_088_required_before_public_claimability_activation` — CDL-088 opening (Phase 1374), prelock (Phase 1375), ratification (Phase 1376); explicit `GO Phase 1374` required
- `replay_nullifier_policy_required_before_live_claim_endpoint` — Phase 1377 delivers policy ADR or CDL
- `legacy_public_labeled_fastapi_routes_carry_forward_phase_1301` — Phase 1378 removes/replaces
- `adr_0031_sidecar_query_completeness_required` — Phase 1379 closes all `NotImplementedError`
- `cdl_048_ecl_to_ilc_dry_run_wiring_required` — Phase 1380 wires in gate-closed state; Phase 1388 activates
- `cdl_006_challenge_node_spec_phase_1381` — Phase 1381 completed spec + stub; Phase 1382 still owns production runtime + tests
- `cdl_009_fork_legitimacy_ux_unbuilt_phase_993` — Phase 1383 delivers badge schema + eligibility + CLI surface
- `cdl_048_activation_and_counsel_clearance_required_before_phase_1389` — Phase 1388
- `public_economics_requires_public_node_admission_verified_phase_1387a` — Phase 1387a
  verifies no private or semi-private node can construct public ECU, public reputation,
  public settlement, or public claimability events
- `accepted_adr_cdl_runtime_coverage_matrix_phase_1387a` — Phase 1387a classifies every
  accepted ADR and ratified CDL as implemented, covered by a phase before public RC,
  documentation/governance-only, explicitly deferred outside public RC, or a blocker
- `public_rc_gate_phase_1389_required_all_six_blockers_closed` — Phase 1389 re-executes Phase 1336 gate

### 3.2 Deferred governance (scheduled this window; some items feed Phase 1387/1389)

- Security review scope record — Phase 1384; project-authority security disposition required at Phase 1387
- TLA+ SafetyNoDualCert disposition — Phase 1385
- Genesis validator bootstrap exception record — Phase 1386; production split custody is a mainnet-launch carry-forward
- Production TLS gRPC path proof — COMPLETE Phase 1386a; also verifies epoch-0 sentinel reconciliation
- Validator endpoint registry ADR — Phase 1386b
- Persistent QUIC connectivity proof — Phase 1386c
- Accepted ADR/CDL public-RC coverage audit and public-economics admission firewall — Phase 1387a

### 3.3 Simulation-conditional

None in this window. All items are governance or implementation tracks. No CDL ratification in this window is gated on simulation evidence.

---

## 4. Runtime Hardening Carry-Forward Disposition (Window 1343-1368 Joint Audit)

The following 8 items were surfaced in the Window 1343-1368 joint Codex + Claude Code
audit and must be explicitly scheduled or deferred with authority before Phase 1369
closes the sequence lock.

| Sev | Finding | Location | Window 1369 assignment |
|-----|---------|----------|------------------------|
| M | Huge-finite `Decimal` values escape quantize validation; input boundary rejects floats and non-finite values but does not cap magnitude/exponent | `fee_burn_split_runtime.py:87`, `allocation_distributor_runtime.py:197`, `treasury_governance_runtime.py:107`, `ecu_price_clamp_runtime.py:105`, `validator_reward_pool_routing_runtime.py:168`, `epoch_attribution_settle_runtime.py:61` | **Phase 1369 Fix1** — NON-SENSITIVE numeric hardening pass; add magnitude cap `if d.adjusted() > 28: raise ValueError("invalid_amount_magnitude")` at all 6 boundaries |
| M | Genesis intervention counter TOCTOU: read/evaluate/write not atomic; concurrent calls could push `lifetime_invocations` past 3; blast radius limited to extra audit log entries | `genesis_intervention_runtime.py:427` | **Phase 1369 Fix1** — add file-lock wrapper around full read/evaluate/write in `record_genesis_intervention_guardrail_invocation` |
| M | Governance weight accepts unbounded `quality_score`, `base_weight`, `contribution_bonus`, `genesis_baseline_weight`; one hostile input dominates normalized shares; contract unclear | `governance_weight.py:73,109,198` | **Phase 1369 Fix1** — document pre-normalization contract or add bounds (at minimum `quality_score <= 1`) |
| L/M | Genesis audit log append non-atomic; concurrent writers can interleave log lines | `genesis_intervention_runtime.py:321` | **Phase 1369 Fix1** — pair with counter-lock fix; shared lock covers both |
| L/M | LMDB pruning batch cap applies to total cursor entries scanned, not eligible tier-2 records; a large prefix of non-prunable records starves pruning | `lmdb_graph_pruning_runtime.py:154` | **Phase 1369 Fix1** — low priority; adjust cap semantics or add prunable-record counter |
| L | LMDB pruning opens write transaction even when `dry_run=True`; no data written but exclusive write lock acquired unnecessarily | `lmdb_graph_pruning_runtime.py:154` | **Phase 1369 Fix1** — trivial: open read transaction when `dry_run=True` |
| L | `get_epoch_chain()` materializes `records = list(...)` before bounding by `max_epoch_chain_records`; receive-size/channel limit should be added for production | `production_bridge.py:526` | **CLOSED Phase 1386a** — added channel receive-size limit and bounded response iteration |
| L | `_decimal_to_string()` dead branch: both branches return the same expression; no behavioral impact | Seven epoch/economic runtimes | **Phase 1369 Fix1** — trivial cleanup; bundle with other hardening |

### 4.1 Public-Only Economics Admission Gap

The private-shard canon is already explicit: private and semi-private graph work may exist,
but it does not create protocol ECU, public reputation, public settlement rights, public
corroboration, or public claimability until it is deliberately promoted or admitted into
the public graph. Historical "shadow economics" phrasing means operator-local advisory
scoring only; it is not a protocol economic category and does not authorize private ECU
generation. The current runtime shape leaves a gap at the production event-construction
boundary: settlement helpers such as `epoch_attribution_settle_runtime.py` and passive ECU
helpers can settle or compute caller-supplied events, but they do not themselves prove the
source node was public and publicly admitted.

**Phase 1387a assignment:** implement or verify a fail-closed production admission firewall
before Phase 1388/1389. The firewall must reject public economic event construction unless
the source has `visibility=public`, public graph admission evidence, eligible public
evaluation or promotion state, and zero promotion carry-forward for reputation or
corroboration reuse. Phase 1387a must also produce an accepted ADR/CDL coverage matrix so
no ratified or accepted public-RC functionality remains unrouted before activation.

**Phase 1369 Fix1 draft instruction:** After the Phase 1369 sequence lock is committed,
Claude Code will draft a NON-SENSITIVE `antigravity_prompt__phase_1369_fix1_g8_numeric_hardening.md`
addressing items 1-6 and 8 above. The human reviewer must authorize the Fix1 prompt before
Codex executes it. Fix1 is not a prerequisite for Phases 1370-1376; it may run in parallel
with those phases.

---

## 5. Identity Bootstrap CDL — CDL-090 Scope

**CDL number: CDL-090** (next fresh number after CDL-089; confirm by direct-reading the CDL
register for CDL-089 as the latest numbered row, confirming CDL-090 is absent, and confirming
CDL-088 remains reserved outside the register)

CDL-090 governs the non-custodial identity-seed path for ILC. It must address:

- Non-custodial identity-seed path: user controls seed material; no server-side custodian
- Ceremony modes: interactive (human operator ceremony) and agent-mode (automated test/devnet)
- Secure output target: seed output goes to a designated secure store, not stdout
- No-stdout-fallback rule: any fallback that writes seed material to stdout is prohibited
- Genesis-rooted birth attestation linkage: `agent_id` must be bound to a signed Genesis/Atlas
  lineage anchor per ADR-0038 before CDL-090 ratification

**Rejected candidates:**
- Custodial key management (violates non-custodial default)
- Entropy from private graph content (private graph content must not become entropy source)
- Stdout as a valid output path (information leakage risk)

**Non-goals for CDL-090:**
- Does not govern ECU-to-ILC conversion (CDL-048)
- Does not govern public claimability API surface (CDL-088)
- Does not govern validator key ceremony (Phase 1386)

**Prerequisite chain:** ADR-0038 (Phase 1370) → CDL-090 opening (Phase 1371) → deliberation/prelock
(Phase 1372) → ratification (Phase 1373) → CDL-088 opening (Phase 1374) prerequisite satisfied

---

## 6. CDL-088 Scope

**CDL number: CDL-088** (pre-reserved; no new CDL number assignment required)

CDL-088 governs public claimability authority for ILC. Candidate scope elements for deliberation:

- Bounded public claimability authority: time-bounded or condition-bounded opening of the
  public claim endpoint
- Reciprocal scoring (if included): contributor-identity and claim score interlock
- ECU-escrow admission (if included): ECU escrow as prerequisite for claim admission

**Critical constraint:** CDL-088 must NOT be opened without explicit `GO Phase 1374`.
The Phase 1362 selection explicitly preserved CDL-088 for public claimability, and the
Phase 1363 scoped prelock record states that CDL-088 remains unopened and reserved for
public-claimability authority. Opening CDL-088 before CDL-090 is ratified is a stop
condition.

---

## 7. CDL Number Assignments

| CDL | Title (candidate) | Decision digest anchor | Opening phase | Ratification phase |
|-----|-------------------|----------------------|---------------|-------------------|
| CDL-090 | Identity bootstrap — non-custodial identity-seed path | Non-custodial path; ceremony modes; secure output; no-stdout-fallback; Genesis-rooted birth attestation | Phase 1371 | Phase 1373 |
| CDL-088 | Public claimability authority | Bounded public claimability; reciprocal scoring; ECU-escrow admission (all TBD at Phase 1374) | Phase 1374 (conditional — requires explicit `GO Phase 1374`) | Phase 1376 |

Notes:
- CDL-090 is the next fresh CDL number; assignment must be confirmed by direct-reading the CDL register for CDL-089 as the last numbered row, confirming CDL-090 is absent, and confirming CDL-088 remains pre-reserved outside the register
- CDL-088 is pre-reserved and pre-authorized as a number; opening requires explicit `GO Phase 1374`
- No other new CDL numbers are assigned in this window

---

## 8. Candidate Phase Table

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 1369 | Sequence lock + capsule v5.58; record hardening carry-forward disposition | Gate / Foundation | **SENSITIVE** |
| 2 | 1369 Fix1 | Numeric hardening pass: Decimal magnitude, genesis counter, governance bounds, LMDB, dead branch | Runtime | NON-SENSITIVE |
| 3 | 1370 | Agent birth attestation ADR-0038 | Spec / ADR | NON-SENSITIVE |
| 4 | 1371 | Identity bootstrap CDL-090 opening | Constitutional | **SENSITIVE** |
| 5 | 1372 | Identity bootstrap CDL-090 deliberation/prelock | Constitutional | **SENSITIVE** |
| 6 | 1373 | Identity bootstrap CDL-090 ratification | Constitutional | **SENSITIVE** |
| 7 | 1374 | CDL-088 opening | Constitutional | **SENSITIVE** |
| 8 | 1375 | CDL-088 deliberation/prelock | Constitutional | **SENSITIVE** |
| 9 | 1376 | CDL-088 ratification | Constitutional | **SENSITIVE** |
| 10 | 1377 | Replay/nullifier + duplicate-claim registry policy ADR | Constitutional / Spec | **SENSITIVE** |
| 11 | 1378 | Legacy `/v1/public/*` FastAPI route cleanup | Runtime | **SENSITIVE** |
| 12 | 1379 | ADR-0031 sidecar query runtime completeness | Runtime | **SENSITIVE** |
| 13 | 1380 | CDL-048 ECU-to-ILC dry-run wiring | Runtime | COMPLETE |
| 14 | 1381 | CDL-006 challenge node spec + stub | Constitutional / Runtime-prep | **SENSITIVE** |
| 15 | 1382 | CDL-006 challenge node runtime + tests | Constitutional / Runtime | **SENSITIVE** |
| 16 | 1383 | CDL-009 fork legitimacy UX | Constitutional / Runtime | **SENSITIVE** |
| 17 | 1384 | External security audit engagement | Governance review | NON-SENSITIVE |
| 18 | 1385 | TLA+ SafetyNoDualCert disposition | Governance review | COMPLETE: defer-with-authority; owned-object Spec B proof preserved, epoch-checkpoint/shared-object proof deferred; closed by Phase 1385a Spec D |
| 19 | 1386 | Genesis validator bootstrap exception record | Constitutional | COMPLETE; Genesis-controlled single-custodian pre-RC/testnet exception; single-operator-compromise resistance is not confirmed |
| 20 | 1386a | Production TLS gRPC path proof | Runtime | COMPLETE; TLS path proven; epoch-0 sentinel reconciled; channel receive limit added |
| 21 | 1386b | Validator endpoint registry ADR | Spec / ADR | COMPLETE; ADR-0039 accepted; endpoint registry/projection contract defined |
| 22 | 1386c | Persistent QUIC connectivity proof | Runtime | COMPLETE; projection-backed persistent sessions implemented in `ilc_consensus/`; direct QUIC and CDL-078 relay fallback proven; activation path requires `endpoint_projection_path` instead of hardcoded config peers |
| 23 | 1387 | Pre-activation hardening gate | Gate | COMPLETE: RE-RUN PASS; v0.2 supersedes original failed-closed v0.1 report |
| 24 | 1387a | Accepted ADR/CDL coverage audit + public-economics admission firewall | Runtime / Gate | COMPLETE: PASS; public-economics firewall confirmed |
| 25 | 1388 | CDL-048 activation + counsel clearance | Constitutional / Runtime | COMPLETE after rerun; `cdl_048_activated_phase_1388`, `counsel_clearance_public_verifier_api_phase_1388`, and `first_live_value_path_activation_phase_1388`; runtime unlock committed in `e96a629d`; public claimability remains false until Phase 1389. |
| 25a | 1388a | CDL-048 self-counsel clearance | Governance / Prompt | COMPLETE; `counsel_clearance_cdl_048_activation_phase_1388a`; internal self-counsel prerequisite cleared for successful Phase 1388 rerun; no public claimability activation. |
| 26 | 1389 | Public claimability / API activation gate | Gate | COMPLETE after rerun: v0.1 failed closed; v0.2 PASS records `result=public_claimability_activated` and `claimability_runtime_public_mode_blockers_cleared_phase_1389_rerun` |
| 27 | 1390 | Window closure handoff | Gate | COMPLETE; `window_1369_1390_closed_phase_1390.v0.1`; Window 1391+ requires explicit GO |

**Note on Phase 1369 Fix1:** This is a lettered sub-phase slot authorized by the Phase 1369
sequence lock. It is NON-SENSITIVE (no CDL mutation, no value-path activation, no public surface
change). The Fix1 prompt will be drafted by Claude Code and reviewed by the human before Codex
executes it.

**Note on Phase 1374 explicit authorization:** Phase 1374 requires a separate `GO Phase 1374`
even after the guidance doc is approved. CDL-088 is a high-authority constitutionally scoped
CDL that has been pre-reserved since Phase 1362 with special protection. The Phase 1369
sequence lock records this requirement explicitly.

**Note on Phase 1389 fails-closed logic:** Phase 1389 re-executes the Phase 1336 gate with
all six blockers, plus the Window 1369-1390 accepted-functionality and public-economics
precondition from Phase 1387a. It fails closed if any of the following is not confirmed closed:
1. CDL-088 not ratified (Phase 1376 incomplete)
2. Agent birth attestation spec missing (Phase 1370 incomplete)
3. Identity bootstrap ADR/CDL not drafted and ratified (Phases 1370-1373 incomplete)
4. Replay/nullifier policy unwritten (Phase 1377 incomplete)
5. Legacy `/v1/public/*` FastAPI routes not cleaned up (Phase 1378 incomplete)
6. Counsel clearance for public verifier API surface not obtained (closed by successful Phase 1388 rerun)
7. Phase 1387a did not prove accepted ADR/CDL coverage and public-only economics admission

---

## 9. Sensitivity Classification

**SENSITIVE (require explicit human GO token before execution):**

- **Phase 1369** — sequence lock; authorizes window phase order and sensitive phase boundaries;
  publishes hardening carry-forward disposition; always SENSITIVE
- **Phase 1371** — CDL-090 opening; CDL mutation; `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1371`
- **Phase 1372** — CDL-090 deliberation/prelock; touches CDL document boundary (constitutional deliberation record)
- **Phase 1373** — CDL-090 ratification; CDL mutation; `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1373`
- **Phase 1374** — CDL-088 opening; CDL mutation; requires additional `GO Phase 1374` beyond guidance doc approval; `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1374`
- **Phase 1375** — CDL-088 deliberation/prelock; constitutional deliberation record
- **Phase 1376** — CDL-088 ratification; CDL mutation; `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1376`
- **Phase 1377** — replay/nullifier policy; governs live claim endpoint admission; constitutional significance
- **Phase 1378** — legacy FastAPI cleanup; public-facing server surface change
- **Phase 1379** — ADR-0031 sidecar completeness; closes `NotImplementedError` on a public-query surface
- **Phase 1380** — CDL-048 dry-run wiring; touches ECU-to-ILC conversion path even in gate-closed state
- **Phase 1381** — CDL-006 challenge node spec; governance completeness spec on constitutional surface
- **Phase 1382** — CDL-006 challenge node runtime + tests; production governance runtime
- **Phase 1383** — CDL-009 fork legitimacy UX; production governance UX surface
- **Phase 1386** — genesis validator bootstrap exception record; Genesis authority surface
- **Phase 1386c** — persistent QUIC connectivity proof; `ilc_consensus/` Rust source change
- **Phase 1387** — pre-activation hardening gate; always SENSITIVE
- **Phase 1387a** — accepted ADR/CDL coverage audit and public-economics firewall; always SENSITIVE
- **Phase 1388** — CDL-048 activation + counsel clearance; first live value-path activation
- **Phase 1389** — public claimability gate; explicit `GO Phase 1389` required; always SENSITIVE
- **Phase 1390** — window closure handoff; always SENSITIVE

**NON-SENSITIVE:**

- **Phase 1369 Fix1** — numeric hardening only; no CDL mutation; no value-path or public surface activation; no protocol semantic change; bundled low-risk cleanup
- **Phase 1370** — ADR-0038 agent birth attestation; spec/ADR document only; no CDL mutation; no runtime activation
- **Phase 1384** — security review scope record; AI-assisted and community path; no runtime or CDL change
- **Phase 1385** — TLA+ SafetyNoDualCert disposition; governance disposition document only
- **Phase 1386a** — production TLS gRPC path proof; testnet infrastructure only; no production activation; no CDL mutation
- **Phase 1386b** — validator endpoint registry ADR; spec/ADR document only; no CDL mutation

**Pre-commit hook block — CDL mutations require these env vars:**

```
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1371  # CDL-090 opening
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1373  # CDL-090 ratification
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1374  # CDL-088 opening
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1376  # CDL-088 ratification
```

---

## 10. Scope Notes for Fixed Phases

### Phase 1369 — Sequence lock + capsule v5.58

**SENSITIVE** — requires explicit `GO Phase 1369`.

Deliverables:
- `docs/specs/ilc_phase_1369_1390_sequence_lock_v0.1.md` — records: Phase 1368 closure commit `390e0be4`, capsule v5.57 baseline, CDL-089 ratified, CDL-088 reserved outside the register, CDL-090 next fresh number, locked phase order 1369-1390, hardening carry-forward disposition (all 8 items from the joint audit assigned to Fix1 or Phase 1386a), and explicit `GO Phase 1374` and `GO Phase 1389` requirements
- `docs/specs/ilc_antigravity_context_capsule_v5.58.md` — capsule update recording window entry state
- STATUS.md updated
- PLANNING_INDEX.md §0 updated

Required content in sequence lock: every runtime hardening item from §4 of this guidance
doc must appear with its assigned phase or explicit deferred-with-authority record.

Commit subject: `phase 1369 sequence lock window 1369-1390`

### Phase 1369 Fix1 — Numeric hardening pass

**NON-SENSITIVE** — may proceed after Phase 1369 sequence lock commits and Fix1 prompt is
reviewed and authorized.

Deliverables: runtime changes to `fee_burn_split_runtime.py`, `allocation_distributor_runtime.py`,
`treasury_governance_runtime.py`, `ecu_price_clamp_runtime.py`, `validator_reward_pool_routing_runtime.py`,
`epoch_attribution_settle_runtime.py`, `genesis_intervention_runtime.py`, `governance_weight.py`,
`lmdb_graph_pruning_runtime.py`, and seven `_decimal_to_string` files. Tests for each change.
No CDL mutation. No production activation. No public surface change.

Commit subject: `phase 1369 fix1 numeric hardening pass`

### Phase 1370 — Agent birth attestation ADR-0038

**NON-SENSITIVE** — may proceed after guidance doc approval.

Deliverables: `docs/adr/ADR_0038_Agent_Birth_Attestation.md` or similar path.

Required content:
- Genesis-rooted identity-origin proof specification
- `agent_id` binding to signed Genesis/Atlas lineage anchor
- Non-custodial default requirement
- No-private-graph-content-as-entropy rule
- Ceremony modes (interactive, agent-mode)
- Secure output target requirement

This ADR is a prerequisite for CDL-090 deliberation. Phase 1371 must not execute before
Phase 1370 commits the ADR.

Commit subject: `phase 1370 agent birth attestation adr-0038`

### Phase 1371 — Identity bootstrap CDL-090 opening

**SENSITIVE** — requires `GO Phase 1371`.
Pre-commit hook: `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1371`

Deliverables: CDL register row for CDL-090; opening document at
`docs/specs/ilc_cdl_090_identity_bootstrap_opening_1371_v0.1.md`.

Required CDL opening content:
- Non-custodial identity-seed path definition
- Ceremony modes: interactive and agent-mode
- Secure output target specification (not stdout)
- No-stdout-fallback rule
- Genesis-rooted birth attestation linkage to ADR-0038

Historical non-ratification token: `cdl_090_not_ratified_phase_1371`
Opening token: `cdl_090_identity_bootstrap_opened_phase_1371`

Commit subject: `phase 1371 cdl-090 identity bootstrap opening`

### Phase 1372 — CDL-090 deliberation/prelock

**SENSITIVE** — requires `GO Phase 1372`.

Deliverables: prelock spec at `docs/specs/ilc_cdl_090_prelock_spec_1372_v0.1.md`.

Standard deliberation pattern: resolve any open questions from Phase 1371 opening;
lock scope constants and non-goals; record prelock token
`cdl_090_prelock_committed_phase_1372`.

Phase 1373 must not execute before Phase 1372 is committed.

Commit subject: `phase 1372 cdl-090 identity bootstrap deliberation prelock`

### Phase 1373 — CDL-090 ratification

**SENSITIVE** — requires `GO Phase 1373`.
Pre-commit hook: `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1373`

Deliverables: CDL register mutation for CDL-090 from open to ratified; ratification
evidence at `docs/specs/ilc_cdl_090_ratification_evidence_1373_v0.1.md`.

Standard ratification pattern: 7 tests (5 + 2), pre-commit split, 4-path resolver;
historical hardening: Phase 1371 prelock test must read CDL at historical opening commit
ref and assert `status: open`.

Ratification token: `cdl_090_ratified_phase_1373`

Commit subject: `phase 1373 cdl-090 identity bootstrap ratification`

### Phase 1374 — CDL-088 opening

**SENSITIVE** — requires explicit `GO Phase 1374` (separate from guidance doc approval).
Pre-commit hook: `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1374`

Must NOT execute before Phase 1373 (CDL-090 ratified) and explicit `GO Phase 1374`.

Deliverables: CDL register row for CDL-088 (adding the pre-reserved/absent row as open);
opening document at `docs/specs/ilc_cdl_088_public_claimability_opening_1374_v0.1.md`.

Required scope elements for deliberation: bounded public claimability authority;
reciprocal scoring (if included); ECU-escrow admission (if included).

Historical non-ratification token: `cdl_088_not_ratified_phase_1374`
Opening token: `cdl_088_public_claimability_opened_phase_1374`

Commit subject: `phase 1374 cdl-088 public claimability opening`

### Phase 1375 — CDL-088 deliberation/prelock

**SENSITIVE** — requires `GO Phase 1375`.

Deliverables: prelock spec at `docs/specs/ilc_cdl_088_prelock_spec_1375_v0.1.md`.

Prelock token: `cdl_088_prelock_committed_phase_1375`

Commit subject: `phase 1375 cdl-088 public claimability deliberation prelock`

### Phase 1376 — CDL-088 ratification

**SENSITIVE** — requires `GO Phase 1376`.
Pre-commit hook: `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1376`

Deliverables: CDL register mutation; ratification evidence at
`docs/specs/ilc_cdl_088_ratification_evidence_1376_v0.1.md`.

Ratification token: `cdl_088_ratified_phase_1376`

Commit subject: `phase 1376 cdl-088 public claimability ratification`

### Phase 1377 — Replay/nullifier + duplicate-claim registry policy

**SENSITIVE** — requires `GO Phase 1377`.

Deliverables: policy document at `docs/specs/ilc_replay_nullifier_policy_1377_v0.1.md`
(ADR or CDL as determined; if CDL mutation, separate pre-commit hook required).

Required content:
- What counts as a replay (definition)
- Nullifier construction: how nullifiers are derived from claim inputs
- Nullifier storage: where nullifiers are persisted and for how long
- Epoch-bounded expiry: nullifier validity window
- Duplicate-claim rejection mechanism at public API layer

This policy must be in place before any live claim endpoint activation (Phase 1388/1389).

Commit subject: `phase 1377 replay nullifier duplicate-claim registry policy`

### Phase 1378 — Legacy FastAPI route cleanup

**SENSITIVE** — requires `GO Phase 1378`.

Deliverables: runtime changes removing or replacing all `/v1/public/*` routes flagged
in Phase 1301. Tests proving no public-labeled route exists outside authorized public
verifier surface.

Required token from Phase 1301: `legacy_public_labeled_fastapi_routes_carry_forward_phase_1301`
must be searched and confirmed before executing. Record: `legacy_public_labeled_fastapi_routes_cleaned_phase_1378`

Commit subject: `phase 1378 legacy fastapi public route cleanup`

### Phase 1379 — ADR-0031 sidecar query runtime completeness

**SENSITIVE** — requires `GO Phase 1379`.

Deliverables: implementation of all query types currently raising `NotImplementedError`
in `ilc_core/graph/sidecar_query_runtime.py`. Tests for each implemented type.

Before executing, read `ilc_core/graph/sidecar_query_runtime.py` in full to enumerate
every `NotImplementedError` site. Only close query types whose scope is confirmed not
to require CDL-088 ratification or public API authorization.

Record: `adr_0031_sidecar_query_runtime_completeness_phase_1379`

Commit subject: `phase 1379 adr-0031 sidecar query runtime completeness`

### Phase 1380 — CDL-048 ECU-to-ILC dry-run wiring

**SENSITIVE** — requires `GO Phase 1380`. Prerequisites: Phase 1373 (CDL-090 ratified)
and Phase 1376 (CDL-088 ratified) must both be complete.

Deliverables: sweeper runtime wired in gate-closed state. No live activation.
Tests proving ECU-to-ILC flow semantics and double-entry correctness at the wire level.

CDL-048 was ratified at Phase 419. Read the CDL-048 ratification entry before drafting
to confirm the ECU-to-ILC conversion constants and constraints.

Record: `cdl_048_dry_run_wiring_phase_1380` (gate-closed state).
Phase 1380 also records `cdl_048_not_activated_phase_1380`,
`gate_closed_state_confirmed_phase_1380`, and
`double_entry_conservation_proven_wire_level_phase_1380`.
No activation record — activation is Phase 1388 only.

Commit subject: `phase 1380 cdl-048 ecu-to-ilc dry-run wiring`

### Phase 1381 — CDL-006 challenge node spec

**SENSITIVE** — requires `GO Phase 1381`.

Deliverables:
- `docs/specs/ilc_cdl_006_challenge_node_spec_1381_v0.1.md` — challenge record schema,
  multi-body (3-body) quorum logic spec, audit path writer spec
- `ilc_core/governance/challenge_node_runtime.py` stub (spec stub only; no production logic)
- Tests for stub schema conformance

CDL-006 ratified multi-body checks at Phase 993. Read CDL register line for CDL-006
before drafting to confirm ratified scope.

Record: `cdl_006_challenge_node_spec_phase_1381`

Phase 1381 is COMPLETE. It also records
`cdl_006_challenge_node_runtime_stub_phase_1381` and
`cdl_006_multi_body_3_body_quorum_spec_committed`. The runtime file is a
schema/signature stub only; production quorum verification and audit-path
writing remain Phase 1382 scope.

Commit subject: `phase 1381 cdl-006 challenge node spec`

### Phase 1382 — CDL-006 challenge node runtime + tests

**SENSITIVE** — requires `GO Phase 1382`. Prerequisite: Phase 1381 complete.

Deliverables:
- `ilc_core/governance/challenge_node_runtime.py` production implementation:
  challenge record schema enforcement, multi-body (3-body) quorum verification,
  audit-path record writer
- Quorum verification tests
- Audit-path record tests

Record: `cdl_006_challenge_node_runtime_phase_1382.v0.1`

Phase 1382 is COMPLETE. It also records
`cdl_006_3_body_quorum_verification_implemented` and
`cdl_006_audit_path_record_writer_implemented`. The runtime helper validates
challenge records, enforces the exact 3-body affirmative quorum model, and emits
deterministic audit-path records with graph-commitment patches. No challenge
triggering, governance decision execution, graph write integration, CDL
mutation, public serving, or public activation occurred.

Commit subject: `phase 1382 cdl-006 challenge node runtime tests`

### Phase 1383 — CDL-009 fork legitimacy UX

**COMPLETE** — executed after explicit `GO Phase 1383`.

Deliverables:
- Badge schema definition (signature-badge + eligibility rules) — COMPLETE
- Eligibility rules contract document — COMPLETE
- CLI/operator surface for fork-signal inspection — COMPLETE
- Tests for badge schema and eligibility verification — COMPLETE

CDL-009 ratified signature-badge+eligibility-rules at Phase 993. Read CDL register
line for CDL-009 before drafting to confirm ratified scope.

Record: `cdl_009_fork_legitimacy_ux_phase_1383.v0.1`

Commit subject: `phase 1383 cdl-009 fork legitimacy ux`

### Phase 1384 — Security review scope record

**NON-SENSITIVE** to initiate.

Deliverables:
- Security review scope document at `docs/specs/ilc_security_review_scope_1384_v0.1.md`
  recording: review path (AI-assisted structured review plus open source community security
  contributions), rationale for no commercial audit firm requirement, scope (`ilc_consensus/`
  BFT safety + `ilc_core/` economic surfaces + HIGH-001 defense review), and Phase 1387
  project-authority disposition requirement.

Phase 1387 cannot pass without a project-authority security disposition document for every
known HIGH-severity finding in the scoped surfaces. The disposition may close, accept, or
defer the finding, but it must record rationale and bounded authority. The Phase 1384 scope
record alone is not sufficient to satisfy that gate.

Record: `security_review_scope_recorded_phase_1384`

Commit subject: `phase 1384 security review scope record`

### Phase 1385 — TLA+ SafetyNoDualCert disposition

**NON-SENSITIVE**.

Deliverables: disposition document at `docs/specs/ilc_tla_plus_safetynodualcert_disposition_1385_v0.1.md`.

Status: COMPLETE. Phase 1385 selects explicit governance deferral with rationale,
bounded carry-forward authority, M-019 empirical coverage limitations, and a scope split:
owned-object Spec B `SafetyNoDualCert` has bounded TLC evidence; epoch-checkpoint/shared-object
dual-cert safety remains deferred to Spec D or equivalent future formal-methods work.

Record: `tla_plus_safetynodualcert_disposed_phase_1385`
Record: `safetynodualcert_deferred_with_authority_phase_1385`

Commit subject: `phase 1385 tla+ safetynodualcert disposition`

### Phase 1386 — Genesis validator bootstrap record

**SENSITIVE** — requires `GO Phase 1386`.

Deliverables:
- Genesis-controlled single-custodian pre-RC/testnet exception recorded
- Bootstrap record at `docs/specs/ilc_genesis_validator_bootstrap_record_1386_v0.1.md`

Record must state that split custody is not claimed, single-operator-compromise
resistance is not confirmed, no private key material is committed, and production
split custody remains required before mainnet launch.

This addresses M-022 open item #7 for the current public-RC window. It does not
authorize production genesis-signed artifacts.

Record: `genesis_validator_bootstrap_record_committed_phase_1386`

Commit subject: `phase 1386 genesis validator bootstrap record`

### Phase 1386a — Production TLS gRPC path proof

**NON-SENSITIVE** — testnet infrastructure only; no production activation.

Status: COMPLETE. Phase 1386a records `production_tls_grpc_path_proven_phase_1386a`,
`epoch_0_sentinel_reconciliation_verified_phase_1386a`, and
`get_epoch_chain_channel_limit_added_phase_1386a`.

Deliverables:
- Rust optional gRPC server now uses tonic `ServerTlsConfig`
- `build_secure_grpc_read_stub` from `ilc_core/consensus/production_bridge.py` was run with
  `tls_root_certificates` against a TLS-enabled validator endpoint
- Epoch-0 sentinel reconciliation is verified: `GetEpochChain(0,0)` returns an empty
  complete chain at genesis
- Channel receive-size limit and bounded response iteration were added to `get_epoch_chain()`
- Findings and proof are recorded at `docs/specs/ilc_production_tls_grpc_proof_1386a_v0.1.md`

Record: `production_tls_grpc_path_proven_phase_1386a`

Commit subject: `phase 1386a production tls grpc path proof`

### Phase 1386b — Validator endpoint registry ADR

**NON-SENSITIVE** — ADR document only; no CDL mutation.

Status: COMPLETE. ADR-0039 records `validator_endpoint_registry_adr_ratified_phase_1386b`,
`quic_endpoint_epoch_scoped_signed_edge_defined`,
`read_only_projection_contract_defined_phase_1386b`, and
`no_hardcoded_peer_list_production_activation_path_phase_1386b`.

Deliverables: ADR document defining:
- `QUIC_ENDPOINT` as an epoch-scoped signed edge on existing `agent_id` nodes
- Direct endpoint form and CDL-078 relay endpoint form
- Epoch scoping bound to CDL-068 topology shuffle
- Update propagation without genesis restart
- Read-only projection/cache contract: derived from signed graph edges only; limited to
  current topology epoch's validator set; invalidated and rebuilt on each topology shuffle;
  never allowed to acquire its own write/update/set/insert/delete path

Reference: `docs/research/ilc_validator_connectivity_production_model_v0.1.md`

Record: `validator_endpoint_registry_adr_ratified_phase_1386b`

Commit subject: `phase 1386b validator endpoint registry adr`

### Phase 1386c — Persistent QUIC connectivity proof

**SENSITIVE** — requires `GO Phase 1386c`. Prerequisites: Phase 1386b ADR ratified.
Involves `ilc_consensus/` Rust source change.

Deliverables:
- Persistent per-topology-epoch QUIC sessions in `ilc_consensus/` Rust
- Direct QUIC peer-to-peer path proven first
- CDL-078 relay pass-through fallback proven second
- No hardcoded peer list in activation path; addresses read from Phase 1386b registry projection
- Acceptance test: reject any projection type with write/update/set/insert/delete methods
  outside full rebuild from signed graph edges

Status: COMPLETE. Phase 1386c records `persistent_validator_quic_sessions_proven_phase_1386c`,
`direct_quic_path_proven_phase_1386c`, `cdl_078_relay_fallback_implemented_phase_1386c`,
`no_hardcoded_peer_list_activation_path_confirmed_phase_1386c`, and
`write_path_projection_rejected_phase_1386c`. It adds `ilc_consensus/src/persistent_quic.rs`,
requires `endpoint_projection_path` for `settlement_path=mysticeti_fast_path`, and keeps
legacy config peers scoped to `settlement_path=none` non-activation/testnet posture.

Record: `persistent_validator_quic_sessions_proven_phase_1386c`

Commit subject: `phase 1386c persistent quic connectivity proof`

### Phase 1387 — Pre-activation hardening gate

**SENSITIVE** — requires `GO Phase 1387`.

Gate passes only if ALL of the following are confirmed:
1. Project-authority security disposition document for every known HIGH-severity finding in
   `ilc_consensus/` BFT safety, `ilc_core/` economic surfaces, or HIGH-001 defense
2. HIGH-001 defense verified in a non-loopback deployment
3. `production_tls_grpc_path_proven_phase_1386a` recorded
4. Phase 1386b endpoint-registry ADR ratified and `persistent_validator_quic_sessions_proven_phase_1386c`
   recorded — OR — each of 1386b/1386c explicitly deferred with authority and bounded carry-forward scope
5. All 8 runtime hardening items from §4 are addressed (Phase 1369 Fix1 complete) or explicitly
   deferred with authority and bounded carry-forward scope
6. No hardcoded peer list exists in any production activation path

Gate fails closed if any predecessor phase is incomplete or if any known HIGH-severity
finding is missing a project-authority security disposition.

Phase 1387 result: original v0.1 gate report recorded
`pre_activation_hardening_gate_failed_phase_1387` with
`gate_failed_reason=project_authority_security_disposition_missing`. Phase 1387
was re-run after Phase 1387-Fix committed the missing disposition and now records
`pre_activation_hardening_gate_pass_phase_1387` in the v0.2 re-run report. Phase
1387a is next. Phase 1388 must not proceed until Phase 1387a records its own pass.

Commit subject: `phase 1387 pre-activation hardening gate`

### Phase 1387a — Accepted ADR/CDL Coverage Audit + Public-Economics Admission Firewall

**SENSITIVE** — requires `GO Phase 1387a`. Prerequisite: Phase 1387 gate pass.

Status: COMPLETE. Phase 1387a publishes
`docs/specs/ilc_accepted_adr_cdl_public_rc_coverage_matrix_1387a_v0.1.md`,
`docs/specs/ilc_public_economics_admission_firewall_1387a_v0.1.md`, and
`ilc_core/ledger/public_economics_admission_firewall.py`; it records
`accepted_adr_cdl_runtime_coverage_matrix_phase_1387a`,
`public_economics_requires_public_node_admission_verified_phase_1387a`,
`private_visibility_excluded_from_public_economics_phase_1387a`, and
`no_unrouted_accepted_cdl_adr_functionality_before_public_rc_phase_1387a`.
Phase 1388 subsequently executed and failed closed on missing counsel clearance.

Deliverables:
- Accepted ADR/CDL coverage matrix at
  `docs/specs/ilc_accepted_adr_cdl_public_rc_coverage_matrix_1387a_v0.1.md`
- Public-economics admission firewall spec/evidence at
  `docs/specs/ilc_public_economics_admission_firewall_1387a_v0.1.md`
- Runtime guard and tests proving production public ECU, public reputation, public
  settlement, and public claimability events cannot be constructed from private or
  semi-private nodes

Coverage matrix classification must include every accepted ADR and ratified CDL in the
active corpus, with exactly one of: implemented for public RC, covered by a later phase
before 1389, documentation/governance-only with no runtime obligation, explicitly deferred
outside the public-RC claim, or `gap_blocks_public_rc`. Phase 1389 must fail closed if any
entry remains unknown or `gap_blocks_public_rc`.

The public-economics firewall must enforce the current canon: private and semi-private
nodes are off-chain/shard-local and may only have operator-local advisory scoring. They do
not generate protocol ECU, public reputation, public settlement rights, public corroboration,
or public claimability. Public economic event construction must require public-node
visibility, public graph admission evidence, eligible public evaluation or promotion state,
and zero promotion carry-forward for reputation or corroboration reuse.

Record: `accepted_adr_cdl_runtime_coverage_matrix_phase_1387a`,
`public_economics_requires_public_node_admission_verified_phase_1387a`,
`private_visibility_excluded_from_public_economics_phase_1387a`, and
`no_unrouted_accepted_cdl_adr_functionality_before_public_rc_phase_1387a`

Commit subject: `phase 1387a adr cdl coverage public economics firewall`

### Phase 1388 — CDL-048 activation + counsel clearance

**SENSITIVE** — executed after `GO Phase 1388`; first execution failed closed,
then a rerun completed after Phase 1388a.

Prerequisites checked:
- Phase 1387 gate PASS is confirmed through the superseding v0.2 rerun report,
  not the original v0.1 failed-closed report named by the stale prompt input.
- Phase 1387a accepted-functionality/public-economics firewall PASS is confirmed.
- Counsel sign-off on the public verifier API surface was missing at first execution time.
- Phase 1388a subsequently supplied the required Genesis-authority self-counsel
  clearance for the narrow CDL-048 pre-production/testnet activation scope.

Disposition:
- `docs/specs/ilc_phase_1388_cdl_048_activation_counsel_clearance_blocked_v0.1.md`
  records `phase_1388_cdl_048_activation_failed_closed`,
  `cdl_048_activation_not_performed_phase_1388`,
  `counsel_clearance_public_verifier_api_missing_phase_1388`,
  `first_live_value_path_activation_not_performed_phase_1388`,
  `phase_1388_prompt_v0_1_gate_reference_superseded_by_v0_2_pass`, and
  `phase_1389_not_opened_phase_1388`.
- Historical blocked record remains canonical for the first execution only.
- `docs/specs/ilc_counsel_clearance_1388_v0.1.md` records
  `cdl_048_activated_phase_1388`,
  `counsel_clearance_public_verifier_api_phase_1388`, and
  `first_live_value_path_activation_phase_1388`.
- Runtime commit `e96a629d` opens the CDL-048 activation-request path while
  preserving `public_claimability_activated=False`.

Phase 1389 is now the next public claimability gate and remains SENSITIVE,
requiring explicit `GO Phase 1389`.

Historical failed-closed commit subject:
`phase 1388 cdl-048 activation counsel clearance failed closed`

Successful rerun commit subjects:
`phase 1388 cdl-048 runtime activation`
`phase 1388 cdl-048 activation counsel clearance`

### Phase 1388a — CDL-048 self-counsel clearance

**NON-SENSITIVE** — documentation and prompt hardening only.

Status: COMPLETE. Phase 1388a publishes
`docs/specs/ilc_counsel_clearance_cdl_048_activation_1388a_v0.1.md`, adds a
scoped Phase 1388a note to `LICENSING.md`, adds a scoped addendum to
`docs/specs/ilc_cdl_086_counsel_disposition_1220_v0.1.md`, and hardens the
Phase 1388 prompt.

Record: `counsel_clearance_cdl_048_activation_phase_1388a` and
`self_counsel_decision_not_external_legal_opinion_phase_1388a`.

Scope: internal Genesis-authority self-counsel decision for the narrow CDL-048
pre-production/testnet activation surface only. It is not external legal advice,
does not authorize mainnet, does not authorize public conversions with
real-world economic value, and does not open Phase 1389.

Commit subject: `phase 1388a cdl-048 self-counsel clearance`

### Phase 1389 — Public claimability/API activation gate

**SENSITIVE** — executed after explicit `GO Phase 1389` and failed closed.

Re-executes the Phase 1336 gate with all six blockers confirmed closed:

| Blocker | Closing phase | Required confirmation |
|---------|--------------|----------------------|
| CDL-088 not ratified | Phase 1376 | `cdl_088_ratified_phase_1376` token present |
| Agent birth attestation spec missing | Phase 1370 | ADR-0038 document committed |
| Identity bootstrap ADR/CDL not drafted/ratified | Phases 1370-1373 | `cdl_090_ratified_phase_1373` token present |
| Replay/nullifier policy unwritten | Phase 1377 | Policy document committed |
| Legacy `/v1/public/*` routes not cleaned up | Phase 1378 | `legacy_public_labeled_fastapi_routes_cleaned_phase_1378` token present |
| Counsel clearance for public verifier API surface | Phase 1388 | `counsel_clearance_public_verifier_api_phase_1388` token present |
| Accepted ADR/CDL coverage and public-only economics admission | Phase 1387a | `no_unrouted_accepted_cdl_adr_functionality_before_public_rc_phase_1387a` and `public_economics_requires_public_node_admission_verified_phase_1387a` tokens present |

Result: `public_claimability_gate_failed_phase_1389`.

The six governance/document blockers and Phase 1387/1387a/1388 prerequisites
were direct-read. The gate failed because `ilc_core/sidecars/claimability_receipt_verifier.py`
still carries public-mode blockers for public claimability API authority,
replay/nullifier activation, duplicate-claim registry activation, public-safe
disclosure schema finality, and public transport-principal activation.

Record: `gate_failed_reason=claimability_runtime_public_mode_blockers_still_active`

Commit subject: `phase 1389 public claimability api activation gate`

### Phase 1389a — Claimability public-mode governance decisions

**NON-SENSITIVE** — governance/disposition only; no runtime activation.

Closes the three Phase 1305 public-mode blockers that can be resolved by
committed governance authority:

```text
claimability_public_mode_governance_decisions_phase_1389a
cdl_088_is_public_claimability_api_authority_phase_1389a
public_safe_disclosure_schema_final_cdl_088_scope_phase_1389a
transport_principal_resolved_at_d2d_layer_adr_0039_cdl_078_phase_1389a
claimability_runtime_registry_blockers_remain_phase_1389a
```

Disposition: CDL-088 is the ratified public claimability API authority; Phase
1291 plus CDL-088 and the verifier expected-key sets define the public-safe
claimability disclosure schema; ADR-0039 signed `QUIC_ENDPOINT` edges plus
CDL-078/Phase 1386c route transport-principal resolution to the D2D/admission
layer. Replay/nullifier and duplicate-claim registry blockers remain runtime
carry-forward.

Phase 1389a did not mutate `ilc_core/`, remove `_PUBLIC_MODE_BLOCKERS`,
activate public claimability, open a public API, or rerun Phase 1389. The later
"after Phase 1397a" phrase was corrected by the user as a fat-finger; Phase
1389b subsequently executed after Phase 1389a under explicit authorization.

Commit subject: `phase 1389a claimability public mode governance decisions`

### Phase 1389b — Claimability public-mode runtime

**SENSITIVE** — executed after explicit `GO Phase 1389b`.

Implements the two runtime blockers preserved by Phase 1389a. Runtime commit
`aed33474` adds `claim_nullifier_registry_v1`, wires optional registry-backed
admission into the claimability verifier, rejects active replay nullifiers,
rejects duplicate claim material at admission, rejects premature and closed
claim windows by issuance epoch, and empties `_PUBLIC_MODE_BLOCKERS`.

Record:

```text
claimability_public_mode_runtime_phase_1389b
claim_nullifier_registry_v1_active_phase_1389b
duplicate_claim_registry_active_phase_1389b
claimability_verifier_public_mode_ready_phase_1389b
public_mode_blockers_empty_phase_1389b
```

Non-authorization: no public verifier API serving, claim endpoint serving,
wallet action, ECU minting, ILC settlement, CDL mutation, public RC publication,
or mainnet launch.

Commit subject: `phase 1389b claimability nullifier registry runtime`

### Phase 1389 rerun — Public claimability activation gate v0.2

**SENSITIVE** — executed after explicit user authorization to rerun Phase 1389 if
the post-1389b state was green.

Supersedes the historical Phase 1389 v0.1 failed-closed report for routing.
Phase 1389a closed the three governance-resolvable public-mode blockers; Phase
1389b implemented the replay/nullifier and duplicate-claim runtime blockers.
The v0.2 rerun report records:

```text
public_claimability_gate_phase_1389_executed
result=public_claimability_activated
public_claimability_gate_rerun_passed_after_1389b
claimability_runtime_public_mode_blockers_cleared_phase_1389_rerun
phase_1389_v0_1_failed_closed_superseded_by_v0_2_pass
```

The rerun adds no public serving route, starts no public HTTP listener, performs
no wallet action, mints no ECU, settles no ILC, publishes no public RC artifacts,
launches no mainnet, mutates no CDL row, and records no external legal advice or
legal conclusion.

Commit subject: `phase 1389 public claimability activation gate rerun`

### Phase 1390 — Window closure handoff

**SENSITIVE** — complete after explicit `GO Phase 1390`.

Deliverables:
- `docs/specs/ilc_window_1369_1390_handoff_1390_v0.1.md` — follows
  `docs/specs/ilc_window_closure_handoff_doc_schema_v0.1.md` exactly
- Must record MemPalace refresh disposition
- Must record honest closure verdict: landed phases, open/incomplete phases, carry-forward

Record:

```text
window_1369_1390_closed_phase_1390.v0.1
window_1369_1390_closure_verdict_recorded_phase_1390
mempalace_refresh_disposition_recorded_phase_1390
window_1391_not_open_phase_1390
go_window_1391_required_next
```

Commit subject: `phase 1390 window 1369-1390 closure handoff`

---

## 11. Key Dependencies and Open Questions

### Strict dependency chain (from forward plan)

```
Phase 1369 sequence lock
    → Phase 1370 agent birth attestation ADR
        → Phase 1371 CDL-090 opening
            → Phase 1372 CDL-090 prelock
                → Phase 1373 CDL-090 ratification
    → Phase 1374 CDL-088 opening  [requires separate GO Phase 1374; scope drafting parallel]
        → Phase 1375 CDL-088 prelock
            → Phase 1376 CDL-088 ratification
    → Phase 1377 replay/nullifier policy
    → Phase 1378 FastAPI cleanup
    → Phase 1379 ADR-0031 sidecar
    → Phase 1380 CDL-048 dry-run wiring  [requires 1373 + 1376]
    → Phase 1381 CDL-006 spec
        → Phase 1382 CDL-006 runtime
    → Phase 1383 CDL-009 UX  [complete; CLI/operator only]
    → Phase 1384 security review scope  [parallel; disposition gate required at 1387]
    → Phase 1385 TLA+ disposition  [complete; deferral closed by Phase 1385a Spec D]
    → Phase 1386 bootstrap exception record
        → Phase 1386a production TLS gRPC  [complete]
            → Phase 1386b endpoint registry ADR  [complete]
                → Phase 1386c persistent QUIC
                    → Phase 1387 hardening gate
                        → Phase 1387a accepted ADR/CDL coverage + public-economics firewall
                            → Phase 1388 CDL-048 activation + counsel
                                → Phase 1389 public claimability gate
                                    → Phase 1389a public-mode governance decisions
                                        → Phase 1389b public-mode runtime
                                            → Phase 1389 rerun public-claimability gate
                                                → Phase 1390 closure
```

### Must-resolve at Phase 1369 entry

1. **What is the exact scope of CDL-090?** — Non-custodial seed path is the core; ceremony
   modes and secure output target are confirmed scope. Deliberation at Phase 1372 resolves
   any open questions from Phase 1371 opening.
2. **Does Phase 1380 require CDL-088 ratification as a hard prerequisite?** — Yes. Phase 1380
   must not execute before both CDL-090 (Phase 1373) and CDL-088 (Phase 1376) are ratified.
3. **Phase 1384 review path selection** — the Phase 1384 prompt records that the review path is
   AI-assisted structured review plus open source community security contributions; commercial
   audit firm engagement is not required under current funding and anonymity constraints.
4. **Phase 1374 CDL-088 scope** — exact contents (reciprocal scoring, ECU-escrow admission)
   are deliberated at Phase 1375. Phase 1374 opens the CDL with candidate scope only.

### Open questions for Phase 1369 sequence lock

- Does the Phase 1369 Fix1 warrant a separate human-authorized GO token, or is authorization
  by guidance doc approval sufficient? Recommendation: separate GO after Fix1 prompt review.
- Is Phase 1386c a hard Phase 1387 prerequisite or may it be explicitly deferred with
  bounded carry-forward authority? Forward plan permits explicit defer-with-authority.
- Phase 1387a is not optional for public RC: if the accepted ADR/CDL coverage matrix finds
  any `gap_blocks_public_rc` item or the public-only economics admission firewall is not
  proven, Phase 1388/1389 must fail closed or defer public RC.

---

## 12. Known Patterns and Technical Constraints

### Novel patterns introduced this window

1. **First window with explicit `GO Phase NNN` for CDL opening** (Phase 1374 requires
   `GO Phase 1374` separate from guidance doc approval): pattern established to protect
   CDL-088 public-claimability authority from accidental early opening.
2. **First CDL ratified as a prerequisite for another CDL opening** (CDL-090 ratified
   Phase 1373 before CDL-088 opens Phase 1374): captures the identity-before-claim
   dependency chain.
3. **First live value-path activation** (Phase 1388 CDL-048): pattern for separate commit
   required for sweeper runtime unlock.
4. **Phase 1369 Fix1 lettered sub-phase**: first use of a Fix1 slot authorized by sequence
   lock for low-risk bundled numeric hardening.

### Historical prelock hardening

Each CDL ratification phase (1373, 1376) must harden the corresponding prelock test to
assert `"status: open"` at the historical opening commit ref, not at HEAD. This is the
standard prelock hardening pattern established at Phase 374 and required for every
subsequent CDL ratification. Read the actual CDL register at the opening commit ref;
do not reason by analogy.

### Phantom edit guard

Multiple `ilc_core/` runtime files are mutation targets in this window:
- Phase 1369 Fix1: `fee_burn_split_runtime.py`, `allocation_distributor_runtime.py`,
  `treasury_governance_runtime.py`, `ecu_price_clamp_runtime.py`,
  `validator_reward_pool_routing_runtime.py`, `epoch_attribution_settle_runtime.py`,
  `genesis_intervention_runtime.py`, `governance_weight.py`, `lmdb_graph_pruning_runtime.py`
- Phase 1379: `ilc_core/graph/sidecar_query_runtime.py`
- Phase 1378: FastAPI route files (location to be confirmed by Phase 1378 §0c search)
- Phase 1380: sweeper/conversion runtime (CDL-048 related)
- Phase 1381/1382: `ilc_core/governance/challenge_node_runtime.py` (new file)
- Phase 1383: `ilc_core/governance/fork_legitimacy_runtime.py`
- Phase 1387a: public economics admission/event-construction boundary files (location to
  be confirmed by §0 discovery; likely touches attribution, passive ECU, claimability,
  node admission, or promotion-continuity runtime surfaces)
- Phase 1388: first live activation runtime (sweeper unlock)

Detection: `git diff --check -- ilc_core` after any runtime phase.
Fix: `git checkout -- <phantom-edited-file>` and re-execute only the authorized mutations.

**CDL doc and runtime in separate commits**: any CDL ratification phase that also mutates
a runtime file (Phase 1373 if it flips an activation flag, Phase 1376 if applicable,
Phase 1388) must use two commits: CDL document commit (requires `ILC_CDL_MUTATION_AUTHORIZED`)
and runtime commit (separate, clean-state guard passes).

### Pre-commit hook clean-state guard

For phases that mutate `ilc_core/` runtime files: the pre-commit hook verifies no
uncommitted CDL document mutations are staged alongside runtime mutations. Use separate
commits for CDL docs and runtime changes.

### Closure gate selftest guard chain

Phase 1390 closure gate must include category-3 selftest env vars for all prior closure
gates in the test suite. Read each prior gate test file explicitly; do not reason from
the list by analogy. Missing a selftest guard causes the gate test to re-enter the full
prior gate rather than short-circuit.

---

## 13. Non-Goals

This window does NOT:

- Activate public RC without Phase 1389 producing explicit `result=public_claimability_activated`
- Open CDL-088 without explicit `GO Phase 1374`
- Ratify CDL-090 without explicit `GO Phase 1373`
- Activate production minting (deferred from Window 1343-1368; no re-gate in this window)
- Publish source, produce release artifacts, or activate public repository distribution
- Close the counsel license, CLA, or trademark tokens
  (`counsel_license_instrument_selection_required_before_public_rc`,
   `counsel_cla_text_approved_required_before_external_contributors`,
   `counsel_trademark_policy_published_required_before_public_launch`)
- Sign Genesis v0.2 or produce a v0.2/v0.3 release artifact
- Open Window 1391+ (Mode-2 refutation adjudication and settlement)
- Implement Dynamic Epistemic Traversal Engine (post-Phase 1241 deferred item)
- Execute CDL-052 Mode-2 settlement-grade adjudication (Window 1391+)
- Activate local ECU reputation scoring in production (separate governance)
- Complete or authorize `routing_reputation_runtime.py` float migration (separate window)
- Make any sender-privacy claim or activate transfer mixing in production
- Implement TOON harness token efficiency (Phase 1333-1337 deferred item)
- Execute any phase in this window before Phase 1369 sequence lock receives `GO Phase 1369`

---

## 14. Key Canonical Anchors for Prompt Drafting

| Artifact | Path | Note |
|----------|------|------|
| Context capsule v5.57 (PRIMARY) | `docs/specs/ilc_antigravity_context_capsule_v5.57.md` | Current capsule baseline |
| Window 1343-1368 closure handoff | `docs/specs/ilc_window_1343_1368_handoff_1368_v0.1.md` | Prior window inheritance |
| Window 1289-1302 guidance doc (format ref) | `docs/specs/ilc_window_1289_1302_candidate_phase_grouping_v0.1.md` | Recent guidance doc format reference |
| CDL register | `docs/specs/ilc_constitutional_decision_log_v0.1.md` | CDL-089 ratified at line 118; confirm CDL-088 and CDL-090 are absent from the register and use the Phase 1363 scoped prelock record / Phase 1368 handoff for the CDL-088 reservation claim |
| Phase completion log | `docs/phases/STATUS.md` | Phase completion history |
| Forward plan (Window 1369-1390 section) | `docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md` lines 813-893 | Authoritative phase table and dependency order |
| Validator connectivity production model | `docs/research/ilc_validator_connectivity_production_model_v0.1.md` | 1386b/1386c architecture |
| ADR-0037 Genesis canonical lineage contract | `docs/adr/ADR_0037_Genesis_Canonical_Lineage_Contract.md` | ADR-0038 predecessor |
| PLANNING_INDEX | `docs/PLANNING_INDEX.md` | §0 must be updated at Phase 1369 and Phase 1390 |
| Sidecar query runtime | `ilc_core/graph/sidecar_query_runtime.py` | Phase 1379 target; Phase 1379 removes the residual `NotImplementedError` fallback and confirms all locked read-only query types dispatch |
| Production bridge | `ilc_core/consensus/production_bridge.py` | Phase 1386a TLS target; `get_epoch_chain` channel limit |
| Phase 1343-1368 sequence lock | `docs/specs/ilc_phase_1343_1368_sequence_lock_v0.1.md` | Format reference for Phase 1369 sequence lock |
| Window closure handoff schema | `docs/specs/ilc_window_closure_handoff_doc_schema_v0.1.md` | Phase 1390 must follow exactly |
| CDL-006 register entry | `docs/specs/ilc_constitutional_decision_log_v0.1.md` line 34 | CDL-006 multi-body check ratified Phase 993 |
| CDL-009 register entry | `docs/specs/ilc_constitutional_decision_log_v0.1.md` line 37 | CDL-009 signature-badge+eligibility ratified Phase 993 |
| CDL-048 ratification evidence | (confirmed ratified Phase 419) | Phase 1380 CDL-048 dry-run prerequisite |
| For closure gate (Phase 1390): all Phase 1369-1389 test files and artifacts | — | Required for closure gate verification |

---

**Gate:** This guidance document is proposed for human and Codex review before any phase executes. Do not open Phase 1369 without explicit `GO Phase 1369` from the human reviewer.
