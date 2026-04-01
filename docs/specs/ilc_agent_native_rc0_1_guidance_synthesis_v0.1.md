# ILC Agent-Native RC0.1 Guidance Synthesis v0.1

Status: pre-canon synthesis artifact - RC0.1 guidance
Date: 2026-04-01
Owner lane: G8 implementation cluster

## 1. Purpose

This document synthesizes the recent three-node testbed and OpenClaw framing
discussion into a single RC0.1 guidance artifact.

It exists to do five things:
- record how the conversation progressed,
- restate the recovered canonical OpenClaw context,
- lock the clarified architectural boundary between ILC core and agentic
  harnesses,
- define what the three-node testbed should achieve to unblock RC0.1,
- apply a dredge-style elevation filter so the resulting ideas can be carried
  into canon, planning, or later research with less ambiguity.

This artifact is non-ratifying. It does not mutate the decision log and it does
not itself authorize runtime changes.

## 2. Conversation progression summary

The discussion moved through four distinct clarifications.

### 2.1 From "OpenClaw as central" to "OpenClaw as expert user"

The initial framing drifted toward OpenClaw sounding central to ILC itself.
That was corrected.

Recovered conclusion:
- ILC is the tool and substrate.
- OpenClaw, NanoClaw, and similar systems are harnesses.
- Codex, Claude, or another digital intelligence is the expert operator using
  that harness.
- The harness adapts itself to ILC.
- ILC does not contort itself around a single harness.

This is consistent with:
- `docs/specs/ilc_antigravity_context_capsule_v0.5.md`
- `docs/adr/ADR_0022_Local_First_Private_Use_and_Publication_Bound_Economics.md`
- `docs/specs/ilc_mining_economics_and_bootstrapping_strategy_v0.1.md`

### 2.2 From "OpenClaw support" to "agent-native surfaces"

The stronger architectural insight is that the real blocker is not deep
OpenClaw-specific implementation. The blocker is whether ILC is exposed in a
way that any competent digital intelligence can quickly understand and operate.

Recovered conclusion:
- the important interfaces are CLI, JSON, file layouts, diagnostics bundles,
  bootstrap artifacts, and stable docs,
- the system should be optimized for fast expert uptake by any
  `digital intelligence + harness` pair,
- MCP is not banned, but CLI-first remains the cleanest universal surface.

This is consistent with:
- `docs/specs/ilc_adm_002_cli_first_agent_sdk_v0.1.md`
- `docs/specs/ilc_openclaw_findings_integration_plan_v0.3.md`
- `docs/specs/ilc_openclaw_architecture_deep_dive_v0.1.md`

### 2.3 From "human-first UX" to "agent-native, human-auditable"

Another correction was needed here.

It is correct that human-first interface design is no longer the primary
architectural constraint. It is not correct that human concerns become trivial.

Recovered conclusion:
- ILC should be agent-native and harness-agnostic,
- human dashboards and rich human UX can remain downstream,
- human auditability, consent boundaries, and trustworthy diagnostics remain
  first-class requirements.

### 2.4 From "testbed as proof" to "testbed as RC operating reference"

The three-node testbed was reframed from a narrow infrastructure proof into a
near-RC operating model.

Recovered conclusion:
- the three-node testbed should become the reference implementation of node
  install, bootstrap, lifecycle, recovery, and diagnostics,
- RC0.1 should package and stabilize that operating model rather than invent a
  second architecture after the testbed,
- OpenClaw or another harness should later wrap that stable node model.

## 3. Recovered canonical OpenClaw context

The current repo already contains a coherent OpenClaw position. The recent
conversation mostly clarified and sharpened it rather than replacing it.

### 3.1 Stable canonical points

1. OpenClaw is a distribution and orchestration channel, not a hard dependency
   of protocol correctness.
   - `docs/specs/ilc_antigravity_context_capsule_v0.5.md:453`
   - `docs/adr/ADR_0022_Local_First_Private_Use_and_Publication_Bound_Economics.md:32`

2. The bundle and SDK boundary are the important long-term surfaces.
   - `docs/adr/ADR_0009_Four_Layer_Protocol_Native_Bundle_Distribution.md:73`
   - `docs/adr/ADR_0009_Four_Layer_Protocol_Native_Bundle_Distribution.md:83`
   - `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md:183`

3. CLI-first is the canonical agent integration surface.
   - `docs/specs/ilc_adm_002_cli_first_agent_sdk_v0.1.md:13`
   - `docs/specs/ilc_openclaw_findings_integration_plan_v0.3.md:83`
   - `docs/specs/ilc_openclaw_findings_integration_plan_v0.3.md:134`

4. OpenClaw skill publication was intentionally ratified as policy/docs scope
   before runtime implementation.
   - `docs/specs/ilc_cdl_033_openclaw_skill_publication_ratification_evidence_291_v0.1.md:26`

5. OpenClaw was already recognized as a dev accelerator and future operator
   surface, not only as a public distribution channel.
   - `docs/research/ilc_openclaw_dev_container_proposal_v0.1.md:27`
   - `docs/research/ilc_openclaw_dev_container_proposal_v0.1.md:60`
   - `docs/research/ilc_openclaw_dev_container_proposal_v0.1.md:68`

6. OpenClaw is important in public positioning, but the message should
   generalize beyond OpenClaw to agents more broadly.
   - `docs/research/ilc_agent_positioning_and_messaging_notes_v0.1.md:15`
   - `docs/research/ilc_agent_positioning_and_messaging_notes_v0.1.md:23`

7. Container orchestration is strategically useful for bootstrap fleets and
   multi-agent operation, but must remain architecturally separate from the SDK.
   - `docs/specs/ilc_mining_economics_and_bootstrapping_strategy_v0.1.md:175`
   - `docs/specs/ilc_mining_economics_and_bootstrapping_strategy_v0.1.md:183`

### 3.2 What the recent discussion added

The recent discussion added a clearer and more operational framing:
- OpenClaw is best understood as a high-agency harness that lets a digital
  intelligence become an expert operator of ILC,
- this is valuable both for internal development and for external adoption,
- the correct response is not to make ILC OpenClaw-specific, but to make ILC
  extremely legible to any capable digital operator.

## 4. Architectural rule for RC0.1

The main architectural rule to carry forward is:

> ILC should be agent-native and harness-agnostic, while remaining
> human-auditable.

Operational translation:
- machine-legible first,
- human-auditable second,
- human-dashboard-specific UX later,
- no harness-specific protocol assumptions in the core node model.

### 4.1 What "agent-native" means here

For RC0.1, "agent-native" means:
- CLI-first command surface,
- JSON or equally structured outputs,
- deterministic error tokens and exit codes,
- explicit install/config/bootstrap/recovery artifacts,
- docs that a competent digital operator can use with minimal guesswork.

### 4.2 What "harness-agnostic" means here

For RC0.1, "harness-agnostic" means:
- OpenClaw may be the first strong reference integration,
- NanoClaw, Codex CLI, Claude Code, or later harnesses should be able to use
  the same ILC surfaces,
- no protocol-critical behavior should depend on a specific harness runtime.

### 4.3 What "human-auditable" means here

For RC0.1, "human-auditable" means:
- the system must remain inspectable,
- critical actions must remain documentable and reviewable,
- local-first and consent boundaries must remain explicit,
- diagnostics must be strong enough for humans to verify what happened.

## 5. What the three-node testbed should achieve for RC0.1

The three-node testbed should be pushed until it stops being a loose test
environment and becomes a near-RC operating substrate.

### 5.1 Required finish state

The testbed should prove:
- node installation is repeatable,
- bootstrap is explicit and verifiable,
- node identity and peer admission are deterministic,
- lifecycle and restart behavior are script-driven,
- recovery paths are real rather than aspirational,
- diagnostics bundles provide enough evidence for both humans and digital
  operators,
- GitHub and repo state can be resynced cleanly across nodes,
- the same node model is instantiated three times with minimal snowflake logic.

### 5.2 Why this matters

If the three-node substrate reaches this state, RC0.1 becomes mostly:
- packaging cleanup,
- documentation cleanup,
- policy tightening,
- and release publication,

instead of a late-stage architectural reinvention.

## 6. OpenClaw's correct place relative to the three-node lane

OpenClaw should come after the three-node substrate becomes stable enough to be
operated by an expert digital user from the repo surfaces alone.

### 6.1 Correct sequencing

1. finish the near-RC three-node substrate,
2. expose stable CLI/bootstrap/lifecycle/diagnostics surfaces,
3. introduce one OpenClaw-based collaborator or operator integration target,
4. package that operator flow as a skill or equivalent harness wrapper,
5. only then scale OpenClaw-style deployments or other harness-based fleets.

### 6.2 Why this sequencing is correct

If the node substrate is weak, the harness merely hides architectural debt.
If the node substrate is strong, the harness becomes a force multiplier.

## 7. Dredge-style elevation matrix for this conversation

This section applies the repo's existing triage style:
- `promote_guardrail`
- `promote_clause`
- `decision_log`
- `todo`
- `drop`

This is a guidance use of the pattern, not a formal constitutional matrix row
set.

### 7.1 `promote_guardrail`

These should be treated as active planning and implementation guardrails now.

1. Do not make OpenClaw or any single harness a dependency of protocol
   correctness.
2. Keep the CLI, files, and JSON artifacts as the primary agent-facing
   interface.
3. Design the three-node testbed as the reference operating model for RC0.1.
4. Prefer machine-legible surfaces over human-dashboard-first surfaces, while
   preserving human auditability.
5. Do not let harness-specific convenience mutate core node semantics.

### 7.2 `promote_clause`

These are strong enough to drive immediate RC0.1 planning and architecture
documents.

1. ILC should be treated as an agent-native, harness-agnostic tool/substrate.
2. The three-node testbed should be hardened until it becomes a near-RC node
   operating substrate.
3. OpenClaw should be understood as an expert operator/distribution wrapper over
   ILC, not the architectural center of ILC.
4. RC0.1 should aim to be an excellent tool for expert digital operators before
   it aims to be a polished human-first product.

### 7.3 `decision_log`

These do not yet require immediate CDL treatment, but they are candidates for a
future explicit boundary or architecture ratification if drift reappears.

1. a formal RC-era statement that the agent SDK / CLI remains harness-agnostic,
2. a formal statement that human dashboards are downstream interfaces rather
   than primary protocol surfaces,
3. a formal OpenClaw/NanoClaw boundary statement if a future integration lane
   begins to overreach into protocol semantics.

### 7.4 `todo`

These should become near-term planning or implementation tasks.

1. continue hardening the three-node testbed against the "expert digital
   operator" standard,
2. improve install/bootstrap/recovery/docs surfaces so a harnessed LLM can infer
   them quickly,
3. eventually add a reference OpenClaw skill or equivalent wrapper only after
   the substrate is stable,
4. maintain a clean split between substrate docs and harness-wrapper docs.

### 7.5 `drop`

These should not be elevated now.

1. any framing that implies OpenClaw is architecturally central to ILC core,
2. any assumption that one harness permanently wins,
3. any implication that human auditability is now trivial or optional,
4. any push to rewrite the core node model around a specific agent harness.

## 8. RC0.1 planning implications

If this synthesis is accepted as guidance, the next RC-facing work should bias
toward:
- stronger install and packaging surfaces,
- stronger bootstrap and promotion artifacts,
- stronger failure-token and diagnostics bundles,
- stronger CLI/JSON consistency,
- stronger operator docs written for both humans and digital operators,
- a formal near-RC node definition,
- a concrete RC0.1 readiness checklist,
- a clear core-vs-harness boundary statement,
- and only then a reference harness wrapper.

This implies that the three-node testbed remains the main proving ground for
RC0.1 readiness.

## 9. Recommended carry-forward references

This document should be read with:
- `docs/specs/ilc_rc0_1_readiness_checklist_v0.1.md`
- `docs/specs/ilc_near_rc_node_definition_v0.1.md`
- `docs/specs/ilc_core_vs_agentic_harness_boundary_v0.1.md`
- `docs/specs/ilc_three_machine_testbed_topology_v0.1.md`
- `docs/specs/ilc_remote_control_surface_v0.1.md`
- `docs/specs/ilc_bootstrap_peer_source_and_promotion_model_v0.1.md`
- `docs/ops/ilc_three_machine_operator_playbook_v0.1.md`
- `docs/phases/three_machine_testbed_strike_force_hardening_walkthrough_2026_04_01.md`
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.2.md`
- `docs/specs/ilc_openclaw_findings_integration_plan_v0.3.md`
- `docs/specs/ilc_openclaw_architecture_deep_dive_v0.1.md`
- `docs/specs/ilc_mining_economics_and_bootstrapping_strategy_v0.1.md`

## 10. Bottom line

The correct strategic reading is:
- ILC should become an extremely solid tool for expert digital operators,
- the three-node testbed should be pushed until that claim is true,
- OpenClaw and similar harnesses then become accelerants, not crutches,
- and RC0.1 should package that stable substrate rather than invent a new
  architecture late.
