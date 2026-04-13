# ADR-0024: Agent Skills Infrastructure

**Status:** Proposed
**Date:** 2026-03-30
**Authors:** Jamison (ILC), Claude Sonnet 4.6 (architectural review)
**Classification:** Infrastructure / cross-agent coordination — requires no CDL for Tier 1/2;
Tier 3 requires new CDL (skill versioning succession semantics in authored_envelope)
**Dependencies:** agentskills.io open standard (December 2025), CDL-034 (authored envelope
schema), CDL-052 (epistemic runtime), CDL-V7 (Popperian gate for skill versioning claims)

---

## Context

The Agent Skills open standard (published by Anthropic December 18, 2025, hosted at
agentskills.io) defines a cross-platform format for modular, reusable AI agent instruction
packages. Each skill is a directory containing a `SKILL.md` file with YAML frontmatter and
markdown instruction body, optionally bundled with supporting reference files and scripts.

The standard has been adopted by 26+ AI tools including Claude Code, OpenAI Codex, GitHub
Copilot, Cursor, and VS Code. A skill created for one tool is portable to others — making
the format a genuine lingua franca for agent procedural knowledge.

ILC's current agent collaboration architecture (Claude Code + Codex working on the same
repository) has no shared, version-controlled instruction layer below the level of
CLAUDE.md/MEMORY.md. There are recurring workflow patterns — CDL mutation commits,
phase prompt validation, closure gate selftest auditing — that are expressed in prose in
CLAUDE.md and must be re-discovered by each agent in each session. Packaging these as
skills would make them:

1. Cross-agent: both Claude Code and Codex instances can discover and invoke them
2. Invocable: `/skill-name` syntax, not just background context
3. Version-controlled: committed to the repository, reviewed like code
4. Testable: per Nate Jones's testing mandate — each skill can have a benchmark and be
   quantified across versions

A separate, longer-horizon question emerges from this work: whether ILC knowledge nodes
could serve as a native home for skill artifacts — making skills a first-class epistemic
object in the ILC graph, with succession versioning, benchmark-gated advancement, and ECU
attribution. This is architecturally coherent with ILC's design (CDL-V7 Popperian gate,
CDL-052 reuse centrality, CDL-034 authored envelope) but requires significant new
constitutional work and is explicitly deferred to Tier 3.

---

## Decision

Adopt the Agent Skills standard for ILC in three tiers.

### Placement: root `skills/` directory (not `.claude/skills/`)

Skills for this project live at `skills/` in the repository root, not `.claude/skills/`.
Rationale: `.claude/skills/` is Claude Code-specific. A root-level `skills/` directory is:

- Visible to any agent tool (Codex, Cursor, local agents, future tools) without platform
  configuration
- Obviously version-controlled and human-readable alongside other project directories
- Consistent with agentskills.io's cross-platform portability intent

For Claude Code to auto-discover skills at the root `skills/` path, either:
(a) add `.claude/settings.json` with the additional-directories configuration, or
(b) maintain a project-level `.claude/skills/` directory that is git-ignored and generated
    from `skills/` during setup, or
(c) rely on Claude Code's `--add-dir skills/` flag when relevant.

Option (c) is the zero-configuration path for now. If Claude Code updates to natively
support root `skills/` discovery (as the agentskills.io standard matures), this becomes
automatic.

---

### Tier 1 — Immediate: Workflow Skills (Window 545+ candidate)

Seven Group A workflow skills that formalize currently-prose patterns into invocable,
version-controlled instruction sets. All are `disable-model-invocation: true` (user-invoked
only — no side-effect surprises).

| Skill name | Formalizes |
|---|---|
| `phase-validate` | `python3 tools/validate_phase_prompt.py` against a named file |
| `phase-commit` | Two-commit sequence (main + backfill), exact subject format, clean ilc_core/ gate |
| `run-canary` | `python3 tools/run_mutation_canary_phase_297.py` |
| `cdl-status` | Live CDL inventory: ratified, open, reserved rows |
| `selftest-audit` | Closure gate selftest guard chain verification against all prior gate test files |
| `pre-flight-check` | `git diff HEAD -- ilc_core/` must be clean; CDL env vars not set |
| `cdl-open` | Scaffold a new CDL opening stub (new row, additive-only, correct pipe format) |

Each skill directory contains only `SKILL.md` at Tier 1 — no bundled scripts yet. Scripts
may be added in Tier 2 if the workflow complexity warrants it.

---

### Tier 2 — Near-Term: Scaffold Skills (Window 545-554 candidate)

Five Group B scaffold skills that generate boilerplate for ILC's most repetitive artifact
structures. These reduce error in routine phase construction and can be auto-invoked when
Claude detects the relevant context (`disable-model-invocation: false`).

| Skill name | Generates |
|---|---|
| `phase-test-scaffold` | 7-test 5+2 structure, commit resolver, exact-path assertions |
| `cdl-evidence-scaffold` | CDL ratification evidence artifact (standard section structure) |
| `sim-doc-scaffold` | SIM document 6-section structure with required governance token slots |
| `gate-scaffold` | Closure gate 6-category shell script structure with selftest guard chain |
| `coherence-scaffold` | Coherence report + capsule section structure |

Tier 2 skills will have supporting `templates/` subdirectories with reference examples.
These must be authored against verified, passing phase examples — not from memory alone.

---

### Tier 3 — Long-Term Research: skill_node as ILC Knowledge Node Subtype (Window 555+)

A separately scoped research track, documented in
`docs/research/ilc_skill_node_architecture_research_placeholder_v0.1.md`.

The core claim: a skill.md version claim like "v0.2 achieves ≥85% on benchmark B" is a
Popperian bounded-existential falsifiable statement — exactly the form CDL-V7 governs. If
skills are treated as ILC knowledge nodes, then:

- Each skill version is a CID-addressed authored_envelope with `skill_version` and
  `supersedes_cid` fields (requires CDL-034 schema extension)
- Version advancement requires a falsifiable benchmark claim (CDL-V7 Popperian gate)
- Accepted skill nodes gain reuse centrality (CDL-052) as downstream agents load them
- ECU attribution from passive reuse (Phase 542 formula) flows back to skill authors
- A Karpathy-style multi-agent improvement loop (spawn N candidates, run benchmark, select
  the best Popperian-qualifying variant) becomes the native skill optimization method

This is architecturally coherent but requires new constitutional work:
- authored_envelope succession semantics (CDL-034 extension or new CDL)
- benchmark protocol definition (what counts as a skill benchmark claim)
- The above is adjacent to CDL-053 (Werner credit) and the long-tail research track

Do NOT begin Tier 3 implementation before:
- Tier 1 skills are built and in operational use
- At least one skill has been manually tested and benchmarked
- CDL-053 Werner credit research track has produced evidence gates analysis

---

## Out of Scope

The following are explicitly excluded from this ADR:

**Do not migrate existing specs, evidence artifacts, or governance docs into skill folders.**
These are protocol artifacts (the product of the process), not agent instructions (how to
run the process). Conflating them creates confusion about what is constitutional text and
what is procedural guidance.

**Do not import community skills from agentskills.io, SkillsMP, or any external catalog.**
The ILC governance process involves sensitive CDL mutation guards, pre-commit hooks, and
constitutional text management. External skills execute arbitrary bash commands with full
repository access. The security surface is unacceptable without thorough per-skill audit.
Revisit after the community ecosystem matures and a trusted skill audit process exists.

**Do not conflate skills (agent instructions) with knowledge nodes (epistemic artifacts).**
This is the Tier 3 research question — keep them distinct until the succession semantics
are constitutionally designed.

**Do not use `.claude/skills/` as the canonical location.**
Cross-platform portability requires the root `skills/` directory. Platform-specific
configuration can point to it; the canonical source should not be platform-hidden.

---

## Consequences

**Immediate:** ILC gains a shared, version-controlled instruction layer below CLAUDE.md
that both Claude Code and Codex can discover. Recurring workflow patterns become invocable
commands rather than prose to re-discover.

**Near-term:** Scaffold skills reduce error in phase construction and make the project's
conventions more accessible to new agent instances without deep context loading.

**Long-term:** If Tier 3 lands, ILC becomes the first protocol with constitutionally-
governed, benchmark-gated, attribution-tracked skill versioning. Skills become a first-class
procedural knowledge primitive alongside the existing epistemic knowledge node architecture.
This would represent a meaningful extension of ILC's value proposition: not only
preserving declarative knowledge (what is true) but also procedural knowledge (how to do
things correctly) as attributed, reusable, ECU-generating graph artifacts.

---

## References

- agentskills.io specification: https://agentskills.io/specification
- Anthropic Agent Skills overview: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Claude Code skills documentation: https://code.claude.com/docs/en/skills
- CDL-034 (authored envelope schema), CDL-052 (reuse centrality), CDL-V7 (Popperian gate)
- `docs/research/ilc_skill_node_architecture_research_placeholder_v0.1.md`
