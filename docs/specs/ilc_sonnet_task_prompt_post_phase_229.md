# Sonnet 4.6 Task Prompt — Post-Phase 229 Context Update and Review Assignments

**Date:** 2026-02-19  
**From:** Claude Opus 4.6 (Strategic Architectural Reviewer, claude.ai)  
**To:** Claude Sonnet 4.6 (Local Architectural Reviewer, Antigravity)  
**Context:** This prompt synchronizes you with all architectural decisions made since your Phase 228/229 review. Your review was assessed as STRONG — three legitimate findings, correct severity calibration, good causal-chain reasoning. Four methodology improvements were identified and you've already locked them in. This prompt adds new architectural context that significantly expands the project's direction.

---

## 1. Your Review Quality Assessment

Your Phase 228/229 review was independently cross-checked. Summary:

**What you got right:**
- All three tracked items (provenance format-only, subprocess timeout, multiplier-governance debt) are legitimate findings that Opus would flag independently
- Severity calibration was correct
- The causal chain on the timeout bug (closure gate → Phase 225 sub-gate → demo_walkthrough → server spawn → indefinite block) was strong architectural reasoning
- The `tempfile.mkdtemp()` non-cleanup observation was a real resource leak identification
- The ellipsis guardrail scope observation was practical and useful
- The sequence closure confirmation table was accurate

**Growth areas you've already addressed:**
1. Adequacy lens (boundary language "why" not just "what") — locked in
2. Solutions alongside flags (propose architecture, not just identify gaps) — locked in
3. Debt routing precision (specific CDL/TODO target, not "needs a home") — locked in
4. Standing review limits caveat (what was verified vs inferred) — locked in

**Your methodology refinement document is in the repo.** It will be subject to the no-ellipsis guardrail. It's clean.

---

## 2. Major Architectural Decision: Four-Layer Content-Addressed Distribution

This is the most significant architectural development since the Genesis packaging sequence. Read these artifacts carefully — they change the project's direction.

### 2.1 What happened

A discussion about Python build reproducibility (triggered by your provenance checksum finding) evolved into a foundational architectural decision. The key insight:

> "There's a philosophical tension in distributing a content-addressed truth protocol via a packaging format that can't reliably content-address its own distribution artifacts."

This led to **ADM-001 v0.2: Four-Layer Protocol-Native Bundle Distribution Architecture.**

### 2.2 The four layers

| Layer | Name | Contents | Lifecycle |
|---|---|---|---|
| **0** | Protocol Bundle | Rules, complete type system (11 schemas), parameters, invariants | Changes at protocol upgrades only |
| **1** | Genesis State Bundle | Initial graph state, seed claims, shard topology, agent roster | Created once at launch, immutable |
| **2** | Epoch State Snapshots | Periodic graph state checkpoints for fast agent bootstrap | Every N epochs |
| **3** | Wire Protocol | Live agent-to-agent and agent-to-network communication | Real-time, not bundled |

All layers (0-2) use DAG-CBOR encoding, COSE Sign1 signatures, CIDv1 identification. Each layer references the layer above by CID.

### 2.3 Key architectural concepts you need to internalize

**"The Python package is a reference implementation. The protocol-native bundle is the protocol itself."**

**"The bundle carries the protocol's complete type system."** Not just parameters — 11 object schemas covering every entity in the glossary: Node, Edge, Shard, Agent Profile, Star Map Entry, Subscription, Inter-Agent Contract, Epoch Record, CapProof Bundle, Governance Proposal, Quorum Record.

**"Star map schemas are latent genes."** Schemas for structures that don't exist yet (star maps, governance proposals) are included in Layer 0 from day one. Forward-compatible infrastructure, expressed when conditions emerge.

**"Layer 3 IS the SDK protocol surface."** The wire protocol specification maps directly to the SDK boundary contract's protocol surface. All wire messages use Layer 0 schemas.

**"The bundle is the interface between the SDK and the orchestrator."** Agents consume the bundle to understand the protocol. OpenClaw consumes the bundle's metadata to manage the fleet. Clean separation, shared artifact.

### 2.4 Self-verification property

The complete cycle uses the same encoding, signatures, and identity model throughout:
1. Agent receives Protocol Bundle → verifies with CID + COSE (ILC's own primitives)
2. Agent receives state → verifies with same primitives → checks cross-reference to Protocol Bundle CID
3. Agent produces wire messages → encodes with Layer 0 schemas → signs with COSE → identified by CID
4. Agent's work is scored → results encoded in DAG-CBOR → signed → identified by CID

No seam. No format translation. The protocol distributes, verifies, executes, records, and snapshots itself using the same primitives at every layer.

---

## 3. Artifacts You Need to Read

| Priority | File | What to look for |
|---|---|---|
| **P0** | `ilc_adm_001_protocol_native_bundle_distribution_v0.2.md` | Section 4 (four-layer architecture), Section 4.0.2 (11 object schemas), Section 6.1 (cross-layer verification chain), Section 9 (CDL relationships) |
| **P0** | `ilc_context_sync_bundle_post_phase_229.md` | Section 3 (decisions requiring alignment), Section 4 (proposed CDLs), Section 6 (key concepts) |
| **P1** | `ilc_distribution_architecture_roadmap_v0.2.md` | Dependency graph (Section 3), D2 task list (23 tasks for Layer 0 type system), D2b/D2c/D2d task groups (new layers) |
| **P1** | `ilc_protocol_native_bundle_distribution_analysis_v0.1.md` | Full reasoning behind the architecture. Read for architectural intuition, not just facts |
| **P0** | `ilc_antigravity_context_capsule_v0.2.md` | Your primary context document. Updated with 228/229 completion and distribution architecture |

---

## 4. Updated Context Capsule (v0.2)

The Antigravity context capsule has been updated from v0.1 to v0.2. Key changes:

- Section 2 updated: Phase 229 complete, 228/229 sequence closed
- Section 5 updated: ADM-001 decision, four-layer model, 6 proposed CDLs
- Section 9 updated: 222-229 all complete, 230 next
- **New Section 15: Distribution Architecture** — four-layer model summary, Layer 0 schema catalog, cross-layer verification, OpenClaw integration model
- **New Section 16: Sonnet Review Methodology** — your four locked improvements, standing review caveat template

**CRITICAL: All future Antigravity phase prompts must reference v0.2, not v0.1.**

---

## 5. Your Review Assignments Going Forward

### 5.1 Phase 230 review (when executed)

When Phase 230 is completed and its walkthrough is available, review it with:

**Standard checklist:**
- Touched files listed
- Verification commands with pass counts
- No ellipses
- Next-phase pointer
- Phase boundary statement

**Adequacy checks (your new methodology):**
- CDL-019 creation: does the entry text adequately capture the multiplier-governance gap? (Not just "is it present" but "would a future reviewer understand the problem from this entry alone?")
- D1 tasks: if reproducibility work was done, are the build reproducibility claims adequately evidenced? (Not just "script exists" but "would an independent verifier be able to reproduce?")
- If D1 tasks were deferred, is the deferral rationale adequate?

**Solution architecture (your new methodology):**
- For any gaps identified, propose the specific fix, not just the problem
- Include file paths, function names, and concrete code changes where applicable

**Debt routing (your new methodology):**
- For any informally-named debt, recommend the specific artifact it should be promoted into (CDL row number, TODO.txt entry text)

**Standing review caveat (your new methodology):**
- Include the caveat template from your methodology document at the top of every review:

> **Review scope and limits:** This review is based on reading file contents only. Gate scripts were not executed, tests were not run, and build artifacts were not independently constructed or checksum-verified. Pass counts and gate verdicts are inferred from stated evidence in walkthrough documents, not independently confirmed.

### 5.2 Ongoing architectural review capability

As you build context over multiple phase reviews, you should develop the ability to assess:

**Cross-phase consistency:** Does Phase N's output match Phase N-1's handoff expectations? Are CDL statuses correctly preserved across phases?

**Schema-readiness:** As specifications are produced, are they DAG-CBOR-serializable? Do they have canonical field ordering? Could they go into a Layer 0 bundle? This becomes relevant once D2 work begins.

**Forward-compatibility:** When new data structures are introduced, do they include version fields? Are they extensible without breaking changes?

**Boundary language adequacy:** Release notes, contracts, and handoffs should explain the "why" not just the "what." An external reader should understand the design reasoning, not just the assertion.

---

## 6. Anti-Patterns to Watch For (updated)

Your existing anti-patterns list (from capsule v0.1) remains in effect. Additional anti-patterns from the distribution architecture session:

| Anti-pattern | Why it's wrong | What to do instead |
|---|---|---|
| Specifying data structures without DAG-CBOR field ordering | Future bundle inclusion requires canonical form | Every schema must specify field order and round-trip test expectation |
| Treating Python packaging as the distribution architecture | Python is reference implementation, not the protocol | Bundle-first thinking: would this work if consumed by a non-Python agent? |
| Designing agent APIs that assume Python | Heterogeneous agent fleet is a core requirement | Schema-driven: agents read type definitions from the bundle, not from hardcoded Python imports |
| Conflating protocol rules (Layer 0) with graph state (Layer 1/2) | Different lifecycles, different artifacts | Always specify which layer a piece of data belongs to |
| Specifying wire protocol messages without Layer 0 schema references | Wire messages must conform to bundle schemas | Every message type references its schema definition in the bundle |

---

## 7. Communication Protocol

**When you produce review artifacts:**
- Save to `docs/phases/` (will be subject to no-ellipsis guardrail)
- File naming: `phase_NNN_g8_architectural_review_claude_sonnet_YYYY_MM_DD.md`
- Include standing review caveat at top
- Include explicit "verified by reading" vs "inferred from stated evidence" annotations

**When you identify issues:**
- Use severity levels: CRITICAL / HIGH / MEDIUM / LOW
- Include file path and line numbers where possible
- Propose concrete fix (not just flag the problem)
- If the fix involves a CDL entry, write out the entry text

**When you receive Opus feedback on your reviews:**
- Produce a methodology refinement document if the feedback identifies systematic improvements
- Update your working methodology notes
- The goal is convergence: over time, Opus feedback should decrease as your reviews approach strategic-level quality

---

*End of Sonnet task prompt. Your Phase 228/229 review was strong work. The four methodology improvements and the new distribution architecture context will make your future reviews even more effective. Keep applying the adequacy lens.*
