# ILC Window Guidance Document Schema v0.1

**Author:** Claude Sonnet 4.6 (local architectural reviewer)
**Date:** 2026-03-16
**Reference implementation:** `docs/specs/ilc_window_424_433_candidate_phase_grouping_v0.1.md`

This schema defines the standard section structure and content requirements for ILC window guidance documents. It replaces the prior ad-hoc guidance brief format and the earlier candidate-phase-grouping format with a single unified document type.

---

## 1. Document type and naming convention

**File path:** `docs/specs/ilc_window_NNN_MMM_candidate_phase_grouping_vX.Y.md`

**Title:** `# ILC Window NNN-MMM: Candidate Phase Grouping`

**Required header fields:**
```
**Author:** <role>
**Date:** <date>
**Baseline:** Window NNN-1 CLOSED (Phase verdict). Key ratification state. Capsule version.
**Planning note:** This is a candidate grouping, not a locked sequence. Phases NNN-NNN+K are the hard minimum lane. Phases NNN+K+1–MMM-2 are conditional tail slots.
```

---

## 2. Standard section structure

The document has **mandatory sections** that appear in every window and **window-specific content sections** that are inserted between Sections 3 and the CDL assignment section. The mandatory section numbers shift to accommodate window-specific content.

### Mandatory sections (every window)

| Section role | Typical number | Content summary |
|---|---|---|
| Window identity and scope | 1 | Window name, strategic framing (1 paragraph), tail-slot policy statement |
| Baseline and inheritance | 2 | Ratified CDL chain, active runtime chain, canonical anchors inherited, next fresh CDL number |
| Track inventory | 3 | Three subsections: Constitutionally obligated / Deferred governance / Simulation-conditional |
| [Window-specific content] | 4..N | One section per active constitutional lane or governance branch (see below) |
| CDL number assignments | N+1 | Table: CDL / Title / Decision digest anchor / Opening phase / Ratification phase |
| Candidate phase table | N+2 | Table + conditional scenario notes + per-phase subsection notes (see Section 4 below) |
| Sensitivity classification | N+3 | SENSITIVE list with rationale / NON-SENSITIVE list / Conditional rule / Pre-commit hook |
| Scope notes for fixed phases | N+4 | One subsection per firm phase (SENSITIVE + NON-SENSITIVE); conditional phases excluded |
| Key dependencies and open questions | N+5 | Must-resolve at entry / Sequencing constraints / Open questions / Permanently deferred |
| Parallel administrative track | N+6 | If applicable; omit if no parallel track |
| Known patterns and technical constraints | N+7 | Novel patterns this window / Historical prelock hardening / Phantom edit guard / Selftest guard chain |
| Non-goals and explicitly deferred items | N+8 | Bulleted list of what is explicitly NOT in scope |
| Key canonical anchors for prompt drafting | N+9 | Bulleted list Codex should reference in every phase prompt |
| Rationale for single-window scope | N+10 | Numbered list; optional carry-forward caveat |

### Window-specific content sections

Insert between Section 3 (track inventory) and the CDL number assignments section. One section per active lane:

- For each new CDL being opened or ratified: scope section describing files targeted, rejected candidates, and non-goals (follow CDL-049 scope section pattern)
- For governance review branches (Treasury P_e, claim-form review, etc.): one section describing the branch trigger, the verdict structure, and how it drives conditional tail slots
- For runtime tracks: a scope section describing the new module, its location, and its dependency tokens

If a window has no window-specific content (e.g., pure closure gate window), the CDL number assignments section follows directly after Section 3.

---

## 3. Phase table specification

### Column order and names

```
| Order | Phase | Topic | Character | Sensitivity |
```

- **Order**: sequential 1-N within the window (integer)
- **Phase**: absolute phase number
- **Topic**: concise scope description (up to ~12 words)
- **Character**: one of — `Foundation / Constitutional`, `Constitutional`, `Governance review`, `Constitutional / Runtime-prep`, `Constitutional / Runtime`, `Runtime`, `Simulation`, `Synthesis`, `Gate`, `Conditional`
- **Sensitivity**: one of — `**SENSITIVE**`, `constitutional`, `NON-SENSITIVE`, `**conditional**`

### Sensitivity assignment rules

| Phase type | Sensitivity |
|---|---|
| Seq lock + CDL opening | **SENSITIVE** (CDL mutation, requires pre-commit hook) |
| Prelock hardening | `constitutional` (NON-SENSITIVE — no CDL mutation) |
| Governance review | `NON-SENSITIVE` |
| Ratification evidence assembly | `NON-SENSITIVE` |
| CDL ratification (doc-only) | **SENSITIVE** (CDL mutation) |
| CDL ratification (+ runtime mutation) | **SENSITIVE** (CDL mutation + runtime mutation) |
| Runtime implementation | `NON-SENSITIVE` |
| Simulation commissioning | `NON-SENSITIVE` |
| Coherence / synthesis | `NON-SENSITIVE` |
| Closure gate | **SENSITIVE** (structural boundary) |
| Conditional slot (possible CDL opening) | **conditional** |
| Conditional slot (prelock only, all scenarios) | `NON-SENSITIVE` |
| Conditional slot (possible CDL ratification) | **conditional** |
| Conditional slot (never touches CDL) | `NON-SENSITIVE` |

**Important:** Conditional slots must be analyzed per scenario. If all scenarios for a slot leave it NON-SENSITIVE (e.g., a prelock slot is always NON-SENSITIVE regardless of which CDL is being prelock-hardened), write `NON-SENSITIVE`, not `**conditional**`. Only write `**conditional**` when the slot is SENSITIVE in at least one plausible scenario.

### Phase table subsections

After the phase table, add named subsection notes for:

1. **Conditional note on Phases NNN-MMM** — enumerate each scenario (A1, A2, B, C, etc.) with explicit phase-by-phase assignments and carry-forward assumptions
2. **Note on Phase NNN non-ratifying boundary** — if applicable (governance review, evidence assembly)
3. **Note on Phase NNN runtime mutation pattern** — if applicable (CDL ratification that also patches a runtime file); include 5-path resolver spec and custom mutation-scope check requirements

---

## 4. Sensitivity classification section requirements

Must contain in order:

1. **SENSITIVE phases list** — bullet per phase with rationale (type of mutation authorized)
2. **NON-SENSITIVE phases list** — bullet per phase with rationale (what is NOT mutated)
3. **Conditional phases rule** — explicit decision rule: "before executing Phase NNN, confirm with human whether selected scenario assigns CDL mutation; if yes, require GO token; if no, NON-SENSITIVE"
4. **Pre-commit hook block** — literal env var syntax required for CDL mutations:
   ```
   ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=<phase>
   ```
   List which phases require it.

---

## 5. Scope notes for fixed phases requirements

One named subsection per firm phase (phases not conditional). Each subsection must include:

| Field | Required? | Notes |
|---|---|---|
| Sensitivity callout (SENSITIVE / NON-SENSITIVE + GO token rule) | Always | First line of subsection |
| Deliverables list | Always | All committed artifacts with file paths |
| Required content spec (for doc-only artifacts) | If applicable | Section names or content tokens |
| Test structure | Always | Pre-commit split (N+M), commit resolver path count |
| Pre-commit hook | SENSITIVE phases only | Exact env vars |
| Phantom edit guard | If runtime mutation possible | Target file(s), detection command, fix command |
| Commit subject | Always | Exact string |

Conditional phases (tail slots) are NOT given scope notes in this section. Their scope is covered in the phase table conditional note subsection.

---

## 6. Known patterns and technical constraints requirements

Include entries for:

1. **Novel patterns introduced this window** — anything that is "first time in ILC history" (e.g., first amendment-of-existing-runtime, first dual-CDL ratification, first combined prelock phase)
2. **Historical prelock hardening** — standard reminder that each ratification phase must harden the corresponding prelock test to assert `"status: open"` at the historical opening commit ref
3. **Phantom edit guard** — if any `ilc_core/` runtime file is a mutation target in this window; name the specific file(s), describe the canary risk, provide detection and fix commands
4. **Pre-commit hook ilc_core/ clean-state guard** — if runtime mutation phases are present
5. **Closure gate selftest guard chain** — full env var list required in category 3; explicit instruction to read each prior gate test file rather than reasoning by analogy

---

## 7. CDL number assignments table format

```
| CDL | Title (candidate) | Decision digest anchor | Opening phase | Ratification phase |
|-----|-------------------|----------------------|---------------|-------------------|
| CDL-NNN | <title> | `<key governance constants>` | Phase <N> | Phase <M> |
| CDL-NNN+1 | <title> (conditional) | TBD at Phase <K> | Phase <N+K> (conditional) | Phase <N+M> (conditional) |
```

Note below the table: which CDLs are pre-authorized vs. conditional and why.

---

## 8. Canonical anchors section content

Must always include:

- Current context capsule (PRIMARY label)
- Prior window closure handoff
- Prior window sequence lock (format reference for new sequence lock)
- CDL register (`ilc_constitutional_decision_log_v0.1.md`)
- Phase completion log (`STATUS.md`)
- ADM-003 reference agent architecture (carry-forward note)

Should include (if applicable this window):

- Any `ilc_core/` runtime file that is a mutation target
- Evidence artifact from prior window that authorizes current window work (e.g., SIM results, governance review artifact)
- Current prelock artifacts (for ratification phases)

Always close with:
- "For closure gate (Phase MMM): all Phase NNN–MMM-1 test files and artifacts."

Optional MemPalace retrieval appendix:
- guidance authors may add an optional MemPalace retrieval appendix or
  subsection that lists tier-scoped retrieval queries and rendered retrieval
  brief paths used during drafting
- if used, the appendix should also name the logic-gate profile
  `docs/tools/mempalace/ilc_mempalace_logic_gate_profile_v0.1.md` and state
  that retrieved material passed through those gates before being reused
- this appendix is advisory only and must not replace canonical anchors or
  direct repo reads
- if present, it should appear after the canonical anchors section or inside
  the known-patterns section as drafting support only

---

## 9. Evolution notes

This schema was derived from the Window 414-423 guidance brief and the expanded Window 424-433 candidate phase grouping. Earlier windows used different section structures:

- **Window 378-391**: Phase table had `Phase | Topic | Sensitivity | Character` (no Order column, different column order). No baseline/inheritance, sensitivity-classification, scope-notes, known-patterns, non-goals, or anchors sections. This format is superseded.
- **Window 392-413 candidate grouping** (`ilc_window_392_413_candidate_phase_grouping_v0.1.md`): Two-window planning doc format (table only, no scope notes or sensitivity section). This format is superseded for guidance purposes; the two-window planning format may still be used for early exploratory planning before a final guidance doc is written.
- **Window 414-423 guidance brief** (`codex_brief__phases_414_423_g8_...md`): Introduced most sections now in this schema (sensitivity classification, scope notes per phase, known patterns, non-goals, canonical anchors). This is the reference implementation.
- **Window 424-433** (`ilc_window_424_433_candidate_phase_grouping_v0.1.md`): First document conforming to this schema (adds Order column to table, adds Baseline/inheritance and Window-identity sections, consolidates candidate-phase-grouping and guidance-brief into a single file).

Going forward, a single `ilc_window_NNN_MMM_candidate_phase_grouping_vX.Y.md` document in `docs/specs/` serves as both the planning artifact and the Codex execution brief.
