# ILC Planning Bridge: Window 1130–1138 to RC

**Status:** Planning bridge memo — NON-BINDING; dependency map only; not a sequence lock
or guidance doc; requires human review and formal guidance doc drafting before any
Window 1139+ phase executes
**Date:** 2026-05-02
**Author:** Local architectural reviewer (Claude Sonnet 4.6)
**Scope:** Restate current window remainder, then sequence windows from here to RC with
GENESIS-COMPILE-01 as a recurring iterative feedback instrument.

---

## 1. Current Window Remainder: Window 1130–1138

Two phases remain. Neither requires a CDL mutation env var.

| Phase | Topic | Sensitivity | Status |
|-------|-------|-------------|--------|
| 1137 | Coherence report + capsule v5.38 | NON-SENSITIVE | **Pending** |
| 1138 | Window 1130–1138 closure gate | **SENSITIVE** | Requires human GO token |

### Phase 1137 additions vs. the original guidance doc

The window produced materially more than originally planned. Capsule v5.38 must record
all of it:

- Phase 1136A genesis morphogenic hypergraph atlas (curated seed, 31-node star map,
  decomposition recipes, GENESIS-COMPILE-01 diagnostic, 29 tests)
- Phase 1136 disposition: Scenario B advisory; β calibration probe; Track D threshold
- ADR-0035 §9 amendment (compositional primitive basis requirement)
- Markov/trace research memo and terminology reservation (GND-0034, GND-0035)
- ADR-0004 promoted to core star-map node with 7 PROVENANCE edges
- GENESIS-COMPILE-01 result: PARTIAL_WITH_STRUCTURAL_GAPS (31% file coverage, 17/31
  basis-reachable core nodes, 0 missing decomposition recipes)

The Phase 1138 closure gate tests must be updated to cover the atlas artifacts.

### Gate status entering Phase 1138

| Gate item | Status |
|-----------|--------|
| SIM-SPECTRAL-02 disposition committed | ✓ Phase 1136 (`95567e19`) |
| Atlas artifacts (Phase 1136A) | ✓ Phase 1136A (`61e9b7f8`) |
| GENESIS-COMPILE-01 diagnostic | ✓ Phase 1136A (`08facab6`) |
| Coherence report + capsule v5.38 | Pending Phase 1137 |
| Handoff doc | Pending Phase 1138 |

**Phase 1138 human review scope:** The closure gate human review should explicitly cover:
(a) the Scenario B Advisory verdict and the three conditions required before the metric
advances, and (b) the GENESIS-COMPILE-01 PARTIAL_WITH_STRUCTURAL_GAPS finding as a
carry-forward obligation — confirming that the gap is a graph-construction gap (missing
edges), not a primitive-basis failure, and that Tier 1–3 atlas work is the correct
response. Both of these were not in the original Window 1130–1138 guidance doc scope,
so the closure gate should explicitly acknowledge them.

---

## 2. Forward Obligation Summary (entering Window 1139+)

Obligations carried out of Window 1130–1138, ordered by dependency:

### Tier A — SIM-gated (must have SIM evidence before gate clears)

| Obligation | Gate condition | Current status |
|------------|---------------|----------------|
| CDL-085 Werner φ-bound | SIM-SPECTRAL-03 with Genesis seed must show positive before CDL opens | Disposition is Scenario B advisory; not yet sufficient |
| SIM-SPECTRAL-03 (or Fix2) | Human authorization | Recommended in Phase 1136 disposition §6 |

### Tier B — Atlas maturation (iterative; GENESIS-COMPILE-01 drives)

| Obligation | Description | Current state |
|------------|-------------|---------------|
| Tier-1 edge additions | ~10 edges to curated seed: close L2 basis-reachability gap (pubkey, keygen, policy GOVERNS chain) | Identified in compile diagnostic |
| Tier-2 ADR promotion | Add ADR-0019, ADR-0020 as core star-map nodes | Flagged as absent high-authority ADRs |
| Tier-3 runtime linkage | `schema:*` node class linking CDLs to runtime modules | Future window; new node class required |

### Tier C — Governance-gated (CDL/authorization required)

| Obligation | Gate | Status |
|------------|------|--------|
| Star expansion implementation CDL | H-011 patent assessment + human authorization | Blocked |
| SIM-HYPEREDGE-01 commissioning | CDL-083 ratified ✓; authorization needed | Awaiting planning window |
| ADR-0035 implementation CDL | Human authorization + implementation window | Direction accepted; implementation deferred |
| SIM-ECU-STABILITY-01 | Authorization needed | Candidate, not authorized |

### Tier D — RC prerequisites

| Obligation | Notes |
|------------|-------|
| Multi-agent testnet (20–30 agents) | G8/G9 milestone |
| RC substrate hardening | G13–G15 |
| Conley Index formalization | Deferred pre-RC1.0 |

---

## 3. G8 Governance-to-RC Gap Registry

As of Window 1130–1138 close, the GENESIS-COMPILE-01 diagnostic (Phase 1136A baseline,
commit `08facab6`) enumerated the following gaps between the current governance record and
what a fully compile-ready RC baseline requires. This registry is the authoritative
reference for gap-closing work across Windows 1139–1183. Each bucket maps to one or more
window-level obligations in §4 below.

**Note on interpretation:** The GENESIS-COMPILE-01 tool measures graph topology and
authority-path presence only — it does not test source file contents, runtime behavior,
or semantic correctness. A "gap" here means the machine cannot traverse a path in the
star map from the Genesis transition basis to a core node. It does not necessarily mean
the authority chain does not exist in intent. The canonical fix for Tier 1/2 gaps is to
make implicit authority chains explicit via new curated-seed edges.

---

### Gap Bucket 1 — Core Star-Map Nodes Not Yet Reachable from Genesis Basis (Tier 1)

**Scope:** 14 of 31 core star-map nodes are not reachable from the Genesis transition
basis via the currently encoded edges in the curated seed
(`docs/sims/sim_spectral_02/genesis_core_star_map_curated_seed_v0.1.json`). This is a
graph-construction gap: the authority chains exist semantically but are not explicitly
encoded as edges. The diagnostic classified this as an L2 basis-reachability gap — not
an L1 basis failure (the primitive basis itself is intact).

**Unreachable nodes as of baseline checkpoint #0:**

| Node ID | Node type | Root cause | Authority chain needed |
|---------|-----------|------------|----------------------|
| `artifact:genesis_agent1_pubkey_record_838a` | artifact | No edge from genesis ceremony to artifact record | `ceremony:genesis_agent1_keygen_838a → PRODUCES → artifact:genesis_agent1_pubkey_record_838a` |
| `ceremony:genesis_agent1_keygen_838a` | ceremony | No edge from genesis basis to ceremony node | `genesis_basis → INITIATES → ceremony:genesis_agent1_keygen_838a` |
| `policy:genesis_accrual_governor` | policy | Not connected to any basis-reachable node | `genesis_basis → GOVERNS → policy:genesis_accrual_governor` |
| `policy:genesis_authority_sunset` | policy | Not connected to any basis-reachable node | `genesis_basis → GOVERNS → policy:genesis_authority_sunset` |
| `policy:genesis_theta_hard_0_05` | policy | Not connected to any basis-reachable node | `genesis_basis → GOVERNS → policy:genesis_theta_hard_0_05` |
| `policy:genesis_theta_soft_exp_minus_3` | policy | Not connected to any basis-reachable node | `genesis_basis → GOVERNS → policy:genesis_theta_soft_exp_minus_3` |
| `policy:provenance_decay_alpha_0_45` | policy | Not connected to any basis-reachable node | `cdl:084_ratification → CONSTRAINS → policy:provenance_decay_alpha_0_45` |
| `cdl:081` | cdl | No edge linking CDL-081 into basis-reachable subgraph | `ratification_ceremony → PRODUCES → cdl:081` |
| `cdl:083` | cdl | No edge linking CDL-083 into basis-reachable subgraph | `ratification_ceremony → PRODUCES → cdl:083` |
| `cdl:084` | cdl | No edge linking CDL-084 into basis-reachable subgraph | `ratification_ceremony → PRODUCES → cdl:084` |
| `adr:0029` | adr | No edge linking ADR-0029 into basis-reachable subgraph | `governance_decision → PRODUCES → adr:0029` |
| `adr:0030` | adr | No edge linking ADR-0030 into basis-reachable subgraph | `governance_decision → PRODUCES → adr:0030` |
| `adr:0032` | adr | No edge linking ADR-0032 into basis-reachable subgraph | `governance_decision → PRODUCES → adr:0032` |
| `adr:0035` | adr | No edge linking ADR-0035 into basis-reachable subgraph | `governance_decision → PRODUCES → adr:0035` |

**Root cause:** The curated seed encodes approximately 35 edges, but the authority-chain
edges that connect CDL ratification ceremonies, genesis keygen ceremonies, and policy nodes
to the genesis transition basis are missing. Approximately 10 additional explicit edges
are needed to close this gap.

**Closure window:** Window 1139–1147, Phase 1140 (Atlas Tier-1 curated seed patch).

**Closure verification:** GENESIS-COMPILE-01 checkpoint #1 (Phase 1141) must show
`basis_reachable_core_nodes ≥ 28/31`. The target is not 31/31 at this checkpoint because
some nodes (e.g., `adr:0035` — implementation deferred pending CDL opening) may
legitimately remain unlinked until their governing CDL opens.

**Success condition:** After Tier-1 patch, the following paths must be traversable:
(1) genesis basis → genesis keygen ceremony → pubkey artifact;
(2) genesis basis → policy governance chain for all 4 genesis policy nodes;
(3) CDL-081/083/084 ratification linked via PRODUCES edges from their ratification
ceremony nodes;
(4) ADR-0029/0030/0032 linked via PRODUCES or GOVERNS edges.

---

### Gap Bucket 2 — High-Priority ADRs Not Yet in Core Star Map (Tier 2)

**Scope:** 10 high-authority ADRs that govern significant portions of the ILC protocol
are not represented as nodes in the Genesis core star map. These ADRs have established
governance records and are referenced frequently across the repo, but were not included
in the minimal Phase 1136A curated seed.

**Unrepresented ADRs (priority order):**

| ADR | Governance domain | Why it belongs in core star map | Target window/phase |
|-----|-------------------|--------------------------------|---------------------|
| ADR-0019 | Graph-native governance compilation boundary | Directly motivates GENESIS-COMPILE-01 itself; defines the thesis that the governance graph should compile the protocol. Without this node, the star map cannot explain its own diagnostic tool. | Window 1148, Phase 1151 |
| ADR-0020 | Knowledge-node-first architecture | Establishes the knowledge node as the primitive unit of the hypergraph — the epistemic atom that SIM-SPECTRAL-02 measures. Required before Tier-3 runtime linkage for `embedding_pipeline.py` and `node_value_governance_conformance.py`. | Window 1148, Phase 1151 |
| ADR-0022 | Epoch-boundary finality claims | Governs the epoch-boundary witness lane (CDL-057). Without this node, the star map cannot explain epoch finality claims or `freshness_gate.py`. | Window 1148, Phase 1151 |
| ADR-0012 | Staking and unbonding policy | High-frequency governance surface; stake decisions in CDL-046/055 depend on this. Foundational to validator economics. | Window 1148, Phase 1151 |
| ADR-0026 | HTTP gossip transport architecture | Governs CDL-061 and the gossip transport layer. Without this, the star map cannot explain gossip transport as a governed subsystem. | Window 1148, Phase 1151 |
| ADR-0031 | Convergence window and SIM-LEAKAGE-01 synthesis | M-series milestone anchor. Documents convergence planning decisions (M-021, M-022 completion conditions). | Window 1148, Phase 1151 |
| ADR-0023 | Simulation synthesis and P_e governance | Documents P_e calibration decisions from SIM-009. Governs Treasury governor parameter selection (CDL-050). | Window 1148, Phase 1151 |
| ADR-0028 | Aesthetic panel architecture (Register 2) | Governs CDL-059. Without this, the star map cannot explain aesthetic diversity as a governed subsystem. | Window 1148, Phase 1151 |
| ADR-0034 | [Content TBD — confirm with Codex before promotion] | Flagged by GENESIS-COMPILE-01 crawl as high-authority; content review required | Confirm in Window 1148 guidance doc |
| ADR-0008 | [Content TBD — confirm with Codex before promotion] | Flagged by GENESIS-COMPILE-01 crawl as high-authority; content review required | Confirm in Window 1148 guidance doc |

**Root cause:** The Phase 1136A curated seed was designed to be minimal and correct rather
than comprehensive. It prioritized CDLs directly relevant to the SIM-SPECTRAL-02 research
stream. Tier-2 promotion requires explicit node and edge additions for each ADR plus
GOVERNS/CONSTRAINS edges to the protocol surfaces they govern.

**Closure window:** Window 1148–1156, Phase 1151 (Atlas Tier-2 patch). The Window 1148
guidance doc should scope the full 10-ADR promotion list, not just ADR-0019 and ADR-0020.
ADR-0034 and ADR-0008 require a content review pass before promotion; schedule that review
in Phase 1148 (sequence lock) or the guidance doc drafting phase.

**Closure verification:** GENESIS-COMPILE-01 checkpoint #2 (Phase 1152) target:
high-authority unlinked ADR count drops from 10+ to ≤ 3 (all 8 confirmed ADRs promoted;
ADR-0034 and ADR-0008 disposition resolved).

**Success condition:** After Tier-2 patch, all confirmed high-authority ADRs appear as
core star-map nodes AND have at least one GOVERNS or CONSTRAINS edge connecting them to
the CDL or runtime subgraph they govern.

---

### Gap Bucket 3 — Runtime Modules Not Yet Linked to Governance (Tier 3)

**Scope:** 8 `ilc_core/analysis/` modules that implement significant protocol-runtime logic
are not reachable from any governance node in the star map. These modules contribute to
the observed `506/1,623` source file coverage count, but the star map cannot explain
their governance authority because the `schema:*` / `runtime:*` node class does not yet
exist in the star-map vocabulary.

**Unlinked runtime modules:**

| Module | Path | Governing CDL/ADR | Why unlinked | Sequencing constraint |
|--------|------|-------------------|--------------|----------------------|
| `embedding_pipeline.py` | `ilc_core/analysis/embedding_pipeline.py` | ADR-0020 (knowledge-node-first) | ADR-0020 not yet in star map | Requires Tier-2 ADR-0020 promotion first |
| `freshness_gate.py` | `ilc_core/analysis/freshness_gate.py` | CDL-057, ADR-0022 | No runtime node class; ADR-0022 not yet in star map | Requires Tier-2 ADR-0022 promotion first |
| `local_spectral_analytics.py` | `ilc_core/analysis/local_spectral_analytics.py` | CDL-085 (not yet open) | CDL-085 not yet ratified; cannot create IMPLEMENTS edge to unopened CDL | Requires CDL-085 ratification (Window 1157) before full linkage; use governance-stub node in interim |
| `node_value_governance_conformance.py` | `ilc_core/analysis/node_value_governance_conformance.py` | CDL-052 (Popperian gate), ADR-0020 | No runtime node class; ADR-0020 not yet in star map | Requires Tier-2 ADR-0020 promotion first |
| `node_value_kernel.py` | `ilc_core/analysis/node_value_kernel.py` | CDL-047 (treasury), CDL-084 (PROVENANCE) | No runtime node class; CDL-084 in star map but no runtime linkage | Tier-3 new node class required |
| `reuse_diversity_invariants.py` | `ilc_core/analysis/reuse_diversity_invariants.py` | CDL-081 (Hyperedge ECU attribution, `REUSE_ATTRIBUTION_RATE`) | No runtime node class; CDL-081 not yet basis-reachable (Tier-1 gap) | Requires Tier-1 CDL-081 edge addition first |
| `spectral_utils.py` | `ilc_core/analysis/spectral_utils.py` | CDL-085 (not yet open) | Same as `local_spectral_analytics.py` | Requires CDL-085 ratification (Window 1157) before full linkage |
| `utility_flow_rewards.py` | `ilc_core/analysis/utility_flow_rewards.py` | CDL-047 (treasury), CDL-081 (attribution chain) | No runtime node class; CDL-081 not yet basis-reachable (Tier-1 gap) | Requires Tier-1 CDL-081 edge addition first |

**Root cause:** The `schema:*` and `runtime:*` node class does not yet exist in the
star-map vocabulary. Tier-3 work requires: (1) defining the new `runtime:*` node class in
the curated seed schema; (2) adding `runtime:*` nodes for each of the 8 modules above;
(3) adding IMPLEMENTS or GOVERNED_BY edges from each runtime node to its governing CDL/ADR
node. This cannot be done before Tier-2 because several governing nodes (ADR-0020,
ADR-0022) are not yet in the star map. Additionally, `local_spectral_analytics.py` and
`spectral_utils.py` cannot be fully linked until CDL-085 is ratified.

**Closure window:** Window 1166–1174, Phase 1168 (Atlas Tier-3: `schema:*` node class →
runtime module linkage). The Window 1166 guidance doc must note the CDL-085 sequencing
constraint for `local_spectral_analytics.py` and `spectral_utils.py`.

**Closure verification:** GENESIS-COMPILE-01 checkpoint #3 (Phase 1169) target: runtime
modules begin appearing in `core_explainable_sources` set; runtime coverage rises from
~4% to ≥ 30%.

**Success condition:** After Tier-3 patch, all 8 modules have at least one traversable
authority path from the Genesis transition basis through at least one CDL or ADR node to
the runtime node via an IMPLEMENTS or GOVERNED_BY edge. For `local_spectral_analytics.py`
and `spectral_utils.py`, a governance-stub node pointing to the pending CDL-085 ratification
is acceptable at checkpoint #3; full linkage by checkpoint #4.

---

### Gap Bucket 4 — High-Frequency CDL References Not Yet Core-Mapped (Review Queue)

**Scope:** 10 CDLs that are referenced most frequently across repo source files are not
represented as linked nodes in the Genesis core star map. High reference frequency
indicates they govern foundational or widely-used protocol surfaces. Their absence means
GENESIS-COMPILE-01 cannot explain the majority of the repo's CDL-governed source files.

**High-frequency CDL reference queue (ordered by reference count):**

| CDL | Ref count | Known governance domain | Priority | Target window |
|-----|-----------|------------------------|----------|---------------|
| CDL-017 | 816 | Validator-agent identity system: ValidatorID → AgentID; stake = ECU; reputation extends CDL-V chain; topology shuffles via jury machinery | **Tier-2 priority** — governs the fundamental agent identity model; absence means the star map cannot explain the most-referenced protocol surface | Window 1148, Phase 1151 alongside ADR-0019/0020 |
| CDL-001 | 534 | Genesis CDL (packaging track — open genesis_blocker) | **Tier-2 priority** — structurally foundational; inclusion in star map should record its open/blocked status as a node attribute | Window 1148 or standalone; confirm with Codex |
| CDL-019 | 295 | [Content TBD — confirm with Codex before scheduling] | Needs content review; third highest frequency implies widespread governance surface | Window 1148 guidance doc review pass |
| CDL-002 | 293 | [Content TBD — confirm with Codex before scheduling] | Fourth highest; needs content review | Window 1148 guidance doc review pass |
| CDL-007 | 259 | [Content TBD — confirm with Codex before scheduling] | Fifth highest; needs content review | Window 1148 guidance doc review pass |
| CDL-021 | 197 | [Content TBD — confirm with Codex before scheduling] | Sixth highest | Window 1148 guidance doc review pass |
| CDL-022 | 187 | [Content TBD — confirm with Codex before scheduling] | Seventh highest | Window 1148 guidance doc review pass |
| CDL-020 | 141 | [Content TBD — confirm with Codex before scheduling] | Eighth highest | Window 1148 guidance doc review pass |
| CDL-013 | 61 | [Content TBD — confirm with Codex before scheduling] | Ninth highest; still significant | Confirm with Codex |
| CDL-011 | 56 | [Content TBD — confirm with Codex before scheduling] | Tenth highest | Confirm with Codex |

**Root cause:** The curated seed was seeded with the CDLs most directly relevant to the
SIM-SPECTRAL-02 research stream and most architecturally central CDLs. The high-frequency
CDLs above span a broader set of governance surfaces not yet documented as core star-map
nodes. Many may also govern the runtime modules in Bucket 3.

**Recommended resolution process:** The Window 1148 guidance doc should include a CDL
content review pass as a named scope item. For each CDL in the queue, confirm:
(a) what protocol surface it governs;
(b) which `ilc_core/` modules or `docs/` paths are governed by it;
(c) what edge types to add (GOVERNS, CONSTRAINS, PRODUCES, IMPLEMENTS);
(d) whether it belongs in the current Tier-2 pass or a future Tier-N pass.

CDL-017 and CDL-001 are clearly Tier-2 priority and should be added in Phase 1151 alongside
the ADR promotions. CDL-019/002/007/021/022/020 require content review before scheduling.
CDL-013/011 require content review and may be lower priority if their governance surfaces
are already explained by higher-priority CDL/ADR promotions.

**Closure window:** Spans multiple windows. CDL-017 and CDL-001 target Window 1148
Phase 1151. Remaining 8 CDLs: content-review disposition in Window 1148 guidance doc;
scheduling in Window 1148–1157 depending on content.

**Success condition:** At GENESIS-COMPILE-01 checkpoint #2 (Phase 1152), CDL-017 and
CDL-001 appear as core star-map nodes with at least one authority-path edge each. The
remaining 8 CDLs have each received a written content-review disposition in the
Window 1148 guidance doc (promote / defer / out-of-scope).

---

### Gap Bucket 5 — Config/Install/Support Docs Not Linked to Governance (Support Graph)

**Scope:** A set of config, install, support, and archival documents in the repo are
observed by GENESIS-COMPILE-01 as source files but cannot be explained by the core star
map. Unlike Buckets 1–4, these are not gaps in constitutional coverage — they are gaps
in the support/auxiliary coverage ratio that affects the observed
`core_explainable_sources_ratio`. Resolving Bucket 5 is primarily a **denominator
question** rather than a gap-closing question.

**Unlinked support file categories:**

| Category | Example paths | Nature of gap | Resolution approach |
|----------|--------------|---------------|---------------------|
| Config/install READMEs | `config/README.md`, `config/mysticeti_testnet_M009/README.md` | Operational configuration docs not governed by any star-map node | Create `ops:*` or `config:*` node class; link via DOCUMENTS edge from a genesis configuration policy node. Target: Window 1166+ or RC prep window. |
| Historical capsule docs | `docs/specs/ilc_antigravity_context_capsule_v5.*.md` (superseded versions) | Superseded; not governed by current nodes | Add a `capsule:history` meta-node with SUPERSEDED_BY chain edges, or explicitly exclude from RC gate denominator. Low priority. |
| Window handoff docs | `docs/specs/ilc_window_*_handoff_*.md` | Process documentation, not constitutional | Declare as `process:handoff` class or explicitly exclude from RC gate denominator. Confirm denominator scope with human review before checkpoint #4. |
| Phase walkthroughs | `docs/phases/phase_*.md` | Retrospective execution records | Same as handoff docs — likely out of RC gate denominator scope. Confirm with human review. |
| Antigravity task prompts | Phase prompt files in `docs/phases/` | Execution prompts, not constitutional artifacts | Likely out of RC gate denominator scope. Confirm with human review. |
| Research/simulation docs | `docs/sims/**/*.md` | SIM research documentation | Partially linked if the SIM is referenced by a governance obligation (SIM-SPECTRAL-02 is now referenced in capsule v5.38). Older SIMs may not be linked. |

**Denominator choices for GENESIS-COMPILE-01 checkpoint #4 (pre-RC gate):**

| Option | Scope | Tradeoffs |
|--------|-------|-----------|
| **Option A (narrow)** | `ilc_core/` protocol-runtime modules only | Clean and auditable; directly measures what matters for RC correctness; excludes governance docs from denominator |
| **Option B (medium)** | `ilc_core/` + CDL/ADR docs + current capsule | Covers governance record without inflating with historical/process docs |
| **Option C (broad)** | All files observed by the diagnostic | Maximum coverage signal; inflates denominator with files legitimately out-of-scope for RC |

**Recommendation:** Confirm denominator scope with human review before Window 1175 guidance
is drafted (see Open Questions in §8 of this document). Buckets 1–4 should be addressed
regardless of denominator choice — only Bucket 5 is denominator-sensitive.

**Closure window:** Primarily addressed in Phase 1178 (GENESIS-COMPILE-01 checkpoint #4,
pre-RC gate). However, the **denominator decision must be made earlier** — it should be
resolved as a named scope item in the Window 1175 guidance doc drafting, or as a standalone
human review item before Window 1175.

---

### Gap Registry Summary — Window-to-Gap Mapping

| Window | Phases | Gap buckets addressed |
|--------|--------|-----------------------|
| **1139–1147** | 1140–1141 | Bucket 1 (Tier-1 edge additions; 14 unreachable core nodes) |
| **1148–1156** | 1151–1152 | Bucket 2 (Tier-2 ADR promotions; 10 ADRs) + Bucket 4 (CDL-017, CDL-001 + review pass for CDL-019/002/007/021/022/020/013/011) |
| **1157–1165** | 1158–1159 | Bucket 3 partial (CDL-085 ratification unblocks `local_spectral_analytics.py` and `spectral_utils.py` governance-stub linkage) |
| **1166–1174** | 1168–1169 | Bucket 3 full (Tier-3 `runtime:*` node class + 8 module linkages) + Bucket 5 initial (config/ops node class if scoped) |
| **1175–1183** | 1178 | Bucket 5 final (pre-RC denominator confirmation + checkpoint #4 gate) |

---

## 4. Window Sequence: Here to RC

The following is a **candidate arc**, not a locked schedule. Each window guidance doc
requires human review before phases execute. Windows with SENSITIVE phases require explicit
GO tokens. Windows with CDL mutations require `ILC_CDL_MUTATION_AUTHORIZED`.

---

### Window 1139–1147: Run 02 Corrected Baseline + Atlas Tier 1 + SIM-SPECTRAL-03

**Character:** Simulation research + corrected baseline + atlas patch. No CDL. No
`ilc_core/` mutations.

**Corrected baseline requirement (ADDED — supersedes earlier framing):**

The Window 1130–1138 SIM-SPECTRAL-02 Run 02 data (`a93da4f9`, 2026-05-01 19:56) was
produced before the critical normalized-λ₂ / Greek-weights fix (`58c4687f`,
2026-05-02 07:47). The fix corrected two bugs that were silently active during all 333
Run 02 matrix entries:

1. `structural_impedance` was always zero for any connected graph (combinatorial λ₂
   was always > THETA_FLOOR). The V_t formula effectively ran as
   `V_t = el_x + mean_x + 0 + contention`.
2. α/β/γ/δ calibration parameters were not exposed in the CLI; all weights were
   hardcoded to 1.0.

The Phase 1136 disposition was written after the fix but interpreted pre-fix matrix data.
The β calibration probe (the only post-fix run) used the fixed harness, but it varied β
and α — it did not establish a corrected structural-impedance baseline.

**Consequence:** The Run 02 slope values (S1=+0.557, S2=+0.214, S3=+0.358, S4=+0.246,
G2=+0.481) are from a formula missing one of its four terms. The Scenario B advisory
conclusion — "S3 Sybil discrimination is unresolved; a topology-sensitive
Structural_Impedance term is needed" — was reached on data where that term was already
present in the spec but contributing exactly zero. The conclusion is not falsified, but
the baseline is not valid for comparison with SIM-SPECTRAL-03.

**Corrected baseline phase (Phase 1140):** Rerun the same 333-entry homoiconic Run 02
matrix using the fixed harness (`58c4687f`), same seed topology (3 Genesis axioms +
97 synthetic artifacts), same parameters (N=100, seeds 42/1337/2026). Publish a
corrected disposition addendum comparing old vs. corrected Run 02 slope values.

This isolates the formula change from the Genesis seed change. SIM-SPECTRAL-03 then
introduces only one new variable: the 31-node Genesis seed topology. The corrected Run
02 baseline — not the broken Run 02 — becomes the comparison baseline for SIM-SPECTRAL-03.

**Existing Scenario B advisory status:** Provisional and directionally useful. The
directional finding (S1 dominates by slope magnitude across all three topology tracks)
is likely to survive the corrected rerun. But the absolute slope values, the S3/S1
ratio threshold, and the CDL-085 gate condition must all be re-evaluated against the
corrected baseline before the advisory is treated as final.

**Phase sequencing:** Corrected Run 02 (Phase 1140) → corrected disposition addendum
(Phase 1141) → Atlas Tier-1 patch (Phase 1142) → GENESIS-COMPILE-01 checkpoint #1
(Phase 1143) → SIM-SPECTRAL-03 harness + runs (Phases 1144–1146) → closure (Phase 1147).

| Phase | Topic | Sensitivity |
|-------|-------|-------------|
| 1139 | Sequence lock | NON-SENSITIVE |
| 1140 | **SIM-SPECTRAL-02 Run 02 Fix2 corrected baseline** — rerun 333-entry matrix with fixed harness | NON-SENSITIVE |
| 1141 | Corrected Run 02 disposition addendum — compare old vs. corrected slopes; update Scenario B/C verdict | NON-SENSITIVE |
| 1142 | Atlas Tier-1 curated seed patch + star map regeneration | NON-SENSITIVE |
| 1143 | **GENESIS-COMPILE-01 checkpoint #1** — post-Tier-1 atlas | NON-SENSITIVE |
| 1144 | SIM-SPECTRAL-03 harness update (31-node Genesis seed topology) | NON-SENSITIVE |
| 1145 | SIM-SPECTRAL-03 Run 01 | NON-SENSITIVE |
| 1146 | SIM-SPECTRAL-03 disposition + CDL-085 authorization recommendation | NON-SENSITIVE |
| 1147 | Coherence + capsule v5.39 + closure gate | **SENSITIVE** |

**Notes on phase count:** If SIM-SPECTRAL-03 Run 01 warrants a Run 02, the window will
need to extend (1147 → 1148+) or Phase 1147 becomes the closure gate for a Run 01-only
disposition. The Window 1139 guidance doc should scope this explicitly.

**GENESIS-COMPILE-01 checkpoint #1** (Phase 1143) target: basis-reachable core nodes
rises from 17/31 to ≥ 28/31 after Tier-1 edge additions. Interpret failures as missing
explicit graph edges first — the semantics may already imply the authority chain, but the
machine can only traverse what is explicitly encoded. Do not conclude from reachability
failures that the primitive basis is wrong.

**CDL-085 gate condition (updated):** If SIM-SPECTRAL-03 shows materially improved S3
Sybil discrimination relative to the **corrected Run 02 baseline** (not the broken Run
02), Phase 1146 recommends CDL-085 authorization. The S3/S1 ratio threshold must be
re-established from the corrected Run 02 disposition addendum before it is used as a
gate. Human GO token required before CDL-085 opens.

---

### Window 1148–1156: CDL-085 + SIM-HYPEREDGE-01 Planning + Atlas Tier 2

**Character:** Constitutional (CDL-085 opening and prelock) + simulation planning +
atlas patch. `ILC_CDL_MUTATION_AUTHORIZED` required for CDL-085 phases.

**Primary lane:** CDL-085 Werner φ-bound epistemic efficiency KPI — opening, Q-set
definition, prelock.

**Secondary lane:** SIM-HYPEREDGE-01 commissioning and Run 01.

**Tertiary lane:** Atlas Tier-2 — promote ADR-0019 and ADR-0020 to core star-map nodes,
add governance-spine edges, re-run GENESIS-COMPILE-01.

| Phase | Topic | Sensitivity |
|-------|-------|-------------|
| 1148 | Sequence lock | NON-SENSITIVE |
| 1149 | CDL-085 opening | **SENSITIVE** |
| 1150 | CDL-085 Q-set definition + prelock | **SENSITIVE** |
| 1151 | Atlas Tier-2 patch (ADR-0019, ADR-0020 + governance-spine edges) | NON-SENSITIVE |
| 1152 | **GENESIS-COMPILE-01 checkpoint #2** — post-Tier-2 atlas | NON-SENSITIVE |
| 1153 | SIM-HYPEREDGE-01 harness + commissioning | NON-SENSITIVE |
| 1154 | SIM-HYPEREDGE-01 Run 01 | NON-SENSITIVE |
| 1155 | SIM-HYPEREDGE-01 Run 01 disposition | NON-SENSITIVE |
| 1156 | Coherence + capsule v5.40 + closure gate | **SENSITIVE** |

**GENESIS-COMPILE-01 checkpoint #2** (Phase 1152) target: high-authority unlinked ADR
count drops from 15+ to ≤ 8 (ADR-0019, ADR-0020 now linked; runtime modules still unlinked
until Tier 3).

---

### Window 1157–1165: CDL-085 Ratification + SIM-HYPEREDGE-01 Disposition + ADR-0035 CDL

**Character:** Constitutional (CDL-085 ratification, ADR-0035 CDL opening). Heavy.

| Phase | Topic | Sensitivity |
|-------|-------|-------------|
| 1157 | Sequence lock | NON-SENSITIVE |
| 1158 | CDL-085 ratification | **SENSITIVE** |
| 1159 | CDL-085 runtime implementation | NON-SENSITIVE |
| 1160 | SIM-HYPEREDGE-01 Run 02 + gaming probes | NON-SENSITIVE |
| 1161 | SIM-HYPEREDGE-01 disposition | NON-SENSITIVE |
| 1162 | ADR-0035 CDL opening (homoiconic type definition system) | **SENSITIVE** |
| 1163 | ADR-0035 CDL prelock (definition node drafts → ratified nodes) | **SENSITIVE** |
| 1164 | Coherence + capsule v5.41 | NON-SENSITIVE |
| 1165 | Closure gate | **SENSITIVE** |

**Note on ADR-0035 CDL:** This introduces `type="type_definition"` as a new NodeType and
converts the proposed atlas edge types (GOVERNS, CONSTRAINS, PRIMITIVE_INVOCATION) from
atlas proposals to ratified definition nodes. The CDL number is CDL-086 or next available.

---

### Window 1166–1174: Star Expansion + Atlas Tier 3 + SIM-ECU-STABILITY-01

**Character:** Depends on H-011 patent gate resolution. If H-011 cleared, star expansion
CDL opens. Atlas Tier-3 (runtime linkage) also belongs here.

**Gate condition:** H-011 patent assessment must be complete and human authorization
explicit before this window's SENSITIVE phases execute.

| Phase | Topic | Sensitivity |
|-------|-------|-------------|
| 1166 | Sequence lock | NON-SENSITIVE |
| 1167 | Star expansion CDL opening (if H-011 cleared) | **SENSITIVE (conditional)** |
| 1168 | Atlas Tier-3: `schema:*` node class → runtime module linkage | NON-SENSITIVE |
| 1169 | **GENESIS-COMPILE-01 checkpoint #3** — post-Tier-3 atlas | NON-SENSITIVE |
| 1170 | SIM-ECU-STABILITY-01 commissioning and Run 01 | NON-SENSITIVE |
| 1171 | SIM-ECU-STABILITY-01 disposition | NON-SENSITIVE |
| 1172 | Star expansion CDL ratification (if H-011 cleared) | **SENSITIVE (conditional)** |
| 1173 | Coherence + capsule v5.42 | NON-SENSITIVE |
| 1174 | Closure gate | **SENSITIVE** |

**GENESIS-COMPILE-01 checkpoint #3** (Phase 1169) target: `ilc_core/` runtime modules
begin appearing in core-explainable set. Runtime coverage rises from ~4% to ≥ 30%.
This is the first checkpoint where the "compiler-like" thesis can be meaningfully tested.

---

### Window 1175–1183: Multi-Agent Testnet + RC Prep (G8/G9 → G13)

**Character:** Operational/infrastructure rather than constitutional. Fewer SENSITIVE phases.

| Phase | Topic | Sensitivity |
|-------|-------|-------------|
| 1175 | Sequence lock + G8/G9 ops playbook | NON-SENSITIVE |
| 1176 | Multi-agent testnet bootstrap (3 machines → 7 agents → 20 agents) | NON-SENSITIVE |
| 1177 | Testnet stability run + laplacian/spectral validation | NON-SENSITIVE |
| 1178 | **GENESIS-COMPILE-01 checkpoint #4** — pre-RC gate | NON-SENSITIVE |
| 1179 | RC substrate hardening: security, determinism, settlement audit | NON-SENSITIVE |
| 1180 | Conley Index formalization (or explicit pre-RC1.0 deferral) | NON-SENSITIVE |
| 1181 | RC1.0 final coherence + capsule v5.43 | NON-SENSITIVE |
| 1182 | RC1.0 closure gate (full regression) | **SENSITIVE** |
| 1183 | RC1.0 handoff | NON-SENSITIVE |

**GENESIS-COMPILE-01 checkpoint #4** (Phase 1178) is the **pre-RC gate for the Genesis
graph**. Candidate targets (thresholds are placeholders — must be confirmed by human review
before being treated as gates):
- compile_coverage for runtime/schema source kinds: threshold TBD pending denominator
  clarification (all `ilc_core/`? protocol-runtime only? modules governed by ratified
  ADR/CDL surfaces only? the right denominator changes the number significantly)
- 0 core nodes without authority path
- 0 proposed edge types without ratified CDL definition node
- basis_reachable_core_nodes = 31/31

The 60% figure used elsewhere in this document is a **placeholder only**. It must not
become canon until the denominator is defined and a baseline measured. Confirm the
denominator scope with human review before Window 1175 guidance is drafted.

If checkpoint #4 fails against the agreed threshold, RC1.0 must be gated until the gap
is closed.

---

## 5. GENESIS-COMPILE-01 as Recurring Instrument

The diagnostic runs at four scheduled checkpoints plus any atlas-mutation window:

| Checkpoint | Phase | Trigger | Target metric | Gate role |
|-----------|-------|---------|---------------|-----------|
| #0 (baseline) | 1136A (`08facab6`) | First run | PARTIAL_WITH_STRUCTURAL_GAPS; 17/31 basis-reachable | Baseline only; not a gate |
| #1 (post-Tier-1) | 1141 | After Tier-1 curated seed patch | basis_reachable ≥ 28/31; L2 gap closed | Gate for Tier-2 work (failures = missing edges first, not failed primitives) |
| #2 (post-Tier-2) | 1152 | After ADR-0019/0020 promotion | high_authority_unlinked ADRs ≤ 8 | Gate for Tier-3 planning |
| #3 (post-Tier-3) | 1169 | After `schema:*` runtime linkage | runtime modules begin appearing in core-explainable | Gate for RC prep |
| #4 (pre-RC) | 1178 | Before RC1.0 gate | threshold TBD (denominator must be confirmed); 0 unpathed core nodes; 0 unratified proposed edges | Hard RC gate — threshold must be ratified before this phase |

**Running the diagnostic:** The tool already exists at
`tools/genesis_compile_coverage_diagnostic.py`. Re-running it after curated seed changes
requires regenerating the star map first:

```bash
python tools/crawl_genesis_node_candidates.py
python tools/compare_genesis_star_map_to_repo_graph.py
python tools/genesis_compile_coverage_diagnostic.py
```

**Interpreting change:** Compare `basis_reachable_core_nodes_ratio`,
`core_explainable_sources_ratio_of_observed`, and
`authority_path_valid_sources_ratio_of_core_explainable` across checkpoints.
A checkpoint that moves all three ratios up is a healthy promotion. A checkpoint that
moves only one ratio while leaving others flat indicates a surface-level linkage without
deep authority grounding.

**What the diagnostic does NOT test:** Source file contents, semantic correctness of
edges, or runtime behavior. It tests graph topology and authority-path presence only.
Do not use it as a substitute for functional tests or CDL evidence tests.

---

## 6. Key Sequencing Dependencies

```
Window 1130-1138 (CLOSED — Phase 1138, 961319bb)
    ↓
Window 1139-1147
    Phase 1140: Run 02 Fix2 corrected baseline (same matrix, fixed harness)
    Phase 1141: Corrected Run 02 disposition addendum
    Phase 1142: Atlas Tier-1 curated seed patch
    Phase 1143: GENESIS-COMPILE-01 checkpoint #1
    Phases 1144-1146: SIM-SPECTRAL-03 (harness + run + disposition)
    ↓  corrected Run 02 baseline established; SIM-SPECTRAL-03 positive result needed
CDL-085 authorization (human GO token)
    ↓
Window 1148-1156 (CDL-085 opening + SIM-HYPEREDGE-01 + Atlas Tier 2)
    ↓  CDL-085 prelock complete
Window 1157-1165 (CDL-085 ratification + ADR-0035 CDL)
    ↓  H-011 patent gate + human authorization
Window 1166-1174 (Star expansion + Atlas Tier 3)
    ↓  GENESIS-COMPILE-01 #3 passes
Window 1175-1183 (Testnet + RC prep)
    ↓  GENESIS-COMPILE-01 #4 passes
RC1.0
```

Hard-gated transitions (require explicit human GO before execution):
- CDL-085 opening: after SIM-SPECTRAL-03 disposition recommends it
- Star expansion CDL: after H-011 patent assessment + explicit authorization
- RC1.0 closure gate: after GENESIS-COMPILE-01 #4 passes

---

## 7. Open Questions for Human Review

Before committing to this arc, the following questions need human disposition:

| Question | Why it matters |
|----------|---------------|
| **Corrected Run 02 scope** | Should Fix2 rerun use the exact same 333-entry matrix and seeds (42/1337/2026), or a reduced scope? Recommend same matrix to allow slope-by-slope comparison. Confirm in Window 1139 guidance doc. |
| **Scenario B advisory status after corrected rerun** | If the corrected Run 02 shows materially different S3/S1 ratios, the existing advisory verdict must be revised before it is used as a CDL-085 gate input. Do not treat the Phase 1136 advisory as final until the corrected disposition addendum is complete. |
| **CDL-085 S3/S1 gate threshold** | The 0.647 ratio (and the < 0.60 gate target) came from pre-fix data. This threshold must be re-established from the corrected Run 02 baseline. Do not carry the 0.647 figure forward as a gate number. |
| **H-011 patent gate timeline** | Determines whether star expansion CDL can open in Window 1166–1174 or must slip |
| **SIM-ECU-STABILITY-01 authorization** | Determines whether it runs alongside star expansion or separately |
| **ADR-0035 CDL number** | CDL-085 is Werner φ-bound. ADR-0035 CDL would be CDL-086 or next. Confirm sequence. |
| **Conley Index pre-RC1.0 deferral** | Is this a hard deferral or should a planning window be opened before RC? |
| **GENESIS-COMPILE-01 #4 threshold** | Is 60% runtime coverage the right RC gate threshold, or should it be higher? |
| **SIM-SPECTRAL-03 scope** | Should it re-run the full 333-entry matrix, or just Track A + gaming probes against Genesis seed? Recommend at minimum Track A + all gaming probes (S3, G2) to give the CDL-085 gate condition a clean read. |

---

## 8. What This Is Not

This document is a planning bridge memo, not an approved guidance doc. It does not
authorize any phase to execute. The formal guidance document for Window 1139–1147 must be
produced following the standard schema (`docs/specs/ilc_window_guidance_doc_schema_v0.1.md`),
proposed to human (and Codex when available), and approved before phases execute.

`ilc_planning_bridge_window_1130_1138_to_rc_v0.1`
