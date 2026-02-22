# ILC SDK Boundary Contract 234 v0.1

Status: Phase-234 planning artifact (non-ratifying)
Date: 2026-02-20
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

This artifact locks the SDK boundary for the CLI-first integration surface so protocol responsibilities are separated from orchestration and runtime concerns.

Scope constraints:
- no parameter ratification is performed in this phase,
- no `ilc_core/` runtime behavior is changed,
- no CDL status is mutated from `open` to `ratified`,
- ADM-002 is referenced as proposed and not ratified by this contract.

## 2. Boundary definition

The SDK boundary is the contract line where the ILC CLI owns protocol-native operations (message shaping, signing, verification, and deterministic command semantics), while orchestration logic and host/runtime operations remain external and pluggable.

## 3. Protocol surface (SDK owns)

Protocol primitives exposed by SDK command surface:
- `assert`: create a protocol claim assertion.
- `validate`: submit protocol validation evidence.
- `contradict`: submit contradiction evidence.
- `refute`: submit refutation proof.
- `revise`: publish a revision to prior claim state.
- `link`: create typed claim-to-claim relationship edges.
- `epoch`: interact with epoch state and commitment lifecycle.

Operational commands owned by SDK:
- `query`, `verify`, `balance`, `identity`, `bundle`, `shard`, `capproof`, `config`.

I/O contract:
- output is JSON on stdout,
- complex payloads accept JSON via stdin (or flags for simple payloads),
- errors are emitted on stderr,
- exit codes: `0` success, `1` protocol/runtime error, `2` usage/argument error, `3` network/transport error.

Key and content operations owned by SDK:
- signing via COSE Sign1,
- CID computation and validation,
- identity initialization/export command semantics,
- protocol bundle verification before participation.

CapProof ownership boundary:
- SDK owns running the five probes: `GEMM`, `Infer`, `Graph`, `Bandwidth`, `Determinism`.
- SDK must enforce Phase-231 Gate A fail-closed behavior: failed probe is refusal, never default pass.
- SDK must enforce Phase-231 Gate A no-user-supplied-kernels/backend-hints invariant: probes measure actual host capability, not user override hints.

## 4. Orchestration surface (SDK does not own)

Excluded orchestration responsibilities:
- model selection and LLM inference routing (host agent intelligence concern),
- conversation/session state continuity (CLI invocations are stateless),
- message routing and channel adapters (for example, Telegram, Discord, OpenClaw channel wiring),
- multi-agent role assignment and fleet coordination,
- scheduling/heartbeat policy and task cadence,
- star.map routing and cross-shard L2 behavior (deferred to Phase B/C; no Genesis SDK command).

## 5. Runtime surface (SDK does not own)

Excluded runtime responsibilities:
- key storage and access control at rest (operator environment concern),
- `--key` selects a signing provider; provider may be a local keyfile, a hardware wallet/HSM, or an external wallet SDK callback (provider selection is operator/runtime concern),
- transport configuration and endpoint routing policy,
- daemon/server lifecycle management,
- deployment environment composition (container runtime, OS, package manager, PATH shaping).

## 6. Anti-leakage rules

1. No model-provider-specific API logic is embedded in protocol primitives.
2. No conversation/session state is persisted inside CLI primitive execution paths.
3. No transport-specific branching is embedded in primitive semantics; transport is pluggable.
4. No OpenClaw-specific dependency is required by the CLI binary.
5. No key material is emitted to stdout/stderr output payloads.
6. No protocol primitive command spawns daemon/server lifecycle processes.
7. No `star.map` or cross-shard routing command is present in Genesis SDK surface; L2 routing is deferred to Phase B/C.

## 7. Boundary examples

| Operation | Boundary verdict | Rationale |
| --- | --- | --- |
| `ilc assert --claim "..." --key ./agent.key` | In boundary (protocol surface) | Core epistemic primitive command |
| `ilc assert --claim "..." --key coinbase://agent-wallet-id` | In boundary (protocol surface) | `--key` is provider-selected and not limited to local file paths |
| `ilc refute --cid <cid> --proof proof.json --key ./agent.key` | In boundary (protocol surface) | Core contradiction/refutation primitive |
| `ilc capproof --run` on actual host hardware | In boundary (protocol surface) | CapProof probe execution is protocol-native |
| `ilc bundle --verify <bundle-cid>` | In boundary (protocol surface) | Bundle validation is protocol-native precondition |
| Choosing which LLM/provider should generate next claim | Out of boundary (orchestration surface) | Model-provider routing belongs to host agent logic |
| Persisting chat memory and deciding invocation timing | Out of boundary (orchestration surface) | Session continuity and scheduling are orchestration concerns |
| Storing `agent.key` in HSM or encrypted keystore | Out of boundary (runtime surface) | Key storage hardening is operator/runtime concern |
| Routing a claim across shards through `star.map` | Out of boundary (L2 deferred surface) | `star.map` routing is deferred to Phase B/C, not Genesis SDK |
| Overriding CapProof with user-supplied backend/kernel hint | Out of boundary (anti-leakage violation) | Violates Phase-231 no-user-supplied-kernels invariant |

## 8. ADM-002 relationship

ADM-002 defines the proposed CLI-first interface decision, while this contract defines the responsibility boundary and leakage constraints of that interface. ADM-002 remains proposed (`CDL-032` not ratified), and this phase does not ratify ADM-002.

## 9. Non-goal boundaries

This phase explicitly does not include:
- CDL-032 ratification,
- CDL-033 ratification,
- any runtime implementation work,
- any `ilc_core/` code changes,
- ratification of architectural decisions,
- star.map API/command addition or cross-shard routing command design.

## 10. Canonical anchors

- `docs/specs/ilc_antigravity_context_capsule_v0.2.md`
- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`
- `docs/specs/ilc_adm_002_cli_first_agent_sdk_v0.1.md`
- `docs/specs/ilc_capability_proof_activation_readiness_contract_231_v0.1.md`
- `docs/specs/ilc_openclaw_findings_integration_plan_v0.3.md`
- `docs/specs/ilc_post_genesis_capability_proof_activation_sequence_230_239_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_distribution_architecture_roadmap_v0.3.md`
