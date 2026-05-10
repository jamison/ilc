# ILC Public Claimability Verifier Contract Preflight 1291 v0.1

**Date:** 2026-05-10
**Phase:** 1291, Window 1289-1302
**Status:** Contract boundary recorded; no public API, no public claimability
activation, and no runtime helper added.

```text
public_claimability_verifier_contract_preflight_phase_1291.v0.1
public_claimability_activation_not_authorized_by_default_phase_1291
claimability_verifier_public_api_not_enabled_phase_1291
wallet_withdrawal_transfer_spend_still_blocked_phase_1291
public_rc_remains_blocked_after_phase_1291
public_claimability_verifier_contract_verdict_phase_1291=contract_defined_public_api_not_enabled
claimability_contract_no_runtime_helper_added_phase_1291
phase_1292_verifier_negative_path_corpus_package_boundary_next
```

---

## 1. Verdict

Phase 1291 defines the future public claimability verifier contract shape, but
does not enable a verifier service. It adds no HTTP route, FastAPI route,
socket listener, non-loopback bind, wildcard bind, public host bind, peer
discovery surface, wallet write path, claim endpoint, withdrawal endpoint,
transfer endpoint, spend endpoint, ECU mint endpoint, or ILC settlement
endpoint.

The authoritative verdict is:

```text
public_claimability_verifier_contract_verdict_phase_1291=contract_defined_public_api_not_enabled
```

This is a specification preflight only. No new runtime helper is introduced in
Phase 1291 because adding even a local helper before the public-safe disclosure
schema and negative-path corpus are locked would increase later release review
surface. Existing local helpers remain internal-only and carry their
`PUBLIC_RC_EXCLUDE` headers.

---

## 2. Section 0 Discovery Results

| Check | Result |
|-------|--------|
| Section 0a Known-token audit | Direct-read current planning canon: `docs/PLANNING_INDEX.md`, Capsule v5.52, `docs/phases/STATUS.md`, active Window 1289-1302 sequence lock and guidance, Phase 1291 prompt, Phase 1283 and 1284 claimability preflights, Phase 1274/1275 conversion and proof-binding specs, Phase 1288 Fix1 runtime audit walkthrough, Phase 1255 source allowlist procedure, and the two local ledger helper files. |
| Section 0b Concept-discovery search | Searched public claimability, claimability verifier, claimability API, claim endpoint, public verifier, non-loopback, wallet withdrawal, wallet transfer, wallet spend, ECU mint, ILC settlement, and `PUBLIC_RC_EXCLUDE`. |
| Section 0c Contradiction and non-claim search | Confirmed the repo still records no public claimability activation, no public verifier service, no public or non-loopback claimability API, no wallet withdrawal/transfer/spend semantics, no ECU minting, and no ILC settlement authority. |
| Section 0d Source expansion and newly discovered tokens | The material new Phase 1291 tokens are `public_claimability_verifier_contract_verdict_phase_1291=contract_defined_public_api_not_enabled`, `claimability_contract_no_runtime_helper_added_phase_1291`, and `phase_1292_verifier_negative_path_corpus_package_boundary_next`. |

Exact-token `rg` remains a schema and completion check only. Phase 1291 relied
on direct repo reads plus concept and denial searches before recording this
contract boundary.

---

## 3. Future Contract Envelope

The future verifier contract should use a two-object envelope when and only
when a later phase explicitly authorizes implementation:

```text
ClaimabilityVerifierInput
ClaimabilityVerifierDecision
```

`ClaimabilityVerifierInput` must be a canonical machine-verifiable input object.
At minimum it must carry:

| Field | Required boundary |
|-------|-------------------|
| `contract_version` | Must equal `public_claimability_verifier_contract_preflight_phase_1291.v0.1` or a later ratified successor. |
| `presentation_id` | Deterministic content identifier for the submitted presentation. |
| `canonical_agent_identity` | Canonical agent identity bound to the claimability proof. |
| `epoch_id` | Ratified epoch identifier; no wall-clock expiry source. |
| `settled_runtime_root` | Domain-separated root, for example `settled_runtime_sha256:<64 lowercase hex>`. |
| `wallet_state_root` | Domain-separated root, for example `wallet_state_sha256:<64 lowercase hex>`. |
| `latest_balance_receipt_ref` | Balance receipt reference, for example `balance_receipt_sha256:<64 lowercase hex>`. |
| `history_digest` | Canonical history digest bound to the claimed balance state. |
| `claimability_proof_ref` | Claimability proof reference, for example `claimability_proof_sha256:<64 lowercase hex>`. |
| `conversion_receipt_sha256` | Full SHA-256 hash of the conversion receipt payload. |
| `conversion_key_sha256` | Full SHA-256 hash of the deterministic conversion key. |
| `conversion_lot_id` | ECU lot identifier for the conversion receipt. |
| `conversion_issuance_epoch` | Ratified issuance epoch for the conversion lot. |
| `conversion_deadline_epoch` | Ratified deadline epoch for CDL-048 conversion enforcement. |
| `transport_principal_ref` | Required before any future non-loopback/public serving mode. Phase 1291 does not authorize that mode. |
| `public_claimability_activated` | Must remain `false` in this phase. |
| `non_loopback_claimability_api_enabled` | Must remain `false` in this phase. |
| `wallet_withdrawal_enabled` | Must remain `false` in this phase. |
| `wallet_transfer_enabled` | Must remain `false` in this phase. |
| `wallet_spend_enabled` | Must remain `false` in this phase. |
| `ecu_mint_authorized` | Must remain `false` in this phase. |
| `ilc_settlement_authorized` | Must remain `false` in this phase. |

`ClaimabilityVerifierDecision` must be a deterministic decision object. In any
future implementation, it must carry:

| Field | Required boundary |
|-------|-------------------|
| `contract_version` | The exact contract version used for validation. |
| `decision` | One of the ratified decision tokens. Phase 1291 only authorizes `contract_preflight_recorded_public_api_not_enabled`. |
| `public_api_enabled` | Must be `false` until a later explicit authority phase changes it. |
| `public_claimability_activated` | Must be `false` until a later explicit authority phase changes it. |
| `non_loopback_claimability_api_enabled` | Must be `false` until a later explicit authority phase changes it. |
| `wallet_withdrawal_enabled` | Must be `false`. |
| `wallet_transfer_enabled` | Must be `false`. |
| `wallet_spend_enabled` | Must be `false`. |
| `ecu_mint_authorized` | Must be `false`. |
| `ilc_settlement_authorized` | Must be `false`. |
| `rejection_reasons` | Stable list of denial tokens for every failed precondition. |
| `canonical_decision_sha256` | Future canonical JSON decision hash if implementation is authorized. |

If any future machine artifact hashes, signs, exports, or verifies these
objects, the JSON serialization must be deterministic with sorted keys, compact
separators, and non-finite numeric rejection.

---

## 4. Mandatory Denial Conditions

A future verifier must fail closed if any of these conditions is present:

- Any activation flag is `true` before explicit public activation authority.
- A public or non-loopback claimability API is requested before TransportPrincipal
  public-path authority.
- `wallet_withdrawal_enabled`, `wallet_transfer_enabled`, or
  `wallet_spend_enabled` is `true`.
- `ecu_mint_authorized` or `ilc_settlement_authorized` is `true`.
- A root uses the wrong domain prefix or an invalid SHA-256 digest shape.
- The settled runtime root, wallet-state root, latest balance receipt, history
  digest, claimability proof ref, conversion receipt hash, conversion key hash,
  conversion lot, or conversion epoch fields are missing or mismatched.
- The conversion receipt does not enforce the CDL-048 deadline epoch contract.
- A numeric input is a Python float, a non-finite Decimal, or a string numeric
  value that cannot be parsed into the ratified exact numeric representation.
- A canonical JSON boundary would include non-string keys, cycles, excessive
  depth, excessive node count, or non-deterministic fields.
- A replay/nullifier or duplicate-claim registry requirement remains
  unspecified for the future public mode.
- The field-level public-safe disclosure schema has not been ratified.
- The relevant helper still carries `PUBLIC_RC_EXCLUDE` and has not been
  explicitly promoted by a later release allowlist review.

Phase 1291 records these as contract-denial requirements only. It does not
implement them; stated as an exact guard, Phase 1291 does not implement them.

Exact public-surface denial phrase guard:

```text
no HTTP route
FastAPI route
socket listener
non-loopback bind
wildcard bind
public host bind
peer discovery
public claimability API activation
claim endpoint
withdrawal endpoint
transfer endpoint
spend endpoint
ECU mint endpoint
ILC settlement endpoint
excessive depth
```

---

## 5. Public-Safe Disclosure Boundary

Phase 1291 does not declare the full Phase 1275 proof-binding payload
public-safe. Exact guard: Phase 1291 does not declare the full Phase 1275 proof-binding payload public-safe.
Public-safe field projection remains open. A later phase must decide which
fields may be shown to external requesters, which must be redacted, which may
be represented only by hashes, and whether any field needs a zero-knowledge or
nullifier-style substitute before public serving.

This matters because a verifier input can be technically valid and still be
unsafe for public disclosure. Correctness and public disclosure are separate gates.

---

## 6. `PUBLIC_RC_EXCLUDE` Boundary

Existing local helpers remain excluded from the public RC package unless a
later explicit allowlist review removes or supersedes the marker:

```text
ilc_core/ledger/cdl048_conversion_sweeper_runtime.py
PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface

ilc_core/ledger/claimability_proof_binding_runtime.py
PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface
```

Phase 1291 adds no helper and therefore adds no new `PUBLIC_RC_EXCLUDE` header.
The absence of a new helper is intentional:

```text
claimability_contract_no_runtime_helper_added_phase_1291
```

---

## 7. Carry-Forward Blockers

Public RC remains blocked after Phase 1291 by:

- Public claimability verifier/API activation authority.
- Phase 1292 verifier negative-path corpus and package-profile boundary.
- Release allowlist decision for whether any helper marked `PUBLIC_RC_EXCLUDE`
  is removed, rewritten, or promoted.
- Public-safe disclosure schema, privacy filtering, replay/nullifier policy,
  and duplicate-claim registry.
- TransportPrincipal public-path activation authority before any non-loopback
  claimability API.
- Sidecar public-safe projection schema, bind/listener authority, and peer
  discovery policy.
- Counsel, IP, publication, source allowlist export execution, package
  publication, release artifacts, release keys, and release envelopes.
- Genesis Atlas mutation/regeneration/signing if needed and v0.2 signing
  authorization.
- Wallet withdrawal, wallet transfer, wallet spend, wallet signing authority,
  wallet ledger-write authority, ECU minting, ILC settlement, and withdrawal
  runtime activation.
- CDL-088 opening or any reciprocal scoring or ECU-escrow admission policy.

Next planned phase:

```text
phase_1292_verifier_negative_path_corpus_package_boundary_next
```

Phase 1292 is sensitive and requires explicit authorization before execution.

---

## 8. Non-Authorization Boundary

Phase 1291 does not authorize public RC, public launch, public repository
publication, public package publication, source allowlist export execution,
public release artifact production, release-key generation, release envelope
production, public P2P, public fetch serving, public sidecar/projection
serving, non-loopback sidecar/projection serving, public claimability API
activation, public verifier service, public claimability activation, wallet
withdrawal, wallet transfer, wallet spend, wallet signing authority, wallet
ledger-write authority, ECU minting, ILC settlement, withdrawal runtime
activation, CDL mutation, CDL-088 opening, Genesis Atlas mutation/regeneration
or signing, v0.2 signing, IP filing, paper publication, immutable diagnostic
mutation, or production `commit.epoch` emission.

---

## 9. Graph Delta

```text
graph_delta=support_only:docs/specs/ilc_public_claimability_verifier_contract_preflight_1291_v0.1.md -> ecu/ilc/public_rc
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1291_g8_public_claimability_verifier_contract_preflight.md -> planning/prompts
graph_delta=support_tests_added:tests/test_phase_1291_public_claimability_verifier_contract_preflight.py -> validation
graph_delta=support_only:docs/phases/phase_1291_public_claimability_verifier_contract_preflight_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.52.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
```
