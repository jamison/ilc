# ILC Window 1225-1232: Candidate Phase Grouping

**Author:** Claude Code (local planning synthesis)
**Date:** 2026-05-06
**Baseline:** Window 1218-1224 CLOSED at Phase 1224 (`window_1218_1224_closure_gate_verdict=pass`,
`71a6d168`) + Phase 1224 Fix1 post-closure hardening (`052d62b5`). Fix1 restored TLS
verification defaults, bounded fetch/archive handling in `canon_bundle_key_registry_fetch.py`,
removed wall-clock serve epochs from `truth_primitive_fetch_runtime.py`, and restored the
sensitive-runtime coding taboo guardrail in `tools/check_sensitive_runtime_coding_taboos.py`.
Capsule v5.48 current. CDL-086 ratified. Truth-primitive permanence Genesis-attested. Fetch
distribution architecture reframed (`fetch_distribution_architecture_reframed_phase_1222`).
**Planning note:** Candidate grouping only. Phase 1225 sequence lock publishes the locked
order. Sensitive phases require explicit human GO. Phases 1226-1229 are the firm implementation
lane; Phase 1230 is a conditional tail slot (v0.2 signing); Phases 1231-1232 are fixed synthesis
and closure.

---

## 1. Window Identity and Scope

Window 1225-1232 is the **first RC3-adjacent window**. RC2 is effectively complete — five of
six gates are satisfied; only v0.2 signing remains open (skip-default). The primary obligation
of this window is not governance ratification but **implementation**:

1. Producing the `commit.epoch` causal frontier mapping specification — a firm carry-forward
   from Phase 1219 permanence attestation.
2. Opening CDL-087 (canonical fetch distribution policy) — the constitutional grounding for
   the Phase 1222 §8 reframing that repositions fetch reads as public verifiable infrastructure,
   not scarce peer admission.
3. Prelocking CDL-087 with a concrete spec of high-centrality caching, mirroring, and
   snapshot-distribution requirements.
4. Implementing the agent graph projection interface — the deterministic machine-native graph
   export committed as a design spec in Phase 1222 and now required as a runtime module.

**Character of this window:** implementation-heavy. Every non-sequence-lock, non-closure phase
must produce either a runtime token with tests, a constitutional spec with concrete field values,
or both. Standalone scoping phases are not permitted.

**Tail-slot policy:** Phase 1230 (v0.2 signing) is skip-default. It executes only if
`v0_2_signing_ceremony_authorized_phase_1230` is issued before the sequence lock or before that
phase executes. All other phases are firm.

---

## 2. Baseline and Inheritance

### Ratified CDL chain (current)

| CDL | Scope summary | Status |
|-----|---------------|--------|
| CDL-073 | Homoiconic bootstrap schema | ratified |
| CDL-074 | Truth primitive runtime | ratified |
| CDL-075 | Truth primitive graph persistence | ratified |
| CDL-076 | L1 announcement gossip | ratified |
| CDL-077 | L2 WANT-HAVE/WANT-BLOCK fetch; rate limiting | ratified |
| CDL-078 | L3 relay incentives / routing reputation | ratified |
| CDL-079 | L3 star.map N-gram route index | ratified |
| CDL-080 | L3 spectral routing | ratified |
| CDL-081 | Hyperedge ECU attribution | ratified |
| CDL-082 | (check register) | check register |
| CDL-083 | H-CON-02 panel quorum ejected stake | ratified |
| CDL-084 | Provenance decay α=0.45 / max depth=3 | ratified |
| CDL-085 | Werner φ-bound `EDGE_MINT_PHI_BOUND = Decimal("0.60")` | ratified |
| CDL-086 | Public-launch packaging blocker | ratified |

Next fresh CDL number: **CDL-087**

### Active runtime chain

| Module | Version token |
|--------|---------------|
| Epoch attribution | `epoch_attribution_settle_runtime_1210.v0.7` |
| Tier-3 runtime linkage | `tier3_runtime_linkage_runtime_1201.v0.1` |
| Persistent fetch rate limiter | `persistent_fetch_rate_limiter_runtime_1202.v0.1` |
| HTTP gossip transport | `http_gossip_transport_runtime_568.v0.1` |
| Gossip transport | `gossip_transport_runtime_558.v0.1` |

### Canonical anchors inherited

| Artifact | Token / hash |
|----------|-------------|
| Genesis v0.1 signed root envelope | `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c` |
| Immutable diagnostic SHA | `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56` |
| Genesis v0.2 candidate | 41-node / 73-edge; unsigned; signing deferred |
| Capsule | v5.48 (`c0d9e0a7`) |

---

## 3. Track Inventory

### 3.1 Constitutionally obligated (firm this window)

- `commit_epoch_causal_frontier_mapping_spec_required` — carry-forward from Phase 1219
  permanence attestation; must produce a concrete spec mapping CDL-051 epoch-state/quorum
  records and Genesis epoch-zero bootstrap into the `commit.epoch` ADR-0004 wire format;
  no wall-clock time; no float economics
- `fetch_distribution_architecture_reframed_phase_1222` → open CDL-087 for canonical fetch
  distribution policy; the Phase 1222 §8 reframing must be given constitutional grounding
  before any reciprocal scoring CDL can be opened in a future window
- `agent_graph_projection_interface_implementation_required_window_1225_plus` — carry-forward
  from Phase 1222 handoff; spec exists; runtime module required this window
- `l3_sidecar_infrastructure_spec_required_window_1225_plus` — carry-forward from Phase 1222
  handoff; design spec for how external apps attach to ILC; may be combined with CDL-087
  scope or deferred to a tail slot depending on phase pressure

### 3.2 Deferred governance (not this window unless tail slot permits)

- `genesis_canonical_lineage_contract_required_before_public_rc` — ADR-0037 accepted;
  operational lineage-receipt tooling not yet built; deferred to Window 1233+ unless a
  tail slot opens
- Genesis Canonical Lineage Contract operational tooling — requires allowlist export
  procedure, lineage-receipt format, and integration with release packaging; deferred
- `counsel_license_instrument_selection_required_before_public_rc` — parallel counsel lane;
  no codebase phases assigned; human/counsel track
- `counsel_cla_text_approved_required_before_external_contributors` — same
- `counsel_trademark_policy_published_required_before_public_launch` — same
- `allowlist_export_procedure_defined_required_before_public_repo_publication` — deferred
  to post-RC3 planning unless explicitly authorized earlier

### 3.3 Simulation-conditional (not this window)

- SIM-FETCH-01 (fetch distribution calibration) — required before CDL-087 ratification;
  not this window; CDL-087 opens and prelocks only; SIM in Window 1233+
- SIM-COMPACTION-01 — deferred; required before cross-epoch compaction CDL
- SIM-MONETARY-01 — deferred; prerequisite for CDL-070 PQ ceremony

---

## 4. CDL-087 — Canonical Fetch Distribution Policy

### 4.1 Scope

CDL-087 establishes the constitutional principle that **canonical content reads are public
verifiable infrastructure**, not per-requester admission decisions. It codifies the Phase 1222
§8 reframing and provides the governance foundation needed before any fetch admission CDL
(reciprocal scoring or otherwise) can be opened.

CDL-087 governs:

1. **High-centrality tier definition** — what artifacts constitute canonical public
   infrastructure: Genesis artifacts, ADR-0004 truth primitives, accepted CDLs and ADRs,
   manifests, lineage receipts, and epoch checkpoints.
2. **Caching and mirroring requirements** — high-centrality tier artifacts must be cached,
   mirrored, and snapshot-distributable; operators serving canonical artifacts must maintain
   local cache consistency.
3. **Snapshot distribution** — a valid ILC node must be able to acquire a Genesis-rooted
   verified snapshot and prove lineage without pulling every artifact live from a peer.
4. **Observability requirements** — before any admission scoring CDL can be opened, nodes
   must expose: request pressure per artifact tier, cache hit rates, serve pressure,
   non-cacheable request volume, and failure rates. No future reciprocal admission CDL may
   be ratified without this observability evidence.
5. **Read/write asymmetry rule** — canonical reads are publicly verifiable by content hash
   plus lineage proof; read validity does not depend on requester identity; serving nodes
   may apply operator-local abuse circuit breakers, but these are not constitutional
   admission gates; writes, mutations, publication, and economic recognition remain
   separately gated.
6. **Static rate limiter preservation** — CDL-077's WANT-BLOCK rate limiter remains active
   as an abuse circuit breaker; CDL-087 does not supersede it; it supplements by defining
   the caching/replication layer that reduces legitimate fetch pressure.

CDL-087 does NOT govern:
- Peer-to-peer block serving for non-cached or tail content (reserved for future CDL)
- Reciprocal scoring or ECU-escrow fetch admission (explicitly deferred pending SIM evidence)
- Gossip pull capacity (governed by CDL-060; separate lane)
- Write/mutation admission (governed by existing stake/reputation/CDL chain)

### 4.2 Q-set (Phase 1227 opening)

| Q | Question |
|---|----------|
| Q1 | What artifacts belong to the high-centrality canonical infrastructure tier? (Genesis, truth primitives, ADR/CDL chain, manifests, lineage receipts, epoch checkpoints — exact enumeration) |
| Q2 | What caching guarantees must operators maintain for high-centrality tier artifacts? (TTL, staleness bounds, consistency verification via content hash) |
| Q3 | What is the minimum snapshot format that allows a new node to bootstrap from a Genesis-rooted verified snapshot? (format, fields, lineage proof chain) |
| Q4 | What observability signals must a node expose before any future fetch admission CDL ratification is permitted? (exact metric names, collection interval, output format) |
| Q5 | Does CDL-077 require amendment, or does CDL-087 supplement without amending it? |

### 4.3 Rejected candidates

The following were considered and explicitly excluded from CDL-087 scope:

- Reciprocal scoring formula (Phase 1222 §2) — non-selected; requires SIM calibration
- ECU/stake escrow for fetch capacity — deferred; requires SIM evidence
- Puzzle/PoW fetch fallback — deferred; last-resort tool only
- Gossip admission (CDL-060 lane) — separate track; not this CDL

---

## 5. `commit.epoch` Causal Frontier Mapping

### 5.1 Obligation

Token `commit_epoch_causal_frontier_mapping_spec_required` was recorded at Phase 1219 during
truth-primitive permanence attestation. The obligation: define a concrete specification mapping
CDL-051 epoch-state/quorum records plus Genesis epoch-zero bootstrap into the ADR-0004
`commit.epoch` wire format.

This spec is not a CDL mutation. It is a design specification that resolves the open carry-forward
without touching signed Genesis v0.1 or mutating the CDL register. A future phase may open a CDL
or ADR to govern the production `commit.epoch` emission runtime — that is out of scope here.

### 5.2 Required spec content (Phase 1226)

The spec must answer all of the following with concrete field values (no "TBD" for items with
current best answers):

1. **Wire format fields** — exact fields of a `commit.epoch` envelope: epoch identifier,
   causal predecessor reference, quorum proof reference, Genesis domain hash, issuer
   (consensus layer only — no agent identifier), timestamp policy (no wall-clock; epoch
   sequence number only)
2. **Genesis epoch-zero mapping** — how Genesis epoch-zero bootstrap anchors into
   `commit.epoch` without CDL-051 quorum records (singleton causal frontier; Genesis
   authority as singleton consensus frontier; no agent identifier in the `commit.epoch`
   issuer field; no quorum required; `commit_epoch_agent_submission_rejected` applies
   unconditionally)
3. **Post-Genesis mapping** — how CDL-051 epoch-state records and quorum evidence map
   into `commit.epoch` fields for normal protocol epochs
4. **Non-agent-issuable boundary** — explicit restatement that `commit_epoch_agent_submission_rejected`
   remains active; this spec does not change that boundary
5. **Causal frontier definition** — what constitutes the causal frontier of a bounded
   computation slice in ILC's protocol semantics; how it is derived from validator quorum
   records without wall-clock time
6. **Constitutional routing** — whether this spec requires a new CDL or ADR for production
   runtime activation, or whether CDL-051 already governs it sufficiently; explicit
   carry-forward token if a new governance act is required

---

## 6. Agent Graph Projection Interface Runtime

### 6.1 Obligation

Token `agent_graph_projection_interface_implementation_required_window_1225_plus` was recorded
at Phase 1222 handoff. The design spec (`agent_graph_projection_interface_spec_committed_phase_1222`)
exists. This window produces the runtime module.

### 6.2 Scope

The agent graph projection interface is a **read-only, deterministic, machine-native** graph
export facility. It allows digital agents to acquire a structured, verifiable snapshot of the
ILC epistemic graph (or a shard of it) without requiring live peer connections for every query.

Required runtime capabilities:

- Export a subgraph bounded by: epoch range, node-type filter, provenance depth
- Output format: deterministic JSON with `sort_keys=True`; content-addressable (SHA-256 of
  canonical output verifiable against Genesis-lineage)
- Lineage proof: each export includes the envelope hash chain back to Genesis root
- No float arithmetic anywhere in export or hash computation
- No wall-clock timestamps in export content (epoch sequence numbers only)
- OOM guard: bounded export size; hard cap enforced before building output in memory
- No `assert` for production constraints

Runtime token: `agent_graph_projection_runtime_1229.v0.1` (proposed)

Hard pass condition: minimum 10 tests passing covering: determinism (same input → same
hash across calls), canonical hash (SHA-256 of sort_keys output), lineage proof chain
(envelope hash traces to Genesis root), subgraph filter by epoch range, subgraph filter
by node-type, provenance depth bound, export-size OOM cap (enforced before memory build),
invalid input rejection (malformed filter, out-of-range depth), no wall-clock/random/assert
invariant (verified via import inspection or static probe), no float leakage in any output
field.

---

## 7. CDL Number Assignments

| CDL | Title (candidate) | Decision digest anchor | Opening phase | Ratification phase |
|-----|-------------------|----------------------|---------------|-------------------|
| CDL-087 | Canonical fetch distribution policy | Q1-Q5 opened at Phase 1227; prelock resolution at Phase 1228 | Phase 1227 | Window 1233+ after SIM-FETCH-01 |

Note: CDL-087 opens and prelocks in this window. Ratification requires SIM-FETCH-01 evidence
(not this window). No ratification phase is assigned in Window 1225-1232.

---

## 8. Candidate Phase Table

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 1225 | Window sequence lock | Foundation / Constitutional | **SENSITIVE** |
| 2 | 1226 | `commit.epoch` causal frontier mapping spec | Constitutional / Runtime-prep | NON-SENSITIVE |
| 3 | 1227 | CDL-087 opening — canonical fetch distribution policy | Constitutional | **SENSITIVE** |
| 4 | 1228 | CDL-087 prelock + fetch distribution spec hardening | Constitutional | **SENSITIVE** |
| 5 | 1229 | Agent graph projection interface runtime implementation | Runtime | NON-SENSITIVE |
| 6 | 1230 | v0.2 signing ceremony (conditional — skip-default) | Conditional | **conditional** |
| 7 | 1231 | Coherence report + capsule v5.49 | Synthesis | NON-SENSITIVE |
| 8 | 1232 | Window closure gate | Gate | **SENSITIVE** |

### Conditional note on Phase 1230

**Default: skip.** Phase 1230 executes only if both tokens are issued before sequence lock or
before Phase 1230 executes:

```text
v0_2_signing_ceremony_authorized_phase_1230
GO Phase 1230
```

If either is absent, Phase 1230 records:

```text
v0_2_signing_ceremony_deferred_pending_signing_authorization
```

Phase 1230 is signing-ceremony work only. It does not open any CDL, mutate any runtime, or
produce release keys beyond those specified in ADR-0036.

Pre-execution SHA check required: Genesis v0.2 candidate SHA must be verified against the
unsigned candidate recorded in capsule v5.48 before any signing act.

### Note on Phase 1227 CDL mutation pattern

Phase 1227 opens CDL-087. CDL mutation environment required:

```
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1227
```

Phase 1227 has no runtime constant to introduce. CDL opening commit and any runtime-adjacent
work must be in separate commits per pre-commit hook enforcement.

### Note on Phase 1228 constitutional / SENSITIVE reclassification

Phase 1228 prelocks CDL-087. It resolves Q1-Q5 and locks scope — a constitutional act that
shapes the ratification path even though it does not mutate the CDL register. Per Codex
audit: prelock that resolves open questions and locks scope is sensitive regardless of
register-mutation status. Phase 1228 requires `GO Phase 1228`.

Phase 1228 does not produce a CDL register mutation, so no CDL mutation environment variable
is required. But it is SENSITIVE and requires explicit human GO before execution.

---

## 9. Sensitivity Classification

### SENSITIVE phases (require explicit GO token)

- **Phase 1225** — sequence lock; structural window boundary; requires `GO Phase 1225`
- **Phase 1227** — CDL-087 opening; CDL register mutation; requires `GO Phase 1227` +
  `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1227`
- **Phase 1228** — CDL-087 prelock; resolves Q1-Q5 and locks scope; constitutional act
  even without CDL register mutation; requires `GO Phase 1228`; no CDL mutation env var
  needed
- **Phase 1232** — window closure gate; requires `GO Phase 1232`

### NON-SENSITIVE phases (Codex may proceed after prompt approval)

- **Phase 1226** — spec only; no CDL mutation; no runtime mutation
- **Phase 1229** — runtime implementation in `ilc_core/`; no CDL mutation; separate commit
  from any CDL doc changes
- **Phase 1231** — coherence report and capsule; no CDL or runtime mutation

### Conditional phase rule

Before executing Phase 1230, confirm with human whether
`v0_2_signing_ceremony_authorized_phase_1230` has been issued. If yes: **SENSITIVE**, requires
`GO Phase 1230`; execute ADR-0036 signing sequence. If no: NON-SENSITIVE skip; record deferral
token; no further action.

### Pre-commit hook blocks

CDL mutation environment required for:

```
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1227   # Phase 1227 (CDL-087 opening)
```

No other phase in this window requires CDL mutation environment.

---

## 10. Scope Notes for Fixed Phases

### Phase 1225 — Window Sequence Lock

**SENSITIVE. Requires `GO Phase 1225`.**

Deliverables:

- `docs/specs/ilc_phase_1225_1232_sequence_lock_v0.1.md` — records locked phase order,
  incoming carry-forward tokens, immutable SHA pre-check, RC2/RC3 gate status at window entry,
  and next fresh CDL number (CDL-087)

Required sequence lock content:

- Carry-forward token inventory (all tokens listed in §3 above)
- Immutable diagnostic SHA pre-check: `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56`
- Genesis v0.1 root envelope hash: `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`
- RC2 gate status: 5 SATISFIED, 1 OPEN (v0.2 signing)
- Window character statement: implementation-heavy; no standalone scoping phases
- Next fresh CDL: CDL-087
- Note: `ilc_core/ledger/canon_bundle_key_registry.py` hardening was resolved before sequence
  lock in commit `21a5ad86`; Phase 1225 must record that it is no longer a dirty carry-forward

Test: `tests/test_phase_1225_sequence_lock.py` — minimum 3 tests (file exists, token present,
immutable SHA recorded correctly).

Token: `window_1225_1232_sequence_lock_committed`
Commit subject: `feat(g8): phase 1225 window 1225-1232 sequence lock`

---

### Phase 1226 — `commit.epoch` Causal Frontier Mapping Spec

**NON-SENSITIVE. No CDL mutation. No runtime mutation.**

Deliverables:

- `docs/specs/ilc_commit_epoch_causal_frontier_mapping_spec_1226_v0.1.md` — concrete spec
  satisfying the §5 content requirements above; no "TBD" for items with current best answers

Required content: all six items listed in §5.2. Key invariants the spec must enforce:

- No wall-clock time anywhere in `commit.epoch` wire format or causal frontier definition
- No float economics anywhere in epoch-state mapping
- `commit_epoch_agent_submission_rejected` boundary preserved verbatim
- Genesis epoch-zero explicitly handled as singleton causal frontier

Token: `commit_epoch_causal_frontier_mapping_spec_committed_phase_1226`
(consumes: `commit_epoch_causal_frontier_mapping_spec_required`)

Test: `tests/test_phase_1226_commit_epoch_mapping_spec.py` — minimum 4 tests (file exists,
token present, no-wall-clock assertion, agent-submission boundary recorded).

Commit subject: `docs(spec): phase 1226 commit.epoch causal frontier mapping spec`

---

### Phase 1227 — CDL-087 Opening

**SENSITIVE. Requires `GO Phase 1227` + CDL mutation environment.**

```
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1227
```

Two-commit pattern:

**Commit 1 — CDL register mutation only:**

- CDL register: CDL-087 status → OPEN
- Opening token: `cdl_087_canonical_fetch_distribution_policy_opened_phase_1227`
- Opening spec: `docs/specs/ilc_cdl_087_canonical_fetch_distribution_policy_opening_1227_v0.1.md`

Opening spec must include:
- CDL identity and motivation (Phase 1222 §8 reframing as explicit basis)
- Q1-Q5 question set (per §4.2 above)
- Scope boundary (what CDL-087 governs vs. what it explicitly excludes; per §4.1 and §4.3)
- Dependency chain: CDL-077, CDL-086, ADR-0037, Phase 1222 `fetch_distribution_architecture_reframed_phase_1222`
- Non-ratifying boundary statement: ratification requires SIM-FETCH-01 evidence

**Commit 2 — any non-CDL supporting material** (e.g., supporting spec drafts, test stubs);
may be empty if Commit 1 is self-contained.

Test: `tests/test_phase_1227_cdl_087_opening.py` — minimum 3 tests (CDL-087 status OPEN in
register, opening spec file exists, opening token present).

Token: `cdl_087_canonical_fetch_distribution_policy_opened_phase_1227`
Commit subject: `feat(cdl): open CDL-087 canonical fetch distribution policy (Phase 1227)`

---

### Phase 1228 — CDL-087 Prelock + Fetch Distribution Spec Hardening

**SENSITIVE. Requires `GO Phase 1228`.** No CDL register mutation (no CDL mutation env var
required), but resolving Q1-Q5 and locking scope is a constitutional act.

Deliverables:

- `docs/specs/ilc_cdl_087_prelock_spec_1228_v0.1.md` — records Q1-Q5 resolutions (from
  Phase 1227 opening deliberation), locks scope, and enumerates ratification conditions

Required prelock content:

- Q1-Q5 resolutions with concrete values (no "TBD" for resolvable items)
- High-centrality tier artifact enumeration (exact list per Q1)
- Caching guarantee spec (schema, staleness detection mechanism, content-hash verification
  per Q2; numeric TTL/staleness constants are provisional/candidate defaults until
  SIM-FETCH-01 calibration; lock schema and proof format now, not numeric policy)
- Minimum snapshot format fields (per Q3)
- Required observability signals (exact metric names per Q4)
- CDL-077 relationship: supplement vs. amendment decision (per Q5)
- Ratification conditions: SIM-FETCH-01 pass required; implementation required; parallel
  operation window with static limiter; no unlimited fetch path in regression tests
- Non-bypass rule: static limiter (`transport_abuse_circuit_breaker_not_final_scaling_policy`)
  remains active until CDL-087 is fully ratified

Historical prelock hardening: Phase 1228 must include a test that reads the CDL-087 register
row at the Phase 1227 opening commit ref and asserts `"status": "open"` (or equivalent).

Test: `tests/test_phase_1228_cdl_087_prelock.py` — minimum 5 tests (prelock file exists,
prelock token present, Q1-Q5 all resolved, ratification conditions listed, historical opening
state verified at Phase 1227 commit ref).

Token: `cdl_087_prelock_committed_phase_1228`
Commit subject: `docs(cdl): CDL-087 prelock committed (Phase 1228)`

---

### Phase 1229 — Agent Graph Projection Interface Runtime

**NON-SENSITIVE. Runtime mutation in `ilc_core/`. No CDL mutation.**

Runtime mutation commit must be separate from any CDL doc commits (pre-commit hook
enforcement). Phase 1229 has no CDL mutation, so the separation constraint is satisfied by
construction.

Deliverables:

- `ilc_core/graph/__init__.py` and `ilc_core/graph/agent_graph_projection_runtime.py`
  (new approved subpackage; read-only, deterministic, no I/O by default)
- `tests/test_phase_1229_agent_graph_projection_runtime.py` — minimum 10 tests (hard pass condition; see §6.2)

Phantom edit guard: Before committing, verify runtime version token in
`ilc_core/graph/agent_graph_projection_runtime.py` matches the committed value. If
any background test run includes a mutation canary probe, commit the module first before
running the full suite.

Required runtime properties (per §6.2):

- `AGENT_GRAPH_PROJECTION_RUNTIME_VERSION = "agent_graph_projection_runtime_1229.v0.1"`
- All output: `json.dumps(..., sort_keys=True)` — no insertion-order output
- No float arithmetic in graph export or hash computation
- No `random` import anywhere in module
- No `assert` for production constraints — `if not condition: raise ValueError("token")`
- OOM guard: hard export size cap enforced before building output in memory
- No wall-clock in export content

Token: `agent_graph_projection_runtime_1229.v0.1`
Commit subject: `feat(graph): phase 1229 agent graph projection interface runtime`

---

### Phase 1231 — Coherence Report + Capsule v5.49

**NON-SENSITIVE. Standard synthesis phase.**

Deliverables:

- `docs/specs/ilc_coherence_report_1231_v0.1.md` — records actual verdicts for Phases 1225-1230
- `docs/specs/ilc_antigravity_context_capsule_v5.49.md`

Capsule delta fields:

```
Version: v5.49
Supersedes: v5.48
Produced: Phase 1231, Window 1225-1232
Token: capsule_v5_49_supersedes_v5_48
```

Capsule must record:

- `commit.epoch` mapping spec status (`commit_epoch_causal_frontier_mapping_spec_committed_phase_1226`)
- CDL-087 status (OPEN + PRELOCKED; ratification deferred pending SIM-FETCH-01)
- Agent graph projection runtime token
- v0.2 signing status (executed or deferred)
- `fetch_distribution_architecture_reframed_phase_1222` direction confirmed; reciprocal
  scoring formula in Phase 1222 §2 is explicitly a non-selected research candidate, not the
  preferred direction
- Signed Genesis v0.1 immutability confirmed
- Immutable diagnostic SHA confirmed: `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56`
- MemPalace refresh disposition: local MemPalace active palace was stale as of Phase 1225;
  record whether it has been refreshed or remains advisory-only for Window 1225-1232
- Phase 1232 closure pending

Token: `capsule_v5_49_supersedes_v5_48`
Commit subject: `docs(capsule): phase 1231 coherence report and capsule v5.49`

---

## 11. Open Human Decisions

The following decisions have been **resolved** by Genesis authority and Codex audit before
Phase 1225:

1. **v0.2 signing authorization** — **DEFERRED.** Phase 1230 is skip-default. This window
   already contains `commit.epoch` mapping, CDL-087 opening/prelock, and graph projection
   runtime. Signing after those land cleanly is safer. Issue
   `v0_2_signing_ceremony_authorized_phase_1230` only if signing is to proceed; otherwise
   deferral token is refreshed automatically.

2. **`ilc_core/ledger/canon_bundle_key_registry.py` dirty change** — **RESOLVED: commit as
   standalone pre-Phase-1225 fix.** The diff is atomic-write hardening using unique temp
   files (same F4 pattern as Phase 1218b). Committed at `21a5ad86`; Phase 1225 should record
   it as resolved, not as an active dirty-file carry-forward.

3. **`ilc_core/graph/` subpackage** — **APPROVED.** Cleaner than `epistemic/`, `network/`,
   or `ledger/`. Constraints: module must be read-only, deterministic, no I/O by default,
   must include `__init__.py`. No circular imports from existing `ilc_core/` subpackages.

4. **L3 sidecar infrastructure spec** — **DEFERRED to Window 1233+.** Phase 1229 stays
   focused on machine-native graph projection for digital agents; sidecar UI/visualization
   infrastructure must not compete with that implementation in this window.

No open decisions remain for Phase 1225 sequence lock.

---

## 12. Known Patterns and Technical Constraints

### Novel patterns this window

- **First fetch distribution CDL (CDL-087):** CDL-087 supplements CDL-077 without amending it.
  This is the first CDL that explicitly codifies a "reads are public infrastructure" principle.
  Pattern: opening must cite Phase 1222 §8 reframing explicitly as motivation; prelock must
  enumerate SIM-FETCH-01 as a ratification gate.

- **First `ilc_core/graph/` subpackage (if new):** If `ilc_core/graph/` does not exist, Phase
  1229 creates it. Ensure `__init__.py` is present and the module is importable without circular
  imports from existing `ilc_core/` subpackages.

### Mutation canary risk — Phase 1229 runtime

The mutation canary at `tools/run_mutation_canary_phase_297.py` targets files in
`ilc_core/network/d2d/`. Phase 1229 targets a new `ilc_core/graph/` module — the canary should
not probe it directly. However: any background pytest run that includes the canary during Phase
1229 development must be run only after the module is committed, not while it has uncommitted
edits. Commit the runtime module before running the full suite.

### Historical prelock hardening (Phase 1228)

Phase 1228 must harden the prelock test to verify CDL-087's register row at the Phase 1227
opening commit ref. Do not rely on the current HEAD CDL register state — use `git show
<phase_1227_commit>:docs/specs/ilc_constitutional_decision_log_v0.1.md` and parse the CDL-087
row to assert `status: open`.

### JSON sort_keys invariant (Phase 1229)

Every `json.dumps()` call in `ilc_core/graph/agent_graph_projection_runtime.py` must include
`sort_keys=True`. The graph export is a content-addressed artifact — insertion-order variance
would break hash reproducibility.

### Closure gate selftest guard chain (Phase 1232)

Phase 1232 closure gate must include `ILC_PHASE_1232_GATE_SELFTEST=1` in its category-3
environment variable list. Read each prior gate test file rather than reasoning by analogy.
The selftest guard chain grows with each window — check the Phase 1224 closure gate as the
most recent reference implementation.

### PLANNING_INDEX stale-row cleanup (Phase 1232 pre-close task)

Before or during Phase 1232, sweep `docs/PLANNING_INDEX.md` for any remaining `⬅ CURRENT`
markers on superseded docs. Minimum checks:

- §1 table: confirm "Reciprocal fetch admission spec 1222" no longer marked CURRENT without
  its non-selected-candidate qualifier
- §4 table: confirm Launch Roadmap v0.9 is marked "(superseded by v1.0)", not CURRENT
- §1 footer note: confirm stale "Window 1176+ pending" note is updated to current frontier

Document the stale-row cleanup disposition in the Phase 1232 closure gate commit or in the
window handoff. This is a hygiene gate, not a blocking gate — it should not hold the closure
verdict, but it must be recorded as done or explicitly deferred with a carry-forward token.

---

## 13. Non-Goals and Explicitly Deferred Items

- No CDL-087 ratification this window — requires SIM-FETCH-01 evidence (Window 1233+)
- No reciprocal scoring CDL — non-selected research candidate; deferred pending simulation
- No L4 onion routing / SURB CDL — deferred to Window 1233+
- No cross-epoch compaction CDL — deferred; SIM-COMPACTION-01 required first
- No CDL-070 PQ migration ceremony — deferred; SIM-MONETARY-01 required first
- No public launch claim — CDL-086 ratification satisfies governance precondition only;
  separate constitutional acts required; none authorized this window
- No public repository publication — blocked by counsel carry-forwards
- No Genesis v0.1 mutation
- No v0.2 signing without explicit authorization token
- No external contributor onboarding
- No `genesis_canonical_lineage_contract_required_before_public_rc` implementation —
  deferred to Window 1233+
- No L3 sidecar infrastructure spec — deferred to Window 1233+ unless tail slot opens

---

## 14. Key Canonical Anchors for Prompt Drafting

- **Capsule v5.48** (PRIMARY) — `docs/specs/ilc_antigravity_context_capsule_v5.48.md`
- **Window 1218-1224 handoff** — `docs/specs/ilc_window_1218_1224_handoff_1224_v0.1.md`
- **Window 1218-1224 sequence lock** (format reference) — `docs/specs/ilc_phase_1218_1224_sequence_lock_v0.1.md`
- **Phase 1222 fetch reframing supplement** — `docs/specs/ilc_reciprocal_fetch_admission_model_spec_1222_v0.1.md` §8
- **Truth-primitive permanence ratification event** — `docs/specs/ilc_truth_primitive_permanence_ratification_event_1219_v0.1.md`
- **CDL register** — `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- **Phase completion log** — `docs/phases/STATUS.md`
- **ADR register** — `docs/adr/` (38 accepted through ADR-0037)
- **CDL-077** — `docs/specs/ilc_constitutional_decision_log_v0.1.md` row CDL-077 (rate limiting; CDL-087 supplements this)
- **CDL-051** — `docs/specs/ilc_constitutional_decision_log_v0.1.md` row CDL-051 (epoch-state/quorum records; Phase 1226 mapping basis)
- **ADR-0036** — `docs/adr/ADR_0036_Operational_Release_Key_Genesis_Binding.md` (for Phase 1230 if executed)
- **ILC Coding Security Standards** — CLAUDE.md §ILC Coding Security Standards (apply to Phase 1229 runtime)
- For closure gate (Phase 1232): all Phase 1225–1231 test files and artifacts

---

## 15. Rationale for Single-Window Scope

1. RC2 is effectively complete — this window enters RC3-adjacent territory; the natural
   character shift is from governance ratification to implementation.
2. `commit.epoch` mapping spec is a pre-existing carry-forward obligation with a clear scope;
   it fits comfortably in one NON-SENSITIVE phase.
3. CDL-087 opening + prelock is the right constitutional scope for this window; ratification
   requires SIM-FETCH-01 evidence that is not yet available; attempting ratification without
   simulation evidence would repeat the Phase 1222 design error.
4. Agent graph projection implementation is bounded and well-specified by the Phase 1222 spec;
   6 tests with a hard pass condition is achievable in a single runtime phase.
5. v0.2 signing is a conditional tail slot — it adds no phase pressure if not authorized.
6. Window 1233+ takes up L4, compaction, multi-hop attribution CDL, and SIM-FETCH-01.

Carry-forward caveat: if Phase 1229 agent graph projection runtime proves more complex than
expected (e.g., `ilc_core/graph/` subpackage requires significant scaffolding), Phase 1229
may be split into a scaffolding commit and a runtime commit within the same phase allocation.
The phase count does not change; the commit pattern splits.
