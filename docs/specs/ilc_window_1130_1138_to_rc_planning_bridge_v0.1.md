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

## 3. Window Sequence: Here to RC

The following is a **candidate arc**, not a locked schedule. Each window guidance doc
requires human review before phases execute. Windows with SENSITIVE phases require explicit
GO tokens. Windows with CDL mutations require `ILC_CDL_MUTATION_AUTHORIZED`.

---

### Window 1139–1147: SIM-SPECTRAL-03 + Atlas Tier 1

**Character:** Simulation research + atlas patch. No CDL. No `ilc_core/` mutations.

**Primary lane:** SIM-SPECTRAL-03 — re-run SIM-SPECTRAL-02 Track A using the 31-node
Genesis core star map as the S1 topology seed. Compare slope distribution and gaming probe
results against the homoiconic 3-axiom baseline from Window 1130–1138. This is the
prerequisite for CDL-085 authorization.

**Secondary lane:** Atlas Tier-1 patch — add the ~10 missing authority-chain edges to the
curated seed, regenerate star map, and re-run GENESIS-COMPILE-01.

**Sequencing note:** Atlas Tier-1 (Phases 1140–1141) must complete and pass
GENESIS-COMPILE-01 checkpoint #1 **before** SIM-SPECTRAL-03 harness work begins. The
SIM-SPECTRAL-03 seed topology depends on the patched star map. Running the SIM before
the atlas is repaired would seed it with the incomplete graph.

| Phase | Topic | Sensitivity |
|-------|-------|-------------|
| 1139 | Sequence lock | NON-SENSITIVE |
| 1140 | Atlas Tier-1 curated seed patch + star map regeneration | NON-SENSITIVE |
| 1141 | **GENESIS-COMPILE-01 checkpoint #1** — post-Tier-1 atlas | NON-SENSITIVE |
| 1142 | SIM-SPECTRAL-03 harness update (31-node seed topology) | NON-SENSITIVE |
| 1143 | SIM-SPECTRAL-03 Run 01 | NON-SENSITIVE |
| 1144 | SIM-SPECTRAL-03 Run 01 disposition | NON-SENSITIVE |
| 1145 | SIM-SPECTRAL-03 Run 02 (if Run 01 warranted) | NON-SENSITIVE |
| 1146 | SIM-SPECTRAL-03 disposition + CDL-085 authorization recommendation | NON-SENSITIVE |
| 1147 | Coherence + capsule v5.39 + closure gate | **SENSITIVE** |

**GENESIS-COMPILE-01 checkpoint #1** (Phase 1141) target: basis-reachable core nodes
rises from 17/31 to ≥ 28/31 after Tier-1 edge additions. Interpret failures as missing
explicit graph edges first — the semantics may already imply the authority chain, but the
machine can only traverse what is explicitly encoded. Do not conclude from reachability
failures that the primitive basis is wrong.

**Expected CDL-085 outcome:** If SIM-SPECTRAL-03 shows materially improved S3 Sybil
discrimination under the Genesis seed (S3/S1 ratio < 0.60 rather than 0.647), Phase 1146
recommends CDL-085 authorization. Human GO token required before CDL-085 opens.

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

## 4. GENESIS-COMPILE-01 as Recurring Instrument

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

## 5. Key Sequencing Dependencies

```
Window 1130-1138 (current)
    ↓  Phase 1137 + 1138
Window 1139-1147 (SIM-SPECTRAL-03 + Atlas Tier 1)
    ↓  SIM-SPECTRAL-03 positive result needed
CDL-085 authorization (human GO token)
    ↓
Window 1148-1156 (CDL-085 opening + SIM-HYPEREDGE-01)
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

## 6. Open Questions for Human Review

Before committing to this arc, the following questions need human disposition:

| Question | Why it matters |
|----------|---------------|
| **H-011 patent gate timeline** | Determines whether star expansion CDL can open in Window 1166–1174 or must slip |
| **SIM-ECU-STABILITY-01 authorization** | Determines whether it runs alongside star expansion or separately |
| **ADR-0035 CDL number** | CDL-085 is Werner φ-bound. ADR-0035 CDL would be CDL-086 or next. Confirm sequence. |
| **Conley Index pre-RC1.0 deferral** | Is this a hard deferral or should a planning window be opened before RC? |
| **GENESIS-COMPILE-01 #4 threshold** | Is 60% runtime coverage the right RC gate threshold, or should it be higher? |
| **SIM-SPECTRAL-03 scope** | Should it re-run the full 333-entry matrix, or just Track A + gaming probes against Genesis seed? |

---

## 7. What This Is Not

This document is a planning bridge memo, not an approved guidance doc. It does not
authorize any phase to execute. The formal guidance document for Window 1139–1147 must be
produced following the standard schema (`docs/specs/ilc_window_guidance_doc_schema_v0.1.md`),
proposed to human (and Codex when available), and approved before phases execute.

`ilc_planning_bridge_window_1130_1138_to_rc_v0.1`
