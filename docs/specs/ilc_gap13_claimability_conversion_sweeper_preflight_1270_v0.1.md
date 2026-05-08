# ILC Gap 13 Claimability Conversion-Sweeper Preflight 1270 v0.1

Status: preflight recorded
Date: 2026-05-08
Phase: 1270
Owner lane: G8 public-RC economic boundary

Required tokens:
- `gap13_claimability_conversion_sweeper_preflight_phase_1270.v0.1`
- `public_claimability_runtime_not_activated_phase_1270`
- `cdl_048_conversion_sweeper_requirements_recorded_phase_1270`
- `wallet_withdrawal_transfer_spend_not_enabled_phase_1270`

Decision token:

```text
gap13_claimability_preflight_verdict_phase_1270=requirements_recorded_no_activation
```

## 0. Discovery Discipline

Phase 1270 used exact-token checks only as schema/completion checks. Exact-token
`rg` verified that the required Phase 1270 tokens were not already present
outside the prompt before this artifact was written.

Concept discovery used broader searches for token components, synonyms,
neighboring ideas, and older names: public claimability, wallet claim, wallet
withdrawal, wallet transfer, wallet spend, settlement, epoch commit, lifecycle,
conversion sweeper, mandatory conversion, four issuance epochs, CDL-048,
package profile, claimable profile, and TransportPrincipal.

Contradiction and non-claim search checked denial terms and forbidden
activations: not activated, deferred, read-only, no withdrawal, no transfer, no
spend, no public P2P, no public RC claim, no wallet ledger-write authority, no
ECU minting, and no ILC settlement activation.

Source expansion followed newly discovered anchors rather than relying on exact
tokens alone. The inspected canon and code surfaces were:

- `docs/specs/ilc_gap13_public_claimability_resolution_boundary_1252_v0.1.md`
- `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md`
- `docs/specs/ilc_ecu_to_ilc_lifecycle_contract_spec_615_v0.1.md`
- `docs/specs/ilc_cdl_048_ecu_mandatory_conversion_deadline_ratification_evidence_419_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md`
- `ilc_core/ledger/ecu_ilc_lifecycle_runtime.py`
- `ilc_core/protocol/public_wallet_runtime.py`
- `ilc_core/rc/package_profiles.py`
- `ilc_core/rc/package_profile_ci_gate.py`
- `ilc_core/rc/local_skill_preview.py`
- `ilc_core/rc/atlas_graph_discipline.py`

## 1. Preflight Scope

Phase 1270 records the implementation requirements for Gap 13 public
claimability and the CDL-048 mandatory conversion sweeper. It does not implement
or activate the public claimability runtime.

The controlling inherited boundary remains:

```text
rc0_1_balance_visibility_does_not_imply_public_claimability
ecu_accrual_reaches_ilc_balance_only_through_epoch_commit
wallet_visibility_and_accounting_only
wallet_signing_spend_transfer_deferred_post_rc0_1
no_public_claimability_or_spend_in_lifecycle_spec
```

The live code inspection confirms the current runtime posture:

- `EcuIlcLifecycleRuntime.lifecycle_snapshot()` exposes `claimability_state:
  "deferred"`.
- `EcuIlcLifecycleRuntime.commit_settled_epoch()` materializes settled internal
  wallet state only after an epoch commit and preserves `claimability_state:
  "deferred"`.
- `PublicWalletRuntime` exposes read-only `wallet_status`, `wallet_history`,
  `wallet_export`, and `ledger_summary` views with `claimability_state:
  "deferred"`.
- `PublicWalletRuntime` derives `wallet_state_sha256` and balance-receipt refs
  using canonical JSON with `sort_keys=True`, `allow_nan=False`, and compact
  separators.
- `package_profile_ci_gate` records `public_claimability_runtime_activated:
  False` even when the selected claimable package profile declares future public
  claimability.
- `local_skill_preview` records `public_claimability_enabled: False`,
  `public_p2p_enabled: False`, `final_public_rc_claim: False`, and
  `transport_principal_required_for_non_loopback: True`.

## 2. CDL-048 Conversion-Sweeper Requirements

CDL-048 is already ratified in the live constitutional decision log as the ECU
mandatory conversion deadline framework:

```text
CDL-048
ecu_conversion_deadline = 4 issuance epochs
governed conversion deadline with anti-hoarding forced circulation
```

Phase 1270 records what the runtime sweeper must eventually prove before public
claimability can close:

- ECU lot accounting must track issue epoch, origin, funding provenance,
  deadline epoch, conversion status, amount, and canonical agent identity.
- The sweeper must enforce the CDL-048 four issuance epoch conversion deadline
  deterministically using ratified epoch identifiers, not wall-clock time.
- Conversion must be an epoch-settled lifecycle transition. It must not carry
  reputation or attribution forward automatically.
- Conversion must consume only finite exact numeric values. Runtime boundaries
  must construct `Decimal`, reject non-finite values, and only then continue
  range checks or arithmetic.
- Conversion records and public receipts must serialize machine-verifiable JSON
  with deterministic key ordering and `allow_nan=False`.
- Replay and double-conversion prevention must be keyed by epoch, agent
  identity, ECU lot id, wallet-state root, conversion state transition, and the
  settled runtime root.
- The sweeper must fail closed on missing issuance epoch, missing deadline,
  stale settled root, malformed amount, negative amount, non-finite amount,
  duplicate conversion, and inconsistent wallet history.

This records
`cdl_048_conversion_sweeper_requirements_recorded_phase_1270`. It does not mark
the conversion sweeper complete.

## 3. Public Claimability Requirements

Public claimability must be derived from settled runtime evidence and must not be
treated as an agent manual claim default.

The future public claimability runtime must require at least:

- settled runtime root proof
- wallet-state root
- latest balance receipt
- history digest
- epoch identifier
- canonical agent identity
- full SHA-256 or stronger digest binding for receipts and roots
- replay and double-claim prevention
- TransportPrincipal or equivalent authenticated transport identity before any
  non-loopback public API
- privacy/audit treatment for public proof presentation
- release-key, signer-lineage, BLS/PQ, and public verifier policy alignment
- counsel/IP/publication authorization before public repository or release acts

The current runtime does not provide public withdrawal, transfer, spend,
claim-mint, ECU mint, or public settlement authority. The present public wallet
surface is read-only accounting and evidence export.

## 4. Package and Public-RC Interpretation

`openclaw_skill_claimable` is a target public-RC package profile, not proof that
claimability runtime is active today. Its `public_claimability=True` profile
declaration means that final public RC must include public claimability and
conversion surfaces.

The actual CI gate and preview manifests preserve the current non-activation:

```text
public_claimability_runtime_activated=false
public_claimability_enabled=false
public_rc_claimed=false
public_p2p_enabled=false
```

Therefore the Phase 1270 closing condition is:

```text
public_claimability_runtime_not_activated_phase_1270
wallet_withdrawal_transfer_spend_not_enabled_phase_1270
```

## 5. Non-Claims

Phase 1270 does not authorize or perform:

- public claimability runtime activation
- wallet withdrawal
- wallet transfer
- wallet spend
- wallet signing authority
- wallet ledger-write authority
- ECU minting
- ILC settlement or withdrawal runtime activation
- public RC claim
- public launch claim
- public repository publication
- public package publication
- public P2P exposure
- public fetch serving
- public sidecar/projection serving
- non-loopback claimability API
- CDL register mutation
- CDL-087 ratification
- CDL-088 opening
- release-key generation
- release envelope production
- v0.2 signing
- Genesis mutation, regeneration, or signing

## 6. Closing Condition and Carry-Forward

Phase 1270 closes only the preflight requirements record for Gap 13. The
remaining public-RC blockers are still open:

- implement and verify CDL-048 ECU lot accounting and mandatory conversion
  sweeper runtime
- implement and verify public claimability state machine and proof verifier
- bind public or non-loopback claimability APIs to TransportPrincipal or an
  equivalent authenticated identity contract
- close ATLAS-G-006 public-RC graph reachability
- ratify or otherwise resolve CDL-087 before public fetch/sidecar serving claims
- complete counsel/IP/publication authorization and v0.2 signing authorization

Next planned phase:

```text
Phase 1271 - ATLAS-G-006 public-RC graph reachability gate
phase_1271_atlas_g_006_public_rc_graph_reachability_gate_next
```

## 7. Graph Delta

```text
graph_delta=load_bearing_spec_added:docs/specs/ilc_gap13_claimability_conversion_sweeper_preflight_1270_v0.1.md -> ecu/ilc/public_rc
graph_delta=support_tests_added:tests/test_phase_1270_gap13_claimability_conversion_sweeper_preflight.py -> validation
graph_delta=support_only:docs/phases/phase_1270_gap13_claimability_conversion_sweeper_preflight_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
```
