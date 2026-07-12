# ILC Phase 1575b ECU-to-ILC Value-Path Gap Closure Guidance v0.1

Status: guidance / prompt-hardening input / no activation
Date: 2026-07-12
Owner lane: G10 public-RC economics activation

## 1. Purpose

This guidance aligns Sonnet and Codex before drafting the next Phase 1575b
fix prompts. It addresses the discovered gap between the completed private
economic soft-RC rehearsal and the public-RC requirement that users can see a
real ILC economic result from ECU/value-path activity.

This document does not authorize ECU minting, ILC settlement, public-RC
publication, wallet writes, wallet withdrawals, wallet transfers, wallet spend,
epoch 0-to-1 transition, public mirror publication, or guard clearance.

## 2. Discovery Basis

MemPalace searches run before this guidance:

- `ECU to ILC public RC activation wallet claimability settlement value path`
- `public claimability activated ECU mint not authorized ILC settlement wallet ops`
- `CDL-048 conversion sweeper ECU lot eligible receipt ILC settlement`
- `claimability proof nullifier settled ILC balance wallet visible public RC activation`
- `CDL-057 witness epoch boundary blocking authority ECU ILC conversion batch`
- `OBL-040 ECU conversion deadline public RC activation certificate 1575b`

The searches agreed with direct repo reads: ILC has substantial prebuilt
claimability, conversion, lifecycle, and wallet visibility machinery, but the
final public-RC value path is not yet proven end-to-end and contains three
named value-path blocking preconditions documented below.

Key direct-read anchors:

**Glossary and identity:**

- `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:151`
  defines ECU as internal protocol credit and not an external token.
- `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:152`
  defines ILC as the external settlement token produced when ECU is converted
  at public RC activation.

**Settlement and wallet boundary lock (Phase 576):**

- `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md:13–15`
  authorize only bounded economic visibility for the operator-managed
  three-machine RC lane, not public minting closure, withdrawal, or transfer
  semantics. Token: `rc0_1_balance_visibility_does_not_imply_public_claimability`.
- `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md:28–39`
  define visible ILC balance as settled internal ledger balance, while warning
  that visibility does not imply withdrawal, transferability, or finalized
  public minting. Token: `ecu_accrual_reaches_ilc_balance_only_through_epoch_commit`.
- `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md:43–55`
  define the balance-state progression: (1) submitted ECU claim record, (2)
  epoch-attribution candidate, (3) settled internal balance, (4) deferred
  public-claimability state. Only (3) may be exposed as `balance_ilc`.
- `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md:60–68`
  state the wallet visibility/accounting boundary and no ledger write authority.
  Token: `wallet_visibility_and_accounting_only`; `wallet_has_no_ledger_write_authority`.

**ECU minting / ILC settlement boundary preflight (Phase 1315):**

- `docs/specs/ilc_ecu_minting_ilc_settlement_boundary_preflight_1315_v0.1.md:25–33`
  explicitly say Phase 1315 did not authorize ECU minting, ILC settlement,
  wallet actions, public claimability activation, public endpoint serving,
  release materialization, or signing.
- `docs/specs/ilc_ecu_minting_ilc_settlement_boundary_preflight_1315_v0.1.md:87–104`
  classify ECU minting, ILC settlement, ILC transfer, settlement-root
  publication, withdrawal runtime, and public claim endpoint as not authorized.
- `docs/specs/ilc_ecu_minting_ilc_settlement_boundary_preflight_1315_v0.1.md:114–124`
  define ledger truth objects as authoritative over wallet providers.

**Wallet ECU/ILC activation gate (Phase 1338):**

- `docs/specs/ilc_wallet_ecu_ilc_activation_or_carry_forward_gate_1338_v0.1.md:24–40`
  record carry-forward with no wallet, ECU, ILC, settlement, withdrawal, or
  value-path activation.
- `docs/specs/ilc_wallet_ecu_ilc_activation_or_carry_forward_gate_1338_v0.1.md:61–77`
  keep wallet write, ECU minting, ILC settlement, settlement-root publication,
  public claim endpoint dependency, and value-path activation unauthorized.

**Public claimability runtime (Phase 1389b):**

- `docs/specs/ilc_claimability_public_mode_runtime_1389b_v0.1.md:51–54`
  say the verifier is public-mode-ready as in-process runtime, but this does
  not activate public serving, wallet actions, ECU minting, or ILC settlement.
- `docs/specs/ilc_claimability_public_mode_runtime_1389b_v0.1.md:89–120`
  define deterministic claim nullifier construction and admission semantics.

**Public claimability activation gate (Phase 1389 rerun):**

- `docs/specs/ilc_public_claimability_activation_gate_report_1389_rerun_v0.2.md:21–30`
  record `result=public_claimability_activated` while still not minting ECU,
  settling ILC, performing wallet action, or launching mainnet.
- `docs/specs/ilc_public_claimability_activation_gate_report_1389_rerun_v0.2.md:104–117`
  repeat the same non-authorizations.

**CDL-048 conversion sweeper runtime (Phase 1274 / activated Phase 1388):**

- `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py:1–8`
  carry four critical module-scope tokens:
  - `PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface`
    (line 1) — this module is excluded from the sanitized public mirror.
  - `cdl_048_activated_phase_1388` (line 7) — CDL-048 sweeper was locally
    wired at Phase 1388, meaning the conversion receipt path executes in tests.
    **"Activated" here means locally wired and testable, not public-RC live.**
    All authority flags in every receipt remain False (see lines 305–323 below).
  - `double_entry_conservation_proven_wire_level_phase_1380` (line 6) —
    wire-level accounting verified at Phase 1380, not production live.
- `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py:221–310`
  show `convert_ecu_lot(...)`: conversion receipt generation, replay checks,
  root binding, and the receipt body at lines 298–323.
- `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py:305–323`
  show that every `convert_ecu_lot` receipt body hardcodes:
  ```python
  "ecu_mint_authorized": False,
  "ilc_settlement_authorized": False,
  "public_claimability_activated": False,
  "wallet_spend_enabled": False,
  "wallet_transfer_enabled": False,
  "wallet_withdrawal_enabled": False,
  ```
  This is a receipt-level guard independent of module guards. Even if the
  sweeper module guard were cleared, the receipt body would still record False
  for all authority flags until a signed activation certificate explicitly
  changes this.

**CDL-057 witness absence — the named constitutional blocking precondition:**

- `ilc_core/ledger/distributed_conversion_schema.py:25`
  defines `CDL057_WITNESS_ABSENT_TOKEN = "cdl057_witness_absent_fix2r"`.
- `ilc_core/ledger/distributed_conversion_schema.py:40`
  defines `FIX2R_CDL057_WITNESS_TOKEN = "phase_1568_fix2r_cdl057_witness_reference_wired"`.
- `ilc_core/ledger/distributed_conversion_schema.py:361–374`
  define `attach_cdl057_witness_ref()` which wires the CDL-057 witness field
  but defaults to `CDL057_WITNESS_ABSENT_TOKEN` when no live witness is present.
- Every `ConversionCandidate` produced by
  `ilc_core/ledger/conversion_candidate_runtime.py` currently carries
  `cdl057_witness_ref = CDL057_WITNESS_ABSENT_TOKEN`. This is correct for
  pre-RC evidence but is a named constitutional blocking precondition for the
  distributed production activation.
- `docs/specs/ilc_constitutional_decision_log_v0.1.md:160–175` (CDL-089
  prelock, Phase 1363) lock blocking authority to the CDL-057 epoch-boundary
  witness lane for ECU-to-ILC conversion batches. The lane may block advancement
  of a conversion batch across the epoch boundary when the required validator
  witness record for that batch is absent, invalid, or non-canonical.
- `docs/specs/ilc_constitutional_decision_log_v0.1.md:196–235` (CDL-089
  ratification, Phase 1364) confirm the scope and add: CDL-057 blocking
  authority does not create wallet authority, minting authority, public-serving
  authority, or public-claimability authority.
- **Implication for 1575b-Fix5/Fix6:** Distributed production conversion
  requires real CDL-057 validator epoch-boundary witness records. Currently all
  candidates carry `cdl057_witness_absent_fix2r`. Fix6 must not claim to prove
  CDL-057 witness-lane completion. Fix5 must map this as an explicit named
  dependency.

**OBL-040 closure scope — pre-RC evidence only:**

- `docs/specs/ilc_open_obligation_register_v0.1.md:1027`
  records OBL-040 status as `closed - pre-RC evidence satisfied; production
  value path not live` with the explicit non-claim: "Does not activate live
  production conversion, wallet writes, treasury writes, settlement, production
  minting, public claimability, public RC, or production value-write path."
- `docs/specs/ilc_obl039_obl040_pre_rc_closure_record_1573l_v0.1.md:40–71`
  establish closure token `obl_040_pre_rc_fully_closed_phase_1573l` with
  meaning: "OBL-040 pre-RC evidence requirement is satisfied; production path
  not live."
- The closure evidence originated from disposable namespace
  `block6_private_value_write_soft_rc_rerun006`, wiped by the Phase 1573l
  seven-step rollback protocol. No persistent production state was written.
- **Do not use OBL-040 pre-RC closure as evidence of live production conversion.**

**Lifecycle runtime — settled balance and deferred claimability:**

- `ilc_core/ledger/ecu_ilc_lifecycle_runtime.py:1–21`
  show this is Phase 652 bounded ECU/ILC lifecycle runtime wrapping
  `LmdbWalletStore` and `EcuActiveLayerRuntime`.
- `ilc_core/ledger/ecu_ilc_lifecycle_runtime.py:67`
  shows `"claimability_state": "deferred"` in the current `lifecycle_snapshot`
  output — confirming the path is present but deferred.
- `ilc_core/ledger/ecu_ilc_lifecycle_runtime.py:71–170`
  show the `commit_settled_epoch(...)` path that writes settled ILC balance and
  history. This is the authorized settlement path for bounded rehearsal.
- `ilc_core/ledger/ecu_ilc_lifecycle_runtime.py:194–197`
  show deterministic canonical hashing with `sort_keys=True` and `allow_nan=False`.

**Claimability proof binding runtime (Phase 1275):**

- `ilc_core/ledger/claimability_proof_binding_runtime.py:1–13`
  show `PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface`
  and the explicit non-authorization: no public API, wallet write, mint, spend,
  transfer, withdrawal, or settlement path.
- `ilc_core/ledger/claimability_proof_binding_runtime.py:58–80`
  show `_EXPECTED_CONVERSION_RECEIPT_KEYS` including `ecu_mint_authorized`,
  `ilc_settlement_authorized`, `public_claimability_activated`, and all
  wallet authority fields — all required to be present in the receipt and all
  expected to carry False.
- `ilc_core/ledger/claimability_proof_binding_runtime.py:175–191`
  show the proof payload body hardcodes:
  ```python
  "ecu_mint_authorized": False,
  "ilc_settlement_authorized": False,
  "non_loopback_claimability_api_enabled": False,
  "public_claimability_activated": False,
  "wallet_spend_enabled": False,
  "wallet_transfer_enabled": False,
  "wallet_withdrawal_enabled": False,
  ```
- `ilc_core/ledger/claimability_proof_binding_runtime.py:222–255`
  show the proof payload binds conversion receipt, settled root, wallet root,
  latest balance receipt, history digest, and authority flags.

**Server and sidecar (public verifier API):**

- `ilc_core/server.py:266–285`
  show the public claimability API response marks public claimability true but
  ECU mint, ILC settlement, and wallet operations false.
- `ilc_core/server.py:599–663`
  show the actual `/api/v1/claimability/verify` route and its nullifier
  registry integration.
- `ilc_core/sidecars/public_verifier_api_activation.py:38–57`
  confirm the public verifier manifest has claimability/API enabled but ECU
  mint, ILC settlement, wallet ops, and public RC disabled.

**Public wallet runtime:**

- `ilc_core/protocol/public_wallet_runtime.py:36–109`
  show read-only wallet status, history, export, and ledger summary methods.
- `ilc_core/protocol/public_wallet_runtime.py:126–137`
  show the wallet-visible fields: `balance_ilc`, `balance_ecu`, receipt refs,
  and `claimability_state: deferred`.

**Phase 1575a evidence boundary:**

- `docs/specs/ilc_economic_soft_rc_evidence_1575a_v0.1.md:12–15`
  (Phase 1575a worktree) record that 1575a did not mint ECU, settle ILC, or
  write wallet/treasury state.
- `docs/specs/ilc_economic_soft_rc_evidence_1575a_v0.1.md:44–55`
  show the current 1575a row evidence covers guarded rows but keeps production
  activation false.
- `docs/specs/ilc_economic_soft_rc_evidence_1575a_v0.1.md:103–109`
  state the 1575a non-claims: no mint, no settlement, no wallet writes, no
  epoch 0→1 transition.

**Activation matrix (Phase 1574):**

- `docs/specs/ilc_block6_public_rc_activation_matrix_1574_v0.1.md` row 6:
  "CDL-048 mandatory ECU-to-ILC conversion | Conversion receipt/runtime
  surfaces; no distributed public activation certificate |
  `pending_private_economic_soft_rc_gate`". Option B selected by Phase 1574-Fix1.
  Public claimability/conversion resolves only after Phase 1575a/1575b evidence
  and certificate.

## 3. Correct Current Conclusion

The current private soft-RC evidence is useful but insufficient for public-RC
economic activation. It proves guarded economic modules can produce deterministic
row evidence while staying default-off. It does not prove the end-user value path
from ECU activity to wallet-visible ILC.

**Three named value-path blocking preconditions remain open:**

1. **CDL-057 witness absence.** Every `ConversionCandidate` carries
   `cdl057_witness_ref = "cdl057_witness_absent_fix2r"`. Distributed production
   conversion requires real CDL-057 epoch-boundary witness records from
   validators, authorized by CDL-089 (ratified Phase 1364). No live witness
   records exist. This is the CDL-governed precondition for the
   epoch-boundary conversion batch advance.

2. **Receipt authority flags all False.** `convert_ecu_lot()` hardcodes
   `ecu_mint_authorized: False`, `ilc_settlement_authorized: False`, and
   `public_claimability_activated: False` in every receipt body (lines 305–323).
   These flags are not set by a runtime toggle; they require a signed distributed
   activation certificate from Phase 1575b to advance from False to authorized.

3. **No distributed public activation certificate.** Activation matrix row 6
   explicitly states "no distributed public activation certificate." The
   certificate is Phase 1575b's primary deliverable. Without it, CDL-048
   conversion cannot advance to `public_rc_live`.

The minimum economically honest public-RC claim requires proving:

```text
ECU/value event
  → CDL-048 conversion receipt (convert_ecu_lot)
  → claimability proof/nullifier binding (build_claimability_proof_binding)
  → settled ILC balance (commit_settled_epoch)
  → read-only wallet-visible balance (lifecycle_snapshot / wallet_status)
```

It is acceptable for public RC to leave wallet withdrawal, wallet transfer,
wallet spend, external chain bridge, and public withdrawal runtime disabled if
the release text says so plainly. It is not acceptable to call economics live if
there is no tested path to a settled ILC balance visible through a wallet/query
surface.

Note on claimability state: the current runtime always returns
`"claimability_state": "deferred"` (lifecycle_snapshot line 67). The Fix6
rehearsal must produce a path where this value is updated to a non-deferred
state for the rehearsal agent, or explicitly document why deferred is the
correct rehearsal boundary.

## 4. Sonnet Phase Drafting Guidance

### Phase 1575b-Fix5: ECU-to-ILC Value-Path Gap Closure Spec

Sensitivity: SENSITIVE planning/spec phase; no activation.

Purpose:

- Produce the authoritative gap closure spec for the public-RC value path.
- Map every current false flag and exclusion header to its required activation
  evidence, including the three named blocking preconditions in §3.
- Define the minimum public-RC economics claim and explicitly distinguish it
  from wallet withdrawal/transfer/spend.
- Distinguish "CDL-048 locally activated Phase 1388 (testable, authority flags
  all False)" from "CDL-048 publicly activated with distributed certificates
  (Phase 1575b deliverable)."
- Map CDL-057 witness-lane requirement from CDL-089 (ratified Phase 1364) as
  a named prerequisite for distributed conversion batch epoch-boundary advance.
  Fix5 must state clearly whether Fix6 proves CDL-057 witness completion (it
  cannot — it is a private rehearsal without live validators) and route CDL-057
  witness to the appropriate post-1575b phase.

Required deliverables:

- A spec doc under `docs/specs/`.
- A row-by-row matrix that links activation rows 5, 6, 20, 21, wallet
  visibility, and public claimability.
- A blocking-preconditions table with columns:
  `Precondition | CDL/OBL authority | Current state | Required to close`.
  Minimum rows: CDL-057 witness lane, receipt authority flags, distributed
  activation certificate.
- A citation table including the anchors in §2 of this guidance.
- A no-activation non-claims section.
- STATUS token:
  `ecu_to_ilc_value_path_gap_closure_spec_committed_phase_1575b_fix5`.

Hard stops:

- Do not let this phase certify public-RC economics from 1575a alone.
- Do not conflate OBL-040 pre-RC closure (`obl_040_pre_rc_fully_closed_phase_1573l`)
  with production activation. The closure is explicitly "pre-RC evidence
  satisfied; production value-write path not live."
- Do not conflate CDL-048 local activation at Phase 1388 with public distributed
  activation. Read `cdl048_conversion_sweeper_runtime.py:7,48` and `:305–323`
  before writing any claim about CDL-048 activation state.

### Phase 1575b-Fix6: Private ECU-to-ILC End-to-End Settlement Rehearsal

Sensitivity: SENSITIVE private rehearsal; use isolated branch/worktree and
private namespace. No public export.

Purpose:

- Execute the actual private end-to-end value path from a fixture ECU lot/value
  event to settled wallet-visible ILC balance.
- Reuse existing runtimes where possible instead of inventing a parallel path.
- Prove that the runtime chain is internally consistent with all authority flags
  in their current False state.

Required fixture path (cite exact module:function for each step):

1. Register one or more ECU lots in a `ConversionSweeperState`
   (`cdl048_conversion_sweeper_runtime.py` — `EcuLot` dataclass, `register_lot`).
2. Convert through `convert_ecu_lot(...)` at
   `cdl048_conversion_sweeper_runtime.py:221`. Produces a `ConversionResult`
   with receipt carrying all authority flags = False. The receipt's
   `cdl057_witness_ref` field will carry `"cdl057_witness_absent_fix2r"` —
   **this is expected and must not be patched for the rehearsal**. Fix6 rehearsal
   does not prove CDL-057 witness completion.
3. Commit settled balance through
   `EcuIlcLifecycleRuntime.commit_settled_epoch(...)` at
   `ecu_ilc_lifecycle_runtime.py:71`.
4. Build a claimability proof binding over:
   conversion receipt, settled runtime root, wallet root, latest balance receipt,
   history digest, epoch id, and agent identity via
   `build_claimability_proof_binding(...)` at
   `claimability_proof_binding_runtime.py:~120`.
5. Submit proof through the in-process verifier and, where feasible, the
   TestClient route for `/api/v1/claimability/verify`
   (`ilc_core/server.py:599–663`).
6. Query read-only wallet status/history/export/ledger summary
   (`ilc_core/protocol/public_wallet_runtime.py:36–109`) and assert the
   settled ILC balance is visible and deterministic. Note: `lifecycle_snapshot`
   currently returns `"claimability_state": "deferred"` (line 67). Confirm
   whether this is the correct rehearsal boundary state or whether Fix6 should
   update it for the rehearsal agent.

Required tests:

- Correct conversion receipt accepted.
- Wrong settled root rejected.
- Wrong wallet root rejected.
- Wrong latest balance receipt rejected.
- Wrong history digest rejected.
- Wrong agent id rejected.
- Duplicate conversion/replay rejected (uses `conversion_key` deduplication
  in `cdl048_conversion_sweeper_runtime.py:292–296`).
- Duplicate public claim nullifier rejected.
- Two identical runs produce identical roots, receipts, proof refs, and
  wallet-visible balances.
- No floats, no `allow_nan=True`, no wall-clock protocol fields.
- Wallet withdrawal, transfer, spend, signing, ledger-write, and external bridge
  remain unavailable — verified by checking the authority flags in every
  receipt, proof payload, and wallet response.
- Assert `cdl057_witness_ref == "cdl057_witness_absent_fix2r"` in the
  generated candidates — confirm the absent token is correctly propagated and
  is not silently dropped.

Required deliverables:

- Private evidence doc under `docs/specs/` with `PUBLIC_RC_EXCLUDE`.
- Private runner or test fixture if needed, also `PUBLIC_RC_EXCLUDE`.
- Focused tests.
- STATUS token:
  `ecu_to_ilc_private_end_to_end_rehearsal_passed_phase_1575b_fix6`.

Hard stops:

- Do not write real production state.
- Do not clear guard constants or modify receipt authority flags.
- Do not publish evidence into the sanitized public mirror.
- Do not silently reinterpret `claimability_state: deferred` as public
  withdrawal/transfer authority.
- Do not claim CDL-057 witness-lane completion. Record the absent token
  explicitly in the evidence doc as a named open item for distributed
  production activation.

### Phase 1575b-Fix7: Wallet-Visible ILC Balance Certificate

Sensitivity: SENSITIVE certificate phase; no publication.

Purpose:

- Certify whether the read-only wallet/query surface is sufficient for public RC.
- Keep wallet writes explicitly out of scope unless separately authorized.

Recommended certificate result:

```text
public_rc_wallet_minimum = read_only_settled_ilc_balance_visibility
wallet_withdrawal_transfer_spend = post_rc_or_separate_activation
```

Required checks:

- `wallet_status` exposes `balance_ilc`, `balance_ecu`, last settled epoch,
  history digest, latest receipt, and settled root
  (`ilc_core/protocol/public_wallet_runtime.py:126–137`).
- `wallet_history`, `wallet_export`, and `ledger_summary` agree.
- Replaying the same epoch commit is idempotent
  (token: `settlement_replay_must_fail_closed_or_noop_without_balance_drift`
  from `rc0_1_settlement_wallet_boundary_lock_576_v0.1.md:85`).
- Replaying the same epoch with a different reward delta fails closed.
- Balance display is deterministic and exact numeric — `Decimal`, not float.
- No wallet API method can mutate ledger, graph, settlement, or wallet state
  except the explicitly scoped private rehearsal fixture.

Required deliverables:

- Certificate doc under `docs/specs/`.
- Focused tests or references to the tests added in Fix6.
- STATUS token:
  `wallet_visible_ilc_balance_certificate_committed_phase_1575b_fix7`.

## 5. Phase 1575b and 1575c Integration

Phase 1575b must not be a generic certificate. It must consume:

- 1575a + 1575a-Fix1 private economic soft-RC evidence.
- 1575b-Fix5 value-path gap closure spec (including blocking-preconditions table).
- 1575b-Fix6 private ECU-to-ILC end-to-end evidence.
- 1575b-Fix7 wallet-visible balance certificate.

Phase 1575b must issue a distributed activation certificate. This is the
primary deliverable that advances activation matrix row 6 from
`pending_private_economic_soft_rc_gate` to a claimable state. The certificate
must address each blocking precondition in §3 by name, state which are closed
by Fix6 evidence and which remain open (specifically CDL-057 witness lane and
receipt authority flag activation authority), and record which guard constants
remain True and why.

Phase 1575b can then decide, row by row, which surfaces become
`public_rc_live`. For any row certified public-RC live, 1575b or the follow-on
publication hardening must:

- remove the relevant `PUBLIC_RC_EXCLUDE` header only from certified files;
- rerun `tools/check_public_rc_exclude_imports.py`;
- rerun `ilc_core/rc/source_allowlist_export_rehearsal.py`;
- prove excluded private evidence and private runner files remain absent from
  the sanitized mirror;
- record exactly which guard constants remain True and which, if any, are
  replaced by signed activation certificates rather than conditional runtime
  toggles.

Phase 1575c must not publish public RC unless the release statement can say,
in plain language:

```text
Public RC includes live public-RC economics sufficient to produce wallet-visible
settled ILC balances from authorized ECU/value-path activity. Public RC does
not yet include wallet withdrawal, wallet transfer, wallet spend, external
bridge, or public withdrawal runtime unless a separate activation certificate
explicitly says otherwise. The CDL-057 epoch-boundary witness lane requires
live validator participation and is not activated at public RC launch unless a
separate Phase 1575b certificate explicitly authorizes it.
```

## 6. Anti-Drift Rules

**Value path:**
- Do not equate conversion candidate generation with final ILC coin creation.
- Do not equate public claimability verifier readiness with ILC settlement.
- Do not equate wallet-visible balance with withdrawal or transfer semantics.

**Activation state precision:**
- Do not conflate "CDL-048 locally activated Phase 1388 (all authority flags
  hardcoded False)" with "CDL-048 publicly activated with distributed
  certificate." Read `cdl048_conversion_sweeper_runtime.py:305–323` to see the
  receipt-level authority flags before making any claim.
- Do not use OBL-040 pre-RC closure (`obl_040_pre_rc_fully_closed_phase_1573l`)
  as evidence of live production conversion. The closure record explicitly scopes
  "pre-RC evidence satisfied; production value-write path not live."
- The CDL-057 witness absent token `"cdl057_witness_absent_fix2r"` must be
  treated as a named open blocker in every phase that generates
  `ConversionCandidate` objects. Do not silently drop or ignore it.

**Security and correctness:**
- Do not use hidden conditional gates as public-RC attack surface. Public-RC
  software should prefer compile/export exclusion, signed activation
  certificates, or explicit release profile manifests over runtime booleans
  that can be flipped accidentally.
- Do not use Python `float` at any economic boundary.
- Do not introduce wall-clock ordering into protocol settlement or claimability.
- Do not rely on `out/` private rehearsal evidence in a public mirror.
- Do not merge private rehearsal branch artifacts into main until the branch
  delta has passed import closure, source export rehearsal, and public-RC
  exclusion checks.

## 7. Recommendation

Draft and execute the phases in this order:

1. 1575b-Fix5: value-path gap closure spec (blocking-preconditions table required).
2. 1575b-Fix6: private ECU-to-ILC end-to-end settlement rehearsal.
3. 1575b-Fix7: wallet-visible ILC balance certificate.
4. 1575b: distributed activation certificate, row-by-row decision.
5. 1575c: public RC publication gate.

Do not move directly from 1575a-Fix1 to final public-RC publication. 1575a-Fix1
is strong evidence that the guarded economic rows can be rehearsed safely, but
it is not yet evidence that public users can obtain and verify wallet-visible
settled ILC. The three named blocking preconditions in §3 must each be addressed
by name in the Phase 1575b certificate.
