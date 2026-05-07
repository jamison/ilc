# ILC Window 1233-1240: Candidate Phase Grouping

**Author:** Claude Code (local planning synthesis)
**Date:** 2026-05-06
**Baseline:** Window 1225-1232 CLOSED at Phase 1232 (`e1ce3aa1`),
`window_1225_1232_closure_gate_verdict=pass`. Capsule v5.49 current.
**Planning note:** Candidate grouping only. Phase 1233 sequence lock publishes the
locked order. SENSITIVE phases require explicit human GO. All other phases are
NON-SENSITIVE and may proceed after guidance doc approval.

---

## 1. Window Identity and Scope

Window 1233-1240 is the **commit.epoch runtime alignment and fetch infrastructure
preparation window**. Its primary obligations are:

1. **commit.epoch runtime schema alignment** — the active `make_commit_epoch_event`
   constructor and `validate_commit_epoch_payload` validator still require `created_at`
   (wall-clock ISO 8601). Phase 1226 ratified `epoch_sequence_only_no_wall_clock`.
   This is an active runtime conflict, not schema debt in tombstoned drafts. Aligning
   the runtime is a firm Window 1233 obligation.
2. **commit.epoch emission connector** — no production consensus-layer path currently
   produces a `commit.epoch` event. The `economic_cycle_runtime.py` devnet path exists
   but is not Phase-1226-compliant. A canonical connector is required before production
   emission is authorized.
3. **vote_weight float audit** — `epoch_state_runtime.py` and `finality_evaluator.py`
   use Python `float` for quorum vote weights. These flow into finality aggregation.
   The `epoch_state_cid` in the RC path is not produced from these floats (confirmed:
   it hashes `scenario_manifest`), but the consensus finality path uses `float`
   arithmetic directly. This must be audited and resolved before the commit.epoch
   surface is promoted.
4. **L3 sidecar infrastructure spec** — carried forward from Phase 1222; not addressed
   in Window 1225-1232. Defines sidecar boundaries, graph projection consumption, no
   mutation authority, privacy constraints, agent-vs-human visualisation posture.
5. **SIM-FETCH-01 design and harness** — required before CDL-087 ratification. CDL-087
   remains OPEN / PRELOCKED / NOT RATIFIED. No ratification constants may be locked
   before SIM evidence.
6. **Lineage receipt and allowlist export tooling** — deferred to Window 1241+.
   `allowlist_export_procedure_defined_required_before_public_repo_publication` remains
   an open carry-forward token; no phases in this window address it.

**Character of this window:** implementation-heavy runtime alignment + one spec phase
+ one SIM preparation phase. No CDL ratification is expected unless SIM-FETCH-01
completes and produces evidence within window capacity. CDL-087 ratification remains
gated and is not a window deliverable.

**Fixed phase slots:** Phase 1239 (coherence report + capsule v5.50) and Phase 1240
(closure gate) are fixed. All other phases 1233-1238 are the obligated implementation
lane; no tail-slot conditional phases.

---

## 2. Baseline and Inheritance

### Ratified CDL chain (current through Window 1225-1232)

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
| CDL-087 | Canonical fetch distribution policy | OPEN / PRELOCKED / NOT RATIFIED |

Next fresh CDL number: **CDL-088** (CDL-087 is open, not ratified)

### Active runtime chain (inherited)

| Module | Version token |
|--------|---------------|
| Epoch attribution settle | `epoch_attribution_settle_runtime_1210.v0.7` |
| HTTP fetch transport | `http_fetch_transport_runtime_1212.v0.2` |
| Persistent fetch rate limiter | `persistent_fetch_rate_limiter_runtime_1202.v0.1` |
| Agent graph projection | `agent_graph_projection_runtime_1229.v0.1` |
| Public receipt | `public_receipt_runtime_651.v0.1` |

### Immutable anchors

| Artifact | Value |
|----------|-------|
| Genesis v0.1 signed root envelope hash | `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c` |
| Immutable diagnostic SHA | `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56` |
| Genesis v0.2 candidate | 41-node / 73-edge; unsigned; signing deferred |

---

## 3. Track Inventory

### 3.1 Constitutionally obligated (firm this window)

- `commit_epoch_projection_runtime_required_before_production_emission` — Phase 1226
  carry-forward; audit (Phase 1234), runtime mutation (Phase 1235), and connector
  (Phase 1236) are all required; production emission remains gated after Phase 1236
  until explicitly authorized
- `l3_sidecar_infrastructure_spec_required_window_1225_plus` — Phase 1222 carry-forward;
  Phase 1237 delivers the spec
- SIM-FETCH-01 harness/design — required before any CDL-087 ratification; Phase 1238

### 3.2 Active runtime conflicts (must fix this window)

- **commit.epoch wall-clock**: `make_commit_epoch_event` requires `created_at` (wall-
  clock) at `ilc_core/protocol/event_log.py:299`. `economic_cycle_runtime.py` passes
  `_utc_now()` at lines 446 and 458. Phase 1226 mandates
  `epoch_sequence_only_no_wall_clock`. Audit in Phase 1234; fix executed in Phase 1235
  after GO.
- **vote_weight float in consensus**: `epoch_state_runtime.py` canonical vectors use
  Python `float` vote weights (e.g. `0.40`, `0.35`). `finality_evaluator.py:199` does
  float arithmetic in `aggregate_weights`. `circuit_breaker_interface.py:78` explicitly
  casts to `float`. Genesis bootstrap path correctly enforces `int`. The RC path
  `epoch_state_cid` does not hash these floats (confirmed: hashes `scenario_manifest`
  via `_sha256_json`), but the consensus finality surface uses float arithmetic directly.
  Phase 1234 audits and recommends resolution scope; Phase 1235 executes the fix after GO.

### 3.3 Deferred (not this window)

- CDL-087 ratification — gated by SIM-FETCH-01; SIM harness is Phase 1238; ratification
  is Window 1241+ at earliest
- v0.2 signing — deferred; `v0_2_signing_ceremony_deferred_pending_signing_authorization`
- L4 privacy / onion / SURB — correctly deferred; no prerequisite runtime exists
- Cross-epoch compaction — SIM-COMPACTION-01 required first
- Governance activation ceremony — pieces exist; end-to-end assembly deferred to a
  dedicated window after lineage tooling lands
- Counsel obligations (C1-C5) — human/counsel track; no codebase phases assigned.
  Open tokens: `counsel_license_instrument_selection_required_before_public_rc`,
  `counsel_cla_text_approved_required_before_external_contributors`,
  `counsel_trademark_policy_published_required_before_public_launch`
- `genesis_canonical_lineage_contract_required_before_public_rc` — planning spec
  drafted Phase 1153; ADR opening and acceptance route not yet assigned to a window
- Remaining pre-RC float surfaces in reputation/centrality runtimes —
  `temporal_decay_runtime.py`, `centrality_delta_gossip_runtime.py`, and
  `routing_reputation_runtime.py` use `float` internally; not on critical economic
  settlement path but should migrate before public RC. No window assigned yet.

---

## 4. commit.epoch Runtime Conflict — Detail

### Why this is an active runtime conflict, not schema debt

Three converging confirmed facts:

1. `ilc_core/protocol/event_log.py:299` — `make_commit_epoch_event` takes `created_at:
   str` as a required positional parameter and passes it into the payload
2. `ilc_core/rc/economic_cycle_runtime.py:446,458` — the only non-test callers pass
   `created_at=_utc_now()` where `_utc_now()` is `datetime.now(timezone.utc)...`
3. Phase 1226 ratified `timestamp_policy = "epoch_sequence_only_no_wall_clock"` as part
   of the canonical commit.epoch mapping spec

The wall-clock field is in the active emission path, not only in tombstoned drafts.

### Proposed resolution approach (Phase 1234)

Two options — Phase 1234 recommends one; Phase 1235 executes after GO:

**Option A — New canonical constructor:** Introduce
`make_canonical_commit_epoch_event(epoch_index, epoch_id, ...)` without `created_at`;
mark `make_commit_epoch_event` as `LEGACY_RC_ONLY` with a deprecation comment; migrate
`economic_cycle_runtime` to the new constructor; add tests that reject wall-clock
fields in canonical events.

**Option B — Amend existing constructor:** Remove `created_at` from
`make_commit_epoch_event` and `validate_commit_epoch_payload`; move it to an optional
observability-only annotation field that is not validated as required; migrate callers.

Option A is lower risk (preserves backward compatibility with existing RC/devnet test
fixtures). Phase 1234 audits the call graph and recommends one option; Phase 1235
executes the chosen option after human review and GO.

---

## 5. vote_weight Float — Detail

### Confirmed state

- `epoch_state_runtime.py` Phase 444 canonical test vectors use Python float weights
- `finality_evaluator.py:199` does float arithmetic: `+= record["vote_weight"]`
- `circuit_breaker_interface.py:78` explicitly normalises to `float(vote_weight)`
- Genesis bootstrap (`validator_bootstrap_runtime.py:70`) enforces positive `int`
- RC path `epoch_state_cid` hashes `scenario_manifest`, NOT the quorum records —
  so IEEE 754 drift does not currently affect CID reproducibility in that path

### Scope for Phase 1234

Phase 1234 must determine whether `vote_weight` in the consensus finality path is:
- **Normalised stake fraction** (economic, must be Decimal/integer-ratio)
- **Voting power integer** (protocol, int is correct)
- **Synthetic test value** (test-only, no production path; float acceptable if isolated)

The genesis bootstrap path uses positive int, which suggests integer voting power is
the canonical intent. If `finality_evaluator` and `circuit_breaker_interface` are
on a production consensus path, they need integer ratios or Decimal before the
commit.epoch surface is promoted to production emission.

---

## 6. CDL Number Assignments

| CDL | Status | Scope |
|-----|--------|-------|
| CDL-087 | OPEN / PRELOCKED / NOT RATIFIED | Canonical fetch distribution policy |
| CDL-088 | RESERVED — do not open without explicit authorization | Next fresh number |

No new CDL openings are planned for Window 1233-1240.

---

## 7. Candidate Phase Table

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 1233 | Sequence lock | Gate | **SENSITIVE** |
| 2 | 1234 | commit.epoch audit: call-site inventory + vote_weight scope + mutation plan | Audit/spec | NON-SENSITIVE |
| 3 | 1235 | commit.epoch canonical runtime mutation | Runtime implementation | **SENSITIVE** |
| 4 | 1236 | commit.epoch emission connector spec/stub | Runtime implementation | **SENSITIVE** |
| 5 | 1237 | L3 sidecar infrastructure spec | Spec-only | NON-SENSITIVE |
| 6 | 1238 | SIM-FETCH-01 harness and design | Simulation | NON-SENSITIVE |
| 7 | 1239 | Coherence report + capsule v5.50 | Synthesis | NON-SENSITIVE |
| 8 | 1240 | Window closure gate | Gate | **SENSITIVE** |

Phase 1234 produces a written audit and mutation plan — no runtime edits.
Phase 1235 executes the mutation plan from Phase 1234; requires GO Phase 1235.
Lineage receipt / allowlist export tooling is moved to carry-forward (Window 1241+).

---

## 8. Sensitivity Classification

**SENSITIVE (require explicit human GO token before execution):**
- Phase 1233 — sequence lock; authorizes window phase order and sensitive boundaries;
  consistent with recent practice (Phase 1225 required GO Phase 1225)
- Phase 1235 — canonical runtime mutation on the commit.epoch emission path and
  finality vote_weight surface; touches protocol finalization semantics
- Phase 1236 — commit.epoch emission connector; finality-surface infrastructure even
  if production emission remains gated
- Phase 1240 — window closure gate; always SENSITIVE

**NON-SENSITIVE:**
- Phase 1234 — audit and plan only; no `ilc_core/` edits
- Phase 1237 — spec-only; no runtime mutation
- Phase 1238 — simulation harness; no ratification constants locked
- Phase 1239 — synthesis only

**Lineage receipt / allowlist export tooling** (`allowlist_export_procedure_defined_
required_before_public_repo_publication`) is deferred to Window 1241+. It is
public-release/export-adjacent and must not be treated as a casual tail-slot
implementation task. Requires explicit authorization before scheduling.

**No CDL mutation is planned for this window.** `ILC_CDL_MUTATION_AUTHORIZED` is not
required for any currently planned phase. If Phase 1238 SIM-FETCH-01 produces strong
evidence, CDL-087 ratification may be proposed for Window 1241+, but requires explicit
human authorization.

---

## 9. Scope Notes for Fixed Phases

**Phase 1233 — Sequence lock** SENSITIVE — requires `GO Phase 1233`.
Confirms Phase 1232 closure verdict, immutable diagnostic SHA, CDL-087 unratified
state, v0.2 deferred state. Records window baseline commits and publishes locked
phase order including the sensitivity corrections applied to this guidance doc.

**Phase 1234 — commit.epoch audit + mutation plan** NON-SENSITIVE.
Audit only — no runtime edits to `ilc_core/`. Deliverable is a written findings doc:
- Complete call-site inventory for `make_commit_epoch_event` and
  `validate_commit_epoch_payload` (all callers, not just `economic_cycle_runtime`
  and `devnet_multi_epoch`)
- `vote_weight` scope determination: for each of `epoch_state_runtime.py`,
  `finality_evaluator.py`, `circuit_breaker_interface.py` — is this a production
  consensus path or test/devnet only? Does float enter hash or settlement computation?
- Proposed patch plan for Phase 1235 (Option A or B selection; which files change;
  which tests must be added or updated)
- Tests verifying the audit findings (e.g., confirming `_utc_now()` is called at
  the confirmed line numbers; confirming `vote_weight` float type in canonical vectors)
  but making no runtime changes

**Phase 1235 — commit.epoch canonical runtime mutation** SENSITIVE — requires `GO Phase 1235`.
Executes the Phase 1234 mutation plan:
- Introduce `make_canonical_commit_epoch_event` (no `created_at`)
- Mark `make_commit_epoch_event` `LEGACY_RC_ONLY`
- Migrate callers in `economic_cycle_runtime.py` and `devnet_multi_epoch.py`
- Apply `vote_weight` resolution per Phase 1234 findings (Decimal/int-ratio migration
  or test-only isolation markers as determined)

**Phase 1236 — commit.epoch emission connector** SENSITIVE — requires `GO Phase 1236`.
Produce a canonical connector that reads from consensus epoch-state and settlement
inputs and produces a Phase-1226-compliant `commit.epoch` event. Production emission
remains gated — the connector must be present and tested but
`commit_epoch_projection_runtime_required_before_production_emission` is not closed
until production emission is explicitly authorized in a future phase.

**Phase 1237 — L3 sidecar infrastructure spec** NON-SENSITIVE.
Spec-only. Define: sidecar boundary (read-only, no mutation authority), graph
projection consumption interface, privacy constraints, agent-vs-human visualisation
posture. No runtime mutation.

**Phase 1238 — SIM-FETCH-01 harness and design** NON-SENSITIVE.
Design the simulation harness for CDL-087 fetch calibration. Define: metric names,
collection interval, scenario parameters, evidence format. May begin execution if
harness is complete and within phase scope. Results must be committed before any
CDL-087 ratification phase is opened.

**Phase 1239 — Coherence report + capsule v5.50** NON-SENSITIVE.
Standard synthesis. Records window delivery, open tokens, RC gate status. Coherence
report covers Phases 1233-1238.

**Phase 1240 — Window closure gate** SENSITIVE — requires `GO Phase 1240`.
Verifies all Phase 1233-1239 tokens, immutable diagnostic SHA, CDL-087 unratified,
v0.2 deferred. Issues `window_1233_1240_closure_gate_verdict=pass`.

---

## 10. Key Dependencies and Open Questions

1. **vote_weight production vs. test**: Is `finality_evaluator.py` on a live
   consensus path that feeds production commit.epoch emission, or is it test/devnet
   only? Phase 1234 audit answers this before Phase 1235 touches anything.
2. **commit.epoch Option A vs B**: Full call graph of `make_commit_epoch_event`
   callers must be mapped in Phase 1234 before Phase 1235 selects the migration
   approach. Phase 1234 §0c claim inventory must enumerate all call sites.
3. **SIM-FETCH-01 scope**: Does Phase 1238 only design the harness, or can it run
   and commit results? Depends on simulation runtime availability and phase capacity.

---

## 11. Non-Goals

This window does NOT:
- Ratify CDL-087 (gated on SIM-FETCH-01 evidence)
- Open any new CDL
- Execute v0.2 signing (no authorization token issued)
- Mutate Genesis Atlas or signed Genesis v0.1
- Authorize production commit.epoch emission (gated; requires separate authorization)
- Implement lineage receipt / allowlist export tooling (deferred to Window 1241+)
- Implement Dynamic Epistemic Traversal Engine (deferred to Window 1241+; forward-planning
  spec at `docs/specs/ilc_dynamic_epistemic_traversal_engine_forward_planning_1241_v0.1.md`;
  token `dynamic_epistemic_traversal_engine_forward_planning_recorded_phase_1233_1240`)
- Perform governance activation ceremony
- Implement L4 privacy / onion / SURB
- Begin cross-epoch compaction
- Close counsel carry-forward tokens (`counsel_license_instrument_selection_required_before_public_rc`,
  `counsel_cla_text_approved_required_before_external_contributors`,
  `counsel_trademark_policy_published_required_before_public_launch`) — human/counsel track
- Close `genesis_canonical_lineage_contract_required_before_public_rc` — ADR opening not assigned
- Migrate float surfaces in `temporal_decay_runtime.py`, `centrality_delta_gossip_runtime.py`,
  `routing_reputation_runtime.py` to Decimal (deferred; no window assigned)

---

## 12. Key Canonical Anchors for Prompt Drafting

| Artifact | Path |
|----------|------|
| Phase 1226 commit.epoch mapping spec | `docs/specs/ilc_commit_epoch_causal_frontier_mapping_spec_1226_v0.1.md` |
| CDL-087 prelock spec | `docs/specs/ilc_cdl_087_prelock_spec_1228_v0.1.md` |
| CDL-051 epoch finality | `docs/specs/ilc_cdl_051_*.md` |
| event_log.py (active wall-clock conflict) | `ilc_core/protocol/event_log.py:295-335` |
| economic_cycle_runtime (wall-clock callers) | `ilc_core/rc/economic_cycle_runtime.py:446,458` |
| epoch_state_runtime (float vote_weight vectors) | `ilc_core/consensus/epoch_state_runtime.py:25-62` |
| finality_evaluator (float arithmetic) | `ilc_core/consensus/finality_evaluator.py:199` |
| circuit_breaker_interface (float cast) | `ilc_core/consensus/circuit_breaker_interface.py:78` |
| validator_bootstrap_runtime (int enforcement) | `ilc_core/genesis/validator_bootstrap_runtime.py:70` |
| Canonical glossary | `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md` |
| Window 1225-1232 handoff | `docs/specs/ilc_window_1225_1232_handoff_1232_v0.1.md` |
