# ILC OpenClaw Two-VPS Integration Rehearsal 1575b-Fix2e v0.1

**Phase:** 1575b-Fix2e
**Window:** 1565-1575
**Status:** retained private rehearsal specification
**Sensitivity:** NON-SENSITIVE when executed as scoped: private/testnet rehearsal, synthetic or private fixtures only, no public graph writes, no wallet writes, no ECU minting, no ILC settlement, no OpenClaw/ClawHub publication, no guard clearance, and no public-RC activation.

## 1. Purpose

This phase rehearses the OpenClaw local skill path across two independently scoped nodes. It composes the already committed local capture helper, idle-capacity scheduler, and invite-gated bootstrap helper without changing `ilc_core/` protocol authority.

The phase is an integration rehearsal over the local sidecar surfaces. It is not a public OpenClaw package, not a ClawHub listing, not public installability, and not a public graph submission path.

## 2. Source Basis

The rehearsal is grounded in these direct-read artifacts:

| Source | Relevant fact |
|---|---|
| `docs/sims/ilc_block6_tailscale_topology_record_1567_v0.1.md` | Block 6 has a private Tailscale topology and an OpenClaw-primary node, while public P2P, production economics, wallet writes, and public RC remain unauthorized. |
| `docs/sims/ilc_block6_rehearsal_evidence_1568_lane3_harnesses_v0.1.json` | OpenClaw local skill readiness was previously observed as workspace-local and not ClawHub-published. |
| `docs/architecture/ilc_harness_architecture_spec_1459p_v0.1.md` | Harness work is local deterministic sidecar work; no live LLM calls, no outbound network calls, and no public endpoint claim are implied. |
| `docs/architecture/ilc_core_vs_agentic_harness_boundary_v0.1.md` | Harnesses must not mutate production graph state, wallet state, treasury state, registry state, CDL records, ADR status fields, or public activation flags. |
| `docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md` | OpenClaw is a host for graph-native sidecars, not a protocol substrate. |
| `skills/ilc-openclaw-local-capture/SKILL.md` | Setup begins with `ilc verify-invite`; a valid invite permits local bootstrap/install/setup only. |
| `ilc_core/sidecars/openclaw_local_capture.py` | Capture envelopes preserve `operator_agent_id` and `local_agent_id`, hash raw payloads separately from envelope metadata, and keep ConsentGate local. |
| `ilc_core/sidecars/openclaw_idle_mining.py` | Idle-capacity scheduling enforces per-agent local caps, task-type diversity, duplicate task suppression, and profile/autonomy gates. |
| `ilc_core/sidecars/openclaw_invite_bootstrap.py` | Invite verification persists nullifiers locally and records redeemer-key binding as the forward solution for cross-node replay prevention. |

## 3. Rehearsal Modes

### Fixture Mode

Fixture mode is deterministic local CI. It simulates two redacted node labels, `vps_a` and `vps_b`, using synthetic invite bundles and separate local nullifier stores under `out/block6_openclaw_two_vps_fix2e/`.

Fixture mode must:

1. verify a synthetic invite per node;
2. persist each used nullifier per node;
3. instantiate a fresh store and reject replay per node;
4. prove that a second node with an independent nullifier store can still accept the same synthetic invite, recording the cross-node replay gap;
5. build capture envelopes for two distinct agents over identical raw payload bytes;
6. evaluate different ConsentGate policies per node;
7. evaluate local idle scheduler cap and diversity rules per node;
8. record exact duplicate suppression by raw payload hash only;
9. record semantic duplicate detection as future graph intelligence work.

### Real Two-VPS Mode

Real mode is intentionally fail-closed. The runner refuses real VPS commands unless both `ILC_FIX2E_VPS_A` and `ILC_FIX2E_VPS_B` are explicitly provided in the environment.

Real mode may only use subprocess argument lists. It must not use `shell=True`. It must redact private IPs, invite material, private keys, mnemonics, bearer tokens, and SSH target values from retained evidence.

If real mode is not configured, the evidence records:

```text
real_vps_mode.run=false
real_vps_mode.status=not_configured
```

## 4. Invite-Gated Bootstrap Checks

Each node gets its own synthetic invite bundle and its own nullifier store. Successful local bootstrap means only:

```text
valid_invite -> local bootstrap/install/setup actions allowed
```

It does not authorize:

```text
public graph writes
production identity creation
wallet writes
ECU minting
ILC settlement
public RC activation
OpenClaw publication
ClawHub listing
```

Nonce interoperability requirement: `openclaw_invite_bootstrap.py` accepts only 64-character lowercase hexadecimal nonces. Invite issuance tooling must serialize invite nonces as lowercase hex. Uppercase hex is intentionally rejected by the verifier.

## 5. Attribution and ConsentGate Checks

The fixture records two independent attribution pairs:

```text
vps_a -> operator:vps_a / agent:vps_a
vps_b -> operator:vps_b / agent:vps_b
```

The same raw payload bytes should hash identically on both nodes, while the capture envelopes remain distinct because attribution metadata differs.

ConsentGate decisions are node-local. `vps_a` uses `local_only` and must block submit intent. `vps_b` uses `approved_for_public_submission` and may return submission intent, but `public_submission_performed` must remain false.

## 6. Scheduler Checks

The idle-capacity scheduler is tested independently per node. Each node must show:

1. a valid local idle task offer;
2. `per_agent_idle_window_cap_exceeded` when its own local history reaches the per-window cap;
3. `per_task_type_idle_window_cap_exceeded` when a second task of the same type is offered in the same local idle window.

This does not solve distributed task reservation. Preventing two agents from reserving the same task from a shared queue requires a future shared coordinator or equivalent graph-native reservation substrate.

## 7. Named Gaps

| Gap | Machine-readable value | Meaning | Candidate closure path |
|---|---|---|---|
| Cross-node invite replay prevention | `redeemer_key_binding_required` | Per-node nullifier persistence does not stop a transferred invite from being used on another node. | Bind invite issuance to an intended redeemer public key and verify against the redeemer identity key before accepting. |
| Distributed task reservation | `shared_coordinator_required` | Independent local queues do not prevent two nodes from choosing the same shared task. | Add a shared reservation coordinator or graph-native reservation/nullifier record. |
| Semantic duplicate detection | `future_graph_intelligence_required` | Raw SHA-256 detects identical bytes, not equivalent meaning in different wording. | Route through future graph intelligence, juries, reuse, reputation, and semantic comparison lanes. |

## 8. Evidence Record

Retained evidence is written to:

```text
out/block6_openclaw_two_vps_fix2e/evidence_records.json
```

The evidence must use deterministic JSON with `sort_keys=True`, compact separators, and `allow_nan=False`.

## 9. Non-Claims

Phase 1575b-Fix2e does not publish OpenClaw, create a ClawHub listing, submit public graph nodes, make a public installability claim, mint ECU, write wallets, settle ILC, clear runtime guards, activate public RC, or transition epochs.
