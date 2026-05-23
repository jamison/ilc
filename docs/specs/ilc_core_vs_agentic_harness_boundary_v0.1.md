# ILC Core vs Agentic Harness Boundary v0.1

Status: planning memo
Date: 2026-04-01
Owner lane: G8 implementation cluster

## 1. Purpose

This memo fixes the boundary between ILC core and agentic harnesses such as
OpenClaw, NanoClaw, Codex CLI, Claude Code, or similar systems.

The goal is to prevent harness convenience from distorting core node semantics
while still making ILC easy for high-agency digital operators to use.

## 2. Boundary rule

ILC core is the tool and substrate.
Agentic harnesses are operator wrappers and delivery vehicles.
Digital intelligences use those harnesses to become expert operators of ILC.

The harness adapts itself to ILC.
ILC does not adapt its protocol correctness rules to one harness.

## 3. What belongs in ILC core

ILC core owns:
- protocol semantics,
- node runtime correctness,
- identity and bootstrap semantics,
- lifecycle and recovery primitives,
- CLI and file-based control surfaces,
- diagnostics and evidence emission,
- release packaging inputs.

ILC core should remain:
- agent-native,
- harness-agnostic,
- human-auditable.

## 4. What belongs in a harness layer

A harness layer may provide:
- install wrappers,
- operator UX,
- setup assistance,
- deploy and restart workflows,
- diagnostics collection and summarization,
- bootstrap fetch and staging helpers,
- skill packaging,
- higher-level agent workflows.

A harness should consume the stable ILC surfaces rather than replace them.

## 5. Stable surfaces the harness should use

The preferred harness-facing surfaces are:
- CLI commands,
- structured stdout/stderr markers,
- JSON-friendly outputs,
- explicit config files,
- explicit bootstrap artifacts,
- diagnostics bundles,
- documented file layouts.

This keeps the system usable by OpenClaw, NanoClaw, Codex CLI, Claude Code, and
future harnesses without per-harness protocol forks.

## 6. Explicit non-goals for harnesses

Harnesses must not become:
- a protocol correctness dependency,
- the sole source of peer truth,
- the only supported recovery surface,
- the place where node semantics are silently redefined,
- a substitute for human-auditable evidence.

## 7. OpenClaw-specific implication

OpenClaw is strategically important as:
- a distribution channel,
- an operator wrapper,
- a future multi-agent fleet surface,
- a force multiplier for internal development and external adoption.

It is not the architectural center of ILC core.

The correct sequence is:
1. stabilize the ILC substrate,
2. expose machine-legible operating surfaces,
3. wrap those surfaces in an OpenClaw skill or equivalent operator package,
4. scale harness-driven deployments only after the substrate is boring.

## 8. Pre-RC implementation rule

When evaluating a proposed change, prefer the following test:

Would a competent digital operator still be able to install, bootstrap, run,
recover, and diagnose ILC from the repo surfaces alone if this harness did not
exist?

If the answer is no, the change probably belongs in the wrong layer.

## 9. Relationship to the three-node lane

The three-node testbed should be used to harden the core surfaces that future
harnesses will consume.

The testbed should not be redesigned around a single harness. It should become a
strong enough substrate that a harness wrapper becomes straightforward.

## 10. Harness Scheduling and Provider Quota Signals (Addendum 2026-05-23)

Harnesses may schedule and package maintenance work on behalf of human operators — including `star.map.embedding`, `contradiction.sweep`, `graph.compression`, and `stability.simulation` tasks. This is a legitimate harness function and does not constitute a protocol fork, provided the harness consumes stable `ilc_core/` surfaces and does not redefine admission semantics (see §6).

Provider quota headers and response body quota fields are **operational scheduling signals** only:

| Provider | Signal |
|----------|--------|
| Anthropic | `anthropic-ratelimit-tokens-remaining`, `anthropic-ratelimit-tokens-reset` (response headers) |
| OpenAI | `x-ratelimit-remaining-tokens`, `x-ratelimit-reset-tokens` (response headers) |
| Gemini | `usage_metadata` in response body — no confirmed remaining-tokens response-header contract |

These signals inform the harness when spare capacity may be available for maintenance tasks. They are **not**:
- protocol truth,
- economic proof,
- inputs to Werner credit calculations,
- inputs to any `ilc_core/` protocol surface.

Werner credit for completed maintenance tasks is governed by the Werner flow-governor CDL (Track C, Window 1459+ forward plan). Provider quota state alone does not authorize credit minting. A `ProviderUsageAdapter` implementation must treat Gemini as a local-counter-fallback case rather than assume header-level remaining-quota exposure.

TOON compression applies to outbound/context packing and task envelopes only. Captured model output must preserve raw response bytes as the hashable content; the ILC node envelope (epoch_id, agent_id, metadata) is added separately and must not be included in the content hash.

**Hash-separation invariant:** Tests for any `LocalNodeCapture` implementation must explicitly verify that `content_hash == SHA-256(raw_response_payload)` and that neither TOON-packed prompt metadata nor the node envelope appear in the hash input. A test that only checks the happy-path submission but does not assert this separation is insufficient.

---

## 11. Related references

- `docs/specs/ilc_agent_native_rc0_1_guidance_synthesis_v0.1.md`
- `docs/specs/ilc_rc0_1_readiness_checklist_v0.1.md`
- `docs/specs/ilc_near_rc_node_definition_v0.1.md`
- `docs/specs/ilc_openclaw_findings_integration_plan_v0.3.md`
- `docs/specs/ilc_mining_economics_and_bootstrapping_strategy_v0.1.md`
- `docs/specs/ilc_antigravity_context_capsule_v0.6.md`
