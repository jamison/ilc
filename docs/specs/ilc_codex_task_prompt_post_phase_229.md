# Codex Task Prompt — Post-Phase 229 Context Update and Phase 230 Preparation

**Date:** 2026-02-19  
**From:** Claude Opus 4.6 (Strategic Architectural Reviewer)  
**To:** ChatGPT 5.4 Codex (Project Manager / Code Reviewer)  
**Context:** This prompt synchronizes Codex with all architectural decisions, findings, and task plans produced since Phase 229 completion. Read this in conjunction with `ilc_context_sync_bundle_post_phase_229.md` for full artifact inventory.

---

## 1. Status Update: What Happened

Phases 228 and 229 are CLEAN. The 222-229 Genesis packaging sequence is closed. Both Opus and Sonnet 4.6 reviewed independently and found no blockers. Three items were identified for Phase 230 tracking (see Section 3 below).

After the phase reviews, a major architectural design session occurred. A distribution architecture question (Python build reproducibility) evolved into a foundational architectural decision: **ILC will adopt a four-layer content-addressed distribution model.** This is documented in ADM-001 v0.2 and produces a 73-task roadmap across 8 phases. The decision is proposed (non-normative) and awaits CDL routing.

---

## 2. New Artifacts to Ingest

Please read and incorporate the following into your project context. Priority order:

| Priority | File | What it is | Why you need it |
|---|---|---|---|
| **P0** | `ilc_context_sync_bundle_post_phase_229.md` | Master context inventory | Complete list of all decisions, artifacts, CDL proposals, and status updates |
| **P0** | `ilc_adm_001_protocol_native_bundle_distribution_v0.2.md` | Architectural decision | Defines the four-layer model. All future distribution work follows this. 11 object schemas, 6 CDL proposals, fork semantics |
| **P1** | `ilc_distribution_architecture_roadmap_v0.2.md` | Task roadmap | 73 tasks across 8 phases with dependencies. Phase D1 tasks are Phase 230 scope |
| **P1** | `ilc_protocol_native_bundle_distribution_analysis_v0.1.md` | Canon analysis | Verbatim reasoning behind the architecture. Source material for whitepaper |
| **P2** | `ilc_antigravity_context_capsule_v0.2.md` | Updated capsule | Updated Sonnet context — ensure Antigravity prompts reference v0.2, not v0.1 |

---

## 3. Immediate Action Items (Before Phase 230 Scope Lock)

These three items were identified in the Phase 228/229 review and must be addressed before or within Phase 230:

### 3.1 CRITICAL: Create CDL-019

**What:** The "multiplier-governance surface unification" debt was named in the Phase 229 handoff (`ilc_genesis_packaging_222_228_handoff_v0.1.md`) but has no formal CDL entry.

**Why it matters:** Without a CDL row, this debt is invisible to reviewers who use the CDL as their source of truth. It will be silently dropped from Phase 230 scope lock.

**Required CDL-019 entry:**
- Status: `open`
- Description: "Multiplier-governance surface: resolve relationship between flat Genesis constant (1.2x), refutation-profitability invariant floor, and eventual dynamic ranking-based multiplier mechanism"
- Action: `decision_log`
- Phase identified: 229 (handoff deferred debt)

### 3.2 HIGH: Add subprocess timeout to Phase 229 closure gate test

**What:** `tests/test_genesis_packaging_closure_gate_phase_229.py` function `_run_gate` has no `timeout` parameter. The full execution path chains through all four sub-gates including `demo_walkthrough.py`, which spawns a server. If the server hangs, CI blocks indefinitely.

**Fix:** Add `timeout=900` (15 minutes) to the `subprocess.run` call in `_run_gate`:
```python
def _run_gate(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(CLOSURE_GATE_SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
        timeout=900,
    )
```

### 3.3 MEDIUM: Document provenance checksum limitation

**What:** `tests/test_genesis_release_artifacts_phase_228.py` test `test_phase_228_provenance_file_shape_and_checksum_tokens` verifies the provenance file has the right shape and contains 64-char hex tokens, but does NOT verify those checksums match the actually-built artifacts.

**Fix:** Add an explicit note to `ilc_genesis_release_artifact_provenance_phase_228_v0.1.md` or its contract stating: "Checksums recorded here are from a single authoritative build at Phase 228 execution time. They are not continuously re-verified by the test suite. Independent verification requires running `python -m build` against the same commit and comparing SHA-256 outputs."

---

## 4. Phase 230 Scope Recommendation

The Phase 229 handoff recommends Phase 230 as "post-Genesis capability-proof activation readiness sequence lock." Based on the distribution architecture session, I recommend Phase 230 scope include:

### 4.1 From Phase 229 handoff (existing recommendations)
- CDL runtime implementation planning
- Issuance-policy closure
- CapProof activation readiness

### 4.2 From distribution architecture roadmap (NEW)
- **D1-01:** Pin `SOURCE_DATE_EPOCH=0` in build pipeline
- **D1-02:** Evaluate deterministic build backend (hatch vs flit vs setuptools)
- **D1-03:** Add `tools/check_reproducible_build.sh` deterministic rebuild gate
- **D1-04:** Update provenance contract with reproducibility scope statement

### 4.3 From Phase 228/229 review findings
- Create CDL-019 (multiplier-governance)
- Fix subprocess timeout in Phase 229 test
- Document provenance checksum limitation

### 4.4 Scope boundary
Phase 230 should NOT include:
- Bundle schema specification (D2 tasks) — that's post-Genesis Phase 1
- Genesis state bundle design (D2b) — post-Genesis Phase 1
- Wire protocol specification (D2d) — post-Genesis Phase 1
- OpenClaw integration (D3) — post-Genesis Phase 1-2
- Rust kernel (D4) — milestone-triggered Phase B

---

## 5. Phase Prompt Preparation Notes

When drafting the Phase 230 Antigravity prompt:

**Input file list must include:**
- `ilc_antigravity_context_capsule_v0.2.md` (CRITICAL: use v0.2, not v0.1)
- `ilc_genesis_packaging_222_228_handoff_v0.1.md` (Phase 229 handoff)
- `ilc_distribution_architecture_roadmap_v0.2.md` (for D1 task specs)
- Current `STATUS.md`
- Current `TODO.txt` (or equivalent)

**Antigravity sensitivity protocol:**
- CDL-019 creation: Antigravity MUST use the exact CDL row format specified in Section 3.1 above. No paraphrasing.
- D1 tasks are docs-only and build-toolchain-only. No `ilc_core/` runtime changes.
- Phase 230 must include phase boundary statement: "No runtime behavior in ilc_core/ was changed, no CDL status other than CDL-019 creation was mutated."

**Walkthrough requirements:**
- All existing walkthrough requirements apply (touched files, verification commands, pass counts, no ellipses, next-phase pointer)
- Must include CDL-019 creation evidence
- Must include D1 task completion evidence or explicit deferral with rationale

---

## 6. Architectural Direction for Future Phase Planning

The four-layer content-addressed distribution model (ADM-001 v0.2) is the most significant architectural decision since the Genesis packaging sequence lock. It affects:

**SDK boundary work:** The SDK boundary contract draft (`ilc_agent_sdk_boundary_contract_draft_v0.1.md`) maps directly to Layers 0 and 3. The "protocol surface" = Layer 3 wire protocol using Layer 0 schemas. The "orchestration surface" = what OpenClaw provides using Layer 0 metadata. Future SDK phases should be designed with this mapping in mind.

**CapProof activation:** The CapProof schema (D2-09 in the roadmap) is one of the 11 object schemas that will go into the Layer 0 bundle. CapProof activation work should produce schemas that are DAG-CBOR-ready, even if the actual bundle isn't built yet.

**Issuance policy:** The six open issuance parameters are part of the Layer 0 bundle's scoring parameters block (D2-12). When these parameters are ratified, they need to be expressible in DAG-CBOR canonical form.

**General principle:** All future protocol specification work should be done with DAG-CBOR serializability in mind. Every data structure that will appear in the protocol should have a canonical field ordering, a CIDv1 derivation path, and a round-trip test (encode → decode → re-encode = identical bytes).

---

## 7. Sonnet 4.6 Parallel Review Pipeline

Sonnet 4.6 is now running parallel architectural reviews. Its methodology has been refined with four improvements (adequacy lens, solutions alongside flags, debt routing precision, standing review limits caveat). Going forward:

- **Every Antigravity phase prompt should include `ilc_antigravity_context_capsule_v0.2.md` as first input**
- **Every phase walkthrough should be reviewed by both Opus and Sonnet independently**
- **Sonnet's review artifacts will go into `docs/phases/` and will be subject to the no-ellipsis guardrail**
- **Sonnet will include a standing review caveat distinguishing "verified by reading" from "inferred from stated evidence"**

---

*End of Codex task prompt. Please confirm receipt and flag any questions before Phase 230 scope lock.*
